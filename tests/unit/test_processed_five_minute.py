from __future__ import annotations

import hashlib
import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from spy_research.alpaca.models import StockBar
from spy_research.bars import (
    PROCESSED_FIVE_MINUTE_SCHEMA,
    FiveMinuteBuildService,
    ProcessedDataConflictError,
    ProcessedDataCorruptionError,
    ProcessedDataScopeError,
    ProcessedDataWriteError,
    ProcessedFiveMinuteStore,
    ProcessedFiveMinuteValidator,
    aggregate_rth_1m_to_5m,
)
from spy_research.cli import main
from spy_research.config import load_research_config
from spy_research.data.raw_store import RawBarStore
from spy_research.data.schemas import RawBarRecord
from spy_research.market import ClassifiedRawBar, SessionType, XNYSCalendar


NORMAL_DATE = date(2026, 8, 19)
EARLY_DATE = date(2025, 11, 28)
BASE_PRICE = Decimal("100.123456789012")


def raw_record(timestamp: datetime, index: int) -> RawBarRecord:
    step = Decimal(index % 5) / Decimal("10")
    return RawBarRecord(
        symbol="SPY",
        timestamp=timestamp,
        open=BASE_PRICE + step,
        high=BASE_PRICE + step + Decimal("0.3"),
        low=BASE_PRICE + step - Decimal("0.2"),
        close=BASE_PRICE + step + Decimal("0.1"),
        volume=1000 + index,
        trade_count=20 + index,
        vwap=BASE_PRICE + step + Decimal("0.05"),
        source="alpaca",
        feed="sip",
        timeframe="1Min",
        adjustment="raw",
    )


