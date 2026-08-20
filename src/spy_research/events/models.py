"""Immutable typed models for completed-candle research events."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.bars.validation import ProcessedValidationReport


class EmaCrossDirection(str, Enum):
    """Strict direction of an EMA9/EMA20 relationship reversal."""

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


class DetectedEmaCross(BaseModel):
    """Minimal cross fact produced solely from adjacent verified EMA rows."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"]
    timestamp: datetime
    session_date: date
    direction: EmaCrossDirection
    close: Decimal
    ema9: Decimal
    ema20: Decimal
    previous_ema9: Decimal
    previous_ema20: Decimal
    timeframe: Literal["5Min"] = "5Min"
    session_mode: Literal["RTH_ONLY"] = "RTH_ONLY"
    detector_version: Literal["ema_9_20_completed_candle_cross_v1"] = (
        "ema_9_20_completed_candle_cross_v1"
    )

    @model_validator(mode="after")
    def detected_timestamp_must_be_aware(self) -> Self:
        if self.timestamp.utcoffset() is None:
            raise ValueError("EMA cross timestamp must be timezone-aware")
        return self


class EmaCrossEvent(BaseModel):
    """Completed-candle cross plus same-timestamp descriptive context."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"]
    timestamp: datetime
    session_date: date
    direction: EmaCrossDirection
    reference_price: Decimal
    close: Decimal
    ema9: Decimal
    ema20: Decimal
    previous_ema9: Decimal
    previous_ema20: Decimal
    signed_separation: Decimal
    absolute_separation: Decimal
    previous_signed_separation: Decimal
    separation_delta_1: Decimal | None
    separation_delta_2: Decimal | None
    separation_delta_3: Decimal | None
    vwap: Decimal | None
    close_minus_vwap: Decimal | None
    ema9_minus_vwap: Decimal | None
    ema20_minus_vwap: Decimal | None
    atr14: Decimal | None
    timeframe: Literal["5Min"] = "5Min"
    session_mode: Literal["RTH_ONLY"] = "RTH_ONLY"
    event_version: Literal["ema_9_20_completed_candle_cross_context_v1"] = (
        "ema_9_20_completed_candle_cross_context_v1"
    )

    @model_validator(mode="after")
    def validate_event_identity(self) -> Self:
        if self.timestamp.utcoffset() is None:
            raise ValueError("EMA cross event timestamp must be timezone-aware")
        if self.reference_price != self.close:
            raise ValueError("EMA cross reference_price must equal cross-bar close")
        return self


class EmaCrossSessionSummary(BaseModel):
    """Direction counts and boundaries for one independent RTH session."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    bullish_crosses: int = Field(ge=0)
    bearish_crosses: int = Field(ge=0)
    total_crosses: int = Field(ge=0)
    first_event_timestamp: datetime | None
    last_event_timestamp: datetime | None


class EmaCrossCalculationResult(BaseModel):
    """Validation-gated, in-memory cross events for a requested range."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"]
    start_date: date
    end_date: date
    events: tuple[EmaCrossEvent, ...]
    sessions: tuple[EmaCrossSessionSummary, ...]
    processed_validation: ProcessedValidationReport
