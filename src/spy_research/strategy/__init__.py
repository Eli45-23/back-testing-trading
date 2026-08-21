"""Deterministic strategy-candidate layers built from frozen research objects."""

from spy_research.strategy.base_price_action import (
    BaseSetupInputError,
    interaction_identity,
    qualify_base_price_action_candidate,
)
from spy_research.strategy.base_price_action_service import BasePriceActionService
from spy_research.strategy.base_statistics import (
    BaseStatisticsInputError,
    BaseStrategyGroupDimension,
    BaseStrategyGroupStatistics,
    BaseStrategyHorizonStatistics,
    BaseStrategyStatistics,
    calculate_base_strategy_statistics,
    entry_time_bucket,
    summarize_base_outcome_group,
)
from spy_research.strategy.base_statistics_service import (
    BaseStrategyStatisticsService,
)
from spy_research.strategy.entry_reference import (
    SetupOutcomeInputError,
    select_entry_reference,
)
from spy_research.strategy.models import (
    BasePriceActionCandidate,
    BasePriceActionResult,
    BaseSetupStatus,
    ConfirmationType,
    EntryStatus,
    SetupEntryReference,
    SetupHorizonOutcome,
    SetupOutcome,
    SetupOutcomeResult,
    SetupDirection,
)
from spy_research.strategy.setup_outcome_service import SetupOutcomeService
from spy_research.strategy.setup_outcomes import calculate_setup_outcomes

__all__ = [
    "BasePriceActionCandidate",
    "BasePriceActionResult",
    "BasePriceActionService",
    "BaseSetupInputError",
    "BaseSetupStatus",
    "BaseStatisticsInputError",
    "BaseStrategyGroupDimension",
    "BaseStrategyGroupStatistics",
    "BaseStrategyHorizonStatistics",
    "BaseStrategyStatistics",
    "BaseStrategyStatisticsService",
    "ConfirmationType",
    "EntryStatus",
    "SetupEntryReference",
    "SetupHorizonOutcome",
    "SetupOutcome",
    "SetupOutcomeInputError",
    "SetupOutcomeResult",
    "SetupOutcomeService",
    "SetupDirection",
    "calculate_setup_outcomes",
    "calculate_base_strategy_statistics",
    "entry_time_bucket",
    "summarize_base_outcome_group",
    "interaction_identity",
    "qualify_base_price_action_candidate",
    "select_entry_reference",
]
