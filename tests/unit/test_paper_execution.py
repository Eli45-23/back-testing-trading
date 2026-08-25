from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import httpx
import pytest
from pydantic import SecretStr, ValidationError

from spy_research.cli import build_parser
from spy_research.config import AlpacaEnvironment
from spy_research.data import RawBarRecord
from spy_research.interactions import AvailableLevel, LevelType
from spy_research.live import LiveSignalEvent
from spy_research.market import XNYSCalendar
from spy_research.paper import (
    ALPACA_PAPER_BASE_URL,
    AlpacaPaperBroker,
    BrokerOrderRecord,
    BrokerOrderRole,
    BrokerOrderStatus,
    BrokerPositionRecord,
    BrokerProtectiveOrders,
    PaperCandidate,
    PaperExecutionEngine,
    PaperExecutionError,
    PaperExecutionState,
    PaperRunReport,
    deterministic_client_order_id,
    paper_execution_report_hash,
)
from spy_research.replay import STAGE14_FORWARD_CANDIDATE_IDS
from spy_research.shadow import ShadowForwardStateMachine, ShadowTransitionEvent
from spy_research.strategy.models import SetupDirection


CALENDAR = XNYSCalendar()
SESSION_DATE = date(2026, 8, 19)
SESSION = CALENDAR.session_for_date(SESSION_DATE)
assert SESSION.market_open is not None and SESSION.market_close is not None
OPEN = SESSION.market_open
KNOWN = OPEN + timedelta(minutes=30)


def signal(identity: str = "setup-short") -> LiveSignalEvent:
    return LiveSignalEvent(
        session_date=SESSION_DATE,
        signal_identity=f"signal-{identity}",
        setup_identity=identity,
        direction=SetupDirection.SHORT,
        triggering_level_type=LevelType.PDH,
        triggering_level_price=Decimal("100"),
        break_timestamp=KNOWN - timedelta(minutes=10),
        confirmation_timestamp=KNOWN - timedelta(minutes=5),
        signal_known_at=KNOWN,
        confirmation_close=Decimal("101"),
        atr14=Decimal("2"),
        base_short_membership=True,
        stage13_forward_test_candidate_ids=STAGE14_FORWARD_CANDIDATE_IDS,
    )


def levels() -> tuple[AvailableLevel, ...]:
    return (
        AvailableLevel(
            session_date=SESSION_DATE,
            level_type=LevelType.PDH,
            level_price=Decimal("100"),
            available_from_timestamp=OPEN,
        ),
        AvailableLevel(
            session_date=SESSION_DATE,
            level_type=LevelType.PDC,
            level_price=Decimal("98"),
            available_from_timestamp=OPEN,
        ),
    )


def bar(timestamp: datetime, *, open: str = "100") -> RawBarRecord:
    return RawBarRecord(
        symbol="SPY",
        timestamp=timestamp,
        open=Decimal(open),
        high=Decimal("100.5"),
        low=Decimal("99"),
        close=Decimal("100"),
        volume=100,
        trade_count=10,
        vwap=Decimal("100"),
        source="alpaca",
        feed="sip",
        timeframe="1Min",
        adjustment="raw",
    )


def entry_event(
    candidate: PaperCandidate = PaperCandidate.ATR_0_75,
    *,
    identity: str = "setup-short",
) -> ShadowTransitionEvent:
    machine = ShadowForwardStateMachine(SESSION)
    machine.register_signal(signal(identity), available_levels=levels())
    events = machine.process_bar(bar(KNOWN))
    return next(item for item in events if item.candidate_id == candidate.candidate_id)


