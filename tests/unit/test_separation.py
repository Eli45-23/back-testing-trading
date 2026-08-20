from __future__ import annotations

import hashlib
import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, getcontext

import pytest

from spy_research.alpaca.models import StockBar
from spy_research.bars import ProcessedFiveMinuteStore, aggregate_rth_1m_to_5m
from spy_research.bars.models import FiveMinuteBar
from spy_research.cli import main
from spy_research.config import load_research_config
from spy_research.data.raw_store import RawBarStore
from spy_research.data.schemas import RawBarRecord
from spy_research.indicators import (
    EmaSeparationIndicatorService,
    FiveMinuteIndicatorRow,
    IndicatorInputValidationError,
    IndicatorSequenceError,
    calculate_ema_separation_sessions,
    calculate_session_ema,
    calculate_session_ema_separation,
)
from spy_research.market import ClassifiedRawBar, SessionType, XNYSCalendar


DAY_ONE = date(2026, 8, 18)
DAY_TWO = date(2026, 8, 19)


def ema_row(
    index: int,
    ema9: Decimal | None,
    ema20: Decimal | None,
    *,
    session_date: date = DAY_TWO,
) -> FiveMinuteIndicatorRow:
    timestamp = datetime(
        session_date.year, session_date.month, session_date.day, 13, 30, tzinfo=UTC
    ) + timedelta(minutes=5 * index)
    return FiveMinuteIndicatorRow(
        symbol="SPY",
        timestamp=timestamp,
        session_date=session_date,
        close=Decimal("100"),
        ema9=ema9,
        ema20=ema20,
    )


def synthetic_bars(
    session_date: date,
    *,
    offset: Decimal = Decimal(0),
) -> list[FiveMinuteBar]:
    bars = []
    for index in range(78):
        close = Decimal(index + 1) + offset
        bars.append(
            FiveMinuteBar(
                symbol="SPY",
                timestamp=datetime(
                    session_date.year,
                    session_date.month,
                    session_date.day,
                    13,
                    30,
                    tzinfo=UTC,
                )
                + timedelta(minutes=5 * index),
                session_date=session_date,
                open=close,
                high=close + Decimal("0.3"),
                low=close - Decimal("0.4"),
                close=close,
                volume=1000,
                trade_count=20,
                source="alpaca",
                feed="sip",
                timeframe="5Min",
                adjustment="raw",
                source_bar_count=5,
            )
        )
    return bars


