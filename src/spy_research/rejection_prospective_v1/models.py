"""Immutable prospective-plan and endpoint-schema models."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .protocol import (
    ATR_CANDIDATE,
    CANDIDATES,
    CONTROL,
    ENTRY_VARIANT,
    MODELS,
    PROSPECTIVE_START,
    SESSION_COUNT,
    validate_decimal,
)


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def reject_float_values(cls, values):
        def visit(value):
            if isinstance(value, float):
                raise ValueError("binary float inputs prohibited")
            if isinstance(value, dict):
                for child in value.values():
                    visit(child)
            elif isinstance(value, (list, tuple)):
                for child in value:
                    visit(child)

        visit(values)
        return values


class ProspectiveSession(FrozenModel):
    """One immutable XNYS session in the fixed 60-session plan."""

    session_date: date
    market_open: datetime
    market_close: datetime
    early_close: bool = False

    @model_validator(mode="after")
    def validate_boundaries(self):
        if self.session_date < PROSPECTIVE_START:
            raise ValueError("session precedes prospective window")
        if self.market_open.tzinfo is None or self.market_close.tzinfo is None:
            raise ValueError("session boundaries must be timezone-aware")
        if self.market_open >= self.market_close:
            raise ValueError("market open must precede close")
        ny = ZoneInfo("America/New_York")
        if self.market_open.astimezone(ny).date() != self.session_date:
            raise ValueError("open/session identity mismatch")
        if self.market_close.astimezone(ny).date() != self.session_date:
            raise ValueError("open/session identity mismatch")
        return self


class CandidateSpec(FrozenModel):
    """Frozen candidate identity and its natural ATR-availability population."""

    name: Literal["USD040_TARGET_2R_BE1R", "USD040_TARGET_1.5R", "ATR050_TARGET_1R", "USD040_TARGET_2R"]
    entry_variant: Literal["IMMEDIATE_CLOSE_BACK_1M"] = ENTRY_VARIANT
    role: Literal["PRIMARY", "SECONDARY", "EXPLORATORY_ATR", "CONTROL"]
    stop_family: Literal["USD040", "ATR050"]
    exit_family: Literal["TARGET_1R", "TARGET_1.5R", "TARGET_2R", "TARGET_2R_BE1R"]
    atr_natural_population: bool = False

    @model_validator(mode="after")
    def identity_is_frozen(self):
        expected = {
            "USD040_TARGET_2R_BE1R": ("PRIMARY", "USD040", "TARGET_2R_BE1R", False),
            "USD040_TARGET_1.5R": ("SECONDARY", "USD040", "TARGET_1.5R", False),
            "ATR050_TARGET_1R": ("EXPLORATORY_ATR", "ATR050", "TARGET_1R", True),
            "USD040_TARGET_2R": ("CONTROL", "USD040", "TARGET_2R", False),
        }
        if self.name not in expected or (self.role, self.stop_family, self.exit_family, self.atr_natural_population) != expected[self.name]:
            raise ValueError("candidate identity does not match frozen matrix")
        return self


class ReadinessResult(FrozenModel):
    """A non-selecting endpoint/readiness decision."""

    status: Literal["INTERIM_NO_SELECTION", "BLOCKED_DATA_QUALITY", "ENDPOINT_REACHED_NO_SELECTION"]
    completed_sessions: int = Field(ge=0, le=SESSION_COUNT)
    validated_sessions: int = Field(ge=0, le=SESSION_COUNT)
    candidate_assessments: dict[str, str] = Field(default_factory=dict)
    missing_or_invalid_sessions: tuple[str, ...] = ()