class FakePaperBroker:
    def __init__(self, *, auto_fill_entry: bool = False) -> None:
        self.auto_fill_entry = auto_fill_entry
        self.verified = False
        self.position_qty = Decimal("0")
        self.orders: dict[str, BrokerOrderRecord] = {}
        self.by_client: dict[str, str] = {}
        self.entry_submissions = 0
        self.oco_submissions = 0
        self.flatten_submissions = 0
        self.canceled: list[str] = []

    def verify_paper_account(self) -> None:
        self.verified = True

    def find_order_by_client_id(self, client_order_id, *, role):
        broker_id = self.by_client.get(client_order_id)
        if broker_id is None:
            return None
        order = self.orders[broker_id]
        return order.model_copy(update={"role": role})

    def list_open_orders(self):
        return tuple(
            item
            for item in self.orders.values()
            if item.status not in {
                BrokerOrderStatus.FILLED,
                BrokerOrderStatus.CANCELED,
                BrokerOrderStatus.REJECTED,
                BrokerOrderStatus.EXPIRED,
            }
        )

    def get_position(self, *, observed_at):
        return BrokerPositionRecord(qty=self.position_qty, observed_at=observed_at)

    def submit_market_entry(self, *, qty, client_order_id):
        self.entry_submissions += 1
        status = (
            BrokerOrderStatus.FILLED
            if self.auto_fill_entry
            else BrokerOrderStatus.ACCEPTED
        )
        order = make_order(
            broker_id=f"entry-{self.entry_submissions}",
            client_id=client_order_id,
            role=BrokerOrderRole.ENTRY,
            side="sell",
            order_type="market",
            status=status,
            qty=qty,
            price="100.25" if self.auto_fill_entry else None,
        )
        self._store(order)
        if self.auto_fill_entry:
            self.position_qty = -Decimal(qty)
        return order

    def submit_protective_oco(
        self, *, qty, target_price, stop_price, client_order_id
    ):
        self.oco_submissions += 1
        target = make_order(
            broker_id=f"target-{self.oco_submissions}",
            client_id=client_order_id,
            role=BrokerOrderRole.TARGET,
            side="buy",
            order_type="limit",
            status=BrokerOrderStatus.NEW,
            qty=qty,
            limit_price=target_price,
        )
        stop = make_order(
            broker_id=f"stop-{self.oco_submissions}",
            client_id=f"broker-child-{self.oco_submissions}",
            role=BrokerOrderRole.STOP,
            side="buy",
            order_type="stop",
            status=BrokerOrderStatus.NEW,
            qty=qty,
            stop_price=stop_price,
        )
        self._store(target)
        self._store(stop)
        return BrokerProtectiveOrders(
            oco_client_order_id=client_order_id, target=target, stop=stop
        )

    def get_order(self, broker_order_id, *, role):
        return self.orders[broker_order_id].model_copy(update={"role": role})

    def cancel_order(self, broker_order_id):
        self.canceled.append(broker_order_id)
        current = self.orders[broker_order_id]
        if current.status is not BrokerOrderStatus.FILLED:
            self.orders[broker_order_id] = current.model_copy(
                update={"status": BrokerOrderStatus.CANCELED}
            )

    def submit_market_flatten(self, *, qty, client_order_id):
        self.flatten_submissions += 1
        order = make_order(
            broker_id=f"flatten-{self.flatten_submissions}",
            client_id=client_order_id,
            role=BrokerOrderRole.EOD_FLATTEN,
            side="buy",
            order_type="market",
            status=BrokerOrderStatus.ACCEPTED,
            qty=qty,
        )
        self._store(order)
        return order

    def fill(self, broker_order_id: str, price: str, *, position_qty: str) -> None:
        current = self.orders[broker_order_id]
        self.orders[broker_order_id] = current.model_copy(
            update={
                "status": BrokerOrderStatus.FILLED,
                "filled_qty": Decimal(current.qty),
                "avg_fill_price": Decimal(price),
                "filled_at": KNOWN + timedelta(minutes=1),
            }
        )
        self.position_qty = Decimal(position_qty)

    def _store(self, order: BrokerOrderRecord) -> None:
        self.orders[order.broker_order_id] = order
        self.by_client[order.client_order_id] = order.broker_order_id


def make_order(
    *,
    broker_id: str,
    client_id: str,
    role: BrokerOrderRole,
    side: str,
    order_type: str,
    status: BrokerOrderStatus,
    qty: int = 1,
    price: str | None = None,
    limit_price: Decimal | None = None,
    stop_price: Decimal | None = None,
) -> BrokerOrderRecord:
    filled = status is BrokerOrderStatus.FILLED
    return BrokerOrderRecord(
        broker_order_id=broker_id,
        client_order_id=client_id,
        side=side,
        order_type=order_type,
        role=role,
        status=status,
        qty=qty,
        filled_qty=Decimal(qty) if filled else Decimal("0"),
        avg_fill_price=Decimal(price) if price is not None else None,
        submitted_at=KNOWN,
        filled_at=KNOWN + timedelta(seconds=1) if filled else None,
        limit_price=limit_price,
        stop_price=stop_price,
    )