def source_and_processed(session_date: date):
    session = XNYSCalendar().session_for_date(session_date)
    assert session.market_open is not None and session.market_close is not None
    count = int((session.market_close - session.market_open).total_seconds() // 60)
    source = [
        ClassifiedRawBar(
            bar=raw_record(
                session.market_open + timedelta(minutes=index),
                index,
            ),
            session_date=session_date,
            session_type=SessionType.RTH,
        )
        for index in range(count)
    ]
    return source, list(aggregate_rth_1m_to_5m(source, session))


def stock_bars(source) -> list[StockBar]:
    return [
        StockBar(
            symbol=item.bar.symbol,
            timestamp=item.bar.timestamp,
            open=item.bar.open,
            high=item.bar.high,
            low=item.bar.low,
            close=item.bar.close,
            volume=item.bar.volume,
            trade_count=item.bar.trade_count,
            vwap=item.bar.vwap,
        )
        for item in source
    ]


def issue_codes(report) -> set[str]:
    return {issue.code for issue in report.issues}


def make_processed_store(tmp_path) -> ProcessedFiveMinuteStore:
    return ProcessedFiveMinuteStore(root=tmp_path / "processed")


def make_raw_store(tmp_path, source) -> RawBarStore:
    config = load_research_config()
    store = RawBarStore(config, root=tmp_path / "raw")
    store.persist_bars(stock_bars(source))
    return store


def test_processed_partition_exact_round_trip_and_layout(tmp_path) -> None:
    store = make_processed_store(tmp_path)
    _, bars = source_and_processed(NORMAL_DATE)
    result = store.persist_bars(bars)
    loaded = store.load_processed_5m_bars(
        symbol="SPY", start=NORMAL_DATE, end=NORMAL_DATE
    )
    expected_path = (
        tmp_path
        / "processed"
        / "spy"
        / "5min"
        / "rth"
        / "2026"
        / "08"
        / "2026-08-19.parquet"
    )

    assert result.new_bars == 78
    assert result.partitions_written == 1
    assert result.partition_paths == (expected_path,)
    assert loaded == tuple(bars)
    assert loaded[0].timestamp == bars[0].timestamp
    assert loaded[0].open == bars[0].open
    assert loaded[0].high == bars[0].high
    assert loaded[0].low == bars[0].low
    assert loaded[0].close == bars[0].close
    assert loaded[0].volume == bars[0].volume
    assert loaded[0].trade_count == bars[0].trade_count
    assert loaded[0].source_bar_count == 5
    assert loaded[0].session_type == "RTH"
    assert loaded[0].session_mode == "RTH_ONLY"
    assert loaded[0].source_timeframe == "1Min"
    assert loaded[0].aggregation_method == "rth_1m_to_5m_v1"


def test_processed_loader_returns_chronological_bars(tmp_path) -> None:
    store = make_processed_store(tmp_path)
    _, bars = source_and_processed(NORMAL_DATE)
    store.persist_bars(list(reversed(bars)))
    loaded = store.load_processed_5m_bars(
        symbol="SPY", start=NORMAL_DATE, end=NORMAL_DATE
    )
    assert tuple(item.timestamp for item in loaded) == tuple(
        sorted(item.timestamp for item in loaded)
    )


def test_processed_persistence_is_idempotent_without_rewrite(tmp_path) -> None:
    store = make_processed_store(tmp_path)
    _, bars = source_and_processed(NORMAL_DATE)
    first = store.persist_bars(bars)
    path = store.partition_path(NORMAL_DATE)
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    second = store.persist_bars(bars)
    after = hashlib.sha256(path.read_bytes()).hexdigest()
    assert first.new_bars == 78
    assert second.new_bars == 0
    assert second.existing_identical == 78
    assert second.partitions_written == 0
    assert before == after


def test_processed_conflict_is_rejected_without_overwrite(tmp_path) -> None:
    store = make_processed_store(tmp_path)
    _, bars = source_and_processed(NORMAL_DATE)
    store.persist_bars(bars)
    path = store.partition_path(NORMAL_DATE)
    before = path.read_bytes()
    changed = bars[0].model_copy(update={"close": bars[0].close + Decimal("0.01")})
    with pytest.raises(ProcessedDataConflictError) as exc_info:
        store.persist_bars([changed])
    assert exc_info.value.conflict_count == 1
    assert path.read_bytes() == before


def test_duplicate_stored_identity_is_rejected_and_reported(tmp_path) -> None:
    store = make_processed_store(tmp_path)
    _, bars = source_and_processed(NORMAL_DATE)
    path = store.partition_path(NORMAL_DATE)
    path.parent.mkdir(parents=True)
    rows = [bars[0].model_dump(mode="python")] * 2
    pq.write_table(pa.Table.from_pylist(rows, schema=PROCESSED_FIVE_MINUTE_SCHEMA), path)

    with pytest.raises(ProcessedDataCorruptionError, match="duplicate identities"):
        store.load_processed_5m_bars(
            symbol="SPY", start=NORMAL_DATE, end=NORMAL_DATE
        )
    report = ProcessedFiveMinuteValidator().validate_store(
        store, start=NORMAL_DATE, end=NORMAL_DATE
    )
    assert not report.passed
    assert report.duplicate_bars == 1
    assert "DUPLICATE_PROCESSED_IDENTITY" in issue_codes(report)


def test_corrupted_processed_parquet_is_validation_error(tmp_path) -> None:
    store = make_processed_store(tmp_path)
    path = store.partition_path(NORMAL_DATE)
    path.parent.mkdir(parents=True)
    path.write_bytes(b"not parquet")
    with pytest.raises(ProcessedDataCorruptionError, match="Unable to read"):
        store.load_processed_5m_bars(
            symbol="SPY", start=NORMAL_DATE, end=NORMAL_DATE
        )
    report = ProcessedFiveMinuteValidator().validate_store(
        store, start=NORMAL_DATE, end=NORMAL_DATE
    )
    assert "CORRUPTED_PROCESSED_PARTITION" in issue_codes(report)


def test_failed_atomic_write_cleans_temp_and_preserves_partition(
    tmp_path, monkeypatch
) -> None:
    store = make_processed_store(tmp_path)
    _, bars = source_and_processed(NORMAL_DATE)
    store.persist_bars([bars[0]])
    path = store.partition_path(NORMAL_DATE)
    before = path.read_bytes()

    def fail_write(*args, **kwargs):
        raise OSError("simulated")

    monkeypatch.setattr("spy_research.bars.store.pq.write_table", fail_write)
    with pytest.raises(ProcessedDataWriteError, match="atomically write"):
        store.persist_bars([bars[1]])
    assert path.read_bytes() == before
    assert list(path.parent.glob(f".{path.name}.*.tmp")) == []


@pytest.mark.parametrize(
    ("symbol", "mode"),
    [("QQQ", "RTH_ONLY"), ("SPY", "ALL")],
)
def test_processed_scope_is_frozen(tmp_path, symbol, mode) -> None:
    with pytest.raises(ProcessedDataScopeError):
        make_processed_store(tmp_path).load_processed_5m_bars(
            symbol=symbol,
            start=NORMAL_DATE,
            end=NORMAL_DATE,
            session_mode=mode,
        )


@pytest.mark.parametrize(
    ("session_date", "expected"),
    [(NORMAL_DATE, 78), (EARLY_DATE, 42)],
)
def test_processed_calendar_completeness(session_date, expected) -> None:
    _, bars = source_and_processed(session_date)
    report = ProcessedFiveMinuteValidator().validate_bars(
        bars, start=session_date, end=session_date
    )
    assert report.passed
    assert report.expected_bars == expected
    assert report.total_bars == expected


def test_missing_processed_candle_is_exact_error() -> None:
    _, bars = source_and_processed(NORMAL_DATE)
    missing = bars.pop(20).timestamp
    report = ProcessedFiveMinuteValidator().validate_bars(
        bars, start=NORMAL_DATE, end=NORMAL_DATE
    )
    issue = next(item for item in report.issues if item.code == "MISSING_PROCESSED_BARS")
    assert not report.passed
    assert report.missing_bars == 1
    assert missing.isoformat() in issue.details["missing_timestamps"]


def test_misaligned_processed_timestamp_fails() -> None:
    _, bars = source_and_processed(NORMAL_DATE)
    bars[0] = bars[0].model_copy(
        update={"timestamp": bars[0].timestamp + timedelta(minutes=1)}
    )
    report = ProcessedFiveMinuteValidator().validate_bars(
        bars, start=NORMAL_DATE, end=NORMAL_DATE
    )
    assert not report.passed
    assert "EXTRA_PROCESSED_BARS" in issue_codes(report)


@pytest.mark.parametrize(
    ("updates", "code"),
    [
        ({"high": Decimal("1")}, "INVALID_PROCESSED_HIGH"),
        ({"low": Decimal("1000")}, "INVALID_PROCESSED_LOW"),
        ({"open": Decimal("0")}, "NON_POSITIVE_PROCESSED_PRICE"),
        ({"high": Decimal("NaN")}, "NON_FINITE_PROCESSED_PRICE"),
        ({"volume": -1}, "NEGATIVE_PROCESSED_VOLUME"),
        ({"trade_count": -1}, "NEGATIVE_PROCESSED_TRADE_COUNT"),
    ],
)
def test_invalid_processed_values_fail(updates, code) -> None:
    _, bars = source_and_processed(NORMAL_DATE)
    bars[0] = bars[0].model_copy(update=updates)
    report = ProcessedFiveMinuteValidator().validate_bars(
        bars, start=NORMAL_DATE, end=NORMAL_DATE
    )
    assert not report.passed
    assert code in issue_codes(report)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("symbol", "QQQ"),
        ("source", "other"),
        ("feed", "iex"),
        ("source_timeframe", "5Min"),
        ("timeframe", "1Min"),
        ("adjustment", "split"),
        ("source_bar_count", 4),
        ("session_type", "AFTER_HOURS"),
        ("session_mode", "ALL"),
        ("aggregation_method", "other"),
    ],
)
def test_invalid_processed_provenance_fails(field, value) -> None:
    _, bars = source_and_processed(NORMAL_DATE)
    bars[0] = bars[0].model_copy(update={field: value})
    report = ProcessedFiveMinuteValidator().validate_bars(
        bars, start=NORMAL_DATE, end=NORMAL_DATE
    )
    assert not report.passed
    issue = next(
        item
        for item in report.issues
        if item.code == "PROCESSED_PROVENANCE_MISMATCH"
    )
    assert issue.details["field"] == field


