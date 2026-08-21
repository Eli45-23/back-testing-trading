"""Read-only composition of Stage 2 candles and frozen Stage 7 levels."""

from __future__ import annotations

from collections import Counter
from datetime import date

from spy_research.bars.models import FiveMinuteBar
from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.interactions.classifier import classify_session_level_interactions
from spy_research.interactions.models import (
    AvailableLevel,
    InteractionCount,
    InteractionType,
    LevelInteractionResult,
    LevelType,
)
from spy_research.levels import (
    OpeningFiveMinuteLevels,
    OpeningFiveMinuteLevelsService,
    PremarketLevels,
    PremarketLevelsService,
    PreviousDayLevels,
    PreviousDayLevelsService,
)
from spy_research.market import XNYSCalendar


def build_session_levels(
    *,
    session_date: date,
    market_open,
    previous_day: PreviousDayLevels | None,
    premarket: PremarketLevels | None,
    opening: OpeningFiveMinuteLevels | None,
) -> tuple[AvailableLevel, ...]:
    """Map available Stage 7 values to generic interaction-ready levels."""

    values = []
    if previous_day is not None:
        if previous_day.session_date != session_date:
            raise ValueError("Previous-day level session mismatch")
        values.extend(
            (
                AvailableLevel(session_date=session_date, level_type=LevelType.PDH,
                               level_price=previous_day.pdh,
                               available_from_timestamp=market_open),
                AvailableLevel(session_date=session_date, level_type=LevelType.PDL,
                               level_price=previous_day.pdl,
                               available_from_timestamp=market_open),
                AvailableLevel(session_date=session_date, level_type=LevelType.PDC,
                               level_price=previous_day.pdc,
                               available_from_timestamp=market_open),
            )
        )
    if premarket is not None:
        if premarket.session_date != session_date:
            raise ValueError("Premarket level session mismatch")
        if premarket.status == "AVAILABLE":
            assert premarket.pmh is not None and premarket.pml is not None
            values.extend(
                (
                    AvailableLevel(session_date=session_date, level_type=LevelType.PMH,
                                   level_price=premarket.pmh,
                                   available_from_timestamp=market_open),
                    AvailableLevel(session_date=session_date, level_type=LevelType.PML,
                                   level_price=premarket.pml,
                                   available_from_timestamp=market_open),
                )
            )
    if opening is not None:
        if opening.session_date != session_date:
            raise ValueError("Opening-range level session mismatch")
        values.extend(
            (
                AvailableLevel(session_date=session_date, level_type=LevelType.ORH5,
                               level_price=opening.orh5,
                               available_from_timestamp=opening.available_from_timestamp),
                AvailableLevel(session_date=session_date, level_type=LevelType.ORL5,
                               level_price=opening.orl5,
                               available_from_timestamp=opening.available_from_timestamp),
            )
        )
    return tuple(values)


class LevelInteractionService:
    """Calculate non-NO interaction events entirely from local accepted data."""

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

    def calculate(self, *, start: date, end: date) -> LevelInteractionResult:
        if start > end:
            raise ValueError("start date must be on or before end date")

        previous_result = PreviousDayLevelsService(
            self._config, self._raw_store, calendar=self._calendar
        ).calculate(start=start, end=end)
        premarket_result = PremarketLevelsService(
            self._config, self._raw_store, calendar=self._calendar
        ).calculate(start=start, end=end)
        opening_result = OpeningFiveMinuteLevelsService(
            self._config,
            self._processed_store,
            self._raw_store,
            calendar=self._calendar,
        ).calculate(start=start, end=end)
        bars = self._processed_store.load_processed_5m_bars(
            symbol=self._config.symbol,
            start=start,
            end=end,
            session_mode="RTH_ONLY",
        )

        previous_by_date = {item.session_date: item for item in previous_result.levels}
        premarket_by_date = {item.session_date: item for item in premarket_result.levels}
        opening_by_date = {item.session_date: item for item in opening_result.levels}
        bars_by_date: dict[date, list[FiveMinuteBar]] = {}
        for bar in bars:
            bars_by_date.setdefault(bar.session_date, []).append(bar)

        all_records = []
        for session_date in sorted(bars_by_date):
            session = self._calendar.session_for_date(session_date)
            assert session.market_open is not None
            levels = build_session_levels(
                session_date=session_date,
                market_open=session.market_open,
                previous_day=previous_by_date.get(session_date),
                premarket=premarket_by_date.get(session_date),
                opening=opening_by_date.get(session_date),
            )
            all_records.extend(
                classify_session_level_interactions(
                    tuple(bars_by_date[session_date]),
                    levels,
                    emit_no_interaction=True,
                )
            )

        counter = Counter(
            (record.level_type, record.interaction_type) for record in all_records
        )
        counts = tuple(
            InteractionCount(
                level_type=level_type,
                interaction_type=interaction_type,
                count=counter[(level_type, interaction_type)],
            )
            for level_type in LevelType
            for interaction_type in InteractionType
        )
        emitted = tuple(
            record
            for record in all_records
            if record.interaction_type is not InteractionType.NO_INTERACTION
        )
        return LevelInteractionResult(
            start_date=start,
            end_date=end,
            eligible_pair_count=len(all_records),
            no_interaction_count=sum(
                record.interaction_type is InteractionType.NO_INTERACTION
                for record in all_records
            ),
            interactions=emitted,
            counts=counts,
        )
