"""Deterministic, single-candidate Alpaca paper execution state machine."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, localcontext
from hashlib import sha256
from time import sleep

from spy_research.indicators.atr import ATR_CONTEXT
from spy_research.market import TradingSession
from spy_research.paper.broker import PaperBrokerSession
from spy_research.paper.models import (
    BrokerOrderRecord,
    BrokerOrderRole,
    BrokerOrderStatus,
    BrokerProtectiveOrders,
    PaperCandidate,
    PaperExecutionError,
    PaperExecutionRecord,
    PaperExecutionState,
    TERMINAL_BROKER_ORDER_STATUSES,
)
from spy_research.paper.price_precision import (
    normalize_objective_limit,
    normalize_protective_stop,
    validate_short_protective_prices,
)
from spy_research.shadow import (
    ShadowEventType,
    ShadowPosition,
    ShadowState,
    ShadowTransitionEvent,
)


CLIENT_ORDER_PREFIX = "s14"
MAX_ENTRY_SUBMISSIONS_PER_SESSION = 1
ENTRY_FILL_POLL_INTERVAL_SECONDS = 0.1
ENTRY_FILL_POLL_ATTEMPTS = 50


@dataclass(frozen=True)
class SessionEntrySubmissionState:
    """Immutable broker-submission latch for one XNYS RTH session."""

    session_date: date
    entry_client_order_id: str | None = None
    reconciliation_uncertain: bool = False

    @property
    def consumed(self) -> bool:
        return self.entry_client_order_id is not None


def deterministic_client_order_id(
    *,
    session_date,
    setup_identity: str,
    candidate_id: str,
    role: BrokerOrderRole,
) -> str:
    """Return a <=48 character Alpaca identity derived only from immutable input."""

    material = (
        f"{session_date.isoformat()}|{setup_identity}|{candidate_id}|{role.value}|"
        "stage14-4"
    )
    digest = sha256(material.encode()).hexdigest()[:24]
    role_code = {
        BrokerOrderRole.ENTRY: "ent",
        BrokerOrderRole.PROTECTIVE_OCO: "oco",
        BrokerOrderRole.TARGET: "tgt",
        BrokerOrderRole.STOP: "stp",
        BrokerOrderRole.EOD_FLATTEN: "eod",
    }[role]
    return f"{CLIENT_ORDER_PREFIX}-{session_date:%Y%m%d}-{role_code}-{digest}"


def _updated(record: PaperExecutionRecord, **updates) -> PaperExecutionRecord:
    return PaperExecutionRecord.model_validate({**record.model_dump(), **updates})


class PaperExecutionEngine:
    """Translate selected live shadow entries into paper-only broker actions."""

    def __init__(
        self,
        session: TradingSession,
        *,
        candidate: PaperCandidate,
        qty: int = 1,
        enable_paper_orders: bool = False,
        broker: PaperBrokerSession | None = None,
        fill_poll_waiter: Callable[[float], None] = sleep,
    ) -> None:
        if not session.is_trading_day or session.market_close is None:
            raise PaperExecutionError("paper execution requires an XNYS session")
        if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
            raise PaperExecutionError("paper quantity must be a positive whole share count")
        if enable_paper_orders and broker is None:
            raise PaperExecutionError("enabled paper mode requires a paper broker")
        if not enable_paper_orders and broker is not None:
            raise PaperExecutionError("dry-run paper mode must not receive a broker session")
        self._session = session
        self._candidate = candidate
        self._qty = qty
        self._enabled = enable_paper_orders
        self._broker = broker
        self._fill_poll_waiter = fill_poll_waiter
        self._executions: dict[tuple[str, str], PaperExecutionRecord] = {}
        self._seen_orders: dict[str, BrokerOrderRecord] = {}
        self._actions: list[str] = []
        self._reconciled = not enable_paper_orders
        self._blocked = False
        self._entry_submission_state = SessionEntrySubmissionState(
            session_date=session.session_date
        )

    @property
    def candidate(self) -> PaperCandidate:
        return self._candidate

    @property
    def qty(self) -> int:
        return self._qty

    @property
    def orders_enabled(self) -> bool:
        return self._enabled

    @property
    def maximum_entry_submissions_per_session(self) -> int:
        return MAX_ENTRY_SUBMISSIONS_PER_SESSION

    @property
    def entry_submission_consumed(self) -> bool:
        """Whether this RTH session has already submitted its one entry order."""

        return self._entry_submission_state.consumed

    @property
    def entry_submission_state(self) -> SessionEntrySubmissionState:
        return self._entry_submission_state

    @property
    def executions(self) -> tuple[PaperExecutionRecord, ...]:
        return tuple(self._executions[key] for key in sorted(self._executions))

    @property
    def actions(self) -> tuple[str, ...]:
        return tuple(self._actions)

    def recover(self, shadow_positions: Sequence[ShadowPosition], *, now: datetime) -> None:
        """Rebuild current-session broker state without submitting a past entry."""

        self._require_session_time(now)
        if not self._enabled:
            self._reconciled = True
            return
        assert self._broker is not None
        self._broker.verify_paper_account()
        selected = tuple(
            item
            for item in shadow_positions
            if item.candidate_id == self._candidate.candidate_id
            and item.session_date == self._session.session_date
        )
        open_orders = self._broker.list_open_orders()
        recognized_ids: set[str] = set()
        recovered: list[PaperExecutionRecord] = []
        for position in selected:
            entry_client_id = self._client_id(position, BrokerOrderRole.ENTRY)
            try:
                entry = self._broker.find_order_by_client_id(
                    entry_client_id, role=BrokerOrderRole.ENTRY
                )
            except Exception:
                self._mark_entry_history_uncertain()
                self._block_all(
                    "paper session entry-submission history cannot be reconciled"
                )
            if entry is None:
                continue
            if (
                self.entry_submission_consumed
                and self._entry_submission_state.entry_client_order_id
                != entry.client_order_id
            ):
                self._block_all(
                    "multiple paper entry submissions exist for the current session"
                )
            self._consume_entry_submission(entry.client_order_id)
            recognized_ids.add(entry.client_order_id)
            record = self._record_from_shadow(
                position, state=PaperExecutionState.DRY_RUN_INTENDED
            )
            record = _updated(
                record,
                submitted_timestamp=entry.submitted_at,
                entry_order=entry,
            )
            self._remember_order(entry)
            if entry.status is BrokerOrderStatus.FILLED:
                record = self._with_entry_fill(record, entry)
                oco_client_id = self._client_id(
                    position, BrokerOrderRole.PROTECTIVE_OCO
                )
                target = next(
                    (
                        item
                        for item in open_orders
                        if item.client_order_id == oco_client_id
                        and item.role is BrokerOrderRole.TARGET
                    ),
                    None,
                )
                stop = next(
                    (
                        item
                        for item in open_orders
                        if item.role is BrokerOrderRole.STOP
                        and item.qty == self._qty
                    ),
                    None,
                )
                if target is not None and stop is not None:
                    recognized_ids.update((target.client_order_id, stop.client_order_id))
                    protection = BrokerProtectiveOrders(
                        oco_client_order_id=oco_client_id,
                        target=target,
                        stop=stop,
                    )
                    self._remember_order(target)
                    self._remember_order(stop)
                    record = _updated(
                        record,
                        protective_orders=protection,
                        state=PaperExecutionState.PROTECTIVE_ACTIVE,
                    )
            self._executions[(record.setup_identity, record.candidate_id)] = record
            recovered.append(record)
        unrecognized = tuple(
            item
            for item in open_orders
            if item.client_order_id not in recognized_ids
        )
        if unrecognized:
            self._block_all("paper account contains unreconciled open SPY orders")
        position = self._broker.get_position(observed_at=now)
        expected_qty = sum(
            (item.local_expected_position_qty for item in recovered), Decimal("0")
        )
        if position.qty != expected_qty:
            self._block_all("paper broker position does not match reconstructed state")
        for key, item in tuple(self._executions.items()):
            self._executions[key] = _updated(
                item, broker_reported_position_qty=position.qty
            )
        if sum(item.local_expected_position_qty < 0 for item in recovered) > 1:
            self._block_all("multiple reconstructed paper positions would pyramid SPY")
        self._reconciled = True
        self._actions.append("PAPER_RECONCILIATION_CONFIRMED")
        for key, record in tuple(self._executions.items()):
            if record.state is PaperExecutionState.ENTRY_FILLED_UNPROTECTED:
                self._executions[key] = self._submit_protection(record, now=now)

    def handle_shadow_event(
        self, event: ShadowTransitionEvent, *, now: datetime
    ) -> PaperExecutionRecord | None:
        """Submit only the selected candidate at its accepted actionable entry event."""

        self._require_session_time(now)
        if self._blocked:
            raise PaperExecutionError("paper execution is blocked after reconciliation failure")
        if event.candidate_id != self._candidate.candidate_id:
            return None
        if event.event_type is not ShadowEventType.ENTRY:
            return None
        position = event.position
        if position.state is not ShadowState.ACTIVE:
            return None
        if position.entry_timestamp != event.event_timestamp:
            raise PaperExecutionError("paper entry event timing does not match Stage 14.3")
        if event.event_timestamp >= self._session.market_close:
            raise PaperExecutionError("paper entry cannot be submitted at session end")
        key = (position.setup_identity, position.candidate_id)
        existing = self._executions.get(key)
        if existing is not None:
            return existing
        record = self._record_from_shadow(
            position, state=PaperExecutionState.DRY_RUN_INTENDED
        )
        if not self._enabled:
            self._executions[key] = record
            self._actions.append(
                f"DRY_RUN_ENTRY setup={position.setup_identity} candidate={position.candidate_id} qty={self._qty}"
            )
            return record
        if not self._reconciled:
            raise PaperExecutionError("paper broker must reconcile before new submissions")
        if self.entry_submission_consumed:
            blocked = _updated(
                record,
                state=PaperExecutionState.BLOCKED,
                failure_reason="paper session entry-submission cap already consumed",
            )
            self._executions[key] = blocked
            self._actions.append(
                f"ENTRY_BLOCKED_SESSION_CAP setup={position.setup_identity} "
                f"candidate={position.candidate_id}"
            )
            return blocked
        if any(
            item.local_expected_position_qty < 0
            or item.state
            in (
                PaperExecutionState.ENTRY_SUBMITTED,
                PaperExecutionState.ENTRY_FILLED_UNPROTECTED,
                PaperExecutionState.PROTECTIVE_ACTIVE,
                PaperExecutionState.EOD_FLATTEN_SUBMITTED,
            )
            for item in self._executions.values()
        ):
            raise PaperExecutionError("paper pyramiding and overlapping entries are disabled")
        assert self._broker is not None
        client_id = self._client_id(position, BrokerOrderRole.ENTRY)
        try:
            entry = self._broker.find_order_by_client_id(
                client_id, role=BrokerOrderRole.ENTRY
            )
        except Exception:
            self._mark_entry_history_uncertain()
            self._blocked = True
            raise PaperExecutionError(
                "paper session entry-submission history cannot be reconciled"
            ) from None
        if entry is None:
            try:
                entry = self._broker.submit_market_entry(
                    qty=self._qty, client_order_id=client_id
                )
            except Exception:
                # A failed transport can leave submission acceptance unknowable.
                # Permanently fail closed for the rest of this engine/session.
                self._mark_entry_history_uncertain()
                self._blocked = True
                raise PaperExecutionError(
                    "paper entry submission result is uncertain; session is blocked"
                ) from None
            self._consume_entry_submission(entry.client_order_id)
            local_submission_timestamp = now
            self._actions.append(
                f"ENTRY_SUBMITTED setup={position.setup_identity} candidate={position.candidate_id} qty={self._qty}"
            )
        else:
            self._consume_entry_submission(entry.client_order_id)
            local_submission_timestamp = None
            self._actions.append(
                f"ENTRY_REUSED setup={position.setup_identity} candidate={position.candidate_id}"
            )
        self._validate_entry_identity(entry, client_id)
        self._remember_order(entry)
        record = _updated(
            record,
            state=PaperExecutionState.ENTRY_SUBMITTED,
            local_submission_timestamp=local_submission_timestamp,
            submitted_timestamp=entry.submitted_at,
            entry_order=entry,
        )
        self._executions[key] = record
        if entry.status is BrokerOrderStatus.FILLED:
            record = self._with_entry_fill(record, entry)
            self._executions[key] = record
            record = self._submit_protection(record, now=now)
            self._executions[key] = record
        elif entry.status in TERMINAL_BROKER_ORDER_STATUSES:
            self._fail_record(key, "paper entry terminated without a fill")
        else:
            record = self._poll_entry_fill_and_protect(record, now=now)
            self._executions[key] = record
        return record

    def _poll_entry_fill_and_protect(
        self, record: PaperExecutionRecord, *, now: datetime
    ) -> PaperExecutionRecord:
        """Observe a just-submitted market order without waiting for another bar."""

        assert self._broker is not None
        assert record.entry_order is not None
        previous = record.entry_order
        for _ in range(ENTRY_FILL_POLL_ATTEMPTS):
            self._fill_poll_waiter(ENTRY_FILL_POLL_INTERVAL_SECONDS)
            current = self._broker.get_order(
                previous.broker_order_id, role=BrokerOrderRole.ENTRY
            )
            self._validate_order_progress(previous, current)
            self._remember_order(current)
            if current != previous:
                record = _updated(record, entry_order=current)
                self._executions[(record.setup_identity, record.candidate_id)] = record
                previous = current
            if current.status is BrokerOrderStatus.FILLED:
                record = self._with_entry_fill(record, current)
                self._executions[(record.setup_identity, record.candidate_id)] = record
                return self._submit_protection(record, now=now)
            if current.status in TERMINAL_BROKER_ORDER_STATUSES:
                self._fail_record(
                    (record.setup_identity, record.candidate_id),
                    "paper entry terminated without a fill",
                )
        return record

    def reconcile_broker_state(self, *, now: datetime) -> None:
        """Poll immutable broker order facts and reject conflicting transitions."""

        if not self._enabled:
            return
        self._require_session_time(now)
        if not self._reconciled or self._blocked:
            raise PaperExecutionError("paper broker state is not safely reconciled")
        assert self._broker is not None
        for key, record in tuple(self._executions.items()):
            if record.entry_order is None:
                continue
            entry = self._broker.get_order(
                record.entry_order.broker_order_id, role=BrokerOrderRole.ENTRY
            )
            self._validate_order_progress(record.entry_order, entry)
            self._remember_order(entry)
            if entry != record.entry_order:
                record = _updated(record, entry_order=entry)
            if (
                entry.status is BrokerOrderStatus.FILLED
                and record.actual_fill_price is None
            ):
                record = self._with_entry_fill(record, entry)
                self._executions[key] = record
                record = self._submit_protection(record, now=now)
            if record.protective_orders is not None:
                target = self._broker.get_order(
                    record.protective_orders.target.broker_order_id,
                    role=BrokerOrderRole.TARGET,
                )
                stop = self._broker.get_order(
                    record.protective_orders.stop.broker_order_id,
                    role=BrokerOrderRole.STOP,
                )
                self._validate_order_progress(record.protective_orders.target, target)
                self._validate_order_progress(record.protective_orders.stop, stop)
                if (
                    target.status is BrokerOrderStatus.FILLED
                    and stop.status is BrokerOrderStatus.FILLED
                ):
                    self._fail_record(key, "both paper protective exits reported fills")
                protection = BrokerProtectiveOrders(
                    oco_client_order_id=record.protective_orders.oco_client_order_id,
                    target=target,
                    stop=stop,
                )
                record = _updated(record, protective_orders=protection)
                if (
                    target.status is BrokerOrderStatus.FILLED
                    and record.state is PaperExecutionState.PROTECTIVE_ACTIVE
                ):
                    self._broker.cancel_order(stop.broker_order_id)
                    record = _updated(
                        record,
                        state=PaperExecutionState.TARGET_FILLED,
                        local_expected_position_qty=Decimal("0"),
                        cancel_state="REQUESTED",
                    )
                elif (
                    stop.status is BrokerOrderStatus.FILLED
                    and record.state is PaperExecutionState.PROTECTIVE_ACTIVE
                ):
                    self._broker.cancel_order(target.broker_order_id)
                    record = _updated(
                        record,
                        state=PaperExecutionState.STOP_FILLED,
                        local_expected_position_qty=Decimal("0"),
                        cancel_state="REQUESTED",
                    )
            if record.flatten_order is not None:
                flatten = self._broker.get_order(
                    record.flatten_order.broker_order_id,
                    role=BrokerOrderRole.EOD_FLATTEN,
                )
                self._validate_order_progress(record.flatten_order, flatten)
                record = _updated(record, flatten_order=flatten)
                if flatten.status is BrokerOrderStatus.FILLED:
                    record = _updated(
                        record,
                        state=PaperExecutionState.FLAT,
                        local_expected_position_qty=Decimal("0"),
                        cancel_state="CONFIRMED",
                    )
            self._executions[key] = record
        position = self._broker.get_position(observed_at=now)
        expected = sum(
            (item.local_expected_position_qty for item in self._executions.values()),
            Decimal("0"),
        )
        if position.qty != expected:
            self._block_all("paper broker position differs from local expected quantity")
        for key, record in tuple(self._executions.items()):
            updates = {"broker_reported_position_qty": position.qty}
            if (
                record.state
                in (PaperExecutionState.TARGET_FILLED, PaperExecutionState.STOP_FILLED)
                and position.qty == 0
            ):
                updates.update(state=PaperExecutionState.FLAT, cancel_state="CONFIRMED")
            self._executions[key] = _updated(record, **updates)

    def enforce_session_close(self, *, now: datetime) -> None:
        """Cancel protection and submit a whole-share buy-to-cover at RTH close."""

        self._require_session_time(now)
        if now < self._session.market_close:
            return
        if not self._enabled:
            self._actions.append("DRY_RUN_EOD_FLATTEN_CHECK")
            return
        if not self._reconciled or self._blocked:
            raise PaperExecutionError("cannot flatten unreconciled paper state")
        assert self._broker is not None
        for key, record in tuple(self._executions.items()):
            if record.state in (
                PaperExecutionState.EOD_FLATTEN_SUBMITTED,
                PaperExecutionState.FLAT,
            ):
                continue
            if record.state is PaperExecutionState.ENTRY_SUBMITTED:
                assert record.entry_order is not None
                self._broker.cancel_order(record.entry_order.broker_order_id)
                self._executions[key] = _updated(
                    record, state=PaperExecutionState.FLAT, cancel_state="REQUESTED"
                )
                continue
            if record.local_expected_position_qty >= 0:
                continue
            if record.protective_orders is not None:
                self._broker.cancel_order(record.protective_orders.target.broker_order_id)
                self._broker.cancel_order(record.protective_orders.stop.broker_order_id)
            position = self._broker.get_position(observed_at=now)
            if position.qty != -Decimal(self._qty):
                self._fail_record(key, "paper position mismatch prevents safe EOD flatten")
            flatten_id = self._client_id_from_record(record, BrokerOrderRole.EOD_FLATTEN)
            flatten = self._broker.find_order_by_client_id(
                flatten_id, role=BrokerOrderRole.EOD_FLATTEN
            )
            if flatten is None:
                flatten = self._broker.submit_market_flatten(
                    qty=self._qty, client_order_id=flatten_id
                )
            self._remember_order(flatten)
            self._executions[key] = _updated(
                record,
                flatten_order=flatten,
                state=PaperExecutionState.EOD_FLATTEN_SUBMITTED,
                cancel_state="REQUESTED",
            )
            self._actions.append(
                f"EOD_FLATTEN_SUBMITTED setup={record.setup_identity} qty={self._qty}"
            )

    def _record_from_shadow(
        self, position: ShadowPosition, *, state: PaperExecutionState
    ) -> PaperExecutionRecord:
        if position.candidate_id != self._candidate.candidate_id:
            raise PaperExecutionError("shadow event does not match selected paper candidate")
        if (
            position.entry_timestamp is None
            or position.entry_price is None
            or position.confirmation_atr14 is None
            or position.confirmation_atr14 <= 0
            or position.target_price is None
        ):
            raise PaperExecutionError("shadow candidate is not executable for paper entry")
        return PaperExecutionRecord(
            session_date=position.session_date,
            setup_identity=position.setup_identity,
            candidate_id=position.candidate_id,
            intended_qty=self._qty,
            intended_entry_timestamp=position.entry_timestamp,
            intended_reference_price=position.entry_price,
            confirmation_atr14=position.confirmation_atr14,
            stop_multiplier=position.stop_multiplier,
            objective_price=position.target_price,
            state=state,
        )

    def _with_entry_fill(
        self, record: PaperExecutionRecord, entry: BrokerOrderRecord
    ) -> PaperExecutionRecord:
        if (
            entry.status is not BrokerOrderStatus.FILLED
            or entry.avg_fill_price is None
            or entry.filled_at is None
        ):
            raise PaperExecutionError("paper entry fill is incomplete")
        with localcontext(ATR_CONTEXT):
            stop = entry.avg_fill_price + (
                record.confirmation_atr14 * record.stop_multiplier
            )
            slippage = entry.avg_fill_price - record.intended_reference_price
        if record.objective_price >= entry.avg_fill_price or stop <= entry.avg_fill_price:
            raise PaperExecutionError("actual paper fill cannot support frozen short exits")
        broker_stop = normalize_protective_stop(stop, position_side="short")
        broker_target = normalize_objective_limit(
            record.objective_price, position_side="short"
        )
        validate_short_protective_prices(
            fill_price=entry.avg_fill_price,
            theoretical_stop=stop,
            theoretical_target=record.objective_price,
            broker_stop=broker_stop,
            broker_target=broker_target,
        )
        return _updated(
            record,
            state=PaperExecutionState.ENTRY_FILLED_UNPROTECTED,
            entry_order=entry,
            actual_fill_timestamp=entry.filled_at,
            actual_fill_price=entry.avg_fill_price,
            actual_fill_qty=entry.filled_qty,
            fill_slippage=slippage,
            protective_stop_price=stop,
            protective_target_price=record.objective_price,
            broker_stop_price=broker_stop,
            broker_target_price=broker_target,
            local_expected_position_qty=-Decimal(self._qty),
        )

    def _submit_protection(
        self, record: PaperExecutionRecord, *, now: datetime
    ) -> PaperExecutionRecord:
        assert self._broker is not None
        if record.protective_orders is not None:
            return record
        position = self._broker.get_position(observed_at=now)
        if position.qty != -Decimal(self._qty):
            raise PaperExecutionError("filled paper entry does not reconcile to short position")
        assert record.protective_target_price is not None
        assert record.protective_stop_price is not None
        assert record.broker_target_price is not None
        assert record.broker_stop_price is not None
        client_id = self._client_id_from_record(
            record, BrokerOrderRole.PROTECTIVE_OCO
        )
        protection = self._broker.submit_protective_oco(
            qty=self._qty,
            target_price=record.broker_target_price,
            stop_price=record.broker_stop_price,
            client_order_id=client_id,
        )
        if protection.oco_client_order_id != client_id:
            raise PaperExecutionError("paper OCO client identity changed")
        target = self._broker.get_order(
            protection.target.broker_order_id, role=BrokerOrderRole.TARGET
        )
        stop = self._broker.get_order(
            protection.stop.broker_order_id, role=BrokerOrderRole.STOP
        )
        self._validate_order_progress(protection.target, target)
        self._validate_order_progress(protection.stop, stop)
        protection = BrokerProtectiveOrders(
            oco_client_order_id=client_id,
            target=target,
            stop=stop,
        )
        self._remember_order(target)
        self._remember_order(stop)
        self._actions.append(
            f"PROTECTIVE_OCO_SUBMITTED setup={record.setup_identity} qty={self._qty}"
        )
        return _updated(
            record,
            protective_orders=protection,
            broker_reported_position_qty=position.qty,
            state=PaperExecutionState.PROTECTIVE_ACTIVE,
        )

    def _validate_entry_identity(
        self, order: BrokerOrderRecord, client_id: str
    ) -> None:
        if (
            order.client_order_id != client_id
            or order.role is not BrokerOrderRole.ENTRY
            or order.symbol != "SPY"
            or order.side != "sell"
            or order.order_type != "market"
            or order.qty != self._qty
        ):
            raise PaperExecutionError("paper entry order conflicts with immutable intent")

    def _remember_order(self, order: BrokerOrderRecord) -> None:
        previous = self._seen_orders.get(order.broker_order_id)
        if previous is not None:
            self._validate_order_progress(previous, order)
        self._seen_orders[order.broker_order_id] = order

    @staticmethod
    def _validate_order_progress(
        previous: BrokerOrderRecord, current: BrokerOrderRecord
    ) -> None:
        if (
            previous.broker_order_id != current.broker_order_id
            or previous.client_order_id != current.client_order_id
            or previous.symbol != current.symbol
            or previous.role is not current.role
            or previous.side != current.side
            or previous.order_type != current.order_type
            or previous.qty != current.qty
        ):
            raise PaperExecutionError("conflicting paper broker order identity")
        if current.filled_qty < previous.filled_qty:
            raise PaperExecutionError("paper broker filled quantity regressed")
        if previous.status in TERMINAL_BROKER_ORDER_STATUSES and current != previous:
            raise PaperExecutionError("terminal paper broker order changed")
        progress = {
            BrokerOrderStatus.ACCEPTED: 0,
            BrokerOrderStatus.NEW: 1,
            BrokerOrderStatus.PARTIALLY_FILLED: 2,
            BrokerOrderStatus.PENDING_CANCEL: 2,
            BrokerOrderStatus.FILLED: 3,
            BrokerOrderStatus.CANCELED: 3,
            BrokerOrderStatus.REJECTED: 3,
            BrokerOrderStatus.EXPIRED: 3,
        }
        if progress[current.status] < progress[previous.status]:
            raise PaperExecutionError("paper broker order status regressed")
        if (
            current.status is previous.status
            and current.filled_qty == previous.filled_qty
            and current != previous
        ):
            raise PaperExecutionError("conflicting repeated paper broker update")

    def _client_id(
        self, position: ShadowPosition, role: BrokerOrderRole
    ) -> str:
        return deterministic_client_order_id(
            session_date=position.session_date,
            setup_identity=position.setup_identity,
            candidate_id=position.candidate_id,
            role=role,
        )

    def _client_id_from_record(
        self, record: PaperExecutionRecord, role: BrokerOrderRole
    ) -> str:
        return deterministic_client_order_id(
            session_date=record.session_date,
            setup_identity=record.setup_identity,
            candidate_id=record.candidate_id,
            role=role,
        )

    def _require_session_time(self, timestamp: datetime) -> None:
        if timestamp.utcoffset() is None:
            raise PaperExecutionError("paper execution time must be timezone-aware")
        if timestamp.astimezone(self._session.market_close.tzinfo).date() != self._session.session_date:
            raise PaperExecutionError("paper execution cannot bridge trading sessions")

    def _consume_entry_submission(self, client_order_id: str) -> None:
        previous = self._entry_submission_state.entry_client_order_id
        if previous is not None and previous != client_order_id:
            self._block_all(
                "multiple paper entry submissions exist for the current session"
            )
        self._entry_submission_state = SessionEntrySubmissionState(
            session_date=self._session.session_date,
            entry_client_order_id=client_order_id,
        )

    def _mark_entry_history_uncertain(self) -> None:
        self._entry_submission_state = SessionEntrySubmissionState(
            session_date=self._session.session_date,
            entry_client_order_id=self._entry_submission_state.entry_client_order_id,
            reconciliation_uncertain=True,
        )

    def _fail_record(self, key: tuple[str, str], reason: str) -> None:
        record = self._executions[key]
        self._executions[key] = _updated(
            record, state=PaperExecutionState.BLOCKED, failure_reason=reason
        )
        self._blocked = True
        raise PaperExecutionError(reason)

    def _block_all(self, reason: str) -> None:
        for key, record in tuple(self._executions.items()):
            self._executions[key] = _updated(
                record, state=PaperExecutionState.BLOCKED, failure_reason=reason
            )
        self._blocked = True
        raise PaperExecutionError(reason)
