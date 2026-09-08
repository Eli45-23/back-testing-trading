# Key-Level Reactions V1 — repaired historical discovery

## Technical summary

The repaired engine completed the unchanged descriptive study for **170 development sessions**. It produced **1067 unique level identities including context**, **41,638 touching minutes**, **6,370 reaction episodes**, and **57,330 fixed reaction rows**. These are reactions from levels, not trading outcomes.

The most important data limitation remains premarket coverage: PMH/PML are available only on the four sessions with a complete 04:00–09:30 grid and unavailable on the other 166. RTH coverage is complete. All findings below are descriptive; they do not estimate entries, stops, targets, R multiples, win rates, P&L or strategy quality.

## Scope, data and definitions

- Engine commit: `ae8e87092e53e1ae73e7a6344325f53f39041202`.
- Outcomes: January 2–September 4, 2026 inclusive, New York time.
- Causal context: December 22–31, 2025 only. Prospective September 8–December 1 data was not opened.
- Fixed distances: $0.25, $0.50 and $1.00; fixed horizons: 5, 15 and 30 minutes.
- Primary touch: `minute.low <= level.price <= minute.high`; all five statuses remain in every denominator.
- Fixed predeclared reporting groups are documented in `reporting_plan.md`.

## Coverage and data quality

RTH coverage passed at **66,300/66,300 development minutes** with zero missing minutes, zero duplicates and no invalid development sessions. The seven-session context had 2,550/2,550 RTH minutes. There were no development early closes; December 24, 2025 was an early-close context session.

Premarket coverage was complete on **4/170 sessions** (March 3, April 8, April 13 and July 8). The other 166 sessions remain unavailable for PMH/PML; no sparse premarket extrema were inferred. Previous-session and previous-week context were available for all development sessions. Ten confirmed 1H swings were available before the outcome window.

See `coverage_summary.json`, `coverage_raw.json`, `coverage_sessions.json` and `independent_reconciliation.json`.

## Population reconciliation

The study contains **1,067 unique levels**, **41,638 touching minutes**, **18,056 touch runs**, **6,370 episodes**, **649 gap-cross records**, and **17,758 reversal records**. Every episode has exactly nine reaction rows, and all five statuses sum to each panel denominator. See `independent_reconciliation.json` and `denominators.json`.

## Level-family reaction behavior

The complete family × distance × horizon counts and rates are in `family_reactions.csv`. The compact $0.50/15-minute panel below is a readability anchor, not a selection or ranking:

| Family | Episodes | Rejection-first | Continuation-first | Ambiguous | Unresolved | Censored |
|---|---:|---:|---:|---:|---:|---:|
| PDH | 233 | 60 (25.75%) | 68 (29.18%) | 65 (27.90%) | 36 (15.45%) | 4 (1.72%) |
| PDL | 213 | 70 (32.86%) | 66 (30.99%) | 61 (28.64%) | 15 (7.04%) | 1 (0.47%) |
| PMH | 3 | 2 (66.67%) | 1 (33.33%) | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) |
| PML | 8 | 1 (12.50%) | 2 (25.00%) | 4 (50.00%) | 1 (12.50%) | 0 (0.00%) |
| ORH5 | 439 | 145 (33.03%) | 144 (32.80%) | 100 (22.78%) | 45 (10.25%) | 5 (1.14%) |
| ORL5 | 422 | 149 (35.31%) | 114 (27.01%) | 113 (26.78%) | 42 (9.95%) | 4 (0.95%) |
| PWH | 104 | 28 (26.92%) | 25 (24.04%) | 23 (22.12%) | 25 (24.04%) | 3 (2.88%) |
| PWL | 90 | 29 (32.22%) | 20 (22.22%) | 38 (42.22%) | 2 (2.22%) | 1 (1.11%) |
| 1H_HIGH | 2298 | 715 (31.11%) | 634 (27.59%) | 622 (27.07%) | 298 (12.97%) | 29 (1.26%) |
| 1H_LOW | 2560 | 794 (31.02%) | 705 (27.54%) | 814 (31.80%) | 219 (8.55%) | 28 (1.09%) |

Direct PDH/PDL, PMH/PML, ORH5/ORL5, previous-week and 1H high/low comparisons are in `family_direction_pairs.csv`; no family is labeled best.

## Touch history, breach history and retests

Fixed first-creation, same-session, observed-lifetime, history-completeness, breach-history, multiple-breach, time-of-day and approach-side tables are in the corresponding CSV files. `immediate_retest.csv` separates immediate/single-touch, later single-touch, one-retest and multiple-test descriptive paths. These groups are not filters and repeated touches are not independent sessions.

## Reversal-first discovery

The independent completed-close detector produced 17,758 reversal records across the three distances. Association with levels is measured only at turning-time availability; it is not a rejection-probability estimate. Results by radius, family and nearest-distance bucket are in `reversal_associations.csv`, `reversal_family_associations.csv` and `reversal_nearest_distance.csv`.

## Confluence and next levels

Confluence uses all frozen radii (0, $0.05, $0.10 and $0.25), preserves every identity and separately records shared-source relationships. Tables distinguish one, two and three-plus identities/families; they do not assert that more confluence is better.

`next_level_tables.csv` reports causal first-touch snapshots, distance distributions and reached/invalidated/ambiguous/censored ordering. A next-level hit before rejection recognition remains explicitly separate.

## Monthly and session stability

`monthly_reactions.csv`, `session_reactions.csv` and `session_bootstrap.csv` provide monthly rates, contributing sessions, partial-September labeling and the committed 2,000-draw whole-session pointwise intervals. September is a four-session partial month. These intervals are descriptive uncertainty summaries, not selection criteria.

## Ambiguity, censoring and interpretation limits

Ambiguous outcomes are retained whenever same-minute ordering cannot be known; censoring is separately flagged and never made favorable. Reaction-first percentages are not trade win rates. The study cannot identify a best strategy, establish causality, estimate profitability, or justify new filters, thresholds, entries, exits or forward candidates. It also cannot support strong PMH/PML conclusions beyond the four certified sessions.

## Verification and provenance

- Repair commit: `ae8e87092e53e1ae73e7a6344325f53f39041202`.
- Repaired run manifest records source/protocol/input/output hashes and the 177 permitted partitions.
- Frozen break-and-hold verification: 174/174 hashes matched before and after.
- Focused and full test receipts are recorded in `verification.json` after the post-run test pass.
- No Stage 14 or frozen break-and-hold artifact changed; no Alpaca/network service was contacted.
- The original blocked run remains unchanged in `reports/key_level_reactions_v1/`; this is a separate completed-run directory.

## Review-only next step

Review the completed descriptive evidence and data limitations. Do not alter the declared protocol or infer a trading strategy from this first reaction study.
