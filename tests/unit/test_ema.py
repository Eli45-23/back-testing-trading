from __future__ import annotations

import hashlib
import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, getcontext

import pytest

from spy_research.alpaca.models import StockBar
from spy_research.bars import (
    ProcessedFiveMinuteStore,
    aggregate_rth_1m_to_5m,
)
from spy_research.bars.models import FiveMinuteBar
from spy_research.cli import main
from spy_research.config import load_research_config
from spy_research.data.raw_store import RawBarStore
from spy_research.data.schemas import RawBarRecord
from spy_research.indicators import (
    EmaIndicatorService,
    IndicatorInputValidationError,
    IndicatorSequenceError,
    calculate_ema,
    calculate_ema_sessions,
    calculate_session_ema,
)
from spy_research.market import ClassifiedRawBar, SessionType, XNYSCalendar


DAY_ONE = date(2026, 8, 18)
DAY_TWO = date(2026, 8, 19)


def synthetic_bar(
    session_date: date,
    index: int,
    *,
    close_offset: Decimal = Decimal(0),
) -> FiveMinuteBar:
    timestamp = datetime(
        session_date.year,
        session_date.month,
        session_date.day,
        13,
        30,
        tzinfo=UTC,
    ) + timedelta(minutes=5 * index)
    close = Decimal(index + 1) + close_offset
    return FiveMinuteBar(
        symbol="SPY",
        timestamp=timestamp,
        session_date=session_date,
        open=close - Decimal("0.2"),
        high=close + Decimal("0.3"),
        low=close - Decimal("0.4"),
        close=close,
        volume=1000 + index,
        trade_count=20 + index,
        source="alpaca",
        feed="sip",
        timeframe="5Min",
        adjustment="raw",
        source_bar_count=5,
    )


def synthetic_session(
    session_date: date,
    *,
    offset: Decimal = Decimal(0),
) -> list[FiveMinuteBar]:
    return [synthetic_bar(session_date, index, close_offset=offset) for index in range(78)]


def validated_source_and_processed(session_date: date):
    session = XNYSCalendar().session_for_date(session_date)
    assert session.market_open is not None and session.market_close is not None
    count = int((session.market_close - session.market_open).total_seconds() // 60)
    source = []
    for index in range(count):
        step = Decimal(index % 5) / Decimal("10")
        close = Decimal("100") + step
        record = RawBarRecord(
            symbol="SPY",
            timestamp=session.market_open + timedelta(minutes=index),
            open=close - Decimal("0.1"),
            high=close + Decimal("0.2"),
            low=close - Decimal("0.2"),
            close=close,
            volume=1000 + index,
            trade_count=20 + index,
            vwap=close,
            source="alpaca",
            feed="sip",
            timeframe="1Min",
            adjustment="raw",
        )
        source.append(
            ClassifiedRawBar(
                bar=record,
                session_date=session_date,
                session_type=SessionType.RTH,
            )
        )
    processed = aggregate_rth_1m_to_5m(source, session)
    return source, processed


def persist_validated_stores(tmp_path):
    source, processed = validated_source_and_processed(DAY_TWO)
    config = load_research_config()
    raw_store = RawBarStore(config, root=tmp_path / "raw")
    raw_store.persist_bars(
        [
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
    )
    processed_store = ProcessedFiveMinuteStore(root=tmp_path / "processed")
    processed_store.persist_bars(processed)
    return config, raw_store, processed_store


def test_period_three_warmup_seed_and_recurrence() -> None:
    result = calculate_ema(
        [Decimal("1"), Decimal("2"), Decimal("3"), Decimal("4")],
        3,
    )
    assert result == (None, None, Decimal("2"), Decimal("3.0"))


def test_constant_price_sequence_stays_constant_after_seed() -> None:
    result = calculate_ema([Decimal("7.25")] * 6, 3)
    assert result[:2] == (None, None)
    assert result[2:] == (Decimal("7.25"),) * 4


@pytest.mark.parametrize(
    ("prices", "expected"),
    [
        (["1", "2", "3", "4", "5"], [None, None, "2", "3.0", "4.00"]),
        (["5", "4", "3", "2", "1"], [None, None, "4", "3.0", "2.00"]),
    ],
)
def test_rising_and_falling_sequences(prices, expected) -> None:
    result = calculate_ema([Decimal(item) for item in prices], 3)
    assert result == tuple(Decimal(item) if item is not None else None for item in expected)


def test_decimal_precision_is_local_and_deterministic() -> None:
    original_precision = getcontext().prec
    try:
        getcontext().prec = 6
        result = calculate_ema(
            [Decimal("1.123456789012"), Decimal("2.234567890123"), Decimal("3.345678901234")],
            2,
        )
    finally:
        getcontext().prec = original_precision
    assert result[1] == Decimal("1.6790123395675")
    assert result[2] == Decimal("2.7901233806785")


def test_pure_ema_does_not_mutate_input_and_preserves_length() -> None:
    prices = [Decimal("1"), Decimal("2"), Decimal("3")]
    before = prices.copy()
    result = calculate_ema(prices, 3)
    assert prices == before
    assert len(result) == len(prices)


@pytest.mark.parametrize("length", [0, 1, 8])
def test_fewer_than_period_prices_are_all_unavailable(length) -> None:
    result = calculate_ema([Decimal(index + 1) for index in range(length)], 9)
    assert result == (None,) * length


@pytest.mark.parametrize("period", [0, -1])
def test_nonpositive_period_is_rejected(period) -> None:
    with pytest.raises(ValueError, match="positive"):
        calculate_ema([Decimal("1")], period)


def test_nonfinite_or_non_decimal_price_is_rejected() -> None:
    with pytest.raises(ValueError, match="finite Decimal"):
        calculate_ema([Decimal("NaN")], 1)
    with pytest.raises(ValueError, match="finite Decimal"):
        calculate_ema([1], 1)  # type: ignore[list-item]


def test_session_warmups_seeds_recurrences_and_counts() -> None:
    rows = calculate_session_ema(synthetic_session(DAY_TWO))
    assert len(rows) == 78
    assert all(row.ema9 is None for row in rows[:8])
    assert rows[8].ema9 == Decimal("5")
    assert rows[9].ema9 == Decimal("6.0")
    assert sum(row.ema9 is not None for row in rows) == 70
    assert all(row.ema20 is None for row in rows[:19])
    assert rows[19].ema20 == Decimal("10.5")
    assert rows[20].ema20 == Decimal("11.500000000000000000000000000000000000000000000000")
    assert sum(row.ema20 is not None for row in rows) == 59
    assert rows[8].timestamp == datetime(2026, 8, 19, 14, 10, tzinfo=UTC)
    assert rows[19].timestamp == datetime(2026, 8, 19, 15, 5, tzinfo=UTC)


def test_multi_session_state_resets_and_aug18_never_seeds_aug19() -> None:
    first = synthetic_session(DAY_ONE, offset=Decimal("1000"))
    second = synthetic_session(DAY_TWO)
    rows = calculate_ema_sessions(first + second)
    day_two = [row for row in rows if row.session_date == DAY_TWO]
    assert day_two[0].ema9 is None
    assert day_two[7].ema9 is None
    assert day_two[8].ema9 == Decimal("5")
    assert day_two[19].ema20 == Decimal("10.5")


def test_single_session_calculator_rejects_mixed_dates() -> None:
    bars = synthetic_session(DAY_ONE)[:5] + synthetic_session(DAY_TWO)[:5]
    with pytest.raises(IndicatorSequenceError, match="mixes session dates"):
        calculate_session_ema(bars)


def test_duplicate_timestamp_is_rejected() -> None:
    bars = synthetic_session(DAY_TWO)
    bars.insert(1, bars[0])
    with pytest.raises(IndicatorSequenceError, match="duplicate"):
        calculate_session_ema(bars)


def test_out_of_order_input_is_rejected_without_sorting() -> None:
    bars = synthetic_session(DAY_TWO)
    bars[1], bars[2] = bars[2], bars[1]
    with pytest.raises(IndicatorSequenceError, match="chronological"):
        calculate_session_ema(bars)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("timeframe", "1Min", "timeframe"),
        ("session_mode", "ALL", "session mode"),
        ("session_type", "AFTER_HOURS", "RTH"),
    ],
)
def test_wrong_processed_scope_is_rejected(field, value, message) -> None:
    bars = synthetic_session(DAY_TWO)
    bars[0] = bars[0].model_copy(update={field: value})
    with pytest.raises(IndicatorSequenceError, match=message):
        calculate_session_ema(bars)


