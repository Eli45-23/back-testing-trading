"""Read-only Stage 9.2 composition over frozen Stage 9.1 setups."""

from __future__ import annotations

from collections import Counter
from datetime import date

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.data.schemas import RawBarRecord
from spy_research.data.validation import RawDataValidator
from spy_research.market import MarketSessionClassifier, SessionType, XNYSCalendar
from spy_research.strategy.base_price_action_service import BasePriceActionService
from spy_research.strategy.entry_reference import (
    SetupOutcomeInputError,
    select_entry_reference,
)
from spy_research.strategy.models import (
    BaseSetupStatus,
    EntryStatus,
    SetupOutcomeResult,
)
from spy_research.strategy.setup_outcomes import calculate_setup_outcomes


class SetupOutcomeService:
    """Attach deterministic raw-minute entries and excursions to confirmed setups."""

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

    def calculate(self, *, start: date, end: date) -> SetupOutcomeResult:
        validation = RawDataValidator(self._calendar).validate_raw_store(
            self._raw_store,
            symbol=self._config.symbol,
            start_date=start,
            end_date=end,
        )
        if not validation.passed:
            raise SetupOutcomeInputError(
                f"Raw one-minute validation failed with {validation.error_count} errors"
            )

        setup_result = BasePriceActionService(
            self._config,
            self._processed_store,
            self._raw_store,
            calendar=self._calendar,
        ).calculate(start=start, end=end)
        confirmed = tuple(
            item
            for item in setup_result.candidates
            if item.status is BaseSetupStatus.CONFIRMED
        )

        raw_bars = self._raw_store.load_raw_bars(
            symbol=self._config.symbol,
            start=start,
            end=end,
            feed=self._config.data.feed,
            timeframe=self._config.data.timeframe,
        )
        rth_by_date: dict[date, list[RawBarRecord]] = {}
        for item in MarketSessionClassifier(self._calendar).classify_many(raw_bars):
            if item.session_type is SessionType.RTH:
                rth_by_date.setdefault(item.session_date, []).append(item.bar)

        outcomes = []
        for setup in confirmed:
            bars = tuple(rth_by_date.get(setup.session_date, ()))
            entry = select_entry_reference(setup, bars)
            session = self._calendar.session_for_date(setup.session_date)
            if not session.is_trading_day or session.market_close is None:
                raise SetupOutcomeInputError(
                    "Stage 9.2 requires an authoritative XNYS session"
                )
            outcomes.append(
                calculate_setup_outcomes(
                    setup,
                    entry,
                    bars,
                    session.market_close,
                )
            )

        statuses = Counter(item.entry_reference.entry_status for item in outcomes)
        return SetupOutcomeResult(
            start_date=start,
            end_date=end,
            confirmed_setup_count=len(confirmed),
            available_entry_count=statuses[EntryStatus.AVAILABLE],
            session_end_unavailable_count=statuses[
                EntryStatus.ENTRY_UNAVAILABLE_SESSION_END
            ],
            missing_entry_count=statuses[EntryStatus.ENTRY_REFERENCE_MISSING],
            outcomes=tuple(outcomes),
        )
