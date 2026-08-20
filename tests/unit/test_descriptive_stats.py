from __future__ import annotations

import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Context, Decimal, ROUND_HALF_EVEN, getcontext, localcontext

import pytest

from spy_research.cli import main
from spy_research.events import EmaCrossDirection, EmaCrossEvent
from spy_research.outcomes import (
    EmaCrossOutcome,
    EnrichedEmaCrossOutcome,
    ExcursionResult,
    HorizonOutcome,
    OppositeCrossContext,
)
from spy_research.research_stats import (
    Phase1CrossStatisticsService,
    calculate_phase1_cross_statistics,
    summarize_distribution,
)


START = date(2026, 8, 3)
END = date(2026, 8, 19)


def horizon(
    name: str,
    mfe: str,
    mae: str,
    *,
    complete: bool = True,
) -> HorizonOutcome:
    return HorizonOutcome(
        horizon=name,
        requested_minutes=5,
        observed_minutes=5 if complete else 3,
        complete=complete,
        excursion=ExcursionResult(
            mfe=Decimal(mfe),
            mfe_timestamp=datetime(2026, 8, 19, 15, 0, tzinfo=UTC),
            mae=Decimal(mae),
            mae_timestamp=datetime(2026, 8, 19, 15, 1, tzinfo=UTC),
        ),
    )


def item(
    index: int,
    direction: EmaCrossDirection,
    *,
    mfe: str = "1.0",
    mae: str = "0.5",
    vwap_aligned: bool = True,
    expanding: bool = True,
    complete_15: bool = True,
    complete_30: bool = True,
    complete_60: bool = True,
    atr: Decimal | None = Decimal("0.5"),
    opposite_minutes: int | None = None,
) -> EnrichedEmaCrossOutcome:
    timestamp = datetime(2026, 8, 19, 14, 0, tzinfo=UTC) + timedelta(
        minutes=5 * index
    )
    bullish = direction == EmaCrossDirection.BULLISH
    reference = Decimal("100")
    if bullish:
        vwap = Decimal("99") if vwap_aligned else Decimal("101")
        delta = Decimal("0.2") if expanding else Decimal("0")
        signed = Decimal("0.1")
    else:
        vwap = Decimal("101") if vwap_aligned else Decimal("99")
        delta = Decimal("-0.2") if expanding else Decimal("0")
        signed = Decimal("-0.1")
    event = EmaCrossEvent(
        symbol="SPY",
        timestamp=timestamp,
        session_date=END,
        direction=direction,
        reference_price=reference,
        close=reference,
        ema9=reference + signed,
        ema20=reference,
        previous_ema9=reference - signed,
        previous_ema20=reference,
        signed_separation=signed,
        absolute_separation=abs(signed),
        previous_signed_separation=-signed,
        separation_delta_1=delta,
        separation_delta_2=None,
        separation_delta_3=None,
        vwap=vwap,
        close_minus_vwap=reference - vwap,
        ema9_minus_vwap=reference + signed - vwap,
        ema20_minus_vwap=reference - vwap,
        atr14=atr,
    )
    outcome = EmaCrossOutcome(
        event=event,
        symbol="SPY",
        session_date=END,
        event_timestamp=timestamp,
        reference_price=reference,
        outcome_start_timestamp=timestamp + timedelta(minutes=5),
        available_future_minutes=100,
        five=horizon("5m", mfe, mae),
        fifteen=horizon("15m", mfe, mae, complete=complete_15),
        thirty=horizon("30m", mfe, mae, complete=complete_30),
        sixty=horizon("60m", mfe, mae, complete=complete_60),
        eod=horizon("EOD", mfe, mae),
    )
    opposite = OppositeCrossContext(
        opposite_cross_timestamp=(
            timestamp + timedelta(minutes=opposite_minutes)
            if opposite_minutes is not None
            else None
        ),
        opposite_cross_direction=(
            EmaCrossDirection.BEARISH if bullish else EmaCrossDirection.BULLISH
        )
        if opposite_minutes is not None
        else None,
        minutes_to_opposite_cross=opposite_minutes,
        bars_to_opposite_cross=(
            opposite_minutes // 5 if opposite_minutes is not None else None
        ),
    )
    return EnrichedEmaCrossOutcome(outcome=outcome, opposite_cross=opposite)


def stats(items):
    return calculate_phase1_cross_statistics(items, start=START, end=END)


def group(result, name):
    return next(value for value in result.groups if value.name == name)


def horizon_stats(result, group_name, horizon_name):
    return next(
        value
        for value in group(result, group_name).horizons
        if value.horizon == horizon_name
    )


