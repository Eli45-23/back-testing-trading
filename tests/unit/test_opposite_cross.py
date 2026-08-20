from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from spy_research.events import EmaCrossDirection, EmaCrossEvent
from spy_research.outcomes import (
    EmaCrossOutcome,
    ExcursionResult,
    HorizonOutcome,
    OppositeCrossSequenceError,
    attach_next_opposite_cross,
)


DAY_ONE = date(2026, 8, 18)
DAY_TWO = date(2026, 8, 19)


def event(
    index: int,
    direction: EmaCrossDirection,
    *,
    session_date: date = DAY_TWO,
) -> EmaCrossEvent:
    timestamp = datetime(
        session_date.year, session_date.month, session_date.day, 13, 30, tzinfo=UTC
    ) + timedelta(minutes=5 * index)
    bullish = direction == EmaCrossDirection.BULLISH
    return EmaCrossEvent(
        symbol="SPY",
        timestamp=timestamp,
        session_date=session_date,
        direction=direction,
        reference_price=Decimal("100"),
        close=Decimal("100"),
        ema9=Decimal("101") if bullish else Decimal("99"),
        ema20=Decimal("100"),
        previous_ema9=Decimal("99") if bullish else Decimal("101"),
        previous_ema20=Decimal("100"),
        signed_separation=Decimal("1") if bullish else Decimal("-1"),
        absolute_separation=Decimal("1"),
        previous_signed_separation=Decimal("-1") if bullish else Decimal("1"),
        separation_delta_1=Decimal("2") if bullish else Decimal("-2"),
        separation_delta_2=None,
        separation_delta_3=None,
        vwap=Decimal("100"),
        close_minus_vwap=Decimal("0"),
        ema9_minus_vwap=Decimal("1") if bullish else Decimal("-1"),
        ema20_minus_vwap=Decimal("0"),
        atr14=Decimal("0.5"),
    )


def horizon(name: str, *, complete: bool = True) -> HorizonOutcome:
    return HorizonOutcome(
        horizon=name,
        requested_minutes=5,
        observed_minutes=5,
        complete=complete,
        excursion=ExcursionResult(
            mfe=Decimal("1.25"),
            mfe_timestamp=datetime(2026, 8, 19, 14, 0, tzinfo=UTC),
            mae=Decimal("0.75"),
            mae_timestamp=datetime(2026, 8, 19, 14, 1, tzinfo=UTC),
        ),
    )


def outcome(item: EmaCrossEvent) -> EmaCrossOutcome:
    return EmaCrossOutcome(
        event=item,
        symbol=item.symbol,
        session_date=item.session_date,
        event_timestamp=item.timestamp,
        reference_price=item.reference_price,
        outcome_start_timestamp=item.timestamp + timedelta(minutes=5),
        available_future_minutes=100,
        five=horizon("5m"),
        fifteen=horizon("15m"),
        thirty=horizon("30m"),
        sixty=horizon("60m", complete=False),
        eod=horizon("EOD"),
    )


@pytest.mark.parametrize(
    ("first_direction", "second_direction"),
    [
        (EmaCrossDirection.BULLISH, EmaCrossDirection.BEARISH),
        (EmaCrossDirection.BEARISH, EmaCrossDirection.BULLISH),
    ],
)
def test_opposite_directions_link_correctly(first_direction, second_direction) -> None:
    events = [event(0, first_direction), event(6, second_direction)]
    enriched = attach_next_opposite_cross(events, [outcome(item) for item in events])
    context = enriched[0].opposite_cross
    assert context.opposite_cross_timestamp == events[1].timestamp
    assert context.opposite_cross_direction == second_direction
    assert context.minutes_to_opposite_cross == 30
    assert context.bars_to_opposite_cross == 6


def test_final_event_has_no_opposite_context() -> None:
    item = event(0, EmaCrossDirection.BULLISH)
    context = attach_next_opposite_cross([item], [outcome(item)])[0].opposite_cross
    assert context.opposite_cross_timestamp is None
    assert context.opposite_cross_direction is None
    assert context.minutes_to_opposite_cross is None
    assert context.bars_to_opposite_cross is None


def test_lookup_never_links_to_next_session() -> None:
    first = event(0, EmaCrossDirection.BULLISH, session_date=DAY_ONE)
    second = event(0, EmaCrossDirection.BEARISH, session_date=DAY_TWO)
    enriched = attach_next_opposite_cross(
        [first, second], [outcome(first), outcome(second)]
    )
    assert enriched[0].opposite_cross.opposite_cross_timestamp is None


