from __future__ import annotations

import inspect
import socket
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from spy_research.bars.models import FiveMinuteBar
from spy_research.cli import main
from spy_research.interactions import (
    AvailableLevel,
    InteractionType,
    LevelType,
    LiquiditySweepResult,
    LiquiditySweepService,
    PriceSide,
    SweepInputError,
    SweepType,
    classify_level_interaction,
    classify_sweep_pattern,
)


SESSION = date(2026, 8, 19)
TIMESTAMP = datetime(2026, 8, 19, 13, 35, tzinfo=UTC)
LEVEL_PRICE = Decimal("100.000000000000")


def candle(
    *,
    open_price: str,
    high: str,
    low: str,
    close: str,
) -> FiveMinuteBar:
    return FiveMinuteBar(
        symbol="SPY",
        timestamp=TIMESTAMP,
        session_date=SESSION,
        open=Decimal(open_price),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal(close),
        volume=100,
        trade_count=10,
        source="alpaca",
        feed="sip",
        timeframe="5Min",
        adjustment="raw",
        source_bar_count=5,
    )


def classify_bar(value: FiveMinuteBar):
    return classify_level_interaction(
        value,
        AvailableLevel(
            session_date=SESSION,
            level_type=LevelType.PDH,
            level_price=LEVEL_PRICE,
            available_from_timestamp=TIMESTAMP,
        ),
    )


def wick_above(*, close: str = "99.75"):
    result = classify_bar(
        candle(open_price="99.5", high="100.123456789012", low="99", close=close)
    )
    assert result.interaction_type is InteractionType.WICK_THROUGH_ABOVE
    return result


def wick_below(*, close: str = "100.25"):
    result = classify_bar(
        candle(open_price="100.5", high="101", low="99.876543210988", close=close)
    )
    assert result.interaction_type is InteractionType.WICK_THROUGH_BELOW
    return result


def test_sweep_above_uses_strict_close_and_exact_distances() -> None:
    result = classify_sweep_pattern(wick_above())
    assert result.sweep_type is SweepType.SWEEP_ABOVE
    assert result.excursion_side is PriceSide.ABOVE
    assert result.excursion_amount == Decimal("0.123456789012")
    assert result.reclaim_distance == Decimal("0.250000000000")


def test_sweep_below_uses_strict_close_and_exact_distances() -> None:
    result = classify_sweep_pattern(wick_below())
    assert result.sweep_type is SweepType.SWEEP_BELOW
    assert result.excursion_side is PriceSide.BELOW
    assert result.excursion_amount == Decimal("0.123456789012")
    assert result.reclaim_distance == Decimal("0.250000000000")


@pytest.mark.parametrize(
    ("source", "expected"),
    (
        (wick_above, SweepType.WICK_EQUAL_ABOVE),
        (wick_below, SweepType.WICK_EQUAL_BELOW),
    ),
)
def test_equal_close_is_explicit_non_sweep(source, expected) -> None:
    result = classify_sweep_pattern(source(close="100.000000000000"))
    assert result.sweep_type is expected
    assert result.reclaim_distance == Decimal("0")


@pytest.mark.parametrize(
    "source",
    (
        lambda: classify_bar(
            candle(open_price="99", high="100", low="98", close="99")
        ),
        lambda: classify_bar(
            candle(open_price="99", high="101", low="98", close="100.5")
        ),
        lambda: classify_bar(
            candle(open_price="101", high="102", low="99", close="99.5")
        ),
        lambda: classify_bar(
            candle(open_price="101", high="102", low="100.5", close="101.5")
        ),
    ),
)
def test_non_wick_seed_types_are_rejected(source) -> None:
    interaction = source()
    assert interaction.interaction_type in {
        InteractionType.TOUCH,
        InteractionType.CLOSE_THROUGH_ABOVE,
        InteractionType.CLOSE_THROUGH_BELOW,
        InteractionType.NO_INTERACTION,
    }
    with pytest.raises(SweepInputError, match="Only WICK_THROUGH"):
        classify_sweep_pattern(interaction)


@pytest.mark.parametrize("source", (wick_above, wick_below))
def test_dual_side_facts_and_open_side_are_preserved(source) -> None:
    interaction = source()
    assert interaction.traded_above and interaction.traded_below
    result = classify_sweep_pattern(interaction)
    assert result.traded_above is interaction.traded_above
    assert result.traded_below is interaction.traded_below
    assert result.open_side is interaction.open_side


def test_source_and_market_identity_are_preserved() -> None:
    interaction = wick_above()
    result = classify_sweep_pattern(interaction)
    assert result.source_interaction_identity.endswith("level-interaction-v1")
    assert interaction.candle_timestamp.isoformat() in result.source_interaction_identity
    assert result.session_date == interaction.session_date
    assert result.candle_timestamp == interaction.candle_timestamp
    assert result.candle_completed_at == interaction.candle_completed_at
    assert result.level_type == interaction.level_type
    assert result.level_price == interaction.level_price
    assert result.source_interaction_type == interaction.interaction_type


def test_source_is_immutable_and_output_is_frozen() -> None:
    interaction = wick_above()
    before = interaction.model_dump()
    result = classify_sweep_pattern(interaction)
    assert interaction.model_dump() == before
    with pytest.raises(ValidationError):
        result.sweep_type = SweepType.SWEEP_BELOW


def test_zero_future_bar_contract_and_prefix_stability() -> None:
    interaction = wick_above()
    assert tuple(inspect.signature(classify_sweep_pattern).parameters) == (
        "interaction",
    )
    through_t = classify_sweep_pattern(interaction)
    unrelated_future_session = (
        candle(open_price="101", high="102", low="90", close="91"),
    )
    assert unrelated_future_session
    entire_session = classify_sweep_pattern(interaction)
    assert through_t == entire_session


def test_pure_classifier_is_offline_and_nonpersistent(monkeypatch, tmp_path) -> None:
    def reject_network(*args, **kwargs):
        raise AssertionError("sweep classification must remain offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    classify_sweep_pattern(wick_below())
    assert list(tmp_path.iterdir()) == []


def test_cli_is_offline_read_only_and_reports_patterns(
    monkeypatch, tmp_path, capsys
) -> None:
    pattern = classify_sweep_pattern(wick_above())

    def mocked_calculate(self, *, start, end):
        return LiquiditySweepResult(
            start_date=start,
            end_date=end,
            seed_count=1,
            patterns=(pattern,),
        )

    def reject_network(*args, **kwargs):
        raise AssertionError("sweep-patterns CLI must remain offline")

    monkeypatch.setattr(LiquiditySweepService, "calculate", mocked_calculate)
    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "sweep-patterns",
            "--start",
            "2026-08-19",
            "--end",
            "2026-08-19",
            "--raw-data-root",
            str(tmp_path / "raw"),
            "--processed-data-root",
            str(tmp_path / "processed"),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "wick seeds: 1" in captured.out
    assert "SWEEP_ABOVE=1" in captured.out
    assert "0.123456789012" in captured.out
    assert captured.err == ""
    assert list(tmp_path.iterdir()) == []
