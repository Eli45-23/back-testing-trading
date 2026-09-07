# 2026 V1 break-and-hold: entry-timing analysis

Analysis of the frozen Jan 1–Sep 4, 2026 canonical experiment. All dates/times use New York sessions. No V1 rules, thresholds, levels, raw data, or canonical outcomes were changed.

## Executive summary

The counts reconcile: **170 sessions, 1,435 breaks, 733 first holds, 524 strong holds**. There are **524 exact pairs** and **209 first holds that never become strong**. Excursion differences use **522 pairs with both EOD measurements available**; 2 pairs remain unavailable for that comparison.

Waiting costs **$0.2554 on average** in directional entry price. On complete pairs, it loses **$0.2876 mean remaining MFE** and changes mean MAE by **$-0.1912 of improvement** (negative means more adverse excursion). The complete-pair comparison does not support a blanket claim that a reduction in MAE pays for the later entry.

Strong confirmation also avoids a different population: 203/209 never-strong sequences close-reclaim. On the illustrative $0.50/$0.25 pair, 190 are adverse-first, but 11 are clean favorable-first over EOD and 8 achieve a clean favorable threshold before the reclaim. Calling all avoided events bad would misrepresent the sample.

The supported conclusion is a **selection-versus-delay tradeoff**, not a demonstrated universally superior entry. Whole-cohort hit rates mix different events; matched-event comparisons condition on eventual strong confirmation. Neither alone proves a deployable edge, causation, or realized expectancy.

## Definitions and verification

Verification details and test results: [verification record](break_hold_entry_timing_verification.md). Frozen analysis conventions: [analysis plan](break_hold_entry_timing_analysis_plan.md).
Canonical JSON SHA-256: `6aaf9980ecd7798420151a8b97436311eca6429e9f31fdb33be1ed86c8c47148`. V1 definition: `92b8c227e32c4fd43001da58fa0865fc61e868faa53c0bab2199c258e91f5f4d`. V1 input manifest: `2caffada233ed08d9cec0da158c46ae56b6874ab979cc2d9d54aec844bd8c8cd`.

- EOD MFE/MAE are remaining excursions from each original reference entry; pre-reclaim windows remain separate. Fixed-horizon records remain in each pair’s canonical outcome export.
- Entry disadvantage = direction sign × (strong price − first price). Better/worse use a fixed ±$0.01 tolerance; exact equality is also counted. Delay is strong-known-at minus first-known-at.
- MFE lost = first MFE − strong MFE. MAE improvement = first MAE − strong MAE. Both are calculated within the same complete pair, not by subtracting means with different availability.
- Reclaim is a completed-candle fact. No reclaim by EOD is censoring, not proof that a trade won. For a matched event, the reclaim close is identical; only the time remaining from each entry differs.
- The frozen strict future-minute-start rule remains unchanged: the minute starting exactly at signal completion is excluded. Consequently this is not an executable close-entry fill simulation.
- Small sample flags mean n<30 or fewer than 10 contributing sessions. These are descriptive subgroups without adjusted significance claims.

## 1. Exact paired comparisons


| Group | pairs | sessions | complete EOD pairs | entry disadvantage mean $ | Q25 $ | median $ | Q75 $ | better % | worse % | within 1¢ % | exact same n | delay mean min | delay median min |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 524 | 170 | 522 | 0.2554 | -0.0700 | 0.1800 | 0.5000 | 28.82% | 67.94% | 3.24% | 2 | 5.0000 | 5.0000 |
| LONG | 283 | 132 | 283 | 0.2306 | -0.0816 | 0.1400 | 0.4150 | 31.10% | 65.37% | 3.53% | 1 | 5.0000 | 5.0000 |
| SHORT | 241 | 114 | 239 | 0.2845 | -0.0200 | 0.2500 | 0.6100 | 26.14% | 70.95% | 2.90% | 1 | 5.0000 | 5.0000 |


| Group | complete EOD pairs | MFE lost mean $ | MFE lost median $ | MAE improvement mean $ | MAE improvement median $ | MAE improvement − MFE lost mean $ | MAE saving covers positive MFE loss |
|---|---|---|---|---|---|---|---|
| ALL | 522 | 0.2876 | 0.2150 | -0.1912 | -0.1300 | -0.4788 | 10/374 |
| LONG | 283 | 0.2627 | 0.1650 | -0.1635 | -0.0950 | -0.4262 | 4/194 |
| SHORT | 239 | 0.3171 | 0.2801 | -0.2240 | -0.2010 | -0.5411 | 6/180 |

The last two columns compare dollar excursion magnitudes only, with no risk preference or realized-payoff interpretation. Positive MAE improvement means less adverse excursion; a negative value means waiting worsened MAE.

| Group | first MFE mean $ | strong MFE mean $ | first MAE mean $ | strong MAE mean $ | first EOD move mean $ | strong EOD move mean $ |
|---|---|---|---|---|---|---|
| ALL | 2.8166 | 2.5289 | 2.3132 | 2.5044 | 0.3363 | 0.0791 |
| LONG | 2.5819 | 2.3192 | 2.4567 | 2.6203 | 0.1418 | -0.0888 |
| SHORT | 3.0944 | 2.7773 | 2.1434 | 2.3673 | 0.5666 | 0.2780 |


| Group | first mean MFE/MAE | strong mean MFE/MAE | first reclaims | strong reclaims | first reclaim delay median min | strong reclaim delay median min |
|---|---|---|---|---|---|---|
| ALL | 1.2176 | 1.0098 | 382 | 382 | 25.0000 | 20.0000 |
| LONG | 1.0510 | 0.8851 | 207 | 207 | 25.0000 | 20.0000 |
| SHORT | 1.4437 | 1.1732 | 175 | 175 | 25.0000 | 20.0000 |


### Every frozen threshold on matched events

Rates use all pairs, including ambiguity/no-data. “Lost clean” means favorable-first at first hold but not strong hold; “gained clean” is the reverse. Full categorical transition matrices and both hit timestamps are preserved in JSON.

| Direction | pair $ F/A | n | first clean % | strong clean % | strong − first pp | lost clean n | gained clean n |
|---|---|---|---|---|---|---|---|
| ALL | 0.25/0.25 | 524 | 61.07% | 51.72% | -9.35 | 139 | 90 |
| ALL | 0.50/0.25 | 524 | 50.19% | 38.36% | -11.83 | 134 | 72 |
| ALL | 0.75/0.25 | 524 | 39.89% | 29.77% | -10.11 | 110 | 57 |
| ALL | 1.00/0.25 | 524 | 33.97% | 23.28% | -10.69 | 101 | 45 |
| ALL | 0.50/0.30 | 524 | 54.01% | 40.27% | -13.74 | 138 | 66 |
| ALL | 0.75/0.30 | 524 | 43.32% | 31.68% | -11.64 | 114 | 53 |
| ALL | 1.00/0.30 | 524 | 37.21% | 25.38% | -11.83 | 104 | 42 |
| ALL | 1.50/0.30 | 524 | 26.91% | 18.32% | -8.59 | 75 | 30 |
| ALL | 2.00/0.30 | 524 | 21.18% | 12.98% | -8.21 | 65 | 22 |
| LONG | 0.25/0.25 | 283 | 59.01% | 51.94% | -7.07 | 73 | 53 |
| LONG | 0.50/0.25 | 283 | 45.94% | 38.16% | -7.77 | 62 | 40 |
| LONG | 0.75/0.25 | 283 | 36.04% | 28.98% | -7.07 | 51 | 31 |
| LONG | 1.00/0.25 | 283 | 30.74% | 23.32% | -7.42 | 48 | 27 |
| LONG | 0.50/0.30 | 283 | 50.53% | 40.28% | -10.25 | 63 | 34 |
| LONG | 0.75/0.30 | 283 | 40.28% | 31.45% | -8.83 | 52 | 27 |
| LONG | 1.00/0.30 | 283 | 34.63% | 26.15% | -8.48 | 49 | 25 |
| LONG | 1.50/0.30 | 283 | 24.38% | 19.43% | -4.95 | 34 | 20 |
| LONG | 2.00/0.30 | 283 | 18.37% | 13.78% | -4.59 | 29 | 16 |
| SHORT | 0.25/0.25 | 241 | 63.49% | 51.45% | -12.03 | 66 | 37 |
| SHORT | 0.50/0.25 | 241 | 55.19% | 38.59% | -16.60 | 72 | 32 |
| SHORT | 0.75/0.25 | 241 | 44.40% | 30.71% | -13.69 | 59 | 26 |
| SHORT | 1.00/0.25 | 241 | 37.76% | 23.24% | -14.52 | 53 | 18 |
| SHORT | 0.50/0.30 | 241 | 58.09% | 40.25% | -17.84 | 75 | 32 |
| SHORT | 0.75/0.30 | 241 | 46.89% | 31.95% | -14.94 | 62 | 26 |
| SHORT | 1.00/0.30 | 241 | 40.25% | 24.48% | -15.77 | 55 | 17 |
| SHORT | 1.50/0.30 | 241 | 29.88% | 17.01% | -12.86 | 41 | 10 |
| SHORT | 2.00/0.30 | 241 | 24.48% | 12.03% | -12.45 | 36 | 6 |


## 2. Whole cohorts and the avoided first holds


| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL_FIRST | 733 | 170 | 400/333 | 727 | 1.9900 | 2.6403 | 1.7701 | 2.5310 | 1.0432 | -0.0300 | 79.81% |
| ALL_STRONG | 524 | 170 | 283/241 | 522 | 1.8737 | 2.5289 | 1.7075 | 2.5044 | 1.0098 | 0.0350 | 72.90% |
| PAIRED_FIRST | 524 | 170 | 283/241 | 524 | 2.1325 | 2.8068 | 1.5000 | 2.3060 | 1.2171 | 0.1700 | 72.90% |
| NEVER_STRONG | 209 | 107 | 117/92 | 203 | 1.4300 | 2.2105 | 2.4350 | 3.1115 | 0.7104 | -0.5800 | 97.13% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| ALL_FIRST | 733 | 48.57% | 37.38% | 29.33% | 24.56% | 40.79% | 31.92% | 27.01% | 19.51% | 15.42% |
| ALL_STRONG | 524 | 51.72% | 38.36% | 29.77% | 23.28% | 40.27% | 31.68% | 25.38% | 18.32% | 12.98% |
| PAIRED_FIRST | 524 | 61.07% | 50.19% | 39.89% | 33.97% | 54.01% | 43.32% | 37.21% | 26.91% | 21.18% |
| NEVER_STRONG | 209 | 17.22% | 5.26% | 2.87% | 0.96% | 7.66% | 3.35% | 1.44% | 0.96% | 0.96% |


### Never-strong events by direction


| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LONG | 117 | 71 | 117/0 | 114 | 1.5975 | 2.3799 | 2.5270 | 3.1077 | 0.7658 | -0.5470 | 97.44% |
| SHORT | 92 | 69 | 0/92 | 89 | 0.8000 | 1.9935 | 2.2706 | 3.1165 | 0.6397 | -0.7900 | 96.74% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| LONG | 117 | 15.38% | 5.98% | 2.56% | 1.71% | 10.26% | 3.42% | 2.56% | 1.71% | 1.71% |
| SHORT | 92 | 19.57% | 4.35% | 3.26% | 0.00% | 4.35% | 3.26% | 0.00% | 0.00% | 0.00% |


| Cohort | n | reclaims | no reclaim by EOD | reclaim delay mean min | reclaim delay median min | pre-reclaim MFE mean $ | pre-reclaim MAE mean $ |
|---|---|---|---|---|---|---|---|
| ALL_FIRST | 733 | 585 | 148 | 33.3077 | 15.0000 | 1.4477 | 0.8524 |
| ALL_STRONG | 524 | 382 | 142 | 43.3508 | 20.0000 | 1.6140 | 1.0322 |
| PAIRED_FIRST | 524 | 382 | 142 | 48.3508 | 25.0000 | 1.9551 | 0.8467 |
| NEVER_STRONG | 209 | 203 | 6 | 5.0000 | 5.0000 | 0.1378 | 0.8672 |


### Were avoided events bad, or were good moves also lost?

“Adverse-first” is a threshold-specific bad-path proxy, not a universal trade-quality label. “Favorable touched before reclaim” can include an earlier adverse hit; “clean favorable before reclaim” cannot. Failure timing is known only at the reclaim close.

| Pair $ F/A | never-strong n | clean favorable EOD | adverse first | ambiguous | neither | no future | favorable touched before reclaim | clean favorable before reclaim |
|---|---|---|---|---|---|---|---|---|
| 0.25/0.25 | 209 | 36 | 159 | 8 | 0 | 6 | 44 | 34 |
| 0.50/0.25 | 209 | 11 | 190 | 2 | 0 | 6 | 11 | 8 |
| 0.75/0.25 | 209 | 6 | 197 | 0 | 0 | 6 | 4 | 4 |
| 1.00/0.25 | 209 | 2 | 200 | 0 | 1 | 6 | 1 | 1 |
| 0.50/0.30 | 209 | 16 | 187 | 0 | 0 | 6 | 11 | 10 |
| 0.75/0.30 | 209 | 7 | 196 | 0 | 0 | 6 | 4 | 4 |
| 1.00/0.30 | 209 | 3 | 199 | 0 | 1 | 6 | 1 | 1 |
| 1.50/0.30 | 209 | 2 | 200 | 0 | 1 | 6 | 0 | 0 |
| 2.00/0.30 | 209 | 2 | 200 | 0 | 1 | 6 | 0 | 0 |


## 3. Raw breaks that failed before first hold

Excursion beyond the opening boundary uses the failed break candle’s saved high/low, not an invented raw-break entry price. Delay is from the first crossing minute’s start to the failure-confirming close. The actual elapsed time lies approximately in (reported−1, reported] minutes; intraminute reclaim timing is unavailable. Groups use the raw crossing-minute time bucket.

