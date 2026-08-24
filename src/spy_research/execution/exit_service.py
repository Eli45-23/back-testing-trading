"""Read-only Stage 13.2 composition over accepted execution and research sources."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from hashlib import sha256

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.events.ema_cross import detect_ema_crosses
from spy_research.execution.exit_models import (
    ExitComparisonInputError,
    ExitFamily,
    ExitModelComparisonReport,
    NormalizedCrossExitEvent,
)
from spy_research.execution.exit_simulator import (
    select_opposite_cross_exit,
    simulate_exit_model_trade,
)
from spy_research.execution.exit_statistics import (
    BOOTSTRAP_RESAMPLES,
    BOOTSTRAP_SEED,
    bootstrap_exit_variant,
    summarize_exit_variant,
    trade_views,
)
from spy_research.execution.exit_variants import exit_model_variants
from spy_research.execution.models import (
    AtrStopModel,
    ExecutableTradeSetup,
    RiskTargetModel,
    StrategyPopulation,
)
from spy_research.execution.service import FROZEN_END, FROZEN_START
from spy_research.execution.service import FixedRiskSimulationService
from spy_research.indicators.atr import calculate_atr_sessions
from spy_research.indicators.ema import calculate_ema_sessions
from spy_research.indicators.vwap import calculate_vwap_sessions
from spy_research.interactions import build_session_levels
from spy_research.levels import (
    OpeningFiveMinuteLevelsService,
    PremarketLevelsService,
    PreviousDayLevelsService,
)
from spy_research.market import MarketSessionClassifier, SessionType, XNYSCalendar
from spy_research.strategy.base_price_action_service import BasePriceActionService
from spy_research.strategy.comparisons.ema20_vwap_cross import (
    detect_ema20_vwap_crosses,
)
from spy_research.strategy.comparisons.ema9_vwap_cross import (
    detect_ema9_vwap_crosses,
)
from spy_research.strategy.comparisons.room_to_level import (
    NextLevelAvailability,
    select_room_to_next_level,
)
from spy_research.strategy.models import BaseSetupStatus


class ExitModelComparisonService:
    """Simulate 21 new exits beside the exact accepted Stage 13.1 control."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
        *,
        calendar: XNYSCalendar | None = None,
    ) -> None:
        self._config = config
        self._processed_store = processed_store
        self._raw_store = raw_store
        self._calendar = calendar or XNYSCalendar()

    def calculate(self, *, start: date, end: date) -> ExitModelComparisonReport:
        if start != FROZEN_START or end != FROZEN_END:
            raise ExitComparisonInputError(
                "Stage 13.2 requires the frozen 2026-01-02 through 2026-08-19 range"
            )
        control = FixedRiskSimulationService(
            self._config,
            self._processed_store,
            self._raw_store,
        ).calculate(start=start, end=end)
        setups, atr_by_id = self._setups_from_control(control)
        bars = self._processed_store.load_processed_5m_bars(
            symbol=self._config.symbol,
            start=start,
            end=end,
            session_mode="RTH_ONLY",
        )
        ema_rows = calculate_ema_sessions(bars)
        vwap_rows = calculate_vwap_sessions(bars)
        atr_rows = calculate_atr_sessions(bars)
        cross_events = self._cross_events(ema_rows, vwap_rows)
        room_by_id = self._objective_annotations(
            setups,
            bars,
            atr_rows,
            start=start,
            end=end,
        )
        raw = self._raw_store.load_raw_bars(
            symbol=self._config.symbol,
            start=start,
            end=end,
            feed=self._config.data.feed,
            timeframe=self._config.data.timeframe,
        )
        rth_by_date = defaultdict(list)
        for item in MarketSessionClassifier(self._calendar).classify_many(raw):
            if item.session_type is SessionType.RTH:
                rth_by_date[item.session_date].append(item.bar)

        variants = exit_model_variants()
        new_variants = tuple(
            item for item in variants if item.family is not ExitFamily.FIXED_R_CONTROL
        )
        new_trades = []
        for setup in setups:
            schedules = {
                family: select_opposite_cross_exit(
                    setup,
                    family,
                    cross_events.get((family, setup.session_date), ()),
                )
                for family in (
                    ExitFamily.OPPOSITE_EMA9_20_CROSS,
                    ExitFamily.OPPOSITE_EMA9_VWAP_CROSS,
                    ExitFamily.OPPOSITE_EMA20_VWAP_CROSS,
                )
            }
            room = room_by_id[setup.setup_identity]
            for population in (
                (StrategyPopulation.BASE_ALL, StrategyPopulation.BASE_SHORT)
                if setup.direction.value == "SHORT"
                else (StrategyPopulation.BASE_ALL,)
            ):
                for variant in new_variants:
                    is_objective = (
                        variant.family is ExitFamily.NEXT_OBJECTIVE_LEVEL
                    )
                    new_trades.append(
                        simulate_exit_model_trade(
                            setup,
                            population,
                            variant,
                            atr_by_id[setup.setup_identity],
                            tuple(rth_by_date[setup.session_date]),
                            scheduled_exit=schedules.get(variant.family),
                            objective_price=(
                                room.next_level_price if is_objective else None
                            ),
                            objective_level_types=(
                                room.next_level_types if is_objective else ()
                            ),
                            objective_available=(
                                not is_objective
                                or room.next_level_availability
                                is NextLevelAvailability.AVAILABLE
                            ),
                        )
                    )
        views = trade_views(control.trades, new_trades)
        statistics = tuple(
            summarize_exit_variant(
                views,
                population=population,
                variant=variant,
            )
            for population in StrategyPopulation
            for variant in variants
        )
        bootstrap = tuple(
            bootstrap_exit_variant(
                views,
                population=population,
                variant=variant,
                seed=BOOTSTRAP_SEED,
                resamples=BOOTSTRAP_RESAMPLES,
            )
            for population in StrategyPopulation
            for variant in variants
        )
        return ExitModelComparisonReport(
            start_date=start,
            end_date=end,
            populations=control.populations,
            variants=variants,
            stage13_1_control=control,
            new_trades=tuple(new_trades),
            statistics=statistics,
            bootstrap_uncertainty=bootstrap,
            bootstrap_seed=BOOTSTRAP_SEED,
            bootstrap_resamples=BOOTSTRAP_RESAMPLES,
        )

    @staticmethod
    def _setups_from_control(control):
        anchors = tuple(
            item
            for item in control.trades
            if item.strategy_population is StrategyPopulation.BASE_ALL
            and item.stop_model is AtrStopModel.ATR_0_50
            and item.target_model is RiskTargetModel.R_1
        )
        if len(anchors) != control.populations[0].eligible_entry_n:
            raise ExitComparisonInputError("Stage 13.1 control anchors do not reconcile")
        setups = tuple(
            ExecutableTradeSetup(
                setup_identity=item.setup_identity,
                session_date=item.session_date,
                direction=item.direction,
                level_type=item.level_type,
                confirmation_bar_timestamp=item.confirmation_bar_timestamp,
                signal_known_at=item.signal_known_at,
                entry_timestamp=item.entry_timestamp,
                entry_price=item.entry_price,
            )
            for item in anchors
        )
        return setups, {item.setup_identity: item.confirmation_atr for item in anchors}

    @staticmethod
    def _cross_events(ema_rows, vwap_rows):
        grouped = defaultdict(list)
        for item in detect_ema_crosses(ema_rows):
            family = ExitFamily.OPPOSITE_EMA9_20_CROSS
            identity = sha256(
                (
                    f"{family.value}|{item.session_date}|{item.timestamp.isoformat()}|"
                    f"{item.direction.value}|{item.detector_version}"
                ).encode()
            ).hexdigest()
            grouped[(family, item.session_date)].append(
                NormalizedCrossExitEvent(
                    event_identity=identity,
                    family=family,
                    session_date=item.session_date,
                    direction=item.direction.value,
                    cross_timestamp=item.timestamp,
                    cross_known_at=item.timestamp + timedelta(minutes=5),
                )
            )
        ema9_events, _ = detect_ema9_vwap_crosses(ema_rows, vwap_rows)
        for item in ema9_events:
            family = ExitFamily.OPPOSITE_EMA9_VWAP_CROSS
            grouped[(family, item.session_date)].append(
                NormalizedCrossExitEvent(
                    event_identity=item.event_identity,
                    family=family,
                    session_date=item.session_date,
                    direction=item.direction.value,
                    cross_timestamp=item.cross_timestamp,
                    cross_known_at=item.cross_known_at,
                )
            )
        ema20_events, _ = detect_ema20_vwap_crosses(ema_rows, vwap_rows)
        for item in ema20_events:
            family = ExitFamily.OPPOSITE_EMA20_VWAP_CROSS
            grouped[(family, item.session_date)].append(
                NormalizedCrossExitEvent(
                    event_identity=item.event_identity,
                    family=family,
                    session_date=item.session_date,
                    direction=item.direction.value,
                    cross_timestamp=item.cross_timestamp,
                    cross_known_at=item.cross_known_at,
                )
            )
        return {key: tuple(value) for key, value in grouped.items()}

    def _objective_annotations(self, setups, bars, atr_rows, *, start, end):
        setup_result = BasePriceActionService(
            self._config,
            self._processed_store,
            self._raw_store,
            calendar=self._calendar,
        ).calculate(start=start, end=end)
        candidates = {
            item.setup_identity: item
            for item in setup_result.candidates
            if item.status is BaseSetupStatus.CONFIRMED
        }
        bar_by_key = {(item.session_date, item.timestamp): item for item in bars}
        atr_by_key = {(item.session_date, item.timestamp): item for item in atr_rows}
        previous = PreviousDayLevelsService(
            self._config,
            self._raw_store,
            calendar=self._calendar,
        ).calculate(start=start, end=end)
        premarket = PremarketLevelsService(
            self._config,
            self._raw_store,
            calendar=self._calendar,
        ).calculate(start=start, end=end)
        opening = OpeningFiveMinuteLevelsService(
            self._config,
            self._processed_store,
            self._raw_store,
            calendar=self._calendar,
        ).calculate(start=start, end=end)
        sources = (
            {item.session_date: item for item in previous.levels},
            {item.session_date: item for item in premarket.levels},
            {item.session_date: item for item in opening.levels},
        )
        levels_by_session = {}
        for session_date in sorted(set().union(*(set(item) for item in sources))):
            session = self._calendar.session_for_date(session_date)
            if not session.is_trading_day or session.market_open is None:
                continue
            levels_by_session[session_date] = build_session_levels(
                session_date=session_date,
                market_open=session.market_open,
                previous_day=sources[0].get(session_date),
                premarket=sources[1].get(session_date),
                opening=sources[2].get(session_date),
            )
        annotations = {}
        for setup in setups:
            candidate = candidates.get(setup.setup_identity)
            key = (setup.session_date, setup.confirmation_bar_timestamp)
            if candidate is None or key not in bar_by_key or key not in atr_by_key:
                raise ExitComparisonInputError(
                    "Stage 11.2 objective source does not reconcile to execution"
                )
            annotations[setup.setup_identity] = select_room_to_next_level(
                candidate,
                confirmation_price=bar_by_key[key].close,
                entry_price=setup.entry_price,
                atr14=atr_by_key[key].atr14,
                levels=levels_by_session.get(setup.session_date, ()),
            )
        return annotations
