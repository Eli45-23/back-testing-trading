# Rejection Risk/Exit Study V1 — completed development run

Run provenance: frozen design commit `305f56a0ff607de34bafe8f528226192a5086bf6`; outcome window **2026-01-02 through 2026-09-04 inclusive**; protocol SHA-256 `4836afdeb0d4e2db8eafeb16ed4a818b49a85284d43ea9ee0b420fc195f1a15a`. This is a fixed research matrix, not a strategy-selection or live-trading result. No model is proven, ranked, or approved for deployment.

## Coverage and denominators

The source population is the frozen archived executable population: **3,311 IMMEDIATE_CLOSE_BACK_1M** identities and **6,024 MOMENTUM_AWAY_025** control identities. The 170-session calendar contains **66,300 complete RTH one-minute bars**; duplicate and missing RTH minutes are zero. No early-close session occurred in this interval. The full entry-to-close path was validated before any model was simulated. Exactly 149,360 outcome rows (9,335 entries × 16 models) were generated.

PMH/PML remain source-labeled and sparse/insufficient: only the four certified premarket sessions in the frozen source are eligible; the other 166 sessions were not reconstructed. No prior-session or prior-week data were opened by this run; level and interaction context came from the immutable archived source snapshots.

For every model, `eligible = executable + unavailable`; `ambiguous` is a subset of executable; and `executable = wins + losses + zero-R`. Fixed-stop models have no unavailable entries. ATR models retain unavailable signals explicitly: **1,018 primary / 1,899 control** ATR-unavailable entries, leaving **2,293 / 4,125** ATR-eligible outcomes (availability **69.254% / 68.476%**). Full monthly and directional availability is in [atr_availability.csv](./atr_availability.csv).

## Complete 32-model result (gross, stop-first)

The complete cost/sensitivity matrix is in [cost_sensitivity.csv](./cost_sensitivity.csv), and this table is the frozen gross stop-first view. Win rate is over executable outcomes; drawdown is cumulative event-order diagnostic, not account equity. CIs are whole-session bootstrap 95% intervals (10,000 draws, seed 20260908).

