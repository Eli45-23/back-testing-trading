from __future__ import annotations

import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

import spy_research.cli as cli_module
from spy_research.indicators import FiveMinuteIndicatorRow, FiveMinuteVwapRow
from spy_research.interactions import (
    ImmediateState,
    InteractionType,
    LevelType,
    RetestState,
)
from spy_research.strategy import (
    BasePriceActionCandidate,
    BasePriceActionResult,
    BaseSetupStatus,
    ConfirmationType,
    SetupDirection,
)
from spy_research.strategy.comparisons import (
    Ema20VwapAlignmentComparisonService,
    Ema20VwapAlignmentState,
    Ema20VwapComparisonInputError,
    annotate_confirmed_ema20_vwap_alignment,
    annotate_ema20_vwap_alignment,
    indicator_stack_state,
)


SESSION = date(2026, 8, 19)
CONFIRMATION = datetime(2026, 8, 19, 14, 0, tzinfo=UTC)


def setup(direction: SetupDirection = SetupDirection.LONG) -> BasePriceActionCandidate:
    signal = CONFIRMATION + timedelta(minutes=5)
    return BasePriceActionCandidate(
        setup_identity="setup",
        break_interaction_identity="break",
        follow_through_identity="follow",
        session_date=SESSION,
        level_type=LevelType.PDH,
        level_price=Decimal("100"),
        direction=direction,
        break_interaction_type=(
            InteractionType.CLOSE_THROUGH_ABOVE
            if direction is SetupDirection.LONG
            else InteractionType.CLOSE_THROUGH_BELOW
        ),
        break_timestamp=CONFIRMATION - timedelta(minutes=5),
        break_completed_at=CONFIRMATION,
        exact_immediate_state=ImmediateState.HOLD,
        exact_retest_state=RetestState.NO_RETEST,
        status=BaseSetupStatus.CONFIRMED,
        confirmation_type=ConfirmationType.IMMEDIATE_HOLD,
        confirmation_bar_timestamp=CONFIRMATION,
        signal_known_at=signal,
        earliest_entry_timestamp=signal,
        same_session_executable=True,
    )


def ema(
    ema20: str | None,
    *,
    ema9: str | None = "101",
    timestamp: datetime = CONFIRMATION,
) -> FiveMinuteIndicatorRow:
    return FiveMinuteIndicatorRow(
        symbol="SPY",
        timestamp=timestamp,
        session_date=timestamp.date(),
        close=Decimal("100"),
        ema9=Decimal(ema9) if ema9 is not None else None,
        ema20=Decimal(ema20) if ema20 is not None else None,
    )


def vwap(value: str | None, *, timestamp: datetime = CONFIRMATION):
    return FiveMinuteVwapRow(
        symbol="SPY",
        timestamp=timestamp,
        session_date=timestamp.date(),
        typical_price=Decimal("100"),
        vwap=Decimal(value) if value is not None else None,
    )


@pytest.mark.parametrize(
    "direction,ema20,vwap_value,state,distance",
    (
        (SetupDirection.LONG, "101", "100", Ema20VwapAlignmentState.EMA20_VWAP_ALIGNED, "1"),
        (SetupDirection.LONG, "99", "100", Ema20VwapAlignmentState.EMA20_VWAP_NOT_ALIGNED, "-1"),
        (SetupDirection.LONG, "100", "100", Ema20VwapAlignmentState.EMA20_VWAP_NOT_ALIGNED, "0"),
        (SetupDirection.SHORT, "99", "100", Ema20VwapAlignmentState.EMA20_VWAP_ALIGNED, "1"),
        (SetupDirection.SHORT, "101", "100", Ema20VwapAlignmentState.EMA20_VWAP_NOT_ALIGNED, "-1"),
        (SetupDirection.SHORT, "100", "100", Ema20VwapAlignmentState.EMA20_VWAP_NOT_ALIGNED, "0"),
    ),
)
def test_directional_rules(direction, ema20, vwap_value, state, distance) -> None:
    annotation = annotate_ema20_vwap_alignment(
        setup(direction), ema(ema20), vwap(vwap_value)
    )
    assert annotation.alignment_state is state
    assert annotation.directional_ema20_vwap_distance == Decimal(distance)
    assert annotation.indicator_timestamp == CONFIRMATION


@pytest.mark.parametrize("ema20,vwap_value", ((None, "100"), ("100", None)))
def test_warmup_or_missing_vwap_is_unavailable(ema20, vwap_value) -> None:
    annotation = annotate_ema20_vwap_alignment(
        setup(), ema(ema20), vwap(vwap_value)
    )
    assert annotation.alignment_state is Ema20VwapAlignmentState.EMA20_VWAP_UNAVAILABLE
    assert annotation.directional_ema20_vwap_distance is None
    assert annotation.indicator_timestamp is None


