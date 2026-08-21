from __future__ import annotations

import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from spy_research.cli import main
from spy_research.indicators import FiveMinuteIndicatorRow
from spy_research.interactions import (
    ImmediateState,
    InteractionType,
    LevelType,
    RetestState,
)
from spy_research.strategy import (
    BasePriceActionCandidate,
    BasePriceActionResult,
    BaseSetupStatus,
    BaseStrategyGroupDimension,
    ConfirmationType,
    EntryStatus,
    SetupDirection,
    SetupEntryReference,
    SetupHorizonOutcome,
    SetupOutcome,
    SetupOutcomeResult,
    calculate_base_strategy_statistics,
)
from spy_research.strategy.comparisons import (
    EmaAlignmentComparisonService,
    EmaAlignmentState,
    EmaComparisonInputError,
    annotate_confirmed_setups,
    annotate_ema_alignment,
    calculate_ema_alignment_comparison,
)


SESSION = date(2026, 8, 19)
START = date(2026, 8, 3)
END = date(2026, 8, 19)
CONFIRMATION = datetime(2026, 8, 19, 14, 0, tzinfo=UTC)
SIGNAL = CONFIRMATION + timedelta(minutes=5)


def setup(
    identity: str,
    direction: SetupDirection = SetupDirection.LONG,
    *,
    confirmation: datetime = CONFIRMATION,
    confirmed: bool = True,
    executable: bool = True,
    level: LevelType = LevelType.PDH,
) -> BasePriceActionCandidate:
    signal = confirmation + timedelta(minutes=5)
    return BasePriceActionCandidate(
        setup_identity=identity,
        break_interaction_identity=f"break-{identity}",
        follow_through_identity=f"follow-{identity}",
        session_date=confirmation.date(),
        level_type=level,
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
        status=BaseSetupStatus.CONFIRMED if confirmed else BaseSetupStatus.NO_RETEST,
        confirmation_type=ConfirmationType.IMMEDIATE_HOLD if confirmed else None,
        confirmation_bar_timestamp=confirmation if confirmed else None,
        signal_known_at=signal if confirmed else None,
        earliest_entry_timestamp=signal if confirmed else None,
        same_session_executable=executable if confirmed else False,
    )


def ema_row(
    ema9: str | None,
    ema20: str | None,
    *,
    timestamp: datetime = CONFIRMATION,
    session_date: date = SESSION,
) -> FiveMinuteIndicatorRow:
    return FiveMinuteIndicatorRow(
        symbol="SPY",
        timestamp=timestamp,
        session_date=session_date,
        close=Decimal("100"),
        ema9=Decimal(ema9) if ema9 is not None else None,
        ema20=Decimal(ema20) if ema20 is not None else None,
    )


@pytest.mark.parametrize(
    "direction, ema9, ema20, expected",
    (
        (SetupDirection.LONG, "101", "100", EmaAlignmentState.EMA_ALIGNED),
        (SetupDirection.LONG, "99", "100", EmaAlignmentState.EMA_NOT_ALIGNED),
        (SetupDirection.LONG, "100", "100", EmaAlignmentState.EMA_NOT_ALIGNED),
        (SetupDirection.SHORT, "99", "100", EmaAlignmentState.EMA_ALIGNED),
        (SetupDirection.SHORT, "101", "100", EmaAlignmentState.EMA_NOT_ALIGNED),
        (SetupDirection.SHORT, "100", "100", EmaAlignmentState.EMA_NOT_ALIGNED),
    ),
)
def test_directional_alignment_rules(direction, ema9, ema20, expected) -> None:
    annotation = annotate_ema_alignment(setup("rule", direction), ema_row(ema9, ema20))
    assert annotation.alignment_state is expected
    assert annotation.indicator_timestamp == CONFIRMATION
    assert annotation.setup_identity == "rule"


@pytest.mark.parametrize("ema9, ema20", ((None, "100"), ("100", None), (None, None)))
def test_missing_or_prewarmup_ema_is_explicitly_unavailable(ema9, ema20) -> None:
    annotation = annotate_ema_alignment(setup("warmup"), ema_row(ema9, ema20))
    assert annotation.alignment_state is EmaAlignmentState.EMA_UNAVAILABLE
    assert not annotation.indicator_available


