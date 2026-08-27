"""Deterministic Alpaca equity-price normalization at the broker boundary."""

from __future__ import annotations

from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
from typing import Literal

from spy_research.paper.models import PaperExecutionError


PositionSide = Literal["short", "long"]


def alpaca_equity_tick(price: Decimal) -> Decimal:
    """Return Alpaca's documented equity price increment for ``price``."""

    if not price.is_finite() or price <= 0:
        raise PaperExecutionError("paper protective price must be positive and finite")
    return Decimal("0.01") if price >= Decimal("1") else Decimal("0.0001")


def is_alpaca_equity_price(price: Decimal) -> bool:
    """Return whether a positive equity price is exactly on Alpaca's tick."""

    try:
        tick = alpaca_equity_tick(price)
    except PaperExecutionError:
        return False
    return price == price.quantize(tick)


def normalize_protective_stop(
    theoretical_price: Decimal, *, position_side: PositionSide
) -> Decimal:
    """Move a stop toward the entry/risk boundary, never away from it.

    A short's protective buy-stop rounds down, so it cannot trigger above the
    exact theoretical stop. A long's protective sell-stop rounds up for the
    corresponding reason. Exact-tick prices remain unchanged.
    """

    tick = alpaca_equity_tick(theoretical_price)
    rounding = ROUND_FLOOR if position_side == "short" else ROUND_CEILING
    return theoretical_price.quantize(tick, rounding=rounding)


def normalize_objective_limit(
    theoretical_price: Decimal, *, position_side: PositionSide
) -> Decimal:
    """Normalize a profit objective without reducing its intended reward.

    Short buy-limits round down and long sell-limits round up. The theoretical
    objective remains stored independently by the execution record.
    """

    tick = alpaca_equity_tick(theoretical_price)
    rounding = ROUND_FLOOR if position_side == "short" else ROUND_CEILING
    return theoretical_price.quantize(tick, rounding=rounding)


def validate_short_protective_prices(
    *,
    fill_price: Decimal,
    theoretical_stop: Decimal,
    theoretical_target: Decimal,
    broker_stop: Decimal,
    broker_target: Decimal,
) -> None:
    """Fail closed if normalization weakens or invalidates a short OCO."""

    if not all(
        is_alpaca_equity_price(price) for price in (broker_stop, broker_target)
    ):
        raise PaperExecutionError("paper OCO price violates Alpaca equity precision")
    if broker_stop != normalize_protective_stop(
        theoretical_stop, position_side="short"
    ):
        raise PaperExecutionError("paper stop does not match frozen short normalization")
    if broker_target != normalize_objective_limit(
        theoretical_target, position_side="short"
    ):
        raise PaperExecutionError("paper target does not match frozen short normalization")
    if broker_stop > theoretical_stop:
        raise PaperExecutionError("paper stop normalization weakens short protection")
    if broker_target > theoretical_target:
        raise PaperExecutionError("paper target normalization weakens short objective")
    if not broker_target < fill_price < broker_stop:
        raise PaperExecutionError("paper OCO prices do not bracket the short fill")
