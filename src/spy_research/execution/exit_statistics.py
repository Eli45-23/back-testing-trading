"""Descriptive statistics and session bootstrap for Stage 13.2 exits."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, localcontext
from hashlib import sha256

import numpy as np

from spy_research.execution.exit_models import (
    ExitBootstrapInterval,
    ExitBootstrapUncertainty,
    ExitFamily,
    ExitModelExitReason,
    ExitModelStatus,
    ExitModelTradePath,
    ExitModelVariant,
    ExitMonthlyStatistics,
    ExitPartitionStatistics,
    ExitSliceStatistics,
    ExitVariantStatistics,
    LeaveOneMonthOutR,
)
from spy_research.execution.models import (
    AtrStopModel,
    RealizedTradePath,
    RiskTargetModel,
    StrategyPopulation,
    TradeExitReason,
    TradeSimulationStatus,
)
from spy_research.indicators.ema import EMA_CONTEXT
from spy_research.interactions import LevelType
from spy_research.research_stats import summarize_distribution
from spy_research.strategy.models import SetupDirection


BOOTSTRAP_SEED = 12022026
BOOTSTRAP_RESAMPLES = 10_000
DEVELOPMENT_START = date(2026, 8, 3)


@dataclass(frozen=True)
class _TradeView:
    setup_identity: str
    session_date: date
    direction: SetupDirection
    level_type: LevelType
    population: StrategyPopulation
    variant_id: str
    atr_eligible: bool
    context_eligible: bool
    status: str
    reason: ExitModelExitReason
    r_multiple: Decimal | None
    price_pnl: Decimal | None
    minutes: int | None


def _control_id(stop: AtrStopModel, target: RiskTargetModel) -> str:
    return f"{ExitFamily.FIXED_R_CONTROL.value}:{stop.value}:{target.value}"


def _control_view(item: RealizedTradePath) -> _TradeView:
    status = (
        "UNAVAILABLE"
        if item.exit_status is TradeSimulationStatus.TRADE_UNAVAILABLE_ATR
        else "AMBIGUOUS"
        if item.exit_status is TradeSimulationStatus.AMBIGUOUS_BOTH_TOUCHED
        else "REALIZED"
    )
    reason = (
        ExitModelExitReason.UNAVAILABLE_ATR
        if status == "UNAVAILABLE"
        else ExitModelExitReason.AMBIGUOUS_BOTH_TOUCHED
        if status == "AMBIGUOUS"
        else ExitModelExitReason.STOP
        if item.exit_reason is TradeExitReason.STOP
        else ExitModelExitReason.FIXED_R_TARGET
        if item.exit_reason is TradeExitReason.TARGET
        else ExitModelExitReason.EOD_CLOSE
    )
    return _TradeView(
        setup_identity=item.setup_identity,
        session_date=item.session_date,
        direction=item.direction,
        level_type=item.level_type,
        population=item.strategy_population,
        variant_id=_control_id(item.stop_model, item.target_model),
        atr_eligible=status != "UNAVAILABLE",
        context_eligible=status != "UNAVAILABLE",
        status=status,
        reason=reason,
        r_multiple=item.r_multiple,
        price_pnl=item.price_pnl,
        minutes=item.minutes_in_trade,
    )


def _new_view(item: ExitModelTradePath) -> _TradeView:
    status = (
        "REALIZED"
        if item.status is ExitModelStatus.REALIZED
        else "AMBIGUOUS"
        if item.status is ExitModelStatus.AMBIGUOUS_BOTH_TOUCHED
        else "UNAVAILABLE"
    )
    return _TradeView(
        setup_identity=item.setup_identity,
        session_date=item.session_date,
        direction=item.direction,
        level_type=item.level_type,
        population=item.strategy_population,
        variant_id=item.variant.variant_id,
        atr_eligible=item.atr_eligible,
        context_eligible=item.target_context_eligible,
        status=status,
        reason=item.exit_reason,
        r_multiple=item.r_multiple,
        price_pnl=item.price_pnl,
        minutes=item.minutes_in_trade,
    )


def trade_views(
    controls: Sequence[RealizedTradePath],
    new_trades: Sequence[ExitModelTradePath],
) -> tuple[_TradeView, ...]:
    return tuple(_control_view(item) for item in controls) + tuple(
        _new_view(item) for item in new_trades
    )


def _percentage(numerator: int, denominator: int) -> Decimal | None:
    if not denominator:
        return None
    with localcontext(EMA_CONTEXT):
        return Decimal(numerator) * Decimal(100) / Decimal(denominator)


def _standard_deviation(values: Sequence[Decimal]) -> Decimal | None:
    if not values:
        return None
    with localcontext(EMA_CONTEXT):
        mean = sum(values, Decimal(0)) / Decimal(len(values))
        variance = sum((item - mean) ** 2 for item in values) / Decimal(len(values))
        return variance.sqrt()


def _summary(name: str, values: Sequence[_TradeView]) -> ExitSliceStatistics:
    realized = tuple(item for item in values if item.status == "REALIZED")
    return ExitSliceStatistics(
        name=name,
        trade_n=len(realized),
        r_multiple=summarize_distribution(
            tuple(item.r_multiple for item in realized if item.r_multiple is not None)
        ),
    )


def _partition(
    name: str,
    values: Sequence[_TradeView],
) -> ExitPartitionStatistics:
    realized = tuple(item for item in values if item.status == "REALIZED")
    distribution = summarize_distribution(
        tuple(item.r_multiple for item in realized if item.r_multiple is not None)
    )
    return ExitPartitionStatistics(
        partition=name,
        trade_n=len(realized),
        mean_r=distribution.mean,
        median_r=distribution.median,
    )


def summarize_exit_variant(
    views: Sequence[_TradeView],
    *,
    population: StrategyPopulation,
    variant: ExitModelVariant,
) -> ExitVariantStatistics:
    selected = tuple(
        item
        for item in views
        if item.population is population and item.variant_id == variant.variant_id
    )
    if len({item.setup_identity for item in selected}) != len(selected):
        raise ValueError("variant membership contains duplicate setup identities")
    realized = tuple(item for item in selected if item.status == "REALIZED")
    ambiguous = tuple(item for item in selected if item.status == "AMBIGUOUS")
    unavailable = tuple(item for item in selected if item.status == "UNAVAILABLE")
    r_values = tuple(
        item.r_multiple for item in realized if item.r_multiple is not None
    )
    if len(r_values) != len(realized):
        raise ValueError("realized comparison path lacks R multiple")
    months = []
    for month in range(1, 9):
        scoped = tuple(item for item in realized if item.session_date.month == month)
        distribution = summarize_distribution(
            tuple(item.r_multiple for item in scoped if item.r_multiple is not None)
        )
        months.append(
            ExitMonthlyStatistics(
                month=f"2026-{month:02d}",
                trade_n=len(scoped),
                mean_r=distribution.mean,
                median_r=distribution.median,
                positive_n=sum(item.r_multiple > 0 for item in scoped),
                negative_n=sum(item.r_multiple < 0 for item in scoped),
                zero_n=sum(item.r_multiple == 0 for item in scoped),
            )
        )
    directions = (
        tuple(
            _summary(
                direction.value,
                tuple(item for item in selected if item.direction is direction),
            )
            for direction in SetupDirection
        )
        if population is StrategyPopulation.BASE_ALL
        else ()
    )
    levels = Counter(item.level_type for item in realized)
    partitions = (
        _partition("EXPANDED", selected),
        _partition(
            "JANUARY_JULY",
            tuple(item for item in selected if item.session_date < DEVELOPMENT_START),
        ),
        _partition(
            "AUGUST_DEVELOPMENT",
            tuple(item for item in selected if item.session_date >= DEVELOPMENT_START),
        ),
    )
    leave_one_out = []
    for month in range(1, 9):
        scoped = tuple(item for item in realized if item.session_date.month != month)
        distribution = summarize_distribution(
            tuple(item.r_multiple for item in scoped if item.r_multiple is not None)
        )
        leave_one_out.append(
            LeaveOneMonthOutR(
                excluded_month=f"2026-{month:02d}",
                trade_n=len(scoped),
                mean_r=distribution.mean,
                median_r=distribution.median,
            )
        )
    monthly_medians = tuple(
        item.median_r for item in months if item.median_r is not None
    )
    reasons = Counter(item.reason for item in realized)
    cross_reasons = (
        ExitModelExitReason.OPPOSITE_EMA9_20_CROSS,
        ExitModelExitReason.OPPOSITE_EMA9_VWAP_CROSS,
        ExitModelExitReason.OPPOSITE_EMA20_VWAP_CROSS,
    )
    time_reasons = (
        ExitModelExitReason.TIME_15M,
        ExitModelExitReason.TIME_30M,
        ExitModelExitReason.TIME_60M,
    )
    r_distribution = summarize_distribution(r_values)
    minutes = tuple(
        Decimal(item.minutes) for item in realized if item.minutes is not None
    )
    return ExitVariantStatistics(
        strategy_population=population,
        variant=variant,
        membership_n=len(selected),
        atr_eligible_n=sum(item.atr_eligible for item in selected),
        target_context_eligible_n=sum(item.context_eligible for item in selected),
        realized_n=len(realized),
        unavailable_n=len(unavailable),
        ambiguous_n=len(ambiguous),
        stop_exit_n=reasons[ExitModelExitReason.STOP],
        target_exit_n=(
            reasons[ExitModelExitReason.FIXED_R_TARGET]
            + reasons[ExitModelExitReason.NEXT_OBJECTIVE_LEVEL]
        ),
        cross_exit_n=sum(reasons[item] for item in cross_reasons),
        time_exit_n=sum(reasons[item] for item in time_reasons),
        eod_exit_n=reasons[ExitModelExitReason.EOD_CLOSE],
        r_multiple=r_distribution,
        r_standard_deviation=_standard_deviation(r_values),
        positive_r_n=sum(item > 0 for item in r_values),
        zero_r_n=sum(item == 0 for item in r_values),
        negative_r_n=sum(item < 0 for item in r_values),
        win_rate_percentage=_percentage(
            sum(item > 0 for item in r_values), len(realized)
        ),
        loss_rate_percentage=_percentage(
            sum(item < 0 for item in r_values), len(realized)
        ),
        holding_minutes=summarize_distribution(minutes),
        monthly=tuple(months),
        positive_month_n=sum(item > 0 for item in monthly_medians),
        negative_month_n=sum(item < 0 for item in monthly_medians),
        session_count=len({item.session_date for item in realized}),
        direction_composition=directions,
        level_composition=tuple(
            (level, levels[level]) for level in LevelType if levels[level]
        ),
        partitions=partitions,
        leave_one_month_out=tuple(leave_one_out),
    )


def _linear_percentile(values: Sequence[Decimal], q: Decimal) -> Decimal:
    ordered = tuple(sorted(values))
    if not ordered:
        raise ValueError("bootstrap percentile requires values")
    with localcontext(EMA_CONTEXT):
        rank = Decimal(len(ordered) - 1) * q
        lower = int(rank)
        upper = min(lower + 1, len(ordered) - 1)
        fraction = rank - Decimal(lower)
        return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def bootstrap_exit_variant(
    views: Sequence[_TradeView],
    *,
    population: StrategyPopulation,
    variant: ExitModelVariant,
    seed: int = BOOTSTRAP_SEED,
    resamples: int = BOOTSTRAP_RESAMPLES,
) -> ExitBootstrapUncertainty:
    """Session-cluster R using a deterministically derived seed and 10,000 draws."""

    if resamples != BOOTSTRAP_RESAMPLES:
        raise ValueError("Stage 13.2 requires exactly 10,000 bootstrap resamples")
    selected = tuple(
        item
        for item in views
        if item.population is population and item.variant_id == variant.variant_id
    )
    sessions = tuple(sorted({item.session_date for item in selected}))
    realized = tuple(item for item in selected if item.status == "REALIZED")
    if not sessions or not realized:
        raise ValueError("bootstrap requires membership sessions and realized R")
    by_session: dict[date, list[Decimal]] = defaultdict(list)
    for item in realized:
        assert item.r_multiple is not None
        by_session[item.session_date].append(item.r_multiple)
    derived_seed = int.from_bytes(
        sha256(
            f"{seed}:{population.value}:{variant.variant_id}".encode()
        ).digest()[:8],
        "big",
    )
    rng = np.random.default_rng(derived_seed)
    draws = rng.integers(
        0,
        len(sessions),
        size=(resamples, len(sessions)),
        dtype=np.int16,
    )
    counts = np.zeros((resamples, len(sessions)), dtype=np.int16)
    rows = np.repeat(np.arange(resamples, dtype=np.int32), len(sessions))
    np.add.at(counts, (rows, draws.reshape(-1)), 1)
    session_n = np.array([len(by_session[item]) for item in sessions], dtype=np.int32)
    session_sum = np.array(
        [float(sum(by_session[item], Decimal(0))) for item in sessions],
        dtype=np.float64,
    )
    sample_n = counts @ session_n
    if np.any(sample_n == 0):
        raise ValueError("bootstrap resample contains no realized trades")
    mean_samples = (counts @ session_sum) / sample_n

    unique_values = tuple(
        sorted({value for values in by_session.values() for value in values})
    )
    value_index = {value: index for index, value in enumerate(unique_values)}
    session_value_counts = np.zeros(
        (len(sessions), len(unique_values)), dtype=np.int16
    )
    for session_index, session in enumerate(sessions):
        for value, count in Counter(by_session[session]).items():
            session_value_counts[session_index, value_index[value]] = count
    value_counts = counts @ session_value_counts
    cumulative = np.cumsum(value_counts, axis=1)
    lower_rank = (sample_n - 1) // 2
    upper_rank = sample_n // 2
    lower_index = np.argmax(cumulative > lower_rank[:, None], axis=1)
    upper_index = np.argmax(cumulative > upper_rank[:, None], axis=1)
    float_values = np.array([float(item) for item in unique_values])
    median_samples = (float_values[lower_index] + float_values[upper_index]) / 2

    interval_rows = []
    for metric, samples in (
        ("MEAN_R", mean_samples),
        ("MEDIAN_R", median_samples),
    ):
        decimals = tuple(Decimal(repr(float(item))) for item in samples)
        interval_rows.append(
            ExitBootstrapInterval(
                metric=metric,
                p2_5=_linear_percentile(decimals, Decimal("0.025")),
                p50=_linear_percentile(decimals, Decimal("0.5")),
                p97_5=_linear_percentile(decimals, Decimal("0.975")),
            )
        )
    return ExitBootstrapUncertainty(
        strategy_population=population,
        variant_id=variant.variant_id,
        realized_n=len(realized),
        session_cluster_count=len(sessions),
        seed=seed,
        resamples=resamples,
        intervals=tuple(interval_rows),
    )
