"""Offline Stage 10.8 composition of accepted Stage 9/10 results."""

from __future__ import annotations

from datetime import date, timedelta

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.events import EmaCrossEventService
from spy_research.indicators import EmaIndicatorService, VwapIndicatorService
from spy_research.market import XNYSCalendar
from spy_research.strategy.base_price_action_service import BasePriceActionService
from spy_research.strategy.base_statistics import calculate_base_strategy_statistics
from spy_research.strategy.comparisons.combined_context import (
    CombinedContextMatrixResult,
    calculate_combined_context_matrix,
    combine_context_annotations,
)
from spy_research.strategy.comparisons.ema20_vwap_alignment import (
    annotate_confirmed_ema20_vwap_alignment,
)
from spy_research.strategy.comparisons.ema20_vwap_cross import (
    detect_ema20_vwap_crosses,
)
from spy_research.strategy.comparisons.ema20_vwap_cross_context import (
    annotate_ema20_vwap_cross_context,
)
from spy_research.strategy.comparisons.ema9_vwap_alignment import (
    annotate_confirmed_ema9_vwap_alignment,
)
from spy_research.strategy.comparisons.ema9_vwap_cross import (
    detect_ema9_vwap_crosses,
)
from spy_research.strategy.comparisons.ema9_vwap_cross_context import (
    annotate_ema9_vwap_cross_context,
)
from spy_research.strategy.comparisons.ema_alignment import annotate_confirmed_setups
from spy_research.strategy.comparisons.ema_cross_context import (
    annotate_prior_cross_context,
)
from spy_research.strategy.comparisons.vwap_alignment import (
    annotate_confirmed_vwap_alignment,
)
from spy_research.strategy.setup_outcome_service import SetupOutcomeService


class CombinedContextMatrixService:
    """Join accepted annotations and outcomes without strategy interpretation."""

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

    def calculate(self, *, start: date, end: date) -> CombinedContextMatrixResult:
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
        bars = self._processed_store.load_processed_5m_bars(
            symbol=self._config.symbol,
            start=start,
            end=end,
            session_mode="RTH_ONLY",
        )
        ema_cross_result = EmaCrossEventService(
            self._config, self._processed_store, self._raw_store
        ).calculate(start=start, end=end)
        ema9_vwap_events, _ = detect_ema9_vwap_crosses(
            ema_result.rows, vwap_result.rows
        )
        ema20_vwap_events, _ = detect_ema20_vwap_crosses(
            ema_result.rows, vwap_result.rows
        )
        annotations = combine_context_annotations(
            setup_result,
            annotate_confirmed_setups(setup_result, ema_result.rows),
            annotate_prior_cross_context(setup_result, ema_cross_result.events),
            annotate_confirmed_vwap_alignment(setup_result, bars, vwap_result.rows),
            annotate_confirmed_ema9_vwap_alignment(
                setup_result, ema_result.rows, vwap_result.rows
            ),
            annotate_ema9_vwap_cross_context(setup_result, ema9_vwap_events),
            annotate_confirmed_ema20_vwap_alignment(
                setup_result, ema_result.rows, vwap_result.rows
            ),
            annotate_ema20_vwap_cross_context(setup_result, ema20_vwap_events),
        )
        return calculate_combined_context_matrix(
            setup_result,
            outcome_result,
            base_statistics,
            annotations,
        )
