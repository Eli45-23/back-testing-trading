"""Validated, session-isolated RTH one-minute to five-minute aggregation."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta

from spy_research.bars.models import (
    AggregationResult,
    FiveMinuteBar,
    SessionAggregationSummary,
)
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.data.validation import DataValidationReport, RawDataValidator
from spy_research.market import (
    ClassifiedRawBar,
    MarketSessionClassifier,
    SessionType,
    TradingSession,
    XNYSCalendar,
)


class AggregationError(ValueError):
    """Base error for unsafe or incomplete derived-bar construction."""


class BucketIntegrityError(AggregationError):
    """The source timestamps do not form exact complete five-minute buckets."""


class RawDataValidationGateError(AggregationError):
    """Raw validation failed, so downstream transformation was blocked."""

    def __init__(self, report: DataValidationReport) -> None:
        self.report = report
        super().__init__(
            "Raw-data validation failed; five-minute aggregation is blocked "
            f"({report.error_count} errors)"
        )


def aggregate_rth_1m_to_5m(
    classified_bars: Sequence[ClassifiedRawBar],
    session: TradingSession,
) -> tuple[FiveMinuteBar, ...]:
    """Purely aggregate one session after verifying every expected minute start."""

    if not session.is_trading_day:
        raise BucketIntegrityError("Cannot aggregate a non-trading session")
    assert session.market_open is not None and session.market_close is not None
    market_open = session.market_open.astimezone(UTC)
    market_close = session.market_close.astimezone(UTC)
    duration_minutes = int((market_close - market_open).total_seconds() // 60)
    if duration_minutes <= 0 or duration_minutes % 5 != 0:
        raise BucketIntegrityError(
            "XNYS RTH duration must divide into complete five-minute buckets"
        )

    rth_bars = [
        item.bar
        for item in classified_bars
        if item.session_date == session.session_date
        and item.session_type is SessionType.RTH
    ]
    timestamps = [bar.timestamp.astimezone(UTC) for bar in rth_bars]
    if len(timestamps) != len(set(timestamps)):
        raise BucketIntegrityError("Duplicate RTH minute timestamp in source bars")

    for timestamp in timestamps:
        if timestamp.second != 0 or timestamp.microsecond != 0:
            raise BucketIntegrityError(
                "RTH source timestamps must align exactly to minute boundaries"
            )

    expected_timestamps = tuple(
        market_open + timedelta(minutes=minute)
        for minute in range(duration_minutes)
    )
    expected_set = set(expected_timestamps)
    actual_set = set(timestamps)
    if actual_set != expected_set:
        missing = len(expected_set - actual_set)
        extra = len(actual_set - expected_set)
        raise BucketIntegrityError(
            "RTH source timestamps do not match the exchange session "
            f"(missing={missing}, extra={extra})"
        )

    by_timestamp = {
        bar.timestamp.astimezone(UTC): bar
        for bar in rth_bars
    }
    derived: list[FiveMinuteBar] = []
    for offset in range(0, duration_minutes, 5):
        bucket_start = market_open + timedelta(minutes=offset)
        bucket_timestamps = tuple(
            bucket_start + timedelta(minutes=minute) for minute in range(5)
        )
        source = [by_timestamp[timestamp] for timestamp in bucket_timestamps]
        if len(source) != 5:
            raise BucketIntegrityError(
                f"Five-minute bucket {bucket_start.isoformat()} has {len(source)} bars"
            )
        first = source[0]
        derived.append(
            FiveMinuteBar(
                symbol=first.symbol,
                timestamp=bucket_start,
                session_date=session.session_date,
                open=first.open,
                high=max(bar.high for bar in source),
                low=min(bar.low for bar in source),
                close=source[-1].close,
                volume=sum(bar.volume for bar in source),
                trade_count=sum(bar.trade_count for bar in source),
                source=first.source,
                feed=first.feed,
                timeframe="5Min",
                adjustment=first.adjustment,
                source_bar_count=5,
            )
        )
    return tuple(derived)


class FiveMinuteAggregationService:
    """Load, validate, classify, and aggregate local raw bars without writing."""

    def __init__(
        self,
        config: ResearchConfig,
        store: RawBarStore,
        *,
        calendar: XNYSCalendar | None = None,
        validator: RawDataValidator | None = None,
    ) -> None:
        self._config = config
        self._store = store
        self._calendar = calendar or XNYSCalendar()
        self._validator = validator or RawDataValidator(self._calendar)
        self._classifier = MarketSessionClassifier(self._calendar)

    def aggregate(self, *, start: date, end: date) -> AggregationResult:
        report = self._validator.validate_raw_store(
            self._store,
            symbol=self._config.symbol,
            start_date=start,
            end_date=end,
        )
        if not report.passed:
            raise RawDataValidationGateError(report)

        raw_bars = self._store.load_raw_bars(
            symbol=self._config.symbol,
            start=start,
            end=end,
            feed=self._config.data.feed,
            timeframe=self._config.data.timeframe,
        )
        classified = self._classifier.classify_many(raw_bars)
        derived: list[FiveMinuteBar] = []
        summaries: list[SessionAggregationSummary] = []

        for stats in report.session_stats:
            session = self._calendar.session_for_date(stats.session_date)
            session_bars = aggregate_rth_1m_to_5m(classified, session)
            expected_count = stats.expected_rth_bars // 5
            if len(session_bars) != expected_count:
                raise BucketIntegrityError(
                    f"Session {stats.session_date} expected {expected_count} "
                    f"five-minute bars, received {len(session_bars)}"
                )
            derived.extend(session_bars)
            summaries.append(
                SessionAggregationSummary(
                    session_date=stats.session_date,
                    raw_rth_bars=stats.observed_rth_bars,
                    expected_five_minute_bars=expected_count,
                    five_minute_bars=len(session_bars),
                    first_timestamp=(session_bars[0].timestamp if session_bars else None),
                    last_timestamp=(session_bars[-1].timestamp if session_bars else None),
                )
            )

        return AggregationResult(
            symbol=self._config.symbol,
            start_date=start,
            end_date=end,
            raw_rth_bars=sum(item.raw_rth_bars for item in summaries),
            bars=tuple(derived),
            sessions=tuple(summaries),
            validation_report=report,
        )
