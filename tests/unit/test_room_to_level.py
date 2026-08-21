from __future__ import annotations

import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

import spy_research.cli as cli_module
from spy_research.interactions import (
    AvailableLevel,
    ImmediateState,
    InteractionType,
    LevelType,
    RetestState,
)
from spy_research.strategy import (
    BasePriceActionCandidate,
    BaseSetupStatus,
    ConfirmationType,
    SetupDirection,
)
from spy_research.strategy.comparisons import (
    NextLevelAvailability,
    RoomBucket,
    RoomToLevelComparisonService,
    room_bucket,
    select_room_to_next_level,
)


SESSION = date(2026, 8, 19)
CONFIRMATION = datetime(2026, 8, 19, 14, 0, tzinfo=UTC)
SIGNAL = CONFIRMATION + timedelta(minutes=5)


def setup(
    direction: SetupDirection = SetupDirection.LONG,
    *,
    level_type: LevelType = LevelType.ORL5,
    confirmation: datetime = CONFIRMATION,
    identity: str = "setup",
) -> BasePriceActionCandidate:
    signal = confirmation + timedelta(minutes=5)
    return BasePriceActionCandidate(
        setup_identity=identity,
        break_interaction_identity=f"break-{identity}",
        follow_through_identity=f"follow-{identity}",
        session_date=confirmation.date(),
        level_type=level_type,
        level_price=Decimal("100"),
        direction=direction,
        break_interaction_type=(
            InteractionType.CLOSE_THROUGH_ABOVE
            if direction is SetupDirection.LONG
            else InteractionType.CLOSE_THROUGH_BELOW
        ),
        break_timestamp=confirmation - timedelta(minutes=5),
        break_completed_at=confirmation,
        exact_immediate_state=ImmediateState.HOLD,
        exact_retest_state=RetestState.NO_RETEST,
        status=BaseSetupStatus.CONFIRMED,
        confirmation_type=ConfirmationType.IMMEDIATE_HOLD,
        confirmation_bar_timestamp=confirmation,
        signal_known_at=signal,
        earliest_entry_timestamp=signal,
        same_session_executable=True,
    )


def level(
    level_type: LevelType,
    price: str,
    *,
    available: datetime = SIGNAL,
) -> AvailableLevel:
    return AvailableLevel(
        session_date=SESSION,
        level_type=level_type,
        level_price=Decimal(price),
        available_from_timestamp=available,
    )


def measure(
    direction=SetupDirection.LONG,
    *,
    levels=(),
    confirmation_price="101",
    entry_price="101.1",
    atr="2",
    level_type=LevelType.ORL5,
):
    return select_room_to_next_level(
        setup(direction, level_type=level_type),
        confirmation_price=Decimal(confirmation_price),
        entry_price=Decimal(entry_price) if entry_price is not None else None,
        atr14=Decimal(atr) if atr is not None else None,
        levels=levels,
    )


def test_long_selects_nearest_strictly_above() -> None:
    result = measure(
        levels=(
            level(LevelType.PDL, "99"),
            level(LevelType.PMH, "103"),
            level(LevelType.PDH, "102"),
        )
    )
    assert result.next_level_price == Decimal("102")
    assert result.next_level_types == (LevelType.PDH,)
    assert result.room_from_confirmation == Decimal("1")
    assert result.room_from_entry_reference == Decimal("0.9")
    assert result.number_of_known_levels_above == 2
    assert result.number_of_known_levels_below == 1


def test_short_selects_nearest_strictly_below() -> None:
    result = measure(
        SetupDirection.SHORT,
        confirmation_price="99",
        entry_price="98.9",
        levels=(
            level(LevelType.PDL, "97"),
            level(LevelType.PML, "98"),
            level(LevelType.PDH, "102"),
        ),
    )
    assert result.next_level_price == Decimal("98")
    assert result.next_level_types == (LevelType.PML,)
    assert result.room_from_confirmation == Decimal("1")
    assert result.room_from_entry_reference == Decimal("0.9")


def test_equality_and_triggering_level_are_excluded() -> None:
    result = measure(
        confirmation_price="101",
        level_type=LevelType.PDH,
        levels=(
            level(LevelType.PDC, "101"),
            level(LevelType.PDH, "102"),
            level(LevelType.PMH, "103"),
        ),
    )
    assert result.next_level_price == Decimal("103")
    assert result.next_level_types == (LevelType.PMH,)
    assert result.number_of_known_levels_above == 2


def test_every_level_type_tied_at_triggering_price_is_excluded() -> None:
    result = measure(
        confirmation_price="99",
        level_type=LevelType.PDH,
        levels=(
            level(LevelType.PDH, "100"),
            level(LevelType.PMH, "100"),
            level(LevelType.ORH5, "102"),
        ),
    )
    assert result.next_level_price == Decimal("102")
    assert result.next_level_types == (LevelType.ORH5,)


def test_tied_nearest_level_types_are_preserved_in_enum_order() -> None:
    result = measure(
        levels=(
            level(LevelType.ORH5, "102"),
            level(LevelType.PMH, "102"),
            level(LevelType.PDH, "102"),
        )
    )
    assert result.next_level_types == (
        LevelType.PDH,
        LevelType.PMH,
        LevelType.ORH5,
    )


def test_level_availability_uses_signal_known_at_cutoff() -> None:
    result = measure(
        levels=(
            level(LevelType.ORH5, "101.5", available=SIGNAL + timedelta(seconds=1)),
            level(LevelType.PDH, "103", available=SIGNAL),
        )
    )
    assert result.next_level_price == Decimal("103")
    assert result.known_level_count == 1


