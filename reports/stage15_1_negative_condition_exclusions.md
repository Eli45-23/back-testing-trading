# Stage 15.1 — BASE_SHORT Negative-Condition Exclusion Validation

Frozen range: `2026-01-02` through `2026-08-19`
Baseline: `BASE_SHORT:NEXT_OBJECTIVE_LEVEL:ATR_1_00:NO_FIXED_TARGET`
Stage 14 status: paused and unchanged. No Alpaca connection or order activity.

## 1. Baseline reconciliation

Membership **1040**; realized **589**; unavailable/ambiguous **451**; sessions **120**; mean R **0.0155**; median R **0.0538**; PF **1.0341**; win **53.3%**; +/− months **3/5**; LOMO minimum **-0.0407**; 95% CI **[-0.1056, 0.1494]**.

Baseline reconciliation passed exact Stage 15 Decimal values before any exclusion was evaluated.

## 2. Frozen-condition and overlap accounting

| ID | Condition | Membership | Realized | Unavailable/ambiguous | Unique membership | Unique realized | Sessions | Months | Frozen mean R | Frozen BH q |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | ALL_VWAP_ALIGNED×ROOM_GT_3_ATR | 41 | 41 | 0 | 33 | 33 | 19 | 8 | -0.5720 | 0.0083 |
| 2 | BULLISH_STRUCTURE×ROOM_0_5_TO_1_ATR | 36 | 36 | 0 | 8 | 8 | 27 | 8 | -0.5107 | 0.0036 |
| 3 | NO_VWAP_ALIGNMENT×ROOM_0_5_TO_1_ATR | 42 | 42 | 0 | 25 | 25 | 26 | 8 | -0.3776 | 0.0652 |
| 4 | EMA_ALIGNED×BULLISH_STRUCTURE | 62 | 41 | 21 | 43 | 22 | 35 | 8 | -0.3575 | 0.0753 |

Membership overlap matrix (realized overlap in parentheses):

| | NEG_1 | NEG_2 | NEG_3 | NEG_4 |
|---|---:|---:|---:|---:|
| NEG_1 | 41 (41) | 0 (0) | 0 (0) | 8 (8) |
| NEG_2 | 0 (0) | 36 (36) | 17 (17) | 11 (11) |
| NEG_3 | 0 (0) | 17 (17) | 42 (42) | 0 (0) |
| NEG_4 | 8 (8) | 11 (11) | 0 (0) | 62 (41) |

## 3. Exclusion-variant comparison

