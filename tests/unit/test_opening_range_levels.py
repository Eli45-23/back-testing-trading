from __future__ import annotations

import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from spy_research.bars.models import FiveMinuteBar
from spy_research.cli import main
from spy_research.config import load_research_config
from spy_research.levels import (
    OpeningFiveMinuteLevels,
    OpeningFiveMinuteLevelsResult,
    OpeningFiveMinuteLevelsService,
    OpeningRangeLevelInputError,
    OpeningRangeLevelValidationError,
    calculate_opening_five_minute_levels,
)


SESSION_DATE = date(2026, 8, 19)
OPEN = datetime(2026, 8, 19, 13, 30, tzinfo=UTC)


def bar(
    timestamp: datetime,
    *,
    session_date: date = SESSION_DATE,
    high: str = "770.630000000000",
    low: str = "769.860000000000",
) -> FiveMinuteBar:
    return FiveMinuteBar(
        symbol="SPY",
        timestamp=timestamp,
        session_date=session_date,
        open=Decimal("770.360000000000"),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal("770.021000000000"),
        volume=1000,
        trade_count=100,
        source="alpaca",
        feed="sip",
        timeframe="5Min",
        adjustment="raw",
        source_bar_count=5,
    )


def session_bars() -> tuple[FiveMinuteBar, ...]:
    return (
        bar(OPEN),
        bar(
            OPEN + timedelta(minutes=5),
            high="999.123456789012",
            low="1.123456789012",
        ),
        bar(OPEN + timedelta(minutes=10), high="800", low="700"),
    )


class FakeProcessedStore:
    def __init__(self, bars):
        self.bars = tuple(bars)
        self.loads = []

    def load_processed_5m_bars(self, **kwargs):
        self.loads.append(kwargs)
        return self.bars


