"""Live bootstrap/stream orchestration for Stage 14.3 shadow candidates."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from spy_research.live import (
    LiveAdapterUpdate,
    LiveBootstrapper,
    LiveDataError,
    LiveMessageTransport,
)
from spy_research.market import XNYSCalendar
from spy_research.shadow.engine import ShadowForwardStateMachine
from spy_research.shadow.models import LiveShadowRunReport, ShadowTransitionEvent


class LiveShadowForwardTestService:
    """Reconstruct current state, then shadow-test both candidates live."""

    def __init__(
        self,
        bootstrapper: LiveBootstrapper,
        transport: LiveMessageTransport,
        *,
        calendar: XNYSCalendar | None = None,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._bootstrapper = bootstrapper
        self._transport = transport
        self._calendar = calendar or XNYSCalendar()
        self._clock = clock

    def run(
        self,
        *,
        as_of: datetime | None = None,
        max_bars: int | None = None,
        on_live_update: Callable[
            [LiveAdapterUpdate, tuple[ShadowTransitionEvent, ...]], None
        ]
        | None = None,
    ) -> LiveShadowRunReport:
        if max_bars is not None and max_bars < 1:
            raise LiveDataError("max-bars must be positive")
        started_at = (as_of or self._clock()).astimezone(UTC)
        session_date = started_at.astimezone(ZoneInfo("America/New_York")).date()
        session = self._calendar.session_for_date(session_date)
        machine = ShadowForwardStateMachine(session)
        transitions: list[ShadowTransitionEvent] = []

        def consume_seed(update, levels) -> None:
            transitions.extend(
                machine.consume_live_update(update, available_levels=levels)
            )

        adapter, bootstrap = self._bootstrapper.bootstrap(
            as_of=started_at,
            on_seed_update=consume_seed,
        )
        accepted = duplicates = 0
        for message in self._transport.messages():
            update = adapter.process_message(
                message, received_at=self._clock().astimezone(UTC)
            )
            duplicates += int(update.duplicate_identical)
            shadow_events = machine.consume_live_update(
                update,
                available_levels=adapter.engine.current_levels,
            )
            transitions.extend(shadow_events)
            accepted += int(update.normalized_bar is not None)
            if on_live_update is not None:
                on_live_update(update, shadow_events)
            if max_bars is not None and accepted >= max_bars:
                break
        if bootstrap.session_date != session_date:
            raise LiveDataError("shadow bootstrap session changed unexpectedly")
        return LiveShadowRunReport(
            session_date=session_date,
            accepted_live_bar_count=accepted,
            duplicate_bar_count=duplicates,
            transition_events=tuple(transitions),
            positions=machine.positions,
        )
