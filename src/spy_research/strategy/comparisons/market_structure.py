"""Stage 11.3 confirmed five-minute swing-structure measurements."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Sequence
from datetime import date, datetime, timedelta
from decimal import Decimal, localcontext
from enum import StrEnum
from hashlib import sha256
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.bars import FiveMinuteBar
from spy_research.indicators import FiveMinuteAtrRow
from spy_research.indicators.atr import ATR_CONTEXT
from spy_research.interactions import LevelType
from spy_research.strategy.base_statistics import (
    BaseStrategyGroupDimension,
    BaseStrategyHorizonStatistics,
    BaseStrategyStatistics,
    summarize_base_outcome_group,
)
from spy_research.strategy.comparisons.combined_context import (
    CombinedContextMatrixResult,
)
from spy_research.strategy.comparisons.ema20_vwap_alignment import (
    Ema20VwapAlignmentState,
)
from spy_research.strategy.comparisons.models import (
    Ema9VwapAlignmentState,
    EmaAlignmentState,
    VwapAlignmentState,
)
from spy_research.strategy.comparisons.regime_hypotheses import (
    CombinedRegimeState,
    RegimeHypothesisComparisonResult,
    RegimeLevelCount,
    RegimeSessionCount,
)
from spy_research.strategy.comparisons.room_to_level import (
    NextLevelAvailability,
    RoomBucket,
    RoomToLevelAnnotation,
    RoomToLevelComparisonResult,
)
from spy_research.strategy.models import (
    BasePriceActionCandidate,
    BasePriceActionResult,
    BaseSetupStatus,
    EntryStatus,
    SetupDirection,
    SetupOutcome,
    SetupOutcomeResult,
)


HORIZON_ORDER = ("5m", "15m", "30m", "60m", "EOD")
PIVOT_LEFT = 2
PIVOT_RIGHT = 2
PIVOT_KNOWN_DELAY = timedelta(minutes=15)
CONTEXT_SPECS = (
    ("REGIME_HYPOTHESIS", "combined_state", CombinedRegimeState),
    ("ROOM_BUCKET", "room_bucket", RoomBucket),
    ("EMA9_20_ALIGNMENT", "ema9_20_alignment", EmaAlignmentState),
    ("PRICE_VWAP_ALIGNMENT", "price_vwap_alignment", VwapAlignmentState),
    ("EMA9_VWAP_ALIGNMENT", "ema9_vwap_alignment", Ema9VwapAlignmentState),
    ("EMA20_VWAP_ALIGNMENT", "ema20_vwap_alignment", Ema20VwapAlignmentState),
)


class MarketStructureInputError(ValueError):
    """Frozen bars, setups, indicators, and comparison sources do not reconcile."""


class SwingType(StrEnum):
    HIGH = "HIGH"
    LOW = "LOW"


class HighStructureState(StrEnum):
    HIGHER_HIGH = "HIGHER_HIGH"
    LOWER_HIGH = "LOWER_HIGH"
    EQUAL_HIGH = "EQUAL_HIGH"
    UNAVAILABLE = "UNAVAILABLE"


class LowStructureState(StrEnum):
    HIGHER_LOW = "HIGHER_LOW"
    LOWER_LOW = "LOWER_LOW"
    EQUAL_LOW = "EQUAL_LOW"
    UNAVAILABLE = "UNAVAILABLE"


class CombinedStructureState(StrEnum):
    BULLISH = "BULLISH_STRUCTURE"
    BEARISH = "BEARISH_STRUCTURE"
    MIXED = "MIXED_STRUCTURE"
    UNAVAILABLE = "UNAVAILABLE"


class StructureAgreementState(StrEnum):
    ALIGNED = "STRUCTURE_ALIGNED"
    NOT_ALIGNED = "STRUCTURE_NOT_ALIGNED"
    UNAVAILABLE = "STRUCTURE_UNAVAILABLE"


class StructuralRoomState(StrEnum):
    SWING_BEYOND_OBJECTIVE_LEVEL = "SWING_BEYOND_OBJECTIVE_LEVEL"
    SWING_NOT_BEYOND_OBJECTIVE_LEVEL = "SWING_NOT_BEYOND_OBJECTIVE_LEVEL"
    OBJECTIVE_LEVEL_OPEN_ENDED = "OBJECTIVE_LEVEL_OPEN_ENDED"
    DIRECTIONAL_SWING_UNAVAILABLE = "DIRECTIONAL_SWING_UNAVAILABLE"


class ConfirmedSwing(BaseModel):
    """One immutable pivot after both required right candles have completed."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    session_date: date
    pivot_timestamp: datetime
    pivot_known_at: datetime
    swing_type: SwingType
    swing_price: Decimal
    left_bars: Literal[2] = 2
    right_bars: Literal[2] = 2
    source_timeframe: Literal["5Min"] = "5Min"
    source_session: Literal["RTH"] = "RTH"
    swing_version: Literal["confirmed-pivot-2x2-v1"] = "confirmed-pivot-2x2-v1"

    @model_validator(mode="after")
    def validate_confirmation_time(self) -> Self:
        if self.pivot_timestamp.utcoffset() is None:
            raise ValueError("pivot timestamp must be timezone-aware")
        if self.pivot_known_at != self.pivot_timestamp + PIVOT_KNOWN_DELAY:
            raise ValueError("2x2 pivot must be known exactly 15 minutes later")
        return self


