from __future__ import annotations

import socket
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

import spy_research.cli as cli_module
from spy_research.interactions import LevelType
from spy_research.strategy import (
    CandidateContextRecord,
    CandidateMembership,
    ControlledVariantSelectionService,
    FrozenStabilityHorizon,
    FrozenStabilityRecord,
    FrozenState,
    SetupDirection,
    StrategyVariant,
    VariantSelectionLabel,
    bootstrap_session_uncertainty,
    calculate_controlled_variant_selection,
    candidate_variants,
    evaluate_advancement_criteria,
    select_candidate_memberships,
    select_variant_label,
)
from spy_research.strategy.comparisons import (
    Ema20VwapAlignmentState,
    StructureAgreementState,
)
from spy_research.strategy.comparisons.models import (
    Ema9VwapAlignmentState,
    EmaAlignmentState,
    VwapAlignmentState,
)
from spy_research.strategy.stability import HORIZONS, MAJOR_DIMENSIONS


NY = ZoneInfo("America/New_York")
START = date(2026, 1, 2)
END = date(2026, 8, 19)
DEV_START = date(2026, 8, 3)


def context(
    identity: str = "setup",
    session: date = START,
    *,
    direction: SetupDirection = SetupDirection.LONG,
    ema: EmaAlignmentState = EmaAlignmentState.EMA_ALIGNED,
    price_vwap: VwapAlignmentState = VwapAlignmentState.VWAP_ALIGNED,
    ema9_vwap: Ema9VwapAlignmentState = Ema9VwapAlignmentState.EMA9_VWAP_ALIGNED,
    ema20_vwap: Ema20VwapAlignmentState = Ema20VwapAlignmentState.EMA20_VWAP_ALIGNED,
    structure: StructureAgreementState = StructureAgreementState.ALIGNED,
    room: Decimal | None = Decimal("1.0"),
) -> CandidateContextRecord:
    return CandidateContextRecord(
        setup_identity=identity,
        session_date=session,
        signal_known_at=datetime(session.year, session.month, session.day, 10, tzinfo=NY),
        direction=direction,
        level_type=LevelType.PDH,
        ema9_20_alignment=ema,
        price_vwap_alignment=price_vwap,
        ema9_vwap_alignment=ema9_vwap,
        ema20_vwap_alignment=ema20_vwap,
        structure_agreement=structure,
        room_in_atr=room,
    )


def record(
    identity: str,
    session: date,
    *,
    direction: SetupDirection = SetupDirection.LONG,
    executable: bool = True,
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
            FrozenState(dimension=dimension, state="FROZEN")
            for dimension in MAJOR_DIMENSIONS
        ),
        horizons=(
            tuple(
                FrozenStabilityHorizon(
                    horizon=horizon,
                    complete=True,
                    mfe=Decimal(mfe),
                    mae=Decimal(mae),
                )
                for horizon in HORIZONS
            )
            if executable
            else ()
        ),
    )


def synthetic_sources():
    expanded_contexts = []
    expanded_records = []
    for month in range(1, 9):
        for index in range(5):
            session = date(2026, month, index + 2)
            identity = f"expanded-{month}-{index}"
            expanded_contexts.append(context(identity, session))
            expanded_records.append(record(identity, session))
    development_contexts = []
    development_records = []
    for index in range(5):
        session = date(2026, 8, index + 3)
        identity = f"development-{index}"
        development_contexts.append(context(identity, session))
        development_records.append(record(identity, session))
    return (
        tuple(expanded_contexts),
        tuple(development_contexts),
        tuple(expanded_records),
        tuple(development_records),
    )


def calculate(*, resamples: int = 20):
    expanded_contexts, development_contexts, expanded_records, development_records = (
        synthetic_sources()
    )
    return calculate_controlled_variant_selection(
        expanded_contexts,
        development_contexts,
        expanded_records,
        development_records,
        start=START,
        end=END,
        bootstrap_resamples=resamples,
    )


def evaluation(report, variant: StrategyVariant):
    return next(item for item in report.evaluations if item.variant is variant)


def test_exactly_ten_closed_variants_exist() -> None:
    assert tuple(item.value for item in StrategyVariant) == (
        "BASE_ALL",
        "BASE_LONG",
        "BASE_SHORT",
        "EMA_STACK_ALIGNED",
        "STRUCTURE_ALIGNED",
        "ROOM_GE_1_ATR",
        "EMA_STACK_AND_STRUCTURE",
        "EMA_STACK_AND_ROOM_GE_1_ATR",
        "STRUCTURE_AND_ROOM_GE_1_ATR",
        "FULL_CONFLUENCE",
    )
    with pytest.raises(ValueError):
        StrategyVariant("UNDECLARED")
    with pytest.raises(ValidationError):
        CandidateMembership(setup_identity="x", variants=("UNDECLARED",))


