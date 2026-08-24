"""Pure Stage 13.3 gates over frozen Stage 13.2 statistical records only."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Sequence

from spy_research.execution.classification_models import (
    ExecutionClassificationInputError,
    ExecutionControlReference,
    ExecutionGateResults,
    ExecutionVariantClassification,
    ExecutionVariantClassificationReport,
    ExecutionVariantClassificationRow,
    ExecutionWarning,
    Stage14ExecutionHandoff,
)
from spy_research.execution.exit_models import (
    ExitBootstrapUncertainty,
    ExitFamily,
    ExitModelVariant,
    ExitVariantStatistics,
)
from spy_research.execution.models import StrategyPopulation


def _partition(item: ExitVariantStatistics, name: str):
    try:
        return next(row for row in item.partitions if row.partition == name)
    except StopIteration as exc:
        raise ExecutionClassificationInputError(
            f"missing frozen {name} partition for {item.variant.variant_id}"
        ) from exc


def _mean_bootstrap(item: ExitBootstrapUncertainty):
    try:
        return next(row for row in item.intervals if row.metric == "MEAN_R")
    except StopIteration as exc:
        raise ExecutionClassificationInputError(
            f"missing mean-R bootstrap for {item.variant_id}"
        ) from exc


def _exit_definition(variant: ExitModelVariant) -> str:
    if variant.family is ExitFamily.FIXED_R_CONTROL:
        return f"Fixed {variant.fixed_target_r}R target"
    if variant.family is ExitFamily.TIME_EXIT:
        return f"{variant.time_minutes}-minute time exit"
    return {
        ExitFamily.OPPOSITE_EMA9_20_CROSS: "First opposite EMA9/EMA20 cross",
        ExitFamily.OPPOSITE_EMA9_VWAP_CROSS: "First opposite EMA9/VWAP cross",
        ExitFamily.OPPOSITE_EMA20_VWAP_CROSS: "First opposite EMA20/VWAP cross",
        ExitFamily.NEXT_OBJECTIVE_LEVEL: "Next objective level",
    }[variant.family]


def _warnings(
    *,
    expanded_mean: Decimal,
    expanded_median: Decimal,
    january_july_mean: Decimal,
    development_mean: Decimal,
    worst_loo_mean: Decimal,
    positive_months: int,
    realized_n: int,
    session_count: int,
    bootstrap_lower: Decimal,
    bootstrap_upper: Decimal,
) -> tuple[ExecutionWarning, ...]:
    measured = []
    facts = (
        (expanded_mean < 0, ExecutionWarning.NEGATIVE_EXPANDED_MEAN),
        (expanded_median < 0, ExecutionWarning.NEGATIVE_EXPANDED_MEDIAN),
        (january_july_mean < 0, ExecutionWarning.NEGATIVE_JANUARY_JULY_MEAN),
        (development_mean < 0, ExecutionWarning.NEGATIVE_DEVELOPMENT_MEAN),
        (worst_loo_mean < 0, ExecutionWarning.NEGATIVE_WORST_LOO_MEAN),
        (
            bootstrap_lower <= 0 <= bootstrap_upper,
            ExecutionWarning.BOOTSTRAP_INTERVAL_CROSSES_ZERO,
        ),
        (
            bootstrap_upper < 0,
            ExecutionWarning.BOOTSTRAP_INTERVAL_BELOW_ZERO,
        ),
        (
            positive_months < 5,
            ExecutionWarning.INSUFFICIENT_MONTHLY_STABILITY,
        ),
        (realized_n < 100, ExecutionWarning.INSUFFICIENT_REALIZED_PATHS),
        (session_count < 50, ExecutionWarning.INSUFFICIENT_SESSION_COVERAGE),
    )
    for applies, warning in facts:
        if applies:
            measured.append(warning)
    return tuple(measured)


def classify_execution_variants(
    *,
    start_date: date,
    end_date: date,
    statistics: Sequence[ExitVariantStatistics],
    bootstrap_uncertainty: Sequence[ExitBootstrapUncertainty],
    source_stage13_2_hash: str,
    source_stage13_1_hash: str,
) -> ExecutionVariantClassificationReport:
    """Classify a closed variant universe without accepting market-level inputs."""

    stats = tuple(statistics)
    bootstraps = tuple(bootstrap_uncertainty)
    expected_populations = (
        StrategyPopulation.BASE_ALL,
        StrategyPopulation.BASE_SHORT,
    )
    if len(stats) != 72 or len(bootstraps) != 72:
        raise ExecutionClassificationInputError(
            "Stage 13.3 requires the frozen 72 population/variant statistical rows"
        )
    stats_by_key = {
        (row.strategy_population, row.variant.variant_id): row for row in stats
    }
    bootstrap_by_key = {
        (row.strategy_population, row.variant_id): row for row in bootstraps
    }
    if len(stats_by_key) != 72 or len(bootstrap_by_key) != 72:
        raise ExecutionClassificationInputError("duplicate Stage 13.2 statistical key")
    variants = tuple(
        row.variant
        for row in stats
        if row.strategy_population is StrategyPopulation.BASE_ALL
    )
    if len(variants) != 36:
        raise ExecutionClassificationInputError("missing BASE_ALL control universe")
    expected_keys = {
        (population, variant.variant_id)
        for population in expected_populations
        for variant in variants
    }
    if set(stats_by_key) != expected_keys or set(bootstrap_by_key) != expected_keys:
        raise ExecutionClassificationInputError(
            "Stage 13.2 populations or variant membership changed"
        )
    rows = []
    for variant in variants:
        item = stats_by_key[(StrategyPopulation.BASE_SHORT, variant.variant_id)]
        if item.variant != variant:
            raise ExecutionClassificationInputError(
                f"population variant definitions differ for {variant.variant_id}"
            )
        bootstrap = bootstrap_by_key[
            (StrategyPopulation.BASE_SHORT, variant.variant_id)
        ]
        if bootstrap.realized_n != item.realized_n:
            raise ExecutionClassificationInputError(
                f"bootstrap coverage mismatch for {variant.variant_id}"
            )
        expanded = _partition(item, "EXPANDED")
        january_july = _partition(item, "JANUARY_JULY")
        development = _partition(item, "AUGUST_DEVELOPMENT")
        mean_bootstrap = _mean_bootstrap(bootstrap)
        values = (
            expanded.mean_r,
            expanded.median_r,
            january_july.mean_r,
            january_july.median_r,
            development.mean_r,
            development.median_r,
        )
        loo_means = tuple(
            row.mean_r for row in item.leave_one_month_out if row.mean_r is not None
        )
        if any(value is None for value in values) or not loo_means:
            raise ExecutionClassificationInputError(
                f"incomplete frozen robustness statistics for {variant.variant_id}"
            )
        (
            expanded_mean,
            expanded_median,
            january_july_mean,
            january_july_median,
            development_mean,
            development_median,
        ) = values
        assert all(value is not None for value in values)
        worst_loo_mean = min(loo_means)
        zero_months = len(item.monthly) - item.positive_month_n - item.negative_month_n
        gates = ExecutionGateResults(
            realized_paths_at_least_100=item.realized_n >= 100,
            represented_sessions_at_least_50=item.session_count >= 50,
            expanded_mean_positive=expanded_mean > 0,
            expanded_median_positive=expanded_median > 0,
            january_july_mean_positive=january_july_mean > 0,
            development_mean_positive=development_mean > 0,
            worst_loo_mean_nonnegative=worst_loo_mean >= 0,
            at_least_five_positive_monthly_medians=item.positive_month_n >= 5,
            bootstrap_mean_lower_bound_positive=mean_bootstrap.p2_5 > 0,
        )
        if variant.family is ExitFamily.FIXED_R_CONTROL:
            classification = ExecutionVariantClassification.RETAIN_AS_CONTROL
        elif gates.robust_passed:
            classification = ExecutionVariantClassification.ROBUST_EXECUTION_CANDIDATE
        elif gates.forward_test_passed:
            classification = ExecutionVariantClassification.FORWARD_TEST_CANDIDATE
        else:
            classification = ExecutionVariantClassification.DO_NOT_ADVANCE
        rows.append(
            ExecutionVariantClassificationRow(
                strategy_population=StrategyPopulation.BASE_SHORT,
                variant_id=variant.variant_id,
                family=variant.family,
                stop_multiplier=variant.stop_multiplier,
                exit_definition=_exit_definition(variant),
                realized_paths=item.realized_n,
                session_count=item.session_count,
                expanded_mean_r=expanded_mean,
                expanded_median_r=expanded_median,
                january_july_mean_r=january_july_mean,
                january_july_median_r=january_july_median,
                development_mean_r=development_mean,
                development_median_r=development_median,
                positive_month_count=item.positive_month_n,
                negative_month_count=item.negative_month_n,
                zero_month_count=zero_months,
                worst_loo_mean_r=worst_loo_mean,
                bootstrap_mean_p2_5=mean_bootstrap.p2_5,
                bootstrap_mean_p50=mean_bootstrap.p50,
                bootstrap_mean_p97_5=mean_bootstrap.p97_5,
                gates=gates,
                classification=classification,
                warnings=_warnings(
                    expanded_mean=expanded_mean,
                    expanded_median=expanded_median,
                    january_july_mean=january_july_mean,
                    development_mean=development_mean,
                    worst_loo_mean=worst_loo_mean,
                    positive_months=item.positive_month_n,
                    realized_n=item.realized_n,
                    session_count=item.session_count,
                    bootstrap_lower=mean_bootstrap.p2_5,
                    bootstrap_upper=mean_bootstrap.p97_5,
                ),
            )
        )
    controls = tuple(
        ExecutionControlReference(
            strategy_population=StrategyPopulation.BASE_ALL,
            variant_id=variant.variant_id,
            reason="UNIVERSAL_RESEARCH_CONTROL",
        )
        for variant in variants
    ) + tuple(
        ExecutionControlReference(
            strategy_population=StrategyPopulation.BASE_SHORT,
            variant_id=row.variant_id,
            reason="FIXED_R_REFERENCE",
        )
        for row in rows
        if row.family is ExitFamily.FIXED_R_CONTROL
    )
    robust = tuple(
        row.variant_id
        for row in rows
        if row.classification
        is ExecutionVariantClassification.ROBUST_EXECUTION_CANDIDATE
    )
    forward = tuple(
        row.variant_id
        for row in rows
        if row.classification is ExecutionVariantClassification.FORWARD_TEST_CANDIDATE
    )
    rejected = tuple(
        row.variant_id
        for row in rows
        if row.classification is ExecutionVariantClassification.DO_NOT_ADVANCE
    )
    return ExecutionVariantClassificationReport(
        start_date=start_date,
        end_date=end_date,
        source_stage13_2_hash=source_stage13_2_hash,
        source_stage13_1_hash=source_stage13_1_hash,
        rows=tuple(rows),
        handoff=Stage14ExecutionHandoff(
            robust_candidates=robust,
            forward_test_candidates=forward,
            controls=controls,
            rejected_variants=rejected,
        ),
    )