def test_next_session_level_is_never_carried_backward() -> None:
    next_session = AvailableLevel(
        session_date=SESSION + timedelta(days=1),
        level_type=LevelType.ORH5,
        level_price=Decimal("101.5"),
        available_from_timestamp=SIGNAL,
    )
    result = measure(
        levels=(next_session, level(LevelType.PDH, "103")),
    )
    assert result.next_level_price == Decimal("103")
    assert result.known_level_count == 1


def test_opening_range_is_eligible_at_exact_0935_availability() -> None:
    confirmation = datetime(2026, 8, 19, 13, 30, tzinfo=UTC)
    item = setup(confirmation=confirmation)
    available = confirmation + timedelta(minutes=5)
    result = select_room_to_next_level(
        item,
        confirmation_price=Decimal("101"),
        entry_price=None,
        atr14=Decimal("1"),
        levels=(level(LevelType.ORH5, "102", available=available),),
    )
    assert result.next_level_types == (LevelType.ORH5,)


def test_missing_previous_day_levels_do_not_fabricate_values() -> None:
    result = measure(levels=(level(LevelType.PMH, "102"),))
    assert result.known_level_count == 1
    assert result.next_level_types == (LevelType.PMH,)


def test_no_directional_level_is_open_ended() -> None:
    result = measure(levels=(level(LevelType.PDL, "99"),))
    assert result.next_level_availability is NextLevelAvailability.OPEN_ENDED
    assert result.next_level_price is None
    assert result.room_from_confirmation is None
    assert result.room_bucket is RoomBucket.OPEN_ENDED


def test_atr_normalization_and_unavailable_atr_are_exact() -> None:
    levels = (level(LevelType.PDH, "102"),)
    available = measure(levels=levels, atr="2")
    assert available.room_in_atr == Decimal("0.5")
    assert available.room_bucket is RoomBucket.ATR_0_5_TO_1_0
    unavailable = measure(levels=levels, atr=None)
    assert unavailable.room_in_atr is None
    assert unavailable.room_bucket is RoomBucket.UNAVAILABLE_ATR
    assert unavailable.directional_level_count_within_0_5_atr is None


@pytest.mark.parametrize(
    "value, expected",
    (
        ("0", RoomBucket.LT_0_5_ATR),
        ("0.4999", RoomBucket.LT_0_5_ATR),
        ("0.5", RoomBucket.ATR_0_5_TO_1_0),
        ("1.0", RoomBucket.ATR_1_0_TO_1_5),
        ("1.5", RoomBucket.ATR_1_5_TO_2_0),
        ("2.0", RoomBucket.ATR_2_0_TO_3_0),
        ("3.0", RoomBucket.ATR_2_0_TO_3_0),
        ("3.0001", RoomBucket.GT_3_0_ATR),
    ),
)
def test_fixed_half_open_bucket_boundaries(value, expected) -> None:
    assert room_bucket(Decimal(value), NextLevelAvailability.AVAILABLE) is expected


def test_stacked_directional_counts_use_inclusive_fixed_atr_distances() -> None:
    result = measure(
        atr="2",
        levels=(
            level(LevelType.PDH, "101.5"),
            level(LevelType.PMH, "102"),
            level(LevelType.PDC, "103"),
            level(LevelType.PDL, "99"),
        ),
    )
    assert result.directional_level_count_within_0_5_atr == 2
    assert result.directional_level_count_within_1_0_atr == 3


def test_entry_price_cannot_change_level_selection() -> None:
    levels = (level(LevelType.PDH, "102"), level(LevelType.PMH, "104"))
    first = measure(levels=levels, entry_price="101.1")
    second = measure(levels=levels, entry_price="103")
    assert first.next_level_price == second.next_level_price == Decimal("102")
    assert first.room_from_confirmation == second.room_from_confirmation
    assert first.room_from_entry_reference != second.room_from_entry_reference


def test_annotation_is_immutable_and_contains_no_filter() -> None:
    result = measure(levels=(level(LevelType.PDH, "102"),))
    with pytest.raises(ValidationError):
        result.room_bucket = RoomBucket.OPEN_ENDED
    forbidden = {"qualified", "filter", "score", "target", "stop"}
    assert forbidden.isdisjoint(type(result).model_fields)


def test_exactly_142_setups_can_be_measured_without_outcomes() -> None:
    levels = (level(LevelType.PDH, "102"),)
    results = tuple(
        select_room_to_next_level(
            setup(identity=f"setup-{index:03}"),
            confirmation_price=Decimal("101"),
            entry_price=None,
            atr14=Decimal("2"),
            levels=levels,
        )
        for index in range(142)
    )
    assert len(results) == 142
    assert len({item.setup_identity for item in results}) == 142


def test_cli_is_offline_and_nonpersistent(monkeypatch, tmp_path, capsys) -> None:
    sentinel = object()

    def reject_network(*args, **kwargs):
        raise AssertionError("Stage 11.2 must remain offline")

    def mocked_calculate(self, *, start, end):
        assert start == end == SESSION
        return sentinel

    def mocked_print(result):
        assert result is sentinel
        print("room-to-level-pass")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    monkeypatch.setattr(RoomToLevelComparisonService, "calculate", mocked_calculate)
    monkeypatch.setattr(cli_module, "_print_room_to_level_comparison", mocked_print)
    exit_code = cli_module.main(
        [
            "compare-room-to-next-level",
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
    assert captured.out == "room-to-level-pass\n"
    assert captured.err == ""
    assert list(tmp_path.iterdir()) == []