def test_confirmation_row_is_used_and_later_values_cannot_change_label() -> None:
    item = setup("exact")
    setup_result = BasePriceActionResult(
        start_date=SESSION,
        end_date=SESSION,
        seed_count=1,
        confirmed_count=1,
        non_confirmed_count=0,
        candidates=(item,),
    )
    exact = ema_row("101", "100")
    later_a = ema_row("1", "200", timestamp=CONFIRMATION + timedelta(minutes=5))
    later_b = ema_row("999", "1", timestamp=CONFIRMATION + timedelta(minutes=5))
    first = annotate_confirmed_setups(setup_result, (exact, later_a))
    second = annotate_confirmed_setups(setup_result, (exact, later_b))
    assert first == second
    assert first[0].alignment_state is EmaAlignmentState.EMA_ALIGNED
    assert first[0].indicator_timestamp == item.confirmation_bar_timestamp


def test_entry_timestamp_cannot_select_the_next_ema_row() -> None:
    item = setup("entry-time")
    setup_result = BasePriceActionResult(
        start_date=SESSION,
        end_date=SESSION,
        seed_count=1,
        confirmed_count=1,
        non_confirmed_count=0,
        candidates=(item,),
    )
    at_entry = ema_row("101", "100", timestamp=item.earliest_entry_timestamp)
    annotation = annotate_confirmed_setups(setup_result, (at_entry,))[0]
    assert annotation.alignment_state is EmaAlignmentState.EMA_UNAVAILABLE
    assert annotation.indicator_timestamp is None


def test_no_previous_or_next_session_fallback() -> None:
    item = setup("session")
    setup_result = BasePriceActionResult(
        start_date=SESSION,
        end_date=SESSION,
        seed_count=1,
        confirmed_count=1,
        non_confirmed_count=0,
        candidates=(item,),
    )
    previous = ema_row(
        "101",
        "100",
        timestamp=CONFIRMATION - timedelta(days=1),
        session_date=SESSION - timedelta(days=1),
    )
    following = ema_row(
        "101",
        "100",
        timestamp=CONFIRMATION + timedelta(days=1),
        session_date=SESSION + timedelta(days=1),
    )
    annotation = annotate_confirmed_setups(setup_result, (previous, following))[0]
    assert annotation.alignment_state is EmaAlignmentState.EMA_UNAVAILABLE


def test_mismatched_direct_indicator_row_is_rejected() -> None:
    with pytest.raises(EmaComparisonInputError, match="confirmation timestamp"):
        annotate_ema_alignment(
            setup("mismatch"),
            ema_row("101", "100", timestamp=CONFIRMATION + timedelta(minutes=5)),
        )


def test_nonconfirmed_seeds_are_not_annotated() -> None:
    rejected = setup("rejected", confirmed=False)
    setup_result = BasePriceActionResult(
        start_date=SESSION,
        end_date=SESSION,
        seed_count=1,
        confirmed_count=0,
        non_confirmed_count=1,
        candidates=(rejected,),
    )
    assert annotate_confirmed_setups(setup_result, (ema_row("101", "100"),)) == ()
    with pytest.raises(EmaComparisonInputError, match="Only confirmed"):
        annotate_ema_alignment(rejected, ema_row("101", "100"))


def test_annotation_order_and_indicator_inputs_are_immutable() -> None:
    first_setup = setup("first", confirmation=CONFIRMATION)
    second_setup = setup(
        "second",
        confirmation=CONFIRMATION + timedelta(minutes=5),
    )
    setup_result = BasePriceActionResult(
        start_date=SESSION,
        end_date=SESSION,
        seed_count=2,
        confirmed_count=2,
        non_confirmed_count=0,
        candidates=(first_setup, second_setup),
    )
    rows = (
        ema_row("101", "100", timestamp=CONFIRMATION),
        ema_row("99", "100", timestamp=CONFIRMATION + timedelta(minutes=5)),
    )
    before = tuple(row.model_dump() for row in rows)
    annotations = annotate_confirmed_setups(setup_result, rows)
    assert [item.setup_identity for item in annotations] == ["first", "second"]
    assert tuple(row.model_dump() for row in rows) == before