def enabled_engine(
    broker: FakePaperBroker,
    candidate: PaperCandidate = PaperCandidate.ATR_0_75,
    *,
    qty: int = 1,
) -> PaperExecutionEngine:
    engine = PaperExecutionEngine(
        SESSION,
        candidate=candidate,
        qty=qty,
        enable_paper_orders=True,
        broker=broker,
    )
    engine.recover((), now=KNOWN)
    return engine


def test_candidate_must_be_explicit_enum_and_only_two_are_accepted() -> None:
    assert tuple(item.value for item in PaperCandidate) == ("ATR_0_75", "ATR_1_00")
    with pytest.raises(ValueError):
        PaperCandidate("BEST")


def test_paper_cli_requires_explicit_candidate_and_defaults_to_safe_mode() -> None:
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["paper-trade-live"])
    args = parser.parse_args(
        ["paper-trade-live", "--candidate", "ATR_0_75"]
    )
    assert args.qty == 1
    assert not args.enable_paper_orders
    with pytest.raises(SystemExit):
        parser.parse_args(
            ["paper-trade-live", "--candidate", "ATR_0_75", "--symbol", "AAPL"]
        )


def test_default_is_one_whole_share_and_invalid_quantity_fails() -> None:
    engine = PaperExecutionEngine(SESSION, candidate=PaperCandidate.ATR_0_75)
    assert engine.qty == 1
    for invalid in (0, -1, 1.5, True):
        with pytest.raises(PaperExecutionError, match="positive whole"):
            PaperExecutionEngine(
                SESSION, candidate=PaperCandidate.ATR_0_75, qty=invalid
            )


def test_dry_run_submits_zero_orders_and_retains_intended_action() -> None:
    engine = PaperExecutionEngine(SESSION, candidate=PaperCandidate.ATR_0_75)
    record = engine.handle_shadow_event(entry_event(), now=KNOWN)
    assert record is not None
    assert record.state is PaperExecutionState.DRY_RUN_INTENDED
    assert record.intended_reference_price == Decimal("100")
    assert record.entry_order is None
    assert engine.actions[0].startswith("DRY_RUN_ENTRY")


def test_enabled_mode_requires_reconciliation_before_submission() -> None:
    broker = FakePaperBroker()
    engine = PaperExecutionEngine(
        SESSION,
        candidate=PaperCandidate.ATR_0_75,
        enable_paper_orders=True,
        broker=broker,
    )
    with pytest.raises(PaperExecutionError, match="reconcile"):
        engine.handle_shadow_event(entry_event(), now=KNOWN)
    assert broker.entry_submissions == 0


def test_market_entry_and_deterministic_client_order_id_are_exact() -> None:
    broker = FakePaperBroker()
    engine = enabled_engine(broker)
    record = engine.handle_shadow_event(entry_event(), now=KNOWN)
    assert record is not None and record.entry_order is not None
    expected = deterministic_client_order_id(
        session_date=SESSION_DATE,
        setup_identity="setup-short",
        candidate_id=PaperCandidate.ATR_0_75.candidate_id,
        role=BrokerOrderRole.ENTRY,
    )
    assert record.entry_order.client_order_id == expected
    assert len(expected) <= 48
    assert record.entry_order.side == "sell"
    assert record.entry_order.order_type == "market"
    assert broker.entry_submissions == 1
    identities = {
        deterministic_client_order_id(
            session_date=SESSION_DATE,
            setup_identity="setup-short",
            candidate_id=PaperCandidate.ATR_0_75.candidate_id,
            role=role,
        )
        for role in (
            BrokerOrderRole.ENTRY,
            BrokerOrderRole.PROTECTIVE_OCO,
            BrokerOrderRole.EOD_FLATTEN,
        )
    }
    assert len(identities) == 3


def test_duplicate_signal_and_reconnect_do_not_duplicate_order() -> None:
    broker = FakePaperBroker()
    engine = enabled_engine(broker)
    event = entry_event()
    first = engine.handle_shadow_event(event, now=KNOWN)
    second = engine.handle_shadow_event(event, now=KNOWN + timedelta(seconds=1))
    assert first == second
    assert broker.entry_submissions == 1


