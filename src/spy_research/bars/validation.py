"""Validation and raw reconciliation for processed five-minute partitions."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field

from spy_research.bars.aggregation import FiveMinuteAggregationService
from spy_research.bars.errors import ProcessedDataError
from spy_research.bars.models import FiveMinuteBar
from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.data.validation import ValidationSeverity
from spy_research.market import XNYSCalendar


NEW_YORK = ZoneInfo("America/New_York")


class ProcessedValidationIssue(BaseModel):
    """One deterministic processed-data quality finding."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    severity: ValidationSeverity
    message: str
    session_date: date | None = None
    timestamp: datetime | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class ProcessedSessionStats(BaseModel):
    """Expected, observed, and reconciled counts for one XNYS session."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    expected_bars: int = Field(ge=0)
    observed_bars: int = Field(ge=0)
    missing_bars: int = Field(ge=0)
    extra_bars: int = Field(ge=0)
    reconciliation_errors: int = Field(ge=0)


class ProcessedValidationReport(BaseModel):
    """Machine-readable gate for later indicator processing."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: str
    start_date: date
    end_date: date
    sessions_expected: int = Field(ge=0)
    sessions_present: int = Field(ge=0)
    total_bars: int = Field(ge=0)
    expected_bars: int = Field(ge=0)
    missing_bars: int = Field(ge=0)
    extra_bars: int = Field(ge=0)
    duplicate_bars: int = Field(ge=0)
    reconciliation_errors: int = Field(ge=0)
    error_count: int = Field(ge=0)
    warning_count: int = Field(ge=0)
    passed: bool
    session_stats: tuple[ProcessedSessionStats, ...]
    issues: tuple[ProcessedValidationIssue, ...]


