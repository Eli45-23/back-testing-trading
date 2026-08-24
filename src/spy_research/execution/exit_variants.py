"""Frozen Stage 13.2 exit-model universe and control mappings."""

from __future__ import annotations

from spy_research.execution.exit_models import (
    ExitFamily,
    ExitModelVariant,
    exit_variant_identity,
)
from spy_research.execution.models import AtrStopModel, RiskTargetModel


def _control_ids(stop: AtrStopModel) -> tuple[str, ...]:
    return tuple(
        exit_variant_identity(
            ExitFamily.FIXED_R_CONTROL,
            stop,
            fixed_target=target,
        )
        for target in RiskTargetModel
    )


def exit_model_variants() -> tuple[ExitModelVariant, ...]:
    """Return the exact 15 controls followed by the 21 predeclared exits."""

    controls = tuple(
        ExitModelVariant(
            variant_id=exit_variant_identity(
                ExitFamily.FIXED_R_CONTROL,
                stop,
                fixed_target=target,
            ),
            family=ExitFamily.FIXED_R_CONTROL,
            stop_model=stop,
            stop_multiplier=stop.multiplier,
            fixed_target_model=target,
            fixed_target_r=target.multiple,
            corresponding_control_variant_ids=(
                exit_variant_identity(
                    ExitFamily.FIXED_R_CONTROL,
                    stop,
                    fixed_target=target,
                ),
            ),
        )
        for stop in AtrStopModel
        for target in RiskTargetModel
    )
    cross_families = (
        ExitFamily.OPPOSITE_EMA9_20_CROSS,
        ExitFamily.OPPOSITE_EMA9_VWAP_CROSS,
        ExitFamily.OPPOSITE_EMA20_VWAP_CROSS,
    )
    crosses = tuple(
        ExitModelVariant(
            variant_id=exit_variant_identity(family, stop),
            family=family,
            stop_model=stop,
            stop_multiplier=stop.multiplier,
            corresponding_control_variant_ids=_control_ids(stop),
        )
        for family in cross_families
        for stop in AtrStopModel
    )
    time_exits = tuple(
        ExitModelVariant(
            variant_id=exit_variant_identity(
                ExitFamily.TIME_EXIT,
                stop,
                time_minutes=minutes,
            ),
            family=ExitFamily.TIME_EXIT,
            stop_model=stop,
            stop_multiplier=stop.multiplier,
            time_minutes=minutes,
            corresponding_control_variant_ids=_control_ids(stop),
        )
        for stop in AtrStopModel
        for minutes in (15, 30, 60)
    )
    objectives = tuple(
        ExitModelVariant(
            variant_id=exit_variant_identity(
                ExitFamily.NEXT_OBJECTIVE_LEVEL,
                stop,
            ),
            family=ExitFamily.NEXT_OBJECTIVE_LEVEL,
            stop_model=stop,
            stop_multiplier=stop.multiplier,
            corresponding_control_variant_ids=_control_ids(stop),
        )
        for stop in AtrStopModel
    )
    return controls + crosses + time_exits + objectives
