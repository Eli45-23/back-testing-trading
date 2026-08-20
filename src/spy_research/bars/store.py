"""Atomic, idempotent Parquet storage for processed RTH five-minute bars."""

from __future__ import annotations

import os
import tempfile
from collections import defaultdict
from collections.abc import Iterable, Sequence
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from spy_research.bars.errors import (
    ProcessedDataConflictError,
    ProcessedDataCorruptionError,
    ProcessedDataScopeError,
    ProcessedDataWriteError,
)
from spy_research.bars.models import FiveMinuteBar
from spy_research.config import PROJECT_ROOT
from spy_research.data.schemas import PRICE_TYPE


DEFAULT_PROCESSED_DATA_ROOT = PROJECT_ROOT / "data" / "processed"
PROCESSED_FIVE_MINUTE_SCHEMA = pa.schema(
    [
        pa.field("symbol", pa.string(), nullable=False),
        pa.field("timestamp", pa.timestamp("us", tz="UTC"), nullable=False),
        pa.field("session_date", pa.date32(), nullable=False),
        pa.field("open", PRICE_TYPE, nullable=False),
        pa.field("high", PRICE_TYPE, nullable=False),
        pa.field("low", PRICE_TYPE, nullable=False),
        pa.field("close", PRICE_TYPE, nullable=False),
        pa.field("volume", pa.int64(), nullable=False),
        pa.field("trade_count", pa.int64(), nullable=False),
        pa.field("source", pa.string(), nullable=False),
        pa.field("feed", pa.string(), nullable=False),
        pa.field("source_timeframe", pa.string(), nullable=False),
        pa.field("timeframe", pa.string(), nullable=False),
        pa.field("adjustment", pa.string(), nullable=False),
        pa.field("source_bar_count", pa.int16(), nullable=False),
        pa.field("session_type", pa.string(), nullable=False),
        pa.field("session_mode", pa.string(), nullable=False),
        pa.field("aggregation_method", pa.string(), nullable=False),
    ],
    metadata={
        b"spy_research.schema_version": b"processed-rth-5m-v1",
        b"symbol": b"SPY",
        b"source": b"alpaca",
        b"feed": b"sip",
        b"source_timeframe": b"1Min",
        b"processed_timeframe": b"5Min",
        b"adjustment": b"raw",
        b"session_mode": b"RTH_ONLY",
        b"aggregation_method": b"rth_1m_to_5m_v1",
    },
)


