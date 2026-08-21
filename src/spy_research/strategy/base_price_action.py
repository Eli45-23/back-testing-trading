"""Pure Stage 9.1 exact-price setup qualification and timing."""

from __future__ import annotations

from datetime import datetime, timedelta
from hashlib import sha256

from spy_research.interactions import (
    BreakFollowThrough,
    ImmediateState,
    InteractionType,
    LevelInteraction,
    PriceSide,
    RetestState,
)
from spy_research.strategy.models import (
    BasePriceActionCandidate,
    BaseSetupStatus,
    ConfirmationType,
    SetupDirection,
)


class BaseSetupInputError(ValueError):
    """Stage 8 inputs cannot safely form a Stage 9.1 candidate record."""


def interaction_identity(interaction: LevelInteraction) -> str:
    """Reproduce the immutable Stage 8.1 identity used by Stage 8.2."""

    return (
        f"{interaction.symbol}|{interaction.session_date.isoformat()}|"
        f"{interaction.candle_timestamp.isoformat()}|"
        f"{interaction.level_type.value}|{interaction.interaction_type.value}|"
        f"{interaction.interaction_version}"
    )


def _validate_inputs(
    interaction: LevelInteraction,
    follow_through: BreakFollowThrough,
    session_close: datetime,
) -> SetupDirection:
    if interaction.interaction_type is InteractionType.CLOSE_THROUGH_ABOVE:
        direction = SetupDirection.LONG
        expected_side = PriceSide.ABOVE
    elif interaction.interaction_type is InteractionType.CLOSE_THROUGH_BELOW:
        direction = SetupDirection.SHORT
        expected_side = PriceSide.BELOW
    else:
        raise BaseSetupInputError("Only Stage 8.1 close-throughs may seed Stage 9.1")
    if session_close.utcoffset() is None:
        raise BaseSetupInputError("Session close must be timezone-aware")
    if follow_through.break_interaction_identity != interaction_identity(interaction):
        raise BaseSetupInputError("Stage 8.2 seed identity does not match Stage 8.1")
    matching = (
        follow_through.symbol == interaction.symbol == "SPY"
        and follow_through.session_date == interaction.session_date
        and follow_through.level_type == interaction.level_type
        and follow_through.level_price == interaction.level_price
        and follow_through.break_timestamp == interaction.candle_timestamp
        and follow_through.break_completed_at == interaction.candle_completed_at
        and follow_through.break_interaction_type == interaction.interaction_type
        and follow_through.break_direction is expected_side
        and session_close.date() == interaction.candle_timestamp.date()
    )
    if not matching:
        raise BaseSetupInputError("Stage 8.1 and Stage 8.2 break facts must match")
    if session_close < interaction.candle_completed_at:
        raise BaseSetupInputError("Session close cannot precede the break completion")
    return direction


def _non_confirmation_status(follow_through: BreakFollowThrough) -> BaseSetupStatus:
    immediate = follow_through.immediate.state
    retest = follow_through.retest.state
    if immediate is ImmediateState.UNAVAILABLE or retest is RetestState.UNAVAILABLE:
        return BaseSetupStatus.INCOMPLETE
    if retest is RetestState.RETEST_FAILURE:
        return BaseSetupStatus.REJECTED_RETEST_FAILURE
    if immediate is ImmediateState.EQUAL or retest is RetestState.RETEST_EQUAL:
        return BaseSetupStatus.EQUAL_ONLY
    if retest is RetestState.NO_RETEST:
        return BaseSetupStatus.NO_RETEST
    if immediate is ImmediateState.FAILURE:
        return BaseSetupStatus.REJECTED_IMMEDIATE_FAILURE
    raise BaseSetupInputError("Unsupported Stage 8.2 non-confirmation state combination")


def qualify_base_price_action_candidate(
    interaction: LevelInteraction,
    follow_through: BreakFollowThrough,
    session_close: datetime,
) -> BasePriceActionCandidate:
    """Account for one break using earliest exact-price confirmation only."""

    direction = _validate_inputs(interaction, follow_through, session_close)
    confirmation_type = None
    confirmation_timestamp = None
    retest_offset = None
    if follow_through.immediate.state is ImmediateState.HOLD:
        confirmation_type = ConfirmationType.IMMEDIATE_HOLD
        confirmation_timestamp = follow_through.immediate.bar_timestamp
        expected_timestamp = interaction.candle_timestamp + timedelta(minutes=5)
        if confirmation_timestamp != expected_timestamp:
            raise BaseSetupInputError(
                "Immediate confirmation must be exactly the break bar +1"
            )
    elif follow_through.retest.state is RetestState.RETEST_HOLD:
        confirmation_type = ConfirmationType.RETEST_HOLD
        confirmation_timestamp = follow_through.retest.timestamp
        retest_offset = follow_through.retest.bar_offset
        if confirmation_timestamp is None or retest_offset is None:
            raise BaseSetupInputError("Retest confirmation requires timestamp and offset")
        expected_timestamp = interaction.candle_timestamp + timedelta(
            minutes=5 * retest_offset
        )
        if confirmation_timestamp != expected_timestamp:
            raise BaseSetupInputError(
                "Retest confirmation timestamp must match its frozen offset"
            )

    if confirmation_timestamp is not None:
        signal_known_at = confirmation_timestamp + timedelta(minutes=5)
        if signal_known_at > session_close:
            raise BaseSetupInputError("Confirmation cannot complete after session close")
        status = BaseSetupStatus.CONFIRMED
        same_session_executable = signal_known_at < session_close
        earliest_entry_timestamp = signal_known_at
    else:
        status = _non_confirmation_status(follow_through)
        signal_known_at = None
        earliest_entry_timestamp = None
        same_session_executable = False

    strategy_version = "base-exact-price-v1"
    identity_payload = "|".join(
        (
            interaction.symbol,
            interaction.session_date.isoformat(),
            interaction.level_type.value,
            str(interaction.level_price),
            interaction.candle_timestamp.isoformat(),
            direction.value,
            strategy_version,
        )
    )
    return BasePriceActionCandidate(
        setup_identity=sha256(identity_payload.encode()).hexdigest(),
        break_interaction_identity=follow_through.break_interaction_identity,
        follow_through_identity=(
            f"{follow_through.break_interaction_identity}|"
            f"{follow_through.follow_through_version}"
        ),
        session_date=interaction.session_date,
        level_type=interaction.level_type,
        level_price=interaction.level_price,
        direction=direction,
        break_interaction_type=interaction.interaction_type,
        break_timestamp=interaction.candle_timestamp,
        break_completed_at=interaction.candle_completed_at,
        exact_immediate_state=follow_through.immediate.state,
        exact_retest_state=follow_through.retest.state,
        status=status,
        confirmation_type=confirmation_type,
        confirmation_bar_timestamp=confirmation_timestamp,
        signal_known_at=signal_known_at,
        earliest_entry_timestamp=earliest_entry_timestamp,
        retest_bar_offset=retest_offset,
        same_session_executable=same_session_executable,
    )
