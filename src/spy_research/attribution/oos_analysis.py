"""Pure analysis for the frozen Stage 15.2 out-of-sample candidates."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal
from hashlib import sha256
from statistics import median

from spy_research.attribution.analysis import _mean, _percentile, _sample_std
from spy_research.attribution.exclusion_analysis import (
    _bootstrap,
    _matches,
    _paired_bootstrap_delta,
    _profit_factor,
    _ratio,
    _room_diagnostic,
)
from spy_research.attribution.exclusion_models import (
    ExclusionMetrics,
    ExclusionMonthlyRow,
    RemovalAudit,
    RoomDiagnosticClassification,
)
from spy_research.attribution.models import AttributionObservation
from spy_research.attribution.oos_models import (
    OOSCandidate,
    OOSCandidateResult,
    OOSClassification,
    OOSPeriodReport,
)


CANDIDATE_CONDITIONS = {
    OOSCandidate.BASE_SHORT_CONTROL: (),
    OOSCandidate.EXCLUDE_NEG_1: (1,),
    OOSCandidate.EXCLUDE_NEG_4: (4,),
    OOSCandidate.EXCLUDE_NEG_1_2: (1, 2),
    OOSCandidate.EXCLUDE_NEG_1_4: (1, 4),
    OOSCandidate.EXCLUDE_NEG_1_2_4: (1, 2, 4),
}
STAGE15_1_DELTAS = {
    OOSCandidate.BASE_SHORT_CONTROL: Decimal("0"),
    OOSCandidate.EXCLUDE_NEG_1: Decimal("0.04395443193730639106284599290"),
    OOSCandidate.EXCLUDE_NEG_4: Decimal("0.02790670000457614027530328881"),
    OOSCandidate.EXCLUDE_NEG_1_2: Decimal("0.08404647574057197604171729020"),
    OOSCandidate.EXCLUDE_NEG_1_4: Decimal("0.06410529459618821524353090223"),
    OOSCandidate.EXCLUDE_NEG_1_2_4: Decimal("0.09428528867399297109317302773"),
}
STAGE15_1_ROOM = {
    OOSCandidate.EXCLUDE_NEG_1: RoomDiagnosticClassification.MIXED,
    OOSCandidate.EXCLUDE_NEG_1_2: RoomDiagnosticClassification.MIXED,
    OOSCandidate.EXCLUDE_NEG_1_4: RoomDiagnosticClassification.ENTRY_BEHAVIOR_SUPPORTED,
    OOSCandidate.EXCLUDE_NEG_1_2_4: RoomDiagnosticClassification.MIXED,
}


def _metrics(
    observations: list[AttributionObservation],
    baseline: list[AttributionObservation],
    salt: str,
) -> ExclusionMetrics:
    realized = [item for item in observations if item.r_multiple is not None]
    values = [item.r_multiple for item in realized if item.r_multiple is not None]
    baseline_months: dict[str, int] = defaultdict(int)
    month_values: dict[str, list[Decimal]] = defaultdict(list)
    for item in baseline:
        if item.r_multiple is not None:
            baseline_months[item.session_date.strftime("%Y-%m")] += 1
    for item in realized:
        assert item.r_multiple is not None
        month_values[item.session_date.strftime("%Y-%m")].append(item.r_multiple)
    months = sorted(set(baseline_months) | set(month_values))
    monthly = tuple(
        ExclusionMonthlyRow(
            month=month,
            trades=len(month_values[month]),
            mean_r=_mean(month_values[month]),
            median_r=Decimal(median(month_values[month])) if month_values[month] else None,
            total_r=sum(month_values[month], Decimal(0)),
            baseline_trades=baseline_months[month],
            retained_percentage=_ratio(len(month_values[month]), baseline_months[month]),
        )
        for month in months
    )
    represented = [item for item in monthly if item.trades]
    total_r = sum(values, Decimal(0))
    lomo = [
        (total_r - item.total_r) / Decimal(len(values) - item.trades)
        for item in represented
        if len(values) > item.trades
    ]
    worst = min(represented, key=lambda item: item.mean_r) if represented else None
    low, center, high = _bootstrap(observations, salt)
    mfe = [item.mfe for item in realized if item.mfe is not None]
    mae = [item.mae for item in realized if item.mae is not None]
    return ExclusionMetrics(
        original_membership=len(baseline),
        retained_membership=len(observations),
        retained_percentage=Decimal(len(observations)) / Decimal(len(baseline)),
        realized_retained=len(realized),
        unavailable_or_ambiguous_retained=len(observations) - len(realized),
        sessions=len({item.session_date for item in realized}),
        win_rate=_ratio(sum(value > 0 for value in values), len(values)),
        mean_r=_mean(values),
        median_r=Decimal(median(values)) if values else None,
        standard_deviation_r=_sample_std(values),
        profit_factor=_profit_factor(values),
        target_hit_rate=_ratio(sum(item.exit_reason == "NEXT_OBJECTIVE_LEVEL" for item in realized), len(realized)),
        stop_hit_rate=_ratio(sum(item.exit_reason == "STOP" for item in realized), len(realized)),
        eod_exit_rate=_ratio(sum(item.exit_reason == "EOD_CLOSE" for item in realized), len(realized)),
        median_mfe=Decimal(median(mfe)) if mfe else None,
        median_mae=Decimal(median(mae)) if mae else None,
        fifth_percentile_r=_percentile(values, Decimal("0.05")),
        positive_months=sum(item.total_r > 0 for item in represented),
        negative_months=sum(item.total_r < 0 for item in represented),
        worst_month=worst.month if worst else None,
        worst_month_mean_r=worst.mean_r if worst else None,
        leave_one_month_out_min_mean_r=min(lomo) if lomo else None,
        bootstrap_mean_r_low=low,
        bootstrap_mean_r_median=center,
        bootstrap_mean_r_high=high,
        monthly=monthly,
        periods=(),
    )


def analyze_oos_period(
    observations: tuple[AttributionObservation, ...],
    *,
    period: str,
    start_date: date,
    end_date: date,
) -> OOSPeriodReport:
    baseline = list(observations)
    condition_ids = {
        condition: {item.setup_identity for item in baseline if _matches(item, condition)}
        for condition in range(1, 5)
    }
    baseline_metrics = _metrics(baseline, baseline, f"OOS|{period}|CONTROL")
    results = []
    for candidate in OOSCandidate:
        exclusions = CANDIDATE_CONDITIONS[candidate]
        removed_ids = set().union(*(condition_ids[item] for item in exclusions)) if exclusions else set()
        removed = [item for item in baseline if item.setup_identity in removed_ids]
        retained = [item for item in baseline if item.setup_identity not in removed_ids]
        metrics = baseline_metrics if not exclusions else _metrics(retained, baseline, f"OOS|{period}|{candidate.value}")
        retained_ids = {item.setup_identity for item in retained}
        delta_low, delta_center, delta_high = _paired_bootstrap_delta(
            baseline, retained_ids, f"OOS|{period}|{candidate.value}"
        )
        mean_delta = metrics.mean_r - baseline_metrics.mean_r if metrics.mean_r is not None and baseline_metrics.mean_r is not None else None
        pf_delta = metrics.profit_factor - baseline_metrics.profit_factor if metrics.profit_factor is not None and baseline_metrics.profit_factor is not None else None
        lomo_delta = metrics.leave_one_month_out_min_mean_r - baseline_metrics.leave_one_month_out_min_mean_r if metrics.leave_one_month_out_min_mean_r is not None and baseline_metrics.leave_one_month_out_min_mean_r is not None else None
        retains = metrics.realized_retained * 10 >= baseline_metrics.realized_retained * 7
        sessions_pass = metrics.sessions >= 80
        concentration = (
            sum(item.trades > 0 for item in metrics.monthly) < 4
            or max((item.trades for item in metrics.monthly), default=0) * 2 > metrics.realized_retained
        )
        heavy_reduction = any(
            item.baseline_trades >= 5
            and item.retained_percentage is not None
            and item.retained_percentage < Decimal("0.50")
            for item in metrics.monthly
        )
        pf_pass = pf_delta is not None and pf_delta >= 0
        lomo_pass = lomo_delta is not None and lomo_delta >= 0
        bootstrap_pass = delta_center is not None and delta_center > 0
        reference_delta = STAGE15_1_DELTAS[candidate]
        direction_agrees = candidate is OOSCandidate.BASE_SHORT_CONTROL or (
            mean_delta is not None and mean_delta > 0 and reference_delta > 0
        )
        room = _room_diagnostic(candidate.value, exclusions, removed, retained)
        reference_room = STAGE15_1_ROOM.get(candidate)
        room_replicated = None if reference_room is None else (
            room is not None and room.classification is reference_room
        )
        entry_supported = (
            candidate is not OOSCandidate.EXCLUDE_NEG_1_4
            or (room is not None and room.classification is RoomDiagnosticClassification.ENTRY_BEHAVIOR_SUPPORTED)
        )
        enough = retains and sessions_pass and not concentration and not heavy_reduction
        if candidate is OOSCandidate.BASE_SHORT_CONTROL:
            classification = OOSClassification.DESCRIPTIVELY_REPLICATED
        elif not enough:
            classification = OOSClassification.INSUFFICIENT_OOS_DATA
        elif mean_delta is None or mean_delta <= 0:
            classification = OOSClassification.FAILED_TO_REPLICATE
        elif all((pf_pass, lomo_pass, bootstrap_pass, direction_agrees, entry_supported)):
            classification = OOSClassification.OOS_REPLICATED_RESEARCH_CANDIDATE
        else:
            classification = OOSClassification.DESCRIPTIVELY_REPLICATED
        results.append(OOSCandidateResult(
            candidate=candidate,
            condition_ids=exclusions,
            removal=RemovalAudit(
                variant_id=candidate.value,
                condition_ids=exclusions,
                unique_membership_removed=len(removed),
                realized_removed=sum(item.r_multiple is not None for item in removed),
                unavailable_or_ambiguous_removed=sum(item.r_multiple is None for item in removed),
                sessions_affected=len({item.session_date for item in removed}),
                months_affected=len({item.session_date.strftime("%Y-%m") for item in removed}),
            ),
            metrics=metrics,
            mean_r_delta=mean_delta,
            profit_factor_delta=pf_delta,
            lomo_delta=lomo_delta,
            bootstrap_delta_low=delta_low,
            bootstrap_delta_median=delta_center,
            bootstrap_delta_high=delta_high,
            stage15_1_mean_r_delta=reference_delta,
            direction_agrees_with_stage15_1=direction_agrees,
            retains_70_percent_realized=retains,
            represents_80_sessions=sessions_pass,
            month_concentration_pass=not concentration,
            no_heavily_reduced_month=not heavy_reduction,
            profit_factor_not_deteriorated=pf_pass,
            lomo_not_materially_deteriorated=lomo_pass,
            bootstrap_shift_favorable=bootstrap_pass,
            room_diagnostic=room,
            stage15_1_room_classification=reference_room.value if reference_room else None,
            room_diagnosis_replicated=room_replicated,
            claimed_entry_quality_supported=entry_supported,
            classification=classification,
        ))
    digest = sha256("".join(item.model_dump_json() for item in observations).encode()).hexdigest()
    return OOSPeriodReport(
        period=period,
        start_date=start_date,
        end_date=end_date,
        baseline=baseline_metrics,
        candidates=tuple(results),
        observation_hash=digest,
    )
