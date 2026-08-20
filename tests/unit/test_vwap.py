from __future__ import annotations

import hashlib
import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Context, Decimal, ROUND_HALF_EVEN, getcontext, localcontext

import pytest

from spy_research.alpaca.models import StockBar
from spy_research.bars import ProcessedFiveMinuteStore, aggregate_rth_1m_to_5m
from spy_research.bars.models import FiveMinuteBar
from spy_research.cli import main
from spy_research.config import load_research_config
from spy_research.data.raw_store import RawBarStore
from spy_research.data.schemas import RawBarRecord
from spy_research.indicators import (
    IndicatorInputValidationError,
    IndicatorSequenceError,
    VwapIndicatorService,
    calculate_session_vwap,
    calculate_vwap_sessions,
)
from spy_research.market import ClassifiedRawBar, SessionType, XNYSCalendar


DAY_ONE = date(2026, 8, 18)
DAY_TWO = date(2026, 8, 19)


def vwap_bar(
    session_date: date,
    index: int,
    typical_price: Decimal,
    volume: int,
) -> FiveMinuteBar:
    timestamp = datetime(
        session_date.year,
        session_date.month,
        session_date.day,
        13,
        30,
        tzinfo=UTC,
    ) + timedelta(minutes=5 * index)
    return FiveMinuteBar(
        symbol="SPY",
        timestamp=timestamp,
        session_date=session_date,
        open=typical_price,
        high=typical_price + Decimal("1"),
        low=typical_price - Decimal("1"),
        close=typical_price,
        volume=volume,
        trade_count=max(volume, 0),
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
        vwap_bar(session_date, index, base + Decimal(index), 100 + index)
        for index in range(78)
    ]


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


def test_one_bar_vwap_equals_hlc3() -> None:
    rows = calculate_session_vwap(
        [vwap_bar(DAY_TWO, 0, Decimal("10.25"), 100)]
    )
    assert rows[0].typical_price == Decimal("10.25")
    assert rows[0].vwap == Decimal("10.25")


def test_two_equal_volume_bars() -> None:
    bars = [
        vwap_bar(DAY_TWO, 0, Decimal("1"), 10),
        vwap_bar(DAY_TWO, 1, Decimal("3"), 10),
    ]
    assert tuple(row.vwap for row in calculate_session_vwap(bars)) == (
        Decimal("1"),
        Decimal("2"),
    )


def test_two_unequal_volume_bars() -> None:
    bars = [
        vwap_bar(DAY_TWO, 0, Decimal("1"), 1),
        vwap_bar(DAY_TWO, 1, Decimal("3"), 3),
    ]
    assert tuple(row.vwap for row in calculate_session_vwap(bars)) == (
        Decimal("1"),
        Decimal("2.5"),
    )


def test_cumulative_three_bar_sequence() -> None:
    bars = [
        vwap_bar(DAY_TWO, 0, Decimal("1"), 1),
        vwap_bar(DAY_TWO, 1, Decimal("2"), 1),
        vwap_bar(DAY_TWO, 2, Decimal("4"), 1),
    ]
    values = tuple(row.vwap for row in calculate_session_vwap(bars))
    with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
        expected_final = Decimal(7) / Decimal(3)
    assert values == (Decimal("1"), Decimal("1.5"), expected_final)


def test_first_zero_volume_is_unavailable_until_positive_volume() -> None:
    bars = [
        vwap_bar(DAY_TWO, 0, Decimal("1"), 0),
        vwap_bar(DAY_TWO, 1, Decimal("3"), 2),
    ]
    values = tuple(row.vwap for row in calculate_session_vwap(bars))
    assert values == (None, Decimal("3"))


def test_later_zero_volume_retains_cumulative_vwap() -> None:
    bars = [
        vwap_bar(DAY_TWO, 0, Decimal("2"), 5),
        vwap_bar(DAY_TWO, 1, Decimal("99"), 0),
    ]
    values = tuple(row.vwap for row in calculate_session_vwap(bars))
    assert values == (Decimal("2"), Decimal("2"))


def test_all_zero_volume_session_is_all_unavailable() -> None:
    bars = [vwap_bar(DAY_TWO, index, Decimal(index + 1), 0) for index in range(3)]
    assert tuple(row.vwap for row in calculate_session_vwap(bars)) == (
        None,
        None,
        None,
    )


def test_decimal_precision_is_local_and_deterministic() -> None:
    bars = [
        vwap_bar(DAY_TWO, 0, Decimal("1.123456789012"), 1),
        vwap_bar(DAY_TWO, 1, Decimal("2.234567890123"), 2),
    ]
    original_precision = getcontext().prec
    try:
        getcontext().prec = 6
        value = calculate_session_vwap(bars)[1].vwap
    finally:
        getcontext().prec = original_precision
    assert value == Decimal("1.864197523086")


