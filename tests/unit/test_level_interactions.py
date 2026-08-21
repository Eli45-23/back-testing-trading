from __future__ import annotations

import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from spy_research.bars.models import FiveMinuteBar
from spy_research.cli import main
from spy_research.interactions import (
    AvailableLevel,
    InteractionCount,
    InteractionInputError,
    InteractionType,
    LevelInteractionResult,
    LevelInteractionService,
    LevelNotAvailableError,
    LevelType,
    PriceSide,
    build_session_levels,
    classify_level_interaction,
    classify_session_level_interactions,
)
from spy_research.levels import (
    OpeningFiveMinuteLevels,
    PremarketLevels,
    PreviousDayLevels,
)


SESSION = date(2026, 8, 19)
OPEN_TIME = datetime(2026, 8, 19, 13, 30, tzinfo=UTC)
LEVEL_PRICE = Decimal("100")


def candle(
    timestamp: datetime = OPEN_TIME,
    *,
    session_date: date = SESSION,
    open_price: str = "99",
    high: str = "101",
    low: str = "98",
    close: str = "99",
) -> FiveMinuteBar:
    return FiveMinuteBar(
        symbol="SPY",
        timestamp=timestamp,
        session_date=session_date,
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


def level(
    *,
    level_type: LevelType = LevelType.PDH,
    available: datetime = OPEN_TIME,
    session_date: date = SESSION,
) -> AvailableLevel:
    return AvailableLevel(
        session_date=session_date,
        level_type=level_type,
        level_price=LEVEL_PRICE,
        available_from_timestamp=available,
    )


def classify(value: FiveMinuteBar):
    return classify_level_interaction(value, level())


def test_high_equal_level_is_touch_not_wick() -> None:
    result = classify(candle(high="100", low="98", close="99"))
    assert result.interaction_type is InteractionType.TOUCH
    assert result.traded_above is False


def test_low_equal_level_is_touch_not_wick() -> None:
    result = classify(
        candle(open_price="101", high="102", low="100", close="101")
    )
    assert result.interaction_type is InteractionType.TOUCH
    assert result.traded_below is False


def test_close_equal_level_is_never_close_through() -> None:
    result = classify(candle(high="101", low="98", close="100"))
    assert result.close_side is PriceSide.EQUAL
    assert result.interaction_type is InteractionType.WICK_THROUGH_ABOVE
    assert "CLOSE_THROUGH" not in result.interaction_type.value


@pytest.mark.parametrize(
    ("open_price", "high", "low"),
    (("99", "100", "98"), ("101", "102", "100")),
)
def test_return_to_exact_equality_without_opposite_excursion_is_touch(
    open_price, high, low
) -> None:
    result = classify(
        candle(open_price=open_price, high=high, low=low, close="100")
    )
    assert result.interaction_type is InteractionType.TOUCH


def test_exact_decimal_equality_is_deterministic() -> None:
    result = classify(candle(high="100.000000000000", low="99", close="99.5"))
    assert result.interaction_type is InteractionType.TOUCH


@pytest.mark.parametrize(
    ("close", "expected"),
    (("99", InteractionType.WICK_THROUGH_ABOVE),
     ("100", InteractionType.WICK_THROUGH_ABOVE)),
)
def test_wick_through_above_with_below_or_equal_close(close, expected) -> None:
    result = classify(candle(open_price="99", high="101", low="98", close=close))
    assert result.interaction_type is expected
    assert result.traded_above


@pytest.mark.parametrize(
    ("close", "expected"),
    (("101", InteractionType.WICK_THROUGH_BELOW),
     ("100", InteractionType.WICK_THROUGH_BELOW)),
)
def test_wick_through_below_with_above_or_equal_close(close, expected) -> None:
    result = classify(
        candle(open_price="101", high="102", low="99", close=close)
    )
    assert result.interaction_type is expected
    assert result.traded_below


def test_close_through_above_requires_opposite_or_equal_open() -> None:
    result = classify(
        candle(open_price="99", high="102", low="98", close="101")
    )
    assert result.interaction_type is InteractionType.CLOSE_THROUGH_ABOVE
    assert result.open_side is PriceSide.BELOW
    assert result.close_side is PriceSide.ABOVE


def test_close_through_below_requires_opposite_or_equal_open() -> None:
    result = classify(
        candle(open_price="101", high="102", low="98", close="99")
    )
    assert result.interaction_type is InteractionType.CLOSE_THROUGH_BELOW
    assert result.open_side is PriceSide.ABOVE
    assert result.close_side is PriceSide.BELOW


def test_persistent_entirely_above_is_no_interaction() -> None:
    result = classify(
        candle(open_price="101", high="103", low="100.1", close="102")
    )
    assert result.interaction_type is InteractionType.NO_INTERACTION
    assert not result.range_encountered


def test_persistent_entirely_below_is_no_interaction() -> None:
    result = classify(candle(open_price="99", high="99.9", low="97", close="98"))
    assert result.interaction_type is InteractionType.NO_INTERACTION
    assert not result.range_encountered


def test_same_side_retest_is_wick_not_fresh_close_through() -> None:
    result = classify(
        candle(open_price="101", high="103", low="99", close="102")
    )
    assert result.interaction_type is InteractionType.WICK_THROUGH_BELOW


@pytest.mark.parametrize(
    ("open_price", "close", "expected"),
    (("99", "101", InteractionType.CLOSE_THROUGH_ABOVE),
     ("101", "99", InteractionType.CLOSE_THROUGH_BELOW)),
)
def test_dual_side_close_preserves_both_flags(open_price, close, expected) -> None:
    result = classify(
        candle(open_price=open_price, high="102", low="98", close=close)
    )
    assert result.interaction_type is expected
    assert result.traded_above and result.traded_below


def test_dual_side_equal_close_preserves_flags_and_is_not_close_through() -> None:
    result = classify(
        candle(open_price="100", high="102", low="98", close="100")
    )
    assert result.interaction_type is InteractionType.WICK_THROUGH_ABOVE
    assert result.traded_above and result.traded_below


def test_previous_close_context_is_auditable_but_does_not_use_future() -> None:
    previous = candle(close="99")
    current = candle(
        OPEN_TIME + timedelta(minutes=5),
        open_price="99",
        high="102",
        low="98",
        close="101",
    )
    result = classify_level_interaction(current, level(), previous_candle=previous)
    assert result.previous_close == Decimal("99")
    assert result.previous_close_side is PriceSide.BELOW


def test_pdh_and_pmh_are_eligible_at_first_rth_candle() -> None:
    records = classify_session_level_interactions(
        (candle(),),
        (level(level_type=LevelType.PDH), level(level_type=LevelType.PMH)),
        emit_no_interaction=True,
    )
    assert {record.level_type for record in records} == {LevelType.PDH, LevelType.PMH}


def test_orh5_has_no_self_interaction_and_is_eligible_at_0935() -> None:
    opening_level = level(
        level_type=LevelType.ORH5,
        available=OPEN_TIME + timedelta(minutes=5),
    )
    values = (
        candle(),
        candle(OPEN_TIME + timedelta(minutes=5)),
    )
    records = classify_session_level_interactions(
        values, (opening_level,), emit_no_interaction=True
    )
    assert len(records) == 1
    assert records[0].candle_timestamp == OPEN_TIME + timedelta(minutes=5)


def test_direct_classifier_rejects_level_before_availability() -> None:
    with pytest.raises(LevelNotAvailableError):
        classify_level_interaction(
            candle(),
            level(available=OPEN_TIME + timedelta(minutes=5)),
        )


def test_unavailable_stage7_values_create_no_generic_levels() -> None:
    unavailable = PremarketLevels(
        session_date=SESSION,
        pmh=None,
        pml=None,
        pmh_source_timestamp=None,
        pml_source_timestamp=None,
        source_bar_count=0,
        status="NO_PREMARKET_DATA",
    )
    definitions = build_session_levels(
        session_date=SESSION,
        market_open=OPEN_TIME,
        previous_day=None,
        premarket=unavailable,
        opening=None,
    )
    assert definitions == ()


def test_stage7_level_mapping_uses_frozen_availability() -> None:
    previous = PreviousDayLevels(
        symbol="SPY", session_date=SESSION, source_session_date=date(2026, 8, 18),
        pdh=Decimal("103"), pdl=Decimal("97"), pdc=Decimal("99"),
        pdh_source_timestamp=datetime(2026,8,18,15,tzinfo=UTC),
        pdl_source_timestamp=datetime(2026,8,18,16,tzinfo=UTC),
        pdc_source_timestamp=datetime(2026,8,18,19,59,tzinfo=UTC),
    )
    premarket = PremarketLevels(
        session_date=SESSION, pmh=Decimal("102"), pml=Decimal("98"),
        pmh_source_timestamp=datetime(2026,8,19,12,tzinfo=UTC),
        pml_source_timestamp=datetime(2026,8,19,11,tzinfo=UTC),
        source_bar_count=2, status="AVAILABLE",
    )
    opening = OpeningFiveMinuteLevels(
        session_date=SESSION, orh5=Decimal("101"), orl5=Decimal("99"),
        source_timestamp=OPEN_TIME,
        available_from_timestamp=OPEN_TIME + timedelta(minutes=5),
    )
    definitions = build_session_levels(
        session_date=SESSION, market_open=OPEN_TIME,
        previous_day=previous, premarket=premarket, opening=opening,
    )
    assert len(definitions) == 7
    availability = {item.level_type: item.available_from_timestamp for item in definitions}
    assert availability[LevelType.PDH] == OPEN_TIME
    assert availability[LevelType.PMH] == OPEN_TIME
    assert availability[LevelType.ORH5] == OPEN_TIME + timedelta(minutes=5)


def test_mixed_session_rejected() -> None:
    next_day = candle(
        datetime(2026, 8, 20, 13, 30, tzinfo=UTC),
        session_date=date(2026, 8, 20),
    )
    with pytest.raises(InteractionInputError, match="mix"):
        classify_session_level_interactions((candle(), next_day), (level(),))


def test_duplicate_timestamp_rejected() -> None:
    value = candle()
    with pytest.raises(InteractionInputError, match="Duplicate"):
        classify_session_level_interactions((value, value), (level(),))


def test_out_of_order_rejected() -> None:
    later = candle(OPEN_TIME + timedelta(minutes=5))
    with pytest.raises(InteractionInputError, match="chronological"):
        classify_session_level_interactions((later, candle()), (level(),))


@pytest.mark.parametrize(
    ("field", "value"),
    (("timeframe", "1Min"), ("session_mode", "ALL")),
)
def test_wrong_timeframe_or_session_mode_rejected(field, value) -> None:
    original = candle()
    wrong = FiveMinuteBar.model_construct(**{**original.model_dump(), field: value})
    with pytest.raises(InteractionInputError, match="RTH_ONLY 5Min"):
        classify_session_level_interactions((wrong,), (level(),))


def test_level_session_mismatch_rejected() -> None:
    with pytest.raises(InteractionInputError, match="Level session"):
        classify_session_level_interactions(
            (candle(),),
            (level(session_date=date(2026, 8, 18)),),
        )


def test_inputs_are_not_mutated() -> None:
    values = [candle(), candle(OPEN_TIME + timedelta(minutes=5))]
    definition = level()
    before_bars = [item.model_dump() for item in values]
    before_level = definition.model_dump()
    classify_session_level_interactions(values, (definition,), emit_no_interaction=True)
    assert [item.model_dump() for item in values] == before_bars
    assert definition.model_dump() == before_level


def test_no_lookahead_prefix_matches_full_session_at_t() -> None:
    values = (
        candle(),
        candle(
            OPEN_TIME + timedelta(minutes=5), open_price="99", high="102",
            low="98", close="101",
        ),
        candle(
            OPEN_TIME + timedelta(minutes=10), open_price="101", high="110",
            low="90", close="99",
        ),
    )
    prefix = classify_session_level_interactions(values[:2], (level(),), emit_no_interaction=True)
    full = classify_session_level_interactions(values, (level(),), emit_no_interaction=True)
    full_at_t = tuple(item for item in full if item.candle_timestamp <= values[1].timestamp)
    assert prefix == full_at_t


def test_default_sequence_output_emits_only_actual_interactions() -> None:
    values = (
        candle(open_price="99", high="99.9", low="98", close="99"),
        candle(OPEN_TIME + timedelta(minutes=5)),
    )
    records = classify_session_level_interactions(values, (level(),))
    assert len(records) == 1
    assert records[0].interaction_type is not InteractionType.NO_INTERACTION


def test_completion_timestamp_and_touch_fact_are_explicit() -> None:
    result = classify(candle(high="100", low="98", close="99"))
    assert result.candle_completed_at == result.candle_timestamp + timedelta(minutes=5)
    assert result.range_encountered and result.touched_level


def test_local_pure_path_never_calls_network_or_writes(monkeypatch, tmp_path) -> None:
    def reject_network(*args, **kwargs):
        raise AssertionError("interaction classification must remain offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    classify_session_level_interactions((candle(),), (level(),))
    assert list(tmp_path.iterdir()) == []


def test_cli_is_offline_and_nonpersistent(monkeypatch, tmp_path, capsys) -> None:
    interaction = classify(candle())
    counts = tuple(
        InteractionCount(
            level_type=level_type,
            interaction_type=interaction_type,
            count=(
                1
                if level_type is LevelType.PDH
                and interaction_type is interaction.interaction_type
                else 0
            ),
        )
        for level_type in LevelType
        for interaction_type in InteractionType
    )
    result = LevelInteractionResult(
        start_date=SESSION,
        end_date=SESSION,
        eligible_pair_count=1,
        no_interaction_count=0,
        interactions=(interaction,),
        counts=counts,
    )

    def fake_calculate(self, *, start, end):
        return result

    def reject_network(*args, **kwargs):
        raise AssertionError("level-interactions must remain offline")

    monkeypatch.setattr(LevelInteractionService, "calculate", fake_calculate)
    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "level-interactions",
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
    assert captured.err == ""
    assert "SPY LEVEL INTERACTIONS" in captured.out
    assert "Interaction summary" in captured.out
    assert "Status: PASS" in captured.out
    assert list(tmp_path.iterdir()) == []
