"""Bounded dry-run orchestration for bootstrap plus live SIP continuation."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from time import sleep

from spy_research.live.bootstrap import LiveBootstrapper
from spy_research.live.models import (
    LiveAdapterUpdate,
    LiveDataError,
    LiveSignalRunReport,
)
from spy_research.live.transport import LiveMessageTransport


class LiveSignalEngineService:
    """Run market data through Stage 14.1 without any execution capability."""

    def __init__(
        self,
        bootstrapper: LiveBootstrapper,
        transport: LiveMessageTransport,
        *,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        waiter: Callable[[float], None] = sleep,
    ) -> None:
        self._bootstrapper = bootstrapper
        self._transport = transport
        self._clock = clock
        self._waiter = waiter

    def run(
        self,
        *,
        as_of: datetime | None = None,
        max_bars: int | None = None,
        until: datetime | None = None,
        on_update: Callable[[LiveAdapterUpdate], None] | None = None,
    ) -> LiveSignalRunReport:
        if max_bars is not None and max_bars < 1:
            raise LiveDataError("max-bars must be positive")
        if until is not None and until.utcoffset() is None:
            raise LiveDataError("until must be timezone-aware")
        started_at = (as_of or self._clock()).astimezone(UTC)
        adapter, bootstrap = self._bootstrapper.bootstrap(as_of=started_at)
        accepted = duplicates = ignored = 0
        signals = []
        for message in self._transport.messages():
            received_at = self._clock().astimezone(UTC)
            if until is not None and received_at > until.astimezone(UTC):
                break
            preview = adapter.preview(message)
            if (
                preview is not None
                and adapter.last_timestamp is not None
                and preview.timestamp > adapter.last_timestamp + timedelta(minutes=1)
            ):
                bridged = self._bootstrapper.bridge_gap(
                    adapter, before=preview.timestamp
                )
                for bridge_update in bridged:
                    signals.extend(bridge_update.signal_events)
                    if on_update is not None:
                        on_update(bridge_update)
            update = adapter.process_message(message, received_at=received_at)
            if adapter.pending_known_at is not None:
                delay = (
                    adapter.pending_known_at - received_at
                ).total_seconds()
                if delay > 0:
                    self._waiter(delay)
                update = adapter.release_pending(
                    received_at=self._clock().astimezone(UTC)
                )
            duplicates += int(update.duplicate_identical)
            ignored += int(update.ignored_reason is not None)
            if update.normalized_bar is not None:
                accepted += 1
                signals.extend(update.signal_events)
            if on_update is not None:
                on_update(update)
            if max_bars is not None and accepted >= max_bars:
                break
        return LiveSignalRunReport(
            bootstrap=bootstrap,
            accepted_live_bar_count=accepted,
            duplicate_identical_count=duplicates,
            ignored_message_count=ignored,
            signals=tuple(signals),
        )
