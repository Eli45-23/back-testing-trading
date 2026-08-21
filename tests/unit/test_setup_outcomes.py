from __future__ import annotations

import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from spy_research.cli import main
from spy_research.data.schemas import RawBarRecord
from spy_research.interactions import (
    ImmediateState,
    InteractionType,
    LevelType,
    RetestState,
)
from spy_research.strategy import (
    BasePriceActionCandidate,
    BaseSetupStatus,
    ConfirmationType,
    EntryStatus,
    SetupDirection,
    SetupEntryReference,
    SetupOutcomeInputError,
    SetupOutcomeResult,
    SetupOutcomeService,
    calculate_setup_outcomes,
    select_entry_reference,
)


SESSION = date(2026, 8, 19)
SIGNAL = datetime(2026, 8, 19, 14, 10, tzinfo=UTC)
CLOSE = datetime(2026, 8, 19, 20, 0, tzinfo=UTC)


def setup(
    direction: SetupDirection = SetupDirection.LONG,
    *,
    signal: datetime = SIGNAL,
    executable: bool = True,
    status: BaseSetupStatus = BaseSetupStatus.CONFIRMED,
) -> BasePriceActionCandidate:
    confirmed = status is BaseSetupStatus.CONFIRMED
    return BasePriceActionCandidate(
        setup_identity=f"setup-{direction.value}-{signal.isoformat()}",
        break_interaction_identity="break-1",
        follow_through_identity="follow-1",
        session_date=signal.astimezone(UTC).date(),
        level_type=LevelType.PDH,
        level_price=Decimal("100.00"),
        direction=direction,
        break_interaction_type=(
            InteractionType.CLOSE_THROUGH_ABOVE
            if direction is SetupDirection.LONG
            else InteractionType.CLOSE_THROUGH_BELOW
        ),
        break_timestamp=signal - timedelta(minutes=10),
        break_completed_at=signal - timedelta(minutes=5),
        exact_immediate_state=ImmediateState.HOLD,
        exact_retest_state=RetestState.NO_RETEST,
        status=status,
        confirmation_type=ConfirmationType.IMMEDIATE_HOLD if confirmed else None,
        confirmation_bar_timestamp=signal - timedelta(minutes=5) if confirmed else None,
        signal_known_at=signal if confirmed else None,
        earliest_entry_timestamp=signal if confirmed else None,
        same_session_executable=executable,
    )


