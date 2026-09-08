"""Synthetic-only regressions for the Rejection Entry Study V1 design freeze."""

from datetime import date, datetime, timedelta
from decimal import Decimal as D

import pytest

from spy_research.rejection_entry_v1 import (
    ConfirmationBar,
    EntryFamily,
    LevelInteraction,
    MinuteBar,
    SignalStatus,
    evaluate_interaction,
    first_executable_minute,
    immediate_close_back,
    measure_path,
    momentum_away,
    one_retest_hold,
    pair_signals,
)
from spy_research.rejection_entry_v1.data import load_after_scope_guard, validate_local_root
from spy_research.rejection_entry_v1.manifest import build_manifest, verify_manifest
from spy_research.rejection_entry_v1.population import summarize_population
from spy_research.rejection_entry_v1.protocol import (
    DISTANCES,
    OUTCOME_END,
    PROSPECTIVE_START,
    canonical_protocol,
    completion_at,
    protocol_hash,
)
from spy_research.rejection_entry_v1.reporting import canonical_json, design_record


DAY = date(2026, 1, 5)
NY = __import__("zoneinfo").ZoneInfo("America/New_York")
OPEN = datetime(2026, 1, 5, 9, 30, tzinfo=NY)
CLOSE = datetime(2026, 1, 5, 16, 0, tzinfo=NY)


def interaction(**updates):
    values = dict(
        interaction_id="i-1",
        session_date=DAY,
        level_id="level-1",
        level_family="ORH5",
        level_price=D("100"),
        approach_side="ABOVE",
        first_touch_at=OPEN,
        episode_end_at=OPEN + timedelta(minutes=30),
        touch_starts=(OPEN,),
    )
    values.update(updates)
    return LevelInteraction(**values)


def cbar(start, *, timeframe=1, close="100.10", high="100.20", low="99.90"):
    close_d = D(close)
    high_d = max(D(high), D("100.00"), close_d)
    low_d = min(D(low), D("100.00"), close_d)
    return ConfirmationBar(
        timestamp=start,
        timeframe_minutes=timeframe,
        open=D("100.00"),
        high=high_d,
        low=low_d,
        close=close_d,
        session_date=DAY,
    )


def mbar(start, *, open="100.00", high="100.20", low="99.90", close="100.10"):
    return MinuteBar(
        timestamp=start,
        open=D(open),
        high=D(high),
        low=D(low),
        close=D(close),
        session_date=DAY,
    )


def minutes(start, count, **kwargs):
    return tuple(mbar(start + timedelta(minutes=i), **kwargs) for i in range(count))


def test_protocol_is_explicit_and_decimal_only():
    assert canonical_protocol()["outcome_end"] == "2026-09-04"
    assert protocol_hash()
    assert completion_at(OPEN, 5) == OPEN + timedelta(minutes=5)
    with pytest.raises(TypeError):
        from spy_research.rejection_entry_v1.protocol import decimal
        decimal(1.25)


def test_5m_opening_confirmation_is_available_at_0935_not_0930():
    signal = immediate_close_back(
        interaction(), (cbar(OPEN, timeframe=5),), 5, session_close=CLOSE
    )
    assert signal.status is SignalStatus.CONFIRMED
    assert signal.confirmation_start_at == OPEN
    assert signal.signal_known_at == datetime(2026, 1, 5, 9, 35, tzinfo=NY)
    raw = minutes(OPEN, 20)
    at, price, status = first_executable_minute(signal, raw, session_close=CLOSE)
    assert (at, price, status) == (OPEN + timedelta(minutes=5), D("100.00"), "AVAILABLE")


def test_later_5m_confirmation_excludes_all_constituent_minutes():
    start = OPEN + timedelta(minutes=30)
    signal = immediate_close_back(
        interaction(first_touch_at=start, episode_end_at=start + timedelta(minutes=30), touch_starts=(start,)),
        (cbar(start, timeframe=5),), 5, session_close=CLOSE
    )
    raw = minutes(start, 15)
    path = measure_path(signal, raw, session_close=CLOSE, horizon_minutes=5)
    assert signal.signal_known_at == start + timedelta(minutes=5)
    assert path.entry_timestamp == start + timedelta(minutes=5)
    assert path.observed_minutes == 5
    assert path.entry_timestamp >= signal.signal_known_at