def test_first_submission_consumes_one_per_session_cap_and_blocks_second_active_signal() -> None:
    broker = FakePaperBroker()
    engine = enabled_engine(broker)
    first = engine.handle_shadow_event(entry_event(identity="first"), now=KNOWN)
    second = engine.handle_shadow_event(entry_event(identity="second"), now=KNOWN)

    assert first is not None and first.state is PaperExecutionState.ENTRY_SUBMITTED
    assert second is not None and second.state is PaperExecutionState.BLOCKED
    assert second.failure_reason == "paper session entry-submission cap already consumed"
    assert engine.maximum_entry_submissions_per_session == 1
    assert engine.entry_submission_consumed
    assert broker.entry_submissions == 1
    assert engine.actions[-1].startswith("ENTRY_BLOCKED_SESSION_CAP")


@pytest.mark.parametrize("exit_role", (BrokerOrderRole.TARGET, BrokerOrderRole.STOP))
def test_completed_first_trade_still_blocks_a_second_entry(exit_role) -> None:
    broker = FakePaperBroker(auto_fill_entry=True)
    engine = enabled_engine(broker)
    first = engine.handle_shadow_event(entry_event(identity="first"), now=KNOWN)
    assert first is not None and first.protective_orders is not None
    exit_order = (
        first.protective_orders.target
        if exit_role is BrokerOrderRole.TARGET
        else first.protective_orders.stop
    )
    broker.fill(exit_order.broker_order_id, "99", position_qty="0")
    engine.reconcile_broker_state(now=KNOWN + timedelta(minutes=1))
    assert engine.executions[0].state is PaperExecutionState.FLAT

    second = engine.handle_shadow_event(
        entry_event(identity="second"), now=KNOWN + timedelta(minutes=2)
    )
    assert second is not None and second.state is PaperExecutionState.BLOCKED
    assert broker.entry_submissions == 1


def test_eod_exit_and_rejected_entry_each_consume_the_session_cap() -> None:
    filled_broker = FakePaperBroker(auto_fill_entry=True)
    eod_engine = enabled_engine(filled_broker)
    eod_engine.handle_shadow_event(entry_event(identity="eod"), now=KNOWN)
    eod_engine.enforce_session_close(now=SESSION.market_close)
    blocked_after_eod = eod_engine.handle_shadow_event(
        entry_event(identity="after-eod"), now=SESSION.market_close
    )
    assert eod_engine.entry_submission_consumed
    assert blocked_after_eod is not None
    assert blocked_after_eod.state is PaperExecutionState.BLOCKED
    assert filled_broker.entry_submissions == 1

    rejected_broker = FakePaperBroker()
    original_submit = rejected_broker.submit_market_entry

    def rejected_submit(*, qty, client_order_id):
        order = original_submit(qty=qty, client_order_id=client_order_id)
        rejected = order.model_copy(update={"status": BrokerOrderStatus.REJECTED})
        rejected_broker.orders[order.broker_order_id] = rejected
        return rejected

    rejected_broker.submit_market_entry = rejected_submit
    rejected_engine = enabled_engine(rejected_broker)
    with pytest.raises(PaperExecutionError, match="terminated without a fill"):
        rejected_engine.handle_shadow_event(entry_event(identity="rejected"), now=KNOWN)
    assert rejected_engine.entry_submission_consumed
    assert rejected_broker.entry_submissions == 1


def test_dry_run_intentions_never_consume_the_session_cap() -> None:
    engine = PaperExecutionEngine(SESSION, candidate=PaperCandidate.ATR_0_75)
    engine.handle_shadow_event(entry_event(identity="first"), now=KNOWN)
    engine.handle_shadow_event(entry_event(identity="second"), now=KNOWN)
    assert not engine.entry_submission_consumed
    assert len(engine.executions) == 2


def test_restart_reconstructs_consumed_cap_from_broker_visible_entry_identity() -> None:
    broker = FakePaperBroker()
    first_engine = enabled_engine(broker)
    first_event = entry_event(identity="first")
    first_engine.handle_shadow_event(first_event, now=KNOWN)

    restarted = PaperExecutionEngine(
        SESSION,
        candidate=PaperCandidate.ATR_0_75,
        enable_paper_orders=True,
        broker=broker,
    )
    restarted.recover((first_event.position,), now=KNOWN + timedelta(minutes=1))
    restarted.recover((first_event.position,), now=KNOWN + timedelta(minutes=1))
    assert restarted.entry_submission_consumed
    second = restarted.handle_shadow_event(
        entry_event(identity="second"), now=KNOWN + timedelta(minutes=2)
    )
    assert second is not None and second.state is PaperExecutionState.BLOCKED
    assert broker.entry_submissions == 1


