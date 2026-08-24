from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, localcontext

import pytest

from spy_research.data import RawBarRecord
from spy_research.execution import (
    AtrStopModel,
    ExecutableTradeSetup,
    ExitFamily,
    StrategyPopulation,
    exit_model_variants,
    simulate_exit_model_trade,
)
from spy_research.interactions import AvailableLevel, LevelType
from spy_research.indicators.atr import ATR_CONTEXT
from spy_research.live import LiveSignalEvent
from spy_research.market import XNYSCalendar
from spy_research.replay import STAGE14_FORWARD_CANDIDATE_IDS
from spy_research.shadow import (
    ShadowForwardStateMachine,
    ShadowHistoricalEquivalenceService,
    ShadowInputError,
    ShadowState,
)
from spy_research.strategy.models import SetupDirection


CALENDAR = XNYSCalendar()
SESSION_DATE = date(2026, 8, 19)
SESSION = CALENDAR.session_for_date(SESSION_DATE)
assert SESSION.market_open is not None and SESSION.market_close is not None
OPEN = SESSION.market_open
KNOWN = OPEN + timedelta(minutes=30)


def signal(
    *,
    direction: SetupDirection = SetupDirection.SHORT,
    atr: Decimal | None = Decimal("2"),
    identity: str = "setup-short",
    known_at: datetime = KNOWN,
) -> LiveSignalEvent:
    short = direction is SetupDirection.SHORT
    return LiveSignalEvent(
        session_date=SESSION_DATE,
        signal_identity=f"signal-{identity}",
        setup_identity=identity,
        direction=direction,
        triggering_level_type=LevelType.PDH,
        triggering_level_price=Decimal("100"),
        break_timestamp=known_at - timedelta(minutes=10),
        confirmation_timestamp=known_at - timedelta(minutes=5),
        signal_known_at=known_at,
        confirmation_close=Decimal("101"),
        atr14=atr,
        base_short_membership=short,
        stage13_forward_test_candidate_ids=(
            STAGE14_FORWARD_CANDIDATE_IDS if short else ()
        ),
    )


def levels(*, include_target: bool = True):
    values = [
        AvailableLevel(
            session_date=SESSION_DATE,
            level_type=LevelType.PDH,
            level_price=Decimal("100"),
            available_from_timestamp=OPEN,
        ),
        AvailableLevel(
            session_date=SESSION_DATE,
            level_type=LevelType.PDL,
            level_price=Decimal("95"),
            available_from_timestamp=OPEN,
        ),
    ]
    if include_target:
        values.extend(
            (
                AvailableLevel(
                    session_date=SESSION_DATE,
                    level_type=LevelType.PDC,
                    level_price=Decimal("98"),
                    available_from_timestamp=OPEN,
                ),
                AvailableLevel(
                    session_date=SESSION_DATE,
                    level_type=LevelType.ORL5,
                    level_price=Decimal("98"),
                    available_from_timestamp=OPEN + timedelta(minutes=5),
                ),
            )
        )
    return tuple(values)


def bar(
    timestamp: datetime,
    *,
    open: str = "100",
    high: str = "101",
    low: str = "99",
    close: str = "100",
) -> RawBarRecord:
    return RawBarRecord(
        symbol="SPY",
        timestamp=timestamp,
        open=Decimal(open),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal(close),
        volume=100,
        trade_count=10,
        vwap=Decimal(close),
        source="alpaca",
        feed="sip",
        timeframe="1Min",
        adjustment="raw",
    )


def started(*, live_signal=None, available_levels=None):
    machine = ShadowForwardStateMachine(SESSION)
    machine.register_signal(
        live_signal or signal(),
        available_levels=levels() if available_levels is None else available_levels,
    )
    return machine


def by_multiplier(machine, multiplier: str):
    return next(
        item for item in machine.positions
        if item.stop_multiplier == Decimal(multiplier)
    )


def test_one_short_signal_creates_exactly_two_equal_priority_candidates() -> None:
    machine = ShadowForwardStateMachine(SESSION)
    events = machine.register_signal(signal(), available_levels=levels())
    assert len(events) == 2
    assert tuple(item.candidate_id for item in machine.positions) == tuple(
        sorted(STAGE14_FORWARD_CANDIDATE_IDS)
    )
    assert {item.state for item in machine.positions} == {ShadowState.PENDING_ENTRY}


def test_long_signal_creates_no_shadow_candidates() -> None:
    machine = ShadowForwardStateMachine(SESSION)
    assert machine.register_signal(
        signal(direction=SetupDirection.LONG, identity="setup-long"),
        available_levels=levels(),
    ) == ()
    assert machine.positions == ()