def horizon(name: str, mfe: str, mae: str, *, complete: bool = True):
    requested = {"5m": 5, "15m": 15, "30m": 30, "60m": 60, "EOD": 100}[name]
    return SetupHorizonOutcome(
        horizon=name,
        requested_minutes=requested,
        available_minutes=requested if complete else requested - 1,
        complete=complete,
        mfe=Decimal(mfe),
        mae=Decimal(mae),
        mfe_timestamp=SIGNAL,
        mae_timestamp=SIGNAL,
    )


def outcome(
    item: BasePriceActionCandidate,
    *,
    mfe: str,
    mae: str,
    complete_15m: bool = True,
    available: bool = True,
) -> SetupOutcome:
    if not available:
        reference = SetupEntryReference(
            setup_identity=item.setup_identity,
            session_date=item.session_date,
            direction=item.direction,
            signal_known_at=item.signal_known_at,
            earliest_entry_timestamp=item.earliest_entry_timestamp,
            entry_status=EntryStatus.ENTRY_UNAVAILABLE_SESSION_END,
        )
        return SetupOutcome(
            setup_identity=item.setup_identity,
            setup=item,
            entry_reference=reference,
        )
    reference = SetupEntryReference(
        setup_identity=item.setup_identity,
        session_date=item.session_date,
        direction=item.direction,
        signal_known_at=item.signal_known_at,
        earliest_entry_timestamp=item.earliest_entry_timestamp,
        entry_status=EntryStatus.AVAILABLE,
        entry_reference_timestamp=item.earliest_entry_timestamp,
        entry_reference_price=Decimal("100"),
        entry_delay_minutes=0,
    )
    return SetupOutcome(
        setup_identity=item.setup_identity,
        setup=item,
        entry_reference=reference,
        five=horizon("5m", mfe, mae),
        fifteen=horizon("15m", mfe, mae, complete=complete_15m),
        thirty=horizon("30m", mfe, mae),
        sixty=horizon("60m", mfe, mae),
        eod=horizon("EOD", mfe, mae),
    )


def comparison_fixture():
    aligned_long = setup("aligned-long", SetupDirection.LONG)
    not_short = setup(
        "not-short",
        SetupDirection.SHORT,
        confirmation=CONFIRMATION + timedelta(minutes=5),
        level=LevelType.PDL,
    )
    unavailable_long = setup(
        "unavailable-long",
        SetupDirection.LONG,
        confirmation=CONFIRMATION + timedelta(minutes=10),
        level=LevelType.ORH5,
    )
    closed_short = setup(
        "closed-short",
        SetupDirection.SHORT,
        confirmation=CONFIRMATION + timedelta(minutes=15),
        executable=False,
        level=LevelType.ORL5,
    )
    setups = (aligned_long, not_short, unavailable_long, closed_short)
    setup_result = BasePriceActionResult(
        start_date=START,
        end_date=END,
        seed_count=4,
        confirmed_count=4,
        non_confirmed_count=0,
        candidates=setups,
    )
    outcomes = (
        outcome(aligned_long, mfe="3", mae="1"),
        outcome(not_short, mfe="1", mae="2", complete_15m=False),
        outcome(unavailable_long, mfe="2", mae="2"),
        outcome(closed_short, mfe="0", mae="0", available=False),
    )
    outcome_result = SetupOutcomeResult(
        start_date=START,
        end_date=END,
        confirmed_setup_count=4,
        available_entry_count=3,
        session_end_unavailable_count=1,
        missing_entry_count=0,
        outcomes=outcomes,
    )
    base = calculate_base_strategy_statistics(
        setup_result,
        outcome_result,
        development_session_count=13,
    )
    rows = (
        ema_row("101", "100", timestamp=CONFIRMATION),
        ema_row("101", "100", timestamp=CONFIRMATION + timedelta(minutes=5)),
        ema_row(None, None, timestamp=CONFIRMATION + timedelta(minutes=10)),
        ema_row("99", "100", timestamp=CONFIRMATION + timedelta(minutes=15)),
    )
    annotations = annotate_confirmed_setups(setup_result, rows)
    result = calculate_ema_alignment_comparison(
        setup_result,
        outcome_result,
        base,
        annotations,
    )
    return setup_result, outcome_result, base, rows, result


