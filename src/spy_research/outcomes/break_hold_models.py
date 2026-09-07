"""Versioned underlying-price measurements, distinct from EMA research."""
from decimal import Decimal
from typing import Literal

from pydantic import AwareDatetime
from spy_research.events.break_and_hold_models import FrozenModel, HoldSignal


class WindowMeasurement(FrozenModel):
    horizon: str
    complete: bool
    observed_minutes: int
    requested_end: AwareDatetime
    observed_end: AwareDatetime | None
    mfe: Decimal | None
    mae: Decimal | None
    directional_return: Decimal | None
    mfe_timestamp: AwareDatetime | None
    mae_timestamp: AwareDatetime | None
    minutes_to_mfe: int | None
    minutes_to_mae: int | None


class ThresholdMeasurement(FrozenModel):
    favorable: Decimal
    adverse: Decimal
    favorable_hit: AwareDatetime | None
    adverse_hit: AwareDatetime | None
    result: Literal["FAVORABLE_FIRST", "ADVERSE_FIRST", "AMBIGUOUS_SAME_BAR", "NEITHER", "NO_FUTURE_DATA"]


class HoldOutcome(FrozenModel):
    signal: HoldSignal
    orh5: Decimal
    orl5: Decimal
    reclaim_timestamp: AwareDatetime | None
    windows: tuple[WindowMeasurement, ...]
    thresholds: tuple[ThresholdMeasurement, ...]
    outcome_version: Literal["break_hold_strict_future_minute_v1"] = "break_hold_strict_future_minute_v1"
