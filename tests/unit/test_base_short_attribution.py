from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from spy_research.attribution import analysis
from spy_research.attribution.analysis import ALLOWED_INTERACTIONS, analyze_base_short_attribution
from spy_research.attribution.models import AttributionObservation
from spy_research.attribution.reporting import render_attribution_markdown
from spy_research.attribution.service import (
    FIXED_FACTOR_STATES,
    _atr_regime,
    _candle_quality,
    _gap_context,
    _room_dollars,
    _time_bucket,
)
from spy_research.bars.models import FiveMinuteBar


NY = ZoneInfo("America/New_York")
HASH = "0" * 64


def _factors(**updates: str) -> tuple[tuple[str, str], ...]:
    values = {name: states[0] for name, states in FIXED_FACTOR_STATES}
    values.update(updates)
    return tuple(sorted(values.items()))


def _observation(index: int, *, r: str | None = "0.5", status: str = "REALIZED", **factors: str) -> AttributionObservation:
    session = date(2026, 1, 2) + timedelta(days=index)
    return AttributionObservation(
        setup_identity=f"setup-{index}",
        session_date=session,
        signal_known_at=datetime.combine(session, datetime.min.time(), NY) + timedelta(hours=10),
        level_type="PDH",
        outcome_status=status,
        r_multiple=Decimal(r) if r is not None else None,
        exit_reason="NEXT_OBJECTIVE_LEVEL" if r is not None and Decimal(r) > 0 else "STOP" if r is not None else None,
        mfe=Decimal("1.2") if r is not None else None,
        mae=Decimal("0.4") if r is not None else None,
        factors=_factors(**factors),
    )


def test_observation_rejects_unsorted_or_duplicate_factors() -> None:
    with pytest.raises(ValueError, match="sorted order"):
        _observation(0).model_copy(update={"factors": (("B", "x"), ("A", "y"))}).model_validate(
            _observation(0).model_copy(update={"factors": (("B", "x"), ("A", "y"))}).model_dump()
        )


def test_unrealized_observation_cannot_invent_r() -> None:
    with pytest.raises(ValueError, match="cannot contain R"):
        AttributionObservation(
            setup_identity="bad",
            session_date=date(2026, 1, 2),
            signal_known_at=datetime(2026, 1, 2, 10, tzinfo=NY),
            level_type="PDH",
            outcome_status="AMBIGUOUS_BOTH_TOUCHED",
            r_multiple=Decimal("1"),
            exit_reason=None,
            mfe=None,
            mae=None,
            factors=_factors(),
        )


def test_fixed_buckets_cover_boundaries_without_searching() -> None:
    assert _room_dollars(Decimal("0.50"), False) == "LE_0_50"
    assert _room_dollars(Decimal("0.5000001"), False) == "GT_0_50_LE_1_00"
    assert _atr_regime(Decimal("0.50")) == "NORMAL_0_50_TO_1_00"
    assert _atr_regime(Decimal("1.0001")) == "HIGH_GT_1_00"
    assert _gap_context(Decimal("101"), Decimal("100"), Decimal("4")) == "GAP_UP_GE_0_25_ATR"
    assert _time_bucket(datetime(2026, 1, 2, 11, 30, tzinfo=NY)) == "MIDDAY_1130_1400"


def test_short_candle_quality_is_directional_and_exact_decimal() -> None:
    bar = FiveMinuteBar(
        symbol="SPY", timestamp=datetime(2026, 1, 2, 10, tzinfo=NY), session_date=date(2026, 1, 2),
        open=Decimal("101"), high=Decimal("101.2"), low=Decimal("99.8"), close=Decimal("100"),
        volume=1, trade_count=1, source="alpaca", feed="sip", timeframe="5Min", adjustment="raw", source_bar_count=5,
    )
    assert _candle_quality(bar) == "STRONG"
    assert _candle_quality(bar.model_copy(update={"open": Decimal("100"), "close": Decimal("101")})) == "WEAK_OR_OPPOSING"


