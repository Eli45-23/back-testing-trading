# SPY break-and-hold V1 research

Requested: 2026-01-01 through 2026-09-04 (America/New_York).
Sessions: expected 170, analyzed 170, missing 0, invalid 0.
Definition hash: `92b8c227e32c4fd43001da58fa0865fc61e868faa53c0bab2199c258e91f5f4d`. Input manifest: `2caffada233ed08d9cec0da158c46ae56b6874ab979cc2d9d54aec844bd8c8cd`.
Git base: `f592413ed89885a74a6314ceaa5758aa47ffafa8`; this report may include uncommitted research code.

## Event population

| Measure | Count/rate |
|---|---:|
| Upside breaks | 745 |
| Downside breaks | 690 |
| Failed upside breaks | 345 |
| Failed downside breaks | 357 |
| Failed-break rate, all breaks | 702/1435 = 48.92% |
| First holds / all breaks | 733/1435 = 51.08% |
| Strong holds / first holds | 524/733 = 71.49% |
| Reclaims | 585 |

Sessions with LONG break: 154/170 (90.59%).
Sessions with SHORT break: 144/170 (84.71%).
Sessions with both boundaries broken: 128/170.

## FIRST_HOLD

n=733; measurable EOD n=727; long n=400; short n=333.

| EOD metric ($) | Value |
|---|---:|
| mean_mfe | 2.6403 |
| median_mfe | 1.9900 |
| mean_mae | 2.5310 |
| median_mae | 1.7701 |
| mfe_q25 | 0.8200 |
| mfe_q75 | 3.7012 |
| mae_q25 | 0.7800 |
| mae_q75 | 3.4475 |
| median_eod | -0.0300 |
| ratio_mean_mfe_mae | 1.0432 |

| Horizon | complete n | mean directional return $ | median return $ | median MFE $ | median MAE $ |
|---|---:|---:|---:|---:|---:|
| 5m | 727 | 0.0017 | 0.0013 | 0.3150 | 0.3100 |
| 15m | 718 | 0.0128 | 0.0134 | 0.5825 | 0.5600 |
| 30m | 703 | -0.0319 | -0.0300 | 0.8200 | 0.8000 |
| 60m | 674 | 0.0028 | 0.1045 | 1.1125 | 1.0845 |
| EOD | 727 | 0.0948 | -0.0300 | 1.9900 | 1.7701 |
| PRE_RECLAIM | 727 | -0.0529 | -0.4600 | 0.6200 | 0.6900 |

Threshold percentages use all signals as denominator; ambiguous, neither, and no-data cases are retained.

| Favorable/adverse $ | n | favorable first | adverse first | ambiguous same bar | neither | no future |
|---|---:|---:|---:|---:|---:|---:|
| +0.25/-0.25 | 733 | 356 (48.57%) | 333 (45.43%) | 38 (5.18%) | 0 (0.00%) | 6 (0.82%) |
| +0.50/-0.25 | 733 | 274 (37.38%) | 445 (60.71%) | 8 (1.09%) | 0 (0.00%) | 6 (0.82%) |
| +0.75/-0.25 | 733 | 215 (29.33%) | 509 (69.44%) | 3 (0.41%) | 0 (0.00%) | 6 (0.82%) |
| +1.00/-0.25 | 733 | 180 (24.56%) | 541 (73.81%) | 2 (0.27%) | 4 (0.55%) | 6 (0.82%) |
| +0.50/-0.30 | 733 | 299 (40.79%) | 423 (57.71%) | 5 (0.68%) | 0 (0.00%) | 6 (0.82%) |
| +0.75/-0.30 | 733 | 234 (31.92%) | 489 (66.71%) | 3 (0.41%) | 1 (0.14%) | 6 (0.82%) |
| +1.00/-0.30 | 733 | 198 (27.01%) | 521 (71.08%) | 2 (0.27%) | 6 (0.82%) | 6 (0.82%) |
| +1.50/-0.30 | 733 | 143 (19.51%) | 572 (78.04%) | 0 (0.00%) | 12 (1.64%) | 6 (0.82%) |
| +2.00/-0.30 | 733 | 113 (15.42%) | 598 (81.58%) | 0 (0.00%) | 16 (2.18%) | 6 (0.82%) |

### FIRST_HOLD: direction

| Subgroup | n | sessions | median MFE $ | mean MFE $ | median MAE $ | mean MAE $ | median EOD $ | +.50/-.25 clean % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| LONG | 400 | 137 | 1.8900 | 2.5239 | 2.0500 | 2.6437 | -0.0500 | 34.25% |
| SHORT | 333 | 129 | 2.1589 | 2.7803 | 1.5300 | 2.3954 | -0.0300 | 41.14% |