def test_uncertain_restart_entry_history_fails_closed() -> None:
    class UncertainBroker(FakePaperBroker):
        def find_order_by_client_id(self, client_order_id, *, role):
            raise OSError("simulated unavailable broker history")

    broker = UncertainBroker()
    engine = PaperExecutionEngine(
        SESSION,
        candidate=PaperCandidate.ATR_0_75,
        enable_paper_orders=True,
        broker=broker,
    )
    with pytest.raises(PaperExecutionError, match="history cannot be reconciled"):
        engine.recover((entry_event(identity="first").position,), now=KNOWN)
    assert engine.entry_submission_state.reconciliation_uncertain
    assert broker.entry_submissions == 0


def test_new_xnys_session_gets_a_fresh_immutable_entry_latch() -> None:
    broker = FakePaperBroker()
    first = enabled_engine(broker)
    first.handle_shadow_event(entry_event(identity="first"), now=KNOWN)
    assert first.entry_submission_consumed
    next_session = CALENDAR.session_for_date(date(2026, 8, 20))
    second = PaperExecutionEngine(next_session, candidate=PaperCandidate.ATR_0_75)
    assert second.entry_submission_state.session_date == date(2026, 8, 20)
    assert not second.entry_submission_consumed


def test_long_signal_never_creates_or_consumes_base_short_paper_entry() -> None:
    long_signal = signal("long").model_copy(
        update={
            "direction": SetupDirection.LONG,
            "base_short_membership": False,
            "stage13_forward_test_candidate_ids": (),
        }
    )
    machine = ShadowForwardStateMachine(SESSION)
    assert machine.register_signal(long_signal, available_levels=levels()) == ()
    engine = PaperExecutionEngine(SESSION, candidate=PaperCandidate.ATR_0_75)
    assert not engine.entry_submission_consumed
    assert engine.executions == ()


@pytest.mark.parametrize(
    "candidate,expected_stop",
    (
        (PaperCandidate.ATR_0_75, Decimal("101.75")),
        (PaperCandidate.ATR_1_00, Decimal("102.25")),
    ),
)
def test_fill_reconciliation_uses_actual_fill_for_stop_and_frozen_objective(
    candidate, expected_stop
) -> None:
    broker = FakePaperBroker(auto_fill_entry=True)
    engine = enabled_engine(broker, candidate)
    record = engine.handle_shadow_event(entry_event(candidate), now=KNOWN)
    assert record is not None
    assert record.state is PaperExecutionState.PROTECTIVE_ACTIVE
    assert record.intended_reference_price == Decimal("100")
    assert record.actual_fill_price == Decimal("100.25")
    assert record.fill_slippage == Decimal("0.25")
    assert record.protective_stop_price == expected_stop
    assert record.objective_price == Decimal("98")
    assert record.protective_target_price == Decimal("98")
    assert broker.oco_submissions == 1


def test_entry_fill_after_submission_creates_protection_once() -> None:
    broker = FakePaperBroker()
    engine = enabled_engine(broker)
    record = engine.handle_shadow_event(entry_event(), now=KNOWN)
    assert record is not None and record.entry_order is not None
    broker.fill(record.entry_order.broker_order_id, "100.10", position_qty="-1")
    engine.reconcile_broker_state(now=KNOWN + timedelta(minutes=1))
    assert engine.executions[0].state is PaperExecutionState.PROTECTIVE_ACTIVE
    assert broker.oco_submissions == 1
    engine.reconcile_broker_state(now=KNOWN + timedelta(minutes=2))
    assert broker.oco_submissions == 1


def test_target_fill_cancels_stop_and_reconciles_flat() -> None:
    broker = FakePaperBroker(auto_fill_entry=True)
    engine = enabled_engine(broker)
    record = engine.handle_shadow_event(entry_event(), now=KNOWN)
    assert record is not None and record.protective_orders is not None
    broker.fill(record.protective_orders.target.broker_order_id, "98", position_qty="0")
    engine.reconcile_broker_state(now=KNOWN + timedelta(minutes=1))
    assert record.protective_orders.stop.broker_order_id in broker.canceled
    assert engine.executions[0].state is PaperExecutionState.FLAT
    cancel_count = len(broker.canceled)
    engine.reconcile_broker_state(now=KNOWN + timedelta(minutes=2))
    assert len(broker.canceled) == cancel_count