| Variant | Original M | Removed M/R/U | Retained M/R/U | Membership retained | Realized retained | Sessions | Win | Mean R | Δ mean | Median R | PF | LOMO | 5th pct R | Classification |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| BASE_SHORT_CONTROL | 1040 | 0/0/0 | 1040/589/451 | 100.0% | 100.0% | 120 | 53.3% | 0.0155 | 0.0000 | 0.0538 | 1.0341 | -0.0407 | -1.0000 | NO_IMPROVEMENT |
| EXCLUDE_NEG_1 | 1040 | 41/41/0 | 999/548/451 | 96.1% | 93.0% | 120 | 56.4% | 0.0595 | 0.0440 | 0.0939 | 1.1394 | 0.0051 | -1.0000 | RESEARCH_EXCLUSION_CANDIDATE |
| EXCLUDE_NEG_2 | 1040 | 36/36/0 | 1004/553/451 | 96.5% | 93.9% | 119 | 55.0% | 0.0498 | 0.0343 | 0.0781 | 1.1137 | -0.0117 | -1.0000 | DESCRIPTIVELY_IMPROVED |
| EXCLUDE_NEG_3 | 1040 | 42/42/0 | 998/547/451 | 96.0% | 92.9% | 118 | 54.7% | 0.0457 | 0.0302 | 0.0738 | 1.1037 | -0.0122 | -1.0000 | DESCRIPTIVELY_IMPROVED |
| EXCLUDE_NEG_4 | 1040 | 62/41/21 | 978/548/430 | 94.0% | 93.0% | 118 | 54.6% | 0.0434 | 0.0279 | 0.0745 | 1.0973 | -0.0237 | -1.0000 | RESEARCH_EXCLUSION_CANDIDATE |
| EXCLUDE_ANY_OF_1_TO_4 | 1040 | 145/124/21 | 895/465/430 | 86.1% | 78.9% | 116 | 59.4% | 0.1275 | 0.1120 | 0.1268 | 1.3212 | 0.0578 | -1.0000 | DESCRIPTIVELY_IMPROVED |
| EXCLUDE_NEG_1_2 | 1040 | 77/77/0 | 963/512/451 | 92.6% | 86.9% | 119 | 58.4% | 0.0996 | 0.0840 | 0.1219 | 1.2453 | 0.0398 | -1.0000 | RESEARCH_EXCLUSION_CANDIDATE |
| EXCLUDE_NEG_1_4 | 1040 | 95/74/21 | 945/515/430 | 90.9% | 87.4% | 118 | 57.1% | 0.0796 | 0.0641 | 0.1054 | 1.1893 | 0.0129 | -1.0000 | RESEARCH_EXCLUSION_CANDIDATE |
| EXCLUDE_NEG_2_4 | 1040 | 87/66/21 | 953/523/430 | 91.6% | 88.8% | 118 | 55.8% | 0.0700 | 0.0545 | 0.0922 | 1.1615 | 0.0008 | -1.0000 | DESCRIPTIVELY_IMPROVED |
| EXCLUDE_NEG_1_2_4 | 1040 | 120/99/21 | 920/490/430 | 88.5% | 83.2% | 118 | 58.6% | 0.1098 | 0.0943 | 0.1243 | 1.2709 | 0.0411 | -1.0000 | RESEARCH_EXCLUSION_CANDIDATE |

Outcome-detail metrics:

| Variant | Std R | Target hit | Stop hit | EOD exit | Median MFE | Median MAE |
|---|---:|---:|---:|---:|---:|---:|
| BASE_SHORT_CONTROL | 1.1108 | 50.8% | 45.3% | 3.9% | 1.5700 | 1.3200 |
| EXCLUDE_NEG_1 | 1.1029 | 54.6% | 42.5% | 2.9% | 1.6150 | 1.3250 |
| EXCLUDE_NEG_2 | 1.1199 | 52.3% | 43.6% | 4.2% | 1.5600 | 1.3200 |
| EXCLUDE_NEG_3 | 1.1233 | 51.9% | 43.9% | 4.2% | 1.5350 | 1.3200 |
| EXCLUDE_NEG_4 | 1.1252 | 52.2% | 44.5% | 3.3% | 1.6325 | 1.3200 |
| EXCLUDE_ANY_OF_1_TO_4 | 1.1286 | 57.6% | 39.6% | 2.8% | 1.6078 | 1.3200 |
| EXCLUDE_NEG_1_2 | 1.1106 | 56.4% | 40.4% | 3.1% | 1.5975 | 1.3200 |
| EXCLUDE_NEG_1_4 | 1.1141 | 55.5% | 41.9% | 2.5% | 1.6800 | 1.3200 |
| EXCLUDE_NEG_2_4 | 1.1321 | 53.3% | 43.2% | 3.4% | 1.5950 | 1.3300 |
| EXCLUDE_NEG_1_2_4 | 1.1200 | 56.9% | 40.4% | 2.7% | 1.6150 | 1.3250 |

## 4. Monthly and stability table

Frozen minimum gates: at least 70% of realized trades, at least 80 sessions, at least four represented months with no month exceeding 50% of retained realized trades, and no baseline month with at least five trades reduced below 50% retention.

