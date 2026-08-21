"""Immutable models for the Stage 10.7 EMA20/VWAP cross experiment."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal, localcontext
from enum import StrEnum
from hashlib import sha256
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.indicators.vwap import VWAP_CONTEXT
from spy_research.research_stats import DistributionSummary
from spy_research.strategy.base_statistics import BaseStrategyHorizonStatistics
from spy_research.strategy.comparisons.ema20_vwap_alignment import (
    Ema20VwapAlignmentState,
)
from spy_research.strategy.comparisons.models import (
    Ema9VwapCrossContextState,
)
from spy_research.strategy.models import SetupDirection


HORIZON_ORDER = ("5m", "15m", "30m", "60m", "EOD")


class Ema20VwapCrossDirection(StrEnum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


class Ema20VwapCrossEvent(BaseModel):
    """One completed-candle EMA20/VWAP relationship reversal."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    event_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    direction: Ema20VwapCrossDirection
    cross_timestamp: datetime
    cross_known_at: datetime
    ema20: Decimal
    vwap: Decimal
    prior_ema20: Decimal
    prior_vwap: Decimal
    signed_distance: Decimal
    event_version: Literal["ema20-vwap-completed-candle-cross-v1"] = (
        "ema20-vwap-completed-candle-cross-v1"
    )

    @model_validator(mode="after")
    def validate_event(self) -> Self:
        if self.cross_timestamp.utcoffset() is None:
            raise ValueError("EMA20/VWAP cross timestamp must be timezone-aware")
        if self.cross_known_at != self.cross_timestamp + timedelta(minutes=5):
            raise ValueError("EMA20/VWAP cross known-at must follow by five minutes")
        with localcontext(VWAP_CONTEXT):
            if self.signed_distance != self.ema20 - self.vwap:
                raise ValueError("EMA20/VWAP signed distance mismatch")
        payload = "|".join(
            (
                self.symbol,
                self.cross_timestamp.isoformat(),
                self.direction.value,
                self.event_version,
            )
        )
        if self.event_identity != sha256(payload.encode()).hexdigest():
            raise ValueError("EMA20/VWAP event identity mismatch")
        return self


class Ema20VwapCrossSessionSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    bullish_crosses: int = Field(ge=0)
    bearish_crosses: int = Field(ge=0)
    total_crosses: int = Field(ge=0)
    first_cross_timestamp: datetime | None
    last_cross_timestamp: datetime | None

    @model_validator(mode="after")
    def reconcile_session(self) -> Self:
        if self.bullish_crosses + self.bearish_crosses != self.total_crosses:
            raise ValueError("session cross directions must reconcile")
        return self


class Ema20VwapCrossContextState(StrEnum):
    MATCHING_EMA20_VWAP_CROSS = "MATCHING_EMA20_VWAP_CROSS"
    OPPOSING_EMA20_VWAP_CROSS = "OPPOSING_EMA20_VWAP_CROSS"
    NO_PRIOR_EMA20_VWAP_CROSS = "NO_PRIOR_EMA20_VWAP_CROSS"


class Ema20VwapCrossGroupName(StrEnum):
    BASE_ALL = "BASE_ALL"
    MATCHING_EMA20_VWAP_CROSS = "MATCHING_EMA20_VWAP_CROSS"
    OPPOSING_EMA20_VWAP_CROSS = "OPPOSING_EMA20_VWAP_CROSS"
    NO_PRIOR_EMA20_VWAP_CROSS = "NO_PRIOR_EMA20_VWAP_CROSS"


class Ema20VwapCrossContextAnnotation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    direction: SetupDirection
    confirmation_bar_timestamp: datetime
    signal_known_at: datetime
    cross_state: Ema20VwapCrossContextState
    most_recent_cross_identity: str | None
    cross_direction: Ema20VwapCrossDirection | None
    cross_timestamp: datetime | None
    cross_known_at: datetime | None
    bars_since_cross: int | None = Field(default=None, ge=0)
    minutes_since_cross_completion: int | None = Field(default=None, ge=0)
    comparison_version: Literal["ema20-vwap-prior-cross-context-v1"] = (
        "ema20-vwap-prior-cross-context-v1"
    )

    @model_validator(mode="after")
    def reconcile_context(self) -> Self:
        if self.signal_known_at != self.confirmation_bar_timestamp + timedelta(minutes=5):
            raise ValueError("setup known-at must follow confirmation by five minutes")
        cross_fields = (
            self.most_recent_cross_identity,
            self.cross_direction,
            self.cross_timestamp,
            self.cross_known_at,
            self.bars_since_cross,
            self.minutes_since_cross_completion,
        )
        if self.cross_state is Ema20VwapCrossContextState.NO_PRIOR_EMA20_VWAP_CROSS:
            if any(value is not None for value in cross_fields):
                raise ValueError("no-prior EMA20/VWAP cross requires null fields")
            return self
        if any(value is None for value in cross_fields):
            raise ValueError("EMA20/VWAP cross context requires complete fields")
        assert self.cross_timestamp is not None
        assert self.cross_known_at is not None
        assert self.bars_since_cross is not None
        assert self.minutes_since_cross_completion is not None
        assert self.cross_direction is not None
        if self.cross_known_at != self.cross_timestamp + timedelta(minutes=5):
            raise ValueError("cross known-at must follow timestamp by five minutes")
        if self.cross_known_at > self.signal_known_at:
            raise ValueError("future EMA20/VWAP cross cannot annotate setup")
        elapsed = self.confirmation_bar_timestamp - self.cross_timestamp
        if elapsed.total_seconds() < 0 or elapsed.total_seconds() % 300:
            raise ValueError("EMA20/VWAP recency requires whole five-minute bars")
        if self.bars_since_cross != elapsed.total_seconds() // 300:
            raise ValueError("EMA20/VWAP bars-since-cross mismatch")
        if self.minutes_since_cross_completion != self.bars_since_cross * 5:
            raise ValueError("EMA20/VWAP minutes-since-cross mismatch")
        expected = (
            Ema20VwapCrossDirection.BULLISH
            if self.direction is SetupDirection.LONG
            else Ema20VwapCrossDirection.BEARISH
        )
        matching = self.cross_direction is expected
        if matching != (
            self.cross_state
            is Ema20VwapCrossContextState.MATCHING_EMA20_VWAP_CROSS
        ):
            raise ValueError("EMA20/VWAP cross direction/context mismatch")
        return self