class MarketStructureAnnotation(BaseModel):
    """Outcome-blind structure visible when one frozen setup becomes known."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    direction: SetupDirection
    triggering_level_type: LevelType
    confirmation_bar_timestamp: datetime
    signal_known_at: datetime
    confirmation_close: Decimal
    latest_confirmed_swing_high: ConfirmedSwing | None
    previous_confirmed_swing_high: ConfirmedSwing | None
    latest_confirmed_swing_low: ConfirmedSwing | None
    previous_confirmed_swing_low: ConfirmedSwing | None
    high_structure: HighStructureState
    low_structure: LowStructureState
    combined_structure: CombinedStructureState
    direction_agreement: StructureAgreementState
    confirmation_close_to_latest_swing_high: Decimal | None = Field(
        default=None, ge=0
    )
    confirmation_close_to_latest_swing_low: Decimal | None = Field(
        default=None, ge=0
    )
    atr14: Decimal | None = Field(default=None, gt=0)
    distance_to_swing_high_in_atr: Decimal | None = Field(default=None, ge=0)
    distance_to_swing_low_in_atr: Decimal | None = Field(default=None, ge=0)
    structural_room_state: StructuralRoomState
    structure_version: Literal["confirmed-5m-structure-2x2-v1"] = (
        "confirmed-5m-structure-2x2-v1"
    )

    @model_validator(mode="after")
    def reconcile_annotation(self) -> Self:
        pairs = (
            (
                self.latest_confirmed_swing_high,
                self.previous_confirmed_swing_high,
                self.high_structure,
                HighStructureState.UNAVAILABLE,
                SwingType.HIGH,
            ),
            (
                self.latest_confirmed_swing_low,
                self.previous_confirmed_swing_low,
                self.low_structure,
                LowStructureState.UNAVAILABLE,
                SwingType.LOW,
            ),
        )
        for latest, previous, state, unavailable, swing_type in pairs:
            if latest is not None and latest.swing_type is not swing_type:
                raise ValueError("latest swing type mismatch")
            if previous is not None and previous.swing_type is not swing_type:
                raise ValueError("previous swing type mismatch")
            if (latest is None or previous is None) != (state is unavailable):
                raise ValueError("structure availability requires two swings")
            if latest is not None and latest.pivot_known_at > self.signal_known_at:
                raise ValueError("future-confirmed swing cannot annotate setup")
            if previous is not None and previous.pivot_known_at > self.signal_known_at:
                raise ValueError("future-confirmed swing cannot annotate setup")
            if latest is not None and latest.session_date != self.session_date:
                raise ValueError("latest swing must match setup session")
            if previous is not None and previous.session_date != self.session_date:
                raise ValueError("previous swing must match setup session")
            if (
                latest is not None
                and previous is not None
                and previous.pivot_timestamp >= latest.pivot_timestamp
            ):
                raise ValueError("previous swing must precede latest swing")
        if self.high_structure is not _high_state(
            self.latest_confirmed_swing_high,
            self.previous_confirmed_swing_high,
        ):
            raise ValueError("high structure does not match swing prices")
        if self.low_structure is not _low_state(
            self.latest_confirmed_swing_low,
            self.previous_confirmed_swing_low,
        ):
            raise ValueError("low structure does not match swing prices")
        if self.combined_structure is not _combined_state(
            self.high_structure, self.low_structure
        ):
            raise ValueError("combined structure does not match high/low states")
        combined_unavailable = self.combined_structure is CombinedStructureState.UNAVAILABLE
        if combined_unavailable != (
            self.high_structure is HighStructureState.UNAVAILABLE
            or self.low_structure is LowStructureState.UNAVAILABLE
        ):
            raise ValueError("combined structure availability mismatch")
        if combined_unavailable != (
            self.direction_agreement is StructureAgreementState.UNAVAILABLE
        ):
            raise ValueError("direction agreement availability mismatch")
        expected_agreement = (
            StructureAgreementState.UNAVAILABLE
            if combined_unavailable
            else StructureAgreementState.ALIGNED
            if (
                self.direction is SetupDirection.LONG
                and self.combined_structure is CombinedStructureState.BULLISH
            )
            or (
                self.direction is SetupDirection.SHORT
                and self.combined_structure is CombinedStructureState.BEARISH
            )
            else StructureAgreementState.NOT_ALIGNED
        )
        if self.direction_agreement is not expected_agreement:
            raise ValueError("direction agreement does not match structure")
        expected_high_distance = (
            abs(
                self.confirmation_close
                - self.latest_confirmed_swing_high.swing_price
            )
            if self.latest_confirmed_swing_high is not None
            else None
        )
        expected_low_distance = (
            abs(
                self.confirmation_close
                - self.latest_confirmed_swing_low.swing_price
            )
            if self.latest_confirmed_swing_low is not None
            else None
        )
        if self.confirmation_close_to_latest_swing_high != expected_high_distance:
            raise ValueError("swing-high distance mismatch")
        if self.confirmation_close_to_latest_swing_low != expected_low_distance:
            raise ValueError("swing-low distance mismatch")
        if self.atr14 is None:
            if (
                self.distance_to_swing_high_in_atr is not None
                or self.distance_to_swing_low_in_atr is not None
            ):
                raise ValueError("normalized swing distances require ATR")
        else:
            with localcontext(ATR_CONTEXT):
                expected_high_atr = (
                    expected_high_distance / self.atr14
                    if expected_high_distance is not None
                    else None
                )
                expected_low_atr = (
                    expected_low_distance / self.atr14
                    if expected_low_distance is not None
                    else None
                )
            if self.distance_to_swing_high_in_atr != expected_high_atr:
                raise ValueError("ATR-normalized swing-high distance mismatch")
            if self.distance_to_swing_low_in_atr != expected_low_atr:
                raise ValueError("ATR-normalized swing-low distance mismatch")
        return self


class SwingSessionSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    swing_high_count: int = Field(ge=0)
    swing_low_count: int = Field(ge=0)
    earliest_pivot_known_at: datetime | None
    latest_pivot_known_at: datetime | None

    @model_validator(mode="after")
    def reconcile_summary(self) -> Self:
        empty = self.swing_high_count + self.swing_low_count == 0
        if empty != (self.earliest_pivot_known_at is None):
            raise ValueError("empty swing session cannot have earliest known time")
        if empty != (self.latest_pivot_known_at is None):
            raise ValueError("empty swing session cannot have latest known time")
        return self


class StructureGroupStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    dimension: Literal["COMBINED_STRUCTURE", "DIRECTION_AGREEMENT"]
    state: str
    annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    long_annotation_n: int = Field(ge=0)
    short_annotation_n: int = Field(ge=0)
    session_count: int = Field(ge=0)
    session_composition: tuple[RegimeSessionCount, ...]
    level_composition: tuple[RegimeLevelCount, ...]
    horizons: tuple[BaseStrategyHorizonStatistics, ...]

    @model_validator(mode="after")
    def reconcile_group(self) -> Self:
        if self.long_annotation_n + self.short_annotation_n != self.annotation_n:
            raise ValueError("structure directions must reconcile")
        if sum(item.annotation_n for item in self.session_composition) != self.annotation_n:
            raise ValueError("structure sessions must reconcile")
        if sum(item.annotation_n for item in self.level_composition) != self.annotation_n:
            raise ValueError("structure levels must reconcile")
        if self.session_count != len(self.session_composition):
            raise ValueError("structure session count mismatch")
        if tuple(item.horizon for item in self.horizons) != HORIZON_ORDER:
            raise ValueError("structure horizons must use frozen ordering")
        return self


class StructureContextCrossTab(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    structure_state: CombinedStructureState
    context_dimension: str
    context_state: str
    annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    eod: BaseStrategyHorizonStatistics

    @model_validator(mode="after")
    def eod_only(self) -> Self:
        if self.eod.horizon != "EOD":
            raise ValueError("structure cross-tabs report EOD only")
        return self


class StructureAuditRow(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    annotation: MarketStructureAnnotation
    regime_hypothesis: CombinedRegimeState
    room_bucket: RoomBucket
    eod_mfe: Decimal | None
    eod_mae: Decimal | None


class MarketStructureComparisonResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    start_date: date
    end_date: date
    break_seed_count: int = Field(ge=0)
    confirmed_count: int = Field(ge=0)
    non_confirmed_count: int = Field(ge=0)
    executable_count: int = Field(ge=0)
    session_end_unavailable_count: int = Field(ge=0)
    missing_entry_count: int = Field(ge=0)
    development_session_count: int = Field(ge=0)
    total_confirmed_swing_highs: int = Field(ge=0)
    total_confirmed_swing_lows: int = Field(ge=0)
    source_stage11_1_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_stage11_2_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    swings: tuple[ConfirmedSwing, ...]
    swing_sessions: tuple[SwingSessionSummary, ...]
    annotations: tuple[MarketStructureAnnotation, ...]
    groups: tuple[StructureGroupStatistics, ...]
    cross_tabs: tuple[StructureContextCrossTab, ...]
    audit_rows: tuple[StructureAuditRow, ...]
    base_all_horizons: tuple[BaseStrategyHorizonStatistics, ...]
    report_version: Literal["confirmed-5m-market-structure-comparison-v1"] = (
        "confirmed-5m-market-structure-comparison-v1"
    )
    sample_warning: str = (
        "Thirteen-session development sample; structure states are descriptive, not filters."
    )

    @model_validator(mode="after")
    def reconcile_result(self) -> Self:
        if len(self.annotations) != self.confirmed_count:
            raise ValueError("every confirmed setup requires a structure annotation")
        if len(self.audit_rows) != self.confirmed_count:
            raise ValueError("every confirmed setup requires an audit row")
        if len({item.setup_identity for item in self.annotations}) != len(
            self.annotations
        ):
            raise ValueError("structure annotations require unique setup identities")
        if self.total_confirmed_swing_highs != sum(
            item.swing_type is SwingType.HIGH for item in self.swings
        ):
            raise ValueError("swing-high count mismatch")
        if self.total_confirmed_swing_lows != sum(
            item.swing_type is SwingType.LOW for item in self.swings
        ):
            raise ValueError("swing-low count mismatch")
        if sum(item.swing_high_count for item in self.swing_sessions) != (
            self.total_confirmed_swing_highs
        ):
            raise ValueError("session swing-high counts do not reconcile")
        if sum(item.swing_low_count for item in self.swing_sessions) != (
            self.total_confirmed_swing_lows
        ):
            raise ValueError("session swing-low counts do not reconcile")
        for dimension in ("COMBINED_STRUCTURE", "DIRECTION_AGREEMENT"):
            rows = tuple(item for item in self.groups if item.dimension == dimension)
            if sum(item.annotation_n for item in rows) != self.confirmed_count:
                raise ValueError("structure groups must partition annotations")
            if sum(item.executable_n for item in rows) != self.executable_count:
                raise ValueError("structure groups must partition outcomes")
        expected_tabs = tuple(
            (structure, dimension, state.value)
            for structure in CombinedStructureState
            for dimension, _field, states in CONTEXT_SPECS
            for state in states
        )
        if tuple(
            (item.structure_state, item.context_dimension, item.context_state)
            for item in self.cross_tabs
        ) != expected_tabs:
            raise ValueError("structure cross-tabs must use frozen ordering")
        combined_groups = {
            item.state: item
            for item in self.groups
            if item.dimension == "COMBINED_STRUCTURE"
        }
        for structure in CombinedStructureState:
            for dimension, _field, _states in CONTEXT_SPECS:
                rows = tuple(
                    item
                    for item in self.cross_tabs
                    if item.structure_state is structure
                    and item.context_dimension == dimension
                )
                expected = combined_groups[structure.value]
                if sum(item.annotation_n for item in rows) != expected.annotation_n:
                    raise ValueError("structure cross-tab annotations must reconcile")
                if sum(item.executable_n for item in rows) != expected.executable_n:
                    raise ValueError("structure cross-tab outcomes must reconcile")
        if tuple(item.horizon for item in self.base_all_horizons) != HORIZON_ORDER:
            raise ValueError("BASE_ALL horizons must use frozen ordering")
        return self


def detect_confirmed_swings(
    bars: Sequence[FiveMinuteBar],
) -> tuple[ConfirmedSwing, ...]:
    """Detect the frozen 2-left/2-right pivots independently per RTH session."""

    ordered = tuple(bars)
    keys = tuple((item.session_date, item.timestamp) for item in ordered)
    if keys != tuple(sorted(keys)):
        raise MarketStructureInputError("Five-minute bars must be chronological")
    if len(set(keys)) != len(keys):
        raise MarketStructureInputError("Duplicate five-minute timestamp")
    by_session: dict[date, list[FiveMinuteBar]] = defaultdict(list)
    for bar in ordered:
        by_session[bar.session_date].append(bar)
    swings: list[ConfirmedSwing] = []
    for session_date in sorted(by_session):
        session_bars = by_session[session_date]
        for index in range(PIVOT_LEFT, len(session_bars) - PIVOT_RIGHT):
            pivot = session_bars[index]
            left = session_bars[index - 2 : index]
            right = session_bars[index + 1 : index + 3]
            if all(pivot.high > item.high for item in left) and all(
                pivot.high >= item.high for item in right
            ):
                swings.append(
                    ConfirmedSwing(
                        session_date=session_date,
                        pivot_timestamp=pivot.timestamp,
                        pivot_known_at=pivot.timestamp + PIVOT_KNOWN_DELAY,
                        swing_type=SwingType.HIGH,
                        swing_price=pivot.high,
                    )
                )
            if all(pivot.low < item.low for item in left) and all(
                pivot.low <= item.low for item in right
            ):
                swings.append(
                    ConfirmedSwing(
                        session_date=session_date,
                        pivot_timestamp=pivot.timestamp,
                        pivot_known_at=pivot.timestamp + PIVOT_KNOWN_DELAY,
                        swing_type=SwingType.LOW,
                        swing_price=pivot.low,
                    )
                )
    return tuple(
        sorted(
            swings,
            key=lambda item: (
                item.session_date,
                item.pivot_timestamp,
                tuple(SwingType).index(item.swing_type),
            ),
        )
    )


def _high_state(
    latest: ConfirmedSwing | None,
    previous: ConfirmedSwing | None,
) -> HighStructureState:
    if latest is None or previous is None:
        return HighStructureState.UNAVAILABLE
    if latest.swing_price > previous.swing_price:
        return HighStructureState.HIGHER_HIGH
    if latest.swing_price < previous.swing_price:
        return HighStructureState.LOWER_HIGH
    return HighStructureState.EQUAL_HIGH


def _low_state(
    latest: ConfirmedSwing | None,
    previous: ConfirmedSwing | None,
) -> LowStructureState:
    if latest is None or previous is None:
        return LowStructureState.UNAVAILABLE
    if latest.swing_price > previous.swing_price:
        return LowStructureState.HIGHER_LOW
    if latest.swing_price < previous.swing_price:
        return LowStructureState.LOWER_LOW
    return LowStructureState.EQUAL_LOW


def _combined_state(
    high: HighStructureState,
    low: LowStructureState,
) -> CombinedStructureState:
    if high is HighStructureState.UNAVAILABLE or low is LowStructureState.UNAVAILABLE:
        return CombinedStructureState.UNAVAILABLE
    if (
        high is HighStructureState.HIGHER_HIGH
        and low is LowStructureState.HIGHER_LOW
    ):
        return CombinedStructureState.BULLISH
    if high is HighStructureState.LOWER_HIGH and low is LowStructureState.LOWER_LOW:
        return CombinedStructureState.BEARISH
    return CombinedStructureState.MIXED


def annotate_market_structure(
    setup: BasePriceActionCandidate,
    *,
    confirmation_close: Decimal,
    atr14: Decimal | None,
    swings: Sequence[ConfirmedSwing],
    room: RoomToLevelAnnotation,
) -> MarketStructureAnnotation:
    """Measure only swings confirmed by the setup's frozen known-at timestamp."""

    if setup.status is not BaseSetupStatus.CONFIRMED or setup.signal_known_at is None:
        raise MarketStructureInputError("Structure annotation requires confirmed setup")
    if room.setup_identity != setup.setup_identity:
        raise MarketStructureInputError("Stage 11.2 room identity mismatch")
    visible = tuple(
        item
        for item in swings
        if item.session_date == setup.session_date
        and item.pivot_known_at <= setup.signal_known_at
    )
    highs = tuple(item for item in visible if item.swing_type is SwingType.HIGH)
    lows = tuple(item for item in visible if item.swing_type is SwingType.LOW)
    latest_high = highs[-1] if highs else None
    previous_high = highs[-2] if len(highs) >= 2 else None
    latest_low = lows[-1] if lows else None
    previous_low = lows[-2] if len(lows) >= 2 else None
    high_state = _high_state(latest_high, previous_high)
    low_state = _low_state(latest_low, previous_low)
    combined = _combined_state(high_state, low_state)
    if combined is CombinedStructureState.UNAVAILABLE:
        agreement = StructureAgreementState.UNAVAILABLE
    elif (
        setup.direction is SetupDirection.LONG
        and combined is CombinedStructureState.BULLISH
    ) or (
        setup.direction is SetupDirection.SHORT
        and combined is CombinedStructureState.BEARISH
    ):
        agreement = StructureAgreementState.ALIGNED
    else:
        agreement = StructureAgreementState.NOT_ALIGNED
    high_distance = (
        abs(confirmation_close - latest_high.swing_price)
        if latest_high is not None
        else None
    )
    low_distance = (
        abs(confirmation_close - latest_low.swing_price)
        if latest_low is not None
        else None
    )
    effective_atr = atr14 if atr14 is not None and atr14 > 0 else None
    with localcontext(ATR_CONTEXT):
        high_normalized = (
            high_distance / effective_atr
            if high_distance is not None and effective_atr is not None
            else None
        )
        low_normalized = (
            low_distance / effective_atr
            if low_distance is not None and effective_atr is not None
            else None
        )
    directional_swing = (
        latest_high if setup.direction is SetupDirection.LONG else latest_low
    )
    if directional_swing is None:
        structural_room = StructuralRoomState.DIRECTIONAL_SWING_UNAVAILABLE
    elif room.next_level_availability is NextLevelAvailability.OPEN_ENDED:
        structural_room = StructuralRoomState.OBJECTIVE_LEVEL_OPEN_ENDED
    else:
        assert room.next_level_price is not None
        beyond = (
            directional_swing.swing_price > room.next_level_price
            if setup.direction is SetupDirection.LONG
            else directional_swing.swing_price < room.next_level_price
        )
        structural_room = (
            StructuralRoomState.SWING_BEYOND_OBJECTIVE_LEVEL
            if beyond
            else StructuralRoomState.SWING_NOT_BEYOND_OBJECTIVE_LEVEL
        )
    return MarketStructureAnnotation(
        setup_identity=setup.setup_identity,
        session_date=setup.session_date,
        direction=setup.direction,
        triggering_level_type=setup.level_type,
        confirmation_bar_timestamp=setup.confirmation_bar_timestamp,
        signal_known_at=setup.signal_known_at,
        confirmation_close=confirmation_close,
        latest_confirmed_swing_high=latest_high,
        previous_confirmed_swing_high=previous_high,
        latest_confirmed_swing_low=latest_low,
        previous_confirmed_swing_low=previous_low,
        high_structure=high_state,
        low_structure=low_state,
        combined_structure=combined,
        direction_agreement=agreement,
        confirmation_close_to_latest_swing_high=high_distance,
        confirmation_close_to_latest_swing_low=low_distance,
        atr14=effective_atr,
        distance_to_swing_high_in_atr=high_normalized,
        distance_to_swing_low_in_atr=low_normalized,
        structural_room_state=structural_room,
    )


