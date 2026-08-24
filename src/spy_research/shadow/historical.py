"""Expanded-sample Stage 14.3 replay and Stage 13.2 path equivalence."""

from __future__ import annotations

from collections import defaultdict
from datetime import date

from spy_research.bars import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data import RawBarStore
from spy_research.execution import (
    AtrStopModel,
    ExitFamily,
    ExitModelComparisonService,
    ExitModelExitReason,
    ExitModelStatus,
    StrategyPopulation,
)
from spy_research.levels import PreviousDayLevelsService
from spy_research.live import LiveMarketDataAdapter
from spy_research.market import MarketSessionClassifier, XNYSCalendar
from spy_research.replay import IncrementalSignalStateEngine
from spy_research.shadow.engine import ShadowForwardStateMachine
from spy_research.shadow.models import (
    ShadowHistoricalEquivalence,
    ShadowHistoricalReport,
    ShadowInputError,
    ShadowState,
)


class ShadowHistoricalEquivalenceService:
    """Replay raw minutes and compare both selected paths field-for-field."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
        *,
        calendar: XNYSCalendar | None = None,
        accepted_report=None,
    ) -> None:
        self._config = config
        self._processed_store = processed_store
        self._raw_store = raw_store
        self._calendar = calendar or XNYSCalendar()
        self._accepted_report = accepted_report

    def calculate(self, *, start: date, end: date) -> ShadowHistoricalReport:
        previous = PreviousDayLevelsService(
            self._config, self._raw_store, calendar=self._calendar
        ).calculate(start=start, end=end)
        previous_by_date = {item.session_date: item for item in previous.levels}
        raw = self._raw_store.load_raw_bars(
            symbol=self._config.symbol,
            start=start,
            end=end,
            feed=self._config.data.feed,
            timeframe=self._config.data.timeframe,
        )
        classifier = MarketSessionClassifier(self._calendar)
        by_date = defaultdict(list)
        for bar in raw:
            classified = classifier.classify(bar)
            if self._calendar.session_for_date(classified.session_date).is_trading_day:
                by_date[classified.session_date].append(bar)
        positions = []
        for session_date in sorted(by_date):
            session = self._calendar.session_for_date(session_date)
            replay = IncrementalSignalStateEngine(calendar=self._calendar)
            replay.start_session(
                session,
                previous_day_levels=previous_by_date.get(session_date),
            )
            adapter = LiveMarketDataAdapter(
                replay, session_date=session_date, calendar=self._calendar
            )
            shadow = ShadowForwardStateMachine(session)
            for bar in by_date[session_date]:
                update = adapter.seed(bar)
                shadow.consume_live_update(
                    update,
                    available_levels=adapter.engine.current_levels,
                )
            positions.extend(shadow.positions)
        if any(
            item.state in (ShadowState.PENDING_ENTRY, ShadowState.ACTIVE)
            for item in positions
        ):
            raise ShadowInputError("historical shadow replay ended with open state")
        accepted = self._accepted_report or ExitModelComparisonService(
            self._config,
            self._processed_store,
            self._raw_store,
            calendar=self._calendar,
        ).calculate(start=start, end=end)
        expected = tuple(
            item
            for item in accepted.new_trades
            if item.strategy_population is StrategyPopulation.BASE_SHORT
            and item.variant.family is ExitFamily.NEXT_OBJECTIVE_LEVEL
            and item.variant.stop_model
            in (AtrStopModel.ATR_0_75, AtrStopModel.ATR_1_00)
        )
        observed = {
            (item.setup_identity, item.candidate_id): item
            for item in positions
            if item.state is not ShadowState.ENTRY_UNAVAILABLE_SESSION_END
        }
        expected_by_key = {
            (item.setup_identity, f"BASE_SHORT:{item.variant.variant_id}"): item
            for item in expected
        }
        mismatches = set(observed) ^ set(expected_by_key)
        matched = 0
        for key in set(observed) & set(expected_by_key):
            if self._projection(observed[key]) != self._expected_projection(
                expected_by_key[key]
            ):
                mismatches.add(key)
            else:
                matched += 1
        unavailable = sum(
            item.state is ShadowState.ENTRY_UNAVAILABLE_SESSION_END
            for item in positions
        )
        equivalence = ShadowHistoricalEquivalence(
            exact_match=not mismatches and len(observed) == len(expected),
            shadow_candidate_count=len(positions),
            shadow_executable_path_count=len(observed),
            shadow_entry_unavailable_count=unavailable,
            stage13_path_count=len(expected),
            matched_path_count=matched,
            mismatched_keys=tuple(
                f"{setup}|{candidate}" for setup, candidate in sorted(mismatches)
            ),
        )
        return ShadowHistoricalReport(
            start_date=start,
            end_date=end,
            positions=tuple(positions),
            equivalence=equivalence,
        )

    @staticmethod
    def _projection(item):
        status, reason = {
            ShadowState.TARGET_EXIT: (ExitModelStatus.REALIZED, ExitModelExitReason.NEXT_OBJECTIVE_LEVEL),
            ShadowState.STOP_EXIT: (ExitModelStatus.REALIZED, ExitModelExitReason.STOP),
            ShadowState.EOD_EXIT: (ExitModelStatus.REALIZED, ExitModelExitReason.EOD_CLOSE),
            ShadowState.AMBIGUOUS_BOTH_TOUCHED: (
                ExitModelStatus.AMBIGUOUS_BOTH_TOUCHED,
                ExitModelExitReason.AMBIGUOUS_BOTH_TOUCHED,
            ),
            ShadowState.UNAVAILABLE_ATR: (
                ExitModelStatus.UNAVAILABLE_ATR,
                ExitModelExitReason.UNAVAILABLE_ATR,
            ),
            ShadowState.UNAVAILABLE_OBJECTIVE_LEVEL: (
                ExitModelStatus.UNAVAILABLE_OBJECTIVE,
                ExitModelExitReason.UNAVAILABLE_OBJECTIVE,
            ),
        }[item.state]
        return (
            item.entry_timestamp,
            item.entry_price,
            item.confirmation_atr14,
            item.risk_distance,
            item.stop_price,
            item.target_price,
            item.target_level_types,
            status,
            reason,
            item.exit_timestamp,
            item.exit_price,
            item.realized_price_pnl,
            item.realized_r,
            item.holding_minutes,
            item.bars_observed,
            item.ambiguity,
        )

    @staticmethod
    def _expected_projection(item):
        return (
            item.entry_timestamp,
            item.entry_price,
            item.confirmation_atr,
            item.initial_risk,
            item.stop_price,
            item.objective_price,
            item.objective_level_types,
            item.status,
            item.exit_reason,
            item.exit_timestamp,
            item.exit_price,
            item.price_pnl,
            item.r_multiple,
            item.minutes_in_trade,
            item.bars_observed,
            item.ambiguity,
        )
