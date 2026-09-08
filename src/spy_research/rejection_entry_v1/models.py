"""Immutable schemas for causal rejection-entry research records."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .protocol import (
    EntryFamily,
    LEVEL_FAMILIES,
    SignalStatus,
    completion_at,
    decimal,
    guard_outcome_date,
)

NY = ZoneInfo("America/New_York")


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def no_floats(cls, values):
        def visit(value):
            if isinstance(value, float):
                raise ValueError("binary float inputs prohibited")
            if isinstance(value, dict):
                for item in value.values():
                    visit(item)
            elif isinstance(value, (tuple, list)):
                for item in value:
                    visit(item)
        visit(values)
        return values

    @model_validator(mode="after")
    def valid_values(self):
        for name in type(self).model_fields:
            value = getattr(self, name)
            if isinstance(value, datetime) and value.utcoffset() is None:
                raise ValueError("aware timestamps required")
            if isinstance(value, Decimal) and not value.is_finite():
                raise ValueError("finite Decimal required")
        return self


class MinuteBar(Frozen):
    """A validated RTH minute whose timestamp is the interval start."""

    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    session_date: date

    @model_validator(mode="after")
    def valid_ohlc(self):
        if self.timestamp.second or self.timestamp.microsecond:
            raise ValueError("minute timestamps must be minute aligned")
        if self.timestamp.astimezone(NY).date() != self.session_date:
            raise ValueError("bar/session mismatch")
        if min(self.open, self.high, self.low, self.close) <= 0:
            raise ValueError("positive prices required")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("invalid high")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("invalid low")
        from .protocol import OUTCOME_END
        if self.session_date > OUTCOME_END:
            raise ValueError("bar after frozen outcome window")
        return self


class ConfirmationBar(Frozen):
    """Completed 1m/5m bar; ``timestamp`` remains its start."""

    timestamp: datetime
    timeframe_minutes: Literal[1, 5]
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    session_date: date

    @property
    def completes_at(self) -> datetime:
        return completion_at(self.timestamp, self.timeframe_minutes)

    @model_validator(mode="after")
    def valid_ohlc(self):
        if self.timestamp.second or self.timestamp.microsecond:
            raise ValueError("confirmation timestamps must be minute aligned")
        if self.timestamp.astimezone(NY).date() != self.session_date:
            raise ValueError("confirmation/session mismatch")
        if min(self.open, self.high, self.low, self.close) <= 0:
            raise ValueError("positive prices required")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("invalid high")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("invalid low")
        from .protocol import OUTCOME_END
        if self.session_date > OUTCOME_END:
            raise ValueError("confirmation after frozen outcome window")
        return self


class LevelInteraction(Frozen):
    """All eligible interactions, not a survivor-selected rejection cohort."""

    interaction_id: str
    session_date: date
    level_id: str
    level_family: str
    level_price: Decimal
    approach_side: Literal["ABOVE", "BELOW", "UNKNOWN"]
    first_touch_at: datetime
    episode_end_at: datetime
    touch_starts: tuple[datetime, ...] = ()
    retest_starts: tuple[datetime, ...] = ()
    first_interaction_since_creation: bool | None = None
    first_same_session_touch: bool | None = None
    prior_breach_count: int | None = None
    prior_close_through_count: int | None = None
    level_age_sessions: int | None = None
    confluence_bucket: str | None = None

    @model_validator(mode="after")
    def causal_window(self):
        guard_outcome_date(self.session_date)
        if self.level_family not in LEVEL_FAMILIES:
            raise ValueError("unknown frozen level family")
        if self.level_price <= 0:
            raise ValueError("level price must be positive")
        if not self.first_touch_at < self.episode_end_at:
            raise ValueError("interaction episode must be forward")
        if any(not self.first_touch_at < x < self.episode_end_at for x in self.retest_starts):
            raise ValueError("retest must be strictly inside episode")
        if self.touch_starts and self.touch_starts[0] != self.first_touch_at:
            raise ValueError("first touch identity mismatch")
        return self


class EntrySignal(Frozen):
    """Causal confirmation record; it contains no exit or performance result."""

    interaction_id: str
    session_date: date
    level_id: str
    level_family: str
    level_price: Decimal
    approach_side: Literal["ABOVE", "BELOW", "UNKNOWN"]
    entry_family: EntryFamily
    status: SignalStatus
    first_touch_at: datetime
    confirmation_start_at: datetime | None = None
    signal_known_at: datetime | None = None
    confirmation_timeframe_minutes: int | None = None
    delay_minutes: int | None = None
    displacement_from_level: Decimal | None = None
    executable_entry_timestamp: datetime | None = None
    executable_entry_price: Decimal | None = None
    entry_delay_minutes: int | None = None
    confirmation_bar_id: str | None = None

    @model_validator(mode="after")
    def timing(self):
        guard_outcome_date(self.session_date)
        if self.level_family not in LEVEL_FAMILIES or self.level_price <= 0:
            raise ValueError("unknown level family or invalid level price")
        if self.status is SignalStatus.CONFIRMED:
            if self.signal_known_at is None or self.confirmation_start_at is None:
                raise ValueError("confirmed signal needs completion and bar start")
            if self.signal_known_at <= self.confirmation_start_at:
                raise ValueError("signal is available only at bar completion")
            if self.confirmation_timeframe_minutes not in (1, 5):
                raise ValueError("confirmation timeframe required")
            if self.delay_minutes is not None and self.delay_minutes < 0:
                raise ValueError("negative confirmation delay")
        if self.executable_entry_timestamp is not None:
            if self.signal_known_at is None or self.executable_entry_timestamp < self.signal_known_at:
                raise ValueError("entry cannot precede signal availability")
        return self


class PathMeasurement(Frozen):
    """Descriptive path after the first executable minute; no R/P&L fields."""

    interaction_id: str
    entry_family: EntryFamily
    confirmation_timeframe_minutes: int | None
    signal_known_at: datetime
    entry_status: Literal["AVAILABLE", "SESSION_CLOSE", "MISSING"]
    entry_timestamp: datetime | None
    entry_price: Decimal | None
    observed_minutes: int
    censored_at_session_close: bool
    same_minute_ambiguity: bool
    mfe_from_level: Decimal | None
    mae_through_level: Decimal | None
    directional_close_excursion: Decimal | None
    fixed_distance_first_hits: tuple[tuple[str, datetime | None], ...]


class PairedComparison(Frozen):
    """Exact-identity wait-cost comparison; unavailable signals stay in denominator."""

    interaction_id: str
    left_family: EntryFamily
    right_family: EntryFamily
    left_timeframe_minutes: int | None = None
    right_timeframe_minutes: int | None = None
    left_status: SignalStatus
    right_status: SignalStatus
    delay_minutes: int | None
    entry_price_disadvantage: Decimal | None
    remaining_mfe_delta: Decimal | None
    mae_delta: Decimal | None
    paired: bool


class StudyManifest(Frozen):
    version: str
    protocol_hash: str
    klr_protocol_hash: str
    outcome_start: date
    outcome_end: date
    prospective_excluded_from: date
    level_families: tuple[str, ...]
    entry_families: tuple[EntryFamily, ...]
    source_files: tuple[str, ...]
    outcome_run_performed: bool = False

    @model_validator(mode="after")
    def frozen_scope(self):
        if self.outcome_start.isoformat() != "2026-01-02" or self.outcome_end.isoformat() != "2026-09-04":
            raise ValueError("unexpected outcome scope")
        if self.outcome_run_performed:
            raise ValueError("design freeze must not contain outcome run")
        return self