def test_entry_uses_first_available_open_and_exact_atr_stop_math() -> None:
    machine = started()
    assert machine.process_bar(bar(KNOWN - timedelta(minutes=1))) == ()
    events = machine.process_bar(bar(KNOWN, open="100", high="100", low="99"))
    assert len(events) == 2
    three_quarter = by_multiplier(machine, "0.75")
    one = by_multiplier(machine, "1.00")
    assert three_quarter.entry_timestamp == KNOWN
    assert three_quarter.entry_price == Decimal("100")
    assert three_quarter.risk_distance == Decimal("1.50")
    assert three_quarter.stop_price == Decimal("101.50")
    assert one.risk_distance == Decimal("2.00")
    assert one.stop_price == Decimal("102.00")
    assert all(item.target_price == Decimal("98") for item in machine.positions)
    assert all(
        item.target_level_types == (LevelType.PDC, LevelType.ORL5)
        for item in machine.positions
    )


def test_target_exit_uses_exact_objective_price_and_r() -> None:
    machine = started()
    machine.process_bar(bar(KNOWN, high="100", low="99"))
    machine.process_bar(bar(KNOWN + timedelta(minutes=1), high="100", low="97"))
    assert {item.state for item in machine.positions} == {ShadowState.TARGET_EXIT}
    assert all(item.exit_price == Decimal("98") for item in machine.positions)
    with localcontext(ATR_CONTEXT):
        expected = Decimal("2") / Decimal("1.5")
    assert by_multiplier(machine, "0.75").realized_r == expected
    assert by_multiplier(machine, "1.00").realized_r == Decimal("1")


def test_stop_exit_is_exact_negative_one_r() -> None:
    machine = started()
    machine.process_bar(bar(KNOWN, high="100", low="99"))
    machine.process_bar(bar(KNOWN + timedelta(minutes=1), high="103", low="99"))
    assert {item.state for item in machine.positions} == {ShadowState.STOP_EXIT}
    assert all(item.realized_r == Decimal("-1") for item in machine.positions)


def test_same_minute_stop_and_target_is_ambiguous_without_path_inference() -> None:
    machine = started()
    machine.process_bar(bar(KNOWN, high="103", low="97"))
    assert {item.state for item in machine.positions} == {
        ShadowState.AMBIGUOUS_BOTH_TOUCHED
    }
    assert all(item.exit_price is None and item.ambiguity is not None for item in machine.positions)


def test_eod_fallback_uses_final_rth_close() -> None:
    final = SESSION.market_close - timedelta(minutes=1)
    machine = started(live_signal=signal(known_at=final))
    machine.process_bar(bar(final, high="100", low="99", close="99.5"))
    assert {item.state for item in machine.positions} == {ShadowState.EOD_EXIT}
    assert all(item.exit_price == Decimal("99.5") for item in machine.positions)
    assert all(item.holding_minutes == 0 for item in machine.positions)


@pytest.mark.parametrize(
    "live_signal,available_levels,expected",
    (
        (signal(atr=None, identity="missing-atr"), levels(), ShadowState.UNAVAILABLE_ATR),
        (
            signal(identity="open-ended"),
            levels(include_target=False)[:1],
            ShadowState.UNAVAILABLE_OBJECTIVE_LEVEL,
        ),
    ),
)
def test_unavailable_atr_and_open_ended_objective_are_explicit(
    live_signal, available_levels, expected
) -> None:
    machine = started(live_signal=live_signal, available_levels=available_levels)
    machine.process_bar(bar(KNOWN))
    assert {item.state for item in machine.positions} == {expected}
    assert all(item.bars_observed == 0 for item in machine.positions)


def test_session_end_signal_never_fabricates_an_entry() -> None:
    machine = started(live_signal=signal(known_at=SESSION.market_close))
    assert {item.state for item in machine.positions} == {
        ShadowState.ENTRY_UNAVAILABLE_SESSION_END
    }
    assert all(item.entry_timestamp is None for item in machine.positions)


def test_duplicate_signal_and_identical_finalization_are_idempotent() -> None:
    live_signal = signal()
    machine = ShadowForwardStateMachine(SESSION)
    first = machine.register_signal(live_signal, available_levels=levels())
    assert len(first) == 2
    assert machine.register_signal(live_signal, available_levels=levels()) == ()
    terminal_bar = bar(KNOWN, high="103", low="99")
    machine.process_bar(terminal_bar)
    frozen = machine.positions
    assert machine.process_bar(terminal_bar) == ()
    assert machine.positions == frozen