def test_immediate_close_back_requires_first_completed_bar_and_does_not_rescue_failure():
    first = cbar(OPEN, close="99.80")
    later = cbar(OPEN + timedelta(minutes=1), close="100.20")
    result = immediate_close_back(interaction(), (first, later), 1, session_close=CLOSE)
    assert result.status is SignalStatus.NO_CONFIRMATION


def test_penetration_then_close_back_confirms_on_completion():
    result = immediate_close_back(
        interaction(), (cbar(OPEN, low="99.50", high="100.30", close="100.05"),), 1, session_close=CLOSE
    )
    assert result.status is SignalStatus.CONFIRMED
    assert result.signal_known_at == OPEN + timedelta(minutes=1)


def test_unknown_approach_cannot_create_directional_confirmation():
    result = immediate_close_back(
        interaction(approach_side="UNKNOWN"), (cbar(OPEN),), 1, session_close=CLOSE
    )
    assert result.status is SignalStatus.NO_CONFIRMATION


def test_momentum_away_uses_fixed_distance_and_completed_data():
    result = momentum_away(
        interaction(), (cbar(OPEN, high="100.24"), cbar(OPEN + timedelta(minutes=1), high="100.25")),
        session_close=CLOSE, distance=D("0.25")
    )
    assert result.status is SignalStatus.CONFIRMED
    assert result.signal_known_at == OPEN + timedelta(minutes=2)
    assert result.displacement_from_level == D("0.25")


def test_one_retest_hold_requires_valid_retest_and_completed_hold():
    retest_at = OPEN + timedelta(minutes=3)
    result = one_retest_hold(
        interaction(retest_starts=(retest_at,)),
        (cbar(OPEN), cbar(retest_at, low="99.80", close="100.05")),
        session_close=CLOSE,
    )
    assert result.status is SignalStatus.CONFIRMED
    assert result.confirmation_start_at == retest_at
    assert result.signal_known_at == retest_at + timedelta(minutes=1)


def test_retest_failure_is_not_replaced_by_later_retest():
    first_retest = OPEN + timedelta(minutes=3)
    second_retest = OPEN + timedelta(minutes=6)
    result = one_retest_hold(
        interaction(retest_starts=(first_retest, second_retest)),
        (cbar(OPEN), cbar(first_retest, close="99.70"), cbar(second_retest, close="100.10")),
        session_close=CLOSE,
    )
    assert result.status is SignalStatus.NO_CONFIRMATION


def test_session_close_confirmation_is_explicitly_censored():
    start = datetime(2026, 1, 5, 15, 58, tzinfo=NY)
    result = immediate_close_back(
        interaction(first_touch_at=start, episode_end_at=CLOSE, touch_starts=(start,)),
        (cbar(start, timeframe=5),), 5, session_close=CLOSE
    )
    assert result.status is SignalStatus.CENSORED_SESSION_CLOSE


def test_first_executable_minute_is_at_or_after_signal_and_included_in_path():
    signal = immediate_close_back(interaction(), (cbar(OPEN),), 1, session_close=CLOSE)
    raw = minutes(OPEN + timedelta(minutes=1), 10)
    at, price, status = first_executable_minute(signal, raw, session_close=CLOSE)
    assert at == OPEN + timedelta(minutes=1)
    assert price == D("100.00")
    assert status == "AVAILABLE"
    path = measure_path(signal, raw, session_close=CLOSE, horizon_minutes=5)
    assert path.observed_minutes == 5


def test_same_minute_favorable_and_adverse_hits_remain_ambiguous():
    signal = immediate_close_back(interaction(), (cbar(OPEN),), 1, session_close=CLOSE)
    raw = minutes(OPEN + timedelta(minutes=1), 5, high="101.10", low="98.90")
    path = measure_path(signal, raw, session_close=CLOSE, horizon_minutes=5)
    assert path.same_minute_ambiguity
    assert any("AMBIGUOUS_SAME_MINUTE" in item[0] for item in path.fixed_distance_first_hits)