class Ema20VwapCrossGroupStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: Ema20VwapCrossGroupName
    annotation_n: int = Field(ge=0)
    long_annotation_n: int = Field(ge=0)
    short_annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    horizons: tuple[BaseStrategyHorizonStatistics, ...]

    @model_validator(mode="after")
    def reconcile_group(self) -> Self:
        if self.long_annotation_n + self.short_annotation_n != self.annotation_n:
            raise ValueError("cross group directions must reconcile")
        if self.executable_n > self.annotation_n:
            raise ValueError("executable count exceeds annotations")
        if tuple(item.horizon for item in self.horizons) != HORIZON_ORDER:
            raise ValueError("cross horizons must use frozen ordering")
        return self


class Ema20VwapCrossDirectionStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    direction: SetupDirection
    cross_state: Ema20VwapCrossContextState
    executable_n: int = Field(ge=0)
    eod: BaseStrategyHorizonStatistics


class Ema20VwapCrossRecencyStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    bars_since_cross: int = Field(ge=0)
    annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    long_executable_n: int = Field(ge=0)
    short_executable_n: int = Field(ge=0)
    eod: BaseStrategyHorizonStatistics


class Ema20VwapStateCrossTabCount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    alignment_state: Ema20VwapAlignmentState
    cross_state: Ema20VwapCrossContextState
    annotation_n: int = Field(ge=0)


class Ema9Ema20VwapCrossTabCount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ema9_vwap_cross_state: Ema9VwapCrossContextState
    ema20_vwap_cross_state: Ema20VwapCrossContextState
    annotation_n: int = Field(ge=0)


class Ema20VwapCrossContextComparisonResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    start_date: date
    end_date: date
    break_seed_count: int = Field(ge=0)
    confirmed_count: int = Field(ge=0)
    non_confirmed_count: int = Field(ge=0)
    executable_count: int = Field(ge=0)
    session_end_unavailable_count: int = Field(ge=0)
    missing_entry_count: int = Field(ge=0)
    development_session_count: int = Field(ge=0)
    events: tuple[Ema20VwapCrossEvent, ...]
    event_sessions: tuple[Ema20VwapCrossSessionSummary, ...]
    bullish_event_count: int = Field(ge=0)
    bearish_event_count: int = Field(ge=0)
    annotations: tuple[Ema20VwapCrossContextAnnotation, ...]
    groups: tuple[Ema20VwapCrossGroupStatistics, ...]
    direction_groups: tuple[Ema20VwapCrossDirectionStatistics, ...]
    bars_since_cross_distribution: DistributionSummary
    recency_rows: tuple[Ema20VwapCrossRecencyStatistics, ...]
    ema20_vwap_state_cross_tab: tuple[Ema20VwapStateCrossTabCount, ...]
    ema9_ema20_vwap_cross_tab: tuple[Ema9Ema20VwapCrossTabCount, ...]
    comparison_version: Literal["controlled-ema20-vwap-cross-context-v1"] = (
        "controlled-ema20-vwap-cross-context-v1"
    )
    sample_warning: str = (
        "Exact recency is exploratory; tiny-n rows must not define a cutoff."
    )

    @model_validator(mode="after")
    def reconcile_result(self) -> Self:
        if self.bullish_event_count + self.bearish_event_count != len(self.events):
            raise ValueError("EMA20/VWAP event directions must reconcile")
        if len({item.event_identity for item in self.events}) != len(self.events):
            raise ValueError("EMA20/VWAP event identities must be unique")
        if len(self.annotations) != self.confirmed_count:
            raise ValueError("every confirmed setup requires cross context")
        if tuple(item.name for item in self.groups) != tuple(Ema20VwapCrossGroupName):
            raise ValueError("EMA20/VWAP groups must use frozen ordering")
        if self.groups[0].annotation_n != self.confirmed_count:
            raise ValueError("BASE_ALL annotation mismatch")
        if self.groups[0].executable_n != self.executable_count:
            raise ValueError("BASE_ALL executable mismatch")
        if sum(item.annotation_n for item in self.groups[1:]) != self.confirmed_count:
            raise ValueError("contexts must partition annotations")
        if sum(item.executable_n for item in self.groups[1:]) != self.executable_count:
            raise ValueError("contexts must partition outcomes")
        for table in (
            self.ema20_vwap_state_cross_tab,
            self.ema9_ema20_vwap_cross_tab,
        ):
            if sum(item.annotation_n for item in table) != self.confirmed_count:
                raise ValueError("cross-tab must reconcile annotations")
        observed = tuple(
            sorted(
                {
                    item.bars_since_cross
                    for item in self.annotations
                    if item.bars_since_cross is not None
                }
            )
        )
        if tuple(item.bars_since_cross for item in self.recency_rows) != observed:
            raise ValueError("recency rows must use observed ordering")
        return self
