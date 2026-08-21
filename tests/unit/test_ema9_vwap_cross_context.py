from __future__ import annotations

import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

import spy_research.cli as cli_module
from spy_research.indicators import FiveMinuteIndicatorRow, FiveMinuteVwapRow
from spy_research.interactions import (
    ImmediateState,
    InteractionType,
    LevelType,
    RetestState,
)
from spy_research.strategy import (
    BasePriceActionCandidate,
    BaseSetupStatus,
    ConfirmationType,
    SetupDirection,
)
from spy_research.strategy.comparisons import (
    Ema9VwapCrossContextComparisonService,
    Ema9VwapCrossContextState,
    Ema9VwapCrossDirection,
    Ema9VwapCrossInputError,
    detect_ema9_vwap_crosses,
    select_prior_ema9_vwap_cross,
)


SESSION = date(2026, 8, 19)
START = datetime(2026, 8, 19, 14, 0, tzinfo=UTC)


def rows(values, *, start=START, session=SESSION):
    ema_rows = []
    vwap_rows = []
    for index, (ema9, vwap) in enumerate(values):
        timestamp = start + timedelta(minutes=index * 5)
        ema_rows.append(
            FiveMinuteIndicatorRow(
                symbol="SPY",
                timestamp=timestamp,
                session_date=session,
                close=Decimal("100"),
                ema9=Decimal(ema9) if ema9 is not None else None,
                ema20=None,
            )
        )
        vwap_rows.append(
            FiveMinuteVwapRow(
                symbol="SPY",
                timestamp=timestamp,
                session_date=session,
                typical_price=Decimal("100"),
                vwap=Decimal(vwap) if vwap is not None else None,
            )
        )
    return tuple(ema_rows), tuple(vwap_rows)