| Group | raw breaks | failed | failure % | beyond level mean $ | median $ | Q25 $ | Q75 $ | failure delay mean min | median min |
|---|---|---|---|---|---|---|---|---|---|
| ALL | 1435 | 702 | 48.92% | 0.2206 | 0.1500 | 0.0600 | 0.2716 | 3.8519 | 4.0000 |
| LONG | 745 | 345 | 46.31% | 0.2139 | 0.1600 | 0.0700 | 0.2800 | 3.8029 | 4.0000 |
| SHORT | 690 | 357 | 51.74% | 0.2272 | 0.1450 | 0.0600 | 0.2600 | 3.8992 | 5.0000 |
| 09:35-10:00 | 403 | 185 | 45.91% | 0.2584 | 0.2100 | 0.0910 | 0.3300 | 3.9568 | 5.0000 |
| 10:00-10:30 | 217 | 117 | 53.92% | 0.2538 | 0.2050 | 0.0950 | 0.3200 | 3.9060 | 4.0000 |
| 10:30-11:00 | 145 | 68 | 46.90% | 0.1871 | 0.1400 | 0.0762 | 0.2612 | 3.6471 | 4.0000 |
| 11:00-12:00 | 176 | 80 | 45.45% | 0.1947 | 0.1700 | 0.0700 | 0.2600 | 3.9250 | 4.0000 |
| 12:00-13:30 | 205 | 95 | 46.34% | 0.1626 | 0.1177 | 0.0500 | 0.2250 | 3.7895 | 4.0000 |
| 13:30-15:00 | 170 | 97 | 57.06% | 0.1515 | 0.0900 | 0.0401 | 0.1900 | 3.8144 | 4.0000 |
| 15:00-close | 119 | 60 | 50.42% | 0.3156 | 0.1025 | 0.0350 | 0.2025 | 3.7167 | 4.0000 |

Waiting for first hold excludes these immediate close-failures by construction. That supports its confirmation role, but does **not** establish raw-break trading as inferior: V1 has no raw-break reference entry, adverse threshold path, costs, or exit policy for a like-for-like payoff comparison.

## 4. Time of day


### FIRST_HOLD


| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 09:35-10:00 | 192 | 151 | 106/86 | 192 | 2.4950 | 3.3023 | 2.7400 | 3.5567 | 0.9285 | -0.1150 | 83.85% |
| 10:00-10:30 | 112 | 84 | 60/52 | 112 | 2.3700 | 2.7875 | 2.3028 | 3.1041 | 0.8980 | 0.0750 | 83.04% |
| 10:30-11:00 | 72 | 54 | 39/33 | 72 | 2.6300 | 3.0748 | 1.9950 | 2.5157 | 1.2222 | -0.2138 | 87.50% |
| 11:00-12:00 | 105 | 64 | 67/38 | 105 | 1.7600 | 2.5318 | 1.8800 | 2.2077 | 1.1468 | 0.1600 | 80.95% |
| 12:00-13:30 | 118 | 62 | 65/53 | 118 | 1.9600 | 2.4677 | 1.3100 | 1.9312 | 1.2778 | 0.4198 | 79.66% |
| 13:30-15:00 | 67 | 49 | 32/35 | 67 | 1.1300 | 1.8975 | 1.1900 | 1.6795 | 1.1298 | -0.0590 | 77.61% |
| 15:00-close | 67 | 43 | 31/36 | 61 | 0.6650 | 1.1098 | 0.6300 | 0.9200 | 1.2062 | -0.1590 | 55.22% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| 09:35-10:00 | 192 | 44.27% | 35.42% | 27.08% | 25.52% | 38.54% | 29.69% | 28.12% | 22.92% | 20.83% |
| 10:00-10:30 | 112 | 48.21% | 35.71% | 29.46% | 23.21% | 38.39% | 31.25% | 25.00% | 17.86% | 14.29% |
| 10:30-11:00 | 72 | 47.22% | 38.89% | 29.17% | 23.61% | 38.89% | 29.17% | 23.61% | 16.67% | 11.11% |
| 11:00-12:00 | 105 | 52.38% | 41.90% | 30.48% | 28.57% | 45.71% | 34.29% | 32.38% | 20.95% | 16.19% |
| 12:00-13:30 | 118 | 48.31% | 37.29% | 30.51% | 25.42% | 42.37% | 34.75% | 29.66% | 23.73% | 16.10% |
| 13:30-15:00 | 67 | 56.72% | 40.30% | 35.82% | 25.37% | 43.28% | 37.31% | 26.87% | 14.93% | 10.45% |
| 15:00-close | 67 | 49.25% | 34.33% | 25.37% | 16.42% | 40.30% | 28.36% | 17.91% | 10.45% | 8.96% |


### STRONG_HOLD


| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 09:35-10:00 | 102 | 102 | 60/42 | 102 | 2.5275 | 3.1943 | 2.6300 | 3.7326 | 0.8558 | 0.0550 | 75.49% |
| 10:00-10:30 | 94 | 83 | 48/46 | 94 | 2.2196 | 2.8058 | 2.3300 | 3.0529 | 0.9191 | 0.5625 | 76.60% |
| 10:30-11:00 | 55 | 51 | 27/28 | 55 | 2.2900 | 2.7707 | 1.8200 | 2.5666 | 1.0795 | -0.4250 | 80.00% |
| 11:00-12:00 | 86 | 68 | 51/35 | 86 | 2.0400 | 2.5697 | 1.7300 | 2.1703 | 1.1840 | 0.0600 | 75.58% |
| 12:00-13:30 | 84 | 58 | 43/41 | 84 | 2.0200 | 2.4565 | 1.4375 | 1.9564 | 1.2556 | 0.4675 | 73.81% |
| 13:30-15:00 | 60 | 47 | 31/29 | 60 | 1.0700 | 1.8783 | 1.2100 | 1.8484 | 1.0162 | -0.2125 | 73.33% |
| 15:00-close | 43 | 36 | 23/20 | 41 | 0.7700 | 0.9297 | 0.6850 | 0.8921 | 1.0421 | -0.3200 | 41.86% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| 09:35-10:00 | 102 | 51.96% | 39.22% | 29.41% | 25.49% | 42.16% | 32.35% | 27.45% | 17.65% | 11.76% |
| 10:00-10:30 | 94 | 55.32% | 42.55% | 34.04% | 25.53% | 44.68% | 36.17% | 27.66% | 21.28% | 18.09% |
| 10:30-11:00 | 55 | 52.73% | 43.64% | 36.36% | 27.27% | 47.27% | 38.18% | 32.73% | 27.27% | 16.36% |
| 11:00-12:00 | 86 | 54.65% | 40.70% | 31.40% | 23.26% | 43.02% | 33.72% | 25.58% | 19.77% | 15.12% |
| 12:00-13:30 | 84 | 50.00% | 34.52% | 27.38% | 21.43% | 34.52% | 28.57% | 22.62% | 21.43% | 14.29% |
| 13:30-15:00 | 60 | 45.00% | 26.67% | 18.33% | 16.67% | 28.33% | 20.00% | 18.33% | 8.33% | 6.67% |
| 15:00-close | 43 | 48.84% | 39.53% | 30.23% | 20.93% | 39.53% | 30.23% | 20.93% | 6.98% | 2.33% |


## 5. Distance to next known key level

Buckets preserve the V1 inclusive upper boundaries: ≤$0.25, ($0.25,$0.50], ($0.50,$1], ($1,$1.50], ($1.50,$2], >$2, unavailable. Unavailable does not mean infinite room. All levels were already known at the respective entry. No filter is selected.

### FIRST_HOLD


| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| <=0.25 | 91 | 56 | 46/45 | 90 | 1.7012 | 2.5969 | 1.4400 | 1.9467 | 1.3340 | 0.2350 | 79.12% |
| <=0.50 | 65 | 42 | 30/35 | 65 | 2.0650 | 2.5997 | 1.4300 | 1.8868 | 1.3778 | -0.0600 | 81.54% |
| <=1.00 | 103 | 52 | 63/40 | 101 | 1.4501 | 2.2497 | 2.1600 | 3.1274 | 0.7193 | -0.5150 | 80.58% |
| <=1.50 | 77 | 51 | 35/42 | 76 | 2.1888 | 2.7297 | 2.2448 | 2.9900 | 0.9130 | -0.4400 | 72.73% |
| <=2.00 | 74 | 42 | 38/36 | 74 | 2.0800 | 2.5349 | 1.3000 | 2.6766 | 0.9471 | 0.8000 | 82.43% |
| >2.00 | 199 | 74 | 110/89 | 198 | 2.2876 | 3.0357 | 1.8850 | 2.7715 | 1.0953 | 0.3700 | 79.90% |
| UNAVAILABLE | 124 | 43 | 78/46 | 123 | 1.7600 | 2.3858 | 1.6950 | 2.0506 | 1.1635 | -0.1700 | 81.45% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| <=0.25 | 91 | 51.65% | 40.66% | 30.77% | 23.08% | 43.96% | 31.87% | 24.18% | 18.68% | 15.38% |
| <=0.50 | 65 | 43.08% | 33.85% | 27.69% | 23.08% | 38.46% | 33.85% | 27.69% | 16.92% | 13.85% |
| <=1.00 | 103 | 50.49% | 41.75% | 30.10% | 25.24% | 46.60% | 33.98% | 29.13% | 20.39% | 17.48% |
| <=1.50 | 77 | 48.05% | 36.36% | 32.47% | 28.57% | 40.26% | 35.06% | 31.17% | 28.57% | 22.08% |
| <=2.00 | 74 | 40.54% | 33.78% | 24.32% | 22.97% | 37.84% | 27.03% | 25.68% | 20.27% | 14.86% |
| >2.00 | 199 | 48.74% | 38.69% | 31.66% | 26.63% | 40.70% | 32.66% | 27.64% | 19.10% | 15.08% |
| UNAVAILABLE | 124 | 52.42% | 33.87% | 25.81% | 20.97% | 37.10% | 29.03% | 24.19% | 15.32% | 11.29% |


### STRONG_HOLD


| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| <=0.25 | 50 | 41 | 24/26 | 49 | 1.9724 | 2.5677 | 1.7050 | 2.0884 | 1.2295 | 0.2700 | 74.00% |
| <=0.50 | 46 | 32 | 26/20 | 46 | 1.7625 | 2.5986 | 1.3850 | 2.7201 | 0.9554 | 0.1625 | 69.57% |
| <=1.00 | 72 | 51 | 47/25 | 72 | 1.4202 | 1.9857 | 1.9956 | 2.7154 | 0.7313 | -0.5025 | 76.39% |
| <=1.50 | 51 | 40 | 21/30 | 51 | 1.9600 | 2.4608 | 1.5700 | 2.4957 | 0.9860 | -0.2100 | 62.75% |
| <=2.00 | 45 | 31 | 22/23 | 44 | 1.9425 | 2.5547 | 1.5900 | 2.2402 | 1.1404 | 0.6375 | 75.56% |
| >2.00 | 138 | 69 | 78/60 | 138 | 2.1600 | 2.7933 | 1.7450 | 2.6334 | 1.0607 | 0.0400 | 75.36% |
| UNAVAILABLE | 122 | 64 | 65/57 | 122 | 1.7922 | 2.5278 | 1.8750 | 2.4189 | 1.0450 | 0.1000 | 72.13% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| <=0.25 | 50 | 56.00% | 34.00% | 26.00% | 22.00% | 34.00% | 26.00% | 22.00% | 16.00% | 12.00% |
| <=0.50 | 46 | 52.17% | 45.65% | 36.96% | 32.61% | 50.00% | 39.13% | 34.78% | 23.91% | 21.74% |
| <=1.00 | 72 | 55.56% | 37.50% | 29.17% | 22.22% | 41.67% | 33.33% | 26.39% | 15.28% | 11.11% |
| <=1.50 | 51 | 58.82% | 47.06% | 43.14% | 37.25% | 47.06% | 43.14% | 37.25% | 23.53% | 11.76% |
| <=2.00 | 45 | 57.78% | 42.22% | 20.00% | 13.33% | 46.67% | 24.44% | 17.78% | 13.33% | 6.67% |
| >2.00 | 138 | 42.03% | 32.61% | 26.81% | 20.29% | 34.06% | 28.99% | 22.46% | 18.84% | 13.04% |
| UNAVAILABLE | 122 | 53.28% | 39.34% | 30.33% | 22.13% | 40.16% | 31.15% | 23.77% | 18.03% | 13.93% |


## 6. Opening-range width

Session-weighted width cutoffs (25th/50th/75th percentile): $1.0450, $1.3695, $1.7075. Session counts: {'Q3': 42, 'Q2': 42, 'Q1': 43, 'Q4': 43}. Equal widths stay together; no outcome is used to set a boundary.

### FIRST_HOLD


| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | 189 | 43 | 98/91 | 188 | 1.5000 | 1.9533 | 1.6350 | 2.2484 | 0.8688 | -0.1495 | 79.37% |
| Q2 | 193 | 42 | 110/83 | 190 | 1.6775 | 2.7926 | 1.7025 | 2.4442 | 1.1425 | -0.2162 | 81.87% |
| Q3 | 147 | 42 | 78/69 | 146 | 2.5225 | 3.0939 | 1.5175 | 2.1815 | 1.4182 | 1.0000 | 74.15% |
| Q4 | 204 | 43 | 114/90 | 203 | 2.1000 | 2.8078 | 2.5100 | 3.1252 | 0.8984 | -0.2800 | 82.35% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | 189 | 50.79% | 39.15% | 29.63% | 23.28% | 42.86% | 31.22% | 24.87% | 19.05% | 16.40% |
| Q2 | 193 | 45.60% | 32.12% | 25.39% | 21.76% | 34.72% | 26.94% | 22.80% | 16.58% | 13.47% |
| Q3 | 147 | 54.42% | 42.18% | 31.29% | 26.53% | 48.30% | 38.10% | 33.33% | 26.53% | 21.09% |
| Q4 | 204 | 45.10% | 37.25% | 31.37% | 26.96% | 39.22% | 32.84% | 28.43% | 17.65% | 12.25% |


### STRONG_HOLD


| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | 141 | 43 | 77/64 | 141 | 1.6100 | 1.9795 | 1.5950 | 2.1385 | 0.9256 | -0.0600 | 73.05% |
| Q2 | 129 | 42 | 75/54 | 129 | 1.7150 | 2.7710 | 1.3150 | 2.1227 | 1.3054 | -0.1000 | 75.19% |
| Q3 | 108 | 42 | 57/51 | 108 | 2.2850 | 2.7605 | 1.6675 | 2.2858 | 1.2076 | 0.5325 | 65.74% |
| Q4 | 146 | 43 | 74/72 | 144 | 2.1450 | 2.6765 | 2.3531 | 3.3687 | 0.7945 | -0.4175 | 76.03% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | 141 | 58.87% | 37.59% | 26.24% | 19.86% | 39.01% | 27.66% | 20.57% | 15.60% | 10.64% |
| Q2 | 129 | 47.29% | 34.88% | 31.78% | 27.13% | 37.98% | 34.11% | 29.46% | 17.05% | 12.40% |
| Q3 | 108 | 53.70% | 41.67% | 29.63% | 24.07% | 43.52% | 32.41% | 26.85% | 22.22% | 15.74% |
| Q4 | 146 | 47.26% | 39.73% | 31.51% | 22.60% | 41.10% | 32.88% | 25.34% | 19.18% | 13.70% |


## 7. First versus later break attempts


### FIRST_HOLD


| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FIRST_BREAK_ATTEMPT | 84 | 84 | 46/38 | 84 | 2.6050 | 3.4037 | 2.8500 | 3.8395 | 0.8865 | 0.3750 | 84.52% |
| LATER_BREAK_ATTEMPT | 649 | 157 | 354/295 | 643 | 1.9350 | 2.5406 | 1.6299 | 2.3600 | 1.0765 | -0.0500 | 79.20% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| FIRST_BREAK_ATTEMPT | 84 | 40.48% | 32.14% | 23.81% | 22.62% | 36.90% | 26.19% | 25.00% | 16.67% | 16.67% |
| LATER_BREAK_ATTEMPT | 649 | 49.61% | 38.06% | 30.05% | 24.81% | 41.29% | 32.67% | 27.27% | 19.88% | 15.25% |


### STRONG_HOLD


| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FIRST_BREAK_ATTEMPT | 56 | 56 | 32/24 | 56 | 2.4200 | 3.0954 | 2.8734 | 4.2535 | 0.7277 | -0.5550 | 76.79% |
| LATER_BREAK_ATTEMPT | 468 | 157 | 251/217 | 466 | 1.8025 | 2.4609 | 1.6075 | 2.2943 | 1.0726 | 0.0450 | 72.44% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| FIRST_BREAK_ATTEMPT | 56 | 57.14% | 44.64% | 32.14% | 26.79% | 48.21% | 35.71% | 28.57% | 21.43% | 12.50% |
| LATER_BREAK_ATTEMPT | 468 | 51.07% | 37.61% | 29.49% | 22.86% | 39.32% | 31.20% | 25.00% | 17.95% | 13.03% |


## 8. First versus later valid hold sequences

Rank refers to the originating first-hold sequence, even for its strong entry. This avoids labeling every strong entry “later” merely because its own first hold already occurred.

### FIRST_HOLD


| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FIRST_VALID_HOLD_SEQUENCE | 170 | 170 | 95/75 | 170 | 2.5775 | 3.2865 | 2.3250 | 3.3661 | 0.9764 | 0.3250 | 81.76% |
| LATER_VALID_HOLD_SEQUENCE | 563 | 138 | 305/258 | 557 | 1.7945 | 2.4431 | 1.5650 | 2.2761 | 1.0734 | -0.1000 | 79.22% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| FIRST_VALID_HOLD_SEQUENCE | 170 | 45.88% | 37.06% | 27.06% | 25.88% | 40.00% | 29.41% | 28.24% | 21.76% | 20.59% |
| LATER_VALID_HOLD_SEQUENCE | 563 | 49.38% | 37.48% | 30.02% | 24.16% | 41.03% | 32.68% | 26.64% | 18.83% | 13.85% |


### STRONG_HOLD


| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FIRST_VALID_HOLD_SEQUENCE | 119 | 119 | 69/50 | 119 | 2.4100 | 3.0257 | 2.4400 | 3.5119 | 0.8616 | 0.2850 | 73.95% |
| LATER_VALID_HOLD_SEQUENCE | 405 | 137 | 214/191 | 403 | 1.6500 | 2.3822 | 1.5900 | 2.2069 | 1.0794 | -0.0800 | 72.59% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| FIRST_VALID_HOLD_SEQUENCE | 119 | 55.46% | 41.18% | 31.93% | 26.05% | 44.54% | 35.29% | 28.57% | 21.01% | 15.13% |
| LATER_VALID_HOLD_SEQUENCE | 405 | 50.62% | 37.53% | 29.14% | 22.47% | 39.01% | 30.62% | 24.44% | 17.53% | 12.35% |


## 9. Opposite-boundary break context

This uses actual strict breaks and their canonical known-at times, not V1’s touch-before-event annotation. A first opposite break observed at the same confirmation close is separate from a previously completed opposite break; future daily both-sides status is never used.

### FIRST_HOLD


| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 491 | 124 | 267/224 | 487 | 1.8800 | 2.5286 | 1.5350 | 2.2355 | 1.1311 | 0.0200 | 78.00% |
| NO_OPPOSITE_BREAK_BY_SIGNAL | 233 | 123 | 125/108 | 231 | 2.3500 | 2.8670 | 2.1700 | 3.0618 | 0.9364 | -0.1700 | 83.26% |
| OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 9 | 9 | 8/1 | 9 | 2.2500 | 2.8648 | 2.9550 | 4.8952 | 0.5852 | -1.6400 | 88.89% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 491 | 50.71% | 39.31% | 31.77% | 25.25% | 42.77% | 34.22% | 27.49% | 20.37% | 14.87% |
| NO_OPPOSITE_BREAK_BY_SIGNAL | 233 | 44.21% | 33.05% | 24.03% | 22.75% | 36.48% | 27.04% | 25.75% | 17.17% | 16.31% |
| OPPOSITE_FIRST_OBSERVED_THIS_CLOSE | 9 | 44.44% | 44.44% | 33.33% | 33.33% | 44.44% | 33.33% | 33.33% | 33.33% | 22.22% |


### STRONG_HOLD


| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 365 | 124 | 199/166 | 364 | 1.6574 | 2.3871 | 1.5800 | 2.2788 | 1.0475 | 0.0250 | 71.23% |
| NO_OPPOSITE_BREAK_BY_SIGNAL | 159 | 101 | 84/75 | 158 | 2.3650 | 2.8556 | 2.1925 | 3.0243 | 0.9442 | 0.0550 | 76.73% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 365 | 50.68% | 38.36% | 29.59% | 23.01% | 40.27% | 31.51% | 25.21% | 17.81% | 12.33% |
| NO_OPPOSITE_BREAK_BY_SIGNAL | 159 | 54.09% | 38.36% | 30.19% | 23.90% | 40.25% | 32.08% | 25.79% | 19.50% | 14.47% |


## 10. Long versus short


### FIRST_HOLD


| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LONG | 400 | 137 | 400/0 | 397 | 1.8900 | 2.5239 | 2.0500 | 2.6437 | 0.9547 | -0.0500 | 80.25% |
| SHORT | 333 | 129 | 0/333 | 330 | 2.1589 | 2.7803 | 1.5300 | 2.3954 | 1.1607 | -0.0300 | 79.28% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| LONG | 400 | 46.25% | 34.25% | 26.25% | 22.25% | 38.75% | 29.50% | 25.25% | 17.75% | 13.50% |
| SHORT | 333 | 51.35% | 41.14% | 33.03% | 27.33% | 43.24% | 34.83% | 29.13% | 21.62% | 17.72% |


### STRONG_HOLD


| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LONG | 283 | 132 | 283/0 | 283 | 1.6350 | 2.3192 | 1.8763 | 2.6203 | 0.8851 | -0.1000 | 73.14% |
| SHORT | 241 | 114 | 0/241 | 239 | 2.2600 | 2.7773 | 1.5950 | 2.3673 | 1.1732 | 0.1700 | 72.61% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| LONG | 283 | 51.94% | 38.16% | 28.98% | 23.32% | 40.28% | 31.45% | 26.15% | 19.43% | 13.78% |
| SHORT | 241 | 51.45% | 38.59% | 30.71% | 23.24% | 40.25% | 31.95% | 24.48% | 17.01% | 12.03% |


## 11. Monthly robustness

September contains only September 1–4 and is a partial month. Contributing-session counts in cohort tables can differ from all calendar sessions shown below.

| Month | dataset sessions | first n | strong n |
|---|---|---|---|
| 2026-01 | 20 | 85 | 62 |
| 2026-02 | 19 | 74 | 58 |
| 2026-03 | 22 | 100 | 77 |
| 2026-04 | 21 | 95 | 66 |
| 2026-05 | 20 | 100 | 62 |
| 2026-06 | 21 | 79 | 56 |
| 2026-07 | 22 | 83 | 61 |
| 2026-08 | 21 | 104 | 75 |
| 2026-09 | 4 | 13 | 7 |


### FIRST_HOLD


| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-01 | 85 | 20 | 49/36 | 84 | 1.4925 | 2.1776 | 1.5900 | 2.3090 | 0.9431 | -0.2100 | 78.82% |
| 2026-02 | 74 | 19 | 46/28 | 74 | 2.2650 | 3.0180 | 1.8900 | 2.5700 | 1.1743 | 0.5550 | 77.03% |
| 2026-03 | 100 | 22 | 52/48 | 98 | 2.9475 | 3.5596 | 2.2875 | 3.1417 | 1.1330 | -0.0450 | 79.00% |
| 2026-04 | 95 | 21 | 54/41 | 94 | 1.4200 | 2.0390 | 1.8832 | 2.5214 | 0.8086 | -0.3700 | 82.11% |
| 2026-05 | 100 | 20 | 60/40 | 99 | 1.3500 | 1.8922 | 2.2600 | 2.5640 | 0.7380 | -1.1800 | 82.00% |
| 2026-06 | 79 | 21 | 46/33 | 79 | 3.3800 | 4.0565 | 1.3100 | 3.5432 | 1.1449 | 1.5887 | 77.22% |
| 2026-07 | 83 | 22 | 43/40 | 83 | 2.5300 | 3.0624 | 1.2501 | 2.3096 | 1.3259 | 0.4700 | 77.11% |
| 2026-08 | 104 | 21 | 42/62 | 103 | 1.3300 | 1.7914 | 1.1350 | 1.5790 | 1.1345 | 0.1500 | 83.65% |
| 2026-09 [SMALL] | 13 | 4 | 8/5 | 13 | 2.4700 | 2.0188 | 1.0100 | 1.7603 | 1.1469 | -0.5200 | 76.92% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-01 | 85 | 56.47% | 38.82% | 24.71% | 21.18% | 40.00% | 25.88% | 22.35% | 22.35% | 16.47% |
| 2026-02 | 74 | 47.30% | 37.84% | 31.08% | 17.57% | 40.54% | 32.43% | 18.92% | 16.22% | 12.16% |
| 2026-03 | 100 | 58.00% | 54.00% | 47.00% | 40.00% | 55.00% | 48.00% | 41.00% | 26.00% | 18.00% |
| 2026-04 | 95 | 44.21% | 33.68% | 24.21% | 17.89% | 42.11% | 30.53% | 24.21% | 17.89% | 15.79% |
| 2026-05 | 100 | 42.00% | 31.00% | 23.00% | 20.00% | 33.00% | 25.00% | 21.00% | 11.00% | 8.00% |
| 2026-06 | 79 | 46.84% | 37.97% | 34.18% | 31.65% | 41.77% | 36.71% | 34.18% | 25.32% | 18.99% |
| 2026-07 | 83 | 46.99% | 34.94% | 27.71% | 26.51% | 38.55% | 32.53% | 31.33% | 25.30% | 20.48% |
| 2026-08 | 104 | 46.15% | 30.77% | 22.12% | 19.23% | 35.58% | 24.04% | 21.15% | 12.50% | 12.50% |
| 2026-09 | 13 | 53.85% | 38.46% | 38.46% | 38.46% | 38.46% | 38.46% | 38.46% | 30.77% | 30.77% |


### STRONG_HOLD


| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-01 | 62 | 20 | 40/22 | 62 | 1.5150 | 2.1720 | 1.5900 | 1.9894 | 1.0918 | -0.1450 | 72.58% |
| 2026-02 | 58 | 19 | 35/23 | 58 | 2.2825 | 2.8261 | 2.0750 | 2.6740 | 1.0569 | 0.4800 | 70.69% |
| 2026-03 | 77 | 22 | 37/40 | 77 | 2.7200 | 3.2674 | 2.3900 | 3.2283 | 1.0121 | -0.2100 | 75.32% |
| 2026-04 | 66 | 21 | 39/27 | 66 | 1.3650 | 2.0110 | 1.7175 | 2.3051 | 0.8724 | 0.1375 | 75.76% |
| 2026-05 | 62 | 20 | 40/22 | 61 | 1.3500 | 1.9272 | 2.2200 | 2.3411 | 0.8232 | -0.6201 | 72.58% |
| 2026-06 | 56 | 21 | 28/28 | 56 | 2.9674 | 3.8244 | 1.6845 | 3.6805 | 1.0391 | 1.4975 | 67.86% |
| 2026-07 | 61 | 22 | 31/30 | 61 | 2.2400 | 2.6462 | 1.4100 | 2.5093 | 1.0546 | 0.1400 | 68.85% |
| 2026-08 | 75 | 21 | 29/46 | 74 | 1.2350 | 1.7272 | 1.1500 | 1.5969 | 1.0816 | 0.1500 | 78.67% |
| 2026-09 [SMALL] | 7 | 4 | 4/3 | 7 | 2.6300 | 2.3207 | 0.9100 | 1.1450 | 2.0268 | 1.4000 | 57.14% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-01 | 62 | 50.00% | 30.65% | 25.81% | 16.13% | 30.65% | 25.81% | 17.74% | 12.90% | 11.29% |
| 2026-02 | 58 | 39.66% | 18.97% | 17.24% | 13.79% | 20.69% | 18.97% | 17.24% | 12.07% | 8.62% |
| 2026-03 | 77 | 44.16% | 40.26% | 33.77% | 27.27% | 44.16% | 37.66% | 31.17% | 23.38% | 15.58% |
| 2026-04 | 66 | 54.55% | 42.42% | 28.79% | 21.21% | 45.45% | 31.82% | 24.24% | 15.15% | 12.12% |
| 2026-05 | 62 | 59.68% | 46.77% | 37.10% | 27.42% | 46.77% | 37.10% | 27.42% | 16.13% | 11.29% |
| 2026-06 | 56 | 57.14% | 53.57% | 37.50% | 32.14% | 53.57% | 37.50% | 32.14% | 30.36% | 17.86% |
| 2026-07 | 61 | 59.02% | 42.62% | 27.87% | 24.59% | 44.26% | 29.51% | 26.23% | 21.31% | 11.48% |
| 2026-08 | 75 | 50.67% | 30.67% | 26.67% | 20.00% | 34.67% | 30.67% | 22.67% | 13.33% | 12.00% |
| 2026-09 | 7 | 57.14% | 57.14% | 57.14% | 57.14% | 57.14% | 57.14% | 57.14% | 42.86% | 42.86% |


