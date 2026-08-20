from __future__ import annotations

import hashlib
import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, getcontext

import pytest

from spy_research.alpaca.models import StockBar
from spy_research.bars import ProcessedFiveMinuteStore, aggregate_rth_1m_to_5m
from spy_research.bars.models import FiveMinuteBar
from spy_research.cli import main
from spy_research.config import load_research_config
from spy_research.data.raw_store import RawBarStore
from spy_research.data.schemas import RawBarRecord
from spy_research.indicators import (
    AtrIndicatorService,
    IndicatorInputValidationError,
    IndicatorSequenceError,
    calculate_atr_sessions,
    calculate_session_atr,
    calculate_true_ranges,
    calculate_wilder_atr,
)
from spy_research.market import ClassifiedRawBar, SessionType, XNYSCalendar


DAY_ONE = date(2026, 8, 18)
DAY_TWO = date(2026, 8, 19)


def atr_bar(
    session_date: date,
    index: int,
    *,
    high: Decimal,
    low: Decimal,
    close: Decimal,
) -> FiveMinuteBar:
    timestamp = datetime(
        session_date.year, session_date.month, session_date.day, 13, 30, tzinfo=UTC
    ) + timedelta(minutes=5 * index)
    return FiveMinuteBar(
        symbol="SPY",
        timestamp=timestamp,
        session_date=session_date,
        open=close,
        high=high,
        low=low,
        close=close,
        volume=100,
        trade_count=10,
        source="alpaca",
        feed="sip",
        timeframe="5Min",
        adjustment="raw",
        source_bar_count=5,
    )


def session_bars(
    session_date: date,
    *,
    base: Decimal = Decimal("100"),
) -> list[FiveMinuteBar]:
    return [
        atr_bar(
            session_date,
            index,
            high=base + Decimal(index) + Decimal("1"),
            low=base + Decimal(index) - Decimal("1"),
            close=base + Decimal(index),
        )
        for index in range(78)
    ]


