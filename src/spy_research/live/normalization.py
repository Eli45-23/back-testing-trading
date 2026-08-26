"""Strict Alpaca SIP minute-bar normalization and chronological delivery."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

from pydantic import ValidationError

from spy_research.data.schemas import RawBarRecord
from spy_research.market import MarketSessionClassifier, SessionType, XNYSCalendar
from spy_research.replay import IncrementalSignalStateEngine
from spy_research.live.models import (
    LiveAdapterUpdate,
    LiveDataError,
    LiveSignalEvent,
)


MAX_FINAL_BAR_EARLY_ARRIVAL = timedelta(milliseconds=500)


def _decimal(value: object, field: str) -> Decimal:
    if isinstance(value, bool):
        raise LiveDataError(f"Alpaca live bar has invalid {field}")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise LiveDataError(f"Alpaca live bar has invalid {field}") from None


class AlpacaLiveBarNormalizer:
    """Convert only final SPY SIP minute messages into Stage 14.1 input."""

    REQUIRED_FIELDS = frozenset({"t", "o", "h", "l", "c", "v", "n", "vw"})

    def normalize(self, message: Mapping[str, Any]) -> RawBarRecord | None:
        message_type = message.get("T")
        if message_type != "b":
            return None
        if message.get("S") != "SPY":
            return None
        missing = self.REQUIRED_FIELDS - message.keys()
        if missing:
            raise LiveDataError(
                "Alpaca live SPY bar is missing required market-data fields"
            )
        try:
            timestamp = datetime.fromisoformat(str(message["t"]).replace("Z", "+00:00"))
            if timestamp.utcoffset() is None:
                raise ValueError("timestamp is naive")
            bar = RawBarRecord(
                symbol="SPY",
                timestamp=timestamp.astimezone(UTC),
                open=_decimal(message["o"], "open"),
                high=_decimal(message["h"], "high"),
                low=_decimal(message["l"], "low"),
                close=_decimal(message["c"], "close"),
                volume=int(message["v"]),
                trade_count=int(message["n"]),
                vwap=_decimal(message["vw"], "VWAP"),
                source="alpaca",
                feed="sip",
                timeframe="1Min",
                adjustment="raw",
            )
        except (TypeError, ValueError, ValidationError):
            raise LiveDataError("Alpaca live SPY bar has invalid required fields") from None
        if bar.high < max(bar.open, bar.close, bar.low) or bar.low > min(
            bar.open, bar.close, bar.high
        ):
            raise LiveDataError("Alpaca live SPY bar has invalid OHLC ordering")
        return bar


class LiveMarketDataAdapter:
    """Defensive handoff from closed Alpaca bars to the Stage 14.1 engine."""

    def __init__(
        self,
        engine: IncrementalSignalStateEngine,
        *,
        session_date,
        calendar: XNYSCalendar | None = None,
        normalizer: AlpacaLiveBarNormalizer | None = None,
    ) -> None:
        self._engine = engine
        self._session_date = session_date
        self._calendar = calendar or XNYSCalendar()
        self._classifier = MarketSessionClassifier(self._calendar)
        self._normalizer = normalizer or AlpacaLiveBarNormalizer()
        self._seen: dict[datetime, RawBarRecord] = {}
        self._last_timestamp: datetime | None = None
        self._pending: RawBarRecord | None = None

    @property
    def engine(self) -> IncrementalSignalStateEngine:
        return self._engine

    @property
    def last_timestamp(self) -> datetime | None:
        return self._last_timestamp

    def preview(self, message: Mapping[str, Any]) -> RawBarRecord | None:
        """Normalize a frame without advancing live or replay state."""

        return self._normalizer.normalize(message)

    @property
    def pending_known_at(self) -> datetime | None:
        if self._pending is None:
            return None
        return self._pending.timestamp + timedelta(minutes=1)

    def release_pending(self, *, received_at: datetime) -> LiveAdapterUpdate:
        """Release a retained finalized bar only once its minute is knowable."""

        if received_at.utcoffset() is None:
            raise LiveDataError("live receive timestamp must be timezone-aware")
        if self._pending is None:
            raise LiveDataError("no pending Alpaca minute bar is available")
        bar = self._pending
        known_at = bar.timestamp + timedelta(minutes=1)
        if received_at.astimezone(UTC) < known_at:
            raise LiveDataError("pending Alpaca minute bar is not yet knowable")
        update = self._accept(bar, received_at=received_at.astimezone(UTC))
        self._pending = None
        return update

    def seed(self, bar: RawBarRecord):
        return self._accept(bar, received_at=bar.timestamp + timedelta(minutes=1))

    def process_message(
        self,
        message: Mapping[str, Any],
        *,
        received_at: datetime,
    ) -> LiveAdapterUpdate:
        if received_at.utcoffset() is None:
            raise LiveDataError("live receive timestamp must be timezone-aware")
        bar = self._normalizer.normalize(message)
        if bar is None:
            return LiveAdapterUpdate(ignored_reason="NON_FINAL_OR_NON_SPY_MESSAGE")
        existing = self._seen.get(bar.timestamp)
        if existing is not None:
            return self._accept(bar, received_at=received_at.astimezone(UTC))
        if self._pending is not None:
            if bar.timestamp == self._pending.timestamp:
                if bar == self._pending:
                    return LiveAdapterUpdate(duplicate_identical=True)
                raise LiveDataError("conflicting Alpaca bar for a pending timestamp")
            raise LiveDataError("pending Alpaca bar must release before a later bar")
        received_utc = received_at.astimezone(UTC)
        known_at = bar.timestamp + timedelta(minutes=1)
        if received_utc < known_at:
            if known_at - received_utc > MAX_FINAL_BAR_EARLY_ARRIVAL:
                raise LiveDataError("Alpaca minute bar arrived before closed-bar knowable time")
            self._pending = bar
            return LiveAdapterUpdate(ignored_reason="PENDING_KNOWN_AT")
        return self._accept(bar, received_at=received_utc)

    def _accept(self, bar: RawBarRecord, *, received_at: datetime) -> LiveAdapterUpdate:
        existing = self._seen.get(bar.timestamp)
        if existing is not None:
            if existing == bar:
                return LiveAdapterUpdate(duplicate_identical=True)
            raise LiveDataError("conflicting Alpaca bar for an existing timestamp")
        if self._last_timestamp is not None and bar.timestamp < self._last_timestamp:
            raise LiveDataError("out-of-order Alpaca live bar")
        if received_at < bar.timestamp + timedelta(minutes=1):
            raise LiveDataError("Alpaca minute bar arrived before closed-bar knowable time")
        classified = self._classifier.classify(bar)
        if classified.session_date != self._session_date:
            raise LiveDataError("stale or wrong-session Alpaca live bar")
        if classified.session_type not in (SessionType.PREMARKET, SessionType.RTH):
            return LiveAdapterUpdate(ignored_reason="OUTSIDE_ACCEPTED_LIVE_SESSION")
        replay_update = self._engine.process_one_minute_bar(bar)
        self._seen[bar.timestamp] = bar
        self._last_timestamp = bar.timestamp
        live_signals = tuple(
            LiveSignalEvent.from_replay_update(signal, replay_update)
            for signal in replay_update.signal_events
        )
        return LiveAdapterUpdate(
            normalized_bar=bar,
            replay_update=replay_update,
            signal_events=live_signals,
        )
