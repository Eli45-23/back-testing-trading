from __future__ import annotations

import hashlib
import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext

import pytest

from spy_research.alpaca.models import StockBar
from spy_research.bars import ProcessedFiveMinuteStore, aggregate_rth_1m_to_5m
from spy_research.cli import main
from spy_research.config import load_research_config
from spy_research.data.raw_store import RawBarStore
from spy_research.data.schemas import RawBarRecord
from spy_research.events import (
    EmaCrossDirection,
    EmaCrossEventService,
    detect_ema_crosses,
    detect_session_ema_crosses,
)
from spy_research.indicators import (
    FiveMinuteIndicatorRow,
    IndicatorInputValidationError,
    IndicatorSequenceError,
    calculate_atr_sessions,
    calculate_ema_separation_sessions,
    calculate_ema_sessions,
    calculate_vwap_sessions,
)
from spy_research.market import ClassifiedRawBar, SessionType, XNYSCalendar


DAY_ONE = date(2026, 8, 18)
DAY_TWO = date(2026, 8, 19)


def ema_row(
    index: int,
    separation: Decimal | None,
    *,
    session_date: date = DAY_TWO,
) -> FiveMinuteIndicatorRow:
    ema20 = Decimal("100") if separation is not None else None
    ema9 = Decimal("100") + separation if separation is not None else None
    return FiveMinuteIndicatorRow(
        symbol="SPY",
        timestamp=datetime(
            session_date.year, session_date.month, session_date.day, 13, 30, tzinfo=UTC
        )
        + timedelta(minutes=5 * index),
        session_date=session_date,
        close=Decimal("100") + Decimal(index),
        ema9=ema9,
        ema20=ema20,
    )


def rows_for(separations, *, session_date: date = DAY_TWO):
    return [
        ema_row(
            index,
            Decimal(str(value)) if value is not None else None,
            session_date=session_date,
        )
        for index, value in enumerate(separations)
    ]