def test_stop_fill_cancels_target_and_reconciles_flat() -> None:
    broker = FakePaperBroker(auto_fill_entry=True)
    engine = enabled_engine(broker)
    record = engine.handle_shadow_event(entry_event(), now=KNOWN)
    assert record is not None and record.protective_orders is not None
    broker.fill(
        record.protective_orders.stop.broker_order_id,
        str(record.protective_stop_price),
        position_qty="0",
    )
    engine.reconcile_broker_state(now=KNOWN + timedelta(minutes=1))
    assert record.protective_orders.target.broker_order_id in broker.canceled
    assert engine.executions[0].state is PaperExecutionState.FLAT


def test_simultaneous_protective_fills_fail_closed_without_reversal() -> None:
    broker = FakePaperBroker(auto_fill_entry=True)
    engine = enabled_engine(broker)
    record = engine.handle_shadow_event(entry_event(), now=KNOWN)
    assert record is not None and record.protective_orders is not None
    broker.fill(record.protective_orders.target.broker_order_id, "98", position_qty="1")
    broker.fill(record.protective_orders.stop.broker_order_id, "102", position_qty="1")
    with pytest.raises(PaperExecutionError, match="both paper protective"):
        engine.reconcile_broker_state(now=KNOWN + timedelta(minutes=1))
    assert engine.executions[0].state is PaperExecutionState.BLOCKED


def test_conflicting_terminal_broker_update_fails() -> None:
    broker = FakePaperBroker(auto_fill_entry=True)
    engine = enabled_engine(broker)
    record = engine.handle_shadow_event(entry_event(), now=KNOWN)
    assert record is not None and record.entry_order is not None
    broker.orders[record.entry_order.broker_order_id] = record.entry_order.model_copy(
        update={"avg_fill_price": Decimal("101")}
    )
    with pytest.raises(PaperExecutionError, match="terminal paper broker order changed"):
        engine.reconcile_broker_state(now=KNOWN + timedelta(minutes=1))


def test_broker_position_mismatch_blocks_new_submissions() -> None:
    broker = FakePaperBroker()
    broker.position_qty = Decimal("-1")
    engine = PaperExecutionEngine(
        SESSION,
        candidate=PaperCandidate.ATR_0_75,
        enable_paper_orders=True,
        broker=broker,
    )
    with pytest.raises(PaperExecutionError, match="position"):
        engine.recover((), now=KNOWN)
    assert broker.entry_submissions == 0


def test_restart_reconstructs_filled_entry_and_open_oco_without_duplicates() -> None:
    broker = FakePaperBroker(auto_fill_entry=True)
    first = enabled_engine(broker)
    event = entry_event()
    original = first.handle_shadow_event(event, now=KNOWN)
    assert original is not None
    restarted = PaperExecutionEngine(
        SESSION,
        candidate=PaperCandidate.ATR_0_75,
        enable_paper_orders=True,
        broker=broker,
    )
    restarted.recover((event.position,), now=KNOWN + timedelta(minutes=1))
    assert restarted.executions[0].state is PaperExecutionState.PROTECTIVE_ACTIVE
    assert broker.entry_submissions == 1
    assert broker.oco_submissions == 1


def test_restart_does_not_retroactively_submit_missing_historical_entry() -> None:
    broker = FakePaperBroker()
    event = entry_event()
    restarted = PaperExecutionEngine(
        SESSION,
        candidate=PaperCandidate.ATR_0_75,
        enable_paper_orders=True,
        broker=broker,
    )
    restarted.recover((event.position,), now=KNOWN + timedelta(minutes=1))
    assert restarted.executions == ()
    assert broker.entry_submissions == 0


def test_session_end_unavailable_shadow_event_never_submits() -> None:
    broker = FakePaperBroker()
    engine = enabled_engine(broker)
    machine = ShadowForwardStateMachine(SESSION)
    unavailable_signal = signal("session-end").model_copy(
        update={
            "signal_known_at": SESSION.market_close,
            "confirmation_timestamp": SESSION.market_close - timedelta(minutes=5),
        }
    )
    events = machine.register_signal(unavailable_signal, available_levels=levels())
    assert events
    assert all(engine.handle_shadow_event(event, now=SESSION.market_close) is None for event in events)
    assert broker.entry_submissions == 0


