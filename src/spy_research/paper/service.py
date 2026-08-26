"""Stage 14.4 live orchestration over accepted bootstrap, market data, and shadow state."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from time import sleep
from zoneinfo import ZoneInfo

from spy_research.live import (
    LiveAdapterUpdate,
    LiveBootstrapper,
    LiveDataError,
    LiveMessageTransport,
)
from spy_research.market import XNYSCalendar
from spy_research.paper.engine import PaperExecutionEngine
from spy_research.paper.models import PaperRunReport
from spy_research.shadow import ShadowForwardStateMachine, ShadowTransitionEvent


class LivePaperTradingService:
    """Reconstruct first, then allow only selected-candidate paper actions."""

    def __init__(
        self,
        bootstrapper: LiveBootstrapper,
        transport: LiveMessageTransport,
        execution: PaperExecutionEngine,
        *,
        calendar: XNYSCalendar | None = None,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        waiter: Callable[[float], None] = sleep,
    ) -> None:
        self._bootstrapper = bootstrapper
        self._transport = transport
        self._execution = execution
        self._calendar = calendar or XNYSCalendar()
        self._clock = clock
        self._waiter = waiter

    def run(
        self,
        *,
        as_of: datetime | None = None,
        max_bars: int | None = None,
        on_update: Callable[
            [LiveAdapterUpdate, tuple[ShadowTransitionEvent, ...]], None
        ]
        | None = None,
    ) -> PaperRunReport:
        if max_bars is not None and max_bars < 1:
            raise LiveDataError("max-bars must be positive")
        started_at = (as_of or self._clock()).astimezone(UTC)
        session_date = started_at.astimezone(ZoneInfo("America/New_York")).date()
        session = self._calendar.session_for_date(session_date)
        shadow = ShadowForwardStateMachine(session)

        def seed(update, levels) -> None:
            shadow.consume_live_update(update, available_levels=levels)

        adapter, bootstrap = self._bootstrapper.bootstrap(
            as_of=started_at, on_seed_update=seed
        )
        if bootstrap.session_date != session_date:
            raise LiveDataError("paper bootstrap session changed unexpectedly")
        self._execution.recover(shadow.positions, now=started_at)
        accepted = 0
        for message in self._transport.messages():
            received_at = self._clock().astimezone(UTC)
            preview = adapter.preview(message)
            if (
                preview is not None
                and adapter.last_timestamp is not None
                and preview.timestamp > adapter.last_timestamp + timedelta(minutes=1)
            ):
                # Recovered historical minutes rebuild deterministic signal/shadow
                # state, but their past entry events are never broker-actionable.
                self._bootstrapper.bridge_gap(
                    adapter,
                    before=preview.timestamp,
                    on_seed_update=lambda update, levels: shadow.consume_live_update(
                        update, available_levels=levels
                    ),
                )
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
            shadow_events = shadow.consume_live_update(
                update, available_levels=adapter.engine.current_levels
            )
            for event in shadow_events:
                self._execution.handle_shadow_event(event, now=received_at)
            self._execution.reconcile_broker_state(now=received_at)
            self._execution.enforce_session_close(now=received_at)
            accepted += int(update.normalized_bar is not None)
            if on_update is not None:
                on_update(update, shadow_events)
            if max_bars is not None and accepted >= max_bars:
                break
        return PaperRunReport(
            session_date=session_date,
            candidate=self._execution.candidate,
            qty=self._execution.qty,
            paper_orders_enabled=self._execution.orders_enabled,
            actions=self._execution.actions,
            executions=self._execution.executions,
        )
