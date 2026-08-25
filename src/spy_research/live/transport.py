"""Alpaca SIP WebSocket transport with bounded reconnects and no trade API."""

from __future__ import annotations

import json
import ssl
from collections.abc import Callable, Iterator, Mapping
from decimal import Decimal
from typing import Any, Protocol

import certifi
from pydantic import SecretStr
from websockets.exceptions import ConnectionClosed
from websockets.sync.client import connect

from spy_research.config import AlpacaEnvironment
from spy_research.live.models import (
    ALPACA_SIP_STREAM_URL,
    LiveAuthenticationError,
    LiveTransportError,
)
from spy_research.logging_config import register_sensitive_values


class LiveMessageTransport(Protocol):
    def messages(self) -> Iterator[Mapping[str, Any]]: ...


class AlpacaSipWebSocketTransport:
    """Authenticate and subscribe only to final SPY minute bars on SIP."""

    endpoint = ALPACA_SIP_STREAM_URL

    def __init__(
        self,
        *,
        api_key: SecretStr,
        secret_key: SecretStr,
        max_reconnects: int = 3,
        handshake_timeout_seconds: float = 10.0,
        ssl_context: ssl.SSLContext | None = None,
        connector: Callable[..., Any] = connect,
    ) -> None:
        if max_reconnects < 0:
            raise ValueError("max_reconnects must be non-negative")
        if handshake_timeout_seconds <= 0:
            raise ValueError("handshake_timeout_seconds must be positive")
        self._api_key = api_key
        self._secret_key = secret_key
        self._max_reconnects = max_reconnects
        self._handshake_timeout_seconds = handshake_timeout_seconds
        self._ssl_context = ssl_context or _verified_ssl_context()
        _require_secure_tls(self._ssl_context)
        self._connector = connector
        register_sensitive_values(
            (api_key.get_secret_value(), secret_key.get_secret_value())
        )

    @classmethod
    def from_environment(cls, environment: AlpacaEnvironment, **kwargs):
        if environment.api_key is None or environment.secret_key is None:
            raise LiveAuthenticationError(
                "Alpaca market-data credentials are required in the local .env file"
            )
        return cls(
            api_key=environment.api_key,
            secret_key=environment.secret_key,
            **kwargs,
        )

    def messages(self) -> Iterator[Mapping[str, Any]]:
        reconnects = 0
        while True:
            try:
                with self._connector(
                    self.endpoint,
                    ssl=self._ssl_context,
                ) as websocket:
                    self._await_connected(websocket)
                    websocket.send(
                        json.dumps(
                            {
                                "action": "auth",
                                "key": self._api_key.get_secret_value(),
                                "secret": self._secret_key.get_secret_value(),
                            }
                        )
                    )
                    self._await_authenticated(websocket)
                    websocket.send(
                        json.dumps({"action": "subscribe", "bars": ["SPY"]})
                    )
                    self._await_subscription(websocket)
                    while True:
                        for message in self._decode(websocket.recv()):
                            if message.get("T") == "b":
                                yield message
            except LiveAuthenticationError:
                raise
            except (ConnectionClosed, OSError, TimeoutError):
                if reconnects >= self._max_reconnects:
                    raise LiveTransportError(
                        "Alpaca SIP stream disconnected after bounded reconnect attempts"
                    ) from None
                reconnects += 1

    def _await_authenticated(self, websocket) -> None:
        message = self._handshake_message(websocket, expected_state="authenticated")
        if message.get("T") == "success" and message.get("msg") == "authenticated":
            return
        if message.get("T") == "error":
            raise LiveAuthenticationError("Alpaca rejected data-stream authentication")
        raise LiveAuthenticationError(
            "Alpaca returned an invalid authenticated-state transition"
        )

    def _await_connected(self, websocket) -> None:
        message = self._handshake_message(websocket, expected_state="connected")
        if message.get("T") == "success" and message.get("msg") == "connected":
            return
        if message.get("T") == "error":
            raise LiveAuthenticationError("Alpaca rejected the data-stream connection")
        raise LiveAuthenticationError(
            "Alpaca returned an invalid connected-state transition"
        )

    def _handshake_message(self, websocket, *, expected_state: str) -> Mapping[str, Any]:
        try:
            raw = websocket.recv(timeout=self._handshake_timeout_seconds)
        except TimeoutError:
            raise LiveAuthenticationError(
                f"Alpaca SIP handshake timed out waiting for {expected_state}"
            ) from None
        messages = self._decode(raw)
        if len(messages) != 1:
            raise LiveAuthenticationError(
                f"Alpaca returned an invalid {expected_state} handshake frame"
            )
        return messages[0]

    def _await_subscription(self, websocket) -> None:
        for message in self._decode(websocket.recv()):
            if message.get("T") == "subscription" and "SPY" in message.get("bars", []):
                return
            if message.get("T") == "error":
                raise LiveTransportError("Alpaca rejected the SPY SIP bar subscription")
        raise LiveTransportError("Alpaca returned an invalid subscription response")

    @staticmethod
    def _decode(raw: str | bytes) -> tuple[Mapping[str, Any], ...]:
        try:
            payload = json.loads(raw, parse_float=Decimal)
        except (TypeError, ValueError):
            raise LiveTransportError("Alpaca SIP stream returned malformed JSON") from None
        if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
            raise LiveTransportError("Alpaca SIP stream returned an invalid message batch")
        return tuple(payload)


def _verified_ssl_context() -> ssl.SSLContext:
    """Build the production client context from a maintained trusted CA bundle."""

    try:
        context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH,
            cafile=certifi.where(),
        )
    except (OSError, ssl.SSLError):
        raise LiveTransportError(
            "Alpaca SIP TLS context could not load the trusted CA bundle"
        ) from None
    _require_secure_tls(context)
    return context


def _require_secure_tls(context: ssl.SSLContext) -> None:
    if context.verify_mode != ssl.CERT_REQUIRED or not context.check_hostname:
        raise LiveTransportError(
            "Alpaca SIP TLS requires certificate and hostname verification"
        )
