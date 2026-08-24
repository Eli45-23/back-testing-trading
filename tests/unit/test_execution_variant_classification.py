from __future__ import annotations

import socket
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

import spy_research.cli as cli_module
from spy_research.execution import (
    AtrStopModel,
    ExecutionClassificationInputError,
    ExecutionVariantClassification,
    ExecutionWarning,
    ExitBootstrapInterval,
    ExitBootstrapUncertainty,
    ExitFamily,
    ExitMonthlyStatistics,
    ExitPartitionStatistics,
    ExitVariantStatistics,
    LeaveOneMonthOutR,
    StrategyPopulation,
    classify_execution_variants,
    execution_variant_classification_hash,
    exit_model_variants,
)
from spy_research.interactions import LevelType
from spy_research.research_stats import DistributionSummary


START = date(2026, 1, 2)
END = date(2026, 8, 19)


def distribution(n: int, value: Decimal) -> DistributionSummary:
    return DistributionSummary(
        n=n,
        mean=value,
        median=value,
        minimum=value,
        maximum=value,
        p25=value,
        p75=value,
    )


def statistics_row(population, variant, *, candidate_kind: str = "reject"):
    realized = 589
    if candidate_kind == "forward_negative_median":
        expanded_mean, expanded_median = Decimal("0.02"), Decimal("-1")
        jan_mean, aug_mean, positive_months = Decimal("0.03"), Decimal("-0.02"), 5
    elif candidate_kind == "forward_positive_median":
        expanded_mean, expanded_median = Decimal("0.015"), Decimal("0.05")
        jan_mean, aug_mean, positive_months = Decimal("0.02"), Decimal("-0.10"), 5
    elif candidate_kind == "robust":
        expanded_mean = expanded_median = jan_mean = aug_mean = Decimal("0.10")
        positive_months = 8
    else:
        expanded_mean, expanded_median = Decimal("-0.1"), Decimal("-0.2")
        jan_mean, aug_mean, positive_months = Decimal("-0.1"), Decimal("0.1"), 4
    monthly = tuple(
        ExitMonthlyStatistics(
            month=f"2026-{month:02d}",
            trade_n=(realized // 8 + (1 if month <= realized % 8 else 0)),
            mean_r=Decimal("0.1") if month <= positive_months else Decimal("-0.1"),
            median_r=Decimal("0.1") if month <= positive_months else Decimal("-0.1"),
            positive_n=1,
            negative_n=0,
            zero_n=0,
        )
        for month in range(1, 9)
    )
    loo_value = Decimal("0.01") if candidate_kind == "robust" else Decimal("-0.04")
    return ExitVariantStatistics(
        strategy_population=population,
        variant=variant,
        membership_n=realized,
        atr_eligible_n=realized,
        target_context_eligible_n=realized,
        realized_n=realized,
        unavailable_n=0,
        ambiguous_n=0,
        stop_exit_n=realized,
        target_exit_n=0,
        cross_exit_n=0,
        time_exit_n=0,
        eod_exit_n=0,
        r_multiple=distribution(realized, expanded_mean),
        r_standard_deviation=Decimal("1"),
        positive_r_n=0,
        zero_r_n=0,
        negative_r_n=realized,
        win_rate_percentage=Decimal("0"),
        loss_rate_percentage=Decimal("100"),
        holding_minutes=distribution(realized, Decimal("10")),
        monthly=monthly,
        positive_month_n=positive_months,
        negative_month_n=8 - positive_months,
        session_count=120,
        direction_composition=(),
        level_composition=((LevelType.PDH, realized),),
        partitions=(
            ExitPartitionStatistics(
                partition="EXPANDED", trade_n=realized,
                mean_r=expanded_mean, median_r=expanded_median,
            ),
            ExitPartitionStatistics(
                partition="JANUARY_JULY", trade_n=500,
                mean_r=jan_mean, median_r=expanded_median,
            ),
            ExitPartitionStatistics(
                partition="AUGUST_DEVELOPMENT", trade_n=89,
                mean_r=aug_mean, median_r=expanded_median,
            ),
        ),
        leave_one_month_out=tuple(
            LeaveOneMonthOutR(
                excluded_month=f"2026-{month:02d}",
                trade_n=500,
                mean_r=loo_value,
                median_r=expanded_median,
            )
            for month in range(1, 9)
        ),
    )


def bootstrap_row(population, variant, *, robust: bool = False):
    lower = Decimal("0.01") if robust else Decimal("-0.1")
    return ExitBootstrapUncertainty(
        strategy_population=population,
        variant_id=variant.variant_id,
        realized_n=589,
        session_cluster_count=120,
        seed=1302,
        resamples=10_000,
        intervals=(
            ExitBootstrapInterval(
                metric="MEAN_R", p2_5=lower, p50=Decimal("0.02"), p97_5=Decimal("0.2")
            ),
            ExitBootstrapInterval(
                metric="MEDIAN_R", p2_5=Decimal("-1"), p50=Decimal("0"), p97_5=Decimal("1")
            ),
        ),
    )


def frozen_inputs(*, robust_variant_id: str | None = None):
    stats = []
    bootstraps = []
    for population in (StrategyPopulation.BASE_ALL, StrategyPopulation.BASE_SHORT):
        for variant in exit_model_variants():
            kind = "reject"
            if population is StrategyPopulation.BASE_SHORT:
                if robust_variant_id == variant.variant_id:
                    kind = "robust"
                elif variant.family is ExitFamily.NEXT_OBJECTIVE_LEVEL:
                    if variant.stop_model is AtrStopModel.ATR_0_75:
                        kind = "forward_negative_median"
                    elif variant.stop_model is AtrStopModel.ATR_1_00:
                        kind = "forward_positive_median"
            stats.append(statistics_row(population, variant, candidate_kind=kind))
            bootstraps.append(
                bootstrap_row(
                    population,
                    variant,
                    robust=population is StrategyPopulation.BASE_SHORT
                    and robust_variant_id == variant.variant_id,
                )
            )
    return tuple(stats), tuple(bootstraps)


def classify(stats=None, bootstraps=None):
    if stats is None or bootstraps is None:
        stats, bootstraps = frozen_inputs()
    return classify_execution_variants(
        start_date=START,
        end_date=END,
        statistics=stats,
        bootstrap_uncertainty=bootstraps,
        source_stage13_2_hash="stage13.2",
        source_stage13_1_hash="stage13.1",
    )


def test_mechanical_gates_produce_only_two_forward_candidates() -> None:
    result = classify()
    assert len(result.rows) == 36
    assert result.handoff.robust_candidates == ()
    assert len(result.handoff.forward_test_candidates) == 2
    assert all("NEXT_OBJECTIVE_LEVEL" in item for item in result.handoff.forward_test_candidates)
    assert len(result.handoff.controls) == 51
    assert len(result.handoff.rejected_variants) == 19


def test_candidate_warnings_preserve_measured_failures() -> None:
    result = classify()
    candidates = {
        row.stop_multiplier: row
        for row in result.rows
        if row.classification is ExecutionVariantClassification.FORWARD_TEST_CANDIDATE
    }
    assert ExecutionWarning.NEGATIVE_EXPANDED_MEDIAN in candidates[Decimal("0.75")].warnings
    one = candidates[Decimal("1.00")]
    assert ExecutionWarning.NEGATIVE_EXPANDED_MEDIAN not in one.warnings
    assert {
        ExecutionWarning.NEGATIVE_DEVELOPMENT_MEAN,
        ExecutionWarning.NEGATIVE_WORST_LOO_MEAN,
        ExecutionWarning.BOOTSTRAP_INTERVAL_CROSSES_ZERO,
    }.issubset(one.warnings)


def test_all_robust_gates_are_required_without_reinterpreting_zero() -> None:
    selected = next(
        item for item in exit_model_variants()
        if item.family is ExitFamily.TIME_EXIT
        and item.stop_model is AtrStopModel.ATR_0_50
        and item.time_minutes == 15
    )
    stats, bootstraps = frozen_inputs(robust_variant_id=selected.variant_id)
    result = classify(stats, bootstraps)
    row = next(item for item in result.rows if item.variant_id == selected.variant_id)
    assert row.gates.robust_passed
    assert row.classification is ExecutionVariantClassification.ROBUST_EXECUTION_CANDIDATE
    changed = list(stats)
    index = next(
        i for i, item in enumerate(changed)
        if item.strategy_population is StrategyPopulation.BASE_SHORT
        and item.variant.variant_id == selected.variant_id
    )
    loo = list(changed[index].leave_one_month_out)
    loo[0] = loo[0].model_copy(update={"mean_r": Decimal("-0.0001")})
    changed[index] = changed[index].model_copy(update={"leave_one_month_out": tuple(loo)})
    downgraded = classify(tuple(changed), bootstraps)
    row = next(item for item in downgraded.rows if item.variant_id == selected.variant_id)
    assert row.classification is ExecutionVariantClassification.FORWARD_TEST_CANDIDATE


def test_fixed_r_controls_cannot_be_promoted() -> None:
    selected = next(item for item in exit_model_variants() if item.family is ExitFamily.FIXED_R_CONTROL)
    stats, bootstraps = frozen_inputs(robust_variant_id=selected.variant_id)
    row = next(item for item in classify(stats, bootstraps).rows if item.variant_id == selected.variant_id)
    assert row.gates.robust_passed
    assert row.classification is ExecutionVariantClassification.RETAIN_AS_CONTROL


@pytest.mark.parametrize("field,value", (("realized_n", 99), ("session_count", 49)))
def test_future_sample_coverage_gate_is_explicit(field, value) -> None:
    stats, bootstraps = frozen_inputs()
    selected = next(
        item for item in stats
        if item.strategy_population is StrategyPopulation.BASE_SHORT
        and item.variant.family is ExitFamily.NEXT_OBJECTIVE_LEVEL
        and item.variant.stop_model is AtrStopModel.ATR_0_75
    )
    index = stats.index(selected)
    replacement = selected.model_copy(update={field: value})
    if field == "realized_n":
        replacement = replacement.model_copy(
            update={
                "membership_n": 99,
                "atr_eligible_n": 99,
                "target_context_eligible_n": 99,
                "stop_exit_n": 99,
                "negative_r_n": 99,
                "r_multiple": distribution(99, Decimal("0.02")),
                "holding_minutes": distribution(99, Decimal("10")),
                "monthly": tuple(
                    row.model_copy(update={"trade_n": 99 if i == 0 else 0})
                    for i, row in enumerate(selected.monthly)
                ),
                "level_composition": ((LevelType.PDH, 99),),
                "partitions": tuple(
                    row.model_copy(update={"trade_n": 99 if i == 0 else row.trade_n})
                    for i, row in enumerate(selected.partitions)
                ),
            }
        )
    changed = list(stats)
    changed[index] = replacement
    changed_bootstraps = list(bootstraps)
    bootstrap_index = next(
        i
        for i, item in enumerate(changed_bootstraps)
        if item.strategy_population is StrategyPopulation.BASE_SHORT
        and item.variant_id == selected.variant.variant_id
    )
    bootstrap_field = (
        "realized_n" if field == "realized_n" else "session_cluster_count"
    )
    changed_bootstraps[bootstrap_index] = changed_bootstraps[
        bootstrap_index
    ].model_copy(update={bootstrap_field: value})
    row = next(
        item for item in classify(tuple(changed), tuple(changed_bootstraps)).rows
        if item.variant_id == selected.variant.variant_id
    )
    assert row.classification is ExecutionVariantClassification.DO_NOT_ADVANCE


def test_classifier_rejects_incomplete_or_duplicate_statistical_universe() -> None:
    stats, bootstraps = frozen_inputs()
    with pytest.raises(ExecutionClassificationInputError, match="72"):
        classify(stats[:-1], bootstraps)
    with pytest.raises(ExecutionClassificationInputError, match="duplicate"):
        classify(stats[:-1] + (stats[0],), bootstraps)


def test_report_is_immutable_and_hash_is_deterministic() -> None:
    first = classify()
    second = classify()
    assert first == second
    assert execution_variant_classification_hash(first) == execution_variant_classification_hash(second)
    with pytest.raises(ValidationError):
        first.rows[0].classification = ExecutionVariantClassification.DO_NOT_ADVANCE


def test_classification_cli_is_offline_and_nonpersistent(monkeypatch, tmp_path) -> None:
    result = SimpleNamespace()

    class FakeService:
        def __init__(self, *args):
            pass

        def calculate(self, *, start, end):
            return result

    monkeypatch.setattr(cli_module, "ExecutionVariantClassificationService", FakeService)
    monkeypatch.setattr(cli_module, "_print_execution_variant_classification", lambda report: None)
    monkeypatch.setattr(
        socket,
        "create_connection",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("network")),
    )
    before = tuple(tmp_path.rglob("*"))
    assert cli_module.main(
        (
            "classify-execution-variants",
            "--start", "2026-01-02",
            "--end", "2026-08-19",
            "--raw-data-root", str(tmp_path / "raw"),
            "--processed-data-root", str(tmp_path / "processed"),
        )
    ) == 0
    assert tuple(tmp_path.rglob("*")) == before


def test_classifier_signature_has_no_market_or_optimization_inputs() -> None:
    from inspect import signature

    assert tuple(signature(classify_execution_variants).parameters) == (
        "start_date",
        "end_date",
        "statistics",
        "bootstrap_uncertainty",
        "source_stage13_2_hash",
        "source_stage13_1_hash",
    )
