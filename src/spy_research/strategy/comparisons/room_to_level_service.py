"""Offline Stage 11.2 composition over accepted Stage 3/7/9/10/11 sources."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Sequence

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.indicators import AtrIndicatorService
from spy_research.interactions import build_session_levels
from spy_research.levels import (
    OpeningFiveMinuteLevelsService,
    PremarketLevelsService,
    PreviousDayLevelsService,
)
from spy_research.market import XNYSCalendar
from spy_research.strategy.base_price_action_service import BasePriceActionService
from spy_research.strategy.base_statistics import calculate_base_strategy_statistics
from spy_research.strategy.comparisons.combined_context_service import (
    CombinedContextMatrixService,
)
from spy_research.strategy.comparisons.regime_hypotheses import (
    FrozenQuartileBoundary,
)
from spy_research.strategy.comparisons.regime_hypotheses_service import (
    RegimeHypothesisComparisonService,
)
from spy_research.strategy.comparisons.room_to_level import (
    RoomToLevelComparisonResult,
    build_room_annotations,
    calculate_room_to_level_comparison,
)
from spy_research.strategy.setup_outcome_service import SetupOutcomeService


class RoomToLevelComparisonService:
    """Measure known objective room without writes or setup qualification."""

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
    ) -> RoomToLevelComparisonResult:
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
        previous = PreviousDayLevelsService(
            self._config, self._raw_store, calendar=self._calendar
        ).calculate(start=start, end=end)
        premarket = PremarketLevelsService(
            self._config, self._raw_store, calendar=self._calendar
        ).calculate(start=start, end=end)
        opening = OpeningFiveMinuteLevelsService(
            self._config,
            self._processed_store,
            self._raw_store,
            calendar=self._calendar,
        ).calculate(start=start, end=end)
        previous_by_date = {item.session_date: item for item in previous.levels}
        premarket_by_date = {item.session_date: item for item in premarket.levels}
        opening_by_date = {item.session_date: item for item in opening.levels}
        levels_by_session = {}
        for session_date in sorted(
            set(premarket_by_date) | set(opening_by_date) | set(previous_by_date)
        ):
            session = self._calendar.session_for_date(session_date)
            if not session.is_trading_day or session.market_open is None:
                continue
            levels_by_session[session_date] = build_session_levels(
                session_date=session_date,
                market_open=session.market_open,
                previous_day=previous_by_date.get(session_date),
                premarket=premarket_by_date.get(session_date),
                opening=opening_by_date.get(session_date),
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
        annotations = build_room_annotations(
            setup_result,
            outcome_result,
            bars,
            atr_result.rows,
            levels_by_session,
        )
        return calculate_room_to_level_comparison(
            setup_result,
            outcome_result,
            base_statistics,
            context_result,
            regime_result,
            annotations,
        )
