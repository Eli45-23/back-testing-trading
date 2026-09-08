"""Causal confirmation state machines and executable-reference measurements."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Iterable, Sequence

from .models import (
    ConfirmationBar,
    EntrySignal,
    LevelInteraction,
    MinuteBar,
    PairedComparison,
    PathMeasurement,
)
from .protocol import (
    DISTANCES,
    EntryFamily,
    SignalStatus,
    OUTCOME_END,
    completion_at,
    decimal,
)


def validate_bars(bars: Iterable[MinuteBar | ConfirmationBar]) -> tuple:
    """Validate ordering and exact values before any confirmation is evaluated."""
    values = tuple(bars)
    previous: datetime | None = None
    for bar in values:
        if previous is not None and bar.timestamp <= previous:
            raise ValueError("bars must be strictly chronological")
        previous = bar.timestamp
        if bar.session_date > OUTCOME_END:
            raise ValueError("future outcome bars are prohibited")
    return values


def _bar_contains_touch(bar: ConfirmationBar, interaction: LevelInteraction) -> bool:
    return (
        bar.timestamp <= interaction.first_touch_at < bar.completes_at
        and bar.low <= interaction.level_price <= bar.high
    )


def _bars_for_interaction(
    bars: Sequence[ConfirmationBar], interaction: LevelInteraction
) -> tuple[ConfirmationBar, ...]:
    """Keep only bars that could be known after the interaction, never future bars."""
    validate_bars(bars)
    candidates = tuple(
        bar
        for bar in bars
        if bar.session_date == interaction.session_date
        and bar.timestamp < interaction.episode_end_at
        and (
            bar.timestamp >= interaction.first_touch_at
            or _bar_contains_touch(bar, interaction)
        )
    )
    return candidates


def _closes_on_approach_side(close: Decimal, interaction: LevelInteraction) -> bool:
    if interaction.approach_side == "ABOVE":
        return close >= interaction.level_price
    if interaction.approach_side == "BELOW":
        return close <= interaction.level_price
    return False


def _away_distance(bar: ConfirmationBar, interaction: LevelInteraction) -> Decimal:
    if interaction.approach_side == "ABOVE":
        return bar.high - interaction.level_price
    if interaction.approach_side == "BELOW":
        return interaction.level_price - bar.low
    return Decimal("-1")


def _signal(
    interaction: LevelInteraction,
    family: EntryFamily,
    status: SignalStatus,
    *,
    bar: ConfirmationBar | None = None,
    displacement: Decimal | None = None,
) -> EntrySignal:
    if bar is None:
        return EntrySignal(
            interaction_id=interaction.interaction_id,
                session_date=interaction.session_date,
                level_id=interaction.level_id,
                level_family=interaction.level_family,
                level_price=interaction.level_price,
                approach_side=interaction.approach_side,
            entry_family=family,
            status=status,
            first_touch_at=interaction.first_touch_at,
        )
    known_at = bar.completes_at
    return EntrySignal(
        interaction_id=interaction.interaction_id,
        session_date=interaction.session_date,
        level_id=interaction.level_id,
        level_family=interaction.level_family,
        level_price=interaction.level_price,
        approach_side=interaction.approach_side,
        entry_family=family,
        status=status,
        first_touch_at=interaction.first_touch_at,
        confirmation_start_at=bar.timestamp,
        signal_known_at=known_at,
        confirmation_timeframe_minutes=bar.timeframe_minutes,
        delay_minutes=int((known_at - interaction.first_touch_at).total_seconds() // 60),
        displacement_from_level=displacement if displacement is not None else abs(bar.close - interaction.level_price),
        confirmation_bar_id=f"{interaction.interaction_id}@{bar.timestamp.isoformat()}",
    )


def immediate_close_back(
    interaction: LevelInteraction,
    bars: Sequence[ConfirmationBar],
    timeframe_minutes: int,
    *,
    session_close: datetime,
) -> EntrySignal:
    """Evaluate exactly one predeclared 1m or 5m close-back confirmation.

    The first completed bar containing the interaction must close on the
    approach side.  A later close-back cannot rescue a failed immediate signal.
    """
    if timeframe_minutes not in (1, 5):
        raise ValueError("immediate close-back is frozen to 1m or 5m")
    family = EntryFamily.IMMEDIATE_CLOSE_BACK
    candidates = tuple(
        bar for bar in _bars_for_interaction(bars, interaction)
        if bar.timeframe_minutes == timeframe_minutes
    )
    first = next(
        (bar for bar in candidates if _bar_contains_touch(bar, interaction)), None
    )
    if first is None:
        return _signal(
            interaction,
            family,
            SignalStatus.CENSORED_SESSION_CLOSE
            if interaction.episode_end_at >= session_close
            else SignalStatus.NO_CONFIRMATION,
        )
    if first.completes_at > session_close:
        return _signal(interaction, family, SignalStatus.CENSORED_SESSION_CLOSE)
    if not _closes_on_approach_side(first.close, interaction):
        return _signal(interaction, family, SignalStatus.NO_CONFIRMATION)
    return _signal(interaction, family, SignalStatus.CONFIRMED, bar=first)


def momentum_away(
    interaction: LevelInteraction,
    bars: Sequence[ConfirmationBar],
    *,
    session_close: datetime,
    distance: Decimal,
) -> EntrySignal:
    """Confirm the first completed bar whose completed-data range is away."""
    distance = decimal(distance)
    if distance <= 0:
        raise ValueError("momentum distance must be positive")
    candidates = _bars_for_interaction(bars, interaction)
    first_touch_bar = next(
        (bar for bar in candidates if _bar_contains_touch(bar, interaction)), None
    )
    if first_touch_bar is None:
        return _signal(interaction, EntryFamily.MOMENTUM_AWAY, SignalStatus.CENSORED_SESSION_CLOSE)
    for bar in candidates:
        if bar.completes_at > session_close:
            break
        if _away_distance(bar, interaction) >= distance:
            return _signal(
                interaction,
                EntryFamily.MOMENTUM_AWAY,
                SignalStatus.CONFIRMED,
                bar=bar,
                displacement=distance,
            )
    return _signal(
        interaction,
        EntryFamily.MOMENTUM_AWAY,
        SignalStatus.CENSORED_SESSION_CLOSE
        if interaction.episode_end_at >= session_close
        else SignalStatus.NO_CONFIRMATION,
    )


def one_retest_hold(
    interaction: LevelInteraction,
    bars: Sequence[ConfirmationBar],
    *,
    session_close: datetime,
) -> EntrySignal:
    """Use the frozen KLR retest starts and require a completed hold afterward."""
    family = EntryFamily.ONE_RETEST_HOLD
    initial = immediate_close_back(
        interaction, bars, 1, session_close=session_close
    )
    if initial.status is not SignalStatus.CONFIRMED:
        return _signal(interaction, family, initial.status)
    retest = next(
        (x for x in interaction.retest_starts if x > initial.signal_known_at), None
    )
    if retest is None:
        return _signal(
            interaction,
            family,
            SignalStatus.CENSORED_SESSION_CLOSE
            if interaction.episode_end_at >= session_close
            else SignalStatus.NO_CONFIRMATION,
        )
    candidates = _bars_for_interaction(bars, interaction)
    retest_bar = next(
        (bar for bar in candidates if bar.timestamp == retest), None
    )
    if retest_bar is None or retest_bar.completes_at > session_close:
        return _signal(interaction, family, SignalStatus.CENSORED_SESSION_CLOSE)
    # The retest itself must touch, and the first completed bar at/after it must
    # close back on the original side.  No later successful retest is substituted.
    if (
        retest_bar.low > interaction.level_price
        or retest_bar.high < interaction.level_price
        or not _closes_on_approach_side(retest_bar.close, interaction)
    ):
        return _signal(interaction, family, SignalStatus.NO_CONFIRMATION)
    return _signal(interaction, family, SignalStatus.CONFIRMED, bar=retest_bar)


def evaluate_interaction(
    interaction: LevelInteraction,
    confirmation_bars: Sequence[ConfirmationBar],
    *,
    session_close: datetime,
) -> tuple[EntrySignal, ...]:
    """Return one record per frozen family for every eligible interaction."""
    return (
        immediate_close_back(interaction, confirmation_bars, 1, session_close=session_close),
        immediate_close_back(interaction, confirmation_bars, 5, session_close=session_close),
        momentum_away(
            interaction,
            confirmation_bars,
            session_close=session_close,
            distance=Decimal("0.25"),
        ),
        one_retest_hold(interaction, confirmation_bars, session_close=session_close),
    )


def first_executable_minute(
    signal: EntrySignal,
    raw_rth_minutes: Sequence[MinuteBar],
    *,
    session_close: datetime,
) -> tuple[datetime | None, Decimal | None, str]:
    """Select first same-session minute start at/after completed signal."""
    if signal.status is not SignalStatus.CONFIRMED or signal.signal_known_at is None:
        return None, None, "MISSING"
    bars = validate_bars(raw_rth_minutes)
    selected = next(
        (
            bar for bar in bars
            if bar.session_date == signal.session_date
            and signal.signal_known_at <= bar.timestamp < session_close
        ),
        None,
    )
    if selected is None:
        return None, None, "SESSION_CLOSE"
    return selected.timestamp, selected.open, "AVAILABLE"


def measure_path(
    signal: EntrySignal,
    raw_rth_minutes: Sequence[MinuteBar],
    *,
    session_close: datetime,
    horizon_minutes: int = 30,
) -> PathMeasurement:
    """Measure descriptive excursions after the executable minute only."""
    if signal.signal_known_at is None:
        raise ValueError("path measurement requires a confirmed signal")
    if horizon_minutes <= 0:
        raise ValueError("path horizon must be positive")
    entry_at, entry_price, status = first_executable_minute(
        signal, raw_rth_minutes, session_close=session_close
    )
    if entry_at is None or entry_price is None:
        return PathMeasurement(
            interaction_id=signal.interaction_id,
            entry_family=signal.entry_family,
            confirmation_timeframe_minutes=signal.confirmation_timeframe_minutes,
            signal_known_at=signal.signal_known_at,
            entry_status=status,
            entry_timestamp=None,
            entry_price=None,
            observed_minutes=0,
            censored_at_session_close=status == "SESSION_CLOSE",
            same_minute_ambiguity=False,
            mfe_from_level=None,
            mae_through_level=None,
            directional_close_excursion=None,
            fixed_distance_first_hits=tuple((str(x), None) for x in DISTANCES),
        )
    end = min(entry_at + timedelta(minutes=horizon_minutes), session_close)
    bars = tuple(
        bar for bar in validate_bars(raw_rth_minutes)
        if bar.session_date == signal.session_date
        and entry_at <= bar.timestamp < end
    )
    expected = int((end - entry_at).total_seconds() // 60)
    if len(bars) != expected or any(
        bar.timestamp != entry_at + timedelta(minutes=i)
        for i, bar in enumerate(bars)
    ):
        raise ValueError("missing post-entry RTH minutes; do not fill gaps")
    if signal.approach_side == "UNKNOWN":
        return PathMeasurement(
            interaction_id=signal.interaction_id,
            entry_family=signal.entry_family,
            confirmation_timeframe_minutes=signal.confirmation_timeframe_minutes,
            signal_known_at=signal.signal_known_at,
            entry_status=status,
            entry_timestamp=entry_at,
            entry_price=entry_price,
            observed_minutes=len(bars),
            censored_at_session_close=end >= session_close,
            same_minute_ambiguity=False,
            mfe_from_level=None,
            mae_through_level=None,
            directional_close_excursion=None,
            fixed_distance_first_hits=tuple((f"{x}:UNKNOWN", None) for x in DISTANCES),
        )
    above = signal.approach_side == "ABOVE"
    mfe = max(
        (max(Decimal("0"), bar.high - signal.level_price) if above else max(Decimal("0"), signal.level_price - bar.low))
        for bar in bars
    )
    mae = max(
        (max(Decimal("0"), signal.level_price - bar.low) if above else max(Decimal("0"), bar.high - signal.level_price))
        for bar in bars
    )
    hits = []
    ambiguous = False
    for distance in DISTANCES:
        favorable = next(
            (bar.timestamp for bar in bars if (bar.high >= signal.level_price + distance if above else bar.low <= signal.level_price - distance)),
            None,
        )
        adverse = next(
            (bar.timestamp for bar in bars if (bar.low <= signal.level_price - distance if above else bar.high >= signal.level_price + distance)),
            None,
        )
        if favorable is not None and adverse is not None and favorable == adverse:
            ambiguous = True
            hits.append((f"{distance}:AMBIGUOUS_SAME_MINUTE", favorable))
        elif favorable is not None and (adverse is None or favorable < adverse):
            hits.append((f"{distance}:FAVORABLE", favorable))
        elif adverse is not None:
            hits.append((f"{distance}:ADVERSE", adverse))
        else:
            hits.append((f"{distance}:NONE", None))
    close_move = bars[-1].close - signal.level_price
    if not above:
        close_move = -close_move
    return PathMeasurement(
        interaction_id=signal.interaction_id,
        entry_family=signal.entry_family,
        confirmation_timeframe_minutes=signal.confirmation_timeframe_minutes,
        signal_known_at=signal.signal_known_at,
        entry_status=status,
        entry_timestamp=entry_at,
        entry_price=entry_price,
        observed_minutes=len(bars),
        censored_at_session_close=end >= session_close,
        same_minute_ambiguity=ambiguous,
        mfe_from_level=mfe,
        mae_through_level=mae,
        directional_close_excursion=close_move,
        fixed_distance_first_hits=tuple(hits),
    )


def pair_signals(
    signals: Sequence[EntrySignal],
    left: EntryFamily,
    right: EntryFamily,
    *,
    left_timeframe_minutes: int | None = None,
    right_timeframe_minutes: int | None = None,
) -> tuple[PairedComparison, ...]:
    """Pair exact interaction identities, retaining unavailable statuses."""
    ids = sorted(
        {
            signal.interaction_id
            for signal in signals
            if signal.entry_family in (left, right)
            and (
                signal.entry_family != left
                or left_timeframe_minutes is None
                or signal.confirmation_timeframe_minutes == left_timeframe_minutes
            )
            and (
                signal.entry_family != right
                or right_timeframe_minutes is None
                or signal.confirmation_timeframe_minutes == right_timeframe_minutes
            )
        }
    )
    rows = []
    for interaction_id in ids:
        left_signal = next(
            (
                s for s in signals
                if s.interaction_id == interaction_id
                and s.entry_family == left
                and (left_timeframe_minutes is None or s.confirmation_timeframe_minutes == left_timeframe_minutes)
            ), None
        )
        right_signal = next(
            (
                s for s in signals
                if s.interaction_id == interaction_id
                and s.entry_family == right
                and (right_timeframe_minutes is None or s.confirmation_timeframe_minutes == right_timeframe_minutes)
            ), None
        )
        if left_signal is None or right_signal is None:
            continue
        delay = None
        disadvantage = None
        if left_signal.signal_known_at and right_signal.signal_known_at:
            delay = int((right_signal.signal_known_at - left_signal.signal_known_at).total_seconds() // 60)
        if left_signal.executable_entry_price is not None and right_signal.executable_entry_price is not None:
            disadvantage = right_signal.executable_entry_price - left_signal.executable_entry_price
        rows.append(
            PairedComparison(
                interaction_id=interaction_id,
                left_family=left,
                right_family=right,
                left_timeframe_minutes=left_signal.confirmation_timeframe_minutes,
                right_timeframe_minutes=right_signal.confirmation_timeframe_minutes,
                left_status=left_signal.status,
                right_status=right_signal.status,
                delay_minutes=delay,
                entry_price_disadvantage=disadvantage,
                remaining_mfe_delta=None,
                mae_delta=None,
                paired=left_signal.status is SignalStatus.CONFIRMED and right_signal.status is SignalStatus.CONFIRMED,
            )
        )
    return tuple(rows)


def pair_measurements(
    left_signals: Sequence[EntrySignal],
    right_signals: Sequence[EntrySignal],
    left_paths: Sequence[PathMeasurement],
    right_paths: Sequence[PathMeasurement],
) -> tuple[PairedComparison, ...]:
    """Join executable wait-cost fields without survivor filtering."""
    left_by_id = {row.interaction_id: row for row in left_signals}
    right_by_id = {row.interaction_id: row for row in right_signals}
    lp = {row.interaction_id: row for row in left_paths}
    rp = {row.interaction_id: row for row in right_paths}
    rows = []
    for interaction_id in sorted(set(left_by_id) | set(right_by_id)):
        left = left_by_id.get(interaction_id)
        right = right_by_id.get(interaction_id)
        if left is None or right is None:
            continue
        left_path = lp.get(interaction_id)
        right_path = rp.get(interaction_id)
        delay = None
        disadvantage = None
        mfe_delta = None
        mae_delta = None
        if left.signal_known_at and right.signal_known_at:
            delay = int((right.signal_known_at - left.signal_known_at).total_seconds() // 60)
        if left_path and right_path:
            if left_path.entry_price is not None and right_path.entry_price is not None:
                disadvantage = right_path.entry_price - left_path.entry_price
            if left_path.mfe_from_level is not None and right_path.mfe_from_level is not None:
                mfe_delta = right_path.mfe_from_level - left_path.mfe_from_level
            if left_path.mae_through_level is not None and right_path.mae_through_level is not None:
                mae_delta = right_path.mae_through_level - left_path.mae_through_level
        rows.append(
            PairedComparison(
                interaction_id=interaction_id,
                left_family=left.entry_family,
                right_family=right.entry_family,
                left_timeframe_minutes=left.confirmation_timeframe_minutes,
                right_timeframe_minutes=right.confirmation_timeframe_minutes,
                left_status=left.status,
                right_status=right.status,
                delay_minutes=delay,
                entry_price_disadvantage=disadvantage,
                remaining_mfe_delta=mfe_delta,
                mae_delta=mae_delta,
                paired=left_path is not None and right_path is not None,
            )
        )
    return tuple(rows)
