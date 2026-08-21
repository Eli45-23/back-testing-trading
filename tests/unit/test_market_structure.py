from __future__ import annotations

import inspect
import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

import spy_research.cli as cli_module
from spy_research.bars import FiveMinuteBar
from spy_research.interactions import (
    AvailableLevel,
    ImmediateState,
    InteractionType,
    LevelType,
    RetestState,
)
from spy_research.strategy import (
    BasePriceActionCandidate,
    BaseSetupStatus,
    ConfirmationType,
    SetupDirection,
)
from spy_research.strategy.comparisons import (
    CombinedStructureState,
    ConfirmedSwing,
    HighStructureState,
    LowStructureState,
    MarketStructureComparisonService,
    StructuralRoomState,
    StructureAgreementState,
    SwingType,
    annotate_market_structure,
    detect_confirmed_swings,
    select_room_to_next_level,
)


SESSION = date(2026, 8, 19)
OPEN = datetime(2026, 8, 19, 13, 30, tzinfo=UTC)


def bars(
    highs: list[str],
    lows: list[str] | None = None,
    *,
    start: datetime = OPEN,
) -> tuple[FiveMinuteBar, ...]:
    lows = lows or ["0"] * len(highs)
    result = []
    for index, (high_text, low_text) in enumerate(zip(highs, lows, strict=True)):
        high = Decimal(high_text)
        low = Decimal(low_text)
        close = (high + low) / 2
        timestamp = start + timedelta(minutes=5 * index)
        result.append(
            FiveMinuteBar(
                symbol="SPY",
                timestamp=timestamp,
                session_date=timestamp.date(),
                open=close,
                high=high,
                low=low,
                close=close,
                volume=100,
                trade_count=10,
                source="alpaca",
                feed="sip",
                timeframe="5Min",
                adjustment="raw",
                source_bar_count=5,
            )
        )
    return tuple(result)


def setup(
    *,
    direction: SetupDirection = SetupDirection.LONG,
    identity: str = "setup",
    confirmation: datetime = OPEN + timedelta(hours=2),
) -> BasePriceActionCandidate:
    signal = confirmation + timedelta(minutes=5)
    return BasePriceActionCandidate(
        setup_identity=identity,
        break_interaction_identity=f"break-{identity}",
        follow_through_identity=f"follow-{identity}",
        session_date=confirmation.date(),
        level_type=LevelType.ORL5,
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
        same_session_executable=True,
    )


def swing(
    swing_type: SwingType,
    price: str,
    pivot: datetime,
    *,
    session: date = SESSION,
) -> ConfirmedSwing:
    return ConfirmedSwing(
        session_date=session,
        pivot_timestamp=pivot,
        pivot_known_at=pivot + timedelta(minutes=15),
        swing_type=swing_type,
        swing_price=Decimal(price),
    )


def room(item: BasePriceActionCandidate, *, next_price: str | None = None):
    levels = ()
    if next_price is not None:
        levels = (
            AvailableLevel(
                session_date=item.session_date,
                level_type=LevelType.PDH,
                level_price=Decimal(next_price),
                available_from_timestamp=item.signal_known_at,
            ),
        )
    return select_room_to_next_level(
        item,
        confirmation_price=Decimal("100"),
        entry_price=None,
        atr14=Decimal("2"),
        levels=levels,
    )


def annotation(
    *,
    direction: SetupDirection = SetupDirection.LONG,
    high_prices: tuple[str, str] = ("101", "102"),
    low_prices: tuple[str, str] = ("95", "96"),
    atr: str | None = "2",
    next_price: str | None = None,
):
    item = setup(direction=direction)
    visible = (
        swing(SwingType.HIGH, high_prices[0], OPEN + timedelta(minutes=15)),
        swing(SwingType.LOW, low_prices[0], OPEN + timedelta(minutes=20)),
        swing(SwingType.HIGH, high_prices[1], OPEN + timedelta(minutes=30)),
        swing(SwingType.LOW, low_prices[1], OPEN + timedelta(minutes=35)),
    )
    return annotate_market_structure(
        item,
        confirmation_close=Decimal("100"),
        atr14=Decimal(atr) if atr is not None else None,
        swings=visible,
        room=room(item, next_price=next_price),
    )


