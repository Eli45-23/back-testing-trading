"""Minimal historical bootstrap for deterministic same-session live startup."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, date, datetime, time, timedelta
from typing import Protocol
from zoneinfo import ZoneInfo

from spy_research.alpaca import HistoricalStockDataService
from spy_research.config import ResearchConfig
from spy_research.data.schemas import RawBarRecord
from spy_research.levels import (
    calculate_previous_session_levels,
    map_source_levels_to_next_session,
)
from spy_research.live.models import LiveBootstrapError, LiveBootstrapResult
from spy_research.live.normalization import LiveMarketDataAdapter
from spy_research.market import (
    MarketSessionClassifier,
    SessionType,
    XNYSCalendar,
)
from spy_research.replay import IncrementalSignalStateEngine


NEW_YORK = ZoneInfo("America/New_York")


class HistoricalBootstrapSource(Protocol):
    def fetch(self, *, start: datetime, end: datetime) -> tuple[RawBarRecord, ...]: ...


class AlpacaHistoricalBootstrapSource:
    """Read-only adapter around the accepted SIP historical-bars service."""

    def __init__(self, service: HistoricalStockDataService, config: ResearchConfig) -> None:
        self._service = service
        self._config = config

    def fetch(self, *, start: datetime, end: datetime) -> tuple[RawBarRecord, ...]:
        result = self._service.fetch_stock_bars(start=start, end=end)
        return tuple(
            RawBarRecord.from_stock_bar(bar, self._config) for bar in result.bars
        )


def previous_xnys_session(target: date, calendar: XNYSCalendar) -> date:
    candidate = target - timedelta(days=1)
    while not calendar.session_for_date(candidate).is_trading_day:
        candidate -= timedelta(days=1)
    return candidate


class LiveBootstrapper:
    """Rebuild current state only by replaying prior/current raw minutes."""

    def __init__(
        self,
        source: HistoricalBootstrapSource,
        *,
        calendar: XNYSCalendar | None = None,
    ) -> None:
        self._source = source
        self._calendar = calendar or XNYSCalendar()
        self._classifier = MarketSessionClassifier(self._calendar)

    def bootstrap(
        self,
        *,
        as_of: datetime,
    ) -> tuple[LiveMarketDataAdapter, LiveBootstrapResult]:
        if as_of.utcoffset() is None:
            raise LiveBootstrapError("bootstrap as-of must be timezone-aware")
        as_of_utc = as_of.astimezone(UTC)
        target = as_of_utc.astimezone(NEW_YORK).date()
        session = self._calendar.session_for_date(target)
        if not session.is_trading_day:
            raise LiveBootstrapError("live bootstrap requires an XNYS trading session")
        assert session.market_open is not None and session.market_close is not None
        prior_date = previous_xnys_session(target, self._calendar)
        prior = self._calendar.session_for_date(prior_date)
        assert prior.market_open is not None and prior.market_close is not None
        prior_bars = self._source.fetch(
            start=prior.market_open,
            end=prior.market_close - timedelta(microseconds=1),
        )
        prior_rth = tuple(
            bar for bar in prior_bars
            if self._classifier.classify(bar).session_type is SessionType.RTH
        )
        self._validate_complete_rth(prior_rth, prior.market_open, prior.market_close)
        previous_values = calculate_previous_session_levels(
            prior_rth, calendar=self._calendar
        )
        previous_levels = map_source_levels_to_next_session(
            previous_values, calendar=self._calendar
        )

        engine = IncrementalSignalStateEngine(calendar=self._calendar)
        engine.start_session(session, previous_day_levels=previous_levels)
        adapter = LiveMarketDataAdapter(
            engine, session_date=target, calendar=self._calendar
        )
        last_complete_start = as_of_utc.replace(second=0, microsecond=0) - timedelta(
            minutes=1
        )
        premarket_start = datetime.combine(target, time(4), tzinfo=NEW_YORK).astimezone(UTC)
        current = ()
        if last_complete_start >= premarket_start:
            current = self._source.fetch(
                start=premarket_start,
                end=min(
                    last_complete_start + timedelta(minutes=1, microseconds=-1),
                    session.market_close - timedelta(microseconds=1),
                ),
            )
        accepted = tuple(
            bar for bar in current
            if bar.timestamp <= last_complete_start
            and self._classifier.classify(bar).session_date == target
            and self._classifier.classify(bar).session_type
            in (SessionType.PREMARKET, SessionType.RTH)
        )
        if tuple(sorted(accepted, key=lambda item: item.timestamp)) != accepted:
            raise LiveBootstrapError("historical bootstrap bars are out of order")
        rth = tuple(
            bar for bar in accepted
            if self._classifier.classify(bar).session_type is SessionType.RTH
        )
        expected_rth_end = min(last_complete_start, session.market_close - timedelta(minutes=1))
        if expected_rth_end >= session.market_open:
            self._validate_complete_rth(rth, session.market_open, expected_rth_end + timedelta(minutes=1))
        for bar in accepted:
            adapter.seed(bar)
        premarket_count = len(accepted) - len(rth)
        return adapter, LiveBootstrapResult(
            session_date=target,
            as_of=as_of_utc,
            prior_session_date=prior_date,
            prior_rth_bar_count=len(prior_rth),
            current_premarket_bar_count=premarket_count,
            current_rth_bar_count=len(rth),
            seeded_bar_count=len(accepted),
            last_seeded_timestamp=accepted[-1].timestamp if accepted else None,
        )

    @staticmethod
    def _validate_complete_rth(
        bars: Sequence[RawBarRecord],
        market_open: datetime,
        market_close: datetime,
    ) -> None:
        expected_count = int((market_close - market_open).total_seconds() // 60)
        if len(bars) != expected_count:
            raise LiveBootstrapError("historical bootstrap RTH minute coverage is incomplete")
        for index, bar in enumerate(bars):
            if bar.timestamp != market_open + timedelta(minutes=index):
                raise LiveBootstrapError("historical bootstrap RTH minutes are not consecutive")