| Variant | +/− months | Worst month | Worst mean R | CI | Bootstrap Δ CI | 70% trades | 80 sessions | Month breadth | No heavy month reduction |
|---|---:|---|---:|---:|---:|---|---|---|---|
| BASE_SHORT_CONTROL | 3/5 | 2026-01 | -0.2673 | [-0.1056, 0.1494] | [0.0000, 0.0000] | True | True | True | True |
| EXCLUDE_NEG_1 | 4/4 | 2026-01 | -0.2117 | [-0.0688, 0.1972] | [0.0101, 0.0819] | True | True | True | True |
| EXCLUDE_NEG_2 | 3/5 | 2026-01 | -0.2311 | [-0.0756, 0.1874] | [0.0146, 0.0547] | True | True | True | True |
| EXCLUDE_NEG_3 | 4/4 | 2026-01 | -0.2650 | [-0.0841, 0.1890] | [0.0090, 0.0549] | True | True | True | True |
| EXCLUDE_NEG_4 | 3/5 | 2026-01 | -0.2497 | [-0.0852, 0.1845] | [0.0040, 0.0539] | True | True | True | True |
| EXCLUDE_ANY_OF_1_TO_4 | 5/3 | 2026-01 | -0.1772 | [-0.0162, 0.2827] | [0.0530, 0.1747] | True | True | True | True |
| EXCLUDE_NEG_1_2 | 5/3 | 2026-01 | -0.1696 | [-0.0339, 0.2414] | [0.0409, 0.1304] | True | True | True | True |
| EXCLUDE_NEG_1_4 | 4/4 | 2026-01 | -0.1912 | [-0.0524, 0.2205] | [0.0191, 0.1127] | True | True | True | True |
| EXCLUDE_NEG_2_4 | 4/4 | 2026-01 | -0.2215 | [-0.0641, 0.2142] | [0.0248, 0.0860] | True | True | True | True |
| EXCLUDE_NEG_1_2_4 | 5/3 | 2026-01 | -0.1584 | [-0.0258, 0.2579] | [0.0455, 0.1482] | True | True | True | True |

Complete variant-month rows:

