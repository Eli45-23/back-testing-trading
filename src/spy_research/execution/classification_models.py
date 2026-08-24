"""Immutable Stage 13.3 execution-variant classification results."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import StrEnum
from hashlib import sha256
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.execution.exit_models import ExitFamily
from spy_research.execution.models import StrategyPopulation


class ExecutionClassificationInputError(ValueError):
    """Frozen Stage 13.2 statistics cannot form a Stage 13.3 report."""


class ExecutionVariantClassification(StrEnum):
    RETAIN_AS_CONTROL = "RETAIN_AS_CONTROL"
    FORWARD_TEST_CANDIDATE = "FORWARD_TEST_CANDIDATE"
    ROBUST_EXECUTION_CANDIDATE = "ROBUST_EXECUTION_CANDIDATE"
    DO_NOT_ADVANCE = "DO_NOT_ADVANCE"


class ExecutionWarning(StrEnum):
    NEGATIVE_EXPANDED_MEAN = "NEGATIVE_EXPANDED_MEAN"
    NEGATIVE_EXPANDED_MEDIAN = "NEGATIVE_EXPANDED_MEDIAN"
    NEGATIVE_JANUARY_JULY_MEAN = "NEGATIVE_JANUARY_JULY_MEAN"
    NEGATIVE_DEVELOPMENT_MEAN = "NEGATIVE_DEVELOPMENT_MEAN"
    NEGATIVE_WORST_LOO_MEAN = "NEGATIVE_WORST_LOO_MEAN"
    BOOTSTRAP_INTERVAL_CROSSES_ZERO = "BOOTSTRAP_INTERVAL_CROSSES_ZERO"
    BOOTSTRAP_INTERVAL_BELOW_ZERO = "BOOTSTRAP_INTERVAL_BELOW_ZERO"
    INSUFFICIENT_MONTHLY_STABILITY = "INSUFFICIENT_MONTHLY_STABILITY"
    INSUFFICIENT_REALIZED_PATHS = "INSUFFICIENT_REALIZED_PATHS"
    INSUFFICIENT_SESSION_COVERAGE = "INSUFFICIENT_SESSION_COVERAGE"


class ExecutionGateResults(BaseModel):
    """Every predeclared Stage 13.3 gate, exposed without interpretation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    realized_paths_at_least_100: bool
    represented_sessions_at_least_50: bool
    expanded_mean_positive: bool
    expanded_median_positive: bool
    january_july_mean_positive: bool
    development_mean_positive: bool
    worst_loo_mean_nonnegative: bool
    at_least_five_positive_monthly_medians: bool
    bootstrap_mean_lower_bound_positive: bool

    @property
    def coverage_passed(self) -> bool:
        return (
            self.realized_paths_at_least_100
            and self.represented_sessions_at_least_50
        )

    @property
    def robust_passed(self) -> bool:
        return self.coverage_passed and all(
            (
                self.expanded_mean_positive,
                self.expanded_median_positive,
                self.january_july_mean_positive,
                self.development_mean_positive,
                self.worst_loo_mean_nonnegative,
                self.at_least_five_positive_monthly_medians,
                self.bootstrap_mean_lower_bound_positive,
            )
        )

    @property
    def forward_test_passed(self) -> bool:
        return self.coverage_passed and all(
            (
                self.expanded_mean_positive,
                self.january_july_mean_positive,
                self.at_least_five_positive_monthly_medians,
            )
        )


