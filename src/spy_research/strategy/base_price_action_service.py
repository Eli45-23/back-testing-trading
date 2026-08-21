"""Read-only Stage 8 composition for Stage 9.1 base setup candidates."""

from __future__ import annotations

from datetime import date

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.interactions import (
    BreakFollowThroughService,
    InteractionType,
    LevelInteractionService,
)
from spy_research.market import XNYSCalendar
from spy_research.strategy.base_price_action import (
    interaction_identity,
    qualify_base_price_action_candidate,
)
from spy_research.strategy.models import BasePriceActionResult, BaseSetupStatus


class BasePriceActionService:
    """Build one deterministic candidate record for every Stage 8.2 seed."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
        *,
        calendar: XNYSCalendar | None = None,
    ) -> None:
        self._calendar = calendar or XNYSCalendar()
        self._interactions = LevelInteractionService(
            config,
            processed_store,
            raw_store,
            calendar=self._calendar,
        )
        self._follow_through = BreakFollowThroughService(
            config,
            processed_store,
            raw_store,
            calendar=self._calendar,
        )

    def calculate(self, *, start: date, end: date) -> BasePriceActionResult:
        interactions = self._interactions.calculate(start=start, end=end)
        exact = self._follow_through.calculate(start=start, end=end)
        break_by_identity = {
            interaction_identity(item): item
            for item in interactions.interactions
            if item.interaction_type
            in (
                InteractionType.CLOSE_THROUGH_ABOVE,
                InteractionType.CLOSE_THROUGH_BELOW,
            )
        }
        if len(break_by_identity) != exact.seed_count:
            raise ValueError("Stage 8.1 and Stage 8.2 seed universes do not reconcile")

        candidates = []
        for item in exact.follow_through:
            seed = break_by_identity.get(item.break_interaction_identity)
            if seed is None:
                raise ValueError("Stage 8.2 contains an unknown Stage 8.1 seed")
            session = self._calendar.session_for_date(item.session_date)
            if not session.is_trading_day or session.market_close is None:
                raise ValueError("Stage 9.1 requires an authoritative XNYS session")
            candidates.append(
                qualify_base_price_action_candidate(
                    seed,
                    item,
                    session.market_close,
                )
            )
        ordered = tuple(
            sorted(
                candidates,
                key=lambda item: (
                    item.session_date,
                    item.break_timestamp,
                    item.level_type.value,
                    item.direction.value,
                ),
            )
        )
        confirmed = sum(
            item.status is BaseSetupStatus.CONFIRMED for item in ordered
        )
        return BasePriceActionResult(
            start_date=start,
            end_date=end,
            seed_count=exact.seed_count,
            confirmed_count=confirmed,
            non_confirmed_count=exact.seed_count - confirmed,
            candidates=ordered,
        )
