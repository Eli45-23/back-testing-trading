from __future__ import annotations

import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

import spy_research.cli as cli_module
from spy_research.bars import FiveMinuteBar
from spy_research.indicators import FiveMinuteVwapRow
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
    EntryStatus,
    SetupEntryReference,
    SetupHorizonOutcome,
    SetupOutcome,
    SetupOutcomeResult,
    SetupDirection,
    calculate_base_strategy_statistics,
)
from spy_research.strategy.comparisons import (
    EmaAlignmentAnnotation,
    EmaAlignmentState,
    EmaCrossContextState,
    VwapAlignmentComparisonService,
    VwapAlignmentState,
    VwapComparisonInputError,
    annotate_confirmed_vwap_alignment,
    annotate_vwap_alignment,
    calculate_vwap_alignment_comparison,
    select_prior_ema_cross,
)


SESSION = date(2026, 8, 19)
CONFIRMATION = datetime(2026, 8, 19, 14, 0, tzinfo=UTC)


def setup(
    direction: SetupDirection = SetupDirection.LONG,
    *,
    identity: str = "setup",
    confirmation: datetime = CONFIRMATION,
    executable: bool = True,
) -> BasePriceActionCandidate:
    signal = confirmation + timedelta(minutes=5)
    return BasePriceActionCandidate(
        setup_identity=identity,
        break_interaction_identity=f"break-{identity}",
        follow_through_identity=f"follow-{identity}",
        session_date=SESSION,
        level_type=LevelType.PDH,
        level_price=Decimal("100"),
        direction=direction,
        break_interaction_type=(
            InteractionType.CLOSE_THROUGH_ABOVE
            if direction is SetupDirection.LONG
            else InteractionType.CLOSE_THROUGH_BELOW
        ),
        break_timestamp=confirmation - timedelta(minutes=5),
        break_completed_at=confirmation,
        exact_immediate_state=ImmediateState.HOLD,
        exact_retest_state=RetestState.NO_RETEST,
        status=BaseSetupStatus.CONFIRMED,
        confirmation_type=ConfirmationType.IMMEDIATE_HOLD,
        confirmation_bar_timestamp=confirmation,
        signal_known_at=signal,
        earliest_entry_timestamp=signal,
        same_session_executable=executable,
    )


def bar(close: str = "100", *, timestamp: datetime = CONFIRMATION) -> FiveMinuteBar:
    value = Decimal(close)
    return FiveMinuteBar(
        symbol="SPY",
        timestamp=timestamp,
        session_date=timestamp.date(),
        open=value,
        high=value + Decimal("1"),
        low=value - Decimal("1"),
        close=value,
        volume=100,
        trade_count=10,
        source="alpaca",
        feed="sip",
        timeframe="5Min",
        adjustment="raw",
        source_bar_count=5,
    )


def vwap(value: str | None, *, timestamp: datetime = CONFIRMATION) -> FiveMinuteVwapRow:
    return FiveMinuteVwapRow(
        symbol="SPY",
        timestamp=timestamp,
        session_date=timestamp.date(),
        typical_price=Decimal("100"),
        vwap=Decimal(value) if value is not None else None,
    )


@pytest.mark.parametrize(
    "direction,close,vwap_value,expected,directional",
    (
        (SetupDirection.LONG, "101", "100", VwapAlignmentState.VWAP_ALIGNED, "1"),
        (SetupDirection.LONG, "99", "100", VwapAlignmentState.VWAP_NOT_ALIGNED, "-1"),
        (SetupDirection.LONG, "100", "100", VwapAlignmentState.VWAP_NOT_ALIGNED, "0"),
        (SetupDirection.SHORT, "99", "100", VwapAlignmentState.VWAP_ALIGNED, "1"),
        (SetupDirection.SHORT, "101", "100", VwapAlignmentState.VWAP_NOT_ALIGNED, "-1"),
        (SetupDirection.SHORT, "100", "100", VwapAlignmentState.VWAP_NOT_ALIGNED, "0"),
    ),
)
def test_frozen_directional_rules(direction, close, vwap_value, expected, directional):
    annotation = annotate_vwap_alignment(
        setup(direction), bar(close), vwap(vwap_value)
    )
    assert annotation.alignment_state is expected
    assert annotation.directional_vwap_distance == Decimal(directional)
    assert annotation.indicator_timestamp == CONFIRMATION


