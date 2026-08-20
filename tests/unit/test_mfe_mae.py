from __future__ import annotations

import hashlib
import socket
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from spy_research.alpaca.models import StockBar
from spy_research.bars import ProcessedFiveMinuteStore, aggregate_rth_1m_to_5m
from spy_research.config import load_research_config
from spy_research.data.raw_store import RawBarStore
from spy_research.data.schemas import RawBarRecord
from spy_research.events import (
    EmaCrossDirection,
    EmaCrossEvent,
    detect_session_ema_crosses,
)
from spy_research.indicators import FiveMinuteIndicatorRow
from spy_research.market import ClassifiedRawBar, SessionType, XNYSCalendar
from spy_research.outcomes import (
    EmaCrossOutcomeService,
    OutcomeInputValidationError,
    OutcomeSequenceError,
    calculate_event_outcome,
    calculate_excursion,
    outcome_start_timestamp,
    select_outcome_windows,
)
from spy_research.cli import main


NEW_YORK = ZoneInfo("America/New_York")
DAY = date(2026, 8, 19)


def at(hour: int, minute: int, *, day: date = DAY) -> datetime:
    return datetime.combine(day, time(hour, minute), tzinfo=NEW_YORK).astimezone(UTC)


def raw_bar(
    timestamp: datetime,
    *,
    high: Decimal = Decimal("101"),
    low: Decimal = Decimal("99"),
    close: Decimal = Decimal("100"),
) -> RawBarRecord:
    return RawBarRecord(
        symbol="SPY",
        timestamp=timestamp,
        open=close,
        high=high,
        low=low,
        close=close,
        volume=100,
        trade_count=10,
        vwap=close,
        source="alpaca",
        feed="sip",
        timeframe="1Min",
        adjustment="raw",
    )


def minute_bars(start: datetime, count: int) -> list[RawBarRecord]:
    return [raw_bar(start + timedelta(minutes=index)) for index in range(count)]


def cross_event(
    *,
    timestamp: datetime = at(12, 45),
    direction: EmaCrossDirection = EmaCrossDirection.BULLISH,
) -> EmaCrossEvent:
    session_date = timestamp.astimezone(NEW_YORK).date()
    return EmaCrossEvent(
        symbol="SPY",
        timestamp=timestamp,
        session_date=session_date,
        direction=direction,
        reference_price=Decimal("100"),
        close=Decimal("100"),
        ema9=Decimal("101"),
        ema20=Decimal("100"),
        previous_ema9=Decimal("99"),
        previous_ema20=Decimal("100"),
        signed_separation=Decimal("1"),
        absolute_separation=Decimal("1"),
        previous_signed_separation=Decimal("-1"),
        separation_delta_1=Decimal("2"),
        separation_delta_2=None,
        separation_delta_3=None,
        vwap=Decimal("100"),
        close_minus_vwap=Decimal("0"),
        ema9_minus_vwap=Decimal("1"),
        ema20_minus_vwap=Decimal("0"),
        atr14=Decimal("0.5"),
    )


def selection(
    *,
    event_timestamp: datetime = at(12, 45),
    close: datetime = at(16, 0),
    bars: list[RawBarRecord] | None = None,
):
    return select_outcome_windows(
        event_timestamp=event_timestamp,
        session_date=event_timestamp.astimezone(NEW_YORK).date(),
        session_close=close,
        rth_bars=bars if bars is not None else minute_bars(at(9, 30), 390),
    )