def test_exact_membership_and_combined_requirements() -> None:
    assert candidate_variants(context()) == tuple(StrategyVariant(item) for item in (
        "BASE_ALL",
        "BASE_LONG",
        "EMA_STACK_ALIGNED",
        "STRUCTURE_ALIGNED",
        "ROOM_GE_1_ATR",
        "EMA_STACK_AND_STRUCTURE",
        "EMA_STACK_AND_ROOM_GE_1_ATR",
        "STRUCTURE_AND_ROOM_GE_1_ATR",
        "FULL_CONFLUENCE",
    ))
    no_structure = candidate_variants(
        context(structure=StructureAgreementState.NOT_ALIGNED)
    )
    assert StrategyVariant.EMA_STACK_ALIGNED in no_structure
    assert StrategyVariant.EMA_STACK_AND_STRUCTURE not in no_structure
    assert StrategyVariant.STRUCTURE_AND_ROOM_GE_1_ATR not in no_structure
    assert StrategyVariant.FULL_CONFLUENCE not in no_structure


@pytest.mark.parametrize(
    "field,value",
    (
        ("ema9_20_alignment", EmaAlignmentState.EMA_UNAVAILABLE),
        ("price_vwap_alignment", VwapAlignmentState.VWAP_UNAVAILABLE),
        ("ema9_vwap_alignment", Ema9VwapAlignmentState.EMA9_VWAP_UNAVAILABLE),
        ("ema20_vwap_alignment", Ema20VwapAlignmentState.EMA20_VWAP_UNAVAILABLE),
    ),
)
def test_ema_stack_requires_all_four_exact_available_alignments(field, value) -> None:
    candidate = context().model_copy(update={field: value})
    variants = candidate_variants(candidate)
    assert StrategyVariant.EMA_STACK_ALIGNED not in variants
    assert StrategyVariant.FULL_CONFLUENCE not in variants


@pytest.mark.parametrize(
    "room,qualifies",
    ((Decimal("1.0"), True), (Decimal("0.9999"), False), (None, False)),
)
def test_finite_room_boundary_and_open_ended_unavailable(room, qualifies) -> None:
    variants = candidate_variants(context(room=room))
    assert (StrategyVariant.ROOM_GE_1_ATR in variants) is qualifies
    assert (StrategyVariant.FULL_CONFLUENCE in variants) is qualifies


def test_membership_is_deterministic_and_outcome_independent() -> None:
    contexts = (context("b", date(2026, 1, 3)), context("a", date(2026, 1, 2)))
    first = select_candidate_memberships(contexts)
    second = select_candidate_memberships(tuple(reversed(contexts)))
    assert first == second
    before = first
    changed_future_outcome = record("a", date(2026, 1, 2), mfe="999", mae="0")
    assert changed_future_outcome.horizons[-1].mfe == Decimal("999")
    assert select_candidate_memberships(contexts) == before


def test_base_all_reproduces_frozen_outcomes_and_months_are_isolated() -> None:
    report = calculate()
    base = evaluation(report, StrategyVariant.BASE_ALL)
    assert base.expanded.setup_n == base.expanded.executable_n == 40
    assert base.expanded.session_count == 40
    assert tuple(item.executable_n for item in base.monthly) == (5,) * 8
    assert base.expanded.horizons[-1].mfe.median == Decimal("2")
    assert base.expanded.horizons[-1].mae.median == Decimal("1")
    assert base.expanded.horizons[-1].net_excursion_balance.median == Decimal("1")
    assert base.selection_label is VariantSelectionLabel.RETAIN_AS_CONTROL
    assert evaluation(report, StrategyVariant.BASE_SHORT).selection_label is (
        VariantSelectionLabel.INSUFFICIENT_COVERAGE
    )


def test_development_snapshot_uses_isolated_memberships() -> None:
    expanded_contexts, development_contexts, expanded_records, development_records = (
        synthetic_sources()
    )
    expanded_contexts = tuple(
        item.model_copy(
            update={
                "structure_agreement": StructureAgreementState.NOT_ALIGNED,
            }
        )
        if item.session_date.month == 8
        else item
        for item in expanded_contexts
    )
    report = calculate_controlled_variant_selection(
        expanded_contexts,
        development_contexts,
        expanded_records,
        development_records,
        start=START,
        end=END,
        bootstrap_resamples=10,
    )
    full = evaluation(report, StrategyVariant.FULL_CONFLUENCE)
    assert full.monthly[-1].setup_n == 5
    assert full.development.setup_n == 5
    assert full.expanded.setup_n == 35


