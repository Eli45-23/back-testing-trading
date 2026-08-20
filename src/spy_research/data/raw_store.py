"""Idempotent, atomic Parquet persistence for raw Alpaca stock bars."""

from __future__ import annotations

import os
import tempfile
from collections import defaultdict
from collections.abc import Iterable, Sequence
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pyarrow as pa
import pyarrow.parquet as pq
from pydantic import ValidationError

from spy_research.alpaca.models import StockBar
from spy_research.config import PROJECT_ROOT, ResearchConfig
from spy_research.data.errors import (
    RawDataConflictError,
    RawDataCorruptionError,
    RawDataScopeError,
    RawDataWriteError,
)
from spy_research.data.schemas import (
    RAW_BAR_SCHEMA,
    PersistenceResult,
    RawBarRecord,
)


DEFAULT_RAW_DATA_ROOT = PROJECT_ROOT / "data" / "raw"


class RawBarStore:
    """Daily raw-bar partitions for the frozen SPY/Alpaca/SIP/1Min scope."""

    def __init__(
        self,
        config: ResearchConfig,
        *,
        root: str | Path = DEFAULT_RAW_DATA_ROOT,
    ) -> None:
        self._config = config
        self._root = Path(root)
        self._timezone = ZoneInfo(config.session.timezone)
        self._base_path = (
            self._root
            / config.data.source
            / config.symbol.lower()
            / config.data.timeframe.lower()
        )

    def partition_path(self, partition_date: date) -> Path:
        return (
            self._base_path
            / f"{partition_date:%Y}"
            / f"{partition_date:%m}"
            / f"{partition_date.isoformat()}.parquet"
        )

    def persist_bars(self, bars: Sequence[StockBar]) -> PersistenceResult:
        """Merge bars without duplication and atomically replace changed partitions."""

        incoming_by_date: dict[date, list[RawBarRecord]] = defaultdict(list)
        for bar in bars:
            record = RawBarRecord.from_stock_bar(bar, self._config)
            partition_date = record.timestamp.astimezone(self._timezone).date()
            incoming_by_date[partition_date].append(record)

        existing_identical = 0
        new_bars = 0
        conflicts = 0
        write_plans: dict[Path, tuple[RawBarRecord, ...]] = {}

        for partition_date, incoming_records in incoming_by_date.items():
            path = self.partition_path(partition_date)
            existing_records = self._read_partition(path) if path.exists() else ()
            existing_by_key = {record.unique_key: record for record in existing_records}
            incoming_unique: dict[tuple[str, Any, str, str], RawBarRecord] = {}
            partition_has_new_bars = False

            for record in incoming_records:
                earlier_in_batch = incoming_unique.get(record.unique_key)
                if earlier_in_batch is not None:
                    if earlier_in_batch == record:
                        existing_identical += 1
                        continue
                    conflicts += 1
                    continue
                incoming_unique[record.unique_key] = record

                stored = existing_by_key.get(record.unique_key)
                if stored is None:
                    existing_by_key[record.unique_key] = record
                    new_bars += 1
                    partition_has_new_bars = True
                elif stored == record:
                    existing_identical += 1
                else:
                    conflicts += 1

            if partition_has_new_bars:
                write_plans[path] = tuple(
                    sorted(existing_by_key.values(), key=lambda item: item.timestamp)
                )

        if conflicts:
            raise RawDataConflictError(conflicts)

        written_paths: list[Path] = []
        for path, records in sorted(write_plans.items()):
            self._atomic_write(path, records)
            written_paths.append(path)

        return PersistenceResult(
            bars_received=len(bars),
            new_bars=new_bars,
            existing_identical=existing_identical,
            conflicts=0,
            partitions_written=len(written_paths),
            partition_paths=tuple(written_paths),
        )

    def load_raw_bars(
        self,
        *,
        symbol: str,
        start: date,
        end: date,
        feed: str = "sip",
        timeframe: str = "1Min",
    ) -> tuple[RawBarRecord, ...]:
        """Load available daily partitions without contacting Alpaca."""

        self._validate_scope(symbol=symbol, feed=feed, timeframe=timeframe)
        if start > end:
            raise ValueError("start date must be on or before end date")

        records: list[RawBarRecord] = []
        for partition_date in self._date_range(start, end):
            path = self.partition_path(partition_date)
            if path.exists():
                records.extend(self._read_partition(path))

        ordered = tuple(sorted(records, key=lambda item: item.timestamp))
        seen: set[tuple[str, Any, str, str]] = set()
        for record in ordered:
            if record.unique_key in seen:
                raise RawDataCorruptionError(
                    "Duplicate raw bar key detected while loading Parquet partitions"
                )
            seen.add(record.unique_key)
        return ordered

    def load_partition(self, partition_date: date) -> tuple[RawBarRecord, ...]:
        """Read one New York-date partition without sorting or contacting Alpaca."""

        path = self.partition_path(partition_date)
        return self._read_partition(path) if path.exists() else ()

    def _read_partition(self, path: Path) -> tuple[RawBarRecord, ...]:
        try:
            table = pq.read_table(path)
        except (OSError, pa.ArrowException):
            raise RawDataCorruptionError(
                f"Unable to read raw Parquet partition: {path}"
            ) from None

        if not table.schema.equals(RAW_BAR_SCHEMA, check_metadata=False):
            raise RawDataCorruptionError(
                f"Raw Parquet partition has an unexpected schema: {path}"
            )

        try:
            records = tuple(
                RawBarRecord.model_validate(row) for row in table.to_pylist()
            )
        except ValidationError:
            raise RawDataCorruptionError(
                f"Raw Parquet partition contains invalid records: {path}"
            ) from None
        if len({record.unique_key for record in records}) != len(records):
            raise RawDataCorruptionError(
                f"Raw Parquet partition contains duplicate keys: {path}"
            )
        return records

    def _atomic_write(self, path: Path, records: Iterable[RawBarRecord]) -> None:
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
            table = pa.Table.from_pylist(rows, schema=RAW_BAR_SCHEMA)
            pq.write_table(table, temporary_path, compression="zstd", version="2.6")
            os.replace(temporary_path, path)
        except (OSError, pa.ArrowException, ValueError):
            raise RawDataWriteError(
                f"Unable to atomically write raw Parquet partition: {path}"
            ) from None
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def _validate_scope(self, *, symbol: str, feed: str, timeframe: str) -> None:
        expected = (
            self._config.symbol,
            self._config.data.feed,
            self._config.data.timeframe,
        )
        if (symbol, feed, timeframe) != expected:
            raise RawDataScopeError(
                "Raw storage supports only SPY with Alpaca SIP 1Min data"
            )

    @staticmethod
    def _date_range(start: date, end: date) -> Iterable[date]:
        current = start
        while current <= end:
            yield current
            current += timedelta(days=1)