### FIRST_HOLD: time bucket

| Subgroup | n | sessions | median MFE $ | mean MFE $ | median MAE $ | mean MAE $ | median EOD $ | +.50/-.25 clean % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 09:35-10:00 | 192 | 151 | 2.4950 | 3.3023 | 2.7400 | 3.5567 | -0.1150 | 35.42% |
| 10:00-10:30 | 112 | 84 | 2.3700 | 2.7875 | 2.3028 | 3.1041 | 0.0750 | 35.71% |
| 10:30-11:00 | 72 | 54 | 2.6300 | 3.0748 | 1.9950 | 2.5157 | -0.2138 | 38.89% |
| 11:00-12:00 | 105 | 64 | 1.7600 | 2.5318 | 1.8800 | 2.2077 | 0.1600 | 41.90% |
| 12:00-13:30 | 118 | 62 | 1.9600 | 2.4677 | 1.3100 | 1.9312 | 0.4198 | 37.29% |
| 13:30-15:00 | 67 | 49 | 1.1300 | 1.8975 | 1.1900 | 1.6795 | -0.0590 | 40.30% |
| 15:00-close | 67 | 43 | 0.6650 | 1.1098 | 0.6300 | 0.9200 | -0.1590 | 34.33% |

### FIRST_HOLD: weekday

| Subgroup | n | sessions | median MFE $ | mean MFE $ | median MAE $ | mean MAE $ | median EOD $ | +.50/-.25 clean % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Friday | 163 | 33 | 1.5600 | 2.2078 | 2.1100 | 2.4241 | -0.5400 | 36.20% |
| Monday | 117 | 32 | 2.1225 | 2.4729 | 1.0500 | 2.2601 | 0.7875 | 37.61% |
| Thursday | 174 | 35 | 2.0749 | 2.8902 | 1.8932 | 2.9188 | -0.0150 | 33.91% |
| Tuesday | 136 | 35 | 2.1300 | 2.6977 | 1.7701 | 2.3959 | -0.0400 | 41.18% |
| Wednesday | 143 | 35 | 2.0836 | 2.9073 | 1.3970 | 2.5234 | 0.2050 | 39.16% |

### FIRST_HOLD: next-level distance

| Subgroup | n | sessions | median MFE $ | mean MFE $ | median MAE $ | mean MAE $ | median EOD $ | +.50/-.25 clean % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| <=0.25 | 91 | 56 | 1.7012 | 2.5969 | 1.4400 | 1.9467 | 0.2350 | 40.66% |
| <=0.50 | 65 | 42 | 2.0650 | 2.5997 | 1.4300 | 1.8868 | -0.0600 | 33.85% |
| <=1.00 | 103 | 52 | 1.4501 | 2.2497 | 2.1600 | 3.1274 | -0.5150 | 41.75% |
| <=1.50 | 77 | 51 | 2.1888 | 2.7297 | 2.2448 | 2.9900 | -0.4400 | 36.36% |
| <=2.00 | 74 | 42 | 2.0800 | 2.5349 | 1.3000 | 2.6766 | 0.8000 | 33.78% |
| >2.00 | 199 | 74 | 2.2876 | 3.0357 | 1.8850 | 2.7715 | 0.3700 | 38.69% |
| UNAVAILABLE | 124 | 43 | 1.7600 | 2.3858 | 1.6950 | 2.0506 | -0.1700 | 33.87% |

### FIRST_HOLD: first/later break

| Subgroup | n | sessions | median MFE $ | mean MFE $ | median MAE $ | mean MAE $ | median EOD $ | +.50/-.25 clean % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FIRST_BREAK | 84 | 84 | 2.6050 | 3.4037 | 2.8500 | 3.8395 | 0.3750 | 32.14% |
| LATER_BREAK | 649 | 157 | 1.9350 | 2.5406 | 1.6299 | 2.3600 | -0.0500 | 38.06% |

### FIRST_HOLD: opposite previously tested

| Subgroup | n | sessions | median MFE $ | mean MFE $ | median MAE $ | mean MAE $ | median EOD $ | +.50/-.25 clean % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| False | 230 | 122 | 2.3200 | 2.8629 | 2.2376 | 3.0878 | -0.2150 | 33.04% |
| True | 503 | 126 | 1.9299 | 2.5386 | 1.5500 | 2.2765 | 0.0200 | 39.36% |
## STRONG_HOLD

n=524; measurable EOD n=522; long n=283; short n=241.