### Paired disadvantage and excursion tradeoff by month


| Group | pairs | sessions | complete EOD pairs | entry disadvantage mean $ | Q25 $ | median $ | Q75 $ | better % | worse % | within 1¢ % | exact same n | delay mean min | delay median min |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-01 | 62 | 20 | 62 | 0.3417 | 0.0062 | 0.2025 | 0.5075 | 22.58% | 72.58% | 4.84% | 0 | 5.0000 | 5.0000 |
| 2026-02 | 58 | 19 | 58 | 0.2341 | -0.0737 | 0.2025 | 0.4938 | 27.59% | 65.52% | 6.90% | 0 | 5.0000 | 5.0000 |
| 2026-03 | 77 | 22 | 77 | 0.4357 | 0.0900 | 0.4550 | 0.7300 | 19.48% | 77.92% | 2.60% | 1 | 5.0000 | 5.0000 |
| 2026-04 | 66 | 21 | 66 | 0.1832 | -0.0700 | 0.1450 | 0.3938 | 31.82% | 65.15% | 3.03% | 0 | 5.0000 | 5.0000 |
| 2026-05 | 62 | 20 | 61 | 0.1889 | -0.0900 | 0.1075 | 0.3700 | 32.26% | 64.52% | 3.23% | 0 | 5.0000 | 5.0000 |
| 2026-06 | 56 | 21 | 56 | 0.2983 | -0.2150 | 0.2300 | 0.6900 | 37.50% | 60.71% | 1.79% | 0 | 5.0000 | 5.0000 |
| 2026-07 | 61 | 22 | 61 | 0.2682 | -0.0700 | 0.2200 | 0.4500 | 27.87% | 70.49% | 1.64% | 0 | 5.0000 | 5.0000 |
| 2026-08 | 75 | 21 | 74 | 0.0750 | -0.0802 | 0.0800 | 0.2275 | 34.67% | 62.67% | 2.67% | 1 | 5.0000 | 5.0000 |
| 2026-09 | 7 | 4 | 7 | 0.4321 | 0.1350 | 0.2900 | 0.7025 | 14.29% | 85.71% | 0.00% | 0 | 5.0000 | 5.0000 |


| Group | complete EOD pairs | MFE lost mean $ | MFE lost median $ | MAE improvement mean $ | MAE improvement median $ | MAE improvement − MFE lost mean $ | MAE saving covers positive MFE loss |
|---|---|---|---|---|---|---|---|
| 2026-01 | 62 | 0.3572 | 0.2175 | -0.2455 | -0.1675 | -0.6028 | 0/47 |
| 2026-02 | 58 | 0.2933 | 0.3106 | -0.1737 | -0.0762 | -0.4669 | 0/43 |
| 2026-03 | 77 | 0.4798 | 0.5100 | -0.3707 | -0.4200 | -0.8505 | 3/63 |
| 2026-04 | 66 | 0.2111 | 0.1450 | -0.1180 | -0.1074 | -0.3291 | 2/46 |
| 2026-05 | 61 | 0.2301 | 0.1200 | -0.1488 | -0.1050 | -0.3790 | 3/43 |
| 2026-06 | 56 | 0.3342 | 0.2900 | -0.1899 | -0.0750 | -0.5241 | 0/35 |
| 2026-07 | 61 | 0.2905 | 0.2298 | -0.2241 | -0.1900 | -0.5147 | 1/43 |
| 2026-08 | 74 | 0.0892 | 0.0800 | -0.0479 | -0.0500 | -0.1370 | 1/48 |
| 2026-09 | 7 | 0.4321 | 0.2900 | -0.1787 | -0.1100 | -0.6108 | 0/6 |

The last two columns compare dollar excursion magnitudes only, with no risk preference or realized-payoff interpretation. Positive MAE improvement means less adverse excursion; a negative value means waiting worsened MAE.

| Group | first MFE mean $ | strong MFE mean $ | first MAE mean $ | strong MAE mean $ | first EOD move mean $ | strong EOD move mean $ |
|---|---|---|---|---|---|---|
| 2026-01 | 2.5292 | 2.1720 | 1.7439 | 1.9894 | 0.2304 | -0.1113 |
| 2026-02 | 3.1194 | 2.8261 | 2.5004 | 2.6740 | 0.6339 | 0.3998 |
| 2026-03 | 3.7472 | 3.2674 | 2.8576 | 3.2283 | 0.4715 | 0.0359 |
| 2026-04 | 2.2222 | 2.0110 | 2.1871 | 2.3051 | 0.0271 | -0.1561 |
| 2026-05 | 2.1574 | 1.9272 | 2.1922 | 2.3411 | -0.2764 | -0.4709 |
| 2026-06 | 4.1587 | 3.8244 | 3.4906 | 3.6805 | 0.8714 | 0.5731 |
| 2026-07 | 2.9368 | 2.6462 | 2.2852 | 2.5093 | 0.2838 | 0.0155 |
| 2026-08 | 1.8164 | 1.7272 | 1.5490 | 1.5969 | 0.3842 | 0.3044 |
| 2026-09 | 2.7529 | 2.3207 | 0.9663 | 1.1450 | 1.2486 | 0.8164 |


| Group | first mean MFE/MAE | strong mean MFE/MAE | first reclaims | strong reclaims | first reclaim delay median min | strong reclaim delay median min |
|---|---|---|---|---|---|---|
| 2026-01 | 1.4504 | 1.0918 | 45 | 45 | 20.0000 | 15.0000 |
| 2026-02 | 1.2476 | 1.0569 | 41 | 41 | 15.0000 | 10.0000 |
| 2026-03 | 1.3113 | 1.0121 | 58 | 58 | 30.0000 | 25.0000 |
| 2026-04 | 1.0160 | 0.8724 | 50 | 50 | 25.0000 | 20.0000 |
| 2026-05 | 0.9841 | 0.8232 | 45 | 45 | 25.0000 | 20.0000 |
| 2026-06 | 1.1914 | 1.0391 | 38 | 38 | 25.0000 | 20.0000 |
| 2026-07 | 1.2851 | 1.0546 | 42 | 42 | 25.0000 | 20.0000 |
| 2026-08 | 1.1726 | 1.0816 | 59 | 59 | 25.0000 | 20.0000 |
| 2026-09 | 2.8488 | 2.0268 | 4 | 4 | 32.5000 | 27.5000 |


| Month | pairs | first clean % .50/.25 | strong clean % .50/.25 |
|---|---|---|---|
| 2026-01 | 62 | 53.23% | 30.65% |
| 2026-02 | 58 | 44.83% | 18.97% |
| 2026-03 | 77 | 66.23% | 40.26% |
| 2026-04 | 66 | 46.97% | 42.42% |
| 2026-05 | 62 | 48.39% | 46.77% |
| 2026-06 | 56 | 50.00% | 53.57% |
| 2026-07 | 61 | 45.90% | 42.62% |
| 2026-08 | 75 | 41.33% | 30.67% |
| 2026-09 | 7 | 71.43% | 57.14% |


## 12. Session-bootstrap uncertainty

10,000 whole-session resamples with replacement; deterministic seed 20260906; percentile 95% intervals. All 170 session clusters are sampled. Estimates are event-weighted ratios of resampled cluster sums/counts. Pairs are never broken. LONG and SHORT use the same cluster draws. Intervals are pointwise exploratory intervals, not corrected for multiple comparisons, and do not justify selecting the best context.

Price/excursion differences are in dollars. Hit-rate differences are STRONG minus FIRST in percentage points; negative favors the first reference on matched events.

| Group | metric | n | contributing sessions | estimate | CI low | CI high | valid draws |
|---|---|---|---|---|---|---|---|
| ALL | entry_disadvantage | 524 | 170 | 0.2554 | 0.2065 | 0.3075 | 10000 |
| ALL | mfe_lost | 522 | 170 | 0.2876 | 0.2381 | 0.3406 | 10000 |
| ALL | mae_improvement | 522 | 170 | -0.1912 | -0.2350 | -0.1478 | 10000 |
| ALL | strong_minus_first_clean_0.25/0.25 | 524 | 170 | -9.3511 | -14.8938 | -3.4797 | 10000 |
| ALL | strong_minus_first_clean_0.50/0.25 | 524 | 170 | -11.8321 | -16.8933 | -6.5890 | 10000 |
| ALL | strong_minus_first_clean_0.75/0.25 | 524 | 170 | -10.1145 | -14.4405 | -5.5757 | 10000 |
| ALL | strong_minus_first_clean_1.00/0.25 | 524 | 170 | -10.6870 | -14.8307 | -6.4048 | 10000 |
| ALL | strong_minus_first_clean_0.50/0.30 | 524 | 170 | -13.7405 | -18.7381 | -8.5343 | 10000 |
| ALL | strong_minus_first_clean_0.75/0.30 | 524 | 170 | -11.6412 | -15.8763 | -7.2289 | 10000 |
| ALL | strong_minus_first_clean_1.00/0.30 | 524 | 170 | -11.8321 | -15.9223 | -7.5510 | 10000 |
| ALL | strong_minus_first_clean_1.50/0.30 | 524 | 170 | -8.5878 | -12.0373 | -5.0387 | 10000 |
| ALL | strong_minus_first_clean_2.00/0.30 | 524 | 170 | -8.2061 | -11.5914 | -4.8780 | 10000 |
| LONG | entry_disadvantage | 283 | 132 | 0.2306 | 0.1713 | 0.2938 | 10000 |
| LONG | mfe_lost | 283 | 132 | 0.2627 | 0.2040 | 0.3248 | 10000 |
| LONG | mae_improvement | 283 | 132 | -0.1635 | -0.2212 | -0.1095 | 10000 |
| LONG | strong_minus_first_clean_0.25/0.25 | 283 | 132 | -7.0671 | -14.6668 | 0.6946 | 10000 |
| LONG | strong_minus_first_clean_0.50/0.25 | 283 | 132 | -7.7739 | -15.1515 | -0.6873 | 10000 |
| LONG | strong_minus_first_clean_0.75/0.25 | 283 | 132 | -7.0671 | -13.3893 | -0.7967 | 10000 |
| LONG | strong_minus_first_clean_1.00/0.25 | 283 | 132 | -7.4205 | -13.3122 | -1.4235 | 10000 |
| LONG | strong_minus_first_clean_0.50/0.30 | 283 | 132 | -10.2473 | -16.9384 | -3.8596 | 10000 |
| LONG | strong_minus_first_clean_0.75/0.30 | 283 | 132 | -8.8339 | -14.6497 | -2.8674 | 10000 |
| LONG | strong_minus_first_clean_1.00/0.30 | 283 | 132 | -8.4806 | -14.1819 | -2.6615 | 10000 |
| LONG | strong_minus_first_clean_1.50/0.30 | 283 | 132 | -4.9470 | -10.1449 | 0.0000 | 10000 |
| LONG | strong_minus_first_clean_2.00/0.30 | 283 | 132 | -4.5936 | -9.3496 | 0.0000 | 10000 |
| SHORT | entry_disadvantage | 241 | 114 | 0.2845 | 0.2114 | 0.3602 | 10000 |
| SHORT | mfe_lost | 239 | 114 | 0.3171 | 0.2411 | 0.3978 | 10000 |
| SHORT | mae_improvement | 239 | 114 | -0.2240 | -0.2892 | -0.1586 | 10000 |
| SHORT | strong_minus_first_clean_0.25/0.25 | 241 | 114 | -12.0332 | -20.2382 | -3.7033 | 10000 |
| SHORT | strong_minus_first_clean_0.50/0.25 | 241 | 114 | -16.5975 | -24.2679 | -8.7117 | 10000 |
| SHORT | strong_minus_first_clean_0.75/0.25 | 241 | 114 | -13.6929 | -20.5024 | -6.6667 | 10000 |
| SHORT | strong_minus_first_clean_1.00/0.25 | 241 | 114 | -14.5228 | -20.8740 | -8.2602 | 10000 |
| SHORT | strong_minus_first_clean_0.50/0.30 | 241 | 114 | -17.8423 | -25.8065 | -9.4014 | 10000 |
| SHORT | strong_minus_first_clean_0.75/0.30 | 241 | 114 | -14.9378 | -22.2222 | -7.4074 | 10000 |
| SHORT | strong_minus_first_clean_1.00/0.30 | 241 | 114 | -15.7676 | -22.4809 | -9.2050 | 10000 |
| SHORT | strong_minus_first_clean_1.50/0.30 | 241 | 114 | -12.8631 | -17.6750 | -8.2303 | 10000 |
| SHORT | strong_minus_first_clean_2.00/0.30 | 241 | 114 | -12.4481 | -17.3081 | -7.8189 | 10000 |


