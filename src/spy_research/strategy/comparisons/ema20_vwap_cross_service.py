"""Read-only Stage 10.7 composition over accepted indicators and outcomes."""

from __future__ import annotations

from datetime import date, timedelta

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.indicators import EmaIndicatorService, VwapIndicatorService
from spy_research.market import XNYSCalendar
from spy_research.strategy.base_price_action_service import BasePriceActionService
from spy_research.strategy.base_statistics import calculate_base_strategy_statistics
from spy_research.strategy.comparisons.ema20_vwap_alignment import (
    annotate_confirmed_ema20_vwap_alignment,
)
from spy_research.strategy.comparisons.ema20_vwap_cross import (
    detect_ema20_vwap_crosses,
)
from spy_research.strategy.comparisons.ema20_vwap_cross_context import (
    annotate_ema20_vwap_cross_context,
    calculate_ema20_vwap_cross_context_comparison,
)
from spy_research.strategy.comparisons.ema20_vwap_cross_models import (
    Ema20VwapCrossContextComparisonResult,
)
from spy_research.strategy.comparisons.ema9_vwap_cross import (
    detect_ema9_vwap_crosses,
)
from spy_research.strategy.comparisons.ema9_vwap_cross_context import (
    annotate_ema9_vwap_cross_context,
)
from spy_research.strategy.setup_outcome_service import SetupOutcomeService


class Ema20VwapCrossContextComparisonService:
    """Build EMA20/VWAP events and attach latest already-known context."""

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
        self, *, start: date, end: date
    ) -> Ema20VwapCrossContextComparisonResult:
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
            self._calendar.session_for_date(start + timedelta(days=offset)).is_trading_day
            for offset in range((end - start).days + 1)
        )
        base_statistics = calculate_base_strategy_statistics(
            setup_result,
            outcome_result,
            development_session_count=session_count,
        )
        ema_result = EmaIndicatorService(
            self._config, self._processed_store, self._raw_store
        ).calculate(start=start, end=end)
        vwap_result = VwapIndicatorService(
            self._config, self._processed_store, self._raw_store
        ).calculate(start=start, end=end)
        events, event_sessions = detect_ema20_vwap_crosses(
            ema_result.rows, vwap_result.rows
        )
        annotations = annotate_ema20_vwap_cross_context(setup_result, events)
        alignment_annotations = annotate_confirmed_ema20_vwap_alignment(
            setup_result, ema_result.rows, vwap_result.rows
        )
        ema9_events, _ = detect_ema9_vwap_crosses(
            ema_result.rows, vwap_result.rows
        )
        ema9_annotations = annotate_ema9_vwap_cross_context(
            setup_result, ema9_events
        )
        return calculate_ema20_vwap_cross_context_comparison(
            setup_result,
            outcome_result,
            base_statistics,
            events,
            event_sessions,
            annotations,
            alignment_annotations,
            ema9_annotations,
        )
