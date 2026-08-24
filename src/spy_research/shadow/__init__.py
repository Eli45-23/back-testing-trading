"""Stage 14.3 deterministic market-data-only shadow forward testing."""

from spy_research.shadow.engine import (
    CANDIDATE_MULTIPLIERS,
    ShadowForwardStateMachine,
)
from spy_research.shadow.historical import ShadowHistoricalEquivalenceService
from spy_research.shadow.models import (
    LiveShadowRunReport,
    ShadowEventType,
    ShadowHistoricalEquivalence,
    ShadowHistoricalReport,
    ShadowInputError,
    ShadowPosition,
    ShadowState,
    ShadowTransitionEvent,
    live_shadow_report_hash,
    shadow_historical_report_hash,
)
from spy_research.shadow.service import LiveShadowForwardTestService

__all__ = [
    "CANDIDATE_MULTIPLIERS",
    "LiveShadowForwardTestService",
    "LiveShadowRunReport",
    "ShadowEventType",
    "ShadowForwardStateMachine",
    "ShadowHistoricalEquivalence",
    "ShadowHistoricalEquivalenceService",
    "ShadowHistoricalReport",
    "ShadowInputError",
    "ShadowPosition",
    "ShadowState",
    "ShadowTransitionEvent",
    "live_shadow_report_hash",
    "shadow_historical_report_hash",
]
