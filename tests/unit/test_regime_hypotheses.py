from __future__ import annotations

import inspect
import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

import spy_research.cli as cli_module
from spy_research.strategy import SetupDirection
from spy_research.strategy.comparisons import (
    AlternationState,
    CombinedRegimeState,
    CrossQuartileState,
    EfficiencyState,
    FEATURE_NAMES,
    FeatureQuartile,
    FrozenQuartileBoundary,
    MarketConditionAnnotation,
    MarketConditionFeatureValue,
    RegimeHypothesisComparisonService,
    SeparationState,
    VwapDistanceState,
    classify_regime_hypothesis,
    frozen_boundaries,
)
from spy_research.strategy.comparisons.regime_hypotheses import (
    BOUNDARY_FEATURES,
    CROSS_FEATURES,
    build_regime_hypothesis_annotations,
)


SESSION = date(2026, 8, 19)
CONFIRMATION = datetime(2026, 8, 19, 17, 10, tzinfo=UTC)


def boundaries() -> tuple[FrozenQuartileBoundary, ...]:
    return tuple(
        FrozenQuartileBoundary(
            feature_name=name,
            q1_upper=Decimal("1"),
            q2_upper=Decimal("2"),
            q3_upper=Decimal("3"),
        )
        for name in BOUNDARY_FEATURES
    )


def source_annotation(identity: str = "setup", **overrides) -> MarketConditionAnnotation:
    values = {name: None for name in FEATURE_NAMES}
    values.update(
        {
            "directional_efficiency_24_bars": Decimal("2"),
            "ema9_ema20_separation_atr14": Decimal("2"),
            "close_direction_alternation_fraction_24_bars": Decimal("2"),
            "confirmation_close_vwap_distance_atr14": Decimal("2"),
            **{feature: Decimal("2") for _, feature in CROSS_FEATURES},
        }
    )
    values.update(overrides)
    return MarketConditionAnnotation(
        setup_identity=identity,
        session_date=SESSION,
        direction=SetupDirection.SHORT,
        confirmation_bar_timestamp=CONFIRMATION,
        signal_known_at=CONFIRMATION + timedelta(minutes=5),
        features=tuple(
            MarketConditionFeatureValue(name=name, value=values[name])
            for name in FEATURE_NAMES
        ),
    )


def classify(**values):
    return classify_regime_hypothesis(source_annotation(**values), boundaries())


def test_exact_frozen_boundaries_are_copied_without_recalculation() -> None:
    reports = tuple(
        SimpleNamespace(
            feature_name=name,
            distribution=SimpleNamespace(
                q1_upper=Decimal(f"{index}.1"),
                q2_upper=Decimal(f"{index}.2"),
                q3_upper=Decimal(f"{index}.3"),
            ),
        )
        for index, name in enumerate(BOUNDARY_FEATURES, start=1)
    )
    copied = frozen_boundaries(SimpleNamespace(feature_reports=reports))
    assert tuple(item.feature_name for item in copied) == BOUNDARY_FEATURES
    assert copied[0].q1_upper == Decimal("1.1")
    assert copied[-1].q3_upper == Decimal("8.3")


def test_explicit_frozen_boundaries_are_reused_without_reoptimization() -> None:
    expanded_annotation = source_annotation(
        directional_efficiency_24_bars=Decimal("3.5"),
        ema9_ema20_separation_atr14=Decimal("3.5"),
    )
    expanded_reports = tuple(
        SimpleNamespace(
            feature_name=name,
            distribution=SimpleNamespace(
                q1_upper=Decimal("10"),
                q2_upper=Decimal("20"),
                q3_upper=Decimal("30"),
            ),
        )
        for name in BOUNDARY_FEATURES
    )
    expanded_result = SimpleNamespace(
        annotations=(expanded_annotation,),
        feature_reports=expanded_reports,
    )

    frozen = build_regime_hypothesis_annotations(
        expanded_result,
        boundaries=boundaries(),
    )
    recomputed = build_regime_hypothesis_annotations(expanded_result)

    assert frozen[0].efficiency_state is EfficiencyState.HIGH
    assert frozen[0].separation_state is SeparationState.WIDE
    assert frozen[0].combined_state is CombinedRegimeState.TREND_LIKE_A
    assert recomputed[0].efficiency_state is EfficiencyState.LOW
    assert recomputed[0].separation_state is SeparationState.TIGHT
    assert recomputed[0].combined_state is CombinedRegimeState.OTHER


