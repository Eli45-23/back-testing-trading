"""Read-only Stage 10.2 composition over frozen Stage 4 and Stage 9 results."""

from __future__ import annotations

from datetime import date, timedelta

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.events import EmaCrossEventService
from spy_research.indicators import EmaIndicatorService
from spy_research.market import XNYSCalendar
from spy_research.strategy.base_price_action_service import BasePriceActionService
from spy_research.strategy.base_statistics import calculate_base_strategy_statistics
from spy_research.strategy.comparisons.ema_alignment import annotate_confirmed_setups
from spy_research.strategy.comparisons.ema_cross_context import (
    annotate_prior_cross_context,
    calculate_ema_cross_context_comparison,
)
from spy_research.strategy.comparisons.models import EmaCrossContextComparisonResult
from spy_research.strategy.setup_outcome_service import SetupOutcomeService


class EmaCrossContextComparisonService:
    """Attach latest eligible Stage 4 cross context to unchanged Stage 9 setups."""

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

    def calculate(self, *, start: date, end: date) -> EmaCrossContextComparisonResult:
        setup_result = BasePriceActionService(
            self._config, self._processed_store, self._raw_store, calendar=self._calendar
        ).calculate(start=start, end=end)
        outcome_result = SetupOutcomeService(
            self._config, self._processed_store, self._raw_store, calendar=self._calendar
        ).calculate(start=start, end=end)
        session_count = sum(
            self._calendar.session_for_date(start + timedelta(days=offset)).is_trading_day
            for offset in range((end - start).days + 1)
        )
        base_statistics = calculate_base_strategy_statistics(
            setup_result, outcome_result, development_session_count=session_count
        )
        cross_result = EmaCrossEventService(
            self._config, self._processed_store, self._raw_store
        ).calculate(start=start, end=end)
        annotations = annotate_prior_cross_context(setup_result, cross_result.events)
        ema_result = EmaIndicatorService(
            self._config, self._processed_store, self._raw_store
        ).calculate(start=start, end=end)
        alignment_annotations = annotate_confirmed_setups(setup_result, ema_result.rows)
        return calculate_ema_cross_context_comparison(
            setup_result,
            outcome_result,
            base_statistics,
            annotations,
            alignment_annotations,
            stage4_event_count=len(cross_result.events),
        )
