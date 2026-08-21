from __future__ import annotations

import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

import spy_research.cli as cli_module
from spy_research.events import EmaCrossDirection, EmaCrossEvent
from spy_research.interactions import ImmediateState, InteractionType, LevelType, RetestState
from spy_research.strategy import (
    BasePriceActionCandidate,
    BasePriceActionResult,
    BaseSetupStatus,
    ConfirmationType,
    EntryStatus,
    SetupEntryReference,
    SetupHorizonOutcome,
    SetupOutcome,
    SetupOutcomeResult,
    SetupDirection,
    calculate_base_strategy_statistics,
)
from spy_research.strategy.comparisons import (
    EmaAlignmentAnnotation,
    EmaAlignmentState,
    EmaCrossContextComparisonService,
    EmaCrossContextInputError,
    EmaCrossContextState,
    annotate_prior_cross_context,
    calculate_ema_cross_context_comparison,
    select_prior_ema_cross,
)


SESSION = date(2026, 8, 19)
CONFIRMATION = datetime(2026, 8, 19, 14, 0, tzinfo=UTC)


def setup(
    direction: SetupDirection = SetupDirection.LONG,
    *,
    confirmation: datetime = CONFIRMATION,
    identity: str = "setup",
    session_date: date = SESSION,
) -> BasePriceActionCandidate:
    signal = confirmation + timedelta(minutes=5)
    return BasePriceActionCandidate(
        setup_identity=identity,
        break_interaction_identity=f"break-{identity}",
        follow_through_identity=f"follow-{identity}",
        session_date=session_date,
        level_type=LevelType.PDH,
        level_price=Decimal("100"),
        direction=direction,
        break_interaction_type=(
            InteractionType.CLOSE_THROUGH_ABOVE
            if direction is SetupDirection.LONG
            else InteractionType.CLOSE_THROUGH_BELOW
        ),
        break_timestamp=confirmation - timedelta(minutes=5),
        break_completed_at=confirmation,
        exact_immediate_state=ImmediateState.HOLD,
        exact_retest_state=RetestState.NO_RETEST,
        status=BaseSetupStatus.CONFIRMED,
        confirmation_type=ConfirmationType.IMMEDIATE_HOLD,
        confirmation_bar_timestamp=confirmation,
        signal_known_at=signal,
        earliest_entry_timestamp=signal,
        same_session_executable=True,
    )


def cross(
    timestamp: datetime,
    direction: EmaCrossDirection = EmaCrossDirection.BULLISH,
    *,
    session_date: date = SESSION,
) -> EmaCrossEvent:
    return EmaCrossEvent(
        symbol="SPY",
        timestamp=timestamp,
        session_date=session_date,
        direction=direction,
        reference_price=Decimal("100"),
        close=Decimal("100"),
        ema9=Decimal("101") if direction is EmaCrossDirection.BULLISH else Decimal("99"),
        ema20=Decimal("100"),
        previous_ema9=Decimal("100"),
        previous_ema20=Decimal("100"),
        signed_separation=Decimal("1") if direction is EmaCrossDirection.BULLISH else Decimal("-1"),
        absolute_separation=Decimal("1"),
        previous_signed_separation=Decimal("0"),
        separation_delta_1=Decimal("1"),
        separation_delta_2=None,
        separation_delta_3=None,
        vwap=Decimal("100"),
        close_minus_vwap=Decimal("0"),
        ema9_minus_vwap=Decimal("1") if direction is EmaCrossDirection.BULLISH else Decimal("-1"),
        ema20_minus_vwap=Decimal("0"),
        atr14=Decimal("1"),
    )


@pytest.mark.parametrize(
    "direction,cross_direction,expected",
    (
        (SetupDirection.LONG, EmaCrossDirection.BULLISH, EmaCrossContextState.MATCHING_CROSS),
        (SetupDirection.LONG, EmaCrossDirection.BEARISH, EmaCrossContextState.OPPOSING_CROSS),
        (SetupDirection.SHORT, EmaCrossDirection.BEARISH, EmaCrossContextState.MATCHING_CROSS),
        (SetupDirection.SHORT, EmaCrossDirection.BULLISH, EmaCrossContextState.OPPOSING_CROSS),
    ),
)
def test_setup_cross_directional_relationship(direction, cross_direction, expected) -> None:
    annotation = select_prior_ema_cross(setup(direction), (cross(CONFIRMATION, cross_direction),))
    assert annotation.cross_state is expected