| Entry | Model | Eligible | Exec | Unavailable | Ambig. | Wins | Losses | Mean R | Median R | PF | Max DD R | Max loss streak | 95% CI mean R |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Immediate | USD025_TARGET_1R | 3311 | 3311 | 0 | 206 | 1580 | 1731 | -0.0453 | -1.0000 | 0.9133 | 185.06 | 17 | [-0.0887,-0.0016] |
| Immediate | USD025_TARGET_1.5R | 3311 | 3311 | 0 | 116 | 1304 | 2007 | -0.0163 | -1.0000 | 0.9731 | 110.52 | 17 | [-0.0666,0.0345] |
| Immediate | USD025_TARGET_2R | 3311 | 3311 | 0 | 78 | 1099 | 2212 | -0.0085 | -1.0000 | 0.9872 | 136.00 | 21 | [-0.0658,0.0489] |
| Immediate | USD025_TARGET_2R_BE1R | 3311 | 3311 | 0 | 104 | 881 | 1815 | -0.0020 | -1.0000 | 0.9963 | 112.18 | 17 | [-0.0572,0.0543] |
| Immediate | USD030_TARGET_1R | 3311 | 3311 | 0 | 116 | 1624 | 1687 | -0.0187 | -1.0000 | 0.9633 | 102.45 | 17 | [-0.0619,0.0257] |
| Immediate | USD030_TARGET_1.5R | 3311 | 3311 | 0 | 63 | 1307 | 2004 | -0.0132 | -1.0000 | 0.9781 | 97.02 | 18 | [-0.0639,0.0387] |
| Immediate | USD030_TARGET_2R | 3311 | 3311 | 0 | 39 | 1091 | 2220 | -0.0190 | -1.0000 | 0.9716 | 179.78 | 37 | [-0.0804,0.0429] |
| Immediate | USD030_TARGET_2R_BE1R | 3311 | 3311 | 0 | 60 | 870 | 1751 | 0.0067 | -1.0000 | 1.0129 | 105.20 | 17 | [-0.0477,0.0634] |
| Immediate | USD040_TARGET_1R | 3311 | 3311 | 0 | 68 | 1661 | 1650 | 0.0044 | 0.4500 | 1.0089 | 85.39 | 17 | [-0.0369,0.0469] |
| Immediate | USD040_TARGET_1.5R | 3311 | 3311 | 0 | 36 | 1352 | 1959 | 0.0144 | -1.0000 | 1.0245 | 126.89 | 22 | [-0.0394,0.0698] |
| Immediate | USD040_TARGET_2R | 3311 | 3311 | 0 | 13 | 1118 | 2193 | -0.0032 | -1.0000 | 0.9952 | 196.19 | 29 | [-0.0698,0.0659] |
| Immediate | USD040_TARGET_2R_BE1R | 3311 | 3311 | 0 | 23 | 880 | 1687 | 0.0218 | -0.3000 | 1.0437 | 127.88 | 17 | [-0.0328,0.0802] |
| Immediate | ATR050_TARGET_1R | 3311 | 2293 | 1018 | 14 | 1165 | 1128 | 0.0169 | 1.0000 | 1.0344 | 43.00 | 16 | [-0.0327,0.0673] |
| Immediate | ATR050_TARGET_1.5R | 3311 | 2293 | 1018 | 1 | 930 | 1363 | 0.0134 | -1.0000 | 1.0226 | 67.16 | 21 | [-0.0489,0.0776] |
| Immediate | ATR050_TARGET_2R | 3311 | 2293 | 1018 | 1 | 754 | 1539 | -0.0176 | -1.0000 | 0.9737 | 125.39 | 21 | [-0.0888,0.0542] |
| Immediate | ATR050_TARGET_2R_BE1R | 3311 | 2293 | 1018 | 8 | 569 | 1149 | -0.0029 | -0.0408 | 0.9942 | 89.73 | 16 | [-0.0621,0.0593] |
| Momentum | USD025_TARGET_1R | 6024 | 6024 | 0 | 452 | 2717 | 3307 | -0.0980 | -1.0000 | 0.8216 | 609.08 | 28 | [-0.1372,-0.0564] |
| Momentum | USD025_TARGET_1.5R | 6024 | 6024 | 0 | 229 | 2269 | 3755 | -0.0587 | -1.0000 | 0.9058 | 397.86 | 49 | [-0.1077,-0.0103] |
| Momentum | USD025_TARGET_2R | 6024 | 6024 | 0 | 135 | 1894 | 4130 | -0.0593 | -1.0000 | 0.9134 | 377.20 | 49 | [-0.1120,-0.0063] |
| Momentum | USD025_TARGET_2R_BE1R | 6024 | 6024 | 0 | 196 | 1454 | 3513 | -0.0770 | -1.0000 | 0.8623 | 480.88 | 29 | [-0.1226,-0.0312] |
| Momentum | USD030_TARGET_1R | 6024 | 6024 | 0 | 268 | 2790 | 3234 | -0.0738 | -1.0000 | 0.8625 | 482.78 | 29 | [-0.1138,-0.0325] |
| Momentum | USD030_TARGET_1.5R | 6024 | 6024 | 0 | 136 | 2302 | 3722 | -0.0452 | -1.0000 | 0.9268 | 313.43 | 33 | [-0.0931,0.0033] |
| Momentum | USD030_TARGET_2R | 6024 | 6024 | 0 | 77 | 1928 | 4096 | -0.0448 | -1.0000 | 0.9341 | 366.58 | 34 | [-0.1009,0.0112] |
| Momentum | USD030_TARGET_2R_BE1R | 6024 | 6024 | 0 | 105 | 1467 | 3394 | -0.0581 | -1.0000 | 0.8931 | 432.42 | 29 | [-0.1094,-0.0063] |
| Momentum | USD040_TARGET_1R | 6024 | 6024 | 0 | 129 | 2932 | 3091 | -0.0261 | -1.0000 | 0.9490 | 236.17 | 29 | [-0.0695,0.0170] |
| Momentum | USD040_TARGET_1.5R | 6024 | 6024 | 0 | 60 | 2350 | 3673 | -0.0290 | -1.0000 | 0.9523 | 308.19 | 34 | [-0.0793,0.0213] |
| Momentum | USD040_TARGET_2R | 6024 | 6024 | 0 | 13 | 1953 | 4070 | -0.0393 | -1.0000 | 0.9416 | 443.03 | 39 | [-0.1016,0.0236] |
| Momentum | USD040_TARGET_2R_BE1R | 6024 | 6024 | 0 | 41 | 1460 | 3222 | -0.0394 | -1.0000 | 0.9239 | 369.84 | 31 | [-0.0935,0.0163] |
| Momentum | ATR050_TARGET_1R | 6024 | 4125 | 1899 | 22 | 2048 | 2077 | -0.0068 | -1.0000 | 0.9866 | 107.09 | 31 | [-0.0515,0.0378] |
| Momentum | ATR050_TARGET_1.5R | 6024 | 4125 | 1899 | 7 | 1638 | 2487 | -0.0073 | -1.0000 | 0.9878 | 171.66 | 34 | [-0.0688,0.0522] |
| Momentum | ATR050_TARGET_2R | 6024 | 4125 | 1899 | 10 | 1345 | 2780 | -0.0226 | -1.0000 | 0.9664 | 237.35 | 42 | [-0.0910,0.0457] |
| Momentum | ATR050_TARGET_2R_BE1R | 6024 | 4125 | 1899 | 13 | 1008 | 2102 | -0.0168 | -1.0000 | 0.9666 | 191.29 | 31 | [-0.0728,0.0364] |