def passing_criteria(**overrides):
    values = dict(
        expanded_balance=Decimal("0.01"),
        pre_development_balance=Decimal("0.01"),
        development_balance=Decimal("0.01"),
        positive_months=5,
        leave_one_month_out_balances=(Decimal("0"),) * 8,
        largest_session_percentage=Decimal("10"),
        bootstrap_balance_median=Decimal("0.01"),
    )
    values.update(overrides)
    return evaluate_advancement_criteria(**values)


@pytest.mark.parametrize(
    "override,failed_index",
    (
        ({"expanded_balance": Decimal("0")}, 0),
        ({"pre_development_balance": Decimal("0")}, 1),
        ({"development_balance": Decimal("0")}, 2),
        ({"positive_months": 4}, 3),
        ({"leave_one_month_out_balances": (Decimal("-0.01"),) + (Decimal("0"),) * 7}, 4),
        ({"largest_session_percentage": Decimal("10.0001")}, 5),
        ({"bootstrap_balance_median": Decimal("0")}, 6),
    ),
)
def test_every_advancement_criterion_boundary(override, failed_index) -> None:
    criteria = passing_criteria(**override)
    assert len(criteria) == 7
    assert not criteria[failed_index].passed
    assert sum(not item.passed for item in criteria) == 1


def test_advancement_label_boundaries_and_control_override() -> None:
    passed = passing_criteria()
    assert all(item.passed for item in passed)
    label, _ = select_variant_label(
        StrategyVariant.FULL_CONFLUENCE,
        scorecard_eligible=True,
        criteria=passed,
        executable_n=30,
        executable_session_count=20,
    )
    assert label is VariantSelectionLabel.ADVANCE_TO_STAGE_13
    label, _ = select_variant_label(
        StrategyVariant.FULL_CONFLUENCE,
        scorecard_eligible=False,
        criteria=(),
        executable_n=29,
        executable_session_count=20,
    )
    assert label is VariantSelectionLabel.INSUFFICIENT_COVERAGE
    label, _ = select_variant_label(
        StrategyVariant.BASE_ALL,
        scorecard_eligible=True,
        criteria=passed,
        executable_n=100,
        executable_session_count=50,
    )
    assert label is VariantSelectionLabel.RETAIN_AS_CONTROL


def test_leave_one_out_and_bootstrap_are_deterministic() -> None:
    first = calculate(resamples=40)
    second = calculate(resamples=40)
    first_full = evaluation(first, StrategyVariant.FULL_CONFLUENCE)
    second_full = evaluation(second, StrategyVariant.FULL_CONFLUENCE)
    assert first_full.leave_one_month_out == second_full.leave_one_month_out
    assert first_full.bootstrap_uncertainty == second_full.bootstrap_uncertainty


def test_control_and_direction_bootstraps_reuse_stage12_2_identities() -> None:
    report = calculate(resamples=40)
    _, _, expanded_records, _ = synthetic_sources()
    expected_identities = (
        (StrategyVariant.BASE_ALL, "BASE_ALL", "ALL", expanded_records),
        (
            StrategyVariant.BASE_LONG,
            "DIRECTION",
            "LONG",
            tuple(item for item in expanded_records if item.direction is SetupDirection.LONG),
        ),
    )
    for variant, dimension, state, selected in expected_identities:
        expected = bootstrap_session_uncertainty(
            dimension,
            state,
            selected,
            seed=12022026,
            resamples=40,
        )
        assert evaluation(report, variant).bootstrap_uncertainty == expected


def test_inputs_are_immutable() -> None:
    item = context()
    with pytest.raises(ValidationError):
        item.room_in_atr = Decimal("2")


def test_cli_is_offline_nonpersistent(monkeypatch, tmp_path, capsys) -> None:
    sentinel = object()

    def reject_network(*args, **kwargs):
        raise AssertionError("Stage 12.3 must remain offline")

    def mocked_calculate(self, *, start, end):
        assert start == START and end == END
        return sentinel

    def mocked_print(result):
        assert result is sentinel
        print("stage12.3-pass")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    monkeypatch.setattr(ControlledVariantSelectionService, "calculate", mocked_calculate)
    monkeypatch.setattr(cli_module, "_print_controlled_variant_selection", mocked_print)
    exit_code = cli_module.main(
        [
            "select-stage13-variants",
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
    assert captured.out == "stage12.3-pass\n"
    assert captured.err == ""
    assert list(tmp_path.iterdir()) == []
