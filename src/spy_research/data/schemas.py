"""Typed raw-bar records and the explicit Arrow storage schema."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Literal, Self

import pyarrow as pa
from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.alpaca.models import StockBar
from spy_research.config import ResearchConfig


PRICE_TYPE = pa.decimal128(28, 12)
RAW_BAR_SCHEMA = pa.schema(
    [
        pa.field("symbol", pa.string(), nullable=False),
        pa.field("timestamp", pa.timestamp("us", tz="UTC"), nullable=False),
        pa.field("open", PRICE_TYPE, nullable=False),
        pa.field("high", PRICE_TYPE, nullable=False),
        pa.field("low", PRICE_TYPE, nullable=False),
        pa.field("close", PRICE_TYPE, nullable=False),
        pa.field("volume", pa.int64(), nullable=False),
        pa.field("trade_count", pa.int64(), nullable=False),
        pa.field("vwap", PRICE_TYPE, nullable=False),
        pa.field("source", pa.string(), nullable=False),
        pa.field("feed", pa.string(), nullable=False),
        pa.field("timeframe", pa.string(), nullable=False),
        pa.field("adjustment", pa.string(), nullable=False),
    ],
    metadata={
        b"spy_research.schema_version": b"raw-bars-v1",
        b"source": b"alpaca",
        b"symbol": b"SPY",
        b"feed": b"sip",
        b"timeframe": b"1Min",
        b"adjustment": b"raw",
    },
)


class RawBarRecord(BaseModel):
    """A persisted raw bar plus explicit non-secret provenance columns."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"]
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int = Field(ge=0)
    trade_count: int = Field(ge=0)
    vwap: Decimal
    source: Literal["alpaca"]
    feed: Literal["sip"]
    timeframe: Literal["1Min"]
    adjustment: Literal["raw"]

    @model_validator(mode="after")
    def timestamp_must_be_timezone_aware(self) -> Self:
        if self.timestamp.utcoffset() is None:
            raise ValueError("raw bar timestamp must be timezone-aware")
        return self

    @classmethod
    def from_stock_bar(cls, bar: StockBar, config: ResearchConfig) -> Self:
        return cls(
            symbol=bar.symbol,
            timestamp=bar.timestamp.astimezone(UTC),
            open=bar.open,
            high=bar.high,
            low=bar.low,
            close=bar.close,
            volume=bar.volume,
            trade_count=bar.trade_count,
            vwap=bar.vwap,
            source=config.data.source,
            feed=config.data.feed,
            timeframe=config.data.timeframe,
            adjustment=config.data.adjustment,
        )

    @property
    def unique_key(self) -> tuple[str, datetime, str, str]:
        return self.symbol, self.timestamp, self.feed, self.timeframe


class PersistenceResult(BaseModel):
    """Counts and paths produced by one idempotent persistence operation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    bars_received: int = Field(ge=0)
    new_bars: int = Field(ge=0)
    existing_identical: int = Field(ge=0)
    conflicts: int = Field(ge=0)
    partitions_written: int = Field(ge=0)
    partition_paths: tuple[Path, ...]
