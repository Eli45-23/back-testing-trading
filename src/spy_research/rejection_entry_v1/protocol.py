"""Frozen Rejection Entry Study V1 protocol.

This module contains only predeclared research conventions.  It deliberately
does not load market data, call a broker, or choose a trading strategy.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_EVEN
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
import json
from zoneinfo import ZoneInfo


VERSION = "rejection-entry-study-v1"
OUTCOME_START = date(2026, 1, 2)
OUTCOME_END = date(2026, 9, 4)
PROSPECTIVE_START = date(2026, 9, 8)
NY = ZoneInfo("America/New_York")

# The population is inherited from the completed KLR V1 study.  PMH/PML are
# retained in schemas but remain sparse when premarket coverage is uncertified.
LEVEL_FAMILIES = (
    "PDH", "PDL", "PMH", "PML", "ORH5", "ORL5", "PWH", "PWL",
    "1H_HIGH", "1H_LOW",
)
PRIMARY_LEVEL_FAMILIES = (
    "PDH", "PDL", "ORH5", "ORL5", "PWH", "PWL", "1H_HIGH", "1H_LOW",
)
DISTANCES = (Decimal("0.25"), Decimal("0.50"), Decimal("1.00"))
MOMENTUM_AWAY_DISTANCE = Decimal("0.25")
HORIZONS_MINUTES = (5, 15, 30)
BOOTSTRAP_DRAWS = 2_000
BOOTSTRAP_SEED = 20260908
DECIMAL_QUANT = Decimal("0.000000000001")


class EntryFamily(StrEnum):
    IMMEDIATE_CLOSE_BACK = "IMMEDIATE_CLOSE_BACK"
    # Compatibility labels for the two frozen timeframe variants.  They are
    # aliases of the single Immediate Close-Back family, not extra families.
    IMMEDIATE_CLOSE_BACK_1M = "IMMEDIATE_CLOSE_BACK"
    IMMEDIATE_CLOSE_BACK_5M = "IMMEDIATE_CLOSE_BACK"
    MOMENTUM_AWAY = "MOMENTUM_AWAY"
    ONE_RETEST_HOLD = "ONE_RETEST_HOLD"


class SignalStatus(StrEnum):
    CONFIRMED = "CONFIRMED"
    NO_CONFIRMATION = "NO_CONFIRMATION"
    CENSORED_SESSION_CLOSE = "CENSORED_SESSION_CLOSE"
    AMBIGUOUS = "AMBIGUOUS"
    ENTRY_UNAVAILABLE = "ENTRY_UNAVAILABLE"


def guard_outcome_date(day: date) -> None:
    """Fail closed for any result outside the declared development window."""
    if day < OUTCOME_START or day > OUTCOME_END:
        raise ValueError(f"outcome date outside frozen V1 window: {day.isoformat()}")


def guard_outcome_range(start: date, end: date) -> None:
    if start > end:
        raise ValueError("outcome range is reversed")
    guard_outcome_date(start)
    guard_outcome_date(end)


def reject_prospective_date(day: date) -> None:
    """Explicitly reject the Sep 8-Dec 1 prospective break/hold period."""
    if day >= PROSPECTIVE_START:
        raise ValueError("prospective data is outside Rejection Entry V1 scope")


def completion_at(start: datetime, timeframe_minutes: int) -> datetime:
    if start.utcoffset() is None:
        raise ValueError("aware timestamps required")
    if timeframe_minutes not in (1, 5):
        raise ValueError("only completed 1-minute and 5-minute confirmations are frozen")
    return start + timedelta(minutes=timeframe_minutes)


def canonical_protocol() -> dict:
    """Canonical, JSON-safe protocol payload used for provenance hashing."""
    return {
        "version": VERSION,
        "outcome_start": OUTCOME_START.isoformat(),
        "outcome_end": OUTCOME_END.isoformat(),
        "prospective_start": PROSPECTIVE_START.isoformat(),
        "level_families": list(LEVEL_FAMILIES),
        "primary_level_families": list(PRIMARY_LEVEL_FAMILIES),
        "entry_families": [x.value for x in EntryFamily],
        "reaction_distances": [str(x) for x in DISTANCES],
        "momentum_away_distance": str(MOMENTUM_AWAY_DISTANCE),
        "path_horizons_minutes": list(HORIZONS_MINUTES),
        "bootstrap": {"draws": BOOTSTRAP_DRAWS, "seed": BOOTSTRAP_SEED},
        "decimal_quantization": str(DECIMAL_QUANT),
        "no_strategy_pnl": True,
    }


def protocol_hash() -> str:
    payload = json.dumps(canonical_protocol(), sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


def decimal(value: Decimal | str | int) -> Decimal:
    """Convert exact numeric input without ever accepting binary floats."""
    if isinstance(value, float):
        raise TypeError("binary float inputs are prohibited")
    result = value if isinstance(value, Decimal) else Decimal(str(value))
    if not result.is_finite():
        raise ValueError("finite Decimal required")
    return result


def quantize_decimal(value: Decimal) -> Decimal:
    return decimal(value).quantize(DECIMAL_QUANT, rounding=ROUND_HALF_EVEN)
