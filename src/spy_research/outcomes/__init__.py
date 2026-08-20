"""Post-event, same-session price-excursion outcome research."""

from spy_research.outcomes.mfe_mae import (
    EmaCrossOutcomeService,
    OutcomeInputValidationError,
    OutcomeSequenceError,
    OutcomeWindowSelection,
    SelectedHorizon,
    calculate_event_outcome,
    calculate_excursion,
    outcome_start_timestamp,
    select_outcome_windows,
)
from spy_research.outcomes.models import (
    EmaCrossOutcome,
    EmaCrossOutcomeContextResult,
    EmaCrossOutcomeResult,
    EnrichedEmaCrossOutcome,
    ExcursionResult,
    HorizonOutcome,
    OppositeCrossContext,
)
from spy_research.outcomes.opposite_cross import (
    EmaCrossOutcomeContextService,
    OppositeCrossSequenceError,
    attach_next_opposite_cross,
)

__all__ = [
    "EmaCrossOutcome",
    "EmaCrossOutcomeContextResult",
    "EmaCrossOutcomeContextService",
    "EmaCrossOutcomeResult",
    "EmaCrossOutcomeService",
    "EnrichedEmaCrossOutcome",
    "ExcursionResult",
    "HorizonOutcome",
    "OutcomeInputValidationError",
    "OppositeCrossContext",
    "OppositeCrossSequenceError",
    "OutcomeSequenceError",
    "OutcomeWindowSelection",
    "SelectedHorizon",
    "calculate_event_outcome",
    "calculate_excursion",
    "outcome_start_timestamp",
    "select_outcome_windows",
    "attach_next_opposite_cross",
]
