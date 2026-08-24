"""Pure Stage 12.2 expanded frozen-rule stability analysis.

This module consumes immutable projections of accepted Stage 9-11 records.  It
does not classify setups, inspect bars, or alter any source research object.
"""

from __future__ import annotations

import random
from collections import Counter
from collections.abc import Iterable, Sequence
from datetime import date
from decimal import Decimal, localcontext
from enum import StrEnum
from hashlib import sha256
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.indicators.ema import EMA_CONTEXT
from spy_research.interactions import LevelType
from spy_research.research_stats import (
    DistributionSummary,
    FavorableAdverseCounts,
    summarize_distribution,
)
from spy_research.strategy.models import SetupDirection


HORIZONS = ("5m", "15m", "30m", "60m", "EOD")
CONTEXT_DIMENSIONS = (
    "EMA9_20_ALIGNMENT",
    "EMA9_20_CROSS_CONTEXT",
    "PRICE_VWAP_ALIGNMENT",
    "EMA9_VWAP_ALIGNMENT",
    "EMA9_VWAP_CROSS_CONTEXT",
    "EMA20_VWAP_ALIGNMENT",
    "EMA20_VWAP_CROSS_CONTEXT",
)
STAGE11_DIMENSIONS = (
    "REGIME",
    "ROOM_BUCKET",
    "STRUCTURE",
    "STRUCTURE_AGREEMENT",
)
MAJOR_DIMENSIONS = CONTEXT_DIMENSIONS + STAGE11_DIMENSIONS
BOOTSTRAP_SEED = 12022026
BOOTSTRAP_RESAMPLES = 10_000


class StabilityInputError(ValueError):
    """Frozen source records cannot form a trustworthy stability report."""


class ValidationPartition(StrEnum):
    DEVELOPMENT_SAMPLE = "DEVELOPMENT_SAMPLE"
    PRE_DEVELOPMENT_OUT_OF_SAMPLE = "PRE_DEVELOPMENT_OUT_OF_SAMPLE"
    EXPANDED_ALL = "EXPANDED_ALL"
    MONTH_2026_01 = "MONTH_2026_01"
    MONTH_2026_02 = "MONTH_2026_02"
    MONTH_2026_03 = "MONTH_2026_03"
    MONTH_2026_04 = "MONTH_2026_04"
    MONTH_2026_05 = "MONTH_2026_05"
    MONTH_2026_06 = "MONTH_2026_06"
    MONTH_2026_07 = "MONTH_2026_07"
    MONTH_2026_08 = "MONTH_2026_08"


class SampleSizeLabel(StrEnum):
    VERY_SMALL = "VERY_SMALL"
    SMALL = "SMALL"
    MODERATE = "MODERATE"
    LARGE = "LARGE"


