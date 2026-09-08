"""Design-frozen, offline Rejection Entry Study V1.

Only causal confirmation and wait-cost measurement are implemented.  No
historical outcome runner, broker integration, execution, or P&L model exists.
"""

from .engine import (
    evaluate_interaction,
    first_executable_minute,
    immediate_close_back,
    measure_path,
    momentum_away,
    one_retest_hold,
    pair_measurements,
    pair_signals,
)
from .models import ConfirmationBar, EntrySignal, LevelInteraction, MinuteBar, PairedComparison, PathMeasurement
from .protocol import EntryFamily, SignalStatus, VERSION

__all__ = [
    "VERSION",
    "EntryFamily",
    "SignalStatus",
    "MinuteBar",
    "ConfirmationBar",
    "LevelInteraction",
    "EntrySignal",
    "PathMeasurement",
    "PairedComparison",
    "evaluate_interaction",
    "first_executable_minute",
    "immediate_close_back",
    "momentum_away",
    "one_retest_hold",
    "measure_path",
    "pair_signals",
    "pair_measurements",
]
