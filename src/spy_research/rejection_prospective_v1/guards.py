"""Fail-closed calendar, data-validity, and endpoint guards."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Mapping, Sequence

from .models import ProspectiveSession, ReadinessResult
from .protocol import (
    CANDIDATES,
    CONTROL,
    DEVELOPMENT_END,
    MIN_CONTRIBUTING_SESSIONS,
    MIN_EXECUTABLE_OUTCOMES,
    PROSPECTIVE_END,
    PROSPECTIVE_START,
    SESSION_COUNT,
)


def build_session_plan(*, start: date = PROSPECTIVE_START, count: int = SESSION_COUNT) -> tuple[ProspectiveSession, ...]:
    """Build exactly ``count`` local XNYS sessions; this reads no market data."""

    if start != PROSPECTIVE_START or count != SESSION_COUNT:
        raise ValueError("prospective session plan is frozen")
    from spy_research.market import XNYSCalendar

    calendar = XNYSCalendar()
    result: list[ProspectiveSession] = []
    cursor = start
    while len(result) < count:
        session = calendar.session_for_date(cursor)
        if session.is_trading_day:
            assert session.market_open is not None and session.market_close is not None
            result.append(
                ProspectiveSession(
                    session_date=cursor,
                    market_open=session.market_open,
                    market_close=session.market_close,
                    early_close=session.is_early_close,
                )
            )
        cursor += timedelta(days=1)
    validate_session_plan(result)
    return tuple(result)


def validate_session_plan(sessions: Sequence[ProspectiveSession]) -> None:
    if len(sessions) != SESSION_COUNT:
        raise ValueError("exactly 60 XNYS sessions are required")
    dates = [session.session_date for session in sessions]
    if dates != sorted(dates) or len(set(dates)) != SESSION_COUNT:
        raise ValueError("session dates must be unique and ordered")
    if dates[0] != PROSPECTIVE_START:
        raise ValueError("plan must begin at the first full session after development")
    if dates[-1] != PROSPECTIVE_END:
        raise ValueError("plan must end at the frozen 60th XNYS session")
    if any(day <= DEVELOPMENT_END for day in dates):
        raise ValueError("development dates cannot enter prospective plan")
    from spy_research.market import XNYSCalendar

    calendar = XNYSCalendar()
    for item in sessions:
        authoritative = calendar.session_for_date(item.session_date)
        if not authoritative.is_trading_day or item.market_open != authoritative.market_open or item.market_close != authoritative.market_close:
            raise ValueError("session plan boundary is not authoritative XNYS metadata")


def validate_outcome_date(day: date, sessions: Sequence[ProspectiveSession]) -> None:
    """Allow only one of the predeclared 60 sessions; reject all other dates."""

    validate_session_plan(sessions)
    if day not in {session.session_date for session in sessions}:
        raise ValueError("outcome date is outside the fixed prospective window")


def validate_market_path(path: str | Path, session: ProspectiveSession, *, root: str | Path = ".") -> Path:
    """Validate a prospective partition identity before any caller opens it."""

    candidate = (Path(root) / path).resolve()
    expected_date = session.session_date.isoformat()
    if candidate.suffix != ".parquet" or candidate.stem != expected_date:
        raise ValueError("market partition is not the exact planned session")
    if session.session_date <= DEVELOPMENT_END:
        raise ValueError("development partition cannot be used as prospective outcome data")
    return candidate


def evaluate_readiness(
    *,
    as_of: datetime,
    sessions: Sequence[ProspectiveSession],
    validated_sessions: Sequence[date],
    complete_data: Mapping[date, bool],
    executable_outcomes: Mapping[str, int],
    contributing_sessions: Mapping[str, int],
) -> ReadinessResult:
    """Return interim/block/endpoint status without selecting a model."""

    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("aware endpoint timestamp required")
    validate_session_plan(sessions)
    plan_dates = {session.session_date for session in sessions}
    validated = tuple(validated_sessions)
    if len(validated) != len(set(validated)) or not set(validated) <= plan_dates:
        raise ValueError("validated session inventory is invalid")
    completed = {session.session_date for session in sessions if session.market_close <= as_of.astimezone(UTC)}
    if not set(validated) <= completed:
        raise ValueError("validated session is not complete as of endpoint timestamp")
    if len(completed) < SESSION_COUNT:
        return ReadinessResult(
            status="INTERIM_NO_SELECTION",
            completed_sessions=len(completed),
            validated_sessions=len(validated),
        )
    missing = tuple(sorted(day.isoformat() for day in plan_dates if not complete_data.get(day, False)))
    if set(validated) != plan_dates or missing:
        return ReadinessResult(
            status="BLOCKED_DATA_QUALITY",
            completed_sessions=SESSION_COUNT,
            validated_sessions=len(validated),
            missing_or_invalid_sessions=missing or tuple(sorted(day.isoformat() for day in plan_dates - set(validated))),
        )
    assessments: dict[str, str] = {}
    for model in (*CANDIDATES, CONTROL):
        outcomes = executable_outcomes.get(model)
        sessions_count = contributing_sessions.get(model)
        if type(outcomes) is not int or type(sessions_count) is not int or outcomes < 0 or sessions_count < 0:
            raise ValueError("validated counts are required for every frozen model")
        assessments[model] = (
            "ENDPOINT_REPORT_ELIGIBLE"
            if outcomes >= MIN_EXECUTABLE_OUTCOMES and sessions_count >= MIN_CONTRIBUTING_SESSIONS
            else "INSUFFICIENT_PROSPECTIVE_DATA"
        )
    return ReadinessResult(
        status="ENDPOINT_REACHED_NO_SELECTION",
        completed_sessions=SESSION_COUNT,
        validated_sessions=SESSION_COUNT,
        candidate_assessments=assessments,
    )


def assert_outcome_access_is_enabled(explicit_enable: bool) -> None:
    """Design-phase guard: the design cannot accidentally generate outcomes."""

    if not explicit_enable:
        raise PermissionError("prospective outcome generation is disabled in the design phase")
