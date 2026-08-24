"""Pure Stage 12.3 controlled strategy-variant selection.

Candidate membership is frozen from accepted confirmation-time annotations before
any Stage 9 outcome is joined.  The ten variants and seven advancement criteria
are deliberately closed enums so this layer cannot search arbitrary combinations.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from datetime import date, datetime
from decimal import Decimal, localcontext
from enum import StrEnum
from hashlib import sha256
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.indicators.ema import EMA_CONTEXT
from spy_research.interactions import LevelType
from spy_research.research_stats import (
    FavorableAdverseCounts,
    summarize_distribution,
)
from spy_research.strategy.base_statistics import BaseStrategyHorizonStatistics
from spy_research.strategy.comparisons import (
    Ema20VwapAlignmentState,
    StructureAgreementState,
)
from spy_research.strategy.comparisons.models import (
    Ema9VwapAlignmentState,
    EmaAlignmentState,
    VwapAlignmentState,
)
from spy_research.strategy.models import SetupDirection
from spy_research.strategy.stability import (
    BOOTSTRAP_RESAMPLES,
    BOOTSTRAP_SEED,
    HORIZONS,
    BootstrapInterval,
    FrozenStabilityRecord,
    SessionBootstrapUncertainty,
    ValidationPartition,
    bootstrap_session_uncertainty,
)


DEVELOPMENT_START = date(2026, 8, 3)
DEVELOPMENT_END = date(2026, 8, 19)


class VariantSelectionInputError(ValueError):
    """Frozen Stage 9-12 inputs cannot form a trustworthy selection report."""


class StrategyVariant(StrEnum):
    BASE_ALL = "BASE_ALL"
    BASE_LONG = "BASE_LONG"
    BASE_SHORT = "BASE_SHORT"
    EMA_STACK_ALIGNED = "EMA_STACK_ALIGNED"
    STRUCTURE_ALIGNED = "STRUCTURE_ALIGNED"
    ROOM_GE_1_ATR = "ROOM_GE_1_ATR"
    EMA_STACK_AND_STRUCTURE = "EMA_STACK_AND_STRUCTURE"
    EMA_STACK_AND_ROOM_GE_1_ATR = "EMA_STACK_AND_ROOM_GE_1_ATR"
    STRUCTURE_AND_ROOM_GE_1_ATR = "STRUCTURE_AND_ROOM_GE_1_ATR"
    FULL_CONFLUENCE = "FULL_CONFLUENCE"


class VariantSelectionLabel(StrEnum):
    ADVANCE_TO_STAGE_13 = "ADVANCE_TO_STAGE_13"
    RETAIN_AS_CONTROL = "RETAIN_AS_CONTROL"
    INSUFFICIENT_COVERAGE = "INSUFFICIENT_COVERAGE"
    DO_NOT_ADVANCE = "DO_NOT_ADVANCE"


class AdvancementCriterionName(StrEnum):
    EXPANDED_BALANCE_POSITIVE = "EXPANDED_MEDIAN_EOD_BALANCE_GT_0"
    PRE_DEVELOPMENT_BALANCE_POSITIVE = "PRE_DEVELOPMENT_MEDIAN_EOD_BALANCE_GT_0"
    DEVELOPMENT_BALANCE_POSITIVE = "DEVELOPMENT_MEDIAN_EOD_BALANCE_GT_0"
    FIVE_POSITIVE_MONTHS = "AT_LEAST_5_OF_8_POSITIVE_MONTHS"
    LOO_NEVER_NEGATIVE = "LEAVE_ONE_MONTH_OUT_NEVER_NEGATIVE"
    SESSION_CONCENTRATION = "LARGEST_SESSION_PERCENTAGE_LE_10"
    BOOTSTRAP_MEDIAN_POSITIVE = "BOOTSTRAP_BALANCE_INTERVAL_MEDIAN_GT_0"


class CandidateContextRecord(BaseModel):
    """Outcome-blind accepted context known for one confirmed setup."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    session_date: date
    signal_known_at: datetime
    direction: SetupDirection
    level_type: LevelType
    ema9_20_alignment: EmaAlignmentState
    price_vwap_alignment: VwapAlignmentState
    ema9_vwap_alignment: Ema9VwapAlignmentState
    ema20_vwap_alignment: Ema20VwapAlignmentState
    structure_agreement: StructureAgreementState
    room_in_atr: Decimal | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def timezone_aware(self) -> Self:
        if self.signal_known_at.tzinfo is None:
            raise ValueError("signal_known_at must be timezone-aware")
        return self