def validated_source_and_processed(session_date: date):
    session = XNYSCalendar().session_for_date(session_date)
    assert session.market_open is not None and session.market_close is not None
    count = int((session.market_close - session.market_open).total_seconds() // 60)
    source = []
    for index in range(count):
        close = Decimal("100") + Decimal(index % 5) / Decimal("10")
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
    return source, aggregate_rth_1m_to_5m(source, session)


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


def test_first_true_range_is_intrabar_range() -> None:
    bars = [
        atr_bar(DAY_TWO, 0, high=Decimal("11.5"), low=Decimal("9"), close=Decimal("10"))
    ]
    assert calculate_true_ranges(bars) == (Decimal("2.5"),)


def test_gap_up_uses_high_minus_previous_close() -> None:
    bars = [
        atr_bar(DAY_TWO, 0, high=Decimal("10"), low=Decimal("9"), close=Decimal("9.5")),
        atr_bar(DAY_TWO, 1, high=Decimal("14"), low=Decimal("13"), close=Decimal("13.5")),
    ]
    assert calculate_true_ranges(bars)[1] == Decimal("4.5")


def test_gap_down_uses_previous_close_minus_low() -> None:
    bars = [
        atr_bar(DAY_TWO, 0, high=Decimal("11"), low=Decimal("9"), close=Decimal("10.5")),
        atr_bar(DAY_TWO, 1, high=Decimal("8"), low=Decimal("6"), close=Decimal("7")),
    ]
    assert calculate_true_ranges(bars)[1] == Decimal("4.5")


def test_intrabar_range_wins_when_largest() -> None:
    bars = [
        atr_bar(DAY_TWO, 0, high=Decimal("10"), low=Decimal("9"), close=Decimal("9.5")),
        atr_bar(DAY_TWO, 1, high=Decimal("11"), low=Decimal("8"), close=Decimal("10")),
    ]
    assert calculate_true_ranges(bars)[1] == Decimal("3")


def test_period_three_warmup_and_seed() -> None:
    values = calculate_wilder_atr(
        [Decimal("1"), Decimal("2"), Decimal("6")], period=3
    )
    assert values == (None, None, Decimal("3"))


def test_next_wilder_recurrence() -> None:
    values = calculate_wilder_atr(
        [Decimal("1"), Decimal("2"), Decimal("6"), Decimal("9")], period=3
    )
    assert values[-1] == Decimal("5")


def test_constant_true_range_stays_constant() -> None:
    values = calculate_wilder_atr([Decimal("2.5")] * 8, period=3)
    assert values[2:] == (Decimal("2.5"),) * 6


def test_rising_true_ranges_follow_wilder_not_sma() -> None:
    values = calculate_wilder_atr(
        [Decimal("1"), Decimal("2"), Decimal("3"), Decimal("4"), Decimal("5")],
        period=3,
    )
    assert values == (None, None, Decimal("2"), Decimal("2.6666666666666666666666666666666666666666666666667"), Decimal("3.4444444444444444444444444444444444444444444444443"))


def test_decimal_precision_is_local_and_deterministic() -> None:
    original_precision = getcontext().prec
    try:
        getcontext().prec = 6
        value = calculate_wilder_atr(
            [Decimal("1"), Decimal("2"), Decimal("3"), Decimal("4")], period=3
        )[-1]
    finally:
        getcontext().prec = original_precision
    assert value == Decimal("2.6666666666666666666666666666666666666666666666667")


def test_pure_functions_do_not_mutate_inputs() -> None:
    bars = session_bars(DAY_TWO)[:4]
    bar_snapshot = [bar.model_dump(mode="json") for bar in bars]
    true_ranges = list(calculate_true_ranges(bars))
    range_snapshot = list(true_ranges)
    calculate_wilder_atr(true_ranges, period=3)
    assert [bar.model_dump(mode="json") for bar in bars] == bar_snapshot
    assert true_ranges == range_snapshot


def test_fewer_than_period_is_all_unavailable() -> None:
    assert calculate_wilder_atr([Decimal("1")] * 13) == (None,) * 13


@pytest.mark.parametrize("period", [0, -1])
def test_period_must_be_positive(period: int) -> None:
    with pytest.raises(ValueError, match="positive"):
        calculate_wilder_atr([], period=period)


def test_true_ranges_must_be_non_negative_finite_decimals() -> None:
    with pytest.raises(ValueError, match="finite non-negative Decimal"):
        calculate_wilder_atr([Decimal("-1")])


def test_atr14_warmup_timestamp_and_valid_count() -> None:
    rows = calculate_session_atr(session_bars(DAY_TWO))
    assert all(row.atr14 is None for row in rows[:13])
    assert rows[13].timestamp.hour == 14 and rows[13].timestamp.minute == 35
    assert sum(row.atr14 is not None for row in rows) == 65


def test_first_true_range_does_not_use_prior_day_close() -> None:
    prior = session_bars(DAY_ONE, base=Decimal("1000"))
    current = session_bars(DAY_TWO, base=Decimal("10"))
    rows = calculate_atr_sessions(prior + current)
    first_current = next(row for row in rows if row.session_date == DAY_TWO)
    assert first_current.true_range == Decimal("2")


def test_atr_resets_and_prior_value_is_not_carried() -> None:
    prior = session_bars(DAY_ONE, base=Decimal("1000"))
    current = session_bars(DAY_TWO, base=Decimal("10"))
    rows = calculate_atr_sessions(prior + current)
    current_rows = [row for row in rows if row.session_date == DAY_TWO]
    assert all(row.atr14 is None for row in current_rows[:13])
    assert current_rows[13].atr14 == Decimal("2")


def test_mixed_session_is_rejected() -> None:
    with pytest.raises(IndicatorSequenceError, match="mixes session dates"):
        calculate_session_atr(session_bars(DAY_ONE)[:1] + session_bars(DAY_TWO)[:1])


def test_duplicate_timestamp_is_rejected() -> None:
    bars = session_bars(DAY_TWO)
    bars.insert(1, bars[0])
    with pytest.raises(IndicatorSequenceError, match="duplicate"):
        calculate_session_atr(bars)


def test_out_of_order_input_is_rejected() -> None:
    bars = session_bars(DAY_TWO)
    bars[1], bars[2] = bars[2], bars[1]
    with pytest.raises(IndicatorSequenceError, match="chronological"):
        calculate_session_atr(bars)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("timeframe", "1Min", "timeframe"),
        ("session_mode", "ALL", "session mode"),
        ("session_type", "AFTER_HOURS", "RTH"),
    ],
)
def test_wrong_processed_scope_is_rejected(field, value, message) -> None:
    bars = session_bars(DAY_TWO)
    bars[0] = bars[0].model_copy(update={field: value})
    with pytest.raises(IndicatorSequenceError, match=message):
        calculate_session_atr(bars)


def test_processed_validation_failure_blocks_atr_service(tmp_path) -> None:
    config, raw_store, processed_store = persist_validated_stores(tmp_path)
    processed_store.partition_path(DAY_TWO).unlink()
    with pytest.raises(IndicatorInputValidationError) as exc_info:
        AtrIndicatorService(config, processed_store, raw_store).calculate(
            start=DAY_TWO, end=DAY_TWO
        )
    assert not exc_info.value.report.passed


def test_atr_service_is_read_only_and_input_is_unchanged(tmp_path) -> None:
    config, raw_store, processed_store = persist_validated_stores(tmp_path)
    raw_path = raw_store.partition_path(DAY_TWO)
    processed_path = processed_store.partition_path(DAY_TWO)
    before = tuple(
        hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (raw_path, processed_path)
    )
    result = AtrIndicatorService(config, processed_store, raw_store).calculate(
        start=DAY_TWO, end=DAY_TWO
    )
    after = tuple(
        hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (raw_path, processed_path)
    )
    assert result.processed_validation.passed
    assert len(result.rows) == 78
    assert result.sessions[0].valid_rows == 65
    assert before == after


def test_calculate_atr_cli_is_offline(tmp_path, monkeypatch, capsys) -> None:
    persist_validated_stores(tmp_path)

    def reject_network(*args, **kwargs):
        raise AssertionError("calculate-atr must not open a network connection")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "calculate-atr",
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
    assert "SPY ATR14" in captured.out
    assert "Bars: 78" in captured.out
    assert "ATR14 valid rows: 65" in captured.out
    assert "First ATR14: 10:35 EDT" in captured.out
    assert "Status: PASS" in captured.out
