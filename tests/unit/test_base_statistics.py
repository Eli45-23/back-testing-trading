from __future__ import annotations

import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, localcontext

import pytest

from spy_research.cli import main
from spy_research.indicators.ema import EMA_CONTEXT
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
    BaseStatisticsInputError,
    BaseStrategyGroupDimension,
    BaseStrategyStatisticsService,
    ConfirmationType,
    EntryStatus,
    SetupDirection,
    SetupEntryReference,
    SetupHorizonOutcome,
    SetupOutcome,
    SetupOutcomeResult,
    calculate_base_strategy_statistics,
)


SESSION = date(2026, 8, 19)
START = date(2026, 8, 3)
END = date(2026, 8, 19)
DEFAULT_ENTRY = datetime(2026, 8, 19, 14, 0, tzinfo=UTC)


def candidate(
    identity: str,
    *,
    direction: SetupDirection = SetupDirection.LONG,
    level: LevelType = LevelType.PDH,
    confirmation: ConfirmationType = ConfirmationType.IMMEDIATE_HOLD,
    entry_time: datetime = DEFAULT_ENTRY,
    confirmed: bool = True,
    executable: bool = True,
) -> BasePriceActionCandidate:
    return BasePriceActionCandidate(
        setup_identity=identity,
        break_interaction_identity=f"break-{identity}",
        follow_through_identity=f"follow-{identity}",
        session_date=SESSION,
        level_type=level,
        level_price=Decimal("100"),
        direction=direction,
        break_interaction_type=(
            InteractionType.CLOSE_THROUGH_ABOVE
            if direction is SetupDirection.LONG
            else InteractionType.CLOSE_THROUGH_BELOW
        ),
        break_timestamp=entry_time - timedelta(minutes=10),
        break_completed_at=entry_time - timedelta(minutes=5),
        exact_immediate_state=ImmediateState.HOLD,
        exact_retest_state=(
            RetestState.RETEST_HOLD
            if confirmation is ConfirmationType.RETEST_HOLD
            else RetestState.NO_RETEST
        ),
        status=BaseSetupStatus.CONFIRMED if confirmed else BaseSetupStatus.NO_RETEST,
        confirmation_type=confirmation if confirmed else None,
        confirmation_bar_timestamp=(
            entry_time - timedelta(minutes=5) if confirmed else None
        ),
        signal_known_at=entry_time if confirmed else None,
        earliest_entry_timestamp=entry_time if confirmed else None,
        retest_bar_offset=(
            1
            if confirmed and confirmation is ConfirmationType.RETEST_HOLD
            else None
        ),
        same_session_executable=executable if confirmed else False,
    )


def horizon(
    name: str,
    mfe: str,
    mae: str,
    *,
    complete: bool = True,
) -> SetupHorizonOutcome:
    requested = {"5m": 5, "15m": 15, "30m": 30, "60m": 60, "EOD": 120}[name]
    return SetupHorizonOutcome(
        horizon=name,
        requested_minutes=requested,
        available_minutes=requested if complete else requested - 1,
        complete=complete,
        mfe=Decimal(mfe),
        mae=Decimal(mae),
        mfe_timestamp=DEFAULT_ENTRY,
        mae_timestamp=DEFAULT_ENTRY,
    )


