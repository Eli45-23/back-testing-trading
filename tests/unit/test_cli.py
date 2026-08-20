import json
import re
import socket

import pytest

from spy_research.cli import main


def test_help_reports_foundation_commands(capsys) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--help"])

    captured = capsys.readouterr()
    assert exit_info.value.code == 0
    assert "config-check" in captured.out
    assert "run-manifest" in captured.out


def test_config_check_reports_success_without_credentials(monkeypatch, capsys) -> None:
    api_key = "cli-api-credential-that-must-not-be-shown"
    secret_key = "cli-secret-credential-that-must-not-be-shown"
    monkeypatch.setenv("ALPACA_API_KEY", api_key)
    monkeypatch.setenv("ALPACA_SECRET_KEY", secret_key)

    exit_code = main(["config-check"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Configuration valid" in captured.out
    assert api_key not in captured.out
    assert secret_key not in captured.out
    assert captured.err == ""


def test_run_manifest_is_valid_secret_free_json_without_network(monkeypatch, capsys) -> None:
    api_key = "manifest-api-credential-that-must-not-be-shown"
    secret_key = "manifest-secret-credential-that-must-not-be-shown"
    monkeypatch.setenv("ALPACA_API_KEY", api_key)
    monkeypatch.setenv("ALPACA_SECRET_KEY", secret_key)

    def reject_network(*args, **kwargs):
        raise AssertionError("run-manifest must not open a network connection")

    monkeypatch.setattr(socket, "create_connection", reject_network)

    exit_code = main(
        ["run-manifest", "--start", "2026-08-03", "--end", "2026-08-19"]
    )

    captured = capsys.readouterr()
    manifest = json.loads(captured.out)
    assert exit_code == 0
    assert captured.err == ""
    assert manifest["symbol"] == "SPY"
    assert manifest["start_date"] == "2026-08-03"
    assert manifest["end_date"] == "2026-08-19"
    assert manifest["status"] == "CREATED"
    assert re.fullmatch(r"[0-9a-f]{64}", manifest["config_hash"])
    assert api_key not in captured.out
    assert secret_key not in captured.out
    assert "api_key" not in captured.out
    assert "secret_key" not in captured.out