class CandidateMembership(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    variants: tuple[StrategyVariant, ...]

    @model_validator(mode="after")
    def frozen_order(self) -> Self:
        expected = tuple(item for item in StrategyVariant if item in set(self.variants))
        if self.variants != expected or len(self.variants) != len(set(self.variants)):
            raise ValueError("candidate variants must use the closed deterministic order")
        if StrategyVariant.BASE_ALL not in self.variants:
            raise ValueError("every confirmed setup belongs to BASE_ALL")
        return self


class CandidatePartitionStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    partition: ValidationPartition
    setup_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    session_count: int = Field(ge=0)
    executable_session_count: int = Field(ge=0)
    month_coverage: int = Field(ge=0, le=8)
    long_n: int = Field(ge=0)
    short_n: int = Field(ge=0)
    level_composition: tuple[tuple[LevelType, int], ...]
    percentage_of_base_all: Decimal
    horizons: tuple[BaseStrategyHorizonStatistics, ...]

    @model_validator(mode="after")
    def reconcile(self) -> Self:
        if self.long_n + self.short_n != self.setup_n:
            raise ValueError("variant direction composition mismatch")
        if self.executable_n > self.setup_n:
            raise ValueError("variant executable count exceeds qualifying count")
        if tuple(item.horizon for item in self.horizons) != HORIZONS:
            raise ValueError("variant horizons must use frozen ordering")
        return self


class CandidateDirectionStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    direction: SetupDirection
    setup_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    session_count: int = Field(ge=0)
    horizons: tuple[BaseStrategyHorizonStatistics, ...]


class CandidateLeaveOneMonthOut(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    full_median_eod_balance: Decimal | None
    minimum_exclusion_median_balance: Decimal | None
    maximum_exclusion_median_balance: Decimal | None
    sign_change_count: int = Field(ge=0, le=8)
    exclusions: tuple[tuple[str, Decimal | None], ...]


class AdvancementCriterion(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: AdvancementCriterionName
    passed: bool
    observed: str
    required: str


class CandidateEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    variant: StrategyVariant
    expanded: CandidatePartitionStatistics
    pre_development: CandidatePartitionStatistics
    development: CandidatePartitionStatistics
    monthly: tuple[CandidatePartitionStatistics, ...]
    positive_months: int = Field(ge=0, le=8)
    zero_months: int = Field(ge=0, le=8)
    negative_months: int = Field(ge=0, le=8)
    unavailable_months: int = Field(ge=0, le=8)
    largest_session_percentage: Decimal
    largest_five_sessions_percentage: Decimal
    direction_decomposition: tuple[CandidateDirectionStatistics, ...]
    leave_one_month_out: CandidateLeaveOneMonthOut
    scorecard_eligible: bool
    bootstrap_uncertainty: SessionBootstrapUncertainty | None
    criteria: tuple[AdvancementCriterion, ...]
    selection_label: VariantSelectionLabel
    label_reason: str

    @model_validator(mode="after")
    def reconcile_label(self) -> Self:
        if len(self.monthly) != 8:
            raise ValueError("variant evaluation requires eight chronological months")
        if (
            self.positive_months
            + self.zero_months
            + self.negative_months
            + self.unavailable_months
            != 8
        ):
            raise ValueError("monthly balance availability must reconcile")
        if self.scorecard_eligible != (
            self.expanded.executable_n >= 30
            and self.expanded.executable_session_count >= 20
        ):
            raise ValueError("scorecard eligibility must use frozen coverage rules")
        if self.variant is StrategyVariant.BASE_ALL:
            if self.selection_label is not VariantSelectionLabel.RETAIN_AS_CONTROL:
                raise ValueError("BASE_ALL must remain the control")
        elif not self.scorecard_eligible:
            if self.selection_label is not VariantSelectionLabel.INSUFFICIENT_COVERAGE:
                raise ValueError("ineligible variants require insufficient coverage")
        elif self.selection_label is VariantSelectionLabel.ADVANCE_TO_STAGE_13:
            if not self.criteria or not all(item.passed for item in self.criteria):
                raise ValueError("advancement requires every frozen criterion")
        return self


class ControlledVariantSelectionReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    start_date: date
    end_date: date
    development_start: date
    development_end: date
    expanded_setup_n: int = Field(ge=0)
    expanded_executable_n: int = Field(ge=0)
    expanded_memberships: tuple[CandidateMembership, ...]
    development_memberships: tuple[CandidateMembership, ...]
    evaluations: tuple[CandidateEvaluation, ...]
    bootstrap_seed: int = BOOTSTRAP_SEED
    bootstrap_resamples: int = BOOTSTRAP_RESAMPLES
    report_version: Literal["controlled-stage13-variant-selection-v1"] = (
        "controlled-stage13-variant-selection-v1"
    )
    caveat: str = (
        "Outcome-aware descriptive selection over ten predeclared candidates; "
        "not realized-P/L, optimization, or predictive validation."
    )

    @model_validator(mode="after")
    def reconcile(self) -> Self:
        if tuple(item.variant for item in self.evaluations) != tuple(StrategyVariant):
            raise ValueError("Stage 12.3 requires exactly ten frozen variants")
        if len(self.expanded_memberships) != self.expanded_setup_n:
            raise ValueError("expanded membership population mismatch")
        return self


def qualifies_for_ema_stack(context: CandidateContextRecord) -> bool:
    return (
        context.ema9_20_alignment is EmaAlignmentState.EMA_ALIGNED
        and context.price_vwap_alignment is VwapAlignmentState.VWAP_ALIGNED
        and context.ema9_vwap_alignment
        is Ema9VwapAlignmentState.EMA9_VWAP_ALIGNED
        and context.ema20_vwap_alignment
        is Ema20VwapAlignmentState.EMA20_VWAP_ALIGNED
    )


def qualifies_for_room(context: CandidateContextRecord) -> bool:
    return context.room_in_atr is not None and context.room_in_atr >= Decimal("1.0")


def candidate_variants(context: CandidateContextRecord) -> tuple[StrategyVariant, ...]:
    """Freeze membership without accepting or consulting any outcome value."""

    ema = qualifies_for_ema_stack(context)
    structure = context.structure_agreement is StructureAgreementState.ALIGNED
    room = qualifies_for_room(context)
    predicates = {
        StrategyVariant.BASE_ALL: True,
        StrategyVariant.BASE_LONG: context.direction is SetupDirection.LONG,
        StrategyVariant.BASE_SHORT: context.direction is SetupDirection.SHORT,
        StrategyVariant.EMA_STACK_ALIGNED: ema,
        StrategyVariant.STRUCTURE_ALIGNED: structure,
        StrategyVariant.ROOM_GE_1_ATR: room,
        StrategyVariant.EMA_STACK_AND_STRUCTURE: ema and structure,
        StrategyVariant.EMA_STACK_AND_ROOM_GE_1_ATR: ema and room,
        StrategyVariant.STRUCTURE_AND_ROOM_GE_1_ATR: structure and room,
        StrategyVariant.FULL_CONFLUENCE: ema and structure and room,
    }
    return tuple(item for item in StrategyVariant if predicates[item])


def select_candidate_memberships(
    contexts: Sequence[CandidateContextRecord],
) -> tuple[CandidateMembership, ...]:
    ordered = tuple(sorted(contexts, key=lambda item: (item.session_date, item.setup_identity)))
    if len({item.setup_identity for item in ordered}) != len(ordered):
        raise VariantSelectionInputError("duplicate candidate context identity")
    return tuple(
        CandidateMembership(
            setup_identity=item.setup_identity,
            variants=candidate_variants(item),
        )
        for item in ordered
    )


def _percentage(numerator: int, denominator: int) -> Decimal:
    if denominator == 0:
        return Decimal(0)
    with localcontext(EMA_CONTEXT):
        return Decimal(numerator) * Decimal(100) / Decimal(denominator)


def _horizon_statistics(
    records: Sequence[FrozenStabilityRecord], horizon: str
) -> BaseStrategyHorizonStatistics:
    executable = tuple(item for item in records if item.executable)
    values = tuple(
        next(value for value in item.horizons if value.horizon == horizon)
        for item in executable
    )
    complete = tuple(item for item in values if item.complete)
    mfe = tuple(item.mfe for item in complete)
    mae = tuple(item.mae for item in complete)
    with localcontext(EMA_CONTEXT):
        balance = tuple(a - b for a, b in zip(mfe, mae, strict=True))
        ratios = tuple(a / b for a, b in zip(mfe, mae, strict=True) if b > 0)
    return BaseStrategyHorizonStatistics(
        horizon=horizon,
        complete_n=len(complete),
        incomplete_n=len(executable) - len(complete),
        mfe=summarize_distribution(mfe),
        mae=summarize_distribution(mae),
        net_excursion_balance=summarize_distribution(balance),
        favorable_adverse=FavorableAdverseCounts(
            mfe_greater=sum(a > b for a, b in zip(mfe, mae, strict=True)),
            equal=sum(a == b for a, b in zip(mfe, mae, strict=True)),
            mfe_less=sum(a < b for a, b in zip(mfe, mae, strict=True)),
        ),
        valid_ratio_n=len(ratios),
        zero_mae_n=sum(item == 0 for item in mae),
        median_mfe_mae_ratio=summarize_distribution(ratios).median,
    )


def _partition_statistics(
    records: Sequence[FrozenStabilityRecord],
    *,
    partition: ValidationPartition,
    base_n: int,
) -> CandidatePartitionStatistics:
    selected = tuple(records)
    executable = tuple(item for item in selected if item.executable)
    levels = Counter(item.level_type for item in selected)
    return CandidatePartitionStatistics(
        partition=partition,
        setup_n=len(selected),
        executable_n=len(executable),
        session_count=len({item.session_date for item in selected}),
        executable_session_count=len({item.session_date for item in executable}),
        month_coverage=len({item.session_date.month for item in selected}),
        long_n=sum(item.direction is SetupDirection.LONG for item in selected),
        short_n=sum(item.direction is SetupDirection.SHORT for item in selected),
        level_composition=tuple(
            (level, levels[level]) for level in LevelType if levels[level]
        ),
        percentage_of_base_all=_percentage(len(selected), base_n),
        horizons=tuple(_horizon_statistics(selected, horizon) for horizon in HORIZONS),
    )


def _eod(stats: CandidatePartitionStatistics) -> BaseStrategyHorizonStatistics:
    return next(item for item in stats.horizons if item.horizon == "EOD")


def _sign(value: Decimal | None) -> int | None:
    if value is None:
        return None
    return 1 if value > 0 else (-1 if value < 0 else 0)


def _concentration(records: Sequence[FrozenStabilityRecord]) -> tuple[Decimal, Decimal]:
    counts = sorted(Counter(item.session_date for item in records).values(), reverse=True)
    return (
        _percentage(counts[0], len(records)) if counts else Decimal(0),
        _percentage(sum(counts[:5]), len(records)) if counts else Decimal(0),
    )


def _ids_for_variant(
    memberships: Sequence[CandidateMembership], variant: StrategyVariant
) -> frozenset[str]:
    return frozenset(
        item.setup_identity for item in memberships if variant in item.variants
    )


def _selected(
    records: Sequence[FrozenStabilityRecord], ids: frozenset[str]
) -> tuple[FrozenStabilityRecord, ...]:
    return tuple(item for item in records if item.setup_identity in ids)


def evaluate_advancement_criteria(
    *,
    expanded_balance: Decimal | None,
    pre_development_balance: Decimal | None,
    development_balance: Decimal | None,
    positive_months: int,
    leave_one_month_out_balances: Sequence[Decimal | None],
    largest_session_percentage: Decimal,
    bootstrap_balance_median: Decimal,
) -> tuple[AdvancementCriterion, ...]:
    """Apply only the seven predeclared Stage 12.3 advancement boundaries."""

    exclusions = tuple(leave_one_month_out_balances)
    available = tuple(value for value in exclusions if value is not None)
    specs = (
        (
            AdvancementCriterionName.EXPANDED_BALANCE_POSITIVE,
            expanded_balance is not None and expanded_balance > 0,
            str(expanded_balance),
            "> 0",
        ),
        (
            AdvancementCriterionName.PRE_DEVELOPMENT_BALANCE_POSITIVE,
            pre_development_balance is not None and pre_development_balance > 0,
            str(pre_development_balance),
            "> 0",
        ),
        (
            AdvancementCriterionName.DEVELOPMENT_BALANCE_POSITIVE,
            development_balance is not None and development_balance > 0,
            str(development_balance),
            "> 0",
        ),
        (
            AdvancementCriterionName.FIVE_POSITIVE_MONTHS,
            positive_months >= 5,
            str(positive_months),
            ">= 5",
        ),
        (
            AdvancementCriterionName.LOO_NEVER_NEGATIVE,
            bool(exclusions) and all(value is not None and value >= 0 for value in exclusions),
            str(min(available, default=None)),
            "minimum >= 0",
        ),
        (
            AdvancementCriterionName.SESSION_CONCENTRATION,
            largest_session_percentage <= 10,
            str(largest_session_percentage),
            "<= 10 percent",
        ),
        (
            AdvancementCriterionName.BOOTSTRAP_MEDIAN_POSITIVE,
            bootstrap_balance_median > 0,
            str(bootstrap_balance_median),
            "> 0",
        ),
    )
    return tuple(
        AdvancementCriterion(name=name, passed=passed, observed=observed, required=required)
        for name, passed, observed, required in specs
    )


def select_variant_label(
    variant: StrategyVariant,
    *,
    scorecard_eligible: bool,
    criteria: Sequence[AdvancementCriterion],
    executable_n: int,
    executable_session_count: int,
) -> tuple[VariantSelectionLabel, str]:
    """Select a frozen label without subjective interpretation."""

    if variant is StrategyVariant.BASE_ALL:
        return (
            VariantSelectionLabel.RETAIN_AS_CONTROL,
            "BASE_ALL is the frozen Stage 13 control.",
        )
    if not scorecard_eligible:
        return (
            VariantSelectionLabel.INSUFFICIENT_COVERAGE,
            f"Requires >=30 executable setups and >=20 executable sessions; "
            f"observed {executable_n} and {executable_session_count}.",
        )
    if criteria and all(item.passed for item in criteria):
        return (
            VariantSelectionLabel.ADVANCE_TO_STAGE_13,
            "All seven predeclared advancement criteria passed.",
        )
    failed = ", ".join(item.name.value for item in criteria if not item.passed)
    return (
        VariantSelectionLabel.DO_NOT_ADVANCE,
        f"Failed predeclared criteria: {failed}.",
    )


def calculate_controlled_variant_selection(
    expanded_contexts: Sequence[CandidateContextRecord],
    development_contexts: Sequence[CandidateContextRecord],
    expanded_records: Sequence[FrozenStabilityRecord],
    development_records: Sequence[FrozenStabilityRecord],
    *,
    start: date,
    end: date,
    bootstrap_seed: int = BOOTSTRAP_SEED,
    bootstrap_resamples: int = BOOTSTRAP_RESAMPLES,
) -> ControlledVariantSelectionReport:
    """Freeze memberships first, then join accepted descriptive outcomes."""

    expanded_memberships = select_candidate_memberships(expanded_contexts)
    development_memberships = select_candidate_memberships(development_contexts)
    expanded_ids = {item.setup_identity for item in expanded_contexts}
    development_ids = {item.setup_identity for item in development_contexts}
    if expanded_ids != {item.setup_identity for item in expanded_records}:
        raise VariantSelectionInputError("expanded context/outcome identities mismatch")
    if development_ids != {item.setup_identity for item in development_records}:
        raise VariantSelectionInputError("development context/outcome identities mismatch")

    expanded_records = tuple(expanded_records)
    development_records = tuple(development_records)
    pre_records = tuple(item for item in expanded_records if item.session_date < DEVELOPMENT_START)
    base_month_records = {
        month: (
            tuple(item for item in expanded_records if item.session_date.month == month)
            if month < 8
            else development_records
        )
        for month in range(1, 9)
    }
    evaluations = []
    for variant in StrategyVariant:
        expanded_variant_ids = _ids_for_variant(expanded_memberships, variant)
        development_variant_ids = _ids_for_variant(development_memberships, variant)
        expanded_selected = _selected(expanded_records, expanded_variant_ids)
        development_selected = _selected(development_records, development_variant_ids)
        pre_selected = tuple(
            item for item in pre_records if item.setup_identity in expanded_variant_ids
        )
        expanded_stats = _partition_statistics(
            expanded_selected,
            partition=ValidationPartition.EXPANDED_ALL,
            base_n=len(expanded_records),
        )
        pre_stats = _partition_statistics(
            pre_selected,
            partition=ValidationPartition.PRE_DEVELOPMENT_OUT_OF_SAMPLE,
            base_n=len(pre_records),
        )
        development_stats = _partition_statistics(
            development_selected,
            partition=ValidationPartition.DEVELOPMENT_SAMPLE,
            base_n=len(development_records),
        )
        monthly = []
        for month in range(1, 9):
            ids = expanded_variant_ids if month < 8 else development_variant_ids
            selected = _selected(base_month_records[month], ids)
            monthly.append(
                _partition_statistics(
                    selected,
                    partition=ValidationPartition(f"MONTH_2026_{month:02d}"),
                    base_n=len(base_month_records[month]),
                )
            )
        balances = tuple(_eod(item).net_excursion_balance.median for item in monthly)
        largest, largest_five = _concentration(expanded_selected)
        full_balance = _eod(expanded_stats).net_excursion_balance.median
        exclusions = []
        for month in range(1, 9):
            excluded = tuple(
                item for item in expanded_selected if item.session_date.month != month
            )
            exclusions.append(
                (
                    f"2026-{month:02d}",
                    _horizon_statistics(excluded, "EOD").net_excursion_balance.median,
                )
            )
        available_exclusions = tuple(value for _, value in exclusions if value is not None)
        leave_one_out = CandidateLeaveOneMonthOut(
            full_median_eod_balance=full_balance,
            minimum_exclusion_median_balance=min(available_exclusions, default=None),
            maximum_exclusion_median_balance=max(available_exclusions, default=None),
            sign_change_count=sum(
                _sign(value) != _sign(full_balance) for _, value in exclusions
            ),
            exclusions=tuple(exclusions),
        )
        eligible = (
            expanded_stats.executable_n >= 30
            and expanded_stats.executable_session_count >= 20
        )
        bootstrap_dimension, bootstrap_state = _bootstrap_identity(variant)
        bootstrap = (
            bootstrap_session_uncertainty(
                bootstrap_dimension,
                bootstrap_state,
                expanded_selected,
                seed=bootstrap_seed,
                resamples=bootstrap_resamples,
            )
            if eligible
            else None
        )
        positive = sum(value is not None and value > 0 for value in balances)
        zero = sum(value == 0 for value in balances)
        negative = sum(value is not None and value < 0 for value in balances)
        criteria = (
            evaluate_advancement_criteria(
                expanded_balance=_eod(expanded_stats).net_excursion_balance.median,
                pre_development_balance=_eod(pre_stats).net_excursion_balance.median,
                development_balance=_eod(development_stats).net_excursion_balance.median,
                positive_months=positive,
                leave_one_month_out_balances=tuple(
                    value for _, value in leave_one_out.exclusions
                ),
                largest_session_percentage=largest,
                bootstrap_balance_median=next(
                    item
                    for item in bootstrap.intervals
                    if item.metric == "MEDIAN_EOD_BALANCE"
                ).p50,
            )
            if eligible and bootstrap is not None
            else ()
        )
        label, reason = select_variant_label(
            variant,
            scorecard_eligible=eligible,
            criteria=criteria,
            executable_n=expanded_stats.executable_n,
            executable_session_count=expanded_stats.executable_session_count,
        )
        directions = tuple(
            CandidateDirectionStatistics(
                direction=direction,
                setup_n=len(scoped := tuple(item for item in expanded_selected if item.direction is direction)),
                executable_n=sum(item.executable for item in scoped),
                session_count=len({item.session_date for item in scoped}),
                horizons=tuple(_horizon_statistics(scoped, horizon) for horizon in HORIZONS),
            )
            for direction in SetupDirection
            if any(item.direction is direction for item in expanded_selected)
        )
        evaluations.append(
            CandidateEvaluation(
                variant=variant,
                expanded=expanded_stats,
                pre_development=pre_stats,
                development=development_stats,
                monthly=tuple(monthly),
                positive_months=positive,
                zero_months=zero,
                negative_months=negative,
                unavailable_months=sum(value is None for value in balances),
                largest_session_percentage=largest,
                largest_five_sessions_percentage=largest_five,
                direction_decomposition=directions,
                leave_one_month_out=leave_one_out,
                scorecard_eligible=eligible,
                bootstrap_uncertainty=bootstrap,
                criteria=criteria,
                selection_label=label,
                label_reason=reason,
            )
        )
    return ControlledVariantSelectionReport(
        start_date=start,
        end_date=end,
        development_start=DEVELOPMENT_START,
        development_end=DEVELOPMENT_END,
        expanded_setup_n=len(expanded_records),
        expanded_executable_n=sum(item.executable for item in expanded_records),
        expanded_memberships=expanded_memberships,
        development_memberships=development_memberships,
        evaluations=tuple(evaluations),
        bootstrap_seed=bootstrap_seed,
        bootstrap_resamples=bootstrap_resamples,
    )


def _bootstrap_identity(variant: StrategyVariant) -> tuple[str, str]:
    """Reuse accepted Stage 12.2 identities for identical candidate populations."""
    if variant is StrategyVariant.BASE_ALL:
        return ("BASE_ALL", "ALL")
    if variant is StrategyVariant.BASE_LONG:
        return ("DIRECTION", "LONG")
    if variant is StrategyVariant.BASE_SHORT:
        return ("DIRECTION", "SHORT")
    return ("STRATEGY_VARIANT", variant.value)


def controlled_variant_selection_hash(
    report: ControlledVariantSelectionReport,
) -> str:
    return sha256(report.model_dump_json().encode()).hexdigest()
