from __future__ import annotations

import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest

import spy_research.cli as cli_module
from spy_research.data.schemas import RawBarRecord
from spy_research.interactions import LevelType
from spy_research.interactions import InteractionType
from spy_research.levels import PreviousDayLevels
from spy_research.market import XNYSCalendar
from spy_research.replay import (
    STAGE14_FORWARD_CANDIDATE_IDS,
    IncrementalSignalStateEngine,
    ReplayInputError,
)


CALENDAR = XNYSCalendar()
SESSION_DATE = date(2026, 8, 19)
SESSION = CALENDAR.session_for_date(SESSION_DATE)
assert SESSION.market_open is not None
OPEN = SESSION.market_open


def raw_bar(
    timestamp: datetime,
    *,
    open: str = "99",
    high: str = "101",
    low: str = "98",
    close: str = "99",
) -> RawBarRecord:
    return RawBarRecord(
        symbol="SPY",
        timestamp=timestamp,
        open=Decimal(open),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal(close),
        volume=100,
        trade_count=10,
        vwap=Decimal(close),
        source="alpaca",
        feed="sip",
        timeframe="1Min",
        adjustment="raw",
    )


def previous_levels(session_date: date = SESSION_DATE) -> PreviousDayLevels:
    source_date = session_date - timedelta(days=1)
    source = datetime.combine(source_date, datetime.min.time(), tzinfo=UTC)
    return PreviousDayLevels(
        symbol="SPY",
        session_date=session_date,
        source_session_date=source_date,
        pdh=Decimal("100"),
        pdl=Decimal("90"),
        pdc=Decimal("95"),
        pdh_source_timestamp=source + timedelta(hours=15),
        pdl_source_timestamp=source + timedelta(hours=16),
        pdc_source_timestamp=source + timedelta(hours=20, minutes=59),
    )


def signal_bars(session_open: datetime = OPEN) -> tuple[RawBarRecord, ...]:
    bars = []
    for minute in range(10):
        if minute < 4:
            values = dict(open="99", high="100", low="98", close="99")
        elif minute == 4:
            values = dict(open="99", high="101", low="98", close="101")
        else:
            values = dict(open="101", high="102", low="100.5", close="102")
        bars.append(raw_bar(session_open + timedelta(minutes=minute), **values))
    return tuple(bars)


def started_engine(
    session=SESSION,
    levels: PreviousDayLevels | None = None,
) -> IncrementalSignalStateEngine:
    engine = IncrementalSignalStateEngine(calendar=CALENDAR)
    engine.start_session(
        session,
        previous_day_levels=levels or previous_levels(session.session_date),
    )
    return engine


def test_signal_is_emitted_only_when_confirmation_candle_is_complete() -> None:
    engine = started_engine()
    updates = [engine.process_one_minute_bar(bar) for bar in signal_bars()]
    close_through = next(
        item
        for item in updates[4].level_interactions
        if item.level_type is LevelType.PDH
    )
    assert close_through.interaction_type is InteractionType.CLOSE_THROUGH_ABOVE
    assert close_through.candle_completed_at == updates[4].input_bar_completed_at
    assert not any(update.signal_events for update in updates[:9])
    assert len(updates[9].signal_events) == 1
    signal = updates[9].signal_events[0]
    assert signal.break_timestamp == OPEN
    assert signal.confirmation_candle_timestamp == OPEN + timedelta(minutes=5)
    assert signal.signal_known_at == OPEN + timedelta(minutes=10)
    assert updates[9].input_bar_completed_at == signal.signal_known_at
    assert signal.eligible_stage14_candidate_ids == ()


def test_extreme_future_bars_cannot_change_an_emitted_signal() -> None:
    baseline = started_engine()
    event = None
    for bar in signal_bars():
        update = baseline.process_one_minute_bar(bar)
        if update.signal_events:
            event = update.signal_events[0]
    assert event is not None
    frozen_json = event.model_dump_json()
    for minute in range(10, 15):
        baseline.process_one_minute_bar(
            raw_bar(
                OPEN + timedelta(minutes=minute),
                open="500", high="999", low="1", close="500",
            )
        )
    assert event.model_dump_json() == frozen_json
    assert baseline.signals[0] == event


