# SPY Autonomous Edge Discovery V1 — Phase 1

Status: DESIGN_FROZEN. This phase implements design contracts and synthetic tests only. No predictive relationships, candidate profitability, real validation batch or historical outcome results are produced.

## Data roles and provenance

2024 is the discovery laboratory. 2025 is locked candidate-specific validation, but is not globally untouched: earlier repository research and this conversation have exposed some 2025 results. January 2–September 4, 2026 is INTERNAL_CONFIRMATION and likewise not globally untouched. September 8 onward remains prohibited prospective data. Only December 29, 2023 is permitted as prior-session context; it is never an outcome period. No context interpolation, missing-minute substitution or ATR fallback is permitted.

The complete 672-partition outcome inventory comprises 252 sessions in 2024, 250 in 2025 and 170 in 2026, totaling 261,000 RTH minutes. Its original byte hashes, relative paths, roles, sizes and coverage receipts are frozen. The context partition is recorded separately. Reads for hashing/coverage are distinguished from candidate evaluation. Missing, duplicate, changed, misassigned or out-of-window inputs fail closed before research use.

## Feature universe and prediction-first workflow

The exact feature registry is in feature_registry.json: completed returns; existing EMA9/20, daily-reset Wilder ATR14 and RTH VWAP; distances to VWAP, prior close, PDH/PDL and ORH5/ORL5; opening range and gap; rolling highs/lows; realized volatility; prior-20-minute relative volume; candle structure, consecutive close direction, calendar/time and causal crossing/failure events. No added periods or families, premarket-dependent features, 4H levels, options or external features.

Register each predicate before its outcomes are inspected, including its thresholds, direction, cadence, primary horizon, expected effect and one to three meaningful conditions. Natural reference thresholds or a registered training-only quantile grid are permitted. No threshold may use evaluation data. Each materially changed predicate consumes a hypothesis slot; all examined secondary horizons remain in the atomic comparison count.

Measure 5/15/30/60-minute and EOD directional return, MFE, MAE and favorable-before-adverse behavior, starting at the next executable minute open. Retain unavailable horizons and same-minute ambiguity. Compare against the same eligible unconditional population and month/minute-of-session/direction/feature-availability-matched baseline. Unavailable observations remain in denominators with reasons.

The expanding folds are Q1→Q2, Q1–Q2→Q3 and Q1–Q3→Q4. Fit thresholds only on training prefixes; purge training labels crossing the boundary. Once fold results influence subsequent choices, they are reused development evidence rather than independent validation.

## Search budget and candidate admission

Maximum 100 registered hypothesis specifications, 60 complete signal/risk/exit configurations and three validation candidates. Every serious test, meaningful parameter family and rejected configuration remains in the append-only hash-chained ledger. Identical reruns consume no new slot. Count every inspected threshold, horizon, direction and subgroup contrast; do not claim an effective independent count without justification.

A predictive relationship needs at least 200 observations over 80 sessions, positive directional lift in at least two chronological evaluation folds, and nominal Benjamini–Yekutieli q ≤ 0.10. Because discovery is adaptive, this FDR diagnostic does not eliminate selection bias or establish an edge.

Candidate selection order is chronological-fold net stability, net bootstrap lower bound, lower drawdown, fewer conditions, then stable specification ID. At most three candidates are frozen simultaneously; unused slots remain unused. Failed validation never opens a replacement slot.

## Results and interpretation

All examined discovery profitability is DISCOVERY_RESULTS. Validation and internal confirmation use exact frozen rules. Only survivors of all stages may receive ROBUST_EDGE_CANDIDATE. PROVEN_EDGE is forbidden. The correct final result may be NO ROBUST EDGE DISCOVERED. Historical evidence cannot establish prospective deployment readiness.

The endpoint includes specifications and discovery lineage; complete search ledger including failures; all signal/execution/unavailability denominators; win/loss/zero counts, mean/median R, average win/loss, PF, drawdown, losing streak, long/short, monthly behavior, costs, ambiguity sensitivities, session uncertainty, weaknesses and comparisons of discovery, validation and confirmation. No ranking by P&L or win rate alone.

No live/paper trading, prior research edits, network, commits or pushes are part of Phase 1.