| Variant | Month | Trades | Retained | Mean R | Median R | Total R |
|---|---|---:|---:|---:|---:|---:|
| BASE_SHORT_CONTROL | 2026-01 | 85 | 100.0% | -0.2673 | -1.0000 | -22.7223 |
| BASE_SHORT_CONTROL | 2026-02 | 66 | 100.0% | -0.0570 | 0.0700 | -3.7632 |
| BASE_SHORT_CONTROL | 2026-03 | 93 | 100.0% | -0.1536 | -0.2860 | -14.2838 |
| BASE_SHORT_CONTROL | 2026-04 | 85 | 100.0% | -0.0416 | -1.0000 | -3.5374 |
| BASE_SHORT_CONTROL | 2026-05 | 71 | 100.0% | 0.4255 | 0.1314 | 30.2103 |
| BASE_SHORT_CONTROL | 2026-06 | 69 | 100.0% | 0.1760 | 0.1894 | 12.1457 |
| BASE_SHORT_CONTROL | 2026-07 | 85 | 100.0% | 0.1763 | 0.1353 | 14.9881 |
| BASE_SHORT_CONTROL | 2026-08 | 35 | 100.0% | -0.1115 | 0.0793 | -3.9028 |
| EXCLUDE_NEG_1 | 2026-01 | 79 | 92.9% | -0.2117 | -1.0000 | -16.7223 |
| EXCLUDE_NEG_1 | 2026-02 | 65 | 98.5% | -0.0886 | 0.0685 | -5.7586 |
| EXCLUDE_NEG_1 | 2026-03 | 82 | 88.2% | -0.1103 | 0.0920 | -9.0423 |
| EXCLUDE_NEG_1 | 2026-04 | 82 | 96.5% | -0.0066 | -0.4624 | -0.5374 |
| EXCLUDE_NEG_1 | 2026-05 | 67 | 94.4% | 0.4500 | 0.2077 | 30.1522 |
| EXCLUDE_NEG_1 | 2026-06 | 64 | 92.8% | 0.2214 | 0.2002 | 14.1673 |
| EXCLUDE_NEG_1 | 2026-07 | 81 | 95.3% | 0.2344 | 0.1648 | 18.9881 |
| EXCLUDE_NEG_1 | 2026-08 | 28 | 80.0% | 0.0478 | 0.1700 | 1.3388 |
| EXCLUDE_NEG_2 | 2026-01 | 81 | 95.3% | -0.2311 | -1.0000 | -18.7223 |
| EXCLUDE_NEG_2 | 2026-02 | 63 | 95.5% | -0.0389 | 0.0715 | -2.4487 |
| EXCLUDE_NEG_2 | 2026-03 | 88 | 94.6% | -0.1252 | -0.1219 | -11.0168 |
| EXCLUDE_NEG_2 | 2026-04 | 76 | 89.4% | -0.0268 | -1.0000 | -2.0378 |
| EXCLUDE_NEG_2 | 2026-05 | 68 | 95.8% | 0.4884 | 0.2260 | 33.2103 |
| EXCLUDE_NEG_2 | 2026-06 | 64 | 92.8% | 0.2427 | 0.2002 | 15.5359 |
| EXCLUDE_NEG_2 | 2026-07 | 81 | 95.3% | 0.1716 | 0.1207 | 13.9034 |
| EXCLUDE_NEG_2 | 2026-08 | 32 | 91.4% | -0.0282 | 0.0876 | -0.9028 |
| EXCLUDE_NEG_3 | 2026-01 | 75 | 88.2% | -0.2650 | -1.0000 | -19.8735 |
| EXCLUDE_NEG_3 | 2026-02 | 59 | 89.4% | -0.0645 | 0.0685 | -3.8049 |
| EXCLUDE_NEG_3 | 2026-03 | 89 | 95.7% | -0.1350 | -0.2566 | -12.0168 |
| EXCLUDE_NEG_3 | 2026-04 | 76 | 89.4% | 0.0239 | 0.1011 | 1.8132 |
| EXCLUDE_NEG_3 | 2026-05 | 67 | 94.4% | 0.4604 | 0.1314 | 30.8465 |
| EXCLUDE_NEG_3 | 2026-06 | 65 | 94.2% | 0.2236 | 0.1894 | 14.5359 |
| EXCLUDE_NEG_3 | 2026-07 | 82 | 96.5% | 0.2000 | 0.1395 | 16.3975 |
| EXCLUDE_NEG_3 | 2026-08 | 34 | 97.1% | -0.0854 | 0.0801 | -2.9028 |
| EXCLUDE_NEG_4 | 2026-01 | 83 | 97.6% | -0.2497 | -1.0000 | -20.7223 |
| EXCLUDE_NEG_4 | 2026-02 | 64 | 97.0% | -0.0444 | 0.0700 | -2.8446 |
| EXCLUDE_NEG_4 | 2026-03 | 84 | 90.3% | -0.0977 | 0.0920 | -8.2032 |
| EXCLUDE_NEG_4 | 2026-04 | 81 | 95.3% | -0.0180 | -1.0000 | -1.4547 |
| EXCLUDE_NEG_4 | 2026-05 | 66 | 93.0% | 0.5335 | 0.2511 | 35.2103 |
| EXCLUDE_NEG_4 | 2026-06 | 63 | 91.3% | 0.1977 | 0.1664 | 12.4537 |
| EXCLUDE_NEG_4 | 2026-07 | 78 | 91.8% | 0.1477 | 0.1199 | 11.5187 |
| EXCLUDE_NEG_4 | 2026-08 | 29 | 82.9% | -0.0747 | 0.0810 | -2.1661 |
| EXCLUDE_ANY_OF_1_TO_4 | 2026-01 | 67 | 78.8% | -0.1772 | -1.0000 | -11.8735 |
| EXCLUDE_ANY_OF_1_TO_4 | 2026-02 | 55 | 83.3% | -0.1012 | 0.0468 | -5.5670 |
| EXCLUDE_ANY_OF_1_TO_4 | 2026-03 | 71 | 76.3% | -0.0380 | 0.1883 | -2.6948 |
| EXCLUDE_ANY_OF_1_TO_4 | 2026-04 | 69 | 81.2% | 0.0437 | 0.1271 | 3.0123 |
| EXCLUDE_ANY_OF_1_TO_4 | 2026-05 | 58 | 81.7% | 0.6170 | 0.2899 | 35.7885 |
| EXCLUDE_ANY_OF_1_TO_4 | 2026-06 | 51 | 73.9% | 0.3895 | 0.5019 | 19.8654 |
| EXCLUDE_ANY_OF_1_TO_4 | 2026-07 | 71 | 83.5% | 0.2384 | 0.1436 | 16.9280 |
| EXCLUDE_ANY_OF_1_TO_4 | 2026-08 | 23 | 65.7% | 0.1667 | 0.2295 | 3.8339 |
| EXCLUDE_NEG_1_2 | 2026-01 | 75 | 88.2% | -0.1696 | -1.0000 | -12.7223 |
| EXCLUDE_NEG_1_2 | 2026-02 | 62 | 93.9% | -0.0717 | 0.0700 | -4.4440 |
| EXCLUDE_NEG_1_2 | 2026-03 | 77 | 82.8% | -0.0750 | 0.1540 | -5.7754 |
| EXCLUDE_NEG_1_2 | 2026-04 | 73 | 85.9% | 0.0132 | 0.0752 | 0.9622 |
| EXCLUDE_NEG_1_2 | 2026-05 | 64 | 90.1% | 0.5180 | 0.2511 | 33.1522 |
| EXCLUDE_NEG_1_2 | 2026-06 | 59 | 85.5% | 0.2976 | 0.2286 | 17.5574 |
| EXCLUDE_NEG_1_2 | 2026-07 | 77 | 90.6% | 0.2325 | 0.1436 | 17.9034 |
| EXCLUDE_NEG_1_2 | 2026-08 | 25 | 71.4% | 0.1736 | 0.2295 | 4.3388 |
| EXCLUDE_NEG_1_4 | 2026-01 | 77 | 90.6% | -0.1912 | -1.0000 | -14.7223 |
| EXCLUDE_NEG_1_4 | 2026-02 | 63 | 95.5% | -0.0768 | 0.0685 | -4.8399 |
| EXCLUDE_NEG_1_4 | 2026-03 | 75 | 80.6% | -0.0662 | 0.1660 | -4.9617 |
| EXCLUDE_NEG_1_4 | 2026-04 | 80 | 94.1% | -0.0057 | -0.4624 | -0.4547 |
| EXCLUDE_NEG_1_4 | 2026-05 | 62 | 87.3% | 0.5670 | 0.2899 | 35.1522 |
| EXCLUDE_NEG_1_4 | 2026-06 | 58 | 84.1% | 0.2496 | 0.2274 | 14.4752 |
| EXCLUDE_NEG_1_4 | 2026-07 | 74 | 87.1% | 0.2097 | 0.1395 | 15.5187 |
| EXCLUDE_NEG_1_4 | 2026-08 | 26 | 74.3% | 0.0321 | 0.1123 | 0.8339 |
| EXCLUDE_NEG_2_4 | 2026-01 | 80 | 94.1% | -0.2215 | -1.0000 | -17.7223 |
| EXCLUDE_NEG_2_4 | 2026-02 | 61 | 92.4% | -0.0251 | 0.0715 | -1.5300 |
| EXCLUDE_NEG_2_4 | 2026-03 | 82 | 88.2% | -0.0968 | 0.0920 | -7.9362 |
| EXCLUDE_NEG_2_4 | 2026-04 | 74 | 87.1% | -0.0005 | -0.4624 | -0.0378 |
| EXCLUDE_NEG_2_4 | 2026-05 | 65 | 91.5% | 0.5571 | 0.2578 | 36.2103 |
| EXCLUDE_NEG_2_4 | 2026-06 | 59 | 85.5% | 0.2516 | 0.2110 | 14.8438 |
| EXCLUDE_NEG_2_4 | 2026-07 | 76 | 89.4% | 0.1569 | 0.1199 | 11.9280 |
| EXCLUDE_NEG_2_4 | 2026-08 | 26 | 74.3% | 0.0321 | 0.1123 | 0.8339 |
| EXCLUDE_NEG_1_2_4 | 2026-01 | 74 | 87.1% | -0.1584 | -1.0000 | -11.7223 |
| EXCLUDE_NEG_1_2_4 | 2026-02 | 60 | 90.9% | -0.0588 | 0.0700 | -3.5254 |
| EXCLUDE_NEG_1_2_4 | 2026-03 | 73 | 78.5% | -0.0643 | 0.1660 | -4.6948 |
| EXCLUDE_NEG_1_2_4 | 2026-04 | 73 | 85.9% | 0.0132 | 0.0752 | 0.9622 |
| EXCLUDE_NEG_1_2_4 | 2026-05 | 61 | 85.9% | 0.5927 | 0.3220 | 36.1522 |
| EXCLUDE_NEG_1_2_4 | 2026-06 | 54 | 78.3% | 0.3123 | 0.3605 | 16.8654 |
| EXCLUDE_NEG_1_2_4 | 2026-07 | 72 | 84.7% | 0.2212 | 0.1395 | 15.9280 |
| EXCLUDE_NEG_1_2_4 | 2026-08 | 23 | 65.7% | 0.1667 | 0.2295 | 3.8339 |