def setup_outcome(
    item: BasePriceActionCandidate,
    *,
    mfe: str = "2",
    mae: str = "1",
    incomplete: set[str] | None = None,
) -> SetupOutcome:
    incomplete = incomplete or set()
    entry = SetupEntryReference(
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
    values = {
        name: horizon(name, mfe, mae, complete=name not in incomplete)
        for name in ("5m", "15m", "30m", "60m", "EOD")
    }
    return SetupOutcome(
        setup_identity=item.setup_identity,
        setup=item,
        entry_reference=entry,
        five=values["5m"],
        fifteen=values["15m"],
        thirty=values["30m"],
        sixty=values["60m"],
        eod=values["EOD"],
    )


def unavailable_outcome(item: BasePriceActionCandidate) -> SetupOutcome:
    entry = SetupEntryReference(
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
        entry_reference=entry,
    )


def results(
    available: tuple[SetupOutcome, ...],
    *,
    unavailable: tuple[SetupOutcome, ...] = (),
    nonconfirmed: tuple[BasePriceActionCandidate, ...] = (),
) -> tuple[BasePriceActionResult, SetupOutcomeResult]:
    confirmed = tuple(item.setup for item in available + unavailable)
    setup_result = BasePriceActionResult(
        start_date=START,
        end_date=END,
        seed_count=len(confirmed) + len(nonconfirmed),
        confirmed_count=len(confirmed),
        non_confirmed_count=len(nonconfirmed),
        candidates=confirmed + nonconfirmed,
    )
    outcome_result = SetupOutcomeResult(
        start_date=START,
        end_date=END,
        confirmed_setup_count=len(confirmed),
        available_entry_count=len(available),
        session_end_unavailable_count=len(unavailable),
        missing_entry_count=0,
        outcomes=available + unavailable,
    )
    return setup_result, outcome_result


def report_for(*items: SetupOutcome, unavailable=(), nonconfirmed=()):
    setup_result, outcome_result = results(
        tuple(items),
        unavailable=tuple(unavailable),
        nonconfirmed=tuple(nonconfirmed),
    )
    return calculate_base_strategy_statistics(
        setup_result,
        outcome_result,
        development_session_count=13,
    )


def group(report, dimension, name):
    return next(
        item
        for item in report.groups
        if item.dimension is dimension and item.name == name
    )


def test_population_excludes_non_executable_and_preserves_funnel_counts() -> None:
    live = setup_outcome(candidate("live"))
    closed_setup = candidate("closed", executable=False)
    rejected = candidate("rejected", confirmed=False)
    report = report_for(
        live,
        unavailable=(unavailable_outcome(closed_setup),),
        nonconfirmed=(rejected,),
    )
    assert (
        report.break_seed_count,
        report.confirmed_count,
        report.non_confirmed_count,
    ) == (3, 2, 1)
    assert report.executable_count == 1
    assert report.session_end_unavailable_count == 1
    assert report.immediate_hold_confirmed_count == 2
    assert report.retest_hold_confirmed_count == 0
    assert (
        group(report, BaseStrategyGroupDimension.OVERALL, "OVERALL").executable_n
        == 1
    )


def test_incomplete_fixed_window_is_excluded_but_counted() -> None:
    report = report_for(setup_outcome(candidate("a"), incomplete={"30m"}))
    thirty = group(report, BaseStrategyGroupDimension.OVERALL, "OVERALL").horizons[2]
    assert thirty.complete_n == 0
    assert thirty.incomplete_n == 1
    assert thirty.mfe.mean is None
    assert (
        group(report, BaseStrategyGroupDimension.OVERALL, "OVERALL")
        .horizons[4]
        .complete_n
        == 1
    )


@pytest.mark.parametrize(
    "values, expected_median",
    ((("1", "2", "10"), Decimal("2")), (("1", "2", "4", "10"), Decimal("3"))),
)
def test_odd_and_even_decimal_distribution_statistics(values, expected_median) -> None:
    items = tuple(
        setup_outcome(candidate(f"item-{index}"), mfe=value, mae="1")
        for index, value in enumerate(values)
    )
    stats = group(
        report_for(*items), BaseStrategyGroupDimension.OVERALL, "OVERALL"
    ).horizons[0]
    with localcontext(EMA_CONTEXT):
        expected_mean = sum(
            (Decimal(value) for value in values), Decimal()
        ) / Decimal(len(values))
    assert stats.mfe.mean == expected_mean
    assert stats.mfe.median == expected_median
    assert stats.mfe.minimum == Decimal(min(values, key=Decimal))
    assert stats.mfe.maximum == Decimal(max(values, key=Decimal))
    assert stats.mae.mean == stats.mae.median == Decimal("1")


def test_paired_balance_comparisons_and_ratio_zero_handling() -> None:
    pairs = (("2", "1"), ("1", "1"), ("1", "2"), ("4", "0"))
    items = tuple(
        setup_outcome(candidate(f"pair-{index}"), mfe=mfe, mae=mae)
        for index, (mfe, mae) in enumerate(pairs)
    )
    stats = group(
        report_for(*items), BaseStrategyGroupDimension.OVERALL, "OVERALL"
    ).horizons[0]
    assert stats.net_excursion_balance.median == Decimal("0.5")
    assert stats.favorable_adverse.mfe_greater == 2
    assert stats.favorable_adverse.equal == 1
    assert stats.favorable_adverse.mfe_less == 1
    assert stats.valid_ratio_n == 3
    assert stats.zero_mae_n == 1
    assert stats.median_mfe_mae_ratio == Decimal("1")


@pytest.mark.parametrize("direction", tuple(SetupDirection))
def test_direction_groups(direction) -> None:
    item = setup_outcome(candidate(direction.value, direction=direction))
    report = report_for(item)
    assert (
        group(
            report, BaseStrategyGroupDimension.DIRECTION, direction.value
        ).executable_n
        == 1
    )


@pytest.mark.parametrize("level", tuple(LevelType))
def test_every_level_group_is_retained(level) -> None:
    item = setup_outcome(candidate(level.value, level=level))
    report = report_for(item)
    assert (
        group(report, BaseStrategyGroupDimension.LEVEL, level.value).executable_n
        == 1
    )
    assert sum(
        value.executable_n
        for value in report.groups
        if value.dimension is BaseStrategyGroupDimension.LEVEL
    ) == 1


def test_confirmation_groups_include_empty_retest_population() -> None:
    report = report_for(setup_outcome(candidate("immediate")))
    assert (
        group(
            report,
            BaseStrategyGroupDimension.CONFIRMATION,
            "IMMEDIATE_HOLD",
        ).executable_n
        == 1
    )
    empty = group(report, BaseStrategyGroupDimension.CONFIRMATION, "RETEST_HOLD")
    assert empty.executable_n == 0
    assert all(item.complete_n == 0 for item in empty.horizons)


@pytest.mark.parametrize(
    "hour, minute, label",
    (
        (9, 30, "09:30-09:59"),
        (10, 0, "10:00-10:59"),
        (11, 0, "11:00-11:59"),
        (12, 0, "12:00-12:59"),
        (13, 0, "13:00-13:59"),
        (14, 0, "14:00-14:59"),
        (15, 59, "15:00-16:00"),
    ),
)
def test_entry_time_bucket_boundaries(hour, minute, label) -> None:
    from zoneinfo import ZoneInfo

    entry = datetime(2026, 8, 19, hour, minute, tzinfo=ZoneInfo("America/New_York"))
    item = setup_outcome(candidate(label, entry_time=entry))
    report = report_for(item)
    assert (
        group(
            report, BaseStrategyGroupDimension.ENTRY_TIME_BUCKET, label
        ).executable_n
        == 1
    )
    assert sum(
        value.executable_n
        for value in report.groups
        if value.dimension is BaseStrategyGroupDimension.ENTRY_TIME_BUCKET
    ) == 1


def test_group_order_is_frozen_and_rerun_is_identical() -> None:
    item = setup_outcome(candidate("stable"))
    first = report_for(item)
    second = report_for(item)
    assert first == second
    assert [value.dimension for value in first.groups[:3]] == [
        BaseStrategyGroupDimension.OVERALL,
        BaseStrategyGroupDimension.DIRECTION,
        BaseStrategyGroupDimension.DIRECTION,
    ]
    assert [value.name for value in first.groups[:3]] == ["OVERALL", "LONG", "SHORT"]


def test_mismatched_embedded_setup_is_rejected() -> None:
    original = setup_outcome(candidate("same"))
    setup_result, outcome_result = results((original,))
    changed = original.model_copy(
        update={"setup": candidate("same", level=LevelType.PDL)}
    )
    bad_result = outcome_result.model_copy(update={"outcomes": (changed,)})
    with pytest.raises(BaseStatisticsInputError, match="Embedded"):
        calculate_base_strategy_statistics(
            setup_result, bad_result, development_session_count=13
        )


def test_duplicate_outcome_identity_is_rejected() -> None:
    item = setup_outcome(candidate("duplicate"))
    setup_result, outcome_result = results((item,))
    bad_result = outcome_result.model_copy(
        update={
            "confirmed_setup_count": 2,
            "available_entry_count": 2,
            "outcomes": (item, item),
        }
    )
    with pytest.raises(BaseStatisticsInputError, match="Duplicate setup outcome"):
        calculate_base_strategy_statistics(
            setup_result, bad_result, development_session_count=13
        )


def test_missing_required_horizon_is_rejected() -> None:
    item = setup_outcome(candidate("missing"))
    setup_result, outcome_result = results((item,))
    missing = item.model_copy(update={"five": None})
    bad_result = outcome_result.model_copy(update={"outcomes": (missing,)})
    with pytest.raises(BaseStatisticsInputError, match="missing a required horizon"):
        calculate_base_strategy_statistics(
            setup_result, bad_result, development_session_count=13
        )


def test_aggregation_does_not_mutate_or_reclassify_inputs() -> None:
    item = setup_outcome(candidate("immutable"))
    setup_result, outcome_result = results((item,))
    before_setup = setup_result.model_dump()
    before_outcome = outcome_result.model_dump()
    calculate_base_strategy_statistics(
        setup_result, outcome_result, development_session_count=13
    )
    assert setup_result.model_dump() == before_setup
    assert outcome_result.model_dump() == before_outcome


def test_pure_aggregation_is_offline_and_nonpersistent(monkeypatch, tmp_path) -> None:
    def reject_network(*args, **kwargs):
        raise AssertionError("Stage 9.3 aggregation must remain offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    report_for(setup_outcome(candidate("offline")))
    assert list(tmp_path.iterdir()) == []


def test_cli_is_offline_read_only_and_warns_about_sample_size(
    monkeypatch, tmp_path, capsys
) -> None:
    result = report_for(setup_outcome(candidate("cli")))

    def mocked_calculate(self, *, start, end):
        return result

    def reject_network(*args, **kwargs):
        raise AssertionError("base-strategy-stats CLI must remain offline")

    monkeypatch.setattr(BaseStrategyStatisticsService, "calculate", mocked_calculate)
    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "base-strategy-stats",
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
    assert "sessions: 13" in captured.out
    assert "not evidence of stable expectancy" in captured.out
    assert "not realized returns" in captured.out
    assert captured.err == ""
    assert list(tmp_path.iterdir()) == []
