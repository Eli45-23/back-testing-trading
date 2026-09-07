"""Immutable facts and signal-time context for opening-range research."""
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

Direction = Literal["LONG", "SHORT"]


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class KnownLevel(FrozenModel):
    name: str
    price: Decimal
    available_at: AwareDatetime

    @model_validator(mode="after")
    def finite_price(self):
        if not self.price.is_finite() or self.price <= 0:
            raise ValueError("known level price must be positive and finite")
        return self


class SignalContext(FrozenModel):
    known_levels: tuple[KnownLevel, ...]
    unavailable_levels: tuple[str, ...] = ()
    nearest_above: KnownLevel | None = None
    nearest_below: KnownLevel | None = None
    distance_above: Decimal | None = None
    distance_below: Decimal | None = None
    next_level: KnownLevel | None = None
    next_distance: Decimal | None = None
    next_inside: tuple[tuple[Decimal, bool | None], ...]
    distance_bucket: str
    time_bucket: str
    minutes_since_open: int
    day_of_week: str
    early_close: bool
    opening_range_size: Decimal
    first_boundary_so_far: Literal["ORH5", "ORL5", "AMBIGUOUS_SAME_MINUTE"]
    prior_break_attempts: int = Field(ge=0)
    prior_valid_holds: int = Field(ge=0)
    first_valid_hold: bool
    opposite_boundary_tested_earlier: bool


class HoldSignal(FrozenModel):
    event_id: str
    session_date: date
    direction: Direction
    entry_style: Literal["FIRST_HOLD", "STRONG_HOLD"]
    timestamp: AwareDatetime
    price: Decimal
    context: SignalContext

    @model_validator(mode="after")
    def signal_time_context(self):
        from zoneinfo import ZoneInfo
        if self.timestamp.astimezone(ZoneInfo("America/New_York")).date() != self.session_date:
            raise ValueError("signal timestamp must match session_date")
        if not self.price.is_finite() or self.price <= 0:
            raise ValueError("reference price must be positive and finite")
        if any(level.available_at > self.timestamp for level in self.context.known_levels):
            raise ValueError("future levels cannot enter signal context")
        return self


class BreakHoldEvent(FrozenModel):
    event_id: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    direction: Direction
    orh5: Decimal
    orl5: Decimal
    level_price: Decimal
    first_break_timestamp: AwareDatetime
    break_known_at: AwareDatetime
    break_candle_timestamp: AwareDatetime
    break_ohlc: tuple[Decimal, Decimal, Decimal, Decimal]
    timestamp_resolution: Literal["1Min_interval_start"] = "1Min_interval_start"
    first_hold: HoldSignal | None = None
    strong_hold: HoldSignal | None = None
    failed_break: bool = False
    failure_timestamp: AwareDatetime | None = None
    reclaim_timestamp: AwareDatetime | None = None
    reclaim_close: Decimal | None = None
    bars_break_to_first_hold: int | None = None
    bars_first_to_strong: int | None = None
    bars_first_to_reclaim: int | None = None
    state: Literal["BREAK_PENDING", "FIRST_HOLD_CONFIRMED", "STRONG_HOLD_CONFIRMED", "FAILED_BREAK", "RECLAIMED"] = "BREAK_PENDING"
    event_version: Literal["opening_break_hold_v1"] = "opening_break_hold_v1"
    timeframe: Literal["5Min"] = "5Min"
    session_mode: Literal["RTH_ONLY"] = "RTH_ONLY"

    @model_validator(mode="after")
    def chronology(self):
        if self.orh5 < self.orl5 or self.level_price != (self.orh5 if self.direction == "LONG" else self.orl5):
            raise ValueError("event level must match its opening boundary")
        if not self.break_candle_timestamp <= self.first_break_timestamp < self.break_known_at:
            raise ValueError("crossing minute must precede completed break candle")
        for signal, style in ((self.first_hold,"FIRST_HOLD"),(self.strong_hold,"STRONG_HOLD")):
            if signal and (signal.event_id != self.event_id or signal.direction != self.direction or signal.session_date != self.session_date or signal.entry_style != style):
                raise ValueError("signal identity must match event")
        if self.first_hold and self.first_hold.timestamp < self.break_known_at:
            raise ValueError("hold cannot precede completed break candle")
        if self.strong_hold and (self.first_hold is None or self.strong_hold.timestamp <= self.first_hold.timestamp):
            raise ValueError("strong confirmation must be later than first hold")
        if self.failed_break != (self.failure_timestamp is not None) or (self.failed_break and self.first_hold is not None):
            raise ValueError("immediate failure cannot be a first hold")
        if self.reclaim_timestamp is not None:
            if self.first_hold is None or self.reclaim_close is None or self.reclaim_timestamp <= self.first_hold.timestamp:
                raise ValueError("reclaim requires an earlier first hold")
            if self.strong_hold and self.strong_hold.timestamp >= self.reclaim_timestamp:
                raise ValueError("strong hold cannot occur after reclaim")
        return self


class SessionBreakFacts(FrozenModel):
    """Explicitly post-session facts; never attached as signal-time features."""
    session_date: date
    first_boundary: str | None
    both_sides_broken: bool
    events: tuple[BreakHoldEvent, ...]
