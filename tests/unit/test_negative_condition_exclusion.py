from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from spy_research.attribution import exclusion_analysis as exclusions
from spy_research.attribution.exclusion_analysis import (
    _matches,
    _room_diagnostic,
    _validate_frozen_conditions,
    analyze_exclusions,
)
from spy_research.attribution.exclusion_models import (
    RoomDiagnosticClassification,
)
from spy_research.attribution.exclusion_reporting import render_exclusion_markdown
from spy_research.attribution.models import AttributionObservation, AttributionReport


NY = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parents[2]


def _observation(
    index: int,
    *,
    r: str | None = "0.5",
    vwap: str = "MIXED_ALIGNMENT",
    room: str = "ATR_1_0_TO_1_5",
    structure: str = "MIXED_STRUCTURE",
    ema: str = "EMA_NOT_ALIGNED",
    mfe: str = "0.5",
    mae: str = "0.2",
) -> AttributionObservation:
    month = 1 + index % 8
    day = 2 + index // 8
    session = date(2026, month, min(day, 27))
    factors = tuple(sorted({
        "EMA_ALIGNMENT": ema,
        "MARKET_STRUCTURE": structure,
        "ROOM_ATR": room,
        "VWAP_ALIGNMENT": vwap,
    }.items()))
    return AttributionObservation(
        setup_identity=f"setup-{index}",
        session_date=session,
        signal_known_at=datetime(2026, month, min(day, 27), 10, tzinfo=NY),
        level_type="PDH",
        outcome_status="REALIZED" if r is not None else "UNAVAILABLE_OBJECTIVE",
        r_multiple=Decimal(r) if r is not None else None,
        exit_reason="NEXT_OBJECTIVE_LEVEL" if r is not None and Decimal(r) > 0 else "STOP" if r is not None else None,
        mfe=Decimal(mfe) if r is not None else None,
        mae=Decimal(mae) if r is not None else None,
        confirmation_atr=Decimal("1") if r is not None else None,
        five_minute_mfe=Decimal(mfe) if r is not None else None,
        five_minute_mae=Decimal(mae) if r is not None else None,
        factors=factors,
    )


def _stage15_report() -> AttributionReport:
    return AttributionReport.model_validate_json(
        (ROOT / "reports/stage15_base_short_attribution.json").read_text()
    )


def test_frozen_condition_definitions_are_exact() -> None:
    assert _matches(_observation(1, vwap="ALL_ALIGNED", room="GT_3_0_ATR"), 1)
    assert not _matches(_observation(2, vwap="ALL_ALIGNED", room="ATR_2_0_TO_3_0"), 1)
    assert _matches(_observation(3, structure="BULLISH_STRUCTURE", room="ATR_0_5_TO_1_0"), 2)
    assert _matches(_observation(4, vwap="NONE_ALIGNED", room="ATR_0_5_TO_1_0"), 3)
    assert _matches(_observation(5, ema="EMA_ALIGNED", structure="BULLISH_STRUCTURE"), 4)


def test_stage15_condition_counts_means_and_q_values_reconcile() -> None:
    _validate_frozen_conditions(_stage15_report())


def test_changed_stage15_condition_fails_closed() -> None:
    report = _stage15_report()
    groups = list(report.interaction_groups)
    index = next(
        i for i, item in enumerate(groups)
        if item.factor == "VWAP_ALIGNMENT×ROOM_ATR"
        and item.state == "ALL_ALIGNED×GT_3_0_ATR"
    )
    groups[index] = groups[index].model_copy(update={"mean_r": Decimal("0")})
    changed = report.model_copy(update={"interaction_groups": tuple(groups)})
    with pytest.raises(ValueError, match="no longer reconciles"):
        _validate_frozen_conditions(changed)


