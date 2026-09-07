"""Causal, session-local state machine; no outcome calculations or persistence."""
from collections.abc import Sequence
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from spy_research.bars.models import FiveMinuteBar
from spy_research.data.schemas import RawBarRecord
from spy_research.events.break_and_hold_models import (
    BreakHoldEvent, Direction, HoldSignal, KnownLevel, SessionBreakFacts, SignalContext,
)
from spy_research.levels.opening_range import calculate_opening_five_minute_levels
from spy_research.market import XNYSCalendar

DISTANCES = tuple(map(Decimal, ("0.25", "0.50", "1.00", "1.50", "2.00")))


def level_context(levels: Sequence[KnownLevel], price: Decimal, direction: Direction,
                  known_at: datetime) -> dict[str, Any]:
    """Strict above/below; ties retained in known_levels in stable name order."""
    known = tuple(sorted((x for x in levels if x.available_at <= known_at), key=lambda x: (x.price, x.name)))
    above = next((x for x in known if x.price > price), None)
    below_prices = [x for x in known if x.price < price]
    below = min((x for x in below_prices if x.price == below_prices[-1].price), key=lambda x: x.name) if below_prices else None
    nxt = above if direction == "LONG" else below
    distance = abs(nxt.price - price) if nxt else None
    bucket = "UNAVAILABLE" if distance is None else next((f"<={d}" for d in DISTANCES if distance <= d), ">2.00")
    return dict(known_levels=known, nearest_above=above, nearest_below=below,
                distance_above=above.price-price if above else None,
                distance_below=price-below.price if below else None,
                next_level=nxt, next_distance=distance, distance_bucket=bucket,
                next_inside=tuple((d, distance <= d if distance is not None else None) for d in DISTANCES))


def time_bucket(timestamp: datetime) -> str:
    local = timestamp.astimezone(ZoneInfo("America/New_York"))
    minute = local.hour * 60 + local.minute
    for end, label in ((600, "09:35-10:00"), (630, "10:00-10:30"), (660, "10:30-11:00"),
                       (720, "11:00-12:00"), (810, "12:00-13:30"), (900, "13:30-15:00")):
        if minute < end:
            return label
    return "15:00-close"


def is_strong_hold(first_hold: HoldSignal | None, close: Decimal, level: Decimal,
                   direction: Direction) -> bool:
    """Provisional V1: the next uninterrupted outside close confirms strength."""
    return first_hold is not None and (close > level if direction == "LONG" else close < level)