def build_market_structure_annotations(
    setup_result: BasePriceActionResult,
    bars: Sequence[FiveMinuteBar],
    atr_rows: Sequence[FiveMinuteAtrRow],
    swings: Sequence[ConfirmedSwing],
    room_result: RoomToLevelComparisonResult,
) -> tuple[MarketStructureAnnotation, ...]:
    bar_by_key = {(item.session_date, item.timestamp): item for item in bars}
    atr_by_key = {(item.session_date, item.timestamp): item for item in atr_rows}
    if len(bar_by_key) != len(bars) or len(atr_by_key) != len(atr_rows):
        raise MarketStructureInputError("Duplicate bar or ATR timestamp")
    if frozenset(bar_by_key) != frozenset(atr_by_key):
        raise MarketStructureInputError("Bar and ATR timestamp universes differ")
    room_by_id = {item.setup_identity: item for item in room_result.annotations}
    confirmed = tuple(
        item for item in setup_result.candidates if item.status is BaseSetupStatus.CONFIRMED
    )
    if {item.setup_identity for item in confirmed} != set(room_by_id):
        raise MarketStructureInputError("Setup and Stage 11.2 identities differ")
    annotations = []
    for setup in confirmed:
        key = (setup.session_date, setup.confirmation_bar_timestamp)
        if key not in bar_by_key:
            raise MarketStructureInputError("Confirmation candle is unavailable")
        annotations.append(
            annotate_market_structure(
                setup,
                confirmation_close=bar_by_key[key].close,
                atr14=atr_by_key[key].atr14,
                swings=swings,
                room=room_by_id[setup.setup_identity],
            )
        )
    return tuple(annotations)


