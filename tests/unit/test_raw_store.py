from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pyarrow.parquet as pq
import pytest

from spy_research.alpaca.models import StockBar
from spy_research.config import load_research_config, load_settings
from spy_research.data.errors import (
    RawDataConflictError,
    RawDataCorruptionError,
    RawDataScopeError,
    RawDataWriteError,
)
from spy_research.data.raw_store import RawBarStore
from spy_research.data.schemas import RAW_BAR_SCHEMA


DAY_ONE = date(2026, 8, 19)
DAY_TWO = date(2026, 8, 20)


def bar(
    timestamp: str,
    *,
    open_price: str = "100.123456789012",
    close_price: str = "100.500000000001",
) -> StockBar:
    return StockBar(
        symbol="SPY",
        timestamp=datetime.fromisoformat(timestamp.replace("Z", "+00:00")),
        open=Decimal(open_price),
        high=Decimal("101.123456789012"),
        low=Decimal("99.123456789012"),
        close=Decimal(close_price),
        volume=1234,
        trade_count=42,
        vwap=Decimal("100.333333333333"),
    )


def make_store(tmp_path) -> RawBarStore:
    return RawBarStore(load_research_config(), root=tmp_path / "raw")


def test_write_one_partition_and_exact_typed_round_trip(tmp_path) -> None:
    store = make_store(tmp_path)
    original = bar("2026-08-19T13:30:00.123456Z")

    result = store.persist_bars((original,))
    loaded = store.load_raw_bars(symbol="SPY", start=DAY_ONE, end=DAY_ONE)

    expected_path = (
        tmp_path
        / "raw"
        / "alpaca"
        / "spy"
        / "1min"
        / "2026"
        / "08"
        / "2026-08-19.parquet"
    )
    assert result.new_bars == 1
    assert result.partitions_written == 1
    assert result.partition_paths == (expected_path,)
    assert expected_path.exists()
    assert len(loaded) == 1
    assert loaded[0].timestamp == original.timestamp
    assert loaded[0].timestamp.utcoffset() == timedelta(0)
    assert loaded[0].open == original.open
    assert loaded[0].high == original.high
    assert loaded[0].low == original.low
    assert loaded[0].close == original.close
    assert loaded[0].volume == original.volume
    assert loaded[0].trade_count == original.trade_count
    assert loaded[0].vwap == original.vwap
    assert loaded[0].source == "alpaca"
    assert loaded[0].feed == "sip"
    assert loaded[0].timeframe == "1Min"
    assert loaded[0].adjustment == "raw"


def test_loading_is_deterministically_chronological(tmp_path) -> None:
    store = make_store(tmp_path)
    later = bar("2026-08-19T13:31:00Z")
    earlier = bar("2026-08-19T13:30:00Z")

    store.persist_bars((later, earlier))
    loaded = store.load_raw_bars(symbol="SPY", start=DAY_ONE, end=DAY_ONE)

    assert [record.timestamp.minute for record in loaded] == [30, 31]


def test_identical_duplicate_in_one_batch_is_stored_once(tmp_path) -> None:
    store = make_store(tmp_path)
    original = bar("2026-08-19T13:30:00Z")

    result = store.persist_bars((original, original))
    loaded = store.load_raw_bars(symbol="SPY", start=DAY_ONE, end=DAY_ONE)

    assert result.bars_received == 2
    assert result.new_bars == 1
    assert result.existing_identical == 1
    assert len(loaded) == 1


def test_repeated_identical_persistence_is_idempotent(tmp_path) -> None:
    store = make_store(tmp_path)
    bars = (bar("2026-08-19T13:30:00Z"), bar("2026-08-19T13:31:00Z"))

    first = store.persist_bars(bars)
    second = store.persist_bars(bars)
    loaded = store.load_raw_bars(symbol="SPY", start=DAY_ONE, end=DAY_ONE)

    assert first.new_bars == 2
    assert first.existing_identical == 0
    assert first.partitions_written == 1
    assert second.new_bars == 0
    assert second.existing_identical == 2
    assert second.partitions_written == 0
    assert len(loaded) == 2


def test_conflicting_same_key_is_rejected_without_overwrite(tmp_path) -> None:
    store = make_store(tmp_path)
    original = bar("2026-08-19T13:30:00Z", close_price="100.5")
    conflicting = bar("2026-08-19T13:30:00Z", close_price="100.6")
    store.persist_bars((original,))

    with pytest.raises(RawDataConflictError) as error:
        store.persist_bars((conflicting,))

    loaded = store.load_raw_bars(symbol="SPY", start=DAY_ONE, end=DAY_ONE)
    assert error.value.conflict_count == 1
    assert loaded[0].close == original.close