## 13. Same-minute ambiguity sensitivity

The alternate denominator removes **only** AMBIGUOUS_SAME_BAR. It does not silently drop neither/no-future records. This sensitivity cannot recover the true intraminute order.

| Cohort | F/A $ | all n | ambiguous n | ambiguous % | clean/all % | nonambiguous n | clean/nonambiguous % |
|---|---|---|---|---|---|---|---|
| ALL_FIRST | 0.25/0.25 | 733 | 38 | 5.18% | 48.57% | 695 | 51.22% |
| ALL_FIRST | 0.50/0.25 | 733 | 8 | 1.09% | 37.38% | 725 | 37.79% |
| ALL_FIRST | 0.75/0.25 | 733 | 3 | 0.41% | 29.33% | 730 | 29.45% |
| ALL_FIRST | 1.00/0.25 | 733 | 2 | 0.27% | 24.56% | 731 | 24.62% |
| ALL_FIRST | 0.50/0.30 | 733 | 5 | 0.68% | 40.79% | 728 | 41.07% |
| ALL_FIRST | 0.75/0.30 | 733 | 3 | 0.41% | 31.92% | 730 | 32.05% |
| ALL_FIRST | 1.00/0.30 | 733 | 2 | 0.27% | 27.01% | 731 | 27.09% |
| ALL_FIRST | 1.50/0.30 | 733 | 0 | 0.00% | 19.51% | 733 | 19.51% |
| ALL_FIRST | 2.00/0.30 | 733 | 0 | 0.00% | 15.42% | 733 | 15.42% |
| ALL_STRONG | 0.25/0.25 | 524 | 25 | 4.77% | 51.72% | 499 | 54.31% |
| ALL_STRONG | 0.50/0.25 | 524 | 3 | 0.57% | 38.36% | 521 | 38.58% |
| ALL_STRONG | 0.75/0.25 | 524 | 2 | 0.38% | 29.77% | 522 | 29.89% |
| ALL_STRONG | 1.00/0.25 | 524 | 0 | 0.00% | 23.28% | 524 | 23.28% |
| ALL_STRONG | 0.50/0.30 | 524 | 2 | 0.38% | 40.27% | 522 | 40.42% |
| ALL_STRONG | 0.75/0.30 | 524 | 2 | 0.38% | 31.68% | 522 | 31.80% |
| ALL_STRONG | 1.00/0.30 | 524 | 0 | 0.00% | 25.38% | 524 | 25.38% |
| ALL_STRONG | 1.50/0.30 | 524 | 0 | 0.00% | 18.32% | 524 | 18.32% |
| ALL_STRONG | 2.00/0.30 | 524 | 0 | 0.00% | 12.98% | 524 | 12.98% |
| PAIRED_FIRST | 0.25/0.25 | 524 | 30 | 5.73% | 61.07% | 494 | 64.78% |
| PAIRED_FIRST | 0.50/0.25 | 524 | 6 | 1.15% | 50.19% | 518 | 50.77% |
| PAIRED_FIRST | 0.75/0.25 | 524 | 3 | 0.57% | 39.89% | 521 | 40.12% |
| PAIRED_FIRST | 1.00/0.25 | 524 | 2 | 0.38% | 33.97% | 522 | 34.10% |
| PAIRED_FIRST | 0.50/0.30 | 524 | 5 | 0.95% | 54.01% | 519 | 54.53% |
| PAIRED_FIRST | 0.75/0.30 | 524 | 3 | 0.57% | 43.32% | 521 | 43.57% |
| PAIRED_FIRST | 1.00/0.30 | 524 | 2 | 0.38% | 37.21% | 522 | 37.36% |
| PAIRED_FIRST | 1.50/0.30 | 524 | 0 | 0.00% | 26.91% | 524 | 26.91% |
| PAIRED_FIRST | 2.00/0.30 | 524 | 0 | 0.00% | 21.18% | 524 | 21.18% |
| NEVER_STRONG | 0.25/0.25 | 209 | 8 | 3.83% | 17.22% | 201 | 17.91% |
| NEVER_STRONG | 0.50/0.25 | 209 | 2 | 0.96% | 5.26% | 207 | 5.31% |
| NEVER_STRONG | 0.75/0.25 | 209 | 0 | 0.00% | 2.87% | 209 | 2.87% |
| NEVER_STRONG | 1.00/0.25 | 209 | 0 | 0.00% | 0.96% | 209 | 0.96% |
| NEVER_STRONG | 0.50/0.30 | 209 | 0 | 0.00% | 7.66% | 209 | 7.66% |
| NEVER_STRONG | 0.75/0.30 | 209 | 0 | 0.00% | 3.35% | 209 | 3.35% |
| NEVER_STRONG | 1.00/0.30 | 209 | 0 | 0.00% | 1.44% | 209 | 1.44% |
| NEVER_STRONG | 1.50/0.30 | 209 | 0 | 0.00% | 0.96% | 209 | 0.96% |
| NEVER_STRONG | 2.00/0.30 | 209 | 0 | 0.00% | 0.96% | 209 | 0.96% |


## 14. Outlier sensitivity

Primary observations are never removed. Trimmed means remove 10% from each event-distribution tail only for this diagnostic. Session concentration sums overlapping events’ MFE and is not additive trading profit. The largest-contribution-session omission is a sensitivity comparison only.

| Cohort | metric | n | mean | median | 10% trimmed mean | Q05 | Q25 | Q75 | Q95 |
|---|---|---|---|---|---|---|---|---|---|
| ALL_FIRST | mfe | 727 | 2.6403 | 1.9900 | 2.2407 | 0.0830 | 0.8200 | 3.7012 | 7.5170 |
| ALL_FIRST | mae | 727 | 2.5310 | 1.7701 | 2.0975 | 0.0930 | 0.7800 | 3.4475 | 7.2870 |
| ALL_STRONG | mfe | 522 | 2.5289 | 1.8737 | 2.1631 | 0.1705 | 0.8050 | 3.4800 | 6.9938 |
| ALL_STRONG | mae | 522 | 2.5044 | 1.7075 | 2.0318 | 0.0906 | 0.8302 | 3.3192 | 7.3024 |
| PAIRED_FIRST | mfe | 524 | 2.8068 | 2.1325 | 2.4303 | 0.3130 | 1.0700 | 3.8225 | 7.5085 |
| PAIRED_FIRST | mae | 524 | 2.3060 | 1.5000 | 1.8326 | 0.0000 | 0.5775 | 3.1588 | 7.1102 |
| NEVER_STRONG | mfe | 203 | 2.2105 | 1.4300 | 1.7040 | 0.0000 | 0.3300 | 3.2280 | 7.4530 |
| NEVER_STRONG | mae | 203 | 3.1115 | 2.4350 | 2.7843 | 0.5707 | 1.1775 | 4.1575 | 7.8705 |


### FIRST_HOLD: session contribution

Top five sessions contribute 11.08% of summed event MFE.

| Session | summed event MFE $ | share |
|---|---|---|
| 2026-06-11 | 61.3501 | 3.20% |
| 2026-06-17 | 39.6544 | 2.07% |
| 2026-01-21 | 39.6400 | 2.07% |
| 2026-03-19 | 36.5050 | 1.90% |
| 2026-05-21 | 35.5250 | 1.85% |

Sensitivity excluding only 2026-06-11: remaining n=719, mean MFE $2.5843, median $1.9775. Primary full-sample mean remains $2.6403.

### STRONG_HOLD: session contribution

Top five sessions contribute 11.72% of summed event MFE.

| Session | summed event MFE $ | share |
|---|---|---|
| 2026-01-21 | 35.3050 | 2.67% |
| 2026-03-19 | 34.1375 | 2.59% |
| 2026-06-17 | 29.2190 | 2.21% |
| 2026-06-10 | 28.4850 | 2.16% |
| 2026-06-11 | 27.5560 | 2.09% |

Sensitivity excluding only 2026-01-21: remaining n=517, mean MFE $2.4851, median $1.8600. Primary full-sample mean remains $2.5289.

## 15. Every fixed 20-session rolling window

All 151 windows are included, stepping one session at a time. Adjacent windows heavily overlap and are not independent tests. The selected .50/.25 pair is the predeclared V1 illustrative metric, not a window-specific selection. All nine pairs are retained in the analysis JSON.