## 5. Bootstrap diagnostics

All intervals use 10,000 session-clustered resamples. Variant Δ intervals use paired session resampling against the complete control population.

| Variant | Mean bootstrap median | Mean 95% CI | Δ median | Δ 95% CI | CI above zero |
|---|---:|---:|---:|---:|---|
| BASE_SHORT_CONTROL | 0.0155 | [-0.1056, 0.1494] | 0.0000 | [0.0000, 0.0000] | False |
| EXCLUDE_NEG_1 | 0.0589 | [-0.0688, 0.1972] | 0.0433 | [0.0101, 0.0819] | False |
| EXCLUDE_NEG_2 | 0.0483 | [-0.0756, 0.1874] | 0.0338 | [0.0146, 0.0547] | False |
| EXCLUDE_NEG_3 | 0.0439 | [-0.0841, 0.1890] | 0.0297 | [0.0090, 0.0549] | False |
| EXCLUDE_NEG_4 | 0.0423 | [-0.0852, 0.1845] | 0.0275 | [0.0040, 0.0539] | False |
| EXCLUDE_ANY_OF_1_TO_4 | 0.1268 | [-0.0162, 0.2827] | 0.1106 | [0.0530, 0.1747] | False |
| EXCLUDE_NEG_1_2 | 0.0983 | [-0.0339, 0.2414] | 0.0829 | [0.0409, 0.1304] | False |
| EXCLUDE_NEG_1_4 | 0.0800 | [-0.0524, 0.2205] | 0.0632 | [0.0191, 0.1127] | False |
| EXCLUDE_NEG_2_4 | 0.0688 | [-0.0641, 0.2142] | 0.0537 | [0.0248, 0.0860] | False |
| EXCLUDE_NEG_1_2_4 | 0.1091 | [-0.0258, 0.2579] | 0.0932 | [0.0455, 0.1482] | False |

