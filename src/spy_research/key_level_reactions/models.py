"""Immutable auditable input and output records; Decimal JSON uses strings."""
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator
from spy_research.data.schemas import RawBarRecord

Family = Literal["PDH", "PDL", "PMH", "PML", "ORH5", "ORL5", "PWH", "PWL", "1H_HIGH", "1H_LOW"]


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def no_floats(cls, values):
        def visit(v):
            if isinstance(v, float):
                raise ValueError("Binary float inputs prohibited")
            if isinstance(v, dict):
                for item in v.values():
                    visit(item)
            elif isinstance(v, (tuple, list)):
                for item in v:
                    visit(item)
        visit(values)
        return values

    @model_validator(mode="after")
    def aware(self):
        for name in type(self).model_fields:
            value = getattr(self, name)
            if isinstance(value, datetime) and value.utcoffset() is None:
                raise ValueError("Aware timestamps required")
            if isinstance(value, Decimal) and not value.is_finite():
                raise ValueError("Finite Decimal required")
        return self


class Level(Frozen):
    id: str
    family: Family
    role: Literal["RESISTANCE", "SUPPORT"]
    price: Decimal
    source_timeframe: Literal["1Min", "5Min", "1H_RTH_FULL_BARS"]
    source_ids: tuple[str, ...]
    source_start_at: datetime
    source_end_at: datetime
    created_at: datetime
    available_at: datetime
    expires_at: datetime | None = None
    pivot_bar_start_at: datetime | None = None
    static: bool = True

    @model_validator(mode="after")
    def causal(self):
        if not self.source_start_at < self.source_end_at <= self.created_at <= self.available_at:
            raise ValueError("Noncausal level provenance")
        if self.expires_at is not None and self.expires_at <= self.available_at:
            raise ValueError("Invalid expiration")
        expected = "RESISTANCE" if self.family in ("PDH", "PMH", "ORH5", "PWH", "1H_HIGH") else "SUPPORT"
        if self.role != expected or self.price <= 0:
            raise ValueError("Invalid level role/price")
        if not self.source_ids:
            raise ValueError("Source identities required")
        return self


class Hour(Frozen):
    id: str
    start: datetime
    end: datetime
    high: Decimal
    low: Decimal
    source_ids: tuple[str, ...]

    @model_validator(mode="after")
    def complete_hour(self):
        if self.end-self.start != timedelta(hours=1) or self.low <= 0 or self.high < self.low:
            raise ValueError("Invalid full hour")
        return self


class Coverage(Frozen):
    session: date
    expected: int
    observed: int
    status: str
    premarket_status: str
    warning_codes: tuple[str, ...] = ()


class InputData(Frozen):
    context_start: date
    outcome_start: date
    end: date
    bars: tuple[RawBarRecord, ...]
    coverage: tuple[Coverage, ...]


class AvailabilityIssue(Frozen):
    session: date
    families: tuple[Family, ...]
    reason: str


class LevelSet(Frozen):
    levels: tuple[Level, ...]
    issues: tuple[AvailabilityIssue, ...]
    pivot_audits: tuple["PivotAudit", ...] = ()


class PivotAudit(Frozen):
    pivot_start: datetime
    known_at: datetime
    role: Literal["HIGH", "LOW"]
    status: Literal["CONFIRMED", "EQUAL_EXTREMA", "NOT_STRICT_EXTREMUM"]
    source_ids: tuple[str, ...]


LevelSet.model_rebuild()


class Touch(Frozen):
    id: str
    level_id: str
    start: datetime
    known_at: datetime
    approach: Literal["ABOVE", "BELOW", "UNKNOWN"]
    session_touch_number: int | None
    lifetime_touch_number: int | None
    time_since_previous_touch: int | None
    prior_lifetime_interactions: int | None
    prior_same_session_interactions: int | None
    first_interaction_since_creation: bool | None
    prior_breach_count: int | None
    prior_breach_minute_count: int | None
    prior_close_through_count: int | None
    previously_closed_through: bool | None
    first_breach_known_at: datetime | None
    last_breach_known_at: datetime | None
    last_touch_known_at: datetime | None
    level_age_sessions: int
    history_start_at: datetime
    history_complete_since_creation: bool
    touch_run_number: int
    episode_id: str | None
    continuous_contact: bool
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    prior_price_breached: bool | None
    observed_lifetime_touch_number: int
    observed_session_touch_number: int
    observed_prior_breach_count: int
    observed_prior_breach_minute_count: int
    observed_prior_close_through_count: int
    session_history_complete: bool


