from __future__ import annotations

import socket
from datetime import date, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

import spy_research.cli as cli_module
from spy_research.data.schemas import RawBarRecord
from spy_research.execution import (
    BOOTSTRAP_RESAMPLES,
    AtrStopModel,
    ExecutableTradeSetup,
    ExitComparisonInputError,
    ExitFamily,
    ExitModelExitReason,
    ExitModelStatus,
    NormalizedCrossExitEvent,
    StrategyPopulation,
    bootstrap_exit_variant,
    exit_model_variants,
    select_opposite_cross_exit,
    simulate_exit_model_trade,
    summarize_exit_variant,
    trade_views,
)
from spy_research.interactions import LevelType
from spy_research.strategy.models import SetupDirection


NY = ZoneInfo("America/New_York")
SESSION = date(2026, 1, 2)
ENTRY = datetime(2026, 1, 2, 10, 0, tzinfo=NY)


def setup(direction: SetupDirection = SetupDirection.LONG) -> ExecutableTradeSetup:
    return ExecutableTradeSetup(
        setup_identity=f"exit-{direction.value}",
        session_date=SESSION,
        direction=direction,
        level_type=LevelType.PDH,
        confirmation_bar_timestamp=ENTRY - timedelta(minutes=5),
        signal_known_at=ENTRY,
        entry_timestamp=ENTRY,
        entry_price=Decimal("100"),
    )


def bar(
    minute: int,
    *,
    open: str = "100",
    high: str = "100.4",
    low: str = "99.6",
    close: str = "100",
    day: int = 2,
) -> RawBarRecord:
    return RawBarRecord(
        symbol="SPY",
        timestamp=(
            ENTRY + timedelta(minutes=minute)
            if day == 2
            else datetime(2026, 1, day, 10, 0, tzinfo=NY)
            + timedelta(minutes=minute)
        ),
        open=Decimal(open),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal(close),
        volume=100,
        trade_count=10,
        vwap=Decimal("100"),
        source="alpaca",
        feed="sip",
        timeframe="1Min",
        adjustment="raw",
    )


def variant(
    family: ExitFamily,
    stop: AtrStopModel = AtrStopModel.ATR_0_50,
    minutes=None,
):
    return next(
        item
        for item in exit_model_variants()
        if item.family is family
        and item.stop_model is stop
        and item.time_minutes == minutes
    )


def event(
    known_minute: int,
    *,
    family: ExitFamily = ExitFamily.OPPOSITE_EMA9_20_CROSS,
    direction: str = "BEARISH",
    identity: str = "cross",
) -> NormalizedCrossExitEvent:
    known = ENTRY + timedelta(minutes=known_minute)
    return NormalizedCrossExitEvent(
        event_identity=identity,
        family=family,
        session_date=SESSION,
        direction=direction,
        cross_timestamp=known - timedelta(minutes=5),
        cross_known_at=known,
    )


def simulate(
    family: ExitFamily,
    bars,
    *,
    direction=SetupDirection.LONG,
    stop=AtrStopModel.ATR_0_50,
    minutes=None,
    scheduled=None,
    objective=None,
    objective_available=True,
    atr=Decimal("2"),
):
    return simulate_exit_model_trade(
        setup(direction),
        StrategyPopulation.BASE_ALL,
        variant(family, stop, minutes),
        atr,
        tuple(bars),
        scheduled_exit=scheduled,
        objective_price=objective,
        objective_level_types=(LevelType.PDC,) if objective is not None else (),
        objective_available=objective_available,
    )


def test_exact_variant_universe_and_same_stop_control_mapping() -> None:
    variants = exit_model_variants()
    assert len(variants) == 36
    assert len({item.variant_id for item in variants}) == 36
    assert sum(item.family is ExitFamily.FIXED_R_CONTROL for item in variants) == 15
    assert sum(item.family is not ExitFamily.FIXED_R_CONTROL for item in variants) == 21
    assert all(
        len(item.corresponding_control_variant_ids) == 5
        for item in variants
        if item.family is not ExitFamily.FIXED_R_CONTROL
    )
    assert all(
        f":{item.stop_model.value}:" in control
        for item in variants
        if item.family is not ExitFamily.FIXED_R_CONTROL
        for control in item.corresponding_control_variant_ids
    )


