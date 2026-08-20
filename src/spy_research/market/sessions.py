"""Typed XNYS session metadata and non-mutating raw-bar classification."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from datetime import UTC, date, datetime, time
from enum import StrEnum
from functools import lru_cache
from zoneinfo import ZoneInfo

import exchange_calendars as xcals
from pydantic import BaseModel, ConfigDict, model_validator

from spy_research.data.schemas import RawBarRecord


NEW_YORK = ZoneInfo("America/New_York")
PREMARKET_OPEN = time(4, 0)
REGULAR_CLOSE = time(16, 0)
AFTER_HOURS_CLOSE = time(20, 0)


class SessionType(StrEnum):
    """Phase 1 session labels, including explicit unexpected-bar states."""

    PREMARKET = "PREMARKET"
    RTH = "RTH"
    AFTER_HOURS = "AFTER_HOURS"
    OUTSIDE_SESSION = "OUTSIDE_SESSION"
    NON_SESSION = "NON_SESSION"


class TradingSession(BaseModel):
    """Authoritative XNYS session metadata for one New York calendar date."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    is_trading_day: bool
    market_open: datetime | None
    market_close: datetime | None
    is_early_close: bool

    @model_validator(mode="after")
    def validate_session_metadata(self) -> "TradingSession":
        boundaries = (self.market_open, self.market_close)
        if self.is_trading_day:
            if any(value is None for value in boundaries):
                raise ValueError("trading sessions require open and close timestamps")
            if any(value.utcoffset() is None for value in boundaries if value is not None):
                raise ValueError("session timestamps must be timezone-aware")
            assert self.market_open is not None and self.market_close is not None
            if self.market_open >= self.market_close:
                raise ValueError("market open must precede market close")
        elif any(value is not None for value in boundaries) or self.is_early_close:
            raise ValueError("non-session dates cannot have exchange boundaries")
        return self


class ClassifiedRawBar(BaseModel):
    """A derived classification wrapper that leaves its raw record untouched."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    bar: RawBarRecord
    session_date: date
    session_type: SessionType


class SessionSummary(BaseModel):
    """Local count and boundary summary for one New York calendar date."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    session: TradingSession
    total_bars: int
    counts: dict[SessionType, int]
    first_rth: datetime | None = None
    last_rth: datetime | None = None
    first_after_hours: datetime | None = None


class XNYSCalendar:
    """Small adapter around the authoritative XNYS exchange calendar."""

    def __init__(self) -> None:
        # Left-closed sessions match one-minute bars stamped at interval start:
        # market open is included and the exchange close itself is excluded.
        self._calendar = xcals.get_calendar("XNYS", side="left")

    @lru_cache(maxsize=512)
    def session_for_date(self, session_date: date) -> TradingSession:
        label = session_date.isoformat()
        if not self._calendar.is_session(label):
            return TradingSession(
                session_date=session_date,
                is_trading_day=False,
                market_open=None,
                market_close=None,
                is_early_close=False,
            )

        market_open = (
            self._calendar.session_open(label).to_pydatetime().astimezone(UTC)
        )
        market_close = (
            self._calendar.session_close(label).to_pydatetime().astimezone(UTC)
        )
        return TradingSession(
            session_date=session_date,
            is_trading_day=True,
            market_open=market_open,
            market_close=market_close,
            is_early_close=market_close.astimezone(NEW_YORK).time() < REGULAR_CLOSE,
        )


class MarketSessionClassifier:
    """Classify raw bars using actual daily XNYS open and close boundaries."""

    def __init__(self, calendar: XNYSCalendar | None = None) -> None:
        self._calendar = calendar or XNYSCalendar()

    def classify(self, bar: RawBarRecord) -> ClassifiedRawBar:
        local_timestamp = bar.timestamp.astimezone(NEW_YORK)
        session_date = local_timestamp.date()
        session = self._calendar.session_for_date(session_date)

        if not session.is_trading_day:
            session_type = SessionType.NON_SESSION
        else:
            assert session.market_open is not None and session.market_close is not None
            premarket_open = datetime.combine(
                session_date, PREMARKET_OPEN, tzinfo=NEW_YORK
            )
            after_hours_close = datetime.combine(
                session_date, AFTER_HOURS_CLOSE, tzinfo=NEW_YORK
            )
            timestamp = bar.timestamp.astimezone(UTC)
            if premarket_open <= local_timestamp < session.market_open:
                session_type = SessionType.PREMARKET
            elif session.market_open <= timestamp < session.market_close:
                session_type = SessionType.RTH
            elif session.market_close <= timestamp < after_hours_close.astimezone(UTC):
                session_type = SessionType.AFTER_HOURS
            else:
                session_type = SessionType.OUTSIDE_SESSION

        return ClassifiedRawBar(
            bar=bar,
            session_date=session_date,
            session_type=session_type,
        )

    def classify_many(
        self, bars: Iterable[RawBarRecord]
    ) -> tuple[ClassifiedRawBar, ...]:
        return tuple(self.classify(bar) for bar in bars)

    def summarize(
        self, session_date: date, bars: Iterable[RawBarRecord]
    ) -> SessionSummary:
        classified = tuple(
            item
            for item in self.classify_many(bars)
            if item.session_date == session_date
        )
        counts = Counter(item.session_type for item in classified)
        rth = [
            item.bar.timestamp
            for item in classified
            if item.session_type is SessionType.RTH
        ]
        after_hours = [
            item.bar.timestamp
            for item in classified
            if item.session_type is SessionType.AFTER_HOURS
        ]
        return SessionSummary(
            session=self._calendar.session_for_date(session_date),
            total_bars=len(classified),
            counts={
                session_type: counts[session_type] for session_type in SessionType
            },
            first_rth=min(rth) if rth else None,
            last_rth=max(rth) if rth else None,
            first_after_hours=min(after_hours) if after_hours else None,
        )
