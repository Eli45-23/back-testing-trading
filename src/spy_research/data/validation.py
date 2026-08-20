"""Deterministic, read-only validation of persisted Phase 1 raw bars."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field

from spy_research.data.errors import RawDataError
from spy_research.data.raw_store import RawBarStore
from spy_research.data.schemas import RawBarRecord
from spy_research.market import MarketSessionClassifier, SessionType, XNYSCalendar


NEW_YORK = ZoneInfo("America/New_York")
MAX_MISSING_RANGES = 20


class ValidationSeverity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class ValidationIssue(BaseModel):
    """One stable, machine-readable data-quality finding."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    severity: ValidationSeverity
    message: str
    session_date: date | None = None
    timestamp: datetime | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class SessionValidationStats(BaseModel):
    """Observed and expected counts for one authoritative XNYS session."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    market_open: datetime
    market_close: datetime
    is_early_close: bool
    expected_rth_bars: int = Field(ge=0)
    observed_rth_bars: int = Field(ge=0)
    missing_rth_bars: int = Field(ge=0)
    extra_rth_bars: int = Field(ge=0)
    premarket_bars: int = Field(ge=0)
    premarket_possible_minutes: int = Field(ge=0)
    premarket_missing_minutes: int = Field(ge=0)
    after_hours_bars: int = Field(ge=0)
    after_hours_possible_minutes: int = Field(ge=0)
    after_hours_missing_minutes: int = Field(ge=0)


class DataValidationReport(BaseModel):
    """Immutable validation result that can gate future processing."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: str
    start_date: date
    end_date: date
    total_bars: int = Field(ge=0)
    sessions_checked: int = Field(ge=0)
    expected_sessions: int = Field(ge=0)
    sessions_present: int = Field(ge=0)
    expected_rth_bars: int = Field(ge=0)
    observed_rth_bars: int = Field(ge=0)
    missing_rth_bars: int = Field(ge=0)
    extra_rth_bars: int = Field(ge=0)
    duplicate_keys: int = Field(ge=0)
    error_count: int = Field(ge=0)
    warning_count: int = Field(ge=0)
    info_count: int = Field(ge=0)
    passed: bool
    session_stats: tuple[SessionValidationStats, ...]
    issues: tuple[ValidationIssue, ...]