def persist_validated_stores(tmp_path):
    session = XNYSCalendar().session_for_date(DAY_TWO)
    assert session.market_open is not None and session.market_close is not None
    count = int((session.market_close - session.market_open).total_seconds() // 60)
    source = []
    for index in range(count):
        close = Decimal("100") + Decimal(index % 5) / Decimal("10")
        record = RawBarRecord(
            symbol="SPY",
            timestamp=session.market_open + timedelta(minutes=index),
            open=close - Decimal("0.1"),
            high=close + Decimal("0.2"),
            low=close - Decimal("0.2"),
            close=close,
            volume=1000 + index,
            trade_count=20 + index,
            vwap=close,
            source="alpaca",
            feed="sip",
            timeframe="1Min",
            adjustment="raw",
        )
        source.append(
            ClassifiedRawBar(
                bar=record,
                session_date=DAY_TWO,
                session_type=SessionType.RTH,
            )
        )
    processed = aggregate_rth_1m_to_5m(source, session)
    config = load_research_config()
    raw_store = RawBarStore(config, root=tmp_path / "raw")
    raw_store.persist_bars(
        [
            StockBar(
                symbol=item.bar.symbol,
                timestamp=item.bar.timestamp,
                open=item.bar.open,
                high=item.bar.high,
                low=item.bar.low,
                close=item.bar.close,
                volume=item.bar.volume,
                trade_count=item.bar.trade_count,
                vwap=item.bar.vwap,
            )
            for item in source
        ]
    )
    processed_store = ProcessedFiveMinuteStore(root=tmp_path / "processed")
    processed_store.persist_bars(processed)
    return config, raw_store, processed_store


@pytest.mark.parametrize(
    ("ema9", "ema20", "signed", "absolute"),
    [
        ("12", "10", "2", "2"),
        ("8", "10", "-2", "2"),
        ("10", "10", "0", "0"),
    ],
)
def test_signed_and_absolute_separation(ema9, ema20, signed, absolute) -> None:
    row = calculate_session_ema_separation(
        [ema_row(0, Decimal(ema9), Decimal(ema20))]
    )[0]
    assert row.signed_separation == Decimal(signed)
    assert row.absolute_separation == Decimal(absolute)
    assert row.absolute_separation >= 0


def test_delta_one_two_and_three_arithmetic() -> None:
    rows = calculate_session_ema_separation(
        [
            ema_row(0, Decimal("10"), Decimal("10")),
            ema_row(1, Decimal("11"), Decimal("10")),
            ema_row(2, Decimal("13"), Decimal("10")),
            ema_row(3, Decimal("16"), Decimal("10")),
        ]
    )
    assert rows[1].separation_delta_1 == Decimal("1")
    assert rows[2].separation_delta_2 == Decimal("3")
    assert rows[3].separation_delta_3 == Decimal("6")
    assert rows[3].separation_delta_1 == Decimal("3")
    assert rows[3].separation_delta_2 == Decimal("5")


@pytest.mark.parametrize(
    ("ema9", "ema20"),
    [(None, Decimal("10")), (Decimal("10"), None), (None, None)],
)
def test_unavailable_ema_means_unavailable_metrics(ema9, ema20) -> None:
    row = calculate_session_ema_separation([ema_row(0, ema9, ema20)])[0]
    assert row.signed_separation is None
    assert row.absolute_separation is None
    assert row.separation_delta_1 is None
    assert row.separation_delta_2 is None
    assert row.separation_delta_3 is None


def test_first_valid_separation_has_no_deltas() -> None:
    rows = calculate_session_ema_separation(
        [ema_row(0, None, Decimal("10")), ema_row(1, Decimal("11"), Decimal("10"))]
    )
    assert rows[1].signed_separation == Decimal("1")
    assert rows[1].separation_delta_1 is None
    assert rows[1].separation_delta_2 is None
    assert rows[1].separation_delta_3 is None


def test_delta_requires_exact_prior_valid_row() -> None:
    rows = calculate_session_ema_separation(
        [
            ema_row(0, Decimal("11"), Decimal("10")),
            ema_row(1, None, Decimal("10")),
            ema_row(2, Decimal("13"), Decimal("10")),
        ]
    )
    assert rows[2].separation_delta_1 is None
    assert rows[2].separation_delta_2 == Decimal("2")


def test_decimal_precision_is_local_and_preserved() -> None:
    original_precision = getcontext().prec
    try:
        getcontext().prec = 6
        row = calculate_session_ema_separation(
            [
                ema_row(
                    0,
                    Decimal("1.1234567890123456789012345678901234567890123456789"),
                    Decimal("1.0000000000000000000000000000000000000000000000000"),
                )
            ]
        )[0]
    finally:
        getcontext().prec = original_precision
    assert row.signed_separation == Decimal(
        "0.1234567890123456789012345678901234567890123456789"
    )


def test_input_is_unchanged_and_output_length_matches() -> None:
    rows = [ema_row(0, Decimal("11"), Decimal("10")), ema_row(1, Decimal("12"), Decimal("10"))]
    before = [row.model_dump(mode="json") for row in rows]
    output = calculate_session_ema_separation(rows)
    assert len(output) == len(rows)
    assert [row.model_dump(mode="json") for row in rows] == before


def test_normal_session_availability_counts_and_timestamps() -> None:
    ema_rows = calculate_session_ema(synthetic_bars(DAY_TWO))
    rows = calculate_session_ema_separation(ema_rows)
    assert len(rows) == 78
    assert sum(row.signed_separation is not None for row in rows) == 59
    assert sum(row.absolute_separation is not None for row in rows) == 59
    assert sum(row.separation_delta_1 is not None for row in rows) == 58
    assert sum(row.separation_delta_2 is not None for row in rows) == 57
    assert sum(row.separation_delta_3 is not None for row in rows) == 56
    assert rows[19].timestamp == datetime(2026, 8, 19, 15, 5, tzinfo=UTC)
    assert rows[20].timestamp == datetime(2026, 8, 19, 15, 10, tzinfo=UTC)
    assert rows[21].timestamp == datetime(2026, 8, 19, 15, 15, tzinfo=UTC)
    assert rows[22].timestamp == datetime(2026, 8, 19, 15, 20, tzinfo=UTC)
    assert rows[19].separation_delta_1 is None
    assert rows[20].separation_delta_1 is not None
    assert rows[21].separation_delta_2 is not None
    assert rows[22].separation_delta_3 is not None


def test_multi_session_delta_history_resets() -> None:
    day_one = calculate_session_ema(synthetic_bars(DAY_ONE, offset=Decimal("1000")))
    day_two = calculate_session_ema(synthetic_bars(DAY_TWO))
    rows = calculate_ema_separation_sessions(day_one + day_two)
    second = [row for row in rows if row.session_date == DAY_TWO]
    assert all(row.signed_separation is None for row in second[:19])
    assert second[19].signed_separation is not None
    assert second[19].separation_delta_1 is None
    assert second[19].separation_delta_2 is None
    assert second[19].separation_delta_3 is None


def test_mixed_sessions_are_rejected() -> None:
    rows = [ema_row(0, Decimal("1"), Decimal("1"), session_date=DAY_ONE), ema_row(0, Decimal("1"), Decimal("1"), session_date=DAY_TWO)]
    with pytest.raises(IndicatorSequenceError, match="mixes session dates"):
        calculate_session_ema_separation(rows)


def test_duplicate_timestamp_is_rejected() -> None:
    row = ema_row(0, Decimal("1"), Decimal("1"))
    with pytest.raises(IndicatorSequenceError, match="duplicate"):
        calculate_session_ema_separation([row, row])


def test_out_of_order_is_rejected() -> None:
    rows = [ema_row(1, Decimal("1"), Decimal("1")), ema_row(0, Decimal("1"), Decimal("1"))]
    with pytest.raises(IndicatorSequenceError, match="chronological"):
        calculate_session_ema_separation(rows)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [("timeframe", "1Min", "timeframe"), ("session_mode", "ALL", "session mode")],
)
def test_wrong_scope_is_rejected(field, value, message) -> None:
    row = ema_row(0, Decimal("1"), Decimal("1")).model_copy(update={field: value})
    with pytest.raises(IndicatorSequenceError, match=message):
        calculate_session_ema_separation([row])


