"""Read-only Stage 15 orchestration over accepted historical SPY records."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, time, timedelta
from decimal import Decimal, localcontext
from zoneinfo import ZoneInfo

from spy_research.attribution.analysis import analyze_base_short_attribution
from spy_research.attribution.models import AttributionObservation, AttributionReport
from spy_research.bars.models import FiveMinuteBar
from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.events.ema_cross import detect_ema_crosses
from spy_research.events.models import EmaCrossEvent
from spy_research.execution.exit_models import (
    ExitFamily,
    ExitModelStatus,
    exit_model_comparison_hash,
)
from spy_research.execution.exit_service import ExitModelComparisonService
from spy_research.execution.models import AtrStopModel, StrategyPopulation
from spy_research.indicators.atr import calculate_atr_sessions
from spy_research.indicators.ema import EMA_CONTEXT, calculate_ema_sessions
from spy_research.indicators.separation import calculate_ema_separation_sessions
from spy_research.indicators.vwap import calculate_vwap_sessions
from spy_research.interactions.classifier import classify_session_level_interactions
from spy_research.interactions.service import build_session_levels
from spy_research.levels import (
    OpeningFiveMinuteLevelsService,
    PremarketLevelsService,
    PreviousDayLevelsService,
)
from spy_research.market import XNYSCalendar
from spy_research.strategy.base_price_action_service import BasePriceActionService
from spy_research.strategy.base_statistics import (
    calculate_base_strategy_statistics,
)
from spy_research.strategy.comparisons.combined_context import (
    calculate_combined_context_matrix,
    combine_context_annotations,
)
from spy_research.strategy.comparisons.ema20_vwap_alignment import annotate_confirmed_ema20_vwap_alignment
from spy_research.strategy.comparisons.ema20_vwap_cross import detect_ema20_vwap_crosses
from spy_research.strategy.comparisons.ema20_vwap_cross_context import annotate_ema20_vwap_cross_context
from spy_research.strategy.comparisons.ema9_vwap_alignment import annotate_confirmed_ema9_vwap_alignment
from spy_research.strategy.comparisons.ema9_vwap_cross import detect_ema9_vwap_crosses
from spy_research.strategy.comparisons.ema9_vwap_cross_context import annotate_ema9_vwap_cross_context
from spy_research.strategy.comparisons.ema_alignment import annotate_confirmed_setups
from spy_research.strategy.comparisons.ema_cross_context import annotate_prior_cross_context
from spy_research.strategy.comparisons.market_condition import calculate_market_condition_annotations, calculate_market_condition_report
from spy_research.strategy.comparisons.market_structure import build_market_structure_annotations, detect_confirmed_swings
from spy_research.strategy.comparisons.regime_hypotheses import build_regime_hypothesis_annotations, calculate_regime_hypothesis_comparison
from spy_research.strategy.comparisons.room_to_level import build_room_annotations, calculate_room_to_level_comparison
from spy_research.strategy.comparisons.vwap_alignment import annotate_confirmed_vwap_alignment
from spy_research.strategy.setup_outcome_service import SetupOutcomeService


NEW_YORK = ZoneInfo("America/New_York")
ACCEPTED_STAGE14_4_HASH = "3de987672bc6cc73c39c643f6bd656daefdcbe32e0e6ce3c830405ab8eee183b"

FIXED_FACTOR_STATES = (
    ("LEVEL_TYPE", ("PDH", "PDL", "PDC", "PMH", "PML", "ORH5", "ORL5")),
    ("TIME_OF_DAY", ("OPENING_0935_1000", "MORNING_1000_1130", "MIDDAY_1130_1400", "AFTERNOON_1400_1530", "LATE_1530_1600")),
    ("ROOM_DOLLARS", ("LE_0_50", "GT_0_50_LE_1_00", "GT_1_00_LE_2_00", "GT_2_00", "OPEN_ENDED", "UNAVAILABLE")),
    ("ROOM_ATR", ("LT_0_5_ATR", "ATR_0_5_TO_1_0", "ATR_1_0_TO_1_5", "ATR_1_5_TO_2_0", "ATR_2_0_TO_3_0", "GT_3_0_ATR", "OPEN_ENDED", "UNAVAILABLE_ATR")),
    ("MARKET_STRUCTURE", ("BULLISH_STRUCTURE", "BEARISH_STRUCTURE", "MIXED_STRUCTURE", "UNAVAILABLE")),
    ("EMA_ALIGNMENT", ("EMA_ALIGNED", "EMA_NOT_ALIGNED", "EMA_UNAVAILABLE")),
    ("EMA_SEPARATION", ("WIDE_SEPARATION", "MID_SEPARATION", "TIGHT_SEPARATION", "UNAVAILABLE")),
    ("VWAP_ALIGNMENT", ("ALL_ALIGNED", "MIXED_ALIGNMENT", "NONE_ALIGNED", "UNAVAILABLE")),
    ("ATR_REGIME", ("LOW_LT_0_50", "NORMAL_0_50_TO_1_00", "HIGH_GT_1_00", "UNAVAILABLE")),
    ("BREAK_QUALITY", ("STRONG", "MODERATE", "WEAK_OR_OPPOSING", "ZERO_RANGE", "UNAVAILABLE")),
    ("CONFIRMATION_QUALITY", ("STRONG", "MODERATE", "WEAK_OR_OPPOSING", "ZERO_RANGE", "UNAVAILABLE")),
    ("TREND_CHOP", ("TREND_LIKE_A", "CHOP_LIKE_A", "OTHER", "UNAVAILABLE")),
    ("GAP_CONTEXT", ("GAP_UP_GE_0_25_ATR", "GAP_DOWN_LE_NEG_0_25_ATR", "FLAT_WITHIN_0_25_ATR", "UNAVAILABLE")),
    ("PRIOR_LEVEL_INTERACTIONS", ("ZERO", "ONE", "TWO_PLUS")),
    ("CONFIRMATION_TYPE", ("IMMEDIATE_HOLD", "RETEST_HOLD")),
)


def _time_bucket(value) -> str:
    local = value.astimezone(NEW_YORK).time()
    if local < time(10, 0):
        return "OPENING_0935_1000"
    if local < time(11, 30):
        return "MORNING_1000_1130"
    if local < time(14, 0):
        return "MIDDAY_1130_1400"
    if local < time(15, 30):
        return "AFTERNOON_1400_1530"
    return "LATE_1530_1600"


def _room_dollars(value: Decimal | None, open_ended: bool) -> str:
    if open_ended:
        return "OPEN_ENDED"
    if value is None:
        return "UNAVAILABLE"
    if value <= Decimal("0.50"):
        return "LE_0_50"
    if value <= Decimal("1.00"):
        return "GT_0_50_LE_1_00"
    if value <= Decimal("2.00"):
        return "GT_1_00_LE_2_00"
    return "GT_2_00"


def _atr_regime(value: Decimal | None) -> str:
    if value is None:
        return "UNAVAILABLE"
    if value < Decimal("0.50"):
        return "LOW_LT_0_50"
    if value <= Decimal("1.00"):
        return "NORMAL_0_50_TO_1_00"
    return "HIGH_GT_1_00"


def _candle_quality(bar: FiveMinuteBar | None) -> str:
    if bar is None:
        return "UNAVAILABLE"
    candle_range = bar.high - bar.low
    if candle_range == 0:
        return "ZERO_RANGE"
    directional_body = bar.open - bar.close  # frozen BASE_SHORT direction
    ratio = directional_body / candle_range
    if ratio >= Decimal("0.60"):
        return "STRONG"
    if ratio >= Decimal("0.30"):
        return "MODERATE"
    return "WEAK_OR_OPPOSING"


def _vwap_alignment(context) -> str:
    values = (
        context.price_vwap_alignment.value,
        context.ema9_vwap_alignment.value,
        context.ema20_vwap_alignment.value,
    )
    if any(value.endswith("UNAVAILABLE") for value in values):
        return "UNAVAILABLE"
    aligned = sum("NOT_ALIGNED" not in value and "ALIGNED" in value for value in values)
    if aligned == 3:
        return "ALL_ALIGNED"
    if aligned == 0:
        return "NONE_ALIGNED"
    return "MIXED_ALIGNMENT"


def _gap_context(open_price: Decimal | None, prior_close: Decimal | None, atr: Decimal | None) -> str:
    if open_price is None or prior_close is None or atr is None or atr <= 0:
        return "UNAVAILABLE"
    normalized = (open_price - prior_close) / atr
    if normalized >= Decimal("0.25"):
        return "GAP_UP_GE_0_25_ATR"
    if normalized <= Decimal("-0.25"):
        return "GAP_DOWN_LE_NEG_0_25_ATR"
    return "FLAT_WITHIN_0_25_ATR"


def _normalized_ema_crosses(ema_rows, separation_rows, vwap_rows, atr_rows):
    """Apply the accepted Stage 4 normalization without repeating store validation."""
    detected = detect_ema_crosses(ema_rows)
    separation_by_timestamp = {item.timestamp: item for item in separation_rows}
    vwap_by_timestamp = {item.timestamp: item for item in vwap_rows}
    atr_by_timestamp = {item.timestamp: item for item in atr_rows}
    events = []
    with localcontext(EMA_CONTEXT):
        for cross in detected:
            separation = separation_by_timestamp[cross.timestamp]
            vwap = vwap_by_timestamp[cross.timestamp]
            atr = atr_by_timestamp[cross.timestamp]
            events.append(EmaCrossEvent(
                symbol=cross.symbol,
                timestamp=cross.timestamp,
                session_date=cross.session_date,
                direction=cross.direction,
                reference_price=cross.close,
                close=cross.close,
                ema9=cross.ema9,
                ema20=cross.ema20,
                previous_ema9=cross.previous_ema9,
                previous_ema20=cross.previous_ema20,
                signed_separation=separation.signed_separation,
                absolute_separation=separation.absolute_separation,
                previous_signed_separation=cross.previous_ema9 - cross.previous_ema20,
                separation_delta_1=separation.separation_delta_1,
                separation_delta_2=separation.separation_delta_2,
                separation_delta_3=separation.separation_delta_3,
                vwap=vwap.vwap,
                close_minus_vwap=cross.close - vwap.vwap if vwap.vwap is not None else None,
                ema9_minus_vwap=cross.ema9 - vwap.vwap if vwap.vwap is not None else None,
                ema20_minus_vwap=cross.ema20 - vwap.vwap if vwap.vwap is not None else None,
                atr14=atr.atr14,
            ))
    return tuple(events)


class BaseShortAttributionService:
    """Build the predeclared attribution matrix without writes or qualification changes."""

    def __init__(self, config: ResearchConfig, processed_store: ProcessedFiveMinuteStore, raw_store: RawBarStore, *, calendar: XNYSCalendar | None = None) -> None:
        self._config = config
        self._processed = processed_store
        self._raw = raw_store
        self._calendar = calendar or XNYSCalendar()

    def calculate(self, *, start: date, end: date) -> AttributionReport:
        report, _observations = self.calculate_with_observations(start=start, end=end)
        return report

    def calculate_with_observations(
        self, *, start: date, end: date
    ) -> tuple[AttributionReport, tuple[AttributionObservation, ...]]:
        exit_report = ExitModelComparisonService(self._config, self._processed, self._raw, calendar=self._calendar).calculate(start=start, end=end)
        setup_result = BasePriceActionService(self._config, self._processed, self._raw, calendar=self._calendar).calculate(start=start, end=end)
        outcomes = SetupOutcomeService(self._config, self._processed, self._raw, calendar=self._calendar).calculate(start=start, end=end)
        bars = self._processed.load_processed_5m_bars(symbol=self._config.symbol, start=start, end=end, session_mode="RTH_ONLY")
        ema_rows = calculate_ema_sessions(bars)
        vwap_rows = calculate_vwap_sessions(bars)
        atr_rows = calculate_atr_sessions(bars)
        separation_rows = calculate_ema_separation_sessions(ema_rows)
        ema_crosses = _normalized_ema_crosses(
            ema_rows, separation_rows, vwap_rows, atr_rows
        )
        ema9_vwap_crosses, _ = detect_ema9_vwap_crosses(ema_rows, vwap_rows)
        ema20_vwap_crosses, _ = detect_ema20_vwap_crosses(ema_rows, vwap_rows)
        context_annotations = combine_context_annotations(
            setup_result,
            annotate_confirmed_setups(setup_result, ema_rows),
            annotate_prior_cross_context(setup_result, ema_crosses),
            annotate_confirmed_vwap_alignment(setup_result, bars, vwap_rows),
            annotate_confirmed_ema9_vwap_alignment(setup_result, ema_rows, vwap_rows),
            annotate_ema9_vwap_cross_context(setup_result, ema9_vwap_crosses),
            annotate_confirmed_ema20_vwap_alignment(setup_result, ema_rows, vwap_rows),
            annotate_ema20_vwap_cross_context(setup_result, ema20_vwap_crosses),
        )
        session_count = sum(
            self._calendar.session_for_date(start + timedelta(days=offset)).is_trading_day
            for offset in range((end - start).days + 1)
        )
        base_statistics = calculate_base_strategy_statistics(
            setup_result, outcomes, development_session_count=session_count
        )
        context = calculate_combined_context_matrix(
            setup_result, outcomes, base_statistics, context_annotations
        )
        market_annotations = calculate_market_condition_annotations(
            setup_result, bars, ema_rows, vwap_rows, atr_rows
        )
        market = calculate_market_condition_report(
            setup_result, outcomes, base_statistics, market_annotations
        )
        regime_annotations = build_regime_hypothesis_annotations(market)
        regime = calculate_regime_hypothesis_comparison(
            setup_result, outcomes, base_statistics, market, context, regime_annotations
        )

        previous = PreviousDayLevelsService(self._config, self._raw, calendar=self._calendar).calculate(start=start, end=end)
        premarket = PremarketLevelsService(self._config, self._raw, calendar=self._calendar).calculate(start=start, end=end)
        opening = OpeningFiveMinuteLevelsService(self._config, self._processed, self._raw, calendar=self._calendar).calculate(start=start, end=end)
        previous_by_date = {item.session_date: item for item in previous.levels}
        premarket_by_date = {item.session_date: item for item in premarket.levels}
        opening_by_date = {item.session_date: item for item in opening.levels}
        levels_by_session = {}
        for session_date in sorted(set(previous_by_date) | set(premarket_by_date) | set(opening_by_date)):
            session = self._calendar.session_for_date(session_date)
            if session.is_trading_day and session.market_open is not None:
                levels_by_session[session_date] = build_session_levels(
                    session_date=session_date,
                    market_open=session.market_open,
                    previous_day=previous_by_date.get(session_date),
                    premarket=premarket_by_date.get(session_date),
                    opening=opening_by_date.get(session_date),
                )
        room_annotations = build_room_annotations(
            setup_result, outcomes, bars, atr_rows, levels_by_session
        )
        room = calculate_room_to_level_comparison(
            setup_result, outcomes, base_statistics, context, regime, room_annotations
        )
        swings = detect_confirmed_swings(bars)
        structure_annotations = build_market_structure_annotations(
            setup_result, bars, atr_rows, swings, room
        )

        bars_by_session = defaultdict(list)
        for bar in bars:
            bars_by_session[bar.session_date].append(bar)
        all_interactions = []
        for session_date, session_bars in bars_by_session.items():
            all_interactions.extend(
                classify_session_level_interactions(
                    tuple(session_bars), levels_by_session.get(session_date, ()), emit_no_interaction=False
                )
            )

        setups = {item.setup_identity: item for item in setup_result.candidates}
        outcomes_by_id = {item.setup_identity: item for item in outcomes.outcomes}
        contexts = {item.setup_identity: item for item in context.annotations}
        regimes = {item.setup_identity: item for item in regime.annotations}
        rooms = {item.setup_identity: item for item in room.annotations}
        structures = {item.setup_identity: item for item in structure_annotations}
        bars_by_key = {(item.session_date, item.timestamp): item for item in bars}
        first_open = {}
        for item in bars:
            first_open.setdefault(item.session_date, item.open)
        prior_close = {item.session_date: item.pdc for item in previous.levels}
        interactions = defaultdict(list)
        for item in all_interactions:
            interactions[(item.session_date, item.level_type.value, item.level_price)].append(item)

        primary = tuple(
            item for item in exit_report.new_trades
            if item.strategy_population is StrategyPopulation.BASE_SHORT
            and item.variant.family is ExitFamily.NEXT_OBJECTIVE_LEVEL
            and item.variant.stop_model is AtrStopModel.ATR_1_00
        )
        observations = []
        for trade in primary:
            setup = setups[trade.setup_identity]
            outcome = outcomes_by_id[trade.setup_identity]
            context_row = contexts[trade.setup_identity]
            regime_row = regimes[trade.setup_identity]
            room_row = rooms[trade.setup_identity]
            structure_row = structures[trade.setup_identity]
            prior_n = sum(
                item.candle_timestamp < setup.break_timestamp
                for item in interactions[(setup.session_date, setup.level_type.value, setup.level_price)]
            )
            factors = {
                "LEVEL_TYPE": setup.level_type.value,
                "TIME_OF_DAY": _time_bucket(setup.signal_known_at),
                "ROOM_DOLLARS": _room_dollars(room_row.room_from_entry_reference, room_row.next_level_price is None),
                "ROOM_ATR": room_row.room_bucket.value,
                "MARKET_STRUCTURE": structure_row.combined_structure.value,
                "EMA_ALIGNMENT": context_row.ema9_20_alignment.value,
                "EMA_SEPARATION": regime_row.separation_state.value,
                "VWAP_ALIGNMENT": _vwap_alignment(context_row),
                "ATR_REGIME": _atr_regime(trade.confirmation_atr),
                "BREAK_QUALITY": _candle_quality(bars_by_key.get((setup.session_date, setup.break_timestamp))),
                "CONFIRMATION_QUALITY": _candle_quality(bars_by_key.get((setup.session_date, setup.confirmation_bar_timestamp))),
                "TREND_CHOP": regime_row.combined_state.value,
                "GAP_CONTEXT": _gap_context(first_open.get(setup.session_date), prior_close.get(setup.session_date), trade.confirmation_atr),
                "PRIOR_LEVEL_INTERACTIONS": "ZERO" if prior_n == 0 else "ONE" if prior_n == 1 else "TWO_PLUS",
                "CONFIRMATION_TYPE": setup.confirmation_type.value,
            }
            observations.append(AttributionObservation(
                setup_identity=trade.setup_identity,
                session_date=trade.session_date,
                signal_known_at=trade.signal_known_at,
                level_type=trade.level_type.value,
                outcome_status=trade.status.value,
                r_multiple=trade.r_multiple,
                exit_reason=trade.exit_reason.value if trade.exit_reason is not None else None,
                confirmation_atr=trade.confirmation_atr,
                five_minute_mfe=outcome.five.mfe if outcome.five is not None else None,
                five_minute_mae=outcome.five.mae if outcome.five is not None else None,
                mfe=outcome.eod.mfe if outcome.eod is not None else None,
                mae=outcome.eod.mae if outcome.eod is not None else None,
                factors=tuple(sorted(factors.items())),
            ))
        frozen_observations = tuple(observations)
        report = analyze_base_short_attribution(
            frozen_observations,
            start_date=start,
            end_date=end,
            fixed_factor_states=FIXED_FACTOR_STATES,
            source_exit_hash=exit_model_comparison_hash(exit_report),
            source_stage14_hash=ACCEPTED_STAGE14_4_HASH,
        )
        return report, frozen_observations
