"""Denominator and bootstrap identities frozen before outcome inspection."""

from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Iterable

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models import EntrySignal, LevelInteraction
from .protocol import BOOTSTRAP_DRAWS, BOOTSTRAP_SEED, EntryFamily


class PopulationSummary(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    interactions: int = Field(ge=0)
    sessions: int = Field(ge=0)
    signals_by_family: tuple[tuple[str, int], ...]
    statuses_by_family: tuple[tuple[str, str, int], ...]
    bootstrap_seed: int = BOOTSTRAP_SEED
    bootstrap_draws: int = BOOTSTRAP_DRAWS


def summarize_population(
    interactions: Iterable[LevelInteraction], signals: Iterable[EntrySignal]
) -> PopulationSummary:
    interaction_values = tuple(interactions)
    if len({item.interaction_id for item in interaction_values}) != len(interaction_values):
        raise ValueError("interaction IDs must be unique in the denominator")
    signal_values = tuple(signals)
    families = Counter(item.entry_family.value for item in signal_values)
    statuses = Counter((item.entry_family.value, item.status.value) for item in signal_values)
    return PopulationSummary(
        interactions=len(interaction_values),
        sessions=len({item.session_date for item in interaction_values}),
        signals_by_family=tuple(sorted(families.items())),
        statuses_by_family=tuple(
            (family, status, count)
            for (family, status), count in sorted(statuses.items())
        ),
    )