def test_distribution_mean_odd_median_and_min_max() -> None:
    result = summarize_distribution([Decimal("1"), Decimal("2"), Decimal("6")])
    assert result.mean == Decimal("3")
    assert result.median == Decimal("2")
    assert result.minimum == Decimal("1")
    assert result.maximum == Decimal("6")


def test_even_median_and_linear_p25_p75() -> None:
    result = summarize_distribution(
        [Decimal("1"), Decimal("2"), Decimal("3"), Decimal("4")]
    )
    assert result.median == Decimal("2.5")
    assert result.p25 == Decimal("1.75")
    assert result.p75 == Decimal("3.25")


def test_empty_and_single_value_distribution_semantics() -> None:
    empty = summarize_distribution([])
    assert empty.n == 0
    assert all(
        value is None
        for value in (empty.mean, empty.median, empty.minimum, empty.maximum, empty.p25, empty.p75)
    )
    one = summarize_distribution([Decimal("7.25")])
    assert one.n == 1
    assert all(
        value == Decimal("7.25")
        for value in (one.mean, one.median, one.minimum, one.maximum, one.p25, one.p75)
    )


def test_distribution_decimal_precision_and_input_immutability() -> None:
    values = [Decimal("1.1234567890123456789"), Decimal("2.234567890123456789")]
    before = values.copy()
    original = getcontext().prec
    try:
        getcontext().prec = 6
        result = summarize_distribution(values)
    finally:
        getcontext().prec = original
    assert result.mean == Decimal("1.67901233956790123395")
    assert values == before


def test_fixed_horizon_eligibility_and_eod_availability() -> None:
    items = [
        item(0, EmaCrossDirection.BULLISH),
        item(
            1,
            EmaCrossDirection.BEARISH,
            complete_15=False,
            complete_30=False,
            complete_60=False,
        ),
    ]
    result = stats(items)
    assert horizon_stats(result, "ALL", "5m").eligible_n == 2
    assert horizon_stats(result, "ALL", "15m").eligible_n == 1
    assert horizon_stats(result, "ALL", "15m").excluded_incomplete_n == 1
    assert horizon_stats(result, "ALL", "30m").eligible_n == 1
    assert horizon_stats(result, "ALL", "60m").eligible_n == 1
    assert horizon_stats(result, "ALL", "EOD").eligible_n == 2


def test_threshold_equality_percentage_denominator_and_monotonicity() -> None:
    items = [
        item(0, EmaCrossDirection.BULLISH, mfe="0.50"),
        item(1, EmaCrossDirection.BEARISH, mfe="0.49"),
        item(2, EmaCrossDirection.BULLISH, mfe="1.00"),
    ]
    horizon_result = horizon_stats(stats(items), "ALL", "15m")
    thresholds = {value.threshold: value for value in horizon_result.dollar_thresholds}
    assert thresholds[Decimal("0.50")].reached_n == 2
    assert thresholds[Decimal("0.50")].eligible_n == 3
    with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
        expected_percentage = Decimal(200) / Decimal(3)
    assert thresholds[Decimal("0.50")].percentage == expected_percentage
    assert thresholds[Decimal("1.00")].reached_n == 1
    assert thresholds[Decimal("1.00")].reached_n <= thresholds[Decimal("0.50")].reached_n


def test_incomplete_observation_never_enters_threshold_denominator() -> None:
    items = [
        item(0, EmaCrossDirection.BULLISH, mfe="1.00"),
        item(1, EmaCrossDirection.BEARISH, mfe="3.00", complete_15=False),
    ]
    threshold = next(
        value
        for value in horizon_stats(stats(items), "ALL", "15m").dollar_thresholds
        if value.threshold == Decimal("1.00")
    )
    assert threshold.reached_n == 1
    assert threshold.eligible_n == 1
    assert threshold.percentage == Decimal("100")


def test_direction_vwap_expansion_and_combined_group_counts() -> None:
    items = [
        item(0, EmaCrossDirection.BULLISH, vwap_aligned=True, expanding=True),
        item(1, EmaCrossDirection.BULLISH, vwap_aligned=False, expanding=False),
        item(2, EmaCrossDirection.BEARISH, vwap_aligned=True, expanding=True),
        item(3, EmaCrossDirection.BEARISH, vwap_aligned=False, expanding=False),
    ]
    result = stats(items)
    assert group(result, "BULLISH").total_n == 2
    assert group(result, "BEARISH").total_n == 2
    assert group(result, "VWAP_ALIGNED").total_n == 2
    assert group(result, "VWAP_NOT_ALIGNED").total_n == 2
    assert group(result, "EXPANDING").total_n == 2
    assert group(result, "NOT_EXPANDING").total_n == 2
    assert group(result, "VWAP_ALIGNED_AND_EXPANDING").total_n == 2
    assert group(result, "OTHER").total_n == 2
    assert group(result, "VWAP_ALIGNED").total_n + group(result, "VWAP_NOT_ALIGNED").total_n == 4