@pytest.mark.parametrize(
    "family",
    (
        ExitFamily.OPPOSITE_EMA9_20_CROSS,
        ExitFamily.OPPOSITE_EMA9_VWAP_CROSS,
        ExitFamily.OPPOSITE_EMA20_VWAP_CROSS,
    ),
)
def test_cross_uses_first_opposite_known_strictly_after_entry(family) -> None:
    events = (
        event(-1, family=family, identity="before"),
        event(0, family=family, identity="equal"),
        event(3, family=family, direction="BULLISH", identity="matching"),
        event(5, family=family, identity="first"),
        event(7, family=family, identity="later"),
    )
    result = select_opposite_cross_exit(setup(), family, events)
    assert result is not None
    assert result.executable_at == ENTRY + timedelta(minutes=5)
    assert result.source_event_identity == "first"
    assert result.source_cross_timestamp == ENTRY


def test_cross_known_at_and_first_open_precede_same_minute_stop() -> None:
    family = ExitFamily.OPPOSITE_EMA9_20_CROSS
    scheduled = select_opposite_cross_exit(setup(), family, (event(2),))
    result = simulate(
        family,
        (
            bar(0),
            bar(1),
            bar(2, open="100.25", high="101", low="98", close="99"),
            bar(3, open="999", high="999", low="1", close="1"),
        ),
        scheduled=scheduled,
    )
    assert result.exit_reason is ExitModelExitReason.OPPOSITE_EMA9_20_CROSS
    assert result.exit_timestamp == ENTRY + timedelta(minutes=2)
    assert result.exit_price == Decimal("100.25")
    assert result.r_multiple == Decimal("0.25")
    assert result.bars_observed == 3


def test_stop_in_earlier_minute_wins_before_cross_exit() -> None:
    family = ExitFamily.OPPOSITE_EMA9_20_CROSS
    scheduled = select_opposite_cross_exit(setup(), family, (event(2),))
    result = simulate(
        family,
        (bar(0), bar(1, low="99"), bar(2, open="101")),
        scheduled=scheduled,
    )
    assert result.exit_reason is ExitModelExitReason.STOP
    assert result.exit_timestamp == ENTRY + timedelta(minutes=1)
    assert result.r_multiple == Decimal("-1")


@pytest.mark.parametrize(
    "minutes,reason",
    (
        (15, ExitModelExitReason.TIME_15M),
        (30, ExitModelExitReason.TIME_30M),
        (60, ExitModelExitReason.TIME_60M),
    ),
)
def test_time_exit_is_exact_and_later_bars_are_invisible(minutes, reason) -> None:
    bars = [bar(value) for value in range(minutes + 1)]
    bars[-1] = bar(minutes, open="100.5", high="999", low="1")
    bars.append(bar(minutes + 1, open="1", high="999", low="1"))
    result = simulate(ExitFamily.TIME_EXIT, bars, minutes=minutes)
    assert result.exit_reason is reason
    assert result.exit_timestamp == ENTRY + timedelta(minutes=minutes)
    assert result.exit_price == Decimal("100.5")
    assert result.r_multiple == Decimal("0.5")


def test_time_beyond_available_rth_uses_final_close() -> None:
    result = simulate(
        ExitFamily.TIME_EXIT,
        (bar(0), bar(1, close="100.3")),
        minutes=60,
    )
    assert result.exit_reason is ExitModelExitReason.EOD_CLOSE
    assert result.exit_price == Decimal("100.3")
    assert result.r_multiple == Decimal("0.3")


def test_short_price_pnl_and_r_use_exact_spy_share_arithmetic() -> None:
    result = simulate(
        ExitFamily.TIME_EXIT,
        (bar(0), bar(1, open="99.5", high="100", low="99", close="99.5")),
        direction=SetupDirection.SHORT,
        minutes=15,
    )
    assert result.exit_reason is ExitModelExitReason.EOD_CLOSE
    assert result.price_pnl == Decimal("0.5")
    assert result.r_multiple == Decimal("0.5")


def test_objective_is_frozen_and_uses_exact_decimal_first_hit() -> None:
    result = simulate(
        ExitFamily.NEXT_OBJECTIVE_LEVEL,
        (bar(0), bar(1, high="101.25"), bar(2, high="999", low="1")),
        objective=Decimal("101.25"),
    )
    assert result.objective_price == Decimal("101.25")
    assert result.exit_reason is ExitModelExitReason.NEXT_OBJECTIVE_LEVEL
    assert result.exit_timestamp == ENTRY + timedelta(minutes=1)
    assert result.r_multiple == Decimal("1.25")


def test_objective_same_bar_both_touch_is_ambiguous() -> None:
    result = simulate(
        ExitFamily.NEXT_OBJECTIVE_LEVEL,
        (bar(0, high="101", low="99"),),
        objective=Decimal("101"),
    )
    assert result.status is ExitModelStatus.AMBIGUOUS_BOTH_TOUCHED
    assert result.exit_reason is ExitModelExitReason.AMBIGUOUS_BOTH_TOUCHED
    assert result.r_multiple is None
    assert result.ambiguity is not None