## 6. Room/exit-geometry diagnostic

The diagnostic compares fixed first-five-minute post-entry MFE/MAE normalized by confirmation ATR. This outcome window is independent of which next-objective exit ultimately resolved.

| Variant | Removed realized | Sessions | Removed/retained MFE ATR | Δ favorable | Removed/retained MAE ATR | Δ adverse | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| EXCLUDE_NEG_1 | 41 | 19 | 0.3250/0.3830 | -0.0579 | 0.5302/0.4109 | 0.1192 | MIXED |
| EXCLUDE_NEG_2 | 36 | 27 | 0.3198/0.3848 | -0.0649 | 0.4277/0.4114 | 0.0163 | EXIT_GEOMETRY_DEPENDENT |
| EXCLUDE_NEG_3 | 42 | 26 | 0.3587/0.3788 | -0.0201 | 0.3135/0.4276 | -0.1141 | EXIT_GEOMETRY_DEPENDENT |
| EXCLUDE_ANY_OF_1_TO_4 | 124 | 58 | 0.3107/0.4052 | -0.0945 | 0.4954/0.4000 | 0.0954 | EXIT_GEOMETRY_DEPENDENT |
| EXCLUDE_NEG_1_2 | 77 | 38 | 0.3250/0.3999 | -0.0749 | 0.5137/0.4069 | 0.1069 | MIXED |
| EXCLUDE_NEG_1_4 | 74 | 38 | 0.2703/0.3947 | -0.1244 | 0.5531/0.4000 | 0.1530 | ENTRY_BEHAVIOR_SUPPORTED |
| EXCLUDE_NEG_2_4 | 66 | 39 | 0.3050/0.3947 | -0.0897 | 0.4652/0.4096 | 0.0556 | EXIT_GEOMETRY_DEPENDENT |
| EXCLUDE_NEG_1_2_4 | 99 | 49 | 0.3053/0.4038 | -0.0985 | 0.5174/0.4000 | 0.1174 | MIXED |

