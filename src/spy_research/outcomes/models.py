"""Immutable typed models for post-event price-excursion outcomes."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.data.validation import DataValidationReport
from spy_research.events.models import EmaCrossDirection, EmaCrossEvent


class ExcursionResult(BaseModel):
    """Favorable/adverse excursion magnitudes and earliest extreme times."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    mfe: Decimal | None
    mfe_timestamp: datetime | None
    mae: Decimal | None
    mae_timestamp: datetime | None

    @model_validator(mode="after")
    def validate_availability(self) -> Self:
        values = (self.mfe, self.mfe_timestamp, self.mae, self.mae_timestamp)
        if any(value is None for value in values) and not all(
            value is None for value in values
        ):
            raise ValueError("excursion values and timestamps must share availability")
        if self.mfe is not None and (self.mfe < 0 or self.mae < 0):
            raise ValueError("excursion magnitudes must be non-negative")
        return self


class HorizonOutcome(BaseModel):
    """One fixed or EOD horizon with explicit completeness semantics."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    horizon: Literal["5m", "15m", "30m", "60m", "EOD"]
    requested_minutes: int = Field(ge=0)
    observed_minutes: int = Field(ge=0)
    complete: bool
    excursion: ExcursionResult


class EmaCrossOutcome(BaseModel):
    """One Stage 4 event and its same-session future one-minute outcomes."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    event: EmaCrossEvent
    symbol: Literal["SPY"]
    session_date: date
    event_timestamp: datetime
    reference_price: Decimal
    outcome_start_timestamp: datetime
    available_future_minutes: int = Field(ge=0)
    five: HorizonOutcome
    fifteen: HorizonOutcome
    thirty: HorizonOutcome
    sixty: HorizonOutcome
    eod: HorizonOutcome
    outcome_version: Literal["post_cross_rth_1m_mfe_mae_v1"] = (
        "post_cross_rth_1m_mfe_mae_v1"
    )

    @model_validator(mode="after")
    def preserve_event_identity(self) -> Self:
        if self.symbol != self.event.symbol:
            raise ValueError("outcome symbol must match event")
        if self.session_date != self.event.session_date:
            raise ValueError("outcome session_date must match event")
        if self.event_timestamp != self.event.timestamp:
            raise ValueError("outcome event_timestamp must match event")
        if self.reference_price != self.event.reference_price:
            raise ValueError("outcome reference_price must match event")
        return self


class EmaCrossOutcomeResult(BaseModel):
    """Validation-gated, in-memory outcomes for a requested event range."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"]
    start_date: date
    end_date: date
    outcomes: tuple[EmaCrossOutcome, ...]
    raw_validation: DataValidationReport


class OppositeCrossContext(BaseModel):
    """First later opposite-direction Stage 4 event in the same RTH session."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    opposite_cross_timestamp: datetime | None
    opposite_cross_direction: EmaCrossDirection | None
    minutes_to_opposite_cross: int | None = Field(default=None, ge=1)
    bars_to_opposite_cross: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_shared_availability(self) -> Self:
        values = (
            self.opposite_cross_timestamp,
            self.opposite_cross_direction,
            self.minutes_to_opposite_cross,
            self.bars_to_opposite_cross,
        )
        if any(value is None for value in values) and not all(
            value is None for value in values
        ):
            raise ValueError("opposite-cross context fields must share availability")
        return self


class EnrichedEmaCrossOutcome(BaseModel):
    """An unchanged Stage 5.1 outcome plus descriptive reversal timing."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    outcome: EmaCrossOutcome
    opposite_cross: OppositeCrossContext
    context_version: Literal["next_same_session_opposite_cross_v1"] = (
        "next_same_session_opposite_cross_v1"
    )


class EmaCrossOutcomeContextResult(BaseModel):
    """Stage 5.1 result retained with an aligned enriched outcome sequence."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    base_result: EmaCrossOutcomeResult
    outcomes: tuple[EnrichedEmaCrossOutcome, ...]