@pytest.mark.parametrize("bars", (0, 1, 3))
def test_exact_bar_and_completion_recency(bars: int) -> None:
    event = cross(CONFIRMATION - timedelta(minutes=bars * 5))
    annotation = select_prior_ema_cross(setup(), (event,))
    assert annotation.bars_since_cross == bars
    assert annotation.minutes_since_cross_completion == bars * 5
    assert annotation.cross_known_at <= annotation.signal_known_at


def test_future_cross_is_forbidden_and_later_cross_cannot_change_annotation() -> None:
    item = setup()
    eligible = cross(CONFIRMATION - timedelta(minutes=5))
    future = cross(CONFIRMATION + timedelta(minutes=5), EmaCrossDirection.BEARISH)
    first = select_prior_ema_cross(item, (eligible,))
    second = select_prior_ema_cross(item, (eligible, future))
    assert first == second
    assert second.cross_state is EmaCrossContextState.MATCHING_CROSS


def test_latest_eligible_cross_is_authoritative_even_when_opposing() -> None:
    older_matching = cross(CONFIRMATION - timedelta(minutes=10))
    newer_opposing = cross(CONFIRMATION - timedelta(minutes=5), EmaCrossDirection.BEARISH)
    annotation = select_prior_ema_cross(setup(), (older_matching, newer_opposing))
    assert annotation.cross_state is EmaCrossContextState.OPPOSING_CROSS
    assert annotation.cross_timestamp == newer_opposing.timestamp


def test_no_prior_cross_is_explicit_and_has_null_cross_fields() -> None:
    annotation = select_prior_ema_cross(setup(), ())
    assert annotation.cross_state is EmaCrossContextState.NO_PRIOR_CROSS
    assert annotation.cross_timestamp is None
    assert annotation.bars_since_cross is None


def test_prior_and_next_session_events_never_bridge() -> None:
    item = setup()
    setup_result = BasePriceActionResult(
        start_date=SESSION,
        end_date=SESSION,
        seed_count=1,
        confirmed_count=1,
        non_confirmed_count=0,
        candidates=(item,),
    )
    events = (
        cross(CONFIRMATION - timedelta(days=1), session_date=SESSION - timedelta(days=1)),
        cross(CONFIRMATION + timedelta(days=1), session_date=SESSION + timedelta(days=1)),
    )
    annotation = annotate_prior_cross_context(setup_result, events)[0]
    assert annotation.cross_state is EmaCrossContextState.NO_PRIOR_CROSS


def test_duplicate_cross_timestamp_is_rejected_deterministically() -> None:
    events = (
        cross(CONFIRMATION - timedelta(minutes=5)),
        cross(CONFIRMATION - timedelta(minutes=5), EmaCrossDirection.BEARISH),
    )
    with pytest.raises(EmaCrossContextInputError, match="Duplicate"):
        select_prior_ema_cross(setup(), events)


