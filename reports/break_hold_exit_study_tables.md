# Frozen First Hold exit study — complete tables

All primary metrics below use the **stop-first sensitivity scenario**, not reconstructed realized ordering. See the adjacent target-first and resolved-only diagnostics. Initial R is fixed. Event drawdown and streak are signal/event-ID ordered, include overlapping events, and are not account or mark-to-market measures.

Session bootstrap: 10,000 draws; seed 20260908; pointwise 95% intervals, not adjusted for selecting among 21 models. September is partial. Costs are round-trip dollars per share. Missing ATR is not imputed.

## All available entries


| Variant | n | Ambiguous | Mean R stop-first | Mean R target-first | Win % | PF | Event DD R | Losing streak | Mean R 95% CI | Mean R less $0.02 |
|---|---|---|---|---|---|---|---|---|---|---|
| USD025_TARGET_1R | 727 | 45 | -0.0591 | 0.0646 | 47.04% | 0.8883 | 73.0000 | 8 | [-0.1266, 0.0104] | -0.1391 |
| USD025_TARGET_1.5R | 727 | 26 | 0.0144 | 0.1039 | 40.58% | 1.0243 | 37.0000 | 10 | [-0.0720, 0.1062] | -0.0656 |
| USD025_TARGET_2R | 727 | 13 | 0.0440 | 0.0977 | 34.80% | 1.0675 | 46.0000 | 17 | [-0.0588, 0.1545] | -0.0360 |
| USD025_TARGET_2.5R | 727 | 8 | 0.0062 | 0.0447 | 28.75% | 1.0087 | 47.5000 | 18 | [-0.1001, 0.1204] | -0.0738 |
| USD025_TARGET_3R | 727 | 6 | 0.0179 | 0.0509 | 25.45% | 1.0240 | 59.0000 | 18 | [-0.0985, 0.1413] | -0.0621 |
| USD030_TARGET_1R | 727 | 26 | -0.0041 | 0.0674 | 49.79% | 0.9918 | 41.0000 | 10 | [-0.0742, 0.0673] | -0.0708 |
| USD030_TARGET_1.5R | 727 | 13 | 0.0523 | 0.0970 | 42.09% | 1.0903 | 37.5000 | 10 | [-0.0401, 0.1470] | -0.0144 |
| USD030_TARGET_2R | 727 | 6 | 0.0171 | 0.0419 | 33.98% | 1.0259 | 49.0000 | 13 | [-0.0833, 0.1238] | -0.0495 |
| USD030_TARGET_2.5R | 727 | 5 | 0.0274 | 0.0515 | 29.44% | 1.0389 | 47.5000 | 13 | [-0.0829, 0.1440] | -0.0392 |
| USD030_TARGET_3R | 727 | 4 | 0.0529 | 0.0749 | 26.41% | 1.0719 | 35.0000 | 13 | [-0.0696, 0.1874] | -0.0138 |
| ATR050_TARGET_1R | 394 | 1 | 0.1028 | 0.1079 | 55.08% | 1.2294 | 13.0000 | 6 | [0.0049, 0.2088] | 0.0473 |
| ATR050_TARGET_1.5R | 394 | 0 | 0.0926 | 0.0926 | 43.65% | 1.1648 | 19.0000 | 9 | [-0.0202, 0.2197] | 0.0371 |
| ATR050_TARGET_2R | 394 | 0 | 0.0825 | 0.0825 | 36.04% | 1.1292 | 24.0000 | 14 | [-0.0561, 0.2388] | 0.0270 |
| ATR050_TARGET_2.5R | 394 | 0 | 0.0761 | 0.0761 | 30.71% | 1.1101 | 30.5000 | 14 | [-0.0666, 0.2466] | 0.0206 |
| ATR050_TARGET_3R | 394 | 0 | 0.0828 | 0.0828 | 27.16% | 1.1138 | 25.0000 | 14 | [-0.0846, 0.2797] | 0.0273 |
| USD030_RECLAIM | 727 | 0 | 0.0864 | 0.0864 | 10.18% | 1.0994 | 73.7333 | 51 | [-0.1861, 0.4084] | 0.0198 |
| USD030_TIME_15 | 727 | 0 | 0.0432 | 0.0432 | 26.27% | 1.0602 | 55.9833 | 19 | [-0.1137, 0.2199] | -0.0235 |
| USD030_TIME_30 | 727 | 0 | 0.0276 | 0.0276 | 20.50% | 1.0350 | 91.6133 | 30 | [-0.1618, 0.2395] | -0.0391 |
| USD030_TIME_60 | 727 | 0 | 0.0790 | 0.0790 | 16.09% | 1.0946 | 78.8167 | 33 | [-0.1417, 0.3282] | 0.0124 |
| USD030_STRUCTURE_TRAIL | 727 | 0 | 0.1189 | 0.1189 | 15.96% | 1.1431 | 76.1870 | 33 | [-0.1318, 0.4092] | 0.0522 |
| USD030_TARGET_2R_BE1R | 727 | 10 | 0.0404 | 0.0748 | 27.51% | 1.0796 | 33.2837 | 10 | [-0.0434, 0.1290] | -0.0263 |

## Common available-ATR identities — all 21 models

Same 394 entries, so warm-up availability cannot drive comparisons.

| Variant | Mean R | Median R | Win % | PF | Event DD R | LOMO min R | Mean R 95% CI |
|---|---|---|---|---|---|---|---|
| USD025_TARGET_1R | 0.0051 | 1.0000 | 50.25% | 1.0102 | 19.0000 | -0.0171 | [-0.0876, 0.1035] |
| USD025_TARGET_1.5R | 0.0850 | -1.0000 | 43.40% | 1.1502 | 13.5000 | 0.0534 | [-0.0380, 0.2159] |
| USD025_TARGET_2R | 0.1117 | -1.0000 | 37.06% | 1.1774 | 15.0000 | 0.0614 | [-0.0331, 0.2636] |
| USD025_TARGET_2.5R | 0.0749 | -1.0000 | 30.71% | 1.1081 | 20.5000 | 0.0132 | [-0.0774, 0.2383] |
| USD025_TARGET_3R | 0.0863 | -1.0000 | 27.16% | 1.1185 | 21.0000 | 0.0058 | [-0.0896, 0.2722] |
| USD030_TARGET_1R | 0.0558 | 1.0000 | 52.79% | 1.1183 | 11.0000 | 0.0234 | [-0.0415, 0.1600] |
| USD030_TARGET_1.5R | 0.1231 | -1.0000 | 44.92% | 1.2235 | 14.0000 | 0.0746 | [-0.0036, 0.2569] |
| USD030_TARGET_2R | 0.0925 | -1.0000 | 36.55% | 1.1458 | 28.0000 | 0.0218 | [-0.0561, 0.2537] |
| USD030_TARGET_2.5R | 0.1141 | -1.0000 | 31.98% | 1.1677 | 24.0000 | 0.0276 | [-0.0551, 0.2972] |
| USD030_TARGET_3R | 0.1204 | -1.0000 | 28.17% | 1.1677 | 39.0000 | 0.0452 | [-0.0586, 0.3222] |
| ATR050_TARGET_1R | 0.1028 | 1.0000 | 55.08% | 1.2294 | 13.0000 | 0.0585 | [0.0049, 0.2088] |
| ATR050_TARGET_1.5R | 0.0926 | -1.0000 | 43.65% | 1.1648 | 19.0000 | 0.0526 | [-0.0202, 0.2197] |
| ATR050_TARGET_2R | 0.0825 | -1.0000 | 36.04% | 1.1292 | 24.0000 | 0.0216 | [-0.0561, 0.2388] |
| ATR050_TARGET_2.5R | 0.0761 | -1.0000 | 30.71% | 1.1101 | 30.5000 | 0.0101 | [-0.0666, 0.2466] |
| ATR050_TARGET_3R | 0.0828 | -1.0000 | 27.16% | 1.1138 | 25.0000 | 0.0104 | [-0.0846, 0.2797] |
| USD030_RECLAIM | 0.1728 | -1.0000 | 12.69% | 1.2084 | 57.7000 | 0.0624 | [-0.1752, 0.5901] |
| USD030_TIME_15 | 0.0979 | -1.0000 | 30.96% | 1.1483 | 38.8667 | 0.0254 | [-0.1073, 0.3498] |
| USD030_TIME_30 | -0.0010 | -1.0000 | 23.35% | 0.9987 | 58.1640 | -0.0874 | [-0.2275, 0.2700] |
| USD030_TIME_60 | 0.0592 | -1.0000 | 18.27% | 1.0728 | 53.4900 | -0.0579 | [-0.2210, 0.3982] |
| USD030_STRUCTURE_TRAIL | 0.1185 | -1.0000 | 18.27% | 1.1471 | 48.3333 | -0.0424 | [-0.1874, 0.4921] |
| USD030_TARGET_2R_BE1R | 0.0943 | 0.0000 | 28.93% | 1.1963 | 16.0000 | 0.0527 | [-0.0260, 0.2225] |

## USD025_TARGET_1R

