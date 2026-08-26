"""Immutable Stage 14.4 paper-execution records."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, localcontext
from enum import StrEnum
from hashlib import sha256
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.indicators.atr import ATR_CONTEXT
from spy_research.replay import STAGE14_FORWARD_CANDIDATE_IDS


ALPACA_PAPER_BASE_URL = "https://paper-api.alpaca.markets"


class PaperExecutionError(RuntimeError):
    """Paper state cannot be reconciled without risking an invalid order."""


class PaperCandidate(StrEnum):
    ATR_0_75 = "ATR_0_75"
    ATR_1_00 = "ATR_1_00"

    @property
    def candidate_id(self) -> str:
        return {
            PaperCandidate.ATR_0_75: STAGE14_FORWARD_CANDIDATE_IDS[0],
            PaperCandidate.ATR_1_00: STAGE14_FORWARD_CANDIDATE_IDS[1],
        }[self]

    @property
    def stop_multiplier(self) -> Decimal:
        return {
            PaperCandidate.ATR_0_75: Decimal("0.75"),
            PaperCandidate.ATR_1_00: Decimal("1.00"),
        }[self]


class BrokerOrderStatus(StrEnum):
    NEW = "NEW"
    ACCEPTED = "ACCEPTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    PENDING_CANCEL = "PENDING_CANCEL"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


TERMINAL_BROKER_ORDER_STATUSES = frozenset(
    {
        BrokerOrderStatus.FILLED,
        BrokerOrderStatus.CANCELED,
        BrokerOrderStatus.REJECTED,
        BrokerOrderStatus.EXPIRED,
    }
)


class BrokerOrderRole(StrEnum):
    ENTRY = "ENTRY"
    PROTECTIVE_OCO = "PROTECTIVE_OCO"
    TARGET = "TARGET"
    STOP = "STOP"
    EOD_FLATTEN = "EOD_FLATTEN"


class BrokerOrderRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    broker_order_id: str = Field(min_length=1)
    client_order_id: str = Field(min_length=1)
    symbol: Literal["SPY"] = "SPY"
    side: Literal["buy", "sell"]
    order_type: Literal["market", "limit", "stop", "stop_limit"]
    role: BrokerOrderRole
    status: BrokerOrderStatus
    qty: int = Field(gt=0)
    filled_qty: Decimal = Field(ge=0)
    avg_fill_price: Decimal | None = None
    submitted_at: datetime
    filled_at: datetime | None = None
    limit_price: Decimal | None = None
    stop_price: Decimal | None = None

    @model_validator(mode="after")
    def reconcile_fill(self) -> Self:
        if self.submitted_at.utcoffset() is None:
            raise ValueError("broker timestamps must be timezone-aware")
        if self.filled_qty > self.qty:
            raise ValueError("broker fill exceeds intended whole-share quantity")
        if self.status is BrokerOrderStatus.FILLED:
            if self.filled_qty != self.qty or self.avg_fill_price is None:
                raise ValueError("filled broker order requires complete fill details")
            if self.filled_at is None or self.filled_at.utcoffset() is None:
                raise ValueError("filled broker order requires an aware fill timestamp")
            if self.filled_at < self.submitted_at:
                raise ValueError("broker fill cannot precede broker submission")
        elif self.filled_at is not None and self.filled_at.utcoffset() is None:
            raise ValueError("broker fill timestamp must be timezone-aware")
        if self.avg_fill_price is not None and self.avg_fill_price <= 0:
            raise ValueError("broker fill price must be positive")
        return self


class BrokerProtectiveOrders(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    oco_client_order_id: str
    target: BrokerOrderRecord
    stop: BrokerOrderRecord

    @model_validator(mode="after")
    def reconcile(self) -> Self:
        if self.target.role is not BrokerOrderRole.TARGET:
            raise ValueError("protective target role changed")
        if self.stop.role is not BrokerOrderRole.STOP:
            raise ValueError("protective stop role changed")
        if self.target.side != "buy" or self.stop.side != "buy":
            raise ValueError("short protective exits must both buy to cover")
        if self.target.qty != self.stop.qty:
            raise ValueError("protective OCO quantities must match")
        return self


class BrokerPositionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    qty: Decimal
    observed_at: datetime

    @model_validator(mode="after")
    def timestamp_is_aware(self) -> Self:
        if self.observed_at.utcoffset() is None:
            raise ValueError("broker position observation must be timezone-aware")
        return self


class PaperExecutionState(StrEnum):
    DRY_RUN_INTENDED = "DRY_RUN_INTENDED"
    ENTRY_SUBMITTED = "ENTRY_SUBMITTED"
    ENTRY_FILLED_UNPROTECTED = "ENTRY_FILLED_UNPROTECTED"
    PROTECTIVE_ACTIVE = "PROTECTIVE_ACTIVE"
    TARGET_FILLED = "TARGET_FILLED"
    STOP_FILLED = "STOP_FILLED"
    EOD_FLATTEN_SUBMITTED = "EOD_FLATTEN_SUBMITTED"
    FLAT = "FLAT"
    BLOCKED = "BLOCKED"


class PaperExecutionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    setup_identity: str
    candidate_id: str
    intended_side: Literal["sell"] = "sell"
    intended_qty: int = Field(gt=0)
    intended_entry_timestamp: datetime
    intended_reference_price: Decimal
    confirmation_atr14: Decimal
    stop_multiplier: Decimal
    objective_price: Decimal
    local_submission_timestamp: datetime | None = Field(
        default=None, exclude_if=lambda value: value is None
    )
    submitted_timestamp: datetime | None = None
    entry_order: BrokerOrderRecord | None = None
    actual_fill_timestamp: datetime | None = None
    actual_fill_price: Decimal | None = None
    actual_fill_qty: Decimal = Decimal("0")
    fill_slippage: Decimal | None = None
    protective_stop_price: Decimal | None = None
    protective_target_price: Decimal | None = None
    protective_orders: BrokerProtectiveOrders | None = None
    flatten_order: BrokerOrderRecord | None = None
    broker_reported_position_qty: Decimal = Decimal("0")
    local_expected_position_qty: Decimal = Decimal("0")
    cancel_state: Literal["NONE", "REQUESTED", "CONFIRMED"] = "NONE"
    state: PaperExecutionState
    failure_reason: str | None = None
    paper_version: Literal["stage14-4-paper-execution-v1"] = (
        "stage14-4-paper-execution-v1"
    )

    @model_validator(mode="after")
    def reconcile(self) -> Self:
        expected = {
            STAGE14_FORWARD_CANDIDATE_IDS[0]: Decimal("0.75"),
            STAGE14_FORWARD_CANDIDATE_IDS[1]: Decimal("1.00"),
        }
        if expected.get(self.candidate_id) != self.stop_multiplier:
            raise ValueError("paper execution candidate is not accepted Stage 13.3 input")
        if self.intended_entry_timestamp.utcoffset() is None:
            raise ValueError("intended entry timestamp must be timezone-aware")
        if self.intended_reference_price <= 0 or self.confirmation_atr14 <= 0:
            raise ValueError("paper entry reference and ATR must be positive")
        if self.objective_price <= 0:
            raise ValueError("paper objective price must be positive")
        if self.state is PaperExecutionState.BLOCKED:
            if not self.failure_reason:
                raise ValueError("blocked paper state requires a sanitized reason")
            return self
        if self.failure_reason is not None:
            raise ValueError("only blocked paper state may contain a failure reason")
        if self.entry_order is None:
            if self.state is not PaperExecutionState.DRY_RUN_INTENDED:
                raise ValueError("non-dry paper state requires an entry order")
            return self
        if (
            self.local_submission_timestamp is not None
            and self.local_submission_timestamp.utcoffset() is None
        ):
            raise ValueError("local paper submission timestamp must be timezone-aware")
        if self.entry_order.role is not BrokerOrderRole.ENTRY:
            raise ValueError("entry order role changed")
        if self.entry_order.side != "sell" or self.entry_order.qty != self.intended_qty:
            raise ValueError("entry order does not match intended short quantity")
        if self.submitted_timestamp is None or self.submitted_timestamp.utcoffset() is None:
            raise ValueError("initial broker submission timestamp must be preserved")
        if self.actual_fill_price is None:
            if any(
                item is not None
                for item in (
                    self.actual_fill_timestamp,
                    self.fill_slippage,
                    self.protective_stop_price,
                    self.protective_target_price,
                    self.protective_orders,
                )
            ) or self.actual_fill_qty:
                raise ValueError("unfilled entry cannot contain fill or protection values")
            return self
        if self.actual_fill_timestamp is None or self.actual_fill_timestamp.utcoffset() is None:
            raise ValueError("actual fill requires an aware timestamp")
        if self.actual_fill_qty != self.intended_qty:
            raise ValueError("Stage 14.4 manages only completely filled entries")
        with localcontext(ATR_CONTEXT):
            expected_slippage = self.actual_fill_price - self.intended_reference_price
            expected_stop = self.actual_fill_price + (
                self.confirmation_atr14 * self.stop_multiplier
            )
        if self.fill_slippage != expected_slippage:
            raise ValueError("fill slippage must preserve actual minus theoretical price")
        if self.protective_stop_price != expected_stop:
            raise ValueError("paper stop must use actual fill plus frozen ATR risk")
        if self.protective_target_price != self.objective_price:
            raise ValueError("paper target must preserve the frozen objective price")
        if self.state is PaperExecutionState.PROTECTIVE_ACTIVE and self.protective_orders is None:
            raise ValueError("protected state requires broker OCO records")
        return self


class PaperRunReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    symbol: Literal["SPY"] = "SPY"
    candidate: PaperCandidate
    qty: int = Field(gt=0)
    paper_orders_enabled: bool
    actions: tuple[str, ...]
    executions: tuple[PaperExecutionRecord, ...]
    report_version: Literal["stage14-4-paper-forward-test-v1"] = (
        "stage14-4-paper-forward-test-v1"
    )
    caveat: str = (
        "Alpaca paper account only; no live-money path, options, sizing model, "
        "or strategy qualification changes."
    )


def paper_execution_report_hash(report: PaperRunReport) -> str:
    return sha256(report.model_dump_json().encode()).hexdigest()