def test_partition_session_date_mismatch_fails() -> None:
    _, bars = source_and_processed(NORMAL_DATE)
    report = ProcessedFiveMinuteValidator().validate_bars(
        bars,
        start=NORMAL_DATE,
        end=NORMAL_DATE,
        partition_dates=[date(2026, 8, 18)] * len(bars),
    )
    assert not report.passed
    assert "PROCESSED_PARTITION_DATE_MISMATCH" in issue_codes(report)


def test_processed_order_and_duplicate_identity_fail() -> None:
    _, bars = source_and_processed(NORMAL_DATE)
    bars[0], bars[1] = bars[1], bars[0]
    bars.insert(2, bars[0])
    report = ProcessedFiveMinuteValidator().validate_bars(
        bars, start=NORMAL_DATE, end=NORMAL_DATE
    )
    assert not report.passed
    assert report.duplicate_bars == 1
    assert "OUT_OF_ORDER_PROCESSED_TIMESTAMP" in issue_codes(report)


def test_exact_raw_processed_reconciliation_passes(tmp_path) -> None:
    source, bars = source_and_processed(NORMAL_DATE)
    raw_store = make_raw_store(tmp_path, source)
    processed_store = make_processed_store(tmp_path)
    processed_store.persist_bars(bars)
    report = ProcessedFiveMinuteValidator().validate_store(
        processed_store,
        start=NORMAL_DATE,
        end=NORMAL_DATE,
        reconcile=True,
        config=load_research_config(),
        raw_store=raw_store,
    )
    assert report.passed
    assert report.reconciliation_errors == 0