def minute(
    timestamp: datetime,
    *,
    open_price: str = "100.123456789012",
    high: str = "101",
    low: str = "99",
    close: str = "100",
) -> RawBarRecord:
    return RawBarRecord(
        symbol="SPY",
        timestamp=timestamp,
        open=Decimal(open_price),
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


def sequence(count: int, *, start: datetime = SIGNAL) -> tuple[RawBarRecord, ...]:
    return tuple(
        minute(
            start + timedelta(minutes=index),
            open_price="100",
            high=str(101 + index),
            low=str(99 - index),
        )
        for index in range(count)
    )


def test_exact_timestamp_selects_exact_open_with_decimal_precision() -> None:
    bars = (minute(SIGNAL - timedelta(minutes=1)), minute(SIGNAL))
    entry = select_entry_reference(setup(), bars)
    assert entry.entry_reference_timestamp == SIGNAL
    assert entry.entry_reference_price == Decimal("100.123456789012")
    assert entry.entry_delay_minutes == 0


def test_first_bar_at_or_after_signal_records_delay_and_ignores_favorable_later_bar(
) -> None:
    bars = (
        minute(SIGNAL + timedelta(minutes=2), open_price="105"),
        minute(SIGNAL + timedelta(minutes=3), open_price="90"),
    )
    entry = select_entry_reference(setup(), bars)
    assert entry.entry_reference_timestamp == SIGNAL + timedelta(minutes=2)
    assert entry.entry_reference_price == Decimal("105")
    assert entry.entry_delay_minutes == 2


def test_entry_selection_is_deterministic_and_does_not_mutate_input() -> None:
    bars = list(sequence(3))
    before = tuple(item.model_dump() for item in bars)
    assert select_entry_reference(setup(), bars) == select_entry_reference(
        setup(), bars
    )
    assert tuple(item.model_dump() for item in bars) == before


def test_nonconfirmed_setup_is_rejected() -> None:
    with pytest.raises(SetupOutcomeInputError, match="Only confirmed"):
        select_entry_reference(setup(status=BaseSetupStatus.NO_RETEST), sequence(2))


def test_session_end_setup_has_explicit_no_entry() -> None:
    item = setup(signal=CLOSE, executable=False)
    entry = select_entry_reference(item, ())
    outcome = calculate_setup_outcomes(item, entry, (), CLOSE)
    assert entry.entry_status is EntryStatus.ENTRY_UNAVAILABLE_SESSION_END
    assert entry.entry_reference_price is None
    assert outcome.five is None and outcome.eod is None


def test_missing_same_session_entry_is_explicit_and_never_bridges_overnight() -> None:
    item = setup(signal=CLOSE - timedelta(minutes=1))
    entry = select_entry_reference(item, ())
    assert entry.entry_status is EntryStatus.ENTRY_REFERENCE_MISSING
    assert entry.entry_reference_timestamp is None


@pytest.mark.parametrize(
    "bad_bars, message",
    (
        ((minute(datetime(2026, 8, 20, 14, 10, tzinfo=UTC)),), "wrong setup session"),
        ((minute(datetime(2026, 8, 19, 12, 0, tzinfo=UTC)),), "RTH"),
        ((minute(SIGNAL), minute(SIGNAL)), "Duplicate"),
        ((minute(SIGNAL + timedelta(minutes=1)), minute(SIGNAL)), "chronological"),
    ),
)
def test_wrong_session_duplicate_and_ordered_inputs_are_rejected(
    bad_bars, message
) -> None:
    with pytest.raises(SetupOutcomeInputError, match=message):
        select_entry_reference(setup(), bad_bars)


def test_wrong_provenance_is_rejected_even_if_constructed_without_schema_validation(
) -> None:
    bad = minute(SIGNAL).model_copy(update={"timeframe": "5Min"})
    with pytest.raises(SetupOutcomeInputError, match="raw 1Min"):
        select_entry_reference(setup(), (bad,))


def test_entry_reference_model_rejects_pre_signal_and_inconsistent_delay() -> None:
    with pytest.raises(ValidationError, match="cannot precede"):
        SetupEntryReference(
            setup_identity="x",
            session_date=SESSION,
            direction=SetupDirection.LONG,
            signal_known_at=SIGNAL,
            earliest_entry_timestamp=SIGNAL,
            entry_status=EntryStatus.AVAILABLE,
            entry_reference_timestamp=SIGNAL - timedelta(minutes=1),
            entry_reference_price=Decimal("100"),
            entry_delay_minutes=0,
        )


@pytest.mark.parametrize(
    "direction, expected_mfe, expected_mae",
    (
        (SetupDirection.LONG, Decimal("5"), Decimal("5")),
        (SetupDirection.SHORT, Decimal("5"), Decimal("5")),
    ),
)
def test_five_minute_long_and_short_math(direction, expected_mfe, expected_mae) -> None:
    item = setup(direction)
    bars = sequence(65)
    outcome = calculate_setup_outcomes(
        item, select_entry_reference(item, bars), bars, CLOSE
    )
    assert outcome.five is not None
    assert outcome.five.mfe == expected_mfe
    assert outcome.five.mae == expected_mae
    assert outcome.five.available_minutes == 5
    assert outcome.five.complete


def test_all_fixed_windows_and_eod_use_exact_entry_inclusive_minute_counts() -> None:
    item = setup()
    bars = sequence(65)
    outcome = calculate_setup_outcomes(
        item, select_entry_reference(item, bars), bars, SIGNAL + timedelta(minutes=65)
    )
    assert [
        (value.requested_minutes, value.available_minutes, value.mfe, value.mae)
        for value in (
            outcome.five,
            outcome.fifteen,
            outcome.thirty,
            outcome.sixty,
            outcome.eod,
        )
        if value is not None
    ] == [
        (5, 5, Decimal("5"), Decimal("5")),
        (15, 15, Decimal("15"), Decimal("15")),
        (30, 30, Decimal("30"), Decimal("30")),
        (60, 60, Decimal("60"), Decimal("60")),
        (65, 65, Decimal("65"), Decimal("65")),
    ]


def test_entry_minute_high_and_low_participate() -> None:
    item = setup()
    bars = (
        minute(SIGNAL, open_price="100", high="110", low="90"),
        *sequence(4, start=SIGNAL + timedelta(minutes=1)),
    )
    outcome = calculate_setup_outcomes(
        item, select_entry_reference(item, bars), bars, CLOSE
    )
    assert outcome.five is not None
    assert outcome.five.mfe == Decimal("10")
    assert outcome.five.mae == Decimal("10")
    assert outcome.five.mfe_timestamp == SIGNAL
    assert outcome.five.mae_timestamp == SIGNAL


def test_tied_extremes_preserve_earliest_timestamp() -> None:
    item = setup()
    bars = tuple(
        minute(
            SIGNAL + timedelta(minutes=i),
            open_price="100",
            high="102",
            low="98",
        )
        for i in range(5)
    )
    outcome = calculate_setup_outcomes(
        item, select_entry_reference(item, bars), bars, CLOSE
    )
    assert outcome.five is not None
    assert outcome.five.mfe_timestamp == SIGNAL
    assert outcome.five.mae_timestamp == SIGNAL


def test_nonnegative_clamp_when_no_favorable_or_adverse_excursion() -> None:
    item = setup()
    bars = tuple(
        minute(
            SIGNAL + timedelta(minutes=i),
            open_price="100",
            high="99",
            low="101",
        )
        for i in range(5)
    )
    outcome = calculate_setup_outcomes(
        item, select_entry_reference(item, bars), bars, CLOSE
    )
    assert outcome.five is not None
    assert outcome.five.mfe == Decimal("0")
    assert outcome.five.mae == Decimal("0")


def test_near_close_windows_compute_available_minutes_without_overnight_bridge(
) -> None:
    signal = CLOSE - timedelta(minutes=2)
    item = setup(signal=signal)
    bars = sequence(2, start=signal)
    outcome = calculate_setup_outcomes(
        item, select_entry_reference(item, bars), bars, CLOSE
    )
    fixed = (outcome.five, outcome.fifteen, outcome.thirty, outcome.sixty)
    assert all(value is not None and not value.complete for value in fixed)
    assert all(value is not None and value.available_minutes == 2 for value in fixed)
    assert outcome.eod is not None and outcome.eod.complete
    assert outcome.eod.available_minutes == 2


@pytest.mark.parametrize("attribute", ("five", "fifteen", "thirty", "sixty"))
def test_later_minutes_cannot_change_completed_fixed_horizons(attribute) -> None:
    item = setup()
    bars = sequence(70)
    baseline = calculate_setup_outcomes(
        item, select_entry_reference(item, bars), bars, CLOSE
    )
    changed = list(bars)
    changed[-1] = minute(
        changed[-1].timestamp,
        open_price="100",
        high="9999",
        low="1",
    )
    extended = calculate_setup_outcomes(
        item, select_entry_reference(item, changed), changed, CLOSE
    )
    assert getattr(baseline, attribute) == getattr(extended, attribute)


def test_entry_price_must_match_raw_open() -> None:
    item = setup()
    bars = sequence(5)
    entry = select_entry_reference(item, bars).model_copy(
        update={"entry_reference_price": Decimal("999")}
    )
    with pytest.raises(SetupOutcomeInputError, match="does not match"):
        calculate_setup_outcomes(item, entry, bars, CLOSE)


def test_pure_functions_are_offline_and_nonpersistent(monkeypatch, tmp_path) -> None:
    def reject_network(*args, **kwargs):
        raise AssertionError("Stage 9.2 pure functions must stay offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    item = setup()
    bars = sequence(5)
    calculate_setup_outcomes(item, select_entry_reference(item, bars), bars, CLOSE)
    assert list(tmp_path.iterdir()) == []


def test_cli_is_offline_read_only_and_reports_reconciliation(
    monkeypatch, tmp_path, capsys
) -> None:
    item = setup()
    bars = sequence(5)
    outcome = calculate_setup_outcomes(
        item, select_entry_reference(item, bars), bars, CLOSE
    )

    def mocked_calculate(self, *, start, end):
        return SetupOutcomeResult(
            start_date=start,
            end_date=end,
            confirmed_setup_count=1,
            available_entry_count=1,
            session_end_unavailable_count=0,
            missing_entry_count=0,
            outcomes=(outcome,),
        )

    def reject_network(*args, **kwargs):
        raise AssertionError("base-setup-outcomes CLI must remain offline")

    monkeypatch.setattr(SetupOutcomeService, "calculate", mocked_calculate)
    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "base-setup-outcomes",
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
    assert "confirmed: 1  entries: 1" in captured.out
    assert "5m: complete=1 incomplete=0" in captured.out
    assert "not a guaranteed live fill" in captured.out
    assert "not realized P/L" in captured.out
    assert captured.err == ""
    assert list(tmp_path.iterdir()) == []
