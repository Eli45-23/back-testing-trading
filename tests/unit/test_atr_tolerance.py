from __future__ import annotations

import inspect
import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest

from spy_research.interactions import (
    ATR_TOLERANCE_FRACTION,
    AtrToleranceInputError,
    AtrToleranceResult,
    AtrToleranceService,
    BreakFollowThrough,
    BreakFollowThroughResult,
    ImmediateAssessment,
    ImmediateState,
    InteractionType,
    LevelType,
    PriceSide,
    RetestAssessment,
    RetestState,
    TolerantImmediateState,
    TolerantRetestState,
    calculate_atr_tolerance_follow_through,
    calculate_tolerance_amount,
    calculate_tolerance_boundary,
    classify_tolerant_immediate,
    classify_tolerant_retest,
)
from spy_research.cli import main


SESSION = date(2026, 8, 19)
BREAK_TIME = datetime(2026, 8, 19, 14, 35, tzinfo=UTC)
LEVEL = Decimal("100.000000000000")
ATR = Decimal("0.600000000000")


def exact_result(
    direction: PriceSide = PriceSide.ABOVE,
    *,
    immediate_state: ImmediateState = ImmediateState.FAILURE,
    immediate_close: Decimal | None = Decimal("99.970000000000"),
    retest_state: RetestState = RetestState.RETEST_FAILURE,
    retest_close: Decimal | None = Decimal("99.970000000000"),
    retest_offset: int | None = 2,
) -> BreakFollowThrough:
    unavailable_immediate = immediate_state is ImmediateState.UNAVAILABLE
    unavailable_retest = retest_state in {
        RetestState.NO_RETEST,
        RetestState.UNAVAILABLE,
    }
    return BreakFollowThrough(
        break_interaction_identity="SPY|2026-08-19|seed|level-interaction-v1",
        session_date=SESSION,
        level_type=LevelType.PDH,
        level_price=LEVEL,
        break_timestamp=BREAK_TIME,
        break_completed_at=BREAK_TIME + timedelta(minutes=5),
        break_interaction_type=(
            InteractionType.CLOSE_THROUGH_ABOVE
            if direction is PriceSide.ABOVE
            else InteractionType.CLOSE_THROUGH_BELOW
        ),
        break_direction=direction,
        immediate=ImmediateAssessment(
            state=immediate_state,
            bar_timestamp=(
                None if unavailable_immediate else BREAK_TIME + timedelta(minutes=5)
            ),
            close=None if unavailable_immediate else immediate_close,
            close_side=None,
        ),
        retest=RetestAssessment(
            state=retest_state,
            bar_offset=None if unavailable_retest else retest_offset,
            timestamp=(
                None
                if unavailable_retest
                else BREAK_TIME + timedelta(minutes=5 * (retest_offset or 1))
            ),
            open=None if unavailable_retest else LEVEL,
            high=None if unavailable_retest else LEVEL + Decimal("0.1"),
            low=None if unavailable_retest else LEVEL - Decimal("0.1"),
            close=None if unavailable_retest else retest_close,
            requested_bars=3,
            available_bars=(0 if retest_state is RetestState.UNAVAILABLE else 3),
            window_complete=retest_state is not RetestState.UNAVAILABLE,
        ),
    )


def test_tolerance_fraction_amount_boundaries_and_precision() -> None:
    assert ATR_TOLERANCE_FRACTION == Decimal("0.10")
    assert calculate_tolerance_amount(ATR) == Decimal("0.0600000000000")
    assert calculate_tolerance_boundary(PriceSide.ABOVE, LEVEL, ATR) == Decimal(
        "99.9400000000000"
    )
    assert calculate_tolerance_boundary(PriceSide.BELOW, LEVEL, ATR) == Decimal(
        "100.0600000000000"
    )


@pytest.mark.parametrize(
    ("close", "expected"),
    (
        (Decimal("100.01"), TolerantImmediateState.HOLD_EXACT),
        (Decimal("100"), TolerantImmediateState.HOLD_WITHIN_TOLERANCE),
        (Decimal("99.97"), TolerantImmediateState.HOLD_WITHIN_TOLERANCE),
        (Decimal("99.94"), TolerantImmediateState.HOLD_WITHIN_TOLERANCE),
        (Decimal("99.9399"), TolerantImmediateState.FAILURE),
    ),
)
def test_bullish_immediate_boundaries(close, expected) -> None:
    assert classify_tolerant_immediate(PriceSide.ABOVE, LEVEL, ATR, close) is expected