def test_prefix_replay_matches_the_same_event_in_a_longer_replay() -> None:
    prefix = started_engine()
    full = started_engine()
    prefix_events = tuple(
        event
        for bar in signal_bars()
        for event in prefix.process_one_minute_bar(bar).signal_events
    )
    full_bars = signal_bars() + tuple(
        raw_bar(
            OPEN + timedelta(minutes=minute),
            open="102", high="103", low="101", close="102",
        )
        for minute in range(10, 15)
    )
    full_events = tuple(
        event
        for bar in full_bars
        for event in full.process_one_minute_bar(bar).signal_events
    )
    assert full_events[: len(prefix_events)] == prefix_events


def test_opening_levels_are_unusable_before_0935() -> None:
    engine = started_engine(levels=previous_levels().model_copy(update={"pdh": Decimal("999")}))
    for bar in signal_bars()[:5]:
        update = engine.process_one_minute_bar(bar)
    assert update.completed_five_minute_bar is not None
    opening = tuple(
        item for item in engine.current_levels
        if item.level_type in (LevelType.ORH5, LevelType.ORL5)
    )
    assert len(opening) == 2
    assert all(item.available_from_timestamp == OPEN + timedelta(minutes=5) for item in opening)
    assert engine.finish_session().break_seed_count == 0


def test_premarket_levels_freeze_before_rth_and_ignore_rth_extremes() -> None:
    engine = started_engine()
    premarket_timestamp = OPEN - timedelta(minutes=1)
    engine.process_one_minute_bar(
        raw_bar(premarket_timestamp, open="104", high="105", low="94", close="95")
    )
    for bar in signal_bars()[:5]:
        engine.process_one_minute_bar(bar)
    before = {
        item.level_type: item.level_price
        for item in engine.current_levels
        if item.level_type in (LevelType.PMH, LevelType.PML)
    }
    for minute in range(5, 10):
        engine.process_one_minute_bar(
            raw_bar(
                OPEN + timedelta(minutes=minute),
                open="500", high="999", low="1", close="500",
            )
        )
    after = {
        item.level_type: item.level_price
        for item in engine.current_levels
        if item.level_type in (LevelType.PMH, LevelType.PML)
    }
    assert before == after == {LevelType.PMH: Decimal("105"), LevelType.PML: Decimal("94")}


def test_previous_day_levels_cannot_use_the_current_session_as_source() -> None:
    invalid = previous_levels().model_copy(
        update={"source_session_date": SESSION_DATE}
    )
    engine = IncrementalSignalStateEngine(calendar=CALENDAR)
    with pytest.raises(ReplayInputError, match="prior XNYS"):
        engine.start_session(SESSION, previous_day_levels=invalid)


def test_duplicate_and_out_of_order_minute_bars_are_rejected() -> None:
    duplicate = started_engine()
    first = signal_bars()[0]
    duplicate.process_one_minute_bar(first)
    with pytest.raises(ReplayInputError, match="duplicate"):
        duplicate.process_one_minute_bar(first)
    out_of_order = started_engine()
    out_of_order.process_one_minute_bar(signal_bars()[0])
    out_of_order.process_one_minute_bar(signal_bars()[1])
    with pytest.raises(ReplayInputError, match="chronological"):
        out_of_order.process_one_minute_bar(signal_bars()[0])


def test_future_five_minute_bar_cannot_mutate_prior_indicator_state() -> None:
    engine = started_engine(levels=previous_levels().model_copy(update={"pdh": Decimal("999")}))
    last_update = None
    for minute in range(100):
        bucket = minute // 5
        close = str(100 + bucket)
        last_update = engine.process_one_minute_bar(
            raw_bar(
                OPEN + timedelta(minutes=minute),
                open=close, high=str(101 + bucket), low=str(99 + bucket), close=close,
            )
        )
    assert last_update is not None and last_update.latest_ema is not None
    prior_json = last_update.latest_ema.model_dump_json()
    for minute in range(100, 105):
        engine.process_one_minute_bar(
            raw_bar(
                OPEN + timedelta(minutes=minute),
                open="1", high="999", low="1", close="1",
            )
        )
    assert last_update.latest_ema.model_dump_json() == prior_json


