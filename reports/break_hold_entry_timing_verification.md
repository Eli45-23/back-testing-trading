# Frozen V1 entry-timing analysis verification

Verified September 6, 2026. This is an offline analysis of the saved canonical report, not a signal-detection rerun.

## Results

- Full test suite: **1,112 passed** (including 18 new analysis regression cases; previous count 1,094).
- Focused analysis tests: **18 passed**.
- Canonical counts: **170 sessions, 1,435 breaks, 733 FIRST_HOLD, 524 STRONG_HOLD**.
- Exact matched identities: **524**; never-strong first holds: **209**.
- Complete paired EOD excursion records: **522**; two unavailable pairs retained in entry and threshold counts.
- Independent arithmetic from the canonical JSON confirms mean directional entry disadvantage, paired MFE loss, paired MAE improvement, and net change of −62 clean outcomes at the predeclared $0.50/$0.25 illustrative pair.
- All subgroup populations partition their original style counts. All threshold category counts sum to their denominators. Available plus unavailable EOD counts reconcile.
- Monthly and session-width partitions reconcile to 170 sessions; monthly pairs reconcile to 524.
- All **151** fixed 20-session windows are present.
- Paired CSV: **524 unique event rows**, including both reference prices, outcomes, and threshold-hit timestamps.
- Matched reclaim identities reconcile: **382 reclaims from each reference entry**; their remaining time to the same reclaim differs.
- Compilation/import: PASS. Dependency check: no broken requirements.
- Git whitespace check: PASS.

## Frozen integrity

SHA-256 comparison against the pre-analysis inventory: **1,493 existing files checked, zero changed or missing**. The inventory covers the then-existing Python source, research configuration, canonical V1 JSON/CSV/Markdown, and existing raw/processed Parquet files. New analysis files are outside that frozen inventory.

Canonical JSON SHA-256:

`6aaf9980ecd7798420151a8b97436311eca6429e9f31fdb33be1ed86c8c47148`

No frozen V1, Stage 14, historical data, or existing research implementation was edited during this analysis. Pre-existing uncommitted changes from earlier work were preserved; the worktree is intentionally not clean. Nothing was staged, committed, or pushed. No broker connection, market-data download, PAPER order, or live execution occurred.

## Reproduction

From the repository root:

```sh
PYTHONPATH=src .venv/bin/python scripts/analyze_break_hold_entry_timing.py
PYTHONPATH=src .venv/bin/python -m pytest -q
```

The analysis uses 10,000 whole-session bootstrap resamples, seed 20260906, and the conventions recorded in [the pre-analysis plan](break_hold_entry_timing_analysis_plan.md). It refuses canonical count/identity/threshold discrepancies rather than interpreting a changed population.

The analysis remains descriptive: overlapping outcomes are not additive trading profits, bootstrap intervals are pointwise, and eventual-strong pairing conditions on a later event. No realized entry-policy expectancy or independent validation is claimed.
