from __future__ import annotations

import socket
from datetime import UTC, date, datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from spy_research.cli import main
from spy_research.config import load_research_config
from spy_research.data.schemas import RawBarRecord
from spy_research.levels import (
    MissingPreviousDaySource,
    PreviousDayLevelInputError,
    PreviousDayLevelsResult,
    PreviousDayLevelsService,
    PreviousDayLevelValidationError,
    calculate_previous_session_levels,
    map_source_levels_to_next_session,
    next_xnys_session_date,
)
from spy_research.market import XNYSCalendar


def bar(
    timestamp: datetime,
    *,
    high: str = "101",
    low: str = "99",
    close: str = "100",
) -> RawBarRecord:
    return RawBarRecord(
        symbol="SPY",
        timestamp=timestamp,
        open=Decimal("100"),
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


def normal_bars() -> tuple[RawBarRecord, ...]:
    return (
        bar(datetime(2026, 8, 3, 13, 30, tzinfo=UTC), high="101.1", low="99.4"),
        bar(
            datetime(2026, 8, 3, 13, 31, tzinfo=UTC),
            high="102.123456789012",
            low="98.765432109876",
        ),
        bar(
            datetime(2026, 8, 3, 19, 59, tzinfo=UTC),
            high="102.123456789012",
            low="98.765432109876",
            close="100.987654321098",
        ),
    )


class FakeStore:
    def __init__(self, partitions):
        self.partitions = partitions
        self.loaded = []

    def load_partition(self, session_date):
        self.loaded.append(session_date)
        return self.partitions.get(session_date, ())


class PassingValidator:
    def validate_raw_bars(self, *args, **kwargs):
        return SimpleNamespace(passed=True, issues=())


def service(store, *, validator=None):
    return PreviousDayLevelsService(
        load_research_config(),
        store,
        validator=validator or PassingValidator(),
    )


def test_pdh_pdl_and_pdc_use_high_low_and_final_close() -> None:
    result = calculate_previous_session_levels(normal_bars())
    assert result.pdh == Decimal("102.123456789012")
    assert result.pdl == Decimal("98.765432109876")
    assert result.pdc == Decimal("100.987654321098")
    assert result.pdc_source_timestamp == datetime(2026, 8, 3, 19, 59, tzinfo=UTC)


def test_equal_high_and_low_ties_choose_earliest_timestamp() -> None:
    result = calculate_previous_session_levels(normal_bars())
    expected = datetime(2026, 8, 3, 13, 31, tzinfo=UTC)
    assert result.pdh_source_timestamp == expected
    assert result.pdl_source_timestamp == expected


def test_decimal_precision_and_input_are_preserved() -> None:
    values = list(normal_bars())
    before = [item.model_dump() for item in values]
    result = calculate_previous_session_levels(values)
    assert result.pdh == Decimal("102.123456789012")
    assert result.pdl == Decimal("98.765432109876")
    assert result.pdc == Decimal("100.987654321098")
    assert [item.model_dump() for item in values] == before


def test_result_is_immutable_and_auditable() -> None:
    result = calculate_previous_session_levels(normal_bars())
    assert result.timeframe_source == "1Min"
    assert result.source_session == "RTH"
    assert result.level_version == "previous-day-levels-v1"
    with pytest.raises(ValidationError):
        result.pdh = Decimal("999")


def test_duplicate_timestamps_are_rejected() -> None:
    first = normal_bars()[0]
    with pytest.raises(PreviousDayLevelInputError, match="Duplicate"):
        calculate_previous_session_levels((first, first))


def test_out_of_order_bars_are_rejected() -> None:
    values = normal_bars()
    with pytest.raises(PreviousDayLevelInputError, match="chronological"):
        calculate_previous_session_levels((values[1], values[0]))


def test_mixed_session_dates_are_rejected() -> None:
    mixed = bar(datetime(2026, 8, 4, 13, 30, tzinfo=UTC))
    with pytest.raises(PreviousDayLevelInputError, match="mix"):
        calculate_previous_session_levels((normal_bars()[0], mixed))


def test_non_rth_bar_is_rejected() -> None:
    premarket = bar(datetime(2026, 8, 3, 13, 29, tzinfo=UTC))
    with pytest.raises(PreviousDayLevelInputError, match="only XNYS RTH"):
        calculate_previous_session_levels((premarket,))


@pytest.mark.parametrize(
    ("field", "value"),
    (("symbol", "QQQ"), ("timeframe", "5Min")),
)
def test_wrong_symbol_or_timeframe_is_rejected(field, value) -> None:
    original = normal_bars()[0]
    wrong = RawBarRecord.model_construct(**{**original.model_dump(), field: value})
    with pytest.raises(PreviousDayLevelInputError, match="raw 1Min"):
        calculate_previous_session_levels((wrong,))


def test_monday_maps_to_friday() -> None:
    assert next_xnys_session_date(date(2026, 7, 31)) == date(2026, 8, 3)


def test_exchange_holiday_is_skipped() -> None:
    assert next_xnys_session_date(date(2026, 7, 2)) == date(2026, 7, 6)


def test_early_close_uses_actual_final_rth_minute_and_maps_forward() -> None:
    calendar = XNYSCalendar()
    session = calendar.session_for_date(date(2026, 11, 27))
    assert session.is_early_close
    values = (
        bar(datetime(2026, 11, 27, 14, 30, tzinfo=UTC), close="100"),
        bar(datetime(2026, 11, 27, 17, 59, tzinfo=UTC), close="101.25"),
    )
    source = calculate_previous_session_levels(values, calendar=calendar)
    mapped = map_source_levels_to_next_session(source, calendar=calendar)
    assert source.pdc == Decimal("101.25")
    assert source.pdc_source_timestamp == datetime(2026, 11, 27, 17, 59, tzinfo=UTC)
    assert mapped.session_date == date(2026, 11, 30)


def test_first_requested_date_automatically_loads_prior_session() -> None:
    fake = FakeStore({date(2026, 8, 3): normal_bars()})
    result = service(fake).calculate(start=date(2026, 8, 4), end=date(2026, 8, 4))
    assert fake.loaded == [date(2026, 8, 3)]
    assert result.levels[0].session_date == date(2026, 8, 4)
    assert result.levels[0].source_session_date == date(2026, 8, 3)


def test_current_session_partition_is_never_loaded_or_used() -> None:
    source = normal_bars()
    target = (
        bar(datetime(2026, 8, 4, 13, 30, tzinfo=UTC), high="999", low="1", close="500"),
    )
    fake = FakeStore({date(2026, 8, 3): source, date(2026, 8, 4): target})
    result = service(fake).calculate(start=date(2026, 8, 4), end=date(2026, 8, 4))
    assert fake.loaded == [date(2026, 8, 3)]
    assert result.levels[0].pdh == Decimal("102.123456789012")
    assert result.levels[0].pdl == Decimal("98.765432109876")
    assert result.levels[0].pdc == Decimal("100.987654321098")


def test_prefix_no_lookahead_result_is_unchanged_by_target_data() -> None:
    first_store = FakeStore({date(2026, 8, 3): normal_bars()})
    second_store = FakeStore(
        {
            date(2026, 8, 3): normal_bars(),
            date(2026, 8, 4): (
                bar(datetime(2026, 8, 4, 13, 30, tzinfo=UTC), high="999", low="1"),
            ),
        }
    )
    first = service(first_store).calculate(start=date(2026, 8, 4), end=date(2026, 8, 4))
    second = service(second_store).calculate(start=date(2026, 8, 4), end=date(2026, 8, 4))
    assert first == second


def test_validation_failure_blocks_level_creation() -> None:
    fake = FakeStore({date(2026, 8, 3): normal_bars()})
    failing = SimpleNamespace(
        validate_raw_bars=lambda *args, **kwargs: SimpleNamespace(
            passed=False,
            issues=(SimpleNamespace(code="MISSING_RTH_MINUTES", severity="ERROR"),),
        )
    )
    with pytest.raises(PreviousDayLevelValidationError, match="MISSING_RTH_MINUTES"):
        service(fake, validator=failing).calculate(
            start=date(2026, 8, 4), end=date(2026, 8, 4)
        )


def test_missing_prior_session_is_explicit_and_not_fabricated() -> None:
    result = service(FakeStore({})).calculate(
        start=date(2026, 8, 3), end=date(2026, 8, 3)
    )
    assert result.levels == ()
    assert result.missing_sources == (
        MissingPreviousDaySource(
            session_date=date(2026, 8, 3),
            source_session_date=date(2026, 7, 31),
        ),
    )


def test_weekend_dates_in_requested_range_are_not_targets() -> None:
    fake = FakeStore({date(2026, 8, 7): normal_bars()})
    result = service(fake).calculate(start=date(2026, 8, 8), end=date(2026, 8, 9))
    assert result.levels == ()
    assert result.missing_sources == ()
    assert fake.loaded == []


def test_local_service_path_never_calls_network(monkeypatch) -> None:
    def reject_network(*args, **kwargs):
        raise AssertionError("local previous-day level calculation must remain offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    fake = FakeStore({date(2026, 8, 3): normal_bars()})
    result = service(fake).calculate(start=date(2026, 8, 4), end=date(2026, 8, 4))
    assert len(result.levels) == 1


def test_cli_is_offline_nonpersistent_and_reports_missing(monkeypatch, tmp_path, capsys) -> None:
    result = PreviousDayLevelsResult(
        symbol="SPY",
        start_date=date(2026, 8, 3),
        end_date=date(2026, 8, 3),
        levels=(),
        missing_sources=(
            MissingPreviousDaySource(
                session_date=date(2026, 8, 3),
                source_session_date=date(2026, 7, 31),
            ),
        ),
    )

    def fake_calculate(self, *, start, end):
        return result

    def reject_network(*args, **kwargs):
        raise AssertionError("previous-day-levels must remain offline")

    monkeypatch.setattr(PreviousDayLevelsService, "calculate", fake_calculate)
    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "previous-day-levels",
            "--start",
            "2026-08-03",
            "--end",
            "2026-08-03",
            "--raw-data-root",
            str(tmp_path),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.err == ""
    assert "SPY PREVIOUS-DAY LEVELS" in captured.out
    assert "2026-08-03 requires 2026-07-31" in captured.out
    assert "Status: INCOMPLETE" in captured.out
    assert list(tmp_path.iterdir()) == []