def test_frozen_high_and_low_pivots_and_known_time() -> None:
    source = bars(
        ["10", "11", "14", "14", "13"],
        ["5", "4", "1", "1", "2"],
    )
    result = detect_confirmed_swings(source)
    assert tuple(item.swing_type for item in result) == (SwingType.HIGH, SwingType.LOW)
    assert {item.swing_price for item in result} == {Decimal("14"), Decimal("1")}
    assert all(item.pivot_timestamp == OPEN + timedelta(minutes=10) for item in result)
    assert all(item.pivot_known_at == OPEN + timedelta(minutes=25) for item in result)


def test_right_ties_are_accepted_but_left_ties_are_rejected() -> None:
    right_high = detect_confirmed_swings(bars(["1", "2", "5", "5", "5"]))
    assert any(item.swing_type is SwingType.HIGH for item in right_high)
    left_high = detect_confirmed_swings(bars(["1", "5", "5", "4", "3"]))
    assert not any(item.swing_type is SwingType.HIGH for item in left_high)
    right_low = detect_confirmed_swings(
        bars(["10"] * 5, ["5", "4", "1", "1", "1"])
    )
    assert any(item.swing_type is SwingType.LOW for item in right_low)
    left_low = detect_confirmed_swings(
        bars(["10"] * 5, ["5", "1", "1", "2", "3"])
    )
    assert not any(item.swing_type is SwingType.LOW for item in left_low)


def test_first_and_last_two_bars_cannot_be_pivots() -> None:
    source = bars(["9", "8", "1", "2", "8", "9"])
    assert detect_confirmed_swings(source) == ()


def test_changing_bars_after_required_right_window_cannot_change_pivot() -> None:
    first = detect_confirmed_swings(bars(["1", "2", "5", "4", "3", "2"]))
    second = detect_confirmed_swings(bars(["1", "2", "5", "4", "3", "999"]))
    target = OPEN + timedelta(minutes=10)
    assert tuple(item for item in first if item.pivot_timestamp == target) == tuple(
        item for item in second if item.pivot_timestamp == target
    )


@pytest.mark.parametrize("right_index", (3, 4))
def test_changing_either_required_right_bar_can_change_confirmation(
    right_index,
) -> None:
    confirmed = detect_confirmed_swings(bars(["1", "2", "5", "4", "3"]))
    changed = ["1", "2", "5", "4", "3"]
    changed[right_index] = "6"
    rejected = detect_confirmed_swings(bars(changed))
    target = OPEN + timedelta(minutes=10)
    assert any(
        item.swing_type is SwingType.HIGH and item.pivot_timestamp == target
        for item in confirmed
    )
    assert not any(
        item.swing_type is SwingType.HIGH and item.pivot_timestamp == target
        for item in rejected
    )


def test_detection_resets_at_session_boundary() -> None:
    first = bars(["1", "2", "9"], start=OPEN)
    second_open = datetime(2026, 8, 20, 13, 30, tzinfo=UTC)
    second = bars(["8", "7", "1"], start=second_open)
    assert detect_confirmed_swings(first + second) == ()


def test_future_confirmed_swing_is_invisible_before_t_plus_15() -> None:
    item = setup(confirmation=OPEN + timedelta(minutes=20))
    future = swing(SwingType.HIGH, "102", OPEN + timedelta(minutes=15))
    result = annotate_market_structure(
        item,
        confirmation_close=Decimal("100"),
        atr14=Decimal("2"),
        swings=(future,),
        room=room(item),
    )
    assert future.pivot_known_at > item.signal_known_at
    assert result.latest_confirmed_swing_high is None


def test_prior_and_next_session_swings_are_never_visible() -> None:
    item = setup()
    prior = swing(
        SwingType.HIGH,
        "101",
        OPEN - timedelta(days=1),
        session=SESSION - timedelta(days=1),
    )
    following = swing(
        SwingType.HIGH,
        "103",
        OPEN,
        session=SESSION + timedelta(days=1),
    )
    result = annotate_market_structure(
        item,
        confirmation_close=Decimal("100"),
        atr14=None,
        swings=(prior, following),
        room=room(item),
    )
    assert result.latest_confirmed_swing_high is None


