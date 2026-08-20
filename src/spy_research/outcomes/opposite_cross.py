"""Descriptive same-session next-opposite-cross context for fixed outcomes."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.events.models import EmaCrossEvent
from spy_research.outcomes.mfe_mae import EmaCrossOutcomeService
from spy_research.outcomes.models import (
    EmaCrossOutcome,
    EmaCrossOutcomeContextResult,
    EnrichedEmaCrossOutcome,
    OppositeCrossContext,
)


class OppositeCrossSequenceError(ValueError):
    """Events and outcomes cannot be safely aligned for reversal lookup."""


def _event_identity(event: EmaCrossEvent) -> tuple[object, ...]:
    return event.symbol, event.timestamp, event.direction, event.event_version


def attach_next_opposite_cross(
    events: Sequence[EmaCrossEvent],
    outcomes: Sequence[EmaCrossOutcome],
) -> tuple[EnrichedEmaCrossOutcome, ...]:
    """Attach the first later opposite event without changing base outcomes."""

    if len(events) != len(outcomes):
        raise OppositeCrossSequenceError("Event/outcome sequences must have equal length")
    previous_timestamp = None
    identities = set()
    for event, outcome in zip(events, outcomes, strict=True):
        identity = _event_identity(event)
        if identity in identities:
            raise OppositeCrossSequenceError("Duplicate event identity")
        if previous_timestamp is not None and event.timestamp <= previous_timestamp:
            raise OppositeCrossSequenceError(
                "Event sequence must be strictly chronological"
            )
        if _event_identity(outcome.event) != identity:
            raise OppositeCrossSequenceError("Outcome/event identity mismatch")
        if outcome.session_date != event.session_date:
            raise OppositeCrossSequenceError("Outcome/event session linkage mismatch")
        identities.add(identity)
        previous_timestamp = event.timestamp

    enriched = []
    for index, (event, outcome) in enumerate(zip(events, outcomes, strict=True)):
        opposite = next(
            (
                candidate
                for candidate in events[index + 1 :]
                if candidate.session_date == event.session_date
                and candidate.direction != event.direction
            ),
            None,
        )
        if opposite is None:
            context = OppositeCrossContext(
                opposite_cross_timestamp=None,
                opposite_cross_direction=None,
                minutes_to_opposite_cross=None,
                bars_to_opposite_cross=None,
            )
        else:
            elapsed_seconds = (opposite.timestamp - event.timestamp).total_seconds()
            if elapsed_seconds <= 0 or elapsed_seconds % 300 != 0:
                raise OppositeCrossSequenceError(
                    "Opposite cross timestamps must align to positive five-minute steps"
                )
            elapsed_minutes = int(elapsed_seconds // 60)
            context = OppositeCrossContext(
                opposite_cross_timestamp=opposite.timestamp,
                opposite_cross_direction=opposite.direction,
                minutes_to_opposite_cross=elapsed_minutes,
                bars_to_opposite_cross=elapsed_minutes // 5,
            )
        enriched.append(
            EnrichedEmaCrossOutcome(outcome=outcome, opposite_cross=context)
        )
    return tuple(enriched)


class EmaCrossOutcomeContextService:
    """Calculate unchanged Stage 5.1 outcomes, then attach reversal metadata."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
    ) -> None:
        self._outcome_service = EmaCrossOutcomeService(
            config,
            processed_store,
            raw_store,
        )

    def calculate(self, *, start: date, end: date) -> EmaCrossOutcomeContextResult:
        base_result = self._outcome_service.calculate(start=start, end=end)
        events = tuple(outcome.event for outcome in base_result.outcomes)
        enriched = attach_next_opposite_cross(events, base_result.outcomes)
        return EmaCrossOutcomeContextResult(
            base_result=base_result,
            outcomes=enriched,
        )
