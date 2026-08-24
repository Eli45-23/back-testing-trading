"""Offline Stage 14.1 replay and independent accepted-batch reconciliation."""

from __future__ import annotations

from collections import defaultdict
from datetime import date

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.levels import PreviousDayLevelsService
from spy_research.market import MarketSessionClassifier, XNYSCalendar
from spy_research.replay.engine import IncrementalSignalStateEngine
from spy_research.replay.models import (
    ReplayBatchReconciliation,
    ReplayInputError,
    SignalReplayReport,
)
from spy_research.strategy.base_price_action_service import BasePriceActionService
from spy_research.strategy.models import BaseSetupStatus, SetupDirection


class SignalReplayService:
    """Feed local raw bars individually, then reconcile against accepted Stage 9."""

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

    def calculate(self, *, start: date, end: date) -> SignalReplayReport:
        if start > end:
            raise ReplayInputError("start date must be on or before end date")
        previous = PreviousDayLevelsService(
            self._config,
            self._raw_store,
            calendar=self._calendar,
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
        signals, sessions, replay_bars = self._run_incremental(
            by_date,
            previous_by_date,
            reuse_engine=True,
        )
        chunk_signals, chunk_sessions, chunk_bars = self._run_incremental(
            by_date,
            previous_by_date,
            reuse_engine=False,
        )
        chunk_match = (
            signals == chunk_signals
            and sessions == chunk_sessions
            and replay_bars == chunk_bars
        )
        stored_bars = self._processed_store.load_processed_5m_bars(
            symbol=self._config.symbol,
            start=start,
            end=end,
            session_mode="RTH_ONLY",
        )
        processed_match = tuple(replay_bars) == stored_bars
        batch = BasePriceActionService(
            self._config,
            self._processed_store,
            self._raw_store,
            calendar=self._calendar,
        ).calculate(start=start, end=end)
        confirmed = tuple(
            item for item in batch.candidates if item.status is BaseSetupStatus.CONFIRMED
        )
        replay_seed_count = sum(item.break_seed_count for item in sessions)
        reconciliation = self._reconcile(
            tuple(signals),
            confirmed,
            replay_seed_count=replay_seed_count,
            batch_seed_count=batch.seed_count,
        )
        return SignalReplayReport(
            start_date=start,
            end_date=end,
            raw_bar_count=sum(item.raw_bar_count for item in sessions),
            rth_one_minute_count=sum(item.rth_one_minute_count for item in sessions),
            five_minute_count=len(replay_bars),
            break_seed_count=replay_seed_count,
            confirmed_signal_count=len(signals),
            executable_signal_count=sum(item.same_session_executable for item in signals),
            base_short_confirmed_count=sum(item.base_short_membership for item in signals),
            base_short_executable_count=sum(
                item.base_short_membership and item.same_session_executable
                for item in signals
            ),
            signals=tuple(signals),
            sessions=tuple(sessions),
            batch_reconciliation=reconciliation,
            processed_five_minute_exact_match=processed_match,
            session_chunk_replay_exact_match=chunk_match,
        )

    def _run_incremental(self, by_date, previous_by_date, *, reuse_engine: bool):
        engine = IncrementalSignalStateEngine(calendar=self._calendar)
        sessions = []
        signals = []
        replay_bars = []
        for session_date in sorted(by_date):
            if not reuse_engine:
                engine = IncrementalSignalStateEngine(calendar=self._calendar)
            engine.start_session(
                self._calendar.session_for_date(session_date),
                previous_day_levels=previous_by_date.get(session_date),
            )
            for bar in by_date[session_date]:
                update = engine.process_one_minute_bar(bar)
                signals.extend(update.signal_events)
            replay_bars.extend(engine.completed_five_minute_bars)
            sessions.append(engine.finish_session())
        return tuple(signals), tuple(sessions), tuple(replay_bars)

    @staticmethod
    def _reconcile(
        signals,
        confirmed,
        *,
        replay_seed_count: int,
        batch_seed_count: int,
    ) -> ReplayBatchReconciliation:
        replay_by_id = {item.setup_identity: item for item in signals}
        batch_by_id = {item.setup_identity: item for item in confirmed}
        mismatched = set(replay_by_id) ^ set(batch_by_id)
        for identity in set(replay_by_id) & set(batch_by_id):
            replay = replay_by_id[identity]
            batch = batch_by_id[identity]
            expected = (
                batch.direction,
                batch.session_date,
                batch.level_type,
                batch.level_price,
                batch.break_timestamp,
                batch.confirmation_bar_timestamp,
                batch.confirmation_type,
                batch.signal_known_at,
                batch.same_session_executable,
                batch.direction is SetupDirection.SHORT,
            )
            observed = (
                replay.direction,
                replay.session_date,
                replay.triggering_level_type,
                replay.triggering_level_price,
                replay.break_timestamp,
                replay.confirmation_candle_timestamp,
                replay.confirmation_type,
                replay.signal_known_at,
                replay.same_session_executable,
                replay.base_short_membership,
            )
            if observed != expected:
                mismatched.add(identity)
        replay_executable = sum(item.same_session_executable for item in signals)
        batch_executable = sum(item.same_session_executable for item in confirmed)
        replay_short = sum(item.base_short_membership for item in signals)
        batch_short = sum(item.direction is SetupDirection.SHORT for item in confirmed)
        replay_short_executable = sum(
            item.base_short_membership and item.same_session_executable
            for item in signals
        )
        batch_short_executable = sum(
            item.direction is SetupDirection.SHORT and item.same_session_executable
            for item in confirmed
        )
        exact = not mismatched and all(
            (
                replay_seed_count == batch_seed_count,
                len(signals) == len(confirmed),
                replay_executable == batch_executable,
                replay_short == batch_short,
                replay_short_executable == batch_short_executable,
            )
        )
        return ReplayBatchReconciliation(
            exact_match=exact,
            replay_break_seed_count=replay_seed_count,
            batch_break_seed_count=batch_seed_count,
            replay_confirmed_count=len(signals),
            batch_confirmed_count=len(confirmed),
            replay_executable_count=replay_executable,
            batch_executable_count=batch_executable,
            replay_base_short_confirmed_count=replay_short,
            batch_base_short_confirmed_count=batch_short,
            replay_base_short_executable_count=replay_short_executable,
            batch_base_short_executable_count=batch_short_executable,
            mismatched_setup_identities=tuple(sorted(mismatched)),
        )
