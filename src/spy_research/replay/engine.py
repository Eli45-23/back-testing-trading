"""Chronological one-minute state transitions shared by replay and future live data."""

from __future__ import annotations

from datetime import timedelta
from hashlib import sha256

from spy_research.bars.models import FiveMinuteBar
from spy_research.data.schemas import RawBarRecord
from spy_research.events.ema_cross import detect_ema_crosses
from spy_research.execution import AtrStopModel, ExitFamily, exit_variant_identity
from spy_research.indicators.atr import calculate_session_atr
from spy_research.indicators.ema import calculate_session_ema
from spy_research.indicators.vwap import calculate_session_vwap
from spy_research.interactions import (
    InteractionType,
    LevelInteraction,
    build_session_levels,
)
from spy_research.interactions.classifier import classify_level_interaction
from spy_research.interactions.follow_through import calculate_break_follow_through
from spy_research.levels import (
    PreviousDayLevels,
    calculate_opening_five_minute_levels,
    calculate_premarket_levels,
    next_xnys_session_date,
)
from spy_research.market import (
    MarketSessionClassifier,
    SessionType,
    TradingSession,
    XNYSCalendar,
)
from spy_research.replay.models import (
    IncrementalReplayUpdate,
    ReplayCrossEvent,
    ReplayCrossType,
    ReplayInputError,
    ReplaySessionSummary,
    ReplaySignalEvent,
)
from spy_research.strategy.base_price_action import (
    qualify_base_price_action_candidate,
)
from spy_research.strategy.comparisons.ema20_vwap_cross import (
    detect_ema20_vwap_crosses,
)
from spy_research.strategy.comparisons.ema9_vwap_cross import (
    detect_ema9_vwap_crosses,
)
from spy_research.strategy.models import BaseSetupStatus, SetupDirection


STAGE14_FORWARD_CANDIDATE_IDS = (
    "BASE_SHORT:"
    + exit_variant_identity(
        ExitFamily.NEXT_OBJECTIVE_LEVEL,
        AtrStopModel.ATR_0_75,
    ),
    "BASE_SHORT:"
    + exit_variant_identity(
        ExitFamily.NEXT_OBJECTIVE_LEVEL,
        AtrStopModel.ATR_1_00,
    ),
)


