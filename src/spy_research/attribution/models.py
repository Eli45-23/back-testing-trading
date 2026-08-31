"""Immutable Stage 15 BASE_SHORT attribution records and report models."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AttributionClassification(StrEnum):
    DESCRIPTIVELY_INTERESTING = "DESCRIPTIVELY_INTERESTING"
    RESEARCH_CANDIDATE = "RESEARCH_CANDIDATE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class AttributionObservation(BaseModel):
    """One frozen execution outcome plus features known at signal_known_at."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    session_date: date
    signal_known_at: datetime
    level_type: str
    outcome_status: str
    r_multiple: Decimal | None
    exit_reason: str | None
    mfe: Decimal | None
    mae: Decimal | None
    factors: tuple[tuple[str, str], ...]
    confirmation_atr: Decimal | None = None
    five_minute_mfe: Decimal | None = None
    five_minute_mae: Decimal | None = None
    observation_version: Literal["stage15-base-short-attribution-v1"] = (
        "stage15-base-short-attribution-v1"
    )

    @model_validator(mode="after")
    def reconcile(self) -> Self:
        names = tuple(name for name, _ in self.factors)
        if names != tuple(sorted(names)) or len(names) != len(set(names)):
            raise ValueError("factors must have unique names in sorted order")
        if self.signal_known_at.utcoffset() is None:
            raise ValueError("signal_known_at must be timezone-aware")
        if self.outcome_status == "REALIZED" and self.r_multiple is None:
            raise ValueError("realized observations require R")
        if self.outcome_status != "REALIZED" and self.r_multiple is not None:
            raise ValueError("unrealized observations cannot contain R")
        return self

    def factor(self, name: str) -> str:
        try:
            return dict(self.factors)[name]
        except KeyError as exc:
            raise KeyError(name) from exc


class MonthlyAttribution(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    month: str = Field(pattern=r"^2026-(0[1-9]|1[0-2])$")
    trades: int = Field(ge=0)
    mean_r: Decimal | None
    total_r: Decimal


class AttributionGroup(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    factor: str
    state: str
    population_n: int = Field(ge=0)
    trades: int = Field(ge=0)
    unavailable_or_ambiguous: int = Field(ge=0)
    sessions: int = Field(ge=0)
    win_rate: Decimal | None
    mean_r: Decimal | None
    median_r: Decimal | None
    profit_factor: Decimal | None
    standard_deviation_r: Decimal | None
    target_hit_rate: Decimal | None
    stop_hit_rate: Decimal | None
    eod_exit_rate: Decimal | None
    median_mfe: Decimal | None
    median_mae: Decimal | None
    monthly_performance: tuple[MonthlyAttribution, ...]
    positive_months: int = Field(ge=0)
    negative_months: int = Field(ge=0)
    leave_one_month_out_min_mean_r: Decimal | None
    bootstrap_mean_r_low: Decimal | None
    bootstrap_mean_r_high: Decimal | None
    mean_r_delta_from_baseline: Decimal | None
    raw_p_value: Decimal | None
    fdr_q_value: Decimal | None
    fewer_than_30_trades: bool
    fewer_than_10_sessions: bool
    month_concentration: bool
    classification: AttributionClassification

    @model_validator(mode="after")
    def reconcile(self) -> Self:
        if self.population_n != self.trades + self.unavailable_or_ambiguous:
            raise ValueError("group population must reconcile")
        if self.fewer_than_30_trades != (self.trades < 30):
            raise ValueError("trade sparsity flag mismatch")
        if self.fewer_than_10_sessions != (self.sessions < 10):
            raise ValueError("session sparsity flag mismatch")
        return self


class MultipleTestingSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    family: Literal["SINGLE_FACTOR", "PREDECLARED_INTERACTION"]
    hypotheses: int = Field(ge=0)
    fdr_method: Literal["BENJAMINI_HOCHBERG"] = "BENJAMINI_HOCHBERG"
    fdr_level: Decimal = Decimal("0.10")
    raw_p_le_0_10: int = Field(ge=0)
    fdr_q_le_0_10: int = Field(ge=0)


class AttributionReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    start_date: date
    end_date: date
    candidate_identity: Literal[
        "BASE_SHORT:NEXT_OBJECTIVE_LEVEL:ATR_1_00:NO_FIXED_TARGET"
    ] = "BASE_SHORT:NEXT_OBJECTIVE_LEVEL:ATR_1_00:NO_FIXED_TARGET"
    observation_count: int = Field(ge=0)
    baseline: AttributionGroup
    single_factor_groups: tuple[AttributionGroup, ...]
    interaction_groups: tuple[AttributionGroup, ...]
    multiple_testing: tuple[MultipleTestingSummary, ...]
    fixed_factor_states: tuple[tuple[str, tuple[str, ...]], ...]
    allowed_interactions: tuple[str, ...]
    source_exit_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_stage14_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    report_version: Literal["stage15-base-short-attribution-report-v1"] = (
        "stage15-base-short-attribution-report-v1"
    )
    research_warning: str = (
        "Exploratory attribution only; classifications do not alter or authorize a live candidate."
    )

    @model_validator(mode="after")
    def reconcile(self) -> Self:
        if self.baseline.factor != "BASELINE":
            raise ValueError("baseline row must be explicit")
        if self.baseline.population_n != self.observation_count:
            raise ValueError("baseline must contain every observation")
        factor_states = dict(self.fixed_factor_states)
        expected_single = tuple(
            (factor, state)
            for factor, states in self.fixed_factor_states
            for state in states
        )
        if tuple((item.factor, item.state) for item in self.single_factor_groups) != expected_single:
            raise ValueError("single-factor rows must use the complete frozen state universe")
        for factor in factor_states:
            if sum(
                item.population_n
                for item in self.single_factor_groups
                if item.factor == factor
            ) != self.observation_count:
                raise ValueError(f"{factor} must partition every observation")
        expected_interactions = tuple(
            (name, f"{left_state}×{right_state}")
            for name in self.allowed_interactions
            for left, right in (name.split("×"),)
            for left_state in factor_states[left]
            for right_state in factor_states[right]
        )
        if tuple((item.factor, item.state) for item in self.interaction_groups) != expected_interactions:
            raise ValueError("interaction rows must use only the complete predeclared universe")
        for interaction in self.allowed_interactions:
            if sum(
                item.population_n
                for item in self.interaction_groups
                if item.factor == interaction
            ) != self.observation_count:
                raise ValueError(f"{interaction} must partition every observation")
        return self
