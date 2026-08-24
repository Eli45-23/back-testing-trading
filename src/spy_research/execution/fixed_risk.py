"""Frozen Stage 13.1 stop, target, and population definitions."""

from __future__ import annotations

from spy_research.execution.models import (
    AtrStopModel,
    ExecutableTradeSetup,
    FixedRiskVariant,
    RiskTargetModel,
    StrategyPopulation,
)
from spy_research.strategy.models import SetupDirection


STOP_MULTIPLIERS = {item: item.multiplier for item in AtrStopModel}
TARGET_MULTIPLES = {item: item.multiple for item in RiskTargetModel}


def fixed_risk_variants() -> tuple[FixedRiskVariant, ...]:
    """Return the exact stop-major, target-minor Cartesian product."""

    return tuple(
        FixedRiskVariant(
            stop_model=stop,
            stop_multiplier=STOP_MULTIPLIERS[stop],
            target_model=target,
            target_r=TARGET_MULTIPLES[target],
        )
        for stop in AtrStopModel
        for target in RiskTargetModel
    )


def strategy_populations(
    setup: ExecutableTradeSetup,
) -> tuple[StrategyPopulation, ...]:
    """Apply only the accepted BASE_ALL and direction-only BASE_SHORT membership."""

    populations = [StrategyPopulation.BASE_ALL]
    if setup.direction is SetupDirection.SHORT:
        populations.append(StrategyPopulation.BASE_SHORT)
    return tuple(populations)
