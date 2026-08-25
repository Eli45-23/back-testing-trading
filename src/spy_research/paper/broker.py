"""Fail-closed Alpaca paper REST adapter for Stage 14.4."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Protocol

import httpx
from pydantic import SecretStr

from spy_research.config import AlpacaEnvironment
from spy_research.logging_config import register_sensitive_values
from spy_research.paper.models import (
    ALPACA_PAPER_BASE_URL,
    BrokerOrderRecord,
    BrokerOrderRole,
    BrokerOrderStatus,
    BrokerPositionRecord,
    BrokerProtectiveOrders,
    PaperExecutionError,
)


class PaperBrokerSession(Protocol):
    """Only the paper-account operations required by the execution state machine."""

    def verify_paper_account(self) -> None: ...

    def find_order_by_client_id(
        self, client_order_id: str, *, role: BrokerOrderRole
    ) -> BrokerOrderRecord | None: ...

    def get_order(
        self, broker_order_id: str, *, role: BrokerOrderRole
    ) -> BrokerOrderRecord: ...

    def list_open_orders(self) -> tuple[BrokerOrderRecord, ...]: ...

    def get_position(self, *, observed_at: datetime) -> BrokerPositionRecord: ...

    def submit_market_entry(
        self, *, qty: int, client_order_id: str
    ) -> BrokerOrderRecord: ...

    def submit_protective_oco(
        self,
        *,
        qty: int,
        target_price: Decimal,
        stop_price: Decimal,
        client_order_id: str,
    ) -> BrokerProtectiveOrders: ...

    def cancel_order(self, broker_order_id: str) -> None: ...

    def submit_market_flatten(
        self, *, qty: int, client_order_id: str
    ) -> BrokerOrderRecord: ...


class AlpacaPaperBroker:
    """Stock-order adapter permanently pinned to Alpaca's paper endpoint."""

    base_url = ALPACA_PAPER_BASE_URL

    def __init__(
        self,
        *,
        api_key: SecretStr,
        secret_key: SecretStr,
        timeout: float = 10.0,
        base_url: str = ALPACA_PAPER_BASE_URL,
        client: httpx.Client | None = None,
    ) -> None:
        normalized = base_url.rstrip("/")
        if normalized != ALPACA_PAPER_BASE_URL:
            raise PaperExecutionError(
                "paper execution requires the fixed Alpaca paper-trading endpoint"
            )
        if client is not None and str(client.base_url).rstrip("/") != ALPACA_PAPER_BASE_URL:
            raise PaperExecutionError(
                "injected broker client is not pinned to the Alpaca paper endpoint"
            )
        if timeout <= 0:
            raise ValueError("paper broker timeout must be positive")
        self._api_key = api_key
        self._secret_key = secret_key
        self._client = client or httpx.Client(
            base_url=ALPACA_PAPER_BASE_URL,
            timeout=timeout,
            headers={
                "APCA-API-KEY-ID": api_key.get_secret_value(),
                "APCA-API-SECRET-KEY": secret_key.get_secret_value(),
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        self._owns_client = client is None
        register_sensitive_values(
            (api_key.get_secret_value(), secret_key.get_secret_value())
        )

    @classmethod
    def from_environment(cls, environment: AlpacaEnvironment, **kwargs):
        if environment.paper_api_key is None or environment.paper_secret_key is None:
            raise PaperExecutionError(
                "Alpaca paper credentials are required in the local .env file"
            )
        return cls(
            api_key=environment.paper_api_key,
            secret_key=environment.paper_secret_key,
            **kwargs,
        )

    def __enter__(self) -> "AlpacaPaperBroker":
        return self

    def __exit__(self, *_args) -> None:
        if self._owns_client:
            self._client.close()

    def verify_paper_account(self) -> None:
        response = self._raw_request("GET", "/v2/account")
        if response.status_code == 401:
            raise PaperExecutionError(
                "configured credentials are not authorized for the Alpaca "
                "paper account (HTTP 401)"
            )
        payload = self._validated_response(response)
        if not isinstance(payload, Mapping):
            raise PaperExecutionError("paper account response is invalid")
        if payload.get("status") != "ACTIVE":
            raise PaperExecutionError("Alpaca paper account is not active")
        if payload.get("account_blocked") or payload.get("trading_blocked"):
            raise PaperExecutionError("Alpaca paper account is blocked")

    def find_order_by_client_id(
        self, client_order_id: str, *, role: BrokerOrderRole
    ) -> BrokerOrderRecord | None:
        response = self._raw_request(
            "GET",
            "/v2/orders:by_client_order_id",
            params={"client_order_id": client_order_id},
        )
        if response.status_code == 404:
            return None
        payload = self._validated_response(response)
        return self._parse_order(payload, role=role)

    def list_open_orders(self) -> tuple[BrokerOrderRecord, ...]:
        payload = self._request(
            "GET",
            "/v2/orders",
            params={"status": "open", "nested": "true", "symbols": "SPY"},
        )
        if not isinstance(payload, list):
            raise PaperExecutionError("paper open-order response is invalid")
        records: list[BrokerOrderRecord] = []
        for item in payload:
            if not isinstance(item, Mapping):
                raise PaperExecutionError("paper open-order item is invalid")
            role = self._infer_role(item)
            records.append(self._parse_order(item, role=role))
            for leg in item.get("legs") or ():
                if not isinstance(leg, Mapping):
                    raise PaperExecutionError("paper OCO leg is invalid")
                records.append(self._parse_order(leg, role=self._infer_role(leg)))
        return tuple(records)

    def get_order(
        self, broker_order_id: str, *, role: BrokerOrderRole
    ) -> BrokerOrderRecord:
        payload = self._request("GET", f"/v2/orders/{broker_order_id}")
        return self._parse_order(payload, role=role)

    def get_position(self, *, observed_at: datetime) -> BrokerPositionRecord:
        response = self._raw_request("GET", "/v2/positions/SPY")
        if response.status_code == 404:
            return BrokerPositionRecord(qty=Decimal("0"), observed_at=observed_at)
        payload = self._validated_response(response)
        if not isinstance(payload, Mapping) or payload.get("symbol") != "SPY":
            raise PaperExecutionError("paper position response is invalid")
        try:
            qty = Decimal(str(payload["qty"]))
            side = payload.get("side")
        except (KeyError, ValueError):
            raise PaperExecutionError("paper position quantity is invalid") from None
        if side == "short" and qty > 0:
            qty = -qty
        if side == "long" and qty < 0:
            raise PaperExecutionError("paper position side and quantity conflict")
        return BrokerPositionRecord(qty=qty, observed_at=observed_at)

    def submit_market_entry(
        self, *, qty: int, client_order_id: str
    ) -> BrokerOrderRecord:
        payload = self._request(
            "POST",
            "/v2/orders",
            json={
                "symbol": "SPY",
                "qty": str(qty),
                "side": "sell",
                "type": "market",
                "time_in_force": "day",
                "client_order_id": client_order_id,
                "extended_hours": False,
            },
        )
        return self._parse_order(payload, role=BrokerOrderRole.ENTRY)

    def submit_protective_oco(
        self,
        *,
        qty: int,
        target_price: Decimal,
        stop_price: Decimal,
        client_order_id: str,
    ) -> BrokerProtectiveOrders:
        payload = self._request(
            "POST",
            "/v2/orders",
            json={
                "symbol": "SPY",
                "qty": str(qty),
                "side": "buy",
                "type": "limit",
                "time_in_force": "day",
                "order_class": "oco",
                "client_order_id": client_order_id,
                "take_profit": {"limit_price": str(target_price)},
                "stop_loss": {"stop_price": str(stop_price)},
                "extended_hours": False,
            },
        )
        if not isinstance(payload, Mapping):
            raise PaperExecutionError("paper OCO response is invalid")
        members = [payload, *(payload.get("legs") or ())]
        target = stop = None
        for item in members:
            if not isinstance(item, Mapping):
                raise PaperExecutionError("paper OCO member is invalid")
            item_type = str(item.get("type") or item.get("order_type") or "")
            if item_type == "limit":
                target = self._parse_order(item, role=BrokerOrderRole.TARGET)
            elif item_type in {"stop", "stop_limit"}:
                stop = self._parse_order(item, role=BrokerOrderRole.STOP)
        if target is None or stop is None:
            raise PaperExecutionError("paper OCO response lacks target or stop leg")
        return BrokerProtectiveOrders(
            oco_client_order_id=client_order_id,
            target=target,
            stop=stop,
        )

    def cancel_order(self, broker_order_id: str) -> None:
        response = self._raw_request("DELETE", f"/v2/orders/{broker_order_id}")
        if response.status_code not in (204, 404):
            self._validated_response(response)

    def submit_market_flatten(
        self, *, qty: int, client_order_id: str
    ) -> BrokerOrderRecord:
        payload = self._request(
            "POST",
            "/v2/orders",
            json={
                "symbol": "SPY",
                "qty": str(qty),
                "side": "buy",
                "type": "market",
                "time_in_force": "day",
                "client_order_id": client_order_id,
                "extended_hours": False,
            },
        )
        return self._parse_order(payload, role=BrokerOrderRole.EOD_FLATTEN)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        response = self._raw_request(method, path, **kwargs)
        return self._validated_response(response)

    def _raw_request(self, method: str, path: str, **kwargs) -> httpx.Response:
        try:
            response = self._client.request(method, path, **kwargs)
        except (httpx.HTTPError, OSError, TimeoutError):
            raise PaperExecutionError("Alpaca paper broker request failed") from None
        return response

    @staticmethod
    def _validated_response(response: httpx.Response) -> Any:
        if response.status_code >= 400:
            raise PaperExecutionError(
                f"Alpaca paper broker rejected request with HTTP {response.status_code}"
            )
        try:
            return response.json()
        except ValueError:
            raise PaperExecutionError("Alpaca paper broker returned invalid JSON") from None

    @classmethod
    def _parse_order(
        cls, payload: Any, *, role: BrokerOrderRole
    ) -> BrokerOrderRecord:
        if not isinstance(payload, Mapping) or payload.get("symbol") != "SPY":
            raise PaperExecutionError("paper order response is invalid or non-SPY")
        try:
            submitted_at = cls._datetime(payload["submitted_at"])
            filled_at = (
                cls._datetime(payload["filled_at"])
                if payload.get("filled_at") is not None
                else None
            )
            order_type = str(payload.get("type") or payload.get("order_type"))
            return BrokerOrderRecord(
                broker_order_id=str(payload["id"]),
                client_order_id=str(payload["client_order_id"]),
                side=str(payload["side"]),
                order_type=order_type,
                role=role,
                status=cls._status(str(payload["status"])),
                qty=int(Decimal(str(payload["qty"]))),
                filled_qty=Decimal(str(payload.get("filled_qty") or "0")),
                avg_fill_price=(
                    Decimal(str(payload["filled_avg_price"]))
                    if payload.get("filled_avg_price") is not None
                    else None
                ),
                submitted_at=submitted_at,
                filled_at=filled_at,
                limit_price=(
                    Decimal(str(payload["limit_price"]))
                    if payload.get("limit_price") is not None
                    else None
                ),
                stop_price=(
                    Decimal(str(payload["stop_price"]))
                    if payload.get("stop_price") is not None
                    else None
                ),
            )
        except (KeyError, TypeError, ValueError):
            raise PaperExecutionError("paper order response fields are invalid") from None

    @staticmethod
    def _datetime(value: Any) -> datetime:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.utcoffset() is None:
            raise ValueError("broker timestamp lacks timezone")
        return parsed.astimezone(UTC)

    @staticmethod
    def _status(value: str) -> BrokerOrderStatus:
        mapping = {
            "new": BrokerOrderStatus.NEW,
            "accepted": BrokerOrderStatus.ACCEPTED,
            "pending_new": BrokerOrderStatus.ACCEPTED,
            "accepted_for_bidding": BrokerOrderStatus.ACCEPTED,
            "partially_filled": BrokerOrderStatus.PARTIALLY_FILLED,
            "filled": BrokerOrderStatus.FILLED,
            "pending_cancel": BrokerOrderStatus.PENDING_CANCEL,
            "canceled": BrokerOrderStatus.CANCELED,
            "done_for_day": BrokerOrderStatus.CANCELED,
            "replaced": BrokerOrderStatus.CANCELED,
            "rejected": BrokerOrderStatus.REJECTED,
            "expired": BrokerOrderStatus.EXPIRED,
            "stopped": BrokerOrderStatus.EXPIRED,
            "suspended": BrokerOrderStatus.REJECTED,
            "calculated": BrokerOrderStatus.ACCEPTED,
        }
        try:
            return mapping[value]
        except KeyError:
            raise PaperExecutionError("paper order returned an unknown status") from None

    @staticmethod
    def _infer_role(payload: Mapping[str, Any]) -> BrokerOrderRole:
        side = payload.get("side")
        order_type = payload.get("type") or payload.get("order_type")
        if side == "sell" and order_type == "market":
            return BrokerOrderRole.ENTRY
        if side == "buy" and order_type == "limit":
            return BrokerOrderRole.TARGET
        if side == "buy" and order_type in {"stop", "stop_limit"}:
            return BrokerOrderRole.STOP
        if side == "buy" and order_type == "market":
            return BrokerOrderRole.EOD_FLATTEN
        raise PaperExecutionError("paper open order has an unsupported role")