def test_vwap_does_not_mutate_input_and_preserves_length() -> None:
    bars = session_bars(DAY_TWO)
    before = [bar.model_dump(mode="json") for bar in bars]
    rows = calculate_session_vwap(bars)
    assert len(rows) == len(bars)
    assert [bar.model_dump(mode="json") for bar in bars] == before


def test_normal_session_has_vwap_for_every_positive_volume_bar() -> None:
    rows = calculate_session_vwap(session_bars(DAY_TWO))
    assert len(rows) == 78
    assert sum(row.vwap is not None for row in rows) == 78


def test_first_second_and_final_vwap_use_cumulative_prefixes() -> None:
    bars = session_bars(DAY_TWO)
    rows = calculate_session_vwap(bars)
    first = bars[0].close
    with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
        second = (
            bars[0].close * Decimal(bars[0].volume)
            + bars[1].close * Decimal(bars[1].volume)
        ) / Decimal(bars[0].volume + bars[1].volume)
        final = sum(
            bar.close * Decimal(bar.volume) for bar in bars
        ) / Decimal(sum(bar.volume for bar in bars))
    assert rows[0].vwap == first
    assert rows[1].vwap == second
    assert rows[-1].vwap == final


def test_multi_session_vwap_resets_and_prior_day_never_carries() -> None:
    first = session_bars(DAY_ONE, base=Decimal("1000"))
    second = session_bars(DAY_TWO, base=Decimal("10"))
    rows = calculate_vwap_sessions(first + second)
    day_two = [row for row in rows if row.session_date == DAY_TWO]
    assert day_two[0].vwap == Decimal("10")
    assert day_two[0].vwap == day_two[0].typical_price


def test_mixed_session_is_rejected() -> None:
    bars = session_bars(DAY_ONE)[:1] + session_bars(DAY_TWO)[:1]
    with pytest.raises(IndicatorSequenceError, match="mixes session dates"):
        calculate_session_vwap(bars)


def test_duplicate_timestamp_is_rejected() -> None:
    bars = session_bars(DAY_TWO)
    bars.insert(1, bars[0])
    with pytest.raises(IndicatorSequenceError, match="duplicate"):
        calculate_session_vwap(bars)


def test_out_of_order_input_is_rejected() -> None:
    bars = session_bars(DAY_TWO)
    bars[1], bars[2] = bars[2], bars[1]
    with pytest.raises(IndicatorSequenceError, match="chronological"):
        calculate_session_vwap(bars)


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
        calculate_session_vwap(bars)


def test_negative_volume_is_rejected() -> None:
    bars = session_bars(DAY_TWO)
    bars[0] = bars[0].model_copy(update={"volume": -1})
    with pytest.raises(IndicatorSequenceError, match="non-negative"):
        calculate_session_vwap(bars)


def test_processed_validation_failure_blocks_vwap_service(tmp_path) -> None:
    config, raw_store, processed_store = persist_validated_stores(tmp_path)
    processed_store.partition_path(DAY_TWO).unlink()
    with pytest.raises(IndicatorInputValidationError) as exc_info:
        VwapIndicatorService(config, processed_store, raw_store).calculate(
            start=DAY_TWO, end=DAY_TWO
        )
    assert not exc_info.value.report.passed


def test_vwap_service_is_read_only(tmp_path) -> None:
    config, raw_store, processed_store = persist_validated_stores(tmp_path)
    raw_path = raw_store.partition_path(DAY_TWO)
    processed_path = processed_store.partition_path(DAY_TWO)
    before = (
        hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        hashlib.sha256(processed_path.read_bytes()).hexdigest(),
    )
    result = VwapIndicatorService(config, processed_store, raw_store).calculate(
        start=DAY_TWO, end=DAY_TWO
    )
    after = (
        hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        hashlib.sha256(processed_path.read_bytes()).hexdigest(),
    )
    assert result.processed_validation.passed
    assert len(result.rows) == 78
    assert before == after


def test_calculate_vwap_cli_is_offline(tmp_path, monkeypatch, capsys) -> None:
    persist_validated_stores(tmp_path)

    def reject_network(*args, **kwargs):
        raise AssertionError("calculate-vwap must not open a network connection")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "calculate-vwap",
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
    assert "Bars: 78" in captured.out
    assert "VWAP valid rows: 78" in captured.out
    assert "Status: PASS" in captured.out
