"""Deterministic, offline realized-trade simulation research."""

from spy_research.execution.fixed_risk import (
    STOP_MULTIPLIERS,
    TARGET_MULTIPLES,
    fixed_risk_variants,
    strategy_populations,
)
from spy_research.execution.models import (
    AmbiguityMetadata,
    AtrStopModel,
    DirectionTradeStatistics,
    ExecutableTradeSetup,
    ExecutionInputError,
    FixedRiskSimulationReport,
    FixedRiskTradeStatistics,
    FixedRiskVariant,
    MonthlyTradeStatistics,
    PopulationReconciliation,
    RealizedTradePath,
    RiskTargetModel,
    StrategyPopulation,
    TradeExitReason,
    TradeSimulationStatus,
    fixed_risk_simulation_hash,
)
from spy_research.execution.service import FixedRiskSimulationService
from spy_research.execution.simulator import simulate_fixed_risk_trade
from spy_research.execution.statistics import (
    calculate_fixed_risk_report,
    summarize_trade_variant,
)

__all__ = [
    "STOP_MULTIPLIERS",
    "TARGET_MULTIPLES",
    "AmbiguityMetadata",
    "AtrStopModel",
    "DirectionTradeStatistics",
    "ExecutableTradeSetup",
    "ExecutionInputError",
    "FixedRiskSimulationReport",
    "FixedRiskSimulationService",
    "FixedRiskTradeStatistics",
    "FixedRiskVariant",
    "MonthlyTradeStatistics",
    "PopulationReconciliation",
    "RealizedTradePath",
    "RiskTargetModel",
    "StrategyPopulation",
    "TradeExitReason",
    "TradeSimulationStatus",
    "calculate_fixed_risk_report",
    "fixed_risk_simulation_hash",
    "fixed_risk_variants",
    "simulate_fixed_risk_trade",
    "strategy_populations",
    "summarize_trade_variant",
]
