import json
import re
from copy import deepcopy
from datetime import date
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from spy_research.config import ResearchConfig, load_research_config, load_settings
from spy_research.research_run import (
    ResearchRun,
    RunLifecycleError,
    RunStatus,
    build_config_snapshot,
    calculate_config_hash,
    get_git_commit,
)


START_DATE = date(2026, 8, 3)
END_DATE = date(2026, 8, 19)


def create_run(config: ResearchConfig | None = None) -> ResearchRun:
    return ResearchRun.create(
        config or load_research_config(),
        start_date=START_DATE,
        end_date=END_DATE,
    )


def changed_config(*path_and_value: object) -> ResearchConfig:
    *path, value = path_and_value
    raw = deepcopy(load_research_config().model_dump(mode="json"))
    target = raw
    for key in path[:-1]:
        target = target[str(key)]
    target[str(path[-1])] = value
    return ResearchConfig.model_validate(raw)


def test_run_ids_are_unique_valid_uuids_and_immutable() -> None:
    first = create_run()
    second = create_run()

    assert UUID(str(first.run_id)) == first.run_id
    assert first.run_id != second.run_id
    with pytest.raises(ValidationError, match="frozen"):
        first.run_id = uuid4()  # type: ignore[misc]


def test_run_timestamps_are_timezone_aware() -> None:
    run = create_run()
    assert run.created_at.utcoffset() is not None

    run.start()
    run.complete()

    assert run.started_at is not None and run.started_at.utcoffset() is not None
    assert run.completed_at is not None and run.completed_at.utcoffset() is not None


def test_identical_configuration_produces_same_sha256_hash() -> None:
    first = create_run()
    second = create_run()

    assert first.config_hash == second.config_hash
    assert re.fullmatch(r"[0-9a-f]{64}", first.config_hash)


def test_changing_ema_fast_changes_hash() -> None:
    original = create_run()
    changed = create_run(changed_config("ema", "fast", 10))

    assert original.config_hash != changed.config_hash


def test_changing_another_meaningful_setting_changes_hash() -> None:
    original = create_run()
    changed = create_run(changed_config("atr", "length", 20))

    assert original.config_hash != changed.config_hash


def test_dictionary_order_does_not_affect_hash() -> None:
    first = {"symbol": "SPY", "ema": {"fast": 9, "slow": 20}}
    reordered = {"ema": {"slow": 20, "fast": 9}, "symbol": "SPY"}

    assert calculate_config_hash(first) == calculate_config_hash(reordered)


def test_credentials_are_absent_and_cannot_influence_hash(tmp_path, monkeypatch) -> None:
    first_api_key = "first-dotenv-api-credential"
    first_secret_key = "first-dotenv-secret-credential"
    second_api_key = "second-dotenv-api-credential"
    second_secret_key = "second-dotenv-secret-credential"
    first_env = tmp_path / "first.env"
    second_env = tmp_path / "second.env"
    first_env.write_text(
        f"ALPACA_API_KEY={first_api_key}\nALPACA_SECRET_KEY={first_secret_key}\n",
        encoding="utf-8",
    )
    second_env.write_text(
        f"ALPACA_API_KEY={second_api_key}\nALPACA_SECRET_KEY={second_secret_key}\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("ALPACA_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_SECRET_KEY", raising=False)

    first_settings = load_settings(env_path=first_env)
    second_settings = load_settings(env_path=second_env)
    first_snapshot = build_config_snapshot(first_settings.research)
    second_snapshot = build_config_snapshot(second_settings.research)
    serialized_snapshot = json.dumps(first_snapshot)

    assert "api_key" not in serialized_snapshot
    assert "secret_key" not in serialized_snapshot
    assert first_api_key not in serialized_snapshot
    assert first_secret_key not in serialized_snapshot
    assert calculate_config_hash(first_snapshot) == calculate_config_hash(second_snapshot)


def test_git_metadata_absence_is_safe(tmp_path) -> None:
    assert get_git_commit(tmp_path) is None


def test_created_running_completed_lifecycle() -> None:
    run = create_run()
    assert run.status is RunStatus.CREATED

    run.start()
    assert run.status is RunStatus.RUNNING

    run.complete()
    assert run.status is RunStatus.COMPLETED
    assert run.error_type is None
    assert run.error_message is None


def test_failure_records_redacted_error_information(monkeypatch) -> None:
    api_key = "failure-api-credential"
    secret_key = "failure-secret-credential"
    monkeypatch.setenv("ALPACA_API_KEY", api_key)
    monkeypatch.setenv("ALPACA_SECRET_KEY", secret_key)
    load_settings(env_path=None)
    run = create_run()

    run.start()
    run.fail(RuntimeError(f"operation failed for {api_key}/{secret_key}"))

    assert run.status is RunStatus.FAILED
    assert run.error_type == "RuntimeError"
    assert run.error_message == "operation failed for **********/**********"
    assert run.completed_at is not None


@pytest.mark.parametrize("transition", ["start", "complete", "fail"])
def test_terminal_run_rejects_invalid_transitions(transition: str) -> None:
    run = create_run()
    run.start()
    run.complete()

    with pytest.raises(RunLifecycleError):
        if transition == "fail":
            run.fail(RuntimeError("expected test failure"))
        else:
            getattr(run, transition)()


def test_end_date_cannot_precede_start_date() -> None:
    with pytest.raises(ValidationError, match="start_date must be on or before end_date"):
        ResearchRun.create(
            load_research_config(),
            start_date=END_DATE,
            end_date=START_DATE,
        )
