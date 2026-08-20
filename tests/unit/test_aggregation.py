from __future__ import annotations

import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from spy_research.alpaca.models import StockBar
from spy_research.bars import (
    BucketIntegrityError,
    FiveMinuteAggregationService,
    RawDataValidationGateError,
    aggregate_rth_1m_to_5m,
)
from spy_research.cli import main
from spy_research.config import load_research_config
from spy_research.data.raw_store import RawBarStore
from spy_research.data.schemas import RawBarRecord
from spy_research.market import (
    ClassifiedRawBar,
    SessionType,
    TradingSession,
    XNYSCalendar,
)


BASE_PRICE = Decimal("100.000000000001")


def raw_bar(timestamp: datetime, index: int = 0) -> RawBarRecord:
    step = Decimal(index)
    return RawBarRecord(
        symbol="SPY",
        timestamp=timestamp,
        open=BASE_PRICE + step,
        high=BASE_PRICE + Decimal("1") + step,
        low=BASE_PRICE - Decimal("1") - step,
        close=BASE_PRICE + Decimal("0.5") + step,
        volume=100 + index,
        trade_count=10 + index,
        vwap=BASE_PRICE + Decimal("0.25") + step,
        source="alpaca",
        feed="sip",
        timeframe="1Min",
        adjustment="raw",
    )


def classified(
    timestamp: datetime,
    index: int = 0,
    session_type: SessionType = SessionType.RTH,
) -> ClassifiedRawBar:
    return ClassifiedRawBar(
        bar=raw_bar(timestamp, index),
        session_date=timestamp.astimezone(UTC).date(),
        session_type=session_type,
    )


def five_minute_test_session() -> TradingSession:
    return TradingSession(
        session_date=date(2026, 8, 19),
        is_trading_day=True,
        market_open=datetime(2026, 8, 19, 13, 30, tzinfo=UTC),
        market_close=datetime(2026, 8, 19, 13, 35, tzinfo=UTC),
        is_early_close=False,
    )


def exact_bucket() -> list[ClassifiedRawBar]:
    start = datetime(2026, 8, 19, 13, 30, tzinfo=UTC)
    return [classified(start + timedelta(minutes=index), index) for index in range(5)]


def full_session(session_date: date) -> tuple[TradingSession, list[ClassifiedRawBar]]:
    session = XNYSCalendar().session_for_date(session_date)
    assert session.market_open is not None and session.market_close is not None
    count = int((session.market_close - session.market_open).total_seconds() // 60)
    values = [
        ClassifiedRawBar(
            bar=raw_bar(
                session.market_open + timedelta(minutes=index),
                index % 5,
            ),
            session_date=session_date,
            session_type=SessionType.RTH,
        )
        for index in range(count)
    ]
    return session, values


def to_stock_bars(values: list[ClassifiedRawBar]) -> list[StockBar]:
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
        for item in values
    ]


def test_exact_bucket_aggregation_rules() -> None:
    result = aggregate_rth_1m_to_5m(exact_bucket(), five_minute_test_session())
    candle = result[0]

    assert len(result) == 1
    assert candle.timestamp == datetime(2026, 8, 19, 13, 30, tzinfo=UTC)
    assert candle.open == Decimal("100.000000000001")
    assert candle.high == Decimal("105.000000000001")
    assert candle.low == Decimal("95.000000000001")
    assert candle.close == Decimal("104.500000000001")
    assert candle.volume == 510
    assert candle.trade_count == 60
    assert candle.source_bar_count == 5
    assert candle.timeframe == "5Min"
    assert not hasattr(candle, "vwap")


@pytest.mark.parametrize(
    ("session_date", "expected_count", "first_hour", "last_hour", "last_minute"),
    [
        (date(2026, 8, 19), 78, 13, 19, 55),
        (date(2025, 11, 28), 42, 14, 17, 55),
    ],
)
def test_calendar_session_counts_and_boundaries(
    session_date, expected_count, first_hour, last_hour, last_minute
) -> None:
    session, values = full_session(session_date)
    result = aggregate_rth_1m_to_5m(values, session)

    assert len(result) == expected_count
    assert result[0].timestamp.hour == first_hour
    assert result[0].timestamp.minute == 30
    assert result[1].timestamp == result[0].timestamp + timedelta(minutes=5)
    assert result[-1].timestamp.hour == last_hour
    assert result[-1].timestamp.minute == last_minute


@pytest.mark.parametrize(
    "excluded_timestamp",
    [
        datetime(2026, 8, 19, 8, 0, tzinfo=UTC),
        datetime(2026, 8, 19, 20, 0, tzinfo=UTC),
        datetime(2026, 8, 19, 23, 59, tzinfo=UTC),
    ],
)
def test_non_rth_bars_are_excluded(excluded_timestamp) -> None:
    values = exact_bucket()
    values.append(
        ClassifiedRawBar(
            bar=raw_bar(excluded_timestamp),
            session_date=date(2026, 8, 19),
            session_type=(
                SessionType.PREMARKET
                if excluded_timestamp.hour < 13
                else SessionType.AFTER_HOURS
            ),
        )
    )
    result = aggregate_rth_1m_to_5m(values, five_minute_test_session())
    assert len(result) == 1
    assert result[0].source_bar_count == 5


@pytest.mark.parametrize("missing_index", [0, 2, 4])
def test_missing_minute_or_four_bar_bucket_fails(missing_index) -> None:
    values = exact_bucket()
    values.pop(missing_index)
    with pytest.raises(BucketIntegrityError, match="missing=1"):
        aggregate_rth_1m_to_5m(values, five_minute_test_session())