def _session_summaries(
    bars: Sequence[FiveMinuteBar], swings: Sequence[ConfirmedSwing]
) -> tuple[SwingSessionSummary, ...]:
    sessions = tuple(sorted({item.session_date for item in bars}))
    return tuple(
        SwingSessionSummary(
            session_date=session,
            swing_high_count=sum(
                item.session_date == session and item.swing_type is SwingType.HIGH
                for item in swings
            ),
            swing_low_count=sum(
                item.session_date == session and item.swing_type is SwingType.LOW
                for item in swings
            ),
            earliest_pivot_known_at=min(
                (
                    item.pivot_known_at
                    for item in swings
                    if item.session_date == session
                ),
                default=None,
            ),
            latest_pivot_known_at=max(
                (
                    item.pivot_known_at
                    for item in swings
                    if item.session_date == session
                ),
                default=None,
            ),
        )
        for session in sessions
    )


def _structure_group(
    dimension: Literal["COMBINED_STRUCTURE", "DIRECTION_AGREEMENT"],
    state: StrEnum,
    annotations: Sequence[MarketStructureAnnotation],
    available_outcomes: Sequence[SetupOutcome],
) -> StructureGroupStatistics:
    field = (
        "combined_structure"
        if dimension == "COMBINED_STRUCTURE"
        else "direction_agreement"
    )
    selected = tuple(item for item in annotations if getattr(item, field) is state)
    identities = {item.setup_identity for item in selected}
    outcomes = tuple(
        item for item in available_outcomes if item.setup_identity in identities
    )
    sessions = Counter(item.session_date for item in selected)
    levels = Counter(item.triggering_level_type for item in selected)
    stats = summarize_base_outcome_group(
        BaseStrategyGroupDimension.OVERALL, f"{dimension}:{state.value}", outcomes
    )
    return StructureGroupStatistics(
        dimension=dimension,
        state=state.value,
        annotation_n=len(selected),
        executable_n=len(outcomes),
        long_annotation_n=sum(item.direction is SetupDirection.LONG for item in selected),
        short_annotation_n=sum(
            item.direction is SetupDirection.SHORT for item in selected
        ),
        session_count=len(sessions),
        session_composition=tuple(
            RegimeSessionCount(session_date=session, annotation_n=count)
            for session, count in sorted(sessions.items())
        ),
        level_composition=tuple(
            RegimeLevelCount(level_type=level, annotation_n=levels[level])
            for level in LevelType
            if levels[level]
        ),
        horizons=stats.horizons,
    )