Membership/status counts: `{'RESOLVED': 682, 'UNAVAILABLE_ENTRY': 6, 'AMBIGUOUS_STOP_TARGET': 45}`. Exit reasons: `{'TARGET_TOUCH': 342, 'STOP_TOUCH': 339, 'SAME_MINUTE_STOP_TARGET': 45, 'STOP_GAP': 1}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 727 | 170 | 47.04% | 1.0000 | -1.0000 | 0.2500 | -0.2500 | -0.0591 | -1.0000 | 0.8883 | 73.0000 | 8 | [-0.1266, 0.0104] |
| LONG | 397 | 137 | 45.59% | 1.0000 | -1.0000 | 0.2500 | -0.2500 | -0.0882 | -1.0000 | 0.8380 | 49.0000 | 9 | [-0.1818, 0.0084] |
| SHORT | 330 | 128 | 48.79% | 1.0000 | -1.0000 | 0.2500 | -0.2500 | -0.0242 | -1.0000 | 0.9527 | 29.0000 | 8 | [-0.1239, 0.0765] |

Win-rate 95% CI (fractions): [0.4367, 0.5052]; target-first mean-R CI: [-0.0074, 0.1400]. Positive/negative months: 3/6; worst month mean R: -0.1919; LOMO minimum mean R: -0.0886. Session-sum drawdown R: 72.0000.

Paired stop-first delta versus $0.30/2R on this model's available identities: -0.0763 R, 95% CI [-0.1611, 0.0058], n=727. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 727 | -0.0591 | -1.0000 | 47.04% | 0.8883 | 73.0000 | 8 |
| Target-first | 727 | 0.0646 | 1.0000 | 53.23% | 1.1382 | 27.0000 | 8 |
| Resolved only (selection diagnostic) | 682 | 0.0029 | 1.0000 | 50.15% | 1.0059 | 42.0000 | 8 |
| $0.01 RT cost / stop-first | 727 | -0.0991 | -1.0400 | 47.04% | 0.8200 | 97.2000 | 8 |
| $0.02 RT cost / stop-first | 727 | -0.1391 | -1.0800 | 47.04% | 0.7567 | 123.8000 | 8 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 84 | 0.1667 | 1.0000 | 58.33% | 1.4000 | 1.0000 | -1.0000 |
| 2026-02 | 74 | 0.0270 | 1.0000 | 51.35% | 1.0556 | 1.0000 | -1.0000 |
| 2026-03 | 98 | -0.0408 | -1.0000 | 47.96% | 0.9216 | 1.0000 | -1.0000 |
| 2026-04 | 94 | -0.1702 | -1.0000 | 41.49% | 0.7091 | 1.0000 | -1.0000 |
| 2026-05 | 99 | -0.1919 | -1.0000 | 40.40% | 0.6780 | 1.0000 | -1.0000 |
| 2026-06 | 79 | -0.0633 | -1.0000 | 46.84% | 0.8810 | 1.0000 | -1.0000 |
| 2026-07 | 83 | -0.0843 | -1.0000 | 45.78% | 0.8444 | 1.0000 | -1.0000 |
| 2026-08 | 103 | -0.1068 | -1.0000 | 44.66% | 0.8070 | 1.0000 | -1.0000 |
| 2026-09 | 13 | 0.2308 | 1.0000 | 61.54% | 1.6000 | 1.0000 | -1.0000 |

## USD025_TARGET_1.5R

Membership/status counts: `{'RESOLVED': 701, 'UNAVAILABLE_ENTRY': 6, 'AMBIGUOUS_STOP_TARGET': 26}`. Exit reasons: `{'STOP_TOUCH': 405, 'TARGET_TOUCH': 295, 'SAME_MINUTE_STOP_TARGET': 26, 'STOP_GAP': 1}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 727 | 170 | 40.58% | 1.5000 | -1.0000 | 0.3750 | -0.2500 | 0.0144 | -1.0000 | 1.0243 | 37.0000 | 10 | [-0.0720, 0.1062] |
| LONG | 397 | 137 | 37.03% | 1.5000 | -1.0000 | 0.3750 | -0.2500 | -0.0743 | -1.0000 | 0.8820 | 36.5000 | 11 | [-0.1863, 0.0440] |
| SHORT | 330 | 128 | 44.85% | 1.5000 | -1.0000 | 0.3750 | -0.2500 | 0.1212 | -1.0000 | 1.2198 | 13.0000 | 9 | [-0.0090, 0.2500] |

Win-rate 95% CI (fractions): [0.3712, 0.4425]; target-first mean-R CI: [0.0104, 0.2007]. Positive/negative months: 6/3; worst month mean R: -0.1162; LOMO minimum mean R: -0.0064. Session-sum drawdown R: 35.5000.

Paired stop-first delta versus $0.30/2R on this model's available identities: -0.0027 R, 95% CI [-0.0757, 0.0706], n=727. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 727 | 0.0144 | -1.0000 | 40.58% | 1.0243 | 37.0000 | 10 |
| Target-first | 727 | 0.1039 | -1.0000 | 44.15% | 1.1860 | 21.0000 | 10 |
| Resolved only (selection diagnostic) | 701 | 0.0521 | -1.0000 | 42.08% | 1.0899 | 24.0000 | 10 |
| $0.01 RT cost / stop-first | 727 | -0.0256 | -1.0400 | 40.58% | 0.9586 | 50.4800 | 10 |
| $0.02 RT cost / stop-first | 727 | -0.0656 | -1.0800 | 40.58% | 0.8978 | 66.9200 | 10 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 84 | 0.1012 | -1.0000 | 44.05% | 1.1809 | 1.5000 | -1.0000 |
| 2026-02 | 74 | 0.0135 | -1.0000 | 40.54% | 1.0227 | 1.5000 | -1.0000 |
| 2026-03 | 98 | 0.1480 | -1.0000 | 45.92% | 1.2736 | 1.5000 | -1.0000 |
| 2026-04 | 94 | -0.0160 | -1.0000 | 39.36% | 0.9737 | 1.5000 | -1.0000 |
| 2026-05 | 99 | -0.1162 | -1.0000 | 35.35% | 0.8203 | 1.5000 | -1.0000 |
| 2026-06 | 79 | 0.0127 | -1.0000 | 40.51% | 1.0213 | 1.5000 | -1.0000 |
| 2026-07 | 83 | 0.0542 | -1.0000 | 42.17% | 1.0938 | 1.5000 | -1.0000 |
| 2026-08 | 103 | -0.0777 | -1.0000 | 36.89% | 0.8769 | 1.5000 | -1.0000 |
| 2026-09 | 13 | 0.1538 | -1.0000 | 46.15% | 1.2857 | 1.5000 | -1.0000 |

## USD025_TARGET_2R

Membership/status counts: `{'RESOLVED': 714, 'UNAVAILABLE_ENTRY': 6, 'AMBIGUOUS_STOP_TARGET': 13}`. Exit reasons: `{'STOP_TOUCH': 460, 'TARGET_TOUCH': 253, 'SAME_MINUTE_STOP_TARGET': 13, 'STOP_GAP': 1}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 727 | 170 | 34.80% | 2.0000 | -1.0000 | 0.5000 | -0.2500 | 0.0440 | -1.0000 | 1.0675 | 46.0000 | 17 | [-0.0588, 0.1545] |
| LONG | 397 | 137 | 31.99% | 2.0000 | -1.0000 | 0.5000 | -0.2500 | -0.0403 | -1.0000 | 0.9407 | 32.0000 | 13 | [-0.1774, 0.1035] |
| SHORT | 330 | 128 | 38.18% | 2.0000 | -1.0000 | 0.5000 | -0.2500 | 0.1455 | -1.0000 | 1.2353 | 18.0000 | 11 | [-0.0058, 0.3012] |

Win-rate 95% CI (fractions): [0.3137, 0.3848]; target-first mean-R CI: [-0.0077, 0.2092]. Positive/negative months: 6/3; worst month mean R: -0.1212; LOMO minimum mean R: 0.0064. Session-sum drawdown R: 46.0000.

Paired stop-first delta versus $0.30/2R on this model's available identities: 0.0269 R, 95% CI [-0.0353, 0.0897], n=727. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 727 | 0.0440 | -1.0000 | 34.80% | 1.0675 | 46.0000 | 17 |
| Target-first | 727 | 0.0977 | -1.0000 | 36.59% | 1.1540 | 29.0000 | 14 |
| Resolved only (selection diagnostic) | 714 | 0.0630 | -1.0000 | 35.43% | 1.0976 | 39.0000 | 16 |
| $0.01 RT cost / stop-first | 727 | 0.0040 | -1.0400 | 34.80% | 1.0059 | 59.4800 | 17 |
| $0.02 RT cost / stop-first | 727 | -0.0360 | -1.0800 | 34.80% | 0.9489 | 72.9600 | 17 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 84 | 0.1071 | -1.0000 | 36.90% | 1.1698 | 2.0000 | -1.0000 |
| 2026-02 | 74 | 0.0946 | -1.0000 | 36.49% | 1.1489 | 2.0000 | -1.0000 |
| 2026-03 | 98 | 0.2857 | -1.0000 | 42.86% | 1.5000 | 2.0000 | -1.0000 |
| 2026-04 | 94 | 0.0213 | -1.0000 | 34.04% | 1.0323 | 2.0000 | -1.0000 |
| 2026-05 | 99 | -0.1212 | -1.0000 | 29.29% | 0.8286 | 2.0000 | -1.0000 |
| 2026-06 | 79 | 0.1013 | -1.0000 | 36.71% | 1.1600 | 2.0000 | -1.0000 |
| 2026-07 | 83 | -0.0241 | -1.0000 | 32.53% | 0.9643 | 2.0000 | -1.0000 |
| 2026-08 | 103 | -0.0971 | -1.0000 | 30.10% | 0.8611 | 2.0000 | -1.0000 |
| 2026-09 | 13 | 0.1538 | -1.0000 | 38.46% | 1.2500 | 2.0000 | -1.0000 |

## USD025_TARGET_2.5R

Membership/status counts: `{'RESOLVED': 719, 'UNAVAILABLE_ENTRY': 6, 'AMBIGUOUS_STOP_TARGET': 8}`. Exit reasons: `{'STOP_TOUCH': 509, 'TARGET_TOUCH': 209, 'SAME_MINUTE_STOP_TARGET': 8, 'STOP_GAP': 1}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 727 | 170 | 28.75% | 2.5000 | -1.0000 | 0.6250 | -0.2500 | 0.0062 | -1.0000 | 1.0087 | 47.5000 | 18 | [-0.1001, 0.1204] |
| LONG | 397 | 137 | 25.19% | 2.5000 | -1.0000 | 0.6250 | -0.2500 | -0.1184 | -1.0000 | 0.8418 | 59.0000 | 19 | [-0.2547, 0.0263] |
| SHORT | 330 | 128 | 33.03% | 2.5000 | -1.0000 | 0.6250 | -0.2500 | 0.1561 | -1.0000 | 1.2330 | 16.0000 | 11 | [-0.0106, 0.3285] |

