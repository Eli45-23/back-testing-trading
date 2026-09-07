# First Hold quality study: verification

As of September 6, 2026. Assessment: **share with caveats**, not an entry-policy approval.

## Verified population and timing

- Canonical population: **170 sessions, 1,435 breaks, 733 First Holds, 524 eventual-strong, 209 never-strong**.
- Canonical signal detection was not rerun. Original saved signal records were joined by exact event identity.
- Two reference modes remain distinct: original close V1 and entry-inclusive first executable minute open.
- New reference outcomes: **1,257 records**, **1,249 available entries** and **eight unavailable at session close** (six First Holds, two Strong Holds). No session crossover, missing-minute fill, or entry-price imputation.
- Available matched executable pairs: **522**. All **524** original pairs remain in threshold denominators and the paired CSV; unavailable prices are blank with explicit entry status.
- Exact signal-time eligibility is tested for opening completion at 09:35 and later completions, both LONG and SHORT. A minute inside confirmation is excluded even if its extremes dominate; the minute starting at completion is included and supplies the reference open.
- Changing the eligible minute's future close does not change its entry-reference price. Session-close signals do not use next-session bars. Duplicate, wrong-feed, and wrong-session inputs fail closed.

## Leakage and independent checks

- Feature API accepts only a First Hold signal, bars, and its session. It does not accept eventual label, event/reclaim state, strong signal, or outcomes.
- Future-bar removal/mutation leaves features identical, including late signals with warmed-up indicators. Altering later strong/reclaim metadata cannot change the feature vector.
- Exact completed confirmation-row matching is enforced. Relative volume excludes confirmation and requires six prior completed bars. Unavailable ATR/EMA/structure history is not backfilled.
- **Independent saved-output audit:** all 733 candle-feature records reconstructed directly from raw-minute OHLC/volume; all 1,249 executable paths and every one of the nine threshold pairs checked against raw minutes; all 522 paired entry-price differences recomputed. PASS.
- Numeric availability, categorical partitions, threshold denominators, 733-row feature CSV, and 524-row paired CSV reconcile. All 66,300 RTH minutes across 170 sessions are present.
- Whole-session bootstrap uses shared label/pair resampling, not independent event resampling. Determinism, event weighting, missing denominators and tied-rank correlations have focused regression coverage.

Reproduce the independent audit:

```sh
PYTHONPATH=src .venv/bin/python scripts/verify_first_hold_quality.py
```

## Tests and frozen integrity

- Focused new tests: **25 passed**.
- Full suite: **1,137 passed** (previous baseline 1,112).
- Compilation/import and dependency check: PASS.
- Git whitespace check and new-source whitespace scan: PASS.
- Static secret-pattern scan of new study code and artifacts: PASS. This is a bounded static check, not a guarantee that arbitrary text can never contain a secret.
- **1,512 pre-existing files compared against their pre-study SHA-256 inventory: zero changed or missing.** This includes then-existing source, research configuration, reports, and raw/processed Parquet data. Existing Stage 14 execution source and previous V1 outputs remain untouched. New study files are additions outside that inventory.

Canonical V1 JSON SHA-256:

`6aaf9980ecd7798420151a8b97436311eca6429e9f31fdb33be1ed86c8c47148`

V1 definition hash:

`92b8c227e32c4fd43001da58fa0865fc61e868faa53c0bab2199c258e91f5f4d`

Original input-manifest hash:

`2caffada233ed08d9cec0da158c46ae56b6874ab979cc2d9d54aec844bd8c8cd`

No broker connection, data download, PAPER/live order, Stage 14 edit, options layer, trained model, feature score, strategy filter, exit model, staging, commit, or push occurred. Pre-existing uncommitted work remains preserved; the worktree is intentionally not clean.

## Required caveats and incomplete enrichment

1. **Stage 11.1 categorical regime labels unavailable:** no saved calibration artifact with causal signal-time provenance was found among the controlling project artifacts. Full-period recalibration would violate the requested predictor-time constraint. All 733 rows retain an explicit unavailable label, while all Stage 10.9 continuous inputs are measured. A verified calibration artifact and availability date would be required to add those labels; this is the one requested enrichment not numerically evaluated.
2. Six session-close First Holds have no opportunity to demonstrate progression that day. They remain in the requested never-strong population, explicitly censored. Never-strong is not synonymous with a failed trade.
3. Deeper boundary distance mechanically buffers against a close-reclaim. Longer pre-reclaim exposure and larger MAE may accompany survival. Associations do not establish entry-policy expectancy.
4. Warm-up availability, direction, time of day and volatility affect group composition. Monthly and directional tables expose, but do not causally resolve, these confounders.
5. Bootstrap intervals are exploratory/pointwise across correlated features, not multiplicity-adjusted confirmation. The largest absolute standardized differences are highlighted descriptively; none is certified as a filter.
6. The historical minute open is a timing-valid reference, not a guaranteed executable fill. Spread, latency, slippage and fees are outside this phase.

The requested Markdown decision report and complete table appendix were read and checked for coverage, denominators, linked artifacts, timing caveats and consistency with the saved results. No chart or deployment artifact was requested.
