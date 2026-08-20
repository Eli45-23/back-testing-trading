from __future__ import annotations

import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from spy_research.cli import main
from spy_research.config import load_research_config
from spy_research.data.raw_store import RawBarStore
from spy_research.data.schemas import RawBarRecord
from spy_research.market import MarketSessionClassifier, SessionType, XNYSCalendar


def raw_bar(timestamp: datetime) -> RawBarRecord:
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


@pytest.fixture(scope="module")
def calendar() -> XNYSCalendar:
    return XNYSCalendar()


@pytest.fixture(scope="module")
def classifier(calendar) -> MarketSessionClassifier:
    return MarketSessionClassifier(calendar)


@pytest.mark.parametrize(
    ("session_date", "is_trading_day", "open_utc", "close_utc", "early"),
    [
        (
            date(2026, 8, 19),
            True,
            "2026-08-19T13:30:00+00:00",
            "2026-08-19T20:00:00+00:00",
            False,
        ),
        (date(2026, 8, 22), False, None, None, False),
        (date(2026, 12, 25), False, None, None, False),
        (
            date(2025, 11, 28),
            True,
            "2025-11-28T14:30:00+00:00",
            "2025-11-28T18:00:00+00:00",
            True,
        ),
        (
            date(2026, 3, 16),
            True,
            "2026-03-16T13:30:00+00:00",
            "2026-03-16T20:00:00+00:00",
            False,
        ),
        (
            date(2026, 1, 5),
            True,
            "2026-01-05T14:30:00+00:00",
            "2026-01-05T21:00:00+00:00",
            False,
        ),
    ],
)
def test_authoritative_calendar_sessions(
    calendar, session_date, is_trading_day, open_utc, close_utc, early
) -> None:
    session = calendar.session_for_date(session_date)

    assert session.is_trading_day is is_trading_day
    assert session.is_early_close is early
    actual_open = session.market_open.isoformat() if session.market_open else None
    actual_close = session.market_close.isoformat() if session.market_close else None
    assert actual_open == open_utc
    assert actual_close == close_utc


@pytest.mark.parametrize(
    ("timestamp", "expected"),
    [
        ("2026-08-19T07:59:00+00:00", SessionType.OUTSIDE_SESSION),
        ("2026-08-19T08:00:00+00:00", SessionType.PREMARKET),
        ("2026-08-19T13:29:00+00:00", SessionType.PREMARKET),
        ("2026-08-19T13:30:00+00:00", SessionType.RTH),
        ("2026-08-19T19:59:00+00:00", SessionType.RTH),
        ("2026-08-19T20:00:00+00:00", SessionType.AFTER_HOURS),
        ("2026-08-19T23:59:00+00:00", SessionType.AFTER_HOURS),
        ("2026-08-20T00:00:00+00:00", SessionType.OUTSIDE_SESSION),
        ("2025-11-28T17:59:00+00:00", SessionType.RTH),
        ("2025-11-28T18:00:00+00:00", SessionType.AFTER_HOURS),
        ("2026-08-22T14:00:00+00:00", SessionType.NON_SESSION),
        ("2026-12-25T15:00:00+00:00", SessionType.NON_SESSION),
        ("2026-03-16T13:29:00+00:00", SessionType.PREMARKET),
        ("2026-03-16T13:30:00+00:00", SessionType.RTH),
        ("2026-01-05T14:29:00+00:00", SessionType.PREMARKET),
        ("2026-01-05T14:30:00+00:00", SessionType.RTH),
    ],
)
def test_bar_classification_boundaries(classifier, timestamp, expected) -> None:
    classified = classifier.classify(raw_bar(datetime.fromisoformat(timestamp)))
    assert classified.session_type is expected


def test_utc_timestamp_uses_new_york_session_date(classifier) -> None:
    classified = classifier.classify(
        raw_bar(datetime.fromisoformat("2026-08-20T00:00:00+00:00"))
    )
    assert classified.session_date == date(2026, 8, 19)


def test_classification_does_not_mutate_raw_record(classifier) -> None:
    bar = raw_bar(datetime(2026, 8, 19, 13, 30, tzinfo=UTC))
    before = bar.model_dump(mode="json")

    classified = classifier.classify(bar)

    assert bar.model_dump(mode="json") == before
    assert classified.bar is bar


def test_normal_session_contains_390_rth_minute_starts(classifier) -> None:
    start = datetime(2026, 8, 19, 13, 30, tzinfo=UTC)
    bars = [raw_bar(start + timedelta(minutes=minute)) for minute in range(390)]
    summary = classifier.summarize(date(2026, 8, 19), bars)

    assert summary.counts[SessionType.RTH] == 390
    assert summary.first_rth == start
    assert summary.last_rth == datetime(2026, 8, 19, 19, 59, tzinfo=UTC)


def test_early_close_session_contains_210_rth_minute_starts(classifier) -> None:
    start = datetime(2025, 11, 28, 14, 30, tzinfo=UTC)
    bars = [raw_bar(start + timedelta(minutes=minute)) for minute in range(210)]
    summary = classifier.summarize(date(2025, 11, 28), bars)

    assert summary.session.is_early_close
    assert summary.counts[SessionType.RTH] == 210
    assert summary.last_rth == datetime(2025, 11, 28, 17, 59, tzinfo=UTC)


def test_session_summary_cli_uses_local_parquet_without_network(
    tmp_path, monkeypatch, capsys
) -> None:
    config = load_research_config()
    store = RawBarStore(config, root=tmp_path / "raw")
    start = datetime(2026, 8, 19, 13, 30, tzinfo=UTC)
    # The store accepts API-shaped bars, so use the source conversion inverse here.
    from spy_research.alpaca.models import StockBar

    bars = [
        StockBar(
            symbol="SPY",
            timestamp=start + timedelta(minutes=minute),
            open=Decimal("100"),
            high=Decimal("101"),
            low=Decimal("99"),
            close=Decimal("100.5"),
            volume=100,
            trade_count=10,
            vwap=Decimal("100.25"),
        )
        for minute in range(2)
    ]
    store.persist_bars(bars)

    def reject_network(*args, **kwargs):
        raise AssertionError("session-summary must not open a network connection")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "session-summary",
            "--start",
            "2026-08-19",
            "--end",
            "2026-08-19",
            "--data-root",
            str(tmp_path / "raw"),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert "Session: 2026-08-19" in captured.out
    assert "Trading day: yes" in captured.out
    assert "RTH bars: 2" in captured.out
    assert "First RTH: 2026-08-19T13:30:00+00:00" in captured.out


def test_session_summary_rejects_reversed_date_range(capsys) -> None:
    exit_code = main(
        ["session-summary", "--start", "2026-08-20", "--end", "2026-08-19"]
    )
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "start date must be on or before end date" in captured.err
