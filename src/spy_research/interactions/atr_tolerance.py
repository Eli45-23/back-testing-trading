"""Parallel fixed 0.10 event-ATR interpretation of Stage 8.2 outcomes."""

from __future__ import annotations

from decimal import Decimal, localcontext

from spy_research.indicators.atr import ATR_CONTEXT
from spy_research.interactions.follow_through import FollowThroughInputError
from spy_research.interactions.models import (
    AtrToleranceFollowThrough,
    BreakFollowThrough,
    ImmediateState,
    PriceSide,
    RetestState,
    TolerantImmediateState,
    TolerantRetestState,
)


ATR_TOLERANCE_FRACTION = Decimal("0.10")


class AtrToleranceInputError(FollowThroughInputError):
    """Exact follow-through or event ATR violates frozen Stage 8.4 scope."""


def _validate_direction(direction: PriceSide) -> None:
    if direction not in (PriceSide.ABOVE, PriceSide.BELOW):
        raise AtrToleranceInputError("Break direction must be ABOVE or BELOW")


def calculate_tolerance_amount(event_atr: Decimal) -> Decimal:
    """Return exactly 0.10 of one positive event-time ATR14 value."""

    if not isinstance(event_atr, Decimal) or not event_atr.is_finite() or event_atr <= 0:
        raise AtrToleranceInputError("Event ATR must be a finite positive Decimal")
    with localcontext(ATR_CONTEXT):
        return event_atr * ATR_TOLERANCE_FRACTION


def calculate_tolerance_boundary(
    break_direction: PriceSide,
    level_price: Decimal,
    event_atr: Decimal,
) -> Decimal:
    """Return the frozen lower (above break) or upper (below break) boundary."""

    _validate_direction(break_direction)
    tolerance = calculate_tolerance_amount(event_atr)
    with localcontext(ATR_CONTEXT):
        if break_direction is PriceSide.ABOVE:
            return level_price - tolerance
        return level_price + tolerance


def classify_tolerant_immediate(
    break_direction: PriceSide,
    level_price: Decimal,
    event_atr: Decimal | None,
    next_close: Decimal | None,
) -> TolerantImmediateState:
    """Interpret the existing Stage 8.2 next close against a fixed boundary."""

    _validate_direction(break_direction)
    if next_close is None:
        return TolerantImmediateState.UNAVAILABLE
    if event_atr is None:
        return TolerantImmediateState.UNAVAILABLE_ATR
    boundary = calculate_tolerance_boundary(break_direction, level_price, event_atr)
    if break_direction is PriceSide.ABOVE:
        if next_close > level_price:
            return TolerantImmediateState.HOLD_EXACT
        if next_close >= boundary:
            return TolerantImmediateState.HOLD_WITHIN_TOLERANCE
    else:
        if next_close < level_price:
            return TolerantImmediateState.HOLD_EXACT
        if next_close <= boundary:
            return TolerantImmediateState.HOLD_WITHIN_TOLERANCE
    return TolerantImmediateState.FAILURE


def classify_tolerant_retest(
    break_direction: PriceSide,
    level_price: Decimal,
    event_atr: Decimal | None,
    exact_retest_state: RetestState,
    retest_close: Decimal | None,
) -> TolerantRetestState:
    """Reinterpret only the exact Stage 8.2 first-retest close."""

    _validate_direction(break_direction)
    if exact_retest_state is RetestState.UNAVAILABLE:
        return TolerantRetestState.UNAVAILABLE
    if event_atr is None:
        return TolerantRetestState.UNAVAILABLE_ATR
    if exact_retest_state is RetestState.NO_RETEST:
        return TolerantRetestState.NO_RETEST
    if retest_close is None:
        raise AtrToleranceInputError(
            "An exact retest state requires the Stage 8.2 retest close"
        )
    boundary = calculate_tolerance_boundary(break_direction, level_price, event_atr)
    if break_direction is PriceSide.ABOVE:
        if retest_close > level_price:
            return TolerantRetestState.RETEST_HOLD_EXACT
        if retest_close >= boundary:
            return TolerantRetestState.RETEST_HOLD_WITHIN_TOLERANCE
    else:
        if retest_close < level_price:
            return TolerantRetestState.RETEST_HOLD_EXACT
        if retest_close <= boundary:
            return TolerantRetestState.RETEST_HOLD_WITHIN_TOLERANCE
    return TolerantRetestState.RETEST_FAILURE


