import logging

from spy_research.config import load_settings
from spy_research.logging_config import configure_logging


def test_logging_redacts_alpaca_credentials(monkeypatch, capsys) -> None:
    api_key = "api-credential-that-must-not-be-logged"
    secret_key = "secret-credential-that-must-not-be-logged"
    monkeypatch.setenv("ALPACA_API_KEY", api_key)
    monkeypatch.setenv("ALPACA_SECRET_KEY", secret_key)
    configure_logging()

    logging.getLogger("spy_research.test").info("credentials=%s/%s", api_key, secret_key)

    captured = capsys.readouterr()
    assert api_key not in captured.err
    assert secret_key not in captured.err
    assert "credentials=**********/**********" in captured.err
    assert "INFO" in captured.err
    assert "spy_research.test" in captured.err


def test_logging_redacts_both_credentials_loaded_from_dotenv(tmp_path, monkeypatch, capsys) -> None:
    api_key = "dotenv-api-credential-that-must-not-be-logged"
    secret_key = "dotenv-secret-credential-that-must-not-be-logged"
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text(
        f"ALPACA_API_KEY={api_key}\nALPACA_SECRET_KEY={secret_key}\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("ALPACA_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_SECRET_KEY", raising=False)

    settings = load_settings(env_path=dotenv_path)
    configure_logging()
    assert settings.alpaca.api_key is not None
    assert settings.alpaca.secret_key is not None
    assert api_key not in str(settings)
    assert api_key not in repr(settings)
    assert secret_key not in str(settings)
    assert secret_key not in repr(settings)
    logging.getLogger("spy_research.dotenv-test").info(
        "credentials=%s/%s",
        settings.alpaca.api_key.get_secret_value(),
        settings.alpaca.secret_key.get_secret_value(),
    )

    captured = capsys.readouterr()
    assert api_key not in captured.err
    assert secret_key not in captured.err
    assert "credentials=**********/**********" in captured.err