def test_group_assignment_uses_event_context_not_future_outcome() -> None:
    first = item(0, EmaCrossDirection.BULLISH, mfe="0.1", vwap_aligned=True)
    second = item(1, EmaCrossDirection.BULLISH, mfe="9", vwap_aligned=True)
    result = stats([first, second])
    assert group(result, "VWAP_ALIGNED").total_n == 2
    assert group(result, "VWAP_NOT_ALIGNED").total_n == 0


def test_equality_is_not_aligned_and_not_expanding() -> None:
    value = item(0, EmaCrossDirection.BULLISH, vwap_aligned=False, expanding=False)
    result = stats([value])
    assert group(result, "VWAP_NOT_ALIGNED").total_n == 1
    assert group(result, "NOT_EXPANDING").total_n == 1


def test_atr_normalization_thresholds_and_unavailable_exclusion() -> None:
    items = [
        item(0, EmaCrossDirection.BULLISH, mfe="1.0", atr=Decimal("2")),
        item(1, EmaCrossDirection.BEARISH, mfe="2.0", atr=Decimal("1")),
        item(2, EmaCrossDirection.BULLISH, mfe="9.0", atr=None),
    ]
    horizon_result = horizon_stats(stats(items), "ALL", "5m")
    thresholds = {value.threshold: value for value in horizon_result.atr_thresholds}
    assert horizon_result.atr_eligible_n == 2
    assert horizon_result.atr_excluded_n == 1
    assert thresholds[Decimal("0.5")].reached_n == 2
    assert thresholds[Decimal("1.0")].reached_n == 1
    assert thresholds[Decimal("1.5")].reached_n == 1
    assert thresholds[Decimal("2.0")].reached_n == 1
    assert all(value.eligible_n == 2 for value in thresholds.values())


def test_favorable_adverse_relationship_counts() -> None:
    items = [
        item(0, EmaCrossDirection.BULLISH, mfe="2", mae="1"),
        item(1, EmaCrossDirection.BEARISH, mfe="1", mae="1"),
        item(2, EmaCrossDirection.BULLISH, mfe="0.5", mae="1"),
    ]
    counts = horizon_stats(stats(items), "ALL", "5m").favorable_adverse
    assert (counts.mfe_greater, counts.equal, counts.mfe_less) == (1, 1, 1)


def test_absolute_separation_and_opposite_timing_summaries() -> None:
    items = [
        item(0, EmaCrossDirection.BULLISH, opposite_minutes=30),
        item(1, EmaCrossDirection.BEARISH, opposite_minutes=10),
        item(2, EmaCrossDirection.BULLISH),
    ]
    result = stats(items)
    assert result.absolute_separation.n == 3
    assert result.absolute_separation.median == Decimal("0.1")
    assert result.opposite_cross_timing.with_opposite_n == 2
    assert result.opposite_cross_timing.without_opposite_n == 1
    assert result.opposite_cross_timing.minutes.mean == Decimal("20")


def test_empty_small_groups_remain_visible() -> None:
    result = stats([item(0, EmaCrossDirection.BULLISH)])
    bearish = group(result, "BEARISH")
    assert bearish.total_n == 0
    assert all(value.mfe.n == 0 and value.mfe.mean is None for value in bearish.horizons)


def test_statistics_do_not_mutate_stage4_or_stage5_inputs() -> None:
    items = [item(0, EmaCrossDirection.BULLISH), item(1, EmaCrossDirection.BEARISH)]
    before = [value.model_dump(mode="json") for value in items]
    stats(items)
    assert [value.model_dump(mode="json") for value in items] == before


def test_cross_stats_cli_is_offline_and_nonwriting(monkeypatch, tmp_path, capsys) -> None:
    result = stats([item(0, EmaCrossDirection.BULLISH)])

    def fake_calculate(self, *, start, end):
        return result

    def reject_network(*args, **kwargs):
        raise AssertionError("cross-stats must remain offline")

    monkeypatch.setattr(Phase1CrossStatisticsService, "calculate", fake_calculate)
    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        ["cross-stats", "--start", START.isoformat(), "--end", END.isoformat()]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.err == ""
    assert "PHASE 1 EMA CROSS STATISTICS" in captured.out
    assert "Sample: n=1" in captured.out
    assert "Data limitation:" in captured.out
    assert "Status: PASS" in captured.out
    assert list(tmp_path.iterdir()) == []