| EOD metric ($) | Value |
|---|---:|
| mean_mfe | 2.5289 |
| median_mfe | 1.8737 |
| mean_mae | 2.5044 |
| median_mae | 1.7075 |
| mfe_q25 | 0.8050 |
| mfe_q75 | 3.4800 |
| mae_q25 | 0.8302 |
| mae_q75 | 3.3192 |
| median_eod | 0.0350 |
| ratio_mean_mfe_mae | 1.0098 |

| Horizon | complete n | mean directional return $ | median return $ | median MFE $ | median MAE $ |
|---|---:|---:|---:|---:|---:|
| 5m | 522 | 0.0195 | 0.0225 | 0.3400 | 0.2800 |
| 15m | 513 | -0.0228 | -0.0200 | 0.5550 | 0.5799 |
| 30m | 504 | -0.0636 | -0.0160 | 0.7725 | 0.7972 |
| 60m | 483 | -0.0634 | 0.0550 | 1.0700 | 1.1000 |
| EOD | 522 | 0.0791 | 0.0350 | 1.8737 | 1.7075 |
| PRE_RECLAIM | 522 | -0.0760 | -0.5282 | 0.8000 | 0.8500 |

Threshold percentages use all signals as denominator; ambiguous, neither, and no-data cases are retained.

| Favorable/adverse $ | n | favorable first | adverse first | ambiguous same bar | neither | no future |
|---|---:|---:|---:|---:|---:|---:|
| +0.25/-0.25 | 524 | 271 (51.72%) | 226 (43.13%) | 25 (4.77%) | 0 (0.00%) | 2 (0.38%) |
| +0.50/-0.25 | 524 | 201 (38.36%) | 318 (60.69%) | 3 (0.57%) | 0 (0.00%) | 2 (0.38%) |
| +0.75/-0.25 | 524 | 156 (29.77%) | 363 (69.27%) | 2 (0.38%) | 1 (0.19%) | 2 (0.38%) |
| +1.00/-0.25 | 524 | 122 (23.28%) | 396 (75.57%) | 0 (0.00%) | 4 (0.76%) | 2 (0.38%) |
| +0.50/-0.30 | 524 | 211 (40.27%) | 309 (58.97%) | 2 (0.38%) | 0 (0.00%) | 2 (0.38%) |
| +0.75/-0.30 | 524 | 166 (31.68%) | 353 (67.37%) | 2 (0.38%) | 1 (0.19%) | 2 (0.38%) |
| +1.00/-0.30 | 524 | 133 (25.38%) | 385 (73.47%) | 0 (0.00%) | 4 (0.76%) | 2 (0.38%) |
| +1.50/-0.30 | 524 | 96 (18.32%) | 416 (79.39%) | 0 (0.00%) | 10 (1.91%) | 2 (0.38%) |
| +2.00/-0.30 | 524 | 68 (12.98%) | 439 (83.78%) | 0 (0.00%) | 15 (2.86%) | 2 (0.38%) |

### STRONG_HOLD: direction

| Subgroup | n | sessions | median MFE $ | mean MFE $ | median MAE $ | mean MAE $ | median EOD $ | +.50/-.25 clean % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| LONG | 283 | 132 | 1.6350 | 2.3192 | 1.8763 | 2.6203 | -0.1000 | 38.16% |
| SHORT | 241 | 114 | 2.2600 | 2.7773 | 1.5950 | 2.3673 | 0.1700 | 38.59% |

### STRONG_HOLD: time bucket

| Subgroup | n | sessions | median MFE $ | mean MFE $ | median MAE $ | mean MAE $ | median EOD $ | +.50/-.25 clean % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 09:35-10:00 | 102 | 102 | 2.5275 | 3.1943 | 2.6300 | 3.7326 | 0.0550 | 39.22% |
| 10:00-10:30 | 94 | 83 | 2.2196 | 2.8058 | 2.3300 | 3.0529 | 0.5625 | 42.55% |
| 10:30-11:00 | 55 | 51 | 2.2900 | 2.7707 | 1.8200 | 2.5666 | -0.4250 | 43.64% |
| 11:00-12:00 | 86 | 68 | 2.0400 | 2.5697 | 1.7300 | 2.1703 | 0.0600 | 40.70% |
| 12:00-13:30 | 84 | 58 | 2.0200 | 2.4565 | 1.4375 | 1.9564 | 0.4675 | 34.52% |
| 13:30-15:00 | 60 | 47 | 1.0700 | 1.8783 | 1.2100 | 1.8484 | -0.2125 | 26.67% |
| 15:00-close | 43 | 36 | 0.7700 | 0.9297 | 0.6850 | 0.8921 | -0.3200 | 39.53% |

### STRONG_HOLD: weekday