Win-rate 95% CI (fractions): [0.2571, 0.3201]; target-first mean-R CI: [-0.0655, 0.1601]. Positive/negative months: 4/5; worst month mean R: -0.1436; LOMO minimum mean R: -0.0429. Session-sum drawdown R: 44.5000.

Paired stop-first delta versus $0.30/2R on this model's available identities: -0.0109 R, 95% CI [-0.0616, 0.0371], n=727. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 727 | 0.0062 | -1.0000 | 28.75% | 1.0087 | 47.5000 | 18 |
| Target-first | 727 | 0.0447 | -1.0000 | 29.85% | 1.0637 | 34.5000 | 14 |
| Resolved only (selection diagnostic) | 719 | 0.0174 | -1.0000 | 29.07% | 1.0245 | 41.5000 | 17 |
| $0.01 RT cost / stop-first | 727 | -0.0338 | -1.0400 | 28.75% | 0.9544 | 60.7400 | 18 |
| $0.02 RT cost / stop-first | 727 | -0.0738 | -1.0800 | 28.75% | 0.9041 | 78.1000 | 18 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 84 | -0.1250 | -1.0000 | 25.00% | 0.8333 | 2.5000 | -1.0000 |
| 2026-02 | 74 | 0.0878 | -1.0000 | 31.08% | 1.1275 | 2.5000 | -1.0000 |
| 2026-03 | 98 | 0.3214 | -1.0000 | 37.76% | 1.5164 | 2.5000 | -1.0000 |
| 2026-04 | 94 | -0.1436 | -1.0000 | 24.47% | 0.8099 | 2.5000 | -1.0000 |
| 2026-05 | 99 | -0.1162 | -1.0000 | 25.25% | 0.8446 | 2.5000 | -1.0000 |
| 2026-06 | 79 | 0.1962 | -1.0000 | 34.18% | 1.2981 | 2.5000 | -1.0000 |
| 2026-07 | 83 | -0.1145 | -1.0000 | 25.30% | 0.8468 | 2.5000 | -1.0000 |
| 2026-08 | 103 | -0.0825 | -1.0000 | 26.21% | 0.8882 | 2.5000 | -1.0000 |
| 2026-09 | 13 | 0.3462 | -1.0000 | 38.46% | 1.5625 | 2.5000 | -1.0000 |

## USD025_TARGET_3R

Membership/status counts: `{'RESOLVED': 721, 'UNAVAILABLE_ENTRY': 6, 'AMBIGUOUS_STOP_TARGET': 6}`. Exit reasons: `{'STOP_TOUCH': 535, 'TARGET_TOUCH': 185, 'SAME_MINUTE_STOP_TARGET': 6, 'STOP_GAP': 1}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 727 | 170 | 25.45% | 3.0000 | -1.0000 | 0.7500 | -0.2500 | 0.0179 | -1.0000 | 1.0240 | 59.0000 | 18 | [-0.0985, 0.1413] |
| LONG | 397 | 137 | 21.91% | 3.0000 | -1.0000 | 0.7500 | -0.2500 | -0.1234 | -1.0000 | 0.8419 | 66.0000 | 19 | [-0.2655, 0.0295] |
| SHORT | 330 | 128 | 29.70% | 3.0000 | -1.0000 | 0.7500 | -0.2500 | 0.1879 | -1.0000 | 1.2672 | 30.0000 | 12 | [0.0031, 0.3846] |

Win-rate 95% CI (fractions): [0.2254, 0.2853]; target-first mean-R CI: [-0.0705, 0.1796]. Positive/negative months: 4/5; worst month mean R: -0.1919; LOMO minimum mean R: -0.0397. Session-sum drawdown R: 57.0000.

Paired stop-first delta versus $0.30/2R on this model's available identities: 0.0008 R, 95% CI [-0.0717, 0.0720], n=727. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 727 | 0.0179 | -1.0000 | 25.45% | 1.0240 | 59.0000 | 18 |
| Target-first | 727 | 0.0509 | -1.0000 | 26.27% | 1.0690 | 39.0000 | 15 |
| Resolved only (selection diagnostic) | 721 | 0.0264 | -1.0000 | 25.66% | 1.0354 | 54.0000 | 17 |
| $0.01 RT cost / stop-first | 727 | -0.0221 | -1.0400 | 25.45% | 0.9715 | 76.0800 | 18 |
| $0.02 RT cost / stop-first | 727 | -0.0621 | -1.0800 | 25.45% | 0.9229 | 93.1600 | 18 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 84 | -0.0476 | -1.0000 | 23.81% | 0.9375 | 3.0000 | -1.0000 |
| 2026-02 | 74 | 0.1892 | -1.0000 | 29.73% | 1.2692 | 3.0000 | -1.0000 |
| 2026-03 | 98 | 0.3878 | -1.0000 | 34.69% | 1.5938 | 3.0000 | -1.0000 |
| 2026-04 | 94 | -0.1915 | -1.0000 | 20.21% | 0.7600 | 3.0000 | -1.0000 |
| 2026-05 | 99 | -0.1919 | -1.0000 | 20.20% | 0.7595 | 3.0000 | -1.0000 |
| 2026-06 | 79 | 0.1646 | -1.0000 | 29.11% | 1.2321 | 3.0000 | -1.0000 |
| 2026-07 | 83 | -0.0843 | -1.0000 | 22.89% | 0.8906 | 3.0000 | -1.0000 |
| 2026-08 | 103 | -0.1068 | -1.0000 | 22.33% | 0.8625 | 3.0000 | -1.0000 |
| 2026-09 | 13 | 0.5385 | -1.0000 | 38.46% | 1.8750 | 3.0000 | -1.0000 |

## USD030_TARGET_1R

Membership/status counts: `{'RESOLVED': 701, 'UNAVAILABLE_ENTRY': 6, 'AMBIGUOUS_STOP_TARGET': 26}`. Exit reasons: `{'TARGET_TOUCH': 362, 'STOP_TOUCH': 339, 'SAME_MINUTE_STOP_TARGET': 26}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 727 | 170 | 49.79% | 1.0000 | -1.0000 | 0.3000 | -0.3000 | -0.0041 | -1.0000 | 0.9918 | 41.0000 | 10 | [-0.0742, 0.0673] |
| LONG | 397 | 137 | 48.61% | 1.0000 | -1.0000 | 0.3000 | -0.3000 | -0.0277 | -1.0000 | 0.9461 | 26.0000 | 11 | [-0.1218, 0.0670] |
| SHORT | 330 | 128 | 51.21% | 1.0000 | -1.0000 | 0.3000 | -0.3000 | 0.0242 | 1.0000 | 1.0497 | 19.0000 | 9 | [-0.0822, 0.1329] |

Win-rate 95% CI (fractions): [0.4629, 0.5336]; target-first mean-R CI: [-0.0082, 0.1438]. Positive/negative months: 5/4; worst month mean R: -0.1068; LOMO minimum mean R: -0.0207. Session-sum drawdown R: 40.0000.

Paired stop-first delta versus $0.30/2R on this model's available identities: -0.0213 R, 95% CI [-0.0935, 0.0503], n=727. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 727 | -0.0041 | -1.0000 | 49.79% | 0.9918 | 41.0000 | 10 |
| Target-first | 727 | 0.0674 | 1.0000 | 53.37% | 1.1445 | 20.0000 | 10 |
| Resolved only (selection diagnostic) | 701 | 0.0328 | 1.0000 | 51.64% | 1.0678 | 26.0000 | 10 |
| $0.01 RT cost / stop-first | 727 | -0.0375 | -1.0333 | 49.79% | 0.9278 | 53.2333 | 10 |
| $0.02 RT cost / stop-first | 727 | -0.0708 | -1.0667 | 49.79% | 0.8678 | 72.6667 | 10 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 84 | 0.0952 | 1.0000 | 54.76% | 1.2105 | 1.0000 | -1.0000 |
| 2026-02 | 74 | 0.0270 | 1.0000 | 51.35% | 1.0556 | 1.0000 | -1.0000 |
| 2026-03 | 98 | 0.1020 | 1.0000 | 55.10% | 1.2273 | 1.0000 | -1.0000 |
| 2026-04 | 94 | -0.0638 | -1.0000 | 46.81% | 0.8800 | 1.0000 | -1.0000 |
| 2026-05 | 99 | -0.0909 | -1.0000 | 45.45% | 0.8333 | 1.0000 | -1.0000 |
| 2026-06 | 79 | -0.0633 | -1.0000 | 46.84% | 0.8810 | 1.0000 | -1.0000 |
| 2026-07 | 83 | 0.0361 | 1.0000 | 51.81% | 1.0750 | 1.0000 | -1.0000 |
| 2026-08 | 103 | -0.1068 | -1.0000 | 44.66% | 0.8070 | 1.0000 | -1.0000 |
| 2026-09 | 13 | 0.3846 | 1.0000 | 69.23% | 2.2500 | 1.0000 | -1.0000 |

## USD030_TARGET_1.5R

