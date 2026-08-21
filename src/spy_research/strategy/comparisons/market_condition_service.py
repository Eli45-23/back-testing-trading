"""Offline orchestration for Stage 10.9 market-condition measurements."""

from __future__ import annotations

from datetime import date, timedelta

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.indicators import (
    AtrIndicatorService,
    EmaIndicatorService,
    VwapIndicatorService,
)
from spy_research.market import XNYSCalendar
from spy_research.strategy.base_price_action_service import BasePriceActionService
from spy_research.strategy.base_statistics import calculate_base_strategy_statistics
from spy_research.strategy.comparisons.market_condition import (
    MarketConditionFeatureResult,
    calculate_market_condition_annotations,
    calculate_market_condition_report,
)
from spy_research.strategy.setup_outcome_service import SetupOutcomeService


class MarketConditionFeatureService:
    """Compose accepted local bars, indicators, setups, and outcomes read-only."""

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

    def calculate(self, *, start: date, end: date) -> MarketConditionFeatureResult:
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
        ema_result = EmaIndicatorService(
            self._config, self._processed_store, self._raw_store
        ).calculate(start=start, end=end)
        vwap_result = VwapIndicatorService(
            self._config, self._processed_store, self._raw_store
        ).calculate(start=start, end=end)
        atr_result = AtrIndicatorService(
            self._config, self._processed_store, self._raw_store
        ).calculate(start=start, end=end)
        annotations = calculate_market_condition_annotations(
            setup_result,
            bars,
            ema_result.rows,
            vwap_result.rows,
            atr_result.rows,
        )
        return calculate_market_condition_report(
            setup_result,
            outcome_result,
            base_statistics,
            annotations,
        )
