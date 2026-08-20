from __future__ import annotations

import hashlib
import json
import socket
import subprocess
import sys
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from spy_research.alpaca.models import StockBar
from spy_research.cli import main
from spy_research.config import load_research_config
from spy_research.data.raw_store import RawBarStore
from spy_research.data.schemas import RawBarRecord
from spy_research.data.validation import RawDataValidator, ValidationSeverity


def bar(timestamp: datetime) -> RawBarRecord:
    return RawBarRecord(
        symbol="SPY",
        timestamp=timestamp,
        open=Decimal("100"),
        high=Decimal("101"),
        low=Decimal("99"),
        close=Decimal("100.5"),
        volume=100,
        trade_count=10,
        vwap=Decimal("100.25"),
        source="alpaca",
        feed="sip",
        timeframe="1Min",
        adjustment="raw",
    )


def rth_bars(session_date: date, *, close_hour_utc: int) -> list[RawBarRecord]:
    open_hour = 13 if session_date.month in range(3, 11) else 14
    start = datetime(
        session_date.year, session_date.month, session_date.day, open_hour, 30,
        tzinfo=UTC,
    )
    end = datetime(
        session_date.year, session_date.month, session_date.day, close_hour_utc, 0,
        tzinfo=UTC,
    )
    count = int((end - start).total_seconds() // 60)
    return [bar(start + timedelta(minutes=minute)) for minute in range(count)]


def issue_codes(report) -> set[str]:
    return {issue.code for issue in report.issues}


def test_market_package_imports_in_fresh_process() -> None:
    result = subprocess.run(
        [sys.executable, "-c", "import spy_research.market"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


@pytest.fixture(scope="module")
def validator() -> RawDataValidator:
    return RawDataValidator()


def test_valid_normal_session(validator) -> None:
    bars = rth_bars(date(2026, 8, 19), close_hour_utc=20)
    report = validator.validate_raw_bars(
        bars, symbol="SPY", start_date=date(2026, 8, 19), end_date=date(2026, 8, 19)
    )
    assert report.passed
    assert report.expected_rth_bars == 390
    assert report.observed_rth_bars == 390
    assert report.missing_rth_bars == 0


def test_valid_early_close_session(validator) -> None:
    bars = rth_bars(date(2025, 11, 28), close_hour_utc=18)
    report = validator.validate_raw_bars(
        bars, symbol="SPY", start_date=date(2025, 11, 28), end_date=date(2025, 11, 28)
    )
    assert report.passed
    assert report.expected_rth_bars == 210
    assert report.observed_rth_bars == 210
    assert report.info_count == 1
    assert "EARLY_CLOSE_SESSION" in issue_codes(report)


@pytest.mark.parametrize("missing_indices", [(47,), (47, 312)])
def test_missing_rth_minutes_are_exact_errors(validator, missing_indices) -> None:
    bars = rth_bars(date(2026, 8, 19), close_hour_utc=20)
    missing = [bars[index].timestamp for index in missing_indices]
    bars = [value for index, value in enumerate(bars) if index not in missing_indices]
    report = validator.validate_raw_bars(
        bars, symbol="SPY", start_date=date(2026, 8, 19), end_date=date(2026, 8, 19)
    )
    issue = next(item for item in report.issues if item.code == "MISSING_RTH_MINUTES")
    assert not report.passed
    assert report.missing_rth_bars == len(missing)
    rendered = " ".join(issue.details["missing_ranges"])
    assert all(timestamp.isoformat() in rendered for timestamp in missing)


def test_entire_expected_session_missing(validator) -> None:
    report = validator.validate_raw_bars(
        [], symbol="SPY", start_date=date(2026, 8, 19), end_date=date(2026, 8, 19)
    )
    assert not report.passed
    assert report.sessions_present == 0
    assert report.missing_rth_bars == 390
    assert "MISSING_EXPECTED_SESSION" in issue_codes(report)


@pytest.mark.parametrize("non_session", [date(2026, 8, 22), date(2026, 12, 25)])
def test_weekend_and_holiday_are_not_missing_sessions(validator, non_session) -> None:
    report = validator.validate_raw_bars(
        [], symbol="SPY", start_date=non_session, end_date=non_session
    )
    assert report.passed
    assert report.expected_sessions == 0
    assert report.missing_rth_bars == 0


def test_duplicate_key_and_timestamp_fail(validator) -> None:
    bars = rth_bars(date(2026, 8, 19), close_hour_utc=20)
    bars.insert(1, bars[0])
    report = validator.validate_raw_bars(
        bars, symbol="SPY", start_date=date(2026, 8, 19), end_date=date(2026, 8, 19)
    )
    assert not report.passed
    assert report.duplicate_keys == 1
    assert {"DUPLICATE_TIMESTAMP", "DUPLICATE_UNIQUE_KEY"} <= issue_codes(report)


def test_out_of_order_timestamp_fails_without_validator_sorting(validator) -> None:
    bars = rth_bars(date(2026, 8, 19), close_hour_utc=20)
    bars[1], bars[2] = bars[2], bars[1]
    report = validator.validate_raw_bars(
        bars, symbol="SPY", start_date=date(2026, 8, 19), end_date=date(2026, 8, 19)
    )
    assert not report.passed
    assert "OUT_OF_ORDER_TIMESTAMP" in issue_codes(report)


@pytest.mark.parametrize(
    ("updates", "code"),
    [
        ({"high": Decimal("98")}, "INVALID_OHLC_HIGH"),
        ({"high": Decimal("99.5")}, "INVALID_OHLC_HIGH"),
        ({"low": Decimal("101")}, "INVALID_OHLC_LOW"),
        ({"open": Decimal("0")}, "NON_POSITIVE_PRICE"),
        ({"close": Decimal("-1")}, "NON_POSITIVE_PRICE"),
        ({"high": Decimal("NaN")}, "NON_FINITE_PRICE"),
        ({"volume": -1}, "NEGATIVE_VOLUME"),
        ({"trade_count": -1}, "NEGATIVE_TRADE_COUNT"),
        ({"vwap": Decimal("0")}, "INVALID_VWAP"),
        ({"vwap": Decimal("Infinity")}, "INVALID_VWAP"),
    ],
)
def test_invalid_bar_values_fail(validator, updates, code) -> None:
    bars = rth_bars(date(2026, 8, 19), close_hour_utc=20)
    bars[0] = bars[0].model_copy(update=updates)
    report = validator.validate_raw_bars(
        bars, symbol="SPY", start_date=date(2026, 8, 19), end_date=date(2026, 8, 19)
    )
    assert not report.passed
    assert code in issue_codes(report)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("symbol", "QQQ"),
        ("source", "other"),
        ("feed", "iex"),
        ("timeframe", "5Min"),
        ("adjustment", "split"),
    ],
)
def test_provenance_mismatch_fails(validator, field, value) -> None:
    bars = rth_bars(date(2026, 8, 19), close_hour_utc=20)
    bars[0] = bars[0].model_copy(update={field: value})
    report = validator.validate_raw_bars(
        bars, symbol="SPY", start_date=date(2026, 8, 19), end_date=date(2026, 8, 19)
    )
    assert not report.passed
    issue = next(item for item in report.issues if item.code == "PROVENANCE_MISMATCH")
    assert issue.details["field"] == field


@pytest.mark.parametrize(
    "timestamp",
    [
        datetime(2026, 8, 19, 13, 30, 1, tzinfo=UTC),
        datetime(2026, 8, 19, 13, 30, 0, 1, tzinfo=UTC),
    ],
)
def test_timestamp_alignment_fails(validator, timestamp) -> None:
    bars = rth_bars(date(2026, 8, 19), close_hour_utc=20)
    bars[0] = bars[0].model_copy(update={"timestamp": timestamp})
    report = validator.validate_raw_bars(
        bars, symbol="SPY", start_date=date(2026, 8, 19), end_date=date(2026, 8, 19)
    )
    assert not report.passed
    assert "TIMESTAMP_NOT_MINUTE_ALIGNED" in issue_codes(report)


def test_non_session_bar_is_error(validator) -> None:
    saturday = date(2026, 8, 22)
    report = validator.validate_raw_bars(
        [bar(datetime(2026, 8, 22, 14, 0, tzinfo=UTC))],
        symbol="SPY", start_date=saturday, end_date=saturday,
    )
    assert not report.passed
    assert "NON_SESSION_BAR" in issue_codes(report)


def test_outside_session_bar_is_visible_warning_not_failure(validator) -> None:
    bars = rth_bars(date(2026, 8, 19), close_hour_utc=20)
    bars.append(bar(datetime(2026, 8, 20, 0, 0, tzinfo=UTC)))
    report = validator.validate_raw_bars(
        bars, symbol="SPY", start_date=date(2026, 8, 19), end_date=date(2026, 8, 19)
    )
    assert report.passed
    assert report.warning_count == 1
    assert "OUTSIDE_SESSION_BAR" in issue_codes(report)


def test_sparse_extended_hours_do_not_fail(validator) -> None:
    bars = [bar(datetime(2026, 8, 19, 8, 0, tzinfo=UTC))]
    bars.extend(rth_bars(date(2026, 8, 19), close_hour_utc=20))
    bars.append(bar(datetime(2026, 8, 19, 23, 59, tzinfo=UTC)))
    report = validator.validate_raw_bars(
        bars, symbol="SPY", start_date=date(2026, 8, 19), end_date=date(2026, 8, 19)
    )
    assert report.passed
    assert report.warning_count == 0
    assert report.session_stats[0].premarket_bars == 1
    assert report.session_stats[0].premarket_missing_minutes == 329
    assert report.session_stats[0].after_hours_bars == 1
    assert report.session_stats[0].after_hours_missing_minutes == 239


def test_dst_session_completeness_uses_edt_open(validator) -> None:
    bars = rth_bars(date(2026, 3, 16), close_hour_utc=20)
    report = validator.validate_raw_bars(
        bars, symbol="SPY", start_date=date(2026, 3, 16), end_date=date(2026, 3, 16)
    )
    assert report.passed
    assert report.session_stats[0].market_open.hour == 13
    assert report.expected_rth_bars == 390


def test_report_is_deterministic_json_serializable(validator) -> None:
    bars = rth_bars(date(2026, 8, 19), close_hour_utc=20)
    report = validator.validate_raw_bars(
        bars, symbol="SPY", start_date=date(2026, 8, 19), end_date=date(2026, 8, 19)
    )
    first = report.model_dump_json()
    second = report.model_dump_json()
    assert first == second
    assert json.loads(first)["passed"] is True


def _stock_bars(records: list[RawBarRecord]) -> list[StockBar]:
    return [
        StockBar(
            symbol=value.symbol,
            timestamp=value.timestamp,
            open=value.open,
            high=value.high,
            low=value.low,
            close=value.close,
            volume=value.volume,
            trade_count=value.trade_count,
            vwap=value.vwap,
        )
        for value in records
    ]


@pytest.mark.parametrize(("missing", "expected_exit"), [(False, 0), (True, 1)])
def test_validate_data_cli_exit_codes_and_offline_behavior(
    tmp_path, monkeypatch, capsys, missing, expected_exit
) -> None:
    config = load_research_config()
    store = RawBarStore(config, root=tmp_path / "raw")
    records = rth_bars(date(2026, 8, 19), close_hour_utc=20)
    if missing:
        records.pop(47)
    store.persist_bars(_stock_bars(records))

    def reject_network(*args, **kwargs):
        raise AssertionError("validate-data must not open a network connection")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main([
        "validate-data", "--start", "2026-08-19", "--end", "2026-08-19",
        "--data-root", str(tmp_path / "raw"),
    ])
    captured = capsys.readouterr()
    assert exit_code == expected_exit
    assert f"Status: {'FAIL' if missing else 'PASS'}" in captured.out
    assert captured.err == ""


def test_validate_data_json_has_no_credentials(tmp_path, monkeypatch, capsys) -> None:
    api_key = "validation-api-credential-must-not-appear"
    secret_key = "validation-secret-credential-must-not-appear"
    monkeypatch.setenv("ALPACA_API_KEY", api_key)
    monkeypatch.setenv("ALPACA_SECRET_KEY", secret_key)
    config = load_research_config()
    store = RawBarStore(config, root=tmp_path / "raw")
    store.persist_bars(
        _stock_bars(rth_bars(date(2026, 8, 19), close_hour_utc=20))
    )
    exit_code = main([
        "validate-data", "--start", "2026-08-19", "--end", "2026-08-19",
        "--data-root", str(tmp_path / "raw"), "--json",
    ])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out)["passed"] is True
    assert api_key not in captured.out
    assert secret_key not in captured.out


