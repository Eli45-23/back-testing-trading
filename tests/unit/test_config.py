from datetime import time

import pytest
import yaml
from pydantic import ValidationError

from spy_research.config import AlpacaEnvironment, load_research_config, load_settings


def test_research_yaml_loads_expected_values() -> None:
    config = load_research_config()

    assert config.symbol == "SPY"
    assert config.ema.fast == 9
    assert config.ema.slow == 20
    assert config.atr.length == 14
    assert config.session.rth_start == time(9, 30)
    assert config.session.rth_end == time(16, 0)


def test_env_file_is_not_required_for_research_config(tmp_path) -> None:
    missing_env = tmp_path / ".env"

    settings = load_settings(env_path=missing_env)

    assert settings.research.symbol == "SPY"
    assert settings.alpaca.api_key is None
    assert settings.alpaca.secret_key is None


def test_environment_cannot_override_frozen_yaml_feed(monkeypatch) -> None:
    monkeypatch.setenv("ALPACA_DATA_FEED", "iex")

    settings = load_settings(env_path=None)

    assert settings.research.data.feed == "sip"
    assert not hasattr(settings.alpaca, "data_feed")


def test_credentials_are_redacted_from_string_representations(monkeypatch) -> None:
    api_key = "test-api-key-that-must-remain-private"
    secret_key = "test-secret-key-that-must-remain-private"
    monkeypatch.setenv("ALPACA_API_KEY", api_key)
    monkeypatch.setenv("ALPACA_SECRET_KEY", secret_key)

    credentials = AlpacaEnvironment()

    assert credentials.api_key is not None
    assert credentials.secret_key is not None
    assert api_key not in str(credentials)
    assert api_key not in repr(credentials)
    assert secret_key not in str(credentials)
    assert secret_key not in repr(credentials)
    assert "**********" in repr(credentials)


@pytest.mark.parametrize(
    ("field", "invalid_value", "expected_error"),
    [
        ("symbol", "QQQ", "Phase 1 supports only the 'SPY' symbol"),
        ("feed", "iex", "Phase 1 supports only the Alpaca 'sip' feed"),
    ],
)
def test_phase_one_rejects_invalid_symbol_and_feed(
    tmp_path, field: str, invalid_value: str, expected_error: str
) -> None:
    source = load_research_config().model_dump(mode="json")
    if field == "symbol":
        source["symbol"] = invalid_value
    else:
        source["data"]["feed"] = invalid_value
    config_path = tmp_path / "invalid-research.yaml"
    config_path.write_text(yaml.safe_dump(source), encoding="utf-8")

    with pytest.raises(ValidationError, match=expected_error):
        load_research_config(config_path)