def _is_immediate_reclassified(
    exact: ImmediateState,
    tolerant: TolerantImmediateState,
) -> bool:
    return (
        exact is ImmediateState.FAILURE
        and tolerant is TolerantImmediateState.HOLD_WITHIN_TOLERANCE
    ) or (
        exact is ImmediateState.EQUAL
        and tolerant is TolerantImmediateState.HOLD_WITHIN_TOLERANCE
    )


def _is_retest_reclassified(
    exact: RetestState,
    tolerant: TolerantRetestState,
) -> bool:
    return (
        exact is RetestState.RETEST_FAILURE
        and tolerant is TolerantRetestState.RETEST_HOLD_WITHIN_TOLERANCE
    ) or (
        exact is RetestState.RETEST_EQUAL
        and tolerant is TolerantRetestState.RETEST_HOLD_WITHIN_TOLERANCE
    )


def _penetration(
    direction: PriceSide,
    level: Decimal,
    close: Decimal | None,
    event_atr: Decimal | None,
    within_tolerance: bool,
) -> tuple[Decimal | None, Decimal | None]:
    if not within_tolerance or close is None or event_atr is None:
        return None, None
    with localcontext(ATR_CONTEXT):
        amount = level - close if direction is PriceSide.ABOVE else close - level
        if amount < 0:
            amount = Decimal(0)
        return amount, amount / event_atr


def calculate_atr_tolerance_follow_through(
    exact: BreakFollowThrough,
    event_atr: Decimal | None,
) -> AtrToleranceFollowThrough:
    """Attach one parallel tolerant interpretation without altering Stage 8.2."""

    immediate = classify_tolerant_immediate(
        exact.break_direction,
        exact.level_price,
        event_atr,
        exact.immediate.close,
    )
    retest = classify_tolerant_retest(
        exact.break_direction,
        exact.level_price,
        event_atr,
        exact.retest.state,
        exact.retest.close,
    )
    atr_available = event_atr is not None
    tolerance_amount = (
        calculate_tolerance_amount(event_atr) if event_atr is not None else None
    )
    boundary = (
        calculate_tolerance_boundary(
            exact.break_direction,
            exact.level_price,
            event_atr,
        )
        if event_atr is not None
        else None
    )
    immediate_reclassified = _is_immediate_reclassified(
        exact.immediate.state, immediate
    )
    retest_reclassified = _is_retest_reclassified(exact.retest.state, retest)
    immediate_penetration, immediate_ratio = _penetration(
        exact.break_direction,
        exact.level_price,
        exact.immediate.close,
        event_atr,
        immediate
        is TolerantImmediateState.HOLD_WITHIN_TOLERANCE,
    )
    retest_penetration, retest_ratio = _penetration(
        exact.break_direction,
        exact.level_price,
        exact.retest.close,
        event_atr,
        retest
        is TolerantRetestState.RETEST_HOLD_WITHIN_TOLERANCE,
    )
    return AtrToleranceFollowThrough(
        break_interaction_identity=exact.break_interaction_identity,
        session_date=exact.session_date,
        level_type=exact.level_type,
        level_price=exact.level_price,
        break_timestamp=exact.break_timestamp,
        break_interaction_type=exact.break_interaction_type,
        break_direction=exact.break_direction,
        atr_available=atr_available,
        event_atr=event_atr,
        tolerance_amount=tolerance_amount,
        tolerance_boundary=boundary,
        immediate_timestamp=exact.immediate.bar_timestamp,
        immediate_close=exact.immediate.close,
        exact_immediate_state=exact.immediate.state,
        tolerant_immediate_state=immediate,
        immediate_reclassified=immediate_reclassified,
        immediate_penetration=immediate_penetration,
        immediate_penetration_as_atr=immediate_ratio,
        exact_retest_state=exact.retest.state,
        tolerant_retest_state=retest,
        retest_reclassified=retest_reclassified,
        retest_bar_offset=exact.retest.bar_offset,
        retest_timestamp=exact.retest.timestamp,
        retest_close=exact.retest.close,
        retest_penetration=retest_penetration,
        retest_penetration_as_atr=retest_ratio,
        available_retest_bars=exact.retest.available_bars,
        retest_window_complete=exact.retest.window_complete,
    )