@pytest.mark.parametrize(
    ("close", "expected"),
    (
        (Decimal("99.99"), TolerantImmediateState.HOLD_EXACT),
        (Decimal("100"), TolerantImmediateState.HOLD_WITHIN_TOLERANCE),
        (Decimal("100.03"), TolerantImmediateState.HOLD_WITHIN_TOLERANCE),
        (Decimal("100.06"), TolerantImmediateState.HOLD_WITHIN_TOLERANCE),
        (Decimal("100.0601"), TolerantImmediateState.FAILURE),
    ),
)
def test_bearish_immediate_boundaries(close, expected) -> None:
    assert classify_tolerant_immediate(PriceSide.BELOW, LEVEL, ATR, close) is expected


@pytest.mark.parametrize(
    ("direction", "exact_state", "close", "expected"),
    (
        (
            PriceSide.ABOVE,
            RetestState.RETEST_HOLD,
            Decimal("100.01"),
            TolerantRetestState.RETEST_HOLD_EXACT,
        ),
        (
            PriceSide.ABOVE,
            RetestState.RETEST_FAILURE,
            Decimal("99.97"),
            TolerantRetestState.RETEST_HOLD_WITHIN_TOLERANCE,
        ),
        (
            PriceSide.ABOVE,
            RetestState.RETEST_FAILURE,
            Decimal("99.93"),
            TolerantRetestState.RETEST_FAILURE,
        ),
        (
            PriceSide.BELOW,
            RetestState.RETEST_FAILURE,
            Decimal("100.03"),
            TolerantRetestState.RETEST_HOLD_WITHIN_TOLERANCE,
        ),
        (
            PriceSide.BELOW,
            RetestState.RETEST_FAILURE,
            Decimal("100.07"),
            TolerantRetestState.RETEST_FAILURE,
        ),
        (
            PriceSide.ABOVE,
            RetestState.RETEST_EQUAL,
            Decimal("100"),
            TolerantRetestState.RETEST_HOLD_WITHIN_TOLERANCE,
        ),
    ),
)
def test_tolerant_retest_interprets_same_selected_close(
    direction, exact_state, close, expected
) -> None:
    assert (
        classify_tolerant_retest(direction, LEVEL, ATR, exact_state, close)
        is expected
    )


def test_no_retest_remains_no_retest_when_atr_exists() -> None:
    assert (
        classify_tolerant_retest(
            PriceSide.ABOVE,
            LEVEL,
            ATR,
            RetestState.NO_RETEST,
            None,
        )
        is TolerantRetestState.NO_RETEST
    )


def test_pre_atr_seed_is_explicitly_unavailable_without_fallback() -> None:
    result = calculate_atr_tolerance_follow_through(exact_result(), None)
    assert not result.atr_available
    assert result.event_atr is None
    assert result.tolerance_amount is None
    assert result.tolerance_boundary is None
    assert result.tolerant_immediate_state is TolerantImmediateState.UNAVAILABLE_ATR
    assert result.tolerant_retest_state is TolerantRetestState.UNAVAILABLE_ATR


def test_no_future_bar_precedes_atr_unavailability() -> None:
    exact = exact_result(
        immediate_state=ImmediateState.UNAVAILABLE,
        immediate_close=None,
        retest_state=RetestState.UNAVAILABLE,
        retest_close=None,
        retest_offset=None,
    )
    result = calculate_atr_tolerance_follow_through(exact, None)
    assert result.tolerant_immediate_state is TolerantImmediateState.UNAVAILABLE
    assert result.tolerant_retest_state is TolerantRetestState.UNAVAILABLE


def test_failure_reclassification_records_penetration_and_ratio() -> None:
    result = calculate_atr_tolerance_follow_through(exact_result(), ATR)
    assert result.immediate_reclassified
    assert result.retest_reclassified
    assert result.immediate_penetration == Decimal("0.030000000000")
    assert result.immediate_penetration_as_atr == Decimal("0.05")
    assert result.retest_penetration == Decimal("0.030000000000")
    assert result.retest_penetration_as_atr == Decimal("0.05")


