"""Pure deterministic classification of completed candles against levels."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import timedelta
from decimal import Decimal

from spy_research.bars.models import FiveMinuteBar
from spy_research.interactions.models import (
    AvailableLevel,
    InteractionType,
    LevelInteraction,
    PriceSide,
)


class InteractionInputError(ValueError):
    """Candle/level inputs cannot form trustworthy interaction records."""


class LevelNotAvailableError(InteractionInputError):
    """A candle precedes the level's frozen availability timestamp."""


def price_side(value: Decimal, level: Decimal) -> PriceSide:
    if value > level:
        return PriceSide.ABOVE
    if value < level:
        return PriceSide.BELOW
    return PriceSide.EQUAL


def _validate_candle(candle: FiveMinuteBar) -> None:
    if (
        candle.symbol != "SPY"
        or candle.source != "alpaca"
        or candle.feed != "sip"
        or candle.source_timeframe != "1Min"
        or candle.timeframe != "5Min"
        or candle.adjustment != "raw"
        or candle.source_bar_count != 5
        or candle.session_type != "RTH"
        or candle.session_mode != "RTH_ONLY"
        or candle.aggregation_method != "rth_1m_to_5m_v1"
    ):
        raise InteractionInputError(
            "Interactions require self-built SPY RTH_ONLY 5Min candles"
        )


def validate_interaction_candle(candle: FiveMinuteBar) -> None:
    """Shared provenance gate for Stage 8 completed-candle calculations."""

    _validate_candle(candle)


def _interaction_type(
    *,
    open_side: PriceSide,
    close_side: PriceSide,
    range_encountered: bool,
    traded_above: bool,
    traded_below: bool,
) -> InteractionType:
    if not range_encountered:
        return InteractionType.NO_INTERACTION

    if close_side is PriceSide.ABOVE and open_side is not PriceSide.ABOVE:
        return InteractionType.CLOSE_THROUGH_ABOVE
    if close_side is PriceSide.BELOW and open_side is not PriceSide.BELOW:
        return InteractionType.CLOSE_THROUGH_BELOW

    if open_side is PriceSide.ABOVE and traded_below:
        return InteractionType.WICK_THROUGH_BELOW
    if open_side is PriceSide.BELOW and traded_above:
        return InteractionType.WICK_THROUGH_ABOVE

    if close_side is PriceSide.EQUAL:
        if open_side is not PriceSide.EQUAL:
            # The open-side checks above already captured a strict excursion
            # through the opposite side. Merely returning to equality is TOUCH.
            return InteractionType.TOUCH
        if traded_above and not traded_below:
            return InteractionType.WICK_THROUGH_ABOVE
        if traded_below and not traded_above:
            return InteractionType.WICK_THROUGH_BELOW
        if traded_above and traded_below:
            # A single primary type is required. Preserve both raw flags and use
            # deterministic ABOVE precedence only when open and close are equal.
            return InteractionType.WICK_THROUGH_ABOVE

    if close_side is PriceSide.ABOVE and traded_below:
        return InteractionType.WICK_THROUGH_BELOW
    if close_side is PriceSide.BELOW and traded_above:
        return InteractionType.WICK_THROUGH_ABOVE
    return InteractionType.TOUCH


def classify_level_interaction(
    candle: FiveMinuteBar,
    level: AvailableLevel,
    *,
    previous_candle: FiveMinuteBar | None = None,
) -> LevelInteraction:
    """Classify one completed candle using no future information."""

    _validate_candle(candle)
    if candle.session_date != level.session_date or candle.symbol != level.symbol:
        raise InteractionInputError("Candle and level must share symbol and session")
    if candle.timestamp < level.available_from_timestamp:
        raise LevelNotAvailableError(
            "Candle begins before the level is available for interaction"
        )
    if previous_candle is not None:
        _validate_candle(previous_candle)
        if (
            previous_candle.session_date != candle.session_date
            or previous_candle.timestamp >= candle.timestamp
        ):
            raise InteractionInputError(
                "Previous candle must be earlier in the same RTH session"
            )

    open_side = price_side(candle.open, level.level_price)
    close_side = price_side(candle.close, level.level_price)
    range_encountered = candle.low <= level.level_price <= candle.high
    traded_above = candle.high > level.level_price
    traded_below = candle.low < level.level_price
    previous_close = previous_candle.close if previous_candle is not None else None
    previous_side = (
        price_side(previous_close, level.level_price)
        if previous_close is not None
        else None
    )
    interaction_type = _interaction_type(
        open_side=open_side,
        close_side=close_side,
        range_encountered=range_encountered,
        traded_above=traded_above,
        traded_below=traded_below,
    )
    return LevelInteraction(
        session_date=candle.session_date,
        candle_timestamp=candle.timestamp,
        candle_completed_at=candle.timestamp + timedelta(minutes=5),
        level_type=level.level_type,
        level_price=level.level_price,
        level_available_from=level.available_from_timestamp,
        interaction_type=interaction_type,
        open=candle.open,
        high=candle.high,
        low=candle.low,
        close=candle.close,
        open_side=open_side,
        close_side=close_side,
        previous_close=previous_close,
        previous_close_side=previous_side,
        range_encountered=range_encountered,
        traded_above=traded_above,
        traded_below=traded_below,
        touched_level=range_encountered,
    )


def classify_session_level_interactions(
    candles: Sequence[FiveMinuteBar],
    levels: Sequence[AvailableLevel],
    *,
    emit_no_interaction: bool = False,
) -> tuple[LevelInteraction, ...]:
    """Validate one session and classify each availability-eligible pair."""

    if not candles:
        return ()
    session_date = candles[0].session_date
    previous_timestamp = None
    seen_timestamps = set()
    for candle in candles:
        _validate_candle(candle)
        if candle.session_date != session_date:
            raise InteractionInputError("Interaction input cannot mix sessions")
        if candle.timestamp in seen_timestamps:
            raise InteractionInputError("Duplicate five-minute timestamps are invalid")
        if previous_timestamp is not None and candle.timestamp < previous_timestamp:
            raise InteractionInputError("Candles must be strictly chronological")
        seen_timestamps.add(candle.timestamp)
        previous_timestamp = candle.timestamp
    for level in levels:
        if level.session_date != session_date:
            raise InteractionInputError("Level session does not match candle session")

    records = []
    previous = None
    for candle in candles:
        for level in levels:
            if candle.timestamp < level.available_from_timestamp:
                continue
            record = classify_level_interaction(
                candle,
                level,
                previous_candle=previous,
            )
            if emit_no_interaction or record.interaction_type is not InteractionType.NO_INTERACTION:
                records.append(record)
        previous = candle
    return tuple(records)