class PassingValidator:
    def __init__(self):
        self.calls = []

    def validate_store(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return SimpleNamespace(passed=True, issues=())


def service(processed, *, validator=None):
    return OpeningFiveMinuteLevelsService(
        load_research_config(),
        processed,
        SimpleNamespace(),
        validator=validator or PassingValidator(),
    )


def test_first_bar_high_low_become_orh5_orl5() -> None:
    result = calculate_opening_five_minute_levels(session_bars())
    assert result.orh5 == Decimal("770.630000000000")
    assert result.orl5 == Decimal("769.860000000000")


def test_later_higher_high_and_lower_low_are_ignored() -> None:
    result = calculate_opening_five_minute_levels(session_bars())
    assert result.orh5 != Decimal("999.123456789012")
    assert result.orl5 != Decimal("1.123456789012")


def test_decimal_source_timestamp_and_input_are_preserved() -> None:
    values = list(session_bars())
    before = [item.model_dump() for item in values]
    result = calculate_opening_five_minute_levels(values)
    assert result.orh5 == Decimal("770.630000000000")
    assert result.orl5 == Decimal("769.860000000000")
    assert result.source_timestamp == OPEN
    assert [item.model_dump() for item in values] == before


def test_result_is_immutable_and_has_frozen_provenance() -> None:
    result = calculate_opening_five_minute_levels(session_bars())
    assert result.source_bar_count == 1
    assert result.timeframe_source == "5Min"
    assert result.session_mode == "RTH_ONLY"
    assert result.level_version == "opening-5m-levels-v1"
    with pytest.raises(ValidationError):
        result.orh5 = Decimal("999")


def test_empty_input_is_rejected() -> None:
    with pytest.raises(OpeningRangeLevelInputError, match="cannot be empty"):
        calculate_opening_five_minute_levels(())


def test_first_bar_must_be_calendar_session_open_bucket() -> None:
    with pytest.raises(OpeningRangeLevelInputError, match="session open"):
        calculate_opening_five_minute_levels((bar(OPEN + timedelta(minutes=5)),))


def test_normal_session_source_is_0930_et_and_available_at_0935() -> None:
    result = calculate_opening_five_minute_levels(session_bars())
    assert result.source_timestamp == OPEN
    assert result.available_from_timestamp == OPEN + timedelta(minutes=5)
    source_local = result.source_timestamp.astimezone(ZoneInfo("America/New_York"))
    available_local = result.available_from_timestamp.astimezone(
        ZoneInfo("America/New_York")
    )
    assert (source_local.hour, source_local.minute) == (9, 30)
    assert (available_local.hour, available_local.minute) == (9, 35)


def test_duplicate_timestamps_are_rejected() -> None:
    first = session_bars()[0]
    with pytest.raises(OpeningRangeLevelInputError, match="Duplicate"):
        calculate_opening_five_minute_levels((first, first))


def test_out_of_order_rows_are_rejected() -> None:
    values = session_bars()
    with pytest.raises(OpeningRangeLevelInputError, match="chronological"):
        calculate_opening_five_minute_levels((values[1], values[0]))


def test_mixed_sessions_are_rejected() -> None:
    next_day = bar(
        datetime(2026, 8, 20, 13, 30, tzinfo=UTC),
        session_date=date(2026, 8, 20),
    )
    with pytest.raises(OpeningRangeLevelInputError, match="mix"):
        calculate_opening_five_minute_levels((session_bars()[0], next_day))


@pytest.mark.parametrize(
    ("field", "value"),
    (("timeframe", "1Min"), ("session_mode", "ALL"), ("session_type", "PREMARKET")),
)
def test_wrong_timeframe_or_session_scope_is_rejected(field, value) -> None:
    original = session_bars()[0]
    wrong = FiveMinuteBar.model_construct(**{**original.model_dump(), field: value})
    with pytest.raises(OpeningRangeLevelInputError, match="RTH_ONLY 5Min"):
        calculate_opening_five_minute_levels((wrong,))


def test_first_bar_prefix_equals_full_session_with_extremes() -> None:
    prefix = calculate_opening_five_minute_levels((session_bars()[0],))
    full = calculate_opening_five_minute_levels(session_bars())
    assert prefix == full


def test_service_uses_processed_validation_with_raw_reconciliation() -> None:
    validator = PassingValidator()
    processed = FakeProcessedStore(session_bars())
    result = service(processed, validator=validator).calculate(
        start=SESSION_DATE, end=SESSION_DATE
    )
    assert len(result.levels) == 1
    assert validator.calls[0][1]["reconcile"] is True
    assert validator.calls[0][1]["raw_store"] is not None
    assert processed.loads[0]["session_mode"] == "RTH_ONLY"


def test_processed_validation_failure_blocks_service() -> None:
    failing = SimpleNamespace(
        validate_store=lambda *args, **kwargs: SimpleNamespace(
            passed=False,
            issues=(
                SimpleNamespace(
                    code="RAW_PROCESSED_RECONCILIATION_MISMATCH",
                    severity="ERROR",
                ),
            ),
        )
    )
    with pytest.raises(
        OpeningRangeLevelValidationError,
        match="RAW_PROCESSED_RECONCILIATION_MISMATCH",
    ):
        service(FakeProcessedStore(session_bars()), validator=failing).calculate(
            start=SESSION_DATE, end=SESSION_DATE
        )


def test_local_service_never_calls_network(monkeypatch) -> None:
    def reject_network(*args, **kwargs):
        raise AssertionError("opening-range calculation must remain offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    result = service(FakeProcessedStore(session_bars())).calculate(
        start=SESSION_DATE, end=SESSION_DATE
    )
    assert result.levels[0].orh5 == Decimal("770.630000000000")


def test_cli_is_offline_nonpersistent(monkeypatch, tmp_path, capsys) -> None:
    level = OpeningFiveMinuteLevels(
        session_date=SESSION_DATE,
        orh5=Decimal("770.630"),
        orl5=Decimal("769.860"),
        source_timestamp=OPEN,
        available_from_timestamp=OPEN + timedelta(minutes=5),
    )
    result = OpeningFiveMinuteLevelsResult(
        start_date=SESSION_DATE,
        end_date=SESSION_DATE,
        levels=(level,),
    )

    def fake_calculate(self, *, start, end):
        return result

    def reject_network(*args, **kwargs):
        raise AssertionError("opening-5m-levels must remain offline")

    monkeypatch.setattr(OpeningFiveMinuteLevelsService, "calculate", fake_calculate)
    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "opening-5m-levels",
            "--start",
            SESSION_DATE.isoformat(),
            "--end",
            SESSION_DATE.isoformat(),
            "--raw-data-root",
            str(tmp_path / "raw"),
            "--processed-data-root",
            str(tmp_path / "processed"),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.err == ""
    assert "SPY OPENING 5-MINUTE LEVELS" in captured.out
    assert "09:35" in captured.out
    assert "Status: PASS" in captured.out
    assert list(tmp_path.iterdir()) == []
