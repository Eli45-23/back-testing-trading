"""Paginated historical SPY bar retrieval using validated research settings."""

from __future__ import annotations

from datetime import UTC, date, datetime, time
from typing import Any
from zoneinfo import ZoneInfo

from pydantic import ValidationError

from spy_research.alpaca.client import AlpacaDataClient
from spy_research.alpaca.errors import (
    AlpacaPaginationError,
    AlpacaResponseError,
    DuplicateBarError,
)
from spy_research.alpaca.models import HistoricalBarsResult, StockBar
from spy_research.config import ResearchConfig


class HistoricalStockDataService:
    """Fetch raw one-minute SPY bars across every Alpaca response page."""

    def __init__(
        self,
        client: AlpacaDataClient,
        config: ResearchConfig,
        *,
        page_limit: int = 10_000,
        max_pages: int = 10_000,
    ) -> None:
        if not 1 <= page_limit <= 10_000:
            raise ValueError("page_limit must be between 1 and 10000")
        if max_pages < 1:
            raise ValueError("max_pages must be positive")
        self._client = client
        self._config = config
        self._page_limit = page_limit
        self._max_pages = max_pages

    def fetch_stock_bars(
        self,
        *,
        start: date | datetime,
        end: date | datetime,
    ) -> HistoricalBarsResult:
        """Fetch the frozen SPY/1Min/SIP/raw dataset for an explicit range."""

        start_utc, end_utc = self._utc_range(start, end)
        params: dict[str, str | int] = {
            "start": self._format_utc(start_utc),
            "end": self._format_utc(end_utc),
            "timeframe": self._config.data.timeframe,
            "feed": self._config.data.feed,
            "adjustment": self._config.data.adjustment,
            "limit": self._page_limit,
            "sort": "asc",
        }

        bars: list[StockBar] = []
        seen_page_tokens: set[str] = set()
        page_token: str | None = None
        pages_fetched = 0

        while True:
            if pages_fetched >= self._max_pages:
                raise AlpacaPaginationError(
                    f"Alpaca pagination exceeded the safety limit of {self._max_pages} pages"
                )
            request_params = dict(params)
            if page_token is not None:
                request_params["page_token"] = page_token

            payload = self._client.get_json(
                f"/v2/stocks/{self._config.symbol}/bars",
                request_params,
            )
            pages_fetched += 1
            bars.extend(self._parse_page(payload, pages_fetched))

            next_page_token = payload.get("next_page_token")
            if next_page_token is None:
                break
            if not isinstance(next_page_token, str) or not next_page_token:
                raise AlpacaPaginationError(
                    f"Alpaca page {pages_fetched} returned a malformed page token"
                )
            if next_page_token in seen_page_tokens:
                raise AlpacaPaginationError(
                    f"Alpaca repeated a page token after page {pages_fetched}"
                )
            seen_page_tokens.add(next_page_token)
            page_token = next_page_token

        ordered_bars = tuple(sorted(bars, key=lambda bar: bar.timestamp))
        self._validate_unique_timestamps(ordered_bars)
        return HistoricalBarsResult(bars=ordered_bars, pages_fetched=pages_fetched)

    def _parse_page(self, payload: dict[str, Any], page_number: int) -> list[StockBar]:
        response_symbol = payload.get("symbol")
        if response_symbol is not None and response_symbol != self._config.symbol:
            raise AlpacaResponseError(
                f"Alpaca page {page_number} returned an unexpected symbol"
            )
        raw_bars = payload.get("bars")
        if not isinstance(raw_bars, list):
            raise AlpacaResponseError(
                f"Alpaca page {page_number} is missing the expected bars list"
            )

        parsed: list[StockBar] = []
        for index, raw_bar in enumerate(raw_bars):
            if not isinstance(raw_bar, dict):
                raise AlpacaResponseError(
                    f"Alpaca bar {index} on page {page_number} is not an object"
                )
            try:
                parsed.append(
                    StockBar.model_validate({"symbol": self._config.symbol, **raw_bar})
                )
            except ValidationError:
                raise AlpacaResponseError(
                    f"Alpaca bar {index} on page {page_number} has missing or "
                    "invalid required fields"
                ) from None
        return parsed

    @staticmethod
    def _validate_unique_timestamps(bars: tuple[StockBar, ...]) -> None:
        seen: set[datetime] = set()
        for bar in bars:
            if bar.timestamp in seen:
                raise DuplicateBarError(
                    f"Alpaca returned duplicate SPY bar timestamp {bar.timestamp.isoformat()}"
                )
            seen.add(bar.timestamp)

    def _utc_range(
        self,
        start: date | datetime,
        end: date | datetime,
    ) -> tuple[datetime, datetime]:
        timezone = ZoneInfo(self._config.session.timezone)
        if isinstance(start, datetime) != isinstance(end, datetime):
            raise ValueError("start and end must both be dates or both be datetimes")

        if isinstance(start, datetime) and isinstance(end, datetime):
            if start.utcoffset() is None or end.utcoffset() is None:
                raise ValueError("datetime boundaries must be timezone-aware")
            start_utc = start.astimezone(UTC)
            end_utc = end.astimezone(UTC)
        else:
            if start > end:
                raise ValueError("start date must be on or before end date")
            start_utc = datetime.combine(start, time.min, timezone).astimezone(UTC)
            end_utc = datetime.combine(end, time.max, timezone).astimezone(UTC)

        if start_utc > end_utc:
            raise ValueError("start must be on or before end")
        return start_utc, end_utc

    @staticmethod
    def _format_utc(value: datetime) -> str:
        return value.isoformat(timespec="microseconds").replace("+00:00", "Z")