def test_unknown_approach_preserves_unavailable_directional_path_fields():
    from spy_research.rejection_entry_v1.models import EntrySignal
    signal = EntrySignal(
        interaction_id="unknown",
        session_date=DAY,
        level_id="level-1",
        level_family="ORH5",
        level_price=D("100"),
        approach_side="UNKNOWN",
        entry_family=EntryFamily.IMMEDIATE_CLOSE_BACK,
        status=SignalStatus.CONFIRMED,
        first_touch_at=OPEN,
        confirmation_start_at=OPEN,
        signal_known_at=OPEN + timedelta(minutes=1),
        confirmation_timeframe_minutes=1,
    )
    path = measure_path(signal, minutes(OPEN + timedelta(minutes=1), 5), session_close=CLOSE, horizon_minutes=5)
    assert path.mfe_from_level is None and path.mae_through_level is None
    assert all(item[0].endswith(":UNKNOWN") for item in path.fixed_distance_first_hits)


def test_fixed_distance_first_hit_preserves_adverse_before_favorable_order():
    signal = immediate_close_back(interaction(), (cbar(OPEN),), 1, session_close=CLOSE)
    raw = (
        mbar(OPEN + timedelta(minutes=1), high="100.10", low="99.70", close="99.90"),
        mbar(OPEN + timedelta(minutes=2), high="100.60", low="99.90", close="100.20"),
        *minutes(OPEN + timedelta(minutes=3), 3),
    )
    path = measure_path(signal, raw, session_close=CLOSE, horizon_minutes=5)
    assert path.fixed_distance_first_hits[0][0].endswith(":ADVERSE")


def test_every_interaction_gets_all_families_and_pairing_is_identity_based():
    rows = evaluate_interaction(interaction(), (cbar(OPEN),), session_close=CLOSE)
    assert {row.entry_family for row in rows} == set(EntryFamily)
    paired = pair_signals(rows, EntryFamily.IMMEDIATE_CLOSE_BACK, EntryFamily.MOMENTUM_AWAY, left_timeframe_minutes=1)
    assert len(paired) == 1 and paired[0].interaction_id == "i-1"


def test_population_denominator_retains_unconfirmed_interactions():
    i2 = interaction(interaction_id="i-2", first_touch_at=OPEN + timedelta(minutes=40), episode_end_at=OPEN + timedelta(minutes=70), touch_starts=(OPEN + timedelta(minutes=40),))
    rows = evaluate_interaction(interaction(), (cbar(OPEN),), session_close=CLOSE)
    rows += evaluate_interaction(i2, (), session_close=CLOSE)
    summary = summarize_population((interaction(), i2), rows)
    assert summary.interactions == 2 and summary.sessions == 1
    assert sum(count for _, _, count in summary.statuses_by_family) == 8


def test_post_outcome_and_prospective_dates_fail_before_reader_call():
    calls = []
    def reader(*args):
        calls.append(args)
        return ()
    with pytest.raises(ValueError):
        load_after_scope_guard(reader, context_start=date(2025, 12, 1), outcome_start=DAY, outcome_end=PROSPECTIVE_START)
    assert calls == []
    assert OUTCOME_END == date(2026, 9, 4)


def test_context_warmup_bar_before_outcome_window_is_allowed_but_future_is_not():
    warmup = MinuteBar(
        timestamp=datetime(2025, 12, 31, 9, 30, tzinfo=NY),
        open=D("100"), high=D("101"), low=D("99"), close=D("100"),
        session_date=date(2025, 12, 31),
    )
    assert warmup.session_date < DAY
    with pytest.raises(ValueError):
        MinuteBar(
            timestamp=datetime(2026, 9, 8, 9, 30, tzinfo=NY),
            open=D("100"), high=D("101"), low=D("99"), close=D("100"),
            session_date=PROSPECTIVE_START,
        )


def test_local_root_rejects_network_url():
    with pytest.raises(ValueError):
        validate_local_root("https://example.invalid/data")


def test_design_manifest_cannot_claim_outcome_run():
    manifest = build_manifest(
        klr_protocol_hash="d39d4a67b22b7c2d775a7f7fbdece6dee1ca513ecf358e89c5d52140a0588592",
        source_files=("protocol.py",),
    )
    assert not manifest.outcome_run_performed
    assert canonical_json(design_record()).find("outcome_run_performed") >= 0


def test_checked_in_design_manifest_fingerprints_only_new_package():
    payload = verify_manifest(
        __import__("pathlib").Path("reports/rejection_entry_study_v1/freeze_manifest.json"),
        repository_root=__import__("pathlib").Path("."),
    )
    assert payload["outcome_run_performed"] is False