class RawDataValidator:
    """Validate bars without sorting, repairing, dropping, or mutating them."""

    def __init__(self, calendar: XNYSCalendar | None = None) -> None:
        self._calendar = calendar or XNYSCalendar()
        self._classifier = MarketSessionClassifier(self._calendar)

    def validate_raw_store(
        self,
        store: RawBarStore,
        *,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> DataValidationReport:
        bars: list[RawBarRecord] = []
        partition_dates: list[date] = []
        store_issues: list[ValidationIssue] = []
        for partition_date in _date_range(start_date, end_date):
            try:
                partition = store.load_partition(partition_date)
            except RawDataError as exc:
                store_issues.append(
                    _issue(
                        "CORRUPTED_PARTITION",
                        ValidationSeverity.ERROR,
                        str(exc),
                        session_date=partition_date,
                    )
                )
                continue
            bars.extend(partition)
            partition_dates.extend([partition_date] * len(partition))
        return self.validate_raw_bars(
            bars,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            partition_dates=partition_dates,
            initial_issues=store_issues,
        )

    def validate_raw_bars(
        self,
        bars: Sequence[RawBarRecord],
        *,
        symbol: str,
        start_date: date,
        end_date: date,
        partition_dates: Sequence[date] | None = None,
        initial_issues: Sequence[ValidationIssue] = (),
    ) -> DataValidationReport:
        if start_date > end_date:
            raise ValueError("start date must be on or before end date")
        if partition_dates is not None and len(partition_dates) != len(bars):
            raise ValueError("partition_dates must align one-to-one with bars")

        issues = list(initial_issues)
        classified_by_date: dict[date, list[tuple[RawBarRecord, SessionType]]] = {}
        seen_keys: set[tuple[object, ...]] = set()
        duplicate_keys = 0
        previous_timestamp: datetime | None = None

        for index, bar in enumerate(bars):
            timestamp = bar.timestamp
            aware = _is_aware(timestamp)
            session_date = timestamp.astimezone(NEW_YORK).date() if aware else None

            if previous_timestamp is not None and aware and _is_aware(previous_timestamp):
                if timestamp == previous_timestamp:
                    issues.append(_issue("DUPLICATE_TIMESTAMP", ValidationSeverity.ERROR,
                        "Repeated timestamp violates strict chronological ordering",
                        session_date=session_date, timestamp=timestamp))
                elif timestamp < previous_timestamp:
                    issues.append(_issue("OUT_OF_ORDER_TIMESTAMP", ValidationSeverity.ERROR,
                        "Bar timestamp is earlier than the preceding input bar",
                        session_date=session_date, timestamp=timestamp,
                        details={"input_index": index}))
            previous_timestamp = timestamp

            key = (bar.symbol, timestamp, bar.feed, bar.timeframe)
            if key in seen_keys:
                duplicate_keys += 1
                issues.append(_issue("DUPLICATE_UNIQUE_KEY", ValidationSeverity.ERROR,
                    "Duplicate symbol/timestamp/feed/timeframe key",
                    session_date=session_date, timestamp=timestamp))
            seen_keys.add(key)

            self._validate_bar_fields(bar, session_date, issues)
            if not aware:
                issues.append(_issue("NAIVE_TIMESTAMP", ValidationSeverity.ERROR,
                    "Raw bar timestamp must be timezone-aware"))
                continue

            if timestamp.second != 0 or timestamp.microsecond != 0:
                issues.append(_issue("TIMESTAMP_NOT_MINUTE_ALIGNED", ValidationSeverity.ERROR,
                    "One-minute bar timestamp must have zero seconds and microseconds",
                    session_date=session_date, timestamp=timestamp))

            assert session_date is not None
            if session_date < start_date or session_date > end_date:
                issues.append(_issue("DATE_OUT_OF_RANGE", ValidationSeverity.ERROR,
                    "Bar New York date falls outside the requested range",
                    session_date=session_date, timestamp=timestamp))

            if partition_dates is not None and partition_dates[index] != session_date:
                issues.append(_issue("PARTITION_DATE_MISMATCH", ValidationSeverity.ERROR,
                    "Bar New York date does not match its raw partition date",
                    session_date=session_date, timestamp=timestamp,
                    details={"partition_date": partition_dates[index].isoformat()}))

            classified = self._classifier.classify(bar)
            classified_by_date.setdefault(session_date, []).append(
                (bar, classified.session_type)
            )
            if classified.session_type is SessionType.OUTSIDE_SESSION:
                issues.append(_issue("OUTSIDE_SESSION_BAR", ValidationSeverity.WARNING,
                    "Bar is outside the defined 04:00-20:00 trading-day window",
                    session_date=session_date, timestamp=timestamp))
            elif classified.session_type is SessionType.NON_SESSION:
                issues.append(_issue("NON_SESSION_BAR", ValidationSeverity.ERROR,
                    "Bar exists on a date that is not an XNYS trading session",
                    session_date=session_date, timestamp=timestamp))

        expected_dates = [
            value
            for value in _date_range(start_date, end_date)
            if self._calendar.session_for_date(value).is_trading_day
        ]
        stats: list[SessionValidationStats] = []
        sessions_present = 0

        for session_date in expected_dates:
            session = self._calendar.session_for_date(session_date)
            assert session.market_open is not None and session.market_close is not None
            expected = _minute_starts(session.market_open, session.market_close)
            premarket_expected = _minute_starts(
                datetime.combine(session_date, time(4), tzinfo=NEW_YORK),
                session.market_open,
            )
            after_hours_expected = _minute_starts(
                session.market_close,
                datetime.combine(session_date, time(20), tzinfo=NEW_YORK),
            )
            day_bars = classified_by_date.get(session_date, [])
            if day_bars:
                sessions_present += 1
            else:
                issues.append(_issue("MISSING_EXPECTED_SESSION", ValidationSeverity.ERROR,
                    "Expected XNYS trading session has no raw bars",
                    session_date=session_date,
                    details={"expected_rth_bars": len(expected)}))

            observed = {
                bar.timestamp.astimezone(UTC)
                for bar, session_type in day_bars
                if session_type is SessionType.RTH
                and _is_aware(bar.timestamp)
                and bar.timestamp.second == 0
                and bar.timestamp.microsecond == 0
            }
            premarket_observed = {
                bar.timestamp.astimezone(UTC)
                for bar, session_type in day_bars
                if session_type is SessionType.PREMARKET
                and _is_aware(bar.timestamp)
                and bar.timestamp.second == 0
                and bar.timestamp.microsecond == 0
            }
            after_hours_observed = {
                bar.timestamp.astimezone(UTC)
                for bar, session_type in day_bars
                if session_type is SessionType.AFTER_HOURS
                and _is_aware(bar.timestamp)
                and bar.timestamp.second == 0
                and bar.timestamp.microsecond == 0
            }
            missing = sorted(expected - observed)
            extra = sorted(observed - expected)
            if missing:
                issues.append(_issue("MISSING_RTH_MINUTES", ValidationSeverity.ERROR,
                    "Required RTH minute starts are missing",
                    session_date=session_date,
                    details={"missing_count": len(missing),
                             "missing_ranges": _summarize_ranges(missing)}))
            if extra:
                issues.append(_issue("EXTRA_RTH_MINUTES", ValidationSeverity.ERROR,
                    "Observed RTH timestamps do not match the exchange schedule",
                    session_date=session_date,
                    details={"extra_count": len(extra),
                             "extra_ranges": _summarize_ranges(extra)}))
            if session.is_early_close:
                issues.append(_issue("EARLY_CLOSE_SESSION", ValidationSeverity.INFO,
                    "XNYS session uses an authoritative early close",
                    session_date=session_date,
                    details={"market_close": session.market_close.isoformat()}))

            counts = Counter(session_type for _, session_type in day_bars)
            stats.append(SessionValidationStats(
                session_date=session_date,
                market_open=session.market_open,
                market_close=session.market_close,
                is_early_close=session.is_early_close,
                expected_rth_bars=len(expected),
                observed_rth_bars=len(observed),
                missing_rth_bars=len(missing),
                extra_rth_bars=len(extra),
                premarket_bars=counts[SessionType.PREMARKET],
                premarket_possible_minutes=len(premarket_expected),
                premarket_missing_minutes=len(
                    premarket_expected - premarket_observed
                ),
                after_hours_bars=counts[SessionType.AFTER_HOURS],
                after_hours_possible_minutes=len(after_hours_expected),
                after_hours_missing_minutes=len(
                    after_hours_expected - after_hours_observed
                ),
            ))

        severity_counts = Counter(issue.severity for issue in issues)
        return DataValidationReport(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            total_bars=len(bars),
            sessions_checked=len(expected_dates),
            expected_sessions=len(expected_dates),
            sessions_present=sessions_present,
            expected_rth_bars=sum(item.expected_rth_bars for item in stats),
            observed_rth_bars=sum(item.observed_rth_bars for item in stats),
            missing_rth_bars=sum(item.missing_rth_bars for item in stats),
            extra_rth_bars=sum(item.extra_rth_bars for item in stats),
            duplicate_keys=duplicate_keys,
            error_count=severity_counts[ValidationSeverity.ERROR],
            warning_count=severity_counts[ValidationSeverity.WARNING],
            info_count=severity_counts[ValidationSeverity.INFO],
            passed=severity_counts[ValidationSeverity.ERROR] == 0,
            session_stats=tuple(stats),
            issues=tuple(issues),
        )

    @staticmethod
    def _validate_bar_fields(
        bar: RawBarRecord,
        session_date: date | None,
        issues: list[ValidationIssue],
    ) -> None:
        timestamp = bar.timestamp if _is_aware(bar.timestamp) else None
        expected = {
            "symbol": "SPY", "source": "alpaca", "feed": "sip",
            "timeframe": "1Min", "adjustment": "raw",
        }
        for field, expected_value in expected.items():
            actual = getattr(bar, field)
            if actual != expected_value:
                issues.append(_issue("PROVENANCE_MISMATCH", ValidationSeverity.ERROR,
                    f"Raw bar {field} must be {expected_value}",
                    session_date=session_date, timestamp=timestamp,
                    details={"field": field, "actual": str(actual),
                             "expected": expected_value}))

        prices = {name: getattr(bar, name) for name in ("open", "high", "low", "close")}
        finite_prices = all(_decimal_is_finite(value) for value in prices.values())
        if not finite_prices:
            issues.append(_issue("NON_FINITE_PRICE", ValidationSeverity.ERROR,
                "OHLC prices must be finite", session_date=session_date,
                timestamp=timestamp))
        else:
            for name, value in prices.items():
                if value <= 0:
                    issues.append(_issue("NON_POSITIVE_PRICE", ValidationSeverity.ERROR,
                        f"{name} price must be greater than zero",
                        session_date=session_date, timestamp=timestamp,
                        details={"field": name}))
            try:
                if bar.high < bar.low or bar.high < bar.open or bar.high < bar.close:
                    issues.append(_issue("INVALID_OHLC_HIGH", ValidationSeverity.ERROR,
                        "High must be at least open, close, and low",
                        session_date=session_date, timestamp=timestamp))
                if bar.low > bar.open or bar.low > bar.close or bar.low > bar.high:
                    issues.append(_issue("INVALID_OHLC_LOW", ValidationSeverity.ERROR,
                        "Low must be at most open, close, and high",
                        session_date=session_date, timestamp=timestamp))
            except InvalidOperation:
                pass

        if bar.volume < 0:
            issues.append(_issue("NEGATIVE_VOLUME", ValidationSeverity.ERROR,
                "Volume must be non-negative", session_date=session_date,
                timestamp=timestamp))
        if bar.trade_count < 0:
            issues.append(_issue("NEGATIVE_TRADE_COUNT", ValidationSeverity.ERROR,
                "Trade count must be non-negative", session_date=session_date,
                timestamp=timestamp))
        if not _decimal_is_finite(bar.vwap) or bar.vwap <= 0:
            issues.append(_issue("INVALID_VWAP", ValidationSeverity.ERROR,
                "VWAP must be finite and greater than zero",
                session_date=session_date, timestamp=timestamp))


def _issue(
    code: str,
    severity: ValidationSeverity,
    message: str,
    *,
    session_date: date | None = None,
    timestamp: datetime | None = None,
    details: dict[str, Any] | None = None,
) -> ValidationIssue:
    return ValidationIssue(code=code, severity=severity, message=message,
                           session_date=session_date, timestamp=timestamp,
                           details=details or {})


def _is_aware(value: datetime) -> bool:
    return value.tzinfo is not None and value.utcoffset() is not None


def _decimal_is_finite(value: Decimal) -> bool:
    return isinstance(value, Decimal) and value.is_finite()


def _date_range(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def _minute_starts(start: datetime, end: datetime) -> set[datetime]:
    values: set[datetime] = set()
    current = start.astimezone(UTC)
    while current < end.astimezone(UTC):
        values.add(current)
        current += timedelta(minutes=1)
    return values


def _summarize_ranges(timestamps: Sequence[datetime]) -> list[str]:
    if not timestamps:
        return []
    ranges: list[tuple[datetime, datetime]] = []
    range_start = previous = timestamps[0]
    for timestamp in timestamps[1:]:
        if timestamp != previous + timedelta(minutes=1):
            ranges.append((range_start, previous))
            range_start = timestamp
        previous = timestamp
    ranges.append((range_start, previous))

    rendered = [
        start.isoformat() if start == end else f"{start.isoformat()}/{end.isoformat()}"
        for start, end in ranges[:MAX_MISSING_RANGES]
    ]
    if len(ranges) > MAX_MISSING_RANGES:
        rendered.append(f"... {len(ranges) - MAX_MISSING_RANGES} more ranges")
    return rendered