Membership/status counts: `{'RESOLVED': 714, 'UNAVAILABLE_ENTRY': 6, 'AMBIGUOUS_STOP_TARGET': 13}`. Exit reasons: `{'TARGET_TOUCH': 304, 'STOP_TOUCH': 408, 'SAME_MINUTE_STOP_TARGET': 13, 'TARGET_GAP': 2}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 727 | 170 | 42.09% | 1.5000 | -1.0000 | 0.4500 | -0.3000 | 0.0523 | -1.0000 | 1.0903 | 37.5000 | 10 | [-0.0401, 0.1470] |
| LONG | 397 | 137 | 41.06% | 1.5000 | -1.0000 | 0.4500 | -0.3000 | 0.0264 | -1.0000 | 1.0449 | 22.0000 | 11 | [-0.0936, 0.1503] |
| SHORT | 330 | 128 | 43.33% | 1.5000 | -1.0000 | 0.4500 | -0.3000 | 0.0833 | -1.0000 | 1.1471 | 20.5000 | 9 | [-0.0488, 0.2167] |

Win-rate 95% CI (fractions): [0.3840, 0.4588]; target-first mean-R CI: [0.0013, 0.1935]. Positive/negative months: 6/3; worst month mean R: -0.1019; LOMO minimum mean R: 0.0175. Session-sum drawdown R: 35.5000.

Paired stop-first delta versus $0.30/2R on this model's available identities: 0.0351 R, 95% CI [-0.0154, 0.0868], n=727. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 727 | 0.0523 | -1.0000 | 42.09% | 1.0903 | 37.5000 | 10 |
| Target-first | 727 | 0.0970 | -1.0000 | 43.88% | 1.1728 | 25.0000 | 10 |
| Resolved only (selection diagnostic) | 714 | 0.0714 | -1.0000 | 42.86% | 1.1250 | 29.5000 | 10 |
| $0.01 RT cost / stop-first | 727 | 0.0189 | -1.0333 | 42.09% | 1.0316 | 48.1667 | 10 |
| $0.02 RT cost / stop-first | 727 | -0.0144 | -1.0667 | 42.09% | 0.9767 | 58.8333 | 10 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 84 | 0.0714 | -1.0000 | 42.86% | 1.1250 | 1.5000 | -1.0000 |
| 2026-02 | 74 | 0.0473 | -1.0000 | 41.89% | 1.0814 | 1.5000 | -1.0000 |
| 2026-03 | 98 | 0.2755 | 1.5000 | 51.02% | 1.5625 | 1.5000 | -1.0000 |
| 2026-04 | 94 | 0.1170 | -1.0000 | 44.68% | 1.2115 | 1.5000 | -1.0000 |
| 2026-05 | 99 | -0.0404 | -1.0000 | 38.38% | 0.9344 | 1.5000 | -1.0000 |
| 2026-06 | 79 | 0.0443 | -1.0000 | 41.77% | 1.0761 | 1.5000 | -1.0000 |
| 2026-07 | 83 | -0.0060 | -1.0000 | 39.76% | 0.9900 | 1.5000 | -1.0000 |
| 2026-08 | 103 | -0.1019 | -1.0000 | 35.92% | 0.8409 | 1.5000 | -1.0000 |
| 2026-09 | 13 | 0.1538 | -1.0000 | 46.15% | 1.2857 | 1.5000 | -1.0000 |

## USD030_TARGET_2R

Membership/status counts: `{'RESOLVED': 721, 'UNAVAILABLE_ENTRY': 6, 'AMBIGUOUS_STOP_TARGET': 6}`. Exit reasons: `{'TARGET_TOUCH': 246, 'STOP_TOUCH': 474, 'SAME_MINUTE_STOP_TARGET': 6, 'EOD_CLOSE': 1}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 727 | 170 | 33.98% | 1.9937 | -1.0000 | 0.5981 | -0.3000 | 0.0171 | -1.0000 | 1.0259 | 49.0000 | 13 | [-0.0833, 0.1238] |
| LONG | 397 | 137 | 31.99% | 1.9878 | -1.0000 | 0.5963 | -0.3000 | -0.0442 | -1.0000 | 0.9350 | 39.0000 | 11 | [-0.1784, 0.0969] |
| SHORT | 330 | 128 | 36.36% | 2.0000 | -1.0000 | 0.6000 | -0.3000 | 0.0909 | -1.0000 | 1.1429 | 22.0000 | 9 | [-0.0526, 0.2397] |

Win-rate 95% CI (fractions): [0.3062, 0.3753]; target-first mean-R CI: [-0.0597, 0.1486]. Positive/negative months: 4/5; worst month mean R: -0.1553; LOMO minimum mean R: -0.0343. Session-sum drawdown R: 49.0000.

Paired stop-first delta versus $0.30/2R on this model's available identities: 0.0000 R, 95% CI [0.0000, 0.0000], n=727. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 727 | 0.0171 | -1.0000 | 33.98% | 1.0259 | 49.0000 | 13 |
| Target-first | 727 | 0.0419 | -1.0000 | 34.80% | 1.0642 | 36.0000 | 13 |
| Resolved only (selection diagnostic) | 721 | 0.0256 | -1.0000 | 34.26% | 1.0389 | 44.0000 | 13 |
| $0.01 RT cost / stop-first | 727 | -0.0162 | -1.0333 | 33.98% | 0.9762 | 60.2333 | 13 |
| $0.02 RT cost / stop-first | 727 | -0.0495 | -1.0667 | 33.98% | 0.9297 | 71.4667 | 13 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 84 | -0.1071 | -1.0000 | 29.76% | 0.8475 | 2.0000 | -1.0000 |
| 2026-02 | 74 | -0.0270 | -1.0000 | 32.43% | 0.9600 | 2.0000 | -1.0000 |
| 2026-03 | 98 | 0.3469 | -1.0000 | 44.90% | 1.6296 | 2.0000 | -1.0000 |
| 2026-04 | 94 | 0.0686 | -1.0000 | 36.17% | 1.1075 | 1.9544 | -1.0000 |
| 2026-05 | 99 | -0.1212 | -1.0000 | 29.29% | 0.8286 | 2.0000 | -1.0000 |
| 2026-06 | 79 | 0.1772 | -1.0000 | 39.24% | 1.2917 | 2.0000 | -1.0000 |
| 2026-07 | 83 | -0.0602 | -1.0000 | 31.33% | 0.9123 | 2.0000 | -1.0000 |
| 2026-08 | 103 | -0.1553 | -1.0000 | 28.16% | 0.7838 | 2.0000 | -1.0000 |
| 2026-09 | 13 | 0.1538 | -1.0000 | 38.46% | 1.2500 | 2.0000 | -1.0000 |

## USD030_TARGET_2.5R

Membership/status counts: `{'RESOLVED': 722, 'UNAVAILABLE_ENTRY': 6, 'AMBIGUOUS_STOP_TARGET': 5}`. Exit reasons: `{'STOP_TOUCH': 508, 'TARGET_TOUCH': 213, 'SAME_MINUTE_STOP_TARGET': 5, 'EOD_CLOSE': 1}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 727 | 170 | 29.44% | 2.4904 | -1.0000 | 0.7471 | -0.3000 | 0.0274 | -1.0000 | 1.0389 | 47.5000 | 13 | [-0.0829, 0.1440] |
| LONG | 397 | 137 | 26.70% | 2.4807 | -1.0000 | 0.7442 | -0.3000 | -0.0707 | -1.0000 | 0.9036 | 42.0000 | 14 | [-0.2109, 0.0768] |
| SHORT | 330 | 128 | 32.73% | 2.5000 | -1.0000 | 0.7500 | -0.3000 | 0.1455 | -1.0000 | 1.2162 | 25.0000 | 12 | [-0.0170, 0.3190] |

Win-rate 95% CI (fractions): [0.2631, 0.3276]; target-first mean-R CI: [-0.0618, 0.1696]. Positive/negative months: 5/4; worst month mean R: -0.2184; LOMO minimum mean R: -0.0351. Session-sum drawdown R: 45.0000.

Paired stop-first delta versus $0.30/2R on this model's available identities: 0.0103 R, 95% CI [-0.0443, 0.0619], n=727. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 727 | 0.0274 | -1.0000 | 29.44% | 1.0389 | 47.5000 | 13 |
| Target-first | 727 | 0.0515 | -1.0000 | 30.12% | 1.0737 | 37.0000 | 13 |
| Resolved only (selection diagnostic) | 722 | 0.0346 | -1.0000 | 29.64% | 1.0491 | 43.5000 | 13 |
| $0.01 RT cost / stop-first | 727 | -0.0059 | -1.0333 | 29.44% | 0.9919 | 58.5333 | 13 |
| $0.02 RT cost / stop-first | 727 | -0.0392 | -1.0667 | 29.44% | 0.9479 | 72.5177 | 13 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 84 | -0.0833 | -1.0000 | 26.19% | 0.8871 | 2.5000 | -1.0000 |
| 2026-02 | 74 | 0.0405 | -1.0000 | 29.73% | 1.0577 | 2.5000 | -1.0000 |
| 2026-03 | 98 | 0.4286 | -1.0000 | 40.82% | 1.7241 | 2.5000 | -1.0000 |
| 2026-04 | 94 | -0.0165 | -1.0000 | 28.72% | 0.9769 | 2.4240 | -1.0000 |
| 2026-05 | 99 | -0.1515 | -1.0000 | 24.24% | 0.8000 | 2.5000 | -1.0000 |
| 2026-06 | 79 | 0.1519 | -1.0000 | 32.91% | 1.2264 | 2.5000 | -1.0000 |
| 2026-07 | 83 | 0.0542 | -1.0000 | 30.12% | 1.0776 | 2.5000 | -1.0000 |
| 2026-08 | 103 | -0.2184 | -1.0000 | 22.33% | 0.7188 | 2.5000 | -1.0000 |
| 2026-09 | 13 | 0.3462 | -1.0000 | 38.46% | 1.5625 | 2.5000 | -1.0000 |

## USD030_TARGET_3R

Membership/status counts: `{'RESOLVED': 723, 'UNAVAILABLE_ENTRY': 6, 'AMBIGUOUS_STOP_TARGET': 4}`. Exit reasons: `{'STOP_TOUCH': 531, 'TARGET_TOUCH': 191, 'SAME_MINUTE_STOP_TARGET': 4, 'EOD_CLOSE': 1}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 727 | 170 | 26.41% | 2.9867 | -1.0000 | 0.8960 | -0.3000 | 0.0529 | -1.0000 | 1.0719 | 35.0000 | 13 | [-0.0696, 0.1874] |
| LONG | 397 | 137 | 23.93% | 2.9731 | -1.0000 | 0.8919 | -0.3000 | -0.0492 | -1.0000 | 0.9353 | 43.0000 | 14 | [-0.2111, 0.1213] |
| SHORT | 330 | 128 | 29.39% | 3.0000 | -1.0000 | 0.9000 | -0.3000 | 0.1758 | -1.0000 | 1.2489 | 26.0000 | 14 | [-0.0029, 0.3711] |

