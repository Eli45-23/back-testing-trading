from __future__ import annotations

import socket
from datetime import date, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

import spy_research.cli as cli_module
import spy_research.execution.service as execution_service_module
from spy_research.data.schemas import RawBarRecord
from spy_research.execution import (
    AtrStopModel,
    ExecutableTradeSetup,
    ExecutionInputError,
    FixedRiskSimulationService,
    RiskTargetModel,
    StrategyPopulation,
    TradeExitReason,
    TradeSimulationStatus,
    fixed_risk_variants,
    simulate_fixed_risk_trade,
    strategy_populations,
    summarize_trade_variant,
)
from spy_research.interactions import LevelType
from spy_research.strategy.models import EntryStatus, SetupDirection


NY = ZoneInfo("America/New_York")
SESSION = date(2026, 1, 2)
ENTRY = datetime(2026, 1, 2, 10, 0, tzinfo=NY)


def setup(direction: SetupDirection = SetupDirection.LONG) -> ExecutableTradeSetup:
    return ExecutableTradeSetup(
        setup_identity=f"setup-{direction.value}",
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
    high: str = "100.5",
    low: str = "99.5",
    close: str = "100",
    day: int = 2,
) -> RawBarRecord:
    return RawBarRecord(
        symbol="SPY",
        timestamp=datetime(2026, 1, day, 10, minute, tzinfo=NY),
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


def variant(stop=AtrStopModel.ATR_0_50, target=RiskTargetModel.R_1):
    return next(
        item
        for item in fixed_risk_variants()
        if item.stop_model is stop and item.target_model is target
    )


def simulate(
    direction: SetupDirection,
    bars,
    *,
    atr: Decimal | None = Decimal("2"),
    selected_variant=None,
):
    return simulate_fixed_risk_trade(
        setup(direction),
        StrategyPopulation.BASE_ALL,
        selected_variant or variant(),
        atr,
        tuple(bars),
    )


def test_exact_frozen_stop_and_target_family() -> None:
    assert tuple(item.value for item in AtrStopModel) == (
        "ATR_0_50",
        "ATR_0_75",
        "ATR_1_00",
    )
    assert tuple(item.value for item in RiskTargetModel) == (
        "1R",
        "1.5R",
        "2R",
        "2.5R",
        "3R",
    )
    variants = fixed_risk_variants()
    assert len(variants) == 15
    assert len({(item.stop_model, item.target_model) for item in variants}) == 15
    assert {item.stop_multiplier for item in variants} == {
        Decimal("0.50"),
        Decimal("0.75"),
        Decimal("1.00"),
    }
    assert {item.target_r for item in variants} == {
        Decimal("1"),
        Decimal("1.5"),
        Decimal("2"),
        Decimal("2.5"),
        Decimal("3"),
    }
    with pytest.raises(ValueError):
        AtrStopModel("ATR_1_25")
    with pytest.raises(ValidationError):
        type(variant())(
            stop_model=AtrStopModel.ATR_0_50,
            stop_multiplier=Decimal("9"),
            target_model=RiskTargetModel.R_1,
            target_r=Decimal("1"),
        )


@pytest.mark.parametrize(
    "direction,test_bar,reason,expected_r",
    (
        (
            SetupDirection.LONG,
            bar(0, high="100.5", low="99", close="99.2"),
            TradeExitReason.STOP,
            Decimal("-1"),
        ),
        (
            SetupDirection.LONG,
            bar(0, high="101", low="99.5", close="100.8"),
            TradeExitReason.TARGET,
            Decimal("1"),
        ),
        (
            SetupDirection.SHORT,
            bar(0, high="101", low="99.5", close="100.8"),
            TradeExitReason.STOP,
            Decimal("-1"),
        ),
        (
            SetupDirection.SHORT,
            bar(0, high="100.5", low="99", close="99.2"),
            TradeExitReason.TARGET,
            Decimal("1"),
        ),
    ),
)
def test_long_and_short_exact_first_hits(direction, test_bar, reason, expected_r) -> None:
    result = simulate(direction, (test_bar,))
    assert result.exit_status is TradeSimulationStatus.SIMULATED
    assert result.exit_reason is reason
    assert result.r_multiple == expected_r
    assert result.bars_observed == result.minutes_observed == 1
    assert result.minutes_in_trade == 0


def test_all_stop_and_target_models_produce_exact_decimal_risk_prices() -> None:
    entry = setup(SetupDirection.LONG)
    for item in fixed_risk_variants():
        result = simulate_fixed_risk_trade(
            entry,
            StrategyPopulation.BASE_ALL,
            item,
            Decimal("2"),
            (bar(0, high="110", low="99.9", close="105"),),
        )
        assert result.initial_risk == Decimal("2") * item.stop_multiplier
        assert result.stop_price == Decimal("100") - result.initial_risk
        assert result.target_price == Decimal("100") + item.target_r * result.initial_risk
        assert result.exit_reason is TradeExitReason.TARGET
        assert result.r_multiple == item.target_r


def test_repeating_decimal_atr_still_has_exact_stop_and_target_r() -> None:
    repeating = Decimal("0.71428571428571428571428571428571428571428571428571")
    target = simulate(
        SetupDirection.LONG,
        (bar(0, high="110", low="99.9"),),
        atr=repeating,
        selected_variant=variant(AtrStopModel.ATR_0_75, RiskTargetModel.R_2_5),
    )
    stop = simulate(
        SetupDirection.SHORT,
        (bar(0, high="110", low="99.9"),),
        atr=repeating,
        selected_variant=variant(AtrStopModel.ATR_0_75, RiskTargetModel.R_3),
    )
    assert target.r_multiple == Decimal("2.5")
    assert stop.r_multiple == Decimal("-1")


def test_same_minute_both_touch_is_ambiguous_and_retains_ohlc() -> None:
    result = simulate(
        SetupDirection.LONG,
        (bar(0, high="101", low="99", close="100"),),
    )
    assert result.exit_status is TradeSimulationStatus.AMBIGUOUS_BOTH_TOUCHED
    assert result.exit_timestamp == ENTRY
    assert result.exit_price is result.exit_reason is None
    assert result.price_pnl is result.r_multiple is None
    assert result.ambiguity is not None
    assert result.ambiguity.high == Decimal("101")
    assert result.ambiguity.low == Decimal("99")
    assert result.ambiguity.stop_touched and result.ambiguity.target_touched


@pytest.mark.parametrize(
    "close,expected",
    (("100.5", Decimal("0.5")), ("99.5", Decimal("-0.5"))),
)
def test_eod_exit_supports_partial_positive_and_negative_above_minus_one(close, expected) -> None:
    result = simulate(
        SetupDirection.LONG,
        (
            bar(0),
            bar(1, high="100.6", low="99.4", close=close),
        ),
    )
    assert result.exit_reason is TradeExitReason.EOD_CLOSE
    assert result.exit_timestamp == ENTRY + timedelta(minutes=1)
    assert result.exit_price == Decimal(close)
    assert result.r_multiple == expected
    assert result.minutes_in_trade == 1
    assert result.bars_observed == 2


@pytest.mark.parametrize("atr", (None, Decimal("0"), Decimal("-0.1")))
def test_missing_or_nonpositive_confirmation_atr_is_unavailable(atr) -> None:
    result = simulate(
        SetupDirection.LONG,
        (bar(0, high="999", low="1"),),
        atr=atr,
    )
    assert result.exit_status is TradeSimulationStatus.TRADE_UNAVAILABLE_ATR
    assert result.stop_price is result.target_price is result.r_multiple is None
    assert result.bars_observed == 0


def test_bars_before_entry_and_after_first_exit_cannot_change_outcome() -> None:
    baseline = simulate(
        SetupDirection.LONG,
        (
            bar(0, high="101", low="99.5"),
            bar(1, high="999", low="1"),
        ),
    )
    before_values = bar(0).model_dump()
    before_values.update(
        timestamp=ENTRY - timedelta(minutes=1),
        high=Decimal("999"),
        low=Decimal("1"),
    )
    before = RawBarRecord.model_validate(before_values)
    changed = simulate(
        SetupDirection.LONG,
        (
            before,
            bar(0, high="101", low="99.5"),
            bar(1, high="100", low="100"),
        ),
    )
    assert baseline.exit_reason is TradeExitReason.TARGET
    assert changed.exit_reason is TradeExitReason.TARGET
    assert baseline.exit_timestamp == changed.exit_timestamp == ENTRY
    assert baseline.r_multiple == changed.r_multiple == Decimal("1")


def test_next_session_is_rejected_and_cannot_be_carried_overnight() -> None:
    with pytest.raises(ExecutionInputError, match="setup session"):
        simulate(
            SetupDirection.LONG,
            (
                bar(0),
                bar(1, day=3, high="999", low="1"),
            ),
        )


def test_missing_atr_cannot_be_backfilled_by_later_prices() -> None:
    first = simulate(SetupDirection.LONG, (bar(0),), atr=None)
    second = simulate(
        SetupDirection.LONG,
        (bar(0), bar(1, high="200", low="1")),
        atr=None,
    )
    assert first == second


def test_service_uses_only_exact_confirmation_timestamp_atr(monkeypatch) -> None:
    frozen_setup = SimpleNamespace(
        setup_identity="confirmation-cutoff",
        session_date=SESSION,
        direction=SetupDirection.LONG,
        level_type=LevelType.PDH,
        confirmation_bar_timestamp=ENTRY - timedelta(minutes=5),
        signal_known_at=ENTRY,
    )
    outcome = SimpleNamespace(
        setup=frozen_setup,
        entry_reference=SimpleNamespace(
            entry_status=EntryStatus.AVAILABLE,
            entry_reference_timestamp=ENTRY,
            entry_reference_price=Decimal("100"),
        ),
    )

    class FakeOutcomeService:
        def __init__(self, *args):
            pass

        def calculate(self, *, start, end):
            return SimpleNamespace(outcomes=(outcome,))

    class FakeAtrService:
        def __init__(self, *args):
            pass

        def calculate(self, *, start, end):
            return SimpleNamespace(
                rows=(
                    SimpleNamespace(
                        session_date=SESSION,
                        timestamp=ENTRY - timedelta(minutes=5),
                        atr14=None,
                    ),
                    SimpleNamespace(
                        session_date=SESSION,
                        timestamp=ENTRY,
                        atr14=Decimal("2"),
                    ),
                )
            )

    class FakeRawStore:
        def load_raw_bars(self, **kwargs):
            return ()

    monkeypatch.setattr(
        execution_service_module,
        "SetupOutcomeService",
        FakeOutcomeService,
    )
    monkeypatch.setattr(execution_service_module, "AtrIndicatorService", FakeAtrService)
    config = SimpleNamespace(
        symbol="SPY",
        data=SimpleNamespace(feed="sip", timeframe="1Min"),
    )
    result = FixedRiskSimulationService(config, object(), FakeRawStore()).calculate(
        start=date(2026, 1, 2),
        end=date(2026, 8, 19),
    )
    assert len(result.trades) == 15
    assert all(
        item.exit_status is TradeSimulationStatus.TRADE_UNAVAILABLE_ATR
        for item in result.trades
    )


def test_entry_must_equal_frozen_stage9_timestamp_and_open() -> None:
    with pytest.raises(ExecutionInputError, match="accepted Stage 9"):
        simulate(
            SetupDirection.LONG,
            (bar(0, open="100.01"),),
        )


def test_membership_is_outcome_blind_and_exact() -> None:
    long = setup(SetupDirection.LONG)
    short = setup(SetupDirection.SHORT)
    assert strategy_populations(long) == (StrategyPopulation.BASE_ALL,)
    assert strategy_populations(short) == (
        StrategyPopulation.BASE_ALL,
        StrategyPopulation.BASE_SHORT,
    )
    before = strategy_populations(short)
    simulate(
        SetupDirection.SHORT,
        (bar(0, high="101", low="99.5"),),
    )
    assert strategy_populations(short) == before


def test_outputs_and_inputs_are_deterministic_and_immutable() -> None:
    first = simulate(SetupDirection.LONG, (bar(0), bar(1, close="100.25")))
    second = simulate(SetupDirection.LONG, (bar(0), bar(1, close="100.25")))
    assert first == second
    with pytest.raises(ValidationError):
        first.entry_price = Decimal("1")


def test_primary_statistics_exclude_unavailable_and_ambiguous() -> None:
    definite = simulate(
        SetupDirection.LONG,
        (bar(0, high="101", low="99.5"),),
    )
    ambiguous = simulate(
        SetupDirection.LONG,
        (bar(0, high="101", low="99"),),
    )
    unavailable = simulate(SetupDirection.LONG, (bar(0),), atr=None)
    stats = summarize_trade_variant(
        (definite, ambiguous, unavailable),
        population=StrategyPopulation.BASE_ALL,
        variant=variant(),
        start=SESSION,
        end=SESSION,
    )
    assert stats.eligible_setup_n == 3
    assert stats.unavailable_atr_n == 1
    assert stats.executable_simulated_n == 2
    assert stats.ambiguous_both_touched_n == 1
    assert stats.realized_trade_n == stats.target_exit_n == 1
    assert stats.r_multiple.n == 1
    assert stats.win_rate_percentage == Decimal("100")
    assert stats.monthly[0].trade_n == 1


def test_cli_is_offline_and_nonpersistent(monkeypatch, tmp_path, capsys) -> None:
    sentinel = object()

    def reject_network(*args, **kwargs):
        raise AssertionError("Stage 13.1 must remain offline")

    def mocked_calculate(self, *, start, end):
        assert start == date(2026, 1, 2)
        assert end == date(2026, 8, 19)
        return sentinel

    def mocked_print(result):
        assert result is sentinel
        print("stage13.1-pass")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    monkeypatch.setattr(FixedRiskSimulationService, "calculate", mocked_calculate)
    monkeypatch.setattr(cli_module, "_print_fixed_risk_simulation", mocked_print)
    before = tuple(tmp_path.iterdir())
    result = cli_module.main(
        [
            "simulate-fixed-risk-trades",
            "--start",
            "2026-01-02",
            "--end",
            "2026-08-19",
            "--raw-data-root",
            str(tmp_path / "raw"),
            "--processed-data-root",
            str(tmp_path / "processed"),
        ]
    )
    assert result == 0
    assert "stage13.1-pass" in capsys.readouterr().out
    assert tuple(tmp_path.iterdir()) == before