def test_base_all_exactly_reproduces_stage_9_statistics() -> None:
    _, _, base, _, result = comparison_fixture()
    baseline = next(
        item
        for item in base.groups
        if item.dimension is BaseStrategyGroupDimension.OVERALL
    )
    assert result.groups[0].horizons == baseline.horizons


def test_alignment_groups_partition_annotations_and_executable_outcomes() -> None:
    _, _, _, _, result = comparison_fixture()
    assert [item.annotation_n for item in result.groups] == [4, 2, 1, 1]
    assert [item.executable_n for item in result.groups] == [3, 1, 1, 1]
    assert sum(item.annotation_n for item in result.groups[1:]) == 4
    assert sum(item.executable_n for item in result.groups[1:]) == 3


def test_completeness_and_direction_partitions_are_unchanged() -> None:
    _, _, _, _, result = comparison_fixture()
    not_aligned = result.groups[2]
    assert not_aligned.horizons[1].complete_n == 0
    assert not_aligned.horizons[1].incomplete_n == 1
    assert sum(item.executable_n for item in result.direction_groups) == 3
    assert [item.executable_n for item in result.direction_groups] == [1, 0, 1, 0, 1, 0]


def test_empty_groups_and_baseline_deltas_are_deterministic() -> None:
    _, _, _, _, result = comparison_fixture()
    assert result == comparison_fixture()[-1]
    aligned = result.groups[1]
    assert aligned.deltas[-1].median_mfe_delta == Decimal("1")
    empty = result.direction_groups[1]
    assert empty.executable_n == 0
    assert empty.horizons[-1].mfe.median is None


def test_comparison_cannot_mutate_stage_9_or_stage_3_inputs() -> None:
    setup_result, outcome_result, base, rows, _ = comparison_fixture()
    before = (
        setup_result.model_dump(),
        outcome_result.model_dump(),
        base.model_dump(),
        tuple(item.model_dump() for item in rows),
    )
    annotations = annotate_confirmed_setups(setup_result, rows)
    calculate_ema_alignment_comparison(
        setup_result, outcome_result, base, annotations
    )
    assert before == (
        setup_result.model_dump(),
        outcome_result.model_dump(),
        base.model_dump(),
        tuple(item.model_dump() for item in rows),
    )


def test_pure_comparison_is_offline_and_nonpersistent(monkeypatch, tmp_path) -> None:
    def reject_network(*args, **kwargs):
        raise AssertionError("Stage 10.1 comparison must remain offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    comparison_fixture()
    assert list(tmp_path.iterdir()) == []


def test_cli_is_offline_read_only_and_reports_controlled_comparison(
    monkeypatch, tmp_path, capsys
) -> None:
    result = comparison_fixture()[-1]

    def mocked_calculate(self, *, start, end):
        return result

    def reject_network(*args, **kwargs):
        raise AssertionError("compare-ema-alignment CLI must remain offline")

    monkeypatch.setattr(EmaAlignmentComparisonService, "calculate", mocked_calculate)
    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "compare-ema-alignment",
            "--start",
            START.isoformat(),
            "--end",
            END.isoformat(),
            "--raw-data-root",
            str(tmp_path / "raw"),
            "--processed-data-root",
            str(tmp_path / "processed"),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "BASE_ALL: setups=4" in captured.out
    assert "development sample = 13 sessions" in captured.out
    assert "do not modify Stage 9" in captured.out
    assert captured.err == ""
    assert list(tmp_path.iterdir()) == []
