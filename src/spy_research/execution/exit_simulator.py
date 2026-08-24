"""Pure first-hit simulation for the 21 new Stage 13.2 exit variants."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import timedelta
from decimal import Decimal, localcontext

from spy_research.data.schemas import RawBarRecord
from spy_research.execution.exit_models import (
    ExitComparisonInputError,
    ExitFamily,
    ExitModelExitReason,
    ExitModelStatus,
    ExitModelTradePath,
    ExitModelVariant,
    NormalizedCrossExitEvent,
    ScheduledExit,
)
from spy_research.execution.models import (
    AmbiguityMetadata,
    ExecutableTradeSetup,
    StrategyPopulation,
)
from spy_research.indicators.atr import ATR_CONTEXT
from spy_research.interactions import LevelType
from spy_research.market import MarketSessionClassifier, SessionType
from spy_research.strategy.models import SetupDirection


CROSS_REASON = {
    ExitFamily.OPPOSITE_EMA9_20_CROSS: (
        ExitModelExitReason.OPPOSITE_EMA9_20_CROSS
    ),
    ExitFamily.OPPOSITE_EMA9_VWAP_CROSS: (
        ExitModelExitReason.OPPOSITE_EMA9_VWAP_CROSS
    ),
    ExitFamily.OPPOSITE_EMA20_VWAP_CROSS: (
        ExitModelExitReason.OPPOSITE_EMA20_VWAP_CROSS
    ),
}
TIME_REASON = {
    15: ExitModelExitReason.TIME_15M,
    30: ExitModelExitReason.TIME_30M,
    60: ExitModelExitReason.TIME_60M,
}


def select_opposite_cross_exit(
    setup: ExecutableTradeSetup,
    family: ExitFamily,
    events: Sequence[NormalizedCrossExitEvent],
) -> ScheduledExit | None:
    """Select the first same-session opposite cross known strictly after entry."""

    if family not in CROSS_REASON:
        raise ExitComparisonInputError("opposite-cross selection requires a cross family")
    previous = None
    seen = set()
    eligible = []
    expected_direction = (
        "BEARISH" if setup.direction is SetupDirection.LONG else "BULLISH"
    )
    for event in events:
        if event.family is not family:
            raise ExitComparisonInputError("cross event family mismatch")
        if event.session_date != setup.session_date:
            raise ExitComparisonInputError("cross events must remain in setup session")
        if event.event_identity in seen:
            raise ExitComparisonInputError("duplicate cross event identity")
        if previous is not None and event.cross_known_at <= previous:
            raise ExitComparisonInputError("cross events must be strictly chronological")
        previous = event.cross_known_at
        seen.add(event.event_identity)
        if (
            event.direction == expected_direction
            and event.cross_known_at > setup.entry_timestamp
        ):
            eligible.append(event)
    if not eligible:
        return None
    selected = eligible[0]
    return ScheduledExit(
        executable_at=selected.cross_known_at,
        reason=CROSS_REASON[family],
        source_event_identity=selected.event_identity,
        source_cross_timestamp=selected.cross_timestamp,
    )


def _select_bars(
    setup: ExecutableTradeSetup,
    bars: Sequence[RawBarRecord],
) -> tuple[RawBarRecord, ...]:
    classifier = MarketSessionClassifier()
    selected = []
    previous = None
    seen = set()
    for bar in bars:
        if (
            bar.symbol != "SPY"
            or bar.source != "alpaca"
            or bar.feed != "sip"
            or bar.timeframe != "1Min"
            or bar.adjustment != "raw"
        ):
            raise ExitComparisonInputError("exit comparison requires SPY SIP raw 1Min")
        classified = classifier.classify(bar)
        if classified.session_date != setup.session_date:
            raise ExitComparisonInputError("exit bars cannot cross a session boundary")
        if classified.session_type is not SessionType.RTH:
            raise ExitComparisonInputError("exit comparison requires RTH bars")
        if bar.timestamp in seen:
            raise ExitComparisonInputError("duplicate exit bar timestamp")
        if previous is not None and bar.timestamp <= previous:
            raise ExitComparisonInputError("exit bars must be chronological")
        previous = bar.timestamp
        seen.add(bar.timestamp)
        if bar.timestamp >= setup.entry_timestamp:
            selected.append(bar)
    if not selected:
        raise ExitComparisonInputError("exit variant lacks its accepted entry minute")
    if (
        selected[0].timestamp != setup.entry_timestamp
        or selected[0].open != setup.entry_price
    ):
        raise ExitComparisonInputError("entry must equal the accepted Stage 9 reference")
    return tuple(selected)


def _whole_minutes(start, end) -> int:
    seconds = (end - start).total_seconds()
    if seconds < 0 or seconds % 60:
        raise ExitComparisonInputError("exit duration must be whole minutes")
    return int(seconds // 60)


def _pnl(setup: ExecutableTradeSetup, exit_price: Decimal) -> Decimal:
    with localcontext(ATR_CONTEXT):
        return (
            exit_price - setup.entry_price
            if setup.direction is SetupDirection.LONG
            else setup.entry_price - exit_price
        )


def simulate_exit_model_trade(
    setup: ExecutableTradeSetup,
    strategy_population: StrategyPopulation,
    variant: ExitModelVariant,
    confirmation_atr: Decimal | None,
    chronological_same_session_rth_bars: Sequence[RawBarRecord],
    *,
    scheduled_exit: ScheduledExit | None = None,
    objective_price: Decimal | None = None,
    objective_level_types: Sequence[LevelType] = (),
    objective_available: bool = True,
) -> ExitModelTradePath:
    """Simulate one new exit path; minute-open exits precede that minute's range."""

    if variant.family is ExitFamily.FIXED_R_CONTROL:
        raise ExitComparisonInputError("accepted controls must use Stage 13.1 paths")
    if variant.family in CROSS_REASON:
        if scheduled_exit is not None and scheduled_exit.reason is not CROSS_REASON[
            variant.family
        ]:
            raise ExitComparisonInputError("scheduled cross reason mismatch")
    elif variant.family is ExitFamily.TIME_EXIT:
        assert variant.time_minutes is not None
        expected = ScheduledExit(
            executable_at=setup.entry_timestamp
            + timedelta(minutes=variant.time_minutes),
            reason=TIME_REASON[variant.time_minutes],
        )
        if scheduled_exit is not None and scheduled_exit != expected:
            raise ExitComparisonInputError("time exit must use its frozen entry offset")
        scheduled_exit = expected
    elif scheduled_exit is not None:
        raise ExitComparisonInputError("objective variant cannot contain scheduled exit")

    is_objective = variant.family is ExitFamily.NEXT_OBJECTIVE_LEVEL
    context_eligible = bool(
        not is_objective or (objective_available and objective_price is not None)
    )
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
        variant=variant,
        objective_price=objective_price,
        objective_level_types=tuple(objective_level_types),
        scheduled_exit=scheduled_exit,
    )
    if confirmation_atr is None or confirmation_atr <= 0:
        return ExitModelTradePath(
            **base,
            stop_price=None,
            initial_risk=None,
            atr_eligible=False,
            target_context_eligible=context_eligible,
            status=ExitModelStatus.UNAVAILABLE_ATR,
            exit_timestamp=None,
            exit_price=None,
            exit_reason=ExitModelExitReason.UNAVAILABLE_ATR,
            price_pnl=None,
            r_multiple=None,
            minutes_in_trade=None,
            bars_observed=0,
        )
    with localcontext(ATR_CONTEXT):
        risk = confirmation_atr * variant.stop_multiplier
        stop = (
            setup.entry_price - risk
            if setup.direction is SetupDirection.LONG
            else setup.entry_price + risk
        )
    if is_objective and not context_eligible:
        return ExitModelTradePath(
            **base,
            stop_price=stop,
            initial_risk=risk,
            atr_eligible=True,
            target_context_eligible=False,
            status=ExitModelStatus.UNAVAILABLE_OBJECTIVE,
            exit_timestamp=None,
            exit_price=None,
            exit_reason=ExitModelExitReason.UNAVAILABLE_OBJECTIVE,
            price_pnl=None,
            r_multiple=None,
            minutes_in_trade=None,
            bars_observed=0,
        )
    if not is_objective and objective_price is not None:
        raise ExitComparisonInputError("only objective variants may contain a target")
    bars = _select_bars(setup, chronological_same_session_rth_bars)
    for observed, bar in enumerate(bars, start=1):
        if scheduled_exit is not None and bar.timestamp >= scheduled_exit.executable_at:
            pnl = _pnl(setup, bar.open)
            with localcontext(ATR_CONTEXT):
                r_multiple = pnl / risk
            return ExitModelTradePath(
                **base,
                stop_price=stop,
                initial_risk=risk,
                atr_eligible=True,
                target_context_eligible=True,
                status=ExitModelStatus.REALIZED,
                exit_timestamp=bar.timestamp,
                exit_price=bar.open,
                exit_reason=scheduled_exit.reason,
                price_pnl=pnl,
                r_multiple=r_multiple,
                minutes_in_trade=_whole_minutes(setup.entry_timestamp, bar.timestamp),
                bars_observed=observed,
            )
        stop_touched = (
            bar.low <= stop
            if setup.direction is SetupDirection.LONG
            else bar.high >= stop
        )
        target_touched = bool(
            is_objective
            and objective_price is not None
            and (
                bar.high >= objective_price
                if setup.direction is SetupDirection.LONG
                else bar.low <= objective_price
            )
        )
        if stop_touched and target_touched:
            return ExitModelTradePath(
                **base,
                stop_price=stop,
                initial_risk=risk,
                atr_eligible=True,
                target_context_eligible=True,
                status=ExitModelStatus.AMBIGUOUS_BOTH_TOUCHED,
                exit_timestamp=bar.timestamp,
                exit_price=None,
                exit_reason=ExitModelExitReason.AMBIGUOUS_BOTH_TOUCHED,
                price_pnl=None,
                r_multiple=None,
                minutes_in_trade=_whole_minutes(setup.entry_timestamp, bar.timestamp),
                bars_observed=observed,
                ambiguity=AmbiguityMetadata(
                    timestamp=bar.timestamp,
                    open=bar.open,
                    high=bar.high,
                    low=bar.low,
                    close=bar.close,
                ),
            )
        if stop_touched or target_touched:
            reason = (
                ExitModelExitReason.STOP
                if stop_touched
                else ExitModelExitReason.NEXT_OBJECTIVE_LEVEL
            )
            exit_price = stop if stop_touched else objective_price
            assert exit_price is not None
            pnl = _pnl(setup, exit_price)
            with localcontext(ATR_CONTEXT):
                r_multiple = Decimal("-1") if stop_touched else pnl / risk
            return ExitModelTradePath(
                **base,
                stop_price=stop,
                initial_risk=risk,
                atr_eligible=True,
                target_context_eligible=True,
                status=ExitModelStatus.REALIZED,
                exit_timestamp=bar.timestamp,
                exit_price=exit_price,
                exit_reason=reason,
                price_pnl=pnl,
                r_multiple=r_multiple,
                minutes_in_trade=_whole_minutes(setup.entry_timestamp, bar.timestamp),
                bars_observed=observed,
            )
    final = bars[-1]
    pnl = _pnl(setup, final.close)
    with localcontext(ATR_CONTEXT):
        r_multiple = pnl / risk
    return ExitModelTradePath(
        **base,
        stop_price=stop,
        initial_risk=risk,
        atr_eligible=True,
        target_context_eligible=True,
        status=ExitModelStatus.REALIZED,
        exit_timestamp=final.timestamp,
        exit_price=final.close,
        exit_reason=ExitModelExitReason.EOD_CLOSE,
        price_pnl=pnl,
        r_multiple=r_multiple,
        minutes_in_trade=_whole_minutes(setup.entry_timestamp, final.timestamp),
        bars_observed=len(bars),
    )
