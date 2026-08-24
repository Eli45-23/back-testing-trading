"""Incremental two-candidate shadow state machine for completed RTH minutes."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta
from decimal import Decimal, localcontext

from spy_research.data.schemas import RawBarRecord
from spy_research.execution import AmbiguityMetadata
from spy_research.indicators.atr import ATR_CONTEXT
from spy_research.interactions import AvailableLevel, LevelType
from spy_research.live import LiveAdapterUpdate, LiveSignalEvent
from spy_research.market import MarketSessionClassifier, SessionType, TradingSession
from spy_research.replay import STAGE14_FORWARD_CANDIDATE_IDS
from spy_research.shadow.models import (
    ShadowEventType,
    ShadowInputError,
    ShadowPosition,
    ShadowState,
    ShadowTransitionEvent,
    TERMINAL_SHADOW_STATES,
)


CANDIDATE_MULTIPLIERS = {
    STAGE14_FORWARD_CANDIDATE_IDS[0]: Decimal("0.75"),
    STAGE14_FORWARD_CANDIDATE_IDS[1]: Decimal("1.00"),
}


def _updated(position: ShadowPosition, **updates) -> ShadowPosition:
    return ShadowPosition.model_validate({**position.model_dump(), **updates})


class ShadowForwardStateMachine:
    """Consume accepted bars/signals without access to future state."""

    def __init__(self, session: TradingSession) -> None:
        if not session.is_trading_day or session.market_close is None:
            raise ShadowInputError("shadow testing requires an XNYS session")
        self._session = session
        self._classifier = MarketSessionClassifier()
        self._positions: dict[tuple[str, str], ShadowPosition] = {}
        self._signals: dict[str, LiveSignalEvent] = {}
        self._seen_bars: dict[datetime, RawBarRecord] = {}
        self._last_rth_timestamp: datetime | None = None

    @property
    def positions(self) -> tuple[ShadowPosition, ...]:
        return tuple(self._positions[key] for key in sorted(self._positions))

    def consume_live_update(
        self,
        update: LiveAdapterUpdate,
        *,
        available_levels: Sequence[AvailableLevel],
    ) -> tuple[ShadowTransitionEvent, ...]:
        events = []
        if update.normalized_bar is not None:
            events.extend(self.process_bar(update.normalized_bar))
        for signal in update.signal_events:
            events.extend(self.register_signal(signal, available_levels=available_levels))
        return tuple(events)

    def register_signal(
        self,
        signal: LiveSignalEvent,
        *,
        available_levels: Sequence[AvailableLevel],
    ) -> tuple[ShadowTransitionEvent, ...]:
        existing = self._signals.get(signal.setup_identity)
        if existing is not None:
            if existing == signal:
                return ()
            raise ShadowInputError("conflicting duplicate live signal")
        if signal.session_date != self._session.session_date:
            raise ShadowInputError("shadow signal belongs to another session")
        self._signals[signal.setup_identity] = signal
        if not signal.base_short_membership:
            if signal.stage13_forward_test_candidate_ids:
                raise ShadowInputError("LONG signal cannot contain Stage 13 candidates")
            return ()
        if signal.stage13_forward_test_candidate_ids != STAGE14_FORWARD_CANDIDATE_IDS:
            raise ShadowInputError("BASE_SHORT candidate identities changed")
        target_price, target_types = self._select_objective(signal, available_levels)
        events = []
        for candidate_id in STAGE14_FORWARD_CANDIDATE_IDS:
            key = (signal.setup_identity, candidate_id)
            if key in self._positions:
                raise ShadowInputError("shadow candidate identity already exists")
            state = (
                ShadowState.ENTRY_UNAVAILABLE_SESSION_END
                if signal.signal_known_at >= self._session.market_close
                else ShadowState.PENDING_ENTRY
            )
            position = ShadowPosition(
                session_date=signal.session_date,
                setup_identity=signal.setup_identity,
                candidate_id=candidate_id,
                signal_known_at=signal.signal_known_at,
                confirmation_timestamp=signal.confirmation_timestamp,
                confirmation_close=signal.confirmation_close,
                confirmation_atr14=signal.atr14,
                stop_multiplier=CANDIDATE_MULTIPLIERS[candidate_id],
                triggering_level_type=signal.triggering_level_type,
                triggering_level_price=signal.triggering_level_price,
                target_level_types=target_types,
                target_price=target_price,
                state=state,
            )
            self._positions[key] = position
            event_type = (
                ShadowEventType.UNAVAILABLE
                if state is ShadowState.ENTRY_UNAVAILABLE_SESSION_END
                else ShadowEventType.CANDIDATE_CREATED
            )
            events.append(
                ShadowTransitionEvent.from_position(
                    event_type, signal.signal_known_at, position
                )
            )
        return tuple(events)

    def process_bar(self, bar: RawBarRecord) -> tuple[ShadowTransitionEvent, ...]:
        existing = self._seen_bars.get(bar.timestamp)
        if existing is not None:
            if existing == bar:
                return ()
            raise ShadowInputError("conflicting duplicate shadow minute")
        classified = self._classifier.classify(bar)
        if classified.session_date != self._session.session_date:
            if any(item.state not in TERMINAL_SHADOW_STATES for item in self.positions):
                raise ShadowInputError("shadow position cannot carry overnight")
            raise ShadowInputError("shadow bar belongs to another session")
        if classified.session_type is not SessionType.RTH:
            return ()
        if self._last_rth_timestamp is not None and bar.timestamp < self._last_rth_timestamp:
            raise ShadowInputError("shadow RTH minutes must be chronological")
        self._seen_bars[bar.timestamp] = bar
        self._last_rth_timestamp = bar.timestamp
        events = []
        for key in sorted(self._positions):
            current = self._positions[key]
            if current.state in TERMINAL_SHADOW_STATES:
                continue
            if current.state is ShadowState.PENDING_ENTRY:
                if bar.timestamp < current.signal_known_at:
                    continue
                entered, entry_event = self._enter(current, bar)
                self._positions[key] = entered
                events.append(entry_event)
                current = entered
                if current.state in TERMINAL_SHADOW_STATES:
                    continue
            updated, exit_event = self._observe(current, bar)
            self._positions[key] = updated
            if exit_event is not None:
                events.append(exit_event)
        return tuple(events)

    def _enter(
        self, pending: ShadowPosition, bar: RawBarRecord
    ) -> tuple[ShadowPosition, ShadowTransitionEvent]:
        if pending.state is not ShadowState.PENDING_ENTRY:
            raise ShadowInputError("only pending candidates may enter")
        common = dict(entry_timestamp=bar.timestamp, entry_price=bar.open)
        if pending.confirmation_atr14 is None or pending.confirmation_atr14 <= 0:
            entered = _updated(
                pending, **common, state=ShadowState.UNAVAILABLE_ATR
            )
            return entered, ShadowTransitionEvent.from_position(
                ShadowEventType.UNAVAILABLE, bar.timestamp, entered
            )
        with localcontext(ATR_CONTEXT):
            risk = pending.confirmation_atr14 * pending.stop_multiplier
            stop = bar.open + risk
        if pending.target_price is None:
            entered = _updated(
                pending,
                **common,
                risk_distance=risk,
                stop_price=stop,
                state=ShadowState.UNAVAILABLE_OBJECTIVE_LEVEL,
            )
            return entered, ShadowTransitionEvent.from_position(
                ShadowEventType.UNAVAILABLE, bar.timestamp, entered
            )
        with localcontext(ATR_CONTEXT):
            target_distance = bar.open - pending.target_price
            target_r = target_distance / risk
        entered = _updated(
            pending,
            **common,
            risk_distance=risk,
            stop_price=stop,
            target_distance=target_distance,
            target_r=target_r,
            state=ShadowState.ACTIVE,
        )
        return entered, ShadowTransitionEvent.from_position(
            ShadowEventType.ENTRY, bar.timestamp, entered
        )

    def _observe(
        self, active: ShadowPosition, bar: RawBarRecord
    ) -> tuple[ShadowPosition, ShadowTransitionEvent | None]:
        if active.state is not ShadowState.ACTIVE:
            raise ShadowInputError("only active candidates may observe price")
        assert active.entry_timestamp is not None and active.entry_price is not None
        assert active.stop_price is not None and active.target_price is not None
        assert active.risk_distance is not None
        observed = active.bars_observed + 1
        minutes = int((bar.timestamp - active.entry_timestamp).total_seconds() // 60)
        stop_touched = bar.high >= active.stop_price
        target_touched = bar.low <= active.target_price
        if stop_touched and target_touched:
            final = _updated(
                active,
                state=ShadowState.AMBIGUOUS_BOTH_TOUCHED,
                exit_timestamp=bar.timestamp,
                holding_minutes=minutes,
                bars_observed=observed,
                ambiguity=AmbiguityMetadata(
                    timestamp=bar.timestamp,
                    open=bar.open,
                    high=bar.high,
                    low=bar.low,
                    close=bar.close,
                ),
            )
            return final, ShadowTransitionEvent.from_position(
                ShadowEventType.EXIT, bar.timestamp, final
            )
        if stop_touched or target_touched:
            state = ShadowState.STOP_EXIT if stop_touched else ShadowState.TARGET_EXIT
            exit_price = active.stop_price if stop_touched else active.target_price
            with localcontext(ATR_CONTEXT):
                pnl = active.entry_price - exit_price
                realized_r = Decimal("-1") if stop_touched else pnl / active.risk_distance
            final = _updated(
                active,
                state=state,
                exit_timestamp=bar.timestamp,
                exit_price=exit_price,
                realized_price_pnl=pnl,
                realized_r=realized_r,
                holding_minutes=minutes,
                bars_observed=observed,
            )
            return final, ShadowTransitionEvent.from_position(
                ShadowEventType.EXIT, bar.timestamp, final
            )
        assert self._session.market_close is not None
        if bar.timestamp == self._session.market_close - timedelta(minutes=1):
            with localcontext(ATR_CONTEXT):
                pnl = active.entry_price - bar.close
                realized_r = pnl / active.risk_distance
            final = _updated(
                active,
                state=ShadowState.EOD_EXIT,
                exit_timestamp=bar.timestamp,
                exit_price=bar.close,
                realized_price_pnl=pnl,
                realized_r=realized_r,
                holding_minutes=minutes,
                bars_observed=observed,
            )
            return final, ShadowTransitionEvent.from_position(
                ShadowEventType.EXIT, bar.timestamp, final
            )
        return _updated(active, bars_observed=observed), None

    @staticmethod
    def _select_objective(
        signal: LiveSignalEvent,
        levels: Sequence[AvailableLevel],
    ) -> tuple[Decimal | None, tuple[LevelType, ...]]:
        known = tuple(
            item
            for item in levels
            if item.session_date == signal.session_date
            and item.available_from_timestamp <= signal.signal_known_at
        )
        directional = tuple(
            item
            for item in known
            if item.level_price < signal.confirmation_close
            and item.level_type is not signal.triggering_level_type
            and item.level_price != signal.triggering_level_price
        )
        if not directional:
            return None, ()
        price = max(item.level_price for item in directional)
        types = tuple(
            level_type
            for level_type in LevelType
            if any(
                item.level_type is level_type and item.level_price == price
                for item in directional
            )
        )
        return price, types
