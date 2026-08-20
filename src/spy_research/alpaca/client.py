"""Reusable authenticated HTTP client with bounded transient retries."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Self

import httpx
from pydantic import SecretStr

from spy_research.alpaca.errors import (
    AlpacaAuthenticationError,
    AlpacaCredentialsError,
    AlpacaRateLimitError,
    AlpacaRequestError,
    AlpacaResponseError,
)
from spy_research.config import AlpacaEnvironment
from spy_research.logging_config import register_sensitive_values


logger = logging.getLogger(__name__)
ALPACA_DATA_BASE_URL = "https://data.alpaca.markets"
TRANSIENT_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


@dataclass(frozen=True, slots=True)
class RetryConfig:
    """Explicit retry limits; ``max_retries`` excludes the first attempt."""

    max_retries: int = 3
    backoff_factor: float = 0.5
    max_backoff_seconds: float = 8.0

    def __post_init__(self) -> None:
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.backoff_factor < 0 or self.max_backoff_seconds < 0:
            raise ValueError("retry backoff values must be non-negative")


class AlpacaDataClient:
    """Small synchronous HTTP client for Alpaca's historical data API."""

    def __init__(
        self,
        *,
        api_key: SecretStr,
        secret_key: SecretStr,
        timeout: float = 10.0,
        retry: RetryConfig | None = None,
        http_client: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self._api_key = api_key
        self._secret_key = secret_key
        self._retry = retry or RetryConfig()
        self._sleep = sleep
        self._owns_http_client = http_client is None
        self._http_client = http_client or httpx.Client(
            base_url=ALPACA_DATA_BASE_URL,
            timeout=httpx.Timeout(timeout),
        )
        register_sensitive_values(
            (api_key.get_secret_value(), secret_key.get_secret_value())
        )

    @classmethod
    def from_environment(
        cls,
        environment: AlpacaEnvironment,
        **kwargs: Any,
    ) -> Self:
        if environment.api_key is None or environment.secret_key is None:
            raise AlpacaCredentialsError(
                "Alpaca credentials are required; configure ALPACA_API_KEY and "
                "ALPACA_SECRET_KEY in the local .env file"
            )
        return cls(
            api_key=environment.api_key,
            secret_key=environment.secret_key,
            **kwargs,
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_http_client:
            self._http_client.close()

    def get_json(self, path: str, params: Mapping[str, str | int]) -> dict[str, Any]:
        """GET a JSON object, retrying only bounded transient failures."""

        total_attempts = self._retry.max_retries + 1
        for attempt in range(total_attempts):
            try:
                response = self._http_client.get(
                    path,
                    params=params,
                    headers=self._authentication_headers(),
                )
            except httpx.TransportError:
                if attempt < self._retry.max_retries:
                    self._log_and_wait(attempt, "transport failure")
                    continue
                raise AlpacaRequestError(
                    f"Alpaca request failed after {total_attempts} attempts "
                    "because of a transport error"
                ) from None

            if response.status_code in TRANSIENT_STATUS_CODES:
                if attempt < self._retry.max_retries:
                    self._log_and_wait(
                        attempt,
                        f"HTTP {response.status_code}",
                        retry_after=response.headers.get("Retry-After"),
                    )
                    continue
                if response.status_code == 429:
                    raise AlpacaRateLimitError(
                        f"Alpaca rate limit persisted after {total_attempts} attempts"
                    )
                raise AlpacaRequestError(
                    f"Alpaca returned HTTP {response.status_code} after "
                    f"{total_attempts} attempts"
                )

            if response.status_code in {401, 403}:
                raise AlpacaAuthenticationError(
                    f"Alpaca rejected authentication or SIP entitlement "
                    f"with HTTP {response.status_code}"
                )
            if response.is_error:
                raise AlpacaRequestError(
                    f"Alpaca rejected the historical-data request with "
                    f"HTTP {response.status_code}"
                )

            try:
                payload = response.json()
            except (ValueError, UnicodeDecodeError):
                raise AlpacaResponseError(
                    "Alpaca returned malformed JSON for a successful request"
                ) from None
            if not isinstance(payload, dict):
                raise AlpacaResponseError("Alpaca response must be a JSON object")
            return payload

        raise AssertionError("retry loop exited unexpectedly")

    def _authentication_headers(self) -> dict[str, str]:
        return {
            "APCA-API-KEY-ID": self._api_key.get_secret_value(),
            "APCA-API-SECRET-KEY": self._secret_key.get_secret_value(),
        }

    def _log_and_wait(
        self,
        attempt: int,
        reason: str,
        *,
        retry_after: str | None = None,
    ) -> None:
        delay = self._backoff_delay(attempt, retry_after)
        logger.warning(
            "Transient Alpaca %s; retrying in %.2fs (%d/%d)",
            reason,
            delay,
            attempt + 1,
            self._retry.max_retries,
        )
        self._sleep(delay)

    def _backoff_delay(self, attempt: int, retry_after: str | None) -> float:
        if retry_after is not None:
            try:
                parsed_retry_after = float(retry_after)
            except ValueError:
                pass
            else:
                if parsed_retry_after >= 0:
                    return min(parsed_retry_after, self._retry.max_backoff_seconds)
        exponential = self._retry.backoff_factor * (2**attempt)
        return min(exponential, self._retry.max_backoff_seconds)