Win-rate 95% CI (fractions): [0.2333, 0.2975]; target-first mean-R CI: [-0.0495, 0.2111]. Positive/negative months: 4/5; worst month mean R: -0.1892; LOMO minimum mean R: -0.0056. Session-sum drawdown R: 33.0000.

Paired stop-first delta versus $0.30/2R on this model's available identities: 0.0358 R, 95% CI [-0.0379, 0.1097], n=727. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 727 | 0.0529 | -1.0000 | 26.41% | 1.0719 | 35.0000 | 13 |
| Target-first | 727 | 0.0749 | -1.0000 | 26.96% | 1.1025 | 35.0000 | 13 |
| Resolved only (selection diagnostic) | 723 | 0.0587 | -1.0000 | 26.56% | 1.0799 | 35.0000 | 13 |
| $0.01 RT cost / stop-first | 727 | 0.0196 | -1.0333 | 26.41% | 1.0257 | 38.6000 | 13 |
| $0.02 RT cost / stop-first | 727 | -0.0138 | -1.0667 | 26.41% | 0.9824 | 46.0177 | 13 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 84 | -0.0476 | -1.0000 | 23.81% | 0.9375 | 3.0000 | -1.0000 |
| 2026-02 | 74 | -0.1892 | -1.0000 | 20.27% | 0.7627 | 3.0000 | -1.0000 |
| 2026-03 | 98 | 0.4286 | -1.0000 | 35.71% | 1.6667 | 3.0000 | -1.0000 |
| 2026-04 | 94 | -0.0484 | -1.0000 | 24.47% | 0.9359 | 2.8891 | -1.0000 |
| 2026-05 | 99 | -0.1111 | -1.0000 | 22.22% | 0.8571 | 3.0000 | -1.0000 |
| 2026-06 | 79 | 0.2152 | -1.0000 | 30.38% | 1.3091 | 3.0000 | -1.0000 |
| 2026-07 | 83 | 0.2048 | -1.0000 | 30.12% | 1.2931 | 3.0000 | -1.0000 |
| 2026-08 | 103 | -0.1068 | -1.0000 | 22.33% | 0.8625 | 3.0000 | -1.0000 |
| 2026-09 | 13 | 0.5385 | -1.0000 | 38.46% | 1.8750 | 3.0000 | -1.0000 |

## ATR050_TARGET_1R

Membership/status counts: `{'UNAVAILABLE_ATR': 333, 'RESOLVED': 393, 'UNAVAILABLE_ENTRY': 6, 'AMBIGUOUS_STOP_TARGET': 1}`. Exit reasons: `{'TARGET_TOUCH': 217, 'STOP_TOUCH': 175, 'EOD_CLOSE': 1, 'SAME_MINUTE_STOP_TARGET': 1}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 394 | 112 | 55.08% | 1.0000 | -0.9972 | 0.4418 | -0.4196 | 0.1028 | 1.0000 | 1.2294 | 13.0000 | 6 | [0.0049, 0.2088] |
| LONG | 212 | 79 | 50.94% | 1.0000 | -1.0000 | 0.4481 | -0.4311 | 0.0189 | 1.0000 | 1.0385 | 14.0000 | 7 | [-0.1062, 0.1477] |
| SHORT | 182 | 80 | 59.89% | 1.0000 | -0.9932 | 0.4355 | -0.4033 | 0.2005 | 1.0000 | 1.5033 | 8.0000 | 6 | [0.0414, 0.3721] |

Win-rate 95% CI (fractions): [0.5013, 0.6038]; target-first mean-R CI: [0.0108, 0.2131]. Positive/negative months: 6/3; worst month mean R: -0.1892; LOMO minimum mean R: 0.0585. Session-sum drawdown R: 12.0000.

Paired stop-first delta versus $0.30/2R on this model's available identities: 0.0103 R, 95% CI [-0.1071, 0.1238], n=394. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 394 | 0.1028 | 1.0000 | 55.08% | 1.2294 | 13.0000 | 6 |
| Target-first | 394 | 0.1079 | 1.0000 | 55.33% | 1.2421 | 13.0000 | 6 |
| Resolved only (selection diagnostic) | 393 | 0.1056 | 1.0000 | 55.22% | 1.2364 | 13.0000 | 6 |
| $0.01 RT cost / stop-first | 394 | 0.0750 | 0.9542 | 55.08% | 1.1629 | 15.5007 | 6 |
| $0.02 RT cost / stop-first | 394 | 0.0473 | 0.9084 | 55.08% | 1.0999 | 18.0503 | 6 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 44 | 0.1364 | 1.0000 | 56.82% | 1.3158 | 1.0000 | -1.0000 |
| 2026-02 | 37 | -0.1892 | -1.0000 | 40.54% | 0.6818 | 1.0000 | -1.0000 |
| 2026-03 | 52 | 0.3941 | 1.0000 | 69.23% | 2.3217 | 1.0000 | -0.9691 |
| 2026-04 | 54 | -0.0370 | -1.0000 | 48.15% | 0.9286 | 1.0000 | -1.0000 |
| 2026-05 | 52 | 0.0385 | 1.0000 | 51.92% | 1.0800 | 1.0000 | -1.0000 |
| 2026-06 | 38 | 0.4737 | 1.0000 | 73.68% | 2.8000 | 1.0000 | -1.0000 |
| 2026-07 | 47 | 0.1489 | 1.0000 | 57.45% | 1.3500 | 1.0000 | -1.0000 |
| 2026-08 | 64 | -0.0938 | -1.0000 | 45.31% | 0.8286 | 1.0000 | -1.0000 |
| 2026-09 | 6 | 0.3333 | 1.0000 | 66.67% | 2.0000 | 1.0000 | -1.0000 |

## ATR050_TARGET_1.5R

Membership/status counts: `{'UNAVAILABLE_ATR': 333, 'RESOLVED': 394, 'UNAVAILABLE_ENTRY': 6}`. Exit reasons: `{'TARGET_TOUCH': 172, 'STOP_TOUCH': 221, 'EOD_CLOSE': 1}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 394 | 112 | 43.65% | 1.5000 | -0.9978 | 0.6483 | -0.4316 | 0.0926 | -1.0000 | 1.1648 | 19.0000 | 9 | [-0.0202, 0.2197] |
| LONG | 212 | 79 | 41.04% | 1.5000 | -1.0000 | 0.6465 | -0.4459 | 0.0259 | -1.0000 | 1.0440 | 17.0000 | 8 | [-0.1111, 0.1786] |
| SHORT | 182 | 80 | 46.70% | 1.5000 | -0.9949 | 0.6502 | -0.4131 | 0.1703 | -1.0000 | 1.3212 | 15.0000 | 7 | [-0.0092, 0.3728] |

Win-rate 95% CI (fractions): [0.3912, 0.4873]; target-first mean-R CI: [-0.0202, 0.2197]. Positive/negative months: 5/4; worst month mean R: -0.1797; LOMO minimum mean R: 0.0526. Session-sum drawdown R: 17.5000.

Paired stop-first delta versus $0.30/2R on this model's available identities: 0.0001 R, 95% CI [-0.1116, 0.1085], n=394. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 394 | 0.0926 | -1.0000 | 43.65% | 1.1648 | 19.0000 | 9 |
| Target-first | 394 | 0.0926 | -1.0000 | 43.65% | 1.1648 | 19.0000 | 9 |
| Resolved only (selection diagnostic) | 394 | 0.0926 | -1.0000 | 43.65% | 1.1648 | 19.0000 | 9 |
| $0.01 RT cost / stop-first | 394 | 0.0649 | -1.0140 | 43.65% | 1.1123 | 21.4738 | 9 |
| $0.02 RT cost / stop-first | 394 | 0.0371 | -1.0280 | 43.65% | 1.0625 | 23.9476 | 9 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 44 | -0.0341 | -1.0000 | 38.64% | 0.9444 | 1.5000 | -1.0000 |
| 2026-02 | 37 | -0.0541 | -1.0000 | 37.84% | 0.9130 | 1.5000 | -1.0000 |
| 2026-03 | 52 | 0.3557 | 1.5000 | 53.85% | 1.7868 | 1.5000 | -0.9794 |
| 2026-04 | 54 | 0.1574 | -1.0000 | 46.30% | 1.2931 | 1.5000 | -1.0000 |
| 2026-05 | 52 | -0.0385 | -1.0000 | 38.46% | 0.9375 | 1.5000 | -1.0000 |
| 2026-06 | 38 | 0.3158 | 1.5000 | 52.63% | 1.6667 | 1.5000 | -1.0000 |
| 2026-07 | 47 | 0.2766 | 1.5000 | 51.06% | 1.5652 | 1.5000 | -1.0000 |
| 2026-08 | 64 | -0.1797 | -1.0000 | 32.81% | 0.7326 | 1.5000 | -1.0000 |
| 2026-09 | 6 | 0.2500 | 0.2500 | 50.00% | 1.5000 | 1.5000 | -1.0000 |

## ATR050_TARGET_2R

