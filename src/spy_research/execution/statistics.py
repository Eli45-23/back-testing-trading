"""Descriptive statistics for frozen Stage 13.1 realized trade paths."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from datetime import date
from decimal import Decimal, localcontext

from spy_research.execution.models import (
    DirectionTradeStatistics,
    FixedRiskSimulationReport,
    FixedRiskTradeStatistics,
    FixedRiskVariant,
    MonthlyTradeStatistics,
    PopulationReconciliation,
    RealizedTradePath,
    StrategyPopulation,
    TradeExitReason,
    TradeSimulationStatus,
)
from spy_research.indicators.ema import EMA_CONTEXT
from spy_research.interactions import LevelType
from spy_research.research_stats import summarize_distribution
from spy_research.strategy.models import SetupDirection


def _percentage(numerator: int, denominator: int) -> Decimal | None:
    if not denominator:
        return None
    with localcontext(EMA_CONTEXT):
        return Decimal(numerator) * Decimal(100) / Decimal(denominator)


def _month_keys(start: date, end: date) -> tuple[tuple[int, int], ...]:
    keys = []
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        keys.append((year, month))
        month += 1
        if month == 13:
            year += 1
            month = 1
    return tuple(keys)


def summarize_trade_variant(
    trades: Sequence[RealizedTradePath],
    *,
    population: StrategyPopulation,
    variant: FixedRiskVariant,
    start: date,
    end: date,
) -> FixedRiskTradeStatistics:
    selected = tuple(
        item
        for item in trades
        if item.strategy_population is population
        and item.stop_model is variant.stop_model
        and item.target_model is variant.target_model
    )
    unavailable = tuple(
        item
        for item in selected
        if item.exit_status is TradeSimulationStatus.TRADE_UNAVAILABLE_ATR
    )
    executable = tuple(
        item
        for item in selected
        if item.exit_status is not TradeSimulationStatus.TRADE_UNAVAILABLE_ATR
    )
    ambiguous = tuple(
        item
        for item in executable
        if item.exit_status is TradeSimulationStatus.AMBIGUOUS_BOTH_TOUCHED
    )
    realized = tuple(
        item
        for item in executable
        if item.exit_status is TradeSimulationStatus.SIMULATED
    )
    r_values = tuple(item.r_multiple for item in realized)
    pnl_values = tuple(item.price_pnl for item in realized)
    minute_values = tuple(
        Decimal(item.minutes_in_trade)
        for item in realized
        if item.minutes_in_trade is not None
    )
    if any(item is None for item in r_values + pnl_values):
        raise ValueError("realized trades require P/L and R")
    r_typed = tuple(item for item in r_values if item is not None)
    pnl_typed = tuple(item for item in pnl_values if item is not None)
    months = tuple(
        MonthlyTradeStatistics(
            month=f"{year:04d}-{month:02d}",
            trade_n=len(
                scoped := tuple(
                    item
                    for item in realized
                    if (item.session_date.year, item.session_date.month) == (year, month)
                )
            ),
            median_r=summarize_distribution(
                tuple(item.r_multiple for item in scoped if item.r_multiple is not None)
            ).median,
        )
        for year, month in _month_keys(start, end)
    )
    directions = (
        tuple(
            DirectionTradeStatistics(
                direction=direction,
                trade_n=len(
                    scoped := tuple(
                        item for item in realized if item.direction is direction
                    )
                ),
                r_multiple=summarize_distribution(
                    tuple(item.r_multiple for item in scoped if item.r_multiple is not None)
                ),
                price_pnl=summarize_distribution(
                    tuple(item.price_pnl for item in scoped if item.price_pnl is not None)
                ),
            )
            for direction in SetupDirection
        )
        if population is StrategyPopulation.BASE_ALL
        else ()
    )
    levels = Counter(item.level_type for item in realized)
    return FixedRiskTradeStatistics(
        strategy_population=population,
        variant=variant,
        eligible_setup_n=len(selected),
        unavailable_atr_n=len(unavailable),
        executable_simulated_n=len(executable),
        realized_trade_n=len(realized),
        target_exit_n=sum(item.exit_reason is TradeExitReason.TARGET for item in realized),
        stop_exit_n=sum(item.exit_reason is TradeExitReason.STOP for item in realized),
        eod_exit_n=sum(item.exit_reason is TradeExitReason.EOD_CLOSE for item in realized),
        ambiguous_both_touched_n=len(ambiguous),
        r_multiple=summarize_distribution(r_typed),
        price_pnl=summarize_distribution(pnl_typed),
        positive_r_n=sum(item > 0 for item in r_typed),
        zero_r_n=sum(item == 0 for item in r_typed),
        negative_r_n=sum(item < 0 for item in r_typed),
        win_rate_percentage=_percentage(sum(item > 0 for item in r_typed), len(realized)),
        loss_rate_percentage=_percentage(sum(item < 0 for item in r_typed), len(realized)),
        holding_minutes=summarize_distribution(minute_values),
        monthly=months,
        direction_decomposition=directions,
        level_composition=tuple(
            (level, levels[level]) for level in LevelType if levels[level]
        ),
    )


def calculate_fixed_risk_report(
    trades: Sequence[RealizedTradePath],
    populations: Sequence[PopulationReconciliation],
    variants: Sequence[FixedRiskVariant],
    *,
    start: date,
    end: date,
) -> FixedRiskSimulationReport:
    """Aggregate primary performance only from definite realized exits."""

    ordered_trades = tuple(trades)
    ordered_variants = tuple(variants)
    statistics = tuple(
        summarize_trade_variant(
            ordered_trades,
            population=population,
            variant=variant,
            start=start,
            end=end,
        )
        for population in StrategyPopulation
        for variant in ordered_variants
    )
    return FixedRiskSimulationReport(
        start_date=start,
        end_date=end,
        populations=tuple(populations),
        variants=ordered_variants,
        trades=ordered_trades,
        statistics=statistics,
    )
