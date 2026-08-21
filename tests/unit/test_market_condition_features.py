from __future__ import annotations

import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

import spy_research.cli as cli_module
from spy_research.bars import FiveMinuteBar
from spy_research.indicators import (
    FiveMinuteAtrRow,
    FiveMinuteIndicatorRow,
    FiveMinuteVwapRow,
)
from spy_research.interactions import (
    ImmediateState,
    InteractionType,
    LevelType,
    RetestState,
)
from spy_research.research_stats import summarize_distribution
from spy_research.strategy import (
    BasePriceActionCandidate,
    BasePriceActionResult,
    BaseSetupStatus,
    ConfirmationType,
    SetupDirection,
)
from spy_research.strategy.comparisons import (
    FeatureQuartile,
    MarketConditionFeatureService,
    assign_feature_quartile,
    calculate_market_condition_annotations,
)


SESSION = date(2026, 8, 19)
OPEN = datetime(2026, 8, 19, 13, 30, tzinfo=UTC)


def setup(timestamp: datetime, identity: str = "setup") -> BasePriceActionCandidate:
    return BasePriceActionCandidate(
        setup_identity=identity,
        break_interaction_identity=f"break-{identity}",
        follow_through_identity=f"follow-{identity}",
        session_date=timestamp.date(),
        level_type=LevelType.ORL5,
        level_price=Decimal("100"),
        direction=SetupDirection.LONG,
        break_interaction_type=InteractionType.CLOSE_THROUGH_ABOVE,
        break_timestamp=timestamp - timedelta(minutes=5),
        break_completed_at=timestamp,
        exact_immediate_state=ImmediateState.HOLD,
        exact_retest_state=RetestState.NO_RETEST,
        status=BaseSetupStatus.CONFIRMED,
        confirmation_type=ConfirmationType.IMMEDIATE_HOLD,
        confirmation_bar_timestamp=timestamp,
        signal_known_at=timestamp + timedelta(minutes=5),
        earliest_entry_timestamp=timestamp + timedelta(minutes=5),
        same_session_executable=True,
    )


def inputs(
    closes: list[str],
    *,
    start: datetime = OPEN,
    ema9: list[str | None] | None = None,
    ema20: list[str | None] | None = None,
    vwap: list[str | None] | None = None,
    atr: list[str | None] | None = None,
):
    count = len(closes)
    ema9 = ema9 or [str(100 + index) for index in range(count)]
    ema20 = ema20 or ["99"] * count
    vwap = vwap or ["100"] * count
    atr = atr or ["2"] * count
    bars = []
    ema_rows = []
    vwap_rows = []
    atr_rows = []
    for index, close_text in enumerate(closes):
        timestamp = start + timedelta(minutes=5 * index)
        session = timestamp.date()
        close = Decimal(close_text)
        bars.append(
            FiveMinuteBar(
                symbol="SPY",
                timestamp=timestamp,
                session_date=session,
                open=close,
                high=close + Decimal("1"),
                low=close - Decimal("1"),
                close=close,
                volume=100,
                trade_count=10,
                source="alpaca",
                feed="sip",
                timeframe="5Min",
                adjustment="raw",
                source_bar_count=5,
            )
        )
        ema_rows.append(
            FiveMinuteIndicatorRow(
                symbol="SPY",
                timestamp=timestamp,
                session_date=session,
                close=close,
                ema9=Decimal(ema9[index]) if ema9[index] is not None else None,
                ema20=(
                    Decimal(ema20[index]) if ema20[index] is not None else None
                ),
            )
        )
        vwap_rows.append(
            FiveMinuteVwapRow(
                symbol="SPY",
                timestamp=timestamp,
                session_date=session,
                typical_price=close,
                vwap=Decimal(vwap[index]) if vwap[index] is not None else None,
            )
        )
        atr_rows.append(
            FiveMinuteAtrRow(
                symbol="SPY",
                timestamp=timestamp,
                session_date=session,
                true_range=Decimal("2"),
                atr14=Decimal(atr[index]) if atr[index] is not None else None,
            )
        )
    return tuple(bars), tuple(ema_rows), tuple(vwap_rows), tuple(atr_rows)


def annotate(
    closes: list[str],
    *,
    confirmation_index: int | None = None,
    **kwargs,
):
    source = inputs(closes, **kwargs)
    index = len(closes) - 1 if confirmation_index is None else confirmation_index
    item = setup(source[0][index].timestamp)
    setups = BasePriceActionResult(
        start_date=SESSION,
        end_date=SESSION,
        seed_count=1,
        confirmed_count=1,
        non_confirmed_count=0,
        candidates=(item,),
    )
    return calculate_market_condition_annotations(setups, *source)[0]


def test_exact_confirmation_cutoff_ignores_all_future_rows() -> None:
    base = [str(100 + index) for index in range(25)]
    first = annotate(base, confirmation_index=23)
    changed = base.copy()
    changed[24] = "999"
    second = annotate(
        changed,
        confirmation_index=23,
        ema9=[str(100 + index) for index in range(24)] + ["9999"],
        ema20=["99"] * 24 + ["-9999"],
        vwap=["100"] * 24 + ["7777"],
        atr=["2"] * 24 + ["8888"],
    )
    assert first == second


def test_exact_six_bar_membership_and_decimal_formulas() -> None:
    annotation = annotate([str(100 + index) for index in range(24)])
    assert annotation.value("rolling_high_low_range_6_bars") == Decimal("7")
    assert annotation.value("directional_efficiency_6_bars") == Decimal("1")
    assert annotation.value("range_overlap_fraction_6_bars") == Decimal("1")
    assert annotation.value("close_direction_alternation_fraction_6_bars") == 0
    assert annotation.value("ema9_slope_3_bars") == Decimal("1")
    assert annotation.value("ema9_ema20_absolute_separation") == Decimal("24")
    assert annotation.value("ema9_ema20_separation_atr14") == Decimal("12")