def test_report_keeps_unavailable_and_ambiguous_in_baseline(monkeypatch) -> None:
    monkeypatch.setattr(analysis, "BOOTSTRAP_RESAMPLES", 20)
    observations = tuple(_observation(index, r="0.5" if index % 2 else "-1") for index in range(12)) + (
        _observation(20, r=None, status="UNAVAILABLE_OBJECTIVE"),
        _observation(21, r=None, status="AMBIGUOUS_BOTH_TOUCHED"),
    )
    report = analyze_base_short_attribution(
        observations,
        start_date=date(2026, 1, 2), end_date=date(2026, 8, 19),
        fixed_factor_states=FIXED_FACTOR_STATES, source_exit_hash=HASH, source_stage14_hash=HASH,
    )
    assert report.baseline.population_n == 14
    assert report.baseline.trades == 12
    assert report.baseline.unavailable_or_ambiguous == 2


def test_only_predeclared_interactions_are_emitted(monkeypatch) -> None:
    monkeypatch.setattr(analysis, "BOOTSTRAP_RESAMPLES", 5)
    report = analyze_base_short_attribution(
        tuple(_observation(index) for index in range(2)),
        start_date=date(2026, 1, 2), end_date=date(2026, 8, 19),
        fixed_factor_states=FIXED_FACTOR_STATES, source_exit_hash=HASH, source_stage14_hash=HASH,
    )
    assert report.allowed_interactions == ALLOWED_INTERACTIONS
    assert {item.factor for item in report.interaction_groups} == set(ALLOWED_INTERACTIONS)


def test_sparse_groups_are_always_insufficient_evidence(monkeypatch) -> None:
    monkeypatch.setattr(analysis, "BOOTSTRAP_RESAMPLES", 5)
    report = analyze_base_short_attribution(
        tuple(_observation(index, r="2", LEVEL_TYPE="PDH") for index in range(8))
        + tuple(_observation(index + 20, r="-1", LEVEL_TYPE="PDL") for index in range(8)),
        start_date=date(2026, 1, 2), end_date=date(2026, 8, 19),
        fixed_factor_states=FIXED_FACTOR_STATES, source_exit_hash=HASH, source_stage14_hash=HASH,
    )
    pdh = next(item for item in report.single_factor_groups if item.factor == "LEVEL_TYPE" and item.state == "PDH")
    assert pdh.fewer_than_30_trades
    assert pdh.classification.value == "INSUFFICIENT_EVIDENCE"


def test_monthly_and_leave_one_month_out_are_reported(monkeypatch) -> None:
    monkeypatch.setattr(analysis, "BOOTSTRAP_RESAMPLES", 5)
    observations = tuple(
        AttributionObservation(
            **_observation(index).model_dump(exclude={"session_date", "signal_known_at"}),
            session_date=date(2026, 1 + index % 4, 2),
            signal_known_at=datetime(2026, 1 + index % 4, 2, 10, tzinfo=NY),
        )
        for index in range(40)
    )
    report = analyze_base_short_attribution(
        observations, start_date=date(2026, 1, 2), end_date=date(2026, 8, 19),
        fixed_factor_states=FIXED_FACTOR_STATES, source_exit_hash=HASH, source_stage14_hash=HASH,
    )
    assert len(report.baseline.monthly_performance) == 8
    assert report.baseline.leave_one_month_out_min_mean_r is not None
    assert not report.baseline.month_concentration


def test_markdown_contains_complete_review_sections(monkeypatch) -> None:
    monkeypatch.setattr(analysis, "BOOTSTRAP_RESAMPLES", 5)
    report = analyze_base_short_attribution(
        tuple(_observation(index) for index in range(2)),
        start_date=date(2026, 1, 2), end_date=date(2026, 8, 19),
        fixed_factor_states=FIXED_FACTOR_STATES, source_exit_hash=HASH, source_stage14_hash=HASH,
    )
    markdown = render_attribution_markdown(report)
    assert "## 2. Complete single-factor attribution table" in markdown
    assert "## 3. Complete predeclared interaction table" in markdown
    assert "## 5. Multiple-testing diagnostics" in markdown
    assert "Stage 14 remains paused and unchanged" in markdown
