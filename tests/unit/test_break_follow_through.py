from __future__ import annotations

import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from spy_research.bars.models import FiveMinuteBar
from spy_research.cli import main
from spy_research.interactions import (
    AvailableLevel,
    BreakFollowThroughResult,
    BreakFollowThroughService,
    FollowThroughInputError,
    ImmediateState,
    InteractionType,
    LevelType,
    PriceSide,
    RetestState,
    calculate_break_follow_through,
    classify_immediate_hold,
    classify_level_interaction,
    classify_retest,
)


SESSION = date(2026, 8, 19)
BREAK_TIME = datetime(2026, 8, 19, 14, 0, tzinfo=UTC)
LEVEL = Decimal("100")


def bar(
    offset: int,
    *,
    session_date: date = SESSION,
    open_price: str = "101",
    high: str = "102",
    low: str = "100.5",
    close: str = "101",
) -> FiveMinuteBar:
    return FiveMinuteBar(
        symbol="SPY",
        timestamp=BREAK_TIME + timedelta(minutes=5 * offset),
        session_date=session_date,
        open=Decimal(open_price),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal(close),
        volume=100,
        trade_count=10,
        source="alpaca",
        feed="sip",
        timeframe="5Min",
        adjustment="raw",
        source_bar_count=5,
    )


def seed(direction: PriceSide = PriceSide.ABOVE):
    definition = AvailableLevel(
        session_date=SESSION,
        level_type=LevelType.PDH,
        level_price=LEVEL,
        available_from_timestamp=BREAK_TIME,
    )
    if direction is PriceSide.ABOVE:
        break_bar = bar(
            0, open_price="99", high="102", low="98", close="101"
        )
    else:
        break_bar = bar(
            0, open_price="101", high="102", low="98", close="99"
        )
    return classify_level_interaction(break_bar, definition)


@pytest.mark.parametrize(
    ("direction", "close", "expected"),
    (
        (PriceSide.ABOVE, "101", ImmediateState.HOLD),
        (PriceSide.ABOVE, "99", ImmediateState.FAILURE),
        (PriceSide.ABOVE, "100", ImmediateState.EQUAL),
        (PriceSide.BELOW, "99", ImmediateState.HOLD),
        (PriceSide.BELOW, "101", ImmediateState.FAILURE),
        (PriceSide.BELOW, "100", ImmediateState.EQUAL),
    ),
)
def test_immediate_state_exact_close_semantics(direction, close, expected) -> None:
    next_bar = bar(1, open_price="100", high="102", low="98", close=close)
    result = classify_immediate_hold(direction, LEVEL, next_bar)
    assert result.state is expected
    assert result.close == Decimal(close)


def test_immediate_unavailable_without_next_bar() -> None:
    result = classify_immediate_hold(PriceSide.ABOVE, LEVEL, None)
    assert result.state is ImmediateState.UNAVAILABLE
    assert result.bar_timestamp is None


@pytest.mark.parametrize(
    ("direction", "high", "low", "close"),
    (
        (PriceSide.ABOVE, "102", "100", "101"),
        (PriceSide.ABOVE, "102", "99", "101"),
        (PriceSide.BELOW, "100", "98", "99"),
        (PriceSide.BELOW, "101", "98", "99"),
    ),
)
def test_exact_or_through_retest_that_closes_on_break_side_holds(
    direction, high, low, close
) -> None:
    result = classify_retest(
        direction,
        LEVEL,
        (bar(1, open_price="100", high=high, low=low, close=close),),
    )
    assert result.state is RetestState.RETEST_HOLD
    assert result.bar_offset == 1


@pytest.mark.parametrize(
    ("direction", "close"),
    ((PriceSide.ABOVE, "99"), (PriceSide.BELOW, "101")),
)
def test_retest_close_back_through_is_failure(direction, close) -> None:
    result = classify_retest(
        direction,
        LEVEL,
        (bar(1, open_price="100", high="102", low="98", close=close),),
    )
    assert result.state is RetestState.RETEST_FAILURE


@pytest.mark.parametrize("direction", (PriceSide.ABOVE, PriceSide.BELOW))
def test_retest_equal_is_neither_hold_nor_failure(direction) -> None:
    result = classify_retest(
        direction,
        LEVEL,
        (bar(1, open_price="100", high="102", low="98", close="100"),),
    )
    assert result.state is RetestState.RETEST_EQUAL


def test_first_qualifying_retest_can_be_bar_plus_two() -> None:
    result = classify_retest(
        PriceSide.ABOVE,
        LEVEL,
        (
            bar(1, open_price="102", high="103", low="101", close="102"),
            bar(2, open_price="101", high="102", low="100", close="101"),
            bar(3, open_price="101", high="102", low="99", close="99"),
        ),
    )
    assert result.state is RetestState.RETEST_HOLD
    assert result.bar_offset == 2


def test_first_qualifying_retest_can_be_bar_plus_three() -> None:
    result = classify_retest(
        PriceSide.ABOVE,
        LEVEL,
        (
            bar(1, open_price="102", high="103", low="101", close="102"),
            bar(2, open_price="102", high="103", low="101", close="102"),
            bar(3, open_price="102", high="103", low="99", close="101"),
        ),
    )
    assert result.state is RetestState.RETEST_HOLD
    assert result.bar_offset == 3


def test_first_failed_retest_is_not_relabelled_by_later_recovery() -> None:
    result = classify_retest(
        PriceSide.ABOVE,
        LEVEL,
        (
            bar(1, open_price="102", high="103", low="101", close="102"),
            bar(2, open_price="101", high="102", low="99", close="99"),
            bar(3, open_price="99", high="102", low="98", close="101"),
        ),
    )
    assert result.state is RetestState.RETEST_FAILURE
    assert result.bar_offset == 2


