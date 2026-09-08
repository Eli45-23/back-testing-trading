# Rejection Entry Study V1 — completed historical discovery

## Technical summary

The frozen four-variant confirmation study ran on 170 complete development sessions from 2026-01-02 through 2026-09-04. It evaluated every eligible interaction, not only later rejections, and used no network or post-cutoff partitions.

## Population and coverage

The denominator contains 6370 eligible interaction episodes. The local validation found 4 certified premarket sessions; PMH/PML remain unavailable for the other 166 sessions. RTH, prior-session, prior-week, and 1H warm-up gates passed.

## Variant signal frequency

| Variant | Eligible | Signals | Signal rate | Executable | Above/up | Below/down |
|---|---:|---:|---:|---:|---:|---:|
| IMMEDIATE_CLOSE_BACK_1M | 6370 | 3356 | 52.68% | 3311 | 1686 | 1670 |
| IMMEDIATE_CLOSE_BACK_5M | 6370 | 3319 | 52.10% | 3233 | 1661 | 1658 |
| MOMENTUM_AWAY_025 | 6370 | 6168 | 96.83% | 6024 | 3097 | 3071 |
| ONE_RETEST_HOLD | 6370 | 1045 | 16.41% | 1031 | 518 | 527 |

## Path quality and fixed directional pairs

Path metrics are descriptive post-executable-reference excursions. Same-minute favorable/adverse ordering remains ambiguous; unresolved and session-close-censored observations stay separate.

| Variant | Paths | Mean MFE | Median MFE | Mean MAE | Median MAE |
|---|---:|---:|---:|---:|---:|
| IMMEDIATE_CLOSE_BACK_1M | 3311 | 1.082530292962851102385986107 | 0.760000000000 | 1.098896526729084868619752341 | 0.750000000000 |
| IMMEDIATE_CLOSE_BACK_5M | 3233 | 1.087627961645530467058459635 | 0.760000000000 | 1.076396721311475409836065574 | 0.780000000000 |
| MOMENTUM_AWAY_025 | 6024 | 1.112736039176626826029216467 | 0.780000000000 | 1.130716666666666666666666667 | 0.810050000000 |
| ONE_RETEST_HOLD | 1031 | 1.013322405431619786614936954 | 0.689900000000 | 1.012806789524733268671193016 | 0.710000000000 |

## Paired waiting-cost comparisons

Each exact-identity paired subset is reported alongside the unconditional Immediate population. A paired subset is not a valid live filter for the earlier signal because later confirmation is future information.

- **IMMEDIATE_CLOSE_BACK_1M vs IMMEDIATE_CLOSE_BACK_5M**: 6370 exact pairs; 2337 executable pairs; mean additional wait 2.062214848610535047698050601 minutes; directional disadvantage mean 0.1869952075310226786478391100; right-worse 59.31%.
- **IMMEDIATE_CLOSE_BACK_1M vs MOMENTUM_AWAY_025**: 6370 exact pairs; 3210 executable pairs; mean additional wait 2.609578660200060624431645953 minutes; directional disadvantage mean 0.02614915887850467289719626168; right-worse 44.30%.
- **IMMEDIATE_CLOSE_BACK_1M vs ONE_RETEST_HOLD**: 6370 exact pairs; 1031 executable pairs; mean additional wait 8.728229665071770334928229665 minutes; directional disadvantage mean -0.01277070805043646944713870029; right-worse 43.74%.

## Context and robustness

Context tables use fixed, predeclared groups only. Monthly and whole-session bootstrap tables include zero-signal sessions. Reversal associations are independent and must not be read as rejection probabilities.

## What cannot be concluded

This is an entry-confirmation and waiting-cost study, not a trading backtest. It does not estimate stops, targets, R, P&L, profit factor, position sizing, or a best strategy, and it does not authorize a live candidate or alter Stage 14.

## Provenance and verification

Git commit: `a3909eaa0271a381fd6e05756628c07148bac65c`. Rejection Entry protocol hash: `b6175efed8e555cc47bf7df90705cc32ea94e24a7fa30f78a69c115d3f3fa484`. Design hash recorded: `b6175efed8e555cc47bf7df90705cc32ea94e24a7fa30f78a69c115d3f3fa484`. Post-cutoff outcome partitions opened: 0. Failed-run provenance preserved separately.