| Start | End | style | n | EOD n | median MFE $ | median MAE $ | clean .50/.25 % |
|---|---|---|---|---|---|---|---|
| 2026-01-02 | 2026-01-30 | FIRST_HOLD | 85 | 84 | 1.4925 | 1.5900 | 38.82% |
| 2026-01-02 | 2026-01-30 | STRONG_HOLD | 62 | 62 | 1.5150 | 1.5900 | 30.65% |
| 2026-01-05 | 2026-02-02 | FIRST_HOLD | 84 | 83 | 1.5300 | 1.5600 | 36.90% |
| 2026-01-05 | 2026-02-02 | STRONG_HOLD | 61 | 61 | 1.5500 | 1.5850 | 27.87% |
| 2026-01-06 | 2026-02-03 | FIRST_HOLD | 82 | 82 | 1.6500 | 1.5900 | 37.80% |
| 2026-01-06 | 2026-02-03 | STRONG_HOLD | 59 | 59 | 1.6350 | 1.5950 | 30.51% |
| 2026-01-07 | 2026-02-04 | FIRST_HOLD | 84 | 84 | 1.6500 | 1.7381 | 36.90% |
| 2026-01-07 | 2026-02-04 | STRONG_HOLD | 61 | 61 | 1.6350 | 1.6200 | 26.23% |
| 2026-01-08 | 2026-02-05 | FIRST_HOLD | 85 | 85 | 1.5700 | 1.8250 | 36.47% |
| 2026-01-08 | 2026-02-05 | STRONG_HOLD | 62 | 62 | 1.6098 | 1.7725 | 25.81% |
| 2026-01-09 | 2026-02-06 | FIRST_HOLD | 79 | 79 | 2.0500 | 1.8400 | 40.51% |
| 2026-01-09 | 2026-02-06 | STRONG_HOLD | 57 | 57 | 1.9450 | 1.9762 | 28.07% |
| 2026-01-12 | 2026-02-09 | FIRST_HOLD | 76 | 76 | 2.0200 | 1.7881 | 42.11% |
| 2026-01-12 | 2026-02-09 | STRONG_HOLD | 55 | 55 | 1.8600 | 1.9600 | 29.09% |
| 2026-01-13 | 2026-02-10 | FIRST_HOLD | 85 | 85 | 2.0500 | 1.8250 | 42.35% |
| 2026-01-13 | 2026-02-10 | STRONG_HOLD | 61 | 61 | 1.9450 | 1.9600 | 26.23% |
| 2026-01-14 | 2026-02-11 | FIRST_HOLD | 85 | 85 | 2.0500 | 1.8250 | 41.18% |
| 2026-01-14 | 2026-02-11 | STRONG_HOLD | 61 | 61 | 1.9450 | 1.9600 | 24.59% |
| 2026-01-15 | 2026-02-12 | FIRST_HOLD | 82 | 82 | 2.0200 | 1.8875 | 40.24% |
| 2026-01-15 | 2026-02-12 | STRONG_HOLD | 59 | 59 | 1.9450 | 1.8200 | 22.03% |
| 2026-01-16 | 2026-02-13 | FIRST_HOLD | 80 | 80 | 2.1200 | 2.0631 | 38.75% |
| 2026-01-16 | 2026-02-13 | STRONG_HOLD | 60 | 60 | 1.9025 | 1.9881 | 23.33% |
| 2026-01-20 | 2026-02-17 | FIRST_HOLD | 85 | 85 | 2.3200 | 2.7800 | 36.47% |
| 2026-01-20 | 2026-02-17 | STRONG_HOLD | 62 | 62 | 2.1700 | 2.1862 | 24.19% |
| 2026-01-21 | 2026-02-18 | FIRST_HOLD | 82 | 82 | 2.3272 | 2.1631 | 37.80% |
| 2026-01-21 | 2026-02-18 | STRONG_HOLD | 61 | 61 | 2.1700 | 2.0462 | 26.23% |
| 2026-01-22 | 2026-02-19 | FIRST_HOLD | 85 | 85 | 1.9775 | 2.2562 | 38.82% |
| 2026-01-22 | 2026-02-19 | STRONG_HOLD | 64 | 64 | 1.6098 | 2.3831 | 23.44% |
| 2026-01-23 | 2026-02-20 | FIRST_HOLD | 81 | 81 | 2.0375 | 2.1700 | 38.27% |
| 2026-01-23 | 2026-02-20 | STRONG_HOLD | 61 | 61 | 1.6799 | 2.2400 | 22.95% |
| 2026-01-26 | 2026-02-23 | FIRST_HOLD | 75 | 75 | 2.3200 | 2.2562 | 41.33% |
| 2026-01-26 | 2026-02-23 | STRONG_HOLD | 58 | 58 | 2.0575 | 2.3831 | 20.69% |
| 2026-01-27 | 2026-02-24 | FIRST_HOLD | 75 | 75 | 2.3200 | 2.2562 | 41.33% |
| 2026-01-27 | 2026-02-24 | STRONG_HOLD | 58 | 58 | 2.1700 | 2.3831 | 22.41% |
| 2026-01-28 | 2026-02-25 | FIRST_HOLD | 76 | 76 | 2.3272 | 2.1631 | 40.79% |
| 2026-01-28 | 2026-02-25 | STRONG_HOLD | 59 | 59 | 2.1800 | 2.3262 | 23.73% |
| 2026-01-29 | 2026-02-26 | FIRST_HOLD | 76 | 76 | 2.3272 | 2.1631 | 40.79% |
| 2026-01-29 | 2026-02-26 | STRONG_HOLD | 59 | 59 | 2.2100 | 2.3262 | 23.73% |
| 2026-01-30 | 2026-02-27 | FIRST_HOLD | 82 | 82 | 2.1774 | 1.9350 | 39.02% |
| 2026-01-30 | 2026-02-27 | STRONG_HOLD | 63 | 63 | 2.2800 | 2.2400 | 20.63% |
| 2026-02-02 | 2026-03-02 | FIRST_HOLD | 75 | 75 | 2.3200 | 1.8800 | 38.67% |
| 2026-02-02 | 2026-03-02 | STRONG_HOLD | 59 | 59 | 2.2850 | 1.9100 | 18.64% |
| 2026-02-03 | 2026-03-03 | FIRST_HOLD | 76 | 76 | 2.3272 | 1.8900 | 39.47% |
| 2026-02-03 | 2026-03-03 | STRONG_HOLD | 60 | 60 | 2.3050 | 2.0750 | 18.33% |
| 2026-02-04 | 2026-03-04 | FIRST_HOLD | 77 | 77 | 2.2100 | 1.9700 | 40.26% |
| 2026-02-04 | 2026-03-04 | STRONG_HOLD | 61 | 61 | 2.2800 | 2.2400 | 16.39% |
| 2026-02-05 | 2026-03-05 | FIRST_HOLD | 78 | 78 | 2.2025 | 1.8900 | 39.74% |
| 2026-02-05 | 2026-03-05 | STRONG_HOLD | 61 | 61 | 2.2800 | 2.2400 | 21.31% |
| 2026-02-06 | 2026-03-06 | FIRST_HOLD | 80 | 80 | 2.1548 | 2.0350 | 40.00% |
| 2026-02-06 | 2026-03-06 | STRONG_HOLD | 60 | 60 | 2.2450 | 2.2650 | 21.67% |
| 2026-02-09 | 2026-03-09 | FIRST_HOLD | 81 | 81 | 2.1500 | 2.7800 | 40.74% |
| 2026-02-09 | 2026-03-09 | STRONG_HOLD | 61 | 61 | 2.1800 | 2.2900 | 22.95% |
| 2026-02-10 | 2026-03-10 | FIRST_HOLD | 87 | 87 | 2.0200 | 2.7400 | 43.68% |
| 2026-02-10 | 2026-03-10 | STRONG_HOLD | 66 | 66 | 1.8150 | 2.6009 | 24.24% |
| 2026-02-11 | 2026-03-11 | FIRST_HOLD | 81 | 81 | 2.0200 | 2.7400 | 44.44% |
| 2026-02-11 | 2026-03-11 | STRONG_HOLD | 62 | 62 | 1.8150 | 2.6785 | 27.42% |
| 2026-02-12 | 2026-03-12 | FIRST_HOLD | 86 | 86 | 2.0288 | 2.7350 | 46.51% |
| 2026-02-12 | 2026-03-12 | STRONG_HOLD | 66 | 66 | 2.1750 | 2.4700 | 27.27% |
| 2026-02-13 | 2026-03-13 | FIRST_HOLD | 88 | 88 | 2.0288 | 2.7350 | 47.73% |
| 2026-02-13 | 2026-03-13 | STRONG_HOLD | 68 | 68 | 2.1750 | 2.4700 | 27.94% |
| 2026-02-17 | 2026-03-16 | FIRST_HOLD | 86 | 85 | 2.0823 | 2.2600 | 51.16% |
| 2026-02-17 | 2026-03-16 | STRONG_HOLD | 66 | 66 | 2.2600 | 2.3500 | 28.79% |
| 2026-02-18 | 2026-03-17 | FIRST_HOLD | 84 | 83 | 1.9775 | 1.8800 | 51.19% |
| 2026-02-18 | 2026-03-17 | STRONG_HOLD | 66 | 66 | 2.0800 | 2.2650 | 30.30% |
| 2026-02-19 | 2026-03-18 | FIRST_HOLD | 86 | 85 | 1.9400 | 1.9000 | 48.84% |
| 2026-02-19 | 2026-03-18 | STRONG_HOLD | 66 | 66 | 2.2100 | 2.2200 | 28.79% |
| 2026-02-20 | 2026-03-19 | FIRST_HOLD | 83 | 82 | 2.1774 | 1.7250 | 51.81% |
| 2026-02-20 | 2026-03-19 | STRONG_HOLD | 65 | 65 | 2.5900 | 2.0300 | 33.85% |
| 2026-02-23 | 2026-03-20 | FIRST_HOLD | 84 | 83 | 2.1950 | 1.7300 | 52.38% |
| 2026-02-23 | 2026-03-20 | STRONG_HOLD | 65 | 65 | 2.5900 | 2.0300 | 35.38% |
| 2026-02-24 | 2026-03-23 | FIRST_HOLD | 88 | 86 | 2.1548 | 1.8850 | 51.14% |
| 2026-02-24 | 2026-03-23 | STRONG_HOLD | 68 | 68 | 2.5500 | 2.2200 | 35.29% |
| 2026-02-25 | 2026-03-24 | FIRST_HOLD | 94 | 92 | 2.2025 | 2.0988 | 50.00% |
| 2026-02-25 | 2026-03-24 | STRONG_HOLD | 71 | 71 | 2.5500 | 2.0500 | 35.21% |
| 2026-02-26 | 2026-03-25 | FIRST_HOLD | 95 | 93 | 2.4850 | 2.1500 | 49.47% |
| 2026-02-26 | 2026-03-25 | STRONG_HOLD | 73 | 73 | 2.5500 | 2.1500 | 34.25% |
| 2026-02-27 | 2026-03-26 | FIRST_HOLD | 99 | 97 | 2.3600 | 2.2600 | 50.51% |
| 2026-02-27 | 2026-03-26 | STRONG_HOLD | 75 | 75 | 2.5200 | 2.3100 | 36.00% |
| 2026-03-02 | 2026-03-27 | FIRST_HOLD | 96 | 94 | 2.8362 | 2.3450 | 53.12% |
| 2026-03-02 | 2026-03-27 | STRONG_HOLD | 74 | 74 | 2.5850 | 2.4150 | 39.19% |
| 2026-03-03 | 2026-03-30 | FIRST_HOLD | 96 | 94 | 2.8362 | 2.3450 | 53.12% |
| 2026-03-03 | 2026-03-30 | STRONG_HOLD | 74 | 74 | 2.5850 | 2.4150 | 40.54% |
| 2026-03-04 | 2026-03-31 | FIRST_HOLD | 97 | 95 | 2.8825 | 2.3150 | 53.61% |
| 2026-03-04 | 2026-03-31 | STRONG_HOLD | 74 | 74 | 2.5850 | 2.4150 | 41.89% |
| 2026-03-05 | 2026-04-01 | FIRST_HOLD | 98 | 96 | 2.8938 | 2.2875 | 51.02% |
| 2026-03-05 | 2026-04-01 | STRONG_HOLD | 74 | 74 | 2.6700 | 2.3850 | 43.24% |
| 2026-03-06 | 2026-04-02 | FIRST_HOLD | 95 | 93 | 2.8825 | 2.3150 | 50.53% |
| 2026-03-06 | 2026-04-02 | STRONG_HOLD | 72 | 72 | 2.5850 | 2.4150 | 40.28% |
| 2026-03-09 | 2026-04-06 | FIRST_HOLD | 92 | 90 | 2.9475 | 2.1146 | 51.09% |
| 2026-03-09 | 2026-04-06 | STRONG_HOLD | 71 | 71 | 2.6200 | 2.1500 | 40.85% |
| 2026-03-10 | 2026-04-07 | FIRST_HOLD | 93 | 91 | 2.9050 | 2.1301 | 51.61% |
| 2026-03-10 | 2026-04-07 | STRONG_HOLD | 72 | 72 | 2.5850 | 2.2362 | 44.44% |
| 2026-03-11 | 2026-04-08 | FIRST_HOLD | 91 | 89 | 2.9712 | 2.0675 | 48.35% |
| 2026-03-11 | 2026-04-08 | STRONG_HOLD | 70 | 70 | 2.6700 | 2.0250 | 42.86% |
| 2026-03-12 | 2026-04-09 | FIRST_HOLD | 94 | 92 | 2.9806 | 2.0150 | 46.81% |
| 2026-03-12 | 2026-04-09 | STRONG_HOLD | 71 | 71 | 2.7200 | 1.9830 | 39.44% |
| 2026-03-13 | 2026-04-10 | FIRST_HOLD | 92 | 90 | 2.7812 | 1.9725 | 44.57% |
| 2026-03-13 | 2026-04-10 | STRONG_HOLD | 69 | 69 | 2.5200 | 1.7400 | 40.58% |
| 2026-03-16 | 2026-04-13 | FIRST_HOLD | 91 | 89 | 2.6800 | 1.9750 | 41.76% |
| 2026-03-16 | 2026-04-13 | STRONG_HOLD | 67 | 67 | 2.5200 | 1.7400 | 41.79% |
| 2026-03-17 | 2026-04-14 | FIRST_HOLD | 86 | 85 | 2.6400 | 1.9750 | 40.70% |
| 2026-03-17 | 2026-04-14 | STRONG_HOLD | 63 | 63 | 2.5500 | 1.7050 | 42.86% |
| 2026-03-18 | 2026-04-15 | FIRST_HOLD | 83 | 82 | 3.0100 | 2.0675 | 42.17% |
| 2026-03-18 | 2026-04-15 | STRONG_HOLD | 61 | 61 | 2.8700 | 1.7400 | 44.26% |
| 2026-03-19 | 2026-04-16 | FIRST_HOLD | 88 | 87 | 2.6000 | 1.9750 | 40.91% |
| 2026-03-19 | 2026-04-16 | STRONG_HOLD | 68 | 68 | 2.3700 | 1.9104 | 42.65% |
| 2026-03-20 | 2026-04-17 | FIRST_HOLD | 82 | 81 | 2.4400 | 2.0550 | 40.24% |
| 2026-03-20 | 2026-04-17 | STRONG_HOLD | 62 | 62 | 2.2600 | 1.9104 | 41.94% |
| 2026-03-23 | 2026-04-20 | FIRST_HOLD | 88 | 87 | 2.1450 | 2.0550 | 39.77% |
| 2026-03-23 | 2026-04-20 | STRONG_HOLD | 66 | 66 | 2.0600 | 1.8928 | 40.91% |
| 2026-03-24 | 2026-04-21 | FIRST_HOLD | 87 | 87 | 2.1878 | 1.9750 | 40.23% |
| 2026-03-24 | 2026-04-21 | STRONG_HOLD | 64 | 64 | 2.0600 | 1.7650 | 43.75% |
| 2026-03-25 | 2026-04-22 | FIRST_HOLD | 85 | 85 | 2.0314 | 1.9191 | 40.00% |
| 2026-03-25 | 2026-04-22 | STRONG_HOLD | 63 | 63 | 1.9000 | 1.7050 | 42.86% |
| 2026-03-26 | 2026-04-23 | FIRST_HOLD | 84 | 84 | 2.0007 | 1.9327 | 40.48% |
| 2026-03-26 | 2026-04-23 | STRONG_HOLD | 62 | 62 | 1.7799 | 1.7650 | 46.77% |
| 2026-03-27 | 2026-04-24 | FIRST_HOLD | 83 | 83 | 2.0314 | 1.8963 | 38.55% |
| 2026-03-27 | 2026-04-24 | STRONG_HOLD | 60 | 60 | 1.8949 | 1.7225 | 45.00% |
| 2026-03-30 | 2026-04-27 | FIRST_HOLD | 85 | 85 | 1.6900 | 1.8230 | 36.47% |
| 2026-03-30 | 2026-04-27 | STRONG_HOLD | 60 | 60 | 1.5239 | 1.6725 | 43.33% |
| 2026-03-31 | 2026-04-28 | FIRST_HOLD | 87 | 87 | 1.4800 | 1.8963 | 34.48% |
| 2026-03-31 | 2026-04-28 | STRONG_HOLD | 61 | 61 | 1.4150 | 1.7050 | 42.62% |
| 2026-04-01 | 2026-04-29 | FIRST_HOLD | 91 | 90 | 1.4050 | 1.8832 | 32.97% |
| 2026-04-01 | 2026-04-29 | STRONG_HOLD | 63 | 63 | 1.3500 | 1.7300 | 41.27% |
| 2026-04-02 | 2026-04-30 | FIRST_HOLD | 91 | 90 | 1.4200 | 1.8832 | 35.16% |
| 2026-04-02 | 2026-04-30 | STRONG_HOLD | 64 | 64 | 1.3650 | 1.7175 | 42.19% |
| 2026-04-06 | 2026-05-01 | FIRST_HOLD | 95 | 93 | 1.4300 | 1.9499 | 35.79% |
| 2026-04-06 | 2026-05-01 | STRONG_HOLD | 65 | 65 | 1.3500 | 1.7400 | 44.62% |
| 2026-04-07 | 2026-05-04 | FIRST_HOLD | 91 | 89 | 1.5400 | 1.8963 | 35.16% |
| 2026-04-07 | 2026-05-04 | STRONG_HOLD | 62 | 62 | 1.4060 | 1.7175 | 43.55% |
| 2026-04-08 | 2026-05-05 | FIRST_HOLD | 88 | 86 | 1.4450 | 1.8138 | 34.09% |
| 2026-04-08 | 2026-05-05 | STRONG_HOLD | 60 | 60 | 1.4060 | 1.6725 | 40.00% |
| 2026-04-09 | 2026-05-06 | FIRST_HOLD | 84 | 82 | 1.3975 | 1.8650 | 34.52% |
| 2026-04-09 | 2026-05-06 | STRONG_HOLD | 57 | 57 | 1.3850 | 1.6600 | 42.11% |
| 2026-04-10 | 2026-05-07 | FIRST_HOLD | 81 | 79 | 1.3950 | 1.8963 | 37.04% |
| 2026-04-10 | 2026-05-07 | STRONG_HOLD | 57 | 57 | 1.3500 | 1.7300 | 45.61% |
| 2026-04-13 | 2026-05-08 | FIRST_HOLD | 78 | 76 | 1.3875 | 1.8982 | 38.46% |
| 2026-04-13 | 2026-05-08 | STRONG_HOLD | 55 | 55 | 1.2100 | 1.7400 | 47.27% |
| 2026-04-14 | 2026-05-11 | FIRST_HOLD | 77 | 75 | 1.3950 | 1.8963 | 40.26% |
| 2026-04-14 | 2026-05-11 | STRONG_HOLD | 55 | 55 | 1.2100 | 1.7400 | 45.45% |
| 2026-04-15 | 2026-05-12 | FIRST_HOLD | 83 | 81 | 1.3800 | 1.9500 | 37.35% |
| 2026-04-15 | 2026-05-12 | STRONG_HOLD | 58 | 58 | 1.1300 | 1.8332 | 48.28% |
| 2026-04-16 | 2026-05-13 | FIRST_HOLD | 83 | 81 | 1.3800 | 1.9463 | 37.35% |
| 2026-04-16 | 2026-05-13 | STRONG_HOLD | 58 | 58 | 1.2800 | 1.8332 | 48.28% |
| 2026-04-17 | 2026-05-14 | FIRST_HOLD | 75 | 73 | 1.6300 | 1.9000 | 40.00% |
| 2026-04-17 | 2026-05-14 | STRONG_HOLD | 51 | 51 | 1.4150 | 1.3150 | 50.98% |
| 2026-04-20 | 2026-05-15 | FIRST_HOLD | 81 | 79 | 1.4100 | 2.0500 | 35.80% |
| 2026-04-20 | 2026-05-15 | STRONG_HOLD | 53 | 52 | 1.3975 | 1.6950 | 49.06% |
| 2026-04-21 | 2026-05-18 | FIRST_HOLD | 78 | 76 | 1.4450 | 2.0800 | 35.90% |
| 2026-04-21 | 2026-05-18 | STRONG_HOLD | 50 | 49 | 1.6700 | 1.7400 | 50.00% |
| 2026-04-22 | 2026-05-19 | FIRST_HOLD | 81 | 79 | 1.5400 | 2.1010 | 34.57% |
| 2026-04-22 | 2026-05-19 | STRONG_HOLD | 53 | 52 | 1.5425 | 2.3450 | 49.06% |
| 2026-04-23 | 2026-05-20 | FIRST_HOLD | 80 | 78 | 1.4100 | 2.4800 | 35.00% |
| 2026-04-23 | 2026-05-20 | STRONG_HOLD | 51 | 50 | 1.4125 | 2.5025 | 50.98% |
| 2026-04-24 | 2026-05-21 | FIRST_HOLD | 84 | 82 | 1.4450 | 2.1600 | 34.52% |
| 2026-04-24 | 2026-05-21 | STRONG_HOLD | 52 | 51 | 1.4150 | 2.2100 | 50.00% |
| 2026-04-27 | 2026-05-22 | FIRST_HOLD | 95 | 93 | 1.4000 | 2.4350 | 30.53% |
| 2026-04-27 | 2026-05-22 | STRONG_HOLD | 58 | 57 | 1.3850 | 2.5300 | 48.28% |
| 2026-04-28 | 2026-05-26 | FIRST_HOLD | 97 | 95 | 1.3800 | 2.4250 | 30.93% |
| 2026-04-28 | 2026-05-26 | STRONG_HOLD | 60 | 59 | 1.3200 | 2.5300 | 46.67% |
| 2026-04-29 | 2026-05-27 | FIRST_HOLD | 99 | 97 | 1.4000 | 2.2600 | 32.32% |
| 2026-04-29 | 2026-05-27 | STRONG_HOLD | 62 | 61 | 1.3850 | 2.4800 | 46.77% |
| 2026-04-30 | 2026-05-28 | FIRST_HOLD | 95 | 94 | 1.4300 | 2.4200 | 31.58% |
| 2026-04-30 | 2026-05-28 | STRONG_HOLD | 59 | 58 | 1.4666 | 2.2650 | 47.46% |
| 2026-05-01 | 2026-05-29 | FIRST_HOLD | 100 | 99 | 1.3500 | 2.2600 | 31.00% |
| 2026-05-01 | 2026-05-29 | STRONG_HOLD | 62 | 61 | 1.3500 | 2.2200 | 46.77% |
| 2026-05-04 | 2026-06-01 | FIRST_HOLD | 98 | 98 | 1.3650 | 2.2950 | 29.59% |
| 2026-05-04 | 2026-06-01 | STRONG_HOLD | 61 | 60 | 1.4000 | 1.9050 | 47.54% |
| 2026-05-05 | 2026-06-02 | FIRST_HOLD | 97 | 97 | 1.3700 | 2.2400 | 29.90% |
| 2026-05-05 | 2026-06-02 | STRONG_HOLD | 60 | 59 | 1.4100 | 1.6700 | 51.67% |
| 2026-05-06 | 2026-06-03 | FIRST_HOLD | 96 | 96 | 1.3650 | 2.2500 | 30.21% |
| 2026-05-06 | 2026-06-03 | STRONG_HOLD | 59 | 58 | 1.4000 | 1.7400 | 52.54% |
| 2026-05-07 | 2026-06-04 | FIRST_HOLD | 97 | 97 | 1.3700 | 2.2400 | 29.90% |
| 2026-05-07 | 2026-06-04 | STRONG_HOLD | 59 | 58 | 1.4000 | 1.7400 | 54.24% |
| 2026-05-08 | 2026-06-05 | FIRST_HOLD | 94 | 94 | 1.3850 | 2.1900 | 28.72% |
| 2026-05-08 | 2026-06-05 | STRONG_HOLD | 56 | 55 | 1.4100 | 1.5699 | 55.36% |
| 2026-05-11 | 2026-06-08 | FIRST_HOLD | 99 | 99 | 1.4100 | 2.2600 | 28.28% |
| 2026-05-11 | 2026-06-08 | STRONG_HOLD | 60 | 59 | 1.5231 | 1.6900 | 51.67% |
| 2026-05-12 | 2026-06-09 | FIRST_HOLD | 100 | 100 | 1.4300 | 2.2950 | 29.00% |
| 2026-05-12 | 2026-06-09 | STRONG_HOLD | 61 | 60 | 1.5316 | 1.9050 | 54.10% |
| 2026-05-13 | 2026-06-10 | FIRST_HOLD | 99 | 99 | 1.5100 | 2.0900 | 31.31% |
| 2026-05-13 | 2026-06-10 | STRONG_HOLD | 63 | 62 | 1.8550 | 1.7700 | 50.79% |
| 2026-05-14 | 2026-06-11 | FIRST_HOLD | 104 | 104 | 1.5550 | 2.2950 | 30.77% |
| 2026-05-14 | 2026-06-11 | STRONG_HOLD | 66 | 65 | 1.8850 | 1.8100 | 48.48% |
| 2026-05-15 | 2026-06-12 | FIRST_HOLD | 111 | 111 | 1.5500 | 2.3300 | 31.53% |
| 2026-05-15 | 2026-06-12 | STRONG_HOLD | 69 | 68 | 1.6975 | 1.9050 | 49.28% |
| 2026-05-18 | 2026-06-15 | FIRST_HOLD | 108 | 108 | 1.8300 | 2.0600 | 32.41% |
| 2026-05-18 | 2026-06-15 | STRONG_HOLD | 68 | 68 | 1.9025 | 1.7700 | 50.00% |
| 2026-05-19 | 2026-06-16 | FIRST_HOLD | 105 | 105 | 1.8500 | 1.9100 | 31.43% |
| 2026-05-19 | 2026-06-16 | STRONG_HOLD | 67 | 67 | 1.9200 | 1.7500 | 49.25% |
| 2026-05-20 | 2026-06-17 | FIRST_HOLD | 105 | 105 | 1.8899 | 1.8900 | 32.38% |
| 2026-05-20 | 2026-06-17 | STRONG_HOLD | 66 | 66 | 2.0800 | 1.6925 | 46.97% |
| 2026-05-21 | 2026-06-18 | FIRST_HOLD | 105 | 105 | 1.7800 | 1.9100 | 31.43% |
| 2026-05-21 | 2026-06-18 | STRONG_HOLD | 68 | 68 | 1.9025 | 1.7700 | 44.12% |
| 2026-05-22 | 2026-06-22 | FIRST_HOLD | 102 | 102 | 1.5550 | 2.0600 | 30.39% |
| 2026-05-22 | 2026-06-22 | STRONG_HOLD | 66 | 66 | 1.6975 | 1.8000 | 43.94% |
| 2026-05-26 | 2026-06-23 | FIRST_HOLD | 90 | 90 | 1.9450 | 1.5950 | 33.33% |
| 2026-05-26 | 2026-06-23 | STRONG_HOLD | 62 | 62 | 2.0000 | 1.6845 | 45.16% |
| 2026-05-27 | 2026-06-24 | FIRST_HOLD | 86 | 86 | 2.6350 | 1.3450 | 34.88% |
| 2026-05-27 | 2026-06-24 | STRONG_HOLD | 59 | 59 | 2.2100 | 1.5900 | 50.85% |
| 2026-05-28 | 2026-06-25 | FIRST_HOLD | 83 | 83 | 2.8800 | 1.4800 | 34.94% |
| 2026-05-28 | 2026-06-25 | STRONG_HOLD | 57 | 57 | 2.5700 | 1.6790 | 50.88% |
| 2026-05-29 | 2026-06-26 | FIRST_HOLD | 81 | 81 | 2.9800 | 1.4800 | 37.04% |
| 2026-05-29 | 2026-06-26 | STRONG_HOLD | 57 | 57 | 2.7800 | 1.6900 | 52.63% |
| 2026-06-01 | 2026-06-29 | FIRST_HOLD | 78 | 78 | 3.2050 | 1.3250 | 37.18% |
| 2026-06-01 | 2026-06-29 | STRONG_HOLD | 55 | 55 | 2.9599 | 1.6900 | 52.73% |
| 2026-06-02 | 2026-06-30 | FIRST_HOLD | 75 | 75 | 2.9800 | 1.4800 | 40.00% |
| 2026-06-02 | 2026-06-30 | STRONG_HOLD | 54 | 54 | 2.8700 | 1.6925 | 51.85% |
| 2026-06-03 | 2026-07-01 | FIRST_HOLD | 74 | 74 | 3.2050 | 1.7850 | 37.84% |
| 2026-06-03 | 2026-07-01 | STRONG_HOLD | 53 | 53 | 2.9750 | 1.6950 | 50.94% |
| 2026-06-04 | 2026-07-02 | FIRST_HOLD | 77 | 77 | 3.3800 | 1.4800 | 37.66% |
| 2026-06-04 | 2026-07-02 | STRONG_HOLD | 54 | 54 | 2.9825 | 1.7225 | 50.00% |
| 2026-06-05 | 2026-07-06 | FIRST_HOLD | 76 | 76 | 3.0050 | 1.7850 | 39.47% |
| 2026-06-05 | 2026-07-06 | STRONG_HOLD | 54 | 54 | 2.8775 | 1.7225 | 48.15% |
| 2026-06-08 | 2026-07-07 | FIRST_HOLD | 76 | 76 | 3.0050 | 1.7850 | 39.47% |
| 2026-06-08 | 2026-07-07 | STRONG_HOLD | 54 | 54 | 2.8775 | 1.7225 | 46.30% |
| 2026-06-09 | 2026-07-08 | FIRST_HOLD | 74 | 74 | 2.8450 | 1.7850 | 39.19% |
| 2026-06-09 | 2026-07-08 | STRONG_HOLD | 51 | 51 | 2.7800 | 1.6950 | 49.02% |
| 2026-06-10 | 2026-07-09 | FIRST_HOLD | 74 | 74 | 2.9208 | 1.7850 | 36.49% |
| 2026-06-10 | 2026-07-09 | STRONG_HOLD | 51 | 51 | 2.9300 | 1.6790 | 47.06% |
| 2026-06-11 | 2026-07-10 | FIRST_HOLD | 73 | 73 | 2.6750 | 2.2706 | 34.25% |
| 2026-06-11 | 2026-07-10 | STRONG_HOLD | 50 | 50 | 2.5075 | 1.6345 | 48.00% |
| 2026-06-12 | 2026-07-13 | FIRST_HOLD | 69 | 69 | 2.6750 | 1.3100 | 36.23% |
| 2026-06-12 | 2026-07-13 | STRONG_HOLD | 48 | 48 | 2.6225 | 1.5200 | 50.00% |
| 2026-06-15 | 2026-07-14 | FIRST_HOLD | 65 | 65 | 2.7600 | 1.3700 | 33.85% |
| 2026-06-15 | 2026-07-14 | STRONG_HOLD | 48 | 48 | 2.6225 | 1.5425 | 45.83% |
| 2026-06-16 | 2026-07-15 | FIRST_HOLD | 66 | 66 | 2.6675 | 1.5350 | 34.85% |
| 2026-06-16 | 2026-07-15 | STRONG_HOLD | 49 | 49 | 2.5350 | 1.5300 | 46.94% |
| 2026-06-17 | 2026-07-16 | FIRST_HOLD | 72 | 72 | 2.7175 | 1.5350 | 33.33% |
| 2026-06-17 | 2026-07-16 | STRONG_HOLD | 54 | 54 | 2.6225 | 1.5425 | 44.44% |
| 2026-06-18 | 2026-07-17 | FIRST_HOLD | 67 | 67 | 2.6750 | 1.3280 | 32.84% |
| 2026-06-18 | 2026-07-17 | STRONG_HOLD | 52 | 52 | 2.5075 | 1.5425 | 48.08% |
| 2026-06-22 | 2026-07-20 | FIRST_HOLD | 66 | 66 | 2.8000 | 1.2900 | 36.36% |
| 2026-06-22 | 2026-07-20 | STRONG_HOLD | 52 | 52 | 2.7400 | 1.4950 | 50.00% |
| 2026-06-23 | 2026-07-21 | FIRST_HOLD | 67 | 67 | 2.7600 | 1.1150 | 37.31% |
| 2026-06-23 | 2026-07-21 | STRONG_HOLD | 53 | 53 | 2.5350 | 1.4800 | 49.06% |
| 2026-06-24 | 2026-07-22 | FIRST_HOLD | 67 | 67 | 2.6750 | 1.0800 | 38.81% |
| 2026-06-24 | 2026-07-22 | STRONG_HOLD | 53 | 53 | 2.4800 | 1.3901 | 50.94% |
| 2026-06-25 | 2026-07-23 | FIRST_HOLD | 68 | 68 | 2.6000 | 1.0900 | 36.76% |
| 2026-06-25 | 2026-07-23 | STRONG_HOLD | 54 | 54 | 2.4700 | 1.3600 | 46.30% |
| 2026-06-26 | 2026-07-24 | FIRST_HOLD | 73 | 73 | 2.5400 | 1.1150 | 32.88% |
| 2026-06-26 | 2026-07-24 | STRONG_HOLD | 56 | 56 | 2.2800 | 1.4000 | 44.64% |
| 2026-06-29 | 2026-07-27 | FIRST_HOLD | 73 | 73 | 2.5400 | 1.1000 | 31.51% |
| 2026-06-29 | 2026-07-27 | STRONG_HOLD | 56 | 56 | 2.2800 | 1.3600 | 42.86% |
| 2026-06-30 | 2026-07-28 | FIRST_HOLD | 69 | 69 | 2.3900 | 1.1150 | 31.88% |
| 2026-06-30 | 2026-07-28 | STRONG_HOLD | 54 | 54 | 2.2050 | 1.3600 | 44.44% |
| 2026-07-01 | 2026-07-29 | FIRST_HOLD | 72 | 72 | 2.4400 | 1.2126 | 33.33% |
| 2026-07-01 | 2026-07-29 | STRONG_HOLD | 56 | 56 | 2.2050 | 1.4000 | 42.86% |
| 2026-07-02 | 2026-07-30 | FIRST_HOLD | 76 | 76 | 2.4400 | 1.3190 | 34.21% |
| 2026-07-02 | 2026-07-30 | STRONG_HOLD | 57 | 57 | 2.2400 | 1.4100 | 42.11% |
| 2026-07-06 | 2026-07-31 | FIRST_HOLD | 78 | 78 | 2.4400 | 1.2800 | 34.62% |
| 2026-07-06 | 2026-07-31 | STRONG_HOLD | 58 | 58 | 2.2050 | 1.4400 | 41.38% |
| 2026-07-07 | 2026-08-03 | FIRST_HOLD | 78 | 78 | 2.4400 | 1.2800 | 33.33% |
| 2026-07-07 | 2026-08-03 | STRONG_HOLD | 58 | 58 | 2.2050 | 1.4400 | 43.10% |
| 2026-07-08 | 2026-08-04 | FIRST_HOLD | 79 | 79 | 2.4900 | 1.2501 | 32.91% |
| 2026-07-08 | 2026-08-04 | STRONG_HOLD | 58 | 58 | 2.2050 | 1.4400 | 43.10% |
| 2026-07-09 | 2026-08-05 | FIRST_HOLD | 76 | 76 | 2.5425 | 1.1750 | 34.21% |
| 2026-07-09 | 2026-08-05 | STRONG_HOLD | 57 | 57 | 2.2400 | 1.4100 | 43.86% |
| 2026-07-10 | 2026-08-06 | FIRST_HOLD | 82 | 82 | 2.3375 | 1.2126 | 32.93% |
| 2026-07-10 | 2026-08-06 | STRONG_HOLD | 61 | 61 | 1.9000 | 1.3901 | 39.34% |
| 2026-07-13 | 2026-08-07 | FIRST_HOLD | 82 | 82 | 2.2800 | 1.1450 | 32.93% |
| 2026-07-13 | 2026-08-07 | STRONG_HOLD | 61 | 61 | 1.8750 | 1.2200 | 40.98% |
| 2026-07-14 | 2026-08-10 | FIRST_HOLD | 87 | 87 | 2.1200 | 1.2501 | 29.89% |
| 2026-07-14 | 2026-08-10 | STRONG_HOLD | 62 | 62 | 1.7475 | 1.3526 | 37.10% |
| 2026-07-15 | 2026-08-11 | FIRST_HOLD | 85 | 85 | 2.1700 | 1.1750 | 30.59% |
| 2026-07-15 | 2026-08-11 | STRONG_HOLD | 59 | 59 | 1.8302 | 1.1800 | 38.98% |
| 2026-07-16 | 2026-08-12 | FIRST_HOLD | 84 | 84 | 2.1100 | 1.0900 | 32.14% |
| 2026-07-16 | 2026-08-12 | STRONG_HOLD | 59 | 58 | 1.7475 | 1.1700 | 37.29% |
| 2026-07-17 | 2026-08-13 | FIRST_HOLD | 78 | 78 | 2.0975 | 1.0800 | 33.33% |
| 2026-07-17 | 2026-08-13 | STRONG_HOLD | 55 | 54 | 1.7475 | 1.1550 | 40.00% |
| 2026-07-20 | 2026-08-14 | FIRST_HOLD | 77 | 77 | 2.1000 | 1.0800 | 33.77% |
| 2026-07-20 | 2026-08-14 | STRONG_HOLD | 54 | 53 | 1.7800 | 1.1500 | 38.89% |
| 2026-07-21 | 2026-08-17 | FIRST_HOLD | 81 | 81 | 2.1700 | 1.0150 | 30.86% |
| 2026-07-21 | 2026-08-17 | STRONG_HOLD | 57 | 56 | 1.8725 | 1.0300 | 36.84% |
| 2026-07-22 | 2026-08-18 | FIRST_HOLD | 81 | 81 | 2.1000 | 0.9700 | 32.10% |
| 2026-07-22 | 2026-08-18 | STRONG_HOLD | 58 | 57 | 1.7800 | 1.0100 | 34.48% |
| 2026-07-23 | 2026-08-19 | FIRST_HOLD | 90 | 90 | 1.5500 | 1.0025 | 28.89% |
| 2026-07-23 | 2026-08-19 | STRONG_HOLD | 63 | 62 | 1.5308 | 1.0200 | 33.33% |
| 2026-07-24 | 2026-08-20 | FIRST_HOLD | 93 | 93 | 1.5100 | 1.0600 | 27.96% |
| 2026-07-24 | 2026-08-20 | STRONG_HOLD | 64 | 63 | 1.4750 | 1.0100 | 32.81% |
| 2026-07-27 | 2026-08-21 | FIRST_HOLD | 96 | 96 | 1.4200 | 1.0375 | 29.17% |
| 2026-07-27 | 2026-08-21 | STRONG_HOLD | 67 | 66 | 1.4103 | 1.0650 | 31.34% |
| 2026-07-28 | 2026-08-24 | FIRST_HOLD | 101 | 101 | 1.3300 | 1.1000 | 28.71% |
| 2026-07-28 | 2026-08-24 | STRONG_HOLD | 70 | 69 | 1.3100 | 1.1500 | 31.43% |
| 2026-07-29 | 2026-08-25 | FIRST_HOLD | 101 | 100 | 1.3300 | 1.0925 | 28.71% |
| 2026-07-29 | 2026-08-25 | STRONG_HOLD | 69 | 68 | 1.3425 | 1.1400 | 30.43% |
| 2026-07-30 | 2026-08-26 | FIRST_HOLD | 103 | 102 | 1.2850 | 1.1125 | 27.18% |
| 2026-07-30 | 2026-08-26 | STRONG_HOLD | 71 | 70 | 1.2350 | 1.1500 | 29.58% |
| 2026-07-31 | 2026-08-27 | FIRST_HOLD | 101 | 100 | 1.3100 | 1.0925 | 26.73% |
| 2026-07-31 | 2026-08-27 | STRONG_HOLD | 70 | 69 | 1.2300 | 1.1500 | 28.57% |
| 2026-08-03 | 2026-08-28 | FIRST_HOLD | 101 | 100 | 1.3300 | 1.1125 | 28.71% |
| 2026-08-03 | 2026-08-28 | STRONG_HOLD | 72 | 71 | 1.3100 | 1.1300 | 29.17% |
| 2026-08-04 | 2026-08-31 | FIRST_HOLD | 103 | 102 | 1.3300 | 1.1575 | 31.07% |
| 2026-08-04 | 2026-08-31 | STRONG_HOLD | 74 | 73 | 1.2300 | 1.1500 | 29.73% |
| 2026-08-05 | 2026-09-01 | FIRST_HOLD | 108 | 107 | 1.2800 | 1.2400 | 30.56% |
| 2026-08-05 | 2026-09-01 | STRONG_HOLD | 76 | 75 | 1.1600 | 1.1600 | 30.26% |
| 2026-08-06 | 2026-09-02 | FIRST_HOLD | 109 | 108 | 1.2850 | 1.2100 | 30.28% |
| 2026-08-06 | 2026-09-02 | STRONG_HOLD | 76 | 75 | 1.1600 | 1.1600 | 30.26% |
| 2026-08-07 | 2026-09-03 | FIRST_HOLD | 104 | 103 | 1.3350 | 1.1800 | 31.73% |
| 2026-08-07 | 2026-09-03 | STRONG_HOLD | 72 | 71 | 1.3100 | 1.2100 | 33.33% |
| 2026-08-10 | 2026-09-04 | FIRST_HOLD | 100 | 99 | 1.3300 | 1.1800 | 33.00% |
| 2026-08-10 | 2026-09-04 | STRONG_HOLD | 68 | 67 | 1.2300 | 1.2100 | 32.35% |