def test_unrecognized_open_order_blocks_restart() -> None:
    broker = FakePaperBroker()
    broker._store(
        make_order(
            broker_id="foreign",
            client_id="foreign-order",
            role=BrokerOrderRole.ENTRY,
            side="sell",
            order_type="market",
            status=BrokerOrderStatus.NEW,
        )
    )
    engine = PaperExecutionEngine(
        SESSION,
        candidate=PaperCandidate.ATR_0_75,
        enable_paper_orders=True,
        broker=broker,
    )
    with pytest.raises(PaperExecutionError, match="unreconciled open"):
        engine.recover((), now=KNOWN)


def test_eod_cancels_protection_then_submits_one_buy_to_cover() -> None:
    broker = FakePaperBroker(auto_fill_entry=True)
    engine = enabled_engine(broker)
    record = engine.handle_shadow_event(entry_event(), now=KNOWN)
    assert record is not None and record.protective_orders is not None
    engine.enforce_session_close(now=SESSION.market_close)
    assert set(broker.canceled) == {
        record.protective_orders.target.broker_order_id,
        record.protective_orders.stop.broker_order_id,
    }
    assert broker.flatten_submissions == 1
    assert engine.executions[0].state is PaperExecutionState.EOD_FLATTEN_SUBMITTED
    flatten = engine.executions[0].flatten_order
    assert flatten is not None and flatten.side == "buy" and flatten.qty == 1


def test_eod_flatten_fill_closes_local_state_and_cannot_reverse() -> None:
    broker = FakePaperBroker(auto_fill_entry=True)
    engine = enabled_engine(broker)
    engine.handle_shadow_event(entry_event(), now=KNOWN)
    engine.enforce_session_close(now=SESSION.market_close)
    flatten = engine.executions[0].flatten_order
    assert flatten is not None
    broker.fill(flatten.broker_order_id, "99", position_qty="0")
    engine.reconcile_broker_state(now=SESSION.market_close)
    assert engine.executions[0].state is PaperExecutionState.FLAT
    assert engine.executions[0].local_expected_position_qty == 0


def test_next_session_timestamp_is_rejected_without_carry() -> None:
    engine = PaperExecutionEngine(SESSION, candidate=PaperCandidate.ATR_0_75)
    next_open = CALENDAR.session_for_date(date(2026, 8, 20)).market_open
    assert next_open is not None
    with pytest.raises(PaperExecutionError, match="cannot bridge"):
        engine.handle_shadow_event(entry_event(), now=next_open)


def test_models_and_adapter_enforce_spy_only() -> None:
    with pytest.raises(ValidationError):
        BrokerPositionRecord(symbol="AAPL", qty=Decimal("0"), observed_at=KNOWN)


def test_live_alpaca_endpoint_is_structurally_impossible() -> None:
    with pytest.raises(PaperExecutionError, match="fixed Alpaca paper"):
        AlpacaPaperBroker(
            api_key=SecretStr("test-key"),
            secret_key=SecretStr("test-secret"),
            base_url="https://api.alpaca.markets",
        )
    assert AlpacaPaperBroker.base_url == ALPACA_PAPER_BASE_URL
    live_client = httpx.Client(base_url="https://api.alpaca.markets")
    with pytest.raises(PaperExecutionError, match="injected broker client"):
        AlpacaPaperBroker(
            api_key=SecretStr("test-key"),
            secret_key=SecretStr("test-secret"),
            client=live_client,
        )
    live_client.close()


def test_paper_broker_uses_only_dedicated_paper_credentials(monkeypatch) -> None:
    market_key = "market-key-not-for-paper"
    market_secret = "market-secret-not-for-paper"
    paper_key = "dedicated-paper-key"
    paper_secret = "dedicated-paper-secret"
    monkeypatch.setenv("ALPACA_API_KEY", market_key)
    monkeypatch.setenv("ALPACA_SECRET_KEY", market_secret)
    monkeypatch.setenv("ALPACA_PAPER_API_KEY", paper_key)
    monkeypatch.setenv("ALPACA_PAPER_SECRET_KEY", paper_secret)
    environment = AlpacaEnvironment()
    with AlpacaPaperBroker.from_environment(environment) as broker:
        assert broker._client.headers["apca-api-key-id"] == paper_key
        assert broker._client.headers["apca-api-secret-key"] == paper_secret
        assert broker._client.headers["apca-api-key-id"] != market_key
        assert broker._client.headers["apca-api-secret-key"] != market_secret