def test_cross_events_are_never_emitted_before_known_at() -> None:
    engine = started_engine(levels=previous_levels().model_copy(update={"pdh": Decimal("999")}))
    crosses = []
    for minute in range(150):
        bucket = minute // 5
        price = 100 + bucket if bucket < 22 else 150 - (bucket * 3)
        update = engine.process_one_minute_bar(
            raw_bar(
                OPEN + timedelta(minutes=minute),
                open=str(price), high=str(price + 1), low=str(price - 1), close=str(price),
            )
        )
        for cross in update.cross_events:
            crosses.append(cross)
            assert cross.known_at == update.input_bar_completed_at
            assert cross.known_at == cross.event_timestamp + timedelta(minutes=5)
    assert crosses


def test_session_restart_drops_pending_break_state() -> None:
    engine = started_engine()
    for bar in signal_bars()[:5]:
        engine.process_one_minute_bar(bar)
    first = engine.finish_session()
    assert first.break_seed_count == 1
    assert first.confirmed_signal_count == 0
    next_date = date(2026, 8, 20)
    next_session = CALENDAR.session_for_date(next_date)
    assert next_session.market_open is not None
    engine.start_session(
        next_session,
        previous_day_levels=previous_levels(next_date),
    )
    for minute in range(5):
        engine.process_one_minute_bar(
            raw_bar(
                next_session.market_open + timedelta(minutes=minute),
                open="101", high="102", low="100.5", close="102",
            )
        )
    assert engine.finish_session().confirmed_signal_count == 0


def test_session_chunks_and_reused_engine_emit_identical_streams() -> None:
    dates = (date(2026, 8, 19), date(2026, 8, 20))
    reused = IncrementalSignalStateEngine(calendar=CALENDAR)
    reused_signals = []
    chunked_signals = []
    for session_date in dates:
        session = CALENDAR.session_for_date(session_date)
        assert session.market_open is not None
        bars = signal_bars(session.market_open)
        reused.start_session(
            session,
            previous_day_levels=previous_levels(session_date),
        )
        for bar in bars:
            reused_signals.extend(reused.process_one_minute_bar(bar).signal_events)
        reused.finish_session()
        chunk = IncrementalSignalStateEngine(calendar=CALENDAR)
        chunk.start_session(
            session,
            previous_day_levels=previous_levels(session_date),
        )
        for bar in bars:
            chunked_signals.extend(chunk.process_one_minute_bar(bar).signal_events)
        chunk.finish_session()
    assert tuple(reused_signals) == tuple(chunked_signals)


def test_base_short_signal_attaches_both_candidates_without_selecting_one() -> None:
    engine = started_engine(
        levels=previous_levels().model_copy(
            update={"pdh": Decimal("999"), "pdl": Decimal("100")}
        )
    )
    bars = []
    for minute in range(10):
        if minute < 4:
            values = dict(open="101", high="102", low="100", close="101")
        elif minute == 4:
            values = dict(open="101", high="102", low="99", close="99")
        else:
            values = dict(open="99", high="99.5", low="98", close="98")
        bars.append(raw_bar(OPEN + timedelta(minutes=minute), **values))
    signals = tuple(
        signal
        for bar in bars
        for signal in engine.process_one_minute_bar(bar).signal_events
    )
    short = next(item for item in signals if item.base_short_membership)
    assert short.eligible_stage14_candidate_ids == STAGE14_FORWARD_CANDIDATE_IDS


def test_replay_cli_is_offline_and_nonpersistent(monkeypatch, tmp_path) -> None:
    result = SimpleNamespace()

    class FakeService:
        def __init__(self, *args):
            pass

        def calculate(self, *, start, end):
            return result

    monkeypatch.setattr(cli_module, "SignalReplayService", FakeService)
    monkeypatch.setattr(cli_module, "_print_signal_replay", lambda report: None)
    monkeypatch.setattr(
        socket,
        "create_connection",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("network")),
    )
    before = tuple(tmp_path.rglob("*"))
    assert cli_module.main(
        (
            "replay-signal-engine",
            "--start", "2026-01-02",
            "--end", "2026-08-19",
            "--raw-data-root", str(tmp_path / "raw"),
            "--processed-data-root", str(tmp_path / "processed"),
        )
    ) == 0
    assert tuple(tmp_path.rglob("*")) == before
