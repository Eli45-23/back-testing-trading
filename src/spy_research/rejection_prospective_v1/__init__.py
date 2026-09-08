"""Frozen prospective Rejection Validation V1 design.

This package is deliberately design-only: it contains no market-data loader,
broker client, paper/live execution path, or outcome runner.
"""

from .models import CandidateSpec, ProspectiveSession, ReadinessResult
from .protocol import (
    BOOTSTRAP_DRAWS,
    BOOTSTRAP_SEED,
    CANDIDATES,
    CONTROL,
    DEVELOPMENT_END,
    ENTRY_VARIANT,
    MODELS,
    PROSPECTIVE_END,
    PROSPECTIVE_START,
    protocol_hash,
)
from .guards import build_session_plan, evaluate_readiness, validate_outcome_date

__all__ = [
    "BOOTSTRAP_DRAWS",
    "BOOTSTRAP_SEED",
    "CANDIDATES",
    "CONTROL",
    "DEVELOPMENT_END",
    "ENTRY_VARIANT",
    "MODELS",
    "PROSPECTIVE_END",
    "PROSPECTIVE_START",
    "CandidateSpec",
    "ProspectiveSession",
    "ReadinessResult",
    "build_session_plan",
    "evaluate_readiness",
    "protocol_hash",
    "validate_outcome_date",
]
