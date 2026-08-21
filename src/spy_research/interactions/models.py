"""Immutable, auditable models for candle-versus-level interactions."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PriceSide(StrEnum):
    ABOVE = "ABOVE"
    BELOW = "BELOW"
    EQUAL = "EQUAL"


class LevelType(StrEnum):
    PDH = "PDH"
    PDL = "PDL"
    PDC = "PDC"
    PMH = "PMH"
    PML = "PML"
    ORH5 = "ORH5"
    ORL5 = "ORL5"


class InteractionType(StrEnum):
    NO_INTERACTION = "NO_INTERACTION"
    TOUCH = "TOUCH"
    WICK_THROUGH_ABOVE = "WICK_THROUGH_ABOVE"
    WICK_THROUGH_BELOW = "WICK_THROUGH_BELOW"
    CLOSE_THROUGH_ABOVE = "CLOSE_THROUGH_ABOVE"
    CLOSE_THROUGH_BELOW = "CLOSE_THROUGH_BELOW"


class ImmediateState(StrEnum):
    HOLD = "HOLD"
    FAILURE = "FAILURE"
    EQUAL = "EQUAL"
    UNAVAILABLE = "UNAVAILABLE"


class RetestState(StrEnum):
    RETEST_HOLD = "RETEST_HOLD"
    RETEST_FAILURE = "RETEST_FAILURE"
    RETEST_EQUAL = "RETEST_EQUAL"
    NO_RETEST = "NO_RETEST"
    UNAVAILABLE = "UNAVAILABLE"


class SweepType(StrEnum):
    SWEEP_ABOVE = "SWEEP_ABOVE"
    SWEEP_BELOW = "SWEEP_BELOW"
    WICK_EQUAL_ABOVE = "WICK_EQUAL_ABOVE"
    WICK_EQUAL_BELOW = "WICK_EQUAL_BELOW"


class TolerantImmediateState(StrEnum):
    HOLD_EXACT = "HOLD_EXACT"
    HOLD_WITHIN_TOLERANCE = "HOLD_WITHIN_TOLERANCE"
    FAILURE = "FAILURE"
    UNAVAILABLE = "UNAVAILABLE"
    UNAVAILABLE_ATR = "UNAVAILABLE_ATR"


class TolerantRetestState(StrEnum):
    RETEST_HOLD_EXACT = "RETEST_HOLD_EXACT"
    RETEST_HOLD_WITHIN_TOLERANCE = "RETEST_HOLD_WITHIN_TOLERANCE"
    RETEST_FAILURE = "RETEST_FAILURE"
    NO_RETEST = "NO_RETEST"
    UNAVAILABLE = "UNAVAILABLE"
    UNAVAILABLE_ATR = "UNAVAILABLE_ATR"


class AvailableLevel(BaseModel):
    """One Stage 7 price and the first candle timestamp eligible to use it."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    session_date: date
    level_type: LevelType
    level_price: Decimal
    available_from_timestamp: datetime


class LevelInteraction(BaseModel):
    """Exact current/prior candle facts and one deterministic classification."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    session_date: date
    candle_timestamp: datetime
    candle_completed_at: datetime
    level_type: LevelType
    level_price: Decimal
    level_available_from: datetime
    interaction_type: InteractionType
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    open_side: PriceSide
    close_side: PriceSide
    previous_close: Decimal | None
    previous_close_side: PriceSide | None
    range_encountered: bool
    traded_above: bool
    traded_below: bool
    touched_level: bool
    timeframe: Literal["5Min"] = "5Min"
    session_mode: Literal["RTH_ONLY"] = "RTH_ONLY"
    interaction_version: Literal["level-interaction-v1"] = "level-interaction-v1"


class InteractionCount(BaseModel):
    """Audit count for one level type and classification."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    level_type: LevelType
    interaction_type: InteractionType
    count: int = Field(ge=0)


class LevelInteractionResult(BaseModel):
    """Non-NO events plus complete eligible-pair audit counts."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    start_date: date
    end_date: date
    eligible_pair_count: int = Field(ge=0)
    no_interaction_count: int = Field(ge=0)
    interactions: tuple[LevelInteraction, ...]
    counts: tuple[InteractionCount, ...]


class ImmediateAssessment(BaseModel):
    """State of exactly the first completed bar after a close-through."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    state: ImmediateState
    bar_timestamp: datetime | None = None
    close: Decimal | None = None
    close_side: PriceSide | None = None