## 16. Decision report: ten explicit answers

1. **Is raw break clearly inferior?** Not established as a trading policy. First confirmation excludes 702/1,435 raw breaks (48.92%) that fail their close, supporting a confirmation role. No frozen raw-entry outcome/exit model exists for an apples-to-apples expectancy claim.
2. **Is first hold clearly better?** On the 524 eventual-strong sequences, first hold has better average entry and remaining excursion geometry. Across complete entry policies, superiority is not established: strong also excludes 209 different events. The illustrative clean rate is 37.38% versus 38.36% across whole cohorts, but 50.19% versus 38.36% on matched events. Selection and delay must not be conflated.
3. **How much entry quality is lost?** Waiting always takes five minutes in this V1 sample. Mean directional disadvantage is $0.2554, median $0.1800. Strong is worse by more than one cent on 356/524 pairs, better on 151, and within one cent on 17. Mean remaining MFE lost is $0.2876.
4. **How much adverse excursion is avoided?** Within complete pairs, none on average: MAE increases by $0.1912. LONG and SHORT both show adverse average changes. Across different populations, strong avoids many early failures; that is a separate selection benefit, not within-event MAE improvement.
5. **Does MAE improvement justify waiting?** Not clearly supported on paired excursion evidence: mean MAE worsens while MFE falls. Only 10/374 pairs with positive MFE loss have a dollar MAE saving at least as large. This magnitude comparison is not a risk utility or realized-profit model.
6. **Where does strong appear useful?** It avoids 190 adverse-first paths among the 209 never-strong events at $0.50/$0.25, but also excludes 11 clean favorable-first outcomes (eight clean before reclaim). Whole-cohort descriptive clean rates are higher for strong in 10:00–10:30 and 10:30–11:00, but lower in 13:30–15:00. These are different memberships and time-bucket migration, not tested context-specific entry rules. No context is certified superior.
7. **Does more room mean better outcomes?** A monotonic association is not supported. At $0.50/$0.25, first-hold clean rates range non-monotonically across available-room buckets (33.78%–41.75%); strong’s >$2 bucket is 32.61%, versus 47.06% at ($1,$1.50]. Unavailable room remains its own group. Opening width is also non-monotonic; the widest quartile has higher median MAE for both styles. None becomes a filter.
8. **Does time of day matter?** Descriptive behavior varies: the same illustrative first-hold clean rates span 34.33%–41.90%, strong 26.67%–43.64%. Later signals have shorter remaining exposure, which mechanically affects EOD excursions and censoring. These differences do not establish causality or an optimized time restriction.
9. **Are months consistent?** Paired entry disadvantage and MFE loss are positive, and MAE improvement negative, in every displayed month. The illustrative matched clean-rate comparison favors first in eight of nine months; June is the exception. September has just four sessions and seven pairs. Absolute hit rates vary substantially across the 151 rolling windows; do not infer a stable payoff.
10. **What is supported or uncertain?** The selection-versus-delay tradeoff is supported by this sample. Session-bootstrap 95% intervals for aggregate entry disadvantage ($0.2065–$0.3075), MFE loss ($0.2381–$0.3406), and MAE improvement (−$0.2350 to −$0.1478) exclude zero. They are pointwise, not a multiple-testing license to select contexts. Removing ambiguity changes the illustrative whole-cohort rates from 37.38%/38.36% to 37.79%/38.58%, without reversing their ordering. Outliers elevate means, but the five largest-contribution sessions account for only about 11%–12% of summed event MFE. Causation, policy expectancy, transaction-cost resilience, and independent replication remain uncertain.

No signal refinement, parameter search, data exclusion, options conversion, or trading deployment was performed.

## Future hypotheses and independent validation

- Treat Jan 1–Sep 4, 2026 as in-sample discovery for any refinement. No refinement is implemented here.
- Potential hypotheses include whether strength’s avoided-failure benefit differs by direction/time, and whether its extra close is worth the measured delay. Freeze one limited hypothesis set before opening new outcomes.
- Reserve complete unseen sessions after Sep 4, 2026. Freeze the test dates or minimum number of sessions, definitions, threshold family, paired estimands, missing-data rules, and a one-time evaluation schedule before running it. Avoid repeated peeking and stopping on a favorable result.
- Keep unmodified V1 first/strong controls, all failures, and ambiguity categories. Validate calendar coverage and input lineage before interpreting results. Use the same session-clustered uncertainty method and report each month separately.
- Earlier 2024/2025 samples have already been used for other studies in this repository. They are not automatically untouched holdouts. Any earlier-period alternative needs a documented provenance/exposure audit before being labeled independent.
- Before claiming entry-policy expectancy, separately predeclare a realized underlying exit/cost model. Before any options study, validate that underlying result independently. No options layer or trading deployment is authorized by this analysis.

