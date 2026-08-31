"""Predeclared Stage 15 statistics over frozen BASE_SHORT observations."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, localcontext
from hashlib import sha256
from math import erfc, sqrt
from random import Random
from statistics import median

from spy_research.attribution.models import (
    AttributionClassification,
    AttributionGroup,
    AttributionObservation,
    AttributionReport,
    MonthlyAttribution,
    MultipleTestingSummary,
)


BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 150_014
FDR_LEVEL = Decimal("0.10")
ALLOWED_INTERACTIONS = (
    "LEVEL_TYPE×ROOM_ATR",
    "LEVEL_TYPE×TIME_OF_DAY",
    "MARKET_STRUCTURE×ROOM_ATR",
    "VWAP_ALIGNMENT×ROOM_ATR",
    "EMA_ALIGNMENT×MARKET_STRUCTURE",
    "BREAK_QUALITY×CONFIRMATION_QUALITY",
)


def _ratio(part: int, whole: int) -> Decimal | None:
    return Decimal(part) / Decimal(whole) if whole else None


def _mean(values: list[Decimal]) -> Decimal | None:
    return sum(values, Decimal(0)) / Decimal(len(values)) if values else None


def _sample_std(values: list[Decimal]) -> Decimal | None:
    if len(values) < 2:
        return None
    mean = _mean(values)
    assert mean is not None
    with localcontext() as context:
        context.prec = 40
        return (sum((item - mean) ** 2 for item in values) / Decimal(len(values) - 1)).sqrt()


def _percentile(values: list[Decimal], fraction: Decimal) -> Decimal | None:
    if not values:
        return None
    ordered = sorted(values)
    rank = fraction * Decimal(len(ordered) - 1)
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - Decimal(lower)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * weight


def _bootstrap_ci(observations: list[AttributionObservation], salt: str) -> tuple[Decimal | None, Decimal | None]:
    realized = [item for item in observations if item.r_multiple is not None]
    by_session: dict[object, list[Decimal]] = defaultdict(list)
    for item in realized:
        assert item.r_multiple is not None
        by_session[item.session_date].append(item.r_multiple)
    sessions = sorted(by_session)
    if not sessions:
        return None, None
    seed = BOOTSTRAP_SEED + int(sha256(salt.encode()).hexdigest()[:8], 16)
    rng = Random(seed)
    means: list[Decimal] = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        values: list[Decimal] = []
        for _ in sessions:
            values.extend(by_session[rng.choice(sessions)])
        mean = _mean(values)
        assert mean is not None
        means.append(mean)
    return _percentile(means, Decimal("0.025")), _percentile(means, Decimal("0.975"))


def _p_value(group_values: list[Decimal], complement_values: list[Decimal]) -> Decimal | None:
    if len(group_values) < 2 or len(complement_values) < 2:
        return None
    group_mean = _mean(group_values)
    complement_mean = _mean(complement_values)
    group_std = _sample_std(group_values)
    complement_std = _sample_std(complement_values)
    assert group_mean is not None and complement_mean is not None
    assert group_std is not None and complement_std is not None
    variance = group_std ** 2 / Decimal(len(group_values)) + complement_std ** 2 / Decimal(len(complement_values))
    if variance == 0:
        return Decimal(1) if group_mean == complement_mean else Decimal(0)
    z = float(abs(group_mean - complement_mean) / variance.sqrt())
    return Decimal(str(erfc(z / sqrt(2))))


def _monthly(realized: list[AttributionObservation]) -> tuple[MonthlyAttribution, ...]:
    by_month: dict[str, list[Decimal]] = defaultdict(list)
    for item in realized:
        assert item.r_multiple is not None
        by_month[item.session_date.strftime("%Y-%m")].append(item.r_multiple)
    rows = []
    for month in (f"2026-{number:02d}" for number in range(1, 9)):
        values = by_month.get(month, [])
        rows.append(MonthlyAttribution(month=month, trades=len(values), mean_r=_mean(values), total_r=sum(values, Decimal(0))))
    return tuple(rows)


def _summarize(
    observations: list[AttributionObservation],
    *,
    factor: str,
    state: str,
    baseline_mean: Decimal | None,
    baseline_values: list[Decimal],
    baseline_observations: list[AttributionObservation],
) -> AttributionGroup:
    realized = [item for item in observations if item.r_multiple is not None]
    values = [item.r_multiple for item in realized if item.r_multiple is not None]
    positive = sum((value for value in values if value > 0), Decimal(0))
    negative = abs(sum((value for value in values if value < 0), Decimal(0)))
    months = _monthly(realized)
    represented = [item for item in months if item.trades]
    positive_months = sum(item.total_r > 0 for item in represented)
    negative_months = sum(item.total_r < 0 for item in represented)
    total = sum(values, Decimal(0))
    lomo = [
        (total - item.total_r) / Decimal(len(values) - item.trades)
        for item in represented
        if len(values) > item.trades
    ]
    concentration = bool(values) and (
        len(represented) < 4 or max(item.trades for item in represented) * 2 > len(values)
    )
    low, high = _bootstrap_ci(observations, f"{factor}|{state}")
    group_ids = {item.setup_identity for item in realized}
    complement = [
        item.r_multiple
        for item in baseline_observations
        if item.setup_identity not in group_ids and item.r_multiple is not None
    ]
    mean = _mean(values)
    return AttributionGroup(
        factor=factor,
        state=state,
        population_n=len(observations),
        trades=len(values),
        unavailable_or_ambiguous=len(observations) - len(values),
        sessions=len({item.session_date for item in realized}),
        win_rate=_ratio(sum(value > 0 for value in values), len(values)),
        mean_r=mean,
        median_r=Decimal(median(values)) if values else None,
        profit_factor=(positive / negative if negative else None),
        standard_deviation_r=_sample_std(values),
        target_hit_rate=_ratio(sum(item.exit_reason == "NEXT_OBJECTIVE_LEVEL" for item in realized), len(values)),
        stop_hit_rate=_ratio(sum(item.exit_reason == "STOP" for item in realized), len(values)),
        eod_exit_rate=_ratio(sum(item.exit_reason == "EOD_CLOSE" for item in realized), len(values)),
        median_mfe=Decimal(median([item.mfe for item in realized if item.mfe is not None])) if any(item.mfe is not None for item in realized) else None,
        median_mae=Decimal(median([item.mae for item in realized if item.mae is not None])) if any(item.mae is not None for item in realized) else None,
        monthly_performance=months,
        positive_months=positive_months,
        negative_months=negative_months,
        leave_one_month_out_min_mean_r=min(lomo) if lomo else None,
        bootstrap_mean_r_low=low,
        bootstrap_mean_r_high=high,
        mean_r_delta_from_baseline=(mean - baseline_mean if mean is not None and baseline_mean is not None else None),
        raw_p_value=(None if factor == "BASELINE" else _p_value(values, complement)),
        fdr_q_value=None,
        fewer_than_30_trades=len(values) < 30,
        fewer_than_10_sessions=len({item.session_date for item in realized}) < 10,
        month_concentration=concentration,
        classification=AttributionClassification.INSUFFICIENT_EVIDENCE,
    )


def _apply_bh(groups: list[AttributionGroup]) -> tuple[list[AttributionGroup], MultipleTestingSummary]:
    tested = [(index, item.raw_p_value) for index, item in enumerate(groups) if item.raw_p_value is not None]
    ordered = sorted(tested, key=lambda pair: pair[1])
    q_values: dict[int, Decimal] = {}
    running = Decimal(1)
    count = len(ordered)
    for rank_index in range(count - 1, -1, -1):
        index, p_value = ordered[rank_index]
        assert p_value is not None
        rank = rank_index + 1
        running = min(running, p_value * Decimal(count) / Decimal(rank))
        q_values[index] = min(Decimal(1), running)
    updated = []
    for index, item in enumerate(groups):
        q = q_values.get(index)
        sparse = item.fewer_than_30_trades or item.fewer_than_10_sessions or item.month_concentration
        ci_excludes_zero = (
            item.bootstrap_mean_r_low is not None
            and item.bootstrap_mean_r_high is not None
            and (
                item.bootstrap_mean_r_low > 0
                or item.bootstrap_mean_r_high < 0
            )
        )
        if sparse:
            classification = AttributionClassification.INSUFFICIENT_EVIDENCE
        elif q is not None and q <= FDR_LEVEL and ci_excludes_zero:
            classification = AttributionClassification.RESEARCH_CANDIDATE
        elif item.raw_p_value is not None and item.raw_p_value <= FDR_LEVEL:
            classification = AttributionClassification.DESCRIPTIVELY_INTERESTING
        else:
            classification = AttributionClassification.INSUFFICIENT_EVIDENCE
        updated.append(item.model_copy(update={"fdr_q_value": q, "classification": classification}))
    family = "PREDECLARED_INTERACTION" if groups and "×" in groups[0].factor else "SINGLE_FACTOR"
    summary = MultipleTestingSummary(
        family=family,
        hypotheses=count,
        raw_p_le_0_10=sum(p is not None and p <= FDR_LEVEL for _, p in tested),
        fdr_q_le_0_10=sum(q <= FDR_LEVEL for q in q_values.values()),
    )
    return updated, summary


def analyze_base_short_attribution(
    observations: tuple[AttributionObservation, ...],
    *,
    start_date,
    end_date,
    fixed_factor_states: tuple[tuple[str, tuple[str, ...]], ...],
    source_exit_hash: str,
    source_stage14_hash: str,
) -> AttributionReport:
    """Analyze only predeclared factors and interactions; never derive thresholds."""
    baseline_observations = list(observations)
    baseline_values = [item.r_multiple for item in observations if item.r_multiple is not None]
    baseline_mean = _mean(baseline_values)
    baseline = _summarize(list(observations), factor="BASELINE", state="BASE_SHORT_ATR_1_00", baseline_mean=baseline_mean, baseline_values=baseline_values, baseline_observations=baseline_observations)
    baseline = baseline.model_copy(update={"classification": AttributionClassification.INSUFFICIENT_EVIDENCE})

    single: list[AttributionGroup] = []
    for factor, states in fixed_factor_states:
        for state in states:
            members = [item for item in observations if item.factor(factor) == state]
            single.append(_summarize(members, factor=factor, state=state, baseline_mean=baseline_mean, baseline_values=baseline_values, baseline_observations=baseline_observations))

    interactions: list[AttributionGroup] = []
    for name in ALLOWED_INTERACTIONS:
        left, right = name.split("×")
        left_states = dict(fixed_factor_states)[left]
        right_states = dict(fixed_factor_states)[right]
        for left_state in left_states:
            for right_state in right_states:
                members = [
                    item for item in observations
                    if item.factor(left) == left_state and item.factor(right) == right_state
                ]
                interactions.append(_summarize(members, factor=name, state=f"{left_state}×{right_state}", baseline_mean=baseline_mean, baseline_values=baseline_values, baseline_observations=baseline_observations))

    single, single_testing = _apply_bh(single)
    interactions, interaction_testing = _apply_bh(interactions)
    return AttributionReport(
        start_date=start_date,
        end_date=end_date,
        observation_count=len(observations),
        baseline=baseline,
        single_factor_groups=tuple(single),
        interaction_groups=tuple(interactions),
        multiple_testing=(single_testing, interaction_testing),
        fixed_factor_states=fixed_factor_states,
        allowed_interactions=ALLOWED_INTERACTIONS,
        source_exit_hash=source_exit_hash,
        source_stage14_hash=source_stage14_hash,
    )