def test_adjacent_reversal_is_five_minutes_and_one_bar() -> None:
    events = [
        event(0, EmaCrossDirection.BULLISH),
        event(1, EmaCrossDirection.BEARISH),
    ]
    context = attach_next_opposite_cross(
        events, [outcome(item) for item in events]
    )[0].opposite_cross
    assert context.minutes_to_opposite_cross == 5
    assert context.bars_to_opposite_cross == 1


def test_first_later_opposite_is_selected_and_same_direction_is_ignored() -> None:
    events = [
        event(0, EmaCrossDirection.BULLISH),
        event(1, EmaCrossDirection.BULLISH),
        event(2, EmaCrossDirection.BEARISH),
        event(3, EmaCrossDirection.BEARISH),
    ]
    enriched = attach_next_opposite_cross(events, [outcome(item) for item in events])
    assert enriched[0].opposite_cross.opposite_cross_timestamp == events[2].timestamp
    assert enriched[0].opposite_cross.minutes_to_opposite_cross == 10


def test_event_identity_and_entire_stage51_outcome_are_preserved() -> None:
    events = [
        event(0, EmaCrossDirection.BULLISH),
        event(2, EmaCrossDirection.BEARISH),
    ]
    outcomes = [outcome(item) for item in events]
    before = [item.model_dump(mode="json") for item in outcomes]
    enriched = attach_next_opposite_cross(events, outcomes)
    assert tuple(item.outcome for item in enriched) == tuple(outcomes)
    assert [item.model_dump(mode="json") for item in outcomes] == before
    assert enriched[0].outcome.event == events[0]


def test_mfe_mae_extremes_counts_reference_start_and_flags_are_unchanged() -> None:
    events = [
        event(0, EmaCrossDirection.BULLISH),
        event(2, EmaCrossDirection.BEARISH),
    ]
    outcomes = [outcome(item) for item in events]
    enriched = attach_next_opposite_cross(events, outcomes)
    for base, item in zip(outcomes, enriched, strict=True):
        assert item.outcome.model_dump(mode="json") == base.model_dump(mode="json")
        assert item.outcome.reference_price == base.reference_price
        assert item.outcome.outcome_start_timestamp == base.outcome_start_timestamp
        assert item.outcome.available_future_minutes == base.available_future_minutes
        for field in ("five", "fifteen", "thirty", "sixty", "eod"):
            assert getattr(item.outcome, field) == getattr(base, field)


def test_duplicate_event_identity_is_rejected() -> None:
    item = event(0, EmaCrossDirection.BULLISH)
    with pytest.raises(OppositeCrossSequenceError, match="Duplicate"):
        attach_next_opposite_cross([item, item], [outcome(item), outcome(item)])


def test_out_of_order_events_are_rejected_without_sorting() -> None:
    first = event(0, EmaCrossDirection.BULLISH)
    second = event(1, EmaCrossDirection.BEARISH)
    with pytest.raises(OppositeCrossSequenceError, match="chronological"):
        attach_next_opposite_cross(
            [second, first], [outcome(second), outcome(first)]
        )


def test_event_outcome_identity_mismatch_is_rejected() -> None:
    first = event(0, EmaCrossDirection.BULLISH)
    second = event(1, EmaCrossDirection.BEARISH)
    with pytest.raises(OppositeCrossSequenceError, match="identity mismatch"):
        attach_next_opposite_cross([first], [outcome(second)])


def test_wrong_session_linkage_is_rejected() -> None:
    item = event(0, EmaCrossDirection.BULLISH)
    mismatched = outcome(item).model_copy(update={"session_date": DAY_ONE})
    with pytest.raises(OppositeCrossSequenceError, match="session linkage"):
        attach_next_opposite_cross([item], [mismatched])


def test_non_five_minute_opposite_interval_is_rejected() -> None:
    first = event(0, EmaCrossDirection.BULLISH)
    second = event(1, EmaCrossDirection.BEARISH).model_copy(
        update={"timestamp": first.timestamp + timedelta(minutes=7)}
    )
    with pytest.raises(OppositeCrossSequenceError, match="five-minute"):
        attach_next_opposite_cross([first, second], [outcome(first), outcome(second)])


def test_pure_enrichment_has_no_network_or_persistence(monkeypatch, tmp_path) -> None:
    def reject_network(*args, **kwargs):
        raise AssertionError("opposite-cross enrichment must remain offline")

    monkeypatch.setattr("socket.create_connection", reject_network)
    events = [
        event(0, EmaCrossDirection.BULLISH),
        event(1, EmaCrossDirection.BEARISH),
    ]
    attach_next_opposite_cross(events, [outcome(item) for item in events])
    assert list(tmp_path.iterdir()) == []