@pytest.mark.parametrize("field", ["close", "volume"])
def test_modified_processed_content_fails_reconciliation(field) -> None:
    _, expected = source_and_processed(NORMAL_DATE)
    actual = list(expected)
    update = (
        {"close": actual[10].close + Decimal("0.01")}
        if field == "close"
        else {"volume": actual[10].volume + 1}
    )
    actual[10] = actual[10].model_copy(update=update)
    report = ProcessedFiveMinuteValidator().validate_bars(
        actual,
        start=NORMAL_DATE,
        end=NORMAL_DATE,
        expected_reaggregated=expected,
    )
    assert not report.passed
    assert report.reconciliation_errors == 1
    assert "RAW_PROCESSED_RECONCILIATION_MISMATCH" in issue_codes(report)


def test_build_does_not_mutate_raw_partition(tmp_path) -> None:
    source, _ = source_and_processed(NORMAL_DATE)
    raw_store = make_raw_store(tmp_path, source)
    processed_store = make_processed_store(tmp_path)
    raw_path = raw_store.partition_path(NORMAL_DATE)
    before = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    result = FiveMinuteBuildService(
        load_research_config(), raw_store, processed_store
    ).build(start=NORMAL_DATE, end=NORMAL_DATE)
    after = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    assert result.validation.passed
    assert before == after


def test_build_and_validation_clis_are_offline_idempotent_and_secret_free(
    tmp_path, monkeypatch, capsys
) -> None:
    api_key = "processed-api-credential-must-not-appear"
    secret_key = "processed-secret-credential-must-not-appear"
    monkeypatch.setenv("ALPACA_API_KEY", api_key)
    monkeypatch.setenv("ALPACA_SECRET_KEY", secret_key)
    source, _ = source_and_processed(NORMAL_DATE)
    raw_store = make_raw_store(tmp_path, source)
    processed_root = tmp_path / "processed"

    def reject_network(*args, **kwargs):
        raise AssertionError("processed CLIs must not open a network connection")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    command = [
        "build-5m",
        "--start",
        NORMAL_DATE.isoformat(),
        "--end",
        NORMAL_DATE.isoformat(),
        "--raw-data-root",
        str(tmp_path / "raw"),
        "--processed-data-root",
        str(processed_root),
    ]
    first_exit = main(command)
    first = capsys.readouterr()
    first_hash = hashlib.sha256(
        ProcessedFiveMinuteStore(root=processed_root)
        .partition_path(NORMAL_DATE)
        .read_bytes()
    ).hexdigest()
    second_exit = main(command)
    second = capsys.readouterr()
    second_hash = hashlib.sha256(
        ProcessedFiveMinuteStore(root=processed_root)
        .partition_path(NORMAL_DATE)
        .read_bytes()
    ).hexdigest()
    validation_exit = main(
        [
            "validate-5m",
            "--start",
            NORMAL_DATE.isoformat(),
            "--end",
            NORMAL_DATE.isoformat(),
            "--raw-data-root",
            str(tmp_path / "raw"),
            "--processed-data-root",
            str(processed_root),
            "--json",
        ]
    )
    validation = capsys.readouterr()
    validation_hash = hashlib.sha256(
        ProcessedFiveMinuteStore(root=processed_root)
        .partition_path(NORMAL_DATE)
        .read_bytes()
    ).hexdigest()
    combined = first.out + second.out + validation.out
    assert first_exit == second_exit == validation_exit == 0
    assert "New processed bars: 78" in first.out
    assert "New processed bars: 0" in second.out
    assert "Existing identical: 78" in second.out
    assert '"passed": true' in validation.out
    assert first_hash == second_hash == validation_hash
    assert api_key not in combined
    assert secret_key not in combined


def test_processed_schema_metadata_contains_lineage_not_credentials(
    tmp_path, monkeypatch
) -> None:
    api_key = "schema-api-credential-must-not-appear"
    secret_key = "schema-secret-credential-must-not-appear"
    monkeypatch.setenv("ALPACA_API_KEY", api_key)
    monkeypatch.setenv("ALPACA_SECRET_KEY", secret_key)
    store = make_processed_store(tmp_path)
    _, bars = source_and_processed(NORMAL_DATE)
    store.persist_bars(bars)
    path = store.partition_path(NORMAL_DATE)
    table = pq.read_table(path)
    metadata = pq.read_metadata(path).metadata or {}
    serialized_metadata = b"".join(metadata.keys()) + b"".join(metadata.values())
    serialized_rows = str(table.to_pylist())
    assert table.schema.equals(PROCESSED_FIVE_MINUTE_SCHEMA, check_metadata=False)
    assert metadata[b"aggregation_method"] == b"rth_1m_to_5m_v1"
    assert metadata[b"session_mode"] == b"RTH_ONLY"
    assert api_key not in serialized_rows
    assert secret_key not in serialized_rows
    assert api_key.encode() not in serialized_metadata
    assert secret_key.encode() not in serialized_metadata
