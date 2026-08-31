"""Immutable Stage 15.1 negative-condition exclusion validation models."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ExclusionClassification(StrEnum):
    NO_IMPROVEMENT = "NO_IMPROVEMENT"
    DESCRIPTIVELY_IMPROVED = "DESCRIPTIVELY_IMPROVED"
    RESEARCH_EXCLUSION_CANDIDATE = "RESEARCH_EXCLUSION_CANDIDATE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class RoomDiagnosticClassification(StrEnum):
    ENTRY_BEHAVIOR_SUPPORTED = "ENTRY_BEHAVIOR_SUPPORTED"
    EXIT_GEOMETRY_DEPENDENT = "EXIT_GEOMETRY_DEPENDENT"
    MIXED = "MIXED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class ExclusionMonthlyRow(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    month: str
    trades: int = Field(ge=0)
    mean_r: Decimal | None
    median_r: Decimal | None
    total_r: Decimal
    baseline_trades: int = Field(ge=0)
    retained_percentage: Decimal | None


class ExclusionPeriodRow(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    period: Literal["PRE_DEVELOPMENT", "DEVELOPMENT", "EXPANDED"]
    trades: int = Field(ge=0)
    mean_r: Decimal | None
    baseline_mean_r: Decimal | None
    mean_r_delta: Decimal | None
    median_r: Decimal | None
    profit_factor: Decimal | None


class ExclusionMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    original_membership: int = Field(ge=0)
    retained_membership: int = Field(ge=0)
    retained_percentage: Decimal
    realized_retained: int = Field(ge=0)
    unavailable_or_ambiguous_retained: int = Field(ge=0)
    sessions: int = Field(ge=0)
    win_rate: Decimal | None
    mean_r: Decimal | None
    median_r: Decimal | None
    standard_deviation_r: Decimal | None
    profit_factor: Decimal | None
    target_hit_rate: Decimal | None
    stop_hit_rate: Decimal | None
    eod_exit_rate: Decimal | None
    median_mfe: Decimal | None
    median_mae: Decimal | None
    fifth_percentile_r: Decimal | None
    positive_months: int = Field(ge=0)
    negative_months: int = Field(ge=0)
    worst_month: str | None
    worst_month_mean_r: Decimal | None
    leave_one_month_out_min_mean_r: Decimal | None
    bootstrap_mean_r_low: Decimal | None
    bootstrap_mean_r_median: Decimal | None
    bootstrap_mean_r_high: Decimal | None
    monthly: tuple[ExclusionMonthlyRow, ...]
    periods: tuple[ExclusionPeriodRow, ...]

    @model_validator(mode="after")
    def reconcile(self) -> Self:
        if self.retained_membership != self.realized_retained + self.unavailable_or_ambiguous_retained:
            raise ValueError("retained membership must reconcile")
        return self


class RemovalAudit(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    variant_id: str
    condition_ids: tuple[int, ...]
    unique_membership_removed: int = Field(ge=0)
    realized_removed: int = Field(ge=0)
    unavailable_or_ambiguous_removed: int = Field(ge=0)
    sessions_affected: int = Field(ge=0)
    months_affected: int = Field(ge=0)


class ConditionOverlapCell(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    left_condition: int = Field(ge=1, le=4)
    right_condition: int = Field(ge=1, le=4)
    membership_overlap: int = Field(ge=0)
    realized_overlap: int = Field(ge=0)


class ConditionAudit(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    condition_id: int = Field(ge=1, le=4)
    condition_name: str
    membership_n: int = Field(ge=0)
    realized_n: int = Field(ge=0)
    unavailable_or_ambiguous_n: int = Field(ge=0)
    unique_membership_n: int = Field(ge=0)
    unique_realized_n: int = Field(ge=0)
    sessions: int = Field(ge=0)
    months: int = Field(ge=0)
    stage15_mean_r: Decimal
    stage15_fdr_q_value: Decimal


class RoomGeometryDiagnostic(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    variant_id: str
    removed_realized_n: int = Field(ge=0)
    removed_sessions: int = Field(ge=0)
    removed_median_five_mfe_atr: Decimal | None
    retained_median_five_mfe_atr: Decimal | None
    removed_median_five_mae_atr: Decimal | None
    retained_median_five_mae_atr: Decimal | None
    favorable_excursion_delta: Decimal | None
    adverse_excursion_delta: Decimal | None
    classification: RoomDiagnosticClassification


class ExclusionVariantResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    variant_id: str
    condition_ids: tuple[int, ...]
    removal: RemovalAudit
    metrics: ExclusionMetrics
    mean_r_delta: Decimal | None
    median_r_delta: Decimal | None
    profit_factor_delta: Decimal | None
    lomo_min_delta: Decimal | None
    bootstrap_delta_low: Decimal | None
    bootstrap_delta_median: Decimal | None
    bootstrap_delta_high: Decimal | None
    retains_70_percent_realized: bool
    represents_80_sessions: bool
    month_concentration_pass: bool
    no_heavily_reduced_month: bool
    pre_development_improves: bool
    development_improves: bool
    classification: ExclusionClassification
    room_diagnostic: RoomGeometryDiagnostic | None


class ExclusionValidationReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    symbol: Literal["SPY"] = "SPY"
    start_date: date
    end_date: date
    baseline_candidate: Literal[
        "BASE_SHORT:NEXT_OBJECTIVE_LEVEL:ATR_1_00:NO_FIXED_TARGET"
    ] = "BASE_SHORT:NEXT_OBJECTIVE_LEVEL:ATR_1_00:NO_FIXED_TARGET"
    baseline: ExclusionMetrics
    conditions: tuple[ConditionAudit, ...]
    overlap_matrix: tuple[ConditionOverlapCell, ...]
    variants: tuple[ExclusionVariantResult, ...]
    source_stage15_report_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    report_version: Literal["stage15-1-negative-exclusion-validation-v1"] = (
        "stage15-1-negative-exclusion-validation-v1"
    )
    research_warning: str = (
        "Predeclared exclusion validation only; no live filter or candidate is authorized."
    )

    @model_validator(mode="after")
    def reconcile(self) -> Self:
        if tuple(item.condition_id for item in self.conditions) != (1, 2, 3, 4):
            raise ValueError("conditions must remain frozen in 1-4 order")
        if len(self.overlap_matrix) != 16:
            raise ValueError("overlap matrix must contain every ordered pair")
        expected = (
            "BASE_SHORT_CONTROL", "EXCLUDE_NEG_1", "EXCLUDE_NEG_2",
            "EXCLUDE_NEG_3", "EXCLUDE_NEG_4", "EXCLUDE_ANY_OF_1_TO_4",
            "EXCLUDE_NEG_1_2", "EXCLUDE_NEG_1_4", "EXCLUDE_NEG_2_4",
            "EXCLUDE_NEG_1_2_4",
        )
        if tuple(item.variant_id for item in self.variants) != expected:
            raise ValueError("variant universe must remain exactly predeclared")
        return self
