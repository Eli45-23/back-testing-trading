from datetime import UTC, date, datetime
from decimal import Decimal

import httpx
import pytest
from pydantic import SecretStr

from spy_research.alpaca.client import (
    ALPACA_DATA_BASE_URL,
    AlpacaDataClient,
    RetryConfig,
)
from spy_research.alpaca.errors import (
    AlpacaAuthenticationError,
    AlpacaPaginationError,
    AlpacaRateLimitError,
    AlpacaRequestError,
    AlpacaResponseError,
    DuplicateBarError,
)
from spy_research.alpaca.historical import HistoricalStockDataService
from spy_research.config import load_research_config


API_KEY = "mock-api-key-never-log"
SECRET_KEY = "mock-secret-key-never-log"
START_DATE = date(2026, 8, 3)
END_DATE = date(2026, 8, 4)


def raw_bar(timestamp: str, price: float = 100.0) -> dict[str, object]:
    return {
        "t": timestamp,
        "o": price,
        "h": price + 1,
        "l": price - 1,
        "c": price + 0.5,
        "v": 1000,
        "n": 20,
        "vw": price + 0.25,
    }


def make_service(
    handler,
    *,
    retry: RetryConfig | None = None,
    sleep=lambda delay: None,
    page_limit: int = 10_000,
) -> tuple[HistoricalStockDataService, httpx.Client]:
    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(base_url=ALPACA_DATA_BASE_URL, transport=transport)
    client = AlpacaDataClient(
        api_key=SecretStr(API_KEY),
        secret_key=SecretStr(SECRET_KEY),
        retry=retry or RetryConfig(max_retries=0),
        http_client=http_client,
        sleep=sleep,
    )
    service = HistoricalStockDataService(
        client,
        load_research_config(),
        page_limit=page_limit,
    )
    return service, http_client


def fetch(service: HistoricalStockDataService):
    return service.fetch_stock_bars(start=START_DATE, end=END_DATE)


def test_request_construction_authentication_and_frozen_parameters() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/v2/stocks/SPY/bars"
        assert request.headers["APCA-API-KEY-ID"] == API_KEY
        assert request.headers["APCA-API-SECRET-KEY"] == SECRET_KEY
        assert request.url.params["timeframe"] == "1Min"
        assert request.url.params["feed"] == "sip"
        assert request.url.params["adjustment"] == "raw"
        assert request.url.params["sort"] == "asc"
        assert request.url.params["limit"] == "37"
        assert request.url.params["start"] == "2026-08-03T04:00:00.000000Z"
        assert request.url.params["end"] == "2026-08-05T03:59:59.999999Z"
        return httpx.Response(200, json={"bars": [], "symbol": "SPY"})

    service, http_client = make_service(handler, page_limit=37)
    try:
        result = fetch(service)
    finally:
        http_client.close()

    assert result.pages_fetched == 1
    assert result.bars == ()


def test_single_page_response_parses_typed_raw_bar() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"bars": [raw_bar("2026-08-03T13:30:00Z")], "symbol": "SPY"},
        )

    service, http_client = make_service(handler)
    try:
        result = fetch(service)
    finally:
        http_client.close()

    assert len(result.bars) == 1
    assert result.bars[0].symbol == "SPY"
    assert result.bars[0].timestamp == datetime(2026, 8, 3, 13, 30, tzinfo=UTC)
    assert result.bars[0].timestamp.utcoffset() is not None
    assert result.bars[0].open == Decimal("100.0")
    assert result.bars[0].trade_count == 20


def test_multi_page_response_uses_tokens_and_sorts_chronologically() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if len(requests) == 1:
            return httpx.Response(
                200,
                json={
                    "bars": [raw_bar("2026-08-03T13:31:00Z")],
                    "next_page_token": "page-two",
                },
            )
        assert request.url.params["page_token"] == "page-two"
        return httpx.Response(
            200,
            json={"bars": [raw_bar("2026-08-03T13:30:00Z")]},
        )

    service, http_client = make_service(handler)
    try:
        result = fetch(service)
    finally:
        http_client.close()

    assert result.pages_fetched == 2
    assert [bar.timestamp.minute for bar in result.bars] == [30, 31]


def test_repeated_pagination_token_is_rejected() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            200,
            json={"bars": [], "next_page_token": "repeated-token"},
        )

    service, http_client = make_service(handler)
    try:
        with pytest.raises(AlpacaPaginationError, match="repeated a page token"):
            fetch(service)
    finally:
        http_client.close()

    assert calls == 2


