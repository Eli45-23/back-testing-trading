"""Offline Stage 11.3 orchestration over accepted RTH five-minute bars."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Sequence

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.indicators import AtrIndicatorService
from spy_research.market import XNYSCalendar
from spy_research.strategy.base_price_action_service import BasePriceActionService
from spy_research.strategy.base_statistics import calculate_base_strategy_statistics
from spy_research.strategy.comparisons.combined_context_service import (
    CombinedContextMatrixService,
)
from spy_research.strategy.comparisons.market_structure import (
    MarketStructureComparisonResult,
    build_market_structure_annotations,
    calculate_market_structure_comparison,
    detect_confirmed_swings,
)
from spy_research.strategy.comparisons.regime_hypotheses import (
    FrozenQuartileBoundary,
)
from spy_research.strategy.comparisons.regime_hypotheses_service import (
    RegimeHypothesisComparisonService,
)
from spy_research.strategy.comparisons.room_to_level_service import (
    RoomToLevelComparisonService,
)
from spy_research.strategy.setup_outcome_service import SetupOutcomeService


class MarketStructureComparisonService:
    """Measure confirmed five-minute structure without writes or qualification."""

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
        regime_boundaries: Sequence[FrozenQuartileBoundary] | None = None,
    ) -> MarketStructureComparisonResult:
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
        bars = self._processed_store.load_processed_5m_bars(
            symbol=self._config.symbol,
            start=start,
            end=end,
            session_mode="RTH_ONLY",
        )
        atr_result = AtrIndicatorService(
            self._config, self._processed_store, self._raw_store
        ).calculate(start=start, end=end)
        context_result = CombinedContextMatrixService(
            self._config,
            self._processed_store,
            self._raw_store,
            calendar=self._calendar,
        ).calculate(start=start, end=end)
        regime_result = RegimeHypothesisComparisonService(
            self._config,
            self._processed_store,
            self._raw_store,
            calendar=self._calendar,
        ).calculate(start=start, end=end, boundaries=regime_boundaries)
        room_result = RoomToLevelComparisonService(
            self._config,
            self._processed_store,
            self._raw_store,
            calendar=self._calendar,
        ).calculate(
            start=start,
            end=end,
            regime_boundaries=regime_boundaries,
        )
        swings = detect_confirmed_swings(bars)
        annotations = build_market_structure_annotations(
            setup_result,
            bars,
            atr_result.rows,
            swings,
            room_result,
        )
        return calculate_market_structure_comparison(
            setup_result,
            outcome_result,
            base_statistics,
            context_result,
            regime_result,
            room_result,
            bars,
            swings,
            annotations,
        )
