"""Read-only Stage 13.1 composition over frozen Stage 3/9/12 records."""

from __future__ import annotations

from datetime import date

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.execution.fixed_risk import fixed_risk_variants, strategy_populations
from spy_research.execution.models import (
    ExecutableTradeSetup,
    ExecutionInputError,
    FixedRiskSimulationReport,
    PopulationReconciliation,
    StrategyPopulation,
)
from spy_research.execution.simulator import simulate_fixed_risk_trade
from spy_research.execution.statistics import calculate_fixed_risk_report
from spy_research.indicators import AtrIndicatorService
from spy_research.market import MarketSessionClassifier, SessionType
from spy_research.strategy.models import EntryStatus, SetupDirection
from spy_research.strategy.setup_outcome_service import SetupOutcomeService


FROZEN_START = date(2026, 1, 2)
FROZEN_END = date(2026, 8, 19)


class FixedRiskSimulationService:
    """Build accepted entries, freeze memberships, then simulate local raw bars."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
    ) -> None:
        self._config = config
        self._processed_store = processed_store
        self._raw_store = raw_store

    def calculate(self, *, start: date, end: date) -> FixedRiskSimulationReport:
        if start != FROZEN_START or end != FROZEN_END:
            raise ExecutionInputError(
                "Stage 13.1 requires the frozen 2026-01-02 through 2026-08-19 range"
            )
        outcomes = SetupOutcomeService(
            self._config,
            self._processed_store,
            self._raw_store,
        ).calculate(start=start, end=end)
        atr = AtrIndicatorService(
            self._config,
            self._processed_store,
            self._raw_store,
        ).calculate(start=start, end=end)
        atr_by_key = {
            (item.session_date, item.timestamp): item.atr14 for item in atr.rows
        }
        if len(atr_by_key) != len(atr.rows):
            raise ExecutionInputError("confirmation ATR rows contain duplicate keys")

        raw = self._raw_store.load_raw_bars(
            symbol=self._config.symbol,
            start=start,
            end=end,
            feed=self._config.data.feed,
            timeframe=self._config.data.timeframe,
        )
        rth_by_date = {}
        for item in MarketSessionClassifier().classify_many(raw):
            if item.session_type is SessionType.RTH:
                rth_by_date.setdefault(item.session_date, []).append(item.bar)

        confirmed_all = len(outcomes.outcomes)
        confirmed_short = sum(
            item.setup.direction is SetupDirection.SHORT for item in outcomes.outcomes
        )
        available = tuple(
            item
            for item in outcomes.outcomes
            if item.entry_reference.entry_status is EntryStatus.AVAILABLE
        )
        setups = []
        for item in available:
            setup = item.setup
            entry = item.entry_reference
            if (
                setup.confirmation_bar_timestamp is None
                or setup.signal_known_at is None
                or entry.entry_reference_timestamp is None
                or entry.entry_reference_price is None
            ):
                raise ExecutionInputError("accepted executable setup lacks frozen timing")
            setups.append(
                ExecutableTradeSetup(
                    setup_identity=setup.setup_identity,
                    session_date=setup.session_date,
                    direction=setup.direction,
                    level_type=setup.level_type,
                    confirmation_bar_timestamp=setup.confirmation_bar_timestamp,
                    signal_known_at=setup.signal_known_at,
                    entry_timestamp=entry.entry_reference_timestamp,
                    entry_price=entry.entry_reference_price,
                )
            )
        if len({item.setup_identity for item in setups}) != len(setups):
            raise ExecutionInputError("duplicate executable setup identity")

        variants = fixed_risk_variants()
        trades = []
        for setup in setups:
            confirmation_atr = atr_by_key.get(
                (setup.session_date, setup.confirmation_bar_timestamp)
            )
            bars = tuple(rth_by_date.get(setup.session_date, ()))
            for population in strategy_populations(setup):
                for variant in variants:
                    trades.append(
                        simulate_fixed_risk_trade(
                            setup,
                            population,
                            variant,
                            confirmation_atr,
                            bars,
                        )
                    )
        eligible_short = sum(item.direction is SetupDirection.SHORT for item in setups)
        populations = (
            PopulationReconciliation(
                strategy_population=StrategyPopulation.BASE_ALL,
                confirmed_membership_n=confirmed_all,
                eligible_entry_n=len(setups),
            ),
            PopulationReconciliation(
                strategy_population=StrategyPopulation.BASE_SHORT,
                confirmed_membership_n=confirmed_short,
                eligible_entry_n=eligible_short,
            ),
        )
        return calculate_fixed_risk_report(
            trades,
            populations,
            variants,
            start=start,
            end=end,
        )
