"""Synthetic regressions for the frozen prospective rejection-validation design."""

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from spy_research.rejection_prospective_v1.guards import (
    assert_outcome_access_is_enabled,
    build_session_plan,
    evaluate_readiness,
    validate_market_path,
    validate_outcome_date,
)
from spy_research.rejection_prospective_v1.models import CandidateSpec, ProspectiveSession
from spy_research.rejection_prospective_v1.protocol import (
    ATR_CANDIDATE,
    CANDIDATES,
    CONTROL,
    MODELS,
    PROSPECTIVE_START,
    SESSION_COUNT,
    protocol_hash,
    validate_decimal,
)


@pytest.fixture(scope="module")
def plan():
    return build_session_plan()


def test_matrix_is_exactly_four_models_and_one_entry():
    assert CANDIDATES == ("USD040_TARGET_2R_BE1R", "USD040_TARGET_1.5R", "ATR050_TARGET_1R")
    assert CONTROL == "USD040_TARGET_2R"
    assert MODELS == (*CANDIDATES, CONTROL)
    assert len(MODELS) == 4


def test_session_plan_is_fixed_60_and_starts_after_development(plan):
    assert len(plan) == SESSION_COUNT == 60
    assert plan[0].session_date == date(2026, 9, 8)
    assert plan[-1].session_date > date(2026, 9, 4)
    assert [x.session_date for x in plan] == sorted(x.session_date for x in plan)


def test_session_plan_is_not_extendable(plan):
    with pytest.raises(ValueError):
        build_session_plan(count=61)
    with pytest.raises(ValueError):
        build_session_plan(start=date(2026, 9, 9))


def test_session_boundaries_are_causal_and_immutable(plan):
    first = plan[0]
    assert first.market_open < first.market_close
    with pytest.raises(ValidationError):
        first.session_date = date(2026, 9, 9)


def test_only_planned_dates_are_valid_outcomes(plan):
    validate_outcome_date(plan[0].session_date, plan)
    validate_outcome_date(plan[-1].session_date, plan)
    for day in (date(2026, 9, 4), date(2026, 12, 2), date(2027, 1, 4)):
        with pytest.raises(ValueError):
            validate_outcome_date(day, plan)


def test_path_guard_rejects_development_and_unplanned_partitions(plan):
    with pytest.raises(ValueError):
        validate_market_path("data/2026-09-07.parquet", plan[0])
    with pytest.raises(ValueError):
        validate_market_path("data/2026-12-02.parquet", plan[-1])
    assert validate_market_path("data/2026-09-08.parquet", plan[0]).name == "2026-09-08.parquet"


def test_fixed_candidate_specs_match_frozen_roles():
    assert CandidateSpec(name="USD040_TARGET_2R_BE1R", role="PRIMARY", stop_family="USD040", exit_family="TARGET_2R_BE1R")
    assert CandidateSpec(name="USD040_TARGET_1.5R", role="SECONDARY", stop_family="USD040", exit_family="TARGET_1.5R")
    assert CandidateSpec(name=ATR_CANDIDATE, role="EXPLORATORY_ATR", stop_family="ATR050", exit_family="TARGET_1R", atr_natural_population=True)
    assert CandidateSpec(name=CONTROL, role="CONTROL", stop_family="USD040", exit_family="TARGET_2R")


def test_candidate_spec_cannot_be_renamed_or_redefined():
    with pytest.raises(ValueError):
        CandidateSpec(name="USD040_TARGET_2R", role="PRIMARY", stop_family="USD040", exit_family="TARGET_2R")
    with pytest.raises(ValueError):
        CandidateSpec(name=ATR_CANDIDATE, role="EXPLORATORY_ATR", stop_family="USD040", exit_family="TARGET_1R")


def _endpoint_inputs(plan, *, complete=True, validated=None, counts=None, contrib=None, as_of=None):
    validated = [x.session_date for x in plan] if validated is None else validated
    counts = {model: 200 for model in MODELS} if counts is None else counts
    contrib = {model: 40 for model in MODELS} if contrib is None else contrib
    complete_data = {x.session_date: complete for x in plan}
    as_of = plan[-1].market_close + timedelta(seconds=1) if as_of is None else as_of
    return evaluate_readiness(as_of=as_of, sessions=plan, validated_sessions=validated,
                              complete_data=complete_data, executable_outcomes=counts,
                              contributing_sessions=contrib)


def test_interim_status_before_sixty_sessions(plan):
    result = _endpoint_inputs(plan, validated=[], as_of=plan[0].market_close + timedelta(seconds=1))
    assert result.status == "INTERIM_NO_SELECTION"
    assert result.completed_sessions < 60


