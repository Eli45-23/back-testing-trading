"""Typed configuration loading for SPY research.

Non-secret research settings live in YAML. Alpaca credentials are read only
from environment variables or a local ``.env`` file and are represented with
``SecretStr`` so their values are redacted from string representations.
"""

from __future__ import annotations

from datetime import time
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import yaml
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from spy_research.logging_config import register_sensitive_values


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "research.yaml"
DEFAULT_ENV_PATH = PROJECT_ROOT / ".env"


class StrictModel(BaseModel):
    """Base model that rejects misspelled or unsupported configuration keys."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class ResearchMetadata(StrictModel):
    version: str = Field(min_length=1)


class DataConfig(StrictModel):
    source: Literal["alpaca"]
    feed: Literal["sip"]
    timeframe: Literal["1Min"]
    adjustment: Literal["raw"]

    @field_validator("feed", mode="before")
    @classmethod
    def enforce_phase_one_feed(cls, value: object) -> object:
        if value != "sip":
            raise ValueError("Phase 1 supports only the Alpaca 'sip' feed")
        return value


class SessionConfig(StrictModel):
    timezone: str
    indicator_mode: Literal["RTH_ONLY"]
    rth_start: time
    rth_end: time

    @field_validator("timezone")
    @classmethod
    def timezone_must_exist(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"unknown timezone: {value}") from exc
        return value

    @model_validator(mode="after")
    def session_must_have_positive_duration(self) -> "SessionConfig":
        if self.rth_start >= self.rth_end:
            raise ValueError("rth_start must be earlier than rth_end")
        return self


class BarsConfig(StrictModel):
    research_timeframe: Literal["5Min"]


class EmaConfig(StrictModel):
    fast: int = Field(gt=0)
    slow: int = Field(gt=0)

    @model_validator(mode="after")
    def fast_period_must_be_shorter(self) -> "EmaConfig":
        if self.fast >= self.slow:
            raise ValueError("ema.fast must be shorter than ema.slow")
        return self


class VwapConfig(StrictModel):
    reset: Literal["daily"]
    session: Literal["RTH"]
    price_source: Literal["hlc3"]


class AtrConfig(StrictModel):
    length: int = Field(gt=0)
    method: Literal["wilder"]


class OutcomesConfig(StrictModel):
    horizons_minutes: tuple[int, ...] = Field(min_length=1)
    include_eod: bool

    @field_validator("horizons_minutes")
    @classmethod
    def horizons_must_be_positive_and_unique(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        if any(horizon <= 0 for horizon in value):
            raise ValueError("outcome horizons must be positive")
        if len(value) != len(set(value)):
            raise ValueError("outcome horizons must be unique")
        return value


class DatabaseConfig(StrictModel):
    engine: Literal["sqlite"]


class ResearchConfig(StrictModel):
    research: ResearchMetadata
    symbol: Literal["SPY"]
    data: DataConfig
    session: SessionConfig
    bars: BarsConfig
    ema: EmaConfig
    vwap: VwapConfig
    atr: AtrConfig
    outcomes: OutcomesConfig
    database: DatabaseConfig

    @field_validator("symbol", mode="before")
    @classmethod
    def enforce_phase_one_symbol(cls, value: object) -> object:
        if value != "SPY":
            raise ValueError("Phase 1 supports only the 'SPY' symbol")
        return value


class AlpacaEnvironment(BaseSettings):
    """Optional Alpaca environment values for future data ingestion.

    Credentials are intentionally optional during the research foundation
    stage so configuration and tests never require a funded or live account.
    """

    model_config = SettingsConfigDict(extra="ignore", frozen=True)

    api_key: SecretStr | None = Field(default=None, validation_alias="ALPACA_API_KEY")
    secret_key: SecretStr | None = Field(default=None, validation_alias="ALPACA_SECRET_KEY")


class AppConfig(StrictModel):
    research: ResearchConfig
    alpaca: AlpacaEnvironment


def load_research_config(path: str | Path = DEFAULT_CONFIG_PATH) -> ResearchConfig:
    """Load and validate non-secret research configuration from YAML."""

    config_path = Path(path)
    with config_path.open(encoding="utf-8") as config_file:
        raw_config = yaml.safe_load(config_file)

    if not isinstance(raw_config, dict):
        raise ValueError(f"research configuration must be a mapping: {config_path}")

    return ResearchConfig.model_validate(raw_config)


def load_settings(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    env_path: str | Path | None = DEFAULT_ENV_PATH,
) -> AppConfig:
    """Load validated YAML settings plus optional Alpaca environment values."""

    alpaca = AlpacaEnvironment(_env_file=env_path, _env_file_encoding="utf-8")
    register_sensitive_values(
        secret.get_secret_value()
        for secret in (alpaca.api_key, alpaca.secret_key)
        if secret is not None
    )
    return AppConfig(research=load_research_config(config_path), alpaca=alpaca)
