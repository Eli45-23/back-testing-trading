from __future__ import annotations

import inspect
import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from spy_research.bars.models import FiveMinuteBar
from spy_research.interactions import (
    AvailableLevel,
    BreakFollowThrough,
    BreakFollowThroughResult,
    ImmediateAssessment,
    ImmediateState,
    InteractionType,
    LevelType,
    PriceSide,
    RetestAssessment,
    RetestState,
    classify_level_interaction,
)
from spy_research.strategy import (
    BasePriceActionResult,
    BasePriceActionService,
    BaseSetupInputError,
    BaseSetupStatus,
    ConfirmationType,
    SetupDirection,
    interaction_identity,
    qualify_base_price_action_candidate,
)
from spy_research.cli import main


SESSION = date(2026, 8, 19)
BREAK_TIME = datetime(2026, 8, 19, 14, 0, tzinfo=UTC)
SESSION_CLOSE = datetime(2026, 8, 19, 20, 0, tzinfo=UTC)
LEVEL = Decimal("100")


def bar(
    timestamp: datetime,
    *,
    open_price: str,
    high: str,
    low: str,
    close: str,
) -> FiveMinuteBar:
    return FiveMinuteBar(
        symbol="SPY",
        timestamp=timestamp,
        session_date=SESSION,
        open=Decimal(open_price),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal(close),
        volume=100,
        trade_count=10,
        source="alpaca",
        feed="sip",
        timeframe="5Min",
        adjustment="raw",
        source_bar_count=5,
    )


def seed(
    direction: SetupDirection = SetupDirection.LONG,
    *,
    timestamp: datetime = BREAK_TIME,
    level_type: LevelType = LevelType.PDH,
):
    if direction is SetupDirection.LONG:
        candle = bar(
            timestamp,
            open_price="99",
            high="102",
            low="98",
            close="101",
        )
    else:
        candle = bar(
            timestamp,
            open_price="101",
            high="102",
            low="98",
            close="99",
        )
    return classify_level_interaction(
        candle,
        AvailableLevel(
            session_date=SESSION,
            level_type=level_type,
            level_price=LEVEL,
            available_from_timestamp=timestamp,
        ),
    )


def follow(
    interaction,
    *,
    immediate_state: ImmediateState = ImmediateState.HOLD,
    immediate_timestamp: datetime | None = None,
    retest_state: RetestState = RetestState.NO_RETEST,
    retest_offset: int | None = None,
) -> BreakFollowThrough:
    immediate_timestamp = (
        interaction.candle_timestamp + timedelta(minutes=5)
        if immediate_timestamp is None and immediate_state is not ImmediateState.UNAVAILABLE
        else immediate_timestamp
    )
    retest_timestamp = (
        interaction.candle_timestamp + timedelta(minutes=5 * retest_offset)
        if retest_offset is not None
        else None
    )
    return BreakFollowThrough(
        break_interaction_identity=interaction_identity(interaction),
        session_date=interaction.session_date,
        level_type=interaction.level_type,
        level_price=interaction.level_price,
        break_timestamp=interaction.candle_timestamp,
        break_completed_at=interaction.candle_completed_at,
        break_interaction_type=interaction.interaction_type,
        break_direction=(
            PriceSide.ABOVE
            if interaction.interaction_type is InteractionType.CLOSE_THROUGH_ABOVE
            else PriceSide.BELOW
        ),
        immediate=ImmediateAssessment(
            state=immediate_state,
            bar_timestamp=immediate_timestamp,
            close=None if immediate_timestamp is None else LEVEL,
            close_side=None,
        ),
        retest=RetestAssessment(
            state=retest_state,
            bar_offset=retest_offset,
            timestamp=retest_timestamp,
            open=None if retest_timestamp is None else LEVEL,
            high=None if retest_timestamp is None else LEVEL + 1,
            low=None if retest_timestamp is None else LEVEL - 1,
            close=None if retest_timestamp is None else LEVEL,
            requested_bars=3,
            available_bars=(0 if retest_state is RetestState.UNAVAILABLE else 3),
            window_complete=retest_state is not RetestState.UNAVAILABLE,
        ),
    )


@pytest.mark.parametrize(
    ("direction", "expected"),
    (
        (SetupDirection.LONG, SetupDirection.LONG),
        (SetupDirection.SHORT, SetupDirection.SHORT),
    ),
)
def test_immediate_hold_confirms_direction_and_completion_timing(
    direction, expected
) -> None:
    interaction = seed(direction)
    result = qualify_base_price_action_candidate(
        interaction,
        follow(interaction),
        SESSION_CLOSE,
    )
    assert result.status is BaseSetupStatus.CONFIRMED
    assert result.direction is expected
    assert result.confirmation_type is ConfirmationType.IMMEDIATE_HOLD
    assert result.confirmation_bar_timestamp == BREAK_TIME + timedelta(minutes=5)
    assert result.signal_known_at == BREAK_TIME + timedelta(minutes=10)
    assert result.earliest_entry_timestamp == result.signal_known_at
    assert result.same_session_executable