def test_exact_hold_remains_exact_and_is_not_marked_reclassified() -> None:
    exact = exact_result(
        immediate_state=ImmediateState.HOLD,
        immediate_close=Decimal("100.01"),
        retest_state=RetestState.RETEST_HOLD,
        retest_close=Decimal("100.02"),
    )
    result = calculate_atr_tolerance_follow_through(exact, ATR)
    assert result.tolerant_immediate_state is TolerantImmediateState.HOLD_EXACT
    assert result.tolerant_retest_state is TolerantRetestState.RETEST_HOLD_EXACT
    assert not result.immediate_reclassified
    assert not result.retest_reclassified


def test_exact_retest_identity_and_input_are_preserved() -> None:
    exact = exact_result()
    before = exact.model_dump()
    result = calculate_atr_tolerance_follow_through(exact, ATR)
    assert exact.model_dump() == before
    assert result.break_interaction_identity == exact.break_interaction_identity
    assert result.retest_timestamp == exact.retest.timestamp
    assert result.retest_bar_offset == exact.retest.bar_offset
    assert result.available_retest_bars == exact.retest.available_bars
    assert result.retest_window_complete == exact.retest.window_complete


def test_zero_lookahead_signature_and_later_data_cannot_change_result() -> None:
    exact = exact_result()
    assert tuple(inspect.signature(calculate_atr_tolerance_follow_through).parameters) == (
        "exact",
        "event_atr",
    )
    prefix = calculate_atr_tolerance_follow_through(exact, ATR)
    unrelated_later_atr = Decimal("9.99")
    unrelated_bar_four_close = Decimal("90")
    assert unrelated_later_atr and unrelated_bar_four_close
    full_session = calculate_atr_tolerance_follow_through(exact, ATR)
    assert prefix == full_session


def test_service_joins_only_break_timestamp_atr() -> None:
    exact = exact_result()
    service = object.__new__(AtrToleranceService)
    service._follow_through = SimpleNamespace(
        calculate=lambda **kwargs: BreakFollowThroughResult(
            start_date=SESSION,
            end_date=SESSION,
            seed_count=1,
            follow_through=(exact,),
        )
    )
    service._atr = SimpleNamespace(
        calculate=lambda **kwargs: SimpleNamespace(
            rows=(
                SimpleNamespace(timestamp=BREAK_TIME, atr14=ATR),
                SimpleNamespace(
                    timestamp=BREAK_TIME + timedelta(minutes=5),
                    atr14=Decimal("9.99"),
                ),
            )
        )
    )
    result = service.calculate(start=SESSION, end=SESSION)
    assert result.comparisons[0].event_atr == ATR
    assert result.comparisons[0].tolerance_amount == Decimal("0.0600000000000")


def test_invalid_or_zero_atr_is_rejected() -> None:
    with pytest.raises(AtrToleranceInputError):
        calculate_tolerance_amount(Decimal("0"))


def test_pure_tolerance_logic_is_offline_and_nonpersistent(monkeypatch, tmp_path) -> None:
    def reject_network(*args, **kwargs):
        raise AssertionError("ATR tolerance calculation must remain offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    calculate_atr_tolerance_follow_through(exact_result(), ATR)
    assert list(tmp_path.iterdir()) == []


def test_cli_is_offline_read_only_and_reports_parallel_comparison(
    monkeypatch, tmp_path, capsys
) -> None:
    comparison = calculate_atr_tolerance_follow_through(exact_result(), ATR)

    def mocked_calculate(self, *, start, end):
        return AtrToleranceResult(
            start_date=start,
            end_date=end,
            seed_count=1,
            atr_available_count=1,
            atr_unavailable_count=0,
            comparisons=(comparison,),
        )

    def reject_network(*args, **kwargs):
        raise AssertionError("atr-tolerance CLI must remain offline")

    monkeypatch.setattr(AtrToleranceService, "calculate", mocked_calculate)
    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "atr-tolerance",
            "--start",
            "2026-08-19",
            "--end",
            "2026-08-19",
            "--raw-data-root",
            str(tmp_path / "raw"),
            "--processed-data-root",
            str(tmp_path / "processed"),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "seeds: 1" in captured.out
    assert "FAILURE -> HOLD_WITHIN_TOLERANCE: 1" in captured.out
    assert captured.err == ""
    assert list(tmp_path.iterdir()) == []