def test_multi_day_bars_create_daily_partitions(tmp_path) -> None:
    store = make_store(tmp_path)
    bars = (bar("2026-08-19T13:30:00Z"), bar("2026-08-20T13:30:00Z"))

    result = store.persist_bars(bars)

    assert result.partitions_written == 2
    assert store.partition_path(DAY_ONE).exists()
    assert store.partition_path(DAY_TWO).exists()


def test_requested_range_loads_only_available_partitions(tmp_path) -> None:
    store = make_store(tmp_path)
    store.persist_bars(
        (
            bar("2026-08-19T13:30:00Z"),
            bar("2026-08-20T13:30:00Z"),
            bar("2026-08-21T13:30:00Z"),
        )
    )

    loaded = store.load_raw_bars(symbol="SPY", start=DAY_TWO, end=DAY_TWO)

    assert len(loaded) == 1
    assert loaded[0].timestamp.date() == DAY_TWO


def test_missing_date_partitions_return_empty_result(tmp_path) -> None:
    store = make_store(tmp_path)

    loaded = store.load_raw_bars(symbol="SPY", start=DAY_ONE, end=DAY_TWO)

    assert loaded == ()


def test_corrupted_parquet_file_has_clear_error(tmp_path) -> None:
    store = make_store(tmp_path)
    path = store.partition_path(DAY_ONE)
    path.parent.mkdir(parents=True)
    path.write_bytes(b"not a parquet file")

    with pytest.raises(RawDataCorruptionError, match="Unable to read raw Parquet"):
        store.load_raw_bars(symbol="SPY", start=DAY_ONE, end=DAY_ONE)


def test_failed_atomic_write_cleans_temp_and_preserves_existing_file(
    tmp_path, monkeypatch
) -> None:
    store = make_store(tmp_path)
    original = bar("2026-08-19T13:30:00Z")
    store.persist_bars((original,))
    path = store.partition_path(DAY_ONE)
    original_bytes = path.read_bytes()

    def fail_write(*args, **kwargs):
        raise OSError("simulated write failure")

    monkeypatch.setattr("spy_research.data.raw_store.pq.write_table", fail_write)

    with pytest.raises(RawDataWriteError, match="atomically write"):
        store.persist_bars((bar("2026-08-19T13:31:00Z"),))

    assert path.read_bytes() == original_bytes
    assert list(path.parent.glob(f".{path.name}.*.tmp")) == []


@pytest.mark.parametrize(
    ("field", "value"),
    [("symbol", "QQQ"), ("feed", "iex"), ("timeframe", "5Min")],
)
def test_unsupported_scope_is_rejected(tmp_path, field: str, value: str) -> None:
    store = make_store(tmp_path)
    arguments = {
        "symbol": "SPY",
        "start": DAY_ONE,
        "end": DAY_ONE,
        "feed": "sip",
        "timeframe": "1Min",
    }
    arguments[field] = value

    with pytest.raises(RawDataScopeError, match="only SPY with Alpaca SIP 1Min"):
        store.load_raw_bars(**arguments)


def test_parquet_schema_and_metadata_never_contain_credentials(
    tmp_path, monkeypatch
) -> None:
    api_key = "parquet-api-credential-must-not-appear"
    secret_key = "parquet-secret-credential-must-not-appear"
    monkeypatch.setenv("ALPACA_API_KEY", api_key)
    monkeypatch.setenv("ALPACA_SECRET_KEY", secret_key)
    settings = load_settings(env_path=None)
    store = RawBarStore(settings.research, root=tmp_path / "raw")
    store.persist_bars((bar("2026-08-19T13:30:00Z"),))
    path = store.partition_path(DAY_ONE)

    table = pq.read_table(path)
    file_metadata = pq.read_metadata(path).metadata or {}
    serialized_metadata = b"".join(file_metadata.keys()) + b"".join(
        file_metadata.values()
    )
    serialized_rows = str(table.to_pylist())

    assert table.schema.equals(RAW_BAR_SCHEMA, check_metadata=False)
    assert table.column_names == [field.name for field in RAW_BAR_SCHEMA]
    assert api_key not in serialized_rows
    assert secret_key not in serialized_rows
    assert api_key.encode() not in serialized_metadata
    assert secret_key.encode() not in serialized_metadata