Membership/status counts: `{'UNAVAILABLE_ATR': 333, 'RESOLVED': 394, 'UNAVAILABLE_ENTRY': 6}`. Exit reasons: `{'STOP_TOUCH': 251, 'TARGET_TOUCH': 142, 'EOD_CLOSE': 1}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 394 | 112 | 36.04% | 2.0000 | -0.9980 | 0.8736 | -0.4290 | 0.0825 | -1.0000 | 1.1292 | 24.0000 | 14 | [-0.0561, 0.2388] |
| LONG | 212 | 79 | 33.49% | 2.0000 | -1.0000 | 0.8772 | -0.4404 | 0.0047 | -1.0000 | 1.0071 | 24.0000 | 11 | [-0.1737, 0.2083] |
| SHORT | 182 | 80 | 39.01% | 2.0000 | -0.9956 | 0.8701 | -0.4146 | 0.1730 | -1.0000 | 1.2850 | 15.0000 | 7 | [-0.0184, 0.3935] |

Win-rate 95% CI (fractions): [0.3142, 0.4125]; target-first mean-R CI: [-0.0561, 0.2388]. Positive/negative months: 5/3; worst month mean R: -0.2500; LOMO minimum mean R: 0.0216. Session-sum drawdown R: 22.0000.

Paired stop-first delta versus $0.30/2R on this model's available identities: -0.0100 R, 95% CI [-0.1395, 0.1206], n=394. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 394 | 0.0825 | -1.0000 | 36.04% | 1.1292 | 24.0000 | 14 |
| Target-first | 394 | 0.0825 | -1.0000 | 36.04% | 1.1292 | 24.0000 | 14 |
| Resolved only (selection diagnostic) | 394 | 0.0825 | -1.0000 | 36.04% | 1.1292 | 24.0000 | 14 |
| $0.01 RT cost / stop-first | 394 | 0.0547 | -1.0180 | 36.04% | 1.0834 | 26.4738 | 14 |
| $0.02 RT cost / stop-first | 394 | 0.0270 | -1.0359 | 36.04% | 1.0400 | 28.9476 | 14 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 44 | -0.1136 | -1.0000 | 29.55% | 0.8387 | 2.0000 | -1.0000 |
| 2026-02 | 37 | -0.1892 | -1.0000 | 27.03% | 0.7407 | 2.0000 | -1.0000 |
| 2026-03 | 52 | 0.2787 | -1.0000 | 42.31% | 1.4912 | 2.0000 | -0.9835 |
| 2026-04 | 54 | 0.1111 | -1.0000 | 37.04% | 1.1765 | 2.0000 | -1.0000 |
| 2026-05 | 52 | 0.0385 | -1.0000 | 34.62% | 1.0588 | 2.0000 | -1.0000 |
| 2026-06 | 38 | 0.3421 | -1.0000 | 44.74% | 1.6190 | 2.0000 | -1.0000 |
| 2026-07 | 47 | 0.5319 | 2.0000 | 51.06% | 2.0870 | 2.0000 | -1.0000 |
| 2026-08 | 64 | -0.2500 | -1.0000 | 25.00% | 0.6667 | 2.0000 | -1.0000 |
| 2026-09 | 6 | 0.0000 | -1.0000 | 33.33% | 1.0000 | 2.0000 | -1.0000 |

## ATR050_TARGET_2.5R

Membership/status counts: `{'UNAVAILABLE_ATR': 333, 'RESOLVED': 394, 'UNAVAILABLE_ENTRY': 6}`. Exit reasons: `{'STOP_TOUCH': 272, 'TARGET_TOUCH': 121, 'EOD_CLOSE': 1}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 394 | 112 | 30.71% | 2.5000 | -0.9982 | 1.0854 | -0.4308 | 0.0761 | -1.0000 | 1.1101 | 30.5000 | 14 | [-0.0666, 0.2466] |
| LONG | 212 | 79 | 26.89% | 2.5000 | -1.0000 | 1.0824 | -0.4423 | -0.0590 | -1.0000 | 0.9194 | 30.0000 | 16 | [-0.2370, 0.1548] |
| SHORT | 182 | 80 | 35.16% | 2.5000 | -0.9958 | 1.0880 | -0.4157 | 0.2335 | -1.0000 | 1.3616 | 18.0000 | 7 | [0.0244, 0.4720] |

Win-rate 95% CI (fractions): [0.2662, 0.3561]; target-first mean-R CI: [-0.0666, 0.2466]. Positive/negative months: 6/3; worst month mean R: -0.3438; LOMO minimum mean R: 0.0101. Session-sum drawdown R: 28.0000.

Paired stop-first delta versus $0.30/2R on this model's available identities: -0.0164 R, 95% CI [-0.1483, 0.1270], n=394. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 394 | 0.0761 | -1.0000 | 30.71% | 1.1101 | 30.5000 | 14 |
| Target-first | 394 | 0.0761 | -1.0000 | 30.71% | 1.1101 | 30.5000 | 14 |
| Resolved only (selection diagnostic) | 394 | 0.0761 | -1.0000 | 30.71% | 1.1101 | 30.5000 | 14 |
| $0.01 RT cost / stop-first | 394 | 0.0484 | -1.0191 | 30.71% | 1.0680 | 32.9738 | 14 |
| $0.02 RT cost / stop-first | 394 | 0.0206 | -1.0382 | 30.71% | 1.0282 | 35.4476 | 14 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 44 | -0.2045 | -1.0000 | 22.73% | 0.7353 | 2.5000 | -1.0000 |
| 2026-02 | 37 | -0.1486 | -1.0000 | 24.32% | 0.8036 | 2.5000 | -1.0000 |
| 2026-03 | 52 | 0.3557 | -1.0000 | 38.46% | 1.5870 | 2.5000 | -0.9846 |
| 2026-04 | 54 | 0.1667 | -1.0000 | 33.33% | 1.2500 | 2.5000 | -1.0000 |
| 2026-05 | 52 | 0.0096 | -1.0000 | 28.85% | 1.0135 | 2.5000 | -1.0000 |
| 2026-06 | 38 | 0.2895 | -1.0000 | 36.84% | 1.4583 | 2.5000 | -1.0000 |
| 2026-07 | 47 | 0.5638 | -1.0000 | 44.68% | 2.0192 | 2.5000 | -1.0000 |
| 2026-08 | 64 | -0.3438 | -1.0000 | 18.75% | 0.5769 | 2.5000 | -1.0000 |
| 2026-09 | 6 | 0.1667 | -1.0000 | 33.33% | 1.2500 | 2.5000 | -1.0000 |

## ATR050_TARGET_3R

Membership/status counts: `{'UNAVAILABLE_ATR': 333, 'RESOLVED': 394, 'UNAVAILABLE_ENTRY': 6}`. Exit reasons: `{'STOP_TOUCH': 286, 'TARGET_TOUCH': 104, 'EOD_CLOSE': 3, 'TARGET_GAP': 1}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 394 | 112 | 27.16% | 2.9824 | -0.9983 | 1.3027 | -0.4300 | 0.0828 | -1.0000 | 1.1138 | 25.0000 | 14 | [-0.0846, 0.2797] |
| LONG | 212 | 79 | 23.58% | 2.9623 | -1.0000 | 1.2788 | -0.4424 | -0.0655 | -1.0000 | 0.9143 | 29.0000 | 16 | [-0.2628, 0.1667] |
| SHORT | 182 | 80 | 31.32% | 3.0000 | -0.9960 | 1.3236 | -0.4141 | 0.2555 | -1.0000 | 1.3734 | 15.0000 | 7 | [0.0140, 0.5288] |

Win-rate 95% CI (fractions): [0.2298, 0.3208]; target-first mean-R CI: [-0.0846, 0.2797]. Positive/negative months: 5/3; worst month mean R: -0.2727; LOMO minimum mean R: 0.0104. Session-sum drawdown R: 22.5062.

Paired stop-first delta versus $0.30/2R on this model's available identities: -0.0097 R, 95% CI [-0.1593, 0.1529], n=394. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 394 | 0.0828 | -1.0000 | 27.16% | 1.1138 | 25.0000 | 14 |
| Target-first | 394 | 0.0828 | -1.0000 | 27.16% | 1.1138 | 25.0000 | 14 |
| Resolved only (selection diagnostic) | 394 | 0.0828 | -1.0000 | 27.16% | 1.1138 | 25.0000 | 14 |
| $0.01 RT cost / stop-first | 394 | 0.0550 | -1.0198 | 27.16% | 1.0736 | 27.4738 | 14 |
| $0.02 RT cost / stop-first | 394 | 0.0273 | -1.0397 | 27.16% | 1.0355 | 29.9476 | 14 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 44 | -0.2727 | -1.0000 | 18.18% | 0.6667 | 3.0000 | -1.0000 |
| 2026-02 | 37 | -0.1351 | -1.0000 | 21.62% | 0.8276 | 3.0000 | -1.0000 |
| 2026-03 | 52 | 0.3941 | -1.0000 | 34.62% | 1.6116 | 3.0000 | -0.9855 |
| 2026-04 | 54 | 0.0267 | -1.0000 | 25.93% | 1.0361 | 2.9603 | -1.0000 |
| 2026-05 | 52 | 0.0000 | -1.0000 | 25.00% | 1.0000 | 3.0000 | -1.0000 |
| 2026-06 | 38 | 0.3335 | -1.0000 | 34.21% | 1.5069 | 2.8979 | -1.0000 |
| 2026-07 | 47 | 0.6170 | -1.0000 | 40.43% | 2.0357 | 3.0000 | -1.0000 |
| 2026-08 | 64 | -0.2500 | -1.0000 | 18.75% | 0.6923 | 3.0000 | -1.0000 |
| 2026-09 | 6 | 0.3333 | -1.0000 | 33.33% | 1.5000 | 3.0000 | -1.0000 |

## USD030_RECLAIM

Membership/status counts: `{'RESOLVED': 727, 'UNAVAILABLE_ENTRY': 6}`. Exit reasons: `{'STOP_TOUCH': 614, 'EOD_CLOSE': 74, 'RECLAIM_OPEN': 39}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 727 | 170 | 10.18% | 9.3935 | -0.9683 | 2.8180 | -0.2905 | 0.0864 | -1.0000 | 1.0994 | 73.7333 | 51 | [-0.1861, 0.4084] |
| LONG | 397 | 137 | 9.07% | 8.4495 | -0.9663 | 2.5349 | -0.2899 | -0.1124 | -1.0000 | 0.8720 | 91.0667 | 42 | [-0.4236, 0.2574] |
| SHORT | 330 | 128 | 11.52% | 10.2877 | -0.9708 | 3.0863 | -0.2912 | 0.3257 | -1.0000 | 1.3791 | 41.6667 | 27 | [-0.1433, 0.8837] |