def test_malformed_pagination_token_is_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"bars": [], "next_page_token": 123})

    service, http_client = make_service(handler)
    try:
        with pytest.raises(AlpacaPaginationError, match="malformed page token"):
            fetch(service)
    finally:
        http_client.close()


def test_duplicate_timestamp_is_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        timestamp = "2026-08-03T13:30:00Z"
        return httpx.Response(200, json={"bars": [raw_bar(timestamp), raw_bar(timestamp)]})

    service, http_client = make_service(handler)
    try:
        with pytest.raises(DuplicateBarError, match="duplicate SPY bar timestamp"):
            fetch(service)
    finally:
        http_client.close()


def test_malformed_json_is_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"{malformed")

    service, http_client = make_service(handler)
    try:
        with pytest.raises(AlpacaResponseError, match="malformed JSON"):
            fetch(service)
    finally:
        http_client.close()


def test_missing_required_bar_field_is_rejected() -> None:
    incomplete_bar = raw_bar("2026-08-03T13:30:00Z")
    incomplete_bar.pop("c")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"bars": [incomplete_bar]})

    service, http_client = make_service(handler)
    try:
        with pytest.raises(AlpacaResponseError, match="missing or invalid required fields"):
            fetch(service)
    finally:
        http_client.close()


@pytest.mark.parametrize("status_code", [401, 403])
def test_authentication_and_entitlement_failures_are_not_retried(status_code: int) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(status_code)

    service, http_client = make_service(
        handler,
        retry=RetryConfig(max_retries=3, backoff_factor=0),
    )
    try:
        with pytest.raises(AlpacaAuthenticationError, match=f"HTTP {status_code}"):
            fetch(service)
    finally:
        http_client.close()

    assert calls == 1


def test_429_retries_then_succeeds_and_honors_retry_after() -> None:
    calls = 0
    delays: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls < 3:
            return httpx.Response(429, headers={"Retry-After": "2"})
        return httpx.Response(200, json={"bars": []})

    service, http_client = make_service(
        handler,
        retry=RetryConfig(max_retries=2, backoff_factor=0.1),
        sleep=delays.append,
    )
    try:
        result = fetch(service)
    finally:
        http_client.close()

    assert result.pages_fetched == 1
    assert calls == 3
    assert delays == [2.0, 2.0]


@pytest.mark.parametrize("status_code", [500, 502, 503])
def test_selected_server_errors_are_retried(status_code: int) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(status_code)
        return httpx.Response(200, json={"bars": []})

    service, http_client = make_service(
        handler,
        retry=RetryConfig(max_retries=1, backoff_factor=0),
    )
    try:
        fetch(service)
    finally:
        http_client.close()

    assert calls == 2


def test_timeout_is_retried_then_succeeds() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise httpx.ReadTimeout("mock timeout", request=request)
        return httpx.Response(200, json={"bars": []})

    service, http_client = make_service(
        handler,
        retry=RetryConfig(max_retries=1, backoff_factor=0),
    )
    try:
        fetch(service)
    finally:
        http_client.close()

    assert calls == 2


def test_bounded_timeout_retry_exhaustion() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ReadTimeout("mock timeout", request=request)

    service, http_client = make_service(
        handler,
        retry=RetryConfig(max_retries=2, backoff_factor=0),
    )
    try:
        with pytest.raises(AlpacaRequestError, match="after 3 attempts"):
            fetch(service)
    finally:
        http_client.close()

    assert calls == 3


def test_rate_limit_retry_exhaustion_uses_specific_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429)

    service, http_client = make_service(
        handler,
        retry=RetryConfig(max_retries=1, backoff_factor=0),
    )
    try:
        with pytest.raises(AlpacaRateLimitError, match="after 2 attempts"):
            fetch(service)
    finally:
        http_client.close()


def test_credentials_never_appear_in_logs_or_exceptions(caplog) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    service, http_client = make_service(
        handler,
        retry=RetryConfig(max_retries=1, backoff_factor=0),
    )
    try:
        with caplog.at_level("WARNING"):
            with pytest.raises(AlpacaRequestError) as error:
                fetch(service)
    finally:
        http_client.close()

    combined_output = str(error.value) + caplog.text
    assert API_KEY not in combined_output
    assert SECRET_KEY not in combined_output
    assert "APCA-API-KEY-ID" not in combined_output
    assert "APCA-API-SECRET-KEY" not in combined_output


def test_permanent_request_failure_is_not_retried() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(400)

    service, http_client = make_service(
        handler,
        retry=RetryConfig(max_retries=3, backoff_factor=0),
    )
    try:
        with pytest.raises(AlpacaRequestError, match="HTTP 400"):
            fetch(service)
    finally:
        http_client.close()

    assert calls == 1
