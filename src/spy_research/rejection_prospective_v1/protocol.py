"""Predeclared Prospective Rejection Validation V1 protocol.

Only fixed design constants and pure validation helpers live here.  The module
never reads market data or contacts Alpaca.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal, localcontext
from hashlib import sha256
import json

VERSION = "rejection-prospective-validation-v1"
DEVELOPMENT_END = date(2026, 9, 4)
PROSPECTIVE_START = date(2026, 9, 8)
PROSPECTIVE_END = date(2026, 12, 1)
SESSION_COUNT = 60

ENTRY_VARIANT = "IMMEDIATE_CLOSE_BACK_1M"
PRIMARY = "USD040_TARGET_2R_BE1R"
SECONDARY = "USD040_TARGET_1.5R"
ATR_CANDIDATE = "ATR050_TARGET_1R"
CONTROL = "USD040_TARGET_2R"
CANDIDATES = (PRIMARY, SECONDARY, ATR_CANDIDATE)
MODELS = (PRIMARY, SECONDARY, ATR_CANDIDATE, CONTROL)

MIN_EXECUTABLE_OUTCOMES = 200
MIN_CONTRIBUTING_SESSIONS = 40
COST_SCENARIOS = (Decimal("0"), Decimal("0.01"), Decimal("0.02"))
AMBIGUITY_SENSITIVITIES = ("stop_first", "target_first")
BOOTSTRAP_DRAWS = 10_000
BOOTSTRAP_SEED = 20260908
BONFERRONI_COMPARISONS = 3
DECIMAL_PRECISION = 80
with localcontext() as _decimal_context:
    _decimal_context.prec = DECIMAL_PRECISION
    BONFERRONI_ALPHA = Decimal("0.05") / Decimal(BONFERRONI_COMPARISONS)


def canonical_protocol() -> dict:
    """Return the complete JSON-safe freeze payload used for hashing."""

    return {
        "version": VERSION,
        "development_end": DEVELOPMENT_END.isoformat(),
        "prospective_start": PROSPECTIVE_START.isoformat(),
        "prospective_end": PROSPECTIVE_END.isoformat(),
        "fixed_sessions": SESSION_COUNT,
        "entry_variant": ENTRY_VARIANT,
        "candidates": list(CANDIDATES),
        "control": CONTROL,
        "models": list(MODELS),
        "minimum_executable_outcomes": MIN_EXECUTABLE_OUTCOMES,
        "minimum_contributing_sessions": MIN_CONTRIBUTING_SESSIONS,
        "entry_semantics": {
            "availability": "completed 1-minute close-back confirmation",
            "executable_entry": "first same-session 1-minute bar OPEN at or after signal availability",
            "include_entry_minute": True,
            "confirming_bar_lookahead": False,
        },
        "atr": {
            "implementation": "existing calculate_session_atr unchanged",
            "fallback": False,
            "prior_session_inheritance": False,
            "unavailable_policy": "retain ATR-unavailable explicitly; no substitution",
        },
        "ambiguity": {
            "primary": "stop_first",
            "sensitivity": "target_first",
            "zero_r_break_even_is_win": False,
        },
        "costs": [str(value) for value in COST_SCENARIOS],
        "bootstrap": {
            "unit": "whole_session",
            "draws": BOOTSTRAP_DRAWS,
            "seed": BOOTSTRAP_SEED,
            "paired_candidate_control": True,
            "bonferroni_comparisons": BONFERRONI_COMPARISONS,
            "bonferroni_alpha": str(BONFERRONI_ALPHA),
        },
        "coverage": {
            "feed": "Alpaca SIP SPY 1-minute RTH",
            "required_every_session": True,
            "missing_data_policy": "block; never fill or replace",
            "automatic_extension": False,
        },
        "interim_status": "INTERIM_NO_SELECTION",
        "historical_outcomes_enabled_in_design": False,
        "network_enabled_in_design": False,
        "paper_live_enabled_in_design": False,
    }


def protocol_hash() -> str:
    payload = json.dumps(canonical_protocol(), sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


def validate_decimal(value: Decimal | str | int) -> Decimal:
    """Accept exact numeric values only; reject binary floats."""

    if isinstance(value, float):
        raise TypeError("binary float inputs are prohibited")
    result = value if isinstance(value, Decimal) else Decimal(str(value))
    if not result.is_finite():
        raise ValueError("finite Decimal required")
    return result
