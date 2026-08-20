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
    PremarketLevelInputError,
    PremarketLevels,
    PremarketLevelsResult,
    PremarketLevelsService,
    PremarketLevelUnavailableError,
    PremarketLevelValidationError,
    calculate_premarket_levels,
)


SESSION_DATE = date(2026, 8, 19)


def bar(
    timestamp: datetime,
    *,
    high: str = "101",
    low: str = "99",
) -> RawBarRecord:
    return RawBarRecord(
        symbol="SPY",
        timestamp=timestamp,
        open=Decimal("100"),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal("100"),
        volume=100,
        trade_count=10,
        vwap=Decimal("100"),
        source="alpaca",
        feed="sip",
        timeframe="1Min",
        adjustment="raw",
    )


def premarket_bars() -> tuple[RawBarRecord, ...]:
    return (
        bar(
            datetime(2026, 8, 19, 8, 0, tzinfo=UTC),
            high="101.123456789012",
            low="98.876543210987",
        ),
        bar(
            datetime(2026, 8, 19, 9, 0, tzinfo=UTC),
            high="102.123456789012",
            low="97.876543210987",
        ),
        bar(
            datetime(2026, 8, 19, 13, 29, tzinfo=UTC),
            high="102.123456789012",
            low="97.876543210987",
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
    return PremarketLevelsService(
        load_research_config(),
        store,
        validator=validator or PassingValidator(),
    )


def test_pmh_pml_and_source_timestamps() -> None:
    result = calculate_premarket_levels(premarket_bars())
    assert result.pmh == Decimal("102.123456789012")
    assert result.pml == Decimal("97.876543210987")
    expected = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    assert result.pmh_source_timestamp == expected
    assert result.pml_source_timestamp == expected
    assert result.source_bar_count == 3


def test_equal_high_and_low_ties_choose_earliest() -> None:
    result = calculate_premarket_levels(premarket_bars())
    expected = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)
    assert result.pmh_source_timestamp == expected
    assert result.pml_source_timestamp == expected


def test_decimal_precision_input_immutability_and_result_immutability() -> None:
    values = list(premarket_bars())
    before = [item.model_dump() for item in values]
    result = calculate_premarket_levels(values)
    assert result.pmh == Decimal("102.123456789012")
    assert result.pml == Decimal("97.876543210987")
    assert [item.model_dump() for item in values] == before
    with pytest.raises(ValidationError):
        result.pmh = Decimal("999")


def test_one_bar_premarket_uses_same_bar_for_both_levels() -> None:
    value = premarket_bars()[0]
    result = calculate_premarket_levels((value,))
    assert result.pmh == value.high
    assert result.pml == value.low
    assert result.pmh_source_timestamp == result.pml_source_timestamp


def test_empty_premarket_is_explicit() -> None:
    with pytest.raises(PremarketLevelUnavailableError, match="No premarket"):
        calculate_premarket_levels(())


@pytest.mark.parametrize(
    "timestamp",
    (
        datetime(2026, 8, 19, 7, 59, tzinfo=UTC),
        datetime(2026, 8, 19, 13, 30, tzinfo=UTC),
        datetime(2026, 8, 19, 20, 0, tzinfo=UTC),
    ),
)
def test_outside_0400_through_rth_open_is_rejected(timestamp) -> None:
    with pytest.raises(PremarketLevelInputError, match="only same-day PREMARKET"):
        calculate_premarket_levels((bar(timestamp),))


def test_0400_and_0929_et_boundaries_are_included() -> None:
    values = (
        bar(datetime(2026, 8, 19, 8, 0, tzinfo=UTC)),
        bar(datetime(2026, 8, 19, 13, 29, tzinfo=UTC)),
    )
    result = calculate_premarket_levels(values)
    assert result.source_bar_count == 2


def test_duplicate_timestamps_are_rejected() -> None:
    first = premarket_bars()[0]
    with pytest.raises(PremarketLevelInputError, match="Duplicate"):
        calculate_premarket_levels((first, first))


def test_out_of_order_bars_are_rejected() -> None:
    values = premarket_bars()
    with pytest.raises(PremarketLevelInputError, match="chronological"):
        calculate_premarket_levels((values[1], values[0]))


def test_mixed_same_day_requirement_is_enforced() -> None:
    next_day = bar(datetime(2026, 8, 20, 8, 0, tzinfo=UTC))
    with pytest.raises(PremarketLevelInputError, match="mix"):
        calculate_premarket_levels((premarket_bars()[0], next_day))


@pytest.mark.parametrize(
    ("field", "value"),
    (("symbol", "QQQ"), ("timeframe", "5Min")),
)
def test_wrong_symbol_or_timeframe_is_rejected(field, value) -> None:
    original = premarket_bars()[0]
    wrong = RawBarRecord.model_construct(**{**original.model_dump(), field: value})
    with pytest.raises(PremarketLevelInputError, match="raw 1Min"):
        calculate_premarket_levels((wrong,))


def test_service_selects_only_premarket_and_extremes_elsewhere_cannot_affect_it() -> None:
    outside = bar(datetime(2026, 8, 19, 7, 59, tzinfo=UTC), high="999", low="1")
    rth = bar(datetime(2026, 8, 19, 13, 30, tzinfo=UTC), high="999", low="1")
    after = bar(datetime(2026, 8, 19, 20, 0, tzinfo=UTC), high="999", low="1")
    partition = (outside, *premarket_bars(), rth, after)
    result = service(FakeStore({SESSION_DATE: partition})).calculate(
        start=SESSION_DATE, end=SESSION_DATE
    )
    item = result.levels[0]
    assert item.pmh == Decimal("102.123456789012")
    assert item.pml == Decimal("97.876543210987")
    assert item.source_bar_count == 3


def test_premarket_prefix_and_full_day_produce_identical_levels() -> None:
    prefix = FakeStore({SESSION_DATE: premarket_bars()})
    full = FakeStore(
        {
            SESSION_DATE: (
                *premarket_bars(),
                bar(datetime(2026, 8, 19, 13, 30, tzinfo=UTC), high="999", low="1"),
                bar(datetime(2026, 8, 19, 20, 0, tzinfo=UTC), high="999", low="1"),
            )
        }
    )
    prefix_result = service(prefix).calculate(start=SESSION_DATE, end=SESSION_DATE)
    full_result = service(full).calculate(start=SESSION_DATE, end=SESSION_DATE)
    assert prefix_result == full_result


def test_missing_partition_and_no_premarket_are_distinct_states() -> None:
    missing = service(FakeStore({})).calculate(start=SESSION_DATE, end=SESSION_DATE)
    assert missing.levels[0].status == "MISSING_RAW_SESSION"
    rth_only = FakeStore(
        {SESSION_DATE: (bar(datetime(2026, 8, 19, 13, 30, tzinfo=UTC)),)}
    )
    no_premarket = service(rth_only).calculate(start=SESSION_DATE, end=SESSION_DATE)
    assert no_premarket.levels[0].status == "NO_PREMARKET_DATA"
    assert no_premarket.levels[0].pmh is None
    assert no_premarket.levels[0].pml is None


def test_validation_failure_blocks_calculation() -> None:
    failing = SimpleNamespace(
        validate_raw_bars=lambda *args, **kwargs: SimpleNamespace(
            passed=False,
            issues=(SimpleNamespace(code="MISSING_RTH_MINUTES", severity="ERROR"),),
        )
    )
    fake = FakeStore({SESSION_DATE: premarket_bars()})
    with pytest.raises(PremarketLevelValidationError, match="MISSING_RTH_MINUTES"):
        service(fake, validator=failing).calculate(start=SESSION_DATE, end=SESSION_DATE)


def test_nontrading_dates_are_not_loaded() -> None:
    fake = FakeStore({})
    result = service(fake).calculate(
        start=date(2026, 8, 15), end=date(2026, 8, 16)
    )
    assert result.levels == ()
    assert fake.loaded == []


def test_local_service_never_calls_network(monkeypatch) -> None:
    def reject_network(*args, **kwargs):
        raise AssertionError("local premarket-level calculation must remain offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    fake = FakeStore({SESSION_DATE: premarket_bars()})
    result = service(fake).calculate(start=SESSION_DATE, end=SESSION_DATE)
    assert result.levels[0].status == "AVAILABLE"


def test_cli_is_offline_nonpersistent_and_reports_availability(
    monkeypatch, tmp_path, capsys
) -> None:
    result = PremarketLevelsResult(
        start_date=SESSION_DATE,
        end_date=SESSION_DATE,
        levels=(
            PremarketLevels(
                session_date=SESSION_DATE,
                pmh=Decimal("101"),
                pml=Decimal("99"),
                pmh_source_timestamp=datetime(2026, 8, 19, 9, 0, tzinfo=UTC),
                pml_source_timestamp=datetime(2026, 8, 19, 10, 0, tzinfo=UTC),
                source_bar_count=2,
                status="AVAILABLE",
            ),
        ),
    )

    def fake_calculate(self, *, start, end):
        return result

    def reject_network(*args, **kwargs):
        raise AssertionError("premarket-levels must remain offline")

    monkeypatch.setattr(PremarketLevelsService, "calculate", fake_calculate)
    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "premarket-levels",
            "--start",
            SESSION_DATE.isoformat(),
            "--end",
            SESSION_DATE.isoformat(),
            "--raw-data-root",
            str(tmp_path),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.err == ""
    assert "SPY PREMARKET LEVELS" in captured.out
    assert "AVAILABLE" in captured.out
    assert "Status: PASS" in captured.out
    assert list(tmp_path.iterdir()) == []
