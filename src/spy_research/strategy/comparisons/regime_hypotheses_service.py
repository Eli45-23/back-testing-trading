"""Offline Stage 11.1 orchestration over accepted Stage 9/10 results."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Sequence

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.market import XNYSCalendar
from spy_research.strategy.base_price_action_service import BasePriceActionService
from spy_research.strategy.base_statistics import calculate_base_strategy_statistics
from spy_research.strategy.comparisons.combined_context_service import (
    CombinedContextMatrixService,
)
from spy_research.strategy.comparisons.market_condition_service import (
    MarketConditionFeatureService,
)
from spy_research.strategy.comparisons.regime_hypotheses import (
    FrozenQuartileBoundary,
    RegimeHypothesisComparisonResult,
    build_regime_hypothesis_annotations,
    calculate_regime_hypothesis_comparison,
)
from spy_research.strategy.setup_outcome_service import SetupOutcomeService


class RegimeHypothesisComparisonService:
    """Compare predeclared labels without changing any accepted source."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
        *,
        calendar: XNYSCalendar | None = None,
    ) -> None:
        self._config = config
        self._processed_store = processed_store
        self._raw_store = raw_store
        self._calendar = calendar or XNYSCalendar()

    def calculate(
        self,
        *,
        start: date,
        end: date,
        boundaries: Sequence[FrozenQuartileBoundary] | None = None,
    ) -> RegimeHypothesisComparisonResult:
        setup_result = BasePriceActionService(
            self._config,
            self._processed_store,
            self._raw_store,
            calendar=self._calendar,
        ).calculate(start=start, end=end)
        outcome_result = SetupOutcomeService(
            self._config,
            self._processed_store,
            self._raw_store,
            calendar=self._calendar,
        ).calculate(start=start, end=end)
        session_count = sum(
            self._calendar.session_for_date(
                start + timedelta(days=offset)
            ).is_trading_day
            for offset in range((end - start).days + 1)
        )
        base_statistics = calculate_base_strategy_statistics(
            setup_result,
            outcome_result,
            development_session_count=session_count,
        )
        market_result = MarketConditionFeatureService(
            self._config,
            self._processed_store,
            self._raw_store,
            calendar=self._calendar,
        ).calculate(start=start, end=end)
        context_result = CombinedContextMatrixService(
            self._config,
            self._processed_store,
            self._raw_store,
            calendar=self._calendar,
        ).calculate(start=start, end=end)
        annotations = build_regime_hypothesis_annotations(
            market_result,
            boundaries=boundaries,
        )
        return calculate_regime_hypothesis_comparison(
            setup_result,
            outcome_result,
            base_statistics,
            market_result,
            context_result,
            annotations,
            boundaries=boundaries,
        )