def calculate_market_structure_comparison(
    setup_result: BasePriceActionResult,
    outcome_result: SetupOutcomeResult,
    base_statistics: BaseStrategyStatistics,
    context_result: CombinedContextMatrixResult,
    regime_result: RegimeHypothesisComparisonResult,
    room_result: RoomToLevelComparisonResult,
    bars: Sequence[FiveMinuteBar],
    swings: Sequence[ConfirmedSwing],
    annotations: Sequence[MarketStructureAnnotation],
) -> MarketStructureComparisonResult:
    """Join outcomes and accepted context only after structure assignment."""

    sources = (
        setup_result,
        outcome_result,
        base_statistics,
        context_result,
        regime_result,
        room_result,
    )
    if len({(item.start_date, item.end_date) for item in sources}) != 1:
        raise MarketStructureInputError("Frozen source ranges differ")
    annotation_by_id = {item.setup_identity: item for item in annotations}
    outcome_by_id = {item.setup_identity: item for item in outcome_result.outcomes}
    context_by_id = {item.setup_identity: item for item in context_result.annotations}
    regime_by_id = {item.setup_identity: item for item in regime_result.annotations}
    room_by_id = {item.setup_identity: item for item in room_result.annotations}
    ids = set(annotation_by_id)
    if (
        len(ids) != len(annotations)
        or ids != set(outcome_by_id)
        or ids != set(context_by_id)
        or ids != set(regime_by_id)
        or ids != set(room_by_id)
    ):
        raise MarketStructureInputError("Structure/source identities do not reconcile")
    available = tuple(
        item
        for item in outcome_result.outcomes
        if item.entry_reference.entry_status is EntryStatus.AVAILABLE
    )
    baseline = next(
        item
        for item in base_statistics.groups
        if item.dimension is BaseStrategyGroupDimension.OVERALL
    )
    if summarize_base_outcome_group(
        BaseStrategyGroupDimension.OVERALL, "OVERALL", available
    ) != baseline:
        raise MarketStructureInputError("BASE_ALL does not reproduce Stage 9.3")
    groups = tuple(
        _structure_group("COMBINED_STRUCTURE", state, annotations, available)
        for state in CombinedStructureState
    ) + tuple(
        _structure_group("DIRECTION_AGREEMENT", state, annotations, available)
        for state in StructureAgreementState
    )
    tabs = []
    for structure in CombinedStructureState:
        structure_ids = {
            item.setup_identity
            for item in annotations
            if item.combined_structure is structure
        }
        for dimension, field, states in CONTEXT_SPECS:
            if dimension == "REGIME_HYPOTHESIS":
                source = regime_by_id
            elif dimension == "ROOM_BUCKET":
                source = room_by_id
            else:
                source = context_by_id
            for state in states:
                selected_ids = {
                    identity
                    for identity in structure_ids
                    if getattr(source[identity], field) is state
                }
                selected_outcomes = tuple(
                    item for item in available if item.setup_identity in selected_ids
                )
                stats = summarize_base_outcome_group(
                    BaseStrategyGroupDimension.OVERALL,
                    f"{structure.value}:{dimension}:{state.value}",
                    selected_outcomes,
                )
                tabs.append(
                    StructureContextCrossTab(
                        structure_state=structure,
                        context_dimension=dimension,
                        context_state=state.value,
                        annotation_n=len(selected_ids),
                        executable_n=len(selected_outcomes),
                        eod=stats.horizons[-1],
                    )
                )
    audits = tuple(
        StructureAuditRow(
            annotation=annotation_by_id[identity],
            regime_hypothesis=regime_by_id[identity].combined_state,
            room_bucket=room_by_id[identity].room_bucket,
            eod_mfe=(
                outcome_by_id[identity].eod.mfe
                if outcome_by_id[identity].eod is not None
                else None
            ),
            eod_mae=(
                outcome_by_id[identity].eod.mae
                if outcome_by_id[identity].eod is not None
                else None
            ),
        )
        for identity in annotation_by_id
    )
    return MarketStructureComparisonResult(
        start_date=setup_result.start_date,
        end_date=setup_result.end_date,
        break_seed_count=setup_result.seed_count,
        confirmed_count=setup_result.confirmed_count,
        non_confirmed_count=setup_result.non_confirmed_count,
        executable_count=outcome_result.available_entry_count,
        session_end_unavailable_count=outcome_result.session_end_unavailable_count,
        missing_entry_count=outcome_result.missing_entry_count,
        development_session_count=base_statistics.development_session_count,
        total_confirmed_swing_highs=sum(
            item.swing_type is SwingType.HIGH for item in swings
        ),
        total_confirmed_swing_lows=sum(
            item.swing_type is SwingType.LOW for item in swings
        ),
        source_stage11_1_hash=sha256(regime_result.model_dump_json().encode()).hexdigest(),
        source_stage11_2_hash=sha256(room_result.model_dump_json().encode()).hexdigest(),
        swings=tuple(swings),
        swing_sessions=_session_summaries(bars, swings),
        annotations=tuple(annotations),
        groups=groups,
        cross_tabs=tuple(tabs),
        audit_rows=audits,
        base_all_horizons=baseline.horizons,
    )