class ProcessedPersistenceResult(BaseModel):
    """Counts and paths resulting from one processed persistence call."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    bars_received: int = Field(ge=0)
    new_bars: int = Field(ge=0)
    existing_identical: int = Field(ge=0)
    conflicts: int = Field(ge=0)
    partitions_written: int = Field(ge=0)
    partition_paths: tuple[Path, ...]


class ProcessedFiveMinuteStore:
    """Daily processed partitions for SPY/5Min/RTH_ONLY candles."""

    def __init__(self, *, root: str | Path = DEFAULT_PROCESSED_DATA_ROOT) -> None:
        self._root = Path(root)
        self._base_path = self._root / "spy" / "5min" / "rth"

    def partition_path(self, partition_date: date) -> Path:
        return (
            self._base_path
            / f"{partition_date:%Y}"
            / f"{partition_date:%m}"
            / f"{partition_date.isoformat()}.parquet"
        )

    def persist_bars(
        self, bars: Sequence[FiveMinuteBar]
    ) -> ProcessedPersistenceResult:
        incoming_by_date: dict[date, list[FiveMinuteBar]] = defaultdict(list)
        for bar in bars:
            incoming_by_date[bar.session_date].append(bar)

        existing_identical = 0
        new_bars = 0
        conflicts = 0
        plans: dict[Path, tuple[FiveMinuteBar, ...]] = {}

        for partition_date, incoming in incoming_by_date.items():
            path = self.partition_path(partition_date)
            existing = self._read_partition(path) if path.exists() else ()
            existing_by_key = {self.identity(bar): bar for bar in existing}
            incoming_unique: dict[tuple[str, Any, str, str], FiveMinuteBar] = {}
            changed = False

            for bar in incoming:
                key = self.identity(bar)
                earlier = incoming_unique.get(key)
                if earlier is not None:
                    if earlier == bar:
                        existing_identical += 1
                    else:
                        conflicts += 1
                    continue
                incoming_unique[key] = bar

                stored = existing_by_key.get(key)
                if stored is None:
                    existing_by_key[key] = bar
                    new_bars += 1
                    changed = True
                elif stored == bar:
                    existing_identical += 1
                else:
                    conflicts += 1

            if changed:
                plans[path] = tuple(
                    sorted(existing_by_key.values(), key=lambda item: item.timestamp)
                )

        if conflicts:
            raise ProcessedDataConflictError(conflicts)

        written: list[Path] = []
        for path, records in sorted(plans.items()):
            self._atomic_write(path, records)
            written.append(path)

        return ProcessedPersistenceResult(
            bars_received=len(bars),
            new_bars=new_bars,
            existing_identical=existing_identical,
            conflicts=0,
            partitions_written=len(written),
            partition_paths=tuple(written),
        )

    def load_processed_5m_bars(
        self,
        *,
        symbol: str,
        start: date,
        end: date,
        session_mode: str = "RTH_ONLY",
    ) -> tuple[FiveMinuteBar, ...]:
        self._validate_scope(symbol=symbol, session_mode=session_mode)
        if start > end:
            raise ValueError("start date must be on or before end date")

        bars: list[FiveMinuteBar] = []
        for partition_date in _date_range(start, end):
            bars.extend(self.load_partition(partition_date))
        ordered = tuple(sorted(bars, key=lambda item: item.timestamp))
        identities = [self.identity(bar) for bar in ordered]
        if len(identities) != len(set(identities)):
            raise ProcessedDataCorruptionError(
                "Duplicate processed five-minute identity detected while loading"
            )
        return ordered

    def load_partition(
        self,
        partition_date: date,
        *,
        reject_duplicates: bool = True,
    ) -> tuple[FiveMinuteBar, ...]:
        path = self.partition_path(partition_date)
        return (
            self._read_partition(path, reject_duplicates=reject_duplicates)
            if path.exists()
            else ()
        )

    @staticmethod
    def identity(bar: FiveMinuteBar) -> tuple[str, datetime, str, str]:
        return bar.symbol, bar.timestamp, bar.timeframe, bar.session_mode

    def _read_partition(
        self,
        path: Path,
        *,
        reject_duplicates: bool = True,
    ) -> tuple[FiveMinuteBar, ...]:
        try:
            table = pq.read_table(path)
        except (OSError, pa.ArrowException):
            raise ProcessedDataCorruptionError(
                f"Unable to read processed Parquet partition: {path}"
            ) from None
        if not table.schema.equals(PROCESSED_FIVE_MINUTE_SCHEMA, check_metadata=False):
            raise ProcessedDataCorruptionError(
                f"Processed Parquet partition has an unexpected schema: {path}"
            )
        try:
            records = tuple(
                FiveMinuteBar.model_validate(row) for row in table.to_pylist()
            )
        except ValidationError:
            raise ProcessedDataCorruptionError(
                f"Processed Parquet partition contains invalid records: {path}"
            ) from None
        if reject_duplicates:
            identities = [self.identity(record) for record in records]
            if len(identities) != len(set(identities)):
                raise ProcessedDataCorruptionError(
                    f"Processed partition contains duplicate identities: {path}"
                )
        return records

    def _atomic_write(
        self,
        path: Path,
        records: Iterable[FiveMinuteBar],
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
            rows = [record.model_dump(mode="python") for record in records]
            table = pa.Table.from_pylist(rows, schema=PROCESSED_FIVE_MINUTE_SCHEMA)
            pq.write_table(table, temporary_path, compression="zstd", version="2.6")
            os.replace(temporary_path, path)
        except (OSError, pa.ArrowException, ValueError):
            raise ProcessedDataWriteError(
                f"Unable to atomically write processed partition: {path}"
            ) from None
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    @staticmethod
    def _validate_scope(*, symbol: str, session_mode: str) -> None:
        if (symbol, session_mode) != ("SPY", "RTH_ONLY"):
            raise ProcessedDataScopeError(
                "Processed storage supports only SPY RTH_ONLY five-minute bars"
            )


def _date_range(start: date, end: date) -> Iterable[date]:
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)
