"""Stage 14.4 paper-only SPY execution boundary."""

from spy_research.paper.broker import AlpacaPaperBroker, PaperBrokerSession
from spy_research.paper.engine import (
    PaperExecutionEngine,
    deterministic_client_order_id,
)
from spy_research.paper.models import (
    ALPACA_PAPER_BASE_URL,
    BrokerOrderRecord,
    BrokerOrderRole,
    BrokerOrderStatus,
    BrokerPositionRecord,
    BrokerProtectiveOrders,
    PaperCandidate,
    PaperExecutionError,
    PaperExecutionRecord,
    PaperExecutionState,
    PaperRunReport,
    paper_execution_report_hash,
)
from spy_research.paper.price_precision import (
    alpaca_equity_tick,
    is_alpaca_equity_price,
    normalize_objective_limit,
    normalize_protective_stop,
    validate_short_protective_prices,
)
from spy_research.paper.service import LivePaperTradingService

__all__ = [
    "ALPACA_PAPER_BASE_URL",
    "AlpacaPaperBroker",
    "BrokerOrderRecord",
    "BrokerOrderRole",
    "BrokerOrderStatus",
    "BrokerPositionRecord",
    "BrokerProtectiveOrders",
    "LivePaperTradingService",
    "PaperBrokerSession",
    "PaperCandidate",
    "PaperExecutionEngine",
    "PaperExecutionError",
    "PaperExecutionRecord",
    "PaperExecutionState",
    "PaperRunReport",
    "deterministic_client_order_id",
    "paper_execution_report_hash",
    "alpaca_equity_tick",
    "is_alpaca_equity_price",
    "normalize_objective_limit",
    "normalize_protective_stop",
    "validate_short_protective_prices",
]