@pytest.mark.parametrize(
    "highs,lows,expected_high,expected_low,expected_combined",
    (
        (
            ("101", "102"),
            ("95", "96"),
            HighStructureState.HIGHER_HIGH,
            LowStructureState.HIGHER_LOW,
            CombinedStructureState.BULLISH,
        ),
        (
            ("102", "101"),
            ("96", "95"),
            HighStructureState.LOWER_HIGH,
            LowStructureState.LOWER_LOW,
            CombinedStructureState.BEARISH,
        ),
        (
            ("101", "101"),
            ("95", "95"),
            HighStructureState.EQUAL_HIGH,
            LowStructureState.EQUAL_LOW,
            CombinedStructureState.MIXED,
        ),
        (
            ("101", "102"),
            ("96", "95"),
            HighStructureState.HIGHER_HIGH,
            LowStructureState.LOWER_LOW,
            CombinedStructureState.MIXED,
        ),
    ),
)
def test_high_low_and_combined_structure_classification(
    highs, lows, expected_high, expected_low, expected_combined
) -> None:
    result = annotation(high_prices=highs, low_prices=lows)
    assert result.high_structure is expected_high
    assert result.low_structure is expected_low
    assert result.combined_structure is expected_combined


def test_insufficient_history_is_unavailable() -> None:
    item = setup()
    result = annotate_market_structure(
        item,
        confirmation_close=Decimal("100"),
        atr14=Decimal("2"),
        swings=(swing(SwingType.HIGH, "102", OPEN + timedelta(minutes=15)),),
        room=room(item),
    )
    assert result.high_structure is HighStructureState.UNAVAILABLE
    assert result.low_structure is LowStructureState.UNAVAILABLE
    assert result.combined_structure is CombinedStructureState.UNAVAILABLE
    assert result.direction_agreement is StructureAgreementState.UNAVAILABLE


def test_direction_agreement_is_descriptive_only() -> None:
    long = annotation(direction=SetupDirection.LONG)
    short = annotation(direction=SetupDirection.SHORT)
    assert long.direction_agreement is StructureAgreementState.ALIGNED
    assert short.direction_agreement is StructureAgreementState.NOT_ALIGNED
    forbidden = {"qualified", "filter", "score", "target", "stop"}
    assert forbidden.isdisjoint(type(long).model_fields)


def test_decimal_distances_and_confirmation_atr_normalization() -> None:
    result = annotation()
    assert result.confirmation_close_to_latest_swing_high == Decimal("2")
    assert result.confirmation_close_to_latest_swing_low == Decimal("4")
    assert result.distance_to_swing_high_in_atr == Decimal("1")
    assert result.distance_to_swing_low_in_atr == Decimal("2")
    unavailable = annotation(atr=None)
    assert unavailable.distance_to_swing_high_in_atr is None
    assert unavailable.distance_to_swing_low_in_atr is None


def test_structural_room_context_does_not_change_objective_level() -> None:
    result = annotation(next_price="101")
    assert result.latest_confirmed_swing_high.swing_price == Decimal("102")
    assert (
        result.structural_room_state
        is StructuralRoomState.SWING_BEYOND_OBJECTIVE_LEVEL
    )
    open_ended = annotation(next_price=None)
    assert (
        open_ended.structural_room_state
        is StructuralRoomState.OBJECTIVE_LEVEL_OPEN_ENDED
    )


def test_outcomes_and_future_bars_are_not_classifier_inputs() -> None:
    assert tuple(inspect.signature(annotate_market_structure).parameters) == (
        "setup",
        "confirmation_close",
        "atr14",
        "swings",
        "room",
    )


def test_exactly_142_annotations_are_immutable_and_unique() -> None:
    results = tuple(
        annotate_market_structure(
            setup(identity=f"setup-{index:03}"),
            confirmation_close=Decimal("100"),
            atr14=Decimal("2"),
            swings=(),
            room=room(setup(identity=f"setup-{index:03}")),
        )
        for index in range(142)
    )
    assert len(results) == 142
    assert len({item.setup_identity for item in results}) == 142
    with pytest.raises(ValidationError):
        results[0].combined_structure = CombinedStructureState.BULLISH


def test_cli_is_offline_and_nonpersistent(monkeypatch, tmp_path, capsys) -> None:
    sentinel = object()

    def reject_network(*args, **kwargs):
        raise AssertionError("Stage 11.3 must remain offline")

    def mocked_calculate(self, *, start, end):
        assert start == end == SESSION
        return sentinel

    def mocked_print(result):
        assert result is sentinel
        print("market-structure-pass")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    monkeypatch.setattr(MarketStructureComparisonService, "calculate", mocked_calculate)
    monkeypatch.setattr(cli_module, "_print_market_structure_comparison", mocked_print)
    exit_code = cli_module.main(
        [
            "compare-market-structure",
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
    assert captured.out == "market-structure-pass\n"
    assert captured.err == ""
    assert list(tmp_path.iterdir()) == []
