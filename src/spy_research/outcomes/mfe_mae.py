"""Same-session future one-minute MFE/MAE calculations for EMA cross events."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, localcontext
from zoneinfo import ZoneInfo

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.data.schemas import RawBarRecord
from spy_research.data.validation import DataValidationReport, RawDataValidator
from spy_research.events import EmaCrossDirection, EmaCrossEvent, EmaCrossEventService
from spy_research.indicators.ema import EMA_CONTEXT
from spy_research.market import MarketSessionClassifier, SessionType, XNYSCalendar
from spy_research.outcomes.models import (
    EmaCrossOutcome,
    EmaCrossOutcomeResult,
    ExcursionResult,
    HorizonOutcome,
)


FIXED_HORIZONS = (5, 15, 30, 60)
NEW_YORK = ZoneInfo("America/New_York")


class OutcomeInputValidationError(ValueError):
    """Raw validation failed, blocking outcome calculation."""

    def __init__(self, report: DataValidationReport) -> None:
        self.report = report
        super().__init__(
            "Raw one-minute validation failed; outcome calculation is blocked "
            f"({report.error_count} errors)"
        )


class OutcomeSequenceError(ValueError):
    """Supplied future bars cannot form deterministic outcome windows."""


@dataclass(frozen=True)
class SelectedHorizon:
    """Internal exact-timestamp selection for one requested horizon."""

    requested_minutes: int
    bars: tuple[RawBarRecord, ...]
    complete: bool


@dataclass(frozen=True)
class OutcomeWindowSelection:
    """Exact fixed and EOD future-bar windows for one completed cross."""

    outcome_start_timestamp: datetime
    future_rth_bars: tuple[RawBarRecord, ...]
    five: SelectedHorizon
    fifteen: SelectedHorizon
    thirty: SelectedHorizon
    sixty: SelectedHorizon
    eod: SelectedHorizon


def outcome_start_timestamp(event_timestamp: datetime) -> datetime:
    """Return the first eligible minute after a completed five-minute candle."""

    if event_timestamp.utcoffset() is None:
        raise ValueError("event timestamp must be timezone-aware")
    return event_timestamp + timedelta(minutes=5)


def _validate_raw_sequence(bars: Sequence[RawBarRecord]) -> None:
    previous_timestamp = None
    seen_timestamps = set()
    for bar in bars:
        if bar.timestamp in seen_timestamps:
            raise OutcomeSequenceError("Outcome input contains a duplicate timestamp")
        if previous_timestamp is not None and bar.timestamp <= previous_timestamp:
            raise OutcomeSequenceError("Outcome input must be strictly chronological")
        seen_timestamps.add(bar.timestamp)
        previous_timestamp = bar.timestamp


def _select_exact_minutes(
    bars_by_timestamp: dict[datetime, RawBarRecord],
    *,
    start: datetime,
    requested_minutes: int,
) -> SelectedHorizon:
    expected = tuple(start + timedelta(minutes=index) for index in range(requested_minutes))
    bars = tuple(bars_by_timestamp[timestamp] for timestamp in expected if timestamp in bars_by_timestamp)
    return SelectedHorizon(
        requested_minutes=requested_minutes,
        bars=bars,
        complete=len(bars) == requested_minutes and requested_minutes > 0,
    )


def select_outcome_windows(
    *,
    event_timestamp: datetime,
    session_date: date,
    session_close: datetime,
    rth_bars: Sequence[RawBarRecord],
) -> OutcomeWindowSelection:
    """Select exact same-session 5/15/30/60/EOD minute-start windows."""

    if session_close.utcoffset() is None:
        raise ValueError("session close must be timezone-aware")
    _validate_raw_sequence(rth_bars)
    start = outcome_start_timestamp(event_timestamp)
    eligible = tuple(
        bar
        for bar in rth_bars
        if bar.timestamp.astimezone(NEW_YORK).date() == session_date
        and bar.timestamp >= start
        and bar.timestamp < session_close
    )
    bars_by_timestamp = {bar.timestamp: bar for bar in eligible}
    selections = {
        minutes: _select_exact_minutes(
            bars_by_timestamp,
            start=start,
            requested_minutes=minutes,
        )
        for minutes in FIXED_HORIZONS
    }
    eod_requested = max(0, int((session_close - start).total_seconds() // 60))
    eod = _select_exact_minutes(
        bars_by_timestamp,
        start=start,
        requested_minutes=eod_requested,
    )
    return OutcomeWindowSelection(
        outcome_start_timestamp=start,
        future_rth_bars=eligible,
        five=selections[5],
        fifteen=selections[15],
        thirty=selections[30],
        sixty=selections[60],
        eod=eod,
    )


def calculate_excursion(
    direction: EmaCrossDirection,
    reference_price: Decimal,
    future_bars: Sequence[RawBarRecord],
) -> ExcursionResult:
    """Calculate floored MFE/MAE magnitudes with earliest tied extremes."""

    _validate_raw_sequence(future_bars)
    if not future_bars:
        return ExcursionResult(
            mfe=None,
            mfe_timestamp=None,
            mae=None,
            mae_timestamp=None,
        )
    if not reference_price.is_finite():
        raise ValueError("reference price must be a finite Decimal")

    highest = future_bars[0]
    lowest = future_bars[0]
    for bar in future_bars[1:]:
        if bar.high > highest.high:
            highest = bar
        if bar.low < lowest.low:
            lowest = bar

    with localcontext(EMA_CONTEXT):
        if direction == EmaCrossDirection.BULLISH:
            raw_mfe = highest.high - reference_price
            raw_mae = reference_price - lowest.low
            mfe_timestamp = highest.timestamp
            mae_timestamp = lowest.timestamp
        elif direction == EmaCrossDirection.BEARISH:
            raw_mfe = reference_price - lowest.low
            raw_mae = highest.high - reference_price
            mfe_timestamp = lowest.timestamp
            mae_timestamp = highest.timestamp
        else:
            raise ValueError("unsupported EMA cross direction")
        return ExcursionResult(
            mfe=max(Decimal(0), raw_mfe),
            mfe_timestamp=mfe_timestamp,
            mae=max(Decimal(0), raw_mae),
            mae_timestamp=mae_timestamp,
        )


def _horizon_outcome(
    *,
    name: str,
    selection: SelectedHorizon,
    event: EmaCrossEvent,
) -> HorizonOutcome:
    return HorizonOutcome(
        horizon=name,
        requested_minutes=selection.requested_minutes,
        observed_minutes=len(selection.bars),
        complete=selection.complete,
        excursion=calculate_excursion(
            event.direction,
            event.reference_price,
            selection.bars,
        ),
    )


def calculate_event_outcome(
    event: EmaCrossEvent,
    *,
    session_close: datetime,
    rth_bars: Sequence[RawBarRecord],
) -> EmaCrossOutcome:
    """Compose all requested horizons for one immutable Stage 4 event."""

    windows = select_outcome_windows(
        event_timestamp=event.timestamp,
        session_date=event.session_date,
        session_close=session_close,
        rth_bars=rth_bars,
    )
    return EmaCrossOutcome(
        event=event,
        symbol=event.symbol,
        session_date=event.session_date,
        event_timestamp=event.timestamp,
        reference_price=event.reference_price,
        outcome_start_timestamp=windows.outcome_start_timestamp,
        available_future_minutes=len(windows.future_rth_bars),
        five=_horizon_outcome(name="5m", selection=windows.five, event=event),
        fifteen=_horizon_outcome(
            name="15m", selection=windows.fifteen, event=event
        ),
        thirty=_horizon_outcome(name="30m", selection=windows.thirty, event=event),
        sixty=_horizon_outcome(name="60m", selection=windows.sixty, event=event),
        eod=_horizon_outcome(name="EOD", selection=windows.eod, event=event),
    )


class EmaCrossOutcomeService:
    """Generate Stage 4 events, validate raw bars, then calculate outcomes."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
    ) -> None:
        self._config = config
        self._processed_store = processed_store
        self._raw_store = raw_store
        self._calendar = XNYSCalendar()

    def calculate(self, *, start: date, end: date) -> EmaCrossOutcomeResult:
        raw_validation = RawDataValidator().validate_raw_store(
            self._raw_store,
            symbol=self._config.symbol,
            start_date=start,
            end_date=end,
        )
        if not raw_validation.passed:
            raise OutcomeInputValidationError(raw_validation)
        event_result = EmaCrossEventService(
            self._config,
            self._processed_store,
            self._raw_store,
        ).calculate(start=start, end=end)
        raw_bars = self._raw_store.load_raw_bars(
            symbol=self._config.symbol,
            start=start,
            end=end,
            feed=self._config.data.feed,
            timeframe=self._config.data.timeframe,
        )
        classified = MarketSessionClassifier(self._calendar).classify_many(raw_bars)
        rth_by_date: dict[date, list[RawBarRecord]] = {}
        for item in classified:
            if item.session_type is SessionType.RTH:
                rth_by_date.setdefault(item.session_date, []).append(item.bar)

        outcomes = []
        for event in event_result.events:
            session = self._calendar.session_for_date(event.session_date)
            assert session.market_close is not None
            outcomes.append(
                calculate_event_outcome(
                    event,
                    session_close=session.market_close,
                    rth_bars=rth_by_date.get(event.session_date, []),
                )
            )
        return EmaCrossOutcomeResult(
            symbol=self._config.symbol,
            start_date=start,
            end_date=end,
            outcomes=tuple(outcomes),
            raw_validation=raw_validation,
        )