def test_nonfinite_ema_is_rejected() -> None:
    row = ema_row(0, Decimal("1"), Decimal("1")).model_copy(update={"ema9": Decimal("NaN")})
    with pytest.raises(IndicatorSequenceError, match="finite"):
        calculate_session_ema_separation([row])


def test_validation_failure_blocks_service(tmp_path) -> None:
    config, raw_store, processed_store = persist_validated_stores(tmp_path)
    processed_store.partition_path(DAY_TWO).unlink()
    with pytest.raises(IndicatorInputValidationError) as exc_info:
        EmaSeparationIndicatorService(config, processed_store, raw_store).calculate(
            start=DAY_TWO, end=DAY_TWO
        )
    assert not exc_info.value.report.passed


def test_service_is_read_only(tmp_path) -> None:
    config, raw_store, processed_store = persist_validated_stores(tmp_path)
    paths = (raw_store.partition_path(DAY_TWO), processed_store.partition_path(DAY_TWO))
    before = tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in paths)
    result = EmaSeparationIndicatorService(config, processed_store, raw_store).calculate(
        start=DAY_TWO, end=DAY_TWO
    )
    after = tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in paths)
    assert result.processed_validation.passed
    assert result.sessions[0].separation_valid_rows == 59
    assert before == after


def test_cli_is_offline_and_reports_boundaries(tmp_path, monkeypatch, capsys) -> None:
    persist_validated_stores(tmp_path)

    def reject_network(*args, **kwargs):
        raise AssertionError("calculate-ema-separation must remain offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    exit_code = main(
        [
            "calculate-ema-separation",
            "--start",
            DAY_TWO.isoformat(),
            "--end",
            DAY_TWO.isoformat(),
            "--raw-data-root",
            str(tmp_path / "raw"),
            "--processed-data-root",
            str(tmp_path / "processed"),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.err == ""
    assert "Bars: 78" in captured.out
    assert "Valid separation rows: 59" in captured.out
    assert "First separation: 11:05 EDT" in captured.out
    assert "First delta-1: 11:10 EDT" in captured.out
    assert "First delta-2: 11:15 EDT" in captured.out
    assert "First delta-3: 11:20 EDT" in captured.out
    assert "Status: PASS" in captured.out