def test_exact_signed_absolute_and_directional_decimal_distances() -> None:
    annotation = annotate_vwap_alignment(
        setup(SetupDirection.SHORT),
        bar("100.123456789012345"),
        vwap("100.223456789012346"),
    )
    assert annotation.signed_price_vwap_distance == Decimal("-0.100000000000001")
    assert annotation.absolute_price_vwap_distance == Decimal("0.100000000000001")
    assert annotation.directional_vwap_distance == Decimal("0.100000000000001")


def test_missing_same_bar_vwap_is_explicitly_unavailable() -> None:
    annotation = annotate_vwap_alignment(setup(), bar(), None)
    assert annotation.alignment_state is VwapAlignmentState.VWAP_UNAVAILABLE
    assert annotation.vwap is None
    assert annotation.indicator_timestamp is None
    assert annotation.directional_vwap_distance is None


def test_exact_confirmation_bar_close_and_vwap_are_used_only() -> None:
    item = setup()
    result = BasePriceActionResult(
        start_date=SESSION,
        end_date=SESSION,
        seed_count=1,
        confirmed_count=1,
        non_confirmed_count=0,
        candidates=(item,),
    )
    exact_bar = bar("101")
    exact_vwap = vwap("100")
    later_bar_a = bar("50", timestamp=CONFIRMATION + timedelta(minutes=5))
    later_bar_b = bar("500", timestamp=CONFIRMATION + timedelta(minutes=5))
    later_vwap_a = vwap("200", timestamp=CONFIRMATION + timedelta(minutes=5))
    later_vwap_b = vwap("1", timestamp=CONFIRMATION + timedelta(minutes=5))
    first = annotate_confirmed_vwap_alignment(
        result, (exact_bar, later_bar_a), (exact_vwap, later_vwap_a)
    )
    second = annotate_confirmed_vwap_alignment(
        result, (exact_bar, later_bar_b), (exact_vwap, later_vwap_b)
    )
    assert first == second
    assert first[0].confirmation_close == Decimal("101")
    assert first[0].vwap == Decimal("100")


def test_no_fallback_to_other_bar_or_previous_session() -> None:
    item = setup()
    result = BasePriceActionResult(
        start_date=SESSION,
        end_date=SESSION,
        seed_count=1,
        confirmed_count=1,
        non_confirmed_count=0,
        candidates=(item,),
    )
    previous = vwap("99", timestamp=CONFIRMATION - timedelta(days=1))
    later = vwap("99", timestamp=CONFIRMATION + timedelta(minutes=5))
    annotation = annotate_confirmed_vwap_alignment(
        result, (bar(),), (previous, later)
    )[0]
    assert annotation.alignment_state is VwapAlignmentState.VWAP_UNAVAILABLE


def test_mismatched_direct_vwap_or_price_bar_is_rejected() -> None:
    with pytest.raises(VwapComparisonInputError, match="confirmation timestamp"):
        annotate_vwap_alignment(
            setup(), bar(), vwap("100", timestamp=CONFIRMATION + timedelta(minutes=5))
        )
    with pytest.raises(VwapComparisonInputError, match="confirmation timestamp"):
        annotate_vwap_alignment(
            setup(), bar(timestamp=CONFIRMATION + timedelta(minutes=5)), vwap("100")
        )