class ExecutionVariantClassificationRow(BaseModel):
    """One frozen BASE_SHORT execution variant and its mechanical result."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    strategy_population: Literal[StrategyPopulation.BASE_SHORT]
    variant_id: str
    family: ExitFamily
    stop_multiplier: Decimal
    exit_definition: str
    realized_paths: int = Field(ge=0)
    session_count: int = Field(ge=0)
    expanded_mean_r: Decimal
    expanded_median_r: Decimal
    january_july_mean_r: Decimal
    january_july_median_r: Decimal
    development_mean_r: Decimal
    development_median_r: Decimal
    positive_month_count: int = Field(ge=0)
    negative_month_count: int = Field(ge=0)
    zero_month_count: int = Field(ge=0)
    worst_loo_mean_r: Decimal
    bootstrap_mean_p2_5: Decimal
    bootstrap_mean_p50: Decimal
    bootstrap_mean_p97_5: Decimal
    gates: ExecutionGateResults
    classification: ExecutionVariantClassification
    warnings: tuple[ExecutionWarning, ...]

    @model_validator(mode="after")
    def reconcile_classification(self) -> Self:
        month_count = (
            self.positive_month_count
            + self.negative_month_count
            + self.zero_month_count
        )
        if month_count != 8:
            raise ValueError("Stage 13.3 requires exactly eight monthly median results")
        is_control = self.family is ExitFamily.FIXED_R_CONTROL
        if is_control:
            expected = ExecutionVariantClassification.RETAIN_AS_CONTROL
        elif self.gates.robust_passed:
            expected = ExecutionVariantClassification.ROBUST_EXECUTION_CANDIDATE
        elif self.gates.forward_test_passed:
            expected = ExecutionVariantClassification.FORWARD_TEST_CANDIDATE
        else:
            expected = ExecutionVariantClassification.DO_NOT_ADVANCE
        if self.classification is not expected:
            raise ValueError("classification does not follow the frozen gates")
        return self


class ExecutionControlReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    strategy_population: StrategyPopulation
    variant_id: str
    reason: Literal["UNIVERSAL_RESEARCH_CONTROL", "FIXED_R_REFERENCE"]


class Stage14ExecutionHandoff(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    robust_candidates: tuple[str, ...]
    forward_test_candidates: tuple[str, ...]
    controls: tuple[ExecutionControlReference, ...]
    rejected_variants: tuple[str, ...]
    framing: Literal[
        "Prospective forward/paper-validation infrastructure; not deployment of a "
        "historically validated profitable strategy."
    ] = (
        "Prospective forward/paper-validation infrastructure; not deployment of a "
        "historically validated profitable strategy."
    )


class ExecutionVariantClassificationReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    start_date: date
    end_date: date
    source_stage13_2_hash: str
    source_stage13_1_hash: str
    rows: tuple[ExecutionVariantClassificationRow, ...]
    handoff: Stage14ExecutionHandoff
    report_version: Literal["stage13-3-controlled-execution-classification-v1"] = (
        "stage13-3-controlled-execution-classification-v1"
    )
    caveat: str = (
        "Mechanical classification of frozen Stage 13.2 statistical records; "
        "no ranking, optimization, new candidate, or deployment recommendation."
    )

    @model_validator(mode="after")
    def reconcile_report(self) -> Self:
        if len(self.rows) != 36 or len({row.variant_id for row in self.rows}) != 36:
            raise ValueError("Stage 13.3 requires all 36 unique BASE_SHORT variants")
        by_class = {
            state: tuple(
                row.variant_id for row in self.rows if row.classification is state
            )
            for state in ExecutionVariantClassification
        }
        if self.handoff.robust_candidates != by_class[
            ExecutionVariantClassification.ROBUST_EXECUTION_CANDIDATE
        ]:
            raise ValueError("robust-candidate handoff mismatch")
        if self.handoff.forward_test_candidates != by_class[
            ExecutionVariantClassification.FORWARD_TEST_CANDIDATE
        ]:
            raise ValueError("forward-test handoff mismatch")
        if self.handoff.rejected_variants != by_class[
            ExecutionVariantClassification.DO_NOT_ADVANCE
        ]:
            raise ValueError("rejected-variant handoff mismatch")
        expected_controls = tuple(
            ExecutionControlReference(
                strategy_population=StrategyPopulation.BASE_ALL,
                variant_id=row.variant_id,
                reason="UNIVERSAL_RESEARCH_CONTROL",
            )
            for row in self.rows
        ) + tuple(
            ExecutionControlReference(
                strategy_population=StrategyPopulation.BASE_SHORT,
                variant_id=row.variant_id,
                reason="FIXED_R_REFERENCE",
            )
            for row in self.rows
            if row.classification
            is ExecutionVariantClassification.RETAIN_AS_CONTROL
        )
        if self.handoff.controls != expected_controls:
            raise ValueError("control handoff must preserve BASE_ALL and fixed-R")
        return self


def execution_variant_classification_hash(
    report: ExecutionVariantClassificationReport,
) -> str:
    return sha256(report.model_dump_json().encode()).hexdigest()
