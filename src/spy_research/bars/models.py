"""Strict immutable models for derived five-minute research bars."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Self
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.data.validation import DataValidationReport


NEW_YORK = ZoneInfo("America/New_York")


class FiveMinuteBar(BaseModel):
    """One complete RTH candle derived from five validated one-minute bars."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"]
    timestamp: datetime
    session_date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int = Field(ge=0)
    trade_count: int = Field(ge=0)
    source: Literal["alpaca"]
    feed: Literal["sip"]
    timeframe: Literal["5Min"]
    adjustment: Literal["raw"]
    source_bar_count: Literal[5]
    session_type: Literal["RTH"] = "RTH"
    source_timeframe: Literal["1Min"] = "1Min"
    session_mode: Literal["RTH_ONLY"] = "RTH_ONLY"
    aggregation_method: Literal["rth_1m_to_5m_v1"] = "rth_1m_to_5m_v1"

    @model_validator(mode="after")
    def validate_derived_bar(self) -> Self:
        if self.timestamp.utcoffset() is None:
            raise ValueError("five-minute timestamp must be timezone-aware")
        if self.timestamp.astimezone(NEW_YORK).date() != self.session_date:
            raise ValueError("five-minute timestamp must match session_date")
        if self.timestamp.second != 0 or self.timestamp.microsecond != 0:
            raise ValueError("five-minute timestamp must align to a minute")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("high must be at least open, close, and low")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low must be at most open, close, and high")
        return self


class SessionAggregationSummary(BaseModel):
    """Counts and boundaries produced for one independent XNYS session."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    raw_rth_bars: int = Field(ge=0)
    expected_five_minute_bars: int = Field(ge=0)
    five_minute_bars: int = Field(ge=0)
    first_timestamp: datetime | None
    last_timestamp: datetime | None


class AggregationResult(BaseModel):
    """In-memory output of a validation-gated date-range transformation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"]
    start_date: date
    end_date: date
    raw_rth_bars: int = Field(ge=0)
    bars: tuple[FiveMinuteBar, ...]
    sessions: tuple[SessionAggregationSummary, ...]
    validation_report: DataValidationReport