def test_duplicate_minute_and_six_bar_bucket_fail() -> None:
    values = exact_bucket()
    values.append(values[2])
    with pytest.raises(BucketIntegrityError, match="Duplicate"):
        aggregate_rth_1m_to_5m(values, five_minute_test_session())


@pytest.mark.parametrize(
    "bad_timestamp",
    [
        datetime(2026, 8, 19, 13, 32, 1, tzinfo=UTC),
        datetime(2026, 8, 19, 13, 32, 0, 1, tzinfo=UTC),
    ],
)
def test_incorrect_minute_alignment_fails(bad_timestamp) -> None:
    values = exact_bucket()
    values[2] = classified(bad_timestamp, 2)
    with pytest.raises(BucketIntegrityError, match="align exactly"):
        aggregate_rth_1m_to_5m(values, five_minute_test_session())


def test_extra_arbitrary_bar_fails() -> None:
    values = exact_bucket()
    values.append(classified(datetime(2026, 8, 19, 13, 35, tzinfo=UTC), 5))
    with pytest.raises(BucketIntegrityError, match="extra=1"):
        aggregate_rth_1m_to_5m(values, five_minute_test_session())


def test_non_trading_session_fails() -> None:
    session = XNYSCalendar().session_for_date(date(2026, 8, 22))
    with pytest.raises(BucketIntegrityError, match="non-trading"):
        aggregate_rth_1m_to_5m([], session)


def test_session_duration_must_divide_by_five() -> None:
    session = five_minute_test_session().model_copy(
        update={"market_close": datetime(2026, 8, 19, 13, 34, tzinfo=UTC)}
    )
    with pytest.raises(BucketIntegrityError, match="complete five-minute"):
        aggregate_rth_1m_to_5m([], session)


def test_other_session_bars_never_mix() -> None:
    values = exact_bucket()
    next_day = datetime(2026, 8, 20, 13, 30, tzinfo=UTC)
    values.extend(classified(next_day + timedelta(minutes=i), i) for i in range(5))
    result = aggregate_rth_1m_to_5m(values, five_minute_test_session())
    assert len(result) == 1
    assert result[0].session_date == date(2026, 8, 19)


def test_separate_sessions_remain_separate() -> None:
    first_session, first_values = full_session(date(2026, 8, 18))
    second_session, second_values = full_session(date(2026, 8, 19))
    combined = first_values + second_values
    first = aggregate_rth_1m_to_5m(combined, first_session)
    second = aggregate_rth_1m_to_5m(combined, second_session)
    assert len(first) == len(second) == 78
    assert first[-1].session_date != second[0].session_date


def test_output_is_chronological_even_if_pure_input_is_reversed() -> None:
    session, values = full_session(date(2026, 8, 19))
    result = aggregate_rth_1m_to_5m(list(reversed(values)), session)
    assert tuple(bar.timestamp for bar in result) == tuple(
        sorted(bar.timestamp for bar in result)
    )


def test_immutable_inputs_are_not_changed() -> None:
    values = exact_bucket()
    before = [item.model_dump(mode="json") for item in values]
    result = aggregate_rth_1m_to_5m(values, five_minute_test_session())
    assert [item.model_dump(mode="json") for item in values] == before
    with pytest.raises(ValidationError):
        result[0].volume = 1


def test_failed_raw_validation_blocks_service(tmp_path) -> None:
    config = load_research_config()
    store = RawBarStore(config, root=tmp_path / "raw")
    _, values = full_session(date(2026, 8, 19))
    values.pop(47)
    store.persist_bars(to_stock_bars(values))

    with pytest.raises(RawDataValidationGateError) as exc_info:
        FiveMinuteAggregationService(config, store).aggregate(
            start=date(2026, 8, 19), end=date(2026, 8, 19)
        )
    assert not exc_info.value.report.passed
    assert exc_info.value.report.missing_rth_bars == 1


def test_service_aggregates_valid_local_store(tmp_path) -> None:
    config = load_research_config()
    store = RawBarStore(config, root=tmp_path / "raw")
    _, values = full_session(date(2026, 8, 19))
    store.persist_bars(to_stock_bars(values))

    result = FiveMinuteAggregationService(config, store).aggregate(
        start=date(2026, 8, 19), end=date(2026, 8, 19)
    )
    assert result.validation_report.passed
    assert result.raw_rth_bars == 390
    assert len(result.bars) == 78
    assert result.sessions[0].expected_five_minute_bars == 78


def test_aggregate_bars_cli_is_offline_and_reports_normal_count(
    tmp_path, monkeypatch, capsys
) -> None:
    config = load_research_config()
    store = RawBarStore(config, root=tmp_path / "raw")
    _, values = full_session(date(2026, 8, 19))
    store.persist_bars(to_stock_bars(values))

    def reject_network(*args, **kwargs):
        raise AssertionError("aggregate-bars must not open a network connection")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "aggregate-bars",
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
    assert "Raw RTH bars: 390" in captured.out
    assert "5-minute bars: 78" in captured.out
    assert "First candle: 09:30 EDT" in captured.out
    assert "Last candle: 15:55 EDT" in captured.out
    assert "Status: PASS" in captured.out


def test_aggregate_bars_cli_fails_at_validation_gate(tmp_path, capsys) -> None:
    config = load_research_config()
    store = RawBarStore(config, root=tmp_path / "raw")
    _, values = full_session(date(2026, 8, 19))
    values.pop()
    store.persist_bars(to_stock_bars(values))
    exit_code = main(
        [
            "aggregate-bars",
            "--start",
            "2026-08-19",
            "--end",
            "2026-08-19",
            "--data-root",
            str(tmp_path / "raw"),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "validation failed" in captured.err.lower()
