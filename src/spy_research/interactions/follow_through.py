"""Bounded post-close-through hold and exact-price retest context."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import timedelta
from decimal import Decimal

from spy_research.bars.models import FiveMinuteBar
from spy_research.interactions.classifier import (
    InteractionInputError,
    price_side,
    validate_interaction_candle,
)
from spy_research.interactions.models import (
    BreakFollowThrough,
    ImmediateAssessment,
    ImmediateState,
    InteractionType,
    LevelInteraction,
    PriceSide,
    RetestAssessment,
    RetestState,
)


RETEST_WINDOW_BARS = 3


class FollowThroughInputError(InteractionInputError):
    """Break seed or bounded subsequent bars violate frozen Stage 8.2 scope."""


def _validate_follow_bar(bar: FiveMinuteBar) -> None:
    try:
        validate_interaction_candle(bar)
    except InteractionInputError as exc:
        raise FollowThroughInputError(str(exc)) from None


def _validate_direction(direction: PriceSide) -> None:
    if direction not in (PriceSide.ABOVE, PriceSide.BELOW):
        raise FollowThroughInputError("Break direction must be ABOVE or BELOW")


def classify_immediate_hold(
    break_direction: PriceSide,
    level_price: Decimal,
    next_bar: FiveMinuteBar | None,
) -> ImmediateAssessment:
    """Classify exactly one next completed candle by its exact close side."""

    _validate_direction(break_direction)
    if next_bar is None:
        return ImmediateAssessment(
            state=ImmediateState.UNAVAILABLE,
            bar_timestamp=None,
            close=None,
            close_side=None,
        )
    _validate_follow_bar(next_bar)
    side = price_side(next_bar.close, level_price)
    if side is PriceSide.EQUAL:
        state = ImmediateState.EQUAL
    elif side is break_direction:
        state = ImmediateState.HOLD
    else:
        state = ImmediateState.FAILURE
    return ImmediateAssessment(
        state=state,
        bar_timestamp=next_bar.timestamp,
        close=next_bar.close,
        close_side=side,
    )


def classify_retest(
    break_direction: PriceSide,
    level_price: Decimal,
    subsequent_bars: Sequence[FiveMinuteBar],
) -> RetestAssessment:
    """Use the first encounter in bars +1 through +3, never later."""

    _validate_direction(break_direction)
    selected = tuple(subsequent_bars[:RETEST_WINDOW_BARS])
    session_date = selected[0].session_date if selected else None
    previous_timestamp = None
    seen_timestamps = set()
    for bar in selected:
        _validate_follow_bar(bar)
        if bar.session_date != session_date:
            raise FollowThroughInputError("Retest input cannot mix sessions")
        if bar.timestamp in seen_timestamps:
            raise FollowThroughInputError("Duplicate retest timestamp")
        if previous_timestamp is not None and bar.timestamp < previous_timestamp:
            raise FollowThroughInputError(
                "Retest bars must be strictly chronological"
            )
        seen_timestamps.add(bar.timestamp)
        previous_timestamp = bar.timestamp
    available = len(selected)
    complete = available == RETEST_WINDOW_BARS
    if not selected:
        return RetestAssessment(
            state=RetestState.UNAVAILABLE,
            requested_bars=RETEST_WINDOW_BARS,
            available_bars=0,
            window_complete=False,
        )

    for offset, bar in enumerate(selected, start=1):
        encountered = (
            bar.low <= level_price
            if break_direction is PriceSide.ABOVE
            else bar.high >= level_price
        )
        if not encountered:
            continue
        side = price_side(bar.close, level_price)
        if side is PriceSide.EQUAL:
            state = RetestState.RETEST_EQUAL
        elif side is break_direction:
            state = RetestState.RETEST_HOLD
        else:
            state = RetestState.RETEST_FAILURE
        return RetestAssessment(
            state=state,
            bar_offset=offset,
            timestamp=bar.timestamp,
            open=bar.open,
            high=bar.high,
            low=bar.low,
            close=bar.close,
            requested_bars=RETEST_WINDOW_BARS,
            available_bars=available,
            window_complete=complete,
        )
    return RetestAssessment(
        state=RetestState.NO_RETEST,
        requested_bars=RETEST_WINDOW_BARS,
        available_bars=available,
        window_complete=complete,
    )


def _break_direction(seed: LevelInteraction) -> PriceSide:
    if seed.interaction_type is InteractionType.CLOSE_THROUGH_ABOVE:
        return PriceSide.ABOVE
    if seed.interaction_type is InteractionType.CLOSE_THROUGH_BELOW:
        return PriceSide.BELOW
    raise FollowThroughInputError(
        "Only CLOSE_THROUGH_ABOVE or CLOSE_THROUGH_BELOW may seed follow-through"
    )


def calculate_break_follow_through(
    seed: LevelInteraction,
    subsequent_bars: Sequence[FiveMinuteBar],
) -> BreakFollowThrough:
    """Calculate context from at most same-session bars +1 through +3."""

    direction = _break_direction(seed)
    selected = tuple(subsequent_bars[:RETEST_WINDOW_BARS])
    previous_timestamp = seed.candle_timestamp
    for bar in selected:
        _validate_follow_bar(bar)
        if bar.session_date != seed.session_date:
            raise FollowThroughInputError("Follow-through cannot bridge sessions")
        if bar.timestamp <= previous_timestamp:
            if bar.timestamp == previous_timestamp:
                raise FollowThroughInputError("Duplicate future timestamp")
            raise FollowThroughInputError("Future bars must be strictly chronological")
        if bar.timestamp != previous_timestamp + timedelta(minutes=5):
            raise FollowThroughInputError(
                "Follow-through bars must be consecutive five-minute candles"
            )
        previous_timestamp = bar.timestamp

    immediate = classify_immediate_hold(
        direction,
        seed.level_price,
        selected[0] if selected else None,
    )
    retest = classify_retest(direction, seed.level_price, selected)
    identity = (
        f"{seed.symbol}|{seed.session_date.isoformat()}|"
        f"{seed.candle_timestamp.isoformat()}|{seed.level_type.value}|"
        f"{seed.interaction_type.value}|{seed.interaction_version}"
    )
    return BreakFollowThrough(
        break_interaction_identity=identity,
        session_date=seed.session_date,
        level_type=seed.level_type,
        level_price=seed.level_price,
        break_timestamp=seed.candle_timestamp,
        break_completed_at=seed.candle_completed_at,
        break_interaction_type=seed.interaction_type,
        break_direction=direction,
        immediate=immediate,
        retest=retest,
    )