def persist_cross_fixture(tmp_path):
    session = XNYSCalendar().session_for_date(DAY_TWO)
    assert session.market_open is not None and session.market_close is not None
    closes = [Decimal("100")] * 78
    closes[20] = Decimal("110")
    source = []
    for minute_index in range(390):
        close = closes[minute_index // 5]
        record = RawBarRecord(
            symbol="SPY",
            timestamp=session.market_open + timedelta(minutes=minute_index),
            open=close,
            high=close + Decimal("0.2"),
            low=close - Decimal("0.2"),
            close=close,
            volume=1000 + minute_index,
            trade_count=20 + minute_index,
            vwap=close,
            source="alpaca",
            feed="sip",
            timeframe="1Min",
            adjustment="raw",
        )
        source.append(
            ClassifiedRawBar(
                bar=record,
                session_date=DAY_TWO,
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


@pytest.mark.parametrize(
    ("previous", "current", "expected"),
    [
        (-1, 1, EmaCrossDirection.BULLISH),
        (1, -1, EmaCrossDirection.BEARISH),
        (0, 1, EmaCrossDirection.BULLISH),
        (0, -1, EmaCrossDirection.BEARISH),
        (-1, 0, None),
        (1, 0, None),
        (0, 0, None),
        (1, 2, None),
        (-1, -2, None),
    ],
)
def test_frozen_cross_state_transitions(previous, current, expected) -> None:
    events = detect_session_ema_crosses(rows_for([previous, current]))
    assert tuple(event.direction for event in events) == (
        (expected,) if expected is not None else ()
    )


@pytest.mark.parametrize(
    ("separations", "directions"),
    [
        ([-1, 1, 2, -1], [EmaCrossDirection.BULLISH, EmaCrossDirection.BEARISH]),
        ([1, -1, -2, 1], [EmaCrossDirection.BEARISH, EmaCrossDirection.BULLISH]),
    ],
)
def test_reversal_sequences_create_only_one_event_per_transition(
    separations, directions
) -> None:
    events = detect_session_ema_crosses(rows_for(separations))
    assert [event.direction for event in events] == directions


@pytest.mark.parametrize(
    "separations",
    [[None, 1], [-1, None], [None, None]],
)
def test_unavailable_previous_or_current_ema_creates_no_event(separations) -> None:
    assert detect_session_ema_crosses(rows_for(separations)) == ()


def test_detected_event_contains_exact_current_and_previous_emas() -> None:
    rows = rows_for([-2, 3])
    event = detect_session_ema_crosses(rows)[0]
    assert event.timestamp == rows[1].timestamp
    assert event.close == rows[1].close
    assert event.ema9 == Decimal("103")
    assert event.ema20 == Decimal("100")
    assert event.previous_ema9 == Decimal("98")
    assert event.previous_ema20 == Decimal("100")


def test_detector_does_not_mutate_input() -> None:
    rows = rows_for([-1, 1, 2])
    before = [row.model_dump(mode="json") for row in rows]
    detect_session_ema_crosses(rows)
    assert [row.model_dump(mode="json") for row in rows] == before


def test_detector_is_prefix_stable_and_uses_no_future_rows() -> None:
    rows = rows_for([-1, 1, 2, -1, 1])
    prefix_events = detect_session_ema_crosses(rows[:3])
    full_events = detect_session_ema_crosses(rows)
    assert prefix_events == tuple(
        event for event in full_events if event.timestamp <= rows[2].timestamp
    )


def test_first_valid_relationship_does_not_create_event() -> None:
    rows = rows_for([None] * 19 + [1])
    assert detect_session_ema_crosses(rows) == ()


def test_multi_session_detector_never_creates_overnight_cross() -> None:
    day_one = rows_for([1], session_date=DAY_ONE)
    day_two = rows_for([-1], session_date=DAY_TWO)
    assert detect_ema_crosses(day_one + day_two) == ()


def test_single_session_detector_rejects_mixed_sessions() -> None:
    rows = rows_for([-1], session_date=DAY_ONE) + rows_for([1], session_date=DAY_TWO)
    with pytest.raises(IndicatorSequenceError, match="mixes session dates"):
        detect_session_ema_crosses(rows)


def test_duplicate_timestamp_is_rejected() -> None:
    row = rows_for([-1])[0]
    with pytest.raises(IndicatorSequenceError, match="duplicate"):
        detect_session_ema_crosses([row, row])


def test_out_of_order_is_rejected_without_sorting() -> None:
    rows = rows_for([-1, 1])
    with pytest.raises(IndicatorSequenceError, match="chronological"):
        detect_session_ema_crosses(list(reversed(rows)))


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [("timeframe", "1Min", "timeframe"), ("session_mode", "ALL", "session mode")],
)
def test_wrong_scope_is_rejected(field, value, message) -> None:
    row = rows_for([-1])[0].model_copy(update={field: value})
    with pytest.raises(IndicatorSequenceError, match=message):
        detect_session_ema_crosses([row])


def test_nonfinite_ema_is_rejected() -> None:
    row = rows_for([-1])[0].model_copy(update={"ema9": Decimal("NaN")})
    with pytest.raises(IndicatorSequenceError, match="finite"):
        detect_session_ema_crosses([row])


def test_events_are_chronological_and_identities_unique() -> None:
    events = detect_session_ema_crosses(rows_for([-1, 1, -1, 1]))
    assert [event.timestamp for event in events] == sorted(
        event.timestamp for event in events
    )
    identities = {
        (event.symbol, event.timestamp, event.direction, event.detector_version)
        for event in events
    }
    assert len(identities) == len(events)


def test_validation_failure_blocks_event_service(tmp_path) -> None:
    config, raw_store, processed_store = persist_cross_fixture(tmp_path)
    processed_store.partition_path(DAY_TWO).unlink()
    with pytest.raises(IndicatorInputValidationError) as exc_info:
        EmaCrossEventService(config, processed_store, raw_store).calculate(
            start=DAY_TWO, end=DAY_TWO
        )
    assert not exc_info.value.report.passed


def test_event_service_attaches_exact_verified_context(tmp_path) -> None:
    config, raw_store, processed_store = persist_cross_fixture(tmp_path)
    bars = processed_store.load_processed_5m_bars(
        symbol="SPY", start=DAY_TWO, end=DAY_TWO, session_mode="RTH_ONLY"
    )
    ema_rows = calculate_ema_sessions(bars)
    separation_rows = calculate_ema_separation_sessions(ema_rows)
    vwap_rows = calculate_vwap_sessions(bars)
    atr_rows = calculate_atr_sessions(bars)
    result = EmaCrossEventService(config, processed_store, raw_store).calculate(
        start=DAY_TWO, end=DAY_TWO
    )
    event = result.events[0]
    index = next(i for i, row in enumerate(ema_rows) if row.timestamp == event.timestamp)
    ema = ema_rows[index]
    previous = ema_rows[index - 1]
    separation = separation_rows[index]
    vwap = vwap_rows[index]
    atr = atr_rows[index]
    assert event.ema9 == ema.ema9
    assert event.ema20 == ema.ema20
    assert event.previous_ema9 == previous.ema9
    assert event.previous_ema20 == previous.ema20
    assert event.signed_separation == separation.signed_separation
    assert event.absolute_separation == separation.absolute_separation
    assert event.previous_signed_separation == previous.ema9 - previous.ema20
    assert event.separation_delta_1 == separation.separation_delta_1
    assert event.separation_delta_2 == separation.separation_delta_2
    assert event.separation_delta_3 == separation.separation_delta_3
    assert event.vwap == vwap.vwap
    with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
        assert event.close_minus_vwap == event.close - event.vwap
        assert event.ema9_minus_vwap == event.ema9 - event.vwap
        assert event.ema20_minus_vwap == event.ema20 - event.vwap
    assert event.atr14 == atr.atr14
    assert event.reference_price == event.close


def test_service_is_read_only_and_does_not_persist_events(tmp_path) -> None:
    config, raw_store, processed_store = persist_cross_fixture(tmp_path)
    paths = (raw_store.partition_path(DAY_TWO), processed_store.partition_path(DAY_TWO))
    before = tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in paths)
    EmaCrossEventService(config, processed_store, raw_store).calculate(
        start=DAY_TWO, end=DAY_TWO
    )
    after = tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in paths)
    assert before == after
    assert not list(tmp_path.rglob("*cross*"))


def test_cli_is_offline_and_prints_only_events(tmp_path, monkeypatch, capsys) -> None:
    persist_cross_fixture(tmp_path)

    def reject_network(*args, **kwargs):
        raise AssertionError("detect-ema-crosses must remain offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "detect-ema-crosses",
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
    assert "SPY EMA Cross Events" in captured.out
    assert "Sessions: 1" in captured.out
    assert "Bullish crosses:" in captured.out
    assert "Bearish crosses:" in captured.out
    assert "Total crosses:" in captured.out
    assert "2026-08-19 11:10 EDT" in captured.out
    assert "Status: PASS" in captured.out