Win-rate 95% CI (fractions): [0.0823, 0.1230]; target-first mean-R CI: [-0.1861, 0.4084]. Positive/negative months: 6/3; worst month mean R: -0.4773; LOMO minimum mean R: 0.0157. Session-sum drawdown R: 71.7333.

Paired stop-first delta versus $0.30/2R on this model's available identities: 0.0693 R, 95% CI [-0.1858, 0.3609], n=727. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 727 | 0.0864 | -1.0000 | 10.18% | 1.0994 | 73.7333 | 51 |
| Target-first | 727 | 0.0864 | -1.0000 | 10.18% | 1.0994 | 73.7333 | 51 |
| Resolved only (selection diagnostic) | 727 | 0.0864 | -1.0000 | 10.18% | 1.0994 | 73.7333 | 51 |
| $0.01 RT cost / stop-first | 727 | 0.0531 | -1.0333 | 10.18% | 1.0590 | 80.0000 | 51 |
| $0.02 RT cost / stop-first | 727 | 0.0198 | -1.0667 | 10.18% | 1.0213 | 86.2667 | 51 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 84 | -0.1498 | -1.0000 | 11.90% | 0.8264 | 5.9900 | -0.9795 |
| 2026-02 | 74 | -0.1054 | -1.0000 | 8.11% | 0.8844 | 9.9500 | -0.9926 |
| 2026-03 | 98 | 0.2017 | -1.0000 | 7.14% | 1.2195 | 15.6857 | -0.9894 |
| 2026-04 | 94 | 0.5629 | -1.0000 | 13.83% | 1.6920 | 9.9525 | -0.9440 |
| 2026-05 | 99 | -0.4773 | -1.0000 | 7.07% | 0.4711 | 6.0119 | -0.9710 |
| 2026-06 | 79 | 0.2331 | -1.0000 | 8.86% | 1.2602 | 12.7405 | -0.9829 |
| 2026-07 | 83 | 0.1253 | -1.0000 | 10.84% | 1.1436 | 9.2037 | -0.9788 |
| 2026-08 | 103 | 0.1351 | -1.0000 | 11.65% | 1.1658 | 8.1556 | -0.9225 |
| 2026-09 | 13 | 1.1577 | -1.0000 | 23.08% | 2.6154 | 8.1222 | -0.9317 |

## USD030_TIME_15

Membership/status counts: `{'RESOLVED': 727, 'UNAVAILABLE_ENTRY': 6}`. Exit reasons: `{'STOP_TOUCH': 518, 'TIME_OPEN': 205, 'EOD_CLOSE': 4}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 727 | 170 | 26.27% | 2.8945 | -0.9802 | 0.8683 | -0.2941 | 0.0432 | -1.0000 | 1.0602 | 55.9833 | 19 | [-0.1137, 0.2199] |
| LONG | 397 | 137 | 25.69% | 2.8188 | -0.9870 | 0.8456 | -0.2961 | -0.0017 | -1.0000 | 0.9976 | 47.6840 | 30 | [-0.1878, 0.2062] |
| SHORT | 330 | 128 | 26.97% | 2.9812 | -0.9719 | 0.8944 | -0.2916 | 0.0971 | -1.0000 | 1.1374 | 25.9000 | 12 | [-0.1188, 0.3412] |

Win-rate 95% CI (fractions): [0.2307, 0.2968]; target-first mean-R CI: [-0.1137, 0.2199]. Positive/negative months: 6/3; worst month mean R: -0.4083; LOMO minimum mean R: -0.0001. Session-sum drawdown R: 53.7503.

Paired stop-first delta versus $0.30/2R on this model's available identities: 0.0260 R, 95% CI [-0.0950, 0.1540], n=727. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 727 | 0.0432 | -1.0000 | 26.27% | 1.0602 | 55.9833 | 19 |
| Target-first | 727 | 0.0432 | -1.0000 | 26.27% | 1.0602 | 55.9833 | 19 |
| Resolved only (selection diagnostic) | 727 | 0.0432 | -1.0000 | 26.27% | 1.0602 | 55.9833 | 19 |
| $0.01 RT cost / stop-first | 727 | 0.0098 | -1.0333 | 26.13% | 1.0132 | 60.8167 | 19 |
| $0.02 RT cost / stop-first | 727 | -0.0235 | -1.0667 | 26.13% | 0.9693 | 68.6713 | 19 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 84 | 0.1130 | -1.0000 | 30.95% | 1.1693 | 2.5214 | -0.9836 |
| 2026-02 | 74 | -0.4083 | -1.0000 | 12.16% | 0.5282 | 3.7593 | -0.9854 |
| 2026-03 | 98 | 0.3205 | -1.0000 | 27.55% | 1.4424 | 3.7930 | -1.0000 |
| 2026-04 | 94 | 0.0339 | -1.0000 | 29.79% | 1.0525 | 2.2810 | -0.9482 |
| 2026-05 | 99 | -0.1197 | -1.0000 | 26.26% | 0.8363 | 2.3288 | -0.9918 |
| 2026-06 | 79 | 0.1928 | -1.0000 | 22.78% | 1.2497 | 4.2352 | -1.0000 |
| 2026-07 | 83 | 0.1823 | -1.0000 | 25.30% | 1.2545 | 3.5515 | -0.9746 |
| 2026-08 | 103 | -0.1219 | -1.0000 | 30.10% | 0.8194 | 1.8370 | -0.9653 |
| 2026-09 | 13 | 0.8885 | -1.0000 | 38.46% | 2.5786 | 3.7733 | -0.9146 |

## USD030_TIME_30

Membership/status counts: `{'RESOLVED': 727, 'UNAVAILABLE_ENTRY': 6}`. Exit reasons: `{'STOP_TOUCH': 571, 'TIME_OPEN': 147, 'EOD_CLOSE': 9}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 727 | 170 | 20.50% | 3.9848 | -0.9925 | 1.1954 | -0.2978 | 0.0276 | -1.0000 | 1.0350 | 91.6133 | 30 | [-0.1618, 0.2395] |
| LONG | 397 | 137 | 20.91% | 3.6296 | -0.9932 | 1.0889 | -0.2980 | -0.0267 | -1.0000 | 0.9660 | 73.4803 | 30 | [-0.2461, 0.2202] |
| SHORT | 330 | 128 | 20.00% | 4.4315 | -0.9917 | 1.3294 | -0.2975 | 0.0929 | -1.0000 | 1.1171 | 38.6833 | 19 | [-0.1954, 0.4208] |

Win-rate 95% CI (fractions): [0.1753, 0.2373]; target-first mean-R CI: [-0.1618, 0.2395]. Positive/negative months: 4/5; worst month mean R: -0.2948; LOMO minimum mean R: -0.0481. Session-sum drawdown R: 90.6133.

Paired stop-first delta versus $0.30/2R on this model's available identities: 0.0105 R, 95% CI [-0.1536, 0.1817], n=727. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 727 | 0.0276 | -1.0000 | 20.50% | 1.0350 | 91.6133 | 30 |
| Target-first | 727 | 0.0276 | -1.0000 | 20.50% | 1.0350 | 91.6133 | 30 |
| Resolved only (selection diagnostic) | 727 | 0.0276 | -1.0000 | 20.50% | 1.0350 | 91.6133 | 30 |
| $0.01 RT cost / stop-first | 727 | -0.0057 | -1.0333 | 20.50% | 0.9930 | 105.8800 | 30 |
| $0.02 RT cost / stop-first | 727 | -0.0391 | -1.0667 | 20.36% | 0.9536 | 120.1467 | 30 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 84 | 0.1598 | -1.0000 | 26.19% | 1.2175 | 3.4161 | -0.9957 |
| 2026-02 | 74 | -0.2948 | -1.0000 | 9.46% | 0.6744 | 6.4548 | -1.0000 |
| 2026-03 | 98 | -0.1605 | -1.0000 | 14.29% | 0.8107 | 4.8119 | -0.9893 |
| 2026-04 | 94 | 0.0685 | -1.0000 | 27.66% | 1.0946 | 2.8629 | -1.0000 |
| 2026-05 | 99 | -0.1422 | -1.0000 | 20.20% | 0.8164 | 3.1300 | -0.9707 |
| 2026-06 | 79 | -0.0994 | -1.0000 | 17.72% | 0.8777 | 4.0226 | -0.9872 |
| 2026-07 | 83 | 0.6146 | -1.0000 | 22.89% | 1.7971 | 6.0534 | -1.0000 |
| 2026-08 | 103 | -0.1070 | -1.0000 | 22.33% | 0.8622 | 2.9991 | -1.0000 |
| 2026-09 | 13 | 1.5144 | -1.0000 | 30.77% | 3.1874 | 7.1717 | -1.0000 |

## USD030_TIME_60