def persist_cross_fixture(tmp_path):
    session = XNYSCalendar().session_for_date(DAY)
    assert session.market_open is not None and session.market_close is not None
    closes = [Decimal("100")] * 78
    closes[20] = Decimal("110")
    source = []
    for minute_index in range(390):
        close = closes[minute_index // 5]
        record = raw_bar(
            session.market_open + timedelta(minutes=minute_index),
            high=close + Decimal("0.2"),
            low=close - Decimal("0.2"),
            close=close,
        )
        source.append(
            ClassifiedRawBar(
                bar=record,
                session_date=DAY,
                session_type=SessionType.RTH,
            )
        )
    processed = aggregate_rth_1m_to_5m(source, session)
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


def test_outcome_starts_five_minutes_after_event_timestamp() -> None:
    assert outcome_start_timestamp(at(12, 45)) == at(12, 50)


def test_cross_candle_minutes_are_excluded() -> None:
    windows = selection()
    assert windows.future_rth_bars[0].timestamp == at(12, 50)
    assert all(bar.timestamp >= at(12, 50) for bar in windows.future_rth_bars)


def test_exact_fixed_horizon_boundaries() -> None:
    windows = selection()
    assert len(windows.five.bars) == 5
    assert windows.five.bars[0].timestamp == at(12, 50)
    assert windows.five.bars[-1].timestamp == at(12, 54)
    assert len(windows.fifteen.bars) == 15
    assert windows.fifteen.bars[-1].timestamp == at(13, 4)
    assert len(windows.thirty.bars) == 30
    assert windows.thirty.bars[-1].timestamp == at(13, 19)
    assert len(windows.sixty.bars) == 60
    assert windows.sixty.bars[-1].timestamp == at(13, 49)


def test_eod_ends_at_final_rth_minute() -> None:
    windows = selection()
    assert windows.eod.bars[-1].timestamp == at(15, 59)
    assert windows.eod.complete


def test_early_close_eod_uses_authoritative_close() -> None:
    early_day = date(2026, 11, 27)
    session = XNYSCalendar().session_for_date(early_day)
    assert session.is_early_close and session.market_open and session.market_close
    event_timestamp = at(12, 45, day=early_day)
    bars = minute_bars(session.market_open, 210)
    windows = select_outcome_windows(
        event_timestamp=event_timestamp,
        session_date=early_day,
        session_close=session.market_close,
        rth_bars=bars,
    )
    assert windows.eod.bars[-1].timestamp == at(12, 59, day=early_day)
    assert windows.eod.requested_minutes == 10
    assert windows.eod.complete


def test_after_hours_and_next_session_are_excluded() -> None:
    bars = minute_bars(at(12, 50), 190)
    bars += [raw_bar(at(16, 0)), raw_bar(at(9, 30, day=date(2026, 8, 20)))]
    windows = selection(bars=bars)
    assert all(bar.timestamp < at(16, 0) for bar in windows.future_rth_bars)
    assert all(bar.timestamp.astimezone(NEW_YORK).date() == DAY for bar in windows.future_rth_bars)


def test_missing_exact_minute_marks_horizon_incomplete() -> None:
    bars = minute_bars(at(12, 50), 5)
    bars.pop(2)
    windows = selection(close=at(12, 55), bars=bars)
    assert len(windows.five.bars) == 4
    assert not windows.five.complete


def test_selector_rejects_duplicate_and_out_of_order_input() -> None:
    bars = minute_bars(at(12, 50), 2)
    with pytest.raises(OutcomeSequenceError, match="duplicate"):
        selection(bars=[bars[0], bars[0]])
    with pytest.raises(OutcomeSequenceError, match="chronological"):
        selection(bars=list(reversed(bars)))


def test_bullish_excursion_math_and_tied_extremes() -> None:
    bars = [
        raw_bar(at(12, 50), high=Decimal("102"), low=Decimal("99")),
        raw_bar(at(12, 51), high=Decimal("103"), low=Decimal("98")),
        raw_bar(at(12, 52), high=Decimal("103"), low=Decimal("98")),
    ]
    result = calculate_excursion(EmaCrossDirection.BULLISH, Decimal("100"), bars)
    assert result.mfe == Decimal("3")
    assert result.mae == Decimal("2")
    assert result.mfe_timestamp == at(12, 51)
    assert result.mae_timestamp == at(12, 51)


def test_bullish_excursions_floor_at_zero() -> None:
    favorable = [raw_bar(at(12, 50), high=Decimal("99"), low=Decimal("98"))]
    adverse = [raw_bar(at(12, 50), high=Decimal("102"), low=Decimal("101"))]
    assert calculate_excursion(EmaCrossDirection.BULLISH, Decimal("100"), favorable).mfe == 0
    assert calculate_excursion(EmaCrossDirection.BULLISH, Decimal("100"), adverse).mae == 0


def test_bearish_excursion_math_and_tied_extremes() -> None:
    bars = [
        raw_bar(at(12, 50), high=Decimal("101"), low=Decimal("98")),
        raw_bar(at(12, 51), high=Decimal("102"), low=Decimal("97")),
        raw_bar(at(12, 52), high=Decimal("102"), low=Decimal("97")),
    ]
    result = calculate_excursion(EmaCrossDirection.BEARISH, Decimal("100"), bars)
    assert result.mfe == Decimal("3")
    assert result.mae == Decimal("2")
    assert result.mfe_timestamp == at(12, 51)
    assert result.mae_timestamp == at(12, 51)


def test_bearish_excursions_floor_at_zero() -> None:
    favorable = [raw_bar(at(12, 50), high=Decimal("102"), low=Decimal("101"))]
    adverse = [raw_bar(at(12, 50), high=Decimal("99"), low=Decimal("98"))]
    assert calculate_excursion(EmaCrossDirection.BEARISH, Decimal("100"), favorable).mfe == 0
    assert calculate_excursion(EmaCrossDirection.BEARISH, Decimal("100"), adverse).mae == 0


def test_no_future_bars_produces_unavailable_excursion() -> None:
    result = calculate_excursion(EmaCrossDirection.BULLISH, Decimal("100"), [])
    assert result.mfe is None and result.mae is None
    assert result.mfe_timestamp is None and result.mae_timestamp is None


@pytest.mark.parametrize(
    ("event_time", "remaining", "expected"),
    [
        ((14, 30), 85, (True, True, True, True)),
        ((15, 15), 40, (True, True, True, False)),
        ((15, 45), 10, (True, False, False, False)),
        ((15, 55), 0, (False, False, False, False)),
    ],
)
def test_horizon_completeness(event_time, remaining, expected) -> None:
    timestamp = at(*event_time)
    windows = selection(event_timestamp=timestamp)
    assert len(windows.future_rth_bars) == remaining
    assert (
        windows.five.complete,
        windows.fifteen.complete,
        windows.thirty.complete,
        windows.sixty.complete,
    ) == expected


def test_incomplete_horizon_still_reports_available_excursion() -> None:
    event = cross_event(timestamp=at(15, 45))
    outcome = calculate_event_outcome(
        event,
        session_close=at(16, 0),
        rth_bars=minute_bars(at(9, 30), 390),
    )
    assert not outcome.fifteen.complete
    assert outcome.fifteen.observed_minutes == 10
    assert outcome.fifteen.excursion.mfe is not None


def test_final_candle_has_unavailable_eod_not_fabricated_zero() -> None:
    event = cross_event(timestamp=at(15, 55))
    outcome = calculate_event_outcome(
        event,
        session_close=at(16, 0),
        rth_bars=minute_bars(at(9, 30), 390),
    )
    assert outcome.available_future_minutes == 0
    assert not outcome.eod.complete
    assert outcome.eod.excursion.mfe is None
    assert outcome.eod.excursion.mae is None


def test_outcome_preserves_full_stage4_event_context() -> None:
    event = cross_event()
    outcome = calculate_event_outcome(
        event,
        session_close=at(16, 0),
        rth_bars=minute_bars(at(9, 30), 390),
    )
    assert outcome.event is event
    assert outcome.reference_price == event.reference_price
    assert outcome.outcome_start_timestamp == at(12, 50)


def test_future_bars_change_outcome_but_not_frozen_event_detection() -> None:
    ema_rows = [
        FiveMinuteIndicatorRow(
            symbol="SPY", timestamp=at(12, 40), session_date=DAY,
            close=Decimal("99"), ema9=Decimal("99"), ema20=Decimal("100")
        ),
        FiveMinuteIndicatorRow(
            symbol="SPY", timestamp=at(12, 45), session_date=DAY,
            close=Decimal("100"), ema9=Decimal("101"), ema20=Decimal("100")
        ),
    ]
    detected_before = detect_session_ema_crosses(ema_rows)
    empty = calculate_excursion(EmaCrossDirection.BULLISH, Decimal("100"), [])
    future = calculate_excursion(
        EmaCrossDirection.BULLISH,
        Decimal("100"),
        [raw_bar(at(12, 50), high=Decimal("105"), low=Decimal("99"))],
    )
    detected_after = detect_session_ema_crosses(ema_rows)
    assert detected_before == detected_after
    assert empty.mfe is None and future.mfe == Decimal("5")


def test_raw_validation_failure_blocks_service(tmp_path) -> None:
    config, raw_store, processed_store = persist_cross_fixture(tmp_path)
    raw_store.partition_path(DAY).unlink()
    with pytest.raises(OutcomeInputValidationError) as exc_info:
        EmaCrossOutcomeService(config, processed_store, raw_store).calculate(
            start=DAY, end=DAY
        )
    assert not exc_info.value.report.passed


def test_service_is_read_only_and_returns_event_outcomes(tmp_path) -> None:
    config, raw_store, processed_store = persist_cross_fixture(tmp_path)
    paths = (raw_store.partition_path(DAY), processed_store.partition_path(DAY))
    before = tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in paths)
    result = EmaCrossOutcomeService(config, processed_store, raw_store).calculate(
        start=DAY, end=DAY
    )
    after = tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in paths)
    assert result.raw_validation.passed
    assert result.outcomes
    assert before == after
    assert not list(tmp_path.rglob("*outcome*"))


def test_cli_is_offline_and_read_only(tmp_path, monkeypatch, capsys) -> None:
    persist_cross_fixture(tmp_path)

    def reject_network(*args, **kwargs):
        raise AssertionError("calculate-cross-outcomes must remain offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "calculate-cross-outcomes",
            "--start", DAY.isoformat(),
            "--end", DAY.isoformat(),
            "--raw-data-root", str(tmp_path / "raw"),
            "--processed-data-root", str(tmp_path / "processed"),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.err == ""
    assert "SPY EMA Cross MFE/MAE Outcomes" in captured.out
    assert "Events:" in captured.out
    assert "Status: PASS" in captured.out