## 7. Pre-development, development, and expanded comparison

| Variant | Period | Trades | Mean R | Baseline mean | Δ mean | Median R | PF |
|---|---|---:|---:|---:|---:|---:|---:|
| BASE_SHORT_CONTROL | PRE_DEVELOPMENT | 554 | 0.0235 | 0.0235 | 0.0000 | 0.0538 | 1.0512 |
| BASE_SHORT_CONTROL | DEVELOPMENT | 35 | -0.1115 | -0.1115 | 0.0000 | 0.0793 | 0.7053 |
| BASE_SHORT_CONTROL | EXPANDED | 589 | 0.0155 | 0.0155 | 0.0000 | 0.0538 | 1.0341 |
| EXCLUDE_NEG_1 | PRE_DEVELOPMENT | 520 | 0.0601 | 0.0235 | 0.0366 | 0.0922 | 1.1384 |
| EXCLUDE_NEG_1 | DEVELOPMENT | 28 | 0.0478 | -0.1115 | 0.1593 | 0.1700 | 1.1674 |
| EXCLUDE_NEG_1 | EXPANDED | 548 | 0.0595 | 0.0155 | 0.0440 | 0.0939 | 1.1394 |
| EXCLUDE_NEG_2 | PRE_DEVELOPMENT | 521 | 0.0546 | 0.0235 | 0.0310 | 0.0738 | 1.1226 |
| EXCLUDE_NEG_2 | DEVELOPMENT | 32 | -0.0282 | -0.1115 | 0.0833 | 0.0876 | 0.9119 |
| EXCLUDE_NEG_2 | EXPANDED | 553 | 0.0498 | 0.0155 | 0.0343 | 0.0781 | 1.1137 |
| EXCLUDE_NEG_3 | PRE_DEVELOPMENT | 513 | 0.0544 | 0.0235 | 0.0308 | 0.0715 | 1.1219 |
| EXCLUDE_NEG_3 | DEVELOPMENT | 34 | -0.0854 | -0.1115 | 0.0261 | 0.0801 | 0.7629 |
| EXCLUDE_NEG_3 | EXPANDED | 547 | 0.0457 | 0.0155 | 0.0302 | 0.0738 | 1.1037 |
| EXCLUDE_NEG_4 | PRE_DEVELOPMENT | 519 | 0.0500 | 0.0235 | 0.0265 | 0.0715 | 1.1111 |
| EXCLUDE_NEG_4 | DEVELOPMENT | 29 | -0.0747 | -0.1115 | 0.0368 | 0.0810 | 0.8031 |
| EXCLUDE_NEG_4 | EXPANDED | 548 | 0.0434 | 0.0155 | 0.0279 | 0.0745 | 1.0973 |
| EXCLUDE_ANY_OF_1_TO_4 | PRE_DEVELOPMENT | 442 | 0.1255 | 0.0235 | 0.1019 | 0.1243 | 1.3088 |
| EXCLUDE_ANY_OF_1_TO_4 | DEVELOPMENT | 23 | 0.1667 | -0.1115 | 0.2782 | 0.2295 | 1.7668 |
| EXCLUDE_ANY_OF_1_TO_4 | EXPANDED | 465 | 0.1275 | 0.0155 | 0.1120 | 0.1268 | 1.3212 |
| EXCLUDE_NEG_1_2 | PRE_DEVELOPMENT | 487 | 0.0958 | 0.0235 | 0.0722 | 0.1165 | 1.2300 |
| EXCLUDE_NEG_1_2 | DEVELOPMENT | 25 | 0.1736 | -0.1115 | 0.2851 | 0.2295 | 1.8678 |
| EXCLUDE_NEG_1_2 | EXPANDED | 512 | 0.0996 | 0.0155 | 0.0840 | 0.1219 | 1.2453 |
| EXCLUDE_NEG_1_4 | PRE_DEVELOPMENT | 489 | 0.0821 | 0.0235 | 0.0586 | 0.1054 | 1.1925 |
| EXCLUDE_NEG_1_4 | DEVELOPMENT | 26 | 0.0321 | -0.1115 | 0.1436 | 0.1123 | 1.1042 |
| EXCLUDE_NEG_1_4 | EXPANDED | 515 | 0.0796 | 0.0155 | 0.0641 | 0.1054 | 1.1893 |
| EXCLUDE_NEG_2_4 | PRE_DEVELOPMENT | 497 | 0.0719 | 0.0235 | 0.0484 | 0.0798 | 1.1636 |
| EXCLUDE_NEG_2_4 | DEVELOPMENT | 26 | 0.0321 | -0.1115 | 0.1436 | 0.1123 | 1.1042 |
| EXCLUDE_NEG_2_4 | EXPANDED | 523 | 0.0700 | 0.0155 | 0.0545 | 0.0922 | 1.1615 |
| EXCLUDE_NEG_1_2_4 | PRE_DEVELOPMENT | 467 | 0.1070 | 0.0235 | 0.0835 | 0.1207 | 1.2581 |
| EXCLUDE_NEG_1_2_4 | DEVELOPMENT | 23 | 0.1667 | -0.1115 | 0.2782 | 0.2295 | 1.7668 |
| EXCLUDE_NEG_1_2_4 | EXPANDED | 490 | 0.1098 | 0.0155 | 0.0943 | 0.1243 | 1.2709 |