@pytest.mark.parametrize(
    "value, efficiency, separation, alternation, distance",
    (
        (
            Decimal("1"),
            EfficiencyState.LOW,
            SeparationState.TIGHT,
            AlternationState.LOW,
            VwapDistanceState.NEAR,
        ),
        (
            Decimal("2"),
            EfficiencyState.MID,
            SeparationState.MID,
            AlternationState.MID,
            VwapDistanceState.MID,
        ),
        (
            Decimal("3"),
            EfficiencyState.MID,
            SeparationState.MID,
            AlternationState.MID,
            VwapDistanceState.MID,
        ),
        (
            Decimal("3.0001"),
            EfficiencyState.HIGH,
            SeparationState.WIDE,
            AlternationState.HIGH,
            VwapDistanceState.FAR,
        ),
    ),
)
def test_deterministic_q1_middle_q4_mapping(
    value, efficiency, separation, alternation, distance
) -> None:
    annotation = classify(
        directional_efficiency_24_bars=value,
        ema9_ema20_separation_atr14=value,
        close_direction_alternation_fraction_24_bars=value,
        confirmation_close_vwap_distance_atr14=value,
    )
    assert annotation.efficiency_state is efficiency
    assert annotation.separation_state is separation
    assert annotation.alternation_state is alternation
    assert annotation.vwap_distance_state is distance


def test_predeclared_trend_like_a_only() -> None:
    annotation = classify(
        directional_efficiency_24_bars=Decimal("4"),
        ema9_ema20_separation_atr14=Decimal("4"),
        close_direction_alternation_fraction_24_bars=Decimal("2"),
    )
    assert annotation.combined_state is CombinedRegimeState.TREND_LIKE_A


def test_predeclared_chop_like_a_only() -> None:
    annotation = classify(
        directional_efficiency_24_bars=Decimal("1"),
        ema9_ema20_separation_atr14=Decimal("2"),
        close_direction_alternation_fraction_24_bars=Decimal("4"),
    )
    assert annotation.combined_state is CombinedRegimeState.CHOP_LIKE_A


def test_other_and_unavailable_propagation_are_explicit() -> None:
    assert classify().combined_state is CombinedRegimeState.OTHER
    unavailable = classify(directional_efficiency_24_bars=None)
    assert unavailable.efficiency_state is EfficiencyState.UNAVAILABLE
    assert unavailable.combined_state is CombinedRegimeState.UNAVAILABLE


def test_cross_activity_reuses_exact_count_and_quartile() -> None:
    annotation = classify(
        ema9_ema20_cross_count_24_bars=Decimal("4"),
        ema9_vwap_cross_count_24_bars=Decimal("1"),
    )
    ema = annotation.cross("EMA9_20")
    assert ema.frozen_value == Decimal("4")
    assert ema.exact_count == 4
    assert ema.quartile is FeatureQuartile.Q4
    assert ema.quartile_state is CrossQuartileState.TOP
    ema_vwap = annotation.cross("EMA9_VWAP")
    assert ema_vwap.exact_count == 1
    assert ema_vwap.quartile_state is CrossQuartileState.BOTTOM


def test_cross_unavailable_is_not_backfilled() -> None:
    annotation = classify(ema20_vwap_cross_count_24_bars=None)
    cross = annotation.cross("EMA20_VWAP")
    assert cross.frozen_value is None
    assert cross.exact_count is None
    assert cross.quartile is None
    assert cross.quartile_state is CrossQuartileState.UNAVAILABLE


def test_assignment_api_cannot_inspect_outcomes() -> None:
    parameters = inspect.signature(classify_regime_hypothesis).parameters
    assert tuple(parameters) == ("annotation", "boundaries")
    first = classify()
    imagined_outcome = {"mfe": Decimal("999"), "mae": Decimal("0")}
    assert imagined_outcome
    assert classify() == first


def test_no_future_or_strategy_fields_are_accepted() -> None:
    payload = source_annotation().model_dump()
    payload["future_close"] = Decimal("999")
    with pytest.raises(ValidationError):
        MarketConditionAnnotation(**payload)
    annotation = classify()
    forbidden = {"qualified", "filter", "score", "confidence", "outcome"}
    assert forbidden.isdisjoint(type(annotation).model_fields)


def test_exactly_142_frozen_annotations_classify_deterministically() -> None:
    annotations = tuple(
        classify_regime_hypothesis(
            source_annotation(identity=f"setup-{index:03}"), boundaries()
        )
        for index in range(142)
    )
    assert len(annotations) == 142
    assert len({item.setup_identity for item in annotations}) == 142
    assert {item.combined_state for item in annotations} == {
        CombinedRegimeState.OTHER
    }


def test_annotation_is_immutable() -> None:
    annotation = classify()
    with pytest.raises(ValidationError):
        annotation.combined_state = CombinedRegimeState.TREND_LIKE_A


def test_cli_is_offline_and_nonpersistent(monkeypatch, tmp_path, capsys) -> None:
    sentinel = object()

    def reject_network(*args, **kwargs):
        raise AssertionError("Stage 11.1 must remain offline")

    def mocked_calculate(self, *, start, end):
        assert start == end == SESSION
        return sentinel

    def mocked_print(result):
        assert result is sentinel
        print("regime-hypothesis-pass")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    monkeypatch.setattr(RegimeHypothesisComparisonService, "calculate", mocked_calculate)
    monkeypatch.setattr(
        cli_module, "_print_regime_hypothesis_comparison", mocked_print
    )
    exit_code = cli_module.main(
        [
            "compare-regime-hypotheses",
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
    assert captured.out == "regime-hypothesis-pass\n"
    assert captured.err == ""
    assert list(tmp_path.iterdir()) == []