def test_cross_and_price_vwap_side_change_counts() -> None:
    sides = ["99", "101", "99", "101", "99", "101"]
    padding = ["99"] * 18
    annotation = annotate(
        ["99", "101", "99", "101", "99", "101"] * 4,
        ema9=padding + sides,
        ema20=["100"] * 24,
        vwap=["100"] * 24,
    )
    assert annotation.value("ema9_ema20_cross_count_6_bars") == 5
    assert annotation.value("ema9_vwap_cross_count_6_bars") == 5
    assert annotation.value("ema20_vwap_cross_count_6_bars") == 0
    assert annotation.value("price_vwap_side_change_count_6_bars") == 5


def test_zero_close_path_is_explicitly_unavailable() -> None:
    annotation = annotate(["100"] * 24)
    assert annotation.value("directional_efficiency_6_bars") is None
    assert annotation.value("directional_efficiency_12_bars") is None
    assert annotation.value("directional_efficiency_24_bars") is None


def test_alternation_fraction_uses_consecutive_close_moves() -> None:
    closes = ["100"] * 18 + ["100", "101", "100", "101", "100", "101"]
    annotation = annotate(closes)
    assert annotation.value("close_direction_alternation_fraction_6_bars") == 1


def test_overlap_fraction_uses_inclusive_adjacent_range_intersection() -> None:
    closes = ["100"] * 18 + ["100", "101", "105", "106", "110", "111"]
    annotation = annotate(closes)
    assert annotation.value("range_overlap_fraction_6_bars") == Decimal("0.6")


def test_atr_warmup_keeps_raw_values_and_marks_ratios_unavailable() -> None:
    annotation = annotate([str(100 + index) for index in range(24)], atr=[None] * 24)
    assert annotation.value("ema9_ema20_absolute_separation") == Decimal("24")
    assert annotation.value("rolling_high_low_range_24_bars") == Decimal("25")
    assert annotation.value("ema9_ema20_separation_atr14") is None
    assert annotation.value("rolling_range_atr14_24_bars") is None
    assert annotation.value("confirmation_close_vwap_distance_atr14") is None


def test_insufficient_same_session_history_is_not_backfilled() -> None:
    first = inputs([str(100 + index) for index in range(24)])
    next_open = datetime(2026, 8, 20, 13, 30, tzinfo=UTC)
    second = inputs(["200"] * 5, start=next_open, ema9=["100"] * 5)
    combined = tuple(left + right for left, right in zip(first, second, strict=True))
    item = setup(combined[0][-1].timestamp, identity="next-session")
    setups = BasePriceActionResult(
        start_date=SESSION,
        end_date=date(2026, 8, 20),
        seed_count=1,
        confirmed_count=1,
        non_confirmed_count=0,
        candidates=(item,),
    )
    annotation = calculate_market_condition_annotations(setups, *combined)[0]
    assert annotation.value("ema9_slope_3_bars") == 0
    assert annotation.value("rolling_high_low_range_6_bars") is None
    assert annotation.value("directional_efficiency_6_bars") is None


def test_quantile_assignment_is_deterministic_and_inclusive_on_ties() -> None:
    distribution = summarize_distribution(tuple(map(Decimal, (1, 2, 3, 4))))
    assert distribution.p25 == Decimal("1.75")
    assert distribution.median == Decimal("2.5")
    assert distribution.p75 == Decimal("3.25")
    assert assign_feature_quartile(Decimal("1.75"), distribution) is FeatureQuartile.Q1
    assert assign_feature_quartile(Decimal("2.5"), distribution) is FeatureQuartile.Q2
    assert assign_feature_quartile(Decimal("3.25"), distribution) is FeatureQuartile.Q3
    assert assign_feature_quartile(Decimal("4"), distribution) is FeatureQuartile.Q4


def test_annotation_is_immutable_and_contains_no_regime_label() -> None:
    annotation = annotate([str(100 + index) for index in range(24)])
    with pytest.raises(ValidationError):
        annotation.direction = SetupDirection.SHORT
    forbidden = {"trend", "chop", "score", "quality", "qualified"}
    assert forbidden.isdisjoint(type(annotation).model_fields)


def test_every_one_of_142_confirmed_setups_receives_one_annotation() -> None:
    source = inputs([str(100 + index) for index in range(24)])
    timestamp = source[0][-1].timestamp
    candidates = tuple(setup(timestamp, identity=f"setup-{index:03}") for index in range(142))
    setups = BasePriceActionResult(
        start_date=SESSION,
        end_date=SESSION,
        seed_count=142,
        confirmed_count=142,
        non_confirmed_count=0,
        candidates=candidates,
    )
    annotations = calculate_market_condition_annotations(setups, *source)
    assert len(annotations) == 142
    assert len({item.setup_identity for item in annotations}) == 142


def test_cli_command_is_offline_read_only(monkeypatch, tmp_path, capsys) -> None:
    sentinel = object()

    def reject_network(*args, **kwargs):
        raise AssertionError("Stage 10.9 must remain offline")

    def mocked_calculate(self, *, start, end):
        assert start == end == SESSION
        return sentinel

    def mocked_print(result):
        assert result is sentinel
        print("market-condition-pass")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    monkeypatch.setattr(MarketConditionFeatureService, "calculate", mocked_calculate)
    monkeypatch.setattr(cli_module, "_print_market_condition_features", mocked_print)
    exit_code = cli_module.main(
        [
            "market-condition-features",
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
    assert captured.out == "market-condition-pass\n"
    assert captured.err == ""
    assert list(tmp_path.iterdir()) == []