def test_conflicting_duplicate_signal_and_bar_fail() -> None:
    machine = started()
    with pytest.raises(ShadowInputError, match="conflicting duplicate live signal"):
        machine.register_signal(
            signal(atr=Decimal("3")), available_levels=levels()
        )
    first = bar(KNOWN, high="100", low="99")
    machine.process_bar(first)
    with pytest.raises(ShadowInputError, match="conflicting duplicate shadow minute"):
        machine.process_bar(first.model_copy(update={"close": Decimal("99.5")}))


def test_restart_replay_reconstruction_equals_uninterrupted_state() -> None:
    bars = (
        bar(KNOWN, high="100", low="99"),
        bar(KNOWN + timedelta(minutes=1), high="100", low="99"),
        bar(KNOWN + timedelta(minutes=2), high="100", low="97"),
    )
    uninterrupted = started()
    for item in bars:
        uninterrupted.process_bar(item)
    reconstructed = started()
    for item in bars:
        reconstructed.process_bar(item)
    assert reconstructed.positions == uninterrupted.positions


def test_future_bars_cannot_mutate_finalized_path_or_backfill_atr() -> None:
    finalized = started()
    finalized.process_bar(bar(KNOWN, high="103", low="99"))
    frozen = tuple(item.model_dump_json() for item in finalized.positions)
    finalized.process_bar(
        bar(KNOWN + timedelta(minutes=1), high="999", low="1", close="500")
    )
    assert tuple(item.model_dump_json() for item in finalized.positions) == frozen

    unavailable = started(live_signal=signal(atr=None, identity="no-backfill"))
    unavailable.process_bar(bar(KNOWN))
    unavailable.process_bar(bar(KNOWN + timedelta(minutes=1), high="999", low="1"))
    assert {item.state for item in unavailable.positions} == {ShadowState.UNAVAILABLE_ATR}


def test_open_position_cannot_cross_session_boundary() -> None:
    machine = started()
    machine.process_bar(bar(KNOWN, high="100", low="99"))
    next_session = CALENDAR.session_for_date(date(2026, 8, 20))
    assert next_session.market_open is not None
    with pytest.raises(ShadowInputError, match="cannot carry overnight"):
        machine.process_bar(bar(next_session.market_open))


def test_shadow_engine_has_no_trading_endpoint() -> None:
    machine = ShadowForwardStateMachine(SESSION)
    assert not any(
        hasattr(machine, name)
        for name in (
            "submit_order",
            "replace_order",
            "cancel_order",
            "positions_api",
            "buying_power",
        )
    )


def test_both_candidate_paths_match_stage13_2_projection_exactly() -> None:
    bars = (
        bar(KNOWN, high="100", low="99"),
        bar(KNOWN + timedelta(minutes=1), high="100", low="97"),
    )
    machine = started()
    for item in bars:
        machine.process_bar(item)
    setup = ExecutableTradeSetup(
        setup_identity="setup-short",
        session_date=SESSION_DATE,
        direction=SetupDirection.SHORT,
        level_type=LevelType.PDH,
        confirmation_bar_timestamp=KNOWN - timedelta(minutes=5),
        signal_known_at=KNOWN,
        entry_timestamp=KNOWN,
        entry_price=Decimal("100"),
    )
    variants = {
        AtrStopModel.ATR_0_75: next(
            item
            for item in exit_model_variants()
            if item.family is ExitFamily.NEXT_OBJECTIVE_LEVEL
            and item.stop_model is AtrStopModel.ATR_0_75
        ),
        AtrStopModel.ATR_1_00: next(
            item
            for item in exit_model_variants()
            if item.family is ExitFamily.NEXT_OBJECTIVE_LEVEL
            and item.stop_model is AtrStopModel.ATR_1_00
        ),
    }
    for stop_model, multiplier in (
        (AtrStopModel.ATR_0_75, "0.75"),
        (AtrStopModel.ATR_1_00, "1.00"),
    ):
        expected = simulate_exit_model_trade(
            setup,
            StrategyPopulation.BASE_SHORT,
            variants[stop_model],
            Decimal("2"),
            bars,
            objective_price=Decimal("98"),
            objective_level_types=(LevelType.PDC, LevelType.ORL5),
            objective_available=True,
        )
        observed = by_multiplier(machine, multiplier)
        assert ShadowHistoricalEquivalenceService._projection(
            observed
        ) == ShadowHistoricalEquivalenceService._expected_projection(expected)