def test_first_hold_retest_is_not_changed_by_later_failure() -> None:
    result = classify_retest(
        PriceSide.ABOVE,
        LEVEL,
        (
            bar(1, open_price="101", high="102", low="100", close="101"),
            bar(2, open_price="101", high="102", low="99", close="99"),
        ),
    )
    assert result.state is RetestState.RETEST_HOLD
    assert result.bar_offset == 1


def test_no_encounter_in_three_bars_is_no_retest_not_failure() -> None:
    values = tuple(
        bar(offset, open_price="102", high="103", low="101", close="102")
        for offset in (1, 2, 3)
    )
    result = classify_retest(PriceSide.ABOVE, LEVEL, values)
    assert result.state is RetestState.NO_RETEST
    assert result.window_complete


@pytest.mark.parametrize("available", (1, 2))
def test_incomplete_window_reports_available_count(available) -> None:
    values = tuple(
        bar(offset, open_price="102", high="103", low="101", close="102")
        for offset in range(1, available + 1)
    )
    result = calculate_break_follow_through(seed(), values)
    assert result.retest.available_bars == available
    assert result.retest.requested_bars == 3
    assert not result.retest.window_complete
    assert result.retest.state is RetestState.NO_RETEST


def test_zero_future_bars_makes_both_states_unavailable() -> None:
    result = calculate_break_follow_through(seed(), ())
    assert result.immediate.state is ImmediateState.UNAVAILABLE
    assert result.retest.state is RetestState.UNAVAILABLE
    assert result.retest.available_bars == 0


def test_no_overnight_bridging() -> None:
    overnight = bar(
        1,
        open_price="101",
        high="102",
        low="100",
        close="101",
    ).model_copy(
        update={
            "session_date": date(2026, 8, 20),
            "timestamp": datetime(2026, 8, 20, 13, 30, tzinfo=UTC),
        }
    )
    with pytest.raises(FollowThroughInputError, match="bridge sessions"):
        calculate_break_follow_through(seed(), (overnight,))


def test_non_close_through_seed_is_rejected() -> None:
    definition = AvailableLevel(
        session_date=SESSION,
        level_type=LevelType.PDH,
        level_price=LEVEL,
        available_from_timestamp=BREAK_TIME,
    )
    touch = classify_level_interaction(
        bar(0, open_price="99", high="100", low="98", close="99"), definition
    )
    assert touch.interaction_type is InteractionType.TOUCH
    with pytest.raises(FollowThroughInputError, match="Only CLOSE_THROUGH"):
        calculate_break_follow_through(touch, ())


def test_duplicate_and_out_of_order_retest_timestamps_rejected() -> None:
    first = bar(1)
    with pytest.raises(FollowThroughInputError, match="Duplicate"):
        classify_retest(PriceSide.ABOVE, LEVEL, (first, first))
    with pytest.raises(FollowThroughInputError, match="chronological"):
        classify_retest(PriceSide.ABOVE, LEVEL, (bar(2), bar(1)))


@pytest.mark.parametrize(
    ("field", "value"),
    (("timeframe", "1Min"), ("session_mode", "ALL")),
)
def test_wrong_timeframe_or_session_mode_rejected(field, value) -> None:
    original = bar(1)
    wrong = FiveMinuteBar.model_construct(**{**original.model_dump(), field: value})
    with pytest.raises(FollowThroughInputError):
        calculate_break_follow_through(seed(), (wrong,))


def test_input_objects_are_immutable_and_unchanged() -> None:
    break_seed = seed()
    values = [bar(1), bar(2), bar(3)]
    before_seed = break_seed.model_dump()
    before_bars = [item.model_dump() for item in values]
    result = calculate_break_follow_through(break_seed, values)
    assert break_seed.model_dump() == before_seed
    assert [item.model_dump() for item in values] == before_bars
    assert result.break_interaction_identity.endswith("level-interaction-v1")


def test_bar_plus_four_and_later_cannot_change_result() -> None:
    first_three = (
        bar(1, open_price="102", high="103", low="101", close="102"),
        bar(2, open_price="102", high="103", low="101", close="102"),
        bar(3, open_price="102", high="103", low="101", close="102"),
    )
    prefix = calculate_break_follow_through(seed(), first_three)
    full = calculate_break_follow_through(
        seed(),
        (*first_three, bar(4, open_price="102", high="103", low="90", close="99")),
    )
    assert prefix == full


def test_pure_follow_through_is_offline_and_nonpersistent(monkeypatch, tmp_path) -> None:
    def reject_network(*args, **kwargs):
        raise AssertionError("follow-through calculation must remain offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    calculate_break_follow_through(seed(), (bar(1),))
    assert list(tmp_path.iterdir()) == []


def test_cli_is_offline_read_only_and_prints_follow_through(
    monkeypatch, tmp_path, capsys
) -> None:
    context = calculate_break_follow_through(seed(), (bar(1),))

    def mocked_calculate(self, *, start, end):
        return BreakFollowThroughResult(
            start_date=start,
            end_date=end,
            seed_count=1,
            follow_through=(context,),
        )

    def reject_network(*args, **kwargs):
        raise AssertionError("break-follow-through CLI must remain offline")

    monkeypatch.setattr(BreakFollowThroughService, "calculate", mocked_calculate)
    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "break-follow-through",
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
    assert "close-through seeds: 1" in captured.out
    assert "HOLD=1" in captured.out
    assert "RETEST_HOLD" in captured.out
    assert captured.err == ""
    assert list(tmp_path.iterdir()) == []