def test_incomplete_data_blocks_endpoint_without_replacement(plan):
    result = _endpoint_inputs(plan, complete=False)
    assert result.status == "BLOCKED_DATA_QUALITY"
    assert len(result.missing_or_invalid_sessions) == 60


def test_missing_validated_session_blocks_endpoint(plan):
    result = _endpoint_inputs(plan, validated=[x.session_date for x in plan[:-1]])
    assert result.status == "BLOCKED_DATA_QUALITY"


def test_future_validated_session_cannot_be_reported_early(plan):
    with pytest.raises(ValueError):
        _endpoint_inputs(plan, validated=[plan[1].session_date], as_of=plan[0].market_close + timedelta(seconds=1))


def test_fixed_sample_gates_and_atr_insufficiency_are_nonselecting(plan):
    counts = {model: 200 for model in MODELS}
    counts[ATR_CANDIDATE] = 199
    result = _endpoint_inputs(plan, counts=counts)
    assert result.status == "ENDPOINT_REACHED_NO_SELECTION"
    assert result.candidate_assessments[ATR_CANDIDATE] == "INSUFFICIENT_PROSPECTIVE_DATA"
    assert result.candidate_assessments[CONTROL] == "ENDPOINT_REPORT_ELIGIBLE"


def test_below_contributing_session_gate_is_insufficient(plan):
    contrib = {model: 40 for model in MODELS}
    contrib["USD040_TARGET_2R_BE1R"] = 39
    result = _endpoint_inputs(plan, contrib=contrib)
    assert result.candidate_assessments["USD040_TARGET_2R_BE1R"] == "INSUFFICIENT_PROSPECTIVE_DATA"


def test_zero_signal_sessions_do_not_block_valid_endpoint(plan):
    result = _endpoint_inputs(plan)
    assert result.validated_sessions == SESSION_COUNT
    assert result.status == "ENDPOINT_REACHED_NO_SELECTION"


def test_counts_required_for_every_frozen_model(plan):
    counts = {model: 200 for model in MODELS}
    counts.pop(CONTROL)
    with pytest.raises(ValueError):
        _endpoint_inputs(plan, counts=counts)


def test_negative_or_invalid_counts_fail_closed(plan):
    counts = {model: 200 for model in MODELS}
    counts[CONTROL] = -1
    with pytest.raises(ValueError):
        _endpoint_inputs(plan, counts=counts)


def test_duplicate_or_outside_validated_sessions_fail_closed(plan):
    dates = [x.session_date for x in plan[:-1]] + [plan[-2].session_date]
    with pytest.raises(ValueError):
        _endpoint_inputs(plan, validated=dates)
    with pytest.raises(ValueError):
        _endpoint_inputs(plan, validated=[date(2026, 12, 2)])


def test_naive_endpoint_is_rejected(plan):
    with pytest.raises(ValueError):
        _endpoint_inputs(plan, as_of=datetime(2026, 12, 1))


def test_protocol_has_fixed_costs_bootstrap_and_bonferroni():
    from spy_research.rejection_prospective_v1.protocol import canonical_protocol

    payload = canonical_protocol()
    assert payload["costs"] == ["0", "0.01", "0.02"]
    assert payload["bootstrap"] == {
        "unit": "whole_session", "draws": 10000, "seed": 20260908,
        "paired_candidate_control": True, "bonferroni_comparisons": 3,
        "bonferroni_alpha": "0.016666666666666666666666666666666666666666666666666666666666666666666666666666667",
    }
    assert payload["historical_outcomes_enabled_in_design"] is False


def test_exact_decimal_policy_rejects_binary_float():
    assert validate_decimal("0.40") == Decimal("0.40")
    with pytest.raises(TypeError):
        validate_decimal(0.4)


def test_protocol_hash_is_stable_and_nonempty():
    assert len(protocol_hash()) == 64
    assert protocol_hash() == protocol_hash()


def test_session_model_rejects_unplanned_dates_and_bad_boundaries():
    with pytest.raises(ValueError):
        ProspectiveSession(session_date=date(2026, 9, 7), market_open=datetime(2026, 9, 7, 13, 30, tzinfo=UTC), market_close=datetime(2026, 9, 7, 20, tzinfo=UTC))
    with pytest.raises(ValueError):
        ProspectiveSession(session_date=date(2026, 9, 8), market_open=datetime(2026, 9, 8, 13, 30), market_close=datetime(2026, 9, 8, 20, tzinfo=UTC))


def test_endpoint_status_never_selects_or_extends(plan):
    result = _endpoint_inputs(plan)
    assert result.status == "ENDPOINT_REACHED_NO_SELECTION"
    assert "best" not in result.model_dump_json().lower()


def test_design_phase_outcome_generation_is_disabled():
    with pytest.raises(PermissionError):
        assert_outcome_access_is_enabled(False)
    assert assert_outcome_access_is_enabled(True) is None