## 8. Written conclusion

- **Single conditions:** `EXCLUDE_NEG_1` is the strongest single exclusion by mean-R improvement (Δ 0.0440 R; retained mean 0.0595 R). Singles 2 and 3 improve realized outcomes descriptively but are classified `EXIT_GEOMETRY_DEPENDENT`; they are not supported as entry filters.
- **All four:** `EXCLUDE_ANY_OF_1_TO_4` retains 86.1% of membership and 78.9% of realized trades, passes every minimum retention gate, and improves mean R by 0.1120. It does not numerically over-filter, but its room diagnostic is `EXIT_GEOMETRY_DEPENDENT`, so it remains `DESCRIPTIVELY_IMPROVED` rather than an entry-rule candidate.
- **Predeclared combinations:** `EXCLUDE_NEG_1_2_4` is strongest by mean-R improvement (Δ 0.0943 R; PF 1.2709; LOMO 0.0411).
- **Stability:** every reported research candidate improves mean R in both the January–July pre-development period and the August development period, passes month-breadth/retention gates, and has a positive paired session-bootstrap delta interval. This is internal historical stability, not independent confirmation.
- **Room versus entry behavior:** the room-based findings are not uniform. NEG_1 is `MIXED`; NEG_2 and NEG_3 are `EXIT_GEOMETRY_DEPENDENT`; NEG_1_4 is `ENTRY_BEHAVIOR_SUPPORTED`; other room combinations are mixed or geometry-dependent. Room exclusions therefore cannot be treated wholesale as entry-quality findings.
- **Research decision:** the frozen gates identify `EXCLUDE_NEG_1`, `EXCLUDE_NEG_4`, `EXCLUDE_NEG_1_2`, `EXCLUDE_NEG_1_4`, `EXCLUDE_NEG_1_2_4` as research exclusion candidates. That is enough only to justify a separately reviewed follow-up test; it does not justify changing BASE_SHORT, creating a forward candidate, or resuming paper trading.

No further combinations, thresholds, level types, time windows, or indicator buckets were searched. No exclusion is authorized for forward testing or live use by this report.

Source Stage 15 report hash: `f6ea0ed5e0166e41defcb92abd03ee70093fffeeb4b941a52bd0ff97fa3bd9df`