def test_predeclared_variants_overlap_and_partitions(monkeypatch) -> None:
    monkeypatch.setattr(exclusions, "BOOTSTRAP_RESAMPLES", 20)
    monkeypatch.setattr(exclusions, "_validate_baseline", lambda *_: None)
    monkeypatch.setattr(exclusions, "_validate_frozen_conditions", lambda *_: None)
    observations = []
    for index in range(120):
        kwargs: dict[str, str | None] = {}
        if index < 20:
            kwargs.update(vwap="ALL_ALIGNED", room="GT_3_0_ATR", r="-1")
        elif index < 40:
            kwargs.update(structure="BULLISH_STRUCTURE", room="ATR_0_5_TO_1_0", r="-1")
        elif index < 60:
            kwargs.update(vwap="NONE_ALIGNED", room="ATR_0_5_TO_1_0", r="-1")
        elif index < 80:
            kwargs.update(ema="EMA_ALIGNED", structure="BULLISH_STRUCTURE", r="-1")
        observations.append(_observation(index, **kwargs))
    observations.extend(
        _observation(120 + index, r=None, vwap="ALL_ALIGNED", room="GT_3_0_ATR")
        for index in range(8)
    )
    frozen = tuple(observations)
    counts = {
        condition: sum(
            item.r_multiple is not None and _matches(item, condition)
            for item in frozen
        )
        for condition in range(1, 5)
    }
    monkeypatch.setattr(exclusions, "EXPECTED_CONDITION_REALIZED", counts)
    monkeypatch.setitem(exclusions.EXPECTED_BASELINE, "realized", 120)
    report = analyze_exclusions(
        frozen, _stage15_report(), source_stage15_report_hash="0" * 64
    )
    assert [item.variant_id for item in report.variants] == [
        item[0] for item in exclusions.VARIANTS
    ]
    union = next(item for item in report.variants if item.variant_id == "EXCLUDE_ANY_OF_1_TO_4")
    assert union.removal.unique_membership_removed == 88
    assert union.removal.realized_removed == 80
    assert union.removal.unavailable_or_ambiguous_removed == 8
    assert union.metrics.retained_membership + union.removal.unique_membership_removed == 128
    assert len(report.overlap_matrix) == 16
    assert report.variants[0].metrics == report.baseline
    for cell in report.overlap_matrix:
        reverse = next(
            item for item in report.overlap_matrix
            if item.left_condition == cell.right_condition
            and item.right_condition == cell.left_condition
        )
        assert cell.membership_overlap == reverse.membership_overlap
        assert cell.realized_overlap == reverse.realized_overlap


def test_room_diagnostic_can_support_entry_behavior() -> None:
    removed = [
        _observation(index, r="-1", mfe="0.1", mae="0.8") for index in range(35)
    ]
    retained = [
        _observation(100 + index, r="0.5", mfe="0.6", mae="0.2")
        for index in range(35)
    ]
    result = _room_diagnostic("EXCLUDE_NEG_1", (1,), removed, retained)
    assert result is not None
    assert result.classification is RoomDiagnosticClassification.ENTRY_BEHAVIOR_SUPPORTED


def test_non_room_variant_has_no_room_diagnostic() -> None:
    assert _room_diagnostic("EXCLUDE_NEG_4", (4,), [], []) is None


def test_report_renderer_contains_all_eight_sections(monkeypatch) -> None:
    monkeypatch.setattr(exclusions, "BOOTSTRAP_RESAMPLES", 5)
    monkeypatch.setattr(exclusions, "_validate_baseline", lambda *_: None)
    monkeypatch.setattr(exclusions, "_validate_frozen_conditions", lambda *_: None)
    observations = tuple(
        _observation(
            index,
            vwap="ALL_ALIGNED" if index < 4 else "MIXED_ALIGNMENT",
            room="GT_3_0_ATR" if index < 4 else "ATR_1_0_TO_1_5",
        )
        for index in range(16)
    )
    monkeypatch.setattr(
        exclusions,
        "EXPECTED_CONDITION_REALIZED",
        {condition: sum(_matches(item, condition) for item in observations) for condition in range(1, 5)},
    )
    monkeypatch.setitem(exclusions.EXPECTED_BASELINE, "realized", 16)
    report = analyze_exclusions(
        observations, _stage15_report(), source_stage15_report_hash="0" * 64
    )
    markdown = render_exclusion_markdown(report)
    for number in range(1, 9):
        assert f"## {number}." in markdown
    assert "No Alpaca connection or order activity" in markdown
