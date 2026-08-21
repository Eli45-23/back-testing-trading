import json
import re
import socket
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from spy_research.cli import main
from spy_research.alpaca.historical import HistoricalStockDataService
from spy_research.alpaca.models import HistoricalBarsResult, StockBar


def test_help_reports_foundation_commands(capsys) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--help"])

    captured = capsys.readouterr()
    assert exit_info.value.code == 0
    assert "config-check" in captured.out
    assert "download-bars" in captured.out
    assert "fetch-bars" in captured.out
    assert "run-manifest" in captured.out
    assert "session-summary" in captured.out
    assert "validate-data" in captured.out
    assert "aggregate-bars" in captured.out
    assert "build-5m" in captured.out
    assert "validate-5m" in captured.out
    assert "calculate-ema" in captured.out
    assert "calculate-vwap" in captured.out
    assert "calculate-atr" in captured.out
    assert "calculate-ema-separation" in captured.out
    assert "detect-ema-crosses" in captured.out
    assert "calculate-cross-outcomes" in captured.out
    assert "cross-stats" in captured.out
    assert "previous-day-levels" in captured.out
    assert "premarket-levels" in captured.out
    assert "opening-5m-levels" in captured.out
    assert "level-interactions" in captured.out
    assert "break-follow-through" in captured.out
    assert "sweep-patterns" in captured.out
    assert "atr-tolerance" in captured.out


def test_config_check_reports_success_without_credentials(monkeypatch, capsys) -> None:
    api_key = "cli-api-credential-that-must-not-be-shown"
    secret_key = "cli-secret-credential-that-must-not-be-shown"
    monkeypatch.setenv("ALPACA_API_KEY", api_key)
    monkeypatch.setenv("ALPACA_SECRET_KEY", secret_key)

    exit_code = main(["config-check"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Configuration valid" in captured.out
    assert api_key not in captured.out
    assert secret_key not in captured.out
    assert captured.err == ""


def test_run_manifest_is_valid_secret_free_json_without_network(monkeypatch, capsys) -> None:
    api_key = "manifest-api-credential-that-must-not-be-shown"
    secret_key = "manifest-secret-credential-that-must-not-be-shown"
    monkeypatch.setenv("ALPACA_API_KEY", api_key)
    monkeypatch.setenv("ALPACA_SECRET_KEY", secret_key)

    def reject_network(*args, **kwargs):
        raise AssertionError("run-manifest must not open a network connection")

    monkeypatch.setattr(socket, "create_connection", reject_network)

    exit_code = main(
        ["run-manifest", "--start", "2026-08-03", "--end", "2026-08-19"]
    )

    captured = capsys.readouterr()
    manifest = json.loads(captured.out)
    assert exit_code == 0
    assert captured.err == ""
    assert manifest["symbol"] == "SPY"
    assert manifest["start_date"] == "2026-08-03"
    assert manifest["end_date"] == "2026-08-19"
    assert manifest["status"] == "CREATED"
    assert re.fullmatch(r"[0-9a-f]{64}", manifest["config_hash"])
    assert api_key not in captured.out
    assert secret_key not in captured.out
    assert "api_key" not in captured.out
    assert "secret_key" not in captured.out


def test_fetch_bars_prints_concise_secret_free_summary(monkeypatch, capsys) -> None:
    api_key = "cli-fetch-api-credential"
    secret_key = "cli-fetch-secret-credential"
    monkeypatch.setenv("ALPACA_API_KEY", api_key)
    monkeypatch.setenv("ALPACA_SECRET_KEY", secret_key)
    bars = (
        StockBar(
            symbol="SPY",
            timestamp=datetime(2026, 8, 3, 13, 30, tzinfo=UTC),
            open=Decimal("100"),
            high=Decimal("101"),
            low=Decimal("99"),
            close=Decimal("100.5"),
            volume=1000,
            trade_count=20,
            vwap=Decimal("100.25"),
        ),
        StockBar(
            symbol="SPY",
            timestamp=datetime(2026, 8, 3, 13, 31, tzinfo=UTC),
            open=Decimal("100.5"),
            high=Decimal("101.5"),
            low=Decimal("100"),
            close=Decimal("101"),
            volume=1200,
            trade_count=22,
            vwap=Decimal("100.75"),
        ),
    )

    def mocked_fetch(self, *, start, end):
        return HistoricalBarsResult(bars=bars, pages_fetched=2)

    def reject_network(*args, **kwargs):
        raise AssertionError("mocked CLI test must not open a network connection")

    monkeypatch.setattr(HistoricalStockDataService, "fetch_stock_bars", mocked_fetch)
    monkeypatch.setattr(socket, "create_connection", reject_network)

    exit_code = main(["fetch-bars", "--start", "2026-08-03", "--end", "2026-08-03"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Symbol: SPY" in captured.out
    assert "Feed: SIP" in captured.out
    assert "Timeframe: 1Min" in captured.out
    assert "Bars received: 2" in captured.out
    assert "First timestamp: 2026-08-03T13:30:00+00:00" in captured.out
    assert "Last timestamp: 2026-08-03T13:31:00+00:00" in captured.out
    assert "Pages fetched: 2" in captured.out
    assert api_key not in captured.out
    assert secret_key not in captured.out
    assert captured.err == ""


def test_download_bars_summary_and_second_run_idempotency(
    tmp_path, monkeypatch, capsys
) -> None:
    api_key = "cli-download-api-credential"
    secret_key = "cli-download-secret-credential"
    monkeypatch.setenv("ALPACA_API_KEY", api_key)
    monkeypatch.setenv("ALPACA_SECRET_KEY", secret_key)
    bars = (
        StockBar(
            symbol="SPY",
            timestamp=datetime(2026, 8, 19, 13, 30, tzinfo=UTC),
            open=Decimal("100.000000000001"),
            high=Decimal("101.000000000001"),
            low=Decimal("99.000000000001"),
            close=Decimal("100.500000000001"),
            volume=1000,
            trade_count=20,
            vwap=Decimal("100.250000000001"),
        ),
    )

    def mocked_fetch(self, *, start, end):
        return HistoricalBarsResult(bars=bars, pages_fetched=1)

    monkeypatch.setattr(HistoricalStockDataService, "fetch_stock_bars", mocked_fetch)
    command = [
        "download-bars",
        "--start",
        "2026-08-19",
        "--end",
        "2026-08-19",
        "--data-root",
        str(tmp_path / "raw"),
    ]

    first_exit = main(command)
    first = capsys.readouterr()
    second_exit = main(command)
    second = capsys.readouterr()

    assert first_exit == 0
    assert "Downloaded: 1" in first.out
    assert "New bars stored: 1" in first.out
    assert "Existing identical bars: 0" in first.out
    assert "Conflicts: 0" in first.out
    assert "Partitions written: 1" in first.out
    assert second_exit == 0
    assert "Downloaded: 1" in second.out
    assert "New bars stored: 0" in second.out
    assert "Existing identical bars: 1" in second.out
    assert "Conflicts: 0" in second.out
    assert "Partitions written: 0" in second.out
    combined_output = first.out + first.err + second.out + second.err
    assert api_key not in combined_output
    assert secret_key not in combined_output