def test_session_calculation_does_not_mutate_processed_bars() -> None:
    bars = synthetic_session(DAY_TWO)
    before = [bar.model_dump(mode="json") for bar in bars]
    calculate_session_ema(bars)
    assert [bar.model_dump(mode="json") for bar in bars] == before


def test_processed_validation_failure_blocks_indicator_service(tmp_path) -> None:
    config, raw_store, processed_store = persist_validated_stores(tmp_path)
    path = processed_store.partition_path(DAY_TWO)
    path.unlink()
    with pytest.raises(IndicatorInputValidationError) as exc_info:
        EmaIndicatorService(config, processed_store, raw_store).calculate(
            start=DAY_TWO, end=DAY_TWO
        )
    assert not exc_info.value.report.passed


def test_indicator_service_is_read_only(tmp_path) -> None:
    config, raw_store, processed_store = persist_validated_stores(tmp_path)
    raw_path = raw_store.partition_path(DAY_TWO)
    processed_path = processed_store.partition_path(DAY_TWO)
    before = (
        hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        hashlib.sha256(processed_path.read_bytes()).hexdigest(),
    )
    result = EmaIndicatorService(config, processed_store, raw_store).calculate(
        start=DAY_TWO, end=DAY_TWO
    )
    after = (
        hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        hashlib.sha256(processed_path.read_bytes()).hexdigest(),
    )
    assert result.processed_validation.passed
    assert len(result.rows) == 78
    assert before == after


def test_calculate_ema_cli_is_offline_and_reports_warmups(
    tmp_path, monkeypatch, capsys
) -> None:
    persist_validated_stores(tmp_path)

    def reject_network(*args, **kwargs):
        raise AssertionError("calculate-ema must not open a network connection")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "calculate-ema",
            "--start",
            DAY_TWO.isoformat(),
            "--end",
            DAY_TWO.isoformat(),
            "--raw-data-root",
            str(tmp_path / "raw"),
            "--processed-data-root",
            str(tmp_path / "processed"),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.err == ""
    assert "5-minute bars: 78" in captured.out
    assert "EMA9 valid rows: 70" in captured.out
    assert "EMA20 valid rows: 59" in captured.out
    assert "EMA9 first valid: 10:10 EDT" in captured.out
    assert "EMA20 first valid: 11:05 EDT" in captured.out
    assert "Status: PASS" in captured.out