@pytest.mark.parametrize("offset", (1, 2, 3))
@pytest.mark.parametrize(
    "immediate_state",
    (ImmediateState.FAILURE, ImmediateState.EQUAL),
)
def test_retest_hold_fallback_preserves_frozen_timestamp_and_offset(
    offset, immediate_state
) -> None:
    interaction = seed()
    exact = follow(
        interaction,
        immediate_state=immediate_state,
        retest_state=RetestState.RETEST_HOLD,
        retest_offset=offset,
    )
    result = qualify_base_price_action_candidate(
        interaction,
        exact,
        SESSION_CLOSE,
    )
    assert result.status is BaseSetupStatus.CONFIRMED
    assert result.confirmation_type is ConfirmationType.RETEST_HOLD
    assert result.confirmation_bar_timestamp == exact.retest.timestamp
    assert result.retest_bar_offset == offset
    assert result.signal_known_at == exact.retest.timestamp + timedelta(minutes=5)


def test_immediate_hold_has_priority_and_one_record_per_break() -> None:
    interaction = seed()
    exact = follow(
        interaction,
        immediate_state=ImmediateState.HOLD,
        retest_state=RetestState.RETEST_HOLD,
        retest_offset=2,
    )
    result = qualify_base_price_action_candidate(
        interaction,
        exact,
        SESSION_CLOSE,
    )
    assert result.confirmation_type is ConfirmationType.IMMEDIATE_HOLD
    assert result.retest_bar_offset is None


def test_identical_input_produces_identical_identity_and_output() -> None:
    interaction = seed()
    exact = follow(interaction)
    first = qualify_base_price_action_candidate(interaction, exact, SESSION_CLOSE)
    second = qualify_base_price_action_candidate(interaction, exact, SESSION_CLOSE)
    assert first == second
    assert len(first.setup_identity) == 64


@pytest.mark.parametrize(
    ("immediate", "retest", "expected"),
    (
        (
            ImmediateState.FAILURE,
            RetestState.RETEST_FAILURE,
            BaseSetupStatus.REJECTED_RETEST_FAILURE,
        ),
        (ImmediateState.FAILURE, RetestState.NO_RETEST, BaseSetupStatus.NO_RETEST),
        (ImmediateState.EQUAL, RetestState.RETEST_EQUAL, BaseSetupStatus.EQUAL_ONLY),
        (
            ImmediateState.UNAVAILABLE,
            RetestState.UNAVAILABLE,
            BaseSetupStatus.INCOMPLETE,
        ),
    ),
)
def test_non_confirmation_statuses_account_for_seed(immediate, retest, expected) -> None:
    interaction = seed()
    exact = follow(
        interaction,
        immediate_state=immediate,
        immediate_timestamp=(None if immediate is ImmediateState.UNAVAILABLE else None),
        retest_state=retest,
        retest_offset=(1 if retest in {RetestState.RETEST_FAILURE, RetestState.RETEST_EQUAL} else None),
    )
    result = qualify_base_price_action_candidate(interaction, exact, SESSION_CLOSE)
    assert result.status is expected
    assert result.confirmation_type is None
    assert result.signal_known_at is None
    assert not result.same_session_executable


def test_immediate_hold_does_not_require_a_retest() -> None:
    interaction = seed()
    result = qualify_base_price_action_candidate(
        interaction,
        follow(interaction, retest_state=RetestState.NO_RETEST),
        SESSION_CLOSE,
    )
    assert result.status is BaseSetupStatus.CONFIRMED
    assert result.confirmation_type is ConfirmationType.IMMEDIATE_HOLD


def test_confirmation_completing_at_session_close_is_not_executable() -> None:
    break_time = SESSION_CLOSE - timedelta(minutes=10)
    interaction = seed(timestamp=break_time)
    result = qualify_base_price_action_candidate(
        interaction,
        follow(interaction),
        SESSION_CLOSE,
    )
    assert result.confirmation_bar_timestamp == SESSION_CLOSE - timedelta(minutes=5)
    assert result.signal_known_at == SESSION_CLOSE
    assert result.earliest_entry_timestamp == SESSION_CLOSE
    assert not result.same_session_executable


def test_confirmation_after_session_close_is_rejected_not_carried_overnight() -> None:
    interaction = seed(timestamp=SESSION_CLOSE - timedelta(minutes=5))
    with pytest.raises(BaseSetupInputError, match="after session close"):
        qualify_base_price_action_candidate(
            interaction,
            follow(interaction),
            SESSION_CLOSE,
        )


def test_touch_seed_is_rejected() -> None:
    candle = bar(BREAK_TIME, open_price="99", high="100", low="98", close="99")
    interaction = classify_level_interaction(
        candle,
        AvailableLevel(
            session_date=SESSION,
            level_type=LevelType.PDH,
            level_price=LEVEL,
            available_from_timestamp=BREAK_TIME,
        ),
    )
    assert interaction.interaction_type is InteractionType.TOUCH
    exact = follow(seed())
    with pytest.raises(BaseSetupInputError, match="Only Stage 8.1 close-throughs"):
        qualify_base_price_action_candidate(interaction, exact, SESSION_CLOSE)