def test_annotation_is_offline_nonpersistent_and_does_not_mutate_inputs(
    monkeypatch, tmp_path
) -> None:
    item = setup()
    event = cross(CONFIRMATION)
    before = (item.model_dump(), event.model_dump())

    def reject_network(*args, **kwargs):
        raise AssertionError("Stage 10.2 annotation must remain offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    select_prior_ema_cross(item, (event,))
    assert before == (item.model_dump(), event.model_dump())
    assert list(tmp_path.iterdir()) == []


def _outcome(item: BasePriceActionCandidate, value: str, *, available: bool = True) -> SetupOutcome:
    reference = SetupEntryReference(
        setup_identity=item.setup_identity,
        session_date=item.session_date,
        direction=item.direction,
        signal_known_at=item.signal_known_at,
        earliest_entry_timestamp=item.earliest_entry_timestamp,
        entry_status=(
            EntryStatus.AVAILABLE
            if available
            else EntryStatus.ENTRY_UNAVAILABLE_SESSION_END
        ),
        entry_reference_timestamp=item.earliest_entry_timestamp if available else None,
        entry_reference_price=Decimal("100") if available else None,
        entry_delay_minutes=0 if available else None,
    )
    if not available:
        return SetupOutcome(
            setup_identity=item.setup_identity,
            setup=item,
            entry_reference=reference,
        )
    horizons = tuple(
        SetupHorizonOutcome(
            horizon=name,
            requested_minutes=minutes,
            available_minutes=minutes,
            complete=True,
            mfe=Decimal(value),
            mae=Decimal("1"),
            mfe_timestamp=item.signal_known_at,
            mae_timestamp=item.signal_known_at,
        )
        for name, minutes in (("5m", 5), ("15m", 15), ("30m", 30), ("60m", 60), ("EOD", 100))
    )
    return SetupOutcome(
        setup_identity=item.setup_identity,
        setup=item,
        entry_reference=reference,
        five=horizons[0],
        fifteen=horizons[1],
        thirty=horizons[2],
        sixty=horizons[3],
        eod=horizons[4],
    )


def test_statistics_partition_and_base_all_reproduce_frozen_stage9() -> None:
    matching = setup(identity="matching")
    opposing = setup(identity="opposing", confirmation=CONFIRMATION + timedelta(minutes=5))
    no_cross = setup(
        SetupDirection.SHORT,
        identity="none",
        confirmation=CONFIRMATION + timedelta(minutes=10),
    )
    setup_result = BasePriceActionResult(
        start_date=SESSION,
        end_date=SESSION,
        seed_count=3,
        confirmed_count=3,
        non_confirmed_count=0,
        candidates=(matching, opposing, no_cross),
    )
    outcome_result = SetupOutcomeResult(
        start_date=SESSION,
        end_date=SESSION,
        confirmed_setup_count=3,
        available_entry_count=2,
        session_end_unavailable_count=1,
        missing_entry_count=0,
        outcomes=(
            _outcome(matching, "3"),
            _outcome(opposing, "2"),
            _outcome(no_cross, "1", available=False),
        ),
    )
    base = calculate_base_strategy_statistics(
        setup_result, outcome_result, development_session_count=1
    )
    cross_annotations = (
        select_prior_ema_cross(matching, (cross(CONFIRMATION),)),
        select_prior_ema_cross(
            opposing,
            (
                cross(
                    CONFIRMATION + timedelta(minutes=5),
                    EmaCrossDirection.BEARISH,
                ),
            ),
        ),
        select_prior_ema_cross(no_cross, ()),
    )
    alignment_annotations = tuple(
        EmaAlignmentAnnotation(
            setup_identity=item.setup_identity,
            session_date=item.session_date,
            direction=item.direction,
            confirmation_bar_timestamp=item.confirmation_bar_timestamp,
            signal_known_at=item.signal_known_at,
            ema9=None,
            ema20=None,
            alignment_state=EmaAlignmentState.EMA_UNAVAILABLE,
            indicator_timestamp=None,
            indicator_available=False,
        )
        for item in (matching, opposing, no_cross)
    )
    result = calculate_ema_cross_context_comparison(
        setup_result,
        outcome_result,
        base,
        cross_annotations,
        alignment_annotations,
        stage4_event_count=2,
    )
    assert [item.annotation_n for item in result.groups] == [3, 1, 1, 1]
    assert [item.executable_n for item in result.groups] == [2, 1, 1, 0]
    assert result.groups[0].horizons == base.groups[0].horizons
    assert result.bars_since_cross_distribution.n == 2
    assert [(item.bars_since_cross, item.annotation_n) for item in result.recency_rows] == [(0, 2)]
    assert sum(item.annotation_n for item in result.alignment_cross_tab) == 3


def test_cli_command_is_offline_read_only(monkeypatch, tmp_path, capsys) -> None:
    sentinel = object()

    def mocked_calculate(self, *, start, end):
        assert start == end == SESSION
        return sentinel

    def mocked_print(result):
        assert result is sentinel
        print("cross-context-pass")

    def reject_network(*args, **kwargs):
        raise AssertionError("cross-context CLI must remain offline")

    monkeypatch.setattr(EmaCrossContextComparisonService, "calculate", mocked_calculate)
    monkeypatch.setattr(cli_module, "_print_ema_cross_context_comparison", mocked_print)
    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = cli_module.main([
        "compare-ema-cross-context",
        "--start", SESSION.isoformat(),
        "--end", SESSION.isoformat(),
        "--raw-data-root", str(tmp_path / "raw"),
        "--processed-data-root", str(tmp_path / "processed"),
    ])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "cross-context-pass\n"
    assert captured.err == ""
    assert list(tmp_path.iterdir()) == []
