"""Deterministic design-stage reporting schemas; no outcome writer is enabled."""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

from .models import EntrySignal, LevelInteraction, PairedComparison, PathMeasurement
from .protocol import canonical_protocol, protocol_hash


def _default(value: Any):
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if hasattr(value, "value"):
        return value.value
    raise TypeError(type(value).__name__)


def canonical_json(value: Any) -> str:
    """Canonical JSON for manifests/rows, retaining Decimal strings."""
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="python")
    return json.dumps(value, default=_default, sort_keys=True, separators=(",", ":"))


def design_record() -> dict[str, Any]:
    return {
        "protocol": canonical_protocol(),
        "protocol_hash": protocol_hash(),
        "outcome_run_performed": False,
        "outcome_artifacts": (),
        "denominator": "all eligible frozen KLR interactions",
        "performance_metrics": (),
    }


def schema_names() -> tuple[str, ...]:
    return (
        "LevelInteraction",
        "EntrySignal",
        "PathMeasurement",
        "PairedComparison",
        "PopulationSummary",
    )


def row_kind(value: Any) -> str:
    if isinstance(value, (LevelInteraction, EntrySignal, PathMeasurement, PairedComparison)):
        return type(value).__name__
    raise TypeError("unsupported report row")