def test_annotation_is_offline_nonpersistent_and_immutable(monkeypatch, tmp_path) -> None:
    item, price, indicator = setup(), bar(), vwap("99")
    before = (item.model_dump(), price.model_dump(), indicator.model_dump())

    def reject_network(*args, **kwargs):
        raise AssertionError("Stage 10.3 must remain offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    annotate_vwap_alignment(item, price, indicator)
    assert before == (item.model_dump(), price.model_dump(), indicator.model_dump())
    assert list(tmp_path.iterdir()) == []


def outcome(
    item: BasePriceActionCandidate,
    mfe: str,
    *,
    available: bool = True,
) -> SetupOutcome:
    reference = SetupEntryReference(
        setup_identity=item.setup_identity,
        session_date=item.session_date,
        direction=item.direction,
        signal_known_at=item.signal_known_at,
        earliest_entry_timestamp=item.earliest_entry_timestamp,
        entry_status=(
            EntryStatus.AVAILABLE
            if available
            else EntryStatus.ENTRY_UNAVAILABLE_SESSION_END
        ),
        entry_reference_timestamp=item.earliest_entry_timestamp if available else None,
        entry_reference_price=Decimal("100") if available else None,
        entry_delay_minutes=0 if available else None,
    )
    if not available:
        return SetupOutcome(
            setup_identity=item.setup_identity,
            setup=item,
            entry_reference=reference,
        )
    horizons = tuple(
        SetupHorizonOutcome(
            horizon=name,
            requested_minutes=minutes,
            available_minutes=minutes,
            complete=True,
            mfe=Decimal(mfe),
            mae=Decimal("1"),
            mfe_timestamp=item.signal_known_at,
            mae_timestamp=item.signal_known_at,
        )
        for name, minutes in (
            ("5m", 5),
            ("15m", 15),
            ("30m", 30),
            ("60m", 60),
            ("EOD", 100),
        )
    )
    return SetupOutcome(
        setup_identity=item.setup_identity,
        setup=item,
        entry_reference=reference,
        five=horizons[0],
        fifteen=horizons[1],
        thirty=horizons[2],
        sixty=horizons[3],
        eod=horizons[4],
    )


def test_statistics_partitions_cross_tabs_and_base_all_are_deterministic() -> None:
    aligned = setup(identity="aligned")
    not_aligned = setup(
        SetupDirection.SHORT,
        identity="not",
        confirmation=CONFIRMATION + timedelta(minutes=5),
    )
    unavailable = setup(
        identity="unavailable",
        confirmation=CONFIRMATION + timedelta(minutes=10),
        executable=False,
    )
    setups = (aligned, not_aligned, unavailable)
    setup_result = BasePriceActionResult(
        start_date=SESSION,
        end_date=SESSION,
        seed_count=3,
        confirmed_count=3,
        non_confirmed_count=0,
        candidates=setups,
    )
    outcome_result = SetupOutcomeResult(
        start_date=SESSION,
        end_date=SESSION,
        confirmed_setup_count=3,
        available_entry_count=2,
        session_end_unavailable_count=1,
        missing_entry_count=0,
        outcomes=(
            outcome(aligned, "3"),
            outcome(not_aligned, "2"),
            outcome(unavailable, "1", available=False),
        ),
    )
    base = calculate_base_strategy_statistics(
        setup_result, outcome_result, development_session_count=1
    )
    vwap_annotations = (
        annotate_vwap_alignment(aligned, bar("101"), vwap("100")),
        annotate_vwap_alignment(
            not_aligned,
            bar("101", timestamp=not_aligned.confirmation_bar_timestamp),
            vwap("100", timestamp=not_aligned.confirmation_bar_timestamp),
        ),
        annotate_vwap_alignment(
            unavailable,
            bar("100", timestamp=unavailable.confirmation_bar_timestamp),
            None,
        ),
    )
    ema_annotations = tuple(
        EmaAlignmentAnnotation(
            setup_identity=item.setup_identity,
            session_date=item.session_date,
            direction=item.direction,
            confirmation_bar_timestamp=item.confirmation_bar_timestamp,
            signal_known_at=item.signal_known_at,
            ema9=None,
            ema20=None,
            alignment_state=EmaAlignmentState.EMA_UNAVAILABLE,
            indicator_timestamp=None,
            indicator_available=False,
        )
        for item in setups
    )
    cross_annotations = tuple(select_prior_ema_cross(item, ()) for item in setups)
    result = calculate_vwap_alignment_comparison(
        setup_result,
        outcome_result,
        base,
        vwap_annotations,
        ema_annotations,
        cross_annotations,
    )
    assert [item.annotation_n for item in result.groups] == [3, 1, 1, 1]
    assert [item.executable_n for item in result.groups] == [2, 1, 1, 0]
    assert result.groups[0].horizons == base.groups[0].horizons
    assert sum(item.annotation_n for item in result.ema_vwap_cross_tab) == 3
    assert sum(item.annotation_n for item in result.cross_context_vwap_cross_tab) == 3
    assert [item.distribution.n for item in result.distance_statistics] == [2, 1, 1]
    assert result.groups[-1].horizons[-1].mfe.median is None


def test_cli_command_is_offline_and_read_only(monkeypatch, tmp_path, capsys) -> None:
    sentinel = object()

    def mocked_calculate(self, *, start, end):
        assert start == end == SESSION
        return sentinel

    def mocked_print(result):
        assert result is sentinel
        print("vwap-comparison-pass")

    def reject_network(*args, **kwargs):
        raise AssertionError("VWAP comparison CLI must remain offline")

    monkeypatch.setattr(VwapAlignmentComparisonService, "calculate", mocked_calculate)
    monkeypatch.setattr(cli_module, "_print_vwap_alignment_comparison", mocked_print)
    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = cli_module.main(
        [
            "compare-vwap-alignment",
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
    assert captured.out == "vwap-comparison-pass\n"
    assert captured.err == ""
    assert list(tmp_path.iterdir()) == []
