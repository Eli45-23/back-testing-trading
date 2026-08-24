from __future__ import annotations

import inspect
import socket
from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

import spy_research.cli as cli_module
from spy_research.interactions import LevelType
from spy_research.strategy import (
    ExpandedStabilityService,
    FrozenStabilityHorizon,
    FrozenStabilityRecord,
    FrozenState,
    SampleSizeLabel,
    SetupDirection,
    ValidationPartition,
    calculate_expanded_stability,
    stability_report_hash,
)
from spy_research.strategy.stability import HORIZONS, MAJOR_DIMENSIONS


START = date(2026, 1, 2)
END = date(2026, 8, 19)
DEV_START = date(2026, 8, 3)
DEV_END = date(2026, 8, 19)


def record(
    identity: str,
    session: date,
    *,
    direction: SetupDirection = SetupDirection.LONG,
    state: str = "STATE_A",
    executable: bool = True,
    incomplete_eod: bool = False,
    mfe: str = "2",
    mae: str = "1",
) -> FrozenStabilityRecord:
    return FrozenStabilityRecord(
        setup_identity=identity,
        session_date=session,
        direction=direction,
        level_type=LevelType.PDH,
        executable=executable,
        states=tuple(
            FrozenState(dimension=dimension, state=state)
            for dimension in MAJOR_DIMENSIONS
        ),
        horizons=(
            tuple(
                FrozenStabilityHorizon(
                    horizon=horizon,
                    complete=not (incomplete_eod and horizon == "EOD"),
                    mfe=Decimal(mfe),
                    mae=Decimal(mae),
                )
                for horizon in HORIZONS
            )
            if executable
            else ()
        ),
    )


def ordered(*items: FrozenStabilityRecord):
    return tuple(sorted(items, key=lambda item: (item.session_date, item.setup_identity)))


def calculate(expanded, development, *, resamples=20):
    return calculate_expanded_stability(
        ordered(*expanded),
        ordered(*development),
        start=START,
        end=END,
        development_start=DEV_START,
        development_end=DEV_END,
        bootstrap_resamples=resamples,
    )


def row(report, partition, dimension="BASE_ALL", state="ALL"):
    return next(
        item
        for item in report.partition_statistics
        if item.partition is partition
        and item.dimension == dimension
        and item.state == state
    )


def test_exact_decimal_base_statistics_and_incomplete_semantics() -> None:
    expanded = (
        record("jan-a", date(2026, 1, 2), mfe="3", mae="1"),
        record(
            "jan-b",
            date(2026, 1, 5),
            direction=SetupDirection.SHORT,
            incomplete_eod=True,
            mfe="9",
            mae="4",
        ),
        record("jan-c", date(2026, 1, 6), executable=False),
    )
    development = (record("dev", DEV_START),)
    report = calculate(expanded, development)
    base = row(report, ValidationPartition.EXPANDED_ALL)
    five, eod = base.horizons[0], base.horizons[-1]
    assert base.setup_n == 3
    assert base.executable_n == 2
    assert five.complete_n == 2 and five.incomplete_n == 0
    assert five.mfe.mean == Decimal("6")
    assert eod.complete_n == 1 and eod.incomplete_n == 1
    assert eod.mfe.mean == eod.mfe.median == Decimal("3")
    assert eod.balance.mean == eod.balance.median == Decimal("2")
    assert eod.favorable_adverse.mfe_greater == 1


def test_partitions_are_chronological_and_months_do_not_leak() -> None:
    expanded = (
        record("jan", date(2026, 1, 2), state="JAN"),
        record("jul", date(2026, 7, 31), state="JUL"),
        record("expanded-aug", DEV_START, state="EXPANDED_AUG"),
    )
    development = (record("isolated-aug", DEV_START, state="DEV_AUG"),)
    report = calculate(expanded, development)
    pre = row(report, ValidationPartition.PRE_DEVELOPMENT_OUT_OF_SAMPLE)
    january = row(report, ValidationPartition.MONTH_2026_01)
    august = row(report, ValidationPartition.MONTH_2026_08)
    assert pre.setup_n == 2
    assert january.setup_n == 1
    assert august.setup_n == 1
    assert row(
        report,
        ValidationPartition.MONTH_2026_08,
        "EMA9_20_ALIGNMENT",
        "DEV_AUG",
    ).setup_n == 1
    assert row(
        report,
        ValidationPartition.MONTH_2026_08,
        "EMA9_20_ALIGNMENT",
        "EXPANDED_AUG",
    ).setup_n == 0


def test_adding_later_sessions_cannot_change_earlier_month_statistics() -> None:
    development = (record("dev", DEV_START),)
    january = (record("jan", date(2026, 1, 2), mfe="3", mae="1"),)
    before = calculate(january, development)
    after = calculate(
        january + (record("later", date(2026, 7, 31), mfe="99", mae="0"),),
        development,
    )
    assert row(before, ValidationPartition.MONTH_2026_01) == row(
        after, ValidationPartition.MONTH_2026_01
    )


def test_bootstrap_is_session_clustered_and_deterministic() -> None:
    expanded = tuple(
        record(
            f"{session}-{index}",
            date(2026, 1 + session % 7, 1 + session),
            mfe=str(session + 1),
            mae=str(index % 2),
        )
        for session in range(1, 21)
        for index in range(5)
    )
    development = (record("dev", DEV_START),)
    first = calculate(expanded, development, resamples=50)
    second = calculate(expanded, development, resamples=50)
    assert first.bootstrap_uncertainty == second.bootstrap_uncertainty
    base = next(
        item
        for item in first.bootstrap_uncertainty
        if item.dimension == "BASE_ALL"
    )
    assert base.session_count == 20
    assert base.executable_n == 100
    assert base.resamples == 50
    assert len(base.intervals) == 3


