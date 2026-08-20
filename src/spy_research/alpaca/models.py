"""Typed raw models returned by Alpaca's historical bars API."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StockBar(BaseModel):
    """An unmodified Alpaca SPY bar.

    Prices and VWAP use ``Decimal`` to preserve the decimal representation
    supplied by the JSON response. No derived values are calculated here.
    """

    model_config = ConfigDict(extra="ignore", frozen=True, populate_by_name=True)

    symbol: Literal["SPY"]
    timestamp: datetime = Field(alias="t")
    open: Decimal = Field(alias="o")
    high: Decimal = Field(alias="h")
    low: Decimal = Field(alias="l")
    close: Decimal = Field(alias="c")
    volume: int = Field(alias="v", ge=0)
    trade_count: int = Field(alias="n", ge=0)
    vwap: Decimal = Field(alias="vw")

    @model_validator(mode="after")
    def timestamp_must_be_timezone_aware(self) -> Self:
        if self.timestamp.utcoffset() is None:
            raise ValueError("bar timestamp must be timezone-aware")
        return self


class HistoricalBarsResult(BaseModel):
    """A complete, validated result across all Alpaca response pages."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    bars: tuple[StockBar, ...]
    pages_fetched: int = Field(ge=1)