def test_mismatched_seed_identity_is_rejected() -> None:
    interaction = seed()
    exact = follow(interaction).model_copy(
        update={"break_interaction_identity": "wrong"}
    )
    with pytest.raises(BaseSetupInputError, match="identity"):
        qualify_base_price_action_candidate(interaction, exact, SESSION_CLOSE)


@pytest.mark.parametrize(
    "updated",
    (
        {"session_date": date(2026, 8, 18)},
        {"symbol": "QQQ"},
    ),
)
def test_mixed_session_or_wrong_symbol_is_rejected(updated) -> None:
    interaction = seed()
    exact = follow(interaction).model_copy(update=updated)
    with pytest.raises(BaseSetupInputError, match="facts must match"):
        qualify_base_price_action_candidate(interaction, exact, SESSION_CLOSE)


def test_input_and_output_are_immutable() -> None:
    interaction = seed()
    exact = follow(interaction)
    before_interaction = interaction.model_dump()
    before_exact = exact.model_dump()
    result = qualify_base_price_action_candidate(interaction, exact, SESSION_CLOSE)
    assert interaction.model_dump() == before_interaction
    assert exact.model_dump() == before_exact
    with pytest.raises(ValidationError):
        result.status = BaseSetupStatus.NO_RETEST


def test_no_lookahead_signature_and_prefix_stability() -> None:
    interaction = seed()
    exact = follow(interaction)
    assert tuple(inspect.signature(qualify_base_price_action_candidate).parameters) == (
        "interaction",
        "follow_through",
        "session_close",
    )
    prefix = qualify_base_price_action_candidate(interaction, exact, SESSION_CLOSE)
    unrelated_bar_four = bar(
        BREAK_TIME + timedelta(minutes=20),
        open_price="100",
        high="200",
        low="1",
        close="50",
    )
    unrelated_next_session = SESSION + timedelta(days=1)
    assert unrelated_bar_four and unrelated_next_session
    full = qualify_base_price_action_candidate(interaction, exact, SESSION_CLOSE)
    assert prefix == full


def test_service_sorts_deterministically_and_reconciles_one_record_per_seed() -> None:
    later = seed(timestamp=BREAK_TIME + timedelta(minutes=10), level_type=LevelType.PDL)
    earlier = seed(timestamp=BREAK_TIME, level_type=LevelType.PDH)
    service = object.__new__(BasePriceActionService)
    service._interactions = SimpleNamespace(
        calculate=lambda **kwargs: SimpleNamespace(interactions=(later, earlier))
    )
    service._follow_through = SimpleNamespace(
        calculate=lambda **kwargs: BreakFollowThroughResult(
            start_date=SESSION,
            end_date=SESSION,
            seed_count=2,
            follow_through=(follow(later), follow(earlier)),
        )
    )
    from spy_research.market import XNYSCalendar

    service._calendar = XNYSCalendar()
    result = service.calculate(start=SESSION, end=SESSION)
    assert result.seed_count == 2
    assert result.confirmed_count == 2
    assert len({item.setup_identity for item in result.candidates}) == 2
    assert [item.break_timestamp for item in result.candidates] == sorted(
        item.break_timestamp for item in result.candidates
    )


def test_pure_setup_qualification_is_offline_and_nonpersistent(
    monkeypatch, tmp_path
) -> None:
    def reject_network(*args, **kwargs):
        raise AssertionError("base setup qualification must remain offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    interaction = seed()
    qualify_base_price_action_candidate(interaction, follow(interaction), SESSION_CLOSE)
    assert list(tmp_path.iterdir()) == []


def test_cli_is_offline_read_only_and_reports_complete_accounting(
    monkeypatch, tmp_path, capsys
) -> None:
    interaction = seed()
    candidate = qualify_base_price_action_candidate(
        interaction,
        follow(interaction),
        SESSION_CLOSE,
    )

    def mocked_calculate(self, *, start, end):
        return BasePriceActionResult(
            start_date=start,
            end_date=end,
            seed_count=1,
            confirmed_count=1,
            non_confirmed_count=0,
            candidates=(candidate,),
        )

    def reject_network(*args, **kwargs):
        raise AssertionError("base-setups CLI must remain offline")

    monkeypatch.setattr(BasePriceActionService, "calculate", mocked_calculate)
    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "base-setups",
            "--start",
            "2026-08-19",
            "--end",
            "2026-08-19",
            "--raw-data-root",
            str(tmp_path / "raw"),
            "--processed-data-root",
            str(tmp_path / "processed"),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "seeds: 1  confirmed: 1  non-confirmed: 0" in captured.out
    assert "IMMEDIATE_HOLD=1" in captured.out
    assert captured.err == ""
    assert list(tmp_path.iterdir()) == []
