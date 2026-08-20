"""Deterministic completed-candle research event detection."""

from spy_research.events.ema_cross import (
    EmaCrossEventService,
    EventContextAlignmentError,
    detect_ema_crosses,
    detect_session_ema_crosses,
)
from spy_research.events.models import (
    DetectedEmaCross,
    EmaCrossCalculationResult,
    EmaCrossDirection,
    EmaCrossEvent,
    EmaCrossSessionSummary,
)

__all__ = [
    "DetectedEmaCross",
    "EmaCrossCalculationResult",
    "EmaCrossDirection",
    "EmaCrossEvent",
    "EmaCrossEventService",
    "EmaCrossSessionSummary",
    "EventContextAlignmentError",
    "detect_ema_crosses",
    "detect_session_ema_crosses",
]