| Subgroup | n | sessions | median MFE $ | mean MFE $ | median MAE $ | mean MAE $ | median EOD $ | +.50/-.25 clean % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Friday | 111 | 33 | 1.5750 | 2.1642 | 2.1600 | 2.6246 | -0.5450 | 38.74% |
| Monday | 85 | 32 | 2.0100 | 2.3901 | 1.3400 | 2.3222 | 0.5250 | 32.94% |
| Thursday | 130 | 35 | 1.9300 | 2.7187 | 1.8928 | 2.8056 | 0.1025 | 31.54% |
| Tuesday | 95 | 35 | 1.7500 | 2.3848 | 1.5600 | 2.4753 | -0.0800 | 47.37% |
| Wednesday | 103 | 35 | 2.1750 | 2.9305 | 1.4750 | 2.1700 | 0.1050 | 42.72% |

### STRONG_HOLD: next-level distance

| Subgroup | n | sessions | median MFE $ | mean MFE $ | median MAE $ | mean MAE $ | median EOD $ | +.50/-.25 clean % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| <=0.25 | 50 | 41 | 1.9724 | 2.5677 | 1.7050 | 2.0884 | 0.2700 | 34.00% |
| <=0.50 | 46 | 32 | 1.7625 | 2.5986 | 1.3850 | 2.7201 | 0.1625 | 45.65% |
| <=1.00 | 72 | 51 | 1.4202 | 1.9857 | 1.9956 | 2.7154 | -0.5025 | 37.50% |
| <=1.50 | 51 | 40 | 1.9600 | 2.4608 | 1.5700 | 2.4957 | -0.2100 | 47.06% |
| <=2.00 | 45 | 31 | 1.9425 | 2.5547 | 1.5900 | 2.2402 | 0.6375 | 42.22% |
| >2.00 | 138 | 69 | 2.1600 | 2.7933 | 1.7450 | 2.6334 | 0.0400 | 32.61% |
| UNAVAILABLE | 122 | 64 | 1.7922 | 2.5278 | 1.8750 | 2.4189 | 0.1000 | 39.34% |

### STRONG_HOLD: first/later break

| Subgroup | n | sessions | median MFE $ | mean MFE $ | median MAE $ | mean MAE $ | median EOD $ | +.50/-.25 clean % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FIRST_BREAK | 56 | 56 | 2.4200 | 3.0954 | 2.8734 | 4.2535 | -0.5550 | 44.64% |
| LATER_BREAK | 468 | 157 | 1.8025 | 2.4609 | 1.6075 | 2.2943 | 0.0450 | 37.61% |

### STRONG_HOLD: opposite previously tested

| Subgroup | n | sessions | median MFE $ | mean MFE $ | median MAE $ | mean MAE $ | median EOD $ | +.50/-.25 clean % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| False | 158 | 100 | 2.3250 | 2.8554 | 2.1950 | 3.0410 | 0.0401 | 38.61% |
| True | 366 | 125 | 1.6799 | 2.3885 | 1.5699 | 2.2737 | 0.0300 | 38.25% |

## Matched-event comparison

These pairs are restricted to events that eventually achieved strong hold. This is survivor selection, not an executable first-hold filter.

| Cohort | n | mean MFE $ | mean MAE $ | +.50/-.25 clean % |
|---|---:|---:|---:|---:|
| All first holds | 733 | 2.6403 | 2.5310 | 37.38% |
| First holds on eventual strong events | 524 | 2.8068 | 2.3060 | 50.19% |
| Strong entries on same events | 524 | 2.5289 | 2.5044 | 38.36% |

Mean directional entry-price deterioration from waiting: $0.2554; positive means a less favorable entry.

## Missing/invalid sessions

None.

## Interpretation and limits

- Raw timestamps are minute starts. Outcomes exclude the minute starting exactly at signal close.
- First crossing timestamps identify a minute interval, never an exact trade timestamp.
- Both-sides-broken is a post-session annotation. Features use only signal-time knowledge.
- Fixed horizons past EOD are incomplete and omitted from complete-horizon return summaries.
- EOD excursions and pre-reclaim excursions are separate. No-reclaim windows run to EOD.
- Close reference prices assume no spread/slippage. No execution/P&L or options model.
- Overlapping events are dependent. Strong-hold cohorts are selected survivors.
- ATR/VWAP omitted from V1; no filters. Missing previous/premarket context remains unavailable.
- MFE/MAE ratios are descriptive excursions, not realized payoff ratios or expectancy.
- Thresholds are nine predeclared comparisons, not optimized exits. No selection or edge claim follows from the best subgroup.
- Backtest evidence does not guarantee future profitability; this does not estimate options profitability.