class ProcessedFiveMinuteValidator:
    """Validate processed bars and optionally reconcile them to Stage 2.1."""

    def __init__(self, calendar: XNYSCalendar | None = None) -> None:
        self._calendar = calendar or XNYSCalendar()

    def validate_store(
        self,
        store: ProcessedFiveMinuteStore,
        *,
        start: date,
        end: date,
        reconcile: bool = False,
        config: ResearchConfig | None = None,
        raw_store: RawBarStore | None = None,
    ) -> ProcessedValidationReport:
        bars: list[FiveMinuteBar] = []
        partition_dates: list[date] = []
        initial_issues: list[ProcessedValidationIssue] = []
        for partition_date in _date_range(start, end):
            try:
                partition = store.load_partition(
                    partition_date,
                    reject_duplicates=False,
                )
            except ProcessedDataError as exc:
                initial_issues.append(
                    _issue(
                        "CORRUPTED_PROCESSED_PARTITION",
                        ValidationSeverity.ERROR,
                        str(exc),
                        session_date=partition_date,
                    )
                )
                continue
            bars.extend(partition)
            partition_dates.extend([partition_date] * len(partition))

        expected: Sequence[FiveMinuteBar] | None = None
        if reconcile:
            if config is None or raw_store is None:
                raise ValueError(
                    "config and raw_store are required for raw reconciliation"
                )
            expected = FiveMinuteAggregationService(
                config,
                raw_store,
                calendar=self._calendar,
            ).aggregate(start=start, end=end).bars

        return self.validate_bars(
            bars,
            start=start,
            end=end,
            partition_dates=partition_dates,
            expected_reaggregated=expected,
            initial_issues=initial_issues,
        )

    def validate_bars(
        self,
        bars: Sequence[FiveMinuteBar],
        *,
        start: date,
        end: date,
        partition_dates: Sequence[date] | None = None,
        expected_reaggregated: Sequence[FiveMinuteBar] | None = None,
        initial_issues: Sequence[ProcessedValidationIssue] = (),
    ) -> ProcessedValidationReport:
        if start > end:
            raise ValueError("start date must be on or before end date")
        if partition_dates is not None and len(partition_dates) != len(bars):
            raise ValueError("partition_dates must align one-to-one with bars")

        issues = list(initial_issues)
        by_date: dict[date, list[FiveMinuteBar]] = {}
        seen: set[tuple[str, datetime, str, str]] = set()
        duplicate_bars = 0
        previous: datetime | None = None

        for index, bar in enumerate(bars):
            timestamp = bar.timestamp
            aware = _is_aware(timestamp)
            local_date = timestamp.astimezone(NEW_YORK).date() if aware else None
            if previous is not None and aware and _is_aware(previous):
                if timestamp <= previous:
                    code = (
                        "DUPLICATE_PROCESSED_TIMESTAMP"
                        if timestamp == previous
                        else "OUT_OF_ORDER_PROCESSED_TIMESTAMP"
                    )
                    issues.append(
                        _issue(
                            code,
                            ValidationSeverity.ERROR,
                            "Processed timestamps must be strictly chronological",
                            session_date=local_date,
                            timestamp=timestamp,
                            details={"input_index": index},
                        )
                    )
            previous = timestamp

            identity = (bar.symbol, timestamp, bar.timeframe, bar.session_mode)
            if identity in seen:
                duplicate_bars += 1
                issues.append(
                    _issue(
                        "DUPLICATE_PROCESSED_IDENTITY",
                        ValidationSeverity.ERROR,
                        "Duplicate symbol/timestamp/timeframe/session-mode identity",
                        session_date=local_date,
                        timestamp=timestamp if aware else None,
                    )
                )
            seen.add(identity)
            self._validate_fields(bar, local_date, issues)

            if not aware:
                issues.append(
                    _issue(
                        "NAIVE_PROCESSED_TIMESTAMP",
                        ValidationSeverity.ERROR,
                        "Processed timestamp must be timezone-aware",
                    )
                )
                continue
            assert local_date is not None
            if local_date != bar.session_date:
                issues.append(
                    _issue(
                        "PROCESSED_SESSION_DATE_MISMATCH",
                        ValidationSeverity.ERROR,
                        "Timestamp New York date differs from session_date",
                        session_date=bar.session_date,
                        timestamp=timestamp,
                    )
                )
            if not self._calendar.session_for_date(bar.session_date).is_trading_day:
                issues.append(
                    _issue(
                        "PROCESSED_NON_SESSION_BAR",
                        ValidationSeverity.ERROR,
                        "Processed bar exists on a non-XNYS session date",
                        session_date=bar.session_date,
                        timestamp=timestamp,
                    )
                )
            if partition_dates is not None and partition_dates[index] != bar.session_date:
                issues.append(
                    _issue(
                        "PROCESSED_PARTITION_DATE_MISMATCH",
                        ValidationSeverity.ERROR,
                        "Processed bar session_date differs from partition date",
                        session_date=bar.session_date,
                        timestamp=timestamp,
                        details={
                            "partition_date": partition_dates[index].isoformat()
                        },
                    )
                )
            by_date.setdefault(bar.session_date, []).append(bar)

        expected_dates = [
            value
            for value in _date_range(start, end)
            if self._calendar.session_for_date(value).is_trading_day
        ]
        stats: list[ProcessedSessionStats] = []
        sessions_present = 0
        expected_by_identity = (
            {
                (bar.symbol, bar.timestamp, bar.timeframe, bar.session_mode): bar
                for bar in expected_reaggregated
            }
            if expected_reaggregated is not None
            else None
        )
        actual_by_identity = {
            (bar.symbol, bar.timestamp, bar.timeframe, bar.session_mode): bar
            for bar in bars
        }

        for session_date in expected_dates:
            session = self._calendar.session_for_date(session_date)
            assert session.market_open is not None and session.market_close is not None
            expected_timestamps = _five_minute_starts(
                session.market_open,
                session.market_close,
            )
            observed = {
                bar.timestamp.astimezone(UTC)
                for bar in by_date.get(session_date, [])
                if _is_aware(bar.timestamp)
            }
            if observed:
                sessions_present += 1
            else:
                issues.append(
                    _issue(
                        "MISSING_PROCESSED_SESSION",
                        ValidationSeverity.ERROR,
                        "Expected XNYS session has no processed five-minute bars",
                        session_date=session_date,
                    )
                )
            missing = sorted(expected_timestamps - observed)
            extra = sorted(observed - expected_timestamps)
            if missing:
                issues.append(
                    _issue(
                        "MISSING_PROCESSED_BARS",
                        ValidationSeverity.ERROR,
                        "Required processed RTH five-minute starts are missing",
                        session_date=session_date,
                        details={
                            "missing_count": len(missing),
                            "missing_timestamps": [item.isoformat() for item in missing],
                        },
                    )
                )
            if extra:
                issues.append(
                    _issue(
                        "EXTRA_PROCESSED_BARS",
                        ValidationSeverity.ERROR,
                        "Processed timestamps do not align to the XNYS session open",
                        session_date=session_date,
                        details={
                            "extra_count": len(extra),
                            "extra_timestamps": [item.isoformat() for item in extra],
                        },
                    )
                )

            reconciliation_errors = 0
            if expected_by_identity is not None:
                expected_day = {
                    key: value
                    for key, value in expected_by_identity.items()
                    if value.session_date == session_date
                }
                actual_day = {
                    key: value
                    for key, value in actual_by_identity.items()
                    if value.session_date == session_date
                }
                for identity in sorted(
                    set(expected_day) | set(actual_day),
                    key=lambda value: value[1],
                ):
                    expected_bar = expected_day.get(identity)
                    actual_bar = actual_day.get(identity)
                    if expected_bar != actual_bar:
                        reconciliation_errors += 1
                        issues.append(
                            _issue(
                                "RAW_PROCESSED_RECONCILIATION_MISMATCH",
                                ValidationSeverity.ERROR,
                                "Persisted candle differs from Stage 2.1 re-aggregation",
                                session_date=session_date,
                                timestamp=identity[1],
                            )
                        )

            stats.append(
                ProcessedSessionStats(
                    session_date=session_date,
                    expected_bars=len(expected_timestamps),
                    observed_bars=len(observed),
                    missing_bars=len(missing),
                    extra_bars=len(extra),
                    reconciliation_errors=reconciliation_errors,
                )
            )

        severity_counts = Counter(issue.severity for issue in issues)
        return ProcessedValidationReport(
            symbol="SPY",
            start_date=start,
            end_date=end,
            sessions_expected=len(expected_dates),
            sessions_present=sessions_present,
            total_bars=len(bars),
            expected_bars=sum(item.expected_bars for item in stats),
            missing_bars=sum(item.missing_bars for item in stats),
            extra_bars=sum(item.extra_bars for item in stats),
            duplicate_bars=duplicate_bars,
            reconciliation_errors=sum(
                item.reconciliation_errors for item in stats
            ),
            error_count=severity_counts[ValidationSeverity.ERROR],
            warning_count=severity_counts[ValidationSeverity.WARNING],
            passed=severity_counts[ValidationSeverity.ERROR] == 0,
            session_stats=tuple(stats),
            issues=tuple(issues),
        )

    @staticmethod
    def _validate_fields(
        bar: FiveMinuteBar,
        session_date: date | None,
        issues: list[ProcessedValidationIssue],
    ) -> None:
        timestamp = bar.timestamp if _is_aware(bar.timestamp) else None
        expected = {
            "symbol": "SPY",
            "source": "alpaca",
            "feed": "sip",
            "source_timeframe": "1Min",
            "timeframe": "5Min",
            "adjustment": "raw",
            "source_bar_count": 5,
            "session_type": "RTH",
            "session_mode": "RTH_ONLY",
            "aggregation_method": "rth_1m_to_5m_v1",
        }
        for field, expected_value in expected.items():
            actual = getattr(bar, field)
            if actual != expected_value:
                issues.append(
                    _issue(
                        "PROCESSED_PROVENANCE_MISMATCH",
                        ValidationSeverity.ERROR,
                        f"Processed {field} must be {expected_value}",
                        session_date=session_date,
                        timestamp=timestamp,
                        details={
                            "field": field,
                            "actual": str(actual),
                            "expected": str(expected_value),
                        },
                    )
                )

        prices = [bar.open, bar.high, bar.low, bar.close]
        if not all(_finite(value) for value in prices):
            issues.append(
                _issue(
                    "NON_FINITE_PROCESSED_PRICE",
                    ValidationSeverity.ERROR,
                    "Processed OHLC values must be finite",
                    session_date=session_date,
                    timestamp=timestamp,
                )
            )
        else:
            if any(value <= 0 for value in prices):
                issues.append(
                    _issue(
                        "NON_POSITIVE_PROCESSED_PRICE",
                        ValidationSeverity.ERROR,
                        "Processed OHLC values must be positive",
                        session_date=session_date,
                        timestamp=timestamp,
                    )
                )
            try:
                if bar.high < max(bar.open, bar.close, bar.low):
                    issues.append(
                        _issue(
                            "INVALID_PROCESSED_HIGH",
                            ValidationSeverity.ERROR,
                            "Processed high is below open, close, or low",
                            session_date=session_date,
                            timestamp=timestamp,
                        )
                    )
                if bar.low > min(bar.open, bar.close, bar.high):
                    issues.append(
                        _issue(
                            "INVALID_PROCESSED_LOW",
                            ValidationSeverity.ERROR,
                            "Processed low is above open, close, or high",
                            session_date=session_date,
                            timestamp=timestamp,
                        )
                    )
            except InvalidOperation:
                pass
        if bar.volume < 0:
            issues.append(
                _issue(
                    "NEGATIVE_PROCESSED_VOLUME",
                    ValidationSeverity.ERROR,
                    "Processed volume must be non-negative",
                    session_date=session_date,
                    timestamp=timestamp,
                )
            )
        if bar.trade_count < 0:
            issues.append(
                _issue(
                    "NEGATIVE_PROCESSED_TRADE_COUNT",
                    ValidationSeverity.ERROR,
                    "Processed trade count must be non-negative",
                    session_date=session_date,
                    timestamp=timestamp,
                )
            )


def _issue(
    code: str,
    severity: ValidationSeverity,
    message: str,
    *,
    session_date: date | None = None,
    timestamp: datetime | None = None,
    details: dict[str, Any] | None = None,
) -> ProcessedValidationIssue:
    return ProcessedValidationIssue(
        code=code,
        severity=severity,
        message=message,
        session_date=session_date,
        timestamp=timestamp,
        details=details or {},
    )


def _is_aware(value: datetime) -> bool:
    return value.tzinfo is not None and value.utcoffset() is not None


def _finite(value: Decimal) -> bool:
    return isinstance(value, Decimal) and value.is_finite()


def _date_range(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def _five_minute_starts(start: datetime, end: datetime) -> set[datetime]:
    values: set[datetime] = set()
    current = start.astimezone(UTC)
    close = end.astimezone(UTC)
    while current < close:
        values.add(current)
        current += timedelta(minutes=5)
    return values
