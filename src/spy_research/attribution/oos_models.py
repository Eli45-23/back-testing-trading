"""Frozen Stage 15.2 out-of-sample validation design."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.attribution.exclusion_models import (
    ExclusionMetrics,
    RemovalAudit,
    RoomGeometryDiagnostic,
)


class OOSCandidate(StrEnum):
    BASE_SHORT_CONTROL = "BASE_SHORT_CONTROL"
    EXCLUDE_NEG_1 = "EXCLUDE_NEG_1"
    EXCLUDE_NEG_4 = "EXCLUDE_NEG_4"
    EXCLUDE_NEG_1_2 = "EXCLUDE_NEG_1_2"
    EXCLUDE_NEG_1_4 = "EXCLUDE_NEG_1_4"
    EXCLUDE_NEG_1_2_4 = "EXCLUDE_NEG_1_2_4"


class OOSClassification(StrEnum):
    OOS_REPLICATED_RESEARCH_CANDIDATE = "OOS_REPLICATED_RESEARCH_CANDIDATE"
    FAILED_TO_REPLICATE = "FAILED_TO_REPLICATE"
    DESCRIPTIVELY_REPLICATED = "DESCRIPTIVELY_REPLICATED"
    INSUFFICIENT_OOS_DATA = "INSUFFICIENT_OOS_DATA"


class FrozenNegativeCondition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    condition_id: Literal[1, 2, 3, 4]
    factor_left: str
    state_left: str
    factor_right: str
    state_right: str


class OOSPeriod(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    year: Literal[2024, 2025]
    start_date: date
    end_date: date
    required: bool


class OOSValidationDesign(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    report_version: Literal["stage15-2-oos-design-v1"] = "stage15-2-oos-design-v1"
    discovery_cutoff: date = date(2026, 8, 19)
    baseline_candidate: Literal[
        "BASE_SHORT:NEXT_OBJECTIVE_LEVEL:ATR_1_00:NO_FIXED_TARGET"
    ] = "BASE_SHORT:NEXT_OBJECTIVE_LEVEL:ATR_1_00:NO_FIXED_TARGET"
    candidates: tuple[OOSCandidate, ...]
    conditions: tuple[FrozenNegativeCondition, ...]
    periods: tuple[OOSPeriod, ...]
    minimum_realized_retention: Decimal = Field(default=Decimal("0.70"))
    minimum_sessions: int = Field(default=80)
    minimum_represented_months: int = Field(default=4)
    maximum_single_month_share: Decimal = Field(default=Decimal("0.50"))
    minimum_month_retention: Decimal = Field(default=Decimal("0.50"))
    minimum_baseline_month_trades_for_retention_gate: int = Field(default=5)
    bootstrap_resamples: int = Field(default=10_000)
    bootstrap_unit: Literal["XNYS_SESSION"] = "XNYS_SESSION"
    permitted_classifications: tuple[OOSClassification, ...] = tuple(
        OOSClassification
    )
    outcome_accessed_when_frozen: Literal[False] = False

    @model_validator(mode="after")
    def reconcile(self) -> Self:
        if self.candidates != tuple(OOSCandidate):
            raise ValueError("Stage 15.2 candidate universe must remain frozen")
        if tuple(item.condition_id for item in self.conditions) != (1, 2, 3, 4):
            raise ValueError("NEG_1 through NEG_4 must remain frozen")
        if tuple(item.year for item in self.periods) != (2025, 2024):
            raise ValueError("Stage 15.2 periods must remain 2025 then optional 2024")
        return self


def frozen_oos_design() -> OOSValidationDesign:
    return OOSValidationDesign(
        candidates=tuple(OOSCandidate),
        conditions=(
            FrozenNegativeCondition(
                condition_id=1,
                factor_left="VWAP_ALIGNMENT",
                state_left="ALL_ALIGNED",
                factor_right="ROOM_ATR",
                state_right="GT_3_0_ATR",
            ),
            FrozenNegativeCondition(
                condition_id=2,
                factor_left="MARKET_STRUCTURE",
                state_left="BULLISH_STRUCTURE",
                factor_right="ROOM_ATR",
                state_right="ATR_0_5_TO_1_0",
            ),
            FrozenNegativeCondition(
                condition_id=3,
                factor_left="VWAP_ALIGNMENT",
                state_left="NONE_ALIGNED",
                factor_right="ROOM_ATR",
                state_right="ATR_0_5_TO_1_0",
            ),
            FrozenNegativeCondition(
                condition_id=4,
                factor_left="EMA_ALIGNMENT",
                state_left="EMA_ALIGNED",
                factor_right="MARKET_STRUCTURE",
                state_right="BULLISH_STRUCTURE",
            ),
        ),
        periods=(
            OOSPeriod(
                year=2025,
                start_date=date(2025, 1, 2),
                end_date=date(2025, 12, 31),
                required=True,
            ),
            OOSPeriod(
                year=2024,
                start_date=date(2024, 1, 2),
                end_date=date(2024, 12, 31),
                required=False,
            ),
        ),
    )


class OOSCandidateResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    candidate: OOSCandidate
    condition_ids: tuple[int, ...]
    removal: RemovalAudit
    metrics: ExclusionMetrics
    mean_r_delta: Decimal | None
    profit_factor_delta: Decimal | None
    lomo_delta: Decimal | None
    bootstrap_delta_low: Decimal | None
    bootstrap_delta_median: Decimal | None
    bootstrap_delta_high: Decimal | None
    stage15_1_mean_r_delta: Decimal
    direction_agrees_with_stage15_1: bool
    retains_70_percent_realized: bool
    represents_80_sessions: bool
    month_concentration_pass: bool
    no_heavily_reduced_month: bool
    profit_factor_not_deteriorated: bool
    lomo_not_materially_deteriorated: bool
    bootstrap_shift_favorable: bool
    room_diagnostic: RoomGeometryDiagnostic | None
    stage15_1_room_classification: str | None
    room_diagnosis_replicated: bool | None
    claimed_entry_quality_supported: bool
    classification: OOSClassification


class OOSPeriodReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    period: Literal["2024", "2025", "COMBINED_2024_2025"]
    start_date: date
    end_date: date
    baseline: ExclusionMetrics
    candidates: tuple[OOSCandidateResult, ...]
    observation_hash: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def reconcile_candidates(self) -> Self:
        if tuple(item.candidate for item in self.candidates) != tuple(OOSCandidate):
            raise ValueError("OOS report must retain the exact frozen candidate order")
        if self.candidates[0].metrics != self.baseline:
            raise ValueError("OOS control must equal the period baseline")
        return self


class OOSOverallResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    candidate: OOSCandidate
    year_mean_r_deltas: tuple[tuple[str, Decimal | None], ...]
    combined_mean_r_delta: Decimal | None
    all_unseen_years_directionally_agree: bool
    classification: OOSClassification


class OOSValidationReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    report_version: Literal["stage15-2-oos-validation-v1"] = (
        "stage15-2-oos-validation-v1"
    )
    design: OOSValidationDesign
    years: tuple[OOSPeriodReport, ...]
    combined: OOSPeriodReport
    overall: tuple[OOSOverallResult, ...]
    hard_stop_applied: Literal[True] = True

    @model_validator(mode="after")
    def reconcile_periods(self) -> Self:
        if tuple(item.period for item in self.years) != ("2025", "2024"):
            raise ValueError("OOS years must be reported separately in frozen order")
        if self.combined.period != "COMBINED_2024_2025":
            raise ValueError("combined OOS period identity changed")
        if tuple(item.candidate for item in self.overall) != tuple(OOSCandidate):
            raise ValueError("overall OOS classifications must retain frozen order")
        return self