def test_decimal_distances_preserve_precision() -> None:
    annotation = annotate_ema20_vwap_alignment(
        setup(SetupDirection.SHORT),
        ema("100.123456789012345"),
        vwap("100.223456789012346"),
    )
    assert annotation.signed_ema20_vwap_distance == Decimal("-0.100000000000001")
    assert annotation.absolute_ema20_vwap_distance == Decimal("0.100000000000001")
    assert annotation.directional_ema20_vwap_distance == Decimal("0.100000000000001")


def test_only_exact_confirmation_rows_can_affect_annotation() -> None:
    item = setup()
    setups = BasePriceActionResult(
        start_date=SESSION,
        end_date=SESSION,
        seed_count=1,
        confirmed_count=1,
        non_confirmed_count=0,
        candidates=(item,),
    )
    later = CONFIRMATION + timedelta(minutes=5)
    first = annotate_confirmed_ema20_vwap_alignment(
        setups,
        (ema("101"), ema("1", timestamp=later)),
        (vwap("100"), vwap("200", timestamp=later)),
    )
    second = annotate_confirmed_ema20_vwap_alignment(
        setups,
        (ema("101"), ema("999", timestamp=later)),
        (vwap("100"), vwap("1", timestamp=later)),
    )
    assert first == second
    assert first[0].alignment_state is Ema20VwapAlignmentState.EMA20_VWAP_ALIGNED


def test_no_previous_session_fallback() -> None:
    item = setup()
    setups = BasePriceActionResult(
        start_date=SESSION,
        end_date=SESSION,
        seed_count=1,
        confirmed_count=1,
        non_confirmed_count=0,
        candidates=(item,),
    )
    previous = CONFIRMATION - timedelta(days=1)
    annotation = annotate_confirmed_ema20_vwap_alignment(
        setups,
        (ema("101", timestamp=previous),),
        (vwap("100", timestamp=previous),),
    )[0]
    assert annotation.alignment_state is Ema20VwapAlignmentState.EMA20_VWAP_UNAVAILABLE


def test_mismatched_direct_row_is_rejected() -> None:
    with pytest.raises(Ema20VwapComparisonInputError, match="confirmation timestamp"):
        annotate_ema20_vwap_alignment(
            setup(), ema("101", timestamp=CONFIRMATION + timedelta(minutes=5)), vwap("100")
        )


def test_stack_state_has_deterministic_order_equality_and_unavailable() -> None:
    assert indicator_stack_state(Decimal("3"), Decimal("2"), Decimal("1")) == (
        "EMA9 > EMA20 > VWAP"
    )
    assert indicator_stack_state(Decimal("2"), Decimal("2"), Decimal("1")) == (
        "EMA20 = EMA9 > VWAP"
    )
    assert indicator_stack_state(Decimal("2"), None, Decimal("1")) == (
        "EMA9 > VWAP | EMA20=UNAVAILABLE"
    )


def test_annotation_is_immutable_offline_and_nonpersistent(monkeypatch, tmp_path) -> None:
    def reject_network(*args, **kwargs):
        raise AssertionError("Stage 10.6 must remain offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    annotation = annotate_ema20_vwap_alignment(setup(), ema("101"), vwap("100"))
    with pytest.raises(ValidationError):
        annotation.alignment_state = Ema20VwapAlignmentState.EMA20_VWAP_NOT_ALIGNED
    assert list(tmp_path.iterdir()) == []


def test_cli_command_is_offline_and_read_only(monkeypatch, tmp_path, capsys) -> None:
    sentinel = object()

    def mocked_calculate(self, *, start, end):
        assert start == end == SESSION
        return sentinel

    def mocked_print(result):
        assert result is sentinel
        print("ema20-vwap-pass")

    monkeypatch.setattr(
        Ema20VwapAlignmentComparisonService, "calculate", mocked_calculate
    )
    monkeypatch.setattr(
        cli_module, "_print_ema20_vwap_alignment_comparison", mocked_print
    )
    exit_code = cli_module.main(
        [
            "compare-ema20-vwap-alignment",
            "--start",
            SESSION.isoformat(),
            "--end",
            SESSION.isoformat(),
            "--raw-data-root",
            str(tmp_path / "raw"),
            "--processed-data-root",
            str(tmp_path / "processed"),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "ema20-vwap-pass\n"
    assert captured.err == ""
    assert list(tmp_path.iterdir()) == []
