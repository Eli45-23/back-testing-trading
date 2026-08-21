"""Read-only join of Stage 8.2 follow-through with Stage 3 event-time ATR14."""

from __future__ import annotations

from datetime import date

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.indicators import AtrIndicatorService
from spy_research.interactions.atr_tolerance import (
    calculate_atr_tolerance_follow_through,
)
from spy_research.interactions.follow_through_service import BreakFollowThroughService
from spy_research.interactions.models import AtrToleranceResult
from spy_research.market import XNYSCalendar


class AtrToleranceService:
    """Compare exact and fixed-tolerance states for every Stage 8.2 seed."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
        *,
        calendar: XNYSCalendar | None = None,
    ) -> None:
        self._follow_through = BreakFollowThroughService(
            config,
            processed_store,
            raw_store,
            calendar=calendar,
        )
        self._atr = AtrIndicatorService(config, processed_store, raw_store)

    def calculate(self, *, start: date, end: date) -> AtrToleranceResult:
        exact = self._follow_through.calculate(start=start, end=end)
        atr = self._atr.calculate(start=start, end=end)
        atr_by_timestamp = {row.timestamp: row.atr14 for row in atr.rows}
        comparisons = tuple(
            calculate_atr_tolerance_follow_through(
                item,
                atr_by_timestamp.get(item.break_timestamp),
            )
            for item in exact.follow_through
        )
        available = sum(item.atr_available for item in comparisons)
        return AtrToleranceResult(
            start_date=start,
            end_date=end,
            seed_count=exact.seed_count,
            atr_available_count=available,
            atr_unavailable_count=exact.seed_count - available,
            comparisons=comparisons,
        )
