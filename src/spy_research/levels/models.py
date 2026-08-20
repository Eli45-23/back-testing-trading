"""Immutable models for objective, look-ahead-safe key levels."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PreviousSessionLevelValues(BaseModel):
    """PDH/PDL/PDC values calculated from one validated RTH source session."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"]
    source_session_date: date
    pdh: Decimal
    pdl: Decimal
    pdc: Decimal
    pdh_source_timestamp: datetime
    pdl_source_timestamp: datetime
    pdc_source_timestamp: datetime
    timeframe_source: Literal["1Min"] = "1Min"
    source_session: Literal["RTH"] = "RTH"
    level_version: Literal["previous-day-levels-v1"] = "previous-day-levels-v1"


class PreviousDayLevels(PreviousSessionLevelValues):
    """Previous-session values mapped to the next XNYS trading session."""

    session_date: date


class MissingPreviousDaySource(BaseModel):
    """An unavailable local source session, reported without fabrication."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    source_session_date: date
    reason: Literal["MISSING_RAW_SOURCE_SESSION"] = "MISSING_RAW_SOURCE_SESSION"


class PreviousDayLevelsResult(BaseModel):
    """Read-only result for all requested XNYS sessions."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"]
    start_date: date
    end_date: date
    levels: tuple[PreviousDayLevels, ...]
    missing_sources: tuple[MissingPreviousDaySource, ...]


class PremarketLevels(BaseModel):
    """Finalized same-day PMH/PML values or an explicit unavailable state."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    session_date: date
    pmh: Decimal | None
    pml: Decimal | None
    pmh_source_timestamp: datetime | None
    pml_source_timestamp: datetime | None
    source_bar_count: int = Field(ge=0)
    status: Literal["AVAILABLE", "NO_PREMARKET_DATA", "MISSING_RAW_SESSION"]
    timeframe_source: Literal["1Min"] = "1Min"
    source_session: Literal["PREMARKET"] = "PREMARKET"
    level_version: Literal["premarket-levels-v1"] = "premarket-levels-v1"

    @model_validator(mode="after")
    def validate_availability(self) -> "PremarketLevels":
        values = (
            self.pmh,
            self.pml,
            self.pmh_source_timestamp,
            self.pml_source_timestamp,
        )
        if self.status == "AVAILABLE":
            if self.source_bar_count == 0 or any(value is None for value in values):
                raise ValueError("available premarket levels require bars and values")
        elif self.source_bar_count != 0 or any(value is not None for value in values):
            raise ValueError("unavailable premarket levels cannot contain values")
        return self


class PremarketLevelsResult(BaseModel):
    """Read-only PMH/PML result for requested XNYS sessions."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    start_date: date
    end_date: date
    levels: tuple[PremarketLevels, ...]


class OpeningFiveMinuteLevels(BaseModel):
    """Opening range from the first completed self-built RTH five-minute bar."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    session_date: date
    orh5: Decimal
    orl5: Decimal
    source_timestamp: datetime
    available_from_timestamp: datetime
    source_bar_count: Literal[1] = 1
    timeframe_source: Literal["5Min"] = "5Min"
    session_mode: Literal["RTH_ONLY"] = "RTH_ONLY"
    level_version: Literal["opening-5m-levels-v1"] = "opening-5m-levels-v1"


class OpeningFiveMinuteLevelsResult(BaseModel):
    """Read-only opening-range result for requested XNYS sessions."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    start_date: date
    end_date: date
    levels: tuple[OpeningFiveMinuteLevels, ...]
