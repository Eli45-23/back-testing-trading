"""Pure one-minute first-hit simulator for frozen Stage 13.1 variants."""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal, localcontext

from spy_research.data.schemas import RawBarRecord
from spy_research.execution.models import (
    AmbiguityMetadata,
    ExecutableTradeSetup,
    ExecutionInputError,
    FixedRiskVariant,
    RealizedTradePath,
    StrategyPopulation,
    TradeExitReason,
    TradeSimulationStatus,
)
from spy_research.indicators.atr import ATR_CONTEXT
from spy_research.market import MarketSessionClassifier, SessionType
from spy_research.strategy.models import SetupDirection


def _validate_and_select_bars(
    setup: ExecutableTradeSetup,
    bars: Sequence[RawBarRecord],
) -> tuple[RawBarRecord, ...]:
    classifier = MarketSessionClassifier()
    previous = None
    seen = set()
    selected = []
    for bar in bars:
        if (
            bar.symbol != "SPY"
            or bar.source != "alpaca"
            or bar.feed != "sip"
            or bar.timeframe != "1Min"
            or bar.adjustment != "raw"
        ):
            raise ExecutionInputError("simulation requires SPY Alpaca SIP raw 1Min bars")
        classified = classifier.classify(bar)
        if classified.session_date != setup.session_date:
            raise ExecutionInputError("simulation bars must remain in the setup session")
        if classified.session_type is not SessionType.RTH:
            raise ExecutionInputError("simulation requires same-session RTH bars")
        if bar.timestamp in seen:
            raise ExecutionInputError("simulation bars contain a duplicate timestamp")
        if previous is not None and bar.timestamp <= previous:
            raise ExecutionInputError("simulation bars must be strictly chronological")
        seen.add(bar.timestamp)
        previous = bar.timestamp
        if bar.timestamp >= setup.entry_timestamp:
            selected.append(bar)
    if not selected:
        raise ExecutionInputError("executable setup lacks its entry minute")
    first = selected[0]
    if first.timestamp != setup.entry_timestamp or first.open != setup.entry_price:
        raise ExecutionInputError("simulation entry must equal the accepted Stage 9 reference")
    return tuple(selected)


def _minutes(entry, event) -> int:
    seconds = (event - entry).total_seconds()
    if seconds < 0 or seconds % 60:
        raise ExecutionInputError("trade duration must be whole nonnegative minutes")
    return int(seconds // 60)


def simulate_fixed_risk_trade(
    setup: ExecutableTradeSetup,
    strategy_population: StrategyPopulation,
    variant: FixedRiskVariant,
    confirmation_atr: Decimal | None,
    chronological_same_session_rth_bars: Sequence[RawBarRecord],
) -> RealizedTradePath:
    """Simulate one frozen trade path without guessing intraminute ordering."""

    base = dict(
        setup_identity=setup.setup_identity,
        session_date=setup.session_date,
        direction=setup.direction,
        level_type=setup.level_type,
        strategy_population=strategy_population,
        confirmation_bar_timestamp=setup.confirmation_bar_timestamp,
        signal_known_at=setup.signal_known_at,
        entry_timestamp=setup.entry_timestamp,
        entry_price=setup.entry_price,
        confirmation_atr=confirmation_atr,
        stop_model=variant.stop_model,
        stop_multiplier=variant.stop_multiplier,
        target_model=variant.target_model,
        target_r=variant.target_r,
    )
    if confirmation_atr is None or confirmation_atr <= 0:
        return RealizedTradePath(
            **base,
            stop_price=None,
            initial_risk=None,
            target_price=None,
            exit_status=TradeSimulationStatus.TRADE_UNAVAILABLE_ATR,
            exit_timestamp=None,
            exit_price=None,
            exit_reason=None,
            price_pnl=None,
            r_multiple=None,
            minutes_in_trade=None,
            bars_observed=0,
            minutes_observed=0,
        )

    bars = _validate_and_select_bars(setup, chronological_same_session_rth_bars)
    with localcontext(ATR_CONTEXT):
        initial_risk = confirmation_atr * variant.stop_multiplier
        if setup.direction is SetupDirection.LONG:
            stop_price = setup.entry_price - initial_risk
            target_price = setup.entry_price + variant.target_r * initial_risk
        else:
            stop_price = setup.entry_price + initial_risk
            target_price = setup.entry_price - variant.target_r * initial_risk

    for observed, bar in enumerate(bars, start=1):
        if setup.direction is SetupDirection.LONG:
            stop_touched = bar.low <= stop_price
            target_touched = bar.high >= target_price
        else:
            stop_touched = bar.high >= stop_price
            target_touched = bar.low <= target_price
        elapsed = _minutes(setup.entry_timestamp, bar.timestamp)
        if stop_touched and target_touched:
            return RealizedTradePath(
                **base,
                stop_price=stop_price,
                initial_risk=initial_risk,
                target_price=target_price,
                exit_status=TradeSimulationStatus.AMBIGUOUS_BOTH_TOUCHED,
                exit_timestamp=bar.timestamp,
                exit_price=None,
                exit_reason=None,
                price_pnl=None,
                r_multiple=None,
                minutes_in_trade=elapsed,
                bars_observed=observed,
                minutes_observed=observed,
                ambiguity=AmbiguityMetadata(
                    timestamp=bar.timestamp,
                    open=bar.open,
                    high=bar.high,
                    low=bar.low,
                    close=bar.close,
                ),
            )
        if stop_touched or target_touched:
            reason = TradeExitReason.STOP if stop_touched else TradeExitReason.TARGET
            exit_price = stop_price if stop_touched else target_price
            with localcontext(ATR_CONTEXT):
                price_pnl = (
                    exit_price - setup.entry_price
                    if setup.direction is SetupDirection.LONG
                    else setup.entry_price - exit_price
                )
                r_multiple = (
                    Decimal("-1")
                    if reason is TradeExitReason.STOP
                    else variant.target_r
                )
            return RealizedTradePath(
                **base,
                stop_price=stop_price,
                initial_risk=initial_risk,
                target_price=target_price,
                exit_status=TradeSimulationStatus.SIMULATED,
                exit_timestamp=bar.timestamp,
                exit_price=exit_price,
                exit_reason=reason,
                price_pnl=price_pnl,
                r_multiple=r_multiple,
                minutes_in_trade=elapsed,
                bars_observed=observed,
                minutes_observed=observed,
            )

    final = bars[-1]
    with localcontext(ATR_CONTEXT):
        price_pnl = (
            final.close - setup.entry_price
            if setup.direction is SetupDirection.LONG
            else setup.entry_price - final.close
        )
        r_multiple = price_pnl / initial_risk
    return RealizedTradePath(
        **base,
        stop_price=stop_price,
        initial_risk=initial_risk,
        target_price=target_price,
        exit_status=TradeSimulationStatus.SIMULATED,
        exit_timestamp=final.timestamp,
        exit_price=final.close,
        exit_reason=TradeExitReason.EOD_CLOSE,
        price_pnl=price_pnl,
        r_multiple=r_multiple,
        minutes_in_trade=_minutes(setup.entry_timestamp, final.timestamp),
        bars_observed=len(bars),
        minutes_observed=len(bars),
    )
