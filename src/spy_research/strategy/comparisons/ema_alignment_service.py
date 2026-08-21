"""Read-only Stage 10.1 composition over frozen Stage 3 and Stage 9 results."""

from __future__ import annotations

from datetime import date, timedelta

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.indicators import EmaIndicatorService
from spy_research.market import XNYSCalendar
from spy_research.strategy.base_price_action_service import BasePriceActionService
from spy_research.strategy.base_statistics import calculate_base_strategy_statistics
from spy_research.strategy.comparisons.ema_alignment import (
    annotate_confirmed_setups,
    calculate_ema_alignment_comparison,
)
from spy_research.strategy.comparisons.models import EmaAlignmentComparisonResult
from spy_research.strategy.setup_outcome_service import SetupOutcomeService


class EmaAlignmentComparisonService:
    """Attach exact confirmation-bar EMA labels and compare frozen outcomes."""

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

    def calculate(self, *, start: date, end: date) -> EmaAlignmentComparisonResult:
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
        ema_result = EmaIndicatorService(
            self._config,
            self._processed_store,
            self._raw_store,
        ).calculate(start=start, end=end)
        annotations = annotate_confirmed_setups(setup_result, ema_result.rows)
        return calculate_ema_alignment_comparison(
            setup_result,
            outcome_result,
            base_statistics,
            annotations,
        )