class IncrementalSignalStateEngine:
    """Consume one completed minute at a time without visibility into future bars."""

    def __init__(self, *, calendar: XNYSCalendar | None = None) -> None:
        self._calendar = calendar or XNYSCalendar()
        self._classifier = MarketSessionClassifier(self._calendar)
        self._last_input_timestamp = None
        self._session: TradingSession | None = None
        self._previous_day: PreviousDayLevels | None = None
        self._premarket_bars: list[RawBarRecord] = []
        self._premarket_levels = None
        self._opening_levels = None
        self._rth_bucket: list[RawBarRecord] = []
        self._five_minute_bars: list[FiveMinuteBar] = []
        self._break_seeds: list[LevelInteraction] = []
        self._signals: list[ReplaySignalEvent] = []
        self._emitted_setup_ids: set[str] = set()
        self._seen_cross_ids: set[str] = set()
        self._cross_counts = {cross_type: 0 for cross_type in ReplayCrossType}
        self._raw_count = 0
        self._rth_count = 0

    @property
    def completed_five_minute_bars(self) -> tuple[FiveMinuteBar, ...]:
        return tuple(self._five_minute_bars)

    @property
    def signals(self) -> tuple[ReplaySignalEvent, ...]:
        return tuple(self._signals)

    @property
    def current_levels(self):
        """Expose only immutable, already-available level definitions."""

        if self._session is None:
            return ()
        return self._levels()

    def start_session(
        self,
        session: TradingSession,
        *,
        previous_day_levels: PreviousDayLevels | None,
    ) -> None:
        if self._session is not None:
            raise ReplayInputError("finish the active session before starting another")
        if not session.is_trading_day:
            raise ReplayInputError("replay requires an XNYS trading session")
        if (
            previous_day_levels is not None
            and previous_day_levels.session_date != session.session_date
        ):
            raise ReplayInputError("previous-day levels belong to another session")
        if previous_day_levels is not None and next_xnys_session_date(
            previous_day_levels.source_session_date,
            calendar=self._calendar,
        ) != session.session_date:
            raise ReplayInputError(
                "previous-day levels must come from the prior XNYS session"
            )
        self._session = session
        self._previous_day = previous_day_levels
        self._premarket_bars = []
        self._premarket_levels = None
        self._opening_levels = None
        self._rth_bucket = []
        self._five_minute_bars = []
        self._break_seeds = []
        self._signals = []
        self._emitted_setup_ids = set()
        self._seen_cross_ids = set()
        self._cross_counts = {cross_type: 0 for cross_type in ReplayCrossType}
        self._raw_count = 0
        self._rth_count = 0

    def process_one_minute_bar(
        self, bar: RawBarRecord
    ) -> IncrementalReplayUpdate:
        if self._session is None:
            raise ReplayInputError("start_session must precede one-minute input")
        if self._last_input_timestamp is not None and bar.timestamp <= self._last_input_timestamp:
            if bar.timestamp == self._last_input_timestamp:
                raise ReplayInputError("duplicate one-minute timestamp")
            raise ReplayInputError("one-minute bars must be strictly chronological")
        classified = self._classifier.classify(bar)
        if classified.session_date != self._session.session_date:
            raise ReplayInputError("one-minute bar does not belong to the active session")
        self._last_input_timestamp = bar.timestamp
        self._raw_count += 1
        completed = None
        latest_ema = None
        latest_vwap = None
        latest_atr = None
        crosses = ()
        interactions = ()
        signals = ()
        if classified.session_type is SessionType.PREMARKET:
            if self._rth_count:
                raise ReplayInputError("premarket data cannot arrive after RTH begins")
            self._premarket_bars.append(bar)
        elif classified.session_type is SessionType.RTH:
            if self._premarket_levels is None and self._premarket_bars:
                self._premarket_levels = calculate_premarket_levels(
                    tuple(self._premarket_bars), calendar=self._calendar
                )
            self._validate_expected_rth_minute(bar)
            self._rth_count += 1
            self._rth_bucket.append(bar)
            if len(self._rth_bucket) == 5:
                completed = self._complete_bucket()
                ema_rows = calculate_session_ema(tuple(self._five_minute_bars))
                vwap_rows = calculate_session_vwap(tuple(self._five_minute_bars))
                atr_rows = calculate_session_atr(tuple(self._five_minute_bars))
                latest_ema = ema_rows[-1]
                latest_vwap = vwap_rows[-1]
                latest_atr = atr_rows[-1]
                crosses = self._new_crosses(ema_rows, vwap_rows)
                interactions, signals = self._update_strategy_state(completed)
        return IncrementalReplayUpdate(
            input_bar_timestamp=bar.timestamp,
            input_bar_completed_at=bar.timestamp + timedelta(minutes=1),
            session_date=classified.session_date,
            session_type=classified.session_type,
            completed_five_minute_bar=completed,
            latest_ema=latest_ema,
            latest_vwap=latest_vwap,
            latest_atr=latest_atr,
            level_interactions=interactions,
            cross_events=crosses,
            signal_events=signals,
        )

    def _validate_expected_rth_minute(self, bar: RawBarRecord) -> None:
        assert self._session is not None and self._session.market_open is not None
        expected = self._session.market_open + timedelta(minutes=self._rth_count)
        if bar.timestamp != expected:
            raise ReplayInputError(
                "RTH one-minute input must be consecutive from the XNYS open"
            )

    def _complete_bucket(self) -> FiveMinuteBar:
        source = tuple(self._rth_bucket)
        self._rth_bucket = []
        first = source[0]
        assert self._session is not None
        completed = FiveMinuteBar(
            symbol=first.symbol,
            timestamp=first.timestamp,
            session_date=self._session.session_date,
            open=first.open,
            high=max(item.high for item in source),
            low=min(item.low for item in source),
            close=source[-1].close,
            volume=sum(item.volume for item in source),
            trade_count=sum(item.trade_count for item in source),
            source=first.source,
            feed=first.feed,
            timeframe="5Min",
            adjustment=first.adjustment,
            source_bar_count=5,
        )
        self._five_minute_bars.append(completed)
        if len(self._five_minute_bars) == 1:
            self._opening_levels = calculate_opening_five_minute_levels(
                (completed,), calendar=self._calendar
            )
        return completed

    def _levels(self):
        assert self._session is not None and self._session.market_open is not None
        return build_session_levels(
            session_date=self._session.session_date,
            market_open=self._session.market_open,
            previous_day=self._previous_day,
            premarket=self._premarket_levels,
            opening=self._opening_levels,
        )

    def _update_strategy_state(
        self, completed: FiveMinuteBar
    ) -> tuple[tuple[LevelInteraction, ...], tuple[ReplaySignalEvent, ...]]:
        previous = (
            self._five_minute_bars[-2] if len(self._five_minute_bars) > 1 else None
        )
        interactions = []
        for level in self._levels():
            if completed.timestamp < level.available_from_timestamp:
                continue
            interaction = classify_level_interaction(
                completed,
                level,
                previous_candle=previous,
            )
            if interaction.interaction_type is not InteractionType.NO_INTERACTION:
                interactions.append(interaction)
            if interaction.interaction_type in (
                InteractionType.CLOSE_THROUGH_ABOVE,
                InteractionType.CLOSE_THROUGH_BELOW,
            ):
                self._break_seeds.append(interaction)
        emitted = []
        index = len(self._five_minute_bars) - 1
        index_by_timestamp = {
            item.timestamp: offset
            for offset, item in enumerate(self._five_minute_bars)
        }
        assert self._session is not None and self._session.market_close is not None
        for seed in self._break_seeds:
            if seed.candle_timestamp not in index_by_timestamp:
                raise ReplayInputError("break seed disappeared from session state")
            seed_index = index_by_timestamp[seed.candle_timestamp]
            distance = index - seed_index
            if distance < 1 or distance > 3:
                continue
            follow = calculate_break_follow_through(
                seed,
                tuple(self._five_minute_bars[seed_index + 1 : index + 1]),
            )
            candidate = qualify_base_price_action_candidate(
                seed,
                follow,
                self._session.market_close,
            )
            if (
                candidate.status is BaseSetupStatus.CONFIRMED
                and candidate.setup_identity not in self._emitted_setup_ids
            ):
                signal = self._signal(candidate)
                expected_known_at = completed.timestamp + timedelta(minutes=5)
                if signal.signal_known_at != expected_known_at:
                    raise ReplayInputError("signal attempted to use a future candle")
                self._emitted_setup_ids.add(candidate.setup_identity)
                self._signals.append(signal)
                emitted.append(signal)
        return tuple(interactions), tuple(emitted)

    @staticmethod
    def _signal(candidate) -> ReplaySignalEvent:
        assert candidate.confirmation_type is not None
        assert candidate.confirmation_bar_timestamp is not None
        assert candidate.signal_known_at is not None
        candidate_ids = (
            STAGE14_FORWARD_CANDIDATE_IDS
            if candidate.direction is SetupDirection.SHORT
            else ()
        )
        identity = sha256(
            (
                f"{candidate.setup_identity}|{candidate.signal_known_at.isoformat()}|"
                "incremental-rth-signal-state-v1"
            ).encode()
        ).hexdigest()
        return ReplaySignalEvent(
            event_identity=identity,
            session_date=candidate.session_date,
            event_timestamp=candidate.confirmation_bar_timestamp,
            known_at=candidate.signal_known_at,
            direction=candidate.direction,
            triggering_level_type=candidate.level_type,
            triggering_level_price=candidate.level_price,
            break_timestamp=candidate.break_timestamp,
            break_completed_at=candidate.break_completed_at,
            break_interaction_type=candidate.break_interaction_type,
            confirmation_type=candidate.confirmation_type,
            confirmation_candle_timestamp=candidate.confirmation_bar_timestamp,
            signal_known_at=candidate.signal_known_at,
            setup_identity=candidate.setup_identity,
            stage9_qualification_status=BaseSetupStatus.CONFIRMED,
            same_session_executable=candidate.same_session_executable,
            base_short_membership=candidate.direction is SetupDirection.SHORT,
            eligible_stage14_candidate_ids=candidate_ids,
        )

    def _new_crosses(self, ema_rows, vwap_rows) -> tuple[ReplayCrossEvent, ...]:
        candidates = []
        for item in detect_ema_crosses(ema_rows):
            identity = sha256(
                (
                    f"EMA9_EMA20|{item.session_date}|{item.timestamp.isoformat()}|"
                    f"{item.direction.value}"
                ).encode()
            ).hexdigest()
            candidates.append(
                ReplayCrossEvent(
                    session_date=item.session_date,
                    cross_type=ReplayCrossType.EMA9_EMA20,
                    direction=item.direction.value,
                    event_timestamp=item.timestamp,
                    known_at=item.timestamp + timedelta(minutes=5),
                    event_identity=identity,
                )
            )
        ema9_events, _ = detect_ema9_vwap_crosses(ema_rows, vwap_rows)
        for item in ema9_events:
            candidates.append(
                ReplayCrossEvent(
                    session_date=item.session_date,
                    cross_type=ReplayCrossType.EMA9_VWAP,
                    direction=item.direction.value,
                    event_timestamp=item.cross_timestamp,
                    known_at=item.cross_known_at,
                    event_identity=item.event_identity,
                )
            )
        ema20_events, _ = detect_ema20_vwap_crosses(ema_rows, vwap_rows)
        for item in ema20_events:
            candidates.append(
                ReplayCrossEvent(
                    session_date=item.session_date,
                    cross_type=ReplayCrossType.EMA20_VWAP,
                    direction=item.direction.value,
                    event_timestamp=item.cross_timestamp,
                    known_at=item.cross_known_at,
                    event_identity=item.event_identity,
                )
            )
        emitted = []
        for item in sorted(candidates, key=lambda row: (row.known_at, row.cross_type.value)):
            if item.event_identity in self._seen_cross_ids:
                continue
            self._seen_cross_ids.add(item.event_identity)
            self._cross_counts[item.cross_type] += 1
            emitted.append(item)
        return tuple(emitted)

    def finish_session(self) -> ReplaySessionSummary:
        if self._session is None:
            raise ReplayInputError("no active replay session")
        if self._rth_bucket:
            raise ReplayInputError("session ended with an incomplete five-minute bucket")
        ema_rows = calculate_session_ema(tuple(self._five_minute_bars))
        atr_rows = calculate_session_atr(tuple(self._five_minute_bars))
        summary = ReplaySessionSummary(
            session_date=self._session.session_date,
            raw_bar_count=self._raw_count,
            premarket_bar_count=len(self._premarket_bars),
            rth_one_minute_count=self._rth_count,
            five_minute_count=len(self._five_minute_bars),
            break_seed_count=len(self._break_seeds),
            confirmed_signal_count=len(self._signals),
            executable_signal_count=sum(
                item.same_session_executable for item in self._signals
            ),
            base_short_confirmed_count=sum(
                item.base_short_membership for item in self._signals
            ),
            base_short_executable_count=sum(
                item.base_short_membership and item.same_session_executable
                for item in self._signals
            ),
            ema9_valid_count=sum(item.ema9 is not None for item in ema_rows),
            ema20_valid_count=sum(item.ema20 is not None for item in ema_rows),
            atr14_valid_count=sum(item.atr14 is not None for item in atr_rows),
            ema9_ema20_cross_count=self._cross_counts[ReplayCrossType.EMA9_EMA20],
            ema9_vwap_cross_count=self._cross_counts[ReplayCrossType.EMA9_VWAP],
            ema20_vwap_cross_count=self._cross_counts[ReplayCrossType.EMA20_VWAP],
            previous_day_levels_available=self._previous_day is not None,
            premarket_levels_available=self._premarket_levels is not None,
            opening_levels_available=self._opening_levels is not None,
        )
        self._session = None
        return summary
