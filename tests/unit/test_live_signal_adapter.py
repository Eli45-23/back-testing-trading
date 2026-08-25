from __future__ import annotations

import json
import ssl
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import SecretStr

from spy_research.data.schemas import RawBarRecord
from spy_research.config import AlpacaEnvironment
from spy_research.live import (
    ALPACA_SIP_STREAM_URL,
    AlpacaLiveBarNormalizer,
    AlpacaSipWebSocketTransport,
    LiveAuthenticationError,
    LiveBootstrapper,
    LiveDataError,
    LiveMarketDataAdapter,
    LiveSignalEngineService,
    LiveTransportError,
    live_signal_report_hash,
)
from spy_research.levels import PreviousDayLevels
from spy_research.market import XNYSCalendar
from spy_research.replay import (
    STAGE14_FORWARD_CANDIDATE_IDS,
    IncrementalSignalStateEngine,
)


CALENDAR = XNYSCalendar()
SESSION_DATE = date(2026, 8, 19)
SESSION = CALENDAR.session_for_date(SESSION_DATE)
PRIOR_DATE = date(2026, 8, 18)
PRIOR = CALENDAR.session_for_date(PRIOR_DATE)
assert SESSION.market_open is not None and SESSION.market_close is not None
assert PRIOR.market_open is not None and PRIOR.market_close is not None
OPEN = SESSION.market_open


def raw_bar(
    timestamp: datetime,
    *,
    open: str = "99",
    high: str = "101",
    low: str = "98",
    close: str = "99",
    volume: int = 100,
) -> RawBarRecord:
    return RawBarRecord(
        symbol="SPY",
        timestamp=timestamp,
        open=Decimal(open),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal(close),
        volume=volume,
        trade_count=10,
        vwap=Decimal(close),
        source="alpaca",
        feed="sip",
        timeframe="1Min",
        adjustment="raw",
    )


def live_message(bar: RawBarRecord, *, symbol: str = "SPY") -> dict[str, object]:
    return {
        "T": "b",
        "S": symbol,
        "t": bar.timestamp.isoformat().replace("+00:00", "Z"),
        "o": str(bar.open),
        "h": str(bar.high),
        "l": str(bar.low),
        "c": str(bar.close),
        "v": bar.volume,
        "n": bar.trade_count,
        "vw": str(bar.vwap),
    }