class FrozenState(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    dimension: str
    state: str


class FrozenStabilityHorizon(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    horizon: Literal["5m", "15m", "30m", "60m", "EOD"]
    complete: bool
    mfe: Decimal
    mae: Decimal


class FrozenStabilityRecord(BaseModel):
    """Lossless outcome projection plus outcome-blind accepted context states."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    session_date: date
    direction: SetupDirection
    level_type: LevelType
    executable: bool
    states: tuple[FrozenState, ...]
    horizons: tuple[FrozenStabilityHorizon, ...]

    @model_validator(mode="after")
    def reconcile(self):
        dimensions = tuple(item.dimension for item in self.states)
        if len(dimensions) != len(set(dimensions)):
            raise ValueError("stability state dimensions must be unique")
        if self.executable != bool(self.horizons):
            raise ValueError("only executable records may contain horizons")
        if self.executable and tuple(item.horizon for item in self.horizons) != HORIZONS:
            raise ValueError("executable records require all frozen horizons")
        return self

    def state(self, dimension: str) -> str:
        try:
            return next(item.state for item in self.states if item.dimension == dimension)
        except StopIteration as exc:
            raise StabilityInputError(f"Missing frozen state: {dimension}") from exc


class StabilityHorizonStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    horizon: Literal["5m", "15m", "30m", "60m", "EOD"]
    executable_n: int = Field(ge=0)
    complete_n: int = Field(ge=0)
    incomplete_n: int = Field(ge=0)
    mfe: DistributionSummary
    mae: DistributionSummary
    balance: DistributionSummary
    favorable_adverse: FavorableAdverseCounts
    median_mfe_mae_ratio: Decimal | None
    zero_mae_n: int = Field(ge=0)


class GroupPartitionStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    partition: ValidationPartition
    dimension: str
    state: str
    direction_scope: SetupDirection | None = None
    level_scope: LevelType | None = None
    setup_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    session_count: int = Field(ge=0)
    long_n: int = Field(ge=0)
    short_n: int = Field(ge=0)
    level_composition: tuple[tuple[LevelType, int], ...]
    percentage_of_parent: Decimal
    sample_size: SampleSizeLabel
    horizons: tuple[StabilityHorizonStatistics, ...]


class ResearchStabilityRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    dimension: str
    state: str
    total_executable_n: int = Field(ge=30)
    distinct_sessions: int = Field(ge=0)
    months_represented: int = Field(ge=0)
    monthly_executable_n: tuple[tuple[str, int], ...]
    positive_months: int = Field(ge=0)
    negative_months: int = Field(ge=0)
    zero_months: int = Field(ge=0)
    unavailable_months: int = Field(ge=0)
    minimum_monthly_median_balance: Decimal | None
    maximum_monthly_median_balance: Decimal | None
    median_of_monthly_median_balances: Decimal | None
    overall_median_eod_balance: Decimal | None
    largest_month_percentage: Decimal
    largest_session_percentage: Decimal
    one_month_over_25_percent: bool
    one_session_over_10_percent: bool


class SessionConcentration(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    dimension: str
    state: str
    setup_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    distinct_sessions: int = Field(ge=0)
    median_setups_per_present_session: Decimal | None
    maximum_single_session_n: int = Field(ge=0)
    largest_session_percentage: Decimal
    largest_five_sessions_percentage: Decimal


class TwoWayStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    left_dimension: str
    left_state: str
    right_dimension: str
    right_state: str
    setup_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    session_count: int = Field(ge=0)
    long_n: int = Field(ge=0)
    short_n: int = Field(ge=0)
    below_30_executable: bool
    eod: StabilityHorizonStatistics


class LeaveOneMonthOutSensitivity(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    dimension: str
    state: str
    executable_n: int = Field(ge=100)
    full_median_mfe: Decimal | None
    full_median_mae: Decimal | None
    full_median_balance: Decimal | None
    minimum_exclusion_median_balance: Decimal | None
    maximum_exclusion_median_balance: Decimal | None
    sign_change_exclusions: int = Field(ge=0, le=8)
    exclusions: tuple[tuple[str, Decimal | None], ...]


class BootstrapInterval(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    metric: Literal["MEDIAN_EOD_MFE", "MEDIAN_EOD_MAE", "MEDIAN_EOD_BALANCE"]
    p2_5: Decimal
    p50: Decimal
    p97_5: Decimal


class SessionBootstrapUncertainty(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    dimension: str
    state: str
    executable_n: int = Field(ge=100)
    session_count: int = Field(ge=20)
    seed: int
    resamples: int = Field(gt=0)
    intervals: tuple[BootstrapInterval, ...]
    label: Literal["BOOTSTRAP_UNCERTAINTY_INTERVAL"] = (
        "BOOTSTRAP_UNCERTAINTY_INTERVAL"
    )


class PartitionComparison(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    dimension: str
    state: str
    comparison_partition: Literal[
        "PRE_DEVELOPMENT_OUT_OF_SAMPLE", "EXPANDED_ALL"
    ]
    development_n: int = Field(ge=0)
    comparison_n: int = Field(ge=0)
    development_sessions: int = Field(ge=0)
    comparison_sessions: int = Field(ge=0)
    development_median_mfe: Decimal | None
    comparison_median_mfe: Decimal | None
    median_mfe_difference: Decimal | None
    development_median_mae: Decimal | None
    comparison_median_mae: Decimal | None
    median_mae_difference: Decimal | None
    development_median_balance: Decimal | None
    comparison_median_balance: Decimal | None
    median_balance_difference: Decimal | None
    sign_agrees: bool | None
    population_ratio: Decimal | None
    development_largest_session_percentage: Decimal
    comparison_largest_session_percentage: Decimal
    development_long_percentage: Decimal
    comparison_long_percentage: Decimal
    long_percentage_shift: Decimal


class ExpandedStabilityReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    start_date: date
    end_date: date
    development_start: date
    development_end: date
    expanded_setup_n: int = Field(ge=0)
    expanded_executable_n: int = Field(ge=0)
    expanded_session_count: int = Field(ge=0)
    development_setup_n: int = Field(ge=0)
    development_executable_n: int = Field(ge=0)
    development_session_count: int = Field(ge=0)
    partition_statistics: tuple[GroupPartitionStatistics, ...]
    stability_scorecard: tuple[ResearchStabilityRecord, ...]
    direction_controlled: tuple[GroupPartitionStatistics, ...]
    level_controlled: tuple[GroupPartitionStatistics, ...]
    session_concentration: tuple[SessionConcentration, ...]
    two_way_relationships: tuple[TwoWayStatistics, ...]
    leave_one_month_out: tuple[LeaveOneMonthOutSensitivity, ...]
    bootstrap_uncertainty: tuple[SessionBootstrapUncertainty, ...]
    development_comparisons: tuple[PartitionComparison, ...]
    bootstrap_seed: int = BOOTSTRAP_SEED
    bootstrap_resamples: int = BOOTSTRAP_RESAMPLES
    report_version: Literal["expanded-frozen-rule-stability-v1"] = (
        "expanded-frozen-rule-stability-v1"
    )
    methodological_label: Literal["EXPANDED_FROZEN_RULE_STABILITY_ANALYSIS"] = (
        "EXPANDED_FROZEN_RULE_STABILITY_ANALYSIS"
    )
    caveat: str = (
        "August-derived boundaries were applied backward to January-July; this is "
        "not chronological out-of-sample or predictive validation."
    )


def sample_size_label(n: int) -> SampleSizeLabel:
    if n < 10:
        return SampleSizeLabel.VERY_SMALL
    if n < 30:
        return SampleSizeLabel.SMALL
    if n < 100:
        return SampleSizeLabel.MODERATE
    return SampleSizeLabel.LARGE


def _percentage(numerator: int, denominator: int) -> Decimal:
    if not denominator:
        return Decimal(0)
    with localcontext(EMA_CONTEXT):
        return Decimal(numerator) * Decimal(100) / Decimal(denominator)


def _horizon_statistics(
    records: Sequence[FrozenStabilityRecord], horizon: str
) -> StabilityHorizonStatistics:
    executable = tuple(item for item in records if item.executable)
    values = tuple(
        next(value for value in item.horizons if value.horizon == horizon)
        for item in executable
    )
    complete = tuple(item for item in values if item.complete)
    mfe = tuple(item.mfe for item in complete)
    mae = tuple(item.mae for item in complete)
    with localcontext(EMA_CONTEXT):
        balances = tuple(a - b for a, b in zip(mfe, mae, strict=True))
        ratios = tuple(a / b for a, b in zip(mfe, mae, strict=True) if b > 0)
    return StabilityHorizonStatistics(
        horizon=horizon,
        executable_n=len(executable),
        complete_n=len(complete),
        incomplete_n=len(executable) - len(complete),
        mfe=summarize_distribution(mfe),
        mae=summarize_distribution(mae),
        balance=summarize_distribution(balances),
        favorable_adverse=FavorableAdverseCounts(
            mfe_greater=sum(a > b for a, b in zip(mfe, mae, strict=True)),
            equal=sum(a == b for a, b in zip(mfe, mae, strict=True)),
            mfe_less=sum(a < b for a, b in zip(mfe, mae, strict=True)),
        ),
        median_mfe_mae_ratio=summarize_distribution(ratios).median,
        zero_mae_n=sum(item == 0 for item in mae),
    )


def _group_statistics(
    records: Sequence[FrozenStabilityRecord],
    *,
    partition: ValidationPartition,
    dimension: str,
    state: str,
    parent_n: int,
    direction_scope: SetupDirection | None = None,
    level_scope: LevelType | None = None,
) -> GroupPartitionStatistics:
    selected = tuple(records)
    executable = tuple(item for item in selected if item.executable)
    levels = Counter(item.level_type for item in selected)
    return GroupPartitionStatistics(
        partition=partition,
        dimension=dimension,
        state=state,
        direction_scope=direction_scope,
        level_scope=level_scope,
        setup_n=len(selected),
        executable_n=len(executable),
        session_count=len({item.session_date for item in selected}),
        long_n=sum(item.direction is SetupDirection.LONG for item in selected),
        short_n=sum(item.direction is SetupDirection.SHORT for item in selected),
        level_composition=tuple(
            (level, levels[level]) for level in LevelType if levels[level]
        ),
        percentage_of_parent=_percentage(len(selected), parent_n),
        sample_size=sample_size_label(len(executable)),
        horizons=tuple(_horizon_statistics(selected, horizon) for horizon in HORIZONS),
    )


def _state_universe(records: Sequence[FrozenStabilityRecord]):
    values: dict[str, set[str]] = {dimension: set() for dimension in MAJOR_DIMENSIONS}
    for item in records:
        for state in item.states:
            if state.dimension in values:
                values[state.dimension].add(state.state)
    return tuple(
        (dimension, state)
        for dimension in MAJOR_DIMENSIONS
        for state in sorted(values[dimension])
    )


def _major_specs(records: Sequence[FrozenStabilityRecord]):
    return (
        (("BASE_ALL", "ALL"),)
        + tuple(("DIRECTION", item.value) for item in SetupDirection)
        + tuple(("LEVEL", item.value) for item in LevelType)
        + _state_universe(records)
    )


def _select(
    records: Sequence[FrozenStabilityRecord], dimension: str, state: str
) -> tuple[FrozenStabilityRecord, ...]:
    if dimension == "BASE_ALL":
        return tuple(records)
    if dimension == "DIRECTION":
        return tuple(item for item in records if item.direction.value == state)
    if dimension == "LEVEL":
        return tuple(item for item in records if item.level_type.value == state)
    return tuple(item for item in records if item.state(dimension) == state)


def _month_partition(month: int) -> ValidationPartition:
    return ValidationPartition(f"MONTH_2026_{month:02d}")


def _eod(row: GroupPartitionStatistics) -> StabilityHorizonStatistics:
    return next(item for item in row.horizons if item.horizon == "EOD")


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


def _linear_percentile(values: Sequence[Decimal], q: Decimal) -> Decimal:
    ordered = tuple(sorted(values))
    if not ordered:
        raise StabilityInputError("bootstrap percentile requires values")
    with localcontext(EMA_CONTEXT):
        rank = Decimal(len(ordered) - 1) * q
        lower = int(rank)
        upper = min(lower + 1, len(ordered) - 1)
        fraction = rank - Decimal(lower)
        return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def _bootstrap(
    dimension: str,
    state: str,
    records: Sequence[FrozenStabilityRecord],
    *,
    seed: int,
    resamples: int,
) -> SessionBootstrapUncertainty:
    executable = tuple(item for item in records if item.executable)
    by_session: dict[date, tuple[tuple[Decimal, Decimal, Decimal], ...]] = {}
    for session in sorted({item.session_date for item in executable}):
        values = []
        for item in executable:
            if item.session_date != session:
                continue
            eod = next(value for value in item.horizons if value.horizon == "EOD")
            if not eod.complete:
                continue
            with localcontext(EMA_CONTEXT):
                values.append((eod.mfe, eod.mae, eod.mfe - eod.mae))
        by_session[session] = tuple(values)
    sessions = tuple(by_session)
    derived_seed = int.from_bytes(
        sha256(f"{seed}:{dimension}:{state}".encode()).digest()[:8], "big"
    )
    rng = random.Random(derived_seed)
    samples: dict[str, list[Decimal]] = {"MFE": [], "MAE": [], "BALANCE": []}
    for _ in range(resamples):
        selected = tuple(
            value
            for _session in range(len(sessions))
            for value in by_session[sessions[rng.randrange(len(sessions))]]
        )
        if not selected:
            raise StabilityInputError("eligible bootstrap group lacks EOD outcomes")
        samples["MFE"].append(
            _linear_percentile(tuple(item[0] for item in selected), Decimal("0.5"))
        )
        samples["MAE"].append(
            _linear_percentile(tuple(item[1] for item in selected), Decimal("0.5"))
        )
        samples["BALANCE"].append(
            _linear_percentile(tuple(item[2] for item in selected), Decimal("0.5"))
        )
    intervals = []
    for metric, label in (
        ("MFE", "MEDIAN_EOD_MFE"),
        ("MAE", "MEDIAN_EOD_MAE"),
        ("BALANCE", "MEDIAN_EOD_BALANCE"),
    ):
        intervals.append(
            BootstrapInterval(
                metric=label,
                p2_5=_linear_percentile(samples[metric], Decimal("0.025")),
                p50=_linear_percentile(samples[metric], Decimal("0.5")),
                p97_5=_linear_percentile(samples[metric], Decimal("0.975")),
            )
        )
    return SessionBootstrapUncertainty(
        dimension=dimension,
        state=state,
        executable_n=len(executable),
        session_count=len(sessions),
        seed=seed,
        resamples=resamples,
        intervals=tuple(intervals),
    )


def _validate_records(
    expanded: Sequence[FrozenStabilityRecord],
    development: Sequence[FrozenStabilityRecord],
) -> None:
    for label, records in (("expanded", expanded), ("development", development)):
        identities = tuple(item.setup_identity for item in records)
        if len(identities) != len(set(identities)):
            raise StabilityInputError(f"Duplicate {label} setup identity")
        if tuple(records) != tuple(sorted(records, key=lambda x: (x.session_date, x.setup_identity))):
            raise StabilityInputError(f"{label} records must be deterministic")
        for item in records:
            if frozenset(state.dimension for state in item.states) != frozenset(
                MAJOR_DIMENSIONS
            ):
                raise StabilityInputError("Frozen context universe mismatch")


def calculate_expanded_stability(
    expanded: Sequence[FrozenStabilityRecord],
    development: Sequence[FrozenStabilityRecord],
    *,
    start: date,
    end: date,
    development_start: date,
    development_end: date,
    bootstrap_seed: int = BOOTSTRAP_SEED,
    bootstrap_resamples: int = BOOTSTRAP_RESAMPLES,
) -> ExpandedStabilityReport:
    """Calculate descriptive stability without modifying classifications."""

    _validate_records(expanded, development)
    expanded = tuple(expanded)
    development = tuple(development)
    predevelopment = tuple(item for item in expanded if item.session_date < development_start)
    if any(item.session_date >= development_start for item in predevelopment):
        raise StabilityInputError("Pre-development partition is not chronological")
    partition_records = {
        ValidationPartition.DEVELOPMENT_SAMPLE: development,
        ValidationPartition.PRE_DEVELOPMENT_OUT_OF_SAMPLE: predevelopment,
        ValidationPartition.EXPANDED_ALL: expanded,
    }
    for month in range(1, 8):
        partition_records[_month_partition(month)] = tuple(
            item for item in expanded if item.session_date.month == month
        )
    partition_records[ValidationPartition.MONTH_2026_08] = development

    specs = _major_specs(expanded + development)
    rows = []
    for partition in ValidationPartition:
        records = partition_records[partition]
        for dimension, state in specs:
            rows.append(
                _group_statistics(
                    _select(records, dimension, state),
                    partition=partition,
                    dimension=dimension,
                    state=state,
                    parent_n=len(records),
                )
            )
    row_index = {(r.partition, r.dimension, r.state): r for r in rows}
    expanded_base = row_index[(ValidationPartition.EXPANDED_ALL, "BASE_ALL", "ALL")]

    scorecard = []
    for dimension, state in specs:
        overall = row_index[(ValidationPartition.EXPANDED_ALL, dimension, state)]
        if overall.executable_n < 30:
            continue
        monthly = tuple(
            row_index[(_month_partition(month), dimension, state)]
            for month in range(1, 9)
        )
        balances = tuple(_eod(item).balance.median for item in monthly)
        available = tuple(item for item in balances if item is not None)
        selected = _select(expanded, dimension, state)
        session_pct, _ = _concentration(selected)
        month_counts = tuple(item.executable_n for item in monthly)
        month_pct = _percentage(max(month_counts, default=0), overall.executable_n)
        scorecard.append(
            ResearchStabilityRecord(
                dimension=dimension,
                state=state,
                total_executable_n=overall.executable_n,
                distinct_sessions=overall.session_count,
                months_represented=sum(item > 0 for item in month_counts),
                monthly_executable_n=tuple(
                    (f"2026-{month:02d}", row.executable_n)
                    for month, row in enumerate(monthly, start=1)
                ),
                positive_months=sum(item is not None and item > 0 for item in balances),
                negative_months=sum(item is not None and item < 0 for item in balances),
                zero_months=sum(item == 0 for item in balances),
                unavailable_months=sum(item is None for item in balances),
                minimum_monthly_median_balance=min(available, default=None),
                maximum_monthly_median_balance=max(available, default=None),
                median_of_monthly_median_balances=summarize_distribution(available).median,
                overall_median_eod_balance=_eod(overall).balance.median,
                largest_month_percentage=month_pct,
                largest_session_percentage=session_pct,
                one_month_over_25_percent=month_pct > 25,
                one_session_over_10_percent=session_pct > 10,
            )
        )

    direction_rows = []
    for direction in SetupDirection:
        scoped = tuple(item for item in expanded if item.direction is direction)
        direction_rows.append(
            _group_statistics(
                scoped,
                partition=ValidationPartition.EXPANDED_ALL,
                dimension="DIRECTION_BASE",
                state=direction.value,
                parent_n=len(scoped),
                direction_scope=direction,
            )
        )
        for dimension, state in _state_universe(expanded):
            if dimension not in CONTEXT_DIMENSIONS:
                continue
            selected = tuple(item for item in scoped if item.state(dimension) == state)
            direction_rows.append(
                _group_statistics(
                    selected,
                    partition=ValidationPartition.EXPANDED_ALL,
                    dimension=dimension,
                    state=state,
                    parent_n=len(scoped),
                    direction_scope=direction,
                )
            )

    level_rows = []
    for level in LevelType:
        scoped = tuple(item for item in expanded if item.level_type is level)
        for dimension, state in _state_universe(expanded):
            selected = tuple(item for item in scoped if item.state(dimension) == state)
            level_rows.append(
                _group_statistics(
                    selected,
                    partition=ValidationPartition.EXPANDED_ALL,
                    dimension=dimension,
                    state=state,
                    parent_n=len(scoped),
                    level_scope=level,
                )
            )

    concentrations = []
    for dimension, state in _state_universe(expanded):
        if dimension not in STAGE11_DIMENSIONS[:3]:
            continue
        selected = _select(expanded, dimension, state)
        counts = tuple(Counter(item.session_date for item in selected).values())
        largest, largest_five = _concentration(selected)
        concentrations.append(
            SessionConcentration(
                dimension=dimension,
                state=state,
                setup_n=len(selected),
                executable_n=sum(item.executable for item in selected),
                distinct_sessions=len(counts),
                median_setups_per_present_session=summarize_distribution(
                    tuple(Decimal(item) for item in counts)
                ).median,
                maximum_single_session_n=max(counts, default=0),
                largest_session_percentage=largest,
                largest_five_sessions_percentage=largest_five,
            )
        )

    pairs = (
        ("REGIME", "ROOM_BUCKET"),
        ("REGIME", "STRUCTURE"),
        ("ROOM_BUCKET", "STRUCTURE"),
    )
    universes = {dimension: sorted({item.state(dimension) for item in expanded}) for dimension in STAGE11_DIMENSIONS}
    two_way = []
    for left, right in pairs:
        for left_state in universes[left]:
            for right_state in universes[right]:
                selected = tuple(
                    item for item in expanded
                    if item.state(left) == left_state and item.state(right) == right_state
                )
                eod = _horizon_statistics(selected, "EOD")
                executable_n = sum(item.executable for item in selected)
                two_way.append(
                    TwoWayStatistics(
                        left_dimension=left,
                        left_state=left_state,
                        right_dimension=right,
                        right_state=right_state,
                        setup_n=len(selected),
                        executable_n=executable_n,
                        session_count=len({item.session_date for item in selected}),
                        long_n=sum(item.direction is SetupDirection.LONG for item in selected),
                        short_n=sum(item.direction is SetupDirection.SHORT for item in selected),
                        below_30_executable=executable_n < 30,
                        eod=eod,
                    )
                )

    leave_one_out = []
    bootstraps = []
    for dimension, state in specs:
        selected = _select(expanded, dimension, state)
        executable_n = sum(item.executable for item in selected)
        sessions = len({item.session_date for item in selected if item.executable})
        if executable_n >= 100:
            full = _horizon_statistics(selected, "EOD")
            exclusion_values = []
            for month in range(1, 9):
                excluded = tuple(item for item in selected if item.session_date.month != month)
                exclusion_values.append((f"2026-{month:02d}", _horizon_statistics(excluded, "EOD").balance.median))
            available = tuple(item for _, item in exclusion_values if item is not None)
            full_sign = _sign(full.balance.median)
            leave_one_out.append(
                LeaveOneMonthOutSensitivity(
                    dimension=dimension,
                    state=state,
                    executable_n=executable_n,
                    full_median_mfe=full.mfe.median,
                    full_median_mae=full.mae.median,
                    full_median_balance=full.balance.median,
                    minimum_exclusion_median_balance=min(available, default=None),
                    maximum_exclusion_median_balance=max(available, default=None),
                    sign_change_exclusions=sum(
                        _sign(value) != full_sign for _, value in exclusion_values
                    ),
                    exclusions=tuple(exclusion_values),
                )
            )
        if executable_n >= 100 and sessions >= 20:
            bootstraps.append(
                _bootstrap(
                    dimension,
                    state,
                    selected,
                    seed=bootstrap_seed,
                    resamples=bootstrap_resamples,
                )
            )

    comparisons = []
    for dimension, state in specs:
        dev = row_index[(ValidationPartition.DEVELOPMENT_SAMPLE, dimension, state)]
        for partition in (
            ValidationPartition.PRE_DEVELOPMENT_OUT_OF_SAMPLE,
            ValidationPartition.EXPANDED_ALL,
        ):
            other = row_index[(partition, dimension, state)]
            dev_eod, other_eod = _eod(dev), _eod(other)
            dev_largest, _ = _concentration(_select(development, dimension, state))
            source = predevelopment if partition is ValidationPartition.PRE_DEVELOPMENT_OUT_OF_SAMPLE else expanded
            other_largest, _ = _concentration(_select(source, dimension, state))
            with localcontext(EMA_CONTEXT):
                comparisons.append(
                    PartitionComparison(
                        dimension=dimension,
                        state=state,
                        comparison_partition=partition.value,
                        development_n=dev.executable_n,
                        comparison_n=other.executable_n,
                        development_sessions=dev.session_count,
                        comparison_sessions=other.session_count,
                        development_median_mfe=dev_eod.mfe.median,
                        comparison_median_mfe=other_eod.mfe.median,
                        median_mfe_difference=(other_eod.mfe.median - dev_eod.mfe.median if other_eod.mfe.median is not None and dev_eod.mfe.median is not None else None),
                        development_median_mae=dev_eod.mae.median,
                        comparison_median_mae=other_eod.mae.median,
                        median_mae_difference=(other_eod.mae.median - dev_eod.mae.median if other_eod.mae.median is not None and dev_eod.mae.median is not None else None),
                        development_median_balance=dev_eod.balance.median,
                        comparison_median_balance=other_eod.balance.median,
                        median_balance_difference=(other_eod.balance.median - dev_eod.balance.median if other_eod.balance.median is not None and dev_eod.balance.median is not None else None),
                        sign_agrees=(_sign(other_eod.balance.median) == _sign(dev_eod.balance.median) if other_eod.balance.median is not None and dev_eod.balance.median is not None else None),
                        population_ratio=(Decimal(other.executable_n) / Decimal(dev.executable_n) if dev.executable_n else None),
                        development_largest_session_percentage=dev_largest,
                        comparison_largest_session_percentage=other_largest,
                        development_long_percentage=_percentage(dev.long_n, dev.setup_n),
                        comparison_long_percentage=_percentage(other.long_n, other.setup_n),
                        long_percentage_shift=_percentage(other.long_n, other.setup_n) - _percentage(dev.long_n, dev.setup_n),
                    )
                )

    return ExpandedStabilityReport(
        start_date=start,
        end_date=end,
        development_start=development_start,
        development_end=development_end,
        expanded_setup_n=len(expanded),
        expanded_executable_n=expanded_base.executable_n,
        expanded_session_count=expanded_base.session_count,
        development_setup_n=len(development),
        development_executable_n=sum(item.executable for item in development),
        development_session_count=len({item.session_date for item in development}),
        partition_statistics=tuple(rows),
        stability_scorecard=tuple(scorecard),
        direction_controlled=tuple(direction_rows),
        level_controlled=tuple(level_rows),
        session_concentration=tuple(concentrations),
        two_way_relationships=tuple(two_way),
        leave_one_month_out=tuple(leave_one_out),
        bootstrap_uncertainty=tuple(bootstraps),
        development_comparisons=tuple(comparisons),
        bootstrap_seed=bootstrap_seed,
        bootstrap_resamples=bootstrap_resamples,
    )


def stability_report_hash(report: ExpandedStabilityReport) -> str:
    return sha256(report.model_dump_json().encode()).hexdigest()