class Episode(Frozen):
    id: str
    level_id: str
    start: datetime
    end: datetime
    approach: Literal["ABOVE", "BELOW", "UNKNOWN"]
    touch_ids: tuple[str, ...]
    retest_starts: tuple[datetime, ...]

    @model_validator(mode="after")
    def window(self):
        from spy_research.market import XNYSCalendar
        from .protocol import NY
        session = XNYSCalendar().session_for_date(self.start.astimezone(NY).date())
        if not session.is_trading_day or not session.market_open <= self.start < session.market_close:
            raise ValueError("Episode outside RTH")
        if self.end != min(self.start+timedelta(minutes=30), session.market_close):
            raise ValueError("Episode must end at fixed horizon or session close")
        if any(not self.start < t < self.end for t in self.retest_starts):
            raise ValueError("Retest outside episode")
        return self


class Reaction(Frozen):
    episode_id: str
    distance: Decimal
    horizon: int
    status: Literal["REJECTION_FIRST", "CONTINUATION_FIRST", "AMBIGUOUS", "UNRESOLVED", "CENSORED"]
    observed_minutes: int
    rejection_known_at: datetime | None
    continuation_known_at: datetime | None
    mfe: Decimal | None
    mae: Decimal | None
    touch_minute_penetration: Decimal | None
    single_candle_rejection: bool
    immediate_rejection: bool
    single_touch_rejection: bool
    one_retest_rejection: bool
    multiple_test_rejection: bool
    retest_results: tuple[str, ...]
    acceptance_known_at: datetime | None
    reclaim_known_at: datetime | None
    quick_reclaim: bool
    later_reclaim: bool
    censored: bool
    mfe_envelope_upper: Decimal | None
    mae_envelope_upper: Decimal | None
    final_close_away: Decimal | None
    time_to_rejection_seconds: int | None
    time_to_reclaim_seconds: int | None
    first_retest_delay_seconds: int | None
    touch_count: int
    retest_count: int
    rejection_ordering: Literal["CONFIRMED", "AMBIGUOUS", "NOT_OBSERVED"]


class Reversal(Frozen):
    id: str
    distance: Decimal
    direction: Literal["UP", "DOWN", "UNESTABLISHED"]
    turning_start: datetime
    turning_price: Decimal
    known_at: datetime | None
    censored: bool
    observation_end_at: datetime


class Relationship(Frozen):
    observation_id: str
    level_id: str
    available_at: datetime
    signed_distance: Decimal
    absolute_distance: Decimal
    bucket: str
    same_price: bool
    shared_source: bool
    family: Family
    level_age_sessions: int
    atr14: Decimal | None = None
    atr_known_at: datetime | None = None
    distance_atr: Decimal | None = None
    atr_status: Literal["AVAILABLE", "UNAVAILABLE", "ZERO_ATR"] = "UNAVAILABLE"


class NextLevel(Frozen):
    episode_id: str
    snapshot_at: datetime
    level_ids: tuple[str, ...]
    price: Decimal | None
    status: str
    reached_known_at: datetime | None = None
    invalidated_known_at: datetime | None = None
    censored: bool = False


class NextLevelReaction(Frozen):
    episode_id: str
    distance: Decimal
    horizon: int
    reached_before_recognition: bool | None
    result: str


class GapCross(Frozen):
    level_id: str
    start: datetime
    known_at: datetime
    previous_close: Decimal
    open: Decimal
    through_original_role: bool


class Ledger(Frozen):
    touches: tuple[Touch, ...]
    episodes: tuple[Episode, ...]
    gap_crosses: tuple[GapCross, ...] = ()