def prior_bars() -> tuple[RawBarRecord, ...]:
    bars = []
    minutes = int((PRIOR.market_close - PRIOR.market_open).total_seconds() // 60)
    for index in range(minutes):
        high = "100"
        low = "90"
        close = "95" if index == minutes - 1 else "99"
        bars.append(
            raw_bar(
                PRIOR.market_open + timedelta(minutes=index),
                open="99",
                high=high,
                low=low,
                close=close,
            )
        )
    return tuple(bars)


def bullish_signal_bars() -> tuple[RawBarRecord, ...]:
    result = []
    for minute in range(10):
        if minute < 4:
            values = dict(open="99", high="100", low="98", close="99")
        elif minute == 4:
            values = dict(open="99", high="101", low="98", close="101")
        else:
            values = dict(open="101", high="102", low="100.5", close="102")
        result.append(raw_bar(OPEN + timedelta(minutes=minute), **values))
    return tuple(result)


def bearish_signal_bars() -> tuple[RawBarRecord, ...]:
    result = []
    for minute in range(10):
        if minute < 4:
            values = dict(open="91", high="92", low="90", close="91")
        elif minute == 4:
            values = dict(open="91", high="92", low="89", close="89")
        else:
            values = dict(open="89", high="89.5", low="87", close="88")
        result.append(raw_bar(OPEN + timedelta(minutes=minute), **values))
    return tuple(result)


def levels() -> PreviousDayLevels:
    return PreviousDayLevels(
        symbol="SPY",
        session_date=SESSION_DATE,
        source_session_date=PRIOR_DATE,
        pdh=Decimal("100"),
        pdl=Decimal("90"),
        pdc=Decimal("95"),
        pdh_source_timestamp=PRIOR.market_open,
        pdl_source_timestamp=PRIOR.market_open,
        pdc_source_timestamp=PRIOR.market_close - timedelta(minutes=1),
    )


def adapter() -> LiveMarketDataAdapter:
    engine = IncrementalSignalStateEngine(calendar=CALENDAR)
    engine.start_session(SESSION, previous_day_levels=levels())
    return LiveMarketDataAdapter(
        engine, session_date=SESSION_DATE, calendar=CALENDAR
    )


class MemorySource:
    def __init__(self, bars: tuple[RawBarRecord, ...]) -> None:
        self.bars = bars
        self.requests: list[tuple[datetime, datetime]] = []

    def fetch(self, *, start: datetime, end: datetime) -> tuple[RawBarRecord, ...]:
        self.requests.append((start, end))
        return tuple(bar for bar in self.bars if start <= bar.timestamp <= end)


class MemoryTransport:
    def __init__(self, messages) -> None:
        self._messages = tuple(messages)

    def messages(self):
        yield from self._messages


def test_normalizer_preserves_exact_decimal_and_stage14_input_fields() -> None:
    message = live_message(raw_bar(OPEN, open="100.10", high="100.30", low="99.90", close="100.20"))
    normalized = AlpacaLiveBarNormalizer().normalize(message)
    assert normalized is not None
    assert normalized.open == Decimal("100.10")
    assert normalized.close == Decimal("100.20")
    assert normalized.timestamp == OPEN
    assert normalized.feed == "sip"
    assert normalized.timeframe == "1Min"
    assert normalized.adjustment == "raw"


def test_non_spy_and_non_final_messages_are_ignored() -> None:
    active = adapter()
    first = bullish_signal_bars()[0]
    wrong = active.process_message(
        live_message(first, symbol="AAPL"), received_at=first.timestamp + timedelta(minutes=1)
    )
    acknowledgement = active.process_message(
        {"T": "subscription", "bars": ["SPY"]},
        received_at=first.timestamp + timedelta(minutes=1),
    )
    assert wrong.ignored_reason == "NON_FINAL_OR_NON_SPY_MESSAGE"
    assert acknowledgement.ignored_reason == "NON_FINAL_OR_NON_SPY_MESSAGE"
    assert active.engine.completed_five_minute_bars == ()


def test_live_normalization_matches_direct_stage14_replay_and_signal_timing() -> None:
    direct = IncrementalSignalStateEngine(calendar=CALENDAR)
    direct.start_session(SESSION, previous_day_levels=levels())
    active = adapter()
    live_signals = []
    for bar in bullish_signal_bars():
        direct_update = direct.process_one_minute_bar(bar)
        live_update = active.process_message(
            live_message(bar), received_at=bar.timestamp + timedelta(minutes=1)
        )
        live_signals.extend(live_update.signal_events)
        assert live_update.replay_update == direct_update
    assert active.engine.completed_five_minute_bars == direct.completed_five_minute_bars
    assert active.engine.signals == direct.signals
    assert len(live_signals) == 1
    assert live_signals[0].signal_known_at == OPEN + timedelta(minutes=10)
    assert live_signals[0].confirmation_close == Decimal("102")


def test_bar_cannot_enter_engine_before_minute_completion() -> None:
    first = bullish_signal_bars()[0]
    with pytest.raises(LiveDataError, match="before closed-bar"):
        adapter().process_message(
            live_message(first), received_at=first.timestamp + timedelta(seconds=59)
        )


def test_identical_duplicate_handoff_is_idempotent_but_conflict_fails() -> None:
    active = adapter()
    first = bullish_signal_bars()[0]
    active.seed(first)
    duplicate = active.process_message(
        live_message(first), received_at=first.timestamp + timedelta(minutes=2)
    )
    assert duplicate.duplicate_identical
    conflict = first.model_copy(update={"close": Decimal("99.5"), "vwap": Decimal("99.5")})
    with pytest.raises(LiveDataError, match="conflicting"):
        active.process_message(
            live_message(conflict), received_at=first.timestamp + timedelta(minutes=2)
        )


def test_out_of_order_new_bar_and_stale_session_fail() -> None:
    active = adapter()
    later = raw_bar(OPEN - timedelta(minutes=1))
    earlier = raw_bar(OPEN - timedelta(minutes=2))
    active.process_message(live_message(later), received_at=OPEN)
    with pytest.raises(LiveDataError, match="out-of-order"):
        active.process_message(live_message(earlier), received_at=OPEN)
    stale = raw_bar(PRIOR.market_open)
    with pytest.raises(LiveDataError, match="stale or wrong-session"):
        adapter().process_message(
            live_message(stale), received_at=OPEN + timedelta(minutes=1)
        )


def test_bootstrap_plus_live_continuation_equals_continuous_replay() -> None:
    premarket = raw_bar(OPEN - timedelta(minutes=1), open="95", high="105", low="94", close="95")
    current = (premarket,) + bullish_signal_bars()
    source = MemorySource(prior_bars() + current)
    active, result = LiveBootstrapper(source, calendar=CALENDAR).bootstrap(
        as_of=OPEN + timedelta(minutes=5)
    )
    assert result.prior_rth_bar_count == 390
    assert result.current_premarket_bar_count == 1
    assert result.current_rth_bar_count == 5
    for bar in bullish_signal_bars()[5:]:
        active.process_message(
            live_message(bar), received_at=bar.timestamp + timedelta(minutes=1)
        )

    continuous = IncrementalSignalStateEngine(calendar=CALENDAR)
    continuous.start_session(SESSION, previous_day_levels=levels())
    continuous.process_one_minute_bar(premarket)
    for bar in bullish_signal_bars():
        continuous.process_one_minute_bar(bar)
    assert active.engine.completed_five_minute_bars == continuous.completed_five_minute_bars
    assert active.engine.signals == continuous.signals
    assert len(source.requests) == 2
    assert source.requests[0] == (
        PRIOR.market_open,
        PRIOR.market_close - timedelta(microseconds=1),
    )


def test_bootstrap_rejects_incomplete_prior_session_instead_of_fabricating_levels() -> None:
    source = MemorySource(prior_bars()[:-1] + bullish_signal_bars()[:5])
    with pytest.raises(LiveDataError, match="coverage is incomplete"):
        LiveBootstrapper(source, calendar=CALENDAR).bootstrap(
            as_of=OPEN + timedelta(minutes=5)
        )


def test_reconnect_boundary_duplicate_does_not_duplicate_signal_state() -> None:
    source = MemorySource(prior_bars() + bullish_signal_bars()[:5])
    now_values = iter(
        [bar.timestamp + timedelta(minutes=1) for bar in bullish_signal_bars()[4:]]
    )
    messages = [live_message(bullish_signal_bars()[4])] + [
        live_message(bar) for bar in bullish_signal_bars()[5:]
    ]
    service = LiveSignalEngineService(
        LiveBootstrapper(source, calendar=CALENDAR),
        MemoryTransport(messages),
        clock=lambda: next(now_values),
    )
    report = service.run(as_of=OPEN + timedelta(minutes=5))
    assert report.duplicate_identical_count == 1
    assert report.accepted_live_bar_count == 5
    assert len(report.signals) == 1
    assert len({event.signal_identity for event in report.signals}) == 1


def test_future_bar_cannot_change_already_emitted_live_event() -> None:
    active = adapter()
    event = None
    for bar in bullish_signal_bars():
        update = active.process_message(
            live_message(bar), received_at=bar.timestamp + timedelta(minutes=1)
        )
        if update.signal_events:
            event = update.signal_events[0]
    assert event is not None
    frozen = event.model_dump_json()
    for minute in range(10, 15):
        bar = raw_bar(
            OPEN + timedelta(minutes=minute),
            open="500", high="999", low="1", close="500",
        )
        active.process_message(live_message(bar), received_at=bar.timestamp + timedelta(minutes=1))
    assert event.model_dump_json() == frozen


def test_base_short_live_event_attaches_both_frozen_candidates_without_selection() -> None:
    active = adapter()
    events = []
    for bar in bearish_signal_bars():
        update = active.process_message(
            live_message(bar), received_at=bar.timestamp + timedelta(minutes=1)
        )
        events.extend(update.signal_events)
    assert len(events) == 1
    assert events[0].base_short_membership
    assert events[0].stage13_forward_test_candidate_ids == STAGE14_FORWARD_CANDIDATE_IDS


class FakeSocket:
    def __init__(self, responses) -> None:
        self.responses = iter(responses)
        self.sent = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def send(self, value):
        self.sent.append(json.loads(value))

    def recv(self, timeout=None):
        value = next(self.responses)
        if isinstance(value, BaseException):
            raise value
        return value


def test_transport_uses_only_sip_bar_subscription_and_redacts_errors() -> None:
    key = "unit-api-key-must-not-leak"
    secret = "unit-secret-key-must-not-leak"
    bar = bullish_signal_bars()[0]
    socket = FakeSocket(
        [
            '[{"T":"success","msg":"connected"}]',
            '[{"T":"success","msg":"authenticated"}]',
            '[{"T":"subscription","bars":["SPY"]}]',
            json.dumps([live_message(bar)]),
        ]
    )
    endpoints = []

    def connector(endpoint, **kwargs):
        endpoints.append(endpoint)
        assert kwargs["ssl"].verify_mode == ssl.CERT_REQUIRED
        assert kwargs["ssl"].check_hostname
        return socket

    transport = AlpacaSipWebSocketTransport(
        api_key=SecretStr(key),
        secret_key=SecretStr(secret),
        connector=connector,
    )
    observed = next(transport.messages())
    assert observed["S"] == "SPY"
    assert endpoints == [ALPACA_SIP_STREAM_URL]
    assert socket.sent[1] == {"action": "subscribe", "bars": ["SPY"]}
    assert not any(
        hasattr(transport, name)
        for name in ("place_order", "cancel_order", "positions", "buying_power")
    )


def test_sip_transport_uses_market_data_credentials_not_paper_credentials(
    monkeypatch,
) -> None:
    monkeypatch.setenv("ALPACA_API_KEY", "market-transport-key")
    monkeypatch.setenv("ALPACA_SECRET_KEY", "market-transport-secret")
    monkeypatch.setenv("ALPACA_PAPER_API_KEY", "paper-broker-key")
    monkeypatch.setenv("ALPACA_PAPER_SECRET_KEY", "paper-broker-secret")
    bar = bullish_signal_bars()[0]
    socket = FakeSocket(
        (
            '[{"T":"success","msg":"connected"}]',
            '[{"T":"success","msg":"authenticated"}]',
            '[{"T":"subscription","bars":["SPY"]}]',
            json.dumps([live_message(bar)]),
        )
    )
    transport = AlpacaSipWebSocketTransport.from_environment(
        AlpacaEnvironment(), connector=lambda endpoint, **kwargs: socket
    )

    next(transport.messages())

    assert socket.sent[0] == {
        "action": "auth",
        "key": "market-transport-key",
        "secret": "market-transport-secret",
    }


def test_transport_reconnect_retains_adapter_state_and_does_not_duplicate_signal() -> None:
    bars = bullish_signal_bars()
    connected = '[{"T":"success","msg":"connected"}]'
    auth = '[{"T":"success","msg":"authenticated"}]'
    subscription = '[{"T":"subscription","bars":["SPY"]}]'
    sockets = iter(
        (
            FakeSocket((connected, auth, subscription, json.dumps([live_message(bars[4])]), OSError())),
            FakeSocket(
                (connected, auth, subscription)
                + tuple(json.dumps([live_message(bar)]) for bar in bars[4:])
            ),
        )
    )
    connector_count = 0

    def connector(endpoint, **_kwargs):
        nonlocal connector_count
        assert endpoint == ALPACA_SIP_STREAM_URL
        connector_count += 1
        return next(sockets)

    transport = AlpacaSipWebSocketTransport(
        api_key=SecretStr("reconnect-api-key"),
        secret_key=SecretStr("reconnect-secret-key"),
        connector=connector,
    )
    source = MemorySource(prior_bars() + bars[:5])
    received = iter(
        [bars[4].timestamp + timedelta(minutes=2)] * 3
        + [bar.timestamp + timedelta(minutes=1) for bar in bars[6:]]
    )
    report = LiveSignalEngineService(
        LiveBootstrapper(source, calendar=CALENDAR),
        transport,
        clock=lambda: next(received),
    ).run(as_of=OPEN + timedelta(minutes=5), max_bars=5)
    assert connector_count == 2
    assert report.duplicate_identical_count == 2
    assert report.accepted_live_bar_count == 5
    assert len(report.signals) == 1


def test_authentication_failure_is_sanitized() -> None:
    key = "auth-api-key-that-must-not-leak"
    secret = "auth-secret-that-must-not-leak"
    socket = FakeSocket(
        (
            '[{"T":"success","msg":"connected"}]',
            '[{"T":"error","code":401,"msg":"auth failed"}]',
        )
    )
    transport = AlpacaSipWebSocketTransport(
        api_key=SecretStr(key),
        secret_key=SecretStr(secret),
        connector=lambda endpoint, **kwargs: socket,
    )
    with pytest.raises(LiveDataError) as error:
        next(transport.messages())
    rendered = str(error.value)
    assert key not in rendered
    assert secret not in rendered


def transport_for_socket(socket: FakeSocket, **kwargs) -> AlpacaSipWebSocketTransport:
    return AlpacaSipWebSocketTransport(
        api_key=SecretStr("handshake-key"),
        secret_key=SecretStr("handshake-secret"),
        connector=lambda endpoint, **connector_kwargs: socket,
        **kwargs,
    )


def test_authenticated_without_connected_is_rejected_before_auth_is_sent() -> None:
    socket = FakeSocket(('[{"T":"success","msg":"authenticated"}]',))
    with pytest.raises(LiveAuthenticationError, match="connected-state transition"):
        next(transport_for_socket(socket).messages())
    assert socket.sent == []


def test_duplicate_connected_frame_is_rejected_during_authentication() -> None:
    connected = '[{"T":"success","msg":"connected"}]'
    socket = FakeSocket((connected, connected))
    with pytest.raises(LiveAuthenticationError, match="authenticated-state transition"):
        next(transport_for_socket(socket).messages())
    assert socket.sent == [
        {"action": "auth", "key": "handshake-key", "secret": "handshake-secret"}
    ]


def test_malformed_handshake_frame_is_rejected() -> None:
    socket = FakeSocket(("not-json",))
    with pytest.raises(LiveTransportError, match="malformed JSON"):
        next(transport_for_socket(socket).messages())
    assert socket.sent == []


def test_authentication_wait_is_bounded_and_subscription_is_not_sent() -> None:
    socket = FakeSocket(
        ('[{"T":"success","msg":"connected"}]', TimeoutError())
    )
    transport = transport_for_socket(socket, handshake_timeout_seconds=0.25)
    with pytest.raises(LiveAuthenticationError, match="timed out waiting for authenticated"):
        next(transport.messages())
    assert len(socket.sent) == 1


def test_bar_before_authentication_fails_without_reaching_stage14_1() -> None:
    bar = bullish_signal_bars()[0]
    socket = FakeSocket(
        (
            '[{"T":"success","msg":"connected"}]',
            json.dumps([live_message(bar)]),
        )
    )
    transport = transport_for_socket(socket)
    source = MemorySource(prior_bars() + bullish_signal_bars()[:5])
    service = LiveSignalEngineService(
        LiveBootstrapper(source, calendar=CALENDAR),
        transport,
        clock=lambda: bar.timestamp + timedelta(minutes=1),
    )
    with pytest.raises(LiveAuthenticationError, match="authenticated-state transition"):
        service.run(as_of=OPEN + timedelta(minutes=5), max_bars=1)
    assert len(socket.sent) == 1


def test_transport_rejects_insecure_injected_tls_context() -> None:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with pytest.raises(LiveTransportError, match="certificate and hostname verification"):
        AlpacaSipWebSocketTransport(
            api_key=SecretStr("tls-key"),
            secret_key=SecretStr("tls-secret"),
            ssl_context=context,
        )


def test_live_report_hash_is_deterministic() -> None:
    bars = bearish_signal_bars()
    source = MemorySource(prior_bars() + bars[:5])
    received = iter(bar.timestamp + timedelta(minutes=1) for bar in bars[5:])
    report = LiveSignalEngineService(
        LiveBootstrapper(source, calendar=CALENDAR),
        MemoryTransport(tuple(live_message(bar) for bar in bars[5:])),
        clock=lambda: next(received),
    ).run(as_of=OPEN + timedelta(minutes=5), max_bars=5)
    assert len(report.signals) == 1
    assert live_signal_report_hash(report) == (
        "ee1b0734f7097244a1acad4219b0a8eb52cb3706c3791eddd47f0b0fb5705484"
    )
