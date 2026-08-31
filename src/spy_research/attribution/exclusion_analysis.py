"""Pure Stage 15.1 analysis over the exact Stage 15 observation population."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal
from hashlib import sha256
from random import Random
from statistics import median

from spy_research.attribution.analysis import _mean, _percentile, _sample_std
from spy_research.attribution.exclusion_models import (
    ConditionAudit,
    ConditionOverlapCell,
    ExclusionClassification,
    ExclusionMetrics,
    ExclusionMonthlyRow,
    ExclusionPeriodRow,
    ExclusionValidationReport,
    ExclusionVariantResult,
    RemovalAudit,
    RoomDiagnosticClassification,
    RoomGeometryDiagnostic,
)
from spy_research.attribution.models import AttributionObservation, AttributionReport


BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 150_101
DEVELOPMENT_START = date(2026, 8, 3)
MONTHS = tuple(f"2026-{value:02d}" for value in range(1, 9))
CONDITIONS = (
    (1, "ALL_VWAP_ALIGNED×ROOM_GT_3_ATR"),
    (2, "BULLISH_STRUCTURE×ROOM_0_5_TO_1_ATR"),
    (3, "NO_VWAP_ALIGNMENT×ROOM_0_5_TO_1_ATR"),
    (4, "EMA_ALIGNED×BULLISH_STRUCTURE"),
)
VARIANTS = (
    ("BASE_SHORT_CONTROL", ()),
    ("EXCLUDE_NEG_1", (1,)),
    ("EXCLUDE_NEG_2", (2,)),
    ("EXCLUDE_NEG_3", (3,)),
    ("EXCLUDE_NEG_4", (4,)),
    ("EXCLUDE_ANY_OF_1_TO_4", (1, 2, 3, 4)),
    ("EXCLUDE_NEG_1_2", (1, 2)),
    ("EXCLUDE_NEG_1_4", (1, 4)),
    ("EXCLUDE_NEG_2_4", (2, 4)),
    ("EXCLUDE_NEG_1_2_4", (1, 2, 4)),
)
EXPECTED_BASELINE = {
    "membership": 1040,
    "realized": 589,
    "sessions": 120,
    "mean_r": Decimal("0.01550883457374802951802346117"),
    "median_r": Decimal("0.053763440860215053763440860215053763440860215053763"),
    "profit_factor": Decimal("1.034083364870415548346748920"),
    "win_rate": Decimal("0.5331069609507640067911714771"),
    "lomo": Decimal("-0.04068640984458862292391584436"),
    "ci_low": Decimal("-0.1055729406662720764288037732"),
    "ci_high": Decimal("0.1494157755424193950966348630"),
}
EXPECTED_CONDITION_REALIZED = {1: 41, 2: 36, 3: 42, 4: 41}
EXPECTED_CONDITION_STAGE15 = {
    1: (
        "VWAP_ALIGNMENT×ROOM_ATR",
        "ALL_ALIGNED×GT_3_0_ATR",
        Decimal("-0.5719796703443959290780644437"),
        Decimal("0.00826819687970277512"),
    ),
    2: (
        "MARKET_STRUCTURE×ROOM_ATR",
        "BULLISH_STRUCTURE×ATR_0_5_TO_1_0",
        Decimal("-0.5107346898020561213408556622"),
        Decimal("0.00359886705663591800"),
    ),
    3: (
        "VWAP_ALIGNMENT×ROOM_ATR",
        "NONE_ALIGNED×ATR_0_5_TO_1_0",
        Decimal("-0.3776304527361786403990969507"),
        Decimal("0.0651876680507612496"),
    ),
    4: (
        "EMA_ALIGNMENT×MARKET_STRUCTURE",
        "EMA_ALIGNED×BULLISH_STRUCTURE",
        Decimal("-0.3574880337800989185518839110"),
        Decimal("0.07525730090056778066666666667"),
    ),
}


def _matches(item: AttributionObservation, condition_id: int) -> bool:
    if condition_id == 1:
        return item.factor("VWAP_ALIGNMENT") == "ALL_ALIGNED" and item.factor("ROOM_ATR") == "GT_3_0_ATR"
    if condition_id == 2:
        return item.factor("MARKET_STRUCTURE") == "BULLISH_STRUCTURE" and item.factor("ROOM_ATR") == "ATR_0_5_TO_1_0"
    if condition_id == 3:
        return item.factor("VWAP_ALIGNMENT") == "NONE_ALIGNED" and item.factor("ROOM_ATR") == "ATR_0_5_TO_1_0"
    if condition_id == 4:
        return item.factor("EMA_ALIGNMENT") == "EMA_ALIGNED" and item.factor("MARKET_STRUCTURE") == "BULLISH_STRUCTURE"
    raise ValueError(f"unknown frozen condition {condition_id}")


def _ratio(part: int, whole: int) -> Decimal | None:
    return Decimal(part) / Decimal(whole) if whole else None


def _profit_factor(values: list[Decimal]) -> Decimal | None:
    positive = sum((item for item in values if item > 0), Decimal(0))
    negative = abs(sum((item for item in values if item < 0), Decimal(0)))
    return positive / negative if negative else None


def _bootstrap(observations: list[AttributionObservation], salt: str) -> tuple[Decimal | None, Decimal | None, Decimal | None]:
    by_session: dict[date, list[Decimal]] = defaultdict(list)
    for item in observations:
        if item.r_multiple is not None:
            by_session[item.session_date].append(item.r_multiple)
    sessions = sorted(by_session)
    if not sessions:
        return None, None, None
    rng = Random(BOOTSTRAP_SEED + int(sha256(salt.encode()).hexdigest()[:8], 16))
    means = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        values = []
        for _session in sessions:
            values.extend(by_session[rng.choice(sessions)])
        value = _mean(values)
        assert value is not None
        means.append(value)
    return (
        _percentile(means, Decimal("0.025")),
        _percentile(means, Decimal("0.50")),
        _percentile(means, Decimal("0.975")),
    )


def _paired_bootstrap_delta(
    baseline: list[AttributionObservation],
    retained_ids: set[str],
    salt: str,
) -> tuple[Decimal | None, Decimal | None, Decimal | None]:
    by_session: dict[date, list[AttributionObservation]] = defaultdict(list)
    for item in baseline:
        if item.r_multiple is not None:
            by_session[item.session_date].append(item)
    sessions = sorted(by_session)
    if not sessions:
        return None, None, None
    rng = Random(BOOTSTRAP_SEED + int(sha256((salt + "|delta").encode()).hexdigest()[:8], 16))
    deltas = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        baseline_values = []
        retained_values = []
        for _session in sessions:
            sampled = by_session[rng.choice(sessions)]
            baseline_values.extend(item.r_multiple for item in sampled if item.r_multiple is not None)
            retained_values.extend(item.r_multiple for item in sampled if item.setup_identity in retained_ids and item.r_multiple is not None)
        base_mean = _mean(baseline_values)
        kept_mean = _mean(retained_values)
        if base_mean is not None and kept_mean is not None:
            deltas.append(kept_mean - base_mean)
    return (
        _percentile(deltas, Decimal("0.025")),
        _percentile(deltas, Decimal("0.50")),
        _percentile(deltas, Decimal("0.975")),
    )


def _period_rows(observations: list[AttributionObservation], baseline: list[AttributionObservation]) -> tuple[ExclusionPeriodRow, ...]:
    specs = (
        ("PRE_DEVELOPMENT", lambda item: item.session_date < DEVELOPMENT_START),
        ("DEVELOPMENT", lambda item: item.session_date >= DEVELOPMENT_START),
        ("EXPANDED", lambda item: True),
    )
    rows = []
    for name, predicate in specs:
        values = [item.r_multiple for item in observations if predicate(item) and item.r_multiple is not None]
        baseline_values = [item.r_multiple for item in baseline if predicate(item) and item.r_multiple is not None]
        mean = _mean(values)
        baseline_mean = _mean(baseline_values)
        rows.append(ExclusionPeriodRow(
            period=name,
            trades=len(values),
            mean_r=mean,
            baseline_mean_r=baseline_mean,
            mean_r_delta=mean - baseline_mean if mean is not None and baseline_mean is not None else None,
            median_r=Decimal(median(values)) if values else None,
            profit_factor=_profit_factor(values),
        ))
    return tuple(rows)


def _metrics(observations: list[AttributionObservation], baseline: list[AttributionObservation], salt: str) -> ExclusionMetrics:
    realized = [item for item in observations if item.r_multiple is not None]
    values = [item.r_multiple for item in realized if item.r_multiple is not None]
    by_month: dict[str, list[Decimal]] = defaultdict(list)
    baseline_month_counts: dict[str, int] = defaultdict(int)
    for item in realized:
        assert item.r_multiple is not None
        by_month[item.session_date.strftime("%Y-%m")].append(item.r_multiple)
    for item in baseline:
        if item.r_multiple is not None:
            baseline_month_counts[item.session_date.strftime("%Y-%m")] += 1
    monthly = []
    for month in MONTHS:
        month_values = by_month[month]
        monthly.append(ExclusionMonthlyRow(
            month=month,
            trades=len(month_values),
            mean_r=_mean(month_values),
            median_r=Decimal(median(month_values)) if month_values else None,
            total_r=sum(month_values, Decimal(0)),
            baseline_trades=baseline_month_counts[month],
            retained_percentage=_ratio(len(month_values), baseline_month_counts[month]),
        ))
    represented = [item for item in monthly if item.trades]
    total_r = sum(values, Decimal(0))
    lomo = [
        (total_r - item.total_r) / Decimal(len(values) - item.trades)
        for item in represented if len(values) > item.trades
    ]
    worst = min(represented, key=lambda item: item.mean_r) if represented else None
    low, center, high = _bootstrap(observations, salt)
    return ExclusionMetrics(
        original_membership=len(baseline),
        retained_membership=len(observations),
        retained_percentage=Decimal(len(observations)) / Decimal(len(baseline)),
        realized_retained=len(realized),
        unavailable_or_ambiguous_retained=len(observations) - len(realized),
        sessions=len({item.session_date for item in realized}),
        win_rate=_ratio(sum(item > 0 for item in values), len(values)),
        mean_r=_mean(values),
        median_r=Decimal(median(values)) if values else None,
        standard_deviation_r=_sample_std(values),
        profit_factor=_profit_factor(values),
        target_hit_rate=_ratio(sum(item.exit_reason == "NEXT_OBJECTIVE_LEVEL" for item in realized), len(realized)),
        stop_hit_rate=_ratio(sum(item.exit_reason == "STOP" for item in realized), len(realized)),
        eod_exit_rate=_ratio(sum(item.exit_reason == "EOD_CLOSE" for item in realized), len(realized)),
        median_mfe=Decimal(median([item.mfe for item in realized if item.mfe is not None])) if any(item.mfe is not None for item in realized) else None,
        median_mae=Decimal(median([item.mae for item in realized if item.mae is not None])) if any(item.mae is not None for item in realized) else None,
        fifth_percentile_r=_percentile(values, Decimal("0.05")),
        positive_months=sum(item.total_r > 0 for item in represented),
        negative_months=sum(item.total_r < 0 for item in represented),
        worst_month=worst.month if worst is not None else None,
        worst_month_mean_r=worst.mean_r if worst is not None else None,
        leave_one_month_out_min_mean_r=min(lomo) if lomo else None,
        bootstrap_mean_r_low=low,
        bootstrap_mean_r_median=center,
        bootstrap_mean_r_high=high,
        monthly=tuple(monthly),
        periods=_period_rows(observations, baseline),
    )


def _room_diagnostic(variant_id: str, condition_ids: tuple[int, ...], removed: list[AttributionObservation], retained: list[AttributionObservation]) -> RoomGeometryDiagnostic | None:
    if not set(condition_ids) & {1, 2, 3}:
        return None
    def normalized(items, field):
        return [
            getattr(item, field) / item.confirmation_atr
            for item in items
            if item.r_multiple is not None
            and getattr(item, field) is not None
            and item.confirmation_atr is not None
            and item.confirmation_atr > 0
        ]
    removed_mfe = normalized(removed, "five_minute_mfe")
    removed_mae = normalized(removed, "five_minute_mae")
    retained_mfe = normalized(retained, "five_minute_mfe")
    retained_mae = normalized(retained, "five_minute_mae")
    removed_sessions = len({item.session_date for item in removed if item.r_multiple is not None})
    med_removed_mfe = Decimal(median(removed_mfe)) if removed_mfe else None
    med_removed_mae = Decimal(median(removed_mae)) if removed_mae else None
    med_retained_mfe = Decimal(median(retained_mfe)) if retained_mfe else None
    med_retained_mae = Decimal(median(retained_mae)) if retained_mae else None
    favorable_delta = med_removed_mfe - med_retained_mfe if med_removed_mfe is not None and med_retained_mfe is not None else None
    adverse_delta = med_removed_mae - med_retained_mae if med_removed_mae is not None and med_retained_mae is not None else None
    removed_n = sum(item.r_multiple is not None for item in removed)
    if removed_n < 30 or removed_sessions < 10 or favorable_delta is None or adverse_delta is None:
        classification = RoomDiagnosticClassification.INSUFFICIENT_EVIDENCE
    else:
        adverse_favorable = favorable_delta <= Decimal("-0.10")
        adverse_adverse = adverse_delta >= Decimal("0.10")
        if adverse_favorable and adverse_adverse:
            classification = RoomDiagnosticClassification.ENTRY_BEHAVIOR_SUPPORTED
        elif adverse_favorable or adverse_adverse:
            classification = RoomDiagnosticClassification.MIXED
        else:
            classification = RoomDiagnosticClassification.EXIT_GEOMETRY_DEPENDENT
    return RoomGeometryDiagnostic(
        variant_id=variant_id,
        removed_realized_n=removed_n,
        removed_sessions=removed_sessions,
        removed_median_five_mfe_atr=med_removed_mfe,
        retained_median_five_mfe_atr=med_retained_mfe,
        removed_median_five_mae_atr=med_removed_mae,
        retained_median_five_mae_atr=med_retained_mae,
        favorable_excursion_delta=favorable_delta,
        adverse_excursion_delta=adverse_delta,
        classification=classification,
    )


def _validate_baseline(stage15: AttributionReport, metrics: ExclusionMetrics) -> None:
    observed = {
        "membership": metrics.retained_membership,
        "realized": metrics.realized_retained,
        "sessions": metrics.sessions,
        "mean_r": metrics.mean_r,
        "median_r": metrics.median_r,
        "profit_factor": metrics.profit_factor,
        "win_rate": metrics.win_rate,
        "lomo": metrics.leave_one_month_out_min_mean_r,
        "ci_low": metrics.bootstrap_mean_r_low,
        "ci_high": metrics.bootstrap_mean_r_high,
    }
    for name, expected in EXPECTED_BASELINE.items():
        if observed[name] != expected:
            raise ValueError(f"Stage 15 baseline reconciliation failed for {name}: {observed[name]} != {expected}")
    if stage15.baseline.population_n != metrics.retained_membership or stage15.baseline.trades != metrics.realized_retained:
        raise ValueError("Stage 15 report and observation population differ")


def _validate_frozen_conditions(stage15: AttributionReport) -> None:
    groups = {
        (item.factor, item.state): item for item in stage15.interaction_groups
    }
    for condition_id, (factor, state, expected_mean, expected_q) in (
        EXPECTED_CONDITION_STAGE15.items()
    ):
        group = groups.get((factor, state))
        if group is None:
            raise ValueError(
                f"frozen condition {condition_id} is absent from the Stage 15 report"
            )
        expected_trades = EXPECTED_CONDITION_REALIZED[condition_id]
        if (
            group.trades != expected_trades
            or group.mean_r != expected_mean
            or group.fdr_q_value != expected_q
        ):
            raise ValueError(
                f"frozen condition {condition_id} no longer reconciles to Stage 15"
            )


def analyze_exclusions(
    observations: tuple[AttributionObservation, ...],
    stage15: AttributionReport,
    *,
    source_stage15_report_hash: str,
) -> ExclusionValidationReport:
    baseline = list(observations)
    condition_ids = {
        condition_id: {item.setup_identity for item in baseline if _matches(item, condition_id)}
        for condition_id, _name in CONDITIONS
    }
    baseline_metrics = _metrics(baseline, baseline, "BASE_SHORT_CONTROL")
    baseline_metrics = baseline_metrics.model_copy(update={
        "bootstrap_mean_r_low": stage15.baseline.bootstrap_mean_r_low,
        "bootstrap_mean_r_high": stage15.baseline.bootstrap_mean_r_high,
    })
    _validate_baseline(stage15, baseline_metrics)
    _validate_frozen_conditions(stage15)
    conditions = []
    for condition_id, name in CONDITIONS:
        members = [item for item in baseline if item.setup_identity in condition_ids[condition_id]]
        others = set().union(*(condition_ids[index] for index in condition_ids if index != condition_id))
        unique = [item for item in members if item.setup_identity not in others]
        realized_n = sum(item.r_multiple is not None for item in members)
        if realized_n != EXPECTED_CONDITION_REALIZED[condition_id]:
            raise ValueError(f"frozen condition {condition_id} realized count changed: {realized_n}")
        conditions.append(ConditionAudit(
            condition_id=condition_id,
            condition_name=name,
            membership_n=len(members),
            realized_n=realized_n,
            unavailable_or_ambiguous_n=len(members) - realized_n,
            unique_membership_n=len(unique),
            unique_realized_n=sum(item.r_multiple is not None for item in unique),
            sessions=len({item.session_date for item in members}),
            months=len({item.session_date.strftime("%Y-%m") for item in members}),
            stage15_mean_r=EXPECTED_CONDITION_STAGE15[condition_id][2],
            stage15_fdr_q_value=EXPECTED_CONDITION_STAGE15[condition_id][3],
        ))
    overlap = tuple(
        ConditionOverlapCell(
            left_condition=left,
            right_condition=right,
            membership_overlap=len(condition_ids[left] & condition_ids[right]),
            realized_overlap=sum(
                item.r_multiple is not None
                for item in baseline
                if item.setup_identity in condition_ids[left] & condition_ids[right]
            ),
        )
        for left in range(1, 5) for right in range(1, 5)
    )
    variants = []
    for variant_id, exclusions in VARIANTS:
        removed_ids = set().union(*(condition_ids[index] for index in exclusions)) if exclusions else set()
        removed = [item for item in baseline if item.setup_identity in removed_ids]
        retained = [item for item in baseline if item.setup_identity not in removed_ids]
        metrics = (
            baseline_metrics
            if variant_id == "BASE_SHORT_CONTROL"
            else _metrics(retained, baseline, variant_id)
        )
        delta_low, delta_center, delta_high = _paired_bootstrap_delta(
            baseline, {item.setup_identity for item in retained}, variant_id
        )
        removal = RemovalAudit(
            variant_id=variant_id,
            condition_ids=exclusions,
            unique_membership_removed=len(removed),
            realized_removed=sum(item.r_multiple is not None for item in removed),
            unavailable_or_ambiguous_removed=sum(item.r_multiple is None for item in removed),
            sessions_affected=len({item.session_date for item in removed}),
            months_affected=len({item.session_date.strftime("%Y-%m") for item in removed}),
        )
        month_concentration = (
            metrics.realized_retained == 0
            or sum(item.trades > 0 for item in metrics.monthly) < 4
            or max((item.trades for item in metrics.monthly), default=0) * 2 > metrics.realized_retained
        )
        heavy_month_reduction = any(
            item.baseline_trades >= 5
            and item.retained_percentage is not None
            and item.retained_percentage < Decimal("0.50")
            for item in metrics.monthly
        )
        retains = metrics.realized_retained * 10 >= EXPECTED_BASELINE["realized"] * 7
        sessions_pass = metrics.sessions >= 80
        pre = next(item for item in metrics.periods if item.period == "PRE_DEVELOPMENT")
        development = next(item for item in metrics.periods if item.period == "DEVELOPMENT")
        pre_improves = pre.mean_r_delta is not None and pre.mean_r_delta > 0
        development_improves = development.mean_r_delta is not None and development.mean_r_delta > 0
        mean_delta = metrics.mean_r - baseline_metrics.mean_r if metrics.mean_r is not None and baseline_metrics.mean_r is not None else None
        median_delta = metrics.median_r - baseline_metrics.median_r if metrics.median_r is not None and baseline_metrics.median_r is not None else None
        pf_delta = metrics.profit_factor - baseline_metrics.profit_factor if metrics.profit_factor is not None and baseline_metrics.profit_factor is not None else None
        lomo_delta = metrics.leave_one_month_out_min_mean_r - baseline_metrics.leave_one_month_out_min_mean_r if metrics.leave_one_month_out_min_mean_r is not None and baseline_metrics.leave_one_month_out_min_mean_r is not None else None
        minimum_gates = retains and sessions_pass and not month_concentration and not heavy_month_reduction
        stability = (
            mean_delta is not None and mean_delta > 0
            and median_delta is not None and median_delta >= Decimal("-0.05")
            and pf_delta is not None and pf_delta > 0
            and lomo_delta is not None and lomo_delta > 0
            and delta_center is not None and delta_center > 0
            and metrics.negative_months <= baseline_metrics.negative_months + 1
            and metrics.positive_months >= baseline_metrics.positive_months - 1
            and pre_improves and development_improves
        )
        if variant_id == "BASE_SHORT_CONTROL":
            classification = ExclusionClassification.NO_IMPROVEMENT
        elif not minimum_gates:
            classification = ExclusionClassification.INSUFFICIENT_EVIDENCE
        elif stability:
            classification = ExclusionClassification.RESEARCH_EXCLUSION_CANDIDATE
        elif mean_delta is not None and mean_delta > 0 and pf_delta is not None and pf_delta > 0:
            classification = ExclusionClassification.DESCRIPTIVELY_IMPROVED
        else:
            classification = ExclusionClassification.NO_IMPROVEMENT
        room_diagnostic = _room_diagnostic(variant_id, exclusions, removed, retained)
        if (
            classification is ExclusionClassification.RESEARCH_EXCLUSION_CANDIDATE
            and room_diagnostic is not None
            and room_diagnostic.classification is RoomDiagnosticClassification.EXIT_GEOMETRY_DEPENDENT
        ):
            classification = ExclusionClassification.DESCRIPTIVELY_IMPROVED
        variants.append(ExclusionVariantResult(
            variant_id=variant_id,
            condition_ids=exclusions,
            removal=removal,
            metrics=metrics,
            mean_r_delta=mean_delta,
            median_r_delta=median_delta,
            profit_factor_delta=pf_delta,
            lomo_min_delta=lomo_delta,
            bootstrap_delta_low=delta_low,
            bootstrap_delta_median=delta_center,
            bootstrap_delta_high=delta_high,
            retains_70_percent_realized=retains,
            represents_80_sessions=sessions_pass,
            month_concentration_pass=not month_concentration,
            no_heavily_reduced_month=not heavy_month_reduction,
            pre_development_improves=pre_improves,
            development_improves=development_improves,
            classification=classification,
            room_diagnostic=room_diagnostic,
        ))
    return ExclusionValidationReport(
        start_date=stage15.start_date,
        end_date=stage15.end_date,
        baseline=baseline_metrics,
        conditions=tuple(conditions),
        overlap_matrix=overlap,
        variants=tuple(variants),
        source_stage15_report_hash=source_stage15_report_hash,
    )
