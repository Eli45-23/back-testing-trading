"""Immutable typed rows and summaries for in-memory indicator output."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.bars.validation import ProcessedValidationReport


class FiveMinuteIndicatorRow(BaseModel):
    """EMA values keyed to one completed RTH five-minute close."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"]
    timestamp: datetime
    session_date: date
    close: Decimal
    ema9: Decimal | None
    ema20: Decimal | None
    timeframe: Literal["5Min"] = "5Min"
    session_mode: Literal["RTH_ONLY"] = "RTH_ONLY"
    indicator_version: Literal["ema_9_20_sma_seed_session_reset_v1"] = (
        "ema_9_20_sma_seed_session_reset_v1"
    )

    @model_validator(mode="after")
    def timestamp_must_be_aware(self) -> Self:
        if self.timestamp.utcoffset() is None:
            raise ValueError("indicator timestamp must be timezone-aware")
        return self


class EmaSessionSummary(BaseModel):
    """Warm-up and valid-value counts for one independent RTH session."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    bars: int = Field(ge=0)
    ema9_valid_rows: int = Field(ge=0)
    ema20_valid_rows: int = Field(ge=0)
    first_ema9_timestamp: datetime | None
    first_ema20_timestamp: datetime | None


class EmaCalculationResult(BaseModel):
    """Validation-gated, in-memory EMA output for a requested range."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"]
    start_date: date
    end_date: date
    rows: tuple[FiveMinuteIndicatorRow, ...]
    sessions: tuple[EmaSessionSummary, ...]
    processed_validation: ProcessedValidationReport


class FiveMinuteVwapRow(BaseModel):
    """Daily RTH session VWAP keyed to a completed five-minute candle."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"]
    timestamp: datetime
    session_date: date
    typical_price: Decimal
    vwap: Decimal | None
    timeframe: Literal["5Min"] = "5Min"
    session_mode: Literal["RTH_ONLY"] = "RTH_ONLY"
    indicator_version: Literal["rth_daily_hlc3_volume_vwap_v1"] = (
        "rth_daily_hlc3_volume_vwap_v1"
    )

    @model_validator(mode="after")
    def vwap_timestamp_must_be_aware(self) -> Self:
        if self.timestamp.utcoffset() is None:
            raise ValueError("VWAP timestamp must be timezone-aware")
        return self


class VwapSessionSummary(BaseModel):
    """Availability and boundary values for one independently reset session."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    bars: int = Field(ge=0)
    valid_rows: int = Field(ge=0)
    first_valid_timestamp: datetime | None
    first_vwap: Decimal | None
    final_vwap: Decimal | None


class VwapCalculationResult(BaseModel):
    """Validation-gated, in-memory daily RTH VWAP output."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"]
    start_date: date
    end_date: date
    rows: tuple[FiveMinuteVwapRow, ...]
    sessions: tuple[VwapSessionSummary, ...]
    processed_validation: ProcessedValidationReport


class FiveMinuteAtrRow(BaseModel):
    """True range and daily-reset ATR14 for one completed five-minute candle."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"]
    timestamp: datetime
    session_date: date
    true_range: Decimal
    atr14: Decimal | None
    timeframe: Literal["5Min"] = "5Min"
    session_mode: Literal["RTH_ONLY"] = "RTH_ONLY"
    indicator_version: Literal["atr14_wilder_session_reset_v1"] = (
        "atr14_wilder_session_reset_v1"
    )

    @model_validator(mode="after")
    def atr_timestamp_must_be_aware(self) -> Self:
        if self.timestamp.utcoffset() is None:
            raise ValueError("ATR timestamp must be timezone-aware")
        return self


class AtrSessionSummary(BaseModel):
    """Warm-up and boundary values for one independently reset session."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    bars: int = Field(ge=0)
    valid_rows: int = Field(ge=0)
    first_valid_timestamp: datetime | None
    first_atr14: Decimal | None
    final_atr14: Decimal | None


class AtrCalculationResult(BaseModel):
    """Validation-gated, in-memory daily-reset ATR14 output."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"]
    start_date: date
    end_date: date
    rows: tuple[FiveMinuteAtrRow, ...]
    sessions: tuple[AtrSessionSummary, ...]
    processed_validation: ProcessedValidationReport


class EmaSeparationRow(BaseModel):
    """Raw EMA9/EMA20 distance metrics for one completed five-minute candle."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"]
    timestamp: datetime
    session_date: date
    ema9: Decimal | None
    ema20: Decimal | None
    signed_separation: Decimal | None
    absolute_separation: Decimal | None
    separation_delta_1: Decimal | None
    separation_delta_2: Decimal | None
    separation_delta_3: Decimal | None
    timeframe: Literal["5Min"] = "5Min"
    session_mode: Literal["RTH_ONLY"] = "RTH_ONLY"
    indicator_version: Literal["ema_9_20_raw_separation_v1"] = (
        "ema_9_20_raw_separation_v1"
    )

    @model_validator(mode="after")
    def separation_timestamp_must_be_aware(self) -> Self:
        if self.timestamp.utcoffset() is None:
            raise ValueError("EMA separation timestamp must be timezone-aware")
        return self


class EmaSeparationSessionSummary(BaseModel):
    """Availability boundaries and counts for one independent RTH session."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    bars: int = Field(ge=0)
    separation_valid_rows: int = Field(ge=0)
    delta_1_valid_rows: int = Field(ge=0)
    delta_2_valid_rows: int = Field(ge=0)
    delta_3_valid_rows: int = Field(ge=0)
    first_separation_timestamp: datetime | None
    first_delta_1_timestamp: datetime | None
    first_delta_2_timestamp: datetime | None
    first_delta_3_timestamp: datetime | None
    final_signed_separation: Decimal | None


class EmaSeparationCalculationResult(BaseModel):
    """Validation-gated, in-memory EMA separation output."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"]
    start_date: date
    end_date: date
    rows: tuple[EmaSeparationRow, ...]
    sessions: tuple[EmaSeparationSessionSummary, ...]
    processed_validation: ProcessedValidationReport
