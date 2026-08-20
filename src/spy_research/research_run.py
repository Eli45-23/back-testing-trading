"""Reproducible research-run metadata and lifecycle primitives."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import UTC, date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.config import PROJECT_ROOT, ResearchConfig
from spy_research.logging_config import redact_sensitive_text
from spy_research.version import get_version


class RunStatus(str, Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RunLifecycleError(ValueError):
    """Raised when a research run receives an invalid state transition."""


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(UTC)


def build_config_snapshot(config: ResearchConfig) -> dict[str, Any]:
    """Create a detached, JSON-compatible snapshot of non-secret settings."""

    snapshot = config.model_dump(mode="json")
    return json.loads(json.dumps(snapshot, sort_keys=True))


def normalized_config_json(config_snapshot: dict[str, Any]) -> str:
    """Serialize a configuration snapshot deterministically."""

    return json.dumps(
        config_snapshot,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def calculate_config_hash(config_snapshot: dict[str, Any]) -> str:
    """Return the SHA-256 digest for a normalized configuration snapshot."""

    normalized = normalized_config_json(config_snapshot).encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def get_git_commit(repository: str | Path = PROJECT_ROOT) -> str | None:
    """Return the current Git commit without failing outside a committed repo."""

    try:
        result = subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "--verify", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    commit = result.stdout.strip()
    if result.returncode != 0 or re.fullmatch(r"[0-9a-fA-F]{7,64}", commit) is None:
        return None
    return commit.lower()


class ResearchRun(BaseModel):
    """Immutable research manifest with explicit, validated lifecycle methods."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=utc_now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: RunStatus = RunStatus.CREATED

    research_version: str
    symbol: str
    start_date: date
    end_date: date
    data_source: str
    data_feed: str
    timeframe: str
    indicator_session_mode: str

    config_snapshot: dict[str, Any]
    config_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    app_version: str
    git_commit: str | None = None

    error_type: str | None = None
    error_message: str | None = None

    @model_validator(mode="after")
    def dates_are_valid(self) -> Self:
        if self.start_date > self.end_date:
            raise ValueError("start_date must be on or before end_date")
        if self.created_at.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")
        return self

    @classmethod
    def create(
        cls,
        config: ResearchConfig,
        *,
        start_date: date,
        end_date: date,
        repository: str | Path = PROJECT_ROOT,
    ) -> Self:
        snapshot = build_config_snapshot(config)
        return cls(
            research_version=config.research.version,
            symbol=config.symbol,
            start_date=start_date,
            end_date=end_date,
            data_source=config.data.source,
            data_feed=config.data.feed,
            timeframe=config.data.timeframe,
            indicator_session_mode=config.session.indicator_mode,
            config_snapshot=snapshot,
            config_hash=calculate_config_hash(snapshot),
            app_version=get_version(),
            git_commit=get_git_commit(repository),
        )

    def start(self) -> None:
        if self.status is not RunStatus.CREATED:
            raise RunLifecycleError(f"cannot start a run with status {self.status.value}")
        object.__setattr__(self, "started_at", utc_now())
        object.__setattr__(self, "status", RunStatus.RUNNING)

    def complete(self) -> None:
        if self.status is not RunStatus.RUNNING:
            raise RunLifecycleError(f"cannot complete a run with status {self.status.value}")
        object.__setattr__(self, "completed_at", utc_now())
        object.__setattr__(self, "status", RunStatus.COMPLETED)

    def fail(self, exception: Exception) -> None:
        if self.status not in {RunStatus.CREATED, RunStatus.RUNNING}:
            raise RunLifecycleError(f"cannot fail a run with status {self.status.value}")
        if self.started_at is None:
            object.__setattr__(self, "started_at", utc_now())
        safe_message = redact_sensitive_text(str(exception))[:1000]
        object.__setattr__(self, "error_type", type(exception).__name__)
        object.__setattr__(self, "error_message", safe_message)
        object.__setattr__(self, "completed_at", utc_now())
        object.__setattr__(self, "status", RunStatus.FAILED)

    def to_manifest(self) -> dict[str, Any]:
        """Return a JSON-compatible manifest without secret configuration."""

        return self.model_dump(mode="json")
