# Frozen First Hold exit study — verification

Completed September 7, 2026. Protocol was declared before outcome computation. Assessment: **share with caveats**, not a validated live trading policy.

## Checks

| Check | Result |
|---|---|
| Full existing + new suite | 1,161 passed; 24 new focused exit tests |
| Frozen variant inventory | Exactly 21 unique models; no post-result additions or threshold changes |
| Record identities | 15,393 unique event/variant pairs = 733 × 21 |
| Available arithmetic | 13,602 rows passed independent price/R consistency checks |
| Independent raw-bar exits | 12,148 fixed, time and reclaim paths matched a separate directional-coordinate implementation |
| Management updates | All recorded updates known after entry, active no earlier than known-at, and tighten only; lifecycle behavior covered by focused tests |
| Aggregate audit | All 21 primary means, win counts, drawdowns and losing streaks independently recalculated |
| Determinism | Repeated full run: JSON, complete tables and CSV all byte-identical |
| Preservation inventory | All 1,524 pre-existing source/report/data/config files unchanged byte-for-byte |
| Dependency check | pip check passed |
| Compilation/import | New study/report modules and scripts passed |
| Credential-pattern scan | New source/tests/scripts/reports passed; no credentials or headers printed |
| Whitespace | git diff --check passed |
| Live boundary | No broker connection, download, PAPER service or order submission; no Stage 14 edits |
| Git | No commit or push; prior dirty-worktree changes preserved |

The raw-path audit does not reuse the simulator or its metric helpers. Trailing and breakeven paths are checked through targeted lifecycle tests and all-record arithmetic/timestamp/monotonic-stop checks, not claimed as fully independently reimplemented models. Source ATR precision received an explicit 80-digit Decimal context and a 50-digit regression before final verification; no rule or parameter changed. Bootstrap aggregation uses numerical arrays, not broker-price calculations.

## Frozen lineage

- Canonical JSON SHA-256: `6aaf9980ecd7798420151a8b97436311eca6429e9f31fdb33be1ed86c8c47148`
- Definition hash: `92b8c227e32c4fd43001da58fa0865fc61e868faa53c0bab2199c258e91f5f4d`
- Input manifest hash: `2caffada233ed08d9cec0da158c46ae56b6874ab979cc2d9d54aec844bd8c8cd`
- Every source raw partition was additionally checked against the saved prior-study lineage before exit simulation. No missing minutes were filled.
- The preservation inventory includes pre-existing Stage 14 source and accepted historical reports/manifests. Existing unrelated uncommitted work was not reverted or incorporated into this study's changes. Accepted historical pipelines were not rerun or rewritten for this task.

## Reproducible outputs

| Artifact | SHA-256 |
|---|---|
| break_hold_exit_study.json | `5626c79646902bea395fb99713cd1fff71d45bbc0f31634fd82b3c9ecd2c5ff2` |
| break_hold_exit_study_tables.md | `9adf9ce4fe5cb8b18e5bb585f70e0ab83ef637a10331930ae7a90e39f4e39959` |
| break_hold_exit_study_trades.csv | `834821ac8acedf8683a98a74093770e9034e642e55856960839115512c640f40` |

Reproduce offline from the repository root with `PYTHONPATH=src OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/analyze_first_hold_exits.py`; audit with `PYTHONPATH=src .venv/bin/python scripts/verify_first_hold_exits.py`.

## Required caveats

This is development-period, event-level evidence. Confidence intervals are pointwise across 21 models; selection can overfit. ATR warm-up reduces the available population. Same-minute ambiguity is unresolved and exact R remains null. Touch/close fills are idealizations, cost sensitivities are not a real execution model, and overlapping-event drawdown is not account drawdown. These limitations prevent a live-policy conclusion. Any shortlist requires separately frozen, genuinely unseen validation without new entry filters or exit retuning.
