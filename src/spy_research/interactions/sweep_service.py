"""Read-only composition of Stage 8.1 wick seeds and Stage 8.3 labels."""

from __future__ import annotations

from datetime import date

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.interactions.models import (
    InteractionType,
    LiquiditySweepResult,
)
from spy_research.interactions.service import LevelInteractionService
from spy_research.interactions.sweeps import classify_sweep_pattern
from spy_research.market import XNYSCalendar


class LiquiditySweepService:
    """Label every Stage 8.1 wick seed without future bars or writes."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
        *,
        calendar: XNYSCalendar | None = None,
    ) -> None:
        self._interaction_service = LevelInteractionService(
            config,
            processed_store,
            raw_store,
            calendar=calendar,
        )

    def calculate(self, *, start: date, end: date) -> LiquiditySweepResult:
        interactions = self._interaction_service.calculate(start=start, end=end)
        seeds = tuple(
            item
            for item in interactions.interactions
            if item.interaction_type
            in (
                InteractionType.WICK_THROUGH_ABOVE,
                InteractionType.WICK_THROUGH_BELOW,
            )
        )
        return LiquiditySweepResult(
            start_date=start,
            end_date=end,
            seed_count=len(seeds),
            patterns=tuple(classify_sweep_pattern(item) for item in seeds),
        )
