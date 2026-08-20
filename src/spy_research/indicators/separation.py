"""Deterministic raw EMA9/EMA20 separation metrics without cross detection."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from datetime import date
from decimal import localcontext

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.indicators.ema import (
    EMA_CONTEXT,
    EmaIndicatorService,
    IndicatorSequenceError,
)
from spy_research.indicators.models import (
    EmaSeparationCalculationResult,
    EmaSeparationRow,
    EmaSeparationSessionSummary,
    FiveMinuteIndicatorRow,
)


def calculate_session_ema_separation(
    ema_rows: Sequence[FiveMinuteIndicatorRow],
) -> tuple[EmaSeparationRow, ...]:
    """Derive raw separations and 1/2/3-bar deltas for one EMA session."""

    if not ema_rows:
        return ()
    session_date = ema_rows[0].session_date
    previous_timestamp = None
    seen_timestamps = set()
    for row in ema_rows:
        if row.session_date != session_date:
            raise IndicatorSequenceError(
                "Single-session EMA separation input mixes session dates"
            )
        if row.timeframe != "5Min":
            raise IndicatorSequenceError(
                "EMA separation input timeframe must be 5Min"
            )
        if row.session_mode != "RTH_ONLY":
            raise IndicatorSequenceError(
                "EMA separation input session mode must be RTH_ONLY"
            )
        if row.timestamp in seen_timestamps:
            raise IndicatorSequenceError(
                "EMA separation input contains a duplicate timestamp"
            )
        if previous_timestamp is not None and row.timestamp <= previous_timestamp:
            raise IndicatorSequenceError(
                "EMA separation input must be strictly chronological"
            )
        for value in (row.ema9, row.ema20):
            if value is not None and not value.is_finite():
                raise IndicatorSequenceError(
                    "EMA separation input values must be finite Decimals"
                )
        seen_timestamps.add(row.timestamp)
        previous_timestamp = row.timestamp

    signed_values = []
    with localcontext(EMA_CONTEXT):
        for row in ema_rows:
            signed_values.append(
                row.ema9 - row.ema20
                if row.ema9 is not None and row.ema20 is not None
                else None
            )

        output: list[EmaSeparationRow] = []
        for index, row in enumerate(ema_rows):
            signed = signed_values[index]

            def delta(lag: int):
                prior_index = index - lag
                if signed is None or prior_index < 0:
                    return None
                prior = signed_values[prior_index]
                return signed - prior if prior is not None else None

            output.append(
                EmaSeparationRow(
                    symbol=row.symbol,
                    timestamp=row.timestamp,
                    session_date=row.session_date,
                    ema9=row.ema9,
                    ema20=row.ema20,
                    signed_separation=signed,
                    absolute_separation=abs(signed) if signed is not None else None,
                    separation_delta_1=delta(1),
                    separation_delta_2=delta(2),
                    separation_delta_3=delta(3),
                )
            )
    return tuple(output)


def calculate_ema_separation_sessions(
    ema_rows: Sequence[FiveMinuteIndicatorRow],
) -> tuple[EmaSeparationRow, ...]:
    """Group EMA rows and reset all separation delta history each session."""

    previous_timestamp = None
    seen_timestamps = set()
    grouped: dict[date, list[FiveMinuteIndicatorRow]] = defaultdict(list)
    for row in ema_rows:
        if row.timestamp in seen_timestamps:
            raise IndicatorSequenceError(
                "EMA separation input contains a duplicate timestamp"
            )
        if previous_timestamp is not None and row.timestamp <= previous_timestamp:
            raise IndicatorSequenceError(
                "EMA separation input must be strictly chronological"
            )
        seen_timestamps.add(row.timestamp)
        previous_timestamp = row.timestamp
        grouped[row.session_date].append(row)

    output: list[EmaSeparationRow] = []
    for session_rows in grouped.values():
        output.extend(calculate_session_ema_separation(session_rows))
    return tuple(output)


class EmaSeparationIndicatorService:
    """Calculate validated EMAs once, then derive read-only separation metrics."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
    ) -> None:
        self._ema_service = EmaIndicatorService(config, processed_store, raw_store)

    def calculate(
        self,
        *,
        start: date,
        end: date,
    ) -> EmaSeparationCalculationResult:
        ema_result = self._ema_service.calculate(start=start, end=end)
        rows = calculate_ema_separation_sessions(ema_result.rows)
        grouped: dict[date, list[EmaSeparationRow]] = defaultdict(list)
        for row in rows:
            grouped[row.session_date].append(row)
        summaries = tuple(
            EmaSeparationSessionSummary(
                session_date=session_date,
                bars=len(session_rows),
                separation_valid_rows=sum(
                    row.signed_separation is not None for row in session_rows
                ),
                delta_1_valid_rows=sum(
                    row.separation_delta_1 is not None for row in session_rows
                ),
                delta_2_valid_rows=sum(
                    row.separation_delta_2 is not None for row in session_rows
                ),
                delta_3_valid_rows=sum(
                    row.separation_delta_3 is not None for row in session_rows
                ),
                first_separation_timestamp=next(
                    (
                        row.timestamp
                        for row in session_rows
                        if row.signed_separation is not None
                    ),
                    None,
                ),
                first_delta_1_timestamp=next(
                    (
                        row.timestamp
                        for row in session_rows
                        if row.separation_delta_1 is not None
                    ),
                    None,
                ),
                first_delta_2_timestamp=next(
                    (
                        row.timestamp
                        for row in session_rows
                        if row.separation_delta_2 is not None
                    ),
                    None,
                ),
                first_delta_3_timestamp=next(
                    (
                        row.timestamp
                        for row in session_rows
                        if row.separation_delta_3 is not None
                    ),
                    None,
                ),
                final_signed_separation=(
                    session_rows[-1].signed_separation if session_rows else None
                ),
            )
            for session_date, session_rows in grouped.items()
        )
        return EmaSeparationCalculationResult(
            symbol=ema_result.symbol,
            start_date=start,
            end_date=end,
            rows=rows,
            sessions=summaries,
            processed_validation=ema_result.processed_validation,
        )
