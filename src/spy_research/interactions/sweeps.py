"""Pure deterministic labels for Stage 8.1 wick-through interactions."""

from __future__ import annotations

from spy_research.interactions.classifier import InteractionInputError
from spy_research.interactions.models import (
    InteractionType,
    LevelInteraction,
    LiquiditySweepPattern,
    PriceSide,
    SweepType,
)


class SweepInputError(InteractionInputError):
    """A source record violates the frozen Stage 8.3 wick-seed contract."""


def _source_identity(interaction: LevelInteraction) -> str:
    return (
        f"{interaction.symbol}|{interaction.session_date.isoformat()}|"
        f"{interaction.candle_timestamp.isoformat()}|"
        f"{interaction.level_type.value}|{interaction.interaction_type.value}|"
        f"{interaction.interaction_version}"
    )


def classify_sweep_pattern(
    interaction: LevelInteraction,
) -> LiquiditySweepPattern:
    """Classify one immutable wick event using only its extreme and close."""

    source_type = interaction.interaction_type
    level = interaction.level_price
    if source_type is InteractionType.WICK_THROUGH_ABOVE:
        if interaction.high <= level or not interaction.traded_above:
            raise SweepInputError(
                "WICK_THROUGH_ABOVE requires a strict traded-above excursion"
            )
        if interaction.close > level:
            raise SweepInputError(
                "WICK_THROUGH_ABOVE cannot close strictly above the level"
            )
        excursion = interaction.high - level
        if interaction.close < level:
            sweep_type = SweepType.SWEEP_ABOVE
            reclaim = level - interaction.close
        else:
            sweep_type = SweepType.WICK_EQUAL_ABOVE
            reclaim = level - interaction.close
        excursion_side = PriceSide.ABOVE
    elif source_type is InteractionType.WICK_THROUGH_BELOW:
        if interaction.low >= level or not interaction.traded_below:
            raise SweepInputError(
                "WICK_THROUGH_BELOW requires a strict traded-below excursion"
            )
        if interaction.close < level:
            raise SweepInputError(
                "WICK_THROUGH_BELOW cannot close strictly below the level"
            )
        excursion = level - interaction.low
        if interaction.close > level:
            sweep_type = SweepType.SWEEP_BELOW
            reclaim = interaction.close - level
        else:
            sweep_type = SweepType.WICK_EQUAL_BELOW
            reclaim = interaction.close - level
        excursion_side = PriceSide.BELOW
    else:
        raise SweepInputError(
            "Only WICK_THROUGH_ABOVE or WICK_THROUGH_BELOW may seed sweep patterns"
        )

    return LiquiditySweepPattern(
        source_interaction_identity=_source_identity(interaction),
        session_date=interaction.session_date,
        candle_timestamp=interaction.candle_timestamp,
        candle_completed_at=interaction.candle_completed_at,
        level_type=interaction.level_type,
        level_price=level,
        source_interaction_type=source_type,
        sweep_type=sweep_type,
        open=interaction.open,
        high=interaction.high,
        low=interaction.low,
        close=interaction.close,
        open_side=interaction.open_side,
        close_side=interaction.close_side,
        traded_above=interaction.traded_above,
        traded_below=interaction.traded_below,
        excursion_amount=excursion,
        excursion_side=excursion_side,
        reclaim_distance=reclaim,
    )
