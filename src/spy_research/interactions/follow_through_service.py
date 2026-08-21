"""Read-only service joining Stage 8.1 seeds to bounded future candles."""

from __future__ import annotations

from datetime import date

from spy_research.bars.models import FiveMinuteBar
from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.interactions.follow_through import calculate_break_follow_through
from spy_research.interactions.models import (
    BreakFollowThroughResult,
    InteractionType,
)
from spy_research.interactions.service import LevelInteractionService
from spy_research.market import XNYSCalendar


class BreakFollowThroughService:
    """Build Stage 8.2 context without modifying Stage 8.1 interactions."""

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

    def calculate(self, *, start: date, end: date) -> BreakFollowThroughResult:
        if start > end:
            raise ValueError("start date must be on or before end date")
        interactions = LevelInteractionService(
            self._config,
            self._processed_store,
            self._raw_store,
            calendar=self._calendar,
        ).calculate(start=start, end=end)
        seeds = tuple(
            item
            for item in interactions.interactions
            if item.interaction_type
            in (
                InteractionType.CLOSE_THROUGH_ABOVE,
                InteractionType.CLOSE_THROUGH_BELOW,
            )
        )
        bars = self._processed_store.load_processed_5m_bars(
            symbol=self._config.symbol,
            start=start,
            end=end,
            session_mode="RTH_ONLY",
        )
        bars_by_date: dict[date, list[FiveMinuteBar]] = {}
        for bar in bars:
            bars_by_date.setdefault(bar.session_date, []).append(bar)

        contexts = []
        for seed in seeds:
            session_bars = bars_by_date.get(seed.session_date, [])
            index_by_timestamp = {
                bar.timestamp: index for index, bar in enumerate(session_bars)
            }
            seed_index = index_by_timestamp.get(seed.candle_timestamp)
            if seed_index is None:
                raise ValueError("Stage 8.1 seed candle is absent from processed data")
            contexts.append(
                calculate_break_follow_through(
                    seed,
                    tuple(session_bars[seed_index + 1 : seed_index + 4]),
                )
            )
        return BreakFollowThroughResult(
            start_date=start,
            end_date=end,
            seed_count=len(seeds),
            follow_through=tuple(contexts),
        )