def detect_break_holds(
    bars: Sequence[FiveMinuteBar], raw_minutes: Sequence[RawBarRecord], *,
    known_levels: Sequence[KnownLevel] = (), unavailable_levels: tuple[str, ...] = (),
    calendar: XNYSCalendar | None = None,
) -> SessionBreakFacts:
    calendar = calendar or XNYSCalendar()
    opening = calculate_opening_five_minute_levels(bars[:1], calendar=calendar)
    session = calendar.session_for_date(opening.session_date)
    assert session.market_open is not None and session.market_close is not None
    for i, bar in enumerate(bars):
        if bar.session_date != opening.session_date or bar.timestamp != session.market_open + timedelta(minutes=5*i) or bar.timestamp >= session.market_close:
            raise ValueError("break/hold requires consecutive, single-session RTH candles")
    stamps = [x.timestamp for x in raw_minutes]
    if stamps != sorted(set(stamps)):
        raise ValueError("raw timestamps must be ordered and unique")
    if any(x.timestamp.astimezone(ZoneInfo("America/New_York")).date() != opening.session_date for x in raw_minutes):
        raise ValueError("raw minutes cannot mix sessions")
    by_time = {x.timestamp: x for x in raw_minutes}
    levels = tuple(known_levels) + (
        KnownLevel(name="ORH5", price=opening.orh5, available_at=opening.available_from_timestamp),
        KnownLevel(name="ORL5", price=opening.orl5, available_at=opening.available_from_timestamp),
    )
    events: list[BreakHoldEvent] = []
    active: dict[str, int] = {}
    first_boundary = None
    prior_holds = 0
    tested_times: dict[str, datetime] = {}

    for i, bar in enumerate(bars[1:], 1):
        end = bar.timestamp + timedelta(minutes=5)
        minutes = tuple(by_time.get(bar.timestamp + timedelta(minutes=m)) for m in range(5))
        if any(x is None for x in minutes):
            raise ValueError("missing raw crossing-minute evidence")
        # Check OHLC agreement so crossing evidence cannot contradict detection.
        if (minutes[0].open, max(x.high for x in minutes), min(x.low for x in minutes), minutes[-1].close) != (bar.open, bar.high, bar.low, bar.close):
            raise ValueError("crossing minutes do not reconcile to five-minute candle")
        crossed = {}
        for direction, level in (("LONG", opening.orh5), ("SHORT", opening.orl5)):
            touched = next((x.timestamp for x in minutes if (x.high > level if direction == "LONG" else x.low < level)), None)
            tested = next((x.timestamp for x in minutes if (x.high >= level if direction == "LONG" else x.low <= level)), None)
            if tested is not None:
                tested_times.setdefault(direction, tested)
            if touched is not None:
                crossed[direction] = touched
        if first_boundary is None and crossed:
            earliest = min(crossed.values())
            winners = [d for d, t in crossed.items() if t == earliest]
            first_boundary = "AMBIGUOUS_SAME_MINUTE" if len(winners) == 2 else ("ORH5" if winners[0] == "LONG" else "ORL5")
        # New breaks ordered by minute, with stable identity for unknowable ties.
        new_directions = sorted((d for d in crossed if d not in active), key=lambda d: (crossed[d], d))
        for direction in new_directions:
            level = opening.orh5 if direction == "LONG" else opening.orl5
            active[direction] = len(events)
            events.append(BreakHoldEvent(
                event_id=f"SPY:{opening.session_date}:{direction}:{crossed[direction].isoformat()}:v1",
                session_date=opening.session_date, direction=direction, orh5=opening.orh5, orl5=opening.orl5,
                level_price=level, first_break_timestamp=crossed[direction], break_known_at=end,
                break_candle_timestamp=bar.timestamp, break_ohlc=(bar.open, bar.high, bar.low, bar.close)))
        holds_this_candle = 0
        for direction, index in tuple(active.items()):
            event = events[index]
            outside = bar.close > event.level_price if direction == "LONG" else bar.close < event.level_price
            changes = {}
            if outside and (event.first_hold is None or event.strong_hold is None):
                style = "FIRST_HOLD" if event.first_hold is None else "STRONG_HOLD"
                if style == "STRONG_HOLD" and not is_strong_hold(event.first_hold, bar.close, event.level_price, direction):
                    continue
                opposite = "SHORT" if direction == "LONG" else "LONG"
                context = SignalContext(
                    **level_context(levels, bar.close, direction, end), unavailable_levels=unavailable_levels,
                    time_bucket=time_bucket(end), minutes_since_open=int((end-session.market_open).total_seconds()/60),
                    day_of_week=opening.session_date.strftime("%A"), early_close=session.is_early_close,
                    opening_range_size=opening.orh5-opening.orl5, first_boundary_so_far=first_boundary,
                    prior_break_attempts=sum(x.first_break_timestamp < event.first_break_timestamp for x in events),
                    prior_valid_holds=prior_holds, first_valid_hold=prior_holds == 0,
                    opposite_boundary_tested_earlier=opposite in tested_times and tested_times[opposite] < event.first_break_timestamp)
                signal = HoldSignal(event_id=event.event_id, session_date=event.session_date,
                    direction=direction, entry_style=style, timestamp=end, price=bar.close, context=context)
                if style == "FIRST_HOLD":
                    changes = dict(first_hold=signal, bars_break_to_first_hold=int((bar.timestamp-event.break_candle_timestamp).total_seconds()/300), state="FIRST_HOLD_CONFIRMED")
                    holds_this_candle += 1
                else:
                    changes = dict(strong_hold=signal, bars_first_to_strong=int((end-event.first_hold.timestamp).total_seconds()/300), state="STRONG_HOLD_CONFIRMED")
            elif not outside:
                if event.first_hold is None:
                    changes = dict(failed_break=True, failure_timestamp=end, state="FAILED_BREAK")
                else:
                    changes = dict(reclaim_timestamp=end, reclaim_close=bar.close,
                        bars_first_to_reclaim=int((end-event.first_hold.timestamp).total_seconds()/300), state="RECLAIMED")
                # A completed close back across the relevant boundary rearms it.
                del active[direction]
            if changes:
                events[index] = BreakHoldEvent.model_validate(event.model_dump() | changes)
        prior_holds += holds_this_candle
    directions = {e.direction for e in events}
    return SessionBreakFacts(session_date=opening.session_date, first_boundary=first_boundary,
        both_sides_broken=len(directions) == 2, events=tuple(events))