def test_validation_does_not_change_parquet_bytes(tmp_path, validator) -> None:
    config = load_research_config()
    store = RawBarStore(config, root=tmp_path / "raw")
    store.persist_bars(
        _stock_bars(rth_bars(date(2026, 8, 19), close_hour_utc=20))
    )
    path = store.partition_path(date(2026, 8, 19))
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    report = validator.validate_raw_store(
        store, symbol="SPY", start_date=date(2026, 8, 19), end_date=date(2026, 8, 19)
    )
    after = hashlib.sha256(path.read_bytes()).hexdigest()
    assert report.passed
    assert before == after


def test_partition_date_mismatch_is_error(validator) -> None:
    value = bar(datetime(2026, 8, 19, 13, 30, tzinfo=UTC))
    report = validator.validate_raw_bars(
        [value], symbol="SPY", start_date=date(2026, 8, 19),
        end_date=date(2026, 8, 19), partition_dates=[date(2026, 8, 20)],
    )
    assert not report.passed
    assert "PARTITION_DATE_MISMATCH" in issue_codes(report)


def test_corrupted_partition_is_validation_error(tmp_path, validator) -> None:
    config = load_research_config()
    store = RawBarStore(config, root=tmp_path / "raw")
    path = store.partition_path(date(2026, 8, 19))
    path.parent.mkdir(parents=True)
    path.write_bytes(b"not parquet")

    report = validator.validate_raw_store(
        store,
        symbol="SPY",
        start_date=date(2026, 8, 19),
        end_date=date(2026, 8, 19),
    )
    assert not report.passed
    assert "CORRUPTED_PARTITION" in issue_codes(report)


def test_zero_volume_and_trade_count_are_allowed(validator) -> None:
    bars = rth_bars(date(2026, 8, 19), close_hour_utc=20)
    bars[0] = bars[0].model_copy(update={"volume": 0, "trade_count": 0})
    report = validator.validate_raw_bars(
        bars, symbol="SPY", start_date=date(2026, 8, 19), end_date=date(2026, 8, 19)
    )
    assert report.passed
    assert all(issue.severity is not ValidationSeverity.ERROR for issue in report.issues)
