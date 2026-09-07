from __future__ import annotations

from decimal import Decimal
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from spy_research.attribution import exclusion_analysis
from spy_research.attribution.models import AttributionObservation
from spy_research.attribution.oos_analysis import analyze_oos_period

from spy_research.attribution.oos_models import (
    OOSCandidate,
    OOSClassification,
    frozen_oos_design,
)


def test_oos_candidate_universe_is_exact_and_predeclared() -> None:
    design = frozen_oos_design()
    assert design.candidates == (
        OOSCandidate.BASE_SHORT_CONTROL,
        OOSCandidate.EXCLUDE_NEG_1,
        OOSCandidate.EXCLUDE_NEG_4,
        OOSCandidate.EXCLUDE_NEG_1_2,
        OOSCandidate.EXCLUDE_NEG_1_4,
        OOSCandidate.EXCLUDE_NEG_1_2_4,
    )
    assert design.outcome_accessed_when_frozen is False


def test_oos_negative_conditions_preserve_stage15_states() -> None:
    design = frozen_oos_design()
    assert [
        (item.factor_left, item.state_left, item.factor_right, item.state_right)
        for item in design.conditions
    ] == [
        ("VWAP_ALIGNMENT", "ALL_ALIGNED", "ROOM_ATR", "GT_3_0_ATR"),
        ("MARKET_STRUCTURE", "BULLISH_STRUCTURE", "ROOM_ATR", "ATR_0_5_TO_1_0"),
        ("VWAP_ALIGNMENT", "NONE_ALIGNED", "ROOM_ATR", "ATR_0_5_TO_1_0"),
        ("EMA_ALIGNMENT", "EMA_ALIGNED", "MARKET_STRUCTURE", "BULLISH_STRUCTURE"),
    ]


def test_oos_periods_gates_and_classifications_are_frozen() -> None:
    design = frozen_oos_design()
    assert [(item.year, item.required) for item in design.periods] == [
        (2025, True), (2024, False)
    ]
    assert design.minimum_realized_retention.as_tuple().exponent == -2
    assert design.minimum_realized_retention == Decimal("0.70")
    assert design.minimum_month_retention == Decimal("0.50")
    assert design.minimum_sessions == 80
    assert design.bootstrap_resamples == 10_000
    assert design.permitted_classifications == tuple(OOSClassification)


def _observation(index: int) -> AttributionObservation:
    session = date(2025, 1, 2) + timedelta(days=index)
    values = {
        "VWAP_ALIGNMENT": "MIXED_ALIGNMENT",
        "ROOM_ATR": "ATR_1_0_TO_1_5",
        "MARKET_STRUCTURE": "MIXED_STRUCTURE",
        "EMA_ALIGNMENT": "EMA_NOT_ALIGNED",
    }
    r = Decimal("0.5")
    mfe, mae = Decimal("0.6"), Decimal("0.2")
    if index < 20:
        values.update(VWAP_ALIGNMENT="ALL_ALIGNED", ROOM_ATR="GT_3_0_ATR")
        r, mfe, mae = Decimal("-1"), Decimal("0.1"), Decimal("0.8")
    elif index < 40:
        values.update(EMA_ALIGNMENT="EMA_ALIGNED", MARKET_STRUCTURE="BULLISH_STRUCTURE")
        r, mfe, mae = Decimal("-1"), Decimal("0.1"), Decimal("0.8")
    return AttributionObservation(
        setup_identity=f"oos-{index}",
        session_date=session,
        signal_known_at=datetime.combine(
            session, datetime.min.time(), ZoneInfo("America/New_York")
        ) + timedelta(hours=10),
        level_type="PDH",
        outcome_status="REALIZED",
        r_multiple=r,
        exit_reason="STOP" if r < 0 else "NEXT_OBJECTIVE_LEVEL",
        mfe=mfe,
        mae=mae,
        confirmation_atr=Decimal("1"),
        five_minute_mfe=mfe,
        five_minute_mae=mae,
        factors=tuple(sorted(values.items())),
    )


def test_oos_analysis_emits_only_frozen_candidates_and_reconciles(monkeypatch) -> None:
    monkeypatch.setattr(exclusion_analysis, "BOOTSTRAP_RESAMPLES", 20)
    observations = tuple(_observation(index) for index in range(120))
    report = analyze_oos_period(
        observations,
        period="2025",
        start_date=date(2025, 1, 2),
        end_date=date(2025, 12, 31),
    )
    assert tuple(item.candidate for item in report.candidates) == tuple(OOSCandidate)
    assert report.candidates[0].metrics == report.baseline
    for item in report.candidates:
        assert (
            item.metrics.retained_membership
            + item.removal.unique_membership_removed
            == report.baseline.retained_membership
        )
    assert report.candidates[1].mean_r_delta > 0