def test_missing_dedicated_paper_credentials_fail_closed(monkeypatch) -> None:
    monkeypatch.setenv("ALPACA_API_KEY", "market-only-key")
    monkeypatch.setenv("ALPACA_SECRET_KEY", "market-only-secret")
    monkeypatch.delenv("ALPACA_PAPER_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_PAPER_SECRET_KEY", raising=False)
    with pytest.raises(PaperExecutionError, match="paper credentials are required"):
        AlpacaPaperBroker.from_environment(AlpacaEnvironment())


def test_paper_adapter_uses_only_stock_market_entry_and_short_oco_payloads() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/v2/account":
            return httpx.Response(
                200,
                json={
                    "status": "ACTIVE",
                    "account_blocked": False,
                    "trading_blocked": False,
                },
            )
        if request.url.path == "/v2/orders" and request.method == "POST":
            import json

            body = json.loads(request.content)
            common = {
                "symbol": "SPY",
                "qty": body["qty"],
                "side": body["side"],
                "status": "new",
                "filled_qty": "0",
                "filled_avg_price": None,
                "submitted_at": KNOWN.isoformat(),
                "filled_at": None,
                "client_order_id": body["client_order_id"],
            }
            if body.get("order_class") == "oco":
                return httpx.Response(
                    200,
                    json={
                        **common,
                        "id": "target",
                        "type": "limit",
                        "limit_price": body["take_profit"]["limit_price"],
                        "stop_price": None,
                        "legs": [
                            {
                                **common,
                                "id": "stop",
                                "client_order_id": "broker-stop",
                                "type": "stop",
                                "limit_price": None,
                                "stop_price": body["stop_loss"]["stop_price"],
                            }
                        ],
                    },
                )
            return httpx.Response(
                200,
                json={
                    **common,
                    "id": "entry",
                    "type": "market",
                    "limit_price": None,
                    "stop_price": None,
                },
            )
        raise AssertionError(f"unexpected request {request.method} {request.url}")

    client = httpx.Client(
        base_url=ALPACA_PAPER_BASE_URL,
        transport=httpx.MockTransport(handler),
    )
    broker = AlpacaPaperBroker(
        api_key=SecretStr("test-key"),
        secret_key=SecretStr("test-secret"),
        client=client,
    )
    broker.verify_paper_account()
    entry = broker.submit_market_entry(qty=1, client_order_id="entry-id")
    protection = broker.submit_protective_oco(
        qty=1,
        target_price=Decimal("98"),
        stop_price=Decimal("102"),
        client_order_id="oco-id",
    )
    assert entry.symbol == "SPY" and entry.side == "sell"
    assert protection.target.side == protection.stop.side == "buy"
    assert all("option" not in request.url.path for request in requests)
    assert all(request.url.host == "paper-api.alpaca.markets" for request in requests)


def test_paper_http_failure_is_sanitized_and_never_echoes_credentials() -> None:
    key = "paper-api-key-must-not-leak"
    secret = "paper-secret-key-must-not-leak"
    client = httpx.Client(
        base_url=ALPACA_PAPER_BASE_URL,
        transport=httpx.MockTransport(
            lambda _request: httpx.Response(
                401, json={"message": f"bad {key} {secret}"}
            )
        ),
    )
    broker = AlpacaPaperBroker(
        api_key=SecretStr(key),
        secret_key=SecretStr(secret),
        client=client,
    )
    with pytest.raises(PaperExecutionError) as error:
        broker.verify_paper_account()
    rendered = str(error.value)
    assert "HTTP 401" in rendered
    assert "not authorized for the Alpaca paper account" in rendered
    assert key not in rendered
    assert secret not in rendered
    client.close()


def test_stage14_4_report_hash_is_deterministic() -> None:
    engine = PaperExecutionEngine(SESSION, candidate=PaperCandidate.ATR_0_75)
    engine.handle_shadow_event(entry_event(), now=KNOWN)
    report = PaperRunReport(
        session_date=SESSION_DATE,
        candidate=engine.candidate,
        qty=engine.qty,
        paper_orders_enabled=engine.orders_enabled,
        actions=engine.actions,
        executions=engine.executions,
    )
    assert paper_execution_report_hash(report) == (
        "3de987672bc6cc73c39c643f6bd656daefdcbe32e0e6ce3c830405ab8eee183b"
    )