def setup(
    direction=SetupDirection.LONG,
    *,
    confirmation=START + timedelta(minutes=5),
):
    signal = confirmation + timedelta(minutes=5)
    return BasePriceActionCandidate(
        setup_identity="setup",
        break_interaction_identity="break",
        follow_through_identity="follow",
        session_date=SESSION,
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


@pytest.mark.parametrize(
    "values,direction",
    (
        ((("100", "100"), ("101", "100")), Ema9VwapCrossDirection.BULLISH),
        ((("100", "100"), ("99", "100")), Ema9VwapCrossDirection.BEARISH),
        ((("99", "100"), ("101", "100")), Ema9VwapCrossDirection.BULLISH),
        ((("101", "100"), ("99", "100")), Ema9VwapCrossDirection.BEARISH),
    ),
)
def test_cross_definition_including_equality(values, direction) -> None:
    ema_rows, vwap_rows = rows(values)
    events, _ = detect_ema9_vwap_crosses(ema_rows, vwap_rows)
    assert len(events) == 1
    assert events[0].direction is direction
    assert events[0].cross_timestamp == START + timedelta(minutes=5)
    assert events[0].cross_known_at == START + timedelta(minutes=10)


@pytest.mark.parametrize(
    "values",
    (
        (("101", "100"), ("102", "100"), ("103", "100")),
        (("99", "100"), ("98", "100"), ("97", "100")),
    ),
)
def test_persistent_relationship_does_not_repeat(values) -> None:
    events, _ = detect_ema9_vwap_crosses(*rows(values))
    assert events == ()


@pytest.mark.parametrize(
    "values",
    (
        ((None, "100"), ("101", "100")),
        (("99", "100"), (None, "100")),
        (("99", None), ("101", "100")),
    ),
)
def test_missing_current_or_prior_indicator_prevents_cross(values) -> None:
    events, _ = detect_ema9_vwap_crosses(*rows(values))
    assert events == ()


def test_event_identity_is_deterministic() -> None:
    source = rows((("99", "100"), ("101", "100")))
    first = detect_ema9_vwap_crosses(*source)[0]
    second = detect_ema9_vwap_crosses(*source)[0]
    assert first == second
    assert len(first[0].event_identity) == 64


def test_cross_detection_resets_without_overnight_bridge() -> None:
    first_ema, first_vwap = rows((("99", "100"),))
    next_session = SESSION + timedelta(days=1)
    second_ema, second_vwap = rows(
        (("101", "100"),),
        start=START + timedelta(days=1),
        session=next_session,
    )
    events, summaries = detect_ema9_vwap_crosses(
        first_ema + second_ema,
        first_vwap + second_vwap,
    )
    assert events == ()
    assert [item.total_crosses for item in summaries] == [0, 0]


@pytest.mark.parametrize(
    "direction,cross_direction,expected",
    (
        (
            SetupDirection.LONG,
            Ema9VwapCrossDirection.BULLISH,
            Ema9VwapCrossContextState.MATCHING_EMA9_VWAP_CROSS,
        ),
        (
            SetupDirection.LONG,
            Ema9VwapCrossDirection.BEARISH,
            Ema9VwapCrossContextState.OPPOSING_EMA9_VWAP_CROSS,
        ),
        (
            SetupDirection.SHORT,
            Ema9VwapCrossDirection.BEARISH,
            Ema9VwapCrossContextState.MATCHING_EMA9_VWAP_CROSS,
        ),
        (
            SetupDirection.SHORT,
            Ema9VwapCrossDirection.BULLISH,
            Ema9VwapCrossContextState.OPPOSING_EMA9_VWAP_CROSS,
        ),
    ),
)
def test_directional_context_mapping(direction, cross_direction, expected) -> None:
    values = (
        (("99", "100"), ("101", "100"))
        if cross_direction is Ema9VwapCrossDirection.BULLISH
        else (("101", "100"), ("99", "100"))
    )
    event = detect_ema9_vwap_crosses(*rows(values))[0][0]
    annotation = select_prior_ema9_vwap_cross(setup(direction), (event,))
    assert annotation.cross_state is expected
    assert annotation.bars_since_cross == 0
    assert annotation.minutes_since_cross_completion == 0


@pytest.mark.parametrize("bars", (0, 1, 3))
def test_exact_recency(bars) -> None:
    event = detect_ema9_vwap_crosses(
        *rows((("99", "100"), ("101", "100")))
    )[0][0]
    item = setup(confirmation=event.cross_timestamp + timedelta(minutes=bars * 5))
    annotation = select_prior_ema9_vwap_cross(item, (event,))
    assert annotation.bars_since_cross == bars
    assert annotation.minutes_since_cross_completion == bars * 5


def test_future_cross_and_later_cross_cannot_change_prior_annotation() -> None:
    events = detect_ema9_vwap_crosses(
        *rows((("99", "100"), ("101", "100"), ("99", "100")))
    )[0]
    item = setup(confirmation=events[0].cross_timestamp)
    assert len(events) == 2
    first = select_prior_ema9_vwap_cross(item, events[:1])
    second = select_prior_ema9_vwap_cross(item, events)
    assert first == second


def test_newer_opposing_cross_overrides_older_matching_cross() -> None:
    events = detect_ema9_vwap_crosses(
        *rows((("99", "100"), ("101", "100"), ("99", "100")))
    )[0]
    item = setup(SetupDirection.LONG, confirmation=events[-1].cross_timestamp)
    annotation = select_prior_ema9_vwap_cross(item, events)
    assert annotation.cross_timestamp == events[-1].cross_timestamp
    assert annotation.cross_state is Ema9VwapCrossContextState.OPPOSING_EMA9_VWAP_CROSS


def test_no_prior_cross_is_explicit() -> None:
    annotation = select_prior_ema9_vwap_cross(setup(), ())
    assert annotation.cross_state is Ema9VwapCrossContextState.NO_PRIOR_EMA9_VWAP_CROSS
    assert annotation.cross_timestamp is None


def test_detector_and_context_are_offline_nonpersistent(monkeypatch, tmp_path) -> None:
    def reject_network(*args, **kwargs):
        raise AssertionError("Stage 10.5 must remain offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    events = detect_ema9_vwap_crosses(
        *rows((("99", "100"), ("101", "100")))
    )[0]
    select_prior_ema9_vwap_cross(setup(), events)
    assert list(tmp_path.iterdir()) == []


def test_cli_is_offline_and_read_only(monkeypatch, tmp_path, capsys) -> None:
    sentinel = object()

    def mocked_calculate(self, *, start, end):
        return sentinel

    def mocked_print(result):
        assert result is sentinel
        print("ema9-vwap-cross-pass")

    monkeypatch.setattr(
        Ema9VwapCrossContextComparisonService, "calculate", mocked_calculate
    )
    monkeypatch.setattr(
        cli_module, "_print_ema9_vwap_cross_context_comparison", mocked_print
    )
    exit_code = cli_module.main(
        [
            "compare-ema9-vwap-cross-context",
            "--start",
            SESSION.isoformat(),
            "--end",
            SESSION.isoformat(),
            "--raw-data-root",
            str(tmp_path / "raw"),
            "--processed-data-root",
            str(tmp_path / "processed"),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "ema9-vwap-cross-pass\n"
    assert captured.err == ""
    assert list(tmp_path.iterdir()) == []