class RetestAssessment(BaseModel):
    """First exact-price retest found within the bounded future window."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    state: RetestState
    bar_offset: int | None = Field(default=None, ge=1, le=3)
    timestamp: datetime | None = None
    open: Decimal | None = None
    high: Decimal | None = None
    low: Decimal | None = None
    close: Decimal | None = None
    requested_bars: int = Field(ge=1)
    available_bars: int = Field(ge=0)
    window_complete: bool


class BreakFollowThrough(BaseModel):
    """Immediate and first-retest context linked to one Stage 8.1 seed."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    break_interaction_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    level_type: LevelType
    level_price: Decimal
    break_timestamp: datetime
    break_completed_at: datetime
    break_interaction_type: Literal[
        InteractionType.CLOSE_THROUGH_ABOVE,
        InteractionType.CLOSE_THROUGH_BELOW,
    ]
    break_direction: PriceSide
    immediate: ImmediateAssessment
    retest: RetestAssessment
    follow_through_version: Literal["break-follow-through-v1"] = (
        "break-follow-through-v1"
    )


class BreakFollowThroughResult(BaseModel):
    """Read-only follow-through context for all close-through seeds."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    start_date: date
    end_date: date
    seed_count: int = Field(ge=0)
    follow_through: tuple[BreakFollowThrough, ...]


class LiquiditySweepPattern(BaseModel):
    """Mechanical strict-reclaim label linked to one Stage 8.1 wick event."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_interaction_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    candle_timestamp: datetime
    candle_completed_at: datetime
    level_type: LevelType
    level_price: Decimal
    source_interaction_type: Literal[
        InteractionType.WICK_THROUGH_ABOVE,
        InteractionType.WICK_THROUGH_BELOW,
    ]
    sweep_type: SweepType
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    open_side: PriceSide
    close_side: PriceSide
    traded_above: bool
    traded_below: bool
    excursion_amount: Decimal = Field(gt=0)
    excursion_side: Literal[PriceSide.ABOVE, PriceSide.BELOW]
    reclaim_distance: Decimal = Field(ge=0)
    sweep_version: Literal["liquidity-sweep-pattern-v1"] = (
        "liquidity-sweep-pattern-v1"
    )


class LiquiditySweepResult(BaseModel):
    """Read-only sweep-pattern labels for all Stage 8.1 wick seeds."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    start_date: date
    end_date: date
    seed_count: int = Field(ge=0)
    patterns: tuple[LiquiditySweepPattern, ...]


class AtrToleranceFollowThrough(BaseModel):
    """Parallel fixed-ATR interpretation of one immutable Stage 8.2 result."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    break_interaction_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    level_type: LevelType
    level_price: Decimal
    break_timestamp: datetime
    break_interaction_type: Literal[
        InteractionType.CLOSE_THROUGH_ABOVE,
        InteractionType.CLOSE_THROUGH_BELOW,
    ]
    break_direction: Literal[PriceSide.ABOVE, PriceSide.BELOW]
    atr_available: bool
    event_atr: Decimal | None = None
    tolerance_fraction: Decimal = Decimal("0.10")
    tolerance_amount: Decimal | None = None
    tolerance_boundary: Decimal | None = None
    immediate_timestamp: datetime | None = None
    immediate_close: Decimal | None = None
    exact_immediate_state: ImmediateState
    tolerant_immediate_state: TolerantImmediateState
    immediate_reclassified: bool
    immediate_penetration: Decimal | None = Field(default=None, ge=0)
    immediate_penetration_as_atr: Decimal | None = Field(default=None, ge=0)
    exact_retest_state: RetestState
    tolerant_retest_state: TolerantRetestState
    retest_reclassified: bool
    retest_bar_offset: int | None = Field(default=None, ge=1, le=3)
    retest_timestamp: datetime | None = None
    retest_close: Decimal | None = None
    retest_penetration: Decimal | None = Field(default=None, ge=0)
    retest_penetration_as_atr: Decimal | None = Field(default=None, ge=0)
    available_retest_bars: int = Field(ge=0)
    retest_window_complete: bool
    tolerance_version: Literal["event-atr14-0.10-follow-through-v1"] = (
        "event-atr14-0.10-follow-through-v1"
    )


class AtrToleranceResult(BaseModel):
    """Read-only 0.10 event-ATR comparison over all Stage 8.2 seeds."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    start_date: date
    end_date: date
    seed_count: int = Field(ge=0)
    atr_available_count: int = Field(ge=0)
    atr_unavailable_count: int = Field(ge=0)
    comparisons: tuple[AtrToleranceFollowThrough, ...]