def test_direction_controlled_populations_reconcile_to_direction_bases() -> None:
    expanded = (
        record("long-a", date(2026, 1, 2)),
        record("long-b", date(2026, 1, 5), executable=False),
        record("short-a", date(2026, 1, 6), direction=SetupDirection.SHORT),
    )
    report = calculate(expanded, (record("dev", DEV_START),))
    bases = {
        item.direction_scope: item
        for item in report.direction_controlled
        if item.dimension == "DIRECTION_BASE"
    }
    assert bases[SetupDirection.LONG].setup_n == 2
    assert bases[SetupDirection.LONG].executable_n == 1
    assert bases[SetupDirection.SHORT].setup_n == 1
    assert bases[SetupDirection.SHORT].executable_n == 1
    for direction, base in bases.items():
        states = tuple(
            item
            for item in report.direction_controlled
            if item.direction_scope is direction
            and item.dimension == "EMA9_20_ALIGNMENT"
        )
        assert sum(item.setup_n for item in states) == base.setup_n


def test_session_concentration_uses_present_sessions_only() -> None:
    expanded = tuple(
        record(f"jan-2-{index}", date(2026, 1, 2)) for index in range(3)
    ) + (record("jan-5", date(2026, 1, 5)),)
    report = calculate(expanded, (record("dev", DEV_START),))
    concentration = next(
        item
        for item in report.session_concentration
        if item.dimension == "REGIME" and item.state == "STATE_A"
    )
    assert concentration.setup_n == 4
    assert concentration.distinct_sessions == 2
    assert concentration.median_setups_per_present_session == Decimal("2")
    assert concentration.maximum_single_session_n == 3
    assert concentration.largest_session_percentage == Decimal("75")
    assert concentration.largest_five_sessions_percentage == Decimal("100")


def test_leave_one_month_out_reports_all_calendar_exclusions() -> None:
    expanded = tuple(
        record(
            f"{month}-{index}",
            date(2026, month, min(index + 1, 20)),
            mfe=str(month + 1),
            mae="1",
        )
        for month in range(1, 9)
        for index in range(13)
    )
    report = calculate(expanded, (record("dev", DEV_START),))
    base = next(
        item
        for item in report.leave_one_month_out
        if item.dimension == "BASE_ALL" and item.state == "ALL"
    )
    assert base.executable_n == 104
    assert tuple(month for month, _ in base.exclusions) == tuple(
        f"2026-{month:02d}" for month in range(1, 9)
    )
    assert base.minimum_exclusion_median_balance is not None
    assert base.maximum_exclusion_median_balance is not None


def test_empty_level_controlled_groups_remain_visible_and_labeled() -> None:
    report = calculate(
        (record("jan", date(2026, 1, 2)),),
        (record("dev", DEV_START),),
    )
    empty = next(
        item
        for item in report.level_controlled
        if item.level_scope is LevelType.PDL
        and item.dimension == "EMA9_20_ALIGNMENT"
        and item.state == "STATE_A"
    )
    assert empty.setup_n == empty.executable_n == empty.session_count == 0
    assert empty.sample_size is SampleSizeLabel.VERY_SMALL
    assert all(item.complete_n == item.incomplete_n == 0 for item in empty.horizons)


def test_calculation_does_not_mutate_frozen_source_records() -> None:
    expanded = ordered(record("jan", date(2026, 1, 2)))
    development = ordered(record("dev", DEV_START))
    before = (expanded[0].model_dump_json(), development[0].model_dump_json())
    calculate(expanded, development)
    assert (expanded[0].model_dump_json(), development[0].model_dump_json()) == before
    with pytest.raises(ValidationError):
        expanded[0].setup_identity = "mutated"


@pytest.mark.parametrize(
    "n,label",
    (
        (0, SampleSizeLabel.VERY_SMALL),
        (9, SampleSizeLabel.VERY_SMALL),
        (10, SampleSizeLabel.SMALL),
        (29, SampleSizeLabel.SMALL),
        (30, SampleSizeLabel.MODERATE),
        (99, SampleSizeLabel.MODERATE),
        (100, SampleSizeLabel.LARGE),
    ),
)
def test_frozen_sample_size_disclosure(n, label) -> None:
    expanded = tuple(
        record(f"row-{index}", date(2026, 1, 2)) for index in range(n)
    )
    report = calculate(expanded, (record("dev", DEV_START),))
    assert row(report, ValidationPartition.EXPANDED_ALL).sample_size is label


def test_report_hash_is_deterministic_and_analysis_accepts_no_bars() -> None:
    report = calculate(
        (record("jan", date(2026, 1, 2)),),
        (record("dev", DEV_START),),
    )
    assert stability_report_hash(report) == stability_report_hash(report)
    parameters = inspect.signature(calculate_expanded_stability).parameters
    assert "bars" not in parameters
    assert "future_bars" not in parameters


def test_cli_is_offline_and_nonpersistent(monkeypatch, tmp_path, capsys) -> None:
    sentinel = object()

    def reject_network(*args, **kwargs):
        raise AssertionError("Stage 12.2 must remain offline")

    def mocked_calculate(self, *, start, end):
        assert start == START and end == END
        return sentinel

    def mocked_print(result):
        assert result is sentinel
        print("expanded-stability-pass")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    monkeypatch.setattr(ExpandedStabilityService, "calculate", mocked_calculate)
    monkeypatch.setattr(cli_module, "_print_expanded_stability", mocked_print)
    exit_code = cli_module.main(
        [
            "validate-expanded-stability",
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
    assert captured.out == "expanded-stability-pass\n"
    assert captured.err == ""
    assert list(tmp_path.iterdir()) == []