def test_open_ended_objective_and_missing_atr_are_explicitly_unavailable() -> None:
    objective = simulate(
        ExitFamily.NEXT_OBJECTIVE_LEVEL,
        (bar(0, high="999", low="1"),),
        objective_available=False,
    )
    no_atr = simulate(
        ExitFamily.TIME_EXIT,
        (bar(0, high="999", low="1"),),
        minutes=15,
        atr=None,
    )
    assert objective.status is ExitModelStatus.UNAVAILABLE_OBJECTIVE
    assert objective.bars_observed == 0
    assert no_atr.status is ExitModelStatus.UNAVAILABLE_ATR
    assert no_atr.stop_price is None
    assert no_atr.target_context_eligible


def test_later_atr_cannot_change_stop_and_next_session_is_rejected() -> None:
    baseline = simulate(ExitFamily.TIME_EXIT, (bar(0),), minutes=15)
    changed = simulate(
        ExitFamily.TIME_EXIT,
        (bar(0), bar(1, high="999", low="1")),
        minutes=15,
    )
    assert baseline.stop_price == changed.stop_price == Decimal("99.00")
    with pytest.raises(ExitComparisonInputError, match="session boundary"):
        simulate(ExitFamily.TIME_EXIT, (bar(0), bar(1, day=3)), minutes=15)


def test_bootstrap_is_session_clustered_deterministic_and_exactly_10000() -> None:
    selected = variant(ExitFamily.TIME_EXIT, minutes=15)
    paths = (simulate(ExitFamily.TIME_EXIT, (bar(0),), minutes=15),)
    views = trade_views((), paths)
    first = bootstrap_exit_variant(
        views,
        population=StrategyPopulation.BASE_ALL,
        variant=selected,
    )
    second = bootstrap_exit_variant(
        views,
        population=StrategyPopulation.BASE_ALL,
        variant=selected,
    )
    assert first == second
    assert first.resamples == BOOTSTRAP_RESAMPLES == 10_000
    assert first.label == "BOOTSTRAP_UNCERTAINTY_INTERVAL"
    with pytest.raises(ValueError, match="10,000"):
        bootstrap_exit_variant(
            views,
            population=StrategyPopulation.BASE_ALL,
            variant=selected,
            resamples=10,
        )


def test_primary_statistics_exclude_unavailable_and_ambiguous_paths() -> None:
    selected = variant(ExitFamily.NEXT_OBJECTIVE_LEVEL)
    realized = simulate(
        ExitFamily.NEXT_OBJECTIVE_LEVEL,
        (bar(0, high="101"),),
        objective=Decimal("101"),
    ).model_copy(update={"setup_identity": "realized"})
    ambiguous = simulate(
        ExitFamily.NEXT_OBJECTIVE_LEVEL,
        (bar(0, high="101", low="99"),),
        objective=Decimal("101"),
    ).model_copy(update={"setup_identity": "ambiguous"})
    unavailable = simulate(
        ExitFamily.NEXT_OBJECTIVE_LEVEL,
        (bar(0),),
        objective_available=False,
    ).model_copy(update={"setup_identity": "unavailable"})
    stats = summarize_exit_variant(
        trade_views((), (realized, ambiguous, unavailable)),
        population=StrategyPopulation.BASE_ALL,
        variant=selected,
    )
    assert (stats.membership_n, stats.realized_n) == (3, 1)
    assert (stats.unavailable_n, stats.ambiguous_n) == (1, 1)
    assert stats.r_multiple.n == 1
    assert stats.r_multiple.mean == stats.r_multiple.median == Decimal("1")


def test_compare_exit_models_cli_is_offline_and_nonpersistent(
    monkeypatch, tmp_path
) -> None:
    result = SimpleNamespace()

    class FakeService:
        def __init__(self, *args):
            pass

        def calculate(self, *, start, end):
            return result

    monkeypatch.setattr(cli_module, "ExitModelComparisonService", FakeService)
    monkeypatch.setattr(
        cli_module,
        "_print_exit_model_comparison",
        lambda report: None,
    )
    monkeypatch.setattr(
        socket,
        "create_connection",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("network")),
    )
    before = tuple(tmp_path.rglob("*"))
    assert cli_module.main(
        (
            "compare-exit-models",
            "--start",
            "2026-01-02",
            "--end",
            "2026-08-19",
            "--raw-data-root",
            str(tmp_path / "raw"),
            "--processed-data-root",
            str(tmp_path / "processed"),
        )
    ) == 0
    assert tuple(tmp_path.rglob("*")) == before
