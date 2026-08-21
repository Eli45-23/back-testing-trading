from __future__ import annotations

import socket
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

import spy_research.cli as cli_module
from spy_research.interactions import (
    ImmediateState,
    InteractionType,
    LevelType,
    RetestState,
)
from spy_research.strategy import (
    BasePriceActionCandidate,
    BasePriceActionResult,
    BaseSetupStatus,
    ConfirmationType,
    SetupDirection,
)
from spy_research.strategy.comparisons import (
    CombinedContextInputError,
    CombinedContextMatrixService,
    Ema9VwapAlignmentState,
    Ema9VwapCrossContextState,
    Ema20VwapAlignmentState,
    Ema20VwapCrossContextState,
    EmaAlignmentState,
    EmaCrossContextState,
    VwapAlignmentState,
    combine_context_annotations,
)


SESSION = date(2026, 8, 19)
CONFIRMATION = datetime(2026, 8, 19, 17, 10, tzinfo=UTC)


def setup() -> BasePriceActionCandidate:
    return BasePriceActionCandidate(
        setup_identity="setup",
        break_interaction_identity="break",
        follow_through_identity="follow",
        session_date=SESSION,
        level_type=LevelType.ORL5,
        level_price=Decimal("100"),
        direction=SetupDirection.SHORT,
        break_interaction_type=InteractionType.CLOSE_THROUGH_BELOW,
        break_timestamp=CONFIRMATION - timedelta(minutes=5),
        break_completed_at=CONFIRMATION,
        exact_immediate_state=ImmediateState.HOLD,
        exact_retest_state=RetestState.NO_RETEST,
        status=BaseSetupStatus.CONFIRMED,
        confirmation_type=ConfirmationType.IMMEDIATE_HOLD,
        confirmation_bar_timestamp=CONFIRMATION,
        signal_known_at=CONFIRMATION + timedelta(minutes=5),
        earliest_entry_timestamp=CONFIRMATION + timedelta(minutes=5),
        same_session_executable=True,
    )


def source(**values):
    item = setup()
    return SimpleNamespace(
        setup_identity=item.setup_identity,
        session_date=item.session_date,
        direction=item.direction,
        confirmation_bar_timestamp=item.confirmation_bar_timestamp,
        signal_known_at=item.signal_known_at,
        **values,
    )


def combine(*, future_marker=None):
    item = setup()
    setups = BasePriceActionResult(
        start_date=SESSION,
        end_date=SESSION,
        seed_count=1,
        confirmed_count=1,
        non_confirmed_count=0,
        candidates=(item,),
    )
    ema = source(alignment_state=EmaAlignmentState.EMA_ALIGNED)
    ema.future_marker = future_marker
    return combine_context_annotations(
        setups,
        (ema,),
        (
            source(
                cross_state=EmaCrossContextState.MATCHING_CROSS,
                bars_since_cross=5,
            ),
        ),
        (source(alignment_state=VwapAlignmentState.VWAP_ALIGNED),),
        (source(alignment_state=Ema9VwapAlignmentState.EMA9_VWAP_ALIGNED),),
        (
            source(
                cross_state=Ema9VwapCrossContextState.MATCHING_EMA9_VWAP_CROSS,
                bars_since_cross=3,
            ),
        ),
        (source(alignment_state=Ema20VwapAlignmentState.EMA20_VWAP_ALIGNED),),
        (
            source(
                cross_state=Ema20VwapCrossContextState.MATCHING_EMA20_VWAP_CROSS,
                bars_since_cross=0,
            ),
        ),
    )


def test_combines_all_accepted_states_and_exact_recencies() -> None:
    annotation = combine()[0]
    assert annotation.setup_identity == "setup"
    assert annotation.direction is SetupDirection.SHORT
    assert annotation.level_type is LevelType.ORL5
    assert annotation.ema9_20_alignment is EmaAlignmentState.EMA_ALIGNED
    assert annotation.ema9_20_bars_since_cross == 5
    assert annotation.price_vwap_alignment is VwapAlignmentState.VWAP_ALIGNED
    assert annotation.ema9_vwap_bars_since_cross == 3
    assert annotation.ema20_vwap_bars_since_cross == 0
    assert annotation.context_key.ema20_vwap_bars_since_cross == 0


def test_unrelated_future_fields_cannot_change_combined_record() -> None:
    assert combine(future_marker="first") == combine(future_marker="changed")


def test_source_metadata_mismatch_is_rejected() -> None:
    item = setup()
    setups = BasePriceActionResult(
        start_date=SESSION,
        end_date=SESSION,
        seed_count=1,
        confirmed_count=1,
        non_confirmed_count=0,
        candidates=(item,),
    )
    valid = source(alignment_state=EmaAlignmentState.EMA_ALIGNED)
    invalid = source(cross_state=EmaCrossContextState.NO_PRIOR_CROSS, bars_since_cross=None)
    invalid.signal_known_at += timedelta(minutes=5)
    with pytest.raises(CombinedContextInputError, match="metadata mismatch"):
        combine_context_annotations(
            setups,
            (valid,),
            (invalid,),
            (source(alignment_state=VwapAlignmentState.VWAP_ALIGNED),),
            (source(alignment_state=Ema9VwapAlignmentState.EMA9_VWAP_ALIGNED),),
            (
                source(
                    cross_state=Ema9VwapCrossContextState.NO_PRIOR_EMA9_VWAP_CROSS,
                    bars_since_cross=None,
                ),
            ),
            (source(alignment_state=Ema20VwapAlignmentState.EMA20_VWAP_ALIGNED),),
            (
                source(
                    cross_state=Ema20VwapCrossContextState.NO_PRIOR_EMA20_VWAP_CROSS,
                    bars_since_cross=None,
                ),
            ),
        )


def test_combined_record_is_immutable_and_contains_no_strategy_label() -> None:
    annotation = combine()[0]
    with pytest.raises(ValidationError):
        annotation.direction = SetupDirection.LONG
    forbidden = {"good", "bad", "score", "confidence", "regime", "qualified"}
    assert forbidden.isdisjoint(type(annotation).model_fields)


def test_no_prior_state_and_exact_recency_must_reconcile() -> None:
    annotation = combine()[0]
    payload = annotation.model_dump()
    payload["ema20_vwap_cross_context"] = (
        Ema20VwapCrossContextState.NO_PRIOR_EMA20_VWAP_CROSS
    )
    with pytest.raises(ValidationError, match="state and exact recency"):
        type(annotation)(**payload)


def test_combination_is_offline_and_nonpersistent(monkeypatch, tmp_path) -> None:
    def reject_network(*args, **kwargs):
        raise AssertionError("Stage 10.8 must remain offline")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    combine()
    assert list(tmp_path.iterdir()) == []


def test_cli_is_offline_and_read_only(monkeypatch, tmp_path, capsys) -> None:
    sentinel = object()

    def mocked_calculate(self, *, start, end):
        assert start == end == SESSION
        return sentinel

    def mocked_print(result):
        assert result is sentinel
        print("combined-context-pass")

    monkeypatch.setattr(CombinedContextMatrixService, "calculate", mocked_calculate)
    monkeypatch.setattr(cli_module, "_print_combined_context_matrix", mocked_print)
    exit_code = cli_module.main(
        [
            "compare-combined-context-matrix",
            "--start",
            SESSION.isoformat(),
            "--end",
            SESSION.isoformat(),
            "--raw-data-root",
            str(tmp_path / "raw"),
            "--processed-data-root",
            str(tmp_path / "processed"),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "combined-context-pass\n"
    assert captured.err == ""
    assert list(tmp_path.iterdir()) == []