## Primary observations (descriptive only)

* Immediate Close-Back is less negative than the Momentum control for every natural-population model. Its largest gross differences occur for the BE1R variants; exact/common-identity paired estimates, paired CIs, and missing-partner attrition are in [immediate_momentum_comparisons.csv](./immediate_momentum_comparisons.csv). This is an association, not proof of entry superiority.
* The least-negative Immediate natural means are USD040_TARGET_2R_BE1R (+0.0218), USD040_TARGET_1.5R (+0.0144), ATR050_TARGET_1R (+0.0169), and USD030_TARGET_2R_BE1R (+0.0067). Their point estimates are small and bootstrap intervals include zero. No model is robustly positive across cost scenarios and ambiguity sensitivities.
* Applying $0.01 and $0.02 per-share round-trip scenarios shifts every executable mean downward by cost/risk. Results and both stop-first/target-first sensitivity are in [cost_sensitivity.csv](./cost_sensitivity.csv); these are SPY-equivalent underlying research costs, not 0DTE option costs.
* BE1R is causally next-minute only. The [breakeven_comparisons.csv](./breakeven_comparisons.csv) table shows the change from the otherwise identical TARGET_2R model; zero-R exits are not wins.
* ATR availability is materially incomplete but directionally similar (69.254% Immediate, 68.476% Momentum). Fixed-stop versus ATR comparisons are reported only on common available-ATR identities in [common_atr_comparisons.csv](./common_atr_comparisons.csv) and [common_atr_population_results.csv](./common_atr_population_results.csv).

## Robustness, context and ambiguity

Monthly means, month signs/counts, worst month, and leave-one-month-out minima are in [monthly_results.csv](./monthly_results.csv) and [leave_one_month_out.csv](./leave_one_month_out.csv). Direction, time-of-day, approach side, level family, interaction recurrence, breach history, and frozen confluence groups are descriptive tables in [direction_results.csv](./direction_results.csv) and [context_tables.csv](./context_tables.csv). PMH/PML rows are labeled `SPARSE_INSUFFICIENT`; no context group was used as a filter. Ambiguity counts are explicit in [ambiguity_sensitivity.csv](./ambiguity_sensitivity.csv); stop-first is primary and target-first is sensitivity only. Session-level rows retain zero-event sessions and support clustered bootstrap in [session_results.csv](./session_results.csv).

Across all 16 models, the natural Immediate population has **946** ambiguous outcomes and Momentum has **1,893** (the exact per-model counts are in the machine-readable table; counts are not added to executable denominators). The final run contains 77,088 STOP, 49,218 TARGET, 6,922 BREAKEVEN, 637 EOD, 96 TARGET_OPEN and 892 STOP_OPEN outcomes before ambiguity sensitivity expansion, plus 11,668 ATR-unavailable rows.

## What this study cannot conclude

This is not a trade backtest with a position constraint and does not establish live expectancy, option returns, execution quality, or deployability. Overlapping research events are not account-equity paths. Natural populations differ, ATR models have explicit attrition, and subgroup tables are not predeclared filters. Pointwise bootstrap intervals are unadjusted for the fixed matrix; no multiple-testing selection or ranking is performed. The development window is in-sample for future research, and no out-of-sample claim is made.

## Verification and isolation

The run used only the exact 170 development Parquet partitions, opened through a fail-closed allowlist and guarded file handles. Post–September 4 outcome partitions, September 8–December 1 prospective data, network services, Alpaca, and broker endpoints were not accessed. The kernel, protocol, and all prior frozen artifacts were read-only. Verification details and output hashes are in [verification_receipt.json](./verification_receipt.json) and [output_hashes.json](./output_hashes.json).