Membership/status counts: `{'RESOLVED': 727, 'UNAVAILABLE_ENTRY': 6}`. Exit reasons: `{'STOP_TOUCH': 607, 'TIME_OPEN': 105, 'EOD_CLOSE': 15}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 727 | 170 | 16.09% | 5.6849 | -0.9962 | 1.7055 | -0.2989 | 0.0790 | -1.0000 | 1.0946 | 78.8167 | 33 | [-0.1417, 0.3282] |
| LONG | 397 | 137 | 14.61% | 5.6040 | -0.9956 | 1.6812 | -0.2987 | -0.0314 | -1.0000 | 0.9631 | 68.1500 | 30 | [-0.3027, 0.2825] |
| SHORT | 330 | 128 | 17.88% | 5.7644 | -0.9969 | 1.7293 | -0.2991 | 0.2119 | -1.0000 | 1.2589 | 44.4173 | 19 | [-0.1340, 0.6078] |

Win-rate 95% CI (fractions): [0.1344, 0.1895]; target-first mean-R CI: [-0.1417, 0.3282]. Positive/negative months: 4/5; worst month mean R: -0.2813; LOMO minimum mean R: 0.0104. Session-sum drawdown R: 77.8167.

Paired stop-first delta versus $0.30/2R on this model's available identities: 0.0619 R, 95% CI [-0.1369, 0.2739], n=727. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 727 | 0.0790 | -1.0000 | 16.09% | 1.0946 | 78.8167 | 33 |
| Target-first | 727 | 0.0790 | -1.0000 | 16.09% | 1.0946 | 78.8167 | 33 |
| Resolved only (selection diagnostic) | 727 | 0.0790 | -1.0000 | 16.09% | 1.0946 | 78.8167 | 33 |
| $0.01 RT cost / stop-first | 727 | 0.0457 | -1.0333 | 16.09% | 1.0529 | 89.8720 | 33 |
| $0.02 RT cost / stop-first | 727 | 0.0124 | -1.0667 | 16.09% | 1.0139 | 104.5053 | 33 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 84 | 0.3957 | -1.0000 | 20.24% | 1.5018 | 5.8512 | -0.9886 |
| 2026-02 | 74 | -0.1859 | -1.0000 | 9.46% | 0.7947 | 7.6062 | -1.0000 |
| 2026-03 | 98 | -0.1861 | -1.0000 | 11.22% | 0.7904 | 6.2515 | -1.0000 |
| 2026-04 | 94 | 0.3332 | -1.0000 | 19.15% | 1.4121 | 5.9621 | -1.0000 |
| 2026-05 | 99 | -0.2813 | -1.0000 | 12.12% | 0.6772 | 4.8681 | -0.9916 |
| 2026-06 | 79 | -0.1361 | -1.0000 | 16.46% | 0.8371 | 4.2500 | -1.0000 |
| 2026-07 | 83 | 0.6118 | -1.0000 | 20.48% | 1.7792 | 6.8201 | -0.9874 |
| 2026-08 | 103 | -0.0824 | -1.0000 | 17.48% | 0.9001 | 4.2505 | -1.0000 |
| 2026-09 | 13 | 1.6321 | -1.0000 | 30.77% | 3.3574 | 7.5542 | -1.0000 |

## USD030_STRUCTURE_TRAIL

Membership/status counts: `{'RESOLVED': 727, 'UNAVAILABLE_ENTRY': 6}`. Exit reasons: `{'STOP_TOUCH': 705, 'EOD_CLOSE': 22}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 727 | 170 | 15.96% | 5.9514 | -0.9884 | 1.7854 | -0.2965 | 0.1189 | -1.0000 | 1.1431 | 76.1870 | 33 | [-0.1318, 0.4092] |
| LONG | 397 | 137 | 15.11% | 5.5675 | -0.9870 | 1.6703 | -0.2961 | 0.0036 | -1.0000 | 1.0043 | 80.9167 | 30 | [-0.3027, 0.3689] |
| SHORT | 330 | 128 | 16.97% | 6.3628 | -0.9901 | 1.9088 | -0.2970 | 0.2576 | -1.0000 | 1.3134 | 38.1570 | 19 | [-0.1307, 0.7204] |

Win-rate 95% CI (fractions): [0.1333, 0.1890]; target-first mean-R CI: [-0.1318, 0.4092]. Positive/negative months: 7/2; worst month mean R: -0.3631; LOMO minimum mean R: 0.0469. Session-sum drawdown R: 75.1870.

Paired stop-first delta versus $0.30/2R on this model's available identities: 0.1018 R, 95% CI [-0.1266, 0.3576], n=727. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 727 | 0.1189 | -1.0000 | 15.96% | 1.1431 | 76.1870 | 33 |
| Target-first | 727 | 0.1189 | -1.0000 | 15.96% | 1.1431 | 76.1870 | 33 |
| Resolved only (selection diagnostic) | 727 | 0.1189 | -1.0000 | 15.96% | 1.1431 | 76.1870 | 33 |
| $0.01 RT cost / stop-first | 727 | 0.0856 | -1.0333 | 15.96% | 1.0997 | 90.4537 | 33 |
| $0.02 RT cost / stop-first | 727 | 0.0522 | -1.0667 | 15.82% | 1.0589 | 104.7203 | 33 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 84 | 0.1660 | -1.0000 | 16.67% | 1.2043 | 5.8722 | -0.9752 |
| 2026-02 | 74 | 0.1041 | -1.0000 | 9.46% | 1.1149 | 10.6714 | -1.0000 |
| 2026-03 | 98 | -0.2175 | -1.0000 | 12.24% | 0.7490 | 5.3014 | -0.9876 |
| 2026-04 | 94 | 0.2280 | -1.0000 | 17.02% | 1.2776 | 6.1643 | -0.9897 |
| 2026-05 | 99 | -0.3631 | -1.0000 | 13.13% | 0.5736 | 3.7193 | -0.9802 |
| 2026-06 | 79 | 0.1311 | -1.0000 | 16.46% | 1.1569 | 5.8736 | -1.0000 |
| 2026-07 | 83 | 0.6779 | -1.0000 | 21.69% | 1.8656 | 6.7370 | -1.0000 |
| 2026-08 | 103 | 0.1825 | -1.0000 | 18.45% | 1.2287 | 5.3168 | -0.9788 |
| 2026-09 | 13 | 1.1705 | -1.0000 | 30.77% | 2.6907 | 6.0542 | -1.0000 |

## USD030_TARGET_2R_BE1R

Membership/status counts: `{'RESOLVED': 717, 'UNAVAILABLE_ENTRY': 6, 'AMBIGUOUS_STOP_TARGET': 10}`. Exit reasons: `{'TARGET_TOUCH': 199, 'STOP_TOUCH': 503, 'STOP_GAP': 14, 'SAME_MINUTE_STOP_TARGET': 10, 'EOD_CLOSE': 1}`.

| Direction | n | sessions | Win % | Avg win R | Avg loss R | Avg win $ | Avg loss $ | Mean R | Median R | PF | Event DD R | Losing streak | Mean R 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 727 | 170 | 27.51% | 1.9922 | -0.9764 | 0.5977 | -0.2929 | 0.0404 | -1.0000 | 1.0796 | 33.2837 | 10 | [-0.0434, 0.1290] |
| LONG | 397 | 137 | 26.20% | 1.9851 | -0.9808 | 0.5955 | -0.2942 | 0.0012 | -1.0000 | 1.0023 | 25.2000 | 11 | [-0.1148, 0.1206] |
| SHORT | 330 | 128 | 29.09% | 2.0000 | -0.9708 | 0.6000 | -0.2913 | 0.0876 | -0.2500 | 1.1772 | 20.4170 | 9 | [-0.0388, 0.2203] |

Win-rate 95% CI (fractions): [0.2463, 0.3058]; target-first mean-R CI: [-0.0124, 0.1644]. Positive/negative months: 5/4; worst month mean R: -0.1125; LOMO minimum mean R: 0.0125. Session-sum drawdown R: 32.2837.

Paired stop-first delta versus $0.30/2R on this model's available identities: 0.0233 R, 95% CI [-0.0283, 0.0720], n=727. This is a within-sample comparison, not OOS evidence.

| Scenario | n | Mean R | Median R | Win % | PF | DD R | Losing streak |
|---|---|---|---|---|---|---|---|
| Stop-first | 727 | 0.0404 | -1.0000 | 27.51% | 1.0796 | 33.2837 | 10 |
| Target-first | 727 | 0.0748 | -0.4333 | 28.89% | 1.1494 | 28.5170 | 10 |
| Resolved only (selection diagnostic) | 717 | 0.0480 | -1.0000 | 27.89% | 1.0944 | 30.5170 | 10 |
| $0.01 RT cost / stop-first | 727 | 0.0071 | -1.0333 | 27.51% | 1.0133 | 44.1170 | 16 |
| $0.02 RT cost / stop-first | 727 | -0.0263 | -1.0667 | 27.51% | 0.9528 | 54.9503 | 16 |


| Month | n | Mean R | Median R | Win % | PF | Avg winner R | Avg loser R |
|---|---|---|---|---|---|---|---|
| 2026-01 | 84 | 0.0464 | 0.0000 | 25.00% | 1.1024 | 2.0000 | -0.9769 |
| 2026-02 | 74 | 0.0768 | -0.1583 | 28.38% | 1.1565 | 2.0000 | -0.9815 |
| 2026-03 | 98 | 0.2197 | 0.0000 | 33.67% | 1.4843 | 2.0000 | -0.9667 |
| 2026-04 | 94 | -0.0009 | -1.0000 | 27.66% | 0.9983 | 1.9403 | -0.9908 |
| 2026-05 | 99 | -0.0645 | -1.0000 | 24.24% | 0.8826 | 2.0000 | -0.9711 |
| 2026-06 | 79 | 0.1698 | -1.0000 | 35.44% | 1.3151 | 2.0000 | -0.9678 |
| 2026-07 | 83 | -0.0373 | -0.4333 | 22.89% | 0.9246 | 2.0000 | -0.9786 |
| 2026-08 | 103 | -0.1125 | -1.0000 | 22.33% | 0.7988 | 2.0000 | -0.9760 |
| 2026-09 | 13 | 0.4615 | -0.0000 | 38.46% | 2.5000 | 2.0000 | -1.0000 |

