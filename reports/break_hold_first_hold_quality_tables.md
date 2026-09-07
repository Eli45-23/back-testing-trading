# First Hold quality: complete descriptive tables

All numeric variables remain continuous. E−N = eventual-strong minus never-strong. SMD uses pooled sample standard deviations; no classifier or profitable-category selection. [SMALL] means fewer than 30 available observations in a label or fewer than 10 contributing sessions (category tables flag their category). Warm-up missingness is not imputed. September is partial.

## Reference-mode comparison

### ALL

Same canonical pairs 524; both executable entries available 522; unavailable 2. All-pair threshold denominators retain the unavailable entries.

| Group | pairs | sessions | complete EOD pairs | entry disadvantage mean $ | Q25 $ | median $ | Q75 $ | better % | worse % | within 1¢ % | exact same n | delay mean min | delay median min |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| REFERENCE_CLOSE_V1_ALL | 524 | 170 | 522 | 0.2554 | -0.0700 | 0.1800 | 0.5000 | 28.82% | 67.94% | 3.24% | 2 | 5.0000 | 5.0000 |
| REFERENCE_CLOSE_V1_COMMON | 522 | 170 | 522 | 0.2572 | -0.0700 | 0.1800 | 0.5000 | 28.54% | 68.20% | 3.26% | 2 | 5.0000 | 5.0000 |
| FIRST_EXECUTABLE_MINUTE_OPEN_V1 | 522 | 170 | 522 | 0.2545 | -0.0687 | 0.1800 | 0.4800 | 29.12% | 68.77% | 2.11% | 7 | 5.0000 | 5.0000 |


| Group | complete EOD pairs | MFE lost mean $ | MFE lost median $ | MAE improvement mean $ | MAE improvement median $ | MAE improvement − MFE lost mean $ | MAE saving covers positive MFE loss |
|---|---|---|---|---|---|---|---|
| REFERENCE_CLOSE_V1_ALL | 522 | 0.2876 | 0.2150 | -0.1912 | -0.1300 | -0.4788 | 10/374 |
| REFERENCE_CLOSE_V1_COMMON | 522 | 0.2876 | 0.2150 | -0.1912 | -0.1300 | -0.4788 | 10/374 |
| FIRST_EXECUTABLE_MINUTE_OPEN_V1 | 522 | 0.2802 | 0.2050 | -0.1882 | -0.1350 | -0.4685 | 7/369 |

The last two columns compare dollar excursion magnitudes only, with no risk preference or realized-payoff interpretation. Positive MAE improvement means less adverse excursion; a negative value means waiting worsened MAE.

| Group | first MFE mean $ | strong MFE mean $ | first MAE mean $ | strong MAE mean $ | first EOD move mean $ | strong EOD move mean $ |
|---|---|---|---|---|---|---|
| REFERENCE_CLOSE_V1_ALL | 2.8166 | 2.5289 | 2.3132 | 2.5044 | 0.3363 | 0.0791 |
| REFERENCE_CLOSE_V1_COMMON | 2.8166 | 2.5289 | 2.3132 | 2.5044 | 0.3363 | 0.0791 |
| FIRST_EXECUTABLE_MINUTE_OPEN_V1 | 2.8159 | 2.5356 | 2.3210 | 2.5092 | 0.3343 | 0.0798 |


| Group | first mean MFE/MAE | strong mean MFE/MAE | first reclaims | strong reclaims | first reclaim delay median min | strong reclaim delay median min |
|---|---|---|---|---|---|---|
| REFERENCE_CLOSE_V1_ALL | 1.2176 | 1.0098 | 382 | 382 | 25.0000 | 20.0000 |
| REFERENCE_CLOSE_V1_COMMON | 1.2176 | 1.0098 | 382 | 382 | 25.0000 | 20.0000 |
| FIRST_EXECUTABLE_MINUTE_OPEN_V1 | 1.2132 | 1.0105 | 382 | 382 | 25.0000 | 20.0000 |


| metric | n | estimate | 95% low | 95% high | valid draws |
|---|---|---|---|---|---|
| entry_disadvantage | 522 | 0.2545 | 0.2044 | 0.3079 | 10000 |
| mfe_lost | 522 | 0.2802 | 0.2302 | 0.3334 | 10000 |
| mae_improvement | 522 | -0.1882 | -0.2339 | -0.1453 | 10000 |
| strong_minus_first_clean_0.25/0.25 | 522 | -0.0766 | -0.1355 | -0.0159 | 10000 |
| strong_minus_first_clean_0.50/0.25 | 522 | -0.1284 | -0.1839 | -0.0750 | 10000 |
| strong_minus_first_clean_0.75/0.25 | 522 | -0.0920 | -0.1388 | -0.0458 | 10000 |
| strong_minus_first_clean_1.00/0.25 | 522 | -0.0920 | -0.1358 | -0.0503 | 10000 |
| strong_minus_first_clean_0.50/0.30 | 522 | -0.1494 | -0.2057 | -0.0951 | 10000 |
| strong_minus_first_clean_0.75/0.30 | 522 | -0.1073 | -0.1545 | -0.0619 | 10000 |
| strong_minus_first_clean_1.00/0.30 | 522 | -0.0977 | -0.1417 | -0.0559 | 10000 |
| strong_minus_first_clean_1.50/0.30 | 522 | -0.0728 | -0.1102 | -0.0367 | 10000 |
| strong_minus_first_clean_2.00/0.30 | 522 | -0.0747 | -0.1084 | -0.0429 | 10000 |


| F/A $ | all pairs | first clean % | strong clean % | first categories | strong categories | 95% CI strong−first pp |
|---|---|---|---|---|---|---|
| 0.25/0.25 | 524 | 57.44% | 49.43% | {'FAVORABLE_FIRST': 301, 'ADVERSE_FIRST': 187, 'AMBIGUOUS_SAME_BAR': 36} | {'FAVORABLE_FIRST': 259, 'ADVERSE_FIRST': 220, 'AMBIGUOUS_SAME_BAR': 43, 'NO_FUTURE_DATA': 2} | -13.8890 to -1.9011 |
| 0.50/0.25 | 524 | 45.61% | 32.82% | {'ADVERSE_FIRST': 272, 'FAVORABLE_FIRST': 239, 'AMBIGUOUS_SAME_BAR': 13} | {'FAVORABLE_FIRST': 172, 'ADVERSE_FIRST': 343, 'AMBIGUOUS_SAME_BAR': 7, 'NO_FUTURE_DATA': 2} | -18.3453 to -7.4655 |
| 0.75/0.25 | 524 | 34.16% | 25.00% | {'ADVERSE_FIRST': 339, 'FAVORABLE_FIRST': 179, 'AMBIGUOUS_SAME_BAR': 6} | {'ADVERSE_FIRST': 387, 'FAVORABLE_FIRST': 131, 'AMBIGUOUS_SAME_BAR': 3, 'NEITHER': 1, 'NO_FUTURE_DATA': 2} | -13.8341 to -4.5627 |
| 1.00/0.25 | 524 | 27.86% | 18.70% | {'ADVERSE_FIRST': 374, 'FAVORABLE_FIRST': 146, 'NEITHER': 3, 'AMBIGUOUS_SAME_BAR': 1} | {'ADVERSE_FIRST': 418, 'FAVORABLE_FIRST': 98, 'AMBIGUOUS_SAME_BAR': 2, 'NEITHER': 4, 'NO_FUTURE_DATA': 2} | -13.5247 to -5.0093 |
| 0.50/0.30 | 524 | 51.53% | 36.64% | {'FAVORABLE_FIRST': 270, 'ADVERSE_FIRST': 245, 'AMBIGUOUS_SAME_BAR': 9} | {'FAVORABLE_FIRST': 192, 'ADVERSE_FIRST': 324, 'AMBIGUOUS_SAME_BAR': 6, 'NO_FUTURE_DATA': 2} | -20.4628 to -9.4697 |
| 0.75/0.30 | 524 | 39.31% | 28.63% | {'ADVERSE_FIRST': 312, 'FAVORABLE_FIRST': 206, 'AMBIGUOUS_SAME_BAR': 5, 'NEITHER': 1} | {'ADVERSE_FIRST': 368, 'FAVORABLE_FIRST': 150, 'AMBIGUOUS_SAME_BAR': 3, 'NEITHER': 1, 'NO_FUTURE_DATA': 2} | -15.4150 to -6.1797 |
| 1.00/0.30 | 524 | 32.63% | 22.90% | {'ADVERSE_FIRST': 346, 'FAVORABLE_FIRST': 171, 'NEITHER': 5, 'AMBIGUOUS_SAME_BAR': 2} | {'ADVERSE_FIRST': 396, 'FAVORABLE_FIRST': 120, 'AMBIGUOUS_SAME_BAR': 2, 'NEITHER': 4, 'NO_FUTURE_DATA': 2} | -14.1081 to -5.5662 |
| 1.50/0.30 | 524 | 24.24% | 16.98% | {'ADVERSE_FIRST': 387, 'FAVORABLE_FIRST': 127, 'NEITHER': 10} | {'ADVERSE_FIRST': 423, 'FAVORABLE_FIRST': 89, 'NEITHER': 9, 'AMBIGUOUS_SAME_BAR': 1, 'NO_FUTURE_DATA': 2} | -10.9781 to -3.6562 |
| 2.00/0.30 | 524 | 19.08% | 11.64% | {'ADVERSE_FIRST': 410, 'FAVORABLE_FIRST': 100, 'NEITHER': 14} | {'ADVERSE_FIRST': 447, 'FAVORABLE_FIRST': 61, 'NEITHER': 14, 'NO_FUTURE_DATA': 2} | -10.8009 to -4.2769 |

### LONG

Same canonical pairs 283; both executable entries available 283; unavailable 0. All-pair threshold denominators retain the unavailable entries.

| Group | pairs | sessions | complete EOD pairs | entry disadvantage mean $ | Q25 $ | median $ | Q75 $ | better % | worse % | within 1¢ % | exact same n | delay mean min | delay median min |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| REFERENCE_CLOSE_V1_ALL | 283 | 132 | 283 | 0.2306 | -0.0816 | 0.1400 | 0.4150 | 31.10% | 65.37% | 3.53% | 1 | 5.0000 | 5.0000 |
| REFERENCE_CLOSE_V1_COMMON | 283 | 132 | 283 | 0.2306 | -0.0816 | 0.1400 | 0.4150 | 31.10% | 65.37% | 3.53% | 1 | 5.0000 | 5.0000 |
| FIRST_EXECUTABLE_MINUTE_OPEN_V1 | 283 | 132 | 283 | 0.2284 | -0.0825 | 0.1400 | 0.4300 | 31.80% | 65.72% | 2.47% | 5 | 5.0000 | 5.0000 |


| Group | complete EOD pairs | MFE lost mean $ | MFE lost median $ | MAE improvement mean $ | MAE improvement median $ | MAE improvement − MFE lost mean $ | MAE saving covers positive MFE loss |
|---|---|---|---|---|---|---|---|
| REFERENCE_CLOSE_V1_ALL | 283 | 0.2627 | 0.1650 | -0.1635 | -0.0950 | -0.4262 | 4/194 |
| REFERENCE_CLOSE_V1_COMMON | 283 | 0.2627 | 0.1650 | -0.1635 | -0.0950 | -0.4262 | 4/194 |
| FIRST_EXECUTABLE_MINUTE_OPEN_V1 | 283 | 0.2553 | 0.1638 | -0.1616 | -0.1000 | -0.4170 | 4/191 |

The last two columns compare dollar excursion magnitudes only, with no risk preference or realized-payoff interpretation. Positive MAE improvement means less adverse excursion; a negative value means waiting worsened MAE.

| Group | first MFE mean $ | strong MFE mean $ | first MAE mean $ | strong MAE mean $ | first EOD move mean $ | strong EOD move mean $ |
|---|---|---|---|---|---|---|
| REFERENCE_CLOSE_V1_ALL | 2.5819 | 2.3192 | 2.4567 | 2.6203 | 0.1418 | -0.0888 |
| REFERENCE_CLOSE_V1_COMMON | 2.5819 | 2.3192 | 2.4567 | 2.6203 | 0.1418 | -0.0888 |
| FIRST_EXECUTABLE_MINUTE_OPEN_V1 | 2.5807 | 2.3253 | 2.4625 | 2.6242 | 0.1399 | -0.0885 |


| Group | first mean MFE/MAE | strong mean MFE/MAE | first reclaims | strong reclaims | first reclaim delay median min | strong reclaim delay median min |
|---|---|---|---|---|---|---|
| REFERENCE_CLOSE_V1_ALL | 1.0510 | 0.8851 | 207 | 207 | 25.0000 | 20.0000 |
| REFERENCE_CLOSE_V1_COMMON | 1.0510 | 0.8851 | 207 | 207 | 25.0000 | 20.0000 |
| FIRST_EXECUTABLE_MINUTE_OPEN_V1 | 1.0480 | 0.8861 | 207 | 207 | 25.0000 | 20.0000 |


| metric | n | estimate | 95% low | 95% high | valid draws |
|---|---|---|---|---|---|
| entry_disadvantage | 283 | 0.2284 | 0.1687 | 0.2923 | 10000 |
| mfe_lost | 283 | 0.2553 | 0.1963 | 0.3187 | 10000 |
| mae_improvement | 283 | -0.1616 | -0.2192 | -0.1078 | 10000 |
| strong_minus_first_clean_0.25/0.25 | 283 | -0.0636 | -0.1411 | 0.0155 | 10000 |
| strong_minus_first_clean_0.50/0.25 | 283 | -0.0813 | -0.1516 | -0.0130 | 10000 |
| strong_minus_first_clean_0.75/0.25 | 283 | -0.0459 | -0.1021 | 0.0103 | 10000 |
| strong_minus_first_clean_1.00/0.25 | 283 | -0.0459 | -0.1008 | 0.0069 | 10000 |
| strong_minus_first_clean_0.50/0.30 | 283 | -0.1131 | -0.1786 | -0.0478 | 10000 |
| strong_minus_first_clean_0.75/0.30 | 283 | -0.0707 | -0.1277 | -0.0152 | 10000 |
| strong_minus_first_clean_1.00/0.30 | 283 | -0.0601 | -0.1156 | -0.0068 | 10000 |
| strong_minus_first_clean_1.50/0.30 | 283 | -0.0318 | -0.0836 | 0.0174 | 10000 |
| strong_minus_first_clean_2.00/0.30 | 283 | -0.0318 | -0.0769 | 0.0118 | 10000 |


| F/A $ | all pairs | first clean % | strong clean % | first categories | strong categories | 95% CI strong−first pp |
|---|---|---|---|---|---|---|
| 0.25/0.25 | 283 | 56.54% | 50.18% | {'FAVORABLE_FIRST': 160, 'ADVERSE_FIRST': 105, 'AMBIGUOUS_SAME_BAR': 18} | {'FAVORABLE_FIRST': 142, 'ADVERSE_FIRST': 122, 'AMBIGUOUS_SAME_BAR': 19} | -14.1131 to 1.5529 |
| 0.50/0.25 | 283 | 41.70% | 33.57% | {'ADVERSE_FIRST': 158, 'FAVORABLE_FIRST': 118, 'AMBIGUOUS_SAME_BAR': 7} | {'FAVORABLE_FIRST': 95, 'ADVERSE_FIRST': 184, 'AMBIGUOUS_SAME_BAR': 4} | -15.1642 to -1.3041 |
| 0.75/0.25 | 283 | 29.68% | 25.09% | {'ADVERSE_FIRST': 197, 'FAVORABLE_FIRST': 84, 'AMBIGUOUS_SAME_BAR': 2} | {'ADVERSE_FIRST': 209, 'FAVORABLE_FIRST': 71, 'AMBIGUOUS_SAME_BAR': 2, 'NEITHER': 1} | -10.2117 to 1.0276 |
| 1.00/0.25 | 283 | 24.03% | 19.43% | {'ADVERSE_FIRST': 213, 'FAVORABLE_FIRST': 68, 'NEITHER': 1, 'AMBIGUOUS_SAME_BAR': 1} | {'ADVERSE_FIRST': 225, 'FAVORABLE_FIRST': 55, 'AMBIGUOUS_SAME_BAR': 1, 'NEITHER': 2} | -10.0752 to 0.6921 |
| 0.50/0.30 | 283 | 48.41% | 37.10% | {'FAVORABLE_FIRST': 137, 'ADVERSE_FIRST': 141, 'AMBIGUOUS_SAME_BAR': 5} | {'FAVORABLE_FIRST': 105, 'ADVERSE_FIRST': 174, 'AMBIGUOUS_SAME_BAR': 4} | -17.8571 to -4.7808 |
| 0.75/0.30 | 283 | 35.69% | 28.62% | {'ADVERSE_FIRST': 178, 'FAVORABLE_FIRST': 101, 'AMBIGUOUS_SAME_BAR': 3, 'NEITHER': 1} | {'ADVERSE_FIRST': 199, 'FAVORABLE_FIRST': 81, 'AMBIGUOUS_SAME_BAR': 2, 'NEITHER': 1} | -12.7739 to -1.5244 |
| 1.00/0.30 | 283 | 29.33% | 23.32% | {'ADVERSE_FIRST': 195, 'FAVORABLE_FIRST': 83, 'NEITHER': 3, 'AMBIGUOUS_SAME_BAR': 2} | {'ADVERSE_FIRST': 214, 'FAVORABLE_FIRST': 66, 'AMBIGUOUS_SAME_BAR': 1, 'NEITHER': 2} | -11.5649 to -0.6756 |
| 1.50/0.30 | 283 | 21.55% | 18.37% | {'ADVERSE_FIRST': 217, 'FAVORABLE_FIRST': 61, 'NEITHER': 5} | {'ADVERSE_FIRST': 225, 'FAVORABLE_FIRST': 52, 'AMBIGUOUS_SAME_BAR': 1, 'NEITHER': 5} | -8.3624 to 1.7423 |
| 2.00/0.30 | 283 | 15.90% | 12.72% | {'ADVERSE_FIRST': 230, 'FAVORABLE_FIRST': 45, 'NEITHER': 8} | {'ADVERSE_FIRST': 237, 'FAVORABLE_FIRST': 36, 'NEITHER': 10} | -7.6923 to 1.1769 |

### SHORT

Same canonical pairs 241; both executable entries available 239; unavailable 2. All-pair threshold denominators retain the unavailable entries.

| Group | pairs | sessions | complete EOD pairs | entry disadvantage mean $ | Q25 $ | median $ | Q75 $ | better % | worse % | within 1¢ % | exact same n | delay mean min | delay median min |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| REFERENCE_CLOSE_V1_ALL | 241 | 114 | 239 | 0.2845 | -0.0200 | 0.2500 | 0.6100 | 26.14% | 70.95% | 2.90% | 1 | 5.0000 | 5.0000 |
| REFERENCE_CLOSE_V1_COMMON | 239 | 114 | 239 | 0.2886 | -0.0150 | 0.2600 | 0.6125 | 25.52% | 71.55% | 2.93% | 1 | 5.0000 | 5.0000 |
| FIRST_EXECUTABLE_MINUTE_OPEN_V1 | 239 | 114 | 239 | 0.2855 | -0.0200 | 0.2499 | 0.5975 | 25.94% | 72.38% | 1.67% | 2 | 5.0000 | 5.0000 |


| Group | complete EOD pairs | MFE lost mean $ | MFE lost median $ | MAE improvement mean $ | MAE improvement median $ | MAE improvement − MFE lost mean $ | MAE saving covers positive MFE loss |
|---|---|---|---|---|---|---|---|
| REFERENCE_CLOSE_V1_ALL | 239 | 0.3171 | 0.2801 | -0.2240 | -0.2010 | -0.5411 | 6/180 |
| REFERENCE_CLOSE_V1_COMMON | 239 | 0.3171 | 0.2801 | -0.2240 | -0.2010 | -0.5411 | 6/180 |
| FIRST_EXECUTABLE_MINUTE_OPEN_V1 | 239 | 0.3097 | 0.2829 | -0.2197 | -0.2000 | -0.5294 | 3/178 |

The last two columns compare dollar excursion magnitudes only, with no risk preference or realized-payoff interpretation. Positive MAE improvement means less adverse excursion; a negative value means waiting worsened MAE.

| Group | first MFE mean $ | strong MFE mean $ | first MAE mean $ | strong MAE mean $ | first EOD move mean $ | strong EOD move mean $ |
|---|---|---|---|---|---|---|
| REFERENCE_CLOSE_V1_ALL | 3.0944 | 2.7773 | 2.1434 | 2.3673 | 0.5666 | 0.2780 |
| REFERENCE_CLOSE_V1_COMMON | 3.0944 | 2.7773 | 2.1434 | 2.3673 | 0.5666 | 0.2780 |
| FIRST_EXECUTABLE_MINUTE_OPEN_V1 | 3.0944 | 2.7846 | 2.1534 | 2.3732 | 0.5646 | 0.2791 |


| Group | first mean MFE/MAE | strong mean MFE/MAE | first reclaims | strong reclaims | first reclaim delay median min | strong reclaim delay median min |
|---|---|---|---|---|---|---|
| REFERENCE_CLOSE_V1_ALL | 1.4437 | 1.1732 | 175 | 175 | 25.0000 | 20.0000 |
| REFERENCE_CLOSE_V1_COMMON | 1.4437 | 1.1732 | 175 | 175 | 25.0000 | 20.0000 |
| FIRST_EXECUTABLE_MINUTE_OPEN_V1 | 1.4369 | 1.1734 | 175 | 175 | 25.0000 | 20.0000 |


| metric | n | estimate | 95% low | 95% high | valid draws |
|---|---|---|---|---|---|
| entry_disadvantage | 239 | 0.2855 | 0.2112 | 0.3655 | 10000 |
| mfe_lost | 239 | 0.3097 | 0.2348 | 0.3902 | 10000 |
| mae_improvement | 239 | -0.2197 | -0.2875 | -0.1556 | 10000 |
| strong_minus_first_clean_0.25/0.25 | 239 | -0.0921 | -0.1845 | 0.0038 | 10000 |
| strong_minus_first_clean_0.50/0.25 | 239 | -0.1841 | -0.2716 | -0.0992 | 10000 |
| strong_minus_first_clean_0.75/0.25 | 239 | -0.1464 | -0.2218 | -0.0711 | 10000 |
| strong_minus_first_clean_1.00/0.25 | 239 | -0.1464 | -0.2121 | -0.0823 | 10000 |
| strong_minus_first_clean_0.50/0.30 | 239 | -0.1925 | -0.2791 | -0.1071 | 10000 |
| strong_minus_first_clean_0.75/0.30 | 239 | -0.1506 | -0.2258 | -0.0752 | 10000 |
| strong_minus_first_clean_1.00/0.30 | 239 | -0.1423 | -0.2089 | -0.0757 | 10000 |
| strong_minus_first_clean_1.50/0.30 | 239 | -0.1213 | -0.1730 | -0.0746 | 10000 |
| strong_minus_first_clean_2.00/0.30 | 239 | -0.1255 | -0.1767 | -0.0794 | 10000 |


| F/A $ | all pairs | first clean % | strong clean % | first categories | strong categories | 95% CI strong−first pp |
|---|---|---|---|---|---|---|
| 0.25/0.25 | 241 | 58.51% | 48.55% | {'FAVORABLE_FIRST': 141, 'ADVERSE_FIRST': 82, 'AMBIGUOUS_SAME_BAR': 18} | {'FAVORABLE_FIRST': 117, 'ADVERSE_FIRST': 98, 'AMBIGUOUS_SAME_BAR': 24, 'NO_FUTURE_DATA': 2} | -19.0476 to -0.4405 |
| 0.50/0.25 | 241 | 50.21% | 31.95% | {'FAVORABLE_FIRST': 121, 'ADVERSE_FIRST': 114, 'AMBIGUOUS_SAME_BAR': 6} | {'FAVORABLE_FIRST': 77, 'ADVERSE_FIRST': 159, 'AMBIGUOUS_SAME_BAR': 3, 'NO_FUTURE_DATA': 2} | -26.9235 to -9.8287 |
| 0.75/0.25 | 241 | 39.42% | 24.90% | {'FAVORABLE_FIRST': 95, 'ADVERSE_FIRST': 142, 'AMBIGUOUS_SAME_BAR': 4} | {'FAVORABLE_FIRST': 60, 'ADVERSE_FIRST': 178, 'NO_FUTURE_DATA': 2, 'AMBIGUOUS_SAME_BAR': 1} | -21.9608 to -7.0539 |
| 1.00/0.25 | 241 | 32.37% | 17.84% | {'FAVORABLE_FIRST': 78, 'ADVERSE_FIRST': 161, 'NEITHER': 2} | {'FAVORABLE_FIRST': 43, 'ADVERSE_FIRST': 193, 'NO_FUTURE_DATA': 2, 'AMBIGUOUS_SAME_BAR': 1, 'NEITHER': 2} | -21.0281 to -8.1781 |
| 0.50/0.30 | 241 | 55.19% | 36.10% | {'FAVORABLE_FIRST': 133, 'ADVERSE_FIRST': 104, 'AMBIGUOUS_SAME_BAR': 4} | {'FAVORABLE_FIRST': 87, 'ADVERSE_FIRST': 150, 'NO_FUTURE_DATA': 2, 'AMBIGUOUS_SAME_BAR': 2} | -27.7058 to -10.6481 |
| 0.75/0.30 | 241 | 43.57% | 28.63% | {'FAVORABLE_FIRST': 105, 'ADVERSE_FIRST': 134, 'AMBIGUOUS_SAME_BAR': 2} | {'FAVORABLE_FIRST': 69, 'ADVERSE_FIRST': 169, 'NO_FUTURE_DATA': 2, 'AMBIGUOUS_SAME_BAR': 1} | -22.4066 to -7.4561 |
| 1.00/0.30 | 241 | 36.51% | 22.41% | {'FAVORABLE_FIRST': 88, 'ADVERSE_FIRST': 151, 'NEITHER': 2} | {'FAVORABLE_FIRST': 54, 'ADVERSE_FIRST': 182, 'NO_FUTURE_DATA': 2, 'AMBIGUOUS_SAME_BAR': 1, 'NEITHER': 2} | -20.7048 to -7.5395 |
| 1.50/0.30 | 241 | 27.39% | 15.35% | {'FAVORABLE_FIRST': 66, 'ADVERSE_FIRST': 170, 'NEITHER': 5} | {'FAVORABLE_FIRST': 37, 'ADVERSE_FIRST': 198, 'NEITHER': 4, 'NO_FUTURE_DATA': 2} | -17.1571 to -7.3913 |
| 2.00/0.30 | 241 | 22.82% | 10.37% | {'FAVORABLE_FIRST': 55, 'ADVERSE_FIRST': 180, 'NEITHER': 6} | {'FAVORABLE_FIRST': 25, 'ADVERSE_FIRST': 210, 'NEITHER': 4, 'NO_FUTURE_DATA': 2} | -17.5000 to -7.8652 |


## Signal-time features: ALL


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width | 524/524 (170 sessions) | 1.4455 | 1.3200 | 0.9900 | 1.7324 | 209/209 (107 sessions) | 1.4448 | 1.3200 | 1.0600 | 1.7100 | 0.0007 | 0.0013 | -0.0800 to 0.0786 |
| body_size | 524/524 (170 sessions) | 0.8088 | 0.6400 | 0.3875 | 1.0349 | 209/209 (107 sessions) | 0.5779 | 0.4500 | 0.2850 | 0.7589 | 0.2308 | 0.3863 | 0.1575 to 0.3021 |
| directional_body | 524/524 (170 sessions) | 0.8087 | 0.6400 | 0.3875 | 1.0349 | 209/209 (107 sessions) | 0.5779 | 0.4500 | 0.2850 | 0.7589 | 0.2308 | 0.3862 | 0.1574 to 0.3021 |
| candle_range | 524/524 (170 sessions) | 1.1641 | 0.9850 | 0.6638 | 1.4500 | 209/209 (107 sessions) | 0.9911 | 0.8200 | 0.5800 | 1.2800 | 0.1731 | 0.2479 | 0.0792 to 0.2662 |
| body_range_ratio | 524/524 (170 sessions) | 0.6685 | 0.7078 | 0.5461 | 0.8241 | 209/209 (107 sessions) | 0.5611 | 0.5738 | 0.4233 | 0.7011 | 0.1075 | 0.5143 | 0.0732 to 0.1410 |
| directional_body_range_ratio | 524/524 (170 sessions) | 0.6684 | 0.7078 | 0.5461 | 0.8241 | 209/209 (107 sessions) | 0.5611 | 0.5738 | 0.4233 | 0.7011 | 0.1074 | 0.5132 | 0.0731 to 0.1410 |
| close_location | 524/524 (170 sessions) | 0.5243 | 0.5931 | 0.1363 | 0.8807 | 209/209 (107 sessions) | 0.5436 | 0.5708 | 0.2104 | 0.8736 | -0.0192 | -0.0536 | -0.0789 to 0.0411 |
| directional_close_location | 524/524 (170 sessions) | 0.8309 | 0.8742 | 0.7673 | 0.9500 | 209/209 (107 sessions) | 0.8000 | 0.8476 | 0.7139 | 0.9366 | 0.0309 | 0.1932 | 0.0048 to 0.0570 |
| distance_beyond_level | 524/524 (170 sessions) | 0.4432 | 0.3225 | 0.1500 | 0.5800 | 209/209 (107 sessions) | 0.2041 | 0.1400 | 0.0600 | 0.2800 | 0.2391 | 0.5793 | 0.1884 to 0.2916 |
| distance_beyond_level_atr14 | 293/524 (112 sessions) | 0.4452 | 0.3413 | 0.1550 | 0.6441 | 107/209 (59 sessions) | 0.2201 | 0.1507 | 0.0773 | 0.2893 | 0.2251 | 0.5571 | 0.1636 to 0.2863 |
| candle_volume | 524/524 (170 sessions) | 817515.9122 | 643313.5000 | 409720.7500 | 1014398.0000 | 209/209 (107 sessions) | 843708.8756 | 596016.0000 | 403080.0000 | 1003100.0000 | -26192.9634 | -0.0398 | -146233.4071 to 85702.0594 |
| relative_volume_prior_6 | 371/524 (135 sessions) | 1.2237 | 0.9663 | 0.7408 | 1.4040 | 144/209 (77 sessions) | 1.2372 | 0.9066 | 0.7210 | 1.3041 | -0.0135 | -0.0141 | -0.2229 to 0.1712 |
| atr14 | 293/524 (112 sessions) | 0.8763 | 0.8035 | 0.5927 | 1.0669 | 107/209 (59 sessions) | 0.8180 | 0.6803 | 0.5466 | 1.0410 | 0.0583 | 0.1526 | -0.0502 to 0.1520 |
| minutes_since_open | 524/524 (170 sessions) | 123.6546 | 90.0000 | 25.0000 | 196.2500 | 209/209 (107 sessions) | 122.7990 | 75.0000 | 25.0000 | 195.0000 | 0.8555 | 0.0075 | -18.4245 to 19.5356 |
| minutes_since_ema_cross | 164/524 (82 sessions) | 48.1098 | 35.0000 | 15.0000 | 70.0000 | 64/209 (41 sessions) | 52.2656 | 35.0000 | 15.0000 | 81.2500 | -4.1559 | -0.0943 | -17.4998 to 8.0821 |
| break_attempt_rank | 524/524 (170 sessions) | 6.7042 | 6.0000 | 3.0000 | 9.0000 | 209/209 (107 sessions) | 6.2010 | 5.0000 | 2.0000 | 8.0000 | 0.5032 | 0.1064 | -0.2722 to 1.2510 |
| valid_hold_sequence_rank | 524/524 (170 sessions) | 3.5344 | 3.0000 | 2.0000 | 5.0000 | 209/209 (107 sessions) | 3.4976 | 3.0000 | 2.0000 | 5.0000 | 0.0367 | 0.0154 | -0.4319 to 0.4594 |
| stage10_9.ema9_ema20_absolute_separation | 243/524 (101 sessions) | 0.3000 | 0.2230 | 0.1088 | 0.4361 | 85/209 (48 sessions) | 0.2744 | 0.2103 | 0.0857 | 0.3758 | 0.0256 | 0.0942 | -0.0454 to 0.0975 |
| stage10_9.ema9_ema20_separation_atr14 | 243/524 (101 sessions) | 0.3627 | 0.3396 | 0.1454 | 0.5307 | 85/209 (48 sessions) | 0.3622 | 0.3495 | 0.1485 | 0.5660 | 0.0005 | 0.0021 | -0.0687 to 0.0662 |
| stage10_9.ema9_slope_1_bars | 339/524 (126 sessions) | 0.0040 | 0.0120 | -0.1215 | 0.1318 | 129/209 (71 sessions) | -0.0242 | -0.0114 | -0.1441 | 0.1091 | 0.0282 | 0.1337 | -0.0103 to 0.0681 |
| stage10_9.ema9_slope_2_bars | 328/524 (121 sessions) | -0.0061 | -0.0076 | -0.0907 | 0.0766 | 120/209 (66 sessions) | -0.0277 | -0.0217 | -0.1157 | 0.0661 | 0.0216 | 0.1363 | -0.0100 to 0.0533 |
| stage10_9.ema9_slope_3_bars | 314/524 (118 sessions) | -0.0108 | -0.0077 | -0.0884 | 0.0630 | 115/209 (63 sessions) | -0.0256 | -0.0221 | -0.1033 | 0.0649 | 0.0147 | 0.1032 | -0.0158 to 0.0454 |
| stage10_9.ema20_slope_1_bars | 233/524 (97 sessions) | -0.0080 | 0.0020 | -0.0739 | 0.0494 | 81/209 (46 sessions) | -0.0210 | -0.0109 | -0.0788 | 0.0479 | 0.0131 | 0.1120 | -0.0140 to 0.0410 |
| stage10_9.ema20_slope_2_bars | 226/524 (95 sessions) | -0.0110 | -0.0097 | -0.0589 | 0.0368 | 80/209 (46 sessions) | -0.0167 | -0.0100 | -0.0726 | 0.0410 | 0.0057 | 0.0623 | -0.0144 to 0.0263 |
| stage10_9.ema20_slope_3_bars | 218/524 (92 sessions) | -0.0133 | -0.0077 | -0.0559 | 0.0338 | 79/209 (46 sessions) | -0.0147 | -0.0127 | -0.0649 | 0.0301 | 0.0014 | 0.0162 | -0.0186 to 0.0206 |
| stage10_9.vwap_slope_1_bars | 524/524 (170 sessions) | -0.0001 | -0.0003 | -0.0326 | 0.0348 | 209/209 (107 sessions) | -0.0050 | 0.0027 | -0.0428 | 0.0409 | 0.0049 | 0.0321 | -0.0161 to 0.0263 |
| stage10_9.vwap_slope_2_bars | 473/524 (157 sessions) | -0.0024 | -0.0004 | -0.0233 | 0.0236 | 182/209 (96 sessions) | -0.0030 | -0.0012 | -0.0290 | 0.0221 | 0.0006 | 0.0076 | -0.0113 to 0.0127 |
| stage10_9.vwap_slope_3_bars | 445/524 (150 sessions) | -0.0025 | -0.0000 | -0.0215 | 0.0193 | 165/209 (88 sessions) | 0.0020 | -0.0004 | -0.0226 | 0.0243 | -0.0045 | -0.0791 | -0.0145 to 0.0053 |
| stage10_9.ema9_ema20_cross_count_6_bars | 209/524 (89 sessions) | 0.3110 | 0.0000 | 0.0000 | 1.0000 | 76/209 (43 sessions) | 0.3421 | 0.0000 | 0.0000 | 1.0000 | -0.0311 | -0.0565 | -0.1480 to 0.0896 |
| stage10_9.ema9_ema20_cross_count_12_bars | 171/524 (84 sessions) | 0.6491 | 1.0000 | 0.0000 | 1.0000 | 71/209 (42 sessions) | 0.6056 | 1.0000 | 0.0000 | 1.0000 | 0.0435 | 0.0587 | -0.1470 to 0.2245 |
| stage10_9.ema9_ema20_cross_count_24_bars | 119/524 (68 sessions) | 1.2101 | 1.0000 | 1.0000 | 1.0000 | 44/209 (33 sessions) | 1.0455 | 1.0000 | 0.7500 | 1.0000 | 0.1646 | 0.1780 | -0.1208 to 0.4434 |
| stage10_9.ema9_vwap_cross_count_6_bars | 293/524 (112 sessions) | 0.3379 | 0.0000 | 0.0000 | 1.0000 | 107/209 (59 sessions) | 0.3551 | 0.0000 | 0.0000 | 1.0000 | -0.0173 | -0.0314 | -0.1383 to 0.0964 |
| stage10_9.ema9_vwap_cross_count_12_bars | 243/524 (101 sessions) | 0.6543 | 1.0000 | 0.0000 | 1.0000 | 85/209 (48 sessions) | 0.4353 | 0.0000 | 0.0000 | 1.0000 | 0.2190 | 0.3052 | 0.0560 to 0.3837 |
| stage10_9.ema9_vwap_cross_count_24_bars | 166/524 (82 sessions) | 0.9759 | 1.0000 | 0.0000 | 1.0000 | 70/209 (42 sessions) | 0.8571 | 1.0000 | 0.0000 | 1.0000 | 0.1188 | 0.1345 | -0.1143 to 0.3418 |
| stage10_9.ema20_vwap_cross_count_6_bars | 209/524 (89 sessions) | 0.1770 | 0.0000 | 0.0000 | 0.0000 | 76/209 (43 sessions) | 0.2105 | 0.0000 | 0.0000 | 0.0000 | -0.0335 | -0.0839 | -0.1337 to 0.0668 |
| stage10_9.ema20_vwap_cross_count_12_bars | 171/524 (84 sessions) | 0.3801 | 0.0000 | 0.0000 | 1.0000 | 71/209 (42 sessions) | 0.3803 | 0.0000 | 0.0000 | 1.0000 | -0.0002 | -0.0003 | -0.1599 to 0.1483 |
| stage10_9.ema20_vwap_cross_count_24_bars | 119/524 (68 sessions) | 0.6050 | 1.0000 | 0.0000 | 1.0000 | 44/209 (33 sessions) | 0.5682 | 0.0000 | 0.0000 | 1.0000 | 0.0369 | 0.0507 | -0.2231 to 0.2800 |
| stage10_9.price_vwap_side_change_count_6_bars | 388/524 (139 sessions) | 1.0490 | 1.0000 | 0.0000 | 2.0000 | 153/209 (83 sessions) | 1.0196 | 1.0000 | 0.0000 | 2.0000 | 0.0294 | 0.0266 | -0.1710 to 0.2133 |
| stage10_9.price_vwap_side_change_count_12_bars | 314/524 (118 sessions) | 1.8567 | 2.0000 | 1.0000 | 3.0000 | 115/209 (63 sessions) | 1.6522 | 1.0000 | 0.0000 | 3.0000 | 0.2045 | 0.1301 | -0.0907 to 0.4917 |
| stage10_9.price_vwap_side_change_count_24_bars | 215/524 (91 sessions) | 2.9674 | 2.0000 | 1.0000 | 4.5000 | 78/209 (45 sessions) | 2.4744 | 2.0000 | 1.0000 | 3.7500 | 0.4931 | 0.2121 | -0.1166 to 1.1062 |
| stage10_9.rolling_high_low_range_6_bars | 388/524 (139 sessions) | 2.1368 | 1.8800 | 1.2838 | 2.6425 | 153/209 (83 sessions) | 2.0490 | 1.8400 | 1.3000 | 2.5720 | 0.0878 | 0.0786 | -0.1316 to 0.2939 |
| stage10_9.rolling_high_low_range_12_bars | 314/524 (118 sessions) | 2.8028 | 2.4700 | 1.7425 | 3.4100 | 115/209 (63 sessions) | 2.6225 | 2.1850 | 1.5650 | 3.3600 | 0.1803 | 0.1240 | -0.1864 to 0.5108 |
| stage10_9.rolling_high_low_range_24_bars | 215/524 (91 sessions) | 3.5587 | 3.2600 | 2.2550 | 4.4350 | 78/209 (45 sessions) | 3.3848 | 2.9400 | 2.0812 | 4.2800 | 0.1739 | 0.0991 | -0.4032 to 0.6810 |
| stage10_9.rolling_range_atr14_6_bars | 293/524 (112 sessions) | 2.2791 | 2.1524 | 1.7778 | 2.6000 | 107/209 (59 sessions) | 2.3217 | 2.2213 | 1.6745 | 2.8356 | -0.0426 | -0.0572 | -0.2264 to 0.1443 |
| stage10_9.rolling_range_atr14_12_bars | 293/524 (112 sessions) | 3.1131 | 2.9763 | 2.4711 | 3.6929 | 107/209 (59 sessions) | 3.1678 | 3.0465 | 2.5268 | 3.7343 | -0.0547 | -0.0634 | -0.2435 to 0.1308 |
| stage10_9.rolling_range_atr14_24_bars | 215/524 (91 sessions) | 4.4320 | 4.2557 | 3.6023 | 5.1187 | 78/209 (45 sessions) | 4.6744 | 4.6046 | 3.9278 | 5.1857 | -0.2424 | -0.2174 | -0.5065 to 0.0268 |
| stage10_9.directional_efficiency_6_bars | 388/524 (139 sessions) | 0.4529 | 0.4173 | 0.2319 | 0.6632 | 153/209 (83 sessions) | 0.4210 | 0.3782 | 0.1667 | 0.5936 | 0.0319 | 0.1089 | -0.0255 to 0.0875 |
| stage10_9.directional_efficiency_12_bars | 314/524 (118 sessions) | 0.2812 | 0.2426 | 0.1127 | 0.3975 | 115/209 (63 sessions) | 0.3030 | 0.2806 | 0.1245 | 0.4587 | -0.0218 | -0.1083 | -0.0595 to 0.0158 |
| stage10_9.directional_efficiency_24_bars | 215/524 (91 sessions) | 0.1772 | 0.1539 | 0.0639 | 0.2639 | 78/209 (45 sessions) | 0.2008 | 0.1661 | 0.0819 | 0.2918 | -0.0236 | -0.1662 | -0.0576 to 0.0115 |
| stage10_9.range_overlap_fraction_6_bars | 388/524 (139 sessions) | 0.9995 | 1.0000 | 1.0000 | 1.0000 | 153/209 (83 sessions) | 0.9987 | 1.0000 | 1.0000 | 1.0000 | 0.0008 | 0.0651 | 0.0000 to 0.0028 |
| stage10_9.range_overlap_fraction_12_bars | 314/524 (118 sessions) | 0.9994 | 1.0000 | 1.0000 | 1.0000 | 115/209 (63 sessions) | 0.9992 | 1.0000 | 1.0000 | 1.0000 | 0.0002 | 0.0279 | 0.0000 to 0.0009 |
| stage10_9.range_overlap_fraction_24_bars | 215/524 (91 sessions) | 0.9992 | 1.0000 | 1.0000 | 1.0000 | 78/209 (45 sessions) | 0.9994 | 1.0000 | 1.0000 | 1.0000 | -0.0003 | -0.0445 | -0.0010 to 0.0004 |
| stage10_9.close_direction_alternation_fraction_6_bars | 388/524 (139 sessions) | 0.5238 | 0.5000 | 0.4375 | 0.7500 | 153/209 (83 sessions) | 0.4951 | 0.5000 | 0.2500 | 0.7500 | 0.0287 | 0.1144 | -0.0194 to 0.0761 |
| stage10_9.close_direction_alternation_fraction_12_bars | 314/524 (118 sessions) | 0.5156 | 0.5000 | 0.4000 | 0.6000 | 115/209 (63 sessions) | 0.4887 | 0.5000 | 0.4000 | 0.6000 | 0.0269 | 0.1680 | -0.0005 to 0.0533 |
| stage10_9.close_direction_alternation_fraction_24_bars | 215/524 (91 sessions) | 0.5142 | 0.5000 | 0.4545 | 0.5909 | 78/209 (45 sessions) | 0.4930 | 0.5000 | 0.4091 | 0.5909 | 0.0212 | 0.1846 | -0.0098 to 0.0525 |
| stage10_9.confirmation_close_vwap_distance_atr14 | 293/524 (112 sessions) | 1.2193 | 1.0696 | 0.5184 | 1.6927 | 107/209 (59 sessions) | 1.3850 | 1.1878 | 0.6550 | 1.8334 | -0.1657 | -0.1745 | -0.4420 to 0.0603 |
| stage10_9.ema9_vwap_distance_atr14 | 293/524 (112 sessions) | 0.7094 | 0.5660 | 0.2599 | 0.9553 | 107/209 (59 sessions) | 0.8397 | 0.6426 | 0.2452 | 1.1209 | -0.1304 | -0.1810 | -0.3599 to 0.0455 |
| stage10_9.ema20_vwap_distance_atr14 | 243/524 (101 sessions) | 0.5393 | 0.3807 | 0.1678 | 0.7756 | 85/209 (48 sessions) | 0.7227 | 0.5064 | 0.2360 | 0.9061 | -0.1834 | -0.2954 | -0.4220 to -0.0086 |
| stage11_2.room_from_confirmation | 431/524 (153 sessions) | 1.8912 | 1.3500 | 0.5068 | 2.5610 | 178/209 (96 sessions) | 1.5398 | 1.1974 | 0.4025 | 2.2275 | 0.3514 | 0.1889 | 0.0736 to 0.6250 |
| stage11_2.room_in_atr | 244/524 (99 sessions) | 2.2185 | 1.5492 | 0.6442 | 3.0013 | 91/209 (54 sessions) | 1.6603 | 1.2270 | 0.4124 | 2.0492 | 0.5582 | 0.2661 | 0.0930 to 1.0396 |
| stage11_2.number_of_known_levels_above | 524/524 (170 sessions) | 2.8416 | 3.0000 | 1.0000 | 4.0000 | 209/209 (107 sessions) | 2.7081 | 3.0000 | 2.0000 | 4.0000 | 0.1335 | 0.0772 | -0.1640 to 0.4237 |
| stage11_2.number_of_known_levels_below | 524/524 (170 sessions) | 3.1450 | 3.0000 | 2.0000 | 5.0000 | 209/209 (107 sessions) | 3.2871 | 3.0000 | 2.0000 | 4.0000 | -0.1420 | -0.0822 | -0.4312 to 0.1532 |
| stage11_2.nearest_level_distance_above | 471/524 (157 sessions) | 1.1229 | 0.5050 | 0.2025 | 1.4100 | 184/209 (98 sessions) | 0.8755 | 0.3625 | 0.1362 | 1.3575 | 0.2475 | 0.1721 | 0.0127 to 0.4960 |
| stage11_2.nearest_level_distance_below | 484/524 (166 sessions) | 0.9993 | 0.4199 | 0.1700 | 1.2300 | 203/209 (105 sessions) | 0.7546 | 0.2200 | 0.0800 | 0.7150 | 0.2447 | 0.1623 | 0.0425 to 0.4360 |
| stage11_2.directional_level_count_within_0_5_atr | 293/524 (112 sessions) | 0.1843 | 0.0000 | 0.0000 | 0.0000 | 107/209 (59 sessions) | 0.2523 | 0.0000 | 0.0000 | 0.0000 | -0.0680 | -0.1555 | -0.1909 to 0.0449 |
| stage11_2.directional_level_count_within_1_0_atr | 293/524 (112 sessions) | 0.3618 | 0.0000 | 0.0000 | 1.0000 | 107/209 (59 sessions) | 0.4019 | 0.0000 | 0.0000 | 1.0000 | -0.0401 | -0.0703 | -0.1820 to 0.0907 |
| stage11_3.confirmation_close_to_latest_swing_high | 365/524 (132 sessions) | 1.3340 | 0.9800 | 0.4350 | 1.8300 | 143/209 (77 sessions) | 1.2773 | 0.9400 | 0.4200 | 1.7400 | 0.0567 | 0.0458 | -0.2097 to 0.3006 |
| stage11_3.confirmation_close_to_latest_swing_low | 359/524 (131 sessions) | 1.3727 | 1.0950 | 0.5088 | 1.8600 | 136/209 (73 sessions) | 1.3294 | 1.0575 | 0.4750 | 1.9288 | 0.0433 | 0.0370 | -0.1794 to 0.2515 |
| stage11_3.distance_to_swing_high_in_atr | 293/524 (112 sessions) | 1.4993 | 1.2682 | 0.5480 | 2.0986 | 107/209 (59 sessions) | 1.6252 | 1.3226 | 0.6140 | 2.2897 | -0.1258 | -0.1034 | -0.3989 to 0.1413 |
| stage11_3.distance_to_swing_low_in_atr | 290/524 (111 sessions) | 1.4847 | 1.3356 | 0.7035 | 2.0038 | 104/209 (57 sessions) | 1.4770 | 1.2107 | 0.7402 | 2.1038 | 0.0077 | 0.0074 | -0.2143 to 0.2088 |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG | 400 | 137 | 283 | 117 | 54.01% | 55.98% | 70.75% |
| direction | SHORT | 333 | 129 | 241 | 92 | 45.99% | 44.02% | 72.37% |
| time_bucket | 09:35-10:00 | 192 | 151 | 136 | 56 | 25.95% | 26.79% | 70.83% |
| time_bucket | 10:00-10:30 | 112 | 84 | 74 | 38 | 14.12% | 18.18% | 66.07% |
| time_bucket | 10:30-11:00 | 72 | 54 | 50 | 22 | 9.54% | 10.53% | 69.44% |
| time_bucket | 11:00-12:00 | 105 | 64 | 83 | 22 | 15.84% | 10.53% | 79.05% |
| time_bucket | 12:00-13:30 | 118 | 62 | 86 | 32 | 16.41% | 15.31% | 72.88% |
| time_bucket | 13:30-15:00 | 67 | 49 | 54 | 13 | 10.31% | 6.22% | 80.60% |
| time_bucket | 15:00-close | 67 | 43 | 41 | 26 | 7.82% | 12.44% | 61.19% |
| ema9_20_alignment | EMA_ALIGNED | 211 | 75 | 154 | 57 | 29.39% | 27.27% | 72.99% |
| ema9_20_alignment | EMA_NOT_ALIGNED | 117 | 69 | 89 | 28 | 16.98% | 13.40% | 76.07% |
| ema9_20_alignment | EMA_UNAVAILABLE | 405 | 169 | 281 | 124 | 53.63% | 59.33% | 69.38% |
| price_vwap_alignment | VWAP_ALIGNED | 651 | 170 | 463 | 188 | 88.36% | 89.95% | 71.12% |
| price_vwap_alignment | VWAP_NOT_ALIGNED | 82 | 46 | 61 | 21 | 11.64% | 10.05% | 74.39% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED | 349 | 114 | 255 | 94 | 48.66% | 44.98% | 73.07% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED | 136 | 77 | 98 | 38 | 18.70% | 18.18% | 72.06% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE | 248 | 164 | 171 | 77 | 32.63% | 36.84% | 68.95% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED | 218 | 82 | 162 | 56 | 30.92% | 26.79% | 74.31% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED | 110 | 70 | 81 | 29 | 15.46% | 13.88% | 73.64% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 405 | 169 | 281 | 124 | 53.63% | 59.33% | 69.38% |
| prior_ema_cross | MATCHING_CROSS | 129 | 57 | 90 | 39 | 17.18% | 18.66% | 69.77% |
| prior_ema_cross | NO_PRIOR_CROSS | 505 | 170 | 360 | 145 | 68.70% | 69.38% | 71.29% |
| prior_ema_cross | OPPOSING_CROSS | 99 | 58 | 74 | 25 | 14.12% | 11.96% | 74.75% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 491 | 124 | 359 | 132 | 68.51% | 63.16% | 73.12% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL | 233 | 123 | 159 | 74 | 30.34% | 35.41% | 68.24% |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 9 | 9 | 6 | 3 | 1.15% | 1.44% | 66.67% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 | 56 | 36 | 43 | 13 | 8.21% | 6.22% | 76.79% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 | 40 | 26 | 26 | 14 | 4.96% | 6.70% | 65.00% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 | 38 | 29 | 23 | 15 | 4.39% | 7.18% | 60.53% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 | 51 | 35 | 41 | 10 | 7.82% | 4.78% | 80.39% |
| stage11_2.room_bucket | GT_3_0_ATR | 75 | 33 | 61 | 14 | 11.64% | 6.70% | 81.33% |
| stage11_2.room_bucket | LT_0_5_ATR | 75 | 41 | 50 | 25 | 9.54% | 11.96% | 66.67% |
| stage11_2.room_bucket | OPEN_ENDED | 124 | 43 | 93 | 31 | 17.75% | 14.83% | 75.00% |
| stage11_2.room_bucket | UNAVAILABLE_ATR | 274 | 151 | 187 | 87 | 35.69% | 41.63% | 68.25% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 731 | 169 | 522 | 209 | 99.62% | 100.00% | 71.41% |
| known_level_coverage | PARTIAL_UNAVAILABLE [SMALL] | 2 | 1 | 2 | 0 | 0.38% | 0.00% | 100.00% |
| stage11_3.structure | BEARISH_STRUCTURE | 101 | 62 | 77 | 24 | 14.69% | 11.48% | 76.24% |
| stage11_3.structure | BULLISH_STRUCTURE | 102 | 63 | 76 | 26 | 14.50% | 12.44% | 74.51% |
| stage11_3.structure | MIXED_STRUCTURE | 152 | 73 | 107 | 45 | 20.42% | 21.53% | 70.39% |
| stage11_3.structure | UNAVAILABLE | 378 | 169 | 264 | 114 | 50.38% | 54.55% | 69.84% |
| stage11_3.agreement | STRUCTURE_ALIGNED | 116 | 70 | 85 | 31 | 16.22% | 14.83% | 73.28% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED | 239 | 93 | 175 | 64 | 33.40% | 30.62% | 73.22% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 378 | 169 | 264 | 114 | 50.38% | 54.55% | 69.84% |
| stage11_3.high_structure | EQUAL_HIGH [SMALL] | 4 | 3 | 4 | 0 | 0.76% | 0.00% | 100.00% |
| stage11_3.high_structure | HIGHER_HIGH | 175 | 83 | 130 | 45 | 24.81% | 21.53% | 74.29% |
| stage11_3.high_structure | LOWER_HIGH | 214 | 88 | 152 | 62 | 29.01% | 29.67% | 71.03% |
| stage11_3.high_structure | UNAVAILABLE | 340 | 168 | 238 | 102 | 45.42% | 48.80% | 70.00% |
| stage11_3.low_structure | EQUAL_LOW [SMALL] | 3 | 2 | 2 | 1 | 0.38% | 0.48% | 66.67% |
| stage11_3.low_structure | HIGHER_LOW | 214 | 94 | 149 | 65 | 28.44% | 31.10% | 69.63% |
| stage11_3.low_structure | LOWER_LOW | 160 | 77 | 125 | 35 | 23.85% | 16.75% | 78.12% |
| stage11_3.low_structure | UNAVAILABLE | 356 | 169 | 248 | 108 | 47.33% | 51.67% | 69.66% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE | 234 | 158 | 165 | 69 | 31.49% | 33.01% | 70.51% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED | 86 | 33 | 64 | 22 | 12.21% | 10.53% | 74.42% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL | 99 | 50 | 67 | 32 | 12.79% | 15.31% | 67.68% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL | 314 | 108 | 228 | 86 | 43.51% | 41.15% | 72.61% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 733 | 170 | 524 | 209 | 100.00% | 100.00% | 71.49% |


## Signal-time features: LONG


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width | 283/283 (132 sessions) | 1.4294 | 1.3200 | 0.9900 | 1.7100 | 117/117 (71 sessions) | 1.5271 | 1.4100 | 1.0800 | 1.7324 | -0.0978 | -0.1666 | -0.2139 to 0.0196 |
| body_size | 283/283 (132 sessions) | 0.7716 | 0.6247 | 0.3728 | 0.9775 | 117/117 (71 sessions) | 0.5297 | 0.4200 | 0.2600 | 0.7050 | 0.2420 | 0.4217 | 0.1536 to 0.3266 |
| directional_body | 283/283 (132 sessions) | 0.7716 | 0.6247 | 0.3728 | 0.9775 | 117/117 (71 sessions) | 0.5297 | 0.4200 | 0.2600 | 0.7050 | 0.2420 | 0.4217 | 0.1536 to 0.3266 |
| candle_range | 283/283 (132 sessions) | 1.1334 | 0.9600 | 0.6725 | 1.3800 | 117/117 (71 sessions) | 0.9512 | 0.8000 | 0.5400 | 1.2400 | 0.1822 | 0.2677 | 0.0655 to 0.2942 |
| body_range_ratio | 283/283 (132 sessions) | 0.6637 | 0.7051 | 0.5543 | 0.8228 | 117/117 (71 sessions) | 0.5399 | 0.5590 | 0.4151 | 0.6759 | 0.1238 | 0.5970 | 0.0783 to 0.1685 |
| directional_body_range_ratio | 283/283 (132 sessions) | 0.6637 | 0.7051 | 0.5543 | 0.8228 | 117/117 (71 sessions) | 0.5399 | 0.5590 | 0.4151 | 0.6759 | 0.1238 | 0.5970 | 0.0783 to 0.1685 |
| close_location | 283/283 (132 sessions) | 0.8289 | 0.8750 | 0.7596 | 0.9435 | 117/117 (71 sessions) | 0.8068 | 0.8571 | 0.7028 | 0.9491 | 0.0220 | 0.1400 | -0.0127 to 0.0573 |
| directional_close_location | 283/283 (132 sessions) | 0.8289 | 0.8750 | 0.7596 | 0.9435 | 117/117 (71 sessions) | 0.8068 | 0.8571 | 0.7028 | 0.9491 | 0.0220 | 0.1400 | -0.0127 to 0.0573 |
| distance_beyond_level | 283/283 (132 sessions) | 0.4087 | 0.3100 | 0.1500 | 0.5500 | 117/117 (71 sessions) | 0.1705 | 0.1100 | 0.0550 | 0.2200 | 0.2381 | 0.7057 | 0.1786 to 0.3020 |
| distance_beyond_level_atr14 | 154/283 (75 sessions) | 0.4294 | 0.3520 | 0.1715 | 0.6190 | 61/117 (39 sessions) | 0.1657 | 0.1376 | 0.0696 | 0.2199 | 0.2637 | 0.8646 | 0.2010 to 0.3266 |
| candle_volume | 283/283 (132 sessions) | 818054.0071 | 659479.0000 | 415126.0000 | 1016780.5000 | 117/117 (71 sessions) | 750180.4615 | 556772.0000 | 353058.0000 | 896443.0000 | 67873.5455 | 0.1050 | -97436.4682 to 204517.3820 |
| relative_volume_prior_6 | 196/283 (95 sessions) | 1.2069 | 0.9652 | 0.7500 | 1.3093 | 84/117 (52 sessions) | 1.0351 | 0.8355 | 0.6887 | 1.1145 | 0.1718 | 0.2028 | -0.0457 to 0.3441 |
| atr14 | 154/283 (75 sessions) | 0.8832 | 0.8185 | 0.6113 | 1.1040 | 61/117 (39 sessions) | 0.8556 | 0.6853 | 0.5716 | 1.0555 | 0.0276 | 0.0725 | -0.0965 to 0.1348 |
| minutes_since_open | 283/283 (132 sessions) | 120.4064 | 90.0000 | 25.0000 | 192.5000 | 117/117 (71 sessions) | 111.2821 | 75.0000 | 30.0000 | 180.0000 | 9.1243 | 0.0846 | -12.7896 to 31.2268 |
| minutes_since_ema_cross [SMALL] | 79/283 (48 sessions) | 47.4051 | 35.0000 | 20.0000 | 65.0000 | 27/117 (21 sessions) | 54.8148 | 30.0000 | 17.5000 | 97.5000 | -7.4098 | -0.1669 | -31.5214 to 15.4170 |
| break_attempt_rank | 283/283 (132 sessions) | 6.7138 | 6.0000 | 3.0000 | 9.0000 | 117/117 (71 sessions) | 6.1538 | 5.0000 | 3.0000 | 8.0000 | 0.5599 | 0.1206 | -0.4227 to 1.5169 |
| valid_hold_sequence_rank | 283/283 (132 sessions) | 3.4452 | 3.0000 | 2.0000 | 5.0000 | 117/117 (71 sessions) | 3.4530 | 3.0000 | 2.0000 | 4.0000 | -0.0078 | -0.0034 | -0.5957 to 0.5167 |
| stage10_9.ema9_ema20_absolute_separation | 128/283 (65 sessions) | 0.2838 | 0.2136 | 0.1022 | 0.4256 | 44/117 (29 sessions) | 0.2421 | 0.1366 | 0.0732 | 0.3674 | 0.0418 | 0.1750 | -0.0465 to 0.1249 |
| stage10_9.ema9_ema20_separation_atr14 | 128/283 (65 sessions) | 0.3518 | 0.3326 | 0.1297 | 0.5299 | 44/117 (29 sessions) | 0.3183 | 0.2723 | 0.0921 | 0.5071 | 0.0335 | 0.1315 | -0.0759 to 0.1326 |
| stage10_9.ema9_slope_1_bars | 182/283 (87 sessions) | 0.1402 | 0.1140 | 0.0521 | 0.2031 | 75/117 (48 sessions) | 0.0819 | 0.0808 | -0.0049 | 0.1563 | 0.0583 | 0.3890 | 0.0246 to 0.0913 |
| stage10_9.ema9_slope_2_bars | 175/283 (84 sessions) | 0.0622 | 0.0498 | -0.0222 | 0.1215 | 70/117 (44 sessions) | 0.0324 | 0.0375 | -0.0409 | 0.1159 | 0.0298 | 0.2228 | -0.0078 to 0.0667 |
| stage10_9.ema9_slope_3_bars | 168/283 (81 sessions) | 0.0373 | 0.0342 | -0.0368 | 0.0876 | 66/117 (41 sessions) | 0.0255 | 0.0259 | -0.0494 | 0.0924 | 0.0118 | 0.0924 | -0.0256 to 0.0476 |
| stage10_9.ema20_slope_1_bars | 124/283 (62 sessions) | 0.0576 | 0.0415 | 0.0061 | 0.0992 | 42/117 (27 sessions) | 0.0343 | 0.0261 | -0.0049 | 0.0722 | 0.0233 | 0.2667 | -0.0034 to 0.0506 |
| stage10_9.ema20_slope_2_bars | 119/283 (61 sessions) | 0.0239 | 0.0195 | -0.0196 | 0.0582 | 42/117 (27 sessions) | 0.0143 | 0.0155 | -0.0233 | 0.0537 | 0.0096 | 0.1237 | -0.0187 to 0.0384 |
| stage10_9.ema20_slope_3_bars | 116/283 (59 sessions) | 0.0115 | 0.0093 | -0.0264 | 0.0532 | 41/117 (27 sessions) | 0.0098 | 0.0065 | -0.0252 | 0.0461 | 0.0018 | 0.0240 | -0.0269 to 0.0294 |
| stage10_9.vwap_slope_1_bars | 283/283 (132 sessions) | 0.0835 | 0.0316 | 0.0062 | 0.1279 | 117/117 (71 sessions) | 0.0577 | 0.0259 | 0.0061 | 0.0833 | 0.0259 | 0.2293 | 0.0042 to 0.0476 |
| stage10_9.vwap_slope_2_bars | 252/283 (117 sessions) | 0.0340 | 0.0160 | -0.0019 | 0.0546 | 103/117 (63 sessions) | 0.0253 | 0.0134 | -0.0009 | 0.0462 | 0.0087 | 0.1475 | -0.0045 to 0.0216 |
| stage10_9.vwap_slope_3_bars | 240/283 (114 sessions) | 0.0233 | 0.0137 | -0.0030 | 0.0393 | 95/117 (59 sessions) | 0.0228 | 0.0116 | -0.0028 | 0.0420 | 0.0005 | 0.0104 | -0.0106 to 0.0111 |
| stage10_9.ema9_ema20_cross_count_6_bars | 111/283 (57 sessions) | 0.2703 | 0.0000 | 0.0000 | 0.0000 | 39/117 (25 sessions) | 0.2821 | 0.0000 | 0.0000 | 0.5000 | -0.0118 | -0.0227 | -0.1680 to 0.1432 |
| stage10_9.ema9_ema20_cross_count_12_bars | 89/283 (51 sessions) | 0.6292 | 1.0000 | 0.0000 | 1.0000 | 36/117 (24 sessions) | 0.5278 | 0.0000 | 0.0000 | 1.0000 | 0.1014 | 0.1409 | -0.1521 to 0.3222 |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 64/283 (44 sessions) | 1.1875 | 1.0000 | 1.0000 | 2.0000 | 18/117 (14 sessions) | 0.8889 | 1.0000 | 0.0000 | 1.0000 | 0.2986 | 0.3299 | -0.1805 to 0.7044 |
| stage10_9.ema9_vwap_cross_count_6_bars | 154/283 (75 sessions) | 0.3117 | 0.0000 | 0.0000 | 1.0000 | 61/117 (39 sessions) | 0.3770 | 0.0000 | 0.0000 | 1.0000 | -0.0654 | -0.1162 | -0.2394 to 0.0953 |
| stage10_9.ema9_vwap_cross_count_12_bars | 128/283 (65 sessions) | 0.6016 | 0.0000 | 0.0000 | 1.0000 | 44/117 (29 sessions) | 0.3636 | 0.0000 | 0.0000 | 1.0000 | 0.2379 | 0.3493 | 0.0344 to 0.4280 |
| stage10_9.ema9_vwap_cross_count_24_bars | 85/283 (48 sessions) | 0.9294 | 1.0000 | 0.0000 | 1.0000 | 35/117 (23 sessions) | 0.7143 | 1.0000 | 0.0000 | 1.0000 | 0.2151 | 0.2539 | -0.0493 to 0.4977 |
| stage10_9.ema20_vwap_cross_count_6_bars | 111/283 (57 sessions) | 0.1712 | 0.0000 | 0.0000 | 0.0000 | 39/117 (25 sessions) | 0.2308 | 0.0000 | 0.0000 | 0.0000 | -0.0596 | -0.1460 | -0.2287 to 0.0822 |
| stage10_9.ema20_vwap_cross_count_12_bars | 89/283 (51 sessions) | 0.4045 | 0.0000 | 0.0000 | 1.0000 | 36/117 (24 sessions) | 0.4167 | 0.0000 | 0.0000 | 1.0000 | -0.0122 | -0.0213 | -0.2647 to 0.1935 |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 64/283 (44 sessions) | 0.7031 | 1.0000 | 0.0000 | 1.0000 | 18/117 (14 sessions) | 0.6667 | 0.5000 | 0.0000 | 1.0000 | 0.0365 | 0.0446 | -0.4358 to 0.4265 |
| stage10_9.price_vwap_side_change_count_6_bars | 206/283 (100 sessions) | 0.9563 | 1.0000 | 0.0000 | 2.0000 | 88/117 (55 sessions) | 1.1023 | 1.0000 | 0.0000 | 2.0000 | -0.1460 | -0.1328 | -0.4614 to 0.1396 |
| stage10_9.price_vwap_side_change_count_12_bars | 168/283 (81 sessions) | 1.6905 | 1.0000 | 0.0000 | 3.0000 | 66/117 (41 sessions) | 1.8030 | 1.0000 | 1.0000 | 3.0000 | -0.1126 | -0.0727 | -0.5584 to 0.3012 |
| stage10_9.price_vwap_side_change_count_24_bars | 114/283 (58 sessions) | 2.8158 | 2.0000 | 1.0000 | 4.0000 | 40/117 (26 sessions) | 2.6000 | 2.0000 | 1.0000 | 3.0000 | 0.2158 | 0.0932 | -0.7250 to 1.0945 |
| stage10_9.rolling_high_low_range_6_bars | 206/283 (100 sessions) | 2.0693 | 1.8225 | 1.3002 | 2.5512 | 88/117 (55 sessions) | 1.9906 | 1.7970 | 1.1888 | 2.5112 | 0.0787 | 0.0741 | -0.1836 to 0.3212 |
| stage10_9.rolling_high_low_range_12_bars | 168/283 (81 sessions) | 2.7633 | 2.4700 | 1.8175 | 3.3728 | 66/117 (41 sessions) | 2.6196 | 2.3125 | 1.4975 | 3.2601 | 0.1437 | 0.1038 | -0.2702 to 0.5180 |
| stage10_9.rolling_high_low_range_24_bars | 114/283 (58 sessions) | 3.5762 | 3.4100 | 2.2739 | 4.3850 | 40/117 (26 sessions) | 3.3864 | 2.7300 | 2.0562 | 3.5825 | 0.1898 | 0.1111 | -0.6772 to 0.9468 |
| stage10_9.rolling_range_atr14_6_bars | 154/283 (75 sessions) | 2.2094 | 2.0672 | 1.7073 | 2.6006 | 61/117 (39 sessions) | 2.1330 | 1.9325 | 1.5967 | 2.4372 | 0.0764 | 0.1148 | -0.1350 to 0.2788 |
| stage10_9.rolling_range_atr14_12_bars | 154/283 (75 sessions) | 3.0280 | 2.9586 | 2.4515 | 3.5091 | 61/117 (39 sessions) | 3.0113 | 2.8942 | 2.3639 | 3.4082 | 0.0167 | 0.0206 | -0.2367 to 0.2537 |
| stage10_9.rolling_range_atr14_24_bars | 114/283 (58 sessions) | 4.4150 | 4.3499 | 3.6027 | 5.1321 | 40/117 (26 sessions) | 4.4862 | 4.5321 | 3.8531 | 5.0138 | -0.0712 | -0.0675 | -0.3800 to 0.2655 |
| stage10_9.directional_efficiency_6_bars | 206/283 (100 sessions) | 0.4320 | 0.4000 | 0.2348 | 0.6413 | 88/117 (55 sessions) | 0.3536 | 0.2902 | 0.1253 | 0.5335 | 0.0784 | 0.2793 | 0.0071 to 0.1470 |
| stage10_9.directional_efficiency_12_bars | 168/283 (81 sessions) | 0.2581 | 0.2341 | 0.1052 | 0.3717 | 66/117 (41 sessions) | 0.2790 | 0.2723 | 0.1189 | 0.3844 | -0.0208 | -0.1124 | -0.0637 to 0.0216 |
| stage10_9.directional_efficiency_24_bars | 114/283 (58 sessions) | 0.1631 | 0.1311 | 0.0609 | 0.2467 | 40/117 (26 sessions) | 0.1690 | 0.1286 | 0.0418 | 0.2765 | -0.0059 | -0.0446 | -0.0525 to 0.0444 |
| stage10_9.range_overlap_fraction_6_bars | 206/283 (100 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 88/117 (55 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | 0.0000 to 0.0000 |
| stage10_9.range_overlap_fraction_12_bars | 168/283 (81 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 66/117 (41 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | 0.0000 to 0.0000 |
| stage10_9.range_overlap_fraction_24_bars | 114/283 (58 sessions) | 0.9992 | 1.0000 | 1.0000 | 1.0000 | 40/117 (26 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | -0.0008 | -0.1543 | -0.0020 to 0.0000 |
| stage10_9.close_direction_alternation_fraction_6_bars | 206/283 (100 sessions) | 0.5121 | 0.5000 | 0.2500 | 0.7500 | 88/117 (55 sessions) | 0.5142 | 0.5000 | 0.2500 | 0.7500 | -0.0021 | -0.0084 | -0.0619 to 0.0574 |
| stage10_9.close_direction_alternation_fraction_12_bars | 168/283 (81 sessions) | 0.5042 | 0.5000 | 0.4000 | 0.6000 | 66/117 (41 sessions) | 0.5000 | 0.5000 | 0.4000 | 0.6000 | 0.0042 | 0.0252 | -0.0341 to 0.0411 |
| stage10_9.close_direction_alternation_fraction_24_bars | 114/283 (58 sessions) | 0.5072 | 0.5000 | 0.4545 | 0.5795 | 40/117 (26 sessions) | 0.4852 | 0.5000 | 0.4091 | 0.5909 | 0.0219 | 0.1965 | -0.0220 to 0.0730 |
| stage10_9.confirmation_close_vwap_distance_atr14 | 154/283 (75 sessions) | 1.1639 | 1.0171 | 0.4997 | 1.5895 | 61/117 (39 sessions) | 1.1655 | 0.8049 | 0.5422 | 1.4050 | -0.0016 | -0.0016 | -0.4407 to 0.3234 |
| stage10_9.ema9_vwap_distance_atr14 | 154/283 (75 sessions) | 0.7500 | 0.5820 | 0.2986 | 0.9766 | 61/117 (39 sessions) | 0.8032 | 0.4981 | 0.1912 | 0.9179 | -0.0532 | -0.0654 | -0.4312 to 0.2308 |
| stage10_9.ema20_vwap_distance_atr14 | 128/283 (65 sessions) | 0.5843 | 0.4457 | 0.1781 | 0.7891 | 44/117 (29 sessions) | 0.7535 | 0.3996 | 0.2034 | 0.7872 | -0.1692 | -0.2338 | -0.5982 to 0.1384 |
| stage11_2.room_from_confirmation | 230/283 (109 sessions) | 1.8733 | 1.2650 | 0.5700 | 2.7275 | 92/117 (58 sessions) | 1.5191 | 1.3850 | 0.4975 | 2.3300 | 0.3542 | 0.2047 | -0.0471 to 0.7735 |
| stage11_2.room_in_atr | 131/283 (65 sessions) | 2.2231 | 1.3586 | 0.6297 | 3.1393 | 48/117 (33 sessions) | 1.5443 | 1.2244 | 0.3421 | 2.0439 | 0.6788 | 0.3215 | -0.0099 to 1.4661 |
| stage11_2.number_of_known_levels_above | 283/283 (132 sessions) | 1.4558 | 2.0000 | 1.0000 | 2.0000 | 117/117 (71 sessions) | 1.5214 | 2.0000 | 1.0000 | 2.0000 | -0.0655 | -0.0678 | -0.3220 to 0.1838 |
| stage11_2.number_of_known_levels_below | 283/283 (132 sessions) | 4.5300 | 4.0000 | 4.0000 | 5.0000 | 117/117 (71 sessions) | 4.4701 | 4.0000 | 4.0000 | 5.0000 | 0.0599 | 0.0620 | -0.1910 to 0.3159 |
| stage11_2.nearest_level_distance_above | 230/283 (109 sessions) | 1.8733 | 1.2650 | 0.5700 | 2.7275 | 92/117 (58 sessions) | 1.5191 | 1.3850 | 0.4975 | 2.3300 | 0.3542 | 0.2047 | -0.0471 to 0.7735 |
| stage11_2.nearest_level_distance_below | 283/283 (132 sessions) | 0.3513 | 0.2600 | 0.1275 | 0.4900 | 117/117 (71 sessions) | 0.1611 | 0.1100 | 0.0501 | 0.2200 | 0.1902 | 0.6885 | 0.1343 to 0.2438 |
| stage11_2.directional_level_count_within_0_5_atr | 154/283 (75 sessions) | 0.1883 | 0.0000 | 0.0000 | 0.0000 | 61/117 (39 sessions) | 0.2623 | 0.0000 | 0.0000 | 0.0000 | -0.0740 | -0.1721 | -0.2341 to 0.0664 |
| stage11_2.directional_level_count_within_1_0_atr | 154/283 (75 sessions) | 0.3571 | 0.0000 | 0.0000 | 1.0000 | 61/117 (39 sessions) | 0.3934 | 0.0000 | 0.0000 | 1.0000 | -0.0363 | -0.0673 | -0.2239 to 0.1233 |
| stage11_3.confirmation_close_to_latest_swing_high | 190/283 (91 sessions) | 0.7637 | 0.5250 | 0.2512 | 1.0375 | 84/117 (52 sessions) | 0.8971 | 0.6050 | 0.3588 | 1.1250 | -0.1333 | -0.1705 | -0.3644 to 0.0705 |
| stage11_3.confirmation_close_to_latest_swing_low | 190/283 (92 sessions) | 1.7906 | 1.5525 | 1.0200 | 2.2988 | 80/117 (50 sessions) | 1.6451 | 1.3500 | 0.7275 | 2.2066 | 0.1455 | 0.1175 | -0.1800 to 0.4583 |
| stage11_3.distance_to_swing_high_in_atr | 154/283 (75 sessions) | 0.9358 | 0.6426 | 0.3215 | 1.4209 | 61/117 (39 sessions) | 1.1203 | 0.7734 | 0.4393 | 1.4740 | -0.1845 | -0.2062 | -0.5113 to 0.1022 |
| stage11_3.distance_to_swing_low_in_atr | 153/283 (75 sessions) | 1.8696 | 1.7294 | 1.2495 | 2.3657 | 60/117 (38 sessions) | 1.6883 | 1.5582 | 0.8898 | 2.2186 | 0.1813 | 0.1788 | -0.1935 to 0.5107 |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG | 400 | 137 | 283 | 117 | 100.00% | 100.00% | 70.75% |
| time_bucket | 09:35-10:00 | 106 | 92 | 77 | 29 | 27.21% | 24.79% | 72.64% |
| time_bucket | 10:00-10:30 | 60 | 49 | 38 | 22 | 13.43% | 18.80% | 63.33% |
| time_bucket | 10:30-11:00 | 39 | 32 | 25 | 14 | 8.83% | 11.97% | 64.10% |
| time_bucket | 11:00-12:00 | 67 | 41 | 51 | 16 | 18.02% | 13.68% | 76.12% |
| time_bucket | 12:00-13:30 | 65 | 35 | 45 | 20 | 15.90% | 17.09% | 69.23% |
| time_bucket | 13:30-15:00 | 32 | 24 | 24 | 8 | 8.48% | 6.84% | 75.00% |
| time_bucket | 15:00-close | 31 | 24 | 23 | 8 | 8.13% | 6.84% | 74.19% |
| ema9_20_alignment | EMA_ALIGNED | 99 | 47 | 73 | 26 | 25.80% | 22.22% | 73.74% |
| ema9_20_alignment | EMA_NOT_ALIGNED | 73 | 41 | 55 | 18 | 19.43% | 15.38% | 75.34% |
| ema9_20_alignment | EMA_UNAVAILABLE | 228 | 126 | 155 | 73 | 54.77% | 62.39% | 67.98% |
| price_vwap_alignment | VWAP_ALIGNED | 351 | 137 | 248 | 103 | 87.63% | 88.03% | 70.66% |
| price_vwap_alignment | VWAP_NOT_ALIGNED | 49 | 26 | 35 | 14 | 12.37% | 11.97% | 71.43% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED | 192 | 82 | 135 | 57 | 47.70% | 48.72% | 70.31% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED | 73 | 38 | 52 | 21 | 18.37% | 17.95% | 71.23% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE | 135 | 107 | 96 | 39 | 33.92% | 33.33% | 71.11% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED | 117 | 52 | 85 | 32 | 30.04% | 27.35% | 72.65% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED | 55 | 34 | 43 | 12 | 15.19% | 10.26% | 78.18% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 228 | 126 | 155 | 73 | 54.77% | 62.39% | 67.98% |
| prior_ema_cross | MATCHING_CROSS | 45 | 28 | 33 | 12 | 11.66% | 10.26% | 73.33% |
| prior_ema_cross | NO_PRIOR_CROSS | 294 | 132 | 204 | 90 | 72.08% | 76.92% | 69.39% |
| prior_ema_cross | OPPOSING_CROSS | 61 | 34 | 46 | 15 | 16.25% | 12.82% | 75.41% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 267 | 91 | 193 | 74 | 68.20% | 63.25% | 72.28% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL | 125 | 67 | 84 | 41 | 29.68% | 35.04% | 67.20% |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 8 | 8 | 6 | 2 | 2.12% | 1.71% | 75.00% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 | 30 | 19 | 24 | 6 | 8.48% | 5.13% | 80.00% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 24 | 15 | 16 | 8 | 5.65% | 6.84% | 66.67% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 17 | 13 | 10 | 7 | 3.53% | 5.98% | 58.82% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 24 | 16 | 19 | 5 | 6.71% | 4.27% | 79.17% |
| stage11_2.room_bucket | GT_3_0_ATR | 41 | 21 | 34 | 7 | 12.01% | 5.98% | 82.93% |
| stage11_2.room_bucket | LT_0_5_ATR | 43 | 24 | 28 | 15 | 9.89% | 12.82% | 65.12% |
| stage11_2.room_bucket | OPEN_ENDED | 78 | 28 | 53 | 25 | 18.73% | 21.37% | 67.95% |
| stage11_2.room_bucket | UNAVAILABLE_ATR | 143 | 94 | 99 | 44 | 34.98% | 37.61% | 69.23% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 399 | 136 | 282 | 117 | 99.65% | 100.00% | 70.68% |
| known_level_coverage | PARTIAL_UNAVAILABLE [SMALL] | 1 | 1 | 1 | 0 | 0.35% | 0.00% | 100.00% |
| stage11_3.structure | BEARISH_STRUCTURE | 46 | 32 | 36 | 10 | 12.72% | 8.55% | 78.26% |
| stage11_3.structure | BULLISH_STRUCTURE | 61 | 41 | 44 | 17 | 15.55% | 14.53% | 72.13% |
| stage11_3.structure | MIXED_STRUCTURE | 84 | 47 | 58 | 26 | 20.49% | 22.22% | 69.05% |
| stage11_3.structure | UNAVAILABLE | 209 | 122 | 145 | 64 | 51.24% | 54.70% | 69.38% |
| stage11_3.agreement | STRUCTURE_ALIGNED | 61 | 41 | 44 | 17 | 15.55% | 14.53% | 72.13% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED | 130 | 56 | 94 | 36 | 33.22% | 30.77% | 72.31% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 209 | 122 | 145 | 64 | 51.24% | 54.70% | 69.38% |
| stage11_3.high_structure | EQUAL_HIGH [SMALL] | 1 | 1 | 1 | 0 | 0.35% | 0.00% | 100.00% |
| stage11_3.high_structure | HIGHER_HIGH | 104 | 56 | 75 | 29 | 26.50% | 24.79% | 72.12% |
| stage11_3.high_structure | LOWER_HIGH | 101 | 51 | 71 | 30 | 25.09% | 25.64% | 70.30% |
| stage11_3.high_structure | UNAVAILABLE | 194 | 120 | 136 | 58 | 48.06% | 49.57% | 70.10% |
| stage11_3.low_structure | EQUAL_LOW [SMALL] | 1 | 1 | 1 | 0 | 0.35% | 0.00% | 100.00% |
| stage11_3.low_structure | HIGHER_LOW | 122 | 64 | 82 | 40 | 28.98% | 34.19% | 67.21% |
| stage11_3.low_structure | LOWER_LOW | 85 | 48 | 67 | 18 | 23.67% | 15.38% | 78.82% |
| stage11_3.low_structure | UNAVAILABLE | 192 | 115 | 133 | 59 | 47.00% | 50.43% | 69.27% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE | 126 | 108 | 93 | 33 | 32.86% | 28.21% | 73.81% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED | 49 | 18 | 32 | 17 | 11.31% | 14.53% | 65.31% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL | 57 | 31 | 39 | 18 | 13.78% | 15.38% | 68.42% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL | 168 | 72 | 119 | 49 | 42.05% | 41.88% | 70.83% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 400 | 137 | 283 | 117 | 100.00% | 100.00% | 70.75% |


## Signal-time features: SHORT


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width | 241/241 (114 sessions) | 1.4644 | 1.4000 | 1.0000 | 1.8000 | 92/92 (69 sessions) | 1.3400 | 1.2700 | 0.9811 | 1.6200 | 0.1244 | 0.2276 | 0.0198 to 0.2256 |
| body_size | 241/241 (114 sessions) | 0.8524 | 0.6800 | 0.4200 | 1.1000 | 92/92 (69 sessions) | 0.6393 | 0.5300 | 0.3075 | 0.7875 | 0.2131 | 0.3420 | 0.0902 to 0.3335 |
| directional_body | 241/241 (114 sessions) | 0.8523 | 0.6800 | 0.4200 | 1.1000 | 92/92 (69 sessions) | 0.6393 | 0.5300 | 0.3075 | 0.7875 | 0.2130 | 0.3418 | 0.0902 to 0.3334 |
| candle_range | 241/241 (114 sessions) | 1.2001 | 1.0600 | 0.6600 | 1.5000 | 92/92 (69 sessions) | 1.0417 | 0.8597 | 0.6587 | 1.3938 | 0.1584 | 0.2205 | 0.0040 to 0.3025 |
| body_range_ratio | 241/241 (114 sessions) | 0.6741 | 0.7080 | 0.5461 | 0.8254 | 92/92 (69 sessions) | 0.5879 | 0.5846 | 0.4335 | 0.7353 | 0.0862 | 0.4096 | 0.0345 to 0.1375 |
| directional_body_range_ratio | 241/241 (114 sessions) | 0.6739 | 0.7080 | 0.5461 | 0.8254 | 92/92 (69 sessions) | 0.5879 | 0.5846 | 0.4335 | 0.7353 | 0.0860 | 0.4075 | 0.0343 to 0.1372 |
| close_location | 241/241 (114 sessions) | 0.1667 | 0.1265 | 0.0440 | 0.2235 | 92/92 (69 sessions) | 0.2087 | 0.1808 | 0.0792 | 0.2795 | -0.0420 | -0.2570 | -0.0798 to -0.0054 |
| directional_close_location | 241/241 (114 sessions) | 0.8333 | 0.8735 | 0.7765 | 0.9560 | 92/92 (69 sessions) | 0.7913 | 0.8192 | 0.7205 | 0.9208 | 0.0420 | 0.2570 | 0.0054 to 0.0798 |
| distance_beyond_level | 241/241 (114 sessions) | 0.4838 | 0.3401 | 0.1500 | 0.6100 | 92/92 (69 sessions) | 0.2468 | 0.1700 | 0.0800 | 0.3402 | 0.2370 | 0.4876 | 0.1581 to 0.3183 |
| distance_beyond_level_atr14 | 139/241 (74 sessions) | 0.4627 | 0.3309 | 0.1471 | 0.6675 | 46/92 (34 sessions) | 0.2923 | 0.2130 | 0.1083 | 0.4224 | 0.1704 | 0.3450 | 0.0650 to 0.2808 |
| candle_volume | 241/241 (114 sessions) | 816884.0415 | 614737.0000 | 398456.0000 | 1011276.0000 | 92/92 (69 sessions) | 962652.6196 | 747633.0000 | 495177.7500 | 1087884.0000 | -145768.5781 | -0.2181 | -336514.1618 to 22687.2373 |
| relative_volume_prior_6 | 175/241 (88 sessions) | 1.2425 | 0.9692 | 0.7154 | 1.4464 | 60/92 (44 sessions) | 1.5201 | 1.1090 | 0.8158 | 1.7954 | -0.2776 | -0.2624 | -0.5999 to 0.0189 |
| atr14 | 139/241 (74 sessions) | 0.8687 | 0.7781 | 0.5852 | 1.0595 | 46/92 (34 sessions) | 0.7682 | 0.6388 | 0.4776 | 1.0233 | 0.1005 | 0.2613 | -0.0470 to 0.2406 |
| minutes_since_open | 241/241 (114 sessions) | 127.4689 | 90.0000 | 30.0000 | 200.0000 | 92/92 (69 sessions) | 137.4457 | 70.0000 | 20.0000 | 240.0000 | -9.9768 | -0.0833 | -40.6014 to 20.6467 |
| minutes_since_ema_cross | 85/241 (52 sessions) | 48.7647 | 40.0000 | 15.0000 | 75.0000 | 37/92 (27 sessions) | 50.4054 | 35.0000 | 15.0000 | 75.0000 | -1.6407 | -0.0372 | -17.2707 to 13.0526 |
| break_attempt_rank | 241/241 (114 sessions) | 6.6929 | 6.0000 | 3.0000 | 10.0000 | 92/92 (69 sessions) | 6.2609 | 5.0000 | 2.0000 | 9.0000 | 0.4321 | 0.0892 | -0.6410 to 1.4646 |
| valid_hold_sequence_rank | 241/241 (114 sessions) | 3.6390 | 3.0000 | 2.0000 | 5.0000 | 92/92 (69 sessions) | 3.5543 | 3.0000 | 1.0000 | 5.0000 | 0.0847 | 0.0339 | -0.5040 to 0.6465 |
| stage10_9.ema9_ema20_absolute_separation | 115/241 (64 sessions) | 0.3180 | 0.2270 | 0.1214 | 0.4361 | 41/92 (30 sessions) | 0.3091 | 0.2126 | 0.1230 | 0.3969 | 0.0088 | 0.0291 | -0.1160 to 0.1370 |
| stage10_9.ema9_ema20_separation_atr14 | 115/241 (64 sessions) | 0.3748 | 0.3396 | 0.1795 | 0.5284 | 41/92 (30 sessions) | 0.4092 | 0.3750 | 0.1995 | 0.5919 | -0.0344 | -0.1283 | -0.1392 to 0.0658 |
| stage10_9.ema9_slope_1_bars | 157/241 (80 sessions) | -0.1538 | -0.1284 | -0.2307 | -0.0614 | 54/92 (40 sessions) | -0.1715 | -0.1658 | -0.2638 | -0.0660 | 0.0177 | 0.1072 | -0.0285 to 0.0644 |
| stage10_9.ema9_slope_2_bars | 153/241 (78 sessions) | -0.0844 | -0.0747 | -0.1627 | -0.0020 | 50/92 (38 sessions) | -0.1119 | -0.1078 | -0.2023 | -0.0177 | 0.0275 | 0.1850 | -0.0177 to 0.0722 |
| stage10_9.ema9_slope_3_bars | 146/241 (77 sessions) | -0.0663 | -0.0525 | -0.1412 | 0.0194 | 49/92 (37 sessions) | -0.0944 | -0.0971 | -0.1567 | -0.0117 | 0.0281 | 0.2038 | -0.0169 to 0.0724 |
| stage10_9.ema20_slope_1_bars | 109/241 (62 sessions) | -0.0826 | -0.0725 | -0.1279 | -0.0170 | 39/92 (28 sessions) | -0.0806 | -0.0760 | -0.1329 | -0.0154 | -0.0020 | -0.0192 | -0.0411 to 0.0376 |
| stage10_9.ema20_slope_2_bars | 107/241 (61 sessions) | -0.0498 | -0.0448 | -0.0991 | 0.0099 | 38/92 (28 sessions) | -0.0509 | -0.0581 | -0.1004 | -0.0048 | 0.0011 | 0.0122 | -0.0328 to 0.0351 |
| stage10_9.ema20_slope_3_bars | 102/241 (58 sessions) | -0.0416 | -0.0344 | -0.0875 | 0.0152 | 38/92 (28 sessions) | -0.0411 | -0.0508 | -0.0930 | 0.0027 | -0.0005 | -0.0056 | -0.0352 to 0.0338 |
| stage10_9.vwap_slope_1_bars | 241/241 (114 sessions) | -0.0983 | -0.0368 | -0.1307 | -0.0061 | 92/92 (69 sessions) | -0.0846 | -0.0460 | -0.1475 | -0.0108 | -0.0137 | -0.0987 | -0.0426 to 0.0138 |
| stage10_9.vwap_slope_2_bars | 221/241 (104 sessions) | -0.0439 | -0.0162 | -0.0513 | -0.0023 | 79/92 (61 sessions) | -0.0399 | -0.0292 | -0.0644 | -0.0057 | -0.0040 | -0.0527 | -0.0205 to 0.0124 |
| stage10_9.vwap_slope_3_bars | 205/241 (94 sessions) | -0.0327 | -0.0147 | -0.0479 | -0.0012 | 70/92 (53 sessions) | -0.0263 | -0.0219 | -0.0492 | -0.0041 | -0.0064 | -0.1203 | -0.0191 to 0.0058 |
| stage10_9.ema9_ema20_cross_count_6_bars | 98/241 (57 sessions) | 0.3571 | 0.0000 | 0.0000 | 1.0000 | 37/92 (27 sessions) | 0.4054 | 0.0000 | 0.0000 | 1.0000 | -0.0483 | -0.0826 | -0.2342 to 0.1486 |
| stage10_9.ema9_ema20_cross_count_12_bars | 82/241 (54 sessions) | 0.6707 | 0.5000 | 0.0000 | 1.0000 | 35/92 (26 sessions) | 0.6857 | 1.0000 | 0.0000 | 1.0000 | -0.0150 | -0.0195 | -0.3107 to 0.3035 |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 55/241 (39 sessions) | 1.2364 | 1.0000 | 1.0000 | 1.0000 | 26/92 (22 sessions) | 1.1538 | 1.0000 | 1.0000 | 1.0000 | 0.0825 | 0.0869 | -0.3044 to 0.4774 |
| stage10_9.ema9_vwap_cross_count_6_bars | 139/241 (74 sessions) | 0.3669 | 0.0000 | 0.0000 | 1.0000 | 46/92 (34 sessions) | 0.3261 | 0.0000 | 0.0000 | 1.0000 | 0.0408 | 0.0763 | -0.1037 to 0.1832 |
| stage10_9.ema9_vwap_cross_count_12_bars | 115/241 (64 sessions) | 0.7130 | 1.0000 | 0.0000 | 1.0000 | 41/92 (30 sessions) | 0.5122 | 0.0000 | 0.0000 | 1.0000 | 0.2008 | 0.2660 | -0.0395 to 0.4539 |
| stage10_9.ema9_vwap_cross_count_24_bars | 81/241 (54 sessions) | 1.0247 | 1.0000 | 1.0000 | 1.0000 | 35/92 (26 sessions) | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.0247 | 0.0269 | -0.3363 to 0.3628 |
| stage10_9.ema20_vwap_cross_count_6_bars | 98/241 (57 sessions) | 0.1837 | 0.0000 | 0.0000 | 0.0000 | 37/92 (27 sessions) | 0.1892 | 0.0000 | 0.0000 | 0.0000 | -0.0055 | -0.0141 | -0.1528 to 0.1397 |
| stage10_9.ema20_vwap_cross_count_12_bars | 82/241 (54 sessions) | 0.3537 | 0.0000 | 0.0000 | 1.0000 | 35/92 (26 sessions) | 0.3429 | 0.0000 | 0.0000 | 1.0000 | 0.0108 | 0.0197 | -0.2033 to 0.2150 |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 55/241 (39 sessions) | 0.4909 | 0.0000 | 0.0000 | 1.0000 | 26/92 (22 sessions) | 0.5000 | 0.0000 | 0.0000 | 1.0000 | -0.0091 | -0.0147 | -0.3430 to 0.2800 |
| stage10_9.price_vwap_side_change_count_6_bars | 182/241 (89 sessions) | 1.1538 | 1.0000 | 0.0000 | 2.0000 | 65/92 (49 sessions) | 0.9077 | 1.0000 | 0.0000 | 1.0000 | 0.2462 | 0.2220 | -0.0491 to 0.5234 |
| stage10_9.price_vwap_side_change_count_12_bars | 146/241 (77 sessions) | 2.0479 | 2.0000 | 1.0000 | 3.0000 | 49/92 (37 sessions) | 1.4490 | 1.0000 | 0.0000 | 2.0000 | 0.5990 | 0.3779 | 0.1172 to 1.0761 |
| stage10_9.price_vwap_side_change_count_24_bars | 101/241 (58 sessions) | 3.1386 | 3.0000 | 1.0000 | 5.0000 | 38/92 (28 sessions) | 2.3421 | 1.5000 | 1.0000 | 4.0000 | 0.7965 | 0.3403 | -0.0991 to 1.6702 |
| stage10_9.rolling_high_low_range_6_bars | 182/241 (89 sessions) | 2.2132 | 2.0175 | 1.2812 | 2.8438 | 65/92 (49 sessions) | 2.1281 | 1.9100 | 1.4400 | 2.8200 | 0.0851 | 0.0722 | -0.2516 to 0.4115 |
| stage10_9.rolling_high_low_range_12_bars | 146/241 (77 sessions) | 2.8484 | 2.4725 | 1.6762 | 3.4250 | 49/92 (37 sessions) | 2.6264 | 2.0000 | 1.6400 | 3.3600 | 0.2219 | 0.1441 | -0.3047 to 0.7258 |
| stage10_9.rolling_high_low_range_24_bars | 101/241 (58 sessions) | 3.5388 | 3.2480 | 2.0700 | 4.3900 | 38/92 (28 sessions) | 3.3831 | 2.9800 | 2.1988 | 4.4525 | 0.1558 | 0.0858 | -0.6158 to 0.9027 |
| stage10_9.rolling_range_atr14_6_bars | 139/241 (74 sessions) | 2.3564 | 2.2356 | 1.8490 | 2.5972 | 46/92 (34 sessions) | 2.5720 | 2.5264 | 1.9527 | 3.1996 | -0.2156 | -0.2666 | -0.5134 to 0.0939 |
| stage10_9.rolling_range_atr14_12_bars | 139/241 (74 sessions) | 3.2075 | 2.9951 | 2.5132 | 3.8084 | 46/92 (34 sessions) | 3.3754 | 3.3272 | 2.7309 | 3.7944 | -0.1680 | -0.1854 | -0.4263 to 0.0969 |
| stage10_9.rolling_range_atr14_24_bars | 101/241 (58 sessions) | 4.4512 | 4.1989 | 3.6076 | 5.1172 | 38/92 (28 sessions) | 4.8725 | 4.7998 | 3.9821 | 5.3779 | -0.4213 | -0.3581 | -0.9251 to 0.0424 |
| stage10_9.directional_efficiency_6_bars | 182/241 (89 sessions) | 0.4766 | 0.4632 | 0.2307 | 0.7159 | 65/92 (49 sessions) | 0.5123 | 0.4905 | 0.2350 | 0.7728 | -0.0357 | -0.1191 | -0.1190 to 0.0474 |
| stage10_9.directional_efficiency_12_bars | 146/241 (77 sessions) | 0.3077 | 0.2664 | 0.1224 | 0.4609 | 49/92 (37 sessions) | 0.3354 | 0.3491 | 0.1407 | 0.5130 | -0.0277 | -0.1276 | -0.0854 to 0.0338 |
| stage10_9.directional_efficiency_24_bars | 101/241 (58 sessions) | 0.1932 | 0.1689 | 0.0705 | 0.2726 | 38/92 (28 sessions) | 0.2343 | 0.2271 | 0.0975 | 0.3321 | -0.0411 | -0.2739 | -0.1006 to 0.0149 |
| stage10_9.range_overlap_fraction_6_bars | 182/241 (89 sessions) | 0.9989 | 1.0000 | 1.0000 | 1.0000 | 65/92 (49 sessions) | 0.9969 | 1.0000 | 1.0000 | 1.0000 | 0.0020 | 0.1100 | 0.0000 to 0.0070 |
| stage10_9.range_overlap_fraction_12_bars | 146/241 (77 sessions) | 0.9988 | 1.0000 | 1.0000 | 1.0000 | 49/92 (37 sessions) | 0.9981 | 1.0000 | 1.0000 | 1.0000 | 0.0006 | 0.0542 | 0.0000 to 0.0026 |
| stage10_9.range_overlap_fraction_24_bars | 101/241 (58 sessions) | 0.9991 | 1.0000 | 1.0000 | 1.0000 | 38/92 (28 sessions) | 0.9989 | 1.0000 | 1.0000 | 1.0000 | 0.0003 | 0.0445 | -0.0000 to 0.0014 |
| stage10_9.close_direction_alternation_fraction_6_bars | 182/241 (89 sessions) | 0.5371 | 0.5000 | 0.5000 | 0.7500 | 65/92 (49 sessions) | 0.4692 | 0.5000 | 0.2500 | 0.7500 | 0.0679 | 0.2635 | -0.0080 to 0.1435 |
| stage10_9.close_direction_alternation_fraction_12_bars | 146/241 (77 sessions) | 0.5288 | 0.5500 | 0.4000 | 0.6000 | 49/92 (37 sessions) | 0.4735 | 0.5000 | 0.4000 | 0.6000 | 0.0553 | 0.3608 | 0.0162 to 0.0939 |
| stage10_9.close_direction_alternation_fraction_24_bars | 101/241 (58 sessions) | 0.5221 | 0.5455 | 0.4545 | 0.5909 | 38/92 (28 sessions) | 0.5012 | 0.5000 | 0.4205 | 0.5909 | 0.0209 | 0.1767 | -0.0200 to 0.0599 |
| stage10_9.confirmation_close_vwap_distance_atr14 | 139/241 (74 sessions) | 1.2807 | 1.1382 | 0.5459 | 1.7665 | 46/92 (34 sessions) | 1.6760 | 1.5833 | 1.1439 | 2.2326 | -0.3954 | -0.4409 | -0.6963 to -0.1000 |
| stage10_9.ema9_vwap_distance_atr14 | 139/241 (74 sessions) | 0.6643 | 0.4950 | 0.2068 | 0.9484 | 46/92 (34 sessions) | 0.8882 | 0.8444 | 0.3041 | 1.1877 | -0.2239 | -0.3751 | -0.4591 to -0.0180 |
| stage10_9.ema20_vwap_distance_atr14 | 115/241 (64 sessions) | 0.4892 | 0.3062 | 0.1612 | 0.7733 | 41/92 (30 sessions) | 0.6896 | 0.5596 | 0.3323 | 1.0003 | -0.2003 | -0.4149 | -0.3786 to -0.0295 |
| stage11_2.room_from_confirmation | 201/241 (104 sessions) | 1.9117 | 1.3900 | 0.4700 | 2.5050 | 86/92 (64 sessions) | 1.5620 | 0.9700 | 0.3450 | 2.1475 | 0.3497 | 0.1746 | -0.0314 to 0.7080 |
| stage11_2.room_in_atr | 113/241 (65 sessions) | 2.2132 | 1.6816 | 0.6647 | 2.9010 | 43/92 (31 sessions) | 1.7898 | 1.2270 | 0.5407 | 2.0492 | 0.4234 | 0.2022 | -0.2181 to 0.9909 |
| stage11_2.number_of_known_levels_above | 241/241 (114 sessions) | 4.4689 | 4.0000 | 4.0000 | 5.0000 | 92/92 (69 sessions) | 4.2174 | 4.0000 | 4.0000 | 5.0000 | 0.2515 | 0.2839 | 0.0477 to 0.4584 |
| stage11_2.number_of_known_levels_below | 241/241 (114 sessions) | 1.5187 | 2.0000 | 1.0000 | 2.0000 | 92/92 (69 sessions) | 1.7826 | 2.0000 | 1.0000 | 2.0000 | -0.2639 | -0.2979 | -0.4708 to -0.0600 |
| stage11_2.nearest_level_distance_above | 241/241 (114 sessions) | 0.4068 | 0.2750 | 0.1127 | 0.5001 | 92/92 (69 sessions) | 0.2318 | 0.1700 | 0.0700 | 0.3162 | 0.1750 | 0.3997 | 0.1025 to 0.2529 |
| stage11_2.nearest_level_distance_below | 201/241 (104 sessions) | 1.9117 | 1.3900 | 0.4700 | 2.5050 | 86/92 (64 sessions) | 1.5620 | 0.9700 | 0.3450 | 2.1475 | 0.3497 | 0.1746 | -0.0314 to 0.7080 |
| stage11_2.directional_level_count_within_0_5_atr | 139/241 (74 sessions) | 0.1799 | 0.0000 | 0.0000 | 0.0000 | 46/92 (34 sessions) | 0.2391 | 0.0000 | 0.0000 | 0.0000 | -0.0593 | -0.1320 | -0.2430 to 0.1089 |
| stage11_2.directional_level_count_within_1_0_atr | 139/241 (74 sessions) | 0.3669 | 0.0000 | 0.0000 | 1.0000 | 46/92 (34 sessions) | 0.4130 | 0.0000 | 0.0000 | 1.0000 | -0.0461 | -0.0760 | -0.2345 to 0.1402 |
| stage11_3.confirmation_close_to_latest_swing_high | 175/241 (88 sessions) | 1.9532 | 1.6150 | 0.9640 | 2.5425 | 59/92 (44 sessions) | 1.8188 | 1.5800 | 0.9550 | 2.2725 | 0.1344 | 0.0964 | -0.2423 to 0.4973 |
| stage11_3.confirmation_close_to_latest_swing_low | 169/241 (84 sessions) | 0.9028 | 0.5600 | 0.3000 | 1.2900 | 56/92 (43 sessions) | 0.8784 | 0.6325 | 0.2969 | 1.2125 | 0.0244 | 0.0276 | -0.2233 to 0.2632 |
| stage11_3.distance_to_swing_high_in_atr | 139/241 (74 sessions) | 2.1237 | 1.8673 | 1.2853 | 2.7358 | 46/92 (34 sessions) | 2.2946 | 2.1418 | 1.4397 | 3.0875 | -0.1709 | -0.1382 | -0.5372 to 0.2040 |
| stage11_3.distance_to_swing_low_in_atr | 137/241 (72 sessions) | 1.0548 | 0.8405 | 0.3888 | 1.4723 | 44/92 (33 sessions) | 1.1889 | 0.9209 | 0.6055 | 1.7717 | -0.1341 | -0.1484 | -0.4014 to 0.1185 |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | SHORT | 333 | 129 | 241 | 92 | 100.00% | 100.00% | 72.37% |
| time_bucket | 09:35-10:00 | 86 | 74 | 59 | 27 | 24.48% | 29.35% | 68.60% |
| time_bucket | 10:00-10:30 | 52 | 48 | 36 | 16 | 14.94% | 17.39% | 69.23% |
| time_bucket | 10:30-11:00 | 33 | 26 | 25 | 8 | 10.37% | 8.70% | 75.76% |
| time_bucket | 11:00-12:00 | 38 | 28 | 32 | 6 | 13.28% | 6.52% | 84.21% |
| time_bucket | 12:00-13:30 | 53 | 35 | 41 | 12 | 17.01% | 13.04% | 77.36% |
| time_bucket | 13:30-15:00 | 35 | 30 | 30 | 5 | 12.45% | 5.43% | 85.71% |
| time_bucket | 15:00-close | 36 | 26 | 18 | 18 | 7.47% | 19.57% | 50.00% |
| ema9_20_alignment | EMA_ALIGNED | 112 | 54 | 81 | 31 | 33.61% | 33.70% | 72.32% |
| ema9_20_alignment | EMA_NOT_ALIGNED | 44 | 28 | 34 | 10 | 14.11% | 10.87% | 77.27% |
| ema9_20_alignment | EMA_UNAVAILABLE | 177 | 109 | 126 | 51 | 52.28% | 55.43% | 71.19% |
| price_vwap_alignment | VWAP_ALIGNED | 300 | 129 | 215 | 85 | 89.21% | 92.39% | 71.67% |
| price_vwap_alignment | VWAP_NOT_ALIGNED | 33 | 20 | 26 | 7 | 10.79% | 7.61% | 78.79% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED | 157 | 71 | 120 | 37 | 49.79% | 40.22% | 76.43% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED | 63 | 40 | 46 | 17 | 19.09% | 18.48% | 73.02% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE | 113 | 87 | 75 | 38 | 31.12% | 41.30% | 66.37% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED | 101 | 48 | 77 | 24 | 31.95% | 26.09% | 76.24% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED | 55 | 41 | 38 | 17 | 15.77% | 18.48% | 69.09% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 177 | 109 | 126 | 51 | 52.28% | 55.43% | 71.19% |
| prior_ema_cross | MATCHING_CROSS | 84 | 43 | 57 | 27 | 23.65% | 29.35% | 67.86% |
| prior_ema_cross | NO_PRIOR_CROSS | 211 | 117 | 156 | 55 | 64.73% | 59.78% | 73.93% |
| prior_ema_cross | OPPOSING_CROSS | 38 | 24 | 28 | 10 | 11.62% | 10.87% | 73.68% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 224 | 94 | 166 | 58 | 68.88% | 63.04% | 74.11% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL | 108 | 56 | 75 | 33 | 31.12% | 35.87% | 69.44% |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 1 | 1 | 0 | 1 | 0.00% | 1.09% | 0.00% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 26 | 20 | 19 | 7 | 7.88% | 7.61% | 73.08% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 16 | 12 | 10 | 6 | 4.15% | 6.52% | 62.50% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 21 | 16 | 13 | 8 | 5.39% | 8.70% | 61.90% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 27 | 21 | 22 | 5 | 9.13% | 5.43% | 81.48% |
| stage11_2.room_bucket | GT_3_0_ATR | 34 | 16 | 27 | 7 | 11.20% | 7.61% | 79.41% |
| stage11_2.room_bucket | LT_0_5_ATR | 32 | 21 | 22 | 10 | 9.13% | 10.87% | 68.75% |
| stage11_2.room_bucket | OPEN_ENDED | 46 | 15 | 40 | 6 | 16.60% | 6.52% | 86.96% |
| stage11_2.room_bucket | UNAVAILABLE_ATR | 131 | 95 | 88 | 43 | 36.51% | 46.74% | 67.18% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 332 | 128 | 240 | 92 | 99.59% | 100.00% | 72.29% |
| known_level_coverage | PARTIAL_UNAVAILABLE [SMALL] | 1 | 1 | 1 | 0 | 0.41% | 0.00% | 100.00% |
| stage11_3.structure | BEARISH_STRUCTURE | 55 | 42 | 41 | 14 | 17.01% | 15.22% | 74.55% |
| stage11_3.structure | BULLISH_STRUCTURE | 41 | 33 | 32 | 9 | 13.28% | 9.78% | 78.05% |
| stage11_3.structure | MIXED_STRUCTURE | 68 | 43 | 49 | 19 | 20.33% | 20.65% | 72.06% |
| stage11_3.structure | UNAVAILABLE | 169 | 110 | 119 | 50 | 49.38% | 54.35% | 70.41% |
| stage11_3.agreement | STRUCTURE_ALIGNED | 55 | 42 | 41 | 14 | 17.01% | 15.22% | 74.55% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED | 109 | 58 | 81 | 28 | 33.61% | 30.43% | 74.31% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 169 | 110 | 119 | 50 | 49.38% | 54.35% | 70.41% |
| stage11_3.high_structure | EQUAL_HIGH [SMALL] | 3 | 2 | 3 | 0 | 1.24% | 0.00% | 100.00% |
| stage11_3.high_structure | HIGHER_HIGH | 71 | 49 | 55 | 16 | 22.82% | 17.39% | 77.46% |
| stage11_3.high_structure | LOWER_HIGH | 113 | 61 | 81 | 32 | 33.61% | 34.78% | 71.68% |
| stage11_3.high_structure | UNAVAILABLE | 146 | 100 | 102 | 44 | 42.32% | 47.83% | 69.86% |
| stage11_3.low_structure | EQUAL_LOW [SMALL] | 2 | 1 | 1 | 1 | 0.41% | 1.09% | 50.00% |
| stage11_3.low_structure | HIGHER_LOW | 92 | 54 | 67 | 25 | 27.80% | 27.17% | 72.83% |
| stage11_3.low_structure | LOWER_LOW | 75 | 53 | 58 | 17 | 24.07% | 18.48% | 77.33% |
| stage11_3.low_structure | UNAVAILABLE | 164 | 110 | 115 | 49 | 47.72% | 53.26% | 70.12% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE | 108 | 91 | 72 | 36 | 29.88% | 39.13% | 66.67% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED | 37 | 15 | 32 | 5 | 13.28% | 5.43% | 86.49% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL | 42 | 26 | 28 | 14 | 11.62% | 15.22% | 66.67% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL | 146 | 78 | 109 | 37 | 45.23% | 40.22% | 74.66% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 333 | 129 | 241 | 92 | 100.00% | 100.00% | 72.37% |


## Continuous feature versus separate outcome-quality evaluations

Excursion associations are Spearman correlations. Threshold associations are point-biserial correlations with clean favorable-first = 1 and other evaluable outcomes = 0. Ambiguous and no-future observations are excluded from these correlations only, with evaluable n shown; their counts remain in JSON and categorical outcome tables. These descriptive correlations have no independent-significance claim. No continuous variable is bucketed or optimized.

### REFERENCE_CLOSE_V1: ALL evaluation labels

Labels are retrospective evaluations, never predictors. Never-strong includes session-close censoring; longer pre-reclaim exposure in eventual-strong sequences is not a causal benefit.

| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EVENTUAL_STRONG | 524 | 170 | 283/241 | 524 | 2.1325 | 2.8068 | 1.5000 | 2.3060 | 1.2171 | 0.1700 | 72.90% |
| NEVER_STRONG | 209 | 107 | 117/92 | 203 | 1.4300 | 2.2105 | 2.4350 | 3.1115 | 0.7104 | -0.5800 | 97.13% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| EVENTUAL_STRONG | 524 | 61.07% | 50.19% | 39.89% | 33.97% | 54.01% | 43.32% | 37.21% | 26.91% | 21.18% |
| NEVER_STRONG | 209 | 17.22% | 5.26% | 2.87% | 0.96% | 7.66% | 3.35% | 1.44% | 0.96% | 0.96% |


### REFERENCE_CLOSE_V1: ALL continuous


| feature | pre_reclaim_mfe: r (n) | pre_reclaim_mae: r (n) | 0.25/0.25: r (n) | 0.50/0.25: r (n) | 0.50/0.30: r (n) | 1.00/0.30: r (n) |
|---|---|---|---|---|---|---|
| opening_range_width | 0.1152 (727) | 0.2310 (727) | 0.0074 (689) | 0.0209 (719) | 0.0169 (722) | 0.0661 (725) |
| body_size | 0.2417 (727) | 0.4874 (727) | 0.0233 (689) | 0.0380 (719) | 0.0226 (722) | 0.0659 (725) |
| directional_body | 0.2417 (727) | 0.4874 (727) | 0.0232 (689) | 0.0380 (719) | 0.0225 (722) | 0.0658 (725) |
| candle_range | 0.2383 (727) | 0.5375 (727) | 0.0432 (689) | 0.0466 (719) | 0.0263 (722) | 0.0773 (725) |
| body_range_ratio | 0.1303 (727) | 0.1616 (727) | -0.0154 (689) | -0.0103 (719) | -0.0070 (722) | 0.0200 (725) |
| directional_body_range_ratio | 0.1303 (727) | 0.1616 (727) | -0.0158 (689) | -0.0107 (719) | -0.0074 (722) | 0.0195 (725) |
| close_location | -0.0422 (727) | 0.0051 (727) | -0.0233 (689) | -0.0626 (719) | -0.0346 (722) | -0.0261 (725) |
| directional_close_location | 0.0169 (727) | 0.1657 (727) | -0.0898 (689) | -0.0763 (719) | -0.0697 (722) | -0.0382 (725) |
| distance_beyond_level | 0.2482 (727) | 0.4918 (727) | 0.0588 (689) | 0.0618 (719) | 0.0493 (722) | 0.1039 (725) |
| distance_beyond_level_atr14 | 0.1539 (394) | 0.3244 (394) | 0.0218 (381) | 0.0225 (389) | 0.0257 (390) | 0.0565 (392) |
| candle_volume | 0.1877 (727) | 0.3189 (727) | 0.0557 (689) | 0.0665 (719) | 0.0449 (722) | 0.0856 (725) |
| relative_volume_prior_6 | 0.0985 (509) | -0.0141 (509) | 0.0625 (491) | 0.0464 (504) | 0.0514 (505) | 0.1098 (507) |
| atr14 | 0.2705 (394) | 0.4805 (394) | 0.0472 (381) | 0.0837 (389) | 0.0450 (390) | 0.0933 (392) |
| minutes_since_open | -0.0839 (727) | -0.3077 (727) | 0.0460 (689) | 0.0238 (719) | 0.0457 (722) | -0.0191 (725) |
| minutes_since_ema_cross | -0.0413 (222) | -0.1204 (222) | 0.0301 (216) | -0.0452 (220) | -0.0559 (221) | -0.0520 (221) |
| break_attempt_rank | -0.0438 (727) | -0.2683 (727) | 0.0783 (689) | 0.0564 (719) | 0.0685 (722) | -0.0153 (725) |
| valid_hold_sequence_rank | -0.0705 (727) | -0.2527 (727) | 0.0267 (689) | 0.0175 (719) | 0.0289 (722) | -0.0338 (725) |
| stage10_9.ema9_ema20_absolute_separation | 0.0568 (322) | 0.2270 (322) | 0.0013 (313) | 0.0316 (320) | 0.0284 (321) | 0.0618 (321) |
| stage10_9.ema9_ema20_separation_atr14 | -0.0314 (322) | 0.0644 (322) | -0.0576 (313) | -0.0366 (320) | -0.0068 (321) | -0.0089 (321) |
| stage10_9.ema9_slope_1_bars | 0.0054 (462) | -0.0132 (462) | 0.0364 (445) | -0.0027 (457) | 0.0131 (458) | 0.0046 (460) |
| stage10_9.ema9_slope_2_bars | 0.0075 (442) | -0.0635 (442) | 0.0337 (426) | -0.0019 (437) | 0.0132 (438) | 0.0168 (440) |
| stage10_9.ema9_slope_3_bars | 0.0037 (423) | -0.0601 (423) | 0.0141 (409) | -0.0183 (418) | -0.0008 (419) | 0.0092 (421) |
| stage10_9.ema20_slope_1_bars | -0.0412 (308) | -0.0801 (308) | -0.0013 (299) | -0.0297 (306) | 0.0024 (307) | -0.0291 (307) |
| stage10_9.ema20_slope_2_bars | -0.0382 (300) | -0.1100 (300) | 0.0055 (292) | 0.0041 (298) | 0.0359 (299) | 0.0122 (299) |
| stage10_9.ema20_slope_3_bars | -0.0421 (291) | -0.1017 (291) | -0.0128 (284) | -0.0033 (289) | 0.0334 (290) | -0.0087 (290) |
| stage10_9.vwap_slope_1_bars | -0.0145 (727) | -0.0137 (727) | -0.0635 (689) | -0.0562 (719) | -0.0458 (722) | -0.0623 (725) |
| stage10_9.vwap_slope_2_bars | -0.0166 (649) | -0.0390 (649) | -0.0294 (619) | -0.0388 (641) | -0.0259 (644) | -0.0485 (647) |
| stage10_9.vwap_slope_3_bars | -0.0278 (604) | -0.0285 (604) | -0.0773 (578) | -0.0529 (597) | -0.0527 (599) | -0.0600 (602) |
| stage10_9.ema9_ema20_cross_count_6_bars | 0.0422 (279) | 0.0195 (279) | 0.0268 (272) | 0.0695 (277) | 0.0769 (278) | 0.0570 (278) |
| stage10_9.ema9_ema20_cross_count_12_bars | 0.0847 (236) | 0.0168 (236) | -0.0113 (231) | 0.0857 (234) | 0.0766 (235) | 0.1077 (235) |
| stage10_9.ema9_ema20_cross_count_24_bars | 0.0598 (157) | 0.1174 (157) | 0.0284 (153) | 0.0627 (156) | 0.0354 (156) | 0.0510 (156) |
| stage10_9.ema9_vwap_cross_count_6_bars | -0.0137 (394) | 0.0435 (394) | -0.0121 (381) | -0.0254 (389) | 0.0149 (390) | -0.0545 (392) |
| stage10_9.ema9_vwap_cross_count_12_bars | 0.0882 (322) | -0.0455 (322) | 0.0601 (313) | 0.0866 (320) | 0.1195 (321) | 0.0282 (321) |
| stage10_9.ema9_vwap_cross_count_24_bars | 0.0284 (230) | -0.0378 (230) | -0.0462 (225) | -0.0229 (228) | -0.0038 (229) | -0.0601 (229) |
| stage10_9.ema20_vwap_cross_count_6_bars | -0.0337 (279) | 0.0486 (279) | -0.0548 (272) | -0.0199 (277) | 0.0214 (278) | 0.0440 (278) |
| stage10_9.ema20_vwap_cross_count_12_bars | 0.0034 (236) | 0.0380 (236) | 0.0095 (231) | -0.0378 (234) | -0.0133 (235) | -0.0754 (235) |
| stage10_9.ema20_vwap_cross_count_24_bars | -0.0015 (157) | 0.0427 (157) | -0.0365 (153) | -0.0998 (156) | -0.0391 (156) | -0.0504 (156) |
| stage10_9.price_vwap_side_change_count_6_bars | 0.0579 (535) | 0.1265 (535) | -0.0194 (516) | -0.0130 (530) | -0.0207 (531) | -0.0289 (533) |
| stage10_9.price_vwap_side_change_count_12_bars | 0.1039 (423) | 0.1081 (423) | 0.0070 (409) | 0.0277 (418) | 0.0249 (419) | 0.0261 (421) |
| stage10_9.price_vwap_side_change_count_24_bars | 0.1156 (287) | 0.0338 (287) | 0.0483 (280) | 0.1402 (285) | 0.1304 (286) | 0.0397 (286) |
| stage10_9.rolling_high_low_range_6_bars | 0.2053 (535) | 0.4902 (535) | 0.0611 (516) | 0.0723 (530) | 0.0387 (531) | 0.0813 (533) |
| stage10_9.rolling_high_low_range_12_bars | 0.2223 (423) | 0.4620 (423) | 0.0516 (409) | 0.0936 (418) | 0.0609 (419) | 0.1089 (421) |
| stage10_9.rolling_high_low_range_24_bars | 0.1589 (287) | 0.4194 (287) | 0.0166 (280) | 0.0183 (285) | 0.0024 (286) | 0.0640 (286) |
| stage10_9.rolling_range_atr14_6_bars | 0.0319 (394) | 0.0544 (394) | 0.0400 (381) | 0.0146 (389) | -0.0051 (390) | 0.0324 (392) |
| stage10_9.rolling_range_atr14_12_bars | -0.0261 (394) | 0.0422 (394) | 0.0088 (381) | 0.0042 (389) | 0.0085 (390) | 0.0215 (392) |
| stage10_9.rolling_range_atr14_24_bars | -0.1270 (287) | 0.0587 (287) | -0.1052 (280) | -0.1532 (285) | -0.1139 (286) | -0.1040 (286) |
| stage10_9.directional_efficiency_6_bars | 0.0534 (535) | -0.0869 (535) | 0.0168 (516) | 0.0144 (530) | 0.0041 (531) | 0.0506 (533) |
| stage10_9.directional_efficiency_12_bars | -0.0270 (423) | -0.0558 (423) | -0.0364 (409) | -0.0011 (418) | 0.0564 (419) | 0.0696 (421) |
| stage10_9.directional_efficiency_24_bars | -0.0374 (287) | 0.0796 (287) | -0.0516 (280) | -0.0735 (285) | -0.0515 (286) | -0.0110 (286) |
| stage10_9.range_overlap_fraction_6_bars | 0.0286 (535) | 0.0298 (535) | 0.0031 (516) | 0.0491 (530) | 0.0527 (531) | 0.0373 (533) |
| stage10_9.range_overlap_fraction_12_bars | -0.0085 (423) | 0.0254 (423) | -0.0234 (409) | 0.0111 (418) | 0.0173 (419) | -0.0110 (421) |
| stage10_9.range_overlap_fraction_24_bars | -0.0777 (287) | 0.0583 (287) | -0.0752 (280) | -0.0029 (285) | -0.0448 (286) | -0.1009 (286) |
| stage10_9.close_direction_alternation_fraction_6_bars | -0.0290 (535) | 0.0641 (535) | -0.0051 (516) | -0.0124 (530) | -0.0053 (531) | -0.0302 (533) |
| stage10_9.close_direction_alternation_fraction_12_bars | 0.0153 (423) | 0.0455 (423) | -0.0387 (409) | -0.0617 (418) | -0.0684 (419) | 0.0057 (421) |
| stage10_9.close_direction_alternation_fraction_24_bars | 0.0260 (287) | -0.0221 (287) | 0.0374 (280) | 0.0097 (285) | -0.0032 (286) | 0.0364 (286) |
| stage10_9.confirmation_close_vwap_distance_atr14 | -0.0631 (394) | 0.0182 (394) | -0.1146 (381) | -0.1067 (389) | -0.0821 (390) | -0.0221 (392) |
| stage10_9.ema9_vwap_distance_atr14 | -0.0822 (394) | -0.0112 (394) | -0.0716 (381) | -0.0796 (389) | -0.0678 (390) | -0.0174 (392) |
| stage10_9.ema20_vwap_distance_atr14 | -0.1076 (322) | -0.0229 (322) | -0.0525 (313) | -0.0650 (320) | -0.0722 (321) | -0.0231 (321) |
| stage11_2.room_from_confirmation | 0.0699 (604) | 0.2036 (604) | -0.0019 (572) | -0.0131 (596) | -0.0358 (599) | -0.0048 (602) |
| stage11_2.room_in_atr | 0.0501 (330) | 0.0713 (330) | 0.0286 (318) | -0.0487 (325) | -0.0584 (326) | -0.0051 (328) |
| stage11_2.number_of_known_levels_above | 0.0763 (727) | 0.0511 (727) | 0.0744 (689) | 0.0880 (719) | 0.0664 (722) | 0.0704 (725) |
| stage11_2.number_of_known_levels_below | -0.0788 (727) | -0.0461 (727) | -0.0760 (689) | -0.0912 (719) | -0.0708 (722) | -0.0737 (725) |
| stage11_2.nearest_level_distance_above | 0.0450 (650) | 0.3317 (650) | -0.0169 (613) | -0.0518 (642) | -0.0642 (645) | -0.0227 (648) |
| stage11_2.nearest_level_distance_below | 0.1861 (681) | 0.2267 (681) | 0.0155 (648) | 0.0536 (673) | 0.0365 (676) | 0.0477 (679) |
| stage11_2.directional_level_count_within_0_5_atr | -0.0173 (394) | -0.0322 (394) | 0.0367 (381) | 0.0326 (389) | 0.0184 (390) | -0.0291 (392) |
| stage11_2.directional_level_count_within_1_0_atr | -0.0223 (394) | -0.0162 (394) | -0.0103 (381) | 0.0386 (389) | 0.0304 (390) | -0.0613 (392) |
| stage11_3.confirmation_close_to_latest_swing_high | 0.1369 (502) | 0.2359 (502) | 0.0258 (484) | 0.0742 (497) | 0.0446 (498) | 0.0902 (500) |
| stage11_3.confirmation_close_to_latest_swing_low | 0.0308 (489) | 0.2888 (489) | -0.0263 (468) | -0.0411 (482) | -0.0354 (484) | 0.0167 (487) |
| stage11_3.distance_to_swing_high_in_atr | 0.0152 (394) | 0.0474 (394) | -0.0269 (381) | -0.0117 (389) | -0.0492 (390) | -0.0084 (392) |
| stage11_3.distance_to_swing_low_in_atr | -0.0682 (388) | 0.0577 (388) | -0.0523 (375) | -0.1041 (383) | -0.0581 (384) | -0.0385 (386) |


### REFERENCE_CLOSE_V1: ALL categorical


| feature | category | n | sessions | pre-reclaim MFE n/mean/median | pre-reclaim MAE n/mean/median | 0.25/0.25 | 0.50/0.25 | 0.50/0.30 | 1.00/0.30 | ambiguous n across four pairs | no future n across four pairs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| direction | LONG | 400 | 137 | 397/1.3074/0.5500 | 397/0.8428/0.6900 | 46.25% | 34.25% | 38.75% | 25.25% | 23/7/4/2 | 3/3/3/3 |
| direction | SHORT | 333 | 129 | 330/1.6164/0.7376 | 330/0.8640/0.6975 | 51.35% | 41.14% | 43.24% | 29.13% | 15/1/1/0 | 3/3/3/3 |
| time_bucket | 09:35-10:00 | 192 | 151 | 192/1.8746/0.6650 | 192/1.0497/0.8650 | 44.27% | 35.42% | 38.54% | 28.12% | 19/3/1/0 | 0/0/0/0 |
| time_bucket | 10:00-10:30 | 112 | 84 | 112/1.4551/0.8074 | 112/1.0536/0.7850 | 48.21% | 35.71% | 38.39% | 25.00% | 5/0/0/0 | 0/0/0/0 |
| time_bucket | 10:30-11:00 | 72 | 54 | 72/1.5485/0.8720 | 72/0.9195/0.7900 | 47.22% | 38.89% | 38.89% | 23.61% | 5/3/3/1 | 0/0/0/0 |
| time_bucket | 11:00-12:00 | 105 | 64 | 105/1.4227/0.5500 | 105/0.7272/0.6400 | 52.38% | 41.90% | 45.71% | 32.38% | 4/0/0/0 | 0/0/0/0 |
| time_bucket | 12:00-13:30 | 118 | 62 | 118/1.1872/0.4900 | 118/0.6863/0.5550 | 48.31% | 37.29% | 42.37% | 29.66% | 2/1/0/0 | 0/0/0/0 |
| time_bucket | 13:30-15:00 | 67 | 49 | 67/1.1639/0.5650 | 67/0.6887/0.5500 | 56.72% | 40.30% | 43.28% | 26.87% | 2/1/1/1 | 0/0/0/0 |
| time_bucket | 15:00-close | 67 | 43 | 61/0.8295/0.4800 | 61/0.4996/0.4000 | 49.25% | 34.33% | 40.30% | 17.91% | 1/0/0/0 | 6/6/6/6 |
| ema9_20_alignment | EMA_ALIGNED | 211 | 75 | 208/1.0950/0.4550 | 208/0.6846/0.5400 | 47.87% | 36.02% | 39.81% | 24.64% | 7/2/1/1 | 3/3/3/3 |
| ema9_20_alignment | EMA_NOT_ALIGNED | 117 | 69 | 114/1.1649/0.5625 | 114/0.6075/0.5425 | 53.85% | 41.03% | 47.01% | 30.77% | 2/0/0/0 | 3/3/3/3 |
| ema9_20_alignment | EMA_UNAVAILABLE | 405 | 169 | 405/1.7084/0.7120 | 405/1.0076/0.8250 | 47.41% | 37.04% | 39.51% | 27.16% | 29/6/4/1 | 0/0/0/0 |
| price_vwap_alignment | VWAP_ALIGNED | 651 | 170 | 648/1.4552/0.6100 | 648/0.8818/0.7200 | 47.31% | 36.25% | 39.48% | 26.57% | 37/8/5/2 | 3/3/3/3 |
| price_vwap_alignment | VWAP_NOT_ALIGNED | 82 | 46 | 79/1.3854/0.7100 | 79/0.6116/0.5350 | 58.54% | 46.34% | 51.22% | 30.49% | 1/0/0/0 | 3/3/3/3 |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED | 349 | 114 | 346/1.2607/0.5550 | 346/0.7570/0.6500 | 49.00% | 36.68% | 40.40% | 27.51% | 12/4/3/1 | 3/3/3/3 |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED | 136 | 77 | 133/1.4611/0.6200 | 133/0.6702/0.5600 | 55.88% | 43.38% | 47.06% | 25.00% | 5/1/1/1 | 3/3/3/3 |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE | 248 | 164 | 248/1.7014/0.6575 | 248/1.0833/0.8588 | 43.95% | 35.08% | 37.90% | 27.42% | 21/3/1/0 | 0/0/0/0 |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED | 218 | 82 | 214/1.1088/0.4725 | 214/0.6891/0.5500 | 49.54% | 37.16% | 42.20% | 27.98% | 7/1/0/0 | 4/4/4/4 |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED | 110 | 70 | 108/1.1414/0.5650 | 108/0.5942/0.4800 | 50.91% | 39.09% | 42.73% | 24.55% | 2/1/1/1 | 2/2/2/2 |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 405 | 169 | 405/1.7084/0.7120 | 405/1.0076/0.8250 | 47.41% | 37.04% | 39.51% | 27.16% | 29/6/4/1 | 0/0/0/0 |
| prior_ema_cross | MATCHING_CROSS | 129 | 57 | 126/1.0953/0.5225 | 126/0.6648/0.4750 | 49.61% | 38.76% | 44.19% | 24.81% | 5/2/1/1 | 3/3/3/3 |
| prior_ema_cross | NO_PRIOR_CROSS | 505 | 170 | 505/1.6148/0.6700 | 505/0.9478/0.7800 | 47.13% | 36.44% | 39.01% | 27.52% | 32/6/4/1 | 0/0/0/0 |
| prior_ema_cross | OPPOSING_CROSS | 99 | 58 | 96/1.0312/0.5300 | 96/0.5969/0.4976 | 54.55% | 40.40% | 45.45% | 27.27% | 1/0/0/0 | 3/3/3/3 |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 491 | 124 | 487/1.4180/0.6349 | 487/0.7847/0.6500 | 50.71% | 39.31% | 42.77% | 27.49% | 25/7/5/2 | 4/4/4/4 |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL | 233 | 123 | 231/1.4938/0.5600 | 231/0.9936/0.7800 | 44.21% | 33.05% | 36.48% | 25.75% | 13/1/0/0 | 2/2/2/2 |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 9 | 9 | 9/1.8682/1.4525 | 9/0.8956/0.6500 | 44.44% | 44.44% | 44.44% | 33.33% | 0/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 | 56 | 36 | 56/1.2536/0.6000 | 56/0.7877/0.5850 | 46.43% | 41.07% | 44.64% | 25.00% | 2/1/1/0 | 0/0/0/0 |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 | 40 | 26 | 40/1.3637/0.6125 | 40/0.7080/0.6925 | 52.50% | 40.00% | 45.00% | 32.50% | 1/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 | 38 | 29 | 35/1.0722/0.5500 | 35/0.6808/0.5500 | 50.00% | 39.47% | 44.74% | 26.32% | 1/2/1/1 | 3/3/3/3 |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 | 51 | 35 | 51/1.6170/0.9200 | 51/0.7032/0.6800 | 49.02% | 43.14% | 50.98% | 41.18% | 2/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | GT_3_0_ATR | 75 | 33 | 74/1.2525/0.4675 | 74/0.7068/0.5700 | 50.67% | 33.33% | 34.67% | 22.67% | 1/1/1/1 | 1/1/1/1 |
| stage11_2.room_bucket | LT_0_5_ATR | 75 | 41 | 74/1.1888/0.5375 | 74/0.6359/0.4875 | 50.67% | 40.00% | 42.67% | 24.00% | 5/1/1/0 | 1/1/1/1 |
| stage11_2.room_bucket | OPEN_ENDED | 124 | 43 | 123/1.1712/0.4650 | 123/0.7995/0.5800 | 52.42% | 33.87% | 37.10% | 24.19% | 6/0/0/0 | 1/1/1/1 |
| stage11_2.room_bucket | UNAVAILABLE_ATR | 274 | 151 | 274/1.7628/0.7110 | 274/1.0580/0.8600 | 45.26% | 36.86% | 39.78% | 27.37% | 20/3/1/0 | 0/0/0/0 |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 731 | 169 | 725/1.4445/0.6100 | 725/0.8538/0.6900 | 48.43% | 37.21% | 40.63% | 26.95% | 38/8/5/2 | 6/6/6/6 |
| known_level_coverage | PARTIAL_UNAVAILABLE [SMALL] | 2 | 1 | 2/2.6000/2.6000 | 2/0.3700/0.3700 | 100.00% | 100.00% | 100.00% | 50.00% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.structure | BEARISH_STRUCTURE | 101 | 62 | 101/1.1797/0.4800 | 101/0.6632/0.5500 | 55.45% | 38.61% | 40.59% | 25.74% | 2/1/1/1 | 0/0/0/0 |
| stage11_3.structure | BULLISH_STRUCTURE | 102 | 63 | 102/1.1940/0.6500 | 102/0.6565/0.5400 | 54.90% | 46.08% | 50.00% | 27.45% | 3/2/1/0 | 0/0/0/0 |
| stage11_3.structure | MIXED_STRUCTURE | 152 | 73 | 146/1.1217/0.4604 | 146/0.6682/0.5600 | 46.05% | 34.87% | 40.79% | 28.29% | 4/0/0/0 | 6/6/6/6 |
| stage11_3.structure | UNAVAILABLE | 378 | 169 | 378/1.7136/0.7110 | 378/1.0270/0.8395 | 46.03% | 35.71% | 38.36% | 26.72% | 29/5/3/1 | 0/0/0/0 |
| stage11_3.agreement | STRUCTURE_ALIGNED | 116 | 70 | 116/1.2231/0.7250 | 116/0.6396/0.5425 | 55.17% | 45.69% | 50.00% | 33.62% | 4/2/1/0 | 0/0/0/0 |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED | 239 | 93 | 233/1.1280/0.4850 | 233/0.6752/0.5600 | 49.37% | 35.98% | 40.17% | 24.27% | 5/1/1/1 | 6/6/6/6 |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 378 | 169 | 378/1.7136/0.7110 | 378/1.0270/0.8395 | 46.03% | 35.71% | 38.36% | 26.72% | 29/5/3/1 | 0/0/0/0 |
| stage11_3.high_structure | EQUAL_HIGH [SMALL] | 4 | 3 | 4/0.8527/0.8054 | 4/1.0060/0.7621 | 75.00% | 75.00% | 75.00% | 0.00% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.high_structure | HIGHER_HIGH | 175 | 83 | 173/1.1450/0.5700 | 173/0.6728/0.5497 | 53.14% | 42.29% | 46.29% | 26.86% | 6/4/3/1 | 2/2/2/2 |
| stage11_3.high_structure | LOWER_HIGH | 214 | 88 | 210/1.2473/0.4750 | 210/0.6863/0.5575 | 47.66% | 34.11% | 38.32% | 27.10% | 6/1/1/1 | 4/4/4/4 |
| stage11_3.high_structure | UNAVAILABLE | 340 | 168 | 340/1.7324/0.7025 | 340/1.0446/0.8538 | 46.47% | 36.47% | 39.12% | 27.35% | 26/3/1/0 | 0/0/0/0 |
| stage11_3.low_structure | EQUAL_LOW [SMALL] | 3 | 2 | 3/0.7267/0.4700 | 3/0.5331/0.4300 | 33.33% | 33.33% | 33.33% | 33.33% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.low_structure | HIGHER_LOW | 214 | 94 | 210/1.2093/0.5425 | 210/0.7083/0.5860 | 49.53% | 39.25% | 43.93% | 27.57% | 5/2/1/0 | 4/4/4/4 |
| stage11_3.low_structure | LOWER_LOW | 160 | 77 | 158/1.1285/0.5105 | 158/0.6417/0.5400 | 55.00% | 40.00% | 43.12% | 26.88% | 4/1/1/1 | 2/2/2/2 |
| stage11_3.low_structure | UNAVAILABLE | 356 | 169 | 356/1.7360/0.7110 | 356/1.0337/0.8395 | 45.22% | 35.11% | 37.92% | 26.69% | 29/5/3/1 | 0/0/0/0 |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE | 234 | 158 | 234/1.8272/0.6900 | 234/1.0978/0.8588 | 45.30% | 36.75% | 39.74% | 29.06% | 19/2/0/0 | 0/0/0/0 |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED | 86 | 33 | 85/1.0677/0.4000 | 85/0.6954/0.5100 | 53.49% | 33.72% | 38.37% | 24.42% | 3/0/0/0 | 1/1/1/1 |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL | 99 | 50 | 97/1.3326/0.6900 | 97/0.6787/0.6000 | 51.52% | 40.40% | 42.42% | 24.24% | 4/2/2/0 | 2/2/2/2 |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL | 314 | 108 | 311/1.3019/0.5701 | 311/0.7649/0.6500 | 48.73% | 37.90% | 41.72% | 27.07% | 12/4/3/2 | 3/3/3/3 |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 733 | 170 | 727/1.4477/0.6200 | 727/0.8524/0.6900 | 48.57% | 37.38% | 40.79% | 27.01% | 38/8/5/2 | 6/6/6/6 |


### REFERENCE_CLOSE_V1: LONG evaluation labels

Labels are retrospective evaluations, never predictors. Never-strong includes session-close censoring; longer pre-reclaim exposure in eventual-strong sequences is not a causal benefit.

| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EVENTUAL_STRONG | 283 | 132 | 283/0 | 283 | 1.9550 | 2.5819 | 1.7677 | 2.4567 | 1.0510 | 0.0800 | 73.14% |
| NEVER_STRONG | 117 | 71 | 117/0 | 114 | 1.5975 | 2.3799 | 2.5270 | 3.1077 | 0.7658 | -0.5470 | 97.44% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| EVENTUAL_STRONG | 283 | 59.01% | 45.94% | 36.04% | 30.74% | 50.53% | 40.28% | 34.63% | 24.38% | 18.37% |
| NEVER_STRONG | 117 | 15.38% | 5.98% | 2.56% | 1.71% | 10.26% | 3.42% | 2.56% | 1.71% | 1.71% |


### REFERENCE_CLOSE_V1: LONG continuous


| feature | pre_reclaim_mfe: r (n) | pre_reclaim_mae: r (n) | 0.25/0.25: r (n) | 0.50/0.25: r (n) | 0.50/0.30: r (n) | 1.00/0.30: r (n) |
|---|---|---|---|---|---|---|
| opening_range_width | 0.0790 (397) | 0.2086 (397) | -0.0343 (374) | -0.0085 (390) | -0.0059 (393) | 0.0480 (395) |
| body_size | 0.2555 (397) | 0.4442 (397) | 0.0325 (374) | 0.0155 (390) | 0.0036 (393) | 0.0205 (395) |
| directional_body | 0.2555 (397) | 0.4442 (397) | 0.0325 (374) | 0.0155 (390) | 0.0036 (393) | 0.0205 (395) |
| candle_range | 0.2615 (397) | 0.4930 (397) | 0.0533 (374) | 0.0584 (390) | 0.0329 (393) | 0.0401 (395) |
| body_range_ratio | 0.1333 (397) | 0.1217 (397) | 0.0014 (374) | -0.0327 (390) | -0.0122 (393) | 0.0157 (395) |
| directional_body_range_ratio | 0.1333 (397) | 0.1217 (397) | 0.0014 (374) | -0.0327 (390) | -0.0122 (393) | 0.0157 (395) |
| close_location | 0.0281 (397) | 0.1430 (397) | -0.0438 (374) | -0.0794 (390) | -0.0565 (393) | -0.0107 (395) |
| directional_close_location | 0.0281 (397) | 0.1430 (397) | -0.0438 (374) | -0.0794 (390) | -0.0565 (393) | -0.0107 (395) |
| distance_beyond_level | 0.2780 (397) | 0.4259 (397) | 0.0462 (374) | 0.0053 (390) | -0.0147 (393) | 0.0144 (395) |
| distance_beyond_level_atr14 | 0.1790 (212) | 0.2990 (212) | 0.0581 (204) | 0.0190 (207) | 0.0094 (208) | -0.0174 (210) |
| candle_volume | 0.2607 (397) | 0.2570 (397) | 0.1165 (374) | 0.1047 (390) | 0.0763 (393) | 0.1109 (395) |
| relative_volume_prior_6 | 0.1909 (277) | -0.0528 (277) | 0.1563 (267) | 0.1680 (272) | 0.1607 (273) | 0.1982 (275) |
| atr14 | 0.2593 (212) | 0.4880 (212) | 0.0638 (204) | 0.1184 (207) | 0.0524 (208) | 0.0375 (210) |
| minutes_since_open | -0.1087 (397) | -0.2839 (397) | 0.0655 (374) | 0.0297 (390) | 0.0700 (393) | 0.0140 (395) |
| minutes_since_ema_cross | -0.0387 (103) | -0.0079 (103) | -0.0025 (100) | 0.0100 (101) | -0.0138 (102) | 0.0231 (102) |
| break_attempt_rank | -0.0728 (397) | -0.2488 (397) | 0.0983 (374) | 0.0453 (390) | 0.0672 (393) | -0.0090 (395) |
| valid_hold_sequence_rank | -0.1098 (397) | -0.2231 (397) | 0.0280 (374) | -0.0038 (390) | 0.0191 (393) | -0.0235 (395) |
| stage10_9.ema9_ema20_absolute_separation | 0.0679 (169) | 0.1856 (169) | 0.0236 (164) | 0.0894 (167) | 0.0973 (168) | 0.1101 (168) |
| stage10_9.ema9_ema20_separation_atr14 | 0.0115 (169) | 0.0126 (169) | -0.0151 (164) | 0.0188 (167) | 0.0787 (168) | 0.0747 (168) |
| stage10_9.ema9_slope_1_bars | 0.2226 (254) | 0.2289 (254) | 0.0595 (244) | 0.0474 (249) | 0.0330 (250) | 0.0768 (252) |
| stage10_9.ema9_slope_2_bars | 0.1121 (242) | 0.0309 (242) | 0.0200 (233) | -0.0033 (237) | -0.0028 (238) | 0.0581 (240) |
| stage10_9.ema9_slope_3_bars | 0.0658 (231) | 0.0170 (231) | -0.0176 (223) | -0.0488 (226) | -0.0427 (227) | 0.0399 (229) |
| stage10_9.ema20_slope_1_bars | 0.1144 (163) | 0.0804 (163) | -0.0084 (158) | 0.0209 (161) | 0.0362 (162) | 0.0452 (162) |
| stage10_9.ema20_slope_2_bars | 0.0543 (158) | -0.0461 (158) | -0.0145 (154) | 0.0136 (156) | 0.0435 (157) | 0.0542 (157) |
| stage10_9.ema20_slope_3_bars | -0.0102 (154) | -0.0005 (154) | -0.0777 (150) | -0.0419 (152) | -0.0029 (153) | -0.0023 (153) |
| stage10_9.vwap_slope_1_bars | 0.1562 (397) | 0.2541 (397) | -0.0574 (374) | -0.0414 (390) | -0.0523 (393) | -0.0112 (395) |
| stage10_9.vwap_slope_2_bars | 0.1100 (352) | 0.1673 (352) | 0.0223 (334) | 0.0342 (345) | 0.0195 (348) | 0.0465 (350) |
| stage10_9.vwap_slope_3_bars | 0.0689 (332) | 0.1652 (332) | -0.0482 (316) | -0.0141 (326) | -0.0482 (328) | 0.0332 (330) |
| stage10_9.ema9_ema20_cross_count_6_bars | 0.1203 (147) | -0.0632 (147) | 0.0507 (143) | 0.0640 (145) | 0.0883 (146) | 0.1176 (146) |
| stage10_9.ema9_ema20_cross_count_12_bars | 0.1512 (122) | -0.0834 (122) | -0.0255 (120) | 0.0429 (120) | 0.0531 (121) | 0.0578 (121) |
| stage10_9.ema9_ema20_cross_count_24_bars | 0.0537 (79) | 0.1778 (79) | -0.0182 (78) | -0.0449 (78) | -0.0823 (78) | -0.0851 (78) |
| stage10_9.ema9_vwap_cross_count_6_bars | -0.0575 (212) | 0.0237 (212) | -0.0289 (204) | -0.0649 (207) | -0.0149 (208) | -0.0206 (210) |
| stage10_9.ema9_vwap_cross_count_12_bars | 0.1132 (169) | -0.1172 (169) | 0.0640 (164) | 0.0663 (167) | 0.1411 (168) | 0.1066 (168) |
| stage10_9.ema9_vwap_cross_count_24_bars | -0.0075 (117) | -0.1051 (117) | -0.0361 (115) | -0.0373 (115) | 0.0299 (116) | -0.0588 (116) |
| stage10_9.ema20_vwap_cross_count_6_bars | -0.0928 (147) | -0.0175 (147) | -0.0378 (143) | 0.0179 (145) | 0.0778 (146) | 0.0730 (146) |
| stage10_9.ema20_vwap_cross_count_12_bars | -0.0159 (122) | -0.0125 (122) | 0.0685 (120) | -0.0127 (120) | 0.0321 (121) | -0.0888 (121) |
| stage10_9.ema20_vwap_cross_count_24_bars | -0.0313 (79) | 0.0258 (79) | -0.0726 (78) | -0.1743 (78) | -0.0575 (78) | -0.1680 (78) |
| stage10_9.price_vwap_side_change_count_6_bars | -0.0170 (291) | 0.1743 (291) | -0.0715 (280) | -0.0555 (286) | -0.0697 (287) | -0.0942 (289) |
| stage10_9.price_vwap_side_change_count_12_bars | 0.0416 (231) | 0.1314 (231) | -0.0261 (223) | -0.0359 (226) | -0.0488 (227) | -0.0240 (229) |
| stage10_9.price_vwap_side_change_count_24_bars | 0.0630 (151) | 0.0710 (151) | 0.0470 (147) | 0.1409 (149) | 0.1196 (150) | 0.0492 (150) |
| stage10_9.rolling_high_low_range_6_bars | 0.1692 (291) | 0.4686 (291) | 0.0813 (280) | 0.0691 (286) | 0.0141 (287) | 0.0144 (289) |
| stage10_9.rolling_high_low_range_12_bars | 0.2211 (231) | 0.4477 (231) | 0.0728 (223) | 0.1194 (226) | 0.0665 (227) | 0.0757 (229) |
| stage10_9.rolling_high_low_range_24_bars | 0.1535 (151) | 0.4355 (151) | -0.0082 (147) | 0.0219 (149) | 0.0067 (150) | 0.0431 (150) |
| stage10_9.rolling_range_atr14_6_bars | 0.0362 (212) | 0.0409 (212) | 0.0750 (204) | -0.0134 (207) | -0.0602 (208) | -0.0293 (210) |
| stage10_9.rolling_range_atr14_12_bars | 0.0052 (212) | -0.0324 (212) | 0.0545 (204) | 0.0045 (207) | 0.0207 (208) | 0.0008 (210) |
| stage10_9.rolling_range_atr14_24_bars | -0.1434 (151) | 0.0540 (151) | -0.1436 (147) | -0.1937 (149) | -0.1011 (150) | -0.1006 (150) |
| stage10_9.directional_efficiency_6_bars | 0.0877 (291) | -0.1287 (291) | 0.0887 (280) | 0.0295 (286) | 0.0277 (287) | 0.0723 (289) |
| stage10_9.directional_efficiency_12_bars | 0.0045 (231) | -0.1569 (231) | -0.0077 (223) | 0.0226 (226) | 0.1337 (227) | 0.1208 (229) |
| stage10_9.directional_efficiency_24_bars | 0.0087 (151) | 0.0492 (151) | -0.0313 (147) | -0.0349 (149) | 0.0166 (150) | 0.0421 (150) |
| stage10_9.range_overlap_fraction_6_bars | N/A (291) | N/A (291) | N/A (280) | N/A (286) | N/A (287) | N/A (289) |
| stage10_9.range_overlap_fraction_12_bars | N/A (231) | N/A (231) | N/A (223) | N/A (226) | N/A (227) | N/A (229) |
| stage10_9.range_overlap_fraction_24_bars | -0.1464 (151) | 0.1030 (151) | -0.1182 (147) | -0.0370 (149) | -0.1385 (150) | -0.1996 (150) |
| stage10_9.close_direction_alternation_fraction_6_bars | -0.0241 (291) | 0.0942 (291) | -0.0147 (280) | -0.0018 (286) | -0.0058 (287) | -0.0003 (289) |
| stage10_9.close_direction_alternation_fraction_12_bars | -0.0244 (231) | 0.0168 (231) | -0.0169 (223) | -0.0529 (226) | -0.0804 (227) | -0.0351 (229) |
| stage10_9.close_direction_alternation_fraction_24_bars | 0.0149 (151) | -0.0045 (151) | 0.0469 (147) | -0.0079 (149) | -0.0200 (150) | 0.0310 (150) |
| stage10_9.confirmation_close_vwap_distance_atr14 | 0.0321 (212) | -0.0399 (212) | -0.1145 (204) | -0.0777 (207) | -0.0292 (208) | 0.0223 (210) |
| stage10_9.ema9_vwap_distance_atr14 | -0.0368 (212) | -0.0186 (212) | -0.1031 (204) | -0.0674 (207) | -0.0375 (208) | 0.0126 (210) |
| stage10_9.ema20_vwap_distance_atr14 | -0.0500 (169) | 0.0384 (169) | -0.0786 (164) | -0.0442 (167) | -0.0544 (168) | -0.0188 (168) |
| stage11_2.room_from_confirmation | 0.0229 (320) | 0.2282 (320) | -0.0027 (298) | -0.0699 (313) | -0.1071 (316) | -0.0586 (318) |
| stage11_2.room_in_atr | 0.0019 (177) | 0.1452 (177) | 0.0114 (169) | -0.1377 (172) | -0.1645 (173) | -0.1055 (175) |
| stage11_2.number_of_known_levels_above | 0.0150 (397) | 0.1357 (397) | 0.0299 (374) | 0.0742 (390) | 0.0659 (393) | 0.0597 (395) |
| stage11_2.number_of_known_levels_below | -0.0156 (397) | -0.1283 (397) | -0.0272 (374) | -0.0755 (390) | -0.0714 (393) | -0.0580 (395) |
| stage11_2.nearest_level_distance_above | 0.0229 (320) | 0.2282 (320) | -0.0027 (298) | -0.0699 (313) | -0.1071 (316) | -0.0586 (318) |
| stage11_2.nearest_level_distance_below | 0.2490 (397) | 0.4140 (397) | 0.0296 (374) | -0.0119 (390) | -0.0239 (393) | -0.0077 (395) |
| stage11_2.directional_level_count_within_0_5_atr | 0.0277 (212) | -0.0653 (212) | 0.0471 (204) | 0.0567 (207) | 0.0231 (208) | 0.0372 (210) |
| stage11_2.directional_level_count_within_1_0_atr | 0.0164 (212) | -0.0182 (212) | 0.0130 (204) | 0.0646 (207) | 0.0401 (208) | -0.0287 (210) |
| stage11_3.confirmation_close_to_latest_swing_high | 0.0045 (271) | 0.2096 (271) | 0.0662 (261) | 0.0341 (266) | 0.0008 (267) | 0.0008 (269) |
| stage11_3.confirmation_close_to_latest_swing_low | 0.1285 (267) | 0.3779 (267) | -0.0396 (255) | -0.0371 (261) | -0.0655 (263) | -0.0152 (265) |
| stage11_3.distance_to_swing_high_in_atr | -0.0582 (212) | 0.0556 (212) | 0.0641 (204) | -0.0156 (207) | -0.0497 (208) | -0.0344 (210) |
| stage11_3.distance_to_swing_low_in_atr | 0.0174 (210) | 0.0672 (210) | -0.0935 (202) | -0.1182 (205) | -0.0994 (206) | -0.0985 (208) |


### REFERENCE_CLOSE_V1: LONG categorical


| feature | category | n | sessions | pre-reclaim MFE n/mean/median | pre-reclaim MAE n/mean/median | 0.25/0.25 | 0.50/0.25 | 0.50/0.30 | 1.00/0.30 | ambiguous n across four pairs | no future n across four pairs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| direction | LONG | 400 | 137 | 397/1.3074/0.5500 | 397/0.8428/0.6900 | 46.25% | 34.25% | 38.75% | 25.25% | 23/7/4/2 | 3/3/3/3 |
| time_bucket | 09:35-10:00 | 106 | 92 | 106/1.6807/0.6250 | 106/1.0140/0.8588 | 41.51% | 33.96% | 37.74% | 26.42% | 12/2/0/0 | 0/0/0/0 |
| time_bucket | 10:00-10:30 | 60 | 49 | 60/1.3138/0.6900 | 60/1.0976/0.7275 | 43.33% | 31.67% | 35.00% | 21.67% | 3/0/0/0 | 0/0/0/0 |
| time_bucket | 10:30-11:00 | 39 | 32 | 39/1.4254/0.7493 | 39/0.9554/0.9200 | 46.15% | 38.46% | 38.46% | 23.08% | 3/3/3/1 | 0/0/0/0 |
| time_bucket | 11:00-12:00 | 67 | 41 | 67/1.3768/0.4850 | 67/0.7056/0.6500 | 52.24% | 37.31% | 41.79% | 29.85% | 3/0/0/0 | 0/0/0/0 |
| time_bucket | 12:00-13:30 | 65 | 35 | 65/0.7919/0.2954 | 65/0.6175/0.5497 | 41.54% | 29.23% | 36.92% | 24.62% | 1/1/0/0 | 0/0/0/0 |
| time_bucket | 13:30-15:00 | 32 | 24 | 32/1.1664/0.3875 | 32/0.6969/0.6375 | 59.38% | 37.50% | 37.50% | 21.88% | 1/1/1/1 | 0/0/0/0 |
| time_bucket | 15:00-close | 31 | 24 | 28/0.9082/0.5325 | 28/0.5102/0.4000 | 51.61% | 35.48% | 48.39% | 25.81% | 0/0/0/0 | 3/3/3/3 |
| ema9_20_alignment | EMA_ALIGNED | 99 | 47 | 98/0.9706/0.3750 | 98/0.6486/0.5598 | 43.43% | 29.29% | 36.36% | 22.22% | 4/2/1/1 | 1/1/1/1 |
| ema9_20_alignment | EMA_NOT_ALIGNED | 73 | 41 | 71/0.9572/0.5100 | 71/0.6351/0.5600 | 53.42% | 38.36% | 45.21% | 30.14% | 1/0/0/0 | 2/2/2/2 |
| ema9_20_alignment | EMA_UNAVAILABLE | 228 | 126 | 228/1.5613/0.6304 | 228/0.9910/0.7996 | 45.18% | 35.09% | 37.72% | 25.00% | 18/5/3/1 | 0/0/0/0 |
| price_vwap_alignment | VWAP_ALIGNED | 351 | 137 | 350/1.3052/0.5375 | 350/0.8729/0.7200 | 44.73% | 33.33% | 37.61% | 24.50% | 23/7/4/2 | 1/1/1/1 |
| price_vwap_alignment | VWAP_NOT_ALIGNED | 49 | 26 | 47/1.3241/0.5900 | 47/0.6186/0.5600 | 57.14% | 40.82% | 46.94% | 30.61% | 0/0/0/0 | 2/2/2/2 |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED | 192 | 82 | 191/1.1127/0.5100 | 191/0.7651/0.6800 | 46.88% | 32.29% | 36.98% | 25.00% | 7/4/3/1 | 1/1/1/1 |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED | 73 | 38 | 71/1.3110/0.5500 | 71/0.6128/0.5500 | 56.16% | 41.10% | 46.58% | 26.03% | 3/1/1/1 | 2/2/2/2 |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE | 135 | 107 | 135/1.5810/0.6200 | 135/1.0738/0.8390 | 40.00% | 33.33% | 37.04% | 25.19% | 13/2/0/0 | 0/0/0/0 |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED | 117 | 52 | 115/0.8760/0.3850 | 115/0.6658/0.5700 | 44.44% | 32.48% | 39.32% | 25.64% | 4/1/0/0 | 2/2/2/2 |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED | 55 | 34 | 54/1.1543/0.5400 | 54/0.5942/0.5150 | 54.55% | 34.55% | 41.82% | 25.45% | 1/1/1/1 | 1/1/1/1 |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 228 | 126 | 228/1.5613/0.6304 | 228/0.9910/0.7996 | 45.18% | 35.09% | 37.72% | 25.00% | 18/5/3/1 | 0/0/0/0 |
| prior_ema_cross | MATCHING_CROSS | 45 | 28 | 44/1.2191/0.6700 | 44/0.5745/0.4650 | 46.67% | 35.56% | 48.89% | 26.67% | 3/2/1/1 | 1/1/1/1 |
| prior_ema_cross | NO_PRIOR_CROSS | 294 | 132 | 294/1.4125/0.5550 | 294/0.9271/0.7500 | 44.22% | 32.99% | 36.05% | 24.49% | 20/5/3/1 | 0/0/0/0 |
| prior_ema_cross | OPPOSING_CROSS | 61 | 34 | 59/0.8496/0.5100 | 59/0.6230/0.5500 | 55.74% | 39.34% | 44.26% | 27.87% | 0/0/0/0 | 2/2/2/2 |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 267 | 91 | 265/1.2243/0.5350 | 265/0.7519/0.6500 | 49.06% | 35.96% | 40.82% | 25.47% | 15/6/4/2 | 2/2/2/2 |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL | 125 | 67 | 124/1.4338/0.5400 | 124/1.0331/0.7996 | 40.00% | 29.60% | 33.60% | 24.00% | 8/1/0/0 | 1/1/1/1 |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 8 | 8 | 8/2.1017/1.7038 | 8/0.9044/0.6250 | 50.00% | 50.00% | 50.00% | 37.50% | 0/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 | 30 | 19 | 30/1.1937/0.5600 | 30/0.6857/0.6200 | 46.67% | 36.67% | 43.33% | 20.00% | 1/1/1/0 | 0/0/0/0 |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 24 | 15 | 24/1.0718/0.6446 | 24/0.7874/0.7500 | 50.00% | 37.50% | 45.83% | 33.33% | 0/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 17 | 13 | 16/1.0511/0.7500 | 16/0.6989/0.4175 | 64.71% | 58.82% | 70.59% | 35.29% | 1/2/1/1 | 1/1/1/1 |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 24 | 16 | 24/0.9705/0.6600 | 24/0.7905/0.7475 | 37.50% | 33.33% | 41.67% | 33.33% | 1/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | GT_3_0_ATR | 41 | 21 | 41/1.2051/0.3900 | 41/0.7579/0.5700 | 53.66% | 26.83% | 26.83% | 17.07% | 1/1/1/1 | 0/0/0/0 |
| stage11_2.room_bucket | LT_0_5_ATR | 43 | 24 | 42/1.3413/0.4675 | 42/0.6291/0.4600 | 51.16% | 39.53% | 41.86% | 27.91% | 4/1/1/0 | 1/1/1/1 |
| stage11_2.room_bucket | OPEN_ENDED | 78 | 28 | 77/1.1693/0.3200 | 77/0.7131/0.5700 | 47.44% | 28.21% | 32.05% | 21.79% | 1/0/0/0 | 1/1/1/1 |
| stage11_2.room_bucket | UNAVAILABLE_ATR | 143 | 94 | 143/1.5498/0.6600 | 143/1.0669/0.8577 | 40.56% | 34.27% | 38.46% | 25.87% | 14/2/0/0 | 0/0/0/0 |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 399 | 136 | 396/1.3090/0.5450 | 396/0.8437/0.6900 | 46.12% | 34.09% | 38.60% | 25.31% | 23/7/4/2 | 3/3/3/3 |
| known_level_coverage | PARTIAL_UNAVAILABLE [SMALL] | 1 | 1 | 1/0.6700/0.6700 | 1/0.5000/0.5000 | 100.00% | 100.00% | 100.00% | 0.00% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.structure | BEARISH_STRUCTURE | 46 | 32 | 46/1.0678/0.3950 | 46/0.6782/0.5750 | 54.35% | 30.43% | 32.61% | 15.22% | 1/1/1/1 | 0/0/0/0 |
| stage11_3.structure | BULLISH_STRUCTURE | 61 | 41 | 61/1.1779/0.6900 | 61/0.6297/0.5497 | 54.10% | 45.90% | 52.46% | 32.79% | 3/2/1/0 | 0/0/0/0 |
| stage11_3.structure | MIXED_STRUCTURE | 84 | 47 | 81/0.8289/0.3600 | 81/0.6390/0.5700 | 40.48% | 27.38% | 34.52% | 23.81% | 2/0/0/0 | 3/3/3/3 |
| stage11_3.structure | UNAVAILABLE | 209 | 122 | 209/1.5834/0.6550 | 209/1.0203/0.8250 | 44.50% | 34.45% | 37.80% | 25.84% | 17/4/2/1 | 0/0/0/0 |
| stage11_3.agreement | STRUCTURE_ALIGNED | 61 | 41 | 61/1.1779/0.6900 | 61/0.6297/0.5497 | 54.10% | 45.90% | 52.46% | 32.79% | 3/2/1/0 | 0/0/0/0 |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED | 130 | 56 | 127/0.9154/0.3600 | 127/0.6532/0.5700 | 45.38% | 28.46% | 33.85% | 20.77% | 3/1/1/1 | 3/3/3/3 |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 209 | 122 | 209/1.5834/0.6550 | 209/1.0203/0.8250 | 44.50% | 34.45% | 37.80% | 25.84% | 17/4/2/1 | 0/0/0/0 |
| stage11_3.high_structure | EQUAL_HIGH [SMALL] | 1 | 1 | 1/0.8908/0.8908 | 1/0.8042/0.8042 | 100.00% | 100.00% | 100.00% | 0.00% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.high_structure | HIGHER_HIGH | 104 | 56 | 103/1.0066/0.5250 | 103/0.6501/0.5600 | 50.00% | 38.46% | 44.23% | 26.92% | 5/4/3/1 | 1/1/1/1 |
| stage11_3.high_structure | LOWER_HIGH | 101 | 51 | 99/1.1239/0.3900 | 99/0.6667/0.5700 | 47.52% | 28.71% | 34.65% | 23.76% | 2/1/1/1 | 2/2/2/2 |
| stage11_3.high_structure | UNAVAILABLE | 194 | 120 | 194/1.5629/0.6450 | 194/1.0352/0.8275 | 43.30% | 34.54% | 37.63% | 25.26% | 16/2/0/0 | 0/0/0/0 |
| stage11_3.low_structure | EQUAL_LOW [SMALL] | 1 | 1 | 1/1.7100/1.7100 | 1/0.1094/0.1094 | 100.00% | 100.00% | 100.00% | 100.00% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.low_structure | HIGHER_LOW | 122 | 64 | 120/1.0568/0.5175 | 120/0.6694/0.6075 | 47.54% | 36.07% | 42.62% | 29.51% | 4/2/1/0 | 2/2/2/2 |
| stage11_3.low_structure | LOWER_LOW | 85 | 48 | 84/0.9585/0.3650 | 84/0.6626/0.5600 | 51.76% | 32.94% | 36.47% | 18.82% | 2/1/1/1 | 1/1/1/1 |
| stage11_3.low_structure | UNAVAILABLE | 192 | 115 | 192/1.6147/0.6575 | 192/1.0339/0.8300 | 42.71% | 33.33% | 36.98% | 25.00% | 17/4/2/1 | 0/0/0/0 |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE | 126 | 108 | 126/1.6760/0.6650 | 126/1.0974/0.8395 | 43.65% | 37.30% | 41.27% | 29.37% | 13/2/0/0 | 0/0/0/0 |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED | 49 | 18 | 48/0.9373/0.3200 | 48/0.5582/0.4900 | 46.94% | 26.53% | 32.65% | 20.41% | 0/0/0/0 | 1/1/1/1 |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL | 57 | 31 | 56/1.2797/0.5500 | 56/0.6809/0.6400 | 50.88% | 38.60% | 40.35% | 24.56% | 2/1/1/0 | 1/1/1/1 |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL | 168 | 72 | 167/1.1450/0.4850 | 167/0.7869/0.7200 | 46.43% | 32.74% | 38.10% | 23.81% | 8/4/3/2 | 1/1/1/1 |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 400 | 137 | 397/1.3074/0.5500 | 397/0.8428/0.6900 | 46.25% | 34.25% | 38.75% | 25.25% | 23/7/4/2 | 3/3/3/3 |


### REFERENCE_CLOSE_V1: SHORT evaluation labels

Labels are retrospective evaluations, never predictors. Never-strong includes session-close censoring; longer pre-reclaim exposure in eventual-strong sequences is not a causal benefit.

| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EVENTUAL_STRONG | 241 | 114 | 0/241 | 241 | 2.4700 | 3.0708 | 1.2720 | 2.1291 | 1.4423 | 0.4300 | 72.61% |
| NEVER_STRONG | 92 | 69 | 0/92 | 89 | 0.8000 | 1.9935 | 2.2706 | 3.1165 | 0.6397 | -0.7900 | 96.74% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| EVENTUAL_STRONG | 241 | 63.49% | 55.19% | 44.40% | 37.76% | 58.09% | 46.89% | 40.25% | 29.88% | 24.48% |
| NEVER_STRONG | 92 | 19.57% | 4.35% | 3.26% | 0.00% | 4.35% | 3.26% | 0.00% | 0.00% | 0.00% |


### REFERENCE_CLOSE_V1: SHORT continuous


| feature | pre_reclaim_mfe: r (n) | pre_reclaim_mae: r (n) | 0.25/0.25: r (n) | 0.50/0.25: r (n) | 0.50/0.30: r (n) | 1.00/0.30: r (n) |
|---|---|---|---|---|---|---|
| opening_range_width | 0.1563 (330) | 0.2541 (330) | 0.0614 (315) | 0.0602 (329) | 0.0478 (329) | 0.0911 (330) |
| body_size | 0.2162 (330) | 0.5407 (330) | 0.0058 (315) | 0.0449 (329) | 0.0314 (329) | 0.1014 (330) |
| directional_body | 0.2162 (330) | 0.5407 (330) | 0.0057 (315) | 0.0448 (329) | 0.0313 (329) | 0.1012 (330) |
| candle_range | 0.2040 (330) | 0.5928 (330) | 0.0258 (315) | 0.0257 (329) | 0.0137 (329) | 0.1093 (330) |
| body_range_ratio | 0.1194 (330) | 0.2095 (330) | -0.0420 (315) | 0.0072 (329) | -0.0062 (329) | 0.0203 (330) |
| directional_body_range_ratio | 0.1194 (330) | 0.2095 (330) | -0.0426 (315) | 0.0063 (329) | -0.0071 (329) | 0.0191 (330) |
| close_location | -0.0008 (330) | -0.1954 (330) | 0.1436 (315) | 0.0738 (329) | 0.0852 (329) | 0.0682 (330) |
| directional_close_location | 0.0008 (330) | 0.1954 (330) | -0.1436 (315) | -0.0738 (329) | -0.0852 (329) | -0.0682 (330) |
| distance_beyond_level | 0.2080 (330) | 0.5663 (330) | 0.0624 (315) | 0.0936 (329) | 0.0919 (329) | 0.1667 (330) |
| distance_beyond_level_atr14 | 0.1206 (182) | 0.3543 (182) | -0.0061 (177) | 0.0155 (182) | 0.0329 (182) | 0.1046 (182) |
| candle_volume | 0.0972 (330) | 0.3916 (330) | -0.0174 (315) | 0.0176 (329) | 0.0051 (329) | 0.0539 (330) |
| relative_volume_prior_6 | -0.0305 (232) | 0.0454 (232) | -0.0366 (224) | -0.0677 (232) | -0.0497 (232) | 0.0319 (232) |
| atr14 | 0.3030 (182) | 0.4667 (182) | 0.0300 (177) | 0.0510 (182) | 0.0387 (182) | 0.1567 (182) |
| minutes_since_open | -0.0662 (330) | -0.3322 (330) | 0.0204 (315) | 0.0105 (329) | 0.0153 (329) | -0.0582 (330) |
| minutes_since_ema_cross | -0.0357 (119) | -0.2037 (119) | 0.0581 (116) | -0.0924 (119) | -0.0920 (119) | -0.1190 (119) |
| break_attempt_rank | -0.0126 (330) | -0.2883 (330) | 0.0553 (315) | 0.0670 (329) | 0.0691 (329) | -0.0231 (330) |
| valid_hold_sequence_rank | -0.0326 (330) | -0.2819 (330) | 0.0218 (315) | 0.0343 (329) | 0.0358 (329) | -0.0482 (330) |
| stage10_9.ema9_ema20_absolute_separation | 0.0413 (153) | 0.2783 (153) | -0.0252 (149) | -0.0293 (153) | -0.0367 (153) | 0.0180 (153) |
| stage10_9.ema9_ema20_separation_atr14 | -0.0943 (153) | 0.1294 (153) | -0.1092 (149) | -0.1063 (153) | -0.1018 (153) | -0.0978 (153) |
| stage10_9.ema9_slope_1_bars | -0.0489 (208) | -0.4163 (208) | 0.1126 (201) | 0.0794 (208) | 0.0858 (208) | -0.0006 (208) |
| stage10_9.ema9_slope_2_bars | -0.0189 (200) | -0.2469 (200) | 0.1032 (193) | 0.0850 (200) | 0.0939 (200) | 0.0261 (200) |
| stage10_9.ema9_slope_3_bars | 0.0029 (192) | -0.2068 (192) | 0.0788 (186) | 0.0745 (192) | 0.0821 (192) | 0.0053 (192) |
| stage10_9.ema20_slope_1_bars | -0.0230 (145) | -0.3997 (145) | 0.0751 (141) | 0.0579 (145) | 0.0562 (145) | -0.0605 (145) |
| stage10_9.ema20_slope_2_bars | -0.0340 (142) | -0.2733 (142) | 0.0723 (138) | 0.0769 (142) | 0.0769 (142) | -0.0059 (142) |
| stage10_9.ema20_slope_3_bars | 0.0052 (137) | -0.2804 (137) | 0.0779 (134) | 0.0864 (137) | 0.0960 (137) | 0.0004 (137) |
| stage10_9.vwap_slope_1_bars | -0.0612 (330) | -0.4114 (330) | -0.0326 (315) | -0.0055 (329) | -0.0003 (329) | -0.0795 (330) |
| stage10_9.vwap_slope_2_bars | -0.0175 (297) | -0.3459 (297) | -0.0293 (285) | -0.0329 (296) | -0.0244 (296) | -0.0997 (297) |
| stage10_9.vwap_slope_3_bars | -0.0267 (272) | -0.3250 (272) | -0.0579 (262) | -0.0181 (271) | -0.0141 (271) | -0.1178 (272) |
| stage10_9.ema9_ema20_cross_count_6_bars | -0.0542 (132) | 0.1131 (132) | -0.0062 (129) | 0.0619 (132) | 0.0598 (132) | -0.0051 (132) |
| stage10_9.ema9_ema20_cross_count_12_bars | 0.0080 (114) | 0.1207 (114) | 0.0000 (111) | 0.1227 (114) | 0.0992 (114) | 0.1547 (114) |
| stage10_9.ema9_ema20_cross_count_24_bars | 0.0521 (78) | 0.0418 (78) | 0.0786 (75) | 0.1734 (78) | 0.1565 (78) | 0.1911 (78) |
| stage10_9.ema9_vwap_cross_count_6_bars | 0.0256 (182) | 0.0659 (182) | 0.0079 (177) | 0.0163 (182) | 0.0487 (182) | -0.0966 (182) |
| stage10_9.ema9_vwap_cross_count_12_bars | 0.0376 (153) | 0.0347 (153) | 0.0487 (149) | 0.0912 (153) | 0.0915 (153) | -0.0529 (153) |
| stage10_9.ema9_vwap_cross_count_24_bars | 0.0475 (113) | 0.0374 (113) | -0.0604 (110) | -0.0202 (113) | -0.0400 (113) | -0.0667 (113) |
| stage10_9.ema20_vwap_cross_count_6_bars | 0.0340 (132) | 0.1165 (132) | -0.0728 (129) | -0.0612 (132) | -0.0430 (132) | 0.0119 (132) |
| stage10_9.ema20_vwap_cross_count_12_bars | 0.0290 (114) | 0.0853 (114) | -0.0505 (111) | -0.0589 (114) | -0.0593 (114) | -0.0601 (114) |
| stage10_9.ema20_vwap_cross_count_24_bars | 0.0121 (78) | 0.0539 (78) | -0.0020 (75) | -0.0111 (78) | -0.0309 (78) | 0.1082 (78) |
| stage10_9.price_vwap_side_change_count_6_bars | 0.1396 (244) | 0.0748 (244) | 0.0376 (236) | 0.0273 (244) | 0.0310 (244) | 0.0407 (244) |
| stage10_9.price_vwap_side_change_count_12_bars | 0.1613 (192) | 0.0843 (192) | 0.0422 (186) | 0.0880 (192) | 0.1030 (192) | 0.0783 (192) |
| stage10_9.price_vwap_side_change_count_24_bars | 0.1471 (136) | 0.0137 (136) | 0.0458 (133) | 0.1321 (136) | 0.1387 (136) | 0.0274 (136) |
| stage10_9.rolling_high_low_range_6_bars | 0.2315 (244) | 0.5215 (244) | 0.0343 (236) | 0.0639 (244) | 0.0552 (244) | 0.1409 (244) |
| stage10_9.rolling_high_low_range_12_bars | 0.2286 (192) | 0.4728 (192) | 0.0274 (186) | 0.0627 (192) | 0.0520 (192) | 0.1407 (192) |
| stage10_9.rolling_high_low_range_24_bars | 0.1760 (136) | 0.3904 (136) | 0.0404 (133) | 0.0142 (136) | -0.0020 (136) | 0.0849 (136) |
| stage10_9.rolling_range_atr14_6_bars | -0.0138 (182) | 0.0902 (182) | 0.0029 (177) | 0.0202 (182) | 0.0352 (182) | 0.0784 (182) |
| stage10_9.rolling_range_atr14_12_bars | -0.0840 (182) | 0.1334 (182) | -0.0423 (177) | -0.0149 (182) | -0.0136 (182) | 0.0319 (182) |
| stage10_9.rolling_range_atr14_24_bars | -0.1103 (136) | 0.0604 (136) | -0.0721 (133) | -0.1268 (136) | -0.1323 (136) | -0.1112 (136) |
| stage10_9.directional_efficiency_6_bars | -0.0088 (244) | -0.0382 (244) | -0.0758 (236) | -0.0213 (244) | -0.0346 (244) | 0.0171 (244) |
| stage10_9.directional_efficiency_12_bars | -0.0871 (192) | 0.0666 (192) | -0.0745 (186) | -0.0420 (192) | -0.0308 (192) | 0.0125 (192) |
| stage10_9.directional_efficiency_24_bars | -0.1079 (136) | 0.1324 (136) | -0.0848 (133) | -0.1330 (136) | -0.1289 (136) | -0.0685 (136) |
| stage10_9.range_overlap_fraction_6_bars | 0.0562 (244) | 0.0403 (244) | 0.0095 (236) | 0.0790 (244) | 0.0824 (244) | 0.0582 (244) |
| stage10_9.range_overlap_fraction_12_bars | 0.0034 (192) | 0.0288 (192) | -0.0304 (186) | 0.0265 (192) | 0.0316 (192) | -0.0115 (192) |
| stage10_9.range_overlap_fraction_24_bars | -0.0121 (136) | 0.0179 (136) | -0.0360 (133) | 0.0305 (136) | 0.0370 (136) | -0.0180 (136) |
| stage10_9.close_direction_alternation_fraction_6_bars | -0.0387 (244) | 0.0359 (244) | 0.0035 (236) | -0.0278 (244) | -0.0073 (244) | -0.0647 (244) |
| stage10_9.close_direction_alternation_fraction_12_bars | 0.0575 (192) | 0.0903 (192) | -0.0704 (186) | -0.0811 (192) | -0.0583 (192) | 0.0528 (192) |
| stage10_9.close_direction_alternation_fraction_24_bars | 0.0265 (136) | -0.0347 (136) | 0.0209 (133) | 0.0149 (136) | 0.0080 (136) | 0.0379 (136) |
| stage10_9.confirmation_close_vwap_distance_atr14 | -0.2030 (182) | 0.1003 (182) | -0.1200 (177) | -0.1607 (182) | -0.1585 (182) | -0.0858 (182) |
| stage10_9.ema9_vwap_distance_atr14 | -0.1325 (182) | -0.0037 (182) | -0.0223 (177) | -0.0928 (182) | -0.1125 (182) | -0.0593 (182) |
| stage10_9.ema20_vwap_distance_atr14 | -0.1596 (153) | -0.0843 (153) | -0.0016 (149) | -0.0814 (153) | -0.0955 (153) | -0.0255 (153) |
| stage11_2.room_from_confirmation | 0.1232 (284) | 0.1685 (284) | -0.0023 (274) | 0.0413 (283) | 0.0342 (283) | 0.0467 (284) |
| stage11_2.room_in_atr | 0.1057 (153) | -0.0087 (153) | 0.0498 (149) | 0.0606 (153) | 0.0734 (153) | 0.1173 (153) |
| stage11_2.number_of_known_levels_above | 0.0921 (330) | 0.0735 (330) | 0.1072 (315) | 0.0401 (329) | 0.0408 (329) | 0.0699 (330) |
| stage11_2.number_of_known_levels_below | -0.1037 (330) | -0.0611 (330) | -0.1170 (315) | -0.0522 (329) | -0.0524 (329) | -0.0857 (330) |
| stage11_2.nearest_level_distance_above | 0.1575 (330) | 0.5227 (330) | 0.0454 (315) | 0.0844 (329) | 0.0747 (329) | 0.1733 (330) |
| stage11_2.nearest_level_distance_below | 0.1232 (284) | 0.1685 (284) | -0.0023 (274) | 0.0413 (283) | 0.0342 (283) | 0.0467 (284) |
| stage11_2.directional_level_count_within_0_5_atr | -0.0682 (182) | 0.0054 (182) | 0.0255 (177) | 0.0092 (182) | 0.0143 (182) | -0.0984 (182) |
| stage11_2.directional_level_count_within_1_0_atr | -0.0642 (182) | -0.0164 (182) | -0.0350 (177) | 0.0112 (182) | 0.0196 (182) | -0.0945 (182) |
| stage11_3.confirmation_close_to_latest_swing_high | 0.1957 (231) | 0.4309 (231) | -0.0339 (223) | 0.0343 (231) | 0.0224 (231) | 0.1153 (231) |
| stage11_3.confirmation_close_to_latest_swing_low | 0.0166 (222) | 0.2472 (222) | 0.0337 (213) | 0.0325 (221) | 0.0647 (221) | 0.1160 (222) |
| stage11_3.distance_to_swing_high_in_atr | -0.0470 (182) | 0.1282 (182) | -0.1288 (177) | -0.0874 (182) | -0.1033 (182) | -0.0307 (182) |
| stage11_3.distance_to_swing_low_in_atr | -0.1097 (178) | -0.0023 (178) | 0.0100 (173) | -0.0360 (178) | 0.0231 (178) | 0.0632 (178) |


### REFERENCE_CLOSE_V1: SHORT categorical


| feature | category | n | sessions | pre-reclaim MFE n/mean/median | pre-reclaim MAE n/mean/median | 0.25/0.25 | 0.50/0.25 | 0.50/0.30 | 1.00/0.30 | ambiguous n across four pairs | no future n across four pairs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| direction | SHORT | 333 | 129 | 330/1.6164/0.7376 | 330/0.8640/0.6975 | 51.35% | 41.14% | 43.24% | 29.13% | 15/1/1/0 | 3/3/3/3 |
| time_bucket | 09:35-10:00 | 86 | 74 | 86/2.1136/0.8075 | 86/1.0938/0.9010 | 47.67% | 37.21% | 39.53% | 30.23% | 7/1/1/0 | 0/0/0/0 |
| time_bucket | 10:00-10:30 | 52 | 48 | 52/1.6182/0.8975 | 52/1.0028/0.8200 | 53.85% | 40.38% | 42.31% | 28.85% | 2/0/0/0 | 0/0/0/0 |
| time_bucket | 10:30-11:00 | 33 | 26 | 33/1.6939/0.9050 | 33/0.8770/0.6900 | 48.48% | 39.39% | 39.39% | 24.24% | 2/0/0/0 | 0/0/0/0 |
| time_bucket | 11:00-12:00 | 38 | 28 | 38/1.5036/0.7750 | 38/0.7651/0.5860 | 52.63% | 50.00% | 52.63% | 36.84% | 1/0/0/0 | 0/0/0/0 |
| time_bucket | 12:00-13:30 | 53 | 35 | 53/1.6722/0.6300 | 53/0.7708/0.5650 | 56.60% | 47.17% | 49.06% | 35.85% | 1/0/0/0 | 0/0/0/0 |
| time_bucket | 13:30-15:00 | 35 | 30 | 35/1.1616/0.8838 | 35/0.6812/0.4600 | 54.29% | 42.86% | 48.57% | 31.43% | 1/0/0/0 | 0/0/0/0 |
| time_bucket | 15:00-close | 36 | 26 | 33/0.7628/0.3350 | 33/0.4906/0.3990 | 47.22% | 33.33% | 33.33% | 11.11% | 1/0/0/0 | 3/3/3/3 |
| ema9_20_alignment | EMA_ALIGNED | 112 | 54 | 110/1.2058/0.5300 | 110/0.7167/0.5124 | 51.79% | 41.96% | 42.86% | 26.79% | 3/0/0/0 | 2/2/2/2 |
| ema9_20_alignment | EMA_NOT_ALIGNED | 44 | 28 | 43/1.5077/0.9700 | 43/0.5618/0.4700 | 54.55% | 45.45% | 50.00% | 31.82% | 1/0/0/0 | 1/1/1/1 |
| ema9_20_alignment | EMA_UNAVAILABLE | 177 | 109 | 177/1.8979/0.8670 | 177/1.0289/0.8500 | 50.28% | 39.55% | 41.81% | 29.94% | 11/1/1/0 | 0/0/0/0 |
| price_vwap_alignment | VWAP_ALIGNED | 300 | 129 | 298/1.6315/0.7576 | 298/0.8922/0.7200 | 50.33% | 39.67% | 41.67% | 29.00% | 14/1/1/0 | 2/2/2/2 |
| price_vwap_alignment | VWAP_NOT_ALIGNED | 33 | 20 | 32/1.4755/0.7150 | 32/0.6014/0.4750 | 60.61% | 54.55% | 57.58% | 30.30% | 1/0/0/0 | 1/1/1/1 |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED | 157 | 71 | 155/1.4430/0.7800 | 155/0.7470/0.5650 | 51.59% | 42.04% | 44.59% | 30.57% | 5/0/0/0 | 2/2/2/2 |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED | 63 | 40 | 62/1.6330/0.7000 | 62/0.7359/0.5900 | 55.56% | 46.03% | 47.62% | 23.81% | 2/0/0/0 | 1/1/1/1 |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE | 113 | 87 | 113/1.8451/0.7750 | 113/1.0947/0.8900 | 48.67% | 37.17% | 38.94% | 30.09% | 8/1/1/0 | 0/0/0/0 |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED | 101 | 48 | 99/1.3792/0.5700 | 99/0.7162/0.5001 | 55.45% | 42.57% | 45.54% | 30.69% | 3/0/0/0 | 2/2/2/2 |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED | 55 | 41 | 54/1.1284/0.5850 | 54/0.5942/0.4800 | 47.27% | 43.64% | 43.64% | 23.64% | 1/0/0/0 | 1/1/1/1 |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 177 | 109 | 177/1.8979/0.8670 | 177/1.0289/0.8500 | 50.28% | 39.55% | 41.81% | 29.94% | 11/1/1/0 | 0/0/0/0 |
| prior_ema_cross | MATCHING_CROSS | 84 | 43 | 82/1.0289/0.4450 | 82/0.7132/0.4800 | 51.19% | 40.48% | 41.67% | 23.81% | 2/0/0/0 | 2/2/2/2 |
| prior_ema_cross | NO_PRIOR_CROSS | 211 | 117 | 211/1.8965/0.9050 | 211/0.9767/0.8000 | 51.18% | 41.23% | 43.13% | 31.75% | 12/1/1/0 | 0/0/0/0 |
| prior_ema_cross | OPPOSING_CROSS | 38 | 24 | 37/1.3208/0.5600 | 37/0.5553/0.4700 | 52.63% | 42.11% | 47.37% | 26.32% | 1/0/0/0 | 1/1/1/1 |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 224 | 94 | 222/1.6492/0.8370 | 222/0.8237/0.6546 | 52.68% | 43.30% | 45.09% | 29.91% | 10/1/1/0 | 2/2/2/2 |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL | 108 | 56 | 107/1.5633/0.6400 | 107/0.9479/0.7575 | 49.07% | 37.04% | 39.81% | 27.78% | 5/0/0/0 | 1/1/1/1 |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 1 | 1 | 1/0.0000/0.0000 | 1/0.8250/0.8250 | 0.00% | 0.00% | 0.00% | 0.00% | 0/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 26 | 20 | 26/1.3227/0.7250 | 26/0.9055/0.4526 | 46.15% | 46.15% | 46.15% | 30.77% | 1/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 16 | 12 | 16/1.8016/0.5975 | 16/0.5888/0.5374 | 56.25% | 43.75% | 43.75% | 31.25% | 1/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 21 | 16 | 19/1.0899/0.5400 | 19/0.6655/0.5650 | 38.10% | 23.81% | 23.81% | 19.05% | 0/0/0/0 | 2/2/2/2 |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 27 | 21 | 27/2.1917/1.2980 | 27/0.6257/0.6000 | 59.26% | 51.85% | 59.26% | 48.15% | 1/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | GT_3_0_ATR | 34 | 16 | 33/1.3114/0.5300 | 33/0.6433/0.5550 | 47.06% | 41.18% | 44.12% | 29.41% | 0/0/0/0 | 1/1/1/1 |
| stage11_2.room_bucket | LT_0_5_ATR | 32 | 21 | 32/0.9886/0.6374 | 32/0.6449/0.5275 | 50.00% | 40.62% | 43.75% | 18.75% | 1/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | OPEN_ENDED | 46 | 15 | 46/1.1743/0.7325 | 46/0.9440/0.7326 | 60.87% | 43.48% | 45.65% | 28.26% | 5/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | UNAVAILABLE_ATR | 131 | 95 | 131/1.9952/0.8400 | 131/1.0482/0.8600 | 50.38% | 39.69% | 41.22% | 29.01% | 6/1/1/0 | 0/0/0/0 |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 332 | 128 | 329/1.6075/0.7350 | 329/0.8659/0.7000 | 51.20% | 40.96% | 43.07% | 28.92% | 15/1/1/0 | 3/3/3/3 |
| known_level_coverage | PARTIAL_UNAVAILABLE [SMALL] | 1 | 1 | 1/4.5300/4.5300 | 1/0.2400/0.2400 | 100.00% | 100.00% | 100.00% | 100.00% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.structure | BEARISH_STRUCTURE | 55 | 42 | 55/1.2733/0.8200 | 55/0.6507/0.5200 | 56.36% | 45.45% | 47.27% | 34.55% | 1/0/0/0 | 0/0/0/0 |
| stage11_3.structure | BULLISH_STRUCTURE | 41 | 33 | 41/1.2179/0.5600 | 41/0.6965/0.5100 | 56.10% | 46.34% | 46.34% | 19.51% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.structure | MIXED_STRUCTURE | 68 | 43 | 65/1.4866/0.7100 | 65/0.7046/0.5500 | 52.94% | 44.12% | 48.53% | 33.82% | 2/0/0/0 | 3/3/3/3 |
| stage11_3.structure | UNAVAILABLE | 169 | 110 | 169/1.8746/0.8250 | 169/1.0353/0.8600 | 47.93% | 37.28% | 39.05% | 27.81% | 12/1/1/0 | 0/0/0/0 |
| stage11_3.agreement | STRUCTURE_ALIGNED | 55 | 42 | 55/1.2733/0.8200 | 55/0.6507/0.5200 | 56.36% | 45.45% | 47.27% | 34.55% | 1/0/0/0 | 0/0/0/0 |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED | 109 | 58 | 106/1.3827/0.6600 | 106/0.7015/0.5225 | 54.13% | 44.95% | 47.71% | 28.44% | 2/0/0/0 | 3/3/3/3 |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 169 | 110 | 169/1.8746/0.8250 | 169/1.0353/0.8600 | 47.93% | 37.28% | 39.05% | 27.81% | 12/1/1/0 | 0/0/0/0 |
| stage11_3.high_structure | EQUAL_HIGH [SMALL] | 3 | 2 | 3/0.8400/0.7200 | 3/1.0733/0.7200 | 66.67% | 66.67% | 66.67% | 0.00% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.high_structure | HIGHER_HIGH | 71 | 49 | 70/1.3486/0.8225 | 70/0.7061/0.4975 | 57.75% | 47.89% | 49.30% | 26.76% | 1/0/0/0 | 1/1/1/1 |
| stage11_3.high_structure | LOWER_HIGH | 113 | 61 | 111/1.3575/0.6100 | 111/0.7038/0.5500 | 47.79% | 38.94% | 41.59% | 30.09% | 4/0/0/0 | 2/2/2/2 |
| stage11_3.high_structure | UNAVAILABLE | 146 | 100 | 146/1.9575/0.8325 | 146/1.0571/0.8850 | 50.68% | 39.04% | 41.10% | 30.14% | 10/1/1/0 | 0/0/0/0 |
| stage11_3.low_structure | EQUAL_LOW [SMALL] | 2 | 1 | 2/0.2350/0.2350 | 2/0.7450/0.7450 | 0.00% | 0.00% | 0.00% | 0.00% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.low_structure | HIGHER_LOW | 92 | 54 | 90/1.4126/0.6200 | 90/0.7602/0.5700 | 52.17% | 43.48% | 45.65% | 25.00% | 1/0/0/0 | 2/2/2/2 |
| stage11_3.low_structure | LOWER_LOW | 75 | 53 | 74/1.3215/0.8375 | 74/0.6180/0.4950 | 58.67% | 48.00% | 50.67% | 36.00% | 2/0/0/0 | 1/1/1/1 |
| stage11_3.low_structure | UNAVAILABLE | 164 | 110 | 164/1.8781/0.8320 | 164/1.0334/0.8550 | 48.17% | 37.20% | 39.02% | 28.66% | 12/1/1/0 | 0/0/0/0 |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE | 108 | 91 | 108/2.0035/0.7550 | 108/1.0984/0.8825 | 47.22% | 36.11% | 37.96% | 28.70% | 6/0/0/0 | 0/0/0/0 |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED | 37 | 15 | 37/1.2368/0.6650 | 37/0.8735/0.5600 | 62.16% | 43.24% | 45.95% | 29.73% | 3/0/0/0 | 0/0/0/0 |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL | 42 | 26 | 41/1.4048/0.7401 | 41/0.6756/0.4850 | 52.38% | 42.86% | 45.24% | 23.81% | 2/1/1/0 | 1/1/1/1 |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL | 146 | 78 | 144/1.4837/0.8050 | 144/0.7394/0.5835 | 51.37% | 43.84% | 45.89% | 30.82% | 4/0/0/0 | 2/2/2/2 |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 333 | 129 | 330/1.6164/0.7376 | 330/0.8640/0.6975 | 51.35% | 41.14% | 43.24% | 29.13% | 15/1/1/0 | 3/3/3/3 |


### FIRST_EXECUTABLE_MINUTE_OPEN_V1: ALL evaluation labels

Labels are retrospective evaluations, never predictors. Never-strong includes session-close censoring; longer pre-reclaim exposure in eventual-strong sequences is not a causal benefit.

| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EVENTUAL_STRONG | 524 | 170 | 283/241 | 524 | 2.1200 | 2.8064 | 1.4900 | 2.3137 | 1.2129 | 0.1700 | 72.90% |
| NEVER_STRONG | 209 | 107 | 117/92 | 203 | 1.4500 | 2.2292 | 2.4250 | 3.1102 | 0.7167 | -0.5900 | 97.13% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| EVENTUAL_STRONG | 524 | 57.44% | 45.61% | 34.16% | 27.86% | 51.53% | 39.31% | 32.63% | 24.24% | 19.08% |
| NEVER_STRONG | 209 | 19.62% | 6.70% | 2.87% | 0.96% | 7.66% | 3.35% | 1.44% | 0.96% | 0.96% |


### FIRST_EXECUTABLE_MINUTE_OPEN_V1: ALL continuous


| feature | pre_reclaim_mfe: r (n) | pre_reclaim_mae: r (n) | 0.25/0.25: r (n) | 0.50/0.25: r (n) | 0.50/0.30: r (n) | 1.00/0.30: r (n) |
|---|---|---|---|---|---|---|
| opening_range_width | 0.1296 (727) | 0.2307 (727) | 0.0121 (682) | 0.0030 (714) | 0.0199 (718) | 0.0605 (725) |
| body_size | 0.2691 (727) | 0.4918 (727) | 0.0449 (682) | 0.0355 (714) | 0.0392 (718) | 0.0665 (725) |
| directional_body | 0.2691 (727) | 0.4918 (727) | 0.0449 (682) | 0.0355 (714) | 0.0391 (718) | 0.0664 (725) |
| candle_range | 0.2739 (727) | 0.5416 (727) | 0.0469 (682) | 0.0415 (714) | 0.0441 (718) | 0.0708 (725) |
| body_range_ratio | 0.1314 (727) | 0.1643 (727) | 0.0028 (682) | -0.0124 (714) | -0.0054 (718) | 0.0138 (725) |
| directional_body_range_ratio | 0.1314 (727) | 0.1643 (727) | 0.0025 (682) | -0.0128 (714) | -0.0058 (718) | 0.0132 (725) |
| close_location | -0.0553 (727) | 0.0031 (727) | -0.0358 (682) | -0.0551 (714) | -0.0344 (718) | -0.0332 (725) |
| directional_close_location | 0.0168 (727) | 0.1669 (727) | -0.0679 (682) | -0.0687 (714) | -0.0744 (718) | -0.0431 (725) |
| distance_beyond_level | 0.2557 (727) | 0.4978 (727) | 0.0532 (682) | 0.0652 (714) | 0.0619 (718) | 0.0940 (725) |
| distance_beyond_level_atr14 | 0.1464 (394) | 0.3297 (394) | 0.0392 (376) | 0.0394 (389) | 0.0283 (390) | 0.0716 (392) |
| candle_volume | 0.2168 (727) | 0.3195 (727) | 0.0614 (682) | 0.0584 (714) | 0.0647 (718) | 0.0934 (725) |
| relative_volume_prior_6 | 0.1016 (509) | -0.0210 (509) | 0.0828 (485) | 0.0753 (501) | 0.0820 (504) | 0.1312 (507) |
| atr14 | 0.3006 (394) | 0.4915 (394) | 0.0450 (376) | 0.0370 (389) | 0.0379 (390) | 0.0787 (392) |
| minutes_since_open | -0.1046 (727) | -0.3113 (727) | 0.1001 (682) | 0.0617 (714) | 0.0768 (718) | 0.0012 (725) |
| minutes_since_ema_cross | -0.0580 (222) | -0.1267 (222) | 0.0111 (212) | -0.0299 (221) | 0.0226 (221) | -0.0200 (222) |
| break_attempt_rank | -0.0696 (727) | -0.2686 (727) | 0.1244 (682) | 0.1011 (714) | 0.0935 (718) | 0.0069 (725) |
| valid_hold_sequence_rank | -0.0955 (727) | -0.2533 (727) | 0.0494 (682) | 0.0434 (714) | 0.0489 (718) | -0.0055 (725) |
| stage10_9.ema9_ema20_absolute_separation | 0.0829 (322) | 0.2238 (322) | 0.0682 (309) | 0.0145 (320) | 0.0327 (320) | 0.0147 (322) |
| stage10_9.ema9_ema20_separation_atr14 | -0.0200 (322) | 0.0561 (322) | 0.0196 (309) | -0.0172 (320) | 0.0108 (320) | -0.0380 (322) |
| stage10_9.ema9_slope_1_bars | -0.0079 (462) | -0.0159 (462) | -0.0031 (441) | -0.0024 (455) | 0.0221 (457) | 0.0257 (460) |
| stage10_9.ema9_slope_2_bars | -0.0016 (442) | -0.0629 (442) | -0.0021 (421) | -0.0188 (435) | 0.0069 (437) | 0.0270 (440) |
| stage10_9.ema9_slope_3_bars | -0.0005 (423) | -0.0581 (423) | -0.0152 (402) | -0.0294 (416) | -0.0087 (418) | 0.0196 (421) |
| stage10_9.ema20_slope_1_bars | -0.0484 (308) | -0.0840 (308) | -0.0492 (295) | -0.0257 (306) | 0.0147 (306) | 0.0142 (308) |
| stage10_9.ema20_slope_2_bars | -0.0342 (300) | -0.1115 (300) | -0.0248 (288) | -0.0097 (298) | 0.0326 (298) | 0.0532 (300) |
| stage10_9.ema20_slope_3_bars | -0.0352 (291) | -0.1033 (291) | -0.0329 (279) | -0.0076 (289) | 0.0295 (289) | 0.0362 (291) |
| stage10_9.vwap_slope_1_bars | -0.0240 (727) | -0.0134 (727) | -0.0210 (682) | -0.0355 (714) | -0.0262 (718) | -0.0444 (725) |
| stage10_9.vwap_slope_2_bars | -0.0250 (649) | -0.0387 (649) | 0.0310 (610) | 0.0047 (637) | 0.0124 (641) | -0.0216 (647) |
| stage10_9.vwap_slope_3_bars | -0.0310 (604) | -0.0288 (604) | -0.0076 (577) | -0.0133 (595) | -0.0165 (599) | -0.0301 (602) |
| stage10_9.ema9_ema20_cross_count_6_bars | 0.0661 (279) | 0.0211 (279) | 0.0421 (268) | 0.0728 (277) | 0.0348 (277) | 0.0285 (279) |
| stage10_9.ema9_ema20_cross_count_12_bars | 0.1021 (236) | 0.0223 (236) | -0.0225 (227) | 0.0669 (235) | 0.0360 (235) | 0.0934 (236) |
| stage10_9.ema9_ema20_cross_count_24_bars | 0.0711 (157) | 0.1224 (157) | 0.1022 (152) | 0.0789 (156) | 0.0306 (156) | 0.0803 (157) |
| stage10_9.ema9_vwap_cross_count_6_bars | -0.0025 (394) | 0.0424 (394) | 0.0305 (376) | 0.0032 (389) | -0.0003 (390) | -0.0590 (392) |
| stage10_9.ema9_vwap_cross_count_12_bars | 0.0941 (322) | -0.0473 (322) | 0.0850 (309) | 0.1029 (320) | 0.1071 (320) | 0.0353 (322) |
| stage10_9.ema9_vwap_cross_count_24_bars | 0.0324 (230) | -0.0345 (230) | -0.0119 (221) | 0.0001 (229) | -0.0015 (229) | -0.0332 (230) |
| stage10_9.ema20_vwap_cross_count_6_bars | -0.0407 (279) | 0.0485 (279) | -0.0466 (268) | -0.0202 (277) | -0.0244 (277) | 0.0318 (279) |
| stage10_9.ema20_vwap_cross_count_12_bars | -0.0033 (236) | 0.0374 (236) | 0.0033 (227) | -0.0141 (235) | -0.0038 (235) | -0.0648 (236) |
| stage10_9.ema20_vwap_cross_count_24_bars | 0.0008 (157) | 0.0412 (157) | -0.0683 (152) | -0.0565 (156) | 0.0067 (156) | 0.0100 (157) |
| stage10_9.price_vwap_side_change_count_6_bars | 0.0724 (535) | 0.1296 (535) | -0.0340 (510) | 0.0116 (527) | -0.0193 (530) | -0.0100 (533) |
| stage10_9.price_vwap_side_change_count_12_bars | 0.1039 (423) | 0.1117 (423) | -0.0078 (402) | 0.0286 (416) | 0.0123 (418) | 0.0480 (421) |
| stage10_9.price_vwap_side_change_count_24_bars | 0.1211 (287) | 0.0306 (287) | 0.0757 (275) | 0.1472 (285) | 0.1282 (285) | 0.0858 (287) |
| stage10_9.rolling_high_low_range_6_bars | 0.2411 (535) | 0.4954 (535) | 0.0736 (510) | 0.0401 (527) | 0.0436 (530) | 0.0714 (533) |
| stage10_9.rolling_high_low_range_12_bars | 0.2585 (423) | 0.4714 (423) | 0.0798 (402) | 0.0356 (416) | 0.0480 (418) | 0.0827 (421) |
| stage10_9.rolling_high_low_range_24_bars | 0.1979 (287) | 0.4263 (287) | 0.0754 (275) | 0.0059 (285) | 0.0096 (285) | 0.0371 (287) |
| stage10_9.rolling_range_atr14_6_bars | 0.0549 (394) | 0.0533 (394) | 0.1272 (376) | 0.0306 (389) | 0.0281 (390) | 0.0620 (392) |
| stage10_9.rolling_range_atr14_12_bars | -0.0023 (394) | 0.0434 (394) | 0.0800 (376) | -0.0112 (389) | -0.0004 (390) | -0.0013 (392) |
| stage10_9.rolling_range_atr14_24_bars | -0.1131 (287) | 0.0581 (287) | -0.0232 (275) | -0.1194 (285) | -0.0904 (285) | -0.1197 (287) |
| stage10_9.directional_efficiency_6_bars | 0.0481 (535) | -0.0890 (535) | 0.0518 (510) | 0.0051 (527) | 0.0105 (530) | 0.0538 (533) |
| stage10_9.directional_efficiency_12_bars | -0.0237 (423) | -0.0563 (423) | 0.0175 (402) | 0.0188 (416) | 0.0407 (418) | 0.0411 (421) |
| stage10_9.directional_efficiency_24_bars | -0.0238 (287) | 0.0753 (287) | 0.0218 (275) | -0.0517 (285) | -0.0170 (285) | -0.0127 (287) |
| stage10_9.range_overlap_fraction_6_bars | 0.0290 (535) | 0.0306 (535) | 0.0025 (510) | 0.0473 (527) | 0.0516 (530) | 0.0347 (533) |
| stage10_9.range_overlap_fraction_12_bars | -0.0083 (423) | 0.0225 (423) | -0.0255 (402) | 0.0069 (416) | 0.0155 (418) | -0.0170 (421) |
| stage10_9.range_overlap_fraction_24_bars | -0.0768 (287) | 0.0529 (287) | -0.0724 (275) | -0.0048 (285) | 0.0066 (285) | -0.0497 (287) |
| stage10_9.close_direction_alternation_fraction_6_bars | -0.0315 (535) | 0.0643 (535) | -0.0501 (510) | -0.0125 (527) | 0.0211 (530) | -0.0097 (533) |
| stage10_9.close_direction_alternation_fraction_12_bars | 0.0069 (423) | 0.0450 (423) | -0.0801 (402) | -0.0569 (416) | -0.0639 (418) | 0.0158 (421) |
| stage10_9.close_direction_alternation_fraction_24_bars | 0.0139 (287) | -0.0238 (287) | -0.0105 (275) | 0.0160 (285) | 0.0034 (285) | 0.0366 (287) |
| stage10_9.confirmation_close_vwap_distance_atr14 | -0.0651 (394) | 0.0139 (394) | -0.0695 (376) | -0.0735 (389) | -0.0486 (390) | 0.0038 (392) |
| stage10_9.ema9_vwap_distance_atr14 | -0.0876 (394) | -0.0156 (394) | -0.0709 (376) | -0.0621 (389) | -0.0286 (390) | 0.0001 (392) |
| stage10_9.ema20_vwap_distance_atr14 | -0.1180 (322) | -0.0271 (322) | -0.0601 (309) | -0.0596 (320) | -0.0320 (320) | -0.0082 (322) |
| stage11_2.room_from_confirmation | 0.0777 (604) | 0.2052 (604) | -0.0213 (566) | -0.0181 (592) | -0.0071 (596) | 0.0166 (602) |
| stage11_2.room_in_atr | 0.0462 (330) | 0.0704 (330) | 0.0466 (312) | -0.0283 (325) | -0.0169 (326) | 0.0371 (328) |
| stage11_2.number_of_known_levels_above | 0.0946 (727) | 0.0529 (727) | 0.0570 (682) | 0.0776 (714) | 0.0542 (718) | 0.0669 (725) |
| stage11_2.number_of_known_levels_below | -0.0968 (727) | -0.0480 (727) | -0.0588 (682) | -0.0779 (714) | -0.0572 (718) | -0.0690 (725) |
| stage11_2.nearest_level_distance_above | 0.0531 (650) | 0.3343 (650) | -0.0089 (609) | -0.0304 (638) | -0.0316 (642) | -0.0282 (648) |
| stage11_2.nearest_level_distance_below | 0.1940 (681) | 0.2306 (681) | -0.0084 (639) | 0.0257 (668) | 0.0399 (672) | 0.0662 (679) |
| stage11_2.directional_level_count_within_0_5_atr | -0.0117 (394) | -0.0337 (394) | 0.0055 (376) | 0.0209 (389) | -0.0074 (390) | -0.0402 (392) |
| stage11_2.directional_level_count_within_1_0_atr | -0.0151 (394) | -0.0149 (394) | 0.0026 (376) | 0.0368 (389) | -0.0065 (390) | -0.1006 (392) |
| stage11_3.confirmation_close_to_latest_swing_high | 0.1630 (502) | 0.2407 (502) | 0.0667 (477) | 0.0432 (494) | 0.0393 (497) | 0.0670 (500) |
| stage11_3.confirmation_close_to_latest_swing_low | 0.0502 (489) | 0.2927 (489) | -0.0067 (464) | -0.0321 (481) | -0.0150 (484) | 0.0298 (487) |
| stage11_3.distance_to_swing_high_in_atr | 0.0377 (394) | 0.0516 (394) | 0.0618 (376) | 0.0109 (389) | -0.0237 (390) | -0.0026 (392) |
| stage11_3.distance_to_swing_low_in_atr | -0.0585 (388) | 0.0569 (388) | -0.0270 (370) | -0.0817 (383) | -0.0399 (384) | -0.0301 (386) |


### FIRST_EXECUTABLE_MINUTE_OPEN_V1: ALL categorical


| feature | category | n | sessions | pre-reclaim MFE n/mean/median | pre-reclaim MAE n/mean/median | 0.25/0.25 | 0.50/0.25 | 0.50/0.30 | 1.00/0.30 | ambiguous n across four pairs | no future n across four pairs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| direction | LONG | 400 | 137 | 397/1.3256/0.5650 | 397/0.8472/0.6900 | 45.25% | 31.75% | 37.00% | 21.50% | 19/7/5/2 | 3/3/3/3 |
| direction | SHORT | 333 | 129 | 330/1.6412/0.7425 | 330/0.8712/0.6900 | 48.35% | 37.84% | 41.44% | 26.43% | 26/6/4/0 | 3/3/3/3 |
| time_bucket | 09:35-10:00 | 192 | 151 | 192/1.9001/0.6600 | 192/1.0571/0.8785 | 40.10% | 30.21% | 34.90% | 23.44% | 20/5/4/0 | 0/0/0/0 |
| time_bucket | 10:00-10:30 | 112 | 84 | 112/1.4813/0.7827 | 112/1.0582/0.7750 | 50.00% | 35.71% | 37.50% | 22.32% | 4/1/0/0 | 0/0/0/0 |
| time_bucket | 10:30-11:00 | 72 | 54 | 72/1.5682/0.9025 | 72/0.9199/0.7850 | 43.06% | 33.33% | 38.89% | 22.22% | 5/4/3/2 | 0/0/0/0 |
| time_bucket | 11:00-12:00 | 105 | 64 | 105/1.4373/0.5600 | 105/0.7352/0.6200 | 46.67% | 36.19% | 41.90% | 27.62% | 7/2/1/0 | 0/0/0/0 |
| time_bucket | 12:00-13:30 | 118 | 62 | 118/1.2051/0.5150 | 118/0.6933/0.5625 | 44.92% | 35.59% | 39.83% | 25.42% | 4/0/0/0 | 0/0/0/0 |
| time_bucket | 13:30-15:00 | 67 | 49 | 67/1.1751/0.5700 | 67/0.6912/0.5800 | 56.72% | 38.81% | 41.79% | 25.37% | 3/1/1/0 | 0/0/0/0 |
| time_bucket | 15:00-close | 67 | 43 | 61/0.8591/0.5050 | 61/0.5050/0.4000 | 56.72% | 37.31% | 44.78% | 17.91% | 2/0/0/0 | 6/6/6/6 |
| ema9_20_alignment | EMA_ALIGNED | 211 | 75 | 208/1.1125/0.4850 | 208/0.6899/0.5400 | 50.24% | 36.97% | 40.28% | 23.70% | 9/1/1/0 | 3/3/3/3 |
| ema9_20_alignment | EMA_NOT_ALIGNED | 117 | 69 | 114/1.1862/0.5700 | 114/0.6144/0.5550 | 49.57% | 37.61% | 43.59% | 25.64% | 4/1/1/0 | 3/3/3/3 |
| ema9_20_alignment | EMA_UNAVAILABLE | 405 | 169 | 405/1.7315/0.7300 | 405/1.0131/0.8200 | 43.95% | 32.35% | 37.04% | 23.21% | 32/11/7/2 | 0/0/0/0 |
| price_vwap_alignment | VWAP_ALIGNED | 651 | 170 | 648/1.4753/0.6100 | 648/0.8879/0.7200 | 45.31% | 33.33% | 37.63% | 23.50% | 41/12/8/2 | 3/3/3/3 |
| price_vwap_alignment | VWAP_NOT_ALIGNED | 82 | 46 | 79/1.4161/0.7200 | 79/0.6137/0.5400 | 57.32% | 43.90% | 50.00% | 25.61% | 4/1/1/0 | 3/3/3/3 |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED | 349 | 114 | 346/1.2764/0.5650 | 346/0.7630/0.6500 | 46.99% | 34.38% | 38.97% | 24.07% | 18/6/4/2 | 3/3/3/3 |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED | 136 | 77 | 133/1.4843/0.6300 | 133/0.6729/0.5700 | 55.88% | 41.91% | 46.32% | 22.79% | 4/1/1/0 | 3/3/3/3 |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE | 248 | 164 | 248/1.7292/0.6425 | 248/1.0901/0.8525 | 41.13% | 30.65% | 35.08% | 23.79% | 23/6/4/0 | 0/0/0/0 |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED | 218 | 82 | 214/1.1243/0.5000 | 214/0.6959/0.5600 | 47.71% | 36.24% | 41.28% | 25.23% | 9/2/2/0 | 4/4/4/4 |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED | 110 | 70 | 108/1.1669/0.5775 | 108/0.5983/0.4850 | 54.55% | 39.09% | 41.82% | 22.73% | 4/0/0/0 | 2/2/2/2 |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 405 | 169 | 405/1.7315/0.7300 | 405/1.0131/0.8200 | 43.95% | 32.35% | 37.04% | 23.21% | 32/11/7/2 | 0/0/0/0 |
| prior_ema_cross | MATCHING_CROSS | 129 | 57 | 126/1.1136/0.5300 | 126/0.6713/0.4650 | 54.26% | 40.31% | 44.96% | 24.03% | 6/0/0/0 | 3/3/3/3 |
| prior_ema_cross | NO_PRIOR_CROSS | 505 | 170 | 505/1.6360/0.6600 | 505/0.9538/0.7700 | 43.96% | 32.48% | 36.83% | 23.96% | 35/12/8/2 | 0/0/0/0 |
| prior_ema_cross | OPPOSING_CROSS | 99 | 58 | 96/1.0559/0.5375 | 96/0.5999/0.5150 | 50.51% | 37.37% | 42.42% | 22.22% | 4/1/1/0 | 3/3/3/3 |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 491 | 124 | 487/1.4361/0.6350 | 487/0.7904/0.6500 | 49.69% | 36.86% | 41.75% | 24.64% | 31/9/5/2 | 4/4/4/4 |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL | 233 | 123 | 231/1.5210/0.5650 | 231/0.9995/0.7700 | 41.20% | 30.04% | 33.05% | 21.46% | 14/4/4/0 | 2/2/2/2 |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 9 | 9 | 9/1.9050/1.4700 | 9/0.8904/0.6700 | 22.22% | 22.22% | 44.44% | 33.33% | 0/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 | 56 | 36 | 56/1.2731/0.6050 | 56/0.7988/0.5850 | 50.00% | 39.29% | 41.07% | 17.86% | 4/2/2/1 | 0/0/0/0 |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 | 40 | 26 | 40/1.3845/0.6048 | 40/0.7144/0.6850 | 45.00% | 32.50% | 45.00% | 27.50% | 3/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 | 38 | 29 | 35/1.0815/0.5500 | 35/0.6950/0.5400 | 44.74% | 36.84% | 44.74% | 23.68% | 4/1/1/1 | 3/3/3/3 |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 | 51 | 35 | 51/1.6218/0.9200 | 51/0.7088/0.6800 | 50.98% | 43.14% | 49.02% | 39.22% | 0/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | GT_3_0_ATR | 75 | 33 | 74/1.2797/0.4875 | 74/0.7090/0.5700 | 50.67% | 33.33% | 37.33% | 24.00% | 4/0/0/0 | 1/1/1/1 |
| stage11_2.room_bucket | LT_0_5_ATR | 75 | 41 | 74/1.2094/0.5375 | 74/0.6414/0.4826 | 48.00% | 36.00% | 38.67% | 20.00% | 3/2/1/0 | 1/1/1/1 |
| stage11_2.room_bucket | OPEN_ENDED | 124 | 43 | 123/1.1826/0.4550 | 123/0.8029/0.5800 | 48.39% | 33.06% | 36.29% | 22.58% | 7/1/1/0 | 1/1/1/1 |
| stage11_2.room_bucket | UNAVAILABLE_ATR | 274 | 151 | 274/1.7920/0.7160 | 274/1.0634/0.8575 | 43.43% | 32.48% | 36.86% | 22.99% | 20/7/4/0 | 0/0/0/0 |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 731 | 169 | 725/1.4658/0.6100 | 725/0.8594/0.6900 | 46.51% | 34.47% | 38.85% | 23.67% | 45/13/9/2 | 6/6/6/6 |
| known_level_coverage | PARTIAL_UNAVAILABLE [SMALL] | 2 | 1 | 2/2.5900/2.5900 | 2/0.3800/0.3800 | 100.00% | 50.00% | 100.00% | 50.00% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.structure | BEARISH_STRUCTURE | 101 | 62 | 101/1.1940/0.5100 | 101/0.6709/0.5700 | 51.49% | 36.63% | 40.59% | 23.76% | 3/1/1/0 | 0/0/0/0 |
| stage11_3.structure | BULLISH_STRUCTURE | 102 | 63 | 102/1.2109/0.6450 | 102/0.6599/0.5448 | 54.90% | 45.10% | 50.98% | 25.49% | 4/0/0/0 | 0/0/0/0 |
| stage11_3.structure | MIXED_STRUCTURE | 152 | 73 | 146/1.1392/0.4800 | 146/0.6760/0.5675 | 46.05% | 33.55% | 38.16% | 25.00% | 8/2/1/0 | 6/6/6/6 |
| stage11_3.structure | UNAVAILABLE | 378 | 169 | 378/1.7393/0.7060 | 378/1.0319/0.8400 | 43.39% | 31.48% | 35.71% | 22.75% | 30/10/7/2 | 0/0/0/0 |
| stage11_3.agreement | STRUCTURE_ALIGNED | 116 | 70 | 116/1.2385/0.7175 | 116/0.6469/0.5398 | 52.59% | 43.10% | 49.14% | 30.17% | 6/1/1/0 | 0/0/0/0 |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED | 239 | 93 | 233/1.1449/0.5100 | 233/0.6812/0.5700 | 48.95% | 35.15% | 39.33% | 22.18% | 9/2/1/0 | 6/6/6/6 |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 378 | 169 | 378/1.7393/0.7060 | 378/1.0319/0.8400 | 43.39% | 31.48% | 35.71% | 22.75% | 30/10/7/2 | 0/0/0/0 |
| stage11_3.high_structure | EQUAL_HIGH [SMALL] | 4 | 3 | 4/0.8400/0.7900 | 4/1.0188/0.7875 | 75.00% | 75.00% | 75.00% | 0.00% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.high_structure | HIGHER_HIGH | 175 | 83 | 173/1.1602/0.5900 | 173/0.6795/0.5500 | 52.57% | 40.57% | 45.71% | 24.00% | 9/1/2/2 | 2/2/2/2 |
| stage11_3.high_structure | LOWER_HIGH | 214 | 88 | 210/1.2644/0.5000 | 210/0.6918/0.5700 | 45.79% | 32.71% | 36.92% | 24.30% | 8/3/2/0 | 4/4/4/4 |
| stage11_3.high_structure | UNAVAILABLE | 340 | 168 | 340/1.7597/0.7010 | 340/1.0498/0.8500 | 43.82% | 32.06% | 36.47% | 23.53% | 28/9/5/0 | 0/0/0/0 |
| stage11_3.low_structure | EQUAL_LOW [SMALL] | 3 | 2 | 3/0.7733/0.5100 | 3/0.5131/0.4200 | 33.33% | 33.33% | 33.33% | 33.33% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.low_structure | HIGHER_LOW | 214 | 94 | 210/1.2302/0.5475 | 210/0.7123/0.5925 | 49.07% | 38.32% | 44.39% | 25.70% | 11/3/1/0 | 4/4/4/4 |
| stage11_3.low_structure | LOWER_LOW | 160 | 77 | 158/1.1411/0.5250 | 158/0.6511/0.5399 | 51.88% | 36.88% | 40.62% | 23.12% | 6/1/1/0 | 2/2/2/2 |
| stage11_3.low_structure | UNAVAILABLE | 356 | 169 | 356/1.7610/0.7010 | 356/1.0389/0.8400 | 42.98% | 31.18% | 35.11% | 22.75% | 28/9/7/2 | 0/0/0/0 |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE | 234 | 158 | 234/1.8509/0.6925 | 234/1.1043/0.8525 | 42.74% | 32.48% | 36.32% | 24.79% | 21/6/4/0 | 0/0/0/0 |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED | 86 | 33 | 85/1.0815/0.4300 | 85/0.6954/0.5000 | 52.33% | 33.72% | 38.37% | 22.09% | 3/0/0/0 | 1/1/1/1 |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL | 99 | 50 | 97/1.3512/0.6799 | 97/0.6846/0.6200 | 49.49% | 37.37% | 39.39% | 19.19% | 3/2/1/0 | 2/2/2/2 |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL | 314 | 108 | 311/1.3241/0.6100 | 311/0.7714/0.6550 | 47.13% | 35.35% | 41.08% | 24.84% | 18/5/4/2 | 3/3/3/3 |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 733 | 170 | 727/1.4689/0.6150 | 727/0.8581/0.6900 | 46.66% | 34.52% | 39.02% | 23.74% | 45/13/9/2 | 6/6/6/6 |


### FIRST_EXECUTABLE_MINUTE_OPEN_V1: LONG evaluation labels

Labels are retrospective evaluations, never predictors. Never-strong includes session-close censoring; longer pre-reclaim exposure in eventual-strong sequences is not a causal benefit.

| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EVENTUAL_STRONG | 283 | 132 | 283/0 | 283 | 1.9600 | 2.5807 | 1.7650 | 2.4625 | 1.0480 | 0.0750 | 73.14% |
| NEVER_STRONG | 117 | 71 | 117/0 | 114 | 1.5900 | 2.3900 | 2.5200 | 3.1075 | 0.7691 | -0.5550 | 97.44% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| EVENTUAL_STRONG | 283 | 56.54% | 41.70% | 29.68% | 24.03% | 48.41% | 35.69% | 29.33% | 21.55% | 15.90% |
| NEVER_STRONG | 117 | 17.95% | 7.69% | 2.56% | 1.71% | 9.40% | 3.42% | 2.56% | 1.71% | 1.71% |


### FIRST_EXECUTABLE_MINUTE_OPEN_V1: LONG continuous


| feature | pre_reclaim_mfe: r (n) | pre_reclaim_mae: r (n) | 0.25/0.25: r (n) | 0.50/0.25: r (n) | 0.50/0.30: r (n) | 1.00/0.30: r (n) |
|---|---|---|---|---|---|---|
| opening_range_width | 0.0904 (397) | 0.2096 (397) | -0.0283 (378) | -0.0016 (390) | 0.0069 (392) | 0.0513 (395) |
| body_size | 0.2695 (397) | 0.4476 (397) | 0.0576 (378) | 0.0789 (390) | 0.0792 (392) | 0.0735 (395) |
| directional_body | 0.2695 (397) | 0.4476 (397) | 0.0576 (378) | 0.0789 (390) | 0.0792 (392) | 0.0735 (395) |
| candle_range | 0.2837 (397) | 0.4977 (397) | 0.0669 (378) | 0.0988 (390) | 0.0965 (392) | 0.0807 (395) |
| body_range_ratio | 0.1255 (397) | 0.1224 (397) | -0.0018 (378) | -0.0192 (390) | -0.0012 (392) | 0.0166 (395) |
| directional_body_range_ratio | 0.1255 (397) | 0.1224 (397) | -0.0018 (378) | -0.0192 (390) | -0.0012 (392) | 0.0166 (395) |
| close_location | 0.0276 (397) | 0.1424 (397) | -0.0432 (378) | -0.0571 (390) | -0.0549 (392) | -0.0032 (395) |
| directional_close_location | 0.0276 (397) | 0.1424 (397) | -0.0432 (378) | -0.0571 (390) | -0.0549 (392) | -0.0032 (395) |
| distance_beyond_level | 0.2752 (397) | 0.4301 (397) | 0.0559 (378) | 0.0675 (390) | 0.0704 (392) | 0.0744 (395) |
| distance_beyond_level_atr14 | 0.1737 (212) | 0.2984 (212) | 0.0336 (204) | 0.0400 (208) | 0.0455 (209) | 0.0379 (210) |
| candle_volume | 0.2754 (397) | 0.2584 (397) | 0.0908 (378) | 0.1021 (390) | 0.1186 (392) | 0.1317 (395) |
| relative_volume_prior_6 | 0.1769 (277) | -0.0559 (277) | 0.1292 (268) | 0.1644 (273) | 0.1726 (274) | 0.2444 (275) |
| atr14 | 0.2846 (212) | 0.4929 (212) | 0.0474 (204) | 0.0998 (208) | 0.0896 (209) | 0.0671 (210) |
| minutes_since_open | -0.1285 (397) | -0.2887 (397) | 0.0699 (378) | 0.0494 (390) | 0.0848 (392) | 0.0341 (395) |
| minutes_since_ema_cross | -0.0412 (103) | -0.0121 (103) | -0.0049 (99) | 0.0082 (102) | 0.0458 (102) | 0.0807 (103) |
| break_attempt_rank | -0.0947 (397) | -0.2519 (397) | 0.1248 (378) | 0.0960 (390) | 0.0942 (392) | 0.0311 (395) |
| valid_hold_sequence_rank | -0.1306 (397) | -0.2257 (397) | 0.0194 (378) | 0.0136 (390) | 0.0399 (392) | 0.0242 (395) |
| stage10_9.ema9_ema20_absolute_separation | 0.0865 (169) | 0.1845 (169) | 0.0080 (165) | 0.0759 (168) | 0.1006 (168) | 0.0444 (169) |
| stage10_9.ema9_ema20_separation_atr14 | 0.0122 (169) | 0.0105 (169) | -0.0132 (165) | 0.0382 (168) | 0.0834 (168) | 0.0063 (169) |
| stage10_9.ema9_slope_1_bars | 0.2224 (254) | 0.2302 (254) | 0.0787 (245) | 0.0499 (250) | 0.0710 (251) | 0.1521 (252) |
| stage10_9.ema9_slope_2_bars | 0.1042 (242) | 0.0326 (242) | 0.0410 (233) | -0.0220 (238) | 0.0063 (239) | 0.1099 (240) |
| stage10_9.ema9_slope_3_bars | 0.0579 (231) | 0.0170 (231) | 0.0037 (222) | -0.0579 (227) | -0.0279 (228) | 0.0920 (229) |
| stage10_9.ema20_slope_1_bars | 0.1144 (163) | 0.0803 (163) | 0.0560 (159) | 0.0461 (162) | 0.0964 (162) | 0.1603 (163) |
| stage10_9.ema20_slope_2_bars | 0.0465 (158) | -0.0449 (158) | 0.0433 (154) | 0.0021 (157) | 0.0673 (157) | 0.1512 (158) |
| stage10_9.ema20_slope_3_bars | -0.0162 (154) | -0.0001 (154) | -0.0244 (150) | -0.0536 (153) | 0.0085 (153) | 0.0903 (154) |
| stage10_9.vwap_slope_1_bars | 0.1671 (397) | 0.2580 (397) | -0.0289 (378) | -0.0305 (390) | -0.0292 (392) | 0.0028 (395) |
| stage10_9.vwap_slope_2_bars | 0.1145 (352) | 0.1690 (352) | 0.0713 (338) | 0.0399 (346) | 0.0557 (348) | 0.0529 (350) |
| stage10_9.vwap_slope_3_bars | 0.0696 (332) | 0.1662 (332) | -0.0280 (322) | -0.0049 (327) | 0.0169 (329) | 0.0889 (330) |
| stage10_9.ema9_ema20_cross_count_6_bars | 0.1281 (147) | -0.0669 (147) | 0.0786 (143) | 0.0722 (146) | 0.0376 (146) | 0.0659 (147) |
| stage10_9.ema9_ema20_cross_count_12_bars | 0.1582 (122) | -0.0835 (122) | -0.0234 (118) | 0.0455 (121) | 0.0244 (121) | 0.0342 (122) |
| stage10_9.ema9_ema20_cross_count_24_bars | 0.0596 (79) | 0.1765 (79) | 0.0682 (76) | -0.0051 (78) | -0.0532 (78) | -0.0329 (79) |
| stage10_9.ema9_vwap_cross_count_6_bars | -0.0537 (212) | 0.0248 (212) | 0.0028 (204) | -0.0460 (208) | -0.0474 (209) | -0.0559 (210) |
| stage10_9.ema9_vwap_cross_count_12_bars | 0.1081 (169) | -0.1151 (169) | 0.0765 (165) | 0.1039 (168) | 0.1283 (168) | 0.1021 (169) |
| stage10_9.ema9_vwap_cross_count_24_bars | -0.0299 (117) | -0.1115 (117) | 0.0220 (113) | 0.0081 (116) | 0.0306 (116) | -0.0296 (117) |
| stage10_9.ema20_vwap_cross_count_6_bars | -0.1016 (147) | -0.0258 (147) | -0.0416 (143) | 0.0213 (146) | 0.0023 (146) | 0.0364 (147) |
| stage10_9.ema20_vwap_cross_count_12_bars | -0.0353 (122) | -0.0192 (122) | 0.0489 (118) | 0.0156 (121) | 0.0440 (121) | -0.0777 (122) |
| stage10_9.ema20_vwap_cross_count_24_bars | -0.0467 (79) | 0.0200 (79) | -0.0659 (76) | -0.1233 (78) | -0.0110 (78) | -0.0810 (79) |
| stage10_9.price_vwap_side_change_count_6_bars | 0.0026 (291) | 0.1770 (291) | -0.0412 (282) | -0.0224 (287) | -0.0528 (288) | -0.0733 (289) |
| stage10_9.price_vwap_side_change_count_12_bars | 0.0415 (231) | 0.1326 (231) | -0.0228 (222) | -0.0372 (227) | -0.0550 (228) | -0.0047 (229) |
| stage10_9.price_vwap_side_change_count_24_bars | 0.0822 (151) | 0.0671 (151) | 0.0770 (147) | 0.1240 (150) | 0.1298 (150) | 0.1053 (151) |
| stage10_9.rolling_high_low_range_6_bars | 0.1971 (291) | 0.4714 (291) | 0.0646 (282) | 0.0489 (287) | 0.0504 (288) | 0.0246 (289) |
| stage10_9.rolling_high_low_range_12_bars | 0.2493 (231) | 0.4516 (231) | 0.0425 (222) | 0.0702 (227) | 0.0695 (228) | 0.0649 (229) |
| stage10_9.rolling_high_low_range_24_bars | 0.1986 (151) | 0.4419 (151) | 0.0134 (147) | 0.0257 (150) | 0.0276 (150) | 0.0360 (151) |
| stage10_9.rolling_range_atr14_6_bars | 0.0503 (212) | 0.0402 (212) | 0.0682 (204) | -0.0503 (208) | -0.0221 (209) | -0.0168 (210) |
| stage10_9.rolling_range_atr14_12_bars | 0.0209 (212) | -0.0302 (212) | 0.0427 (204) | -0.0254 (208) | -0.0147 (209) | -0.0584 (210) |
| stage10_9.rolling_range_atr14_24_bars | -0.1264 (151) | 0.0577 (151) | -0.1090 (147) | -0.1553 (150) | -0.1138 (150) | -0.1466 (151) |
| stage10_9.directional_efficiency_6_bars | 0.0668 (291) | -0.1253 (291) | 0.0666 (282) | -0.0104 (287) | 0.0106 (288) | 0.0503 (289) |
| stage10_9.directional_efficiency_12_bars | -0.0008 (231) | -0.1548 (231) | 0.0141 (222) | 0.0441 (227) | 0.0997 (228) | 0.0566 (229) |
| stage10_9.directional_efficiency_24_bars | 0.0201 (151) | 0.0523 (151) | 0.0023 (147) | -0.0232 (150) | 0.0275 (150) | 0.0295 (151) |
| stage10_9.range_overlap_fraction_6_bars | N/A (291) | N/A (291) | N/A (282) | N/A (287) | N/A (288) | N/A (289) |
| stage10_9.range_overlap_fraction_12_bars | N/A (231) | N/A (231) | N/A (222) | N/A (227) | N/A (228) | N/A (229) |
| stage10_9.range_overlap_fraction_24_bars | -0.1462 (151) | 0.1003 (151) | -0.1215 (147) | -0.0411 (150) | -0.0271 (150) | -0.0789 (151) |
| stage10_9.close_direction_alternation_fraction_6_bars | -0.0237 (291) | 0.0969 (291) | -0.0544 (282) | -0.0203 (287) | 0.0141 (288) | 0.0199 (289) |
| stage10_9.close_direction_alternation_fraction_12_bars | -0.0241 (231) | 0.0190 (231) | -0.0507 (222) | -0.0715 (227) | -0.0680 (228) | -0.0246 (229) |
| stage10_9.close_direction_alternation_fraction_24_bars | 0.0079 (151) | -0.0071 (151) | -0.0270 (147) | -0.0210 (150) | 0.0234 (150) | 0.0283 (151) |
| stage10_9.confirmation_close_vwap_distance_atr14 | 0.0239 (212) | -0.0387 (212) | -0.0756 (204) | -0.0454 (208) | 0.0026 (209) | 0.0590 (210) |
| stage10_9.ema9_vwap_distance_atr14 | -0.0344 (212) | -0.0203 (212) | -0.0875 (204) | -0.0426 (208) | -0.0157 (209) | 0.0408 (210) |
| stage10_9.ema20_vwap_distance_atr14 | -0.0404 (169) | 0.0399 (169) | -0.0645 (165) | -0.0402 (168) | -0.0279 (168) | 0.0046 (169) |
| stage11_2.room_from_confirmation | 0.0424 (320) | 0.2295 (320) | 0.0173 (305) | -0.0168 (314) | -0.0365 (316) | -0.0326 (318) |
| stage11_2.room_in_atr | 0.0150 (177) | 0.1476 (177) | 0.0523 (169) | -0.0762 (173) | -0.1023 (174) | -0.0601 (175) |
| stage11_2.number_of_known_levels_above | 0.0379 (397) | 0.1365 (397) | 0.0234 (378) | 0.0364 (390) | 0.0349 (392) | 0.0068 (395) |
| stage11_2.number_of_known_levels_below | -0.0374 (397) | -0.1291 (397) | -0.0212 (378) | -0.0272 (390) | -0.0355 (392) | 0.0001 (395) |
| stage11_2.nearest_level_distance_above | 0.0424 (320) | 0.2295 (320) | 0.0173 (305) | -0.0168 (314) | -0.0365 (316) | -0.0326 (318) |
| stage11_2.nearest_level_distance_below | 0.2464 (397) | 0.4192 (397) | 0.0351 (378) | 0.0439 (390) | 0.0356 (392) | 0.0124 (395) |
| stage11_2.directional_level_count_within_0_5_atr | 0.0244 (212) | -0.0671 (212) | -0.0023 (204) | 0.0207 (208) | -0.0064 (209) | 0.0249 (210) |
| stage11_2.directional_level_count_within_1_0_atr | 0.0073 (212) | -0.0174 (212) | -0.0050 (204) | 0.0712 (208) | 0.0264 (209) | -0.0548 (210) |
| stage11_3.confirmation_close_to_latest_swing_high | 0.0312 (271) | 0.2070 (271) | 0.0443 (262) | 0.0672 (267) | 0.0362 (268) | -0.0372 (269) |
| stage11_3.confirmation_close_to_latest_swing_low | 0.1484 (267) | 0.3789 (267) | -0.0377 (257) | -0.0348 (262) | -0.0134 (264) | 0.0305 (265) |
| stage11_3.distance_to_swing_high_in_atr | -0.0373 (212) | 0.0527 (212) | 0.0601 (204) | 0.0312 (208) | -0.0166 (209) | -0.0723 (210) |
| stage11_3.distance_to_swing_low_in_atr | 0.0193 (210) | 0.0649 (210) | -0.0883 (202) | -0.1165 (206) | -0.0685 (207) | -0.0655 (208) |


### FIRST_EXECUTABLE_MINUTE_OPEN_V1: LONG categorical


| feature | category | n | sessions | pre-reclaim MFE n/mean/median | pre-reclaim MAE n/mean/median | 0.25/0.25 | 0.50/0.25 | 0.50/0.30 | 1.00/0.30 | ambiguous n across four pairs | no future n across four pairs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| direction | LONG | 400 | 137 | 397/1.3256/0.5650 | 397/0.8472/0.6900 | 45.25% | 31.75% | 37.00% | 21.50% | 19/7/5/2 | 3/3/3/3 |
| time_bucket | 09:35-10:00 | 106 | 92 | 106/1.6985/0.6125 | 106/1.0209/0.8525 | 40.57% | 29.25% | 33.96% | 20.75% | 10/3/2/0 | 0/0/0/0 |
| time_bucket | 10:00-10:30 | 60 | 49 | 60/1.3440/0.6925 | 60/1.1016/0.7250 | 53.33% | 35.00% | 36.67% | 20.00% | 0/0/0/0 | 0/0/0/0 |
| time_bucket | 10:30-11:00 | 39 | 32 | 39/1.4413/0.7393 | 39/0.9537/0.9331 | 38.46% | 30.77% | 38.46% | 20.51% | 3/2/2/2 | 0/0/0/0 |
| time_bucket | 11:00-12:00 | 67 | 41 | 67/1.3873/0.5100 | 67/0.7115/0.6500 | 47.76% | 34.33% | 40.30% | 26.87% | 2/1/0/0 | 0/0/0/0 |
| time_bucket | 12:00-13:30 | 65 | 35 | 65/0.8116/0.3100 | 65/0.6208/0.5500 | 36.92% | 26.15% | 30.77% | 16.92% | 1/0/0/0 | 0/0/0/0 |
| time_bucket | 13:30-15:00 | 32 | 24 | 32/1.1776/0.3925 | 32/0.6976/0.6450 | 56.25% | 34.38% | 37.50% | 21.88% | 2/1/1/0 | 0/0/0/0 |
| time_bucket | 15:00-close | 31 | 24 | 28/0.9286/0.5575 | 28/0.5168/0.4050 | 54.84% | 38.71% | 51.61% | 25.81% | 1/0/0/0 | 3/3/3/3 |
| ema9_20_alignment | EMA_ALIGNED | 99 | 47 | 98/0.9891/0.3775 | 98/0.6521/0.5550 | 46.46% | 31.31% | 36.36% | 21.21% | 2/0/0/0 | 1/1/1/1 |
| ema9_20_alignment | EMA_NOT_ALIGNED | 73 | 41 | 71/0.9709/0.5200 | 71/0.6380/0.5700 | 46.58% | 34.25% | 41.10% | 24.66% | 2/1/1/0 | 2/2/2/2 |
| ema9_20_alignment | EMA_UNAVAILABLE | 228 | 126 | 228/1.5807/0.6300 | 228/0.9962/0.8050 | 44.30% | 31.14% | 35.96% | 20.61% | 15/6/4/2 | 0/0/0/0 |
| price_vwap_alignment | VWAP_ALIGNED | 351 | 137 | 350/1.3241/0.5625 | 350/0.8777/0.7200 | 44.73% | 31.05% | 36.18% | 21.37% | 17/6/4/2 | 1/1/1/1 |
| price_vwap_alignment | VWAP_NOT_ALIGNED | 49 | 26 | 47/1.3368/0.6300 | 47/0.6200/0.5700 | 48.98% | 36.73% | 42.86% | 22.45% | 2/1/1/0 | 2/2/2/2 |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED | 192 | 82 | 191/1.1280/0.5200 | 191/0.7683/0.6800 | 44.79% | 30.21% | 35.94% | 21.35% | 8/4/3/2 | 1/1/1/1 |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED | 73 | 38 | 71/1.3294/0.5850 | 71/0.6161/0.5700 | 53.42% | 39.73% | 45.21% | 23.29% | 1/0/0/0 | 2/2/2/2 |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE | 135 | 107 | 135/1.6033/0.6100 | 135/1.0803/0.8400 | 41.48% | 29.63% | 34.07% | 20.74% | 10/3/2/0 | 0/0/0/0 |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED | 117 | 52 | 115/0.8946/0.3800 | 115/0.6697/0.5800 | 43.59% | 31.62% | 38.46% | 23.08% | 3/1/1/0 | 2/2/2/2 |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED | 55 | 34 | 54/1.1665/0.5775 | 54/0.5960/0.5200 | 52.73% | 34.55% | 38.18% | 21.82% | 1/0/0/0 | 1/1/1/1 |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 228 | 126 | 228/1.5807/0.6300 | 228/0.9962/0.8050 | 44.30% | 31.14% | 35.96% | 20.61% | 15/6/4/2 | 0/0/0/0 |
| prior_ema_cross | MATCHING_CROSS | 45 | 28 | 44/1.2399/0.7100 | 44/0.5799/0.4500 | 53.33% | 37.78% | 46.67% | 24.44% | 2/0/0/0 | 1/1/1/1 |
| prior_ema_cross | NO_PRIOR_CROSS | 294 | 132 | 294/1.4308/0.5650 | 294/0.9316/0.7550 | 43.54% | 30.27% | 35.03% | 21.09% | 15/6/4/2 | 0/0/0/0 |
| prior_ema_cross | OPPOSING_CROSS | 61 | 34 | 59/0.8655/0.5200 | 59/0.6258/0.5700 | 47.54% | 34.43% | 39.34% | 21.31% | 2/1/1/0 | 2/2/2/2 |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 267 | 91 | 265/1.2411/0.5600 | 265/0.7559/0.6500 | 49.06% | 34.46% | 40.45% | 22.47% | 10/5/3/2 | 2/2/2/2 |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL | 125 | 67 | 124/1.4536/0.5625 | 124/1.0389/0.7800 | 38.40% | 26.40% | 28.80% | 18.40% | 9/2/2/0 | 1/1/1/1 |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 8 | 8 | 8/2.1419/1.7025 | 8/0.8992/0.6400 | 25.00% | 25.00% | 50.00% | 37.50% | 0/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 | 30 | 19 | 30/1.2059/0.5775 | 30/0.6918/0.6450 | 46.67% | 40.00% | 43.33% | 13.33% | 1/1/1/1 | 0/0/0/0 |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 24 | 15 | 24/1.0892/0.6320 | 24/0.7939/0.7550 | 41.67% | 29.17% | 41.67% | 25.00% | 1/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 17 | 13 | 16/1.0650/0.7750 | 16/0.6991/0.4150 | 58.82% | 52.94% | 70.59% | 35.29% | 2/1/1/1 | 1/1/1/1 |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 24 | 16 | 24/0.9838/0.6500 | 24/0.7938/0.7450 | 37.50% | 29.17% | 37.50% | 29.17% | 0/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | GT_3_0_ATR | 41 | 21 | 41/1.2262/0.3950 | 41/0.7611/0.5700 | 51.22% | 29.27% | 31.71% | 19.51% | 1/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | LT_0_5_ATR | 43 | 24 | 42/1.3550/0.5025 | 42/0.6321/0.4500 | 44.19% | 32.56% | 37.21% | 23.26% | 3/2/1/0 | 1/1/1/1 |
| stage11_2.room_bucket | OPEN_ENDED | 78 | 28 | 77/1.1787/0.3400 | 77/0.7194/0.5600 | 44.87% | 28.21% | 32.05% | 20.51% | 4/1/1/0 | 1/1/1/1 |
| stage11_2.room_bucket | UNAVAILABLE_ATR | 143 | 94 | 143/1.5760/0.6400 | 143/1.0709/0.8500 | 44.06% | 30.77% | 34.97% | 20.28% | 7/2/1/0 | 0/0/0/0 |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 399 | 136 | 396/1.3273/0.5650 | 396/0.8480/0.6900 | 45.11% | 31.83% | 36.84% | 21.55% | 19/7/5/2 | 3/3/3/3 |
| known_level_coverage | PARTIAL_UNAVAILABLE [SMALL] | 1 | 1 | 1/0.6600/0.6600 | 1/0.5100/0.5100 | 100.00% | 0.00% | 100.00% | 0.00% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.structure | BEARISH_STRUCTURE | 46 | 32 | 46/1.0795/0.4025 | 46/0.6828/0.5900 | 47.83% | 30.43% | 34.78% | 15.22% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.structure | BULLISH_STRUCTURE | 61 | 41 | 61/1.1923/0.6799 | 61/0.6342/0.5600 | 50.82% | 44.26% | 52.46% | 29.51% | 3/0/0/0 | 0/0/0/0 |
| stage11_3.structure | MIXED_STRUCTURE | 84 | 47 | 81/0.8434/0.3700 | 81/0.6424/0.5800 | 42.86% | 26.19% | 30.95% | 20.24% | 2/1/1/0 | 3/3/3/3 |
| stage11_3.structure | UNAVAILABLE | 209 | 122 | 209/1.6056/0.6400 | 209/1.0249/0.8100 | 44.02% | 30.62% | 35.41% | 21.05% | 14/6/4/2 | 0/0/0/0 |
| stage11_3.agreement | STRUCTURE_ALIGNED | 61 | 41 | 61/1.1923/0.6799 | 61/0.6342/0.5600 | 50.82% | 44.26% | 52.46% | 29.51% | 3/0/0/0 | 0/0/0/0 |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED | 130 | 56 | 127/0.9289/0.3700 | 127/0.6570/0.5800 | 44.62% | 27.69% | 32.31% | 18.46% | 2/1/1/0 | 3/3/3/3 |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 209 | 122 | 209/1.6056/0.6400 | 209/1.0249/0.8100 | 44.02% | 30.62% | 35.41% | 21.05% | 14/6/4/2 | 0/0/0/0 |
| stage11_3.high_structure | EQUAL_HIGH [SMALL] | 1 | 1 | 1/0.8600/0.8600 | 1/0.8350/0.8350 | 100.00% | 100.00% | 100.00% | 0.00% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.high_structure | HIGHER_HIGH | 104 | 56 | 103/1.0222/0.5247 | 103/0.6544/0.5700 | 50.00% | 38.46% | 44.23% | 24.04% | 5/1/2/2 | 1/1/1/1 |
| stage11_3.high_structure | LOWER_HIGH | 101 | 51 | 99/1.1369/0.3950 | 99/0.6698/0.5800 | 43.56% | 26.73% | 31.68% | 19.80% | 1/1/1/0 | 2/2/2/2 |
| stage11_3.high_structure | UNAVAILABLE | 194 | 120 | 194/1.5855/0.6375 | 194/1.0401/0.8125 | 43.30% | 30.41% | 35.57% | 21.13% | 13/5/2/0 | 0/0/0/0 |
| stage11_3.low_structure | EQUAL_LOW [SMALL] | 1 | 1 | 1/1.7200/1.7200 | 1/0.0994/0.0994 | 100.00% | 100.00% | 100.00% | 100.00% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.low_structure | HIGHER_LOW | 122 | 64 | 120/1.0740/0.5274 | 120/0.6726/0.6050 | 44.26% | 33.61% | 41.80% | 26.23% | 6/2/1/0 | 2/2/2/2 |
| stage11_3.low_structure | LOWER_LOW | 85 | 48 | 84/0.9704/0.3800 | 84/0.6669/0.5700 | 49.41% | 31.76% | 35.29% | 16.47% | 1/0/0/0 | 1/1/1/1 |
| stage11_3.low_structure | UNAVAILABLE | 192 | 115 | 192/1.6363/0.6425 | 192/1.0391/0.8225 | 43.75% | 30.21% | 34.38% | 20.31% | 12/5/4/2 | 0/0/0/0 |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE | 126 | 108 | 126/1.6940/0.6525 | 126/1.1043/0.8445 | 46.03% | 34.13% | 38.10% | 24.60% | 10/3/2/0 | 0/0/0/0 |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED | 49 | 18 | 48/0.9480/0.3126 | 48/0.5614/0.4900 | 46.94% | 26.53% | 32.65% | 18.37% | 1/0/0/0 | 1/1/1/1 |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL | 57 | 31 | 56/1.2948/0.5400 | 56/0.6828/0.6500 | 47.37% | 35.09% | 36.84% | 19.30% | 2/2/1/0 | 1/1/1/1 |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL | 168 | 72 | 167/1.1666/0.5200 | 167/0.7904/0.7100 | 43.45% | 30.36% | 37.50% | 20.83% | 6/2/2/2 | 1/1/1/1 |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 400 | 137 | 397/1.3256/0.5650 | 397/0.8472/0.6900 | 45.25% | 31.75% | 37.00% | 21.50% | 19/7/5/2 | 3/3/3/3 |


### FIRST_EXECUTABLE_MINUTE_OPEN_V1: SHORT evaluation labels

Labels are retrospective evaluations, never predictors. Never-strong includes session-close censoring; longer pre-reclaim exposure in eventual-strong sequences is not a causal benefit.

| Group | n | contributing sessions | L/S | EOD n | MFE median $ | MFE mean $ | MAE median $ | MAE mean $ | mean MFE/MAE | EOD median $ | reclaim % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EVENTUAL_STRONG | 241 | 114 | 0/241 | 241 | 2.4800 | 3.0714 | 1.2700 | 2.1390 | 1.4359 | 0.4450 | 72.61% |
| NEVER_STRONG | 92 | 69 | 0/92 | 89 | 0.8100 | 2.0233 | 2.2800 | 3.1137 | 0.6498 | -0.7900 | 96.74% |

Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.

| Group | n | 0.25/0.25 | 0.50/0.25 | 0.75/0.25 | 1.00/0.25 | 0.50/0.30 | 0.75/0.30 | 1.00/0.30 | 1.50/0.30 | 2.00/0.30 |
|---|---|---|---|---|---|---|---|---|---|---|
| EVENTUAL_STRONG | 241 | 58.51% | 50.21% | 39.42% | 32.37% | 55.19% | 43.57% | 36.51% | 27.39% | 22.82% |
| NEVER_STRONG | 92 | 21.74% | 5.43% | 3.26% | 0.00% | 5.43% | 3.26% | 0.00% | 0.00% | 0.00% |


### FIRST_EXECUTABLE_MINUTE_OPEN_V1: SHORT continuous


| feature | pre_reclaim_mfe: r (n) | pre_reclaim_mae: r (n) | 0.25/0.25: r (n) | 0.50/0.25: r (n) | 0.50/0.30: r (n) | 1.00/0.30: r (n) |
|---|---|---|---|---|---|---|
| opening_range_width | 0.1760 (330) | 0.2528 (330) | 0.0684 (304) | 0.0124 (324) | 0.0383 (326) | 0.0749 (330) |
| body_size | 0.2560 (330) | 0.5486 (330) | 0.0243 (304) | -0.0206 (324) | -0.0113 (326) | 0.0508 (330) |
| directional_body | 0.2560 (330) | 0.5486 (330) | 0.0242 (304) | -0.0207 (324) | -0.0114 (326) | 0.0506 (330) |
| candle_range | 0.2521 (330) | 0.5988 (330) | 0.0184 (304) | -0.0314 (324) | -0.0232 (326) | 0.0541 (330) |
| body_range_ratio | 0.1286 (330) | 0.2151 (330) | 0.0040 (304) | -0.0118 (324) | -0.0157 (326) | 0.0045 (330) |
| directional_body_range_ratio | 0.1286 (330) | 0.2151 (330) | 0.0032 (304) | -0.0128 (324) | -0.0166 (326) | 0.0032 (330) |
| close_location | -0.0014 (330) | -0.1984 (330) | 0.0961 (304) | 0.0813 (324) | 0.0967 (326) | 0.0859 (330) |
| directional_close_location | 0.0014 (330) | 0.1984 (330) | -0.0961 (304) | -0.0813 (324) | -0.0967 (326) | -0.0859 (330) |
| distance_beyond_level | 0.2242 (330) | 0.5763 (330) | 0.0445 (304) | 0.0549 (324) | 0.0490 (326) | 0.1024 (330) |
| distance_beyond_level_atr14 | 0.1066 (182) | 0.3657 (182) | 0.0339 (172) | 0.0290 (181) | 0.0096 (181) | 0.0913 (182) |
| candle_volume | 0.1373 (330) | 0.3927 (330) | 0.0214 (304) | 0.0037 (324) | -0.0002 (326) | 0.0470 (330) |
| relative_volume_prior_6 | -0.0186 (232) | 0.0335 (232) | 0.0204 (217) | -0.0237 (228) | -0.0172 (230) | 0.0293 (232) |
| atr14 | 0.3435 (182) | 0.4890 (182) | 0.0509 (172) | -0.0242 (181) | -0.0157 (181) | 0.0945 (182) |
| minutes_since_open | -0.0872 (330) | -0.3362 (330) | 0.1275 (304) | 0.0673 (324) | 0.0634 (326) | -0.0381 (330) |
| minutes_since_ema_cross | -0.0626 (119) | -0.2113 (119) | 0.0220 (113) | -0.0632 (119) | 0.0022 (119) | -0.1069 (119) |
| break_attempt_rank | -0.0404 (330) | -0.2865 (330) | 0.1240 (304) | 0.1064 (324) | 0.0924 (326) | -0.0196 (330) |
| valid_hold_sequence_rank | -0.0597 (330) | -0.2816 (330) | 0.0790 (304) | 0.0699 (324) | 0.0551 (326) | -0.0401 (330) |
| stage10_9.ema9_ema20_absolute_separation | 0.0714 (153) | 0.2752 (153) | 0.1211 (144) | -0.0525 (152) | -0.0366 (152) | -0.0160 (153) |
| stage10_9.ema9_ema20_separation_atr14 | -0.0775 (153) | 0.1134 (153) | 0.0414 (144) | -0.0890 (152) | -0.0746 (152) | -0.0893 (153) |
| stage10_9.ema9_slope_1_bars | -0.0665 (208) | -0.4190 (208) | 0.0538 (196) | 0.0909 (205) | 0.0847 (206) | 0.0015 (208) |
| stage10_9.ema9_slope_2_bars | -0.0220 (200) | -0.2442 (200) | 0.0486 (188) | 0.0765 (197) | 0.0760 (198) | 0.0081 (200) |
| stage10_9.ema9_slope_3_bars | 0.0092 (192) | -0.2013 (192) | 0.0402 (180) | 0.0746 (189) | 0.0645 (190) | -0.0111 (192) |
| stage10_9.ema20_slope_1_bars | -0.0293 (145) | -0.4028 (145) | -0.0196 (136) | 0.0619 (144) | 0.0696 (144) | -0.0360 (145) |
| stage10_9.ema20_slope_2_bars | -0.0189 (142) | -0.2745 (142) | -0.0026 (134) | 0.0768 (141) | 0.0803 (141) | 0.0109 (142) |
| stage10_9.ema20_slope_3_bars | 0.0258 (137) | -0.2829 (137) | 0.0261 (129) | 0.1009 (136) | 0.1018 (136) | 0.0227 (137) |
| stage10_9.vwap_slope_1_bars | -0.0780 (330) | -0.4130 (330) | 0.0507 (304) | 0.0372 (324) | 0.0327 (326) | -0.0312 (330) |
| stage10_9.vwap_slope_2_bars | -0.0266 (297) | -0.3453 (297) | 0.0517 (272) | 0.0423 (291) | 0.0222 (293) | -0.0395 (297) |
| stage10_9.vwap_slope_3_bars | -0.0208 (272) | -0.3245 (272) | 0.0862 (255) | 0.0578 (268) | 0.0004 (270) | -0.0918 (272) |
| stage10_9.ema9_ema20_cross_count_6_bars | -0.0190 (132) | 0.1177 (132) | -0.0112 (125) | 0.0580 (131) | 0.0199 (131) | -0.0137 (132) |
| stage10_9.ema9_ema20_cross_count_12_bars | 0.0336 (114) | 0.1289 (114) | -0.0234 (109) | 0.0831 (114) | 0.0446 (114) | 0.1470 (114) |
| stage10_9.ema9_ema20_cross_count_24_bars | 0.0722 (78) | 0.0571 (78) | 0.1350 (76) | 0.1620 (78) | 0.1178 (78) | 0.2003 (78) |
| stage10_9.ema9_vwap_cross_count_6_bars | 0.0434 (182) | 0.0631 (182) | 0.0619 (172) | 0.0567 (181) | 0.0530 (181) | -0.0659 (182) |
| stage10_9.ema9_vwap_cross_count_12_bars | 0.0500 (153) | 0.0296 (153) | 0.0841 (144) | 0.0882 (152) | 0.0771 (152) | -0.0352 (153) |
| stage10_9.ema9_vwap_cross_count_24_bars | 0.0733 (113) | 0.0565 (113) | -0.0568 (108) | -0.0201 (113) | -0.0399 (113) | -0.0449 (113) |
| stage10_9.ema20_vwap_cross_count_6_bars | 0.0260 (132) | 0.1307 (132) | -0.0445 (125) | -0.0646 (131) | -0.0537 (131) | 0.0283 (132) |
| stage10_9.ema20_vwap_cross_count_12_bars | 0.0345 (114) | 0.0966 (114) | -0.0358 (109) | -0.0365 (114) | -0.0485 (114) | -0.0477 (114) |
| stage10_9.ema20_vwap_cross_count_24_bars | 0.0356 (78) | 0.0604 (78) | -0.0623 (76) | 0.0390 (78) | 0.0187 (78) | 0.1366 (78) |
| stage10_9.price_vwap_side_change_count_6_bars | 0.1516 (244) | 0.0776 (244) | -0.0317 (228) | 0.0430 (240) | 0.0145 (242) | 0.0551 (244) |
| stage10_9.price_vwap_side_change_count_12_bars | 0.1636 (192) | 0.0889 (192) | -0.0019 (180) | 0.0911 (189) | 0.0812 (190) | 0.0995 (192) |
| stage10_9.price_vwap_side_change_count_24_bars | 0.1423 (136) | 0.0108 (136) | 0.0671 (128) | 0.1654 (135) | 0.1214 (135) | 0.0625 (136) |
| stage10_9.rolling_high_low_range_6_bars | 0.2761 (244) | 0.5314 (244) | 0.0787 (228) | 0.0217 (240) | 0.0298 (242) | 0.1112 (244) |
| stage10_9.rolling_high_low_range_12_bars | 0.2741 (192) | 0.4916 (192) | 0.1247 (180) | -0.0042 (189) | 0.0225 (190) | 0.0977 (192) |
| stage10_9.rolling_high_low_range_24_bars | 0.2162 (136) | 0.4057 (136) | 0.1574 (128) | -0.0109 (135) | -0.0067 (135) | 0.0392 (136) |
| stage10_9.rolling_range_atr14_6_bars | 0.0178 (182) | 0.0858 (182) | 0.1662 (172) | 0.0808 (181) | 0.0611 (181) | 0.1209 (182) |
| stage10_9.rolling_range_atr14_12_bars | -0.0582 (182) | 0.1330 (182) | 0.1033 (172) | -0.0207 (181) | -0.0001 (181) | 0.0403 (182) |
| stage10_9.rolling_range_atr14_24_bars | -0.0942 (136) | 0.0599 (136) | 0.0481 (128) | -0.1005 (135) | -0.0788 (135) | -0.1021 (136) |
| stage10_9.directional_efficiency_6_bars | -0.0048 (244) | -0.0469 (244) | 0.0186 (228) | 0.0027 (240) | -0.0032 (242) | 0.0451 (244) |
| stage10_9.directional_efficiency_12_bars | -0.0833 (192) | 0.0656 (192) | -0.0001 (180) | -0.0288 (189) | -0.0330 (190) | 0.0151 (192) |
| stage10_9.directional_efficiency_24_bars | -0.0980 (136) | 0.1201 (136) | 0.0086 (128) | -0.1063 (135) | -0.0801 (135) | -0.0648 (136) |
| stage10_9.range_overlap_fraction_6_bars | 0.0590 (244) | 0.0410 (244) | 0.0108 (228) | 0.0768 (240) | 0.0813 (242) | 0.0548 (244) |
| stage10_9.range_overlap_fraction_12_bars | 0.0080 (192) | 0.0235 (192) | -0.0249 (180) | 0.0231 (189) | 0.0317 (190) | -0.0177 (192) |
| stage10_9.range_overlap_fraction_24_bars | -0.0070 (136) | 0.0121 (136) | -0.0230 (128) | 0.0315 (135) | 0.0403 (135) | -0.0234 (136) |
| stage10_9.close_direction_alternation_fraction_6_bars | -0.0449 (244) | 0.0326 (244) | -0.0524 (228) | -0.0087 (240) | 0.0263 (242) | -0.0437 (244) |
| stage10_9.close_direction_alternation_fraction_12_bars | 0.0425 (192) | 0.0870 (192) | -0.1358 (180) | -0.0493 (189) | -0.0661 (190) | 0.0594 (192) |
| stage10_9.close_direction_alternation_fraction_24_bars | 0.0064 (136) | -0.0387 (136) | -0.0125 (128) | 0.0373 (135) | -0.0301 (135) | 0.0372 (136) |
| stage10_9.confirmation_close_vwap_distance_atr14 | -0.2114 (182) | 0.0926 (182) | -0.0810 (172) | -0.1282 (181) | -0.1251 (181) | -0.0742 (182) |
| stage10_9.ema9_vwap_distance_atr14 | -0.1479 (182) | -0.0107 (182) | -0.0380 (172) | -0.0848 (181) | -0.0435 (181) | -0.0543 (182) |
| stage10_9.ema20_vwap_distance_atr14 | -0.1866 (153) | -0.0991 (153) | -0.0390 (144) | -0.0736 (152) | -0.0267 (152) | -0.0200 (153) |
| stage11_2.room_from_confirmation | 0.1236 (284) | 0.1708 (284) | -0.0634 (261) | -0.0185 (278) | 0.0241 (280) | 0.0628 (284) |
| stage11_2.room_in_atr | 0.0876 (153) | -0.0124 (153) | 0.0428 (143) | 0.0311 (152) | 0.0903 (152) | 0.1541 (153) |
| stage11_2.number_of_known_levels_above | 0.0844 (330) | 0.0750 (330) | 0.0318 (304) | 0.0473 (324) | 0.0188 (326) | 0.0695 (330) |
| stage11_2.number_of_known_levels_below | -0.0959 (330) | -0.0625 (330) | -0.0421 (304) | -0.0602 (324) | -0.0308 (326) | -0.0864 (330) |
| stage11_2.nearest_level_distance_above | 0.1752 (330) | 0.5323 (330) | 0.0409 (304) | 0.0486 (324) | 0.0465 (326) | 0.1058 (330) |
| stage11_2.nearest_level_distance_below | 0.1236 (284) | 0.1708 (284) | -0.0634 (261) | -0.0185 (278) | 0.0241 (280) | 0.0628 (284) |
| stage11_2.directional_level_count_within_0_5_atr | -0.0552 (182) | 0.0016 (182) | 0.0125 (172) | 0.0219 (181) | -0.0076 (181) | -0.1064 (182) |
| stage11_2.directional_level_count_within_1_0_atr | -0.0446 (182) | -0.0168 (182) | 0.0077 (172) | 0.0005 (181) | -0.0413 (181) | -0.1466 (182) |
| stage11_3.confirmation_close_to_latest_swing_high | 0.2207 (231) | 0.4452 (231) | 0.0264 (215) | -0.0475 (227) | -0.0113 (229) | 0.0866 (231) |
| stage11_3.confirmation_close_to_latest_swing_low | 0.0522 (222) | 0.2587 (222) | 0.1159 (207) | 0.0473 (219) | 0.0386 (220) | 0.0918 (222) |
| stage11_3.distance_to_swing_high_in_atr | -0.0343 (182) | 0.1360 (182) | -0.0032 (172) | -0.0900 (181) | -0.0907 (181) | -0.0031 (182) |
| stage11_3.distance_to_swing_low_in_atr | -0.0811 (178) | 0.0031 (178) | 0.1220 (168) | 0.0229 (177) | 0.0411 (177) | 0.0532 (178) |


### FIRST_EXECUTABLE_MINUTE_OPEN_V1: SHORT categorical


| feature | category | n | sessions | pre-reclaim MFE n/mean/median | pre-reclaim MAE n/mean/median | 0.25/0.25 | 0.50/0.25 | 0.50/0.30 | 1.00/0.30 | ambiguous n across four pairs | no future n across four pairs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| direction | SHORT | 333 | 129 | 330/1.6412/0.7425 | 330/0.8712/0.6900 | 48.35% | 37.84% | 41.44% | 26.43% | 26/6/4/0 | 3/3/3/3 |
| time_bucket | 09:35-10:00 | 86 | 74 | 86/2.1486/0.7935 | 86/1.1016/0.9068 | 39.53% | 31.40% | 36.05% | 26.74% | 10/2/2/0 | 0/0/0/0 |
| time_bucket | 10:00-10:30 | 52 | 48 | 52/1.6397/0.8750 | 52/1.0080/0.8350 | 46.15% | 36.54% | 38.46% | 25.00% | 4/1/0/0 | 0/0/0/0 |
| time_bucket | 10:30-11:00 | 33 | 26 | 33/1.7182/0.9050 | 33/0.8799/0.6900 | 48.48% | 36.36% | 39.39% | 24.24% | 2/2/1/0 | 0/0/0/0 |
| time_bucket | 11:00-12:00 | 38 | 28 | 38/1.5253/0.7650 | 38/0.7770/0.5850 | 44.74% | 39.47% | 44.74% | 28.95% | 5/1/1/0 | 0/0/0/0 |
| time_bucket | 12:00-13:30 | 53 | 35 | 53/1.6878/0.6500 | 53/0.7823/0.5900 | 54.72% | 47.17% | 50.94% | 35.85% | 3/0/0/0 | 0/0/0/0 |
| time_bucket | 13:30-15:00 | 35 | 30 | 35/1.1728/0.9000 | 35/0.6853/0.4650 | 57.14% | 42.86% | 45.71% | 28.57% | 1/0/0/0 | 0/0/0/0 |
| time_bucket | 15:00-close | 36 | 26 | 33/0.8002/0.4300 | 33/0.4951/0.3900 | 58.33% | 36.11% | 38.89% | 11.11% | 1/0/0/0 | 3/3/3/3 |
| ema9_20_alignment | EMA_ALIGNED | 112 | 54 | 110/1.2224/0.5375 | 110/0.7236/0.5200 | 53.57% | 41.96% | 43.75% | 25.89% | 7/1/1/0 | 2/2/2/2 |
| ema9_20_alignment | EMA_NOT_ALIGNED | 44 | 28 | 43/1.5418/0.9800 | 43/0.5754/0.4800 | 54.55% | 43.18% | 47.73% | 27.27% | 2/0/0/0 | 1/1/1/1 |
| ema9_20_alignment | EMA_UNAVAILABLE | 177 | 109 | 177/1.9257/0.9000 | 177/1.0348/0.8500 | 43.50% | 33.90% | 38.42% | 26.55% | 17/5/3/0 | 0/0/0/0 |
| price_vwap_alignment | VWAP_ALIGNED | 300 | 129 | 298/1.6529/0.7425 | 298/0.8999/0.7150 | 46.00% | 36.00% | 39.33% | 26.00% | 24/6/4/0 | 2/2/2/2 |
| price_vwap_alignment | VWAP_NOT_ALIGNED | 33 | 20 | 32/1.5326/0.8125 | 32/0.6044/0.4800 | 69.70% | 54.55% | 60.61% | 30.30% | 2/0/0/0 | 1/1/1/1 |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED | 157 | 71 | 155/1.4593/0.7700 | 155/0.7564/0.5800 | 49.68% | 39.49% | 42.68% | 27.39% | 10/2/1/0 | 2/2/2/2 |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED | 63 | 40 | 62/1.6618/0.7225 | 62/0.7380/0.5850 | 58.73% | 44.44% | 47.62% | 22.22% | 3/1/1/0 | 1/1/1/1 |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE | 113 | 87 | 113/1.8795/0.7500 | 113/1.1018/0.8900 | 40.71% | 31.86% | 36.28% | 27.43% | 13/3/2/0 | 0/0/0/0 |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED | 101 | 48 | 99/1.3912/0.5550 | 99/0.7263/0.5100 | 52.48% | 41.58% | 44.55% | 27.72% | 6/1/1/0 | 2/2/2/2 |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED | 55 | 41 | 54/1.1673/0.5825 | 54/0.6005/0.4800 | 56.36% | 43.64% | 45.45% | 23.64% | 3/0/0/0 | 1/1/1/1 |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 177 | 109 | 177/1.9257/0.9000 | 177/1.0348/0.8500 | 43.50% | 33.90% | 38.42% | 26.55% | 17/5/3/0 | 0/0/0/0 |
| prior_ema_cross | MATCHING_CROSS | 84 | 43 | 82/1.0459/0.4700 | 82/0.7203/0.4750 | 54.76% | 41.67% | 44.05% | 23.81% | 4/0/0/0 | 2/2/2/2 |
| prior_ema_cross | NO_PRIOR_CROSS | 211 | 117 | 211/1.9220/0.9000 | 211/0.9847/0.8100 | 44.55% | 35.55% | 39.34% | 27.96% | 20/6/4/0 | 0/0/0/0 |
| prior_ema_cross | OPPOSING_CROSS | 38 | 24 | 37/1.3595/0.5400 | 37/0.5587/0.4800 | 55.26% | 42.11% | 47.37% | 23.68% | 2/0/0/0 | 1/1/1/1 |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 224 | 94 | 222/1.6689/0.8325 | 222/0.8316/0.6525 | 50.45% | 39.73% | 43.30% | 27.23% | 21/4/2/0 | 2/2/2/2 |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL | 108 | 56 | 107/1.5991/0.6700 | 107/0.9538/0.7350 | 44.44% | 34.26% | 37.96% | 25.00% | 5/2/2/0 | 1/1/1/1 |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 1 | 1 | 1/0.0100/0.0100 | 1/0.8200/0.8200 | 0.00% | 0.00% | 0.00% | 0.00% | 0/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 26 | 20 | 26/1.3507/0.7275 | 26/0.9223/0.4575 | 53.85% | 38.46% | 38.46% | 23.08% | 3/1/1/0 | 0/0/0/0 |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 16 | 12 | 16/1.8275/0.6025 | 16/0.5950/0.5424 | 50.00% | 37.50% | 50.00% | 31.25% | 2/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 21 | 16 | 19/1.0955/0.5400 | 19/0.6916/0.5800 | 33.33% | 23.81% | 23.81% | 14.29% | 2/0/0/0 | 2/2/2/2 |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 27 | 21 | 27/2.1889/1.2780 | 27/0.6331/0.5950 | 62.96% | 55.56% | 59.26% | 48.15% | 0/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | GT_3_0_ATR | 34 | 16 | 33/1.3462/0.5100 | 33/0.6442/0.5600 | 50.00% | 38.24% | 44.12% | 29.41% | 3/0/0/0 | 1/1/1/1 |
| stage11_2.room_bucket | LT_0_5_ATR | 32 | 21 | 32/1.0182/0.6275 | 32/0.6537/0.5375 | 53.12% | 40.62% | 40.62% | 15.62% | 0/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | OPEN_ENDED | 46 | 15 | 46/1.1890/0.7200 | 46/0.9427/0.7320 | 54.35% | 41.30% | 43.48% | 26.09% | 3/0/0/0 | 0/0/0/0 |
| stage11_2.room_bucket | UNAVAILABLE_ATR | 131 | 95 | 131/2.0278/0.8500 | 131/1.0551/0.8700 | 42.75% | 34.35% | 38.93% | 25.95% | 13/5/3/0 | 0/0/0/0 |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 332 | 128 | 329/1.6325/0.7350 | 329/0.8731/0.6900 | 48.19% | 37.65% | 41.27% | 26.20% | 26/6/4/0 | 3/3/3/3 |
| known_level_coverage | PARTIAL_UNAVAILABLE [SMALL] | 1 | 1 | 1/4.5200/4.5200 | 1/0.2500/0.2500 | 100.00% | 100.00% | 100.00% | 100.00% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.structure | BEARISH_STRUCTURE | 55 | 42 | 55/1.2898/0.8150 | 55/0.6609/0.5250 | 54.55% | 41.82% | 45.45% | 30.91% | 3/1/1/0 | 0/0/0/0 |
| stage11_3.structure | BULLISH_STRUCTURE | 41 | 33 | 41/1.2384/0.5450 | 41/0.6981/0.5300 | 60.98% | 46.34% | 48.78% | 19.51% | 1/0/0/0 | 0/0/0/0 |
| stage11_3.structure | MIXED_STRUCTURE | 68 | 43 | 65/1.5077/0.7200 | 65/0.7180/0.5400 | 50.00% | 42.65% | 47.06% | 30.88% | 6/1/0/0 | 3/3/3/3 |
| stage11_3.structure | UNAVAILABLE | 169 | 110 | 169/1.9047/0.8300 | 169/1.0406/0.8600 | 42.60% | 32.54% | 36.09% | 24.85% | 16/4/3/0 | 0/0/0/0 |
| stage11_3.agreement | STRUCTURE_ALIGNED | 55 | 42 | 55/1.2898/0.8150 | 55/0.6609/0.5250 | 54.55% | 41.82% | 45.45% | 30.91% | 3/1/1/0 | 0/0/0/0 |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED | 109 | 58 | 106/1.4035/0.6700 | 106/0.7103/0.5350 | 54.13% | 44.04% | 47.71% | 26.61% | 7/1/0/0 | 3/3/3/3 |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 169 | 110 | 169/1.9047/0.8300 | 169/1.0406/0.8600 | 42.60% | 32.54% | 36.09% | 24.85% | 16/4/3/0 | 0/0/0/0 |
| stage11_3.high_structure | EQUAL_HIGH [SMALL] | 3 | 2 | 3/0.8333/0.7200 | 3/1.0800/0.7400 | 66.67% | 66.67% | 66.67% | 0.00% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.high_structure | HIGHER_HIGH | 71 | 49 | 70/1.3632/0.8275 | 70/0.7166/0.5100 | 56.34% | 43.66% | 47.89% | 23.94% | 4/0/0/0 | 1/1/1/1 |
| stage11_3.high_structure | LOWER_HIGH | 113 | 61 | 111/1.3781/0.6250 | 111/0.7114/0.5400 | 47.79% | 38.05% | 41.59% | 28.32% | 7/2/1/0 | 2/2/2/2 |
| stage11_3.high_structure | UNAVAILABLE | 146 | 100 | 146/1.9912/0.8434 | 146/1.0626/0.8800 | 44.52% | 34.25% | 37.67% | 26.71% | 15/4/3/0 | 0/0/0/0 |
| stage11_3.low_structure | EQUAL_LOW [SMALL] | 2 | 1 | 2/0.3000/0.3000 | 2/0.7200/0.7200 | 0.00% | 0.00% | 0.00% | 0.00% | 0/0/0/0 | 0/0/0/0 |
| stage11_3.low_structure | HIGHER_LOW | 92 | 54 | 90/1.4386/0.6375 | 90/0.7651/0.5850 | 55.43% | 44.57% | 47.83% | 25.00% | 5/1/0/0 | 2/2/2/2 |
| stage11_3.low_structure | LOWER_LOW | 75 | 53 | 74/1.3349/0.8325 | 74/0.6331/0.4850 | 54.67% | 42.67% | 46.67% | 30.67% | 5/1/1/0 | 1/1/1/1 |
| stage11_3.low_structure | UNAVAILABLE | 164 | 110 | 164/1.9070/0.8102 | 164/1.0387/0.8500 | 42.07% | 32.32% | 35.98% | 25.61% | 16/4/3/0 | 0/0/0/0 |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE | 108 | 91 | 108/2.0339/0.7425 | 108/1.1044/0.8835 | 38.89% | 30.56% | 34.26% | 25.00% | 11/3/2/0 | 0/0/0/0 |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED | 37 | 15 | 37/1.2546/0.6500 | 37/0.8692/0.5950 | 59.46% | 43.24% | 45.95% | 27.03% | 2/0/0/0 | 0/0/0/0 |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL | 42 | 26 | 41/1.4282/0.7300 | 41/0.6871/0.4900 | 52.38% | 40.48% | 42.86% | 19.05% | 1/0/0/0 | 1/1/1/1 |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL | 146 | 78 | 144/1.5067/0.8250 | 144/0.7492/0.5900 | 51.37% | 41.10% | 45.21% | 29.45% | 12/3/2/0 | 2/2/2/2 |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 333 | 129 | 330/1.6412/0.7425 | 330/0.8712/0.6900 | 48.35% | 37.84% | 41.44% | 26.43% | 26/6/4/0 | 3/3/3/3 |


## Complete monthly stability: ALL

Every feature is shown, not only those selected for the decision summary. Monthly intervals are not estimated. Monthly medians, quartiles, mean differences and category denominators remain explicit. September contains only four sessions.

### 2026-01


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 62/62 (20 sessions) | 1.1159 | 0.9850 | 0.7350 | 1.3075 | 23/23 (12 sessions) | 1.1646 | 1.0600 | 0.8500 | 1.3200 | -0.0487 | -0.1156 | not resampled |
| body_size [SMALL] | 62/62 (20 sessions) | 0.6418 | 0.5450 | 0.3625 | 0.8712 | 23/23 (12 sessions) | 0.6272 | 0.5300 | 0.3700 | 0.7425 | 0.0147 | 0.0371 | not resampled |
| directional_body [SMALL] | 62/62 (20 sessions) | 0.6418 | 0.5450 | 0.3625 | 0.8712 | 23/23 (12 sessions) | 0.6272 | 0.5300 | 0.3700 | 0.7425 | 0.0147 | 0.0371 | not resampled |
| candle_range [SMALL] | 62/62 (20 sessions) | 0.9159 | 0.8450 | 0.6112 | 1.1850 | 23/23 (12 sessions) | 1.0703 | 0.9199 | 0.7200 | 1.4250 | -0.1544 | -0.3366 | not resampled |
| body_range_ratio [SMALL] | 62/62 (20 sessions) | 0.6798 | 0.7105 | 0.5415 | 0.8237 | 23/23 (12 sessions) | 0.5782 | 0.5922 | 0.4489 | 0.6831 | 0.1017 | 0.5567 | not resampled |
| directional_body_range_ratio [SMALL] | 62/62 (20 sessions) | 0.6798 | 0.7105 | 0.5415 | 0.8237 | 23/23 (12 sessions) | 0.5782 | 0.5922 | 0.4489 | 0.6831 | 0.1017 | 0.5567 | not resampled |
| close_location [SMALL] | 62/62 (20 sessions) | 0.6056 | 0.7648 | 0.2502 | 0.9005 | 23/23 (12 sessions) | 0.4069 | 0.2135 | 0.0938 | 0.8406 | 0.1987 | 0.5625 | not resampled |
| directional_close_location [SMALL] | 62/62 (20 sessions) | 0.8312 | 0.8723 | 0.7623 | 0.9259 | 23/23 (12 sessions) | 0.8520 | 0.9059 | 0.8058 | 0.9530 | -0.0208 | -0.1499 | not resampled |
| distance_beyond_level [SMALL] | 62/62 (20 sessions) | 0.3105 | 0.2640 | 0.1062 | 0.4225 | 23/23 (12 sessions) | 0.2398 | 0.1550 | 0.1000 | 0.2900 | 0.0708 | 0.2872 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 36/62 (12 sessions) | 0.4939 | 0.4162 | 0.1304 | 0.7381 | 9/23 (6 sessions) | 0.2366 | 0.1984 | 0.0701 | 0.2639 | 0.2573 | 0.6727 | not resampled |
| candle_volume [SMALL] | 62/62 (20 sessions) | 984039.1774 | 826765.5000 | 611341.2500 | 1279424.7500 | 23/23 (12 sessions) | 1512776.5652 | 1065423.0000 | 931136.0000 | 1835864.0000 | -528737.3878 | -0.6999 | not resampled |
| relative_volume_prior_6 [SMALL] | 46/62 (15 sessions) | 0.9927 | 0.9659 | 0.6997 | 1.2098 | 14/23 (8 sessions) | 1.4060 | 0.9272 | 0.8372 | 1.0977 | -0.4133 | -0.5927 | not resampled |
| atr14 [SMALL] | 36/62 (12 sessions) | 0.7052 | 0.6670 | 0.4585 | 0.9156 | 9/23 (6 sessions) | 0.7057 | 0.6803 | 0.4922 | 1.0136 | -0.0005 | -0.0019 | not resampled |
| minutes_since_open [SMALL] | 62/62 (20 sessions) | 139.2742 | 105.0000 | 31.2500 | 243.7500 | 23/23 (12 sessions) | 109.5652 | 45.0000 | 15.0000 | 205.0000 | 29.7090 | 0.2518 | not resampled |
| minutes_since_ema_cross [SMALL] | 20/62 (11 sessions) | 50.7500 | 50.0000 | 23.7500 | 66.2500 | 6/23 (5 sessions) | 41.6667 | 25.0000 | 17.5000 | 62.5000 | 9.0833 | 0.2446 | not resampled |
| break_attempt_rank [SMALL] | 62/62 (20 sessions) | 8.4839 | 7.5000 | 3.0000 | 13.0000 | 23/23 (12 sessions) | 6.5217 | 5.0000 | 2.0000 | 10.0000 | 1.9621 | 0.3329 | not resampled |
| valid_hold_sequence_rank [SMALL] | 62/62 (20 sessions) | 3.8387 | 3.5000 | 2.0000 | 5.7500 | 23/23 (12 sessions) | 2.9565 | 2.0000 | 1.0000 | 4.0000 | 0.8822 | 0.3791 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 32/62 (12 sessions) | 0.2267 | 0.2144 | 0.0991 | 0.2950 | 8/23 (6 sessions) | 0.3043 | 0.1529 | 0.0931 | 0.4362 | -0.0775 | -0.3886 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 32/62 (12 sessions) | 0.3494 | 0.3487 | 0.1385 | 0.5239 | 8/23 (6 sessions) | 0.3777 | 0.3149 | 0.1564 | 0.5455 | -0.0283 | -0.1166 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 40/62 (12 sessions) | 0.0215 | 0.0337 | -0.0747 | 0.1162 | 11/23 (7 sessions) | -0.0736 | -0.0127 | -0.1066 | 0.0180 | 0.0952 | 0.6575 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 39/62 (12 sessions) | -0.0056 | 0.0080 | -0.0706 | 0.0543 | 10/23 (6 sessions) | -0.0335 | -0.0372 | -0.0636 | 0.0300 | 0.0279 | 0.2440 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 36/62 (12 sessions) | -0.0160 | -0.0052 | -0.0693 | 0.0447 | 10/23 (6 sessions) | -0.0453 | -0.0254 | -0.0539 | 0.0228 | 0.0293 | 0.2746 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 31/62 (11 sessions) | -0.0037 | 0.0064 | -0.0416 | 0.0473 | 8/23 (6 sessions) | -0.0641 | -0.0090 | -0.0763 | 0.0032 | 0.0603 | 0.7387 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 31/62 (11 sessions) | -0.0115 | -0.0139 | -0.0567 | 0.0282 | 8/23 (6 sessions) | -0.0492 | -0.0268 | -0.0753 | -0.0037 | 0.0377 | 0.5300 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 29/62 (11 sessions) | -0.0119 | -0.0160 | -0.0559 | 0.0195 | 8/23 (6 sessions) | -0.0500 | -0.0273 | -0.0653 | -0.0134 | 0.0381 | 0.5603 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 62/62 (20 sessions) | 0.0185 | 0.0032 | -0.0127 | 0.0280 | 23/23 (12 sessions) | -0.0457 | -0.0208 | -0.1077 | 0.0070 | 0.0642 | 0.5974 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 58/62 (17 sessions) | 0.0019 | 0.0019 | -0.0173 | 0.0162 | 20/23 (11 sessions) | -0.0270 | -0.0211 | -0.0598 | 0.0130 | 0.0289 | 0.5434 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 55/62 (16 sessions) | -0.0024 | 0.0014 | -0.0156 | 0.0151 | 16/23 (9 sessions) | -0.0234 | -0.0132 | -0.0606 | 0.0046 | 0.0210 | 0.5090 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 29/62 (11 sessions) | 0.2069 | 0.0000 | 0.0000 | 0.0000 | 8/23 (6 sessions) | 0.2500 | 0.0000 | 0.0000 | 0.2500 | -0.0431 | -0.0887 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 23/62 (11 sessions) | 0.5217 | 0.0000 | 0.0000 | 1.0000 | 8/23 (6 sessions) | 0.6250 | 0.5000 | 0.0000 | 1.0000 | -0.1033 | -0.1407 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 20/62 (10 sessions) | 1.1000 | 1.0000 | 1.0000 | 1.0000 | 6/23 (6 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.1000 | 0.1232 | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 36/62 (12 sessions) | 0.3889 | 0.0000 | 0.0000 | 1.0000 | 9/23 (6 sessions) | 0.4444 | 0.0000 | 0.0000 | 1.0000 | -0.0556 | -0.0948 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 32/62 (12 sessions) | 0.6250 | 0.0000 | 0.0000 | 1.0000 | 8/23 (6 sessions) | 0.2500 | 0.0000 | 0.0000 | 0.2500 | 0.3750 | 0.5044 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 23/62 (11 sessions) | 0.6957 | 1.0000 | 0.0000 | 1.0000 | 8/23 (6 sessions) | 0.8750 | 1.0000 | 0.7500 | 1.0000 | -0.1793 | -0.3094 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 29/62 (11 sessions) | 0.1379 | 0.0000 | 0.0000 | 0.0000 | 8/23 (6 sessions) | 0.1250 | 0.0000 | 0.0000 | 0.0000 | 0.0129 | 0.0368 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 23/62 (11 sessions) | 0.3478 | 0.0000 | 0.0000 | 1.0000 | 8/23 (6 sessions) | 0.5000 | 0.0000 | 0.0000 | 0.2500 | -0.1522 | -0.2254 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 20/62 (10 sessions) | 0.4000 | 0.0000 | 0.0000 | 1.0000 | 6/23 (6 sessions) | 0.6667 | 0.0000 | 0.0000 | 0.7500 | -0.2667 | -0.3750 | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 48/62 (15 sessions) | 1.0625 | 1.0000 | 0.0000 | 2.0000 | 15/23 (9 sessions) | 0.9333 | 1.0000 | 0.0000 | 2.0000 | 0.1292 | 0.1159 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 36/62 (12 sessions) | 1.6389 | 1.5000 | 0.0000 | 3.0000 | 10/23 (6 sessions) | 1.6000 | 1.0000 | 0.2500 | 2.0000 | 0.0389 | 0.0257 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 29/62 (11 sessions) | 2.6207 | 2.0000 | 1.0000 | 4.0000 | 8/23 (6 sessions) | 1.6250 | 1.0000 | 1.0000 | 2.2500 | 0.9957 | 0.5599 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 48/62 (15 sessions) | 1.6478 | 1.5800 | 1.2600 | 1.9612 | 15/23 (9 sessions) | 2.0539 | 2.1600 | 1.2950 | 2.6140 | -0.4061 | -0.5843 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 36/62 (12 sessions) | 2.0410 | 1.8825 | 1.5801 | 2.4662 | 10/23 (6 sessions) | 2.3551 | 1.7250 | 1.3075 | 2.7850 | -0.3142 | -0.3237 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 29/62 (11 sessions) | 2.9119 | 2.3000 | 1.8250 | 3.6600 | 8/23 (6 sessions) | 3.4489 | 2.7700 | 1.6825 | 4.3222 | -0.5370 | -0.3224 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 36/62 (12 sessions) | 2.2457 | 2.1546 | 1.8305 | 2.6426 | 9/23 (6 sessions) | 2.5369 | 2.4285 | 2.1568 | 3.1524 | -0.2912 | -0.4519 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 36/62 (12 sessions) | 3.0233 | 2.9190 | 2.4647 | 3.5406 | 9/23 (6 sessions) | 3.2638 | 2.9764 | 2.5397 | 3.4348 | -0.2405 | -0.2759 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 29/62 (11 sessions) | 4.2923 | 3.9703 | 3.6196 | 5.1172 | 8/23 (6 sessions) | 4.7191 | 4.5438 | 3.8686 | 5.2947 | -0.4267 | -0.4034 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 48/62 (15 sessions) | 0.4487 | 0.4139 | 0.2625 | 0.6406 | 15/23 (9 sessions) | 0.3309 | 0.2308 | 0.1049 | 0.4148 | 0.1177 | 0.4271 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 36/62 (12 sessions) | 0.2307 | 0.2155 | 0.1061 | 0.2937 | 10/23 (6 sessions) | 0.2396 | 0.1682 | 0.1238 | 0.2451 | -0.0089 | -0.0503 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 29/62 (11 sessions) | 0.1596 | 0.1310 | 0.0675 | 0.2065 | 8/23 (6 sessions) | 0.2133 | 0.2415 | 0.0556 | 0.3098 | -0.0537 | -0.4129 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 48/62 (15 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 15/23 (9 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 36/62 (12 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 10/23 (6 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 29/62 (11 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 8/23 (6 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 48/62 (15 sessions) | 0.5208 | 0.5000 | 0.2500 | 0.7500 | 15/23 (9 sessions) | 0.4333 | 0.5000 | 0.2500 | 0.5000 | 0.0875 | 0.3633 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 36/62 (12 sessions) | 0.5111 | 0.5000 | 0.4000 | 0.6000 | 10/23 (6 sessions) | 0.4900 | 0.4500 | 0.4000 | 0.6000 | 0.0211 | 0.1456 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 29/62 (11 sessions) | 0.5313 | 0.5000 | 0.4545 | 0.5909 | 8/23 (6 sessions) | 0.5114 | 0.4773 | 0.4545 | 0.5341 | 0.0200 | 0.1673 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 36/62 (12 sessions) | 1.0139 | 0.8321 | 0.5499 | 1.1740 | 9/23 (6 sessions) | 1.4145 | 0.8623 | 0.7542 | 2.4608 | -0.4006 | -0.4688 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 36/62 (12 sessions) | 0.7291 | 0.5658 | 0.3874 | 0.9447 | 9/23 (6 sessions) | 0.9509 | 0.6205 | 0.4795 | 1.2977 | -0.2218 | -0.3423 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 32/62 (12 sessions) | 0.6088 | 0.3768 | 0.1900 | 0.9619 | 8/23 (6 sessions) | 0.7689 | 0.4727 | 0.2914 | 0.8840 | -0.1600 | -0.2578 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 47/62 (17 sessions) | 2.0314 | 1.8250 | 0.6800 | 3.5750 | 19/23 (9 sessions) | 1.7739 | 2.0600 | 0.2895 | 2.4675 | 0.2576 | 0.1772 | not resampled |
| stage11_2.room_in_atr [SMALL] | 27/62 (10 sessions) | 3.5338 | 3.3292 | 2.3435 | 4.2545 | 6/23 (4 sessions) | 1.9037 | 1.9295 | 0.5797 | 2.8523 | 1.6300 | 0.6875 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 62/62 (20 sessions) | 2.0968 | 2.0000 | 1.0000 | 3.0000 | 23/23 (12 sessions) | 3.0870 | 4.0000 | 1.0000 | 4.5000 | -0.9902 | -0.5539 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 62/62 (20 sessions) | 3.8387 | 4.0000 | 2.2500 | 5.0000 | 23/23 (12 sessions) | 2.8696 | 2.0000 | 1.5000 | 5.0000 | 0.9691 | 0.5404 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 50/62 (18 sessions) | 1.3396 | 0.4568 | 0.1688 | 2.1675 | 20/23 (10 sessions) | 0.8158 | 0.2800 | 0.1050 | 0.8350 | 0.5238 | 0.3591 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 59/62 (19 sessions) | 0.7663 | 0.3450 | 0.1450 | 0.9275 | 22/23 (11 sessions) | 1.0410 | 0.2895 | 0.1162 | 1.9950 | -0.2748 | -0.2531 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 36/62 (12 sessions) | 0.1389 | 0.0000 | 0.0000 | 0.0000 | 9/23 (6 sessions) | 0.2222 | 0.0000 | 0.0000 | 0.0000 | -0.0833 | -0.2257 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 36/62 (12 sessions) | 0.1389 | 0.0000 | 0.0000 | 0.0000 | 9/23 (6 sessions) | 0.2222 | 0.0000 | 0.0000 | 0.0000 | -0.0833 | -0.2257 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 46/62 (15 sessions) | 0.8341 | 0.6425 | 0.2555 | 1.3625 | 13/23 (7 sessions) | 1.3449 | 0.7255 | 0.3700 | 1.5350 | -0.5108 | -0.4938 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 47/62 (15 sessions) | 1.1107 | 1.0454 | 0.4625 | 1.5775 | 13/23 (8 sessions) | 1.0737 | 0.7900 | 0.2445 | 1.8100 | 0.0370 | 0.0462 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 36/62 (12 sessions) | 1.3356 | 0.7580 | 0.4163 | 2.1250 | 9/23 (6 sessions) | 1.6887 | 1.1438 | 0.8633 | 1.4740 | -0.3531 | -0.2605 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 36/62 (12 sessions) | 1.4181 | 1.3044 | 0.8440 | 2.0523 | 9/23 (6 sessions) | 1.2637 | 1.0257 | 0.4667 | 1.9579 | 0.1544 | 0.1754 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG | 49 | 15 | 40 | 9 | 64.52% | 39.13% | 81.63% |
| direction | SHORT | 36 | 16 | 22 | 14 | 35.48% | 60.87% | 61.11% |
| time_bucket | 09:35-10:00 [SMALL] | 22 | 17 | 14 | 8 | 22.58% | 34.78% | 63.64% |
| time_bucket | 10:00-10:30 [SMALL] | 17 | 11 | 12 | 5 | 19.35% | 21.74% | 70.59% |
| time_bucket | 10:30-11:00 [SMALL] | 3 | 2 | 2 | 1 | 3.23% | 4.35% | 66.67% |
| time_bucket | 11:00-12:00 [SMALL] | 9 | 5 | 8 | 1 | 12.90% | 4.35% | 88.89% |
| time_bucket | 12:00-13:30 [SMALL] | 14 | 7 | 9 | 5 | 14.52% | 21.74% | 64.29% |
| time_bucket | 13:30-15:00 [SMALL] | 13 | 8 | 12 | 1 | 19.35% | 4.35% | 92.31% |
| time_bucket | 15:00-close [SMALL] | 7 | 5 | 5 | 2 | 8.06% | 8.70% | 71.43% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 22 | 7 | 18 | 4 | 29.03% | 17.39% | 81.82% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 18 | 10 | 14 | 4 | 22.58% | 17.39% | 77.78% |
| ema9_20_alignment | EMA_UNAVAILABLE | 45 | 20 | 30 | 15 | 48.39% | 65.22% | 66.67% |
| price_vwap_alignment | VWAP_ALIGNED | 70 | 20 | 50 | 20 | 80.65% | 86.96% | 71.43% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 15 | 7 | 12 | 3 | 19.35% | 13.04% | 80.00% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED | 36 | 10 | 27 | 9 | 43.55% | 39.13% | 75.00% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 19 | 11 | 16 | 3 | 25.81% | 13.04% | 84.21% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE | 30 | 20 | 19 | 11 | 30.65% | 47.83% | 63.33% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 26 | 9 | 19 | 7 | 30.65% | 30.43% | 73.08% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 14 | 9 | 13 | 1 | 20.97% | 4.35% | 92.86% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 45 | 20 | 30 | 15 | 48.39% | 65.22% | 66.67% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 9 | 6 | 7 | 2 | 11.29% | 8.70% | 77.78% |
| prior_ema_cross | NO_PRIOR_CROSS | 59 | 20 | 42 | 17 | 67.74% | 73.91% | 71.19% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 17 | 9 | 13 | 4 | 20.97% | 17.39% | 76.47% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 64 | 15 | 50 | 14 | 80.65% | 60.87% | 78.12% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 20 | 12 | 12 | 8 | 19.35% | 34.78% | 60.00% |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 1 | 1 | 0 | 1 | 0.00% | 4.35% | 0.00% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 2 | 2 | 1 | 1 | 1.61% | 4.35% | 50.00% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 7 | 6 | 6 | 1 | 9.68% | 4.35% | 85.71% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 17 | 6 | 15 | 2 | 24.19% | 8.70% | 88.24% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 7 | 3 | 5 | 2 | 8.06% | 8.70% | 71.43% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 19 | 6 | 15 | 4 | 24.19% | 17.39% | 78.95% |
| stage11_2.room_bucket | UNAVAILABLE_ATR | 33 | 17 | 20 | 13 | 32.26% | 56.52% | 60.61% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 83 | 19 | 60 | 23 | 96.77% | 100.00% | 72.29% |
| known_level_coverage | PARTIAL_UNAVAILABLE [SMALL] | 2 | 1 | 2 | 0 | 3.23% | 0.00% | 100.00% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 18 | 8 | 15 | 3 | 24.19% | 13.04% | 83.33% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 7 | 6 | 6 | 1 | 9.68% | 4.35% | 85.71% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 19 | 6 | 14 | 5 | 22.58% | 21.74% | 73.68% |
| stage11_3.structure | UNAVAILABLE | 41 | 20 | 27 | 14 | 43.55% | 60.87% | 65.85% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 9 | 6 | 7 | 2 | 11.29% | 8.70% | 77.78% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED | 35 | 11 | 28 | 7 | 45.16% | 30.43% | 80.00% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 41 | 20 | 27 | 14 | 43.55% | 60.87% | 65.85% |
| stage11_3.high_structure | EQUAL_HIGH [SMALL] | 2 | 1 | 2 | 0 | 3.23% | 0.00% | 100.00% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 18 | 9 | 16 | 2 | 25.81% | 8.70% | 88.89% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 25 | 9 | 18 | 7 | 29.03% | 30.43% | 72.00% |
| stage11_3.high_structure | UNAVAILABLE | 40 | 20 | 26 | 14 | 41.94% | 60.87% | 65.00% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 17 | 9 | 11 | 6 | 17.74% | 26.09% | 64.71% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 28 | 9 | 24 | 4 | 38.71% | 17.39% | 85.71% |
| stage11_3.low_structure | UNAVAILABLE | 40 | 20 | 27 | 13 | 43.55% | 56.52% | 67.50% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 27 | 18 | 17 | 10 | 27.42% | 43.48% | 62.96% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 15 | 5 | 12 | 3 | 19.35% | 13.04% | 80.00% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 6 | 3 | 4 | 2 | 6.45% | 8.70% | 66.67% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL | 37 | 12 | 29 | 8 | 46.77% | 34.78% | 78.38% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 85 | 20 | 62 | 23 | 100.00% | 100.00% | 72.94% |


### 2026-02


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 58/58 (19 sessions) | 1.5393 | 1.4793 | 0.9600 | 1.9275 | 16/16 (9 sessions) | 1.5019 | 1.3600 | 0.9600 | 1.9600 | 0.0374 | 0.0585 | not resampled |
| body_size [SMALL] | 58/58 (19 sessions) | 0.9953 | 0.8988 | 0.6425 | 1.3262 | 16/16 (9 sessions) | 0.7175 | 0.7275 | 0.5275 | 0.8388 | 0.2778 | 0.5744 | not resampled |
| directional_body [SMALL] | 58/58 (19 sessions) | 0.9953 | 0.8988 | 0.6425 | 1.3262 | 16/16 (9 sessions) | 0.7175 | 0.7275 | 0.5275 | 0.8388 | 0.2778 | 0.5744 | not resampled |
| candle_range [SMALL] | 58/58 (19 sessions) | 1.4047 | 1.3000 | 0.9824 | 1.7575 | 16/16 (9 sessions) | 1.2634 | 1.2725 | 0.8375 | 1.5200 | 0.1412 | 0.2379 | not resampled |
| body_range_ratio [SMALL] | 58/58 (19 sessions) | 0.6928 | 0.7223 | 0.5865 | 0.8234 | 16/16 (9 sessions) | 0.5839 | 0.5545 | 0.4884 | 0.6156 | 0.1089 | 0.6416 | not resampled |
| directional_body_range_ratio [SMALL] | 58/58 (19 sessions) | 0.6928 | 0.7223 | 0.5865 | 0.8234 | 16/16 (9 sessions) | 0.5839 | 0.5545 | 0.4884 | 0.6156 | 0.1089 | 0.6416 | not resampled |
| close_location [SMALL] | 58/58 (19 sessions) | 0.5689 | 0.7248 | 0.1847 | 0.8599 | 16/16 (9 sessions) | 0.6641 | 0.7996 | 0.3527 | 0.9363 | -0.0952 | -0.2761 | not resampled |
| directional_close_location [SMALL] | 58/58 (19 sessions) | 0.8248 | 0.8447 | 0.7748 | 0.9258 | 16/16 (9 sessions) | 0.8483 | 0.8409 | 0.7845 | 0.9534 | -0.0235 | -0.1818 | not resampled |
| distance_beyond_level [SMALL] | 58/58 (19 sessions) | 0.5422 | 0.4300 | 0.2075 | 0.7194 | 16/16 (9 sessions) | 0.3134 | 0.3200 | 0.1575 | 0.4750 | 0.2288 | 0.5493 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 28/58 (9 sessions) | 0.4178 | 0.3161 | 0.1847 | 0.6581 | 9/16 (6 sessions) | 0.2617 | 0.2110 | 0.0914 | 0.2892 | 0.1561 | 0.4603 | not resampled |
| candle_volume [SMALL] | 58/58 (19 sessions) | 1245987.2414 | 1093735.5000 | 751687.0000 | 1565157.7500 | 16/16 (9 sessions) | 1069182.3125 | 906871.0000 | 602414.0000 | 1572862.0000 | 176804.9289 | 0.2727 | not resampled |
| relative_volume_prior_6 [SMALL] | 37/58 (10 sessions) | 1.1198 | 0.9650 | 0.7503 | 1.4598 | 11/16 (7 sessions) | 1.0721 | 1.0478 | 0.8569 | 1.2560 | 0.0477 | 0.1081 | not resampled |
| atr14 [SMALL] | 28/58 (9 sessions) | 1.0908 | 1.0166 | 0.8321 | 1.3264 | 9/16 (6 sessions) | 0.9781 | 0.8753 | 0.7027 | 1.2109 | 0.1127 | 0.3155 | not resampled |
| minutes_since_open [SMALL] | 58/58 (19 sessions) | 111.1207 | 65.0000 | 25.0000 | 168.7500 | 16/16 (9 sessions) | 113.7500 | 100.0000 | 15.0000 | 172.5000 | -2.6293 | -0.0246 | not resampled |
| minutes_since_ema_cross [SMALL] | 18/58 (8 sessions) | 30.0000 | 22.5000 | 10.0000 | 38.7500 | 5/16 (5 sessions) | 31.0000 | 5.0000 | 0.0000 | 50.0000 | -1.0000 | -0.0299 | not resampled |
| break_attempt_rank [SMALL] | 58/58 (19 sessions) | 7.1207 | 6.0000 | 3.0000 | 10.0000 | 16/16 (9 sessions) | 6.7500 | 5.0000 | 2.7500 | 11.2500 | 0.3707 | 0.0718 | not resampled |
| valid_hold_sequence_rank [SMALL] | 58/58 (19 sessions) | 3.8276 | 3.0000 | 2.0000 | 5.7500 | 16/16 (9 sessions) | 3.9375 | 3.5000 | 1.0000 | 6.2500 | -0.1099 | -0.0413 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 25/58 (8 sessions) | 0.3272 | 0.2297 | 0.1103 | 0.5480 | 9/16 (6 sessions) | 0.3028 | 0.1230 | 0.0253 | 0.4794 | 0.0243 | 0.0796 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 25/58 (8 sessions) | 0.3115 | 0.2599 | 0.1371 | 0.3794 | 9/16 (6 sessions) | 0.2638 | 0.1117 | 0.0393 | 0.3959 | 0.0477 | 0.1774 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 35/58 (10 sessions) | 0.0674 | 0.0707 | -0.1234 | 0.2089 | 11/16 (7 sessions) | 0.0085 | 0.1091 | -0.1625 | 0.1498 | 0.0589 | 0.2572 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 34/58 (10 sessions) | 0.0236 | -0.0050 | -0.0786 | 0.1075 | 9/16 (6 sessions) | -0.0362 | 0.0166 | -0.2106 | 0.0960 | 0.0597 | 0.3214 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 33/58 (10 sessions) | 0.0159 | -0.0102 | -0.0820 | 0.0754 | 9/16 (6 sessions) | -0.0363 | -0.0146 | -0.1762 | 0.0684 | 0.0522 | 0.3209 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 25/58 (8 sessions) | 0.0211 | -0.0109 | -0.0736 | 0.1417 | 7/16 (5 sessions) | 0.0050 | 0.0577 | -0.1350 | 0.0842 | 0.0161 | 0.1117 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 24/58 (8 sessions) | -0.0088 | -0.0280 | -0.0763 | 0.0798 | 7/16 (5 sessions) | -0.0088 | 0.0267 | -0.1246 | 0.0549 | 0.0001 | 0.0005 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 24/58 (8 sessions) | -0.0099 | -0.0282 | -0.0644 | 0.0571 | 7/16 (5 sessions) | -0.0074 | 0.0113 | -0.1067 | 0.0440 | -0.0025 | -0.0256 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 58/58 (19 sessions) | 0.0213 | 0.0151 | -0.0299 | 0.0467 | 16/16 (9 sessions) | 0.0282 | 0.0040 | -0.0108 | 0.0552 | -0.0069 | -0.0327 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 48/58 (14 sessions) | -0.0050 | 0.0066 | -0.0135 | 0.0294 | 15/16 (9 sessions) | -0.0015 | -0.0012 | -0.0212 | 0.0149 | -0.0035 | -0.0362 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 45/58 (11 sessions) | 0.0002 | 0.0102 | -0.0076 | 0.0288 | 11/16 (7 sessions) | 0.0115 | 0.0001 | -0.0054 | 0.0119 | -0.0113 | -0.1554 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 21/58 (7 sessions) | 0.4286 | 0.0000 | 0.0000 | 1.0000 | 7/16 (5 sessions) | 0.4286 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 15/58 (7 sessions) | 0.9333 | 1.0000 | 0.5000 | 1.0000 | 5/16 (4 sessions) | 0.6000 | 1.0000 | 0.0000 | 1.0000 | 0.3333 | 0.4443 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 10/58 (7 sessions) | 1.8000 | 1.5000 | 1.0000 | 2.7500 | 2/16 (2 sessions) | 2.0000 | 2.0000 | 1.5000 | 2.5000 | -0.2000 | -0.1601 | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 28/58 (9 sessions) | 0.4643 | 0.0000 | 0.0000 | 1.0000 | 9/16 (6 sessions) | 0.1111 | 0.0000 | 0.0000 | 0.0000 | 0.3532 | 0.6656 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 25/58 (8 sessions) | 0.7200 | 1.0000 | 0.0000 | 1.0000 | 9/16 (6 sessions) | 0.2222 | 0.0000 | 0.0000 | 0.0000 | 0.4978 | 0.6912 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 15/58 (7 sessions) | 1.0667 | 1.0000 | 0.0000 | 1.0000 | 5/16 (4 sessions) | 0.8000 | 1.0000 | 1.0000 | 1.0000 | 0.2667 | 0.2148 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 21/58 (7 sessions) | 0.1429 | 0.0000 | 0.0000 | 0.0000 | 7/16 (5 sessions) | 0.1429 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 15/58 (7 sessions) | 0.2000 | 0.0000 | 0.0000 | 0.0000 | 5/16 (4 sessions) | 0.4000 | 0.0000 | 0.0000 | 1.0000 | -0.2000 | -0.4472 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 10/58 (7 sessions) | 0.3000 | 0.0000 | 0.0000 | 0.0000 | 2/16 (2 sessions) | 0.5000 | 0.5000 | 0.2500 | 0.7500 | -0.2000 | -0.2949 | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 39/58 (10 sessions) | 1.2308 | 1.0000 | 0.0000 | 2.0000 | 11/16 (7 sessions) | 1.1818 | 1.0000 | 0.5000 | 1.5000 | 0.0490 | 0.0459 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 33/58 (10 sessions) | 2.2424 | 2.0000 | 1.0000 | 3.0000 | 9/16 (6 sessions) | 1.6667 | 1.0000 | 1.0000 | 3.0000 | 0.5758 | 0.3925 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 23/58 (8 sessions) | 3.4783 | 3.0000 | 2.0000 | 5.0000 | 7/16 (5 sessions) | 3.7143 | 3.0000 | 2.0000 | 4.5000 | -0.2360 | -0.0928 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 39/58 (10 sessions) | 2.6398 | 2.5400 | 1.8275 | 3.1775 | 11/16 (7 sessions) | 2.1953 | 2.1100 | 1.5300 | 2.6675 | 0.4444 | 0.3893 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 33/58 (10 sessions) | 3.4133 | 3.1100 | 2.3950 | 4.5900 | 9/16 (6 sessions) | 2.9599 | 2.5987 | 1.6650 | 3.5350 | 0.4535 | 0.2958 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 23/58 (8 sessions) | 4.0918 | 3.7850 | 2.9500 | 5.3250 | 7/16 (5 sessions) | 4.8286 | 4.4300 | 3.1950 | 6.5350 | -0.7367 | -0.4229 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 28/58 (9 sessions) | 2.2068 | 1.9335 | 1.7005 | 2.6535 | 9/16 (6 sessions) | 2.0789 | 2.0279 | 1.7800 | 2.4105 | 0.1278 | 0.2096 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 28/58 (9 sessions) | 2.9317 | 2.8055 | 2.4326 | 3.3922 | 9/16 (6 sessions) | 2.8476 | 2.3695 | 2.2512 | 3.1572 | 0.0841 | 0.1050 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 23/58 (8 sessions) | 4.0214 | 3.7378 | 3.3070 | 4.4398 | 7/16 (5 sessions) | 4.5340 | 4.5824 | 4.0839 | 4.9813 | -0.5126 | -0.5452 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 39/58 (10 sessions) | 0.4379 | 0.3706 | 0.2408 | 0.5860 | 11/16 (7 sessions) | 0.4903 | 0.4901 | 0.2185 | 0.8246 | -0.0524 | -0.1727 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 33/58 (10 sessions) | 0.2859 | 0.2623 | 0.1651 | 0.3931 | 9/16 (6 sessions) | 0.3465 | 0.3156 | 0.2067 | 0.4443 | -0.0606 | -0.3483 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 23/58 (8 sessions) | 0.1572 | 0.1282 | 0.0773 | 0.2527 | 7/16 (5 sessions) | 0.1808 | 0.1108 | 0.0679 | 0.2768 | -0.0236 | -0.1818 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 39/58 (10 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 11/16 (7 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 33/58 (10 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9/16 (6 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 23/58 (8 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 7/16 (5 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 39/58 (10 sessions) | 0.4872 | 0.5000 | 0.2500 | 0.7500 | 11/16 (7 sessions) | 0.4318 | 0.5000 | 0.2500 | 0.5000 | 0.0554 | 0.2049 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 33/58 (10 sessions) | 0.4970 | 0.5000 | 0.4000 | 0.6000 | 9/16 (6 sessions) | 0.5111 | 0.5000 | 0.5000 | 0.6000 | -0.0141 | -0.0886 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 23/58 (8 sessions) | 0.5237 | 0.5455 | 0.4545 | 0.5909 | 7/16 (5 sessions) | 0.4935 | 0.5000 | 0.4091 | 0.5682 | 0.0302 | 0.2945 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 28/58 (9 sessions) | 1.1207 | 0.9754 | 0.6124 | 1.6152 | 9/16 (6 sessions) | 0.9356 | 0.6796 | 0.5657 | 1.1878 | 0.1851 | 0.2895 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 28/58 (9 sessions) | 0.5169 | 0.3835 | 0.2024 | 0.6716 | 9/16 (6 sessions) | 0.4612 | 0.2062 | 0.1340 | 0.6597 | 0.0558 | 0.1061 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 25/58 (8 sessions) | 0.4102 | 0.3198 | 0.1410 | 0.5132 | 9/16 (6 sessions) | 0.4068 | 0.2842 | 0.0947 | 0.7598 | 0.0034 | 0.0086 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 49/58 (17 sessions) | 2.6385 | 2.1893 | 0.7150 | 3.9450 | 13/16 (7 sessions) | 2.4363 | 1.9450 | 0.6100 | 3.8600 | 0.2022 | 0.0846 | not resampled |
| stage11_2.room_in_atr [SMALL] | 24/58 (8 sessions) | 2.7433 | 2.3371 | 0.4838 | 3.0190 | 8/16 (5 sessions) | 2.0091 | 1.6941 | 0.3715 | 2.7446 | 0.7343 | 0.2634 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 58/58 (19 sessions) | 2.7759 | 2.0000 | 2.0000 | 4.0000 | 16/16 (9 sessions) | 2.1250 | 2.0000 | 1.0000 | 4.0000 | 0.6509 | 0.3777 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 58/58 (19 sessions) | 3.2241 | 4.0000 | 2.0000 | 4.0000 | 16/16 (9 sessions) | 3.8750 | 4.0000 | 2.0000 | 5.0000 | -0.6509 | -0.3777 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 53/58 (17 sessions) | 1.9259 | 0.7200 | 0.2720 | 2.6900 | 13/16 (7 sessions) | 1.8036 | 0.5650 | 0.3200 | 3.8000 | 0.1224 | 0.0512 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 54/58 (19 sessions) | 0.9647 | 0.4300 | 0.2000 | 1.1805 | 16/16 (9 sessions) | 0.7606 | 0.2625 | 0.0800 | 0.5200 | 0.2041 | 0.1534 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 28/58 (9 sessions) | 0.2500 | 0.0000 | 0.0000 | 0.2500 | 9/16 (6 sessions) | 0.5556 | 0.0000 | 0.0000 | 1.0000 | -0.3056 | -0.5337 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 28/58 (9 sessions) | 0.3571 | 0.0000 | 0.0000 | 1.0000 | 9/16 (6 sessions) | 0.5556 | 0.0000 | 0.0000 | 1.0000 | -0.1984 | -0.2877 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 38/58 (10 sessions) | 1.6054 | 1.1625 | 0.5625 | 2.2188 | 11/16 (7 sessions) | 1.3005 | 0.8300 | 0.4200 | 2.1550 | 0.3050 | 0.2183 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 38/58 (11 sessions) | 1.8257 | 1.6100 | 0.8099 | 2.4112 | 10/16 (6 sessions) | 1.6571 | 1.1474 | 0.8941 | 1.4012 | 0.1686 | 0.1130 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 28/58 (9 sessions) | 1.3886 | 1.0616 | 0.5263 | 2.0602 | 9/16 (6 sessions) | 1.3285 | 0.6855 | 0.5388 | 2.3231 | 0.0600 | 0.0529 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 28/58 (9 sessions) | 1.4790 | 1.3244 | 0.7734 | 1.7689 | 9/16 (6 sessions) | 1.4577 | 1.1479 | 0.7862 | 1.7640 | 0.0213 | 0.0194 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG | 46 | 14 | 35 | 11 | 60.34% | 68.75% | 76.09% |
| direction | SHORT [SMALL] | 28 | 12 | 23 | 5 | 39.66% | 31.25% | 82.14% |
| time_bucket | 09:35-10:00 [SMALL] | 24 | 19 | 19 | 5 | 32.76% | 31.25% | 79.17% |
| time_bucket | 10:00-10:30 [SMALL] | 8 | 6 | 6 | 2 | 10.34% | 12.50% | 75.00% |
| time_bucket | 10:30-11:00 [SMALL] | 7 | 5 | 7 | 0 | 12.07% | 0.00% | 100.00% |
| time_bucket | 11:00-12:00 [SMALL] | 13 | 6 | 9 | 4 | 15.52% | 25.00% | 69.23% |
| time_bucket | 12:00-13:30 [SMALL] | 12 | 5 | 9 | 3 | 15.52% | 18.75% | 75.00% |
| time_bucket | 13:30-15:00 [SMALL] | 4 | 3 | 3 | 1 | 5.17% | 6.25% | 75.00% |
| time_bucket | 15:00-close [SMALL] | 6 | 4 | 5 | 1 | 8.62% | 6.25% | 83.33% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 25 | 7 | 19 | 6 | 32.76% | 37.50% | 76.00% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 9 | 6 | 6 | 3 | 10.34% | 18.75% | 66.67% |
| ema9_20_alignment | EMA_UNAVAILABLE | 40 | 19 | 33 | 7 | 56.90% | 43.75% | 82.50% |
| price_vwap_alignment | VWAP_ALIGNED | 72 | 19 | 57 | 15 | 98.28% | 93.75% | 79.17% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 2 | 2 | 1 | 1 | 1.72% | 6.25% | 50.00% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED [SMALL] | 37 | 9 | 31 | 6 | 53.45% | 37.50% | 83.78% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 10 | 6 | 5 | 5 | 8.62% | 31.25% | 50.00% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 27 | 19 | 22 | 5 | 37.93% | 31.25% | 81.48% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 20 | 7 | 17 | 3 | 29.31% | 18.75% | 85.00% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 14 | 8 | 8 | 6 | 13.79% | 37.50% | 57.14% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 40 | 19 | 33 | 7 | 56.90% | 43.75% | 82.50% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 15 | 7 | 12 | 3 | 20.69% | 18.75% | 80.00% |
| prior_ema_cross | NO_PRIOR_CROSS | 51 | 19 | 40 | 11 | 68.97% | 68.75% | 78.43% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 8 | 5 | 6 | 2 | 10.34% | 12.50% | 75.00% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE [SMALL] | 52 | 9 | 41 | 11 | 70.69% | 68.75% | 78.85% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 21 | 14 | 16 | 5 | 27.59% | 31.25% | 76.19% |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 1 | 1 | 1 | 0 | 1.72% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 1 | 1 | 1 | 0 | 1.72% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 3 | 2 | 1 | 2 | 1.72% | 12.50% | 33.33% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 10 | 5 | 9 | 1 | 15.52% | 6.25% | 90.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 8 | 3 | 6 | 2 | 10.34% | 12.50% | 75.00% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 10 | 4 | 7 | 3 | 12.07% | 18.75% | 70.00% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 12 | 5 | 9 | 3 | 15.52% | 18.75% | 75.00% |
| stage11_2.room_bucket | UNAVAILABLE_ATR | 30 | 17 | 25 | 5 | 43.10% | 31.25% | 83.33% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 74 | 19 | 58 | 16 | 100.00% | 100.00% | 78.38% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 15 | 8 | 12 | 3 | 20.69% | 18.75% | 80.00% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 7 | 5 | 6 | 1 | 10.34% | 6.25% | 85.71% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 16 | 7 | 11 | 5 | 18.97% | 31.25% | 68.75% |
| stage11_3.structure | UNAVAILABLE | 36 | 19 | 29 | 7 | 50.00% | 43.75% | 80.56% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 12 | 6 | 11 | 1 | 18.97% | 6.25% | 91.67% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 26 | 9 | 18 | 8 | 31.03% | 50.00% | 69.23% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 36 | 19 | 29 | 7 | 50.00% | 43.75% | 80.56% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 13 | 7 | 11 | 2 | 18.97% | 12.50% | 84.62% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 25 | 9 | 18 | 7 | 31.03% | 43.75% | 72.00% |
| stage11_3.high_structure | UNAVAILABLE | 36 | 19 | 29 | 7 | 50.00% | 43.75% | 80.56% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 18 | 8 | 13 | 5 | 22.41% | 31.25% | 72.22% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 21 | 8 | 17 | 4 | 29.31% | 25.00% | 80.95% |
| stage11_3.low_structure | UNAVAILABLE | 35 | 19 | 28 | 7 | 48.28% | 43.75% | 80.00% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 26 | 19 | 21 | 5 | 36.21% | 31.25% | 80.77% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 9 | 5 | 6 | 3 | 10.34% | 18.75% | 66.67% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 6 | 4 | 5 | 1 | 8.62% | 6.25% | 83.33% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 33 | 8 | 26 | 7 | 44.83% | 43.75% | 78.79% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 74 | 19 | 58 | 16 | 100.00% | 100.00% | 78.38% |


### 2026-03


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 77/77 (22 sessions) | 1.7323 | 1.7600 | 1.4900 | 2.0000 | 23/23 (15 sessions) | 1.6567 | 1.7600 | 1.1900 | 1.9900 | 0.0756 | 0.1759 | not resampled |
| body_size [SMALL] | 77/77 (22 sessions) | 1.0061 | 1.0100 | 0.5500 | 1.3200 | 23/23 (15 sessions) | 0.6260 | 0.5100 | 0.3100 | 0.8000 | 0.3801 | 0.6895 | not resampled |
| directional_body [SMALL] | 77/77 (22 sessions) | 1.0061 | 1.0100 | 0.5500 | 1.3200 | 23/23 (15 sessions) | 0.6260 | 0.5100 | 0.3100 | 0.8000 | 0.3801 | 0.6895 | not resampled |
| candle_range [SMALL] | 77/77 (22 sessions) | 1.4398 | 1.3700 | 0.9800 | 1.7300 | 23/23 (15 sessions) | 1.1034 | 0.9800 | 0.8350 | 1.2600 | 0.3364 | 0.5906 | not resampled |
| body_range_ratio [SMALL] | 77/77 (22 sessions) | 0.6749 | 0.7414 | 0.5231 | 0.8373 | 23/23 (15 sessions) | 0.5459 | 0.5254 | 0.4180 | 0.7624 | 0.1290 | 0.5750 | not resampled |
| directional_body_range_ratio [SMALL] | 77/77 (22 sessions) | 0.6749 | 0.7414 | 0.5231 | 0.8373 | 23/23 (15 sessions) | 0.5459 | 0.5254 | 0.4180 | 0.7624 | 0.1290 | 0.5750 | not resampled |
| close_location [SMALL] | 77/77 (22 sessions) | 0.4700 | 0.4054 | 0.1119 | 0.8455 | 23/23 (15 sessions) | 0.6297 | 0.7984 | 0.2902 | 0.9328 | -0.1598 | -0.4357 | not resampled |
| directional_close_location [SMALL] | 77/77 (22 sessions) | 0.8190 | 0.8760 | 0.7555 | 0.9561 | 23/23 (15 sessions) | 0.8366 | 0.9231 | 0.7620 | 0.9606 | -0.0176 | -0.0974 | not resampled |
| distance_beyond_level [SMALL] | 77/77 (22 sessions) | 0.5852 | 0.4100 | 0.2300 | 0.8400 | 23/23 (15 sessions) | 0.2669 | 0.1000 | 0.0525 | 0.3500 | 0.3183 | 0.6950 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 45/77 (18 sessions) | 0.4346 | 0.3229 | 0.1567 | 0.5444 | 9/23 (8 sessions) | 0.3143 | 0.1023 | 0.0991 | 0.2896 | 0.1203 | 0.3146 | not resampled |
| candle_volume [SMALL] | 77/77 (22 sessions) | 1277787.3377 | 1121889.0000 | 770971.0000 | 1569516.0000 | 23/23 (15 sessions) | 1551172.6957 | 1352710.0000 | 942213.0000 | 1628403.5000 | -273385.3580 | -0.3241 | not resampled |
| relative_volume_prior_6 [SMALL] | 56/77 (19 sessions) | 1.2427 | 0.9558 | 0.7320 | 1.2619 | 13/23 (9 sessions) | 1.4811 | 1.2732 | 0.8841 | 1.4228 | -0.2384 | -0.2494 | not resampled |
| atr14 [SMALL] | 45/77 (18 sessions) | 1.1415 | 1.1808 | 0.9536 | 1.3028 | 9/23 (8 sessions) | 1.1298 | 1.1100 | 0.8734 | 1.2938 | 0.0117 | 0.0434 | not resampled |
| minutes_since_open [SMALL] | 77/77 (22 sessions) | 121.5584 | 95.0000 | 25.0000 | 175.0000 | 23/23 (15 sessions) | 103.6957 | 40.0000 | 10.0000 | 95.0000 | 17.8628 | 0.1610 | not resampled |
| minutes_since_ema_cross [SMALL] | 25/77 (10 sessions) | 35.2000 | 30.0000 | 20.0000 | 55.0000 | 4/23 (4 sessions) | 35.0000 | 22.5000 | 18.7500 | 38.7500 | 0.2000 | 0.0077 | not resampled |
| break_attempt_rank [SMALL] | 77/77 (22 sessions) | 6.0260 | 6.0000 | 3.0000 | 8.0000 | 23/23 (15 sessions) | 5.0435 | 3.0000 | 1.0000 | 6.5000 | 0.9825 | 0.2426 | not resampled |
| valid_hold_sequence_rank [SMALL] | 77/77 (22 sessions) | 3.3506 | 3.0000 | 2.0000 | 5.0000 | 23/23 (15 sessions) | 3.0435 | 2.0000 | 1.0000 | 3.5000 | 0.3072 | 0.1531 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 37/77 (15 sessions) | 0.3543 | 0.2750 | 0.1235 | 0.5340 | 6/23 (5 sessions) | 0.3936 | 0.3624 | 0.2493 | 0.5085 | -0.0394 | -0.1337 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 37/77 (15 sessions) | 0.3150 | 0.2188 | 0.1119 | 0.5197 | 6/23 (5 sessions) | 0.4181 | 0.4368 | 0.3251 | 0.5424 | -0.1031 | -0.4373 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 53/77 (19 sessions) | 0.0055 | 0.0120 | -0.1293 | 0.1373 | 10/23 (8 sessions) | -0.0591 | -0.1012 | -0.2984 | 0.1892 | 0.0646 | 0.2538 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 51/77 (18 sessions) | -0.0049 | -0.0097 | -0.1053 | 0.1022 | 10/23 (8 sessions) | -0.0798 | -0.1324 | -0.3033 | 0.1158 | 0.0748 | 0.3605 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 48/77 (18 sessions) | -0.0088 | 0.0058 | -0.0988 | 0.0919 | 10/23 (8 sessions) | -0.0518 | -0.0938 | -0.2349 | 0.0982 | 0.0430 | 0.2189 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 33/77 (14 sessions) | -0.0242 | 0.0036 | -0.1167 | 0.0438 | 5/23 (4 sessions) | -0.1401 | -0.2143 | -0.2207 | -0.0299 | 0.1158 | 0.9186 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 32/77 (13 sessions) | -0.0269 | -0.0036 | -0.0912 | 0.0434 | 5/23 (4 sessions) | -0.1322 | -0.1664 | -0.2056 | -0.0481 | 0.1053 | 0.9474 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 32/77 (13 sessions) | -0.0343 | -0.0050 | -0.0981 | 0.0327 | 5/23 (4 sessions) | -0.1071 | -0.1119 | -0.1672 | -0.0524 | 0.0728 | 0.7024 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 77/77 (22 sessions) | -0.0285 | -0.0064 | -0.0703 | 0.0173 | 23/23 (15 sessions) | 0.0206 | 0.0162 | -0.0388 | 0.0873 | -0.0491 | -0.3031 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 71/77 (21 sessions) | 0.0020 | -0.0045 | -0.0360 | 0.0155 | 16/23 (11 sessions) | 0.0097 | 0.0101 | -0.0334 | 0.0570 | -0.0077 | -0.0845 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 65/77 (20 sessions) | -0.0008 | -0.0056 | -0.0377 | 0.0142 | 16/23 (11 sessions) | 0.0096 | -0.0001 | -0.0276 | 0.0635 | -0.0105 | -0.1553 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 31/77 (13 sessions) | 0.3871 | 0.0000 | 0.0000 | 1.0000 | 5/23 (4 sessions) | 0.4000 | 0.0000 | 0.0000 | 1.0000 | -0.0129 | -0.0197 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 25/77 (11 sessions) | 1.0000 | 1.0000 | 0.0000 | 2.0000 | 5/23 (4 sessions) | 0.6000 | 1.0000 | 0.0000 | 1.0000 | 0.4000 | 0.4058 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 18/77 (8 sessions) | 1.6111 | 1.0000 | 1.0000 | 2.0000 | 4/23 (4 sessions) | 1.2500 | 1.0000 | 1.0000 | 1.2500 | 0.3611 | 0.4863 | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 45/77 (18 sessions) | 0.2444 | 0.0000 | 0.0000 | 0.0000 | 9/23 (8 sessions) | 0.4444 | 0.0000 | 0.0000 | 1.0000 | -0.2000 | -0.4444 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 37/77 (15 sessions) | 0.4865 | 0.0000 | 0.0000 | 1.0000 | 6/23 (5 sessions) | 0.6667 | 1.0000 | 0.2500 | 1.0000 | -0.1802 | -0.3022 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 25/77 (11 sessions) | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 5/23 (4 sessions) | 1.2000 | 1.0000 | 1.0000 | 2.0000 | -0.2000 | -0.2044 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 31/77 (13 sessions) | 0.2581 | 0.0000 | 0.0000 | 0.5000 | 5/23 (4 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.2581 | 0.6176 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 25/77 (11 sessions) | 0.2800 | 0.0000 | 0.0000 | 1.0000 | 5/23 (4 sessions) | 0.2000 | 0.0000 | 0.0000 | 0.0000 | 0.0800 | 0.1752 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 18/77 (8 sessions) | 0.5556 | 0.0000 | 0.0000 | 1.0000 | 4/23 (4 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | 0.0556 | 0.0678 | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 57/77 (19 sessions) | 1.0351 | 1.0000 | 0.0000 | 2.0000 | 15/23 (11 sessions) | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.0351 | 0.0306 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 48/77 (18 sessions) | 1.6458 | 1.0000 | 1.0000 | 2.0000 | 10/23 (8 sessions) | 1.3000 | 1.0000 | 1.0000 | 1.0000 | 0.3458 | 0.2478 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 32/77 (13 sessions) | 2.7188 | 2.5000 | 1.0000 | 4.0000 | 5/23 (4 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.7188 | 0.8835 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 57/77 (19 sessions) | 2.7878 | 2.5600 | 2.1200 | 3.4550 | 15/23 (11 sessions) | 2.8899 | 2.9800 | 2.0104 | 3.7890 | -0.1021 | -0.0999 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 48/77 (18 sessions) | 3.6542 | 3.4275 | 2.5775 | 4.6012 | 10/23 (8 sessions) | 3.6896 | 3.6778 | 3.4325 | 3.9925 | -0.0354 | -0.0267 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 32/77 (13 sessions) | 4.3772 | 4.0825 | 3.4300 | 5.5374 | 5/23 (4 sessions) | 4.3200 | 4.2800 | 3.6500 | 4.2800 | 0.0572 | 0.0423 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 45/77 (18 sessions) | 2.2649 | 2.1428 | 1.9190 | 2.5364 | 9/23 (8 sessions) | 2.4899 | 2.5045 | 1.5808 | 3.1149 | -0.2250 | -0.3135 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 45/77 (18 sessions) | 3.0877 | 2.9063 | 2.6081 | 3.4930 | 9/23 (8 sessions) | 3.3755 | 3.1149 | 2.6627 | 4.1790 | -0.2878 | -0.3600 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 32/77 (13 sessions) | 4.0787 | 3.9475 | 3.5284 | 4.4870 | 5/23 (4 sessions) | 4.4899 | 4.9003 | 4.3775 | 5.0765 | -0.4112 | -0.5244 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 57/77 (19 sessions) | 0.3784 | 0.3175 | 0.1507 | 0.6380 | 15/23 (11 sessions) | 0.4623 | 0.3948 | 0.1702 | 0.6663 | -0.0839 | -0.2884 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 48/77 (18 sessions) | 0.2568 | 0.2196 | 0.1000 | 0.3530 | 10/23 (8 sessions) | 0.3563 | 0.3274 | 0.1871 | 0.4985 | -0.0994 | -0.4967 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 32/77 (13 sessions) | 0.1655 | 0.1651 | 0.0523 | 0.2391 | 5/23 (4 sessions) | 0.2100 | 0.2508 | 0.1003 | 0.3109 | -0.0445 | -0.3499 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 57/77 (19 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 15/23 (11 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 48/77 (18 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 10/23 (8 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 32/77 (13 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 5/23 (4 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 57/77 (19 sessions) | 0.5000 | 0.5000 | 0.2500 | 0.7500 | 15/23 (11 sessions) | 0.4000 | 0.2500 | 0.2500 | 0.6250 | 0.1000 | 0.3705 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 48/77 (18 sessions) | 0.4812 | 0.5000 | 0.4000 | 0.6000 | 10/23 (8 sessions) | 0.4500 | 0.4000 | 0.3250 | 0.5750 | 0.0312 | 0.1873 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 32/77 (13 sessions) | 0.5071 | 0.5455 | 0.4545 | 0.5568 | 5/23 (4 sessions) | 0.5091 | 0.4545 | 0.4545 | 0.5909 | -0.0020 | -0.0233 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 45/77 (18 sessions) | 0.8934 | 0.6206 | 0.3678 | 1.2786 | 9/23 (8 sessions) | 1.5316 | 1.6377 | 0.6907 | 1.8953 | -0.6381 | -0.8415 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 45/77 (18 sessions) | 0.5710 | 0.4926 | 0.3078 | 0.7595 | 9/23 (8 sessions) | 0.6205 | 0.5018 | 0.2965 | 0.8624 | -0.0495 | -0.1298 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 37/77 (15 sessions) | 0.4034 | 0.3147 | 0.1663 | 0.6036 | 6/23 (5 sessions) | 0.4129 | 0.4540 | 0.1231 | 0.6994 | -0.0095 | -0.0310 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 67/77 (21 sessions) | 2.4198 | 1.3900 | 0.8400 | 3.3625 | 20/23 (15 sessions) | 1.9828 | 1.0900 | 0.5025 | 2.0225 | 0.4370 | 0.1799 | not resampled |
| stage11_2.room_in_atr [SMALL] | 42/77 (17 sessions) | 2.4374 | 1.1723 | 0.7767 | 3.7830 | 8/23 (8 sessions) | 2.8913 | 1.3913 | 0.1400 | 2.8377 | -0.4539 | -0.1599 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 77/77 (22 sessions) | 3.4545 | 3.0000 | 3.0000 | 5.0000 | 23/23 (15 sessions) | 3.3043 | 3.0000 | 3.0000 | 4.0000 | 0.1502 | 0.1017 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 77/77 (22 sessions) | 2.5455 | 3.0000 | 1.0000 | 3.0000 | 23/23 (15 sessions) | 2.6957 | 3.0000 | 2.0000 | 3.0000 | -0.1502 | -0.1017 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 74/77 (22 sessions) | 1.2985 | 0.7650 | 0.3550 | 1.4199 | 22/23 (15 sessions) | 0.7541 | 0.4750 | 0.1315 | 1.1712 | 0.5444 | 0.3837 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 70/77 (21 sessions) | 1.5131 | 0.6950 | 0.2400 | 1.4362 | 21/23 (15 sessions) | 1.3821 | 0.2100 | 0.0750 | 0.8840 | 0.1309 | 0.0561 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 45/77 (18 sessions) | 0.2000 | 0.0000 | 0.0000 | 0.0000 | 9/23 (8 sessions) | 0.3333 | 0.0000 | 0.0000 | 1.0000 | -0.1333 | -0.2873 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 45/77 (18 sessions) | 0.4667 | 0.0000 | 0.0000 | 1.0000 | 9/23 (8 sessions) | 0.4444 | 0.0000 | 0.0000 | 1.0000 | 0.0222 | 0.0364 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 52/77 (18 sessions) | 1.8596 | 1.5995 | 0.8561 | 2.6388 | 12/23 (10 sessions) | 1.8775 | 2.0500 | 0.9200 | 2.7238 | -0.0179 | -0.0128 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 54/77 (19 sessions) | 1.7218 | 1.4735 | 0.8600 | 2.1025 | 14/23 (10 sessions) | 2.0876 | 1.6690 | 1.0612 | 3.1675 | -0.3658 | -0.2701 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 45/77 (18 sessions) | 1.4481 | 1.2917 | 0.7452 | 1.9906 | 9/23 (8 sessions) | 2.2957 | 2.0702 | 1.4537 | 3.4061 | -0.8476 | -0.7473 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 44/77 (18 sessions) | 1.3873 | 1.3259 | 0.8656 | 1.7464 | 9/23 (8 sessions) | 1.5231 | 0.9279 | 0.7510 | 2.3115 | -0.1357 | -0.1585 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG | 52 | 18 | 37 | 15 | 48.05% | 65.22% | 71.15% |
| direction | SHORT | 48 | 19 | 40 | 8 | 51.95% | 34.78% | 83.33% |
| time_bucket | 09:35-10:00 [SMALL] | 28 | 21 | 20 | 8 | 25.97% | 34.78% | 71.43% |
| time_bucket | 10:00-10:30 [SMALL] | 14 | 10 | 9 | 5 | 11.69% | 21.74% | 64.29% |
| time_bucket | 10:30-11:00 [SMALL] | 10 | 8 | 7 | 3 | 9.09% | 13.04% | 70.00% |
| time_bucket | 11:00-12:00 [SMALL] | 15 | 12 | 13 | 2 | 16.88% | 8.70% | 86.67% |
| time_bucket | 12:00-13:30 [SMALL] | 15 | 9 | 14 | 1 | 18.18% | 4.35% | 93.33% |
| time_bucket | 13:30-15:00 [SMALL] | 11 | 8 | 11 | 0 | 14.29% | 0.00% | 100.00% |
| time_bucket | 15:00-close [SMALL] | 7 | 5 | 3 | 4 | 3.90% | 17.39% | 42.86% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 22 | 11 | 17 | 5 | 22.08% | 21.74% | 77.27% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 21 | 11 | 20 | 1 | 25.97% | 4.35% | 95.24% |
| ema9_20_alignment | EMA_UNAVAILABLE | 57 | 22 | 40 | 17 | 51.95% | 73.91% | 70.18% |
| price_vwap_alignment | VWAP_ALIGNED | 83 | 22 | 62 | 21 | 80.52% | 91.30% | 74.70% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 17 | 8 | 15 | 2 | 19.48% | 8.70% | 88.24% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED | 46 | 18 | 37 | 9 | 48.05% | 39.13% | 80.43% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 20 | 10 | 18 | 2 | 23.38% | 8.70% | 90.00% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE | 34 | 22 | 22 | 12 | 28.57% | 52.17% | 64.71% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED | 30 | 14 | 25 | 5 | 32.47% | 21.74% | 83.33% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 13 | 7 | 12 | 1 | 15.58% | 4.35% | 92.31% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 57 | 22 | 40 | 17 | 51.95% | 73.91% | 70.18% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 12 | 7 | 9 | 3 | 11.69% | 13.04% | 75.00% |
| prior_ema_cross | NO_PRIOR_CROSS | 71 | 22 | 52 | 19 | 67.53% | 82.61% | 73.24% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 17 | 9 | 16 | 1 | 20.78% | 4.35% | 94.12% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 64 | 18 | 53 | 11 | 68.83% | 47.83% | 82.81% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL | 34 | 17 | 22 | 12 | 28.57% | 52.17% | 64.71% |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 2 | 2 | 2 | 0 | 2.60% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 11 | 9 | 11 | 0 | 14.29% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 5 | 3 | 4 | 1 | 5.19% | 4.35% | 80.00% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 6 | 4 | 4 | 2 | 5.19% | 8.70% | 66.67% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 2 | 2 | 2 | 0 | 2.60% | 0.00% | 100.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 15 | 4 | 13 | 2 | 16.88% | 8.70% | 86.67% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 11 | 8 | 8 | 3 | 10.39% | 13.04% | 72.73% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 13 | 6 | 10 | 3 | 12.99% | 13.04% | 76.92% |
| stage11_2.room_bucket | UNAVAILABLE_ATR | 37 | 20 | 25 | 12 | 32.47% | 52.17% | 67.57% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 100 | 22 | 77 | 23 | 100.00% | 100.00% | 77.00% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 16 | 11 | 15 | 1 | 19.48% | 4.35% | 93.75% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 12 | 9 | 10 | 2 | 12.99% | 8.70% | 83.33% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 16 | 9 | 12 | 4 | 15.58% | 17.39% | 75.00% |
| stage11_3.structure | UNAVAILABLE | 56 | 22 | 40 | 16 | 51.95% | 69.57% | 71.43% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 14 | 11 | 13 | 1 | 16.88% | 4.35% | 92.86% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED | 30 | 12 | 24 | 6 | 31.17% | 26.09% | 80.00% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 56 | 22 | 40 | 16 | 51.95% | 69.57% | 71.43% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 20 | 10 | 17 | 3 | 22.08% | 13.04% | 85.00% |
| stage11_3.high_structure | LOWER_HIGH | 30 | 15 | 25 | 5 | 32.47% | 21.74% | 83.33% |
| stage11_3.high_structure | UNAVAILABLE | 50 | 22 | 35 | 15 | 45.45% | 65.22% | 70.00% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 23 | 10 | 18 | 5 | 23.38% | 21.74% | 78.26% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 24 | 15 | 22 | 2 | 28.57% | 8.70% | 91.67% |
| stage11_3.low_structure | UNAVAILABLE | 53 | 22 | 37 | 16 | 48.05% | 69.57% | 69.81% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE | 33 | 21 | 24 | 9 | 31.17% | 39.13% | 72.73% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 6 | 3 | 4 | 2 | 5.19% | 8.70% | 66.67% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 23 | 10 | 20 | 3 | 25.97% | 13.04% | 86.96% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL | 38 | 14 | 29 | 9 | 37.66% | 39.13% | 76.32% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 100 | 22 | 77 | 23 | 100.00% | 100.00% | 77.00% |


### 2026-04


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 66/66 (21 sessions) | 1.2224 | 1.1800 | 0.8200 | 1.6200 | 29/29 (17 sessions) | 1.2487 | 1.2700 | 0.9400 | 1.4000 | -0.0263 | -0.0656 | not resampled |
| body_size [SMALL] | 66/66 (21 sessions) | 0.6380 | 0.4750 | 0.3206 | 0.7513 | 29/29 (17 sessions) | 0.4690 | 0.3800 | 0.2800 | 0.6400 | 0.1691 | 0.3812 | not resampled |
| directional_body [SMALL] | 66/66 (21 sessions) | 0.6380 | 0.4750 | 0.3206 | 0.7513 | 29/29 (17 sessions) | 0.4690 | 0.3800 | 0.2800 | 0.6400 | 0.1691 | 0.3812 | not resampled |
| candle_range [SMALL] | 66/66 (21 sessions) | 1.0097 | 0.8050 | 0.6350 | 1.1900 | 29/29 (17 sessions) | 0.8390 | 0.7500 | 0.6000 | 1.0650 | 0.1707 | 0.3064 | not resampled |
| body_range_ratio [SMALL] | 66/66 (21 sessions) | 0.6183 | 0.6382 | 0.4392 | 0.7959 | 29/29 (17 sessions) | 0.5483 | 0.5850 | 0.4384 | 0.6598 | 0.0700 | 0.3404 | not resampled |
| directional_body_range_ratio [SMALL] | 66/66 (21 sessions) | 0.6183 | 0.6382 | 0.4392 | 0.7959 | 29/29 (17 sessions) | 0.5483 | 0.5850 | 0.4384 | 0.6598 | 0.0700 | 0.3404 | not resampled |
| close_location [SMALL] | 66/66 (21 sessions) | 0.5621 | 0.6023 | 0.2090 | 0.8731 | 29/29 (17 sessions) | 0.5348 | 0.5038 | 0.2500 | 0.8491 | 0.0273 | 0.0842 | not resampled |
| directional_close_location [SMALL] | 66/66 (21 sessions) | 0.7846 | 0.8471 | 0.6578 | 0.9172 | 29/29 (17 sessions) | 0.7759 | 0.7841 | 0.6449 | 0.8868 | 0.0087 | 0.0533 | not resampled |
| distance_beyond_level [SMALL] | 66/66 (21 sessions) | 0.3540 | 0.2146 | 0.0963 | 0.4475 | 29/29 (17 sessions) | 0.1972 | 0.1400 | 0.0600 | 0.2750 | 0.1568 | 0.4632 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 41/66 (16 sessions) | 0.3790 | 0.2432 | 0.1260 | 0.6188 | 14/29 (10 sessions) | 0.2405 | 0.1904 | 0.0610 | 0.3756 | 0.1385 | 0.4167 | not resampled |
| candle_volume [SMALL] | 66/66 (21 sessions) | 705727.6364 | 553847.5000 | 391576.0000 | 855690.2500 | 29/29 (17 sessions) | 792270.3793 | 580339.0000 | 331819.0000 | 1038776.0000 | -86542.7429 | -0.1497 | not resampled |
| relative_volume_prior_6 [SMALL] | 46/66 (17 sessions) | 1.3871 | 1.1520 | 0.8085 | 1.6808 | 20/29 (12 sessions) | 1.3197 | 0.7528 | 0.6573 | 0.9870 | 0.0675 | 0.0645 | not resampled |
| atr14 [SMALL] | 41/66 (16 sessions) | 0.6935 | 0.6781 | 0.5974 | 0.7433 | 14/29 (10 sessions) | 0.7252 | 0.6465 | 0.5910 | 0.7244 | -0.0317 | -0.1351 | not resampled |
| minutes_since_open [SMALL] | 66/66 (21 sessions) | 135.6818 | 105.0000 | 26.2500 | 218.7500 | 29/29 (17 sessions) | 92.4138 | 60.0000 | 20.0000 | 145.0000 | 43.2680 | 0.3994 | not resampled |
| minutes_since_ema_cross [SMALL] | 24/66 (10 sessions) | 50.2083 | 45.0000 | 18.7500 | 71.2500 | 8/29 (5 sessions) | 35.6250 | 35.0000 | 22.5000 | 43.7500 | 14.5833 | 0.4323 | not resampled |
| break_attempt_rank [SMALL] | 66/66 (21 sessions) | 7.1212 | 6.0000 | 3.0000 | 10.0000 | 29/29 (17 sessions) | 5.4483 | 5.0000 | 3.0000 | 7.0000 | 1.6729 | 0.3661 | not resampled |
| valid_hold_sequence_rank [SMALL] | 66/66 (21 sessions) | 3.5455 | 3.0000 | 2.0000 | 5.0000 | 29/29 (17 sessions) | 2.8621 | 3.0000 | 1.0000 | 3.0000 | 0.6834 | 0.3288 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 34/66 (13 sessions) | 0.2180 | 0.1853 | 0.1088 | 0.2808 | 9/29 (6 sessions) | 0.2462 | 0.2132 | 0.1460 | 0.2336 | -0.0282 | -0.1801 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 34/66 (13 sessions) | 0.3459 | 0.3242 | 0.1910 | 0.4922 | 9/29 (6 sessions) | 0.3730 | 0.3552 | 0.2327 | 0.5145 | -0.0272 | -0.1326 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 43/66 (16 sessions) | 0.0100 | 0.0392 | -0.1028 | 0.1315 | 17/29 (11 sessions) | -0.0026 | 0.0042 | -0.0991 | 0.0894 | 0.0125 | 0.0794 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 43/66 (16 sessions) | 0.0071 | 0.0149 | -0.0685 | 0.0867 | 16/29 (11 sessions) | 0.0072 | -0.0116 | -0.0781 | 0.1004 | -0.0001 | -0.0008 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 42/66 (16 sessions) | 0.0052 | 0.0155 | -0.0817 | 0.0753 | 15/29 (11 sessions) | 0.0117 | -0.0250 | -0.0687 | 0.0897 | -0.0066 | -0.0616 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 34/66 (13 sessions) | 0.0193 | 0.0172 | -0.0294 | 0.0739 | 9/29 (6 sessions) | 0.0058 | -0.0084 | -0.0642 | 0.0783 | 0.0135 | 0.1541 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 32/66 (12 sessions) | 0.0120 | 0.0151 | -0.0183 | 0.0453 | 9/29 (6 sessions) | 0.0121 | -0.0268 | -0.0507 | 0.0619 | -0.0001 | -0.0013 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 31/66 (12 sessions) | 0.0155 | 0.0205 | -0.0165 | 0.0379 | 9/29 (6 sessions) | 0.0145 | -0.0264 | -0.0394 | 0.0591 | 0.0010 | 0.0160 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 66/66 (21 sessions) | 0.0010 | 0.0075 | -0.0076 | 0.0349 | 29/29 (17 sessions) | -0.0217 | -0.0025 | -0.0566 | 0.0198 | 0.0228 | 0.1737 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 61/66 (20 sessions) | 0.0074 | 0.0056 | -0.0079 | 0.0201 | 24/29 (15 sessions) | -0.0230 | -0.0062 | -0.0342 | 0.0196 | 0.0304 | 0.4788 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 58/66 (20 sessions) | -0.0035 | 0.0070 | -0.0069 | 0.0210 | 22/29 (13 sessions) | -0.0014 | -0.0029 | -0.0282 | 0.0259 | -0.0021 | -0.0424 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 31/66 (12 sessions) | 0.2581 | 0.0000 | 0.0000 | 0.5000 | 8/29 (5 sessions) | 0.2500 | 0.0000 | 0.0000 | 0.2500 | 0.0081 | 0.0180 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 26/66 (11 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | 7/29 (5 sessions) | 0.7143 | 1.0000 | 0.5000 | 1.0000 | -0.2143 | -0.4237 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 20/66 (11 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 2/29 (2 sessions) | 1.5000 | 1.5000 | 1.2500 | 1.7500 | -0.5000 | -0.7670 | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 41/66 (16 sessions) | 0.3415 | 0.0000 | 0.0000 | 1.0000 | 14/29 (10 sessions) | 0.4286 | 0.0000 | 0.0000 | 1.0000 | -0.0871 | -0.1783 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 34/66 (13 sessions) | 0.6765 | 1.0000 | 0.0000 | 1.0000 | 9/29 (6 sessions) | 0.7778 | 1.0000 | 1.0000 | 1.0000 | -0.1013 | -0.1488 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 26/66 (11 sessions) | 0.8462 | 1.0000 | 0.2500 | 1.0000 | 7/29 (5 sessions) | 1.1429 | 1.0000 | 1.0000 | 1.5000 | -0.2967 | -0.4722 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 31/66 (12 sessions) | 0.1613 | 0.0000 | 0.0000 | 0.0000 | 8/29 (5 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | -0.3387 | -0.8279 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 26/66 (11 sessions) | 0.4615 | 0.0000 | 0.0000 | 1.0000 | 7/29 (5 sessions) | 0.8571 | 1.0000 | 1.0000 | 1.0000 | -0.3956 | -0.7215 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 20/66 (11 sessions) | 0.7000 | 1.0000 | 0.0000 | 1.0000 | 2/29 (2 sessions) | 0.5000 | 0.5000 | 0.2500 | 0.7500 | 0.2000 | 0.3032 | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 49/66 (17 sessions) | 0.9796 | 1.0000 | 0.0000 | 2.0000 | 20/29 (12 sessions) | 1.2000 | 1.0000 | 0.0000 | 2.0000 | -0.2204 | -0.1921 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 42/66 (16 sessions) | 1.8095 | 2.0000 | 1.0000 | 3.0000 | 15/29 (11 sessions) | 2.6667 | 3.0000 | 1.5000 | 4.0000 | -0.8571 | -0.6122 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 31/66 (12 sessions) | 3.1290 | 3.0000 | 1.0000 | 5.0000 | 8/29 (5 sessions) | 4.0000 | 5.0000 | 1.0000 | 5.5000 | -0.8710 | -0.3626 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 49/66 (17 sessions) | 1.7533 | 1.5900 | 1.2600 | 2.1550 | 20/29 (12 sessions) | 1.5304 | 1.5550 | 1.2288 | 1.8100 | 0.2229 | 0.3143 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 42/66 (16 sessions) | 2.1725 | 1.9160 | 1.5150 | 2.7675 | 15/29 (11 sessions) | 2.1383 | 1.9200 | 1.6150 | 2.4450 | 0.0342 | 0.0356 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 31/66 (12 sessions) | 2.9400 | 2.9000 | 2.0556 | 3.7600 | 8/29 (5 sessions) | 2.9569 | 2.9700 | 1.9662 | 3.0550 | -0.0168 | -0.0142 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 41/66 (16 sessions) | 2.4176 | 2.3758 | 1.8247 | 2.6108 | 14/29 (10 sessions) | 2.1810 | 2.2721 | 1.6801 | 2.4651 | 0.2366 | 0.3231 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 41/66 (16 sessions) | 3.0984 | 2.9855 | 2.5422 | 3.7768 | 14/29 (10 sessions) | 2.9000 | 2.7579 | 2.5863 | 3.0953 | 0.1984 | 0.2489 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 31/66 (12 sessions) | 4.5755 | 4.5500 | 3.4346 | 5.4228 | 8/29 (5 sessions) | 4.5324 | 4.8618 | 4.3170 | 5.0922 | 0.0431 | 0.0362 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 49/66 (17 sessions) | 0.5276 | 0.5138 | 0.3343 | 0.7484 | 20/29 (12 sessions) | 0.3648 | 0.2856 | 0.2147 | 0.5420 | 0.1628 | 0.6123 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 42/66 (16 sessions) | 0.3265 | 0.3158 | 0.1221 | 0.5089 | 15/29 (11 sessions) | 0.2690 | 0.2689 | 0.1136 | 0.4282 | 0.0574 | 0.2770 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 31/66 (12 sessions) | 0.1719 | 0.1125 | 0.0394 | 0.2808 | 8/29 (5 sessions) | 0.1757 | 0.1830 | 0.1195 | 0.2271 | -0.0038 | -0.0256 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 49/66 (17 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 20/29 (12 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 42/66 (16 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 15/29 (11 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 31/66 (12 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 8/29 (5 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 49/66 (17 sessions) | 0.5408 | 0.5000 | 0.5000 | 0.7500 | 20/29 (12 sessions) | 0.5625 | 0.5000 | 0.2500 | 0.7500 | -0.0217 | -0.0945 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 42/66 (16 sessions) | 0.4952 | 0.5000 | 0.4000 | 0.6000 | 15/29 (11 sessions) | 0.4933 | 0.5000 | 0.4000 | 0.5500 | 0.0019 | 0.0133 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 31/66 (12 sessions) | 0.4795 | 0.5000 | 0.4091 | 0.5682 | 8/29 (5 sessions) | 0.5170 | 0.5227 | 0.4432 | 0.6023 | -0.0376 | -0.3235 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 41/66 (16 sessions) | 1.2006 | 1.2000 | 0.4261 | 1.6769 | 14/29 (10 sessions) | 1.0703 | 1.1614 | 0.6869 | 1.5388 | 0.1303 | 0.1542 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 41/66 (16 sessions) | 0.7215 | 0.4443 | 0.2569 | 1.0316 | 14/29 (10 sessions) | 0.4587 | 0.3131 | 0.2503 | 0.6495 | 0.2628 | 0.4390 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 34/66 (13 sessions) | 0.5485 | 0.3330 | 0.1714 | 0.6920 | 9/29 (6 sessions) | 0.2560 | 0.2772 | 0.1176 | 0.3815 | 0.2925 | 0.5525 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 64/66 (20 sessions) | 1.3820 | 0.9275 | 0.3575 | 1.8150 | 28/29 (16 sessions) | 1.3095 | 1.3175 | 0.3638 | 1.7250 | 0.0726 | 0.0425 | not resampled |
| stage11_2.room_in_atr [SMALL] | 41/66 (16 sessions) | 1.5641 | 0.8370 | 0.5115 | 2.1801 | 14/29 (10 sessions) | 1.1580 | 0.7532 | 0.5243 | 1.7481 | 0.4060 | 0.2786 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 66/66 (21 sessions) | 2.5758 | 2.0000 | 1.0000 | 4.0000 | 29/29 (17 sessions) | 2.7931 | 3.0000 | 2.0000 | 4.0000 | -0.2173 | -0.1443 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 66/66 (21 sessions) | 3.4091 | 4.0000 | 2.0000 | 5.0000 | 29/29 (17 sessions) | 3.2069 | 3.0000 | 2.0000 | 4.0000 | 0.2022 | 0.1350 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 64/66 (20 sessions) | 0.7548 | 0.5693 | 0.1875 | 0.9700 | 28/29 (16 sessions) | 0.6402 | 0.2675 | 0.1112 | 0.6887 | 0.1146 | 0.1434 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 66/66 (21 sessions) | 0.8866 | 0.2900 | 0.1203 | 1.0398 | 29/29 (17 sessions) | 0.8137 | 0.3600 | 0.0850 | 1.4200 | 0.0728 | 0.0429 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 41/66 (16 sessions) | 0.2439 | 0.0000 | 0.0000 | 0.0000 | 14/29 (10 sessions) | 0.2143 | 0.0000 | 0.0000 | 0.0000 | 0.0296 | 0.0685 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 41/66 (16 sessions) | 0.5854 | 1.0000 | 0.0000 | 1.0000 | 14/29 (10 sessions) | 0.6429 | 1.0000 | 0.0000 | 1.0000 | -0.0575 | -0.0910 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 48/66 (17 sessions) | 0.8971 | 0.7450 | 0.2775 | 1.3162 | 20/29 (12 sessions) | 0.8307 | 0.7475 | 0.5062 | 1.3050 | 0.0663 | 0.0962 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 45/66 (17 sessions) | 1.2805 | 0.9000 | 0.5486 | 1.8400 | 18/29 (11 sessions) | 1.0817 | 0.9900 | 0.5475 | 1.5325 | 0.1989 | 0.2171 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 41/66 (16 sessions) | 1.3336 | 1.1080 | 0.4052 | 2.0173 | 14/29 (10 sessions) | 1.2097 | 0.9718 | 0.6217 | 1.9695 | 0.1238 | 0.1153 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 40/66 (15 sessions) | 1.7831 | 1.3995 | 0.8840 | 2.4048 | 14/29 (10 sessions) | 1.6394 | 1.1522 | 0.8067 | 2.2128 | 0.1436 | 0.1116 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG | 54 | 20 | 39 | 15 | 59.09% | 51.72% | 72.22% |
| direction | SHORT | 41 | 17 | 27 | 14 | 40.91% | 48.28% | 65.85% |
| time_bucket | 09:35-10:00 [SMALL] | 26 | 19 | 17 | 9 | 25.76% | 31.03% | 65.38% |
| time_bucket | 10:00-10:30 [SMALL] | 12 | 10 | 7 | 5 | 10.61% | 17.24% | 58.33% |
| time_bucket | 10:30-11:00 [SMALL] | 11 | 8 | 6 | 5 | 9.09% | 17.24% | 54.55% |
| time_bucket | 11:00-12:00 [SMALL] | 13 | 8 | 10 | 3 | 15.15% | 10.34% | 76.92% |
| time_bucket | 12:00-13:30 [SMALL] | 18 | 9 | 13 | 5 | 19.70% | 17.24% | 72.22% |
| time_bucket | 13:30-15:00 [SMALL] | 8 | 6 | 7 | 1 | 10.61% | 3.45% | 87.50% |
| time_bucket | 15:00-close [SMALL] | 7 | 5 | 6 | 1 | 9.09% | 3.45% | 85.71% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 27 | 10 | 21 | 6 | 31.82% | 20.69% | 77.78% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 16 | 9 | 13 | 3 | 19.70% | 10.34% | 81.25% |
| ema9_20_alignment | EMA_UNAVAILABLE | 52 | 21 | 32 | 20 | 48.48% | 68.97% | 61.54% |
| price_vwap_alignment | VWAP_ALIGNED | 85 | 21 | 59 | 26 | 89.39% | 89.66% | 69.41% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 10 | 5 | 7 | 3 | 10.61% | 10.34% | 70.00% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED | 43 | 16 | 31 | 12 | 46.97% | 41.38% | 72.09% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 19 | 9 | 14 | 5 | 21.21% | 17.24% | 73.68% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE | 33 | 20 | 21 | 12 | 31.82% | 41.38% | 63.64% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 25 | 12 | 21 | 4 | 31.82% | 13.79% | 84.00% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 18 | 9 | 13 | 5 | 19.70% | 17.24% | 72.22% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 52 | 21 | 32 | 20 | 48.48% | 68.97% | 61.54% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 17 | 6 | 12 | 5 | 18.18% | 17.24% | 70.59% |
| prior_ema_cross | NO_PRIOR_CROSS | 63 | 21 | 42 | 21 | 63.64% | 72.41% | 66.67% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 15 | 8 | 12 | 3 | 18.18% | 10.34% | 80.00% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 69 | 19 | 51 | 18 | 77.27% | 62.07% | 73.91% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 26 | 16 | 15 | 11 | 22.73% | 37.93% | 57.69% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 16 | 9 | 11 | 5 | 16.67% | 17.24% | 68.75% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 8 | 6 | 6 | 2 | 9.09% | 6.90% | 75.00% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 2 | 2 | 1 | 1 | 1.52% | 3.45% | 50.00% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 9 | 7 | 7 | 2 | 10.61% | 6.90% | 77.78% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 7 | 3 | 6 | 1 | 9.09% | 3.45% | 85.71% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 13 | 7 | 10 | 3 | 15.15% | 10.34% | 76.92% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 3 | 2 | 2 | 1 | 3.03% | 3.45% | 66.67% |
| stage11_2.room_bucket | UNAVAILABLE_ATR | 37 | 20 | 23 | 14 | 34.85% | 48.28% | 62.16% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 95 | 21 | 66 | 29 | 100.00% | 100.00% | 69.47% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 11 | 7 | 6 | 5 | 9.09% | 17.24% | 54.55% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 13 | 7 | 12 | 1 | 18.18% | 3.45% | 92.31% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 24 | 12 | 18 | 6 | 27.27% | 20.69% | 75.00% |
| stage11_3.structure | UNAVAILABLE | 47 | 21 | 30 | 17 | 45.45% | 58.62% | 63.83% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 14 | 7 | 10 | 4 | 15.15% | 13.79% | 71.43% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED | 34 | 13 | 26 | 8 | 39.39% | 27.59% | 76.47% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 47 | 21 | 30 | 17 | 45.45% | 58.62% | 63.83% |
| stage11_3.high_structure | EQUAL_HIGH [SMALL] | 2 | 2 | 2 | 0 | 3.03% | 0.00% | 100.00% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 22 | 10 | 20 | 2 | 30.30% | 6.90% | 90.91% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 28 | 12 | 16 | 12 | 24.24% | 41.38% | 57.14% |
| stage11_3.high_structure | UNAVAILABLE | 43 | 21 | 28 | 15 | 42.42% | 51.72% | 65.12% |
| stage11_3.low_structure | HIGHER_LOW | 30 | 14 | 22 | 8 | 33.33% | 27.59% | 73.33% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 21 | 9 | 15 | 6 | 22.73% | 20.69% | 71.43% |
| stage11_3.low_structure | UNAVAILABLE | 44 | 21 | 29 | 15 | 43.94% | 51.72% | 65.91% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 29 | 19 | 19 | 10 | 28.79% | 34.48% | 65.52% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 1 | 1 | 1 | 0 | 1.52% | 0.00% | 100.00% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 17 | 8 | 11 | 6 | 16.67% | 20.69% | 64.71% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL | 48 | 16 | 35 | 13 | 53.03% | 44.83% | 72.92% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 95 | 21 | 66 | 29 | 100.00% | 100.00% | 69.47% |


### 2026-05


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width | 62/62 (20 sessions) | 1.2150 | 1.0800 | 0.9400 | 1.4850 | 38/38 (13 sessions) | 1.4303 | 1.1950 | 1.0600 | 1.7100 | -0.2153 | -0.4386 | not resampled |
| body_size | 62/62 (20 sessions) | 0.7119 | 0.5825 | 0.3500 | 0.9100 | 38/38 (13 sessions) | 0.4454 | 0.3350 | 0.1862 | 0.5798 | 0.2665 | 0.5895 | not resampled |
| directional_body | 62/62 (20 sessions) | 0.7119 | 0.5825 | 0.3500 | 0.9100 | 38/38 (13 sessions) | 0.4454 | 0.3350 | 0.1862 | 0.5798 | 0.2665 | 0.5895 | not resampled |
| candle_range | 62/62 (20 sessions) | 0.9868 | 0.8250 | 0.5088 | 1.1425 | 38/38 (13 sessions) | 0.7807 | 0.6200 | 0.4875 | 0.9025 | 0.2061 | 0.3641 | not resampled |
| body_range_ratio | 62/62 (20 sessions) | 0.7072 | 0.7473 | 0.5946 | 0.8694 | 38/38 (13 sessions) | 0.5379 | 0.5748 | 0.3409 | 0.6829 | 0.1693 | 0.7959 | not resampled |
| directional_body_range_ratio | 62/62 (20 sessions) | 0.7072 | 0.7473 | 0.5946 | 0.8694 | 38/38 (13 sessions) | 0.5379 | 0.5748 | 0.3409 | 0.6829 | 0.1693 | 0.7959 | not resampled |
| close_location | 62/62 (20 sessions) | 0.6185 | 0.8231 | 0.1686 | 0.9404 | 38/38 (13 sessions) | 0.5045 | 0.5557 | 0.1730 | 0.8247 | 0.1140 | 0.3156 | not resampled |
| directional_close_location | 62/62 (20 sessions) | 0.8708 | 0.9030 | 0.8270 | 0.9519 | 38/38 (13 sessions) | 0.7750 | 0.8331 | 0.6556 | 0.9171 | 0.0958 | 0.6329 | not resampled |
| distance_beyond_level | 62/62 (20 sessions) | 0.3769 | 0.3100 | 0.2025 | 0.4875 | 38/38 (13 sessions) | 0.1496 | 0.1050 | 0.0625 | 0.1800 | 0.2274 | 0.9808 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 32/62 (12 sessions) | 0.4275 | 0.3946 | 0.2092 | 0.6663 | 21/38 (8 sessions) | 0.1758 | 0.1479 | 0.0925 | 0.2418 | 0.2517 | 1.0018 | not resampled |
| candle_volume | 62/62 (20 sessions) | 571070.2742 | 503936.5000 | 367321.5000 | 677852.2500 | 38/38 (13 sessions) | 499909.0000 | 444571.5000 | 281782.2500 | 632436.0000 | 71161.2742 | 0.2050 | not resampled |
| relative_volume_prior_6 [SMALL] | 43/62 (17 sessions) | 1.1918 | 0.9492 | 0.7888 | 1.4666 | 26/38 (11 sessions) | 1.0252 | 0.8468 | 0.6945 | 1.2206 | 0.1666 | 0.2531 | not resampled |
| atr14 [SMALL] | 32/62 (12 sessions) | 0.6688 | 0.6241 | 0.5505 | 0.7539 | 21/38 (8 sessions) | 0.6121 | 0.5597 | 0.4734 | 0.6001 | 0.0567 | 0.2693 | not resampled |
| minutes_since_open | 62/62 (20 sessions) | 123.3871 | 72.5000 | 25.0000 | 202.5000 | 38/38 (13 sessions) | 157.3684 | 82.5000 | 30.0000 | 313.7500 | -33.9813 | -0.2638 | not resampled |
| minutes_since_ema_cross [SMALL] | 18/62 (10 sessions) | 56.9444 | 57.5000 | 22.5000 | 82.5000 | 13/38 (7 sessions) | 69.2308 | 75.0000 | 35.0000 | 110.0000 | -12.2863 | -0.3022 | not resampled |
| break_attempt_rank | 62/62 (20 sessions) | 6.7742 | 6.0000 | 3.0000 | 10.0000 | 38/38 (13 sessions) | 7.4737 | 7.0000 | 3.0000 | 10.7500 | -0.6995 | -0.1385 | not resampled |
| valid_hold_sequence_rank | 62/62 (20 sessions) | 3.8065 | 3.0000 | 2.0000 | 5.0000 | 38/38 (13 sessions) | 4.6053 | 4.0000 | 2.0000 | 6.0000 | -0.7988 | -0.2635 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 27/62 (11 sessions) | 0.2645 | 0.2532 | 0.0974 | 0.3916 | 18/38 (7 sessions) | 0.1943 | 0.1243 | 0.0824 | 0.2719 | 0.0702 | 0.3636 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 27/62 (11 sessions) | 0.4172 | 0.3925 | 0.1354 | 0.5832 | 18/38 (7 sessions) | 0.3630 | 0.2517 | 0.1538 | 0.4202 | 0.0542 | 0.1663 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 38/62 (15 sessions) | 0.0048 | 0.0526 | -0.0853 | 0.1308 | 24/38 (10 sessions) | 0.0207 | 0.0247 | -0.0641 | 0.0837 | -0.0159 | -0.0922 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 37/62 (14 sessions) | -0.0090 | 0.0052 | -0.1034 | 0.0908 | 23/38 (9 sessions) | 0.0066 | -0.0040 | -0.0682 | 0.0820 | -0.0156 | -0.1191 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 34/62 (13 sessions) | -0.0054 | -0.0053 | -0.1140 | 0.0785 | 23/38 (9 sessions) | 0.0154 | -0.0068 | -0.0550 | 0.0847 | -0.0207 | -0.1724 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 26/62 (11 sessions) | 0.0100 | 0.0275 | -0.0438 | 0.0580 | 18/38 (7 sessions) | -0.0070 | 0.0052 | -0.0240 | 0.0291 | 0.0171 | 0.1890 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 25/62 (11 sessions) | 0.0055 | -0.0111 | -0.0257 | 0.0565 | 18/38 (7 sessions) | -0.0046 | -0.0031 | -0.0237 | 0.0159 | 0.0101 | 0.1322 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 24/62 (10 sessions) | 0.0104 | 0.0060 | -0.0335 | 0.0616 | 17/38 (7 sessions) | -0.0033 | 0.0003 | -0.0127 | 0.0152 | 0.0137 | 0.1958 | not resampled |
| stage10_9.vwap_slope_1_bars | 62/62 (20 sessions) | 0.0157 | 0.0073 | -0.0150 | 0.0530 | 38/38 (13 sessions) | -0.0191 | 0.0038 | -0.0255 | 0.0186 | 0.0348 | 0.3111 | not resampled |
| stage10_9.vwap_slope_2_bars | 57/62 (20 sessions) | 0.0039 | 0.0071 | -0.0152 | 0.0324 | 34/38 (13 sessions) | 0.0032 | 0.0028 | -0.0126 | 0.0191 | 0.0007 | 0.0136 | not resampled |
| stage10_9.vwap_slope_3_bars | 53/62 (19 sessions) | 0.0037 | 0.0044 | -0.0142 | 0.0325 | 31/38 (12 sessions) | 0.0088 | 0.0041 | -0.0100 | 0.0188 | -0.0051 | -0.1137 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 23/62 (10 sessions) | 0.1739 | 0.0000 | 0.0000 | 0.0000 | 17/38 (7 sessions) | 0.1765 | 0.0000 | 0.0000 | 0.0000 | -0.0026 | -0.0066 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 18/62 (9 sessions) | 0.3889 | 0.0000 | 0.0000 | 1.0000 | 17/38 (7 sessions) | 0.3529 | 0.0000 | 0.0000 | 1.0000 | 0.0359 | 0.0592 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 14/62 (7 sessions) | 1.0000 | 1.0000 | 0.2500 | 1.0000 | 14/38 (7 sessions) | 1.1429 | 1.0000 | 1.0000 | 1.7500 | -0.1429 | -0.1641 | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 32/62 (12 sessions) | 0.3125 | 0.0000 | 0.0000 | 0.2500 | 21/38 (8 sessions) | 0.2857 | 0.0000 | 0.0000 | 0.0000 | 0.0268 | 0.0416 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 27/62 (11 sessions) | 0.5926 | 0.0000 | 0.0000 | 1.0000 | 18/38 (7 sessions) | 0.1667 | 0.0000 | 0.0000 | 0.0000 | 0.4259 | 0.6092 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 18/62 (9 sessions) | 0.9444 | 1.0000 | 0.2500 | 1.0000 | 17/38 (7 sessions) | 0.5882 | 1.0000 | 0.0000 | 1.0000 | 0.3562 | 0.5273 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 23/62 (10 sessions) | 0.1304 | 0.0000 | 0.0000 | 0.0000 | 17/38 (7 sessions) | 0.1176 | 0.0000 | 0.0000 | 0.0000 | 0.0128 | 0.0377 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 18/62 (9 sessions) | 0.3889 | 0.0000 | 0.0000 | 1.0000 | 17/38 (7 sessions) | 0.2353 | 0.0000 | 0.0000 | 0.0000 | 0.1536 | 0.3258 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 14/62 (7 sessions) | 0.8571 | 1.0000 | 0.0000 | 1.0000 | 14/38 (7 sessions) | 0.5714 | 1.0000 | 0.0000 | 1.0000 | 0.2857 | 0.3519 | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 44/62 (17 sessions) | 0.9773 | 1.0000 | 0.0000 | 2.0000 | 29/38 (11 sessions) | 0.6897 | 0.0000 | 0.0000 | 1.0000 | 0.2876 | 0.2795 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 34/62 (13 sessions) | 1.7647 | 1.0000 | 1.0000 | 2.7500 | 23/38 (9 sessions) | 1.2174 | 1.0000 | 0.0000 | 2.0000 | 0.5473 | 0.3645 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 24/62 (10 sessions) | 2.7917 | 2.0000 | 1.0000 | 4.0000 | 17/38 (7 sessions) | 1.8824 | 1.0000 | 1.0000 | 3.0000 | 0.9093 | 0.4385 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 44/62 (17 sessions) | 1.8555 | 1.6175 | 1.2500 | 2.2250 | 29/38 (11 sessions) | 1.8136 | 1.6650 | 0.9000 | 2.5100 | 0.0419 | 0.0476 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 34/62 (13 sessions) | 2.2995 | 2.2700 | 1.7250 | 2.8162 | 23/38 (9 sessions) | 2.1500 | 1.9100 | 1.3150 | 2.6400 | 0.1495 | 0.1698 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 24/62 (10 sessions) | 2.9716 | 3.0462 | 2.3238 | 3.6088 | 17/38 (7 sessions) | 2.6253 | 2.4400 | 1.8950 | 3.1950 | 0.3463 | 0.3597 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 32/62 (12 sessions) | 2.5228 | 2.4858 | 2.0062 | 2.9237 | 21/38 (8 sessions) | 2.2997 | 2.0480 | 1.5775 | 2.8485 | 0.2231 | 0.2978 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 32/62 (12 sessions) | 3.3899 | 3.3185 | 2.9609 | 4.0349 | 21/38 (8 sessions) | 3.2258 | 3.3955 | 2.9580 | 3.7375 | 0.1640 | 0.2118 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 24/62 (10 sessions) | 4.8176 | 4.8828 | 3.9611 | 5.3427 | 17/38 (7 sessions) | 5.1271 | 4.7175 | 3.9737 | 5.9547 | -0.3095 | -0.2257 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 44/62 (17 sessions) | 0.4880 | 0.5050 | 0.2088 | 0.7688 | 29/38 (11 sessions) | 0.4448 | 0.3789 | 0.1846 | 0.6751 | 0.0433 | 0.1303 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 34/62 (13 sessions) | 0.3278 | 0.2961 | 0.1219 | 0.5529 | 23/38 (9 sessions) | 0.3147 | 0.3404 | 0.1208 | 0.4219 | 0.0131 | 0.0558 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 24/62 (10 sessions) | 0.2076 | 0.1582 | 0.0862 | 0.3175 | 17/38 (7 sessions) | 0.2379 | 0.2066 | 0.0892 | 0.3349 | -0.0303 | -0.1685 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 44/62 (17 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 29/38 (11 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 34/62 (13 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 23/38 (9 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 24/62 (10 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 17/38 (7 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 44/62 (17 sessions) | 0.4602 | 0.5000 | 0.2500 | 0.5000 | 29/38 (11 sessions) | 0.5345 | 0.5000 | 0.5000 | 0.7500 | -0.0743 | -0.3006 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 34/62 (13 sessions) | 0.5029 | 0.5000 | 0.4000 | 0.6000 | 23/38 (9 sessions) | 0.4957 | 0.5000 | 0.4000 | 0.6000 | 0.0073 | 0.0412 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 24/62 (10 sessions) | 0.4886 | 0.5000 | 0.4091 | 0.5455 | 17/38 (7 sessions) | 0.4973 | 0.5000 | 0.4091 | 0.5909 | -0.0087 | -0.0775 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 32/62 (12 sessions) | 1.5129 | 1.3803 | 0.5570 | 2.1686 | 21/38 (8 sessions) | 1.5150 | 1.1183 | 0.6397 | 2.2335 | -0.0021 | -0.0018 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 32/62 (12 sessions) | 0.8099 | 0.7305 | 0.1935 | 1.0535 | 21/38 (8 sessions) | 1.1634 | 1.1006 | 0.6668 | 1.4878 | -0.3536 | -0.4435 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 27/62 (11 sessions) | 0.6396 | 0.6366 | 0.2384 | 0.7377 | 18/38 (7 sessions) | 0.9899 | 0.7990 | 0.5602 | 1.3988 | -0.3503 | -0.6013 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 46/62 (17 sessions) | 1.3349 | 0.7550 | 0.2850 | 1.9750 | 29/38 (13 sessions) | 1.1716 | 0.8800 | 0.2900 | 1.5100 | 0.1633 | 0.1231 | not resampled |
| stage11_2.room_in_atr [SMALL] | 24/62 (11 sessions) | 2.0700 | 1.4201 | 0.5289 | 2.8623 | 14/38 (8 sessions) | 1.2217 | 1.1122 | 0.6847 | 1.7311 | 0.8483 | 0.4462 | not resampled |
| stage11_2.number_of_known_levels_above | 62/62 (20 sessions) | 2.2742 | 2.0000 | 1.0000 | 3.7500 | 38/38 (13 sessions) | 2.5263 | 3.0000 | 1.2500 | 4.0000 | -0.2521 | -0.1370 | not resampled |
| stage11_2.number_of_known_levels_below | 62/62 (20 sessions) | 3.7258 | 4.0000 | 2.2500 | 5.0000 | 38/38 (13 sessions) | 3.4737 | 3.0000 | 2.0000 | 4.7500 | 0.2521 | 0.1370 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 47/62 (17 sessions) | 0.8371 | 0.3700 | 0.1350 | 1.0050 | 29/38 (13 sessions) | 0.7170 | 0.1700 | 0.0700 | 1.1201 | 0.1201 | 0.1145 | not resampled |
| stage11_2.nearest_level_distance_below | 61/62 (20 sessions) | 0.6942 | 0.3200 | 0.1944 | 0.7000 | 38/38 (13 sessions) | 0.4959 | 0.2000 | 0.0825 | 0.5850 | 0.1983 | 0.2010 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 32/62 (12 sessions) | 0.2500 | 0.0000 | 0.0000 | 0.0000 | 21/38 (8 sessions) | 0.1429 | 0.0000 | 0.0000 | 0.0000 | 0.1071 | 0.2158 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 32/62 (12 sessions) | 0.4062 | 0.0000 | 0.0000 | 1.0000 | 21/38 (8 sessions) | 0.3333 | 0.0000 | 0.0000 | 1.0000 | 0.0729 | 0.1101 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 42/62 (16 sessions) | 1.1145 | 0.7800 | 0.3575 | 1.4700 | 27/38 (10 sessions) | 0.9522 | 0.8050 | 0.4450 | 1.3500 | 0.1624 | 0.1921 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 36/62 (14 sessions) | 1.1250 | 1.0675 | 0.5199 | 1.5950 | 26/38 (10 sessions) | 1.2207 | 0.9600 | 0.3094 | 1.6000 | -0.0956 | -0.1034 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 32/62 (12 sessions) | 1.5403 | 1.0867 | 0.5591 | 1.9754 | 21/38 (8 sessions) | 1.6329 | 1.4668 | 0.6610 | 2.5109 | -0.0926 | -0.0755 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 31/62 (12 sessions) | 1.8173 | 1.7279 | 0.8227 | 2.6241 | 21/38 (8 sessions) | 1.3305 | 1.2201 | 0.4089 | 2.1193 | 0.4868 | 0.4411 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG | 60 | 19 | 40 | 20 | 64.52% | 52.63% | 66.67% |
| direction | SHORT | 40 | 15 | 22 | 18 | 35.48% | 47.37% | 55.00% |
| time_bucket | 09:35-10:00 [SMALL] | 27 | 20 | 18 | 9 | 29.03% | 23.68% | 66.67% |
| time_bucket | 10:00-10:30 [SMALL] | 16 | 12 | 10 | 6 | 16.13% | 15.79% | 62.50% |
| time_bucket | 10:30-11:00 [SMALL] | 10 | 7 | 6 | 4 | 9.68% | 10.53% | 60.00% |
| time_bucket | 11:00-12:00 [SMALL] | 11 | 7 | 9 | 2 | 14.52% | 5.26% | 81.82% |
| time_bucket | 12:00-13:30 [SMALL] | 12 | 8 | 9 | 3 | 14.52% | 7.89% | 75.00% |
| time_bucket | 13:30-15:00 [SMALL] | 8 | 5 | 2 | 6 | 3.23% | 15.79% | 25.00% |
| time_bucket | 15:00-close [SMALL] | 16 | 8 | 8 | 8 | 12.90% | 21.05% | 50.00% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 26 | 9 | 15 | 11 | 24.19% | 28.95% | 57.69% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 19 | 9 | 12 | 7 | 19.35% | 18.42% | 63.16% |
| ema9_20_alignment | EMA_UNAVAILABLE | 55 | 20 | 35 | 20 | 56.45% | 52.63% | 63.64% |
| price_vwap_alignment | VWAP_ALIGNED | 88 | 20 | 55 | 33 | 88.71% | 86.84% | 62.50% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 12 | 4 | 7 | 5 | 11.29% | 13.16% | 58.33% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED | 46 | 15 | 28 | 18 | 45.16% | 47.37% | 60.87% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 18 | 7 | 12 | 6 | 19.35% | 15.79% | 66.67% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE | 36 | 20 | 22 | 14 | 35.48% | 36.84% | 61.11% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED | 31 | 10 | 19 | 12 | 30.65% | 31.58% | 61.29% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 14 | 9 | 8 | 6 | 12.90% | 15.79% | 57.14% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 55 | 20 | 35 | 20 | 56.45% | 52.63% | 63.64% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 16 | 8 | 10 | 6 | 16.13% | 15.79% | 62.50% |
| prior_ema_cross | NO_PRIOR_CROSS | 69 | 20 | 44 | 25 | 70.97% | 65.79% | 63.77% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 15 | 8 | 8 | 7 | 12.90% | 18.42% | 53.33% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 66 | 16 | 41 | 25 | 66.13% | 65.79% | 62.12% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL | 33 | 17 | 21 | 12 | 33.87% | 31.58% | 63.64% |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 1 | 1 | 0 | 1 | 0.00% | 2.63% | 0.00% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 6 | 4 | 3 | 3 | 4.84% | 7.89% | 50.00% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 8 | 4 | 4 | 4 | 6.45% | 10.53% | 50.00% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 4 | 4 | 2 | 2 | 3.23% | 5.26% | 50.00% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 6 | 3 | 4 | 2 | 6.45% | 5.26% | 66.67% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 5 | 4 | 5 | 0 | 8.06% | 0.00% | 100.00% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 9 | 5 | 6 | 3 | 9.68% | 7.89% | 66.67% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 25 | 6 | 16 | 9 | 25.81% | 23.68% | 64.00% |
| stage11_2.room_bucket | UNAVAILABLE_ATR | 37 | 16 | 22 | 15 | 35.48% | 39.47% | 59.46% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 100 | 20 | 62 | 38 | 100.00% | 100.00% | 62.00% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 11 | 6 | 6 | 5 | 9.68% | 13.16% | 54.55% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 15 | 7 | 10 | 5 | 16.13% | 13.16% | 66.67% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 21 | 9 | 12 | 9 | 19.35% | 23.68% | 57.14% |
| stage11_3.structure | UNAVAILABLE | 53 | 20 | 34 | 19 | 54.84% | 50.00% | 64.15% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 16 | 8 | 10 | 6 | 16.13% | 15.79% | 62.50% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED | 31 | 10 | 18 | 13 | 29.03% | 34.21% | 58.06% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 53 | 20 | 34 | 19 | 54.84% | 50.00% | 64.15% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 26 | 10 | 16 | 10 | 25.81% | 26.32% | 61.54% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 26 | 9 | 15 | 11 | 24.19% | 28.95% | 57.69% |
| stage11_3.high_structure | UNAVAILABLE | 48 | 20 | 31 | 17 | 50.00% | 44.74% | 64.58% |
| stage11_3.low_structure | HIGHER_LOW | 32 | 11 | 19 | 13 | 30.65% | 34.21% | 59.38% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 18 | 9 | 10 | 8 | 16.13% | 21.05% | 55.56% |
| stage11_3.low_structure | UNAVAILABLE | 50 | 20 | 33 | 17 | 53.23% | 44.74% | 66.00% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE | 33 | 20 | 22 | 11 | 35.48% | 28.95% | 66.67% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 19 | 5 | 11 | 8 | 17.74% | 21.05% | 57.89% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 10 | 5 | 5 | 5 | 8.06% | 13.16% | 50.00% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL | 38 | 14 | 24 | 14 | 38.71% | 36.84% | 63.16% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 100 | 20 | 62 | 38 | 100.00% | 100.00% | 62.00% |


### 2026-06


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 56/56 (21 sessions) | 2.0595 | 2.2000 | 1.3825 | 2.5100 | 23/23 (12 sessions) | 2.0522 | 2.0075 | 1.3550 | 2.8800 | 0.0073 | 0.0096 | not resampled |
| body_size [SMALL] | 56/56 (21 sessions) | 1.2634 | 0.8725 | 0.5200 | 1.3174 | 23/23 (12 sessions) | 0.8881 | 0.7600 | 0.3775 | 1.4000 | 0.3753 | 0.3357 | not resampled |
| directional_body [SMALL] | 56/56 (21 sessions) | 1.2634 | 0.8725 | 0.5200 | 1.3174 | 23/23 (12 sessions) | 0.8881 | 0.7600 | 0.3775 | 1.4000 | 0.3753 | 0.3357 | not resampled |
| candle_range [SMALL] | 56/56 (21 sessions) | 1.6639 | 1.3225 | 0.8362 | 1.9250 | 23/23 (12 sessions) | 1.4162 | 1.1100 | 0.7750 | 1.8950 | 0.2477 | 0.2123 | not resampled |
| body_range_ratio [SMALL] | 56/56 (21 sessions) | 0.6963 | 0.7120 | 0.5945 | 0.8692 | 23/23 (12 sessions) | 0.6002 | 0.5509 | 0.4542 | 0.7774 | 0.0960 | 0.4579 | not resampled |
| directional_body_range_ratio [SMALL] | 56/56 (21 sessions) | 0.6963 | 0.7120 | 0.5945 | 0.8692 | 23/23 (12 sessions) | 0.6002 | 0.5509 | 0.4542 | 0.7774 | 0.0960 | 0.4579 | not resampled |
| close_location [SMALL] | 56/56 (21 sessions) | 0.5111 | 0.4914 | 0.1478 | 0.9034 | 23/23 (12 sessions) | 0.6363 | 0.7698 | 0.5008 | 0.8698 | -0.1252 | -0.3470 | not resampled |
| directional_close_location [SMALL] | 56/56 (21 sessions) | 0.8519 | 0.8951 | 0.7646 | 0.9724 | 23/23 (12 sessions) | 0.7888 | 0.8214 | 0.6725 | 0.9117 | 0.0631 | 0.4381 | not resampled |
| distance_beyond_level [SMALL] | 56/56 (21 sessions) | 0.7608 | 0.4950 | 0.1802 | 0.8345 | 23/23 (12 sessions) | 0.1986 | 0.1500 | 0.0850 | 0.2650 | 0.5622 | 0.7255 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 29/56 (11 sessions) | 0.6018 | 0.3705 | 0.1887 | 0.5699 | 9/23 (4 sessions) | 0.1752 | 0.0877 | 0.0195 | 0.1767 | 0.4266 | 0.5006 | not resampled |
| candle_volume [SMALL] | 56/56 (21 sessions) | 739001.7500 | 607479.5000 | 397325.2500 | 853633.0000 | 23/23 (12 sessions) | 638861.6957 | 594063.0000 | 515641.0000 | 773689.5000 | 100140.0543 | 0.2042 | not resampled |
| relative_volume_prior_6 [SMALL] | 40/56 (17 sessions) | 1.4248 | 0.8956 | 0.7465 | 1.6191 | 13/23 (6 sessions) | 1.0008 | 0.8689 | 0.7763 | 1.1818 | 0.4240 | 0.3149 | not resampled |
| atr14 [SMALL] | 29/56 (11 sessions) | 1.3300 | 1.1740 | 0.9617 | 1.7175 | 9/23 (4 sessions) | 1.4505 | 1.7107 | 0.9264 | 1.8844 | -0.1206 | -0.2366 | not resampled |
| minutes_since_open [SMALL] | 56/56 (21 sessions) | 111.0714 | 72.5000 | 30.0000 | 183.7500 | 23/23 (12 sessions) | 85.2174 | 50.0000 | 25.0000 | 155.0000 | 25.8540 | 0.2645 | not resampled |
| minutes_since_ema_cross [SMALL] | 14/56 (6 sessions) | 28.9286 | 15.0000 | 0.0000 | 38.7500 | 4/23 (3 sessions) | 23.7500 | 20.0000 | 15.0000 | 28.7500 | 5.1786 | 0.1514 | not resampled |
| break_attempt_rank [SMALL] | 56/56 (21 sessions) | 6.3393 | 5.0000 | 2.7500 | 8.2500 | 23/23 (12 sessions) | 5.3478 | 4.0000 | 3.0000 | 7.5000 | 0.9915 | 0.2006 | not resampled |
| valid_hold_sequence_rank [SMALL] | 56/56 (21 sessions) | 3.2857 | 3.0000 | 1.7500 | 4.2500 | 23/23 (12 sessions) | 2.7391 | 2.0000 | 1.0000 | 4.0000 | 0.5466 | 0.2690 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 23/56 (10 sessions) | 0.5147 | 0.3185 | 0.1593 | 0.6346 | 7/23 (4 sessions) | 0.2932 | 0.2760 | 0.1680 | 0.3846 | 0.2215 | 0.4869 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 23/56 (10 sessions) | 0.3917 | 0.3454 | 0.1171 | 0.5855 | 7/23 (4 sessions) | 0.2964 | 0.3586 | 0.1037 | 0.4503 | 0.0953 | 0.3320 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 35/56 (15 sessions) | -0.0299 | -0.0165 | -0.2204 | 0.1479 | 12/23 (6 sessions) | 0.0191 | 0.0863 | -0.0314 | 0.1086 | -0.0490 | -0.1462 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 34/56 (14 sessions) | -0.0245 | -0.0078 | -0.1484 | 0.1367 | 11/23 (5 sessions) | -0.0630 | 0.0096 | -0.1282 | 0.0313 | 0.0386 | 0.1785 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 32/56 (13 sessions) | -0.0283 | -0.0261 | -0.0966 | 0.1078 | 9/23 (4 sessions) | -0.0582 | 0.0001 | -0.1329 | 0.0439 | 0.0299 | 0.1608 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 23/56 (10 sessions) | -0.0652 | -0.0396 | -0.1447 | 0.0324 | 7/23 (4 sessions) | 0.0380 | 0.0578 | 0.0266 | 0.0779 | -0.1032 | -0.5495 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 22/56 (10 sessions) | -0.0455 | -0.0417 | -0.0982 | 0.0296 | 7/23 (4 sessions) | 0.0029 | 0.0255 | -0.0401 | 0.0404 | -0.0484 | -0.4427 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 21/56 (9 sessions) | -0.0565 | -0.0428 | -0.1048 | 0.0269 | 7/23 (4 sessions) | -0.0017 | 0.0236 | -0.0548 | 0.0384 | -0.0548 | -0.5270 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 56/56 (21 sessions) | -0.0329 | 0.0063 | -0.0726 | 0.0628 | 23/23 (12 sessions) | 0.0273 | 0.0176 | -0.0024 | 0.0618 | -0.0602 | -0.2734 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 49/56 (19 sessions) | -0.0213 | 0.0039 | -0.0496 | 0.0404 | 20/23 (11 sessions) | 0.0113 | 0.0072 | -0.0111 | 0.0165 | -0.0326 | -0.2656 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 46/56 (19 sessions) | -0.0065 | 0.0038 | -0.0457 | 0.0339 | 19/23 (11 sessions) | 0.0184 | 0.0105 | -0.0022 | 0.0283 | -0.0249 | -0.3273 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 19/56 (8 sessions) | 0.4737 | 0.0000 | 0.0000 | 1.0000 | 7/23 (4 sessions) | 0.5714 | 0.0000 | 0.0000 | 1.0000 | -0.0977 | -0.1481 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 18/56 (8 sessions) | 0.8889 | 1.0000 | 0.0000 | 1.7500 | 6/23 (4 sessions) | 0.8333 | 0.5000 | 0.0000 | 1.7500 | 0.0556 | 0.0639 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 9/56 (6 sessions) | 1.4444 | 1.0000 | 1.0000 | 3.0000 | 1/23 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.4444 | N/A | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 29/56 (11 sessions) | 0.2414 | 0.0000 | 0.0000 | 0.0000 | 9/23 (4 sessions) | 0.1111 | 0.0000 | 0.0000 | 0.0000 | 0.1303 | 0.3139 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 23/56 (10 sessions) | 0.5652 | 0.0000 | 0.0000 | 1.0000 | 7/23 (4 sessions) | 0.1429 | 0.0000 | 0.0000 | 0.0000 | 0.4224 | 0.6894 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 16/56 (8 sessions) | 0.8750 | 1.0000 | 0.7500 | 1.0000 | 6/23 (4 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.7500 | 0.5417 | 0.9102 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 19/56 (8 sessions) | 0.2105 | 0.0000 | 0.0000 | 0.0000 | 7/23 (4 sessions) | 0.1429 | 0.0000 | 0.0000 | 0.0000 | 0.0677 | 0.1654 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 18/56 (8 sessions) | 0.5000 | 0.0000 | 0.0000 | 1.0000 | 6/23 (4 sessions) | 0.1667 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5774 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 9/56 (6 sessions) | 0.7778 | 1.0000 | 0.0000 | 1.0000 | 1/23 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.7778 | N/A | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 43/56 (18 sessions) | 1.0465 | 1.0000 | 0.0000 | 2.0000 | 16/23 (9 sessions) | 1.8125 | 2.0000 | 1.0000 | 2.2500 | -0.7660 | -0.6707 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 32/56 (13 sessions) | 1.6875 | 1.0000 | 0.0000 | 3.0000 | 9/23 (4 sessions) | 2.4444 | 2.0000 | 1.0000 | 4.0000 | -0.7569 | -0.4485 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 20/56 (8 sessions) | 2.8500 | 1.0000 | 0.7500 | 5.0000 | 7/23 (4 sessions) | 3.8571 | 5.0000 | 1.0000 | 6.0000 | -1.0071 | -0.3339 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 43/56 (18 sessions) | 2.9407 | 2.5400 | 1.6900 | 3.7650 | 16/23 (9 sessions) | 2.6263 | 2.0700 | 1.4475 | 3.8575 | 0.3144 | 0.2086 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 32/56 (13 sessions) | 3.9778 | 3.5100 | 2.4475 | 5.3549 | 9/23 (4 sessions) | 4.1690 | 5.2250 | 2.5800 | 5.6500 | -0.1911 | -0.0916 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 20/56 (8 sessions) | 5.7394 | 5.9625 | 3.7400 | 7.1350 | 7/23 (4 sessions) | 5.6721 | 5.9050 | 3.9600 | 7.2700 | 0.0673 | 0.0293 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 29/56 (11 sessions) | 2.2567 | 2.1466 | 1.6390 | 2.5615 | 9/23 (4 sessions) | 2.1509 | 2.1386 | 1.5871 | 2.2213 | 0.1058 | 0.1123 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 29/56 (11 sessions) | 2.9898 | 2.6411 | 2.3626 | 3.3890 | 9/23 (4 sessions) | 2.8651 | 2.9493 | 2.5517 | 3.3027 | 0.1247 | 0.1297 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 20/56 (8 sessions) | 4.6767 | 4.4776 | 3.9645 | 5.7072 | 7/23 (4 sessions) | 4.5652 | 4.2496 | 3.7903 | 5.0829 | 0.1115 | 0.0939 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 43/56 (18 sessions) | 0.4812 | 0.4450 | 0.2554 | 0.7193 | 16/23 (9 sessions) | 0.3533 | 0.2813 | 0.2106 | 0.5294 | 0.1279 | 0.4564 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 32/56 (13 sessions) | 0.2778 | 0.2271 | 0.1359 | 0.3812 | 9/23 (4 sessions) | 0.1999 | 0.1468 | 0.1213 | 0.2370 | 0.0778 | 0.4349 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 20/56 (8 sessions) | 0.1970 | 0.2211 | 0.0503 | 0.2686 | 7/23 (4 sessions) | 0.1780 | 0.1392 | 0.0302 | 0.2329 | 0.0189 | 0.1206 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 43/56 (18 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 16/23 (9 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 32/56 (13 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9/23 (4 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 20/56 (8 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 7/23 (4 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 43/56 (18 sessions) | 0.5407 | 0.5000 | 0.5000 | 0.7500 | 16/23 (9 sessions) | 0.5312 | 0.5000 | 0.4375 | 0.7500 | 0.0094 | 0.0376 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 32/56 (13 sessions) | 0.5500 | 0.6000 | 0.4000 | 0.6000 | 9/23 (4 sessions) | 0.4889 | 0.5000 | 0.4000 | 0.6000 | 0.0611 | 0.4533 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 20/56 (8 sessions) | 0.5659 | 0.5455 | 0.5000 | 0.6023 | 7/23 (4 sessions) | 0.4935 | 0.5000 | 0.4545 | 0.5227 | 0.0724 | 0.9672 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 29/56 (11 sessions) | 1.4614 | 1.2553 | 0.9354 | 1.7175 | 9/23 (4 sessions) | 0.9118 | 0.6755 | 0.5873 | 0.7558 | 0.5496 | 0.6118 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 29/56 (11 sessions) | 0.7932 | 0.6192 | 0.2853 | 1.1924 | 9/23 (4 sessions) | 0.6856 | 0.4660 | 0.2527 | 0.9179 | 0.1077 | 0.1723 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 23/56 (10 sessions) | 0.5580 | 0.4094 | 0.1657 | 0.9160 | 7/23 (4 sessions) | 0.7303 | 0.5593 | 0.3804 | 1.1367 | -0.1723 | -0.3323 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 49/56 (20 sessions) | 2.6185 | 1.9450 | 0.8500 | 3.4600 | 16/23 (9 sessions) | 2.1200 | 2.2500 | 1.5862 | 2.4525 | 0.4985 | 0.2255 | not resampled |
| stage11_2.room_in_atr [SMALL] | 26/56 (10 sessions) | 2.4154 | 1.5437 | 0.9337 | 2.8582 | 7/23 (3 sessions) | 1.7556 | 1.3620 | 1.2769 | 1.4617 | 0.6598 | 0.3018 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 56/56 (21 sessions) | 2.8214 | 3.5000 | 1.0000 | 4.0000 | 23/23 (12 sessions) | 1.8261 | 2.0000 | 0.5000 | 2.0000 | 0.9953 | 0.5922 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 56/56 (21 sessions) | 3.1786 | 2.5000 | 2.0000 | 5.0000 | 23/23 (12 sessions) | 4.1739 | 4.0000 | 4.0000 | 5.5000 | -0.9953 | -0.5922 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 50/56 (20 sessions) | 1.6284 | 1.0450 | 0.2421 | 1.9162 | 17/23 (9 sessions) | 1.5202 | 1.7300 | 0.5100 | 2.3300 | 0.1083 | 0.0600 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 55/56 (21 sessions) | 1.4949 | 0.6200 | 0.2550 | 1.9850 | 22/23 (12 sessions) | 0.5588 | 0.1650 | 0.0775 | 0.2725 | 0.9360 | 0.5037 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 29/56 (11 sessions) | 0.1724 | 0.0000 | 0.0000 | 0.0000 | 9/23 (4 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1724 | 0.4176 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 29/56 (11 sessions) | 0.3103 | 0.0000 | 0.0000 | 0.0000 | 9/23 (4 sessions) | 0.1111 | 0.0000 | 0.0000 | 0.0000 | 0.1992 | 0.3589 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 39/56 (16 sessions) | 2.0748 | 1.3100 | 0.4600 | 2.8400 | 15/23 (8 sessions) | 1.6357 | 1.3500 | 0.6800 | 2.4300 | 0.4391 | 0.2437 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 39/56 (15 sessions) | 1.9629 | 1.3200 | 0.7350 | 3.0325 | 14/23 (7 sessions) | 1.9550 | 2.3000 | 0.9900 | 2.7400 | 0.0079 | 0.0049 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 29/56 (11 sessions) | 1.6521 | 1.2484 | 0.6084 | 2.7209 | 9/23 (4 sessions) | 1.3106 | 1.1940 | 0.5932 | 1.9699 | 0.3415 | 0.2688 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 29/56 (11 sessions) | 1.5806 | 1.4917 | 0.4471 | 2.3099 | 9/23 (4 sessions) | 1.6057 | 1.5216 | 1.2842 | 1.6776 | -0.0250 | -0.0225 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG | 46 | 16 | 28 | 18 | 50.00% | 78.26% | 60.87% |
| direction | SHORT | 33 | 14 | 28 | 5 | 50.00% | 21.74% | 84.85% |
| time_bucket | 09:35-10:00 [SMALL] | 20 | 17 | 13 | 7 | 23.21% | 30.43% | 65.00% |
| time_bucket | 10:00-10:30 [SMALL] | 18 | 12 | 11 | 7 | 19.64% | 30.43% | 61.11% |
| time_bucket | 10:30-11:00 [SMALL] | 8 | 7 | 6 | 2 | 10.71% | 8.70% | 75.00% |
| time_bucket | 11:00-12:00 [SMALL] | 9 | 7 | 8 | 1 | 14.29% | 4.35% | 88.89% |
| time_bucket | 12:00-13:30 [SMALL] | 16 | 7 | 11 | 5 | 19.64% | 21.74% | 68.75% |
| time_bucket | 13:30-15:00 [SMALL] | 4 | 4 | 4 | 0 | 7.14% | 0.00% | 100.00% |
| time_bucket | 15:00-close [SMALL] | 4 | 3 | 3 | 1 | 5.36% | 4.35% | 75.00% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 24 | 8 | 17 | 7 | 30.36% | 30.43% | 70.83% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 6 | 4 | 6 | 0 | 10.71% | 0.00% | 100.00% |
| ema9_20_alignment | EMA_UNAVAILABLE | 49 | 21 | 33 | 16 | 58.93% | 69.57% | 67.35% |
| price_vwap_alignment | VWAP_ALIGNED | 74 | 21 | 51 | 23 | 91.07% | 100.00% | 68.92% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 5 | 3 | 5 | 0 | 8.93% | 0.00% | 100.00% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED | 36 | 13 | 28 | 8 | 50.00% | 34.78% | 77.78% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 14 | 8 | 10 | 4 | 17.86% | 17.39% | 71.43% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 29 | 21 | 18 | 11 | 32.14% | 47.83% | 62.07% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 22 | 8 | 16 | 6 | 28.57% | 26.09% | 72.73% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 8 | 6 | 7 | 1 | 12.50% | 4.35% | 87.50% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 49 | 21 | 33 | 16 | 58.93% | 69.57% | 67.35% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 14 | 6 | 10 | 4 | 17.86% | 17.39% | 71.43% |
| prior_ema_cross | NO_PRIOR_CROSS | 61 | 21 | 42 | 19 | 75.00% | 82.61% | 68.85% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 4 | 2 | 4 | 0 | 7.14% | 0.00% | 100.00% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 45 | 11 | 32 | 13 | 57.14% | 56.52% | 71.11% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL | 32 | 15 | 23 | 9 | 41.07% | 39.13% | 71.88% |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 2 | 2 | 1 | 1 | 1.79% | 4.35% | 50.00% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 4 | 3 | 3 | 1 | 5.36% | 4.35% | 75.00% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 9 | 4 | 5 | 4 | 8.93% | 17.39% | 55.56% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 5 | 3 | 4 | 1 | 7.14% | 4.35% | 80.00% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 4 | 3 | 4 | 0 | 7.14% | 0.00% | 100.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 7 | 4 | 6 | 1 | 10.71% | 4.35% | 85.71% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 4 | 3 | 4 | 0 | 7.14% | 0.00% | 100.00% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 14 | 4 | 7 | 7 | 12.50% | 30.43% | 50.00% |
| stage11_2.room_bucket | UNAVAILABLE_ATR | 32 | 20 | 23 | 9 | 41.07% | 39.13% | 71.88% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 79 | 21 | 56 | 23 | 100.00% | 100.00% | 70.89% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 8 | 7 | 7 | 1 | 12.50% | 4.35% | 87.50% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 10 | 6 | 6 | 4 | 10.71% | 17.39% | 60.00% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 13 | 7 | 11 | 2 | 19.64% | 8.70% | 84.62% |
| stage11_3.structure | UNAVAILABLE | 48 | 21 | 32 | 16 | 57.14% | 69.57% | 66.67% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 11 | 8 | 6 | 5 | 10.71% | 21.74% | 54.55% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 20 | 9 | 18 | 2 | 32.14% | 8.70% | 90.00% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 48 | 21 | 32 | 16 | 57.14% | 69.57% | 66.67% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 17 | 8 | 12 | 5 | 21.43% | 21.74% | 70.59% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 19 | 10 | 16 | 3 | 28.57% | 13.04% | 84.21% |
| stage11_3.high_structure | UNAVAILABLE | 43 | 21 | 28 | 15 | 50.00% | 65.22% | 65.12% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 25 | 11 | 18 | 7 | 32.14% | 30.43% | 72.00% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 14 | 8 | 13 | 1 | 23.21% | 4.35% | 92.86% |
| stage11_3.low_structure | UNAVAILABLE | 40 | 21 | 25 | 15 | 44.64% | 65.22% | 62.50% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 28 | 21 | 19 | 9 | 33.93% | 39.13% | 67.86% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 9 | 4 | 5 | 4 | 8.93% | 17.39% | 55.56% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 6 | 4 | 3 | 3 | 5.36% | 13.04% | 50.00% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL | 36 | 11 | 29 | 7 | 51.79% | 30.43% | 80.56% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 79 | 21 | 56 | 23 | 100.00% | 100.00% | 70.89% |


### 2026-07


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 61/61 (22 sessions) | 1.5029 | 1.4600 | 1.2275 | 1.6100 | 22/22 (11 sessions) | 1.4865 | 1.4600 | 1.3000 | 1.6200 | 0.0164 | 0.0358 | not resampled |
| body_size [SMALL] | 61/61 (22 sessions) | 0.7704 | 0.7000 | 0.3685 | 0.9800 | 22/22 (11 sessions) | 0.7561 | 0.5450 | 0.3150 | 1.0100 | 0.0143 | 0.0267 | not resampled |
| directional_body [SMALL] | 61/61 (22 sessions) | 0.7701 | 0.7000 | 0.3685 | 0.9800 | 22/22 (11 sessions) | 0.7561 | 0.5450 | 0.3150 | 1.0100 | 0.0139 | 0.0260 | not resampled |
| candle_range [SMALL] | 61/61 (22 sessions) | 1.1980 | 1.0600 | 0.7000 | 1.3799 | 22/22 (11 sessions) | 1.2461 | 1.0100 | 0.7575 | 1.7662 | -0.0482 | -0.0643 | not resampled |
| body_range_ratio [SMALL] | 61/61 (22 sessions) | 0.6269 | 0.6597 | 0.5023 | 0.8039 | 22/22 (11 sessions) | 0.5655 | 0.5710 | 0.4203 | 0.7346 | 0.0614 | 0.2596 | not resampled |
| directional_body_range_ratio [SMALL] | 61/61 (22 sessions) | 0.6260 | 0.6597 | 0.5023 | 0.8039 | 22/22 (11 sessions) | 0.5655 | 0.5710 | 0.4203 | 0.7346 | 0.0605 | 0.2539 | not resampled |
| close_location [SMALL] | 61/61 (22 sessions) | 0.4810 | 0.4742 | 0.0952 | 0.8791 | 22/22 (11 sessions) | 0.4850 | 0.5474 | 0.1635 | 0.7687 | -0.0040 | -0.0110 | not resampled |
| directional_close_location [SMALL] | 61/61 (22 sessions) | 0.8221 | 0.8868 | 0.7625 | 0.9492 | 22/22 (11 sessions) | 0.7984 | 0.7887 | 0.7148 | 0.9466 | 0.0237 | 0.1354 | not resampled |
| distance_beyond_level [SMALL] | 61/61 (22 sessions) | 0.3615 | 0.3200 | 0.1600 | 0.4580 | 22/22 (11 sessions) | 0.1958 | 0.1650 | 0.0500 | 0.2825 | 0.1658 | 0.6064 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 33/61 (17 sessions) | 0.3594 | 0.3110 | 0.1745 | 0.5241 | 14/22 (7 sessions) | 0.1638 | 0.1091 | 0.0641 | 0.2229 | 0.1956 | 0.8380 | not resampled |
| candle_volume [SMALL] | 61/61 (22 sessions) | 583691.9508 | 540407.0000 | 344255.0000 | 746984.0000 | 22/22 (11 sessions) | 601344.9545 | 526649.5000 | 403023.7500 | 687955.0000 | -17653.0037 | -0.0486 | not resampled |
| relative_volume_prior_6 [SMALL] | 40/61 (19 sessions) | 1.2168 | 1.0123 | 0.7544 | 1.2501 | 20/22 (11 sessions) | 1.2525 | 0.9261 | 0.7624 | 1.3452 | -0.0357 | -0.0314 | not resampled |
| atr14 [SMALL] | 33/61 (17 sessions) | 0.9551 | 0.9126 | 0.7672 | 1.1712 | 14/22 (7 sessions) | 1.0147 | 0.9208 | 0.7875 | 1.2538 | -0.0595 | -0.2091 | not resampled |
| minutes_since_open [SMALL] | 61/61 (22 sessions) | 108.6066 | 70.0000 | 25.0000 | 165.0000 | 22/22 (11 sessions) | 127.2727 | 87.5000 | 51.2500 | 202.5000 | -18.6662 | -0.1798 | not resampled |
| minutes_since_ema_cross [SMALL] | 17/61 (12 sessions) | 70.2941 | 70.0000 | 25.0000 | 95.0000 | 7/22 (4 sessions) | 100.7143 | 115.0000 | 55.0000 | 145.0000 | -30.4202 | -0.5112 | not resampled |
| break_attempt_rank [SMALL] | 61/61 (22 sessions) | 5.4098 | 5.0000 | 2.0000 | 8.0000 | 22/22 (11 sessions) | 5.6818 | 6.0000 | 4.2500 | 7.0000 | -0.2720 | -0.0833 | not resampled |
| valid_hold_sequence_rank [SMALL] | 61/61 (22 sessions) | 2.8197 | 2.0000 | 1.0000 | 4.0000 | 22/22 (11 sessions) | 3.0909 | 3.0000 | 2.0000 | 4.0000 | -0.2712 | -0.1586 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 23/61 (16 sessions) | 0.4221 | 0.4030 | 0.2025 | 0.5709 | 10/22 (5 sessions) | 0.5003 | 0.4259 | 0.2232 | 0.6950 | -0.0782 | -0.2591 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 23/61 (16 sessions) | 0.4895 | 0.4821 | 0.2418 | 0.7003 | 10/22 (5 sessions) | 0.5106 | 0.5230 | 0.2807 | 0.6726 | -0.0210 | -0.0726 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 40/61 (19 sessions) | 0.0159 | 0.0045 | -0.1319 | 0.1584 | 18/22 (10 sessions) | -0.1017 | -0.0761 | -0.2740 | 0.1100 | 0.1176 | 0.4918 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 39/61 (19 sessions) | 0.0080 | -0.0060 | -0.0902 | 0.1047 | 16/22 (9 sessions) | -0.0633 | -0.0337 | -0.2089 | 0.0614 | 0.0713 | 0.3965 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 38/61 (18 sessions) | -0.0062 | 0.0072 | -0.1035 | 0.0799 | 14/22 (7 sessions) | -0.0712 | -0.0568 | -0.2197 | 0.0793 | 0.0650 | 0.3896 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 22/61 (15 sessions) | 0.0206 | 0.0060 | -0.0688 | 0.0670 | 9/22 (5 sessions) | -0.0324 | -0.0273 | -0.1293 | 0.0724 | 0.0530 | 0.3787 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 22/61 (15 sessions) | 0.0199 | -0.0093 | -0.0524 | 0.0528 | 8/22 (5 sessions) | 0.0179 | 0.0283 | -0.0487 | 0.0945 | 0.0020 | 0.0167 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 20/61 (14 sessions) | 0.0065 | -0.0064 | -0.0417 | 0.0495 | 8/22 (5 sessions) | 0.0256 | 0.0152 | -0.0494 | 0.1079 | -0.0191 | -0.1707 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 61/61 (22 sessions) | -0.0071 | 0.0014 | -0.0368 | 0.0698 | 22/22 (11 sessions) | -0.0008 | 0.0254 | -0.0480 | 0.0491 | -0.0063 | -0.0433 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 53/61 (22 sessions) | -0.0044 | -0.0031 | -0.0277 | 0.0372 | 22/22 (11 sessions) | 0.0042 | 0.0114 | -0.0359 | 0.0389 | -0.0085 | -0.1072 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 50/61 (21 sessions) | -0.0001 | 0.0028 | -0.0256 | 0.0261 | 21/22 (11 sessions) | -0.0018 | 0.0022 | -0.0459 | 0.0408 | 0.0017 | 0.0272 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 18/61 (13 sessions) | 0.2222 | 0.0000 | 0.0000 | 0.0000 | 7/22 (4 sessions) | 0.1429 | 0.0000 | 0.0000 | 0.0000 | 0.0794 | 0.1558 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 17/61 (12 sessions) | 0.5294 | 0.0000 | 0.0000 | 1.0000 | 7/22 (4 sessions) | 0.2857 | 0.0000 | 0.0000 | 0.5000 | 0.2437 | 0.3347 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 9/61 (8 sessions) | 0.6667 | 1.0000 | 0.0000 | 1.0000 | 6/22 (4 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.7500 | 0.3333 | 0.6583 | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 33/61 (17 sessions) | 0.4242 | 0.0000 | 0.0000 | 1.0000 | 14/22 (7 sessions) | 0.3571 | 0.0000 | 0.0000 | 1.0000 | 0.0671 | 0.1083 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 23/61 (16 sessions) | 0.7826 | 1.0000 | 0.0000 | 1.0000 | 10/22 (5 sessions) | 0.5000 | 0.0000 | 0.0000 | 1.0000 | 0.2826 | 0.4466 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 16/61 (11 sessions) | 1.1875 | 1.0000 | 1.0000 | 1.0000 | 7/22 (4 sessions) | 0.7143 | 1.0000 | 0.0000 | 1.0000 | 0.4732 | 0.6904 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 18/61 (13 sessions) | 0.1111 | 0.0000 | 0.0000 | 0.0000 | 7/22 (4 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1111 | 0.3997 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 17/61 (12 sessions) | 0.3529 | 0.0000 | 0.0000 | 1.0000 | 7/22 (4 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.3529 | 0.8402 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 9/61 (8 sessions) | 0.6667 | 1.0000 | 0.0000 | 1.0000 | 6/22 (4 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | 0.1667 | 0.3212 | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 41/61 (20 sessions) | 0.8293 | 1.0000 | 0.0000 | 1.0000 | 20/22 (11 sessions) | 0.9500 | 0.5000 | 0.0000 | 1.0000 | -0.1207 | -0.1087 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 38/61 (18 sessions) | 1.9737 | 2.0000 | 0.2500 | 3.0000 | 14/22 (7 sessions) | 0.9286 | 1.0000 | 0.0000 | 1.0000 | 1.0451 | 0.6386 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 19/61 (14 sessions) | 2.0526 | 1.0000 | 1.0000 | 3.0000 | 8/22 (5 sessions) | 1.0000 | 1.0000 | 0.0000 | 2.0000 | 1.0526 | 0.5644 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 41/61 (20 sessions) | 2.4696 | 2.2500 | 1.4900 | 3.0700 | 20/22 (11 sessions) | 2.4760 | 2.2200 | 1.7775 | 3.3926 | -0.0063 | -0.0053 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 38/61 (18 sessions) | 3.2969 | 3.0125 | 2.4138 | 4.1650 | 14/22 (7 sessions) | 3.3325 | 2.7400 | 2.2400 | 4.5075 | -0.0356 | -0.0246 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 19/61 (14 sessions) | 4.1821 | 4.1900 | 3.1000 | 4.8150 | 8/22 (5 sessions) | 4.0950 | 3.7500 | 2.6775 | 4.9725 | 0.0871 | 0.0513 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 33/61 (17 sessions) | 2.3501 | 2.0989 | 1.8622 | 2.7492 | 14/22 (7 sessions) | 2.2847 | 2.3146 | 1.7101 | 2.7180 | 0.0654 | 0.0813 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 33/61 (17 sessions) | 3.3427 | 3.2889 | 2.5457 | 3.8065 | 14/22 (7 sessions) | 3.1015 | 3.1589 | 2.5687 | 3.5483 | 0.2412 | 0.2636 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 19/61 (14 sessions) | 4.9520 | 4.8832 | 4.0540 | 5.6526 | 8/22 (5 sessions) | 4.5760 | 4.2683 | 3.7366 | 5.1001 | 0.3759 | 0.2870 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 41/61 (20 sessions) | 0.4614 | 0.3960 | 0.2319 | 0.7239 | 20/22 (11 sessions) | 0.4416 | 0.4747 | 0.2058 | 0.6601 | 0.0198 | 0.0683 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 38/61 (18 sessions) | 0.2686 | 0.2084 | 0.0879 | 0.3767 | 14/22 (7 sessions) | 0.3406 | 0.4033 | 0.1331 | 0.5240 | -0.0720 | -0.3261 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 19/61 (14 sessions) | 0.2274 | 0.2475 | 0.0881 | 0.3363 | 8/22 (5 sessions) | 0.2273 | 0.2326 | 0.1080 | 0.2805 | 0.0000 | 0.0001 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 41/61 (20 sessions) | 0.9951 | 1.0000 | 1.0000 | 1.0000 | 20/22 (11 sessions) | 0.9900 | 1.0000 | 1.0000 | 1.0000 | 0.0051 | 0.1418 | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 38/61 (18 sessions) | 0.9952 | 1.0000 | 1.0000 | 1.0000 | 14/22 (7 sessions) | 0.9935 | 1.0000 | 1.0000 | 1.0000 | 0.0017 | 0.0791 | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 19/61 (14 sessions) | 0.9954 | 1.0000 | 1.0000 | 1.0000 | 8/22 (5 sessions) | 0.9946 | 1.0000 | 1.0000 | 1.0000 | 0.0009 | 0.0605 | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 41/61 (20 sessions) | 0.5915 | 0.5000 | 0.5000 | 0.7500 | 20/22 (11 sessions) | 0.5625 | 0.5000 | 0.5000 | 0.7500 | 0.0290 | 0.1156 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 38/61 (18 sessions) | 0.5658 | 0.6000 | 0.5000 | 0.6750 | 14/22 (7 sessions) | 0.5857 | 0.6000 | 0.5000 | 0.7000 | -0.0199 | -0.1407 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 19/61 (14 sessions) | 0.5311 | 0.5455 | 0.4545 | 0.6136 | 8/22 (5 sessions) | 0.5511 | 0.5455 | 0.5114 | 0.6364 | -0.0200 | -0.2004 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 33/61 (17 sessions) | 1.3799 | 1.2202 | 0.6086 | 1.7568 | 14/22 (7 sessions) | 2.1273 | 1.4944 | 1.1625 | 1.8042 | -0.7475 | -0.5584 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 33/61 (17 sessions) | 0.8167 | 0.6051 | 0.2476 | 0.8862 | 14/22 (7 sessions) | 1.4755 | 0.7383 | 0.3919 | 1.7599 | -0.6587 | -0.5390 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 23/61 (16 sessions) | 0.6328 | 0.3227 | 0.1437 | 0.7329 | 10/22 (5 sessions) | 1.3919 | 0.4345 | 0.2450 | 2.4435 | -0.7591 | -0.6354 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 54/61 (22 sessions) | 1.7943 | 1.6450 | 0.5054 | 2.4465 | 20/22 (10 sessions) | 1.7984 | 1.3400 | 0.7088 | 2.1825 | -0.0040 | -0.0026 | not resampled |
| stage11_2.room_in_atr [SMALL] | 28/61 (16 sessions) | 1.8603 | 1.6181 | 0.8414 | 2.3634 | 13/22 (6 sessions) | 1.8538 | 1.7587 | 0.3425 | 2.2376 | 0.0065 | 0.0047 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 61/61 (22 sessions) | 2.8197 | 3.0000 | 2.0000 | 4.0000 | 22/22 (11 sessions) | 2.6818 | 3.0000 | 1.0000 | 4.0000 | 0.1379 | 0.0873 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 61/61 (22 sessions) | 3.1803 | 3.0000 | 2.0000 | 4.0000 | 22/22 (11 sessions) | 3.3182 | 3.0000 | 2.0000 | 5.0000 | -0.1379 | -0.0873 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 57/61 (22 sessions) | 1.1371 | 0.5101 | 0.3200 | 1.7200 | 21/22 (11 sessions) | 0.8994 | 0.3750 | 0.2055 | 1.2000 | 0.2377 | 0.1744 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 58/61 (22 sessions) | 0.9009 | 0.4050 | 0.1700 | 1.2100 | 21/22 (10 sessions) | 1.0184 | 0.2400 | 0.0600 | 0.7900 | -0.1176 | -0.0913 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 33/61 (17 sessions) | 0.1212 | 0.0000 | 0.0000 | 0.0000 | 14/22 (7 sessions) | 0.2857 | 0.0000 | 0.0000 | 0.7500 | -0.1645 | -0.4371 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 33/61 (17 sessions) | 0.2424 | 0.0000 | 0.0000 | 0.0000 | 14/22 (7 sessions) | 0.2857 | 0.0000 | 0.0000 | 0.7500 | -0.0433 | -0.0972 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 39/61 (19 sessions) | 1.5121 | 1.2000 | 0.7500 | 1.8650 | 18/22 (10 sessions) | 1.8000 | 1.2845 | 0.3854 | 2.3638 | -0.2879 | -0.2116 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 39/61 (18 sessions) | 1.5318 | 1.3700 | 0.4744 | 2.0850 | 18/22 (10 sessions) | 1.3158 | 1.0850 | 0.6262 | 2.1899 | 0.2160 | 0.2005 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 33/61 (17 sessions) | 1.6888 | 1.4234 | 0.8895 | 2.0747 | 14/22 (7 sessions) | 1.8047 | 1.6913 | 0.7692 | 2.9920 | -0.1158 | -0.0944 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 33/61 (17 sessions) | 1.4682 | 1.3091 | 0.5521 | 2.0962 | 12/22 (6 sessions) | 1.3924 | 1.4633 | 0.6517 | 1.9306 | 0.0757 | 0.0753 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG | 43 | 19 | 31 | 12 | 50.82% | 54.55% | 72.09% |
| direction | SHORT | 40 | 16 | 30 | 10 | 49.18% | 45.45% | 75.00% |
| time_bucket | 09:35-10:00 [SMALL] | 22 | 19 | 20 | 2 | 32.79% | 9.09% | 90.91% |
| time_bucket | 10:00-10:30 [SMALL] | 9 | 7 | 3 | 6 | 4.92% | 27.27% | 33.33% |
| time_bucket | 10:30-11:00 [SMALL] | 14 | 10 | 11 | 3 | 18.03% | 13.64% | 78.57% |
| time_bucket | 11:00-12:00 [SMALL] | 14 | 9 | 10 | 4 | 16.39% | 18.18% | 71.43% |
| time_bucket | 12:00-13:30 [SMALL] | 11 | 7 | 8 | 3 | 13.11% | 13.64% | 72.73% |
| time_bucket | 13:30-15:00 [SMALL] | 8 | 6 | 5 | 3 | 8.20% | 13.64% | 62.50% |
| time_bucket | 15:00-close [SMALL] | 5 | 4 | 4 | 1 | 6.56% | 4.55% | 80.00% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 19 | 10 | 12 | 7 | 19.67% | 31.82% | 63.16% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 14 | 10 | 11 | 3 | 18.03% | 13.64% | 78.57% |
| ema9_20_alignment | EMA_UNAVAILABLE | 50 | 22 | 38 | 12 | 62.30% | 54.55% | 76.00% |
| price_vwap_alignment | VWAP_ALIGNED | 72 | 22 | 52 | 20 | 85.25% | 90.91% | 72.22% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 11 | 9 | 9 | 2 | 14.75% | 9.09% | 81.82% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED | 41 | 16 | 27 | 14 | 44.26% | 63.64% | 65.85% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 18 | 12 | 13 | 5 | 21.31% | 22.73% | 72.22% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 24 | 20 | 21 | 3 | 34.43% | 13.64% | 87.50% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 20 | 10 | 13 | 7 | 21.31% | 31.82% | 65.00% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 13 | 10 | 10 | 3 | 16.39% | 13.64% | 76.92% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 50 | 22 | 38 | 12 | 62.30% | 54.55% | 76.00% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 13 | 6 | 8 | 5 | 13.11% | 22.73% | 61.54% |
| prior_ema_cross | NO_PRIOR_CROSS | 59 | 22 | 44 | 15 | 72.13% | 68.18% | 74.58% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 11 | 8 | 9 | 2 | 14.75% | 9.09% | 81.82% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 64 | 20 | 45 | 19 | 73.77% | 86.36% | 70.31% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 17 | 13 | 14 | 3 | 22.95% | 13.64% | 82.35% |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 2 | 2 | 2 | 0 | 3.28% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 4 | 2 | 4 | 0 | 6.56% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 6 | 5 | 4 | 2 | 6.56% | 9.09% | 66.67% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 7 | 6 | 5 | 2 | 8.20% | 9.09% | 71.43% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 8 | 6 | 6 | 2 | 9.84% | 9.09% | 75.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 8 | 5 | 5 | 3 | 8.20% | 13.64% | 62.50% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 8 | 5 | 4 | 4 | 6.56% | 18.18% | 50.00% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 9 | 4 | 7 | 2 | 11.48% | 9.09% | 77.78% |
| stage11_2.room_bucket | UNAVAILABLE_ATR | 33 | 22 | 26 | 7 | 42.62% | 31.82% | 78.79% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 83 | 22 | 61 | 22 | 100.00% | 100.00% | 73.49% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 7 | 6 | 6 | 1 | 9.84% | 4.55% | 85.71% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 19 | 11 | 12 | 7 | 19.67% | 31.82% | 63.16% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 15 | 10 | 11 | 4 | 18.03% | 18.18% | 73.33% |
| stage11_3.structure | UNAVAILABLE | 42 | 22 | 32 | 10 | 52.46% | 45.45% | 76.19% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 17 | 12 | 12 | 5 | 19.67% | 22.73% | 70.59% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 24 | 13 | 17 | 7 | 27.87% | 31.82% | 70.83% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 42 | 22 | 32 | 10 | 52.46% | 45.45% | 76.19% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 25 | 14 | 16 | 9 | 26.23% | 40.91% | 64.00% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 21 | 9 | 16 | 5 | 26.23% | 22.73% | 76.19% |
| stage11_3.high_structure | UNAVAILABLE | 37 | 22 | 29 | 8 | 47.54% | 36.36% | 78.38% |
| stage11_3.low_structure | EQUAL_LOW [SMALL] | 1 | 1 | 1 | 0 | 1.64% | 0.00% | 100.00% |
| stage11_3.low_structure | HIGHER_LOW | 34 | 14 | 23 | 11 | 37.70% | 50.00% | 67.65% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 8 | 7 | 7 | 1 | 11.48% | 4.55% | 87.50% |
| stage11_3.low_structure | UNAVAILABLE | 40 | 22 | 30 | 10 | 49.18% | 45.45% | 75.00% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 27 | 20 | 22 | 5 | 36.07% | 22.73% | 81.48% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 6 | 2 | 5 | 1 | 8.20% | 4.55% | 83.33% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 9 | 7 | 7 | 2 | 11.48% | 9.09% | 77.78% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL | 41 | 17 | 27 | 14 | 44.26% | 63.64% | 65.85% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 83 | 22 | 61 | 22 | 100.00% | 100.00% | 73.49% |


### 2026-08


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 75/75 (21 sessions) | 1.2686 | 1.3129 | 1.0000 | 1.5450 | 29/29 (15 sessions) | 1.2596 | 1.2400 | 1.0800 | 1.5600 | 0.0090 | 0.0232 | not resampled |
| body_size [SMALL] | 75/75 (21 sessions) | 0.5523 | 0.4940 | 0.3250 | 0.7050 | 29/29 (15 sessions) | 0.3732 | 0.3075 | 0.2000 | 0.5050 | 0.1791 | 0.5473 | not resampled |
| directional_body [SMALL] | 75/75 (21 sessions) | 0.5523 | 0.4940 | 0.3250 | 0.7050 | 29/29 (15 sessions) | 0.3732 | 0.3075 | 0.2000 | 0.5050 | 0.1791 | 0.5473 | not resampled |
| candle_range [SMALL] | 75/75 (21 sessions) | 0.8011 | 0.7100 | 0.5469 | 1.0675 | 29/29 (15 sessions) | 0.6681 | 0.6500 | 0.4050 | 0.7450 | 0.1330 | 0.3429 | not resampled |
| body_range_ratio [SMALL] | 75/75 (21 sessions) | 0.6707 | 0.7152 | 0.5421 | 0.8097 | 29/29 (15 sessions) | 0.5472 | 0.6143 | 0.3378 | 0.6989 | 0.1235 | 0.5778 | not resampled |
| directional_body_range_ratio [SMALL] | 75/75 (21 sessions) | 0.6707 | 0.7152 | 0.5421 | 0.8097 | 29/29 (15 sessions) | 0.5472 | 0.6143 | 0.3378 | 0.6989 | 0.1235 | 0.5778 | not resampled |
| close_location [SMALL] | 75/75 (21 sessions) | 0.4058 | 0.2326 | 0.0584 | 0.7927 | 29/29 (15 sessions) | 0.5082 | 0.4737 | 0.2104 | 0.8577 | -0.1025 | -0.2832 | not resampled |
| directional_close_location [SMALL] | 75/75 (21 sessions) | 0.8482 | 0.8874 | 0.7819 | 0.9669 | 29/29 (15 sessions) | 0.7673 | 0.8577 | 0.6370 | 0.9057 | 0.0809 | 0.4833 | not resampled |
| distance_beyond_level [SMALL] | 75/75 (21 sessions) | 0.3090 | 0.2400 | 0.1100 | 0.4175 | 29/29 (15 sessions) | 0.1691 | 0.1200 | 0.0700 | 0.1950 | 0.1399 | 0.5897 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 46/75 (15 sessions) | 0.4763 | 0.4289 | 0.1708 | 0.6534 | 19/29 (9 sessions) | 0.2370 | 0.2141 | 0.1353 | 0.3119 | 0.2393 | 0.7016 | not resampled |
| candle_volume [SMALL] | 75/75 (21 sessions) | 452251.8133 | 357864.0000 | 256742.5000 | 514926.5000 | 29/29 (15 sessions) | 524045.3793 | 437699.0000 | 258262.0000 | 637730.0000 | -71793.5660 | -0.1821 | not resampled |
| relative_volume_prior_6 [SMALL] | 58/75 (18 sessions) | 1.1819 | 0.9725 | 0.6793 | 1.4097 | 23/29 (11 sessions) | 1.3857 | 1.0217 | 0.6747 | 1.5739 | -0.2038 | -0.1956 | not resampled |
| atr14 [SMALL] | 46/75 (15 sessions) | 0.6016 | 0.5670 | 0.4784 | 0.7449 | 19/29 (9 sessions) | 0.5424 | 0.5453 | 0.4036 | 0.6048 | 0.0592 | 0.3042 | not resampled |
| minutes_since_open [SMALL] | 75/75 (21 sessions) | 133.7333 | 100.0000 | 35.0000 | 190.0000 | 29/29 (15 sessions) | 160.6897 | 120.0000 | 60.0000 | 255.0000 | -26.9563 | -0.2267 | not resampled |
| minutes_since_ema_cross [SMALL] | 26/75 (14 sessions) | 50.5769 | 42.5000 | 16.2500 | 78.7500 | 14/29 (7 sessions) | 40.7143 | 20.0000 | 11.2500 | 50.0000 | 9.8626 | 0.2176 | not resampled |
| break_attempt_rank [SMALL] | 75/75 (21 sessions) | 6.5200 | 6.0000 | 3.0000 | 9.0000 | 29/29 (15 sessions) | 6.9310 | 6.0000 | 3.0000 | 11.0000 | -0.4110 | -0.0947 | not resampled |
| valid_hold_sequence_rank [SMALL] | 75/75 (21 sessions) | 3.8400 | 3.0000 | 2.0000 | 5.0000 | 29/29 (15 sessions) | 4.2414 | 3.0000 | 2.0000 | 6.0000 | -0.4014 | -0.1518 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 40/75 (15 sessions) | 0.1970 | 0.1511 | 0.0763 | 0.2665 | 15/29 (8 sessions) | 0.1472 | 0.1162 | 0.0208 | 0.2319 | 0.0498 | 0.3227 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 40/75 (15 sessions) | 0.3365 | 0.3493 | 0.1625 | 0.4387 | 15/29 (8 sessions) | 0.2874 | 0.3039 | 0.0513 | 0.4849 | 0.0491 | 0.2135 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 52/75 (18 sessions) | -0.0445 | -0.0456 | -0.1221 | 0.0477 | 23/29 (11 sessions) | -0.0188 | -0.0155 | -0.1140 | 0.0689 | -0.0257 | -0.1925 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 48/75 (16 sessions) | -0.0369 | -0.0265 | -0.0872 | 0.0318 | 22/29 (11 sessions) | -0.0047 | -0.0083 | -0.0704 | 0.0596 | -0.0321 | -0.3192 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 48/75 (16 sessions) | -0.0381 | -0.0232 | -0.0749 | 0.0215 | 22/29 (11 sessions) | -0.0145 | -0.0172 | -0.0543 | 0.0391 | -0.0236 | -0.2554 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 37/75 (14 sessions) | -0.0331 | -0.0247 | -0.0755 | 0.0103 | 15/29 (8 sessions) | -0.0161 | -0.0109 | -0.0712 | 0.0235 | -0.0170 | -0.2341 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 36/75 (14 sessions) | -0.0260 | -0.0148 | -0.0600 | 0.0132 | 15/29 (8 sessions) | -0.0123 | -0.0113 | -0.0489 | 0.0199 | -0.0138 | -0.2315 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 35/75 (14 sessions) | -0.0240 | -0.0093 | -0.0446 | 0.0100 | 15/29 (8 sessions) | -0.0149 | -0.0129 | -0.0518 | 0.0208 | -0.0091 | -0.1592 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 75/75 (21 sessions) | 0.0109 | -0.0057 | -0.0288 | 0.0081 | 29/29 (15 sessions) | -0.0023 | -0.0046 | -0.0296 | 0.0088 | 0.0132 | 0.1166 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 70/75 (20 sessions) | -0.0069 | -0.0062 | -0.0251 | 0.0054 | 25/29 (12 sessions) | 0.0048 | -0.0041 | -0.0122 | 0.0036 | -0.0118 | -0.2465 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 67/75 (20 sessions) | -0.0086 | -0.0070 | -0.0246 | 0.0039 | 24/29 (12 sessions) | -0.0002 | -0.0042 | -0.0149 | 0.0054 | -0.0084 | -0.2090 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 35/75 (14 sessions) | 0.3714 | 0.0000 | 0.0000 | 0.5000 | 14/29 (7 sessions) | 0.5714 | 1.0000 | 0.0000 | 1.0000 | -0.2000 | -0.3097 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 27/75 (14 sessions) | 0.5556 | 0.0000 | 0.0000 | 1.0000 | 13/29 (7 sessions) | 0.9231 | 1.0000 | 0.0000 | 1.0000 | -0.3675 | -0.5402 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 17/75 (10 sessions) | 1.2941 | 1.0000 | 1.0000 | 1.0000 | 8/29 (6 sessions) | 1.1250 | 1.0000 | 0.7500 | 1.2500 | 0.1691 | 0.1471 | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 46/75 (15 sessions) | 0.3478 | 0.0000 | 0.0000 | 0.7500 | 19/29 (9 sessions) | 0.4737 | 0.0000 | 0.0000 | 1.0000 | -0.1259 | -0.2075 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 40/75 (15 sessions) | 0.8250 | 1.0000 | 0.0000 | 1.0000 | 15/29 (8 sessions) | 0.7333 | 1.0000 | 0.0000 | 1.0000 | 0.0917 | 0.1021 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 25/75 (13 sessions) | 1.3200 | 1.0000 | 0.0000 | 2.0000 | 12/29 (7 sessions) | 1.3333 | 1.0000 | 0.0000 | 2.2500 | -0.0133 | -0.0103 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 35/75 (14 sessions) | 0.2286 | 0.0000 | 0.0000 | 0.0000 | 14/29 (7 sessions) | 0.4286 | 0.0000 | 0.0000 | 1.0000 | -0.2000 | -0.4026 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 27/75 (14 sessions) | 0.4815 | 0.0000 | 0.0000 | 1.0000 | 13/29 (7 sessions) | 0.6154 | 0.0000 | 0.0000 | 1.0000 | -0.1339 | -0.1955 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 17/75 (10 sessions) | 0.6471 | 1.0000 | 0.0000 | 1.0000 | 8/29 (6 sessions) | 0.7500 | 0.0000 | 0.0000 | 1.2500 | -0.1029 | -0.1184 | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 61/75 (19 sessions) | 1.1639 | 1.0000 | 0.0000 | 2.0000 | 23/29 (11 sessions) | 0.8696 | 1.0000 | 0.0000 | 1.5000 | 0.2944 | 0.2707 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 48/75 (16 sessions) | 2.1875 | 2.0000 | 1.0000 | 3.2500 | 22/29 (11 sessions) | 1.8636 | 1.5000 | 1.0000 | 3.0000 | 0.3239 | 0.1801 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 35/75 (14 sessions) | 3.8571 | 4.0000 | 1.5000 | 5.5000 | 15/29 (8 sessions) | 2.9333 | 3.0000 | 2.0000 | 4.0000 | 0.9238 | 0.3790 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 61/75 (19 sessions) | 1.4003 | 1.1800 | 0.9788 | 1.7900 | 23/29 (11 sessions) | 1.4600 | 1.4300 | 0.9700 | 1.9150 | -0.0597 | -0.0855 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 48/75 (16 sessions) | 1.8910 | 1.7050 | 1.2100 | 2.3050 | 22/29 (11 sessions) | 1.8870 | 1.8150 | 1.3162 | 2.3562 | 0.0040 | 0.0047 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 35/75 (14 sessions) | 2.4373 | 2.1300 | 1.5900 | 2.9750 | 15/29 (8 sessions) | 2.1020 | 2.1150 | 1.4850 | 2.7875 | 0.3353 | 0.3296 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 46/75 (15 sessions) | 2.0472 | 1.9412 | 1.6621 | 2.3255 | 19/29 (9 sessions) | 2.4369 | 2.3017 | 1.7044 | 3.3611 | -0.3897 | -0.5468 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 46/75 (15 sessions) | 3.0415 | 3.0321 | 2.2914 | 3.4760 | 19/29 (9 sessions) | 3.3051 | 3.3402 | 2.6337 | 3.9162 | -0.2636 | -0.2884 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 35/75 (14 sessions) | 4.3238 | 4.1191 | 3.6544 | 4.9374 | 15/29 (8 sessions) | 4.3119 | 4.2821 | 3.7670 | 4.7330 | 0.0119 | 0.0125 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 61/75 (19 sessions) | 0.4261 | 0.3938 | 0.1935 | 0.6154 | 23/29 (11 sessions) | 0.4437 | 0.4146 | 0.1215 | 0.7112 | -0.0176 | -0.0587 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 48/75 (16 sessions) | 0.2787 | 0.2071 | 0.1098 | 0.4378 | 22/29 (11 sessions) | 0.3104 | 0.2636 | 0.1716 | 0.4380 | -0.0318 | -0.1563 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 35/75 (14 sessions) | 0.1604 | 0.1546 | 0.0601 | 0.2271 | 15/29 (8 sessions) | 0.1705 | 0.1160 | 0.0635 | 0.2548 | -0.0101 | -0.0798 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 61/75 (19 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 23/29 (11 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 48/75 (16 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 22/29 (11 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 35/75 (14 sessions) | 0.9975 | 1.0000 | 1.0000 | 1.0000 | 15/29 (8 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | -0.0025 | -0.2883 | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 61/75 (19 sessions) | 0.5492 | 0.5000 | 0.5000 | 0.7500 | 23/29 (11 sessions) | 0.4457 | 0.5000 | 0.2500 | 0.5000 | 0.1035 | 0.4204 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 48/75 (16 sessions) | 0.5250 | 0.5500 | 0.4000 | 0.7000 | 22/29 (11 sessions) | 0.4273 | 0.4000 | 0.3000 | 0.5750 | 0.0977 | 0.5368 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 35/75 (14 sessions) | 0.5013 | 0.5455 | 0.3636 | 0.5909 | 15/29 (8 sessions) | 0.4606 | 0.4545 | 0.3864 | 0.5455 | 0.0407 | 0.2817 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 46/75 (15 sessions) | 1.2447 | 1.2512 | 0.8286 | 1.7479 | 19/29 (9 sessions) | 1.2407 | 1.2626 | 0.7588 | 1.6672 | 0.0040 | 0.0055 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 46/75 (15 sessions) | 0.6797 | 0.5719 | 0.2849 | 1.0819 | 19/29 (9 sessions) | 0.5583 | 0.5359 | 0.0763 | 0.9969 | 0.1215 | 0.2446 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 40/75 (15 sessions) | 0.4831 | 0.5074 | 0.0945 | 0.7933 | 15/29 (8 sessions) | 0.5055 | 0.5121 | 0.2229 | 0.8161 | -0.0225 | -0.0597 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 52/75 (16 sessions) | 0.9499 | 0.6950 | 0.3600 | 1.3938 | 28/29 (14 sessions) | 0.6863 | 0.6512 | 0.1988 | 0.9888 | 0.2636 | 0.3705 | not resampled |
| stage11_2.room_in_atr [SMALL] | 32/75 (11 sessions) | 1.5313 | 0.9811 | 0.6305 | 2.0756 | 19/29 (9 sessions) | 1.1523 | 0.9325 | 0.3356 | 1.8332 | 0.3790 | 0.3129 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 75/75 (21 sessions) | 3.6000 | 4.0000 | 2.0000 | 5.0000 | 29/29 (15 sessions) | 3.0000 | 3.0000 | 2.0000 | 4.0000 | 0.6000 | 0.3431 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 75/75 (21 sessions) | 2.3733 | 2.0000 | 0.5000 | 4.0000 | 29/29 (15 sessions) | 3.0000 | 3.0000 | 2.0000 | 4.0000 | -0.6267 | -0.3586 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 71/75 (18 sessions) | 0.3709 | 0.3000 | 0.1026 | 0.4945 | 28/29 (14 sessions) | 0.4668 | 0.2900 | 0.1238 | 0.6506 | -0.0958 | -0.2378 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 56/75 (19 sessions) | 0.7675 | 0.4325 | 0.1700 | 1.3665 | 29/29 (15 sessions) | 0.3811 | 0.1600 | 0.0700 | 0.6100 | 0.3864 | 0.5458 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 46/75 (15 sessions) | 0.1304 | 0.0000 | 0.0000 | 0.0000 | 19/29 (9 sessions) | 0.3684 | 0.0000 | 0.0000 | 1.0000 | -0.2380 | -0.6084 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 46/75 (15 sessions) | 0.3478 | 0.0000 | 0.0000 | 1.0000 | 19/29 (9 sessions) | 0.5789 | 1.0000 | 0.0000 | 1.0000 | -0.2311 | -0.4726 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 58/75 (19 sessions) | 1.0227 | 0.7400 | 0.5150 | 1.2300 | 23/29 (11 sessions) | 0.9260 | 0.7100 | 0.3625 | 1.4850 | 0.0967 | 0.1136 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 57/75 (19 sessions) | 0.7089 | 0.5400 | 0.3310 | 0.9300 | 20/29 (10 sessions) | 0.8129 | 0.5100 | 0.2938 | 1.1382 | -0.1040 | -0.1699 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 46/75 (15 sessions) | 1.6564 | 1.4390 | 0.7239 | 2.0148 | 19/29 (9 sessions) | 1.4616 | 1.0442 | 0.4958 | 2.3032 | 0.1948 | 0.1522 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 46/75 (15 sessions) | 1.0889 | 1.0588 | 0.6001 | 1.5261 | 18/29 (8 sessions) | 1.5896 | 0.9995 | 0.6449 | 2.5444 | -0.5007 | -0.5870 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG | 42 | 13 | 29 | 13 | 38.67% | 44.83% | 69.05% |
| direction | SHORT | 62 | 17 | 46 | 16 | 61.33% | 55.17% | 74.19% |
| time_bucket | 09:35-10:00 [SMALL] | 20 | 16 | 14 | 6 | 18.67% | 20.69% | 70.00% |
| time_bucket | 10:00-10:30 [SMALL] | 14 | 12 | 13 | 1 | 17.33% | 3.45% | 92.86% |
| time_bucket | 10:30-11:00 [SMALL] | 9 | 7 | 5 | 4 | 6.67% | 13.79% | 55.56% |
| time_bucket | 11:00-12:00 [SMALL] | 20 | 9 | 15 | 5 | 20.00% | 17.24% | 75.00% |
| time_bucket | 12:00-13:30 [SMALL] | 18 | 9 | 13 | 5 | 17.33% | 17.24% | 72.22% |
| time_bucket | 13:30-15:00 [SMALL] | 10 | 8 | 9 | 1 | 12.00% | 3.45% | 90.00% |
| time_bucket | 15:00-close [SMALL] | 13 | 8 | 6 | 7 | 8.00% | 24.14% | 46.15% |
| ema9_20_alignment | EMA_ALIGNED | 43 | 12 | 33 | 10 | 44.00% | 34.48% | 76.74% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 12 | 9 | 7 | 5 | 9.33% | 17.24% | 58.33% |
| ema9_20_alignment | EMA_UNAVAILABLE | 49 | 20 | 35 | 14 | 46.67% | 48.28% | 71.43% |
| price_vwap_alignment | VWAP_ALIGNED | 96 | 21 | 70 | 26 | 93.33% | 89.66% | 72.92% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 8 | 7 | 5 | 3 | 6.67% | 10.34% | 62.50% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED | 61 | 16 | 44 | 17 | 58.67% | 58.62% | 72.13% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 15 | 12 | 9 | 6 | 12.00% | 20.69% | 60.00% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 28 | 18 | 22 | 6 | 29.33% | 20.69% | 78.57% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED | 40 | 11 | 30 | 10 | 40.00% | 34.48% | 75.00% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 15 | 11 | 10 | 5 | 13.33% | 17.24% | 66.67% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 49 | 20 | 35 | 14 | 46.67% | 48.28% | 71.43% |
| prior_ema_cross | MATCHING_CROSS | 30 | 10 | 20 | 10 | 26.67% | 34.48% | 66.67% |
| prior_ema_cross | NO_PRIOR_CROSS | 64 | 21 | 49 | 15 | 65.33% | 51.72% | 76.56% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 10 | 8 | 6 | 4 | 8.00% | 13.79% | 60.00% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 59 | 12 | 41 | 18 | 54.67% | 62.07% | 69.49% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL | 45 | 17 | 34 | 11 | 45.33% | 37.93% | 75.56% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 14 | 8 | 10 | 4 | 13.33% | 13.79% | 71.43% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 4 | 4 | 3 | 1 | 4.00% | 3.45% | 75.00% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 9 | 6 | 5 | 4 | 6.67% | 13.79% | 55.56% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 5 | 3 | 3 | 2 | 4.00% | 6.90% | 60.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 6 | 3 | 5 | 1 | 6.67% | 3.45% | 83.33% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 13 | 6 | 6 | 7 | 8.00% | 24.14% | 46.15% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 24 | 8 | 23 | 1 | 30.67% | 3.45% | 95.83% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 29 | 15 | 20 | 9 | 26.67% | 31.03% | 68.97% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 104 | 21 | 75 | 29 | 100.00% | 100.00% | 72.12% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 12 | 8 | 8 | 4 | 10.67% | 13.79% | 66.67% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 17 | 11 | 14 | 3 | 18.67% | 10.34% | 82.35% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 27 | 12 | 17 | 10 | 22.67% | 34.48% | 62.96% |
| stage11_3.structure | UNAVAILABLE | 48 | 20 | 36 | 12 | 48.00% | 41.38% | 75.00% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 18 | 11 | 14 | 4 | 18.67% | 13.79% | 77.78% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED | 38 | 15 | 25 | 13 | 33.33% | 44.83% | 65.79% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 48 | 20 | 36 | 12 | 48.00% | 41.38% | 75.00% |
| stage11_3.high_structure | HIGHER_HIGH | 32 | 14 | 22 | 10 | 29.33% | 34.48% | 68.75% |
| stage11_3.high_structure | LOWER_HIGH | 36 | 13 | 25 | 11 | 33.33% | 37.93% | 69.44% |
| stage11_3.high_structure | UNAVAILABLE | 36 | 19 | 28 | 8 | 37.33% | 27.59% | 77.78% |
| stage11_3.low_structure | EQUAL_LOW [SMALL] | 2 | 1 | 1 | 1 | 1.33% | 3.45% | 50.00% |
| stage11_3.low_structure | HIGHER_LOW | 32 | 15 | 24 | 8 | 32.00% | 27.59% | 75.00% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 23 | 11 | 15 | 8 | 20.00% | 27.59% | 65.22% |
| stage11_3.low_structure | UNAVAILABLE | 47 | 20 | 35 | 12 | 46.67% | 41.38% | 74.47% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 25 | 17 | 18 | 7 | 24.00% | 24.14% | 72.00% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 17 | 6 | 17 | 0 | 22.67% | 0.00% | 100.00% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 22 | 9 | 12 | 10 | 16.00% | 34.48% | 54.55% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL | 40 | 14 | 28 | 12 | 37.33% | 41.38% | 70.00% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 104 | 21 | 75 | 29 | 100.00% | 100.00% | 72.12% |


### 2026-09 — PARTIAL / SMALL


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 7/7 (4 sessions) | 1.0598 | 0.9695 | 0.9648 | 1.1772 | 6/6 (3 sessions) | 1.0072 | 0.9695 | 0.9695 | 0.9695 | 0.0526 | 0.2410 | not resampled |
| body_size [SMALL] | 7/7 (4 sessions) | 0.4857 | 0.4950 | 0.3649 | 0.6325 | 6/6 (3 sessions) | 0.3467 | 0.3350 | 0.3125 | 0.3575 | 0.1390 | 0.8138 | not resampled |
| directional_body [SMALL] | 7/7 (4 sessions) | 0.4857 | 0.4950 | 0.3649 | 0.6325 | 6/6 (3 sessions) | 0.3467 | 0.3350 | 0.3125 | 0.3575 | 0.1390 | 0.8138 | not resampled |
| candle_range [SMALL] | 7/7 (4 sessions) | 0.9593 | 0.8200 | 0.6324 | 1.0875 | 6/6 (3 sessions) | 0.5933 | 0.5550 | 0.5250 | 0.6750 | 0.3659 | 1.0275 | not resampled |
| body_range_ratio [SMALL] | 7/7 (4 sessions) | 0.5460 | 0.5891 | 0.3786 | 0.7378 | 6/6 (3 sessions) | 0.6019 | 0.5378 | 0.4534 | 0.7045 | -0.0559 | -0.2521 | not resampled |
| directional_body_range_ratio [SMALL] | 7/7 (4 sessions) | 0.5460 | 0.5891 | 0.3786 | 0.7378 | 6/6 (3 sessions) | 0.6019 | 0.5378 | 0.4534 | 0.7045 | -0.0559 | -0.2521 | not resampled |
| close_location [SMALL] | 7/7 (4 sessions) | 0.5966 | 0.5938 | 0.3318 | 0.9596 | 6/6 (3 sessions) | 0.7353 | 0.8410 | 0.5534 | 0.9591 | -0.1387 | -0.3839 | not resampled |
| directional_close_location [SMALL] | 7/7 (4 sessions) | 0.8158 | 0.9457 | 0.6926 | 0.9867 | 6/6 (3 sessions) | 0.8130 | 0.8410 | 0.7282 | 0.9591 | 0.0028 | 0.0125 | not resampled |
| distance_beyond_level [SMALL] | 7/7 (4 sessions) | 0.2729 | 0.3450 | 0.0378 | 0.4575 | 6/6 (3 sessions) | 0.1352 | 0.0955 | 0.0630 | 0.2101 | 0.1377 | 0.7498 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 3/7 (2 sessions) | 0.3213 | 0.0597 | 0.0557 | 0.4562 | 3/6 (1 sessions) | 0.2692 | 0.2199 | 0.1716 | 0.3421 | 0.0521 | 0.1497 | not resampled |
| candle_volume [SMALL] | 7/7 (4 sessions) | 545492.8571 | 426837.0000 | 338161.0000 | 711801.0000 | 6/6 (3 sessions) | 610716.3333 | 523963.0000 | 349152.2500 | 904314.2500 | -65223.4762 | -0.2092 | not resampled |
| relative_volume_prior_6 [SMALL] | 5/7 (3 sessions) | 1.6071 | 1.1885 | 0.7305 | 1.7273 | 4/6 (2 sessions) | 1.1122 | 1.0230 | 0.7188 | 1.4164 | 0.4948 | 0.4749 | not resampled |
| atr14 [SMALL] | 3/7 (2 sessions) | 0.6215 | 0.5022 | 0.4974 | 0.6860 | 3/6 (1 sessions) | 0.5455 | 0.5480 | 0.5324 | 0.5598 | 0.0761 | 0.4964 | not resampled |
| minutes_since_open [SMALL] | 7/7 (4 sessions) | 125.0000 | 40.0000 | 32.5000 | 197.5000 | 6/6 (3 sessions) | 143.3333 | 115.0000 | 25.0000 | 205.0000 | -18.3333 | -0.1251 | not resampled |
| minutes_since_ema_cross [SMALL] | 2/7 (1 sessions) | 155.0000 | 155.0000 | 140.0000 | 170.0000 | 3/6 (1 sessions) | 81.6667 | 30.0000 | 20.0000 | 117.5000 | 73.3333 | 0.8063 | not resampled |
| break_attempt_rank [SMALL] | 7/7 (4 sessions) | 6.5714 | 5.0000 | 3.5000 | 9.0000 | 6/6 (3 sessions) | 5.1667 | 3.0000 | 2.0000 | 4.7500 | 1.4048 | 0.2679 | not resampled |
| valid_hold_sequence_rank [SMALL] | 7/7 (4 sessions) | 2.8571 | 2.0000 | 1.5000 | 4.0000 | 6/6 (3 sessions) | 3.0000 | 2.5000 | 1.2500 | 3.7500 | -0.1429 | -0.0678 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 2/7 (1 sessions) | 0.1885 | 0.1885 | 0.1297 | 0.2474 | 3/6 (1 sessions) | 0.2760 | 0.3177 | 0.1972 | 0.3756 | -0.0874 | -0.4941 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 2/7 (1 sessions) | 0.3813 | 0.3813 | 0.2611 | 0.5015 | 3/6 (1 sessions) | 0.4984 | 0.5559 | 0.3522 | 0.6734 | -0.1171 | -0.3548 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 3/7 (2 sessions) | -0.0094 | -0.0023 | -0.0848 | 0.0695 | 3/6 (1 sessions) | -0.0758 | -0.0374 | -0.1017 | -0.0307 | 0.0664 | 0.5417 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 3/7 (2 sessions) | -0.0102 | 0.0249 | -0.0530 | 0.0501 | 3/6 (1 sessions) | -0.1086 | -0.0745 | -0.1625 | -0.0377 | 0.0984 | 0.8319 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 3/7 (2 sessions) | 0.0020 | 0.0316 | -0.0287 | 0.0474 | 3/6 (1 sessions) | -0.1116 | -0.0951 | -0.1659 | -0.0491 | 0.1136 | 1.1282 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 2/7 (1 sessions) | -0.0556 | -0.0556 | -0.0791 | -0.0320 | 3/6 (1 sessions) | -0.0610 | -0.0557 | -0.0795 | -0.0398 | 0.0054 | 0.1069 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 2/7 (1 sessions) | -0.0406 | -0.0406 | -0.0623 | -0.0189 | 3/6 (1 sessions) | -0.0740 | -0.0787 | -0.1072 | -0.0432 | 0.0334 | 0.5290 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 2/7 (1 sessions) | -0.0300 | -0.0300 | -0.0471 | -0.0130 | 3/6 (1 sessions) | -0.0731 | -0.0871 | -0.1049 | -0.0482 | 0.0431 | 0.7845 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 7/7 (4 sessions) | 0.0265 | -0.0191 | -0.0287 | 0.0406 | 6/6 (3 sessions) | -0.0159 | -0.0161 | -0.0379 | 0.0260 | 0.0424 | 0.4315 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 6/7 (4 sessions) | -0.0095 | -0.0178 | -0.0235 | 0.0081 | 6/6 (3 sessions) | -0.0215 | -0.0229 | -0.0358 | 0.0138 | 0.0120 | 0.2331 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 6/7 (4 sessions) | -0.0081 | -0.0162 | -0.0195 | 0.0080 | 5/6 (2 sessions) | -0.0263 | -0.0290 | -0.0366 | -0.0125 | 0.0183 | 0.5565 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 2/7 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 3/6 (1 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.5000 | -0.3333 | -0.7071 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 2/7 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 3/6 (1 sessions) | 0.6667 | 1.0000 | 0.5000 | 1.0000 | -0.6667 | -1.4142 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 2/7 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1/6 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 3/7 (2 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 3/6 (1 sessions) | 0.6667 | 1.0000 | 0.5000 | 1.0000 | -0.6667 | -1.6330 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 2/7 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 3/6 (1 sessions) | 0.6667 | 1.0000 | 0.5000 | 1.0000 | -0.6667 | -1.4142 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 2/7 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 3/6 (1 sessions) | 0.6667 | 1.0000 | 0.5000 | 1.0000 | -0.6667 | -1.4142 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 2/7 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 3/6 (1 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.5000 | -0.3333 | -0.7071 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 2/7 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 3/6 (1 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.5000 | -0.3333 | -0.7071 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 2/7 (1 sessions) | 0.5000 | 0.5000 | 0.2500 | 0.7500 | 1/6 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.5000 | N/A | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 6/7 (4 sessions) | 1.3333 | 1.5000 | 0.2500 | 2.0000 | 4/6 (2 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | 0.8333 | 0.8165 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 3/7 (2 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.5000 | 3/6 (1 sessions) | 0.6667 | 1.0000 | 0.5000 | 1.0000 | -0.3333 | -0.5774 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 2/7 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 3/6 (1 sessions) | 2.0000 | 3.0000 | 1.5000 | 3.0000 | -2.0000 | -1.4142 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 6/7 (4 sessions) | 1.2417 | 1.1450 | 1.1038 | 1.2912 | 4/6 (2 sessions) | 1.7175 | 1.7425 | 1.0038 | 2.4562 | -0.4758 | -0.7847 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 3/7 (2 sessions) | 1.9367 | 2.1200 | 1.8400 | 2.1250 | 3/6 (1 sessions) | 2.4300 | 2.7600 | 2.1000 | 2.9250 | -0.4933 | -0.7485 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 2/7 (1 sessions) | 2.2350 | 2.2350 | 1.9775 | 2.4925 | 3/6 (1 sessions) | 2.9133 | 3.0900 | 2.8250 | 3.0900 | -0.6783 | -1.3868 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 3/7 (2 sessions) | 2.0696 | 2.1616 | 1.9270 | 2.2582 | 3/6 (1 sessions) | 2.6662 | 1.9162 | 1.7950 | 3.1625 | -0.5967 | -0.5438 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 3/7 (2 sessions) | 3.2817 | 3.1667 | 2.8021 | 3.7038 | 3/6 (1 sessions) | 4.4097 | 5.0370 | 3.9116 | 5.2214 | -1.1280 | -0.9477 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 2/7 (1 sessions) | 4.4835 | 4.4835 | 3.9875 | 4.9794 | 3/6 (1 sessions) | 5.3329 | 5.4059 | 5.1797 | 5.5226 | -0.8494 | -0.9894 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 6/7 (4 sessions) | 0.4350 | 0.4110 | 0.3288 | 0.5309 | 4/6 (2 sessions) | 0.5589 | 0.4548 | 0.3395 | 0.6742 | -0.1239 | -0.4313 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 3/7 (2 sessions) | 0.2988 | 0.2943 | 0.2442 | 0.3512 | 3/6 (1 sessions) | 0.3663 | 0.4671 | 0.2766 | 0.5064 | -0.0674 | -0.3557 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 2/7 (1 sessions) | 0.1906 | 0.1906 | 0.1583 | 0.2229 | 3/6 (1 sessions) | 0.1901 | 0.1422 | 0.1350 | 0.2213 | 0.0005 | 0.0050 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 6/7 (4 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 4/6 (2 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 3/7 (2 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 3/6 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 2/7 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 3/6 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 6/7 (4 sessions) | 0.5000 | 0.5000 | 0.5000 | 0.5000 | 4/6 (2 sessions) | 0.4375 | 0.3750 | 0.1875 | 0.6250 | 0.0625 | 0.2157 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 3/7 (2 sessions) | 0.6000 | 0.6000 | 0.5500 | 0.6500 | 3/6 (1 sessions) | 0.4667 | 0.5000 | 0.3500 | 0.6000 | 0.1333 | 0.6963 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 2/7 (1 sessions) | 0.6591 | 0.6591 | 0.6250 | 0.6932 | 3/6 (1 sessions) | 0.3333 | 0.3182 | 0.2273 | 0.4318 | 0.3258 | 1.8470 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 3/7 (2 sessions) | 2.1215 | 2.1337 | 1.2988 | 2.9504 | 3/6 (1 sessions) | 1.6332 | 1.4050 | 1.3347 | 1.8176 | 0.4883 | 0.3987 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 3/7 (2 sessions) | 1.5699 | 2.1153 | 1.1509 | 2.2616 | 3/6 (1 sessions) | 1.0911 | 1.0894 | 0.6665 | 1.5149 | 0.4788 | 0.4590 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 2/7 (1 sessions) | 1.8803 | 1.8803 | 1.8332 | 1.9273 | 3/6 (1 sessions) | 0.8009 | 0.3124 | 0.3054 | 1.0521 | 1.0794 | 1.5312 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 3/7 (3 sessions) | 1.2550 | 1.0250 | 0.6100 | 1.7850 | 5/6 (3 sessions) | 1.8630 | 2.4550 | 1.3800 | 2.5050 | -0.6080 | -0.5967 | not resampled |
| stage11_2.room_in_atr [SMALL] | 0/7 (0 sessions) | N/A | N/A | N/A | N/A | 2/6 (1 sessions) | 4.4314 | 4.4314 | 4.4069 | 4.4559 | N/A | N/A | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 7/7 (4 sessions) | 3.0000 | 3.0000 | 1.0000 | 5.0000 | 6/6 (3 sessions) | 3.3333 | 3.0000 | 3.0000 | 3.0000 | -0.3333 | -0.1607 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 7/7 (4 sessions) | 3.0000 | 3.0000 | 1.0000 | 5.0000 | 6/6 (3 sessions) | 2.6667 | 3.0000 | 3.0000 | 3.0000 | 0.3333 | 0.1607 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 5/7 (3 sessions) | 0.7070 | 0.3450 | 0.1950 | 0.4200 | 6/6 (3 sessions) | 1.3692 | 1.4575 | 0.2950 | 2.4925 | -0.6622 | -0.5744 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 5/7 (4 sessions) | 0.4281 | 0.4950 | 0.0450 | 0.5450 | 5/6 (3 sessions) | 0.3823 | 0.1205 | 0.0705 | 0.2800 | 0.0458 | 0.0927 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 3/7 (2 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 3/6 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 3/7 (2 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 3/6 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 3/7 (2 sessions) | 0.5867 | 0.4700 | 0.3400 | 0.7750 | 4/6 (2 sessions) | 1.9462 | 2.3225 | 1.8462 | 2.4225 | -1.3596 | -1.8984 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 4/7 (3 sessions) | 0.8538 | 0.8675 | 0.2188 | 1.5025 | 3/6 (1 sessions) | 0.8433 | 0.6200 | 0.5400 | 1.0350 | 0.0104 | 0.0145 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 3/7 (2 sessions) | 1.1232 | 0.9358 | 0.5886 | 1.5641 | 3/6 (1 sessions) | 3.3392 | 4.3037 | 2.8098 | 4.3510 | -2.2160 | -1.5571 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 3/7 (2 sessions) | 1.6710 | 1.6672 | 0.8539 | 2.4862 | 3/6 (1 sessions) | 1.5806 | 1.1315 | 0.9681 | 1.9686 | 0.0903 | 0.0654 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG [SMALL] | 8 | 3 | 4 | 4 | 57.14% | 66.67% | 50.00% |
| direction | SHORT [SMALL] | 5 | 3 | 3 | 2 | 42.86% | 33.33% | 60.00% |
| time_bucket | 09:35-10:00 [SMALL] | 3 | 3 | 1 | 2 | 14.29% | 33.33% | 33.33% |
| time_bucket | 10:00-10:30 [SMALL] | 4 | 4 | 3 | 1 | 42.86% | 16.67% | 75.00% |
| time_bucket | 11:00-12:00 [SMALL] | 1 | 1 | 1 | 0 | 14.29% | 0.00% | 100.00% |
| time_bucket | 12:00-13:30 [SMALL] | 2 | 1 | 0 | 2 | 0.00% | 33.33% | 0.00% |
| time_bucket | 13:30-15:00 [SMALL] | 1 | 1 | 1 | 0 | 14.29% | 0.00% | 100.00% |
| time_bucket | 15:00-close [SMALL] | 2 | 1 | 1 | 1 | 14.29% | 16.67% | 50.00% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 3 | 1 | 2 | 1 | 28.57% | 16.67% | 66.67% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 2 | 1 | 0 | 2 | 0.00% | 33.33% | 0.00% |
| ema9_20_alignment | EMA_UNAVAILABLE [SMALL] | 8 | 4 | 5 | 3 | 71.43% | 50.00% | 62.50% |
| price_vwap_alignment | VWAP_ALIGNED [SMALL] | 11 | 4 | 7 | 4 | 100.00% | 66.67% | 63.64% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 2 | 1 | 0 | 2 | 0.00% | 33.33% | 0.00% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED [SMALL] | 3 | 1 | 2 | 1 | 28.57% | 16.67% | 66.67% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 3 | 2 | 1 | 2 | 14.29% | 33.33% | 33.33% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 7 | 4 | 4 | 3 | 57.14% | 50.00% | 57.14% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 4 | 1 | 2 | 2 | 28.57% | 33.33% | 50.00% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 1 | 1 | 0 | 1 | 0.00% | 16.67% | 0.00% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE [SMALL] | 8 | 4 | 5 | 3 | 71.43% | 50.00% | 62.50% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 3 | 1 | 2 | 1 | 28.57% | 16.67% | 66.67% |
| prior_ema_cross | NO_PRIOR_CROSS [SMALL] | 8 | 4 | 5 | 3 | 71.43% | 50.00% | 62.50% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 2 | 1 | 0 | 2 | 0.00% | 33.33% | 0.00% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE [SMALL] | 8 | 4 | 5 | 3 | 71.43% | 50.00% | 62.50% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 5 | 2 | 2 | 3 | 28.57% | 50.00% | 40.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 2 | 1 | 0 | 2 | 0.00% | 33.33% | 0.00% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 5 | 2 | 4 | 1 | 57.14% | 16.67% | 80.00% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 6 | 4 | 3 | 3 | 42.86% | 50.00% | 50.00% |
| known_level_coverage | COMPLETE_V1_UNIVERSE [SMALL] | 13 | 4 | 7 | 6 | 100.00% | 100.00% | 53.85% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 3 | 1 | 2 | 1 | 28.57% | 16.67% | 66.67% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 2 | 1 | 0 | 2 | 0.00% | 33.33% | 0.00% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 1 | 1 | 1 | 0 | 14.29% | 0.00% | 100.00% |
| stage11_3.structure | UNAVAILABLE [SMALL] | 7 | 4 | 4 | 3 | 57.14% | 50.00% | 57.14% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 5 | 1 | 2 | 3 | 28.57% | 50.00% | 40.00% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 1 | 1 | 1 | 0 | 14.29% | 0.00% | 100.00% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE [SMALL] | 7 | 4 | 4 | 3 | 57.14% | 50.00% | 57.14% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 2 | 1 | 0 | 2 | 0.00% | 33.33% | 0.00% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 4 | 2 | 3 | 1 | 42.86% | 16.67% | 75.00% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 7 | 4 | 4 | 3 | 57.14% | 50.00% | 57.14% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 3 | 2 | 1 | 2 | 14.29% | 33.33% | 33.33% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 3 | 1 | 2 | 1 | 28.57% | 16.67% | 66.67% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 7 | 4 | 4 | 3 | 57.14% | 50.00% | 57.14% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 6 | 3 | 3 | 3 | 42.86% | 50.00% | 50.00% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 4 | 2 | 3 | 1 | 42.86% | 16.67% | 75.00% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 3 | 2 | 1 | 2 | 14.29% | 33.33% | 33.33% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE [SMALL] | 13 | 4 | 7 | 6 | 100.00% | 100.00% | 53.85% |


## Complete monthly stability: LONG

Every feature is shown, not only those selected for the decision summary. Monthly intervals are not estimated. Monthly medians, quartiles, mean differences and category denominators remain explicit. September contains only four sessions.

### 2026-01


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 40/40 (15 sessions) | 1.0484 | 0.9850 | 0.7800 | 1.2700 | 9/9 (6 sessions) | 1.1917 | 1.0600 | 0.7200 | 1.3200 | -0.1433 | -0.4071 | not resampled |
| body_size [SMALL] | 40/40 (15 sessions) | 0.6568 | 0.5650 | 0.3675 | 0.9262 | 9/9 (6 sessions) | 0.3394 | 0.3500 | 0.1800 | 0.4700 | 0.3174 | 0.8203 | not resampled |
| directional_body [SMALL] | 40/40 (15 sessions) | 0.6568 | 0.5650 | 0.3675 | 0.9262 | 9/9 (6 sessions) | 0.3394 | 0.3500 | 0.1800 | 0.4700 | 0.3174 | 0.8203 | not resampled |
| candle_range [SMALL] | 40/40 (15 sessions) | 0.9050 | 0.8325 | 0.5634 | 1.2338 | 9/9 (6 sessions) | 0.8050 | 0.6100 | 0.4100 | 1.1800 | 0.1000 | 0.2192 | not resampled |
| body_range_ratio [SMALL] | 40/40 (15 sessions) | 0.6980 | 0.7394 | 0.5599 | 0.8361 | 9/9 (6 sessions) | 0.4747 | 0.4390 | 0.4151 | 0.6481 | 0.2232 | 1.1635 | not resampled |
| directional_body_range_ratio [SMALL] | 40/40 (15 sessions) | 0.6980 | 0.7394 | 0.5599 | 0.8361 | 9/9 (6 sessions) | 0.4747 | 0.4390 | 0.4151 | 0.6481 | 0.2232 | 1.1635 | not resampled |
| close_location [SMALL] | 40/40 (15 sessions) | 0.8385 | 0.8802 | 0.7924 | 0.9260 | 9/9 (6 sessions) | 0.8308 | 0.9344 | 0.8293 | 0.9569 | 0.0077 | 0.0506 | not resampled |
| directional_close_location [SMALL] | 40/40 (15 sessions) | 0.8385 | 0.8802 | 0.7924 | 0.9260 | 9/9 (6 sessions) | 0.8308 | 0.9344 | 0.8293 | 0.9569 | 0.0077 | 0.0506 | not resampled |
| distance_beyond_level [SMALL] | 40/40 (15 sessions) | 0.3315 | 0.2875 | 0.1350 | 0.4638 | 9/9 (6 sessions) | 0.1438 | 0.1100 | 0.0900 | 0.1350 | 0.1877 | 0.8043 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 24/40 (10 sessions) | 0.4858 | 0.4162 | 0.2139 | 0.6450 | 6/9 (4 sessions) | 0.1615 | 0.1691 | 0.0875 | 0.2421 | 0.3242 | 1.0045 | not resampled |
| candle_volume [SMALL] | 40/40 (15 sessions) | 945860.7000 | 820497.0000 | 594087.0000 | 1270288.2500 | 9/9 (6 sessions) | 1494014.5556 | 1001537.0000 | 428507.0000 | 1115133.0000 | -548153.8556 | -0.6484 | not resampled |
| relative_volume_prior_6 [SMALL] | 30/40 (11 sessions) | 0.9998 | 0.9724 | 0.7073 | 1.1121 | 7/9 (5 sessions) | 1.5285 | 0.8628 | 0.8104 | 0.9263 | -0.5287 | -0.6467 | not resampled |
| atr14 [SMALL] | 24/40 (10 sessions) | 0.6983 | 0.6584 | 0.5037 | 0.8851 | 6/9 (4 sessions) | 0.5376 | 0.4947 | 0.4445 | 0.6346 | 0.1607 | 0.6849 | not resampled |
| minutes_since_open [SMALL] | 40/40 (15 sessions) | 130.8750 | 105.0000 | 33.7500 | 231.2500 | 9/9 (6 sessions) | 161.1111 | 195.0000 | 45.0000 | 220.0000 | -30.2361 | -0.2759 | not resampled |
| minutes_since_ema_cross [SMALL] | 11/40 (6 sessions) | 45.4545 | 35.0000 | 20.0000 | 60.0000 | 3/9 (3 sessions) | 48.3333 | 25.0000 | 20.0000 | 65.0000 | -2.8788 | -0.0710 | not resampled |
| break_attempt_rank [SMALL] | 40/40 (15 sessions) | 8.3750 | 8.0000 | 3.0000 | 13.0000 | 9/9 (6 sessions) | 8.8889 | 7.0000 | 4.0000 | 13.0000 | -0.5139 | -0.0856 | not resampled |
| valid_hold_sequence_rank [SMALL] | 40/40 (15 sessions) | 3.9000 | 4.0000 | 2.0000 | 5.2500 | 9/9 (6 sessions) | 3.8889 | 4.0000 | 2.0000 | 5.0000 | 0.0111 | 0.0047 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 21/40 (9 sessions) | 0.1815 | 0.1884 | 0.0387 | 0.2445 | 5/9 (4 sessions) | 0.1395 | 0.1051 | 0.0572 | 0.1311 | 0.0420 | 0.2783 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 21/40 (9 sessions) | 0.2836 | 0.2688 | 0.0515 | 0.4784 | 5/9 (4 sessions) | 0.2697 | 0.2453 | 0.1150 | 0.3845 | 0.0139 | 0.0639 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 27/40 (10 sessions) | 0.0898 | 0.0872 | 0.0337 | 0.1446 | 6/9 (4 sessions) | 0.0246 | -0.0068 | -0.0123 | 0.0281 | 0.0652 | 0.7949 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 26/40 (10 sessions) | 0.0217 | 0.0328 | -0.0260 | 0.0769 | 6/9 (4 sessions) | -0.0095 | -0.0372 | -0.0600 | 0.0067 | 0.0312 | 0.4092 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 24/40 (10 sessions) | 0.0036 | 0.0131 | -0.0360 | 0.0558 | 6/9 (4 sessions) | -0.0397 | -0.0402 | -0.0539 | -0.0223 | 0.0434 | 0.6870 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 20/40 (8 sessions) | 0.0299 | 0.0369 | -0.0016 | 0.0532 | 5/9 (4 sessions) | -0.0107 | 0.0005 | -0.0186 | 0.0009 | 0.0406 | 1.0933 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 20/40 (8 sessions) | 0.0019 | -0.0038 | -0.0243 | 0.0299 | 5/9 (4 sessions) | -0.0263 | -0.0117 | -0.0419 | -0.0053 | 0.0282 | 0.7448 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 19/40 (8 sessions) | -0.0060 | -0.0103 | -0.0274 | 0.0194 | 5/9 (4 sessions) | -0.0333 | -0.0217 | -0.0329 | -0.0200 | 0.0273 | 0.7072 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 40/40 (15 sessions) | 0.0562 | 0.0155 | -0.0017 | 0.0710 | 9/9 (6 sessions) | 0.0372 | 0.0102 | 0.0035 | 0.0772 | 0.0191 | 0.1969 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 37/40 (13 sessions) | 0.0151 | 0.0104 | -0.0044 | 0.0235 | 8/9 (6 sessions) | 0.0145 | 0.0076 | -0.0037 | 0.0245 | 0.0005 | 0.0113 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 36/40 (13 sessions) | 0.0068 | 0.0039 | -0.0082 | 0.0154 | 7/9 (5 sessions) | -0.0033 | 0.0002 | -0.0132 | 0.0068 | 0.0101 | 0.3149 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 19/40 (8 sessions) | 0.2632 | 0.0000 | 0.0000 | 0.0000 | 5/9 (4 sessions) | 0.2000 | 0.0000 | 0.0000 | 0.0000 | 0.0632 | 0.1163 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 14/40 (7 sessions) | 0.5714 | 0.0000 | 0.0000 | 1.0000 | 5/9 (4 sessions) | 0.4000 | 0.0000 | 0.0000 | 1.0000 | 0.1714 | 0.2168 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 12/40 (7 sessions) | 1.0000 | 1.0000 | 0.7500 | 1.0000 | 4/9 (4 sessions) | 0.7500 | 1.0000 | 0.7500 | 1.0000 | 0.2500 | 0.3162 | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 24/40 (10 sessions) | 0.2917 | 0.0000 | 0.0000 | 0.2500 | 6/9 (4 sessions) | 0.5000 | 0.0000 | 0.0000 | 0.7500 | -0.2083 | -0.3409 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 21/40 (9 sessions) | 0.4286 | 0.0000 | 0.0000 | 1.0000 | 5/9 (4 sessions) | 0.2000 | 0.0000 | 0.0000 | 0.0000 | 0.2286 | 0.3551 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 14/40 (7 sessions) | 0.5714 | 1.0000 | 0.0000 | 1.0000 | 5/9 (4 sessions) | 0.6000 | 1.0000 | 0.0000 | 1.0000 | -0.0286 | -0.0548 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 19/40 (8 sessions) | 0.1053 | 0.0000 | 0.0000 | 0.0000 | 5/9 (4 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1053 | 0.3691 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 14/40 (7 sessions) | 0.3571 | 0.0000 | 0.0000 | 1.0000 | 5/9 (4 sessions) | 0.6000 | 0.0000 | 0.0000 | 0.0000 | -0.2429 | -0.3103 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 12/40 (7 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | 4/9 (4 sessions) | 0.7500 | 0.0000 | 0.0000 | 0.7500 | -0.2500 | -0.2996 | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 31/40 (11 sessions) | 1.0323 | 1.0000 | 0.0000 | 2.0000 | 7/9 (5 sessions) | 0.7143 | 0.0000 | 0.0000 | 1.5000 | 0.3180 | 0.2801 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 24/40 (10 sessions) | 1.4583 | 1.5000 | 0.0000 | 2.0000 | 6/9 (4 sessions) | 1.6667 | 1.5000 | 0.2500 | 2.0000 | -0.2083 | -0.1456 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 19/40 (8 sessions) | 2.3684 | 2.0000 | 1.0000 | 3.5000 | 5/9 (4 sessions) | 1.4000 | 1.0000 | 1.0000 | 2.0000 | 0.9684 | 0.5294 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 31/40 (11 sessions) | 1.5588 | 1.4600 | 1.0400 | 1.8475 | 7/9 (5 sessions) | 1.4918 | 1.1399 | 0.9275 | 2.0350 | 0.0669 | 0.1074 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 24/40 (10 sessions) | 1.9510 | 1.8825 | 1.5688 | 2.2650 | 6/9 (4 sessions) | 1.5325 | 1.3650 | 1.1225 | 1.8025 | 0.4185 | 0.7341 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 19/40 (8 sessions) | 2.7787 | 2.2900 | 1.8725 | 2.9100 | 5/9 (4 sessions) | 2.0770 | 1.7200 | 1.5700 | 2.4600 | 0.7017 | 0.5015 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 24/40 (10 sessions) | 2.1053 | 2.0532 | 1.6809 | 2.3526 | 6/9 (4 sessions) | 2.3022 | 2.3605 | 1.9369 | 2.7187 | -0.1968 | -0.3600 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 24/40 (10 sessions) | 2.9257 | 2.7414 | 2.4647 | 3.2810 | 6/9 (4 sessions) | 2.8263 | 2.7580 | 2.4563 | 3.1196 | 0.0994 | 0.1415 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 19/40 (8 sessions) | 4.0745 | 3.6887 | 3.3562 | 4.4652 | 5/9 (4 sessions) | 4.2512 | 4.5271 | 4.0132 | 4.5604 | -0.1768 | -0.1829 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 31/40 (11 sessions) | 0.4012 | 0.4082 | 0.2706 | 0.5569 | 7/9 (5 sessions) | 0.1514 | 0.1506 | 0.0345 | 0.2486 | 0.2498 | 1.1971 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 24/40 (10 sessions) | 0.2013 | 0.1533 | 0.0866 | 0.2642 | 6/9 (4 sessions) | 0.1962 | 0.2000 | 0.1374 | 0.2451 | 0.0051 | 0.0336 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 19/40 (8 sessions) | 0.1345 | 0.1110 | 0.0626 | 0.1755 | 5/9 (4 sessions) | 0.1729 | 0.2295 | 0.0591 | 0.2535 | -0.0384 | -0.3685 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 31/40 (11 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 7/9 (5 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 24/40 (10 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 6/9 (4 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 19/40 (8 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 5/9 (4 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 31/40 (11 sessions) | 0.5242 | 0.5000 | 0.3750 | 0.7500 | 7/9 (5 sessions) | 0.4643 | 0.2500 | 0.2500 | 0.6250 | 0.0599 | 0.2559 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 24/40 (10 sessions) | 0.5208 | 0.5000 | 0.4000 | 0.6000 | 6/9 (4 sessions) | 0.5500 | 0.5500 | 0.4250 | 0.6750 | -0.0292 | -0.2036 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 19/40 (8 sessions) | 0.5431 | 0.5000 | 0.4773 | 0.5682 | 5/9 (4 sessions) | 0.5455 | 0.4545 | 0.4545 | 0.6364 | -0.0024 | -0.0205 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 24/40 (10 sessions) | 0.9574 | 0.7938 | 0.5775 | 1.0741 | 6/9 (4 sessions) | 1.1104 | 0.8336 | 0.7669 | 0.9293 | -0.1530 | -0.2052 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 24/40 (10 sessions) | 0.7495 | 0.5658 | 0.4225 | 0.8633 | 6/9 (4 sessions) | 0.9304 | 0.5593 | 0.4842 | 0.8149 | -0.1810 | -0.2614 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 21/40 (9 sessions) | 0.6383 | 0.4124 | 0.1940 | 0.9670 | 5/9 (4 sessions) | 0.9017 | 0.6132 | 0.2360 | 0.8452 | -0.2633 | -0.3856 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 28/40 (11 sessions) | 2.1935 | 2.1573 | 0.5310 | 3.7600 | 6/9 (4 sessions) | 2.0159 | 2.3950 | 0.5962 | 3.3088 | 0.1776 | 0.1097 | not resampled |
| stage11_2.room_in_atr [SMALL] | 16/40 (7 sessions) | 3.6408 | 2.9967 | 0.3728 | 5.5079 | 3/9 (2 sessions) | 1.1477 | 0.1810 | 0.1672 | 1.6449 | 2.4931 | 0.8115 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 40/40 (15 sessions) | 1.0000 | 1.0000 | 0.0000 | 1.2500 | 9/9 (6 sessions) | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 40/40 (15 sessions) | 4.9500 | 5.0000 | 4.0000 | 6.0000 | 9/9 (6 sessions) | 4.8889 | 5.0000 | 5.0000 | 5.0000 | 0.0611 | 0.0673 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 28/40 (11 sessions) | 2.1935 | 2.1573 | 0.5310 | 3.7600 | 6/9 (4 sessions) | 2.0159 | 2.3950 | 0.5962 | 3.3088 | 0.1776 | 0.1097 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 40/40 (15 sessions) | 0.2787 | 0.2102 | 0.1026 | 0.3925 | 9/9 (6 sessions) | 0.1438 | 0.1100 | 0.0900 | 0.1350 | 0.1349 | 0.6104 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 24/40 (10 sessions) | 0.2083 | 0.0000 | 0.0000 | 0.0000 | 6/9 (4 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.7500 | -0.1250 | -0.2875 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 24/40 (10 sessions) | 0.2083 | 0.0000 | 0.0000 | 0.0000 | 6/9 (4 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.7500 | -0.1250 | -0.2875 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 30/40 (11 sessions) | 0.4598 | 0.2900 | 0.1512 | 0.6488 | 7/9 (5 sessions) | 0.5286 | 0.3700 | 0.2900 | 0.5578 | -0.0689 | -0.1463 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 32/40 (12 sessions) | 1.4042 | 1.2150 | 0.9912 | 1.9025 | 7/9 (5 sessions) | 0.8739 | 0.5100 | 0.2222 | 1.4475 | 0.5303 | 0.7825 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 24/40 (10 sessions) | 0.8626 | 0.5168 | 0.2096 | 0.8109 | 6/9 (4 sessions) | 1.0813 | 1.0035 | 0.6833 | 1.3915 | -0.2187 | -0.2276 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 24/40 (10 sessions) | 1.8545 | 1.9162 | 1.2654 | 2.3355 | 6/9 (4 sessions) | 1.0053 | 0.7612 | 0.4742 | 1.4525 | 0.8492 | 1.3355 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG | 49 | 15 | 40 | 9 | 100.00% | 100.00% | 81.63% |
| time_bucket | 09:35-10:00 [SMALL] | 11 | 10 | 9 | 2 | 22.50% | 22.22% | 81.82% |
| time_bucket | 10:00-10:30 [SMALL] | 8 | 6 | 7 | 1 | 17.50% | 11.11% | 87.50% |
| time_bucket | 10:30-11:00 [SMALL] | 1 | 1 | 1 | 0 | 2.50% | 0.00% | 100.00% |
| time_bucket | 11:00-12:00 [SMALL] | 8 | 4 | 7 | 1 | 17.50% | 11.11% | 87.50% |
| time_bucket | 12:00-13:30 [SMALL] | 10 | 6 | 7 | 3 | 17.50% | 33.33% | 70.00% |
| time_bucket | 13:30-15:00 [SMALL] | 8 | 5 | 7 | 1 | 17.50% | 11.11% | 87.50% |
| time_bucket | 15:00-close [SMALL] | 3 | 2 | 2 | 1 | 5.00% | 11.11% | 66.67% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 13 | 6 | 11 | 2 | 27.50% | 22.22% | 84.62% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 13 | 7 | 10 | 3 | 25.00% | 33.33% | 76.92% |
| ema9_20_alignment | EMA_UNAVAILABLE [SMALL] | 23 | 14 | 19 | 4 | 47.50% | 44.44% | 82.61% |
| price_vwap_alignment | VWAP_ALIGNED | 39 | 15 | 32 | 7 | 80.00% | 77.78% | 82.05% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 10 | 4 | 8 | 2 | 20.00% | 22.22% | 80.00% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED [SMALL] | 24 | 9 | 19 | 5 | 47.50% | 55.56% | 79.17% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 11 | 5 | 9 | 2 | 22.50% | 22.22% | 81.82% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 14 | 13 | 12 | 2 | 30.00% | 22.22% | 85.71% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 17 | 7 | 13 | 4 | 32.50% | 44.44% | 76.47% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 9 | 4 | 8 | 1 | 20.00% | 11.11% | 88.89% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE [SMALL] | 23 | 14 | 19 | 4 | 47.50% | 44.44% | 82.61% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 2 | 2 | 2 | 0 | 5.00% | 0.00% | 100.00% |
| prior_ema_cross | NO_PRIOR_CROSS | 35 | 15 | 29 | 6 | 72.50% | 66.67% | 82.86% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 12 | 6 | 9 | 3 | 22.50% | 33.33% | 75.00% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 38 | 12 | 32 | 6 | 80.00% | 66.67% | 84.21% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 11 | 7 | 8 | 3 | 20.00% | 33.33% | 72.73% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 3 | 3 | 3 | 0 | 7.50% | 0.00% | 100.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 9 | 3 | 8 | 1 | 20.00% | 11.11% | 88.89% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 7 | 3 | 5 | 2 | 12.50% | 22.22% | 71.43% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 15 | 5 | 12 | 3 | 30.00% | 33.33% | 80.00% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 15 | 10 | 12 | 3 | 30.00% | 33.33% | 80.00% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 48 | 14 | 39 | 9 | 97.50% | 100.00% | 81.25% |
| known_level_coverage | PARTIAL_UNAVAILABLE [SMALL] | 1 | 1 | 1 | 0 | 2.50% | 0.00% | 100.00% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 13 | 7 | 11 | 2 | 27.50% | 22.22% | 84.62% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 4 | 4 | 3 | 1 | 7.50% | 11.11% | 75.00% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 12 | 6 | 9 | 3 | 22.50% | 33.33% | 75.00% |
| stage11_3.structure | UNAVAILABLE [SMALL] | 20 | 13 | 17 | 3 | 42.50% | 33.33% | 85.00% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 4 | 4 | 3 | 1 | 7.50% | 11.11% | 75.00% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 25 | 9 | 20 | 5 | 50.00% | 55.56% | 80.00% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE [SMALL] | 20 | 13 | 17 | 3 | 42.50% | 33.33% | 85.00% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 12 | 7 | 10 | 2 | 25.00% | 22.22% | 83.33% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 18 | 8 | 14 | 4 | 35.00% | 44.44% | 77.78% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 19 | 13 | 16 | 3 | 40.00% | 33.33% | 84.21% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 9 | 6 | 6 | 3 | 15.00% | 33.33% | 66.67% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 20 | 8 | 17 | 3 | 42.50% | 33.33% | 85.00% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 20 | 13 | 17 | 3 | 42.50% | 33.33% | 85.00% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 12 | 11 | 10 | 2 | 25.00% | 22.22% | 83.33% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 13 | 4 | 10 | 3 | 25.00% | 33.33% | 76.92% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 6 | 3 | 4 | 2 | 10.00% | 22.22% | 66.67% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 18 | 6 | 16 | 2 | 40.00% | 22.22% | 88.89% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 49 | 15 | 40 | 9 | 100.00% | 100.00% | 81.63% |


### 2026-02


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 35/35 (14 sessions) | 1.6523 | 1.6675 | 1.2500 | 1.9600 | 11/11 (8 sessions) | 1.6091 | 1.5500 | 1.0500 | 1.9600 | 0.0432 | 0.0623 | not resampled |
| body_size [SMALL] | 35/35 (14 sessions) | 0.9944 | 0.9100 | 0.6725 | 1.3225 | 11/11 (8 sessions) | 0.6864 | 0.7150 | 0.5350 | 0.8600 | 0.3080 | 0.7653 | not resampled |
| directional_body [SMALL] | 35/35 (14 sessions) | 0.9944 | 0.9100 | 0.6725 | 1.3225 | 11/11 (8 sessions) | 0.6864 | 0.7150 | 0.5350 | 0.8600 | 0.3080 | 0.7653 | not resampled |
| candle_range [SMALL] | 35/35 (14 sessions) | 1.4185 | 1.2750 | 0.9800 | 1.7550 | 11/11 (8 sessions) | 1.1768 | 1.2250 | 0.8225 | 1.4200 | 0.2417 | 0.4348 | not resampled |
| body_range_ratio [SMALL] | 35/35 (14 sessions) | 0.7076 | 0.7396 | 0.5956 | 0.8241 | 11/11 (8 sessions) | 0.5956 | 0.5545 | 0.5043 | 0.6446 | 0.1120 | 0.7315 | not resampled |
| directional_body_range_ratio [SMALL] | 35/35 (14 sessions) | 0.7076 | 0.7396 | 0.5956 | 0.8241 | 11/11 (8 sessions) | 0.5956 | 0.5545 | 0.5043 | 0.6446 | 0.1120 | 0.7315 | not resampled |
| close_location [SMALL] | 35/35 (14 sessions) | 0.8262 | 0.8409 | 0.7765 | 0.9130 | 11/11 (8 sessions) | 0.8726 | 0.9290 | 0.7996 | 0.9568 | -0.0464 | -0.3761 | not resampled |
| directional_close_location [SMALL] | 35/35 (14 sessions) | 0.8262 | 0.8409 | 0.7765 | 0.9130 | 11/11 (8 sessions) | 0.8726 | 0.9290 | 0.7996 | 0.9568 | -0.0464 | -0.3761 | not resampled |
| distance_beyond_level [SMALL] | 35/35 (14 sessions) | 0.5321 | 0.4300 | 0.2225 | 0.7164 | 11/11 (8 sessions) | 0.3000 | 0.3200 | 0.0850 | 0.4800 | 0.2321 | 0.6524 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 17/35 (7 sessions) | 0.4742 | 0.3735 | 0.1862 | 0.6971 | 6/11 (5 sessions) | 0.2325 | 0.1324 | 0.0835 | 0.2553 | 0.2417 | 0.6307 | not resampled |
| candle_volume [SMALL] | 35/35 (14 sessions) | 1241527.1143 | 1004377.0000 | 775661.0000 | 1502318.5000 | 11/11 (8 sessions) | 994023.9091 | 902849.0000 | 556886.0000 | 1327788.0000 | 247503.2052 | 0.3781 | not resampled |
| relative_volume_prior_6 [SMALL] | 24/35 (9 sessions) | 1.1142 | 0.9503 | 0.7669 | 1.3044 | 8/11 (6 sessions) | 0.9185 | 0.8884 | 0.7960 | 1.0588 | 0.1957 | 0.4309 | not resampled |
| atr14 [SMALL] | 17/35 (7 sessions) | 1.1867 | 1.2400 | 0.8894 | 1.3931 | 6/11 (5 sessions) | 0.9357 | 0.7890 | 0.6857 | 1.1270 | 0.2509 | 0.6615 | not resampled |
| minutes_since_open [SMALL] | 35/35 (14 sessions) | 109.2857 | 65.0000 | 25.0000 | 160.0000 | 11/11 (8 sessions) | 122.2727 | 100.0000 | 32.5000 | 175.0000 | -12.9870 | -0.1223 | not resampled |
| minutes_since_ema_cross [SMALL] | 11/35 (6 sessions) | 31.8182 | 30.0000 | 10.0000 | 37.5000 | 3/11 (3 sessions) | 50.0000 | 50.0000 | 25.0000 | 75.0000 | -18.1818 | -0.4879 | not resampled |
| break_attempt_rank [SMALL] | 35/35 (14 sessions) | 6.6571 | 7.0000 | 3.0000 | 9.5000 | 11/11 (8 sessions) | 6.6364 | 5.0000 | 3.5000 | 10.5000 | 0.0208 | 0.0047 | not resampled |
| valid_hold_sequence_rank [SMALL] | 35/35 (14 sessions) | 3.4000 | 3.0000 | 2.0000 | 5.0000 | 11/11 (8 sessions) | 3.8182 | 3.0000 | 1.5000 | 6.0000 | -0.4182 | -0.1923 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 15/35 (7 sessions) | 0.3580 | 0.3138 | 0.0802 | 0.5591 | 6/11 (5 sessions) | 0.3957 | 0.2789 | 0.0386 | 0.6166 | -0.0377 | -0.1096 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 15/35 (7 sessions) | 0.3137 | 0.2606 | 0.0985 | 0.4337 | 6/11 (5 sessions) | 0.3444 | 0.2538 | 0.0574 | 0.6432 | -0.0307 | -0.1056 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 23/35 (9 sessions) | 0.1936 | 0.1868 | 0.0765 | 0.2638 | 8/11 (6 sessions) | 0.1124 | 0.1327 | 0.0908 | 0.1697 | 0.0811 | 0.5032 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 22/35 (9 sessions) | 0.0977 | 0.0786 | -0.0162 | 0.1381 | 6/11 (5 sessions) | 0.0565 | 0.0887 | 0.0328 | 0.1221 | 0.0412 | 0.2385 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 21/35 (9 sessions) | 0.0783 | 0.0643 | -0.0162 | 0.1461 | 6/11 (5 sessions) | 0.0446 | 0.0675 | 0.0057 | 0.1012 | 0.0337 | 0.2163 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 15/35 (7 sessions) | 0.1012 | 0.1363 | 0.0176 | 0.1591 | 5/11 (4 sessions) | 0.0663 | 0.0611 | 0.0577 | 0.1072 | 0.0349 | 0.2923 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 14/35 (7 sessions) | 0.0386 | 0.0581 | -0.0324 | 0.1086 | 5/11 (4 sessions) | 0.0375 | 0.0539 | 0.0267 | 0.0560 | 0.0011 | 0.0109 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 14/35 (7 sessions) | 0.0296 | 0.0384 | -0.0387 | 0.1010 | 5/11 (4 sessions) | 0.0324 | 0.0419 | 0.0113 | 0.0461 | -0.0027 | -0.0274 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 35/35 (14 sessions) | 0.1291 | 0.0347 | 0.0189 | 0.1579 | 11/11 (8 sessions) | 0.0893 | 0.0244 | 0.0040 | 0.0777 | 0.0398 | 0.2304 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 28/35 (9 sessions) | 0.0341 | 0.0195 | 0.0096 | 0.0444 | 10/11 (8 sessions) | 0.0291 | 0.0055 | -0.0075 | 0.0472 | 0.0050 | 0.0851 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 28/35 (9 sessions) | 0.0336 | 0.0239 | 0.0109 | 0.0442 | 8/11 (6 sessions) | 0.0180 | 0.0015 | -0.0040 | 0.0339 | 0.0157 | 0.4013 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 12/35 (6 sessions) | 0.3333 | 0.0000 | 0.0000 | 1.0000 | 5/11 (4 sessions) | 0.2000 | 0.0000 | 0.0000 | 0.0000 | 0.1333 | 0.2774 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 9/35 (5 sessions) | 0.8889 | 1.0000 | 1.0000 | 1.0000 | 4/11 (4 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | 0.3889 | 0.6540 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 5/35 (5 sessions) | 1.4000 | 1.0000 | 1.0000 | 2.0000 | 2/11 (2 sessions) | 2.0000 | 2.0000 | 1.5000 | 2.5000 | -0.6000 | -0.5000 | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 17/35 (7 sessions) | 0.2941 | 0.0000 | 0.0000 | 1.0000 | 6/11 (5 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.2941 | 0.7174 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 15/35 (7 sessions) | 0.5333 | 0.0000 | 0.0000 | 1.0000 | 6/11 (5 sessions) | 0.1667 | 0.0000 | 0.0000 | 0.0000 | 0.3667 | 0.6237 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 9/35 (5 sessions) | 0.6667 | 1.0000 | 0.0000 | 1.0000 | 4/11 (4 sessions) | 0.7500 | 1.0000 | 0.7500 | 1.0000 | -0.0833 | -0.1268 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 12/35 (6 sessions) | 0.0833 | 0.0000 | 0.0000 | 0.0000 | 5/11 (4 sessions) | 0.2000 | 0.0000 | 0.0000 | 0.0000 | -0.1167 | -0.3449 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 9/35 (5 sessions) | 0.1111 | 0.0000 | 0.0000 | 0.0000 | 4/11 (4 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | -0.3889 | -0.9385 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 5/35 (5 sessions) | 0.2000 | 0.0000 | 0.0000 | 0.0000 | 2/11 (2 sessions) | 0.5000 | 0.5000 | 0.2500 | 0.7500 | -0.3000 | -0.5883 | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 25/35 (9 sessions) | 1.2400 | 1.0000 | 0.0000 | 2.0000 | 8/11 (6 sessions) | 1.0000 | 1.0000 | 0.0000 | 1.2500 | 0.2400 | 0.2098 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 21/35 (9 sessions) | 2.3333 | 2.0000 | 1.0000 | 3.0000 | 6/11 (5 sessions) | 1.5000 | 1.0000 | 1.0000 | 2.5000 | 0.8333 | 0.5285 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 14/35 (7 sessions) | 3.4286 | 3.0000 | 2.0000 | 4.7500 | 5/11 (4 sessions) | 3.0000 | 3.0000 | 2.0000 | 3.0000 | 0.4286 | 0.1958 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 25/35 (9 sessions) | 2.6577 | 2.5400 | 2.1050 | 2.9900 | 8/11 (6 sessions) | 2.0711 | 2.1094 | 1.4588 | 2.4512 | 0.5866 | 0.6077 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 21/35 (9 sessions) | 3.6536 | 3.1250 | 2.8150 | 5.0100 | 6/11 (5 sessions) | 3.0031 | 2.1318 | 1.6013 | 3.3009 | 0.6504 | 0.3831 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 14/35 (7 sessions) | 4.5489 | 4.0600 | 3.1774 | 6.0488 | 5/11 (4 sessions) | 5.0040 | 4.4300 | 3.2200 | 7.4600 | -0.4551 | -0.2359 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 17/35 (7 sessions) | 2.2498 | 1.8684 | 1.7221 | 2.8560 | 6/11 (5 sessions) | 1.9531 | 1.9040 | 1.7511 | 2.1284 | 0.2967 | 0.4652 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 17/35 (7 sessions) | 2.9124 | 2.9370 | 2.2791 | 3.3951 | 6/11 (5 sessions) | 2.9453 | 2.3466 | 2.1905 | 3.6212 | -0.0329 | -0.0374 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 14/35 (7 sessions) | 4.1196 | 4.1649 | 3.2975 | 4.6459 | 5/11 (4 sessions) | 4.8617 | 4.9017 | 4.5824 | 5.0608 | -0.7422 | -0.8088 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 25/35 (9 sessions) | 0.4014 | 0.3706 | 0.1586 | 0.5048 | 8/11 (6 sessions) | 0.3763 | 0.2569 | 0.1876 | 0.5645 | 0.0251 | 0.0855 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 21/35 (9 sessions) | 0.2389 | 0.2448 | 0.0951 | 0.3757 | 6/11 (5 sessions) | 0.3722 | 0.3623 | 0.3014 | 0.4354 | -0.1333 | -0.8035 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 14/35 (7 sessions) | 0.1516 | 0.1195 | 0.0527 | 0.2580 | 5/11 (4 sessions) | 0.2187 | 0.2045 | 0.0744 | 0.3491 | -0.0671 | -0.5063 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 25/35 (9 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 8/11 (6 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 21/35 (9 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 6/11 (5 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 14/35 (7 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 5/11 (4 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 25/35 (9 sessions) | 0.4900 | 0.5000 | 0.2500 | 0.7500 | 8/11 (6 sessions) | 0.4688 | 0.5000 | 0.2500 | 0.5625 | 0.0212 | 0.0839 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 21/35 (9 sessions) | 0.4857 | 0.5000 | 0.4000 | 0.6000 | 6/11 (5 sessions) | 0.5000 | 0.5500 | 0.4250 | 0.6000 | -0.0143 | -0.0889 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 14/35 (7 sessions) | 0.5065 | 0.5000 | 0.4545 | 0.5455 | 5/11 (4 sessions) | 0.4727 | 0.4091 | 0.4091 | 0.5455 | 0.0338 | 0.3448 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 17/35 (7 sessions) | 1.1670 | 1.3778 | 0.6108 | 1.6894 | 6/11 (5 sessions) | 1.0216 | 0.6619 | 0.5701 | 1.5597 | 0.1454 | 0.2154 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 17/35 (7 sessions) | 0.6423 | 0.3937 | 0.3357 | 0.7269 | 6/11 (5 sessions) | 0.5209 | 0.2649 | 0.0624 | 0.9302 | 0.1214 | 0.1963 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 15/35 (7 sessions) | 0.5249 | 0.4419 | 0.2304 | 0.6740 | 6/11 (5 sessions) | 0.4411 | 0.3335 | 0.1421 | 0.6920 | 0.0838 | 0.1938 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 30/35 (12 sessions) | 3.0505 | 2.4450 | 1.2075 | 4.0773 | 8/11 (6 sessions) | 2.7164 | 3.5400 | 1.5425 | 3.9150 | 0.3341 | 0.1259 | not resampled |
| stage11_2.room_in_atr [SMALL] | 16/35 (6 sessions) | 3.3398 | 2.5197 | 0.5841 | 4.4336 | 5/11 (4 sessions) | 2.5224 | 2.5363 | 0.4684 | 3.3694 | 0.8174 | 0.2508 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 35/35 (14 sessions) | 1.5714 | 2.0000 | 1.0000 | 2.0000 | 11/11 (8 sessions) | 1.0909 | 1.0000 | 0.5000 | 2.0000 | 0.4805 | 0.5509 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 35/35 (14 sessions) | 4.4286 | 4.0000 | 4.0000 | 5.0000 | 11/11 (8 sessions) | 4.9091 | 5.0000 | 4.0000 | 5.5000 | -0.4805 | -0.5509 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 30/35 (12 sessions) | 3.0505 | 2.4450 | 1.2075 | 4.0773 | 8/11 (6 sessions) | 2.7164 | 3.5400 | 1.5425 | 3.9150 | 0.3341 | 0.1259 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 35/35 (14 sessions) | 0.4093 | 0.3503 | 0.1450 | 0.6000 | 11/11 (8 sessions) | 0.2027 | 0.1500 | 0.0700 | 0.3175 | 0.2066 | 0.6996 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 17/35 (7 sessions) | 0.2353 | 0.0000 | 0.0000 | 0.0000 | 6/11 (5 sessions) | 0.5000 | 0.0000 | 0.0000 | 0.7500 | -0.2647 | -0.4737 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 17/35 (7 sessions) | 0.2941 | 0.0000 | 0.0000 | 1.0000 | 6/11 (5 sessions) | 0.5000 | 0.0000 | 0.0000 | 0.7500 | -0.2059 | -0.3559 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 23/35 (9 sessions) | 0.9235 | 0.7450 | 0.4622 | 1.2500 | 8/11 (6 sessions) | 0.9088 | 0.6225 | 0.3625 | 1.0525 | 0.0148 | 0.0190 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 24/35 (9 sessions) | 2.3712 | 2.1700 | 1.5100 | 3.0376 | 7/11 (5 sessions) | 2.0921 | 1.3900 | 1.1474 | 1.9850 | 0.2790 | 0.1817 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 17/35 (7 sessions) | 0.9232 | 0.5986 | 0.3612 | 1.0974 | 6/11 (5 sessions) | 0.9048 | 0.5718 | 0.3608 | 0.6653 | 0.0183 | 0.0195 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 17/35 (7 sessions) | 1.9412 | 1.5971 | 1.2984 | 1.8675 | 6/11 (5 sessions) | 1.9069 | 1.7323 | 1.2861 | 1.9906 | 0.0343 | 0.0322 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG | 46 | 14 | 35 | 11 | 100.00% | 100.00% | 76.09% |
| time_bucket | 09:35-10:00 [SMALL] | 13 | 11 | 10 | 3 | 28.57% | 27.27% | 76.92% |
| time_bucket | 10:00-10:30 [SMALL] | 6 | 4 | 4 | 2 | 11.43% | 18.18% | 66.67% |
| time_bucket | 10:30-11:00 [SMALL] | 5 | 4 | 5 | 0 | 14.29% | 0.00% | 100.00% |
| time_bucket | 11:00-12:00 [SMALL] | 9 | 5 | 7 | 2 | 20.00% | 18.18% | 77.78% |
| time_bucket | 12:00-13:30 [SMALL] | 7 | 4 | 5 | 2 | 14.29% | 18.18% | 71.43% |
| time_bucket | 13:30-15:00 [SMALL] | 2 | 2 | 1 | 1 | 2.86% | 9.09% | 50.00% |
| time_bucket | 15:00-close [SMALL] | 4 | 3 | 3 | 1 | 8.57% | 9.09% | 75.00% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 13 | 7 | 10 | 3 | 28.57% | 27.27% | 76.92% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 8 | 5 | 5 | 3 | 14.29% | 27.27% | 62.50% |
| ema9_20_alignment | EMA_UNAVAILABLE [SMALL] | 25 | 14 | 20 | 5 | 57.14% | 45.45% | 80.00% |
| price_vwap_alignment | VWAP_ALIGNED | 44 | 14 | 34 | 10 | 97.14% | 90.91% | 77.27% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 2 | 2 | 1 | 1 | 2.86% | 9.09% | 50.00% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED [SMALL] | 25 | 8 | 20 | 5 | 57.14% | 45.45% | 80.00% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 6 | 4 | 3 | 3 | 8.57% | 27.27% | 50.00% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 15 | 13 | 12 | 3 | 34.29% | 27.27% | 80.00% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 15 | 6 | 12 | 3 | 34.29% | 27.27% | 80.00% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 6 | 5 | 3 | 3 | 8.57% | 27.27% | 50.00% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE [SMALL] | 25 | 14 | 20 | 5 | 57.14% | 45.45% | 80.00% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 7 | 4 | 6 | 1 | 17.14% | 9.09% | 85.71% |
| prior_ema_cross | NO_PRIOR_CROSS | 32 | 14 | 24 | 8 | 68.57% | 72.73% | 75.00% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 7 | 4 | 5 | 2 | 14.29% | 18.18% | 71.43% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE [SMALL] | 30 | 6 | 23 | 7 | 65.71% | 63.64% | 76.67% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 15 | 9 | 11 | 4 | 31.43% | 36.36% | 73.33% |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 1 | 1 | 1 | 0 | 2.86% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 1 | 1 | 1 | 0 | 2.86% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 6 | 3 | 5 | 1 | 14.29% | 9.09% | 83.33% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 8 | 3 | 6 | 2 | 17.14% | 18.18% | 75.00% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 6 | 3 | 4 | 2 | 11.43% | 18.18% | 66.67% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 8 | 3 | 5 | 3 | 14.29% | 27.27% | 62.50% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 17 | 12 | 14 | 3 | 40.00% | 27.27% | 82.35% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 46 | 14 | 35 | 11 | 100.00% | 100.00% | 76.09% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 8 | 7 | 6 | 2 | 17.14% | 18.18% | 75.00% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 5 | 4 | 5 | 0 | 14.29% | 0.00% | 100.00% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 11 | 6 | 7 | 4 | 20.00% | 36.36% | 63.64% |
| stage11_3.structure | UNAVAILABLE [SMALL] | 22 | 13 | 17 | 5 | 48.57% | 45.45% | 77.27% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 5 | 4 | 5 | 0 | 14.29% | 0.00% | 100.00% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 19 | 8 | 13 | 6 | 37.14% | 54.55% | 68.42% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE [SMALL] | 22 | 13 | 17 | 5 | 48.57% | 45.45% | 77.27% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 9 | 6 | 8 | 1 | 22.86% | 9.09% | 88.89% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 15 | 8 | 10 | 5 | 28.57% | 45.45% | 66.67% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 22 | 13 | 17 | 5 | 48.57% | 45.45% | 77.27% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 13 | 6 | 10 | 3 | 28.57% | 27.27% | 76.92% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 12 | 7 | 9 | 3 | 25.71% | 27.27% | 75.00% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 21 | 13 | 16 | 5 | 45.71% | 45.45% | 76.19% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 15 | 13 | 12 | 3 | 34.29% | 27.27% | 80.00% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 6 | 3 | 3 | 3 | 8.57% | 27.27% | 50.00% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 4 | 3 | 3 | 1 | 8.57% | 9.09% | 75.00% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 21 | 6 | 17 | 4 | 48.57% | 36.36% | 80.95% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 46 | 14 | 35 | 11 | 100.00% | 100.00% | 76.09% |


### 2026-03


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 37/37 (15 sessions) | 1.7797 | 1.8300 | 1.6450 | 2.0000 | 15/15 (11 sessions) | 1.5860 | 1.4900 | 1.1900 | 1.9900 | 0.1937 | 0.4409 | not resampled |
| body_size [SMALL] | 37/37 (15 sessions) | 0.9333 | 0.9300 | 0.4300 | 1.2800 | 15/15 (11 sessions) | 0.5728 | 0.5100 | 0.3375 | 0.7744 | 0.3605 | 0.6800 | not resampled |
| directional_body [SMALL] | 37/37 (15 sessions) | 0.9333 | 0.9300 | 0.4300 | 1.2800 | 15/15 (11 sessions) | 0.5728 | 0.5100 | 0.3375 | 0.7744 | 0.3605 | 0.6800 | not resampled |
| candle_range [SMALL] | 37/37 (15 sessions) | 1.3976 | 1.3586 | 0.9500 | 1.6400 | 15/15 (11 sessions) | 1.0960 | 1.1100 | 0.8150 | 1.2600 | 0.3016 | 0.5226 | not resampled |
| body_range_ratio [SMALL] | 37/37 (15 sessions) | 0.6326 | 0.6908 | 0.3929 | 0.8347 | 15/15 (11 sessions) | 0.5244 | 0.5254 | 0.4555 | 0.5818 | 0.1082 | 0.4683 | not resampled |
| directional_body_range_ratio [SMALL] | 37/37 (15 sessions) | 0.6326 | 0.6908 | 0.3929 | 0.8347 | 15/15 (11 sessions) | 0.5244 | 0.5254 | 0.4555 | 0.5818 | 0.1082 | 0.4683 | not resampled |
| close_location [SMALL] | 37/37 (15 sessions) | 0.8007 | 0.8509 | 0.7195 | 0.9489 | 15/15 (11 sessions) | 0.8575 | 0.9231 | 0.8230 | 0.9606 | -0.0568 | -0.3204 | not resampled |
| directional_close_location [SMALL] | 37/37 (15 sessions) | 0.8007 | 0.8509 | 0.7195 | 0.9489 | 15/15 (11 sessions) | 0.8575 | 0.9231 | 0.8230 | 0.9606 | -0.0568 | -0.3204 | not resampled |
| distance_beyond_level [SMALL] | 37/37 (15 sessions) | 0.5532 | 0.3600 | 0.1900 | 0.8800 | 15/15 (11 sessions) | 0.2161 | 0.0900 | 0.0300 | 0.3500 | 0.3371 | 0.7822 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 24/37 (10 sessions) | 0.4259 | 0.2950 | 0.1563 | 0.5415 | 5/15 (5 sessions) | 0.2202 | 0.1113 | 0.0696 | 0.2896 | 0.2057 | 0.5830 | not resampled |
| candle_volume [SMALL] | 37/37 (15 sessions) | 1285736.7568 | 1168548.0000 | 733641.0000 | 1463135.0000 | 15/15 (11 sessions) | 1358199.3333 | 1072031.0000 | 895473.5000 | 1571791.0000 | -72462.5766 | -0.0992 | not resampled |
| relative_volume_prior_6 [SMALL] | 28/37 (11 sessions) | 1.3607 | 1.0113 | 0.8403 | 1.4225 | 8/15 (6 sessions) | 1.1997 | 0.9304 | 0.8712 | 1.3460 | 0.1610 | 0.1663 | not resampled |
| atr14 [SMALL] | 24/37 (10 sessions) | 1.1506 | 1.1190 | 0.9913 | 1.2895 | 5/15 (5 sessions) | 1.2829 | 1.2938 | 1.2525 | 1.4572 | -0.1323 | -0.4700 | not resampled |
| minutes_since_open [SMALL] | 37/37 (15 sessions) | 146.0811 | 100.0000 | 50.0000 | 265.0000 | 15/15 (11 sessions) | 71.6667 | 40.0000 | 10.0000 | 80.0000 | 74.4144 | 0.6802 | not resampled |
| minutes_since_ema_cross [SMALL] | 15/37 (6 sessions) | 38.3333 | 35.0000 | 20.0000 | 57.5000 | 1/15 (1 sessions) | 25.0000 | 25.0000 | 25.0000 | 25.0000 | 13.3333 | N/A | not resampled |
| break_attempt_rank [SMALL] | 37/37 (15 sessions) | 6.7297 | 6.0000 | 3.0000 | 10.0000 | 15/15 (11 sessions) | 4.2667 | 3.0000 | 1.0000 | 5.5000 | 2.4631 | 0.5973 | not resampled |
| valid_hold_sequence_rank [SMALL] | 37/37 (15 sessions) | 3.7027 | 4.0000 | 2.0000 | 5.0000 | 15/15 (11 sessions) | 2.6667 | 2.0000 | 1.0000 | 3.0000 | 1.0360 | 0.5091 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 19/37 (8 sessions) | 0.3799 | 0.2907 | 0.1284 | 0.6044 | 2/15 (2 sessions) | 0.1695 | 0.1695 | 0.1465 | 0.1924 | 0.2104 | 0.6918 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 19/37 (8 sessions) | 0.3240 | 0.2999 | 0.1233 | 0.5136 | 2/15 (2 sessions) | 0.1991 | 0.1991 | 0.1489 | 0.2492 | 0.1249 | 0.5511 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 28/37 (11 sessions) | 0.1374 | 0.1084 | -0.0081 | 0.2883 | 6/15 (5 sessions) | 0.1319 | 0.1204 | -0.0446 | 0.2667 | 0.0055 | 0.0275 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 27/37 (10 sessions) | 0.0339 | 0.0138 | -0.0658 | 0.1187 | 6/15 (5 sessions) | 0.0697 | 0.0576 | -0.0863 | 0.1806 | -0.0358 | -0.1855 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 27/37 (10 sessions) | 0.0006 | -0.0172 | -0.1021 | 0.0565 | 6/15 (5 sessions) | 0.0724 | 0.0446 | -0.0692 | 0.1895 | -0.0718 | -0.3525 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 18/37 (7 sessions) | 0.0245 | 0.0228 | -0.0441 | 0.0646 | 2/15 (2 sessions) | -0.0198 | -0.0198 | -0.0249 | -0.0147 | 0.0442 | 0.4272 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 18/37 (7 sessions) | -0.0096 | -0.0036 | -0.0631 | 0.0193 | 2/15 (2 sessions) | -0.0365 | -0.0365 | -0.0423 | -0.0307 | 0.0269 | 0.2728 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 18/37 (7 sessions) | -0.0254 | -0.0107 | -0.0881 | 0.0006 | 2/15 (2 sessions) | -0.0296 | -0.0296 | -0.0410 | -0.0182 | 0.0042 | 0.0414 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 37/37 (15 sessions) | 0.0721 | 0.0173 | -0.0064 | 0.1482 | 15/15 (11 sessions) | 0.0794 | 0.0720 | 0.0237 | 0.1348 | -0.0072 | -0.0689 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 35/37 (14 sessions) | 0.0482 | 0.0061 | -0.0076 | 0.1077 | 10/15 (7 sessions) | 0.0331 | 0.0285 | 0.0099 | 0.0617 | 0.0151 | 0.1646 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 32/37 (13 sessions) | 0.0289 | -0.0001 | -0.0095 | 0.0622 | 10/15 (7 sessions) | 0.0396 | 0.0589 | 0.0165 | 0.0671 | -0.0106 | -0.1467 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 18/37 (7 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.7500 | 2/15 (2 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5774 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 15/37 (6 sessions) | 0.8000 | 1.0000 | 0.0000 | 1.0000 | 2/15 (2 sessions) | 0.5000 | 0.5000 | 0.2500 | 0.7500 | 0.3000 | 0.3519 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 14/37 (6 sessions) | 1.5714 | 1.0000 | 1.0000 | 2.0000 | 1/15 (1 sessions) | 2.0000 | 2.0000 | 2.0000 | 2.0000 | -0.4286 | N/A | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 24/37 (10 sessions) | 0.2917 | 0.0000 | 0.0000 | 1.0000 | 5/15 (5 sessions) | 0.6000 | 1.0000 | 0.0000 | 1.0000 | -0.3083 | -0.6456 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 19/37 (8 sessions) | 0.5263 | 0.0000 | 0.0000 | 1.0000 | 2/15 (2 sessions) | 0.5000 | 0.5000 | 0.2500 | 0.7500 | 0.0263 | 0.0426 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 15/37 (6 sessions) | 0.8667 | 1.0000 | 0.0000 | 1.5000 | 2/15 (2 sessions) | 1.0000 | 1.0000 | 0.5000 | 1.5000 | -0.1333 | -0.1302 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 18/37 (7 sessions) | 0.2222 | 0.0000 | 0.0000 | 0.0000 | 2/15 (2 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.2222 | 0.5345 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 15/37 (6 sessions) | 0.2000 | 0.0000 | 0.0000 | 0.0000 | 2/15 (2 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.2000 | 0.5000 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 14/37 (6 sessions) | 0.5714 | 0.0000 | 0.0000 | 1.0000 | 1/15 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | -0.4286 | N/A | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 29/37 (12 sessions) | 0.7241 | 1.0000 | 0.0000 | 1.0000 | 9/15 (7 sessions) | 1.1111 | 1.0000 | 0.0000 | 1.0000 | -0.3870 | -0.3834 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 27/37 (10 sessions) | 1.4074 | 1.0000 | 1.0000 | 2.0000 | 6/15 (5 sessions) | 1.5000 | 1.0000 | 1.0000 | 1.0000 | -0.0926 | -0.0701 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 18/37 (7 sessions) | 2.3333 | 2.0000 | 1.0000 | 3.0000 | 2/15 (2 sessions) | 0.5000 | 0.5000 | 0.2500 | 0.7500 | 1.8333 | 1.1406 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 29/37 (12 sessions) | 2.8155 | 2.5600 | 1.7700 | 3.5690 | 9/15 (7 sessions) | 2.7290 | 2.0700 | 1.9800 | 3.6800 | 0.0866 | 0.0782 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 27/37 (10 sessions) | 3.7826 | 3.5500 | 2.6200 | 4.6600 | 6/15 (5 sessions) | 3.9493 | 3.7928 | 3.6639 | 3.9925 | -0.1667 | -0.1290 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 18/37 (7 sessions) | 4.3969 | 4.0250 | 3.4525 | 5.6400 | 2/15 (2 sessions) | 3.6000 | 3.6000 | 3.5750 | 3.6250 | 0.7969 | 0.6245 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 24/37 (10 sessions) | 2.2704 | 2.0635 | 1.8265 | 2.5947 | 5/15 (5 sessions) | 2.0408 | 1.5808 | 1.4205 | 2.6829 | 0.2297 | 0.3021 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 24/37 (10 sessions) | 3.1687 | 3.0636 | 2.6300 | 3.5442 | 5/15 (5 sessions) | 3.2771 | 3.1149 | 2.6627 | 3.4157 | -0.1084 | -0.1375 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 18/37 (7 sessions) | 4.0853 | 4.0117 | 3.6972 | 4.3981 | 2/15 (2 sessions) | 3.9554 | 3.9554 | 3.3948 | 4.5159 | 0.1299 | 0.1695 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 29/37 (12 sessions) | 0.3577 | 0.2711 | 0.1911 | 0.5094 | 9/15 (7 sessions) | 0.3748 | 0.3187 | 0.0719 | 0.5718 | -0.0171 | -0.0585 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 27/37 (10 sessions) | 0.2581 | 0.2363 | 0.1350 | 0.3556 | 6/15 (5 sessions) | 0.2856 | 0.2982 | 0.1871 | 0.3332 | -0.0275 | -0.1661 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 18/37 (7 sessions) | 0.1365 | 0.1124 | 0.0509 | 0.2138 | 2/15 (2 sessions) | 0.0643 | 0.0643 | 0.0463 | 0.0823 | 0.0722 | 0.6922 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 29/37 (12 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9/15 (7 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 27/37 (10 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 6/15 (5 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 18/37 (7 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 2/15 (2 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 29/37 (12 sessions) | 0.4655 | 0.5000 | 0.2500 | 0.5000 | 9/15 (7 sessions) | 0.5000 | 0.5000 | 0.2500 | 0.7500 | -0.0345 | -0.1177 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 27/37 (10 sessions) | 0.4778 | 0.5000 | 0.4000 | 0.5500 | 6/15 (5 sessions) | 0.5167 | 0.5000 | 0.4000 | 0.6750 | -0.0389 | -0.2289 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 18/37 (7 sessions) | 0.5177 | 0.5455 | 0.4545 | 0.5455 | 2/15 (2 sessions) | 0.5227 | 0.5227 | 0.4886 | 0.5568 | -0.0051 | -0.0662 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 24/37 (10 sessions) | 0.7795 | 0.6092 | 0.3871 | 1.0554 | 5/15 (5 sessions) | 0.9668 | 0.6907 | 0.6506 | 1.2045 | -0.1872 | -0.3242 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 24/37 (10 sessions) | 0.5658 | 0.4639 | 0.3368 | 0.7786 | 5/15 (5 sessions) | 0.5133 | 0.4645 | 0.2965 | 0.7523 | 0.0525 | 0.1600 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 19/37 (8 sessions) | 0.4555 | 0.4425 | 0.2604 | 0.6091 | 2/15 (2 sessions) | 0.3833 | 0.3833 | 0.1931 | 0.5735 | 0.0722 | 0.2400 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 34/37 (13 sessions) | 2.1698 | 1.3850 | 0.9050 | 3.1925 | 14/15 (10 sessions) | 0.9909 | 0.6000 | 0.3082 | 1.8350 | 1.1788 | 0.7021 | not resampled |
| stage11_2.room_in_atr [SMALL] | 24/37 (10 sessions) | 1.9804 | 0.9711 | 0.7835 | 3.1133 | 5/15 (5 sessions) | 0.6368 | 0.1418 | 0.1345 | 1.2136 | 1.3436 | 0.7625 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 37/37 (15 sessions) | 2.2162 | 2.0000 | 2.0000 | 3.0000 | 15/15 (11 sessions) | 2.5333 | 3.0000 | 2.0000 | 3.0000 | -0.3171 | -0.3460 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 37/37 (15 sessions) | 3.7838 | 4.0000 | 3.0000 | 4.0000 | 15/15 (11 sessions) | 3.4667 | 3.0000 | 3.0000 | 4.0000 | 0.3171 | 0.3460 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 34/37 (13 sessions) | 2.1698 | 1.3850 | 0.9050 | 3.1925 | 14/15 (10 sessions) | 0.9909 | 0.6000 | 0.3082 | 1.8350 | 1.1788 | 0.7021 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 37/37 (15 sessions) | 0.4746 | 0.3400 | 0.1550 | 0.7300 | 15/15 (11 sessions) | 0.2161 | 0.0900 | 0.0300 | 0.3500 | 0.2584 | 0.6961 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 24/37 (10 sessions) | 0.2500 | 0.0000 | 0.0000 | 0.0000 | 5/15 (5 sessions) | 0.6000 | 1.0000 | 0.0000 | 1.0000 | -0.3500 | -0.6554 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 24/37 (10 sessions) | 0.5417 | 0.5000 | 0.0000 | 1.0000 | 5/15 (5 sessions) | 0.8000 | 1.0000 | 0.0000 | 1.0000 | -0.2583 | -0.4093 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 26/37 (10 sessions) | 1.3585 | 1.0500 | 0.6911 | 1.9012 | 8/15 (7 sessions) | 1.4206 | 1.1606 | 0.3889 | 2.5050 | -0.0621 | -0.0636 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 27/37 (12 sessions) | 2.2210 | 1.7450 | 1.2325 | 2.7100 | 8/15 (6 sessions) | 2.6385 | 2.7994 | 1.0388 | 3.6135 | -0.4174 | -0.2736 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 24/37 (10 sessions) | 1.1638 | 0.8640 | 0.5993 | 1.6274 | 5/15 (5 sessions) | 1.7581 | 1.4537 | 0.8623 | 2.0405 | -0.5943 | -0.6251 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 23/37 (10 sessions) | 1.6223 | 1.5467 | 1.1174 | 2.0097 | 5/15 (5 sessions) | 1.6465 | 0.8927 | 0.7510 | 2.6517 | -0.0242 | -0.0272 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG | 52 | 18 | 37 | 15 | 100.00% | 100.00% | 71.15% |
| time_bucket | 09:35-10:00 [SMALL] | 14 | 11 | 8 | 6 | 21.62% | 40.00% | 57.14% |
| time_bucket | 10:00-10:30 [SMALL] | 5 | 4 | 2 | 3 | 5.41% | 20.00% | 40.00% |
| time_bucket | 10:30-11:00 [SMALL] | 8 | 6 | 5 | 3 | 13.51% | 20.00% | 62.50% |
| time_bucket | 11:00-12:00 [SMALL] | 7 | 5 | 6 | 1 | 16.22% | 6.67% | 85.71% |
| time_bucket | 12:00-13:30 [SMALL] | 7 | 4 | 6 | 1 | 16.22% | 6.67% | 85.71% |
| time_bucket | 13:30-15:00 [SMALL] | 8 | 6 | 8 | 0 | 21.62% | 0.00% | 100.00% |
| time_bucket | 15:00-close [SMALL] | 3 | 3 | 2 | 1 | 5.41% | 6.67% | 66.67% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 7 | 4 | 6 | 1 | 16.22% | 6.67% | 85.71% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 14 | 6 | 13 | 1 | 35.14% | 6.67% | 92.86% |
| ema9_20_alignment | EMA_UNAVAILABLE | 31 | 17 | 18 | 13 | 48.65% | 86.67% | 58.06% |
| price_vwap_alignment | VWAP_ALIGNED | 39 | 18 | 26 | 13 | 70.27% | 86.67% | 66.67% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 13 | 6 | 11 | 2 | 29.73% | 13.33% | 84.62% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED [SMALL] | 19 | 8 | 14 | 5 | 37.84% | 33.33% | 73.68% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 16 | 7 | 14 | 2 | 37.84% | 13.33% | 87.50% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 17 | 13 | 9 | 8 | 24.32% | 53.33% | 52.94% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 12 | 6 | 10 | 2 | 27.03% | 13.33% | 83.33% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 9 | 4 | 9 | 0 | 24.32% | 0.00% | 100.00% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 31 | 17 | 18 | 13 | 48.65% | 86.67% | 58.06% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 3 | 3 | 3 | 0 | 8.11% | 0.00% | 100.00% |
| prior_ema_cross | NO_PRIOR_CROSS | 36 | 18 | 22 | 14 | 59.46% | 93.33% | 61.11% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 13 | 5 | 12 | 1 | 32.43% | 6.67% | 92.31% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 30 | 10 | 23 | 7 | 62.16% | 46.67% | 76.67% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 20 | 9 | 12 | 8 | 32.43% | 53.33% | 60.00% |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 2 | 2 | 2 | 0 | 5.41% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 7 | 5 | 7 | 0 | 18.92% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 3 | 1 | 2 | 1 | 5.41% | 6.67% | 66.67% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 3 | 2 | 2 | 1 | 5.41% | 6.67% | 66.67% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 1 | 1 | 1 | 0 | 2.70% | 0.00% | 100.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 7 | 3 | 7 | 0 | 18.92% | 0.00% | 100.00% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 8 | 6 | 5 | 3 | 13.51% | 20.00% | 62.50% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 4 | 3 | 3 | 1 | 8.11% | 6.67% | 75.00% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 19 | 14 | 10 | 9 | 27.03% | 60.00% | 52.63% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 52 | 18 | 37 | 15 | 100.00% | 100.00% | 71.15% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 9 | 6 | 8 | 1 | 21.62% | 6.67% | 88.89% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 7 | 6 | 6 | 1 | 16.22% | 6.67% | 85.71% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 8 | 5 | 6 | 2 | 16.22% | 13.33% | 75.00% |
| stage11_3.structure | UNAVAILABLE [SMALL] | 28 | 16 | 17 | 11 | 45.95% | 73.33% | 60.71% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 7 | 6 | 6 | 1 | 16.22% | 6.67% | 85.71% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 17 | 7 | 14 | 3 | 37.84% | 20.00% | 82.35% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE [SMALL] | 28 | 16 | 17 | 11 | 45.95% | 73.33% | 60.71% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 11 | 6 | 9 | 2 | 24.32% | 13.33% | 81.82% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 14 | 7 | 12 | 2 | 32.43% | 13.33% | 85.71% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 27 | 16 | 16 | 11 | 43.24% | 73.33% | 59.26% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 13 | 7 | 11 | 2 | 29.73% | 13.33% | 84.62% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 14 | 7 | 12 | 2 | 32.43% | 13.33% | 85.71% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 25 | 14 | 14 | 11 | 37.84% | 73.33% | 56.00% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 18 | 15 | 11 | 7 | 29.73% | 46.67% | 61.11% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 14 | 7 | 11 | 3 | 29.73% | 20.00% | 78.57% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 20 | 9 | 15 | 5 | 40.54% | 33.33% | 75.00% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 52 | 18 | 37 | 15 | 100.00% | 100.00% | 71.15% |


### 2026-04


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 39/39 (19 sessions) | 1.2053 | 1.1800 | 0.8200 | 1.6200 | 15/15 (12 sessions) | 1.1788 | 1.2650 | 0.9130 | 1.3450 | 0.0265 | 0.0680 | not resampled |
| body_size [SMALL] | 39/39 (19 sessions) | 0.5554 | 0.4750 | 0.3375 | 0.6750 | 15/15 (12 sessions) | 0.4063 | 0.3800 | 0.2125 | 0.6050 | 0.1491 | 0.4647 | not resampled |
| directional_body [SMALL] | 39/39 (19 sessions) | 0.5554 | 0.4750 | 0.3375 | 0.6750 | 15/15 (12 sessions) | 0.4063 | 0.3800 | 0.2125 | 0.6050 | 0.1491 | 0.4647 | not resampled |
| candle_range [SMALL] | 39/39 (19 sessions) | 0.9315 | 0.8000 | 0.6350 | 0.9550 | 15/15 (12 sessions) | 0.7434 | 0.6300 | 0.5300 | 0.9050 | 0.1881 | 0.3498 | not resampled |
| body_range_ratio [SMALL] | 39/39 (19 sessions) | 0.6274 | 0.6579 | 0.4781 | 0.7853 | 15/15 (12 sessions) | 0.5504 | 0.5976 | 0.5003 | 0.6735 | 0.0770 | 0.3954 | not resampled |
| directional_body_range_ratio [SMALL] | 39/39 (19 sessions) | 0.6274 | 0.6579 | 0.4781 | 0.7853 | 15/15 (12 sessions) | 0.5504 | 0.5976 | 0.5003 | 0.6735 | 0.0770 | 0.3954 | not resampled |
| close_location [SMALL] | 39/39 (19 sessions) | 0.7933 | 0.8555 | 0.7060 | 0.9176 | 15/15 (12 sessions) | 0.8003 | 0.8491 | 0.6974 | 0.9178 | -0.0070 | -0.0442 | not resampled |
| directional_close_location [SMALL] | 39/39 (19 sessions) | 0.7933 | 0.8555 | 0.7060 | 0.9176 | 15/15 (12 sessions) | 0.8003 | 0.8491 | 0.6974 | 0.9178 | -0.0070 | -0.0442 | not resampled |
| distance_beyond_level [SMALL] | 39/39 (19 sessions) | 0.2775 | 0.2300 | 0.0950 | 0.3950 | 15/15 (12 sessions) | 0.1729 | 0.1200 | 0.0600 | 0.2400 | 0.1046 | 0.4670 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 23/39 (10 sessions) | 0.3369 | 0.2638 | 0.1215 | 0.5440 | 8/15 (7 sessions) | 0.1965 | 0.1348 | 0.0667 | 0.2599 | 0.1404 | 0.5961 | not resampled |
| candle_volume [SMALL] | 39/39 (19 sessions) | 640791.6667 | 491748.0000 | 355119.5000 | 775777.5000 | 15/15 (12 sessions) | 729727.8667 | 405696.0000 | 301556.0000 | 757980.5000 | -88936.2000 | -0.1447 | not resampled |
| relative_volume_prior_6 [SMALL] | 27/39 (12 sessions) | 1.1605 | 0.9574 | 0.7604 | 1.3793 | 12/15 (10 sessions) | 1.0642 | 0.7185 | 0.6413 | 0.9097 | 0.0963 | 0.1254 | not resampled |
| atr14 [SMALL] | 23/39 (10 sessions) | 0.7446 | 0.7038 | 0.6083 | 0.7860 | 8/15 (7 sessions) | 0.7278 | 0.6283 | 0.5784 | 0.7360 | 0.0168 | 0.0590 | not resampled |
| minutes_since_open [SMALL] | 39/39 (19 sessions) | 128.9744 | 105.0000 | 27.5000 | 202.5000 | 15/15 (12 sessions) | 104.3333 | 75.0000 | 40.0000 | 152.5000 | 24.6410 | 0.2247 | not resampled |
| minutes_since_ema_cross [SMALL] | 12/39 (7 sessions) | 39.1667 | 35.0000 | 20.0000 | 53.7500 | 4/15 (3 sessions) | 32.5000 | 30.0000 | 22.5000 | 40.0000 | 6.6667 | 0.3067 | not resampled |
| break_attempt_rank [SMALL] | 39/39 (19 sessions) | 7.5128 | 6.0000 | 3.5000 | 9.5000 | 15/15 (12 sessions) | 5.8667 | 5.0000 | 3.0000 | 8.0000 | 1.6462 | 0.3416 | not resampled |
| valid_hold_sequence_rank [SMALL] | 39/39 (19 sessions) | 3.4359 | 3.0000 | 2.0000 | 5.0000 | 15/15 (12 sessions) | 3.0667 | 3.0000 | 2.0000 | 3.5000 | 0.3692 | 0.1769 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 20/39 (9 sessions) | 0.2420 | 0.2023 | 0.1023 | 0.3589 | 5/15 (4 sessions) | 0.2076 | 0.2266 | 0.1284 | 0.2336 | 0.0344 | 0.2122 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 20/39 (9 sessions) | 0.3720 | 0.3732 | 0.1499 | 0.5508 | 5/15 (4 sessions) | 0.3766 | 0.3952 | 0.2216 | 0.5145 | -0.0046 | -0.0201 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 24/39 (10 sessions) | 0.1190 | 0.1168 | 0.0523 | 0.1700 | 10/15 (9 sessions) | 0.0733 | 0.0680 | 0.0133 | 0.1259 | 0.0458 | 0.5224 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 24/39 (10 sessions) | 0.0737 | 0.0753 | 0.0178 | 0.1259 | 10/15 (9 sessions) | 0.0412 | 0.0433 | -0.0247 | 0.1117 | 0.0325 | 0.3573 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 23/39 (10 sessions) | 0.0556 | 0.0630 | 0.0004 | 0.0937 | 9/15 (8 sessions) | 0.0459 | 0.0717 | -0.0250 | 0.0915 | 0.0097 | 0.1203 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 20/39 (9 sessions) | 0.0676 | 0.0522 | 0.0183 | 0.1070 | 5/15 (4 sessions) | 0.0421 | 0.0494 | -0.0084 | 0.0783 | 0.0255 | 0.4670 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 18/39 (8 sessions) | 0.0401 | 0.0334 | -0.0020 | 0.0752 | 5/15 (4 sessions) | 0.0262 | 0.0467 | -0.0268 | 0.0619 | 0.0138 | 0.2688 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 18/39 (8 sessions) | 0.0328 | 0.0293 | 0.0039 | 0.0723 | 5/15 (4 sessions) | 0.0237 | 0.0530 | -0.0264 | 0.0591 | 0.0091 | 0.1999 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 39/39 (19 sessions) | 0.0651 | 0.0257 | 0.0075 | 0.0844 | 15/15 (12 sessions) | 0.0595 | 0.0183 | 0.0128 | 0.0642 | 0.0055 | 0.0648 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 37/39 (18 sessions) | 0.0351 | 0.0188 | 0.0035 | 0.0458 | 12/15 (10 sessions) | 0.0158 | 0.0183 | 0.0029 | 0.0246 | 0.0193 | 0.4173 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 35/39 (17 sessions) | 0.0207 | 0.0152 | 0.0035 | 0.0335 | 12/15 (10 sessions) | 0.0187 | 0.0155 | 0.0032 | 0.0357 | 0.0019 | 0.0742 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 18/39 (8 sessions) | 0.2222 | 0.0000 | 0.0000 | 0.0000 | 4/15 (3 sessions) | 0.2500 | 0.0000 | 0.0000 | 0.2500 | -0.0278 | -0.0632 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 14/39 (8 sessions) | 0.5714 | 1.0000 | 0.0000 | 1.0000 | 4/15 (3 sessions) | 0.7500 | 1.0000 | 0.7500 | 1.0000 | -0.1786 | -0.3494 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 10/39 (8 sessions) | 1.2000 | 1.0000 | 1.0000 | 1.0000 | 1/15 (1 sessions) | 2.0000 | 2.0000 | 2.0000 | 2.0000 | -0.8000 | N/A | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 23/39 (10 sessions) | 0.2609 | 0.0000 | 0.0000 | 0.5000 | 8/15 (7 sessions) | 0.3750 | 0.0000 | 0.0000 | 1.0000 | -0.1141 | -0.2447 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 20/39 (9 sessions) | 0.7000 | 1.0000 | 0.0000 | 1.0000 | 5/15 (4 sessions) | 0.8000 | 1.0000 | 1.0000 | 1.0000 | -0.1000 | -0.1599 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 14/39 (8 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 4/15 (3 sessions) | 1.2500 | 1.0000 | 1.0000 | 1.2500 | -0.2500 | -0.3849 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 18/39 (8 sessions) | 0.1667 | 0.0000 | 0.0000 | 0.0000 | 4/15 (3 sessions) | 0.7500 | 1.0000 | 0.7500 | 1.0000 | -0.5833 | -1.4471 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 14/39 (8 sessions) | 0.5714 | 0.5000 | 0.0000 | 1.0000 | 4/15 (3 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | -0.4286 | -0.7358 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 10/39 (8 sessions) | 0.9000 | 1.0000 | 0.2500 | 1.0000 | 1/15 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | -0.1000 | N/A | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 29/39 (12 sessions) | 0.9655 | 0.0000 | 0.0000 | 2.0000 | 12/15 (10 sessions) | 0.9167 | 1.0000 | 0.0000 | 2.0000 | 0.0489 | 0.0432 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 23/39 (10 sessions) | 1.5652 | 1.0000 | 0.0000 | 3.0000 | 9/15 (8 sessions) | 2.2222 | 2.0000 | 1.0000 | 3.0000 | -0.6570 | -0.4526 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 18/39 (8 sessions) | 3.1111 | 2.0000 | 1.0000 | 4.7500 | 4/15 (3 sessions) | 4.0000 | 4.0000 | 1.0000 | 7.0000 | -0.8889 | -0.3292 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 29/39 (12 sessions) | 1.7328 | 1.5900 | 1.2600 | 2.1550 | 12/15 (10 sessions) | 1.4732 | 1.4650 | 1.1750 | 1.7775 | 0.2595 | 0.3653 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 23/39 (10 sessions) | 2.2399 | 1.9630 | 1.4300 | 2.7940 | 9/15 (8 sessions) | 1.9650 | 1.6200 | 1.2900 | 2.4800 | 0.2749 | 0.2632 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 18/39 (8 sessions) | 3.1754 | 2.9400 | 2.2025 | 3.8300 | 4/15 (3 sessions) | 2.1962 | 1.9175 | 1.7900 | 2.3238 | 0.9791 | 0.8805 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 23/39 (10 sessions) | 2.2843 | 2.3039 | 1.7817 | 2.5970 | 8/15 (7 sessions) | 2.0368 | 2.1631 | 1.6499 | 2.3105 | 0.2475 | 0.3783 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 23/39 (10 sessions) | 2.9869 | 2.8187 | 2.3416 | 3.4088 | 8/15 (7 sessions) | 2.6282 | 2.6344 | 2.3340 | 2.8156 | 0.3587 | 0.4459 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 18/39 (8 sessions) | 4.7684 | 4.9342 | 3.7997 | 5.5047 | 4/15 (3 sessions) | 4.0077 | 3.9544 | 3.1081 | 4.8540 | 0.7606 | 0.6347 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 29/39 (12 sessions) | 0.4739 | 0.4642 | 0.2705 | 0.6552 | 12/15 (10 sessions) | 0.3449 | 0.2862 | 0.1581 | 0.5420 | 0.1290 | 0.4931 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 23/39 (10 sessions) | 0.3189 | 0.3262 | 0.1100 | 0.4877 | 9/15 (8 sessions) | 0.2441 | 0.1713 | 0.1108 | 0.3241 | 0.0748 | 0.3653 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 18/39 (8 sessions) | 0.1664 | 0.0918 | 0.0443 | 0.2869 | 4/15 (3 sessions) | 0.1306 | 0.1249 | 0.0767 | 0.1789 | 0.0357 | 0.2325 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 29/39 (12 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 12/15 (10 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 23/39 (10 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9/15 (8 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 18/39 (8 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 4/15 (3 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 29/39 (12 sessions) | 0.5517 | 0.5000 | 0.5000 | 0.7500 | 12/15 (10 sessions) | 0.6042 | 0.6250 | 0.5000 | 0.7500 | -0.0524 | -0.2585 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 23/39 (10 sessions) | 0.5130 | 0.5000 | 0.4000 | 0.6000 | 9/15 (8 sessions) | 0.5111 | 0.5000 | 0.4000 | 0.6000 | 0.0019 | 0.0125 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 18/39 (8 sessions) | 0.5000 | 0.5455 | 0.4545 | 0.5795 | 4/15 (3 sessions) | 0.5795 | 0.5909 | 0.5341 | 0.6364 | -0.0795 | -0.7370 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 23/39 (10 sessions) | 1.3250 | 1.3954 | 0.4539 | 1.9105 | 8/15 (7 sessions) | 0.9579 | 0.9660 | 0.3727 | 1.5562 | 0.3671 | 0.4221 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 23/39 (10 sessions) | 0.7985 | 0.6170 | 0.2404 | 1.2404 | 8/15 (7 sessions) | 0.4600 | 0.3684 | 0.2329 | 0.7072 | 0.3385 | 0.5263 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 20/39 (9 sessions) | 0.5513 | 0.3780 | 0.1729 | 0.6955 | 5/15 (4 sessions) | 0.2183 | 0.2772 | 0.1176 | 0.2839 | 0.3330 | 0.6449 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 37/39 (17 sessions) | 1.0628 | 0.7301 | 0.3600 | 1.5423 | 14/15 (11 sessions) | 1.1171 | 0.8574 | 0.2788 | 1.6975 | -0.0544 | -0.0608 | not resampled |
| stage11_2.room_in_atr [SMALL] | 23/39 (10 sessions) | 1.0562 | 0.7376 | 0.5194 | 1.3713 | 8/15 (7 sessions) | 1.0892 | 0.7532 | 0.5620 | 1.4796 | -0.0329 | -0.0437 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 39/39 (19 sessions) | 1.4615 | 1.0000 | 1.0000 | 2.0000 | 15/15 (12 sessions) | 1.5333 | 2.0000 | 1.0000 | 2.0000 | -0.0718 | -0.1070 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 39/39 (19 sessions) | 4.5128 | 4.0000 | 4.0000 | 5.0000 | 15/15 (12 sessions) | 4.4667 | 4.0000 | 4.0000 | 5.0000 | 0.0462 | 0.0687 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 37/39 (17 sessions) | 1.0628 | 0.7301 | 0.3600 | 1.5423 | 14/15 (11 sessions) | 1.1171 | 0.8574 | 0.2788 | 1.6975 | -0.0544 | -0.0608 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 39/39 (19 sessions) | 0.2407 | 0.1700 | 0.0825 | 0.3175 | 15/15 (12 sessions) | 0.1715 | 0.1200 | 0.0525 | 0.2400 | 0.0691 | 0.3300 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 23/39 (10 sessions) | 0.2174 | 0.0000 | 0.0000 | 0.0000 | 8/15 (7 sessions) | 0.2500 | 0.0000 | 0.0000 | 0.2500 | -0.0326 | -0.0755 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 23/39 (10 sessions) | 0.6522 | 1.0000 | 0.0000 | 1.0000 | 8/15 (7 sessions) | 0.7500 | 1.0000 | 0.0000 | 1.0000 | -0.0978 | -0.1477 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 29/39 (12 sessions) | 0.5490 | 0.4149 | 0.2000 | 0.7700 | 12/15 (10 sessions) | 0.5471 | 0.5250 | 0.4100 | 0.7150 | 0.0019 | 0.0042 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 27/39 (13 sessions) | 1.6366 | 1.5400 | 0.9600 | 1.9525 | 11/15 (9 sessions) | 1.2277 | 1.3100 | 0.9900 | 1.5950 | 0.4088 | 0.4681 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 23/39 (10 sessions) | 0.6814 | 0.4743 | 0.1834 | 1.0082 | 8/15 (7 sessions) | 0.6682 | 0.6722 | 0.4506 | 0.9619 | 0.0132 | 0.0223 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 23/39 (10 sessions) | 2.2262 | 1.7294 | 1.3434 | 3.0984 | 8/15 (7 sessions) | 1.9974 | 2.0672 | 1.0888 | 2.2406 | 0.2288 | 0.1684 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG | 54 | 20 | 39 | 15 | 100.00% | 100.00% | 72.22% |
| time_bucket | 09:35-10:00 [SMALL] | 13 | 13 | 10 | 3 | 25.64% | 20.00% | 76.92% |
| time_bucket | 10:00-10:30 [SMALL] | 9 | 8 | 6 | 3 | 15.38% | 20.00% | 66.67% |
| time_bucket | 10:30-11:00 [SMALL] | 4 | 4 | 1 | 3 | 2.56% | 20.00% | 25.00% |
| time_bucket | 11:00-12:00 [SMALL] | 10 | 6 | 8 | 2 | 20.51% | 13.33% | 80.00% |
| time_bucket | 12:00-13:30 [SMALL] | 11 | 5 | 8 | 3 | 20.51% | 20.00% | 72.73% |
| time_bucket | 13:30-15:00 [SMALL] | 2 | 2 | 2 | 0 | 5.13% | 0.00% | 100.00% |
| time_bucket | 15:00-close [SMALL] | 5 | 4 | 4 | 1 | 10.26% | 6.67% | 80.00% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 18 | 9 | 15 | 3 | 38.46% | 20.00% | 83.33% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 7 | 4 | 5 | 2 | 12.82% | 13.33% | 71.43% |
| ema9_20_alignment | EMA_UNAVAILABLE [SMALL] | 29 | 16 | 19 | 10 | 48.72% | 66.67% | 65.52% |
| price_vwap_alignment | VWAP_ALIGNED | 51 | 20 | 38 | 13 | 97.44% | 86.67% | 74.51% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 3 | 2 | 1 | 2 | 2.56% | 13.33% | 33.33% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED | 30 | 14 | 22 | 8 | 56.41% | 53.33% | 73.33% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 6 | 3 | 4 | 2 | 10.26% | 13.33% | 66.67% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 18 | 14 | 13 | 5 | 33.33% | 33.33% | 72.22% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 18 | 9 | 15 | 3 | 38.46% | 20.00% | 83.33% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 7 | 4 | 5 | 2 | 12.82% | 13.33% | 71.43% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE [SMALL] | 29 | 16 | 19 | 10 | 48.72% | 66.67% | 65.52% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 9 | 5 | 7 | 2 | 17.95% | 13.33% | 77.78% |
| prior_ema_cross | NO_PRIOR_CROSS | 38 | 19 | 27 | 11 | 69.23% | 73.33% | 71.05% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 7 | 4 | 5 | 2 | 12.82% | 13.33% | 71.43% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 45 | 18 | 34 | 11 | 87.18% | 73.33% | 75.56% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 9 | 7 | 5 | 4 | 12.82% | 26.67% | 55.56% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 11 | 6 | 8 | 3 | 20.51% | 20.00% | 72.73% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 6 | 4 | 5 | 1 | 12.82% | 6.67% | 83.33% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 2 | 2 | 1 | 1 | 2.56% | 6.67% | 50.00% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 5 | 4 | 4 | 1 | 10.26% | 6.67% | 80.00% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 7 | 4 | 5 | 2 | 12.82% | 13.33% | 71.43% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 3 | 2 | 2 | 1 | 5.13% | 6.67% | 66.67% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 20 | 13 | 14 | 6 | 35.90% | 40.00% | 70.00% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 54 | 20 | 39 | 15 | 100.00% | 100.00% | 72.22% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 4 | 3 | 2 | 2 | 5.13% | 13.33% | 50.00% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 7 | 3 | 6 | 1 | 15.38% | 6.67% | 85.71% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 16 | 9 | 13 | 3 | 33.33% | 20.00% | 81.25% |
| stage11_3.structure | UNAVAILABLE [SMALL] | 27 | 17 | 18 | 9 | 46.15% | 60.00% | 66.67% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 7 | 3 | 6 | 1 | 15.38% | 6.67% | 85.71% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 20 | 9 | 15 | 5 | 38.46% | 33.33% | 75.00% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE [SMALL] | 27 | 17 | 18 | 9 | 46.15% | 60.00% | 66.67% |
| stage11_3.high_structure | EQUAL_HIGH [SMALL] | 1 | 1 | 1 | 0 | 2.56% | 0.00% | 100.00% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 15 | 7 | 13 | 2 | 33.33% | 13.33% | 86.67% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 12 | 6 | 7 | 5 | 17.95% | 33.33% | 58.33% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 26 | 17 | 18 | 8 | 46.15% | 53.33% | 69.23% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 17 | 11 | 12 | 5 | 30.77% | 33.33% | 70.59% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 13 | 8 | 10 | 3 | 25.64% | 20.00% | 76.92% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 24 | 15 | 17 | 7 | 43.59% | 46.67% | 70.83% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 13 | 13 | 10 | 3 | 25.64% | 20.00% | 76.92% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 1 | 1 | 1 | 0 | 2.56% | 0.00% | 100.00% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 11 | 5 | 7 | 4 | 17.95% | 26.67% | 63.64% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 29 | 13 | 21 | 8 | 53.85% | 53.33% | 72.41% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 54 | 20 | 39 | 15 | 100.00% | 100.00% | 72.22% |


### 2026-05


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 40/40 (19 sessions) | 1.2040 | 1.0800 | 0.9076 | 1.5150 | 20/20 (9 sessions) | 1.6365 | 1.6650 | 1.2125 | 1.7100 | -0.4325 | -0.9441 | not resampled |
| body_size [SMALL] | 40/40 (19 sessions) | 0.6871 | 0.5825 | 0.3500 | 0.8200 | 20/20 (9 sessions) | 0.4002 | 0.3350 | 0.1838 | 0.4900 | 0.2869 | 0.6657 | not resampled |
| directional_body [SMALL] | 40/40 (19 sessions) | 0.6871 | 0.5825 | 0.3500 | 0.8200 | 20/20 (9 sessions) | 0.4002 | 0.3350 | 0.1838 | 0.4900 | 0.2869 | 0.6657 | not resampled |
| candle_range [SMALL] | 40/40 (19 sessions) | 0.9685 | 0.8100 | 0.5162 | 1.0600 | 20/20 (9 sessions) | 0.7310 | 0.6050 | 0.4175 | 0.8449 | 0.2374 | 0.4210 | not resampled |
| body_range_ratio [SMALL] | 40/40 (19 sessions) | 0.7087 | 0.7492 | 0.5865 | 0.8754 | 20/20 (9 sessions) | 0.5148 | 0.5440 | 0.3349 | 0.6657 | 0.1940 | 0.9053 | not resampled |
| directional_body_range_ratio [SMALL] | 40/40 (19 sessions) | 0.7087 | 0.7492 | 0.5865 | 0.8754 | 20/20 (9 sessions) | 0.5148 | 0.5440 | 0.3349 | 0.6657 | 0.1940 | 0.9053 | not resampled |
| close_location [SMALL] | 40/40 (19 sessions) | 0.8792 | 0.9202 | 0.8278 | 0.9771 | 20/20 (9 sessions) | 0.7655 | 0.8107 | 0.5909 | 0.9537 | 0.1137 | 0.7259 | not resampled |
| directional_close_location [SMALL] | 40/40 (19 sessions) | 0.8792 | 0.9202 | 0.8278 | 0.9771 | 20/20 (9 sessions) | 0.7655 | 0.8107 | 0.5909 | 0.9537 | 0.1137 | 0.7259 | not resampled |
| distance_beyond_level [SMALL] | 40/40 (19 sessions) | 0.3810 | 0.3100 | 0.1975 | 0.4925 | 20/20 (9 sessions) | 0.1425 | 0.1150 | 0.0600 | 0.1900 | 0.2385 | 0.9982 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 20/40 (10 sessions) | 0.4323 | 0.3149 | 0.1809 | 0.7047 | 12/20 (5 sessions) | 0.1533 | 0.1474 | 0.0504 | 0.2199 | 0.2790 | 0.9793 | not resampled |
| candle_volume [SMALL] | 40/40 (19 sessions) | 512698.3000 | 480994.0000 | 329422.2500 | 619515.7500 | 20/20 (9 sessions) | 357094.6000 | 292635.5000 | 218261.7500 | 452442.2500 | 155603.7000 | 0.6998 | not resampled |
| relative_volume_prior_6 [SMALL] | 26/40 (15 sessions) | 1.1710 | 0.9482 | 0.8006 | 1.2557 | 16/20 (7 sessions) | 0.8085 | 0.7455 | 0.5950 | 0.9271 | 0.3625 | 0.6455 | not resampled |
| atr14 [SMALL] | 20/40 (10 sessions) | 0.6838 | 0.6712 | 0.5505 | 0.7593 | 12/20 (5 sessions) | 0.7191 | 0.5865 | 0.5542 | 0.8315 | -0.0353 | -0.1502 | not resampled |
| minutes_since_open [SMALL] | 40/40 (19 sessions) | 114.8750 | 65.0000 | 25.0000 | 198.7500 | 20/20 (9 sessions) | 138.2500 | 82.5000 | 47.5000 | 221.2500 | -23.3750 | -0.2038 | not resampled |
| minutes_since_ema_cross [SMALL] | 9/40 (7 sessions) | 61.6667 | 55.0000 | 20.0000 | 85.0000 | 4/20 (4 sessions) | 81.2500 | 95.0000 | 58.7500 | 117.5000 | -19.5833 | -0.4070 | not resampled |
| break_attempt_rank [SMALL] | 40/40 (19 sessions) | 6.5250 | 5.5000 | 3.0000 | 9.2500 | 20/20 (9 sessions) | 8.1000 | 7.5000 | 5.0000 | 10.5000 | -1.5750 | -0.3553 | not resampled |
| valid_hold_sequence_rank [SMALL] | 40/40 (19 sessions) | 3.7500 | 3.0000 | 2.0000 | 5.2500 | 20/20 (9 sessions) | 5.0500 | 4.0000 | 2.7500 | 7.2500 | -1.3000 | -0.4382 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 17/40 (9 sessions) | 0.2388 | 0.2532 | 0.0943 | 0.3263 | 9/20 (4 sessions) | 0.1096 | 0.0906 | 0.0389 | 0.1421 | 0.1292 | 0.8499 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 17/40 (9 sessions) | 0.3714 | 0.3716 | 0.1479 | 0.4768 | 9/20 (4 sessions) | 0.1809 | 0.1621 | 0.0723 | 0.1878 | 0.1905 | 0.7639 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 23/40 (12 sessions) | 0.1136 | 0.1090 | 0.0575 | 0.1659 | 15/20 (7 sessions) | 0.0911 | 0.0681 | 0.0212 | 0.1759 | 0.0225 | 0.2130 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 22/40 (11 sessions) | 0.0501 | 0.0508 | -0.0216 | 0.1121 | 14/20 (6 sessions) | 0.0528 | 0.0375 | -0.0150 | 0.1293 | -0.0027 | -0.0267 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 21/40 (10 sessions) | 0.0412 | 0.0465 | -0.0274 | 0.0892 | 14/20 (6 sessions) | 0.0558 | 0.0073 | -0.0183 | 0.1300 | -0.0146 | -0.1424 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 16/40 (9 sessions) | 0.0634 | 0.0473 | 0.0269 | 0.0992 | 9/20 (4 sessions) | 0.0233 | 0.0190 | 0.0055 | 0.0321 | 0.0401 | 0.8134 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 15/40 (9 sessions) | 0.0420 | 0.0291 | -0.0127 | 0.0851 | 9/20 (4 sessions) | 0.0117 | 0.0151 | -0.0052 | 0.0159 | 0.0303 | 0.6005 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 15/40 (9 sessions) | 0.0373 | 0.0259 | -0.0068 | 0.0795 | 8/20 (4 sessions) | 0.0060 | 0.0033 | -0.0104 | 0.0173 | 0.0313 | 0.6321 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 40/40 (19 sessions) | 0.0706 | 0.0321 | 0.0051 | 0.0792 | 20/20 (9 sessions) | 0.0298 | 0.0096 | 0.0048 | 0.0457 | 0.0408 | 0.4908 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 37/40 (19 sessions) | 0.0274 | 0.0201 | -0.0013 | 0.0477 | 19/20 (8 sessions) | 0.0272 | 0.0079 | 0.0023 | 0.0398 | 0.0002 | 0.0039 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 35/40 (18 sessions) | 0.0178 | 0.0178 | -0.0017 | 0.0374 | 18/20 (8 sessions) | 0.0331 | 0.0083 | 0.0025 | 0.0525 | -0.0153 | -0.3849 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 14/40 (9 sessions) | 0.2143 | 0.0000 | 0.0000 | 0.0000 | 8/20 (4 sessions) | 0.1250 | 0.0000 | 0.0000 | 0.0000 | 0.0893 | 0.2221 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 11/40 (8 sessions) | 0.4545 | 0.0000 | 0.0000 | 1.0000 | 8/20 (4 sessions) | 0.1250 | 0.0000 | 0.0000 | 0.0000 | 0.3295 | 0.5741 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 9/40 (7 sessions) | 1.0000 | 1.0000 | 0.0000 | 2.0000 | 5/20 (4 sessions) | 0.6000 | 0.0000 | 0.0000 | 1.0000 | 0.4000 | 0.3814 | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 20/40 (10 sessions) | 0.3500 | 0.0000 | 0.0000 | 0.2500 | 12/20 (5 sessions) | 0.4167 | 0.0000 | 0.0000 | 0.2500 | -0.0667 | -0.0874 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 17/40 (9 sessions) | 0.5882 | 0.0000 | 0.0000 | 1.0000 | 9/20 (4 sessions) | 0.1111 | 0.0000 | 0.0000 | 0.0000 | 0.4771 | 0.5668 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 11/40 (8 sessions) | 1.0909 | 1.0000 | 0.5000 | 1.5000 | 8/20 (4 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | 0.5909 | 0.7377 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 14/40 (9 sessions) | 0.0714 | 0.0000 | 0.0000 | 0.0000 | 8/20 (4 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0714 | 0.3315 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 11/40 (8 sessions) | 0.3636 | 0.0000 | 0.0000 | 1.0000 | 8/20 (4 sessions) | 0.1250 | 0.0000 | 0.0000 | 0.0000 | 0.2386 | 0.5320 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 9/40 (7 sessions) | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 5/20 (4 sessions) | 0.4000 | 0.0000 | 0.0000 | 1.0000 | 0.6000 | 0.5721 | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 27/40 (15 sessions) | 1.0370 | 1.0000 | 0.0000 | 2.0000 | 18/20 (8 sessions) | 0.8889 | 0.0000 | 0.0000 | 2.0000 | 0.1481 | 0.1313 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 21/40 (10 sessions) | 1.7619 | 1.0000 | 1.0000 | 2.0000 | 14/20 (6 sessions) | 1.5000 | 1.5000 | 0.0000 | 2.7500 | 0.2619 | 0.1734 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 15/40 (9 sessions) | 3.0000 | 2.0000 | 1.5000 | 4.0000 | 8/20 (4 sessions) | 2.1250 | 2.0000 | 1.0000 | 3.0000 | 0.8750 | 0.3808 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 27/40 (15 sessions) | 1.7212 | 1.5150 | 1.2500 | 2.0645 | 18/20 (8 sessions) | 1.9480 | 1.8146 | 1.2375 | 2.7388 | -0.2267 | -0.2681 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 21/40 (10 sessions) | 2.1438 | 2.2350 | 1.6800 | 2.5800 | 14/20 (6 sessions) | 2.4875 | 2.2100 | 1.5100 | 3.1940 | -0.3437 | -0.3753 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 15/40 (9 sessions) | 2.8443 | 2.9300 | 2.1700 | 3.5725 | 8/20 (4 sessions) | 2.5269 | 2.3750 | 2.2200 | 2.7338 | 0.3175 | 0.3894 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 20/40 (10 sessions) | 2.3578 | 2.2532 | 1.8146 | 2.7381 | 12/20 (5 sessions) | 2.1175 | 1.8280 | 1.5030 | 2.7754 | 0.2403 | 0.3421 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 20/40 (10 sessions) | 3.1674 | 3.1405 | 2.7680 | 3.6326 | 12/20 (5 sessions) | 3.0826 | 2.9981 | 2.6188 | 3.7605 | 0.0847 | 0.1082 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 15/40 (9 sessions) | 4.4780 | 4.5366 | 3.7078 | 4.9554 | 8/20 (4 sessions) | 4.6322 | 4.3470 | 3.9346 | 5.0549 | -0.1541 | -0.1392 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 27/40 (15 sessions) | 0.4560 | 0.3608 | 0.1793 | 0.7407 | 18/20 (8 sessions) | 0.3570 | 0.2570 | 0.1656 | 0.4376 | 0.0990 | 0.3116 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 21/40 (10 sessions) | 0.2776 | 0.1992 | 0.1250 | 0.3834 | 14/20 (6 sessions) | 0.2693 | 0.2004 | 0.0965 | 0.3908 | 0.0082 | 0.0394 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 15/40 (9 sessions) | 0.1681 | 0.1463 | 0.0813 | 0.1910 | 8/20 (4 sessions) | 0.1541 | 0.1250 | 0.0730 | 0.2272 | 0.0140 | 0.0967 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 27/40 (15 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 18/20 (8 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 21/40 (10 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 14/20 (6 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 15/40 (9 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 8/20 (4 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 27/40 (15 sessions) | 0.4537 | 0.5000 | 0.2500 | 0.5000 | 18/20 (8 sessions) | 0.5556 | 0.5000 | 0.5000 | 0.7500 | -0.1019 | -0.4268 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 21/40 (10 sessions) | 0.5143 | 0.5000 | 0.4000 | 0.6000 | 14/20 (6 sessions) | 0.5214 | 0.5000 | 0.4250 | 0.6000 | -0.0071 | -0.0373 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 15/40 (9 sessions) | 0.4939 | 0.4545 | 0.4091 | 0.5455 | 8/20 (4 sessions) | 0.5057 | 0.5909 | 0.3523 | 0.6023 | -0.0117 | -0.1052 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 20/40 (10 sessions) | 1.3081 | 1.2484 | 0.3287 | 1.6778 | 12/20 (5 sessions) | 0.8062 | 0.8029 | 0.3772 | 1.0594 | 0.5019 | 0.4711 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 20/40 (10 sessions) | 0.8230 | 0.7305 | 0.3459 | 0.9237 | 12/20 (5 sessions) | 0.7966 | 0.7097 | 0.4158 | 0.9734 | 0.0264 | 0.0328 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 17/40 (9 sessions) | 0.6636 | 0.6366 | 0.2704 | 0.6887 | 9/20 (4 sessions) | 0.8217 | 0.6562 | 0.5501 | 0.7845 | -0.1581 | -0.2410 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 25/40 (15 sessions) | 1.3414 | 0.9500 | 0.3400 | 2.2400 | 11/20 (7 sessions) | 1.6346 | 1.4700 | 1.0450 | 2.2350 | -0.2932 | -0.2379 | not resampled |
| stage11_2.room_in_atr [SMALL] | 12/40 (8 sessions) | 2.2422 | 2.1496 | 0.9415 | 3.4585 | 5/20 (3 sessions) | 1.7392 | 1.9794 | 1.1221 | 2.7266 | 0.5030 | 0.3390 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 40/40 (19 sessions) | 1.0750 | 1.0000 | 0.0000 | 2.0000 | 20/20 (9 sessions) | 1.2000 | 1.5000 | 0.0000 | 2.0000 | -0.1250 | -0.1190 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 40/40 (19 sessions) | 4.9250 | 5.0000 | 4.0000 | 6.0000 | 20/20 (9 sessions) | 4.8000 | 4.5000 | 4.0000 | 6.0000 | 0.1250 | 0.1190 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 25/40 (15 sessions) | 1.3414 | 0.9500 | 0.3400 | 2.2400 | 11/20 (7 sessions) | 1.6346 | 1.4700 | 1.0450 | 2.2350 | -0.2932 | -0.2379 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 40/40 (19 sessions) | 0.3620 | 0.3050 | 0.1850 | 0.4925 | 20/20 (9 sessions) | 0.1425 | 0.1150 | 0.0600 | 0.1900 | 0.2195 | 0.9269 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 20/40 (10 sessions) | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 12/20 (5 sessions) | 0.0833 | 0.0000 | 0.0000 | 0.0000 | 0.0167 | 0.0554 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 20/40 (10 sessions) | 0.1500 | 0.0000 | 0.0000 | 0.0000 | 12/20 (5 sessions) | 0.0833 | 0.0000 | 0.0000 | 0.0000 | 0.0667 | 0.1961 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 25/40 (13 sessions) | 0.5952 | 0.4600 | 0.2900 | 0.7700 | 17/20 (7 sessions) | 0.7932 | 0.6300 | 0.3700 | 1.1000 | -0.1980 | -0.4433 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 21/40 (11 sessions) | 1.3773 | 1.3350 | 0.9195 | 1.8150 | 16/20 (7 sessions) | 1.6012 | 1.3950 | 0.6749 | 2.1625 | -0.2239 | -0.2184 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 20/40 (10 sessions) | 0.9048 | 0.8600 | 0.5094 | 1.1921 | 12/20 (5 sessions) | 1.1167 | 0.7650 | 0.4609 | 1.6326 | -0.2119 | -0.3273 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 20/40 (10 sessions) | 2.1454 | 2.0715 | 1.1111 | 2.8735 | 12/20 (5 sessions) | 1.5066 | 1.2371 | 0.9416 | 2.1312 | 0.6388 | 0.5477 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG | 60 | 19 | 40 | 20 | 100.00% | 100.00% | 66.67% |
| time_bucket | 09:35-10:00 [SMALL] | 15 | 13 | 13 | 2 | 32.50% | 10.00% | 86.67% |
| time_bucket | 10:00-10:30 [SMALL] | 10 | 8 | 6 | 4 | 15.00% | 20.00% | 60.00% |
| time_bucket | 10:30-11:00 [SMALL] | 7 | 5 | 3 | 4 | 7.50% | 20.00% | 42.86% |
| time_bucket | 11:00-12:00 [SMALL] | 9 | 5 | 7 | 2 | 17.50% | 10.00% | 77.78% |
| time_bucket | 12:00-13:30 [SMALL] | 9 | 5 | 6 | 3 | 15.00% | 15.00% | 66.67% |
| time_bucket | 13:30-15:00 [SMALL] | 4 | 3 | 1 | 3 | 2.50% | 15.00% | 25.00% |
| time_bucket | 15:00-close [SMALL] | 6 | 5 | 4 | 2 | 10.00% | 10.00% | 66.67% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 15 | 6 | 9 | 6 | 22.50% | 30.00% | 60.00% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 11 | 5 | 8 | 3 | 20.00% | 15.00% | 72.73% |
| ema9_20_alignment | EMA_UNAVAILABLE | 34 | 18 | 23 | 11 | 57.50% | 55.00% | 67.65% |
| price_vwap_alignment | VWAP_ALIGNED | 53 | 19 | 35 | 18 | 87.50% | 90.00% | 66.04% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 7 | 2 | 5 | 2 | 12.50% | 10.00% | 71.43% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED [SMALL] | 28 | 11 | 16 | 12 | 40.00% | 60.00% | 57.14% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 11 | 4 | 8 | 3 | 20.00% | 15.00% | 72.73% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 21 | 15 | 16 | 5 | 40.00% | 25.00% | 76.19% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 19 | 7 | 13 | 6 | 32.50% | 30.00% | 68.42% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 7 | 4 | 4 | 3 | 10.00% | 15.00% | 57.14% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 34 | 18 | 23 | 11 | 57.50% | 55.00% | 67.65% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 5 | 4 | 4 | 1 | 10.00% | 5.00% | 80.00% |
| prior_ema_cross | NO_PRIOR_CROSS | 47 | 18 | 31 | 16 | 77.50% | 80.00% | 65.96% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 8 | 5 | 5 | 3 | 12.50% | 15.00% | 62.50% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 42 | 13 | 26 | 16 | 65.00% | 80.00% | 61.90% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 17 | 8 | 14 | 3 | 35.00% | 15.00% | 82.35% |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 1 | 1 | 0 | 1 | 0.00% | 5.00% | 0.00% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 1 | 1 | 1 | 0 | 2.50% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 3 | 2 | 2 | 1 | 5.00% | 5.00% | 66.67% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 2 | 2 | 1 | 1 | 2.50% | 5.00% | 50.00% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 4 | 1 | 2 | 2 | 5.00% | 10.00% | 50.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 4 | 3 | 4 | 0 | 10.00% | 0.00% | 100.00% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 3 | 2 | 2 | 1 | 5.00% | 5.00% | 66.67% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 24 | 5 | 15 | 9 | 37.50% | 45.00% | 62.50% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 19 | 12 | 13 | 6 | 32.50% | 30.00% | 68.42% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 60 | 19 | 40 | 20 | 100.00% | 100.00% | 66.67% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 4 | 3 | 3 | 1 | 7.50% | 5.00% | 75.00% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 9 | 5 | 7 | 2 | 17.50% | 10.00% | 77.78% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 15 | 6 | 8 | 7 | 20.00% | 35.00% | 53.33% |
| stage11_3.structure | UNAVAILABLE | 32 | 17 | 22 | 10 | 55.00% | 50.00% | 68.75% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 9 | 5 | 7 | 2 | 17.50% | 10.00% | 77.78% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 19 | 6 | 11 | 8 | 27.50% | 40.00% | 57.89% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 32 | 17 | 22 | 10 | 55.00% | 50.00% | 68.75% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 16 | 8 | 11 | 5 | 27.50% | 25.00% | 68.75% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 16 | 5 | 9 | 7 | 22.50% | 35.00% | 56.25% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 28 | 16 | 20 | 8 | 50.00% | 40.00% | 71.43% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 23 | 9 | 13 | 10 | 32.50% | 50.00% | 56.52% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 8 | 6 | 6 | 2 | 15.00% | 10.00% | 75.00% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 29 | 17 | 21 | 8 | 52.50% | 40.00% | 72.41% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 18 | 15 | 15 | 3 | 37.50% | 15.00% | 83.33% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 18 | 4 | 10 | 8 | 25.00% | 40.00% | 55.56% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 3 | 2 | 2 | 1 | 5.00% | 5.00% | 66.67% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 21 | 9 | 13 | 8 | 32.50% | 40.00% | 61.90% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 60 | 19 | 40 | 20 | 100.00% | 100.00% | 66.67% |


### 2026-06


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 28/28 (16 sessions) | 2.0590 | 1.9688 | 1.3825 | 2.8550 | 18/18 (9 sessions) | 2.0724 | 1.9038 | 1.4100 | 2.9050 | -0.0133 | -0.0162 | not resampled |
| body_size [SMALL] | 28/28 (16 sessions) | 1.1802 | 0.8250 | 0.5100 | 1.0500 | 18/18 (9 sessions) | 0.9211 | 0.8500 | 0.3722 | 1.4050 | 0.2591 | 0.2290 | not resampled |
| directional_body [SMALL] | 28/28 (16 sessions) | 1.1802 | 0.8250 | 0.5100 | 1.0500 | 18/18 (9 sessions) | 0.9211 | 0.8500 | 0.3722 | 1.4050 | 0.2591 | 0.2290 | not resampled |
| candle_range [SMALL] | 28/28 (16 sessions) | 1.5720 | 1.1375 | 0.8175 | 1.5875 | 18/18 (9 sessions) | 1.4822 | 1.2550 | 0.7725 | 2.0625 | 0.0897 | 0.0743 | not resampled |
| body_range_ratio [SMALL] | 28/28 (16 sessions) | 0.6895 | 0.7101 | 0.6213 | 0.8706 | 18/18 (9 sessions) | 0.5880 | 0.5370 | 0.4433 | 0.7538 | 0.1015 | 0.4723 | not resampled |
| directional_body_range_ratio [SMALL] | 28/28 (16 sessions) | 0.6895 | 0.7101 | 0.6213 | 0.8706 | 18/18 (9 sessions) | 0.5880 | 0.5370 | 0.4433 | 0.7538 | 0.1015 | 0.4723 | not resampled |
| close_location [SMALL] | 28/28 (16 sessions) | 0.8630 | 0.9045 | 0.7819 | 0.9756 | 18/18 (9 sessions) | 0.7716 | 0.8178 | 0.6533 | 0.8781 | 0.0915 | 0.6311 | not resampled |
| directional_close_location [SMALL] | 28/28 (16 sessions) | 0.8630 | 0.9045 | 0.7819 | 0.9756 | 18/18 (9 sessions) | 0.7716 | 0.8178 | 0.6533 | 0.8781 | 0.0915 | 0.6311 | not resampled |
| distance_beyond_level [SMALL] | 28/28 (16 sessions) | 0.6262 | 0.4875 | 0.2188 | 0.7600 | 18/18 (9 sessions) | 0.1494 | 0.1500 | 0.0475 | 0.2100 | 0.4768 | 0.8834 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 13/28 (7 sessions) | 0.5098 | 0.3705 | 0.3092 | 0.4954 | 7/18 (3 sessions) | 0.0793 | 0.0795 | 0.0182 | 0.1259 | 0.4305 | 1.0357 | not resampled |
| candle_volume [SMALL] | 28/28 (16 sessions) | 742179.1071 | 617518.0000 | 390925.0000 | 841162.0000 | 18/18 (9 sessions) | 628540.5000 | 582652.0000 | 512066.0000 | 779428.7500 | 113638.6071 | 0.2372 | not resampled |
| relative_volume_prior_6 [SMALL] | 18/28 (11 sessions) | 1.2975 | 0.8059 | 0.7298 | 1.5120 | 11/18 (5 sessions) | 0.9129 | 0.8217 | 0.7743 | 1.1192 | 0.3846 | 0.4117 | not resampled |
| atr14 [SMALL] | 13/28 (7 sessions) | 1.2127 | 1.0864 | 0.8454 | 1.5692 | 7/18 (3 sessions) | 1.5292 | 1.7107 | 1.2556 | 1.8365 | -0.3165 | -0.6753 | not resampled |
| minutes_since_open [SMALL] | 28/28 (16 sessions) | 112.5000 | 62.5000 | 23.7500 | 173.7500 | 18/18 (9 sessions) | 81.3889 | 52.5000 | 25.0000 | 160.0000 | 31.1111 | 0.3064 | not resampled |
| minutes_since_ema_cross [SMALL] | 7/28 (3 sessions) | 30.7143 | 15.0000 | 7.5000 | 50.0000 | 3/18 (2 sessions) | 13.3333 | 20.0000 | 10.0000 | 20.0000 | 17.3810 | 0.5967 | not resampled |
| break_attempt_rank [SMALL] | 28/28 (16 sessions) | 6.3214 | 4.0000 | 2.7500 | 7.0000 | 18/18 (9 sessions) | 5.5556 | 4.0000 | 3.0000 | 7.7500 | 0.7659 | 0.1448 | not resampled |
| valid_hold_sequence_rank [SMALL] | 28/28 (16 sessions) | 3.2143 | 2.5000 | 1.0000 | 4.0000 | 18/18 (9 sessions) | 2.8889 | 2.5000 | 1.2500 | 4.0000 | 0.3254 | 0.1488 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 10/28 (5 sessions) | 0.2651 | 0.1839 | 0.1205 | 0.4402 | 6/18 (3 sessions) | 0.2961 | 0.2703 | 0.1325 | 0.4260 | -0.0310 | -0.1353 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 10/28 (5 sessions) | 0.2970 | 0.1684 | 0.0931 | 0.4461 | 6/18 (3 sessions) | 0.2471 | 0.2547 | 0.0802 | 0.3866 | 0.0499 | 0.1874 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 16/28 (10 sessions) | 0.2465 | 0.1484 | 0.0820 | 0.3030 | 10/18 (5 sessions) | 0.0702 | 0.0921 | 0.0521 | 0.1202 | 0.1763 | 0.7391 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 16/28 (10 sessions) | 0.1166 | 0.0671 | 0.0050 | 0.1709 | 9/18 (4 sessions) | -0.0311 | 0.0103 | -0.0298 | 0.0471 | 0.1478 | 0.9992 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 15/28 (9 sessions) | 0.0667 | 0.0407 | -0.0128 | 0.1488 | 7/18 (3 sessions) | -0.0439 | 0.0210 | -0.0774 | 0.0457 | 0.1106 | 0.8452 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 10/28 (5 sessions) | 0.0878 | 0.0541 | -0.0197 | 0.1190 | 6/18 (3 sessions) | 0.0609 | 0.0647 | 0.0504 | 0.0810 | 0.0268 | 0.2077 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 10/28 (5 sessions) | 0.0301 | 0.0253 | -0.0417 | 0.1049 | 6/18 (3 sessions) | 0.0174 | 0.0267 | -0.0035 | 0.0467 | 0.0126 | 0.1554 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 10/28 (5 sessions) | 0.0054 | 0.0198 | -0.0534 | 0.0612 | 6/18 (3 sessions) | 0.0112 | 0.0255 | -0.0288 | 0.0439 | -0.0058 | -0.0824 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 28/28 (16 sessions) | 0.1119 | 0.0581 | 0.0151 | 0.1901 | 18/18 (9 sessions) | 0.0663 | 0.0200 | 0.0146 | 0.0755 | 0.0456 | 0.3486 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 24/28 (14 sessions) | 0.0571 | 0.0350 | 0.0083 | 0.0796 | 16/18 (9 sessions) | 0.0180 | 0.0113 | -0.0020 | 0.0213 | 0.0390 | 0.5393 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 23/28 (14 sessions) | 0.0418 | 0.0311 | 0.0082 | 0.0557 | 15/18 (9 sessions) | 0.0187 | 0.0105 | -0.0022 | 0.0256 | 0.0231 | 0.3940 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 9/28 (4 sessions) | 0.4444 | 0.0000 | 0.0000 | 1.0000 | 6/18 (3 sessions) | 0.6667 | 0.5000 | 0.0000 | 1.0000 | -0.2222 | -0.3399 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 9/28 (4 sessions) | 0.7778 | 1.0000 | 0.0000 | 1.0000 | 5/18 (3 sessions) | 1.0000 | 1.0000 | 0.0000 | 2.0000 | -0.2222 | -0.2490 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 6/28 (4 sessions) | 1.5000 | 1.0000 | 1.0000 | 2.5000 | 0/18 (0 sessions) | N/A | N/A | N/A | N/A | N/A | N/A | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 13/28 (7 sessions) | 0.3077 | 0.0000 | 0.0000 | 1.0000 | 7/18 (3 sessions) | 0.1429 | 0.0000 | 0.0000 | 0.0000 | 0.1648 | 0.3672 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 10/28 (5 sessions) | 0.5000 | 0.0000 | 0.0000 | 1.0000 | 6/18 (3 sessions) | 0.1667 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5401 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 8/28 (4 sessions) | 0.6250 | 0.5000 | 0.0000 | 1.0000 | 5/18 (3 sessions) | 0.4000 | 0.0000 | 0.0000 | 1.0000 | 0.2250 | 0.3313 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 9/28 (4 sessions) | 0.1111 | 0.0000 | 0.0000 | 0.0000 | 6/18 (3 sessions) | 0.1667 | 0.0000 | 0.0000 | 0.0000 | -0.0556 | -0.1526 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 9/28 (4 sessions) | 0.4444 | 0.0000 | 0.0000 | 1.0000 | 5/18 (3 sessions) | 0.2000 | 0.0000 | 0.0000 | 0.0000 | 0.2444 | 0.4871 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 6/28 (4 sessions) | 0.6667 | 0.5000 | 0.0000 | 1.0000 | 0/18 (0 sessions) | N/A | N/A | N/A | N/A | N/A | N/A | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 20/28 (13 sessions) | 1.0000 | 1.0000 | 0.0000 | 1.2500 | 12/18 (6 sessions) | 1.8333 | 2.0000 | 1.7500 | 2.2500 | -0.8333 | -0.7247 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 15/28 (9 sessions) | 1.6000 | 1.0000 | 0.0000 | 3.0000 | 7/18 (3 sessions) | 2.7143 | 4.0000 | 1.0000 | 4.0000 | -1.1143 | -0.6180 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 9/28 (4 sessions) | 2.5556 | 1.0000 | 0.0000 | 4.0000 | 6/18 (3 sessions) | 4.3333 | 5.5000 | 2.0000 | 6.0000 | -1.7778 | -0.5426 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 20/28 (13 sessions) | 2.5010 | 2.0175 | 1.4875 | 3.1150 | 12/18 (6 sessions) | 2.7392 | 2.5550 | 1.4475 | 3.8675 | -0.2382 | -0.1555 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 15/28 (9 sessions) | 3.1310 | 2.5800 | 1.9800 | 3.8300 | 7/18 (3 sessions) | 4.2529 | 5.2250 | 3.0250 | 5.4600 | -1.1219 | -0.6339 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 9/28 (4 sessions) | 4.9244 | 4.7800 | 2.8000 | 6.8200 | 6/18 (3 sessions) | 6.1292 | 6.5875 | 5.2188 | 7.2700 | -1.2047 | -0.6010 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 13/28 (7 sessions) | 2.1500 | 2.1466 | 1.6594 | 2.3428 | 7/18 (3 sessions) | 1.9176 | 1.8174 | 1.4982 | 2.1895 | 0.2323 | 0.3151 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 13/28 (7 sessions) | 2.6183 | 2.5204 | 2.1374 | 2.8506 | 7/18 (3 sessions) | 2.6881 | 2.7850 | 2.3707 | 3.1260 | -0.0698 | -0.0976 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 9/28 (4 sessions) | 4.4475 | 4.3203 | 3.5801 | 5.5710 | 6/18 (3 sessions) | 4.2787 | 4.0520 | 3.7583 | 4.6468 | 0.1688 | 0.1472 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 20/28 (13 sessions) | 0.4688 | 0.4658 | 0.2925 | 0.6625 | 12/18 (6 sessions) | 0.2849 | 0.2575 | 0.1228 | 0.4460 | 0.1839 | 0.7773 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 15/28 (9 sessions) | 0.2581 | 0.2390 | 0.1542 | 0.3432 | 7/18 (3 sessions) | 0.1746 | 0.1468 | 0.1297 | 0.2032 | 0.0834 | 0.6299 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 9/28 (4 sessions) | 0.1815 | 0.2268 | 0.1252 | 0.2493 | 6/18 (3 sessions) | 0.1134 | 0.0853 | 0.0296 | 0.1676 | 0.0681 | 0.6487 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 20/28 (13 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 12/18 (6 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 15/28 (9 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 7/18 (3 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 9/28 (4 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 6/18 (3 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 20/28 (13 sessions) | 0.6000 | 0.5000 | 0.5000 | 0.7500 | 12/18 (6 sessions) | 0.5625 | 0.5000 | 0.5000 | 0.7500 | 0.0375 | 0.1580 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 15/28 (9 sessions) | 0.5733 | 0.6000 | 0.5000 | 0.6500 | 7/18 (3 sessions) | 0.5143 | 0.5000 | 0.4500 | 0.6000 | 0.0590 | 0.4414 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 9/28 (4 sessions) | 0.5808 | 0.5455 | 0.5000 | 0.6364 | 6/18 (3 sessions) | 0.5000 | 0.5000 | 0.4659 | 0.5341 | 0.0808 | 0.9295 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 13/28 (7 sessions) | 1.3786 | 1.2553 | 1.0225 | 1.7175 | 7/18 (3 sessions) | 0.9886 | 0.6755 | 0.6149 | 1.2772 | 0.3901 | 0.5550 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 13/28 (7 sessions) | 0.7997 | 0.5760 | 0.2853 | 1.1924 | 7/18 (3 sessions) | 0.7671 | 0.4660 | 0.3102 | 1.2102 | 0.0326 | 0.0486 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 10/28 (5 sessions) | 0.6973 | 0.8274 | 0.2945 | 0.9560 | 6/18 (3 sessions) | 0.6394 | 0.4843 | 0.3660 | 0.8882 | 0.0578 | 0.1161 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 22/28 (13 sessions) | 2.7348 | 1.8875 | 1.1650 | 2.3950 | 12/18 (6 sessions) | 2.0254 | 2.3300 | 1.7012 | 2.4525 | 0.7094 | 0.3581 | not resampled |
| stage11_2.room_in_atr [SMALL] | 11/28 (6 sessions) | 3.4741 | 2.7407 | 1.2955 | 4.4596 | 5/18 (2 sessions) | 1.3679 | 1.3620 | 1.3186 | 1.3711 | 2.1062 | 0.8946 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 28/28 (16 sessions) | 1.3214 | 1.0000 | 1.0000 | 2.0000 | 18/18 (9 sessions) | 1.1111 | 1.0000 | 0.0000 | 2.0000 | 0.2103 | 0.2267 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 28/28 (16 sessions) | 4.6786 | 5.0000 | 4.0000 | 5.0000 | 18/18 (9 sessions) | 4.8889 | 5.0000 | 4.0000 | 6.0000 | -0.2103 | -0.2267 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 22/28 (13 sessions) | 2.7348 | 1.8875 | 1.1650 | 2.3950 | 12/18 (6 sessions) | 2.0254 | 2.3300 | 1.7012 | 2.4525 | 0.7094 | 0.3581 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 28/28 (16 sessions) | 0.5027 | 0.4750 | 0.2188 | 0.7025 | 18/18 (9 sessions) | 0.1488 | 0.1500 | 0.0475 | 0.2075 | 0.3538 | 1.0814 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 13/28 (7 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 7/18 (3 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 13/28 (7 sessions) | 0.0769 | 0.0000 | 0.0000 | 0.0000 | 7/18 (3 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0769 | 0.3397 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 17/28 (11 sessions) | 0.9294 | 0.4400 | 0.3200 | 0.8600 | 11/18 (5 sessions) | 1.4632 | 0.9400 | 0.4950 | 2.4300 | -0.5338 | -0.4109 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 19/28 (11 sessions) | 2.4974 | 1.7700 | 1.0950 | 3.1275 | 11/18 (6 sessions) | 2.1864 | 2.4400 | 1.4025 | 2.8400 | 0.3110 | 0.1921 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 13/28 (7 sessions) | 0.9799 | 0.5480 | 0.2422 | 0.9581 | 7/18 (3 sessions) | 0.9565 | 0.7014 | 0.4909 | 1.4983 | 0.0234 | 0.0218 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 13/28 (7 sessions) | 1.9945 | 2.0456 | 1.4962 | 2.3099 | 7/18 (3 sessions) | 1.6849 | 1.5965 | 1.3615 | 1.8881 | 0.3096 | 0.3625 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG | 46 | 16 | 28 | 18 | 100.00% | 100.00% | 60.87% |
| time_bucket | 09:35-10:00 [SMALL] | 14 | 11 | 8 | 6 | 28.57% | 33.33% | 57.14% |
| time_bucket | 10:00-10:30 [SMALL] | 10 | 8 | 5 | 5 | 17.86% | 27.78% | 50.00% |
| time_bucket | 10:30-11:00 [SMALL] | 5 | 5 | 4 | 1 | 14.29% | 5.56% | 80.00% |
| time_bucket | 11:00-12:00 [SMALL] | 3 | 3 | 2 | 1 | 7.14% | 5.56% | 66.67% |
| time_bucket | 12:00-13:30 [SMALL] | 9 | 3 | 4 | 5 | 14.29% | 27.78% | 44.44% |
| time_bucket | 13:30-15:00 [SMALL] | 2 | 2 | 2 | 0 | 7.14% | 0.00% | 100.00% |
| time_bucket | 15:00-close [SMALL] | 3 | 2 | 3 | 0 | 10.71% | 0.00% | 100.00% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 11 | 3 | 5 | 6 | 17.86% | 33.33% | 45.45% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 5 | 3 | 5 | 0 | 17.86% | 0.00% | 100.00% |
| ema9_20_alignment | EMA_UNAVAILABLE | 30 | 16 | 18 | 12 | 64.29% | 66.67% | 60.00% |
| price_vwap_alignment | VWAP_ALIGNED | 44 | 16 | 26 | 18 | 92.86% | 100.00% | 59.09% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 2 | 1 | 2 | 0 | 7.14% | 0.00% | 100.00% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED [SMALL] | 22 | 10 | 14 | 8 | 50.00% | 44.44% | 63.64% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 5 | 2 | 3 | 2 | 10.71% | 11.11% | 60.00% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 19 | 14 | 11 | 8 | 39.29% | 44.44% | 57.89% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 13 | 4 | 7 | 6 | 25.00% | 33.33% | 53.85% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 3 | 2 | 3 | 0 | 10.71% | 0.00% | 100.00% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE | 30 | 16 | 18 | 12 | 64.29% | 66.67% | 60.00% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 6 | 2 | 3 | 3 | 10.71% | 16.67% | 50.00% |
| prior_ema_cross | NO_PRIOR_CROSS | 36 | 16 | 21 | 15 | 75.00% | 83.33% | 58.33% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 4 | 2 | 4 | 0 | 14.29% | 0.00% | 100.00% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE [SMALL] | 24 | 7 | 14 | 10 | 50.00% | 55.56% | 58.33% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 20 | 9 | 13 | 7 | 46.43% | 38.89% | 65.00% |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 2 | 2 | 1 | 1 | 3.57% | 5.56% | 50.00% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 1 | 1 | 1 | 0 | 3.57% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 7 | 3 | 3 | 4 | 10.71% | 22.22% | 42.86% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 1 | 1 | 0 | 1 | 0.00% | 5.56% | 0.00% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 3 | 2 | 3 | 0 | 10.71% | 0.00% | 100.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 4 | 3 | 4 | 0 | 14.29% | 0.00% | 100.00% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 12 | 3 | 6 | 6 | 21.43% | 33.33% | 50.00% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 18 | 11 | 11 | 7 | 39.29% | 38.89% | 61.11% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 46 | 16 | 28 | 18 | 100.00% | 100.00% | 60.87% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 4 | 3 | 4 | 0 | 14.29% | 0.00% | 100.00% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 7 | 4 | 3 | 4 | 10.71% | 22.22% | 42.86% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 5 | 2 | 3 | 2 | 10.71% | 11.11% | 60.00% |
| stage11_3.structure | UNAVAILABLE | 30 | 16 | 18 | 12 | 64.29% | 66.67% | 60.00% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 7 | 4 | 3 | 4 | 10.71% | 22.22% | 42.86% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 9 | 4 | 7 | 2 | 25.00% | 11.11% | 77.78% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE | 30 | 16 | 18 | 12 | 64.29% | 66.67% | 60.00% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 8 | 4 | 4 | 4 | 14.29% | 22.22% | 50.00% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 9 | 4 | 7 | 2 | 25.00% | 11.11% | 77.78% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 29 | 15 | 17 | 12 | 60.71% | 66.67% | 58.62% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 15 | 6 | 8 | 7 | 28.57% | 38.89% | 53.33% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 6 | 5 | 6 | 0 | 21.43% | 0.00% | 100.00% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 25 | 15 | 14 | 11 | 50.00% | 61.11% | 56.00% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 18 | 14 | 11 | 7 | 39.29% | 38.89% | 61.11% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 7 | 3 | 4 | 3 | 14.29% | 16.67% | 57.14% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 3 | 2 | 1 | 2 | 3.57% | 11.11% | 33.33% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 18 | 7 | 12 | 6 | 42.86% | 33.33% | 66.67% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 46 | 16 | 28 | 18 | 100.00% | 100.00% | 60.87% |


### 2026-07


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 31/31 (18 sessions) | 1.4950 | 1.4957 | 1.2750 | 1.6100 | 12/12 (6 sessions) | 1.4036 | 1.4600 | 1.0800 | 1.6078 | 0.0914 | 0.2322 | not resampled |
| body_size [SMALL] | 31/31 (18 sessions) | 0.7142 | 0.6000 | 0.3150 | 0.9650 | 12/12 (6 sessions) | 0.4316 | 0.3450 | 0.2575 | 0.5375 | 0.2826 | 0.6042 | not resampled |
| directional_body [SMALL] | 31/31 (18 sessions) | 0.7142 | 0.6000 | 0.3150 | 0.9650 | 12/12 (6 sessions) | 0.4316 | 0.3450 | 0.2575 | 0.5375 | 0.2826 | 0.6042 | not resampled |
| candle_range [SMALL] | 31/31 (18 sessions) | 1.1524 | 1.0600 | 0.7125 | 1.3190 | 12/12 (6 sessions) | 0.9100 | 0.8900 | 0.5100 | 1.1375 | 0.2424 | 0.4354 | not resampled |
| body_range_ratio [SMALL] | 31/31 (18 sessions) | 0.5892 | 0.6481 | 0.4719 | 0.7452 | 12/12 (6 sessions) | 0.4472 | 0.4601 | 0.3413 | 0.5821 | 0.1420 | 0.6462 | not resampled |
| directional_body_range_ratio [SMALL] | 31/31 (18 sessions) | 0.5892 | 0.6481 | 0.4719 | 0.7452 | 12/12 (6 sessions) | 0.4472 | 0.4601 | 0.3413 | 0.5821 | 0.1420 | 0.6462 | not resampled |
| close_location [SMALL] | 31/31 (18 sessions) | 0.7982 | 0.8791 | 0.6834 | 0.9306 | 12/12 (6 sessions) | 0.7598 | 0.7664 | 0.6382 | 0.9126 | 0.0384 | 0.2191 | not resampled |
| directional_close_location [SMALL] | 31/31 (18 sessions) | 0.7982 | 0.8791 | 0.6834 | 0.9306 | 12/12 (6 sessions) | 0.7598 | 0.7664 | 0.6382 | 0.9126 | 0.0384 | 0.2191 | not resampled |
| distance_beyond_level [SMALL] | 31/31 (18 sessions) | 0.3152 | 0.1900 | 0.1275 | 0.3724 | 12/12 (6 sessions) | 0.1451 | 0.0620 | 0.0399 | 0.2250 | 0.1701 | 0.6583 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 15/31 (12 sessions) | 0.3931 | 0.3138 | 0.1805 | 0.5538 | 6/12 (3 sessions) | 0.1452 | 0.0725 | 0.0584 | 0.1933 | 0.2479 | 0.9618 | not resampled |
| candle_volume [SMALL] | 31/31 (18 sessions) | 573736.8387 | 540407.0000 | 341015.5000 | 770571.0000 | 12/12 (6 sessions) | 485812.0000 | 423192.0000 | 381666.7500 | 568525.2500 | 87924.8387 | 0.3536 | not resampled |
| relative_volume_prior_6 [SMALL] | 20/31 (14 sessions) | 1.1583 | 1.0727 | 0.8241 | 1.4271 | 10/12 (6 sessions) | 0.9408 | 0.8635 | 0.6617 | 1.1729 | 0.2175 | 0.5044 | not resampled |
| atr14 [SMALL] | 15/31 (12 sessions) | 0.9223 | 0.9120 | 0.7792 | 1.1955 | 6/12 (3 sessions) | 0.8563 | 0.8450 | 0.7146 | 0.9365 | 0.0660 | 0.2558 | not resampled |
| minutes_since_open [SMALL] | 31/31 (18 sessions) | 104.5161 | 65.0000 | 20.0000 | 125.0000 | 12/12 (6 sessions) | 112.9167 | 67.5000 | 43.7500 | 136.2500 | -8.4005 | -0.0770 | not resampled |
| minutes_since_ema_cross [SMALL] | 7/31 (7 sessions) | 87.1429 | 95.0000 | 27.5000 | 117.5000 | 3/12 (1 sessions) | 156.6667 | 165.0000 | 140.0000 | 177.5000 | -69.5238 | -1.0532 | not resampled |
| break_attempt_rank [SMALL] | 31/31 (18 sessions) | 5.6129 | 5.0000 | 2.0000 | 8.0000 | 12/12 (6 sessions) | 5.7500 | 6.5000 | 4.0000 | 7.2500 | -0.1371 | -0.0388 | not resampled |
| valid_hold_sequence_rank [SMALL] | 31/31 (18 sessions) | 2.5806 | 2.0000 | 1.0000 | 4.0000 | 12/12 (6 sessions) | 2.8333 | 3.0000 | 2.0000 | 4.0000 | -0.2527 | -0.1608 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 12/31 (11 sessions) | 0.4532 | 0.4514 | 0.2487 | 0.5656 | 4/12 (2 sessions) | 0.5269 | 0.4259 | 0.3730 | 0.5799 | -0.0737 | -0.2746 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 12/31 (11 sessions) | 0.5069 | 0.5549 | 0.3410 | 0.6951 | 4/12 (2 sessions) | 0.6814 | 0.6509 | 0.5334 | 0.7989 | -0.1745 | -0.6802 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 20/31 (14 sessions) | 0.1880 | 0.1307 | 0.0538 | 0.3018 | 8/12 (5 sessions) | 0.1113 | 0.1349 | 0.0784 | 0.1547 | 0.0767 | 0.4858 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 19/31 (14 sessions) | 0.1097 | 0.0691 | 0.0208 | 0.1933 | 7/12 (4 sessions) | 0.0750 | 0.0735 | 0.0570 | 0.1171 | 0.0348 | 0.2307 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 18/31 (13 sessions) | 0.0684 | 0.0464 | -0.0129 | 0.1583 | 6/12 (3 sessions) | 0.0634 | 0.0874 | 0.0420 | 0.1055 | 0.0050 | 0.0363 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 11/31 (10 sessions) | 0.0876 | 0.0504 | 0.0060 | 0.1288 | 3/12 (1 sessions) | 0.1190 | 0.1005 | 0.0865 | 0.1424 | -0.0314 | -0.2448 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 11/31 (10 sessions) | 0.0604 | 0.0441 | -0.0193 | 0.1180 | 3/12 (1 sessions) | 0.1149 | 0.0929 | 0.0773 | 0.1414 | -0.0545 | -0.4540 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 9/31 (8 sessions) | 0.0269 | 0.0252 | -0.0349 | 0.0428 | 3/12 (1 sessions) | 0.1073 | 0.0806 | 0.0660 | 0.1353 | -0.0804 | -0.7763 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 31/31 (18 sessions) | 0.0891 | 0.0698 | 0.0171 | 0.1419 | 12/12 (6 sessions) | 0.0578 | 0.0428 | 0.0335 | 0.0758 | 0.0313 | 0.3789 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 26/31 (15 sessions) | 0.0405 | 0.0324 | -0.0031 | 0.0853 | 12/12 (6 sessions) | 0.0410 | 0.0344 | 0.0205 | 0.0591 | -0.0005 | -0.0103 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 25/31 (15 sessions) | 0.0302 | 0.0237 | 0.0112 | 0.0640 | 11/12 (6 sessions) | 0.0291 | 0.0377 | 0.0232 | 0.0472 | 0.0011 | 0.0230 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 8/31 (8 sessions) | 0.2500 | 0.0000 | 0.0000 | 0.0000 | 3/12 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.2500 | 0.4009 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 7/31 (7 sessions) | 0.7143 | 0.0000 | 0.0000 | 1.0000 | 3/12 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.7143 | 0.7412 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 4/31 (4 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | 3/12 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.5000 | 1.1180 | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 15/31 (12 sessions) | 0.4000 | 0.0000 | 0.0000 | 0.5000 | 6/12 (3 sessions) | 0.1667 | 0.0000 | 0.0000 | 0.0000 | 0.2333 | 0.3502 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 12/31 (11 sessions) | 0.6667 | 1.0000 | 0.0000 | 1.0000 | 4/12 (2 sessions) | 0.2500 | 0.0000 | 0.0000 | 0.2500 | 0.4167 | 0.6699 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 6/31 (6 sessions) | 0.8333 | 1.0000 | 1.0000 | 1.0000 | 3/12 (1 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.5000 | 0.5000 | 1.0801 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 8/31 (8 sessions) | 0.1250 | 0.0000 | 0.0000 | 0.0000 | 3/12 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1250 | 0.4009 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 7/31 (7 sessions) | 0.4286 | 0.0000 | 0.0000 | 1.0000 | 3/12 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.4286 | 0.9258 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 4/31 (4 sessions) | 0.7500 | 1.0000 | 0.7500 | 1.0000 | 3/12 (1 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.5000 | 0.4167 | 0.7828 | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 21/31 (15 sessions) | 0.5238 | 0.0000 | 0.0000 | 1.0000 | 10/12 (6 sessions) | 1.1000 | 0.5000 | 0.0000 | 1.7500 | -0.5762 | -0.5849 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 18/31 (13 sessions) | 1.3889 | 1.0000 | 0.0000 | 2.0000 | 6/12 (3 sessions) | 1.0000 | 0.5000 | 0.0000 | 1.7500 | 0.3889 | 0.2741 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 8/31 (8 sessions) | 1.5000 | 1.0000 | 1.0000 | 1.5000 | 3/12 (1 sessions) | 0.6667 | 0.0000 | 0.0000 | 1.0000 | 0.8333 | 0.6528 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 21/31 (15 sessions) | 2.3952 | 2.3400 | 1.4900 | 2.9650 | 10/12 (6 sessions) | 2.0194 | 1.8475 | 1.5412 | 2.5240 | 0.3758 | 0.3505 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 18/31 (13 sessions) | 3.2367 | 3.0885 | 2.4850 | 4.2451 | 6/12 (3 sessions) | 2.4183 | 2.4600 | 1.5950 | 2.8675 | 0.8183 | 0.6347 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 8/31 (8 sessions) | 4.2588 | 4.7400 | 2.7775 | 4.9750 | 3/12 (1 sessions) | 3.5100 | 2.7000 | 2.3850 | 4.2300 | 0.7488 | 0.3618 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 15/31 (12 sessions) | 2.2453 | 2.0989 | 1.7669 | 2.6620 | 6/12 (3 sessions) | 2.0058 | 1.7855 | 1.6600 | 2.2442 | 0.2394 | 0.3449 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 15/31 (12 sessions) | 3.3295 | 3.3100 | 2.7735 | 3.8416 | 6/12 (3 sessions) | 2.7172 | 2.9185 | 2.2442 | 3.1280 | 0.6123 | 0.6835 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 8/31 (8 sessions) | 4.9380 | 5.0952 | 3.8129 | 6.1464 | 3/12 (1 sessions) | 4.8600 | 3.9368 | 3.6933 | 5.5652 | 0.0780 | 0.0488 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 21/31 (15 sessions) | 0.4968 | 0.4577 | 0.2672 | 0.7239 | 10/12 (6 sessions) | 0.4004 | 0.4747 | 0.0500 | 0.6256 | 0.0964 | 0.3059 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 18/31 (13 sessions) | 0.2635 | 0.2301 | 0.0903 | 0.3425 | 6/12 (3 sessions) | 0.3448 | 0.3383 | 0.2709 | 0.4894 | -0.0813 | -0.3568 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 8/31 (8 sessions) | 0.2226 | 0.2092 | 0.0970 | 0.3093 | 3/12 (1 sessions) | 0.3645 | 0.2927 | 0.2845 | 0.4086 | -0.1419 | -0.8650 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 21/31 (15 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 10/12 (6 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 18/31 (13 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 6/12 (3 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 8/31 (8 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 3/12 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 21/31 (15 sessions) | 0.5238 | 0.5000 | 0.2500 | 0.7500 | 10/12 (6 sessions) | 0.4750 | 0.5000 | 0.3125 | 0.6875 | 0.0488 | 0.1962 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 18/31 (13 sessions) | 0.5000 | 0.5000 | 0.4000 | 0.6000 | 6/12 (3 sessions) | 0.6000 | 0.6500 | 0.5250 | 0.7000 | -0.1000 | -0.6268 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 8/31 (8 sessions) | 0.4943 | 0.4318 | 0.4091 | 0.6023 | 3/12 (1 sessions) | 0.5303 | 0.5455 | 0.4773 | 0.5909 | -0.0360 | -0.3308 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 15/31 (12 sessions) | 1.6220 | 1.3173 | 0.7214 | 2.0054 | 6/12 (3 sessions) | 3.0757 | 3.1552 | 1.1538 | 5.1627 | -1.4537 | -0.8413 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 15/31 (12 sessions) | 1.0540 | 0.7430 | 0.3124 | 1.1415 | 6/12 (3 sessions) | 2.4991 | 2.3814 | 0.6793 | 4.3709 | -1.4451 | -0.9255 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 12/31 (11 sessions) | 0.7984 | 0.3849 | 0.1530 | 0.7020 | 4/12 (2 sessions) | 2.8127 | 3.3326 | 2.1927 | 3.9527 | -2.0144 | -1.4297 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 27/31 (16 sessions) | 1.9954 | 1.7500 | 0.7975 | 2.7002 | 11/12 (5 sessions) | 1.4838 | 1.2000 | 0.5428 | 1.6502 | 0.5116 | 0.3180 | not resampled |
| stage11_2.room_in_atr [SMALL] | 13/31 (11 sessions) | 2.0589 | 1.8874 | 1.0308 | 3.3155 | 6/12 (3 sessions) | 1.6554 | 1.1270 | 0.3213 | 2.1560 | 0.4035 | 0.2593 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 31/31 (18 sessions) | 1.5161 | 2.0000 | 1.0000 | 2.0000 | 12/12 (6 sessions) | 1.5000 | 1.0000 | 1.0000 | 2.0000 | 0.0161 | 0.0180 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 31/31 (18 sessions) | 4.4839 | 4.0000 | 4.0000 | 5.0000 | 12/12 (6 sessions) | 4.5000 | 5.0000 | 4.0000 | 5.0000 | -0.0161 | -0.0180 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 27/31 (16 sessions) | 1.9954 | 1.7500 | 0.7975 | 2.7002 | 11/12 (5 sessions) | 1.4838 | 1.2000 | 0.5428 | 1.6502 | 0.5116 | 0.3180 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 31/31 (18 sessions) | 0.2978 | 0.1700 | 0.1150 | 0.3664 | 12/12 (6 sessions) | 0.1451 | 0.0620 | 0.0399 | 0.2250 | 0.1527 | 0.5754 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 15/31 (12 sessions) | 0.2000 | 0.0000 | 0.0000 | 0.0000 | 6/12 (3 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | -0.3000 | -0.6622 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 15/31 (12 sessions) | 0.2000 | 0.0000 | 0.0000 | 0.0000 | 6/12 (3 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | -0.3000 | -0.6622 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 19/31 (14 sessions) | 0.9333 | 0.7500 | 0.2700 | 1.3976 | 9/12 (5 sessions) | 0.6538 | 0.3405 | 0.3400 | 0.6650 | 0.2794 | 0.3803 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 19/31 (13 sessions) | 1.9406 | 1.8200 | 1.1350 | 2.7450 | 10/12 (6 sessions) | 1.5968 | 1.6350 | 1.0575 | 2.1899 | 0.3437 | 0.3250 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 15/31 (12 sessions) | 1.1855 | 0.8895 | 0.4242 | 2.0735 | 6/12 (3 sessions) | 0.7688 | 0.4709 | 0.2752 | 1.1381 | 0.4168 | 0.4652 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 15/31 (12 sessions) | 1.7467 | 1.8019 | 1.2230 | 2.2559 | 6/12 (3 sessions) | 1.7304 | 1.7894 | 1.2336 | 2.1490 | 0.0162 | 0.0184 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG | 43 | 19 | 31 | 12 | 100.00% | 100.00% | 72.09% |
| time_bucket | 09:35-10:00 [SMALL] | 12 | 11 | 10 | 2 | 32.26% | 16.67% | 83.33% |
| time_bucket | 10:00-10:30 [SMALL] | 7 | 6 | 3 | 4 | 9.68% | 33.33% | 42.86% |
| time_bucket | 10:30-11:00 [SMALL] | 5 | 3 | 4 | 1 | 12.90% | 8.33% | 80.00% |
| time_bucket | 11:00-12:00 [SMALL] | 9 | 7 | 7 | 2 | 22.58% | 16.67% | 77.78% |
| time_bucket | 12:00-13:30 [SMALL] | 3 | 3 | 3 | 0 | 9.68% | 0.00% | 100.00% |
| time_bucket | 13:30-15:00 [SMALL] | 4 | 2 | 1 | 3 | 3.23% | 25.00% | 25.00% |
| time_bucket | 15:00-close [SMALL] | 3 | 3 | 3 | 0 | 9.68% | 0.00% | 100.00% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 10 | 7 | 7 | 3 | 22.58% | 25.00% | 70.00% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 6 | 5 | 5 | 1 | 16.13% | 8.33% | 83.33% |
| ema9_20_alignment | EMA_UNAVAILABLE [SMALL] | 27 | 16 | 19 | 8 | 61.29% | 66.67% | 70.37% |
| price_vwap_alignment | VWAP_ALIGNED | 38 | 19 | 27 | 11 | 87.10% | 91.67% | 71.05% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 5 | 4 | 4 | 1 | 12.90% | 8.33% | 80.00% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED [SMALL] | 23 | 12 | 15 | 8 | 48.39% | 66.67% | 65.22% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 6 | 4 | 5 | 1 | 16.13% | 8.33% | 83.33% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 14 | 12 | 11 | 3 | 35.48% | 25.00% | 78.57% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 11 | 7 | 7 | 4 | 22.58% | 33.33% | 63.64% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 5 | 5 | 5 | 0 | 16.13% | 0.00% | 100.00% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE [SMALL] | 27 | 16 | 19 | 8 | 61.29% | 66.67% | 70.37% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 7 | 4 | 4 | 3 | 12.90% | 25.00% | 57.14% |
| prior_ema_cross | NO_PRIOR_CROSS | 33 | 17 | 24 | 9 | 77.42% | 75.00% | 72.73% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 3 | 3 | 3 | 0 | 9.68% | 0.00% | 100.00% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 31 | 15 | 22 | 9 | 70.97% | 75.00% | 70.97% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 10 | 7 | 7 | 3 | 22.58% | 25.00% | 70.00% |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 2 | 2 | 2 | 0 | 6.45% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 1 | 1 | 1 | 0 | 3.23% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 5 | 4 | 4 | 1 | 12.90% | 8.33% | 80.00% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 2 | 2 | 1 | 1 | 3.23% | 8.33% | 50.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 5 | 4 | 4 | 1 | 12.90% | 8.33% | 80.00% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 6 | 3 | 3 | 3 | 9.68% | 25.00% | 50.00% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 5 | 3 | 4 | 1 | 12.90% | 8.33% | 80.00% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 19 | 13 | 14 | 5 | 45.16% | 41.67% | 73.68% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 43 | 19 | 31 | 12 | 100.00% | 100.00% | 72.09% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 1 | 1 | 1 | 0 | 3.23% | 0.00% | 100.00% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 11 | 7 | 7 | 4 | 22.58% | 33.33% | 63.64% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 7 | 7 | 5 | 2 | 16.13% | 16.67% | 71.43% |
| stage11_3.structure | UNAVAILABLE [SMALL] | 24 | 16 | 18 | 6 | 58.06% | 50.00% | 75.00% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 11 | 7 | 7 | 4 | 22.58% | 33.33% | 63.64% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 8 | 7 | 6 | 2 | 19.35% | 16.67% | 75.00% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE [SMALL] | 24 | 16 | 18 | 6 | 58.06% | 50.00% | 75.00% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 13 | 9 | 9 | 4 | 29.03% | 33.33% | 69.23% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 7 | 6 | 5 | 2 | 16.13% | 16.67% | 71.43% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 23 | 16 | 17 | 6 | 54.84% | 50.00% | 73.91% |
| stage11_3.low_structure | EQUAL_LOW [SMALL] | 1 | 1 | 1 | 0 | 3.23% | 0.00% | 100.00% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 17 | 10 | 11 | 6 | 35.48% | 50.00% | 64.71% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 2 | 2 | 2 | 0 | 6.45% | 0.00% | 100.00% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 23 | 15 | 17 | 6 | 54.84% | 50.00% | 73.91% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 15 | 14 | 12 | 3 | 38.71% | 25.00% | 80.00% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 2 | 1 | 2 | 0 | 6.45% | 0.00% | 100.00% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 3 | 3 | 3 | 0 | 9.68% | 0.00% | 100.00% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 23 | 12 | 14 | 9 | 45.16% | 75.00% | 60.87% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 43 | 19 | 31 | 12 | 100.00% | 100.00% | 72.09% |


### 2026-08


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 29/29 (13 sessions) | 1.2142 | 1.1200 | 1.0000 | 1.3200 | 13/13 (8 sessions) | 1.4011 | 1.3200 | 1.2400 | 1.6500 | -0.1870 | -0.5546 | not resampled |
| body_size [SMALL] | 29/29 (13 sessions) | 0.5606 | 0.5000 | 0.2700 | 0.7700 | 13/13 (8 sessions) | 0.4206 | 0.3450 | 0.2100 | 0.5050 | 0.1401 | 0.3883 | not resampled |
| directional_body [SMALL] | 29/29 (13 sessions) | 0.5606 | 0.5000 | 0.2700 | 0.7700 | 13/13 (8 sessions) | 0.4206 | 0.3450 | 0.2100 | 0.5050 | 0.1401 | 0.3883 | not resampled |
| candle_range [SMALL] | 29/29 (13 sessions) | 0.8111 | 0.7100 | 0.5450 | 1.1100 | 13/13 (8 sessions) | 0.7054 | 0.6600 | 0.6400 | 0.7150 | 0.1057 | 0.2862 | not resampled |
| body_range_ratio [SMALL] | 29/29 (13 sessions) | 0.6742 | 0.7152 | 0.5833 | 0.8000 | 13/13 (8 sessions) | 0.5574 | 0.6515 | 0.3125 | 0.6989 | 0.1168 | 0.5526 | not resampled |
| directional_body_range_ratio [SMALL] | 29/29 (13 sessions) | 0.6742 | 0.7152 | 0.5833 | 0.8000 | 13/13 (8 sessions) | 0.5574 | 0.6515 | 0.3125 | 0.6989 | 0.1168 | 0.5526 | not resampled |
| close_location [SMALL] | 29/29 (13 sessions) | 0.8284 | 0.8444 | 0.7595 | 0.9173 | 13/13 (8 sessions) | 0.8074 | 0.8696 | 0.7429 | 0.9169 | 0.0211 | 0.1373 | not resampled |
| directional_close_location [SMALL] | 29/29 (13 sessions) | 0.8284 | 0.8444 | 0.7595 | 0.9173 | 13/13 (8 sessions) | 0.8074 | 0.8696 | 0.7429 | 0.9169 | 0.0211 | 0.1373 | not resampled |
| distance_beyond_level [SMALL] | 29/29 (13 sessions) | 0.3038 | 0.2400 | 0.1100 | 0.4099 | 13/13 (8 sessions) | 0.1317 | 0.0800 | 0.0501 | 0.1600 | 0.1721 | 0.8509 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 17/29 (8 sessions) | 0.4241 | 0.4180 | 0.2080 | 0.5629 | 9/13 (6 sessions) | 0.1622 | 0.1384 | 0.1331 | 0.2141 | 0.2619 | 1.0966 | not resampled |
| candle_volume [SMALL] | 29/29 (13 sessions) | 554092.0690 | 372898.0000 | 267824.0000 | 510255.0000 | 13/13 (8 sessions) | 478394.2308 | 437699.0000 | 258262.0000 | 717218.0000 | 75697.8382 | 0.1456 | not resampled |
| relative_volume_prior_6 [SMALL] | 21/29 (10 sessions) | 1.3762 | 1.0266 | 0.7129 | 1.3064 | 10/13 (6 sessions) | 1.2771 | 1.1365 | 0.6629 | 1.5710 | 0.0991 | 0.0683 | not resampled |
| atr14 [SMALL] | 17/29 (8 sessions) | 0.5996 | 0.5818 | 0.5456 | 0.6302 | 9/13 (6 sessions) | 0.6140 | 0.6012 | 0.5447 | 0.6542 | -0.0144 | -0.0736 | not resampled |
| minutes_since_open [SMALL] | 29/29 (13 sessions) | 118.2759 | 90.0000 | 20.0000 | 170.0000 | 13/13 (8 sessions) | 120.3846 | 95.0000 | 65.0000 | 135.0000 | -2.1088 | -0.0199 | not resampled |
| minutes_since_ema_cross [SMALL] | 7/29 (6 sessions) | 67.1429 | 50.0000 | 42.5000 | 92.5000 | 4/13 (3 sessions) | 38.7500 | 27.5000 | 16.2500 | 50.0000 | 28.3929 | 0.6090 | not resampled |
| break_attempt_rank [SMALL] | 29/29 (13 sessions) | 5.6552 | 6.0000 | 2.0000 | 8.0000 | 13/13 (8 sessions) | 5.4615 | 5.0000 | 4.0000 | 6.0000 | 0.1936 | 0.0516 | not resampled |
| valid_hold_sequence_rank [SMALL] | 29/29 (13 sessions) | 3.4828 | 4.0000 | 1.0000 | 5.0000 | 13/13 (8 sessions) | 3.4615 | 3.0000 | 2.0000 | 4.0000 | 0.0212 | 0.0093 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 14/29 (7 sessions) | 0.2100 | 0.1579 | 0.1190 | 0.2503 | 5/13 (4 sessions) | 0.1161 | 0.0339 | 0.0204 | 0.1162 | 0.0939 | 0.5975 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 14/29 (7 sessions) | 0.3867 | 0.3560 | 0.2049 | 0.5026 | 5/13 (4 sessions) | 0.2256 | 0.0619 | 0.0375 | 0.3495 | 0.1611 | 0.6277 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 20/29 (10 sessions) | 0.0737 | 0.0661 | 0.0339 | 0.1263 | 10/13 (6 sessions) | 0.0803 | 0.0907 | 0.0002 | 0.1323 | -0.0066 | -0.0736 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 18/29 (9 sessions) | 0.0202 | 0.0274 | -0.0222 | 0.0480 | 10/13 (6 sessions) | 0.0496 | 0.0542 | -0.0326 | 0.1180 | -0.0294 | -0.3340 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 18/29 (9 sessions) | 0.0049 | 0.0003 | -0.0349 | 0.0343 | 10/13 (6 sessions) | 0.0285 | 0.0141 | -0.0302 | 0.0829 | -0.0236 | -0.3129 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 14/29 (7 sessions) | 0.0274 | 0.0284 | 0.0035 | 0.0460 | 5/13 (4 sessions) | 0.0436 | 0.0392 | 0.0077 | 0.0558 | -0.0163 | -0.3154 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 13/29 (7 sessions) | 0.0095 | 0.0093 | -0.0064 | 0.0305 | 5/13 (4 sessions) | 0.0295 | 0.0292 | -0.0113 | 0.0426 | -0.0201 | -0.3818 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 13/29 (7 sessions) | 0.0035 | 0.0099 | -0.0254 | 0.0274 | 5/13 (4 sessions) | 0.0236 | 0.0292 | -0.0129 | 0.0310 | -0.0202 | -0.4071 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 29/29 (13 sessions) | 0.0921 | 0.0122 | 0.0051 | 0.1501 | 13/13 (8 sessions) | 0.0564 | 0.0088 | -0.0001 | 0.1037 | 0.0357 | 0.2705 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 25/29 (12 sessions) | 0.0246 | 0.0068 | -0.0037 | 0.0322 | 12/13 (7 sessions) | 0.0284 | 0.0035 | -0.0039 | 0.0388 | -0.0038 | -0.0747 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 23/29 (12 sessions) | 0.0170 | 0.0047 | -0.0070 | 0.0227 | 11/13 (7 sessions) | 0.0212 | 0.0047 | 0.0006 | 0.0187 | -0.0042 | -0.0925 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 13/29 (7 sessions) | 0.1538 | 0.0000 | 0.0000 | 0.0000 | 4/13 (3 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | -0.3462 | -0.6189 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 10/29 (6 sessions) | 0.3000 | 0.0000 | 0.0000 | 0.7500 | 3/13 (2 sessions) | 1.0000 | 1.0000 | 0.5000 | 1.5000 | -0.7000 | -1.1466 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 4/29 (3 sessions) | 0.7500 | 1.0000 | 0.7500 | 1.0000 | 2/13 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | -0.2500 | -0.5774 | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 17/29 (8 sessions) | 0.3529 | 0.0000 | 0.0000 | 1.0000 | 9/13 (6 sessions) | 0.5556 | 1.0000 | 0.0000 | 1.0000 | -0.2026 | -0.3487 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 14/29 (7 sessions) | 0.9286 | 1.0000 | 0.0000 | 1.0000 | 5/13 (4 sessions) | 0.8000 | 1.0000 | 1.0000 | 1.0000 | 0.1286 | 0.1548 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 8/29 (4 sessions) | 2.0000 | 1.5000 | 1.0000 | 3.0000 | 2/13 (1 sessions) | 1.5000 | 1.5000 | 1.2500 | 1.7500 | 0.5000 | 0.3288 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 13/29 (7 sessions) | 0.4615 | 0.0000 | 0.0000 | 1.0000 | 4/13 (3 sessions) | 0.7500 | 1.0000 | 0.7500 | 1.0000 | -0.2885 | -0.4568 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 10/29 (6 sessions) | 0.8000 | 1.0000 | 0.2500 | 1.0000 | 3/13 (2 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | -0.2000 | -0.3496 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 4/29 (3 sessions) | 1.2500 | 1.0000 | 1.0000 | 1.2500 | 2/13 (1 sessions) | 1.5000 | 1.5000 | 1.2500 | 1.7500 | -0.2500 | -0.4472 | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 21/29 (10 sessions) | 0.9524 | 1.0000 | 0.0000 | 2.0000 | 10/13 (6 sessions) | 1.3000 | 1.0000 | 1.0000 | 2.0000 | -0.3476 | -0.3256 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 18/29 (9 sessions) | 2.1667 | 2.0000 | 0.2500 | 3.0000 | 10/13 (6 sessions) | 2.3000 | 2.0000 | 1.0000 | 3.7500 | -0.1333 | -0.0685 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 13/29 (7 sessions) | 3.8462 | 4.0000 | 1.0000 | 6.0000 | 5/13 (4 sessions) | 2.8000 | 3.0000 | 2.0000 | 3.0000 | 1.0462 | 0.4133 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 21/29 (10 sessions) | 1.3557 | 1.1600 | 0.9900 | 1.7400 | 10/13 (6 sessions) | 1.4220 | 1.4800 | 1.0650 | 1.7475 | -0.0663 | -0.1154 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 18/29 (9 sessions) | 1.9260 | 2.0500 | 1.3762 | 2.2625 | 10/13 (6 sessions) | 1.9345 | 2.0150 | 1.5975 | 2.2638 | -0.0085 | -0.0126 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 13/29 (7 sessions) | 2.6040 | 2.3200 | 2.0400 | 3.6350 | 5/13 (4 sessions) | 2.0730 | 2.2800 | 1.4700 | 2.5500 | 0.5310 | 0.6428 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 17/29 (8 sessions) | 1.9701 | 1.8485 | 1.6682 | 2.1265 | 9/13 (6 sessions) | 2.3207 | 1.9325 | 1.7293 | 2.8942 | -0.3506 | -0.6392 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 17/29 (8 sessions) | 3.0630 | 3.0998 | 2.4542 | 3.5150 | 9/13 (6 sessions) | 3.2326 | 3.3402 | 2.8291 | 3.4697 | -0.1696 | -0.2272 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 13/29 (7 sessions) | 4.7809 | 4.7537 | 3.8409 | 5.6899 | 5/13 (4 sessions) | 4.3174 | 4.2821 | 4.1615 | 4.5371 | 0.4635 | 0.5404 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 21/29 (10 sessions) | 0.4166 | 0.3608 | 0.2513 | 0.5584 | 10/13 (6 sessions) | 0.4792 | 0.3767 | 0.1570 | 0.8932 | -0.0626 | -0.1968 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 18/29 (9 sessions) | 0.2487 | 0.1873 | 0.1200 | 0.3593 | 10/13 (6 sessions) | 0.3017 | 0.3094 | 0.1360 | 0.3750 | -0.0530 | -0.2557 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 13/29 (7 sessions) | 0.1947 | 0.1810 | 0.0987 | 0.2340 | 5/13 (4 sessions) | 0.1432 | 0.1160 | 0.0296 | 0.1168 | 0.0516 | 0.3578 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 21/29 (10 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 10/13 (6 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 18/29 (9 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 10/13 (6 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 13/29 (7 sessions) | 0.9933 | 1.0000 | 1.0000 | 1.0000 | 5/13 (4 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | -0.0067 | -0.4730 | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 21/29 (10 sessions) | 0.5119 | 0.5000 | 0.2500 | 0.7500 | 10/13 (6 sessions) | 0.3750 | 0.5000 | 0.0625 | 0.5000 | 0.1369 | 0.5258 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 18/29 (9 sessions) | 0.4667 | 0.5000 | 0.3250 | 0.6000 | 10/13 (6 sessions) | 0.3800 | 0.3500 | 0.3000 | 0.5000 | 0.0867 | 0.4568 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 13/29 (7 sessions) | 0.4231 | 0.4091 | 0.3636 | 0.5455 | 5/13 (4 sessions) | 0.3727 | 0.3636 | 0.3182 | 0.4091 | 0.0503 | 0.4790 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 17/29 (8 sessions) | 1.0806 | 0.9473 | 0.7681 | 1.3709 | 9/13 (6 sessions) | 0.8991 | 0.5050 | 0.0857 | 1.3251 | 0.1815 | 0.2450 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 17/29 (8 sessions) | 0.6941 | 0.5788 | 0.2733 | 1.1016 | 9/13 (6 sessions) | 0.3094 | 0.2298 | 0.0270 | 0.3653 | 0.3848 | 0.7865 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 14/29 (7 sessions) | 0.4284 | 0.4180 | 0.0331 | 0.8036 | 5/13 (4 sessions) | 0.2097 | 0.1865 | 0.0696 | 0.2191 | 0.2186 | 0.6403 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 25/29 (10 sessions) | 0.5804 | 0.5200 | 0.2150 | 0.6800 | 12/13 (7 sessions) | 0.8231 | 0.7188 | 0.6025 | 1.0012 | -0.2427 | -0.4984 | not resampled |
| stage11_2.room_in_atr [SMALL] | 16/29 (7 sessions) | 0.9892 | 0.7895 | 0.5697 | 1.0710 | 9/13 (6 sessions) | 1.3157 | 0.9459 | 0.8617 | 1.9007 | -0.3265 | -0.3543 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 29/29 (13 sessions) | 1.5862 | 2.0000 | 1.0000 | 2.0000 | 13/13 (8 sessions) | 1.7692 | 2.0000 | 2.0000 | 2.0000 | -0.1830 | -0.2299 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 29/29 (13 sessions) | 4.3793 | 4.0000 | 4.0000 | 5.0000 | 13/13 (8 sessions) | 4.2308 | 4.0000 | 4.0000 | 4.0000 | 0.1485 | 0.1874 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 25/29 (10 sessions) | 0.5804 | 0.5200 | 0.2150 | 0.6800 | 12/13 (7 sessions) | 0.8231 | 0.7188 | 0.6025 | 1.0012 | -0.2427 | -0.4984 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 29/29 (13 sessions) | 0.2791 | 0.2000 | 0.1100 | 0.4000 | 13/13 (8 sessions) | 0.1317 | 0.0800 | 0.0501 | 0.1600 | 0.1474 | 0.7455 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 17/29 (8 sessions) | 0.2353 | 0.0000 | 0.0000 | 0.0000 | 9/13 (6 sessions) | 0.2222 | 0.0000 | 0.0000 | 0.0000 | 0.0131 | 0.0298 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 17/29 (8 sessions) | 0.5882 | 1.0000 | 0.0000 | 1.0000 | 9/13 (6 sessions) | 0.5556 | 1.0000 | 0.0000 | 1.0000 | 0.0327 | 0.0636 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 20/29 (10 sessions) | 0.5103 | 0.4750 | 0.1125 | 0.6625 | 10/13 (6 sessions) | 0.6117 | 0.6012 | 0.2650 | 0.8038 | -0.1015 | -0.2418 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 20/29 (10 sessions) | 0.9762 | 0.9000 | 0.5100 | 1.2200 | 8/13 (5 sessions) | 1.1897 | 1.1388 | 0.4325 | 1.8638 | -0.2135 | -0.3095 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 17/29 (8 sessions) | 0.8970 | 0.7166 | 0.3521 | 1.5297 | 9/13 (6 sessions) | 0.9861 | 0.9166 | 0.4959 | 1.1316 | -0.0892 | -0.1221 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 17/29 (8 sessions) | 1.3719 | 1.4964 | 1.1124 | 1.7135 | 8/13 (5 sessions) | 2.1778 | 2.4683 | 0.7932 | 3.3424 | -0.8058 | -0.8445 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG | 42 | 13 | 29 | 13 | 100.00% | 100.00% | 69.05% |
| time_bucket | 09:35-10:00 [SMALL] | 11 | 9 | 8 | 3 | 27.59% | 23.08% | 72.73% |
| time_bucket | 10:00-10:30 [SMALL] | 3 | 3 | 3 | 0 | 10.34% | 0.00% | 100.00% |
| time_bucket | 10:30-11:00 [SMALL] | 4 | 4 | 2 | 2 | 6.90% | 15.38% | 50.00% |
| time_bucket | 11:00-12:00 [SMALL] | 11 | 5 | 6 | 5 | 20.69% | 38.46% | 54.55% |
| time_bucket | 12:00-13:30 [SMALL] | 7 | 4 | 6 | 1 | 20.69% | 7.69% | 85.71% |
| time_bucket | 13:30-15:00 [SMALL] | 2 | 2 | 2 | 0 | 6.90% | 0.00% | 100.00% |
| time_bucket | 15:00-close [SMALL] | 4 | 2 | 2 | 2 | 6.90% | 15.38% | 50.00% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 12 | 5 | 10 | 2 | 34.48% | 15.38% | 83.33% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 7 | 5 | 4 | 3 | 13.79% | 23.08% | 57.14% |
| ema9_20_alignment | EMA_UNAVAILABLE [SMALL] | 23 | 12 | 15 | 8 | 51.72% | 61.54% | 65.22% |
| price_vwap_alignment | VWAP_ALIGNED | 37 | 13 | 26 | 11 | 89.66% | 84.62% | 70.27% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 5 | 4 | 3 | 2 | 10.34% | 15.38% | 60.00% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED [SMALL] | 21 | 10 | 15 | 6 | 51.72% | 46.15% | 71.43% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 9 | 7 | 5 | 4 | 17.24% | 30.77% | 55.56% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 12 | 10 | 9 | 3 | 31.03% | 23.08% | 75.00% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 11 | 5 | 8 | 3 | 27.59% | 23.08% | 72.73% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 8 | 5 | 6 | 2 | 20.69% | 15.38% | 75.00% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE [SMALL] | 23 | 12 | 15 | 8 | 51.72% | 61.54% | 65.22% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 6 | 4 | 4 | 2 | 13.79% | 15.38% | 66.67% |
| prior_ema_cross | NO_PRIOR_CROSS | 31 | 12 | 22 | 9 | 75.86% | 69.23% | 70.97% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 5 | 4 | 3 | 2 | 10.34% | 15.38% | 60.00% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE [SMALL] | 24 | 8 | 17 | 7 | 58.62% | 53.85% | 70.83% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 18 | 9 | 12 | 6 | 41.38% | 46.15% | 66.67% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 9 | 5 | 6 | 3 | 20.69% | 23.08% | 66.67% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 4 | 4 | 3 | 1 | 10.34% | 7.69% | 75.00% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 4 | 2 | 2 | 2 | 6.90% | 15.38% | 50.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 2 | 1 | 1 | 1 | 3.45% | 7.69% | 50.00% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 6 | 3 | 4 | 2 | 13.79% | 15.38% | 66.67% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 5 | 3 | 4 | 1 | 13.79% | 7.69% | 80.00% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 12 | 7 | 9 | 3 | 31.03% | 23.08% | 75.00% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 42 | 13 | 29 | 13 | 100.00% | 100.00% | 69.05% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 3 | 2 | 1 | 2 | 3.45% | 15.38% | 33.33% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 9 | 7 | 7 | 2 | 24.14% | 15.38% | 77.78% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 9 | 5 | 6 | 3 | 20.69% | 23.08% | 66.67% |
| stage11_3.structure | UNAVAILABLE [SMALL] | 21 | 11 | 15 | 6 | 51.72% | 46.15% | 71.43% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 9 | 7 | 7 | 2 | 24.14% | 15.38% | 77.78% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 12 | 5 | 7 | 5 | 24.14% | 38.46% | 58.33% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE [SMALL] | 21 | 11 | 15 | 6 | 51.72% | 46.15% | 71.43% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 18 | 8 | 11 | 7 | 37.93% | 53.85% | 61.11% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 9 | 6 | 6 | 3 | 20.69% | 23.08% | 66.67% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 15 | 11 | 12 | 3 | 41.38% | 23.08% | 80.00% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 12 | 7 | 10 | 2 | 34.48% | 15.38% | 83.33% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 10 | 5 | 5 | 5 | 17.24% | 38.46% | 50.00% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 20 | 10 | 14 | 6 | 48.28% | 46.15% | 70.00% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 12 | 10 | 9 | 3 | 31.03% | 23.08% | 75.00% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 1 | 1 | 1 | 0 | 3.45% | 0.00% | 100.00% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 13 | 6 | 8 | 5 | 27.59% | 38.46% | 61.54% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 16 | 9 | 11 | 5 | 37.93% | 38.46% | 68.75% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 42 | 13 | 29 | 13 | 100.00% | 100.00% | 69.05% |


### 2026-09 — PARTIAL / SMALL


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 4/4 (3 sessions) | 1.1299 | 1.1772 | 0.9221 | 1.3850 | 4/4 (2 sessions) | 0.9221 | 0.9695 | 0.9221 | 0.9695 | 0.2078 | 0.9211 | not resampled |
| body_size [SMALL] | 4/4 (3 sessions) | 0.5438 | 0.6325 | 0.4912 | 0.6850 | 4/4 (2 sessions) | 0.3625 | 0.3550 | 0.3225 | 0.3950 | 0.1812 | 0.8824 | not resampled |
| directional_body [SMALL] | 4/4 (3 sessions) | 0.5438 | 0.6325 | 0.4912 | 0.6850 | 4/4 (2 sessions) | 0.3625 | 0.3550 | 0.3225 | 0.3950 | 0.1812 | 0.8824 | not resampled |
| candle_range [SMALL] | 4/4 (3 sessions) | 1.2188 | 1.0875 | 0.8688 | 1.4375 | 4/4 (2 sessions) | 0.5300 | 0.5300 | 0.5125 | 0.5475 | 0.6888 | 1.9936 | not resampled |
| body_range_ratio [SMALL] | 4/4 (3 sessions) | 0.4517 | 0.4701 | 0.3090 | 0.6128 | 4/4 (2 sessions) | 0.6840 | 0.6744 | 0.5759 | 0.7825 | -0.2324 | -1.0943 | not resampled |
| directional_body_range_ratio [SMALL] | 4/4 (3 sessions) | 0.4517 | 0.4701 | 0.3090 | 0.6128 | 4/4 (2 sessions) | 0.6840 | 0.6744 | 0.5759 | 0.7825 | -0.2324 | -1.0943 | not resampled |
| close_location [SMALL] | 4/4 (3 sessions) | 0.8609 | 0.9596 | 0.8404 | 0.9801 | 4/4 (2 sessions) | 0.9113 | 0.9552 | 0.8942 | 0.9722 | -0.0504 | -0.2791 | not resampled |
| directional_close_location [SMALL] | 4/4 (3 sessions) | 0.8609 | 0.9596 | 0.8404 | 0.9801 | 4/4 (2 sessions) | 0.9113 | 0.9552 | 0.8942 | 0.9722 | -0.0504 | -0.2791 | not resampled |
| distance_beyond_level [SMALL] | 4/4 (3 sessions) | 0.2789 | 0.2700 | 0.0414 | 0.5075 | 4/4 (2 sessions) | 0.1329 | 0.0955 | 0.0680 | 0.1604 | 0.1460 | 0.6949 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 1/4 (1 sessions) | 0.0517 | 0.0517 | 0.0517 | 0.0517 | 2/4 (1 sessions) | 0.1716 | 0.1716 | 0.1475 | 0.1958 | -0.1199 | N/A | not resampled |
| candle_volume [SMALL] | 4/4 (3 sessions) | 628703.2500 | 594765.5000 | 404226.2500 | 819242.5000 | 4/4 (2 sessions) | 391830.5000 | 394499.5000 | 281751.5000 | 504578.5000 | 236872.7500 | 0.9799 | not resampled |
| relative_volume_prior_6 [SMALL] | 2/4 (2 sessions) | 2.2622 | 2.2622 | 1.4964 | 3.0280 | 2/4 (1 sessions) | 0.6893 | 0.6893 | 0.6599 | 0.7188 | 1.5728 | 1.0262 | not resampled |
| atr14 [SMALL] | 1/4 (1 sessions) | 0.8697 | 0.8697 | 0.8697 | 0.8697 | 2/4 (1 sessions) | 0.5598 | 0.5598 | 0.5539 | 0.5657 | 0.3100 | N/A | not resampled |
| minutes_since_open [SMALL] | 4/4 (3 sessions) | 41.2500 | 32.5000 | 25.0000 | 48.7500 | 4/4 (2 sessions) | 108.7500 | 105.0000 | 18.7500 | 195.0000 | -67.5000 | -0.8591 | not resampled |
| minutes_since_ema_cross [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | 20.0000 | 20.0000 | 15.0000 | 25.0000 | N/A | N/A | not resampled |
| break_attempt_rank [SMALL] | 4/4 (3 sessions) | 3.5000 | 3.5000 | 2.5000 | 4.5000 | 4/4 (2 sessions) | 3.2500 | 3.0000 | 2.0000 | 4.2500 | 0.2500 | 0.1378 | not resampled |
| valid_hold_sequence_rank [SMALL] | 4/4 (3 sessions) | 2.0000 | 2.0000 | 1.7500 | 2.2500 | 4/4 (2 sessions) | 2.2500 | 2.0000 | 1.0000 | 3.2500 | -0.2500 | -0.2070 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | 0.3756 | 0.3756 | 0.3467 | 0.4045 | N/A | N/A | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | 0.6734 | 0.6734 | 0.6147 | 0.7322 | N/A | N/A | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 1/4 (1 sessions) | 0.1414 | 0.1414 | 0.1414 | 0.1414 | 2/4 (1 sessions) | -0.0950 | -0.0950 | -0.1305 | -0.0595 | 0.2364 | N/A | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 1/4 (1 sessions) | 0.0753 | 0.0753 | 0.0753 | 0.0753 | 2/4 (1 sessions) | -0.1625 | -0.1625 | -0.2065 | -0.1185 | 0.2378 | N/A | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 1/4 (1 sessions) | 0.0632 | 0.0632 | 0.0632 | 0.0632 | 2/4 (1 sessions) | -0.1659 | -0.1659 | -0.2012 | -0.1305 | 0.2291 | N/A | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | -0.0795 | -0.0795 | -0.0914 | -0.0676 | N/A | N/A | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | -0.1072 | -0.1072 | -0.1214 | -0.0929 | N/A | N/A | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | -0.1049 | -0.1049 | -0.1139 | -0.0960 | N/A | N/A | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 4/4 (3 sessions) | 0.0711 | 0.0406 | 0.0189 | 0.0928 | 4/4 (2 sessions) | 0.0340 | 0.0136 | -0.0136 | 0.0612 | 0.0370 | 0.4173 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 3/4 (3 sessions) | 0.0093 | 0.0155 | 0.0007 | 0.0210 | 4/4 (2 sessions) | 0.0109 | 0.0053 | -0.0173 | 0.0335 | -0.0016 | -0.0437 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 3/4 (3 sessions) | 0.0058 | 0.0151 | 0.0010 | 0.0152 | 3/4 (1 sessions) | -0.0021 | -0.0125 | -0.0208 | 0.0113 | 0.0079 | 0.3021 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | 0.5000 | 0.5000 | 0.2500 | 0.7500 | N/A | N/A | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | N/A | N/A | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | N/A | N/A | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 1/4 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 2/4 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | -1.0000 | N/A | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | N/A | N/A | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | N/A | N/A | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | 0.5000 | 0.5000 | 0.2500 | 0.7500 | N/A | N/A | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | 0.5000 | 0.5000 | 0.2500 | 0.7500 | N/A | N/A | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | N/A | N/A | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 3/4 (3 sessions) | 2.0000 | 2.0000 | 1.5000 | 2.5000 | 2/4 (1 sessions) | 0.5000 | 0.5000 | 0.2500 | 0.7500 | 1.5000 | 1.6432 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 1/4 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 2/4 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | 3.0000 | 3.0000 | 3.0000 | 3.0000 | N/A | N/A | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 3/4 (3 sessions) | 1.4483 | 1.3350 | 1.2325 | 1.6075 | 2/4 (1 sessions) | 1.7850 | 1.7850 | 1.4175 | 2.1525 | -0.3367 | -0.4962 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 1/4 (1 sessions) | 2.1200 | 2.1200 | 2.1200 | 2.1200 | 2/4 (1 sessions) | 2.9250 | 2.9250 | 2.8425 | 3.0075 | -0.8050 | N/A | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | 3.0900 | 3.0900 | 3.0900 | 3.0900 | N/A | N/A | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 1/4 (1 sessions) | 2.1616 | 2.1616 | 2.1616 | 2.1616 | 2/4 (1 sessions) | 3.1625 | 3.1625 | 2.5394 | 3.7856 | -1.0009 | N/A | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 1/4 (1 sessions) | 2.4375 | 2.4375 | 2.4375 | 2.4375 | 2/4 (1 sessions) | 5.2214 | 5.2214 | 5.1292 | 5.3137 | -2.7839 | N/A | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | 5.5226 | 5.5226 | 5.4642 | 5.5809 | N/A | N/A | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 3/4 (3 sessions) | 0.5090 | 0.3390 | 0.3322 | 0.6008 | 2/4 (1 sessions) | 0.4457 | 0.4457 | 0.3858 | 0.5057 | 0.0633 | 0.2356 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 1/4 (1 sessions) | 0.2943 | 0.2943 | 0.2943 | 0.2943 | 2/4 (1 sessions) | 0.5064 | 0.5064 | 0.4868 | 0.5261 | -0.2121 | N/A | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | 0.2141 | 0.2141 | 0.1709 | 0.2572 | N/A | N/A | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 3/4 (3 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 2/4 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 1/4 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 2/4 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | N/A | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 3/4 (3 sessions) | 0.5000 | 0.5000 | 0.5000 | 0.5000 | 2/4 (1 sessions) | 0.6250 | 0.6250 | 0.4375 | 0.8125 | -0.1250 | -0.4082 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 1/4 (1 sessions) | 0.5000 | 0.5000 | 0.5000 | 0.5000 | 2/4 (1 sessions) | 0.3500 | 0.3500 | 0.2750 | 0.4250 | 0.1500 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | 0.2273 | 0.2273 | 0.1818 | 0.2727 | N/A | N/A | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 1/4 (1 sessions) | 0.4638 | 0.4638 | 0.4638 | 0.4638 | 2/4 (1 sessions) | 1.3347 | 1.3347 | 1.2996 | 1.3699 | -0.8710 | N/A | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 1/4 (1 sessions) | 0.1864 | 0.1864 | 0.1864 | 0.1864 | 2/4 (1 sessions) | 0.6665 | 0.6665 | 0.4550 | 0.8779 | -0.4800 | N/A | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | 0.3054 | 0.3054 | 0.3019 | 0.3089 | N/A | N/A | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 2/4 (2 sessions) | 1.3700 | 1.3700 | 0.7825 | 1.9575 | 4/4 (2 sessions) | 1.9838 | 2.4800 | 1.9562 | 2.5075 | -0.6138 | -0.5071 | not resampled |
| stage11_2.room_in_atr [SMALL] | 0/4 (0 sessions) | N/A | N/A | N/A | N/A | 2/4 (1 sessions) | 4.4314 | 4.4314 | 4.4069 | 4.4559 | N/A | N/A | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 4/4 (3 sessions) | 1.2500 | 1.0000 | 0.0000 | 2.2500 | 4/4 (2 sessions) | 2.7500 | 3.0000 | 2.7500 | 3.0000 | -1.5000 | -1.3416 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 4/4 (3 sessions) | 4.7500 | 5.0000 | 3.7500 | 6.0000 | 4/4 (2 sessions) | 3.2500 | 3.0000 | 3.0000 | 3.2500 | 1.5000 | 1.3416 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 2/4 (2 sessions) | 1.3700 | 1.3700 | 0.7825 | 1.9575 | 4/4 (2 sessions) | 1.9838 | 2.4800 | 1.9562 | 2.5075 | -0.6138 | -0.5071 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 4/4 (3 sessions) | 0.2789 | 0.2700 | 0.0414 | 0.5075 | 4/4 (2 sessions) | 0.1329 | 0.0955 | 0.0680 | 0.1604 | 0.1460 | 0.6949 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 1/4 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 2/4 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 1/4 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 2/4 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 1/4 (1 sessions) | 0.2100 | 0.2100 | 0.2100 | 0.2100 | 2/4 (1 sessions) | 2.4350 | 2.4350 | 2.4225 | 2.4475 | -2.2250 | N/A | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 1/4 (1 sessions) | 1.4500 | 1.4500 | 1.4500 | 1.4500 | 2/4 (1 sessions) | 0.5400 | 0.5400 | 0.5000 | 0.5800 | 0.9100 | N/A | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 1/4 (1 sessions) | 0.2415 | 0.2415 | 0.2415 | 0.2415 | 2/4 (1 sessions) | 4.3510 | 4.3510 | 4.3274 | 4.3746 | -4.1095 | N/A | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 1/4 (1 sessions) | 1.6672 | 1.6672 | 1.6672 | 1.6672 | 2/4 (1 sessions) | 0.9681 | 0.9681 | 0.8864 | 1.0498 | 0.6990 | N/A | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | LONG [SMALL] | 8 | 3 | 4 | 4 | 100.00% | 100.00% | 50.00% |
| time_bucket | 09:35-10:00 [SMALL] | 3 | 3 | 1 | 2 | 25.00% | 50.00% | 33.33% |
| time_bucket | 10:00-10:30 [SMALL] | 2 | 2 | 2 | 0 | 50.00% | 0.00% | 100.00% |
| time_bucket | 11:00-12:00 [SMALL] | 1 | 1 | 1 | 0 | 25.00% | 0.00% | 100.00% |
| time_bucket | 12:00-13:30 [SMALL] | 2 | 1 | 0 | 2 | 0.00% | 50.00% | 0.00% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 2 | 1 | 0 | 2 | 0.00% | 50.00% | 0.00% |
| ema9_20_alignment | EMA_UNAVAILABLE [SMALL] | 6 | 3 | 4 | 2 | 100.00% | 50.00% | 66.67% |
| price_vwap_alignment | VWAP_ALIGNED [SMALL] | 6 | 3 | 4 | 2 | 100.00% | 50.00% | 66.67% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 2 | 1 | 0 | 2 | 0.00% | 50.00% | 0.00% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 3 | 2 | 1 | 2 | 25.00% | 50.00% | 33.33% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 5 | 3 | 3 | 2 | 75.00% | 50.00% | 60.00% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 1 | 1 | 0 | 1 | 0.00% | 25.00% | 0.00% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 1 | 1 | 0 | 1 | 0.00% | 25.00% | 0.00% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE [SMALL] | 6 | 3 | 4 | 2 | 100.00% | 50.00% | 66.67% |
| prior_ema_cross | NO_PRIOR_CROSS [SMALL] | 6 | 3 | 4 | 2 | 100.00% | 50.00% | 66.67% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 2 | 1 | 0 | 2 | 0.00% | 50.00% | 0.00% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE [SMALL] | 3 | 2 | 2 | 1 | 50.00% | 25.00% | 66.67% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 5 | 2 | 2 | 3 | 50.00% | 75.00% | 40.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 2 | 1 | 0 | 2 | 0.00% | 50.00% | 0.00% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 2 | 1 | 2 | 0 | 50.00% | 0.00% | 100.00% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 4 | 2 | 2 | 2 | 50.00% | 50.00% | 50.00% |
| known_level_coverage | COMPLETE_V1_UNIVERSE [SMALL] | 8 | 3 | 4 | 4 | 100.00% | 100.00% | 50.00% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 2 | 1 | 0 | 2 | 0.00% | 50.00% | 0.00% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 1 | 1 | 1 | 0 | 25.00% | 0.00% | 100.00% |
| stage11_3.structure | UNAVAILABLE [SMALL] | 5 | 3 | 3 | 2 | 75.00% | 50.00% | 60.00% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 2 | 1 | 0 | 2 | 0.00% | 50.00% | 0.00% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 1 | 1 | 1 | 0 | 25.00% | 0.00% | 100.00% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE [SMALL] | 5 | 3 | 3 | 2 | 75.00% | 50.00% | 60.00% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 2 | 1 | 0 | 2 | 0.00% | 50.00% | 0.00% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 1 | 1 | 1 | 0 | 25.00% | 0.00% | 100.00% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 5 | 3 | 3 | 2 | 75.00% | 50.00% | 60.00% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 3 | 2 | 1 | 2 | 25.00% | 50.00% | 33.33% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 5 | 3 | 3 | 2 | 75.00% | 50.00% | 60.00% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 5 | 3 | 3 | 2 | 75.00% | 50.00% | 60.00% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 1 | 1 | 1 | 0 | 25.00% | 0.00% | 100.00% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 2 | 1 | 0 | 2 | 0.00% | 50.00% | 0.00% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE [SMALL] | 8 | 3 | 4 | 4 | 100.00% | 100.00% | 50.00% |


## Complete monthly stability: SHORT

Every feature is shown, not only those selected for the decision summary. Monthly intervals are not estimated. Monthly medians, quartiles, mean differences and category denominators remain explicit. September contains only four sessions.

### 2026-01


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 22/22 (11 sessions) | 1.2386 | 0.9600 | 0.7200 | 1.8300 | 14/14 (10 sessions) | 1.1471 | 1.0600 | 0.9662 | 1.3075 | 0.0915 | 0.1844 | not resampled |
| body_size [SMALL] | 22/22 (11 sessions) | 0.6146 | 0.5290 | 0.3550 | 0.7725 | 14/14 (10 sessions) | 0.8121 | 0.6575 | 0.5488 | 1.0525 | -0.1976 | -0.5345 | not resampled |
| directional_body [SMALL] | 22/22 (11 sessions) | 0.6146 | 0.5290 | 0.3550 | 0.7725 | 14/14 (10 sessions) | 0.8121 | 0.6575 | 0.5488 | 1.0525 | -0.1976 | -0.5345 | not resampled |
| candle_range [SMALL] | 22/22 (11 sessions) | 0.9356 | 0.8825 | 0.6525 | 1.0612 | 14/14 (10 sessions) | 1.2408 | 1.1850 | 0.8600 | 1.5800 | -0.3052 | -0.6909 | not resampled |
| body_range_ratio [SMALL] | 22/22 (11 sessions) | 0.6468 | 0.6700 | 0.5093 | 0.7626 | 14/14 (10 sessions) | 0.6446 | 0.6662 | 0.5771 | 0.7171 | 0.0022 | 0.0137 | not resampled |
| directional_body_range_ratio [SMALL] | 22/22 (11 sessions) | 0.6468 | 0.6700 | 0.5093 | 0.7626 | 14/14 (10 sessions) | 0.6446 | 0.6662 | 0.5771 | 0.7171 | 0.0022 | 0.0137 | not resampled |
| close_location [SMALL] | 22/22 (11 sessions) | 0.1821 | 0.1619 | 0.0768 | 0.2569 | 14/14 (10 sessions) | 0.1343 | 0.1034 | 0.0768 | 0.1975 | 0.0478 | 0.3956 | not resampled |
| directional_close_location [SMALL] | 22/22 (11 sessions) | 0.8179 | 0.8381 | 0.7431 | 0.9232 | 14/14 (10 sessions) | 0.8657 | 0.8966 | 0.8025 | 0.9232 | -0.0478 | -0.3956 | not resampled |
| distance_beyond_level [SMALL] | 22/22 (11 sessions) | 0.2723 | 0.2075 | 0.0525 | 0.3825 | 14/14 (10 sessions) | 0.3014 | 0.2725 | 0.1212 | 0.3450 | -0.0291 | -0.1122 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 12/22 (7 sessions) | 0.5102 | 0.4259 | 0.0609 | 0.7875 | 3/14 (2 sessions) | 0.3868 | 0.3318 | 0.1756 | 0.5704 | 0.1234 | 0.2462 | not resampled |
| candle_volume [SMALL] | 22/22 (11 sessions) | 1053454.5909 | 844030.5000 | 689549.7500 | 1279839.0000 | 14/14 (10 sessions) | 1524837.8571 | 1320788.0000 | 992071.2500 | 1863445.5000 | -471383.2662 | -0.7448 | not resampled |
| relative_volume_prior_6 [SMALL] | 16/22 (9 sessions) | 0.9794 | 0.8879 | 0.6979 | 1.2293 | 7/14 (5 sessions) | 1.2834 | 1.0511 | 0.9322 | 1.2824 | -0.3041 | -0.6500 | not resampled |
| atr14 [SMALL] | 12/22 (7 sessions) | 0.7188 | 0.7351 | 0.4333 | 1.0114 | 3/14 (2 sessions) | 1.0417 | 1.0266 | 1.0201 | 1.0558 | -0.3229 | -1.1825 | not resampled |
| minutes_since_open [SMALL] | 22/22 (11 sessions) | 154.5455 | 92.5000 | 32.5000 | 298.7500 | 14/14 (10 sessions) | 76.4286 | 35.0000 | 15.0000 | 57.5000 | 78.1169 | 0.6177 | not resampled |
| minutes_since_ema_cross [SMALL] | 9/22 (7 sessions) | 57.2222 | 55.0000 | 25.0000 | 70.0000 | 3/14 (2 sessions) | 35.0000 | 25.0000 | 15.0000 | 50.0000 | 22.2222 | 0.6309 | not resampled |
| break_attempt_rank [SMALL] | 22/22 (11 sessions) | 8.6818 | 6.0000 | 3.2500 | 12.7500 | 14/14 (10 sessions) | 5.0000 | 3.0000 | 2.0000 | 6.7500 | 3.6818 | 0.6453 | not resampled |
| valid_hold_sequence_rank [SMALL] | 22/22 (11 sessions) | 3.7273 | 3.0000 | 2.0000 | 5.7500 | 14/14 (10 sessions) | 2.3571 | 2.0000 | 1.0000 | 2.7500 | 1.3701 | 0.6029 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 11/22 (7 sessions) | 0.3131 | 0.2830 | 0.2409 | 0.4164 | 3/14 (2 sessions) | 0.5788 | 0.5833 | 0.3790 | 0.7809 | -0.2657 | -1.3287 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 11/22 (7 sessions) | 0.4750 | 0.4611 | 0.3389 | 0.5995 | 3/14 (2 sessions) | 0.5577 | 0.5376 | 0.3539 | 0.7515 | -0.0827 | -0.3456 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 13/22 (7 sessions) | -0.1203 | -0.1466 | -0.1676 | -0.0691 | 5/14 (4 sessions) | -0.1915 | -0.1846 | -0.2503 | -0.0286 | 0.0712 | 0.5175 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 13/22 (7 sessions) | -0.0601 | -0.0732 | -0.1366 | 0.0054 | 4/14 (3 sessions) | -0.0694 | -0.0116 | -0.1627 | 0.0817 | 0.0093 | 0.0592 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 12/22 (7 sessions) | -0.0552 | -0.0703 | -0.1412 | 0.0358 | 4/14 (3 sessions) | -0.0536 | 0.0199 | -0.1025 | 0.0687 | -0.0016 | -0.0098 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 11/22 (7 sessions) | -0.0650 | -0.0845 | -0.1015 | -0.0369 | 3/14 (2 sessions) | -0.1531 | -0.1668 | -0.2523 | -0.0608 | 0.0882 | 0.9077 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 11/22 (7 sessions) | -0.0358 | -0.0662 | -0.0817 | 0.0186 | 3/14 (2 sessions) | -0.0873 | -0.0808 | -0.1874 | 0.0160 | 0.0515 | 0.4820 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 10/22 (7 sessions) | -0.0233 | -0.0563 | -0.0742 | 0.0252 | 3/14 (2 sessions) | -0.0779 | -0.0543 | -0.1633 | 0.0193 | 0.0546 | 0.5161 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 22/22 (11 sessions) | -0.0502 | -0.0249 | -0.0874 | 0.0002 | 14/14 (10 sessions) | -0.0989 | -0.0980 | -0.1536 | -0.0246 | 0.0488 | 0.5636 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 21/22 (10 sessions) | -0.0213 | -0.0135 | -0.0417 | 0.0023 | 12/14 (9 sessions) | -0.0547 | -0.0511 | -0.0860 | -0.0140 | 0.0334 | 0.6849 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 19/22 (9 sessions) | -0.0199 | -0.0144 | -0.0273 | 0.0097 | 9/14 (7 sessions) | -0.0391 | -0.0591 | -0.0698 | 0.0043 | 0.0192 | 0.3946 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 10/22 (7 sessions) | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 3/14 (2 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.5000 | -0.2333 | -0.6183 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 9/22 (7 sessions) | 0.4444 | 0.0000 | 0.0000 | 1.0000 | 3/14 (2 sessions) | 1.0000 | 1.0000 | 0.5000 | 1.5000 | -0.5556 | -0.8550 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 8/22 (6 sessions) | 1.2500 | 1.0000 | 1.0000 | 1.2500 | 2/14 (2 sessions) | 1.5000 | 1.5000 | 1.2500 | 1.7500 | -0.2500 | -0.2887 | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 12/22 (7 sessions) | 0.5833 | 1.0000 | 0.0000 | 1.0000 | 3/14 (2 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.5000 | 0.2500 | 0.4762 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 11/22 (7 sessions) | 1.0000 | 1.0000 | 0.5000 | 1.0000 | 3/14 (2 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.5000 | 0.6667 | 0.7845 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 9/22 (7 sessions) | 0.8889 | 1.0000 | 1.0000 | 1.0000 | 3/14 (2 sessions) | 1.3333 | 1.0000 | 1.0000 | 1.5000 | -0.4444 | -0.7454 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 10/22 (7 sessions) | 0.2000 | 0.0000 | 0.0000 | 0.0000 | 3/14 (2 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.5000 | -0.1333 | -0.2937 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 9/22 (7 sessions) | 0.3333 | 0.0000 | 0.0000 | 1.0000 | 3/14 (2 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.5000 | 0.0000 | 0.0000 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 8/22 (6 sessions) | 0.2500 | 0.0000 | 0.0000 | 0.2500 | 2/14 (2 sessions) | 0.5000 | 0.5000 | 0.2500 | 0.7500 | -0.2500 | -0.5000 | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 17/22 (9 sessions) | 1.1176 | 1.0000 | 0.0000 | 2.0000 | 8/14 (6 sessions) | 1.1250 | 1.0000 | 0.0000 | 2.0000 | -0.0074 | -0.0066 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 12/22 (7 sessions) | 2.0000 | 2.0000 | 0.7500 | 3.0000 | 4/14 (3 sessions) | 1.5000 | 1.0000 | 0.7500 | 1.7500 | 0.5000 | 0.2922 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 10/22 (7 sessions) | 3.1000 | 3.5000 | 1.2500 | 4.7500 | 3/14 (2 sessions) | 2.0000 | 1.0000 | 1.0000 | 2.5000 | 1.1000 | 0.6360 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 17/22 (9 sessions) | 1.8103 | 1.6000 | 1.3800 | 2.1400 | 8/14 (6 sessions) | 2.5458 | 2.3750 | 2.2075 | 3.0740 | -0.7355 | -1.0807 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 12/22 (7 sessions) | 2.2208 | 1.9921 | 1.6663 | 2.7338 | 4/14 (3 sessions) | 3.5890 | 3.1831 | 2.5150 | 4.2572 | -1.3683 | -1.1014 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 10/22 (7 sessions) | 3.1650 | 2.8575 | 1.8188 | 3.8812 | 3/14 (2 sessions) | 5.7354 | 6.7100 | 5.1181 | 6.8400 | -2.5704 | -1.6117 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 12/22 (7 sessions) | 2.5264 | 2.2968 | 2.0032 | 2.8644 | 3/14 (2 sessions) | 3.0063 | 3.1524 | 2.6546 | 3.4310 | -0.4799 | -0.6507 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 12/22 (7 sessions) | 3.2183 | 2.9721 | 2.6497 | 3.9255 | 3/14 (2 sessions) | 4.1387 | 3.4348 | 3.0262 | 4.8993 | -0.9204 | -0.8651 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 10/22 (7 sessions) | 4.7062 | 4.6698 | 3.9985 | 5.2722 | 3/14 (2 sessions) | 5.4987 | 6.1846 | 4.8097 | 6.5307 | -0.7925 | -0.7266 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 17/22 (9 sessions) | 0.5352 | 0.5130 | 0.2673 | 0.8819 | 8/14 (6 sessions) | 0.4880 | 0.4148 | 0.2264 | 0.7154 | 0.0473 | 0.1449 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 12/22 (7 sessions) | 0.2895 | 0.2665 | 0.1890 | 0.3200 | 4/14 (3 sessions) | 0.3046 | 0.1409 | 0.1300 | 0.3156 | -0.0152 | -0.0710 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 10/22 (7 sessions) | 0.2075 | 0.1971 | 0.0756 | 0.3185 | 3/14 (2 sessions) | 0.2806 | 0.4083 | 0.2068 | 0.4183 | -0.0732 | -0.4466 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 17/22 (9 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 8/14 (6 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 12/22 (7 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 4/14 (3 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 10/22 (7 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 3/14 (2 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 17/22 (9 sessions) | 0.5147 | 0.5000 | 0.2500 | 0.7500 | 8/14 (6 sessions) | 0.4062 | 0.5000 | 0.2500 | 0.5000 | 0.1085 | 0.4176 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 12/22 (7 sessions) | 0.4917 | 0.4500 | 0.4000 | 0.5250 | 4/14 (3 sessions) | 0.4000 | 0.3500 | 0.3000 | 0.4500 | 0.0917 | 0.6378 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 10/22 (7 sessions) | 0.5091 | 0.4545 | 0.4545 | 0.5568 | 3/14 (2 sessions) | 0.4545 | 0.5000 | 0.4318 | 0.5000 | 0.0545 | 0.4302 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 12/22 (7 sessions) | 1.1268 | 1.1450 | 0.4824 | 1.6593 | 3/14 (2 sessions) | 2.0225 | 2.4608 | 1.2845 | 2.9797 | -0.8958 | -0.8652 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 12/22 (7 sessions) | 0.6884 | 0.5894 | 0.1358 | 1.0870 | 3/14 (2 sessions) | 0.9918 | 1.2977 | 0.7187 | 1.4178 | -0.3034 | -0.5103 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 11/22 (7 sessions) | 0.5525 | 0.3110 | 0.2219 | 0.6906 | 3/14 (2 sessions) | 0.5475 | 0.3323 | 0.3211 | 0.6663 | 0.0050 | 0.0097 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 19/22 (10 sessions) | 1.7926 | 1.6200 | 0.9175 | 2.2400 | 13/14 (9 sessions) | 1.6622 | 1.8000 | 0.3040 | 2.2300 | 0.1305 | 0.1020 | not resampled |
| stage11_2.room_in_atr [SMALL] | 11/22 (6 sessions) | 3.3781 | 3.3922 | 2.8835 | 4.1458 | 3/14 (2 sessions) | 2.6598 | 2.0830 | 1.9295 | 3.1017 | 0.7183 | 0.7883 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 22/22 (11 sessions) | 4.0909 | 4.0000 | 3.0000 | 4.7500 | 14/14 (10 sessions) | 4.4286 | 4.0000 | 4.0000 | 5.0000 | -0.3377 | -0.3641 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 22/22 (11 sessions) | 1.8182 | 2.0000 | 1.0000 | 2.7500 | 14/14 (10 sessions) | 1.5714 | 2.0000 | 1.0000 | 2.0000 | 0.2468 | 0.2686 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 22/22 (11 sessions) | 0.2528 | 0.2075 | 0.0525 | 0.3600 | 14/14 (10 sessions) | 0.3014 | 0.2725 | 0.1212 | 0.3450 | -0.0487 | -0.1979 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 19/22 (10 sessions) | 1.7926 | 1.6200 | 0.9175 | 2.2400 | 13/14 (9 sessions) | 1.6622 | 1.8000 | 0.3040 | 2.2300 | 0.1305 | 0.1020 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 12/22 (7 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 3/14 (2 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 12/22 (7 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 3/14 (2 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 16/22 (9 sessions) | 1.5360 | 1.4650 | 0.9101 | 1.8525 | 6/14 (4 sessions) | 2.2972 | 1.7650 | 1.1025 | 2.1575 | -0.7612 | -0.6110 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 15/22 (9 sessions) | 0.4844 | 0.2950 | 0.1825 | 0.5725 | 6/14 (5 sessions) | 1.3067 | 0.8600 | 0.7000 | 1.7400 | -0.8222 | -1.0829 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 12/22 (7 sessions) | 2.2817 | 2.0464 | 1.5358 | 3.1032 | 3/14 (2 sessions) | 2.9036 | 1.3826 | 1.1637 | 3.8830 | -0.6220 | -0.4069 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 12/22 (7 sessions) | 0.5453 | 0.4006 | 0.1487 | 0.9042 | 3/14 (2 sessions) | 1.7805 | 1.9579 | 1.0527 | 2.5970 | -1.2352 | -1.6757 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | SHORT | 36 | 16 | 22 | 14 | 100.00% | 100.00% | 61.11% |
| time_bucket | 09:35-10:00 [SMALL] | 11 | 8 | 5 | 6 | 22.73% | 42.86% | 45.45% |
| time_bucket | 10:00-10:30 [SMALL] | 9 | 8 | 5 | 4 | 22.73% | 28.57% | 55.56% |
| time_bucket | 10:30-11:00 [SMALL] | 2 | 1 | 1 | 1 | 4.55% | 7.14% | 50.00% |
| time_bucket | 11:00-12:00 [SMALL] | 1 | 1 | 1 | 0 | 4.55% | 0.00% | 100.00% |
| time_bucket | 12:00-13:30 [SMALL] | 4 | 3 | 2 | 2 | 9.09% | 14.29% | 50.00% |
| time_bucket | 13:30-15:00 [SMALL] | 5 | 5 | 5 | 0 | 22.73% | 0.00% | 100.00% |
| time_bucket | 15:00-close [SMALL] | 4 | 3 | 3 | 1 | 13.64% | 7.14% | 75.00% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 9 | 6 | 7 | 2 | 31.82% | 14.29% | 77.78% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 5 | 3 | 4 | 1 | 18.18% | 7.14% | 80.00% |
| ema9_20_alignment | EMA_UNAVAILABLE [SMALL] | 22 | 14 | 11 | 11 | 50.00% | 78.57% | 50.00% |
| price_vwap_alignment | VWAP_ALIGNED | 31 | 16 | 18 | 13 | 81.82% | 92.86% | 58.06% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 5 | 3 | 4 | 1 | 18.18% | 7.14% | 80.00% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED [SMALL] | 12 | 5 | 8 | 4 | 36.36% | 28.57% | 66.67% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 8 | 6 | 7 | 1 | 31.82% | 7.14% | 87.50% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 16 | 12 | 7 | 9 | 31.82% | 64.29% | 43.75% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 9 | 4 | 6 | 3 | 27.27% | 21.43% | 66.67% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 5 | 5 | 5 | 0 | 22.73% | 0.00% | 100.00% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE [SMALL] | 22 | 14 | 11 | 11 | 50.00% | 78.57% | 50.00% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 7 | 5 | 5 | 2 | 22.73% | 14.29% | 71.43% |
| prior_ema_cross | NO_PRIOR_CROSS [SMALL] | 24 | 15 | 13 | 11 | 59.09% | 78.57% | 54.17% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 5 | 3 | 4 | 1 | 18.18% | 7.14% | 80.00% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE [SMALL] | 26 | 11 | 18 | 8 | 81.82% | 57.14% | 69.23% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 9 | 5 | 4 | 5 | 18.18% | 35.71% | 44.44% |
| opposite_boundary_broken | OPPOSITE_FIRST_OBSERVED_THIS_CLOSE [SMALL] | 1 | 1 | 0 | 1 | 0.00% | 7.14% | 0.00% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 2 | 2 | 1 | 1 | 4.55% | 7.14% | 50.00% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 4 | 4 | 3 | 1 | 13.64% | 7.14% | 75.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 8 | 3 | 7 | 1 | 31.82% | 7.14% | 87.50% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 4 | 1 | 3 | 1 | 13.64% | 7.14% | 75.00% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 18 | 13 | 8 | 10 | 36.36% | 71.43% | 44.44% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 35 | 15 | 21 | 14 | 95.45% | 100.00% | 60.00% |
| known_level_coverage | PARTIAL_UNAVAILABLE [SMALL] | 1 | 1 | 1 | 0 | 4.55% | 0.00% | 100.00% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 5 | 3 | 4 | 1 | 18.18% | 7.14% | 80.00% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 3 | 3 | 3 | 0 | 13.64% | 0.00% | 100.00% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 7 | 4 | 5 | 2 | 22.73% | 14.29% | 71.43% |
| stage11_3.structure | UNAVAILABLE [SMALL] | 21 | 14 | 10 | 11 | 45.45% | 78.57% | 47.62% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 5 | 3 | 4 | 1 | 18.18% | 7.14% | 80.00% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 10 | 6 | 8 | 2 | 36.36% | 14.29% | 80.00% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE [SMALL] | 21 | 14 | 10 | 11 | 45.45% | 78.57% | 47.62% |
| stage11_3.high_structure | EQUAL_HIGH [SMALL] | 2 | 1 | 2 | 0 | 9.09% | 0.00% | 100.00% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 6 | 5 | 6 | 0 | 27.27% | 0.00% | 100.00% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 7 | 4 | 4 | 3 | 18.18% | 21.43% | 57.14% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 21 | 14 | 10 | 11 | 45.45% | 78.57% | 47.62% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 8 | 5 | 5 | 3 | 22.73% | 21.43% | 62.50% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 8 | 5 | 7 | 1 | 31.82% | 7.14% | 87.50% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 20 | 14 | 10 | 10 | 45.45% | 71.43% | 50.00% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 15 | 11 | 7 | 8 | 31.82% | 57.14% | 46.67% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 2 | 1 | 2 | 0 | 9.09% | 0.00% | 100.00% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 19 | 11 | 13 | 6 | 59.09% | 42.86% | 68.42% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 36 | 16 | 22 | 14 | 100.00% | 100.00% | 61.11% |


### 2026-02


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 23/23 (11 sessions) | 1.3673 | 1.3000 | 0.9550 | 1.6900 | 5/5 (5 sessions) | 1.2660 | 1.3000 | 0.9600 | 1.3600 | 0.1013 | 0.1989 | not resampled |
| body_size [SMALL] | 23/23 (11 sessions) | 0.9967 | 0.8200 | 0.6075 | 1.2250 | 5/5 (5 sessions) | 0.7860 | 0.7500 | 0.5500 | 0.7950 | 0.2107 | 0.3454 | not resampled |
| directional_body [SMALL] | 23/23 (11 sessions) | 0.9967 | 0.8200 | 0.6075 | 1.2250 | 5/5 (5 sessions) | 0.7860 | 0.7500 | 0.5500 | 0.7950 | 0.2107 | 0.3454 | not resampled |
| candle_range [SMALL] | 23/23 (11 sessions) | 1.3836 | 1.3400 | 0.9946 | 1.6550 | 5/5 (5 sessions) | 1.4540 | 1.4350 | 1.0200 | 1.5200 | -0.0704 | -0.1058 | not resampled |
| body_range_ratio [SMALL] | 23/23 (11 sessions) | 0.6703 | 0.7000 | 0.5458 | 0.8126 | 5/5 (5 sessions) | 0.5583 | 0.5230 | 0.3833 | 0.5827 | 0.1119 | 0.5661 | not resampled |
| directional_body_range_ratio [SMALL] | 23/23 (11 sessions) | 0.6703 | 0.7000 | 0.5458 | 0.8126 | 5/5 (5 sessions) | 0.5583 | 0.5230 | 0.3833 | 0.5827 | 0.1119 | 0.5661 | not resampled |
| close_location [SMALL] | 23/23 (11 sessions) | 0.1774 | 0.1538 | 0.0676 | 0.2456 | 5/5 (5 sessions) | 0.2053 | 0.2072 | 0.1986 | 0.2255 | -0.0279 | -0.1997 | not resampled |
| directional_close_location [SMALL] | 23/23 (11 sessions) | 0.8226 | 0.8462 | 0.7544 | 0.9324 | 5/5 (5 sessions) | 0.7947 | 0.7928 | 0.7745 | 0.8014 | 0.0279 | 0.1997 | not resampled |
| distance_beyond_level [SMALL] | 23/23 (11 sessions) | 0.5575 | 0.3250 | 0.1975 | 0.7450 | 5/5 (5 sessions) | 0.3430 | 0.3200 | 0.1800 | 0.4700 | 0.2145 | 0.4163 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 11/23 (5 sessions) | 0.3306 | 0.2214 | 0.1915 | 0.3869 | 3/5 (3 sessions) | 0.3200 | 0.2892 | 0.2501 | 0.3745 | 0.0106 | 0.0412 | not resampled |
| candle_volume [SMALL] | 23/23 (11 sessions) | 1252774.3913 | 1338134.0000 | 620194.5000 | 1730500.0000 | 5/5 (5 sessions) | 1234530.8000 | 910893.0000 | 806022.0000 | 1685230.0000 | 18243.5913 | 0.0278 | not resampled |
| relative_volume_prior_6 [SMALL] | 13/23 (5 sessions) | 1.1302 | 1.2410 | 0.7068 | 1.4598 | 3/5 (3 sessions) | 1.4818 | 1.2818 | 1.2560 | 1.6076 | -0.3516 | -0.9149 | not resampled |
| atr14 [SMALL] | 11/23 (5 sessions) | 0.9427 | 0.9229 | 0.7555 | 1.0258 | 3/5 (3 sessions) | 1.0628 | 1.1066 | 0.9797 | 1.1678 | -0.1201 | -0.4124 | not resampled |
| minutes_since_open [SMALL] | 23/23 (11 sessions) | 113.9130 | 65.0000 | 20.0000 | 175.0000 | 5/5 (5 sessions) | 95.0000 | 100.0000 | 15.0000 | 140.0000 | 18.9130 | 0.1691 | not resampled |
| minutes_since_ema_cross [SMALL] | 7/23 (4 sessions) | 27.1429 | 20.0000 | 10.0000 | 42.5000 | 2/5 (2 sessions) | 2.5000 | 2.5000 | 1.2500 | 3.7500 | 24.6429 | 1.0367 | not resampled |
| break_attempt_rank [SMALL] | 23/23 (11 sessions) | 7.8261 | 5.0000 | 3.0000 | 12.0000 | 5/5 (5 sessions) | 7.0000 | 7.0000 | 2.0000 | 11.0000 | 0.8261 | 0.1310 | not resampled |
| valid_hold_sequence_rank [SMALL] | 23/23 (11 sessions) | 4.4783 | 3.0000 | 1.5000 | 8.0000 | 5/5 (5 sessions) | 4.2000 | 5.0000 | 1.0000 | 7.0000 | 0.2783 | 0.0841 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 10/23 (4 sessions) | 0.2808 | 0.2108 | 0.1531 | 0.2939 | 3/5 (3 sessions) | 0.1170 | 0.1230 | 0.0652 | 0.1719 | 0.1638 | 0.7306 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 10/23 (4 sessions) | 0.3083 | 0.2432 | 0.2028 | 0.2956 | 3/5 (3 sessions) | 0.1027 | 0.1001 | 0.0543 | 0.1498 | 0.2055 | 0.8856 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 12/23 (5 sessions) | -0.1745 | -0.1474 | -0.2377 | -0.1061 | 3/5 (3 sessions) | -0.2687 | -0.2845 | -0.3086 | -0.2367 | 0.0942 | 0.8277 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 12/23 (5 sessions) | -0.1125 | -0.1061 | -0.1394 | -0.0331 | 3/5 (3 sessions) | -0.2217 | -0.2713 | -0.2731 | -0.1950 | 0.1092 | 1.0425 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 12/23 (5 sessions) | -0.0934 | -0.0885 | -0.1450 | -0.0374 | 3/5 (3 sessions) | -0.1982 | -0.2051 | -0.2486 | -0.1512 | 0.1048 | 1.1477 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 10/23 (4 sessions) | -0.0990 | -0.0854 | -0.1288 | -0.0465 | 2/5 (2 sessions) | -0.1480 | -0.1480 | -0.1505 | -0.1455 | 0.0490 | 0.6485 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 10/23 (4 sessions) | -0.0751 | -0.0650 | -0.1015 | -0.0387 | 2/5 (2 sessions) | -0.1246 | -0.1246 | -0.1273 | -0.1220 | 0.0495 | 0.7272 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 10/23 (4 sessions) | -0.0653 | -0.0576 | -0.0902 | -0.0342 | 2/5 (2 sessions) | -0.1067 | -0.1067 | -0.1127 | -0.1007 | 0.0414 | 0.6883 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 23/23 (11 sessions) | -0.1428 | -0.0348 | -0.2789 | -0.0175 | 5/5 (5 sessions) | -0.1063 | -0.0478 | -0.1957 | -0.0106 | -0.0366 | -0.2159 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 20/23 (10 sessions) | -0.0597 | -0.0191 | -0.0446 | -0.0050 | 5/5 (5 sessions) | -0.0627 | -0.0307 | -0.1092 | -0.0031 | 0.0030 | 0.0252 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 17/23 (7 sessions) | -0.0550 | -0.0160 | -0.0330 | -0.0043 | 3/5 (3 sessions) | -0.0059 | -0.0003 | -0.0099 | 0.0010 | -0.0491 | -0.5373 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 9/23 (4 sessions) | 0.5556 | 0.0000 | 0.0000 | 1.0000 | 2/5 (2 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | -0.4444 | -0.6489 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 6/23 (4 sessions) | 1.0000 | 1.0000 | 0.2500 | 1.0000 | 1/5 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 5/23 (4 sessions) | 2.2000 | 2.0000 | 1.0000 | 3.0000 | 0/5 (0 sessions) | N/A | N/A | N/A | N/A | N/A | N/A | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 11/23 (5 sessions) | 0.7273 | 1.0000 | 0.0000 | 1.0000 | 3/5 (3 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.5000 | 0.3939 | 0.6198 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 10/23 (4 sessions) | 1.0000 | 1.0000 | 0.2500 | 1.0000 | 3/5 (3 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.5000 | 0.6667 | 0.7511 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 6/23 (4 sessions) | 1.6667 | 1.0000 | 0.2500 | 2.5000 | 1/5 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.6667 | N/A | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 9/23 (4 sessions) | 0.2222 | 0.0000 | 0.0000 | 0.0000 | 2/5 (2 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.2222 | 0.5345 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 6/23 (4 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.7500 | 1/5 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | N/A | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 5/23 (4 sessions) | 0.4000 | 0.0000 | 0.0000 | 0.0000 | 0/5 (0 sessions) | N/A | N/A | N/A | N/A | N/A | N/A | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 14/23 (5 sessions) | 1.2143 | 1.0000 | 1.0000 | 2.0000 | 3/5 (3 sessions) | 1.6667 | 1.0000 | 1.0000 | 2.0000 | -0.4524 | -0.4855 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 12/23 (5 sessions) | 2.0833 | 2.5000 | 1.0000 | 3.0000 | 3/5 (3 sessions) | 2.0000 | 1.0000 | 1.0000 | 2.5000 | 0.0833 | 0.0628 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 9/23 (4 sessions) | 3.5556 | 3.0000 | 2.0000 | 6.0000 | 2/5 (2 sessions) | 5.5000 | 5.5000 | 3.7500 | 7.2500 | -1.9444 | -0.6124 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 14/23 (5 sessions) | 2.6078 | 2.4725 | 1.3550 | 3.4262 | 3/5 (3 sessions) | 2.5267 | 2.8200 | 2.2050 | 2.9950 | 0.0812 | 0.0546 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 12/23 (5 sessions) | 2.9929 | 2.7800 | 2.1025 | 3.7350 | 3/5 (3 sessions) | 2.8733 | 2.8200 | 2.3700 | 3.3500 | 0.1196 | 0.1000 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 9/23 (4 sessions) | 3.3808 | 3.4450 | 2.7125 | 3.7850 | 2/5 (2 sessions) | 4.3900 | 4.3900 | 3.7800 | 5.0000 | -1.0092 | -0.8178 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 11/23 (5 sessions) | 2.1402 | 2.0492 | 1.5929 | 2.4577 | 3/5 (3 sessions) | 2.3307 | 2.5484 | 2.2063 | 2.5639 | -0.1905 | -0.3255 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 11/23 (5 sessions) | 2.9615 | 2.7704 | 2.5979 | 3.0411 | 3/5 (3 sessions) | 2.6522 | 2.5484 | 2.3998 | 2.8528 | 0.3093 | 0.4343 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 9/23 (4 sessions) | 3.8688 | 3.6372 | 3.3360 | 3.7898 | 2/5 (2 sessions) | 3.7148 | 3.7148 | 3.2897 | 4.1398 | 0.1540 | 0.1613 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 14/23 (5 sessions) | 0.5030 | 0.4195 | 0.2634 | 0.6884 | 3/5 (3 sessions) | 0.7944 | 0.8614 | 0.6915 | 0.9307 | -0.2913 | -1.0032 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 12/23 (5 sessions) | 0.3681 | 0.3480 | 0.2468 | 0.4695 | 3/5 (3 sessions) | 0.2952 | 0.2067 | 0.1816 | 0.3644 | 0.0729 | 0.4234 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 9/23 (4 sessions) | 0.1659 | 0.1282 | 0.0826 | 0.1487 | 2/5 (2 sessions) | 0.0861 | 0.0861 | 0.0738 | 0.0985 | 0.0798 | 0.6219 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 14/23 (5 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 3/5 (3 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 12/23 (5 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 3/5 (3 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 9/23 (4 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 2/5 (2 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 14/23 (5 sessions) | 0.4821 | 0.5000 | 0.2500 | 0.6875 | 3/5 (3 sessions) | 0.3333 | 0.5000 | 0.2500 | 0.5000 | 0.1488 | 0.4746 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 12/23 (5 sessions) | 0.5167 | 0.5500 | 0.4750 | 0.6000 | 3/5 (3 sessions) | 0.5333 | 0.5000 | 0.5000 | 0.5500 | -0.0167 | -0.0997 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 9/23 (4 sessions) | 0.5505 | 0.5909 | 0.5455 | 0.6364 | 2/5 (2 sessions) | 0.5455 | 0.5455 | 0.5227 | 0.5682 | 0.0051 | 0.0450 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 11/23 (5 sessions) | 1.0492 | 0.8936 | 0.6744 | 1.1827 | 3/5 (3 sessions) | 0.7636 | 0.6796 | 0.5515 | 0.9337 | 0.2856 | 0.4654 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 11/23 (5 sessions) | 0.3232 | 0.3198 | 0.0947 | 0.5061 | 3/5 (3 sessions) | 0.3418 | 0.2062 | 0.1829 | 0.4330 | -0.0186 | -0.0687 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 10/23 (4 sessions) | 0.2381 | 0.1290 | 0.0588 | 0.3579 | 3/5 (3 sessions) | 0.3382 | 0.2148 | 0.1274 | 0.4873 | -0.1001 | -0.3580 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 19/23 (10 sessions) | 1.9879 | 1.4480 | 0.4552 | 3.6700 | 5/5 (5 sessions) | 1.9880 | 1.5400 | 0.6100 | 1.9450 | -0.0001 | -0.0000 | not resampled |
| stage11_2.room_in_atr [SMALL] | 8/23 (4 sessions) | 1.5505 | 1.8700 | 0.3205 | 2.4007 | 3/5 (3 sessions) | 1.1535 | 1.5827 | 0.8275 | 1.6941 | 0.3970 | 0.3629 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 23/23 (11 sessions) | 4.6087 | 4.0000 | 4.0000 | 5.0000 | 5/5 (5 sessions) | 4.4000 | 4.0000 | 4.0000 | 5.0000 | 0.2087 | 0.2778 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 23/23 (11 sessions) | 1.3913 | 2.0000 | 1.0000 | 2.0000 | 5/5 (5 sessions) | 1.6000 | 2.0000 | 1.0000 | 2.0000 | -0.2087 | -0.2778 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 23/23 (11 sessions) | 0.4591 | 0.2720 | 0.1425 | 0.5450 | 5/5 (5 sessions) | 0.3430 | 0.3200 | 0.1800 | 0.4700 | 0.1161 | 0.2267 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 19/23 (10 sessions) | 1.9879 | 1.4480 | 0.4552 | 3.6700 | 5/5 (5 sessions) | 1.9880 | 1.5400 | 0.6100 | 1.9450 | -0.0001 | -0.0000 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 11/23 (5 sessions) | 0.2727 | 0.0000 | 0.0000 | 0.5000 | 3/5 (3 sessions) | 0.6667 | 0.0000 | 0.0000 | 1.0000 | -0.3939 | -0.6198 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 11/23 (5 sessions) | 0.4545 | 0.0000 | 0.0000 | 0.5000 | 3/5 (3 sessions) | 0.6667 | 0.0000 | 0.0000 | 1.0000 | -0.2121 | -0.2397 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 15/23 (6 sessions) | 2.6510 | 2.1700 | 1.5275 | 3.2050 | 3/5 (3 sessions) | 2.3450 | 2.5900 | 2.0900 | 2.7225 | 0.3060 | 0.1873 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 14/23 (6 sessions) | 0.8907 | 0.5700 | 0.2550 | 1.5475 | 3/5 (3 sessions) | 0.6421 | 0.8700 | 0.4800 | 0.9182 | 0.2486 | 0.2998 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 11/23 (5 sessions) | 2.1078 | 2.0452 | 1.3469 | 2.2402 | 3/5 (3 sessions) | 2.1760 | 2.3231 | 2.0937 | 2.3318 | -0.0681 | -0.0634 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 11/23 (5 sessions) | 0.7646 | 0.5343 | 0.3613 | 0.8577 | 3/5 (3 sessions) | 0.5593 | 0.7862 | 0.4459 | 0.7862 | 0.2053 | 0.3154 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | SHORT [SMALL] | 28 | 12 | 23 | 5 | 100.00% | 100.00% | 82.14% |
| time_bucket | 09:35-10:00 [SMALL] | 11 | 9 | 9 | 2 | 39.13% | 40.00% | 81.82% |
| time_bucket | 10:00-10:30 [SMALL] | 2 | 2 | 2 | 0 | 8.70% | 0.00% | 100.00% |
| time_bucket | 10:30-11:00 [SMALL] | 2 | 1 | 2 | 0 | 8.70% | 0.00% | 100.00% |
| time_bucket | 11:00-12:00 [SMALL] | 4 | 2 | 2 | 2 | 8.70% | 40.00% | 50.00% |
| time_bucket | 12:00-13:30 [SMALL] | 5 | 3 | 4 | 1 | 17.39% | 20.00% | 80.00% |
| time_bucket | 13:30-15:00 [SMALL] | 2 | 2 | 2 | 0 | 8.70% | 0.00% | 100.00% |
| time_bucket | 15:00-close [SMALL] | 2 | 2 | 2 | 0 | 8.70% | 0.00% | 100.00% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 12 | 5 | 9 | 3 | 39.13% | 60.00% | 75.00% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 1 | 1 | 1 | 0 | 4.35% | 0.00% | 100.00% |
| ema9_20_alignment | EMA_UNAVAILABLE [SMALL] | 15 | 11 | 13 | 2 | 56.52% | 40.00% | 86.67% |
| price_vwap_alignment | VWAP_ALIGNED [SMALL] | 28 | 12 | 23 | 5 | 100.00% | 100.00% | 82.14% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED [SMALL] | 12 | 5 | 11 | 1 | 47.83% | 20.00% | 91.67% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 4 | 3 | 2 | 2 | 8.70% | 40.00% | 50.00% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 12 | 10 | 10 | 2 | 43.48% | 40.00% | 83.33% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 5 | 2 | 5 | 0 | 21.74% | 0.00% | 100.00% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 8 | 5 | 5 | 3 | 21.74% | 60.00% | 62.50% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE [SMALL] | 15 | 11 | 13 | 2 | 56.52% | 40.00% | 86.67% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 8 | 5 | 6 | 2 | 26.09% | 40.00% | 75.00% |
| prior_ema_cross | NO_PRIOR_CROSS [SMALL] | 19 | 11 | 16 | 3 | 69.57% | 60.00% | 84.21% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 1 | 1 | 1 | 0 | 4.35% | 0.00% | 100.00% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE [SMALL] | 22 | 9 | 18 | 4 | 78.26% | 80.00% | 81.82% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 6 | 5 | 5 | 1 | 21.74% | 20.00% | 83.33% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 3 | 2 | 1 | 2 | 4.35% | 40.00% | 33.33% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 4 | 2 | 4 | 0 | 17.39% | 0.00% | 100.00% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 4 | 2 | 3 | 1 | 13.04% | 20.00% | 75.00% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 4 | 2 | 4 | 0 | 17.39% | 0.00% | 100.00% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 13 | 10 | 11 | 2 | 47.83% | 40.00% | 84.62% |
| known_level_coverage | COMPLETE_V1_UNIVERSE [SMALL] | 28 | 12 | 23 | 5 | 100.00% | 100.00% | 82.14% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 7 | 5 | 6 | 1 | 26.09% | 20.00% | 85.71% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 2 | 1 | 1 | 1 | 4.35% | 20.00% | 50.00% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 5 | 3 | 4 | 1 | 17.39% | 20.00% | 80.00% |
| stage11_3.structure | UNAVAILABLE [SMALL] | 14 | 11 | 12 | 2 | 52.17% | 40.00% | 85.71% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 7 | 5 | 6 | 1 | 26.09% | 20.00% | 85.71% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 7 | 3 | 5 | 2 | 21.74% | 40.00% | 71.43% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE [SMALL] | 14 | 11 | 12 | 2 | 52.17% | 40.00% | 85.71% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 4 | 2 | 3 | 1 | 13.04% | 20.00% | 75.00% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 10 | 6 | 8 | 2 | 34.78% | 40.00% | 80.00% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 14 | 11 | 12 | 2 | 52.17% | 40.00% | 85.71% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 5 | 3 | 3 | 2 | 13.04% | 40.00% | 60.00% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 9 | 5 | 8 | 1 | 34.78% | 20.00% | 88.89% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 14 | 11 | 12 | 2 | 52.17% | 40.00% | 85.71% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 11 | 11 | 9 | 2 | 39.13% | 40.00% | 81.82% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 3 | 2 | 3 | 0 | 13.04% | 0.00% | 100.00% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 2 | 2 | 2 | 0 | 8.70% | 0.00% | 100.00% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 12 | 6 | 9 | 3 | 39.13% | 60.00% | 75.00% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE [SMALL] | 28 | 12 | 23 | 5 | 100.00% | 100.00% | 82.14% |


### 2026-03


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 40/40 (19 sessions) | 1.6884 | 1.6500 | 1.4900 | 1.9925 | 8/8 (7 sessions) | 1.7891 | 1.8400 | 1.6788 | 2.0400 | -0.1007 | -0.2399 | not resampled |
| body_size [SMALL] | 40/40 (19 sessions) | 1.0735 | 1.0300 | 0.5775 | 1.4275 | 8/8 (7 sessions) | 0.7259 | 0.5250 | 0.2888 | 0.9488 | 0.3476 | 0.6043 | not resampled |
| directional_body [SMALL] | 40/40 (19 sessions) | 1.0735 | 1.0300 | 0.5775 | 1.4275 | 8/8 (7 sessions) | 0.7259 | 0.5250 | 0.2888 | 0.9488 | 0.3476 | 0.6043 | not resampled |
| candle_range [SMALL] | 40/40 (19 sessions) | 1.4789 | 1.4400 | 1.1000 | 1.7550 | 8/8 (7 sessions) | 1.1174 | 0.8797 | 0.8475 | 1.1075 | 0.3615 | 0.6329 | not resampled |
| body_range_ratio [SMALL] | 40/40 (19 sessions) | 0.7141 | 0.7738 | 0.5823 | 0.8388 | 8/8 (7 sessions) | 0.5863 | 0.6317 | 0.3274 | 0.8292 | 0.1277 | 0.5958 | not resampled |
| directional_body_range_ratio [SMALL] | 40/40 (19 sessions) | 0.7141 | 0.7738 | 0.5823 | 0.8388 | 8/8 (7 sessions) | 0.5863 | 0.6317 | 0.3274 | 0.8292 | 0.1277 | 0.5958 | not resampled |
| close_location [SMALL] | 40/40 (19 sessions) | 0.1640 | 0.1122 | 0.0346 | 0.2342 | 8/8 (7 sessions) | 0.2026 | 0.1405 | 0.0521 | 0.2743 | -0.0386 | -0.2083 | not resampled |
| directional_close_location [SMALL] | 40/40 (19 sessions) | 0.8360 | 0.8878 | 0.7658 | 0.9654 | 8/8 (7 sessions) | 0.7974 | 0.8595 | 0.7257 | 0.9479 | 0.0386 | 0.2083 | not resampled |
| distance_beyond_level [SMALL] | 40/40 (19 sessions) | 0.6149 | 0.4575 | 0.2788 | 0.8312 | 8/8 (7 sessions) | 0.3621 | 0.1050 | 0.0928 | 0.4100 | 0.2527 | 0.5147 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 21/40 (12 sessions) | 0.4445 | 0.3322 | 0.2072 | 0.5740 | 4/8 (4 sessions) | 0.4319 | 0.1016 | 0.1005 | 0.4331 | 0.0126 | 0.0297 | not resampled |
| candle_volume [SMALL] | 40/40 (19 sessions) | 1270434.1250 | 1105901.5000 | 793000.7500 | 1570530.7500 | 8/8 (7 sessions) | 1912997.7500 | 1497658.0000 | 1077928.0000 | 1610222.0000 | -642563.6250 | -0.6769 | not resampled |
| relative_volume_prior_6 [SMALL] | 28/40 (13 sessions) | 1.1247 | 0.9381 | 0.7250 | 1.2100 | 5/8 (4 sessions) | 1.9312 | 1.3303 | 1.2732 | 1.9719 | -0.8065 | -0.8650 | not resampled |
| atr14 [SMALL] | 21/40 (12 sessions) | 1.1310 | 1.2667 | 0.9499 | 1.3028 | 4/8 (4 sessions) | 0.9383 | 0.9256 | 0.8531 | 1.0108 | 0.1926 | 0.7965 | not resampled |
| minutes_since_open [SMALL] | 40/40 (19 sessions) | 98.8750 | 70.0000 | 25.0000 | 152.5000 | 8/8 (7 sessions) | 163.7500 | 70.0000 | 25.0000 | 365.0000 | -64.8750 | -0.6100 | not resampled |
| minutes_since_ema_cross [SMALL] | 10/40 (7 sessions) | 30.5000 | 25.0000 | 12.5000 | 30.0000 | 3/8 (3 sessions) | 38.3333 | 20.0000 | 17.5000 | 50.0000 | -7.8333 | -0.2501 | not resampled |
| break_attempt_rank [SMALL] | 40/40 (19 sessions) | 5.3750 | 5.0000 | 3.0000 | 7.0000 | 8/8 (7 sessions) | 6.5000 | 3.0000 | 1.7500 | 12.2500 | -1.1250 | -0.2893 | not resampled |
| valid_hold_sequence_rank [SMALL] | 40/40 (19 sessions) | 3.0250 | 3.0000 | 2.0000 | 4.0000 | 8/8 (7 sessions) | 3.7500 | 2.5000 | 1.7500 | 5.2500 | -0.7250 | -0.3744 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 18/40 (11 sessions) | 0.3272 | 0.2294 | 0.1214 | 0.4529 | 4/8 (4 sessions) | 0.5057 | 0.4635 | 0.3680 | 0.6013 | -0.1785 | -0.6269 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 18/40 (11 sessions) | 0.3055 | 0.1988 | 0.1066 | 0.5153 | 4/8 (4 sessions) | 0.5276 | 0.5188 | 0.4542 | 0.5923 | -0.2222 | -0.9243 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 25/40 (12 sessions) | -0.1422 | -0.1289 | -0.2567 | 0.0147 | 4/8 (4 sessions) | -0.3456 | -0.3543 | -0.4015 | -0.2984 | 0.2033 | 1.0102 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 24/40 (12 sessions) | -0.0486 | -0.0328 | -0.1326 | 0.0958 | 4/8 (4 sessions) | -0.3039 | -0.3255 | -0.3503 | -0.2791 | 0.2553 | 1.3224 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 21/40 (12 sessions) | -0.0210 | 0.0110 | -0.0924 | 0.0942 | 4/8 (4 sessions) | -0.2382 | -0.2315 | -0.2721 | -0.1976 | 0.2173 | 1.3024 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 15/40 (10 sessions) | -0.0827 | -0.0223 | -0.1523 | 0.0073 | 3/8 (3 sessions) | -0.2203 | -0.2207 | -0.2233 | -0.2175 | 0.1376 | 1.1298 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 14/40 (9 sessions) | -0.0492 | -0.0016 | -0.1210 | 0.0477 | 3/8 (3 sessions) | -0.1960 | -0.2056 | -0.2108 | -0.1860 | 0.1469 | 1.2268 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 14/40 (9 sessions) | -0.0458 | 0.0035 | -0.0991 | 0.0378 | 3/8 (3 sessions) | -0.1588 | -0.1672 | -0.1822 | -0.1396 | 0.1130 | 1.0777 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 40/40 (19 sessions) | -0.1215 | -0.0501 | -0.1734 | -0.0059 | 8/8 (7 sessions) | -0.0896 | -0.0536 | -0.1613 | -0.0319 | -0.0320 | -0.2024 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 36/40 (16 sessions) | -0.0429 | -0.0237 | -0.0534 | 0.0048 | 6/8 (5 sessions) | -0.0293 | -0.0337 | -0.0377 | -0.0322 | -0.0136 | -0.1992 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 33/40 (14 sessions) | -0.0297 | -0.0294 | -0.0502 | 0.0053 | 6/8 (5 sessions) | -0.0402 | -0.0284 | -0.0566 | -0.0260 | 0.0105 | 0.2437 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 13/40 (9 sessions) | 0.4615 | 0.0000 | 0.0000 | 1.0000 | 3/8 (3 sessions) | 0.6667 | 1.0000 | 0.5000 | 1.0000 | -0.2051 | -0.2731 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 10/40 (8 sessions) | 1.3000 | 1.5000 | 0.0000 | 2.0000 | 3/8 (3 sessions) | 0.6667 | 1.0000 | 0.5000 | 1.0000 | 0.6333 | 0.5466 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 4/40 (3 sessions) | 1.7500 | 1.5000 | 1.0000 | 2.2500 | 3/8 (3 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.7500 | 1.0113 | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 21/40 (12 sessions) | 0.1905 | 0.0000 | 0.0000 | 0.0000 | 4/8 (4 sessions) | 0.2500 | 0.0000 | 0.0000 | 0.2500 | -0.0595 | -0.1429 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 18/40 (11 sessions) | 0.4444 | 0.0000 | 0.0000 | 1.0000 | 4/8 (4 sessions) | 0.7500 | 1.0000 | 0.7500 | 1.0000 | -0.3056 | -0.5095 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 10/40 (8 sessions) | 1.2000 | 1.0000 | 1.0000 | 1.0000 | 3/8 (3 sessions) | 1.3333 | 1.0000 | 1.0000 | 1.5000 | -0.1333 | -0.1380 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 13/40 (9 sessions) | 0.3077 | 0.0000 | 0.0000 | 1.0000 | 3/8 (3 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.3077 | 0.6918 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 10/40 (8 sessions) | 0.4000 | 0.0000 | 0.0000 | 1.0000 | 3/8 (3 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.5000 | 0.0667 | 0.1263 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 4/40 (3 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | 3/8 (3 sessions) | 0.3333 | 0.0000 | 0.0000 | 0.5000 | 0.1667 | 0.2887 | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 28/40 (13 sessions) | 1.3571 | 1.0000 | 0.0000 | 2.0000 | 6/8 (5 sessions) | 0.8333 | 1.0000 | 0.2500 | 1.0000 | 0.5238 | 0.4222 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 21/40 (12 sessions) | 1.9524 | 2.0000 | 1.0000 | 2.0000 | 4/8 (4 sessions) | 1.0000 | 1.0000 | 0.7500 | 1.2500 | 0.9524 | 0.6399 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 14/40 (9 sessions) | 3.2143 | 3.0000 | 1.0000 | 5.0000 | 3/8 (3 sessions) | 1.3333 | 1.0000 | 1.0000 | 1.5000 | 1.8810 | 0.8195 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 28/40 (13 sessions) | 2.7590 | 2.6000 | 2.1995 | 3.1900 | 6/8 (5 sessions) | 3.1313 | 3.1750 | 2.8300 | 3.7660 | -0.3723 | -0.3952 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 21/40 (12 sessions) | 3.4891 | 3.3900 | 2.5100 | 3.8600 | 4/8 (4 sessions) | 3.3000 | 3.5050 | 2.9975 | 3.8075 | 0.1891 | 0.1357 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 14/40 (9 sessions) | 4.3518 | 4.2800 | 3.4725 | 5.2949 | 3/8 (3 sessions) | 4.8000 | 4.2800 | 4.2800 | 5.0600 | -0.4482 | -0.3023 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 21/40 (12 sessions) | 2.2586 | 2.3285 | 1.9661 | 2.4779 | 4/8 (4 sessions) | 3.0513 | 2.9582 | 2.4022 | 3.6072 | -0.7927 | -1.2736 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 21/40 (12 sessions) | 2.9951 | 2.8055 | 2.5628 | 3.2597 | 4/8 (4 sessions) | 3.4986 | 3.6030 | 2.8730 | 4.2286 | -0.5035 | -0.6032 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 14/40 (9 sessions) | 4.0703 | 3.7074 | 3.3826 | 4.9440 | 3/8 (3 sessions) | 4.8463 | 4.9003 | 4.6389 | 5.0807 | -0.7760 | -0.9505 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 28/40 (13 sessions) | 0.3998 | 0.3924 | 0.1479 | 0.6525 | 6/8 (5 sessions) | 0.5935 | 0.6077 | 0.4274 | 0.8858 | -0.1937 | -0.6727 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 21/40 (12 sessions) | 0.2552 | 0.1637 | 0.0667 | 0.3399 | 4/8 (4 sessions) | 0.4623 | 0.5120 | 0.3886 | 0.5857 | -0.2071 | -0.8643 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 14/40 (9 sessions) | 0.2028 | 0.2142 | 0.0652 | 0.2510 | 3/8 (3 sessions) | 0.3072 | 0.3109 | 0.2808 | 0.3354 | -0.1044 | -0.7840 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 28/40 (13 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 6/8 (5 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 21/40 (12 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 4/8 (4 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 14/40 (9 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 3/8 (3 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 28/40 (13 sessions) | 0.5357 | 0.5000 | 0.4375 | 0.7500 | 6/8 (5 sessions) | 0.2500 | 0.2500 | 0.2500 | 0.2500 | 0.2857 | 1.2344 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 21/40 (12 sessions) | 0.4857 | 0.4000 | 0.4000 | 0.6000 | 4/8 (4 sessions) | 0.3500 | 0.3500 | 0.2750 | 0.4250 | 0.1357 | 0.8433 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 14/40 (9 sessions) | 0.4935 | 0.5227 | 0.4545 | 0.5795 | 3/8 (3 sessions) | 0.5000 | 0.4545 | 0.4318 | 0.5455 | -0.0065 | -0.0663 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 21/40 (12 sessions) | 1.0236 | 0.7722 | 0.3285 | 1.6771 | 4/8 (4 sessions) | 2.2375 | 2.0418 | 1.7165 | 2.5628 | -1.2140 | -1.4271 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 21/40 (12 sessions) | 0.5769 | 0.4926 | 0.2184 | 0.7413 | 4/8 (4 sessions) | 0.7545 | 0.8381 | 0.4174 | 1.1752 | -0.1776 | -0.4004 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 18/40 (11 sessions) | 0.3485 | 0.2290 | 0.1260 | 0.4645 | 4/8 (4 sessions) | 0.4277 | 0.4540 | 0.3088 | 0.5729 | -0.0792 | -0.2511 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 33/40 (17 sessions) | 2.6775 | 1.3900 | 0.7800 | 4.1700 | 6/8 (6 sessions) | 4.2972 | 3.3550 | 1.7262 | 5.7698 | -1.6197 | -0.5495 | not resampled |
| stage11_2.room_in_atr [SMALL] | 18/40 (11 sessions) | 3.0466 | 1.3646 | 0.7211 | 5.7833 | 3/8 (3 sessions) | 6.6488 | 5.9454 | 3.8736 | 9.0723 | -3.6021 | -1.0500 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 40/40 (19 sessions) | 4.6000 | 5.0000 | 4.0000 | 5.0000 | 8/8 (7 sessions) | 4.7500 | 4.5000 | 4.0000 | 5.2500 | -0.1500 | -0.1670 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 40/40 (19 sessions) | 1.4000 | 1.0000 | 1.0000 | 2.0000 | 8/8 (7 sessions) | 1.2500 | 1.5000 | 0.7500 | 2.0000 | 0.1500 | 0.1670 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 40/40 (19 sessions) | 0.5579 | 0.4025 | 0.2788 | 0.7375 | 8/8 (7 sessions) | 0.3396 | 0.1035 | 0.0662 | 0.3875 | 0.2182 | 0.4780 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 33/40 (17 sessions) | 2.6775 | 1.3900 | 0.7800 | 4.1700 | 6/8 (6 sessions) | 4.2972 | 3.3550 | 1.7262 | 5.7698 | -1.6197 | -0.5495 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 21/40 (12 sessions) | 0.1429 | 0.0000 | 0.0000 | 0.0000 | 4/8 (4 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1429 | 0.4272 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 21/40 (12 sessions) | 0.3810 | 0.0000 | 0.0000 | 1.0000 | 4/8 (4 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.3810 | 0.6929 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 26/40 (12 sessions) | 2.3608 | 1.9600 | 1.5400 | 2.9175 | 4/8 (4 sessions) | 2.7912 | 2.7375 | 2.2850 | 3.2438 | -0.4305 | -0.2683 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 27/40 (13 sessions) | 1.2226 | 1.1710 | 0.5375 | 1.7050 | 6/8 (5 sessions) | 1.3530 | 1.4375 | 1.0775 | 1.6760 | -0.1304 | -0.1449 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 21/40 (12 sessions) | 1.7730 | 1.5671 | 1.2369 | 2.0508 | 4/8 (4 sessions) | 2.9677 | 2.8292 | 2.2067 | 3.5902 | -1.1946 | -0.9673 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 21/40 (12 sessions) | 1.1299 | 1.1258 | 0.4536 | 1.4751 | 4/8 (4 sessions) | 1.3688 | 1.4114 | 0.7811 | 1.9990 | -0.2388 | -0.3065 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | SHORT | 48 | 19 | 40 | 8 | 100.00% | 100.00% | 83.33% |
| time_bucket | 09:35-10:00 [SMALL] | 14 | 13 | 12 | 2 | 30.00% | 25.00% | 85.71% |
| time_bucket | 10:00-10:30 [SMALL] | 9 | 9 | 7 | 2 | 17.50% | 25.00% | 77.78% |
| time_bucket | 10:30-11:00 [SMALL] | 2 | 2 | 2 | 0 | 5.00% | 0.00% | 100.00% |
| time_bucket | 11:00-12:00 [SMALL] | 8 | 7 | 7 | 1 | 17.50% | 12.50% | 87.50% |
| time_bucket | 12:00-13:30 [SMALL] | 8 | 6 | 8 | 0 | 20.00% | 0.00% | 100.00% |
| time_bucket | 13:30-15:00 [SMALL] | 3 | 2 | 3 | 0 | 7.50% | 0.00% | 100.00% |
| time_bucket | 15:00-close [SMALL] | 4 | 3 | 1 | 3 | 2.50% | 37.50% | 25.00% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 15 | 9 | 11 | 4 | 27.50% | 50.00% | 73.33% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 7 | 5 | 7 | 0 | 17.50% | 0.00% | 100.00% |
| ema9_20_alignment | EMA_UNAVAILABLE [SMALL] | 26 | 16 | 22 | 4 | 55.00% | 50.00% | 84.62% |
| price_vwap_alignment | VWAP_ALIGNED | 44 | 19 | 36 | 8 | 90.00% | 100.00% | 81.82% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 4 | 2 | 4 | 0 | 10.00% | 0.00% | 100.00% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED [SMALL] | 27 | 13 | 23 | 4 | 57.50% | 50.00% | 85.19% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 4 | 3 | 4 | 0 | 10.00% | 0.00% | 100.00% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 17 | 13 | 13 | 4 | 32.50% | 50.00% | 76.47% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 18 | 11 | 15 | 3 | 37.50% | 37.50% | 83.33% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 4 | 4 | 3 | 1 | 7.50% | 12.50% | 75.00% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE [SMALL] | 26 | 16 | 22 | 4 | 55.00% | 50.00% | 84.62% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 9 | 6 | 6 | 3 | 15.00% | 37.50% | 66.67% |
| prior_ema_cross | NO_PRIOR_CROSS | 35 | 17 | 30 | 5 | 75.00% | 62.50% | 85.71% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 4 | 4 | 4 | 0 | 10.00% | 0.00% | 100.00% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 34 | 15 | 30 | 4 | 75.00% | 50.00% | 88.24% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 14 | 8 | 10 | 4 | 25.00% | 50.00% | 71.43% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 4 | 4 | 4 | 0 | 10.00% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 2 | 2 | 2 | 0 | 5.00% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 3 | 2 | 2 | 1 | 5.00% | 12.50% | 66.67% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 1 | 1 | 1 | 0 | 2.50% | 0.00% | 100.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 8 | 3 | 6 | 2 | 15.00% | 25.00% | 75.00% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 3 | 2 | 3 | 0 | 7.50% | 0.00% | 100.00% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 9 | 3 | 7 | 2 | 17.50% | 25.00% | 77.78% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 18 | 14 | 15 | 3 | 37.50% | 37.50% | 83.33% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 48 | 19 | 40 | 8 | 100.00% | 100.00% | 83.33% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 7 | 6 | 7 | 0 | 17.50% | 0.00% | 100.00% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 5 | 5 | 4 | 1 | 10.00% | 12.50% | 80.00% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 8 | 6 | 6 | 2 | 15.00% | 25.00% | 75.00% |
| stage11_3.structure | UNAVAILABLE [SMALL] | 28 | 17 | 23 | 5 | 57.50% | 62.50% | 82.14% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 7 | 6 | 7 | 0 | 17.50% | 0.00% | 100.00% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 13 | 8 | 10 | 3 | 25.00% | 37.50% | 76.92% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE [SMALL] | 28 | 17 | 23 | 5 | 57.50% | 62.50% | 82.14% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 9 | 6 | 8 | 1 | 20.00% | 12.50% | 88.89% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 16 | 10 | 13 | 3 | 32.50% | 37.50% | 81.25% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 23 | 15 | 19 | 4 | 47.50% | 50.00% | 82.61% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 10 | 7 | 7 | 3 | 17.50% | 37.50% | 70.00% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 10 | 9 | 10 | 0 | 25.00% | 0.00% | 100.00% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 28 | 17 | 23 | 5 | 57.50% | 62.50% | 82.14% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 15 | 14 | 13 | 2 | 32.50% | 25.00% | 86.67% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 6 | 3 | 4 | 2 | 10.00% | 25.00% | 66.67% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 9 | 4 | 9 | 0 | 22.50% | 0.00% | 100.00% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 18 | 10 | 14 | 4 | 35.00% | 50.00% | 77.78% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 48 | 19 | 40 | 8 | 100.00% | 100.00% | 83.33% |


### 2026-04


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 27/27 (14 sessions) | 1.2470 | 1.1800 | 0.9510 | 1.7000 | 14/14 (11 sessions) | 1.3236 | 1.3350 | 0.9428 | 1.6250 | -0.0766 | -0.1827 | not resampled |
| body_size [SMALL] | 27/27 (14 sessions) | 0.7573 | 0.4800 | 0.2675 | 1.2500 | 14/14 (11 sessions) | 0.5361 | 0.3776 | 0.3250 | 0.7000 | 0.2213 | 0.3961 | not resampled |
| directional_body [SMALL] | 27/27 (14 sessions) | 0.7573 | 0.4800 | 0.2675 | 1.2500 | 14/14 (11 sessions) | 0.5361 | 0.3776 | 0.3250 | 0.7000 | 0.2213 | 0.3961 | not resampled |
| candle_range [SMALL] | 27/27 (14 sessions) | 1.1226 | 0.8880 | 0.6400 | 1.6375 | 14/14 (11 sessions) | 0.9414 | 0.8850 | 0.6512 | 1.1212 | 0.1812 | 0.3142 | not resampled |
| body_range_ratio [SMALL] | 27/27 (14 sessions) | 0.6051 | 0.6234 | 0.4067 | 0.8371 | 14/14 (11 sessions) | 0.5460 | 0.5571 | 0.4378 | 0.6527 | 0.0591 | 0.2640 | not resampled |
| directional_body_range_ratio [SMALL] | 27/27 (14 sessions) | 0.6051 | 0.6234 | 0.4067 | 0.8371 | 14/14 (11 sessions) | 0.5460 | 0.5571 | 0.4378 | 0.6527 | 0.0591 | 0.2640 | not resampled |
| close_location [SMALL] | 27/27 (14 sessions) | 0.2280 | 0.1875 | 0.0855 | 0.3649 | 14/14 (11 sessions) | 0.2503 | 0.2343 | 0.1630 | 0.3600 | -0.0223 | -0.1296 | not resampled |
| directional_close_location [SMALL] | 27/27 (14 sessions) | 0.7720 | 0.8125 | 0.6351 | 0.9145 | 14/14 (11 sessions) | 0.7497 | 0.7657 | 0.6400 | 0.8370 | 0.0223 | 0.1296 | not resampled |
| distance_beyond_level [SMALL] | 27/27 (14 sessions) | 0.4646 | 0.1900 | 0.1175 | 0.6450 | 14/14 (11 sessions) | 0.2233 | 0.2000 | 0.0375 | 0.2938 | 0.2413 | 0.5514 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 18/27 (10 sessions) | 0.4329 | 0.2407 | 0.1297 | 0.6957 | 6/14 (5 sessions) | 0.2992 | 0.2778 | 0.0919 | 0.4948 | 0.1337 | 0.3090 | not resampled |
| candle_volume [SMALL] | 27/27 (14 sessions) | 799524.0370 | 681862.0000 | 493851.0000 | 994806.5000 | 14/14 (11 sessions) | 859280.2143 | 604300.5000 | 503083.0000 | 1070688.5000 | -59756.1772 | -0.1129 | not resampled |
| relative_volume_prior_6 [SMALL] | 19/27 (11 sessions) | 1.7092 | 1.3168 | 0.9188 | 2.4241 | 8/14 (6 sessions) | 1.7028 | 0.9299 | 0.7215 | 1.4984 | 0.0064 | 0.0049 | not resampled |
| atr14 [SMALL] | 18/27 (10 sessions) | 0.6282 | 0.6297 | 0.5595 | 0.6908 | 6/14 (5 sessions) | 0.7217 | 0.6612 | 0.6071 | 0.7244 | -0.0936 | -0.6607 | not resampled |
| minutes_since_open [SMALL] | 27/27 (14 sessions) | 145.3704 | 110.0000 | 27.5000 | 255.0000 | 14/14 (11 sessions) | 79.6429 | 42.5000 | 16.2500 | 127.5000 | 65.7275 | 0.6067 | not resampled |
| minutes_since_ema_cross [SMALL] | 12/27 (6 sessions) | 61.2500 | 65.0000 | 13.7500 | 88.7500 | 4/14 (3 sessions) | 38.7500 | 37.5000 | 30.0000 | 46.2500 | 22.5000 | 0.5376 | not resampled |
| break_attempt_rank [SMALL] | 27/27 (14 sessions) | 6.5556 | 6.0000 | 3.0000 | 10.5000 | 14/14 (11 sessions) | 5.0000 | 4.5000 | 2.2500 | 6.7500 | 1.5556 | 0.3634 | not resampled |
| valid_hold_sequence_rank [SMALL] | 27/27 (14 sessions) | 3.7037 | 4.0000 | 2.0000 | 5.0000 | 14/14 (11 sessions) | 2.6429 | 2.0000 | 1.0000 | 3.0000 | 1.0608 | 0.5039 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 14/27 (8 sessions) | 0.1837 | 0.1639 | 0.1151 | 0.2364 | 4/14 (3 sessions) | 0.2944 | 0.1914 | 0.1637 | 0.3221 | -0.1108 | -0.7457 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 14/27 (8 sessions) | 0.3085 | 0.2882 | 0.2279 | 0.3876 | 4/14 (3 sessions) | 0.3686 | 0.3211 | 0.2735 | 0.4163 | -0.0601 | -0.3453 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 19/27 (11 sessions) | -0.1278 | -0.1120 | -0.1934 | -0.0663 | 7/14 (5 sessions) | -0.1109 | -0.1425 | -0.1539 | -0.0820 | -0.0169 | -0.1283 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 19/27 (11 sessions) | -0.0769 | -0.0629 | -0.1165 | -0.0132 | 6/14 (5 sessions) | -0.0494 | -0.0862 | -0.1156 | -0.0534 | -0.0275 | -0.2221 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 19/27 (11 sessions) | -0.0558 | -0.0750 | -0.1196 | 0.0155 | 6/14 (5 sessions) | -0.0394 | -0.0857 | -0.0988 | -0.0537 | -0.0164 | -0.1490 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 14/27 (8 sessions) | -0.0496 | -0.0524 | -0.0720 | 0.0051 | 4/14 (3 sessions) | -0.0395 | -0.0701 | -0.0880 | -0.0216 | -0.0101 | -0.1167 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 14/27 (8 sessions) | -0.0240 | -0.0098 | -0.0504 | 0.0166 | 4/14 (3 sessions) | -0.0055 | -0.0525 | -0.0562 | -0.0018 | -0.0185 | -0.2324 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 13/27 (7 sessions) | -0.0085 | 0.0154 | -0.0520 | 0.0279 | 4/14 (3 sessions) | 0.0031 | -0.0450 | -0.0507 | 0.0087 | -0.0116 | -0.1606 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 27/27 (14 sessions) | -0.0915 | -0.0223 | -0.1595 | 0.0009 | 14/14 (11 sessions) | -0.1088 | -0.0603 | -0.1835 | -0.0315 | 0.0173 | 0.1373 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 24/27 (13 sessions) | -0.0354 | -0.0104 | -0.0730 | 0.0044 | 12/14 (9 sessions) | -0.0618 | -0.0366 | -0.0830 | -0.0247 | 0.0264 | 0.4358 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 23/27 (12 sessions) | -0.0402 | -0.0067 | -0.0722 | 0.0071 | 10/14 (7 sessions) | -0.0255 | -0.0308 | -0.0443 | -0.0102 | -0.0147 | -0.2597 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 13/27 (7 sessions) | 0.3077 | 0.0000 | 0.0000 | 1.0000 | 4/14 (3 sessions) | 0.2500 | 0.0000 | 0.0000 | 0.2500 | 0.0577 | 0.1191 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 12/27 (6 sessions) | 0.4167 | 0.0000 | 0.0000 | 1.0000 | 3/14 (3 sessions) | 0.6667 | 1.0000 | 0.5000 | 1.0000 | -0.2500 | -0.4762 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 10/27 (6 sessions) | 0.8000 | 1.0000 | 1.0000 | 1.0000 | 1/14 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | -0.2000 | N/A | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 18/27 (10 sessions) | 0.4444 | 0.0000 | 0.0000 | 1.0000 | 6/14 (5 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | -0.0556 | -0.1069 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 14/27 (8 sessions) | 0.6429 | 0.5000 | 0.0000 | 1.0000 | 4/14 (3 sessions) | 0.7500 | 1.0000 | 0.7500 | 1.0000 | -0.1071 | -0.1358 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 12/27 (6 sessions) | 0.6667 | 1.0000 | 0.0000 | 1.0000 | 3/14 (3 sessions) | 1.0000 | 1.0000 | 0.5000 | 1.5000 | -0.3333 | -0.5563 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 13/27 (7 sessions) | 0.1538 | 0.0000 | 0.0000 | 0.0000 | 4/14 (3 sessions) | 0.2500 | 0.0000 | 0.0000 | 0.2500 | -0.0962 | -0.2383 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 12/27 (6 sessions) | 0.3333 | 0.0000 | 0.0000 | 1.0000 | 3/14 (3 sessions) | 0.6667 | 1.0000 | 0.5000 | 1.0000 | -0.3333 | -0.6583 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 10/27 (6 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | 1/14 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.5000 | N/A | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 20/27 (11 sessions) | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 8/14 (6 sessions) | 1.6250 | 2.0000 | 0.0000 | 3.0000 | -0.6250 | -0.5321 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 19/27 (11 sessions) | 2.1053 | 2.0000 | 1.0000 | 3.0000 | 6/14 (5 sessions) | 3.3333 | 3.5000 | 3.0000 | 4.0000 | -1.2281 | -0.9666 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 13/27 (7 sessions) | 3.1538 | 4.0000 | 1.0000 | 5.0000 | 4/14 (3 sessions) | 4.0000 | 5.0000 | 4.0000 | 5.0000 | -0.8462 | -0.3983 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 20/27 (11 sessions) | 1.7831 | 1.5700 | 1.2538 | 2.1638 | 8/14 (6 sessions) | 1.6162 | 1.6500 | 1.5375 | 1.8100 | 0.1669 | 0.2285 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 19/27 (11 sessions) | 2.0909 | 1.8900 | 1.6000 | 2.6775 | 6/14 (5 sessions) | 2.3983 | 1.9750 | 1.9125 | 2.3075 | -0.3074 | -0.3566 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 13/27 (7 sessions) | 2.6141 | 2.7300 | 1.8300 | 3.2480 | 4/14 (3 sessions) | 3.7175 | 2.9900 | 2.9800 | 3.7275 | -1.1034 | -0.9416 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 18/27 (10 sessions) | 2.5879 | 2.4676 | 2.2161 | 2.9031 | 6/14 (5 sessions) | 2.3732 | 2.4287 | 1.8637 | 2.8744 | 0.2147 | 0.2628 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 18/27 (10 sessions) | 3.2409 | 3.0649 | 2.6105 | 3.8395 | 6/14 (5 sessions) | 3.2625 | 2.9861 | 2.7442 | 3.8501 | -0.0216 | -0.0282 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 13/27 (7 sessions) | 4.3086 | 4.1752 | 3.2443 | 5.0053 | 4/14 (3 sessions) | 5.0571 | 5.0205 | 4.9110 | 5.1667 | -0.7486 | -0.6487 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 20/27 (11 sessions) | 0.6054 | 0.5355 | 0.4205 | 0.8508 | 8/14 (6 sessions) | 0.3946 | 0.2856 | 0.2480 | 0.5691 | 0.2107 | 0.7904 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 19/27 (11 sessions) | 0.3356 | 0.2690 | 0.1334 | 0.5326 | 6/14 (5 sessions) | 0.3064 | 0.3097 | 0.1721 | 0.4724 | 0.0292 | 0.1342 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 13/27 (7 sessions) | 0.1796 | 0.1595 | 0.0347 | 0.2618 | 4/14 (3 sessions) | 0.2207 | 0.2152 | 0.1884 | 0.2474 | -0.0411 | -0.2861 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 20/27 (11 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 8/14 (6 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 19/27 (11 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 6/14 (5 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 13/27 (7 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 4/14 (3 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 20/27 (11 sessions) | 0.5250 | 0.5000 | 0.4375 | 0.7500 | 8/14 (6 sessions) | 0.5000 | 0.3750 | 0.2500 | 0.7500 | 0.0250 | 0.0934 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 19/27 (11 sessions) | 0.4737 | 0.5000 | 0.3500 | 0.6000 | 6/14 (5 sessions) | 0.4667 | 0.5000 | 0.4250 | 0.5000 | 0.0070 | 0.0539 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 13/27 (7 sessions) | 0.4510 | 0.4545 | 0.3636 | 0.5455 | 4/14 (3 sessions) | 0.4545 | 0.4318 | 0.3977 | 0.4886 | -0.0035 | -0.0291 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 18/27 (10 sessions) | 1.0417 | 0.9559 | 0.4287 | 1.3979 | 6/14 (5 sessions) | 1.2203 | 1.1999 | 0.8718 | 1.4519 | -0.1785 | -0.2172 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 18/27 (10 sessions) | 0.6231 | 0.4152 | 0.3108 | 0.7029 | 6/14 (5 sessions) | 0.4570 | 0.2865 | 0.2672 | 0.4923 | 0.1661 | 0.3013 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 14/27 (8 sessions) | 0.5444 | 0.2343 | 0.1714 | 0.6920 | 4/14 (3 sessions) | 0.3031 | 0.2935 | 0.1607 | 0.4359 | 0.2413 | 0.4177 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 27/27 (14 sessions) | 1.8195 | 1.3400 | 0.4050 | 1.9950 | 14/14 (11 sessions) | 1.5018 | 1.4750 | 0.4650 | 2.1850 | 0.3177 | 0.1360 | not resampled |
| stage11_2.room_in_atr [SMALL] | 18/27 (10 sessions) | 2.2130 | 1.5829 | 0.4644 | 3.1779 | 6/14 (5 sessions) | 1.2498 | 0.8366 | 0.5243 | 1.8079 | 0.9631 | 0.4972 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 27/27 (14 sessions) | 4.1852 | 4.0000 | 4.0000 | 5.0000 | 14/14 (11 sessions) | 4.1429 | 4.0000 | 4.0000 | 4.7500 | 0.0423 | 0.0594 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 27/27 (14 sessions) | 1.8148 | 2.0000 | 1.0000 | 2.0000 | 14/14 (11 sessions) | 1.8571 | 2.0000 | 1.2500 | 2.0000 | -0.0423 | -0.0594 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 27/27 (14 sessions) | 0.3328 | 0.1900 | 0.0925 | 0.5193 | 14/14 (11 sessions) | 0.1632 | 0.1200 | 0.0375 | 0.2712 | 0.1695 | 0.5498 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 27/27 (14 sessions) | 1.8195 | 1.3400 | 0.4050 | 1.9950 | 14/14 (11 sessions) | 1.5018 | 1.4750 | 0.4650 | 2.1850 | 0.3177 | 0.1360 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 18/27 (10 sessions) | 0.2778 | 0.0000 | 0.0000 | 0.7500 | 6/14 (5 sessions) | 0.1667 | 0.0000 | 0.0000 | 0.0000 | 0.1111 | 0.2472 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 18/27 (10 sessions) | 0.5000 | 0.0000 | 0.0000 | 1.0000 | 6/14 (5 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 19/27 (11 sessions) | 1.4284 | 1.2900 | 1.0950 | 1.7468 | 8/14 (6 sessions) | 1.2562 | 1.3200 | 1.0600 | 1.4325 | 0.1722 | 0.2486 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 18/27 (10 sessions) | 0.7465 | 0.5543 | 0.3362 | 0.8562 | 7/14 (5 sessions) | 0.8521 | 0.5549 | 0.4350 | 0.6300 | -0.1056 | -0.1326 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 18/27 (10 sessions) | 2.1668 | 2.0921 | 1.6540 | 2.5174 | 6/14 (5 sessions) | 1.9317 | 2.0493 | 1.8782 | 2.1342 | 0.2351 | 0.2289 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 17/27 (9 sessions) | 1.1835 | 0.9108 | 0.6054 | 1.3908 | 6/14 (5 sessions) | 1.1621 | 0.8508 | 0.7520 | 1.1094 | 0.0213 | 0.0221 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | SHORT | 41 | 17 | 27 | 14 | 100.00% | 100.00% | 65.85% |
| time_bucket | 09:35-10:00 [SMALL] | 13 | 11 | 7 | 6 | 25.93% | 42.86% | 53.85% |
| time_bucket | 10:00-10:30 [SMALL] | 3 | 3 | 1 | 2 | 3.70% | 14.29% | 33.33% |
| time_bucket | 10:30-11:00 [SMALL] | 7 | 5 | 5 | 2 | 18.52% | 14.29% | 71.43% |
| time_bucket | 11:00-12:00 [SMALL] | 3 | 3 | 2 | 1 | 7.41% | 7.14% | 66.67% |
| time_bucket | 12:00-13:30 [SMALL] | 7 | 5 | 5 | 2 | 18.52% | 14.29% | 71.43% |
| time_bucket | 13:30-15:00 [SMALL] | 6 | 5 | 5 | 1 | 18.52% | 7.14% | 83.33% |
| time_bucket | 15:00-close [SMALL] | 2 | 1 | 2 | 0 | 7.41% | 0.00% | 100.00% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 9 | 5 | 6 | 3 | 22.22% | 21.43% | 66.67% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 9 | 5 | 8 | 1 | 29.63% | 7.14% | 88.89% |
| ema9_20_alignment | EMA_UNAVAILABLE [SMALL] | 23 | 14 | 13 | 10 | 48.15% | 71.43% | 56.52% |
| price_vwap_alignment | VWAP_ALIGNED | 34 | 17 | 21 | 13 | 77.78% | 92.86% | 61.76% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 7 | 3 | 6 | 1 | 22.22% | 7.14% | 85.71% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED [SMALL] | 13 | 8 | 9 | 4 | 33.33% | 28.57% | 69.23% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 13 | 6 | 10 | 3 | 37.04% | 21.43% | 76.92% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 15 | 11 | 8 | 7 | 29.63% | 50.00% | 53.33% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 7 | 5 | 6 | 1 | 22.22% | 7.14% | 85.71% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 11 | 6 | 8 | 3 | 29.63% | 21.43% | 72.73% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE [SMALL] | 23 | 14 | 13 | 10 | 48.15% | 71.43% | 56.52% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 8 | 4 | 5 | 3 | 18.52% | 21.43% | 62.50% |
| prior_ema_cross | NO_PRIOR_CROSS [SMALL] | 25 | 15 | 15 | 10 | 55.56% | 71.43% | 60.00% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 8 | 4 | 7 | 1 | 25.93% | 7.14% | 87.50% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE [SMALL] | 24 | 12 | 17 | 7 | 62.96% | 50.00% | 70.83% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 17 | 9 | 10 | 7 | 37.04% | 50.00% | 58.82% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 5 | 4 | 3 | 2 | 11.11% | 14.29% | 60.00% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 2 | 2 | 1 | 1 | 3.70% | 7.14% | 50.00% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 4 | 4 | 3 | 1 | 11.11% | 7.14% | 75.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 7 | 3 | 6 | 1 | 22.22% | 7.14% | 85.71% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 6 | 5 | 5 | 1 | 18.52% | 7.14% | 83.33% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 17 | 12 | 9 | 8 | 33.33% | 57.14% | 52.94% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 41 | 17 | 27 | 14 | 100.00% | 100.00% | 65.85% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 7 | 5 | 4 | 3 | 14.81% | 21.43% | 57.14% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 6 | 5 | 6 | 0 | 22.22% | 0.00% | 100.00% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 8 | 6 | 5 | 3 | 18.52% | 21.43% | 62.50% |
| stage11_3.structure | UNAVAILABLE [SMALL] | 20 | 13 | 12 | 8 | 44.44% | 57.14% | 60.00% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 7 | 5 | 4 | 3 | 14.81% | 21.43% | 57.14% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 14 | 8 | 11 | 3 | 40.74% | 21.43% | 78.57% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE [SMALL] | 20 | 13 | 12 | 8 | 44.44% | 57.14% | 60.00% |
| stage11_3.high_structure | EQUAL_HIGH [SMALL] | 1 | 1 | 1 | 0 | 3.70% | 0.00% | 100.00% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 7 | 6 | 7 | 0 | 25.93% | 0.00% | 100.00% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 16 | 8 | 9 | 7 | 33.33% | 50.00% | 56.25% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 17 | 11 | 10 | 7 | 37.04% | 50.00% | 58.82% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 13 | 7 | 10 | 3 | 37.04% | 21.43% | 76.92% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 8 | 5 | 5 | 3 | 18.52% | 21.43% | 62.50% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 20 | 13 | 12 | 8 | 44.44% | 57.14% | 60.00% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 16 | 11 | 9 | 7 | 33.33% | 50.00% | 56.25% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 6 | 4 | 4 | 2 | 14.81% | 14.29% | 66.67% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 19 | 10 | 14 | 5 | 51.85% | 35.71% | 73.68% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 41 | 17 | 27 | 14 | 100.00% | 100.00% | 65.85% |


### 2026-05


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 22/22 (11 sessions) | 1.2350 | 1.0700 | 0.9400 | 1.2125 | 18/18 (12 sessions) | 1.2011 | 1.0600 | 0.9650 | 1.1400 | 0.0339 | 0.0673 | not resampled |
| body_size [SMALL] | 22/22 (11 sessions) | 0.7569 | 0.5903 | 0.3325 | 1.0400 | 18/18 (12 sessions) | 0.4955 | 0.3676 | 0.1938 | 0.6125 | 0.2613 | 0.5340 | not resampled |
| directional_body [SMALL] | 22/22 (11 sessions) | 0.7569 | 0.5903 | 0.3325 | 1.0400 | 18/18 (12 sessions) | 0.4955 | 0.3676 | 0.1938 | 0.6125 | 0.2613 | 0.5340 | not resampled |
| candle_range [SMALL] | 22/22 (11 sessions) | 1.0201 | 0.8400 | 0.5175 | 1.2850 | 18/18 (12 sessions) | 0.8358 | 0.6550 | 0.5350 | 0.9215 | 0.1843 | 0.3175 | not resampled |
| body_range_ratio [SMALL] | 22/22 (11 sessions) | 0.7044 | 0.7387 | 0.6649 | 0.8086 | 18/18 (12 sessions) | 0.5635 | 0.5833 | 0.3498 | 0.7183 | 0.1408 | 0.6564 | not resampled |
| directional_body_range_ratio [SMALL] | 22/22 (11 sessions) | 0.7044 | 0.7387 | 0.6649 | 0.8086 | 18/18 (12 sessions) | 0.5635 | 0.5833 | 0.3498 | 0.7183 | 0.1408 | 0.6564 | not resampled |
| close_location [SMALL] | 22/22 (11 sessions) | 0.1444 | 0.1262 | 0.0889 | 0.1762 | 18/18 (12 sessions) | 0.2145 | 0.1603 | 0.0954 | 0.2338 | -0.0701 | -0.4791 | not resampled |
| directional_close_location [SMALL] | 22/22 (11 sessions) | 0.8556 | 0.8738 | 0.8238 | 0.9111 | 18/18 (12 sessions) | 0.7855 | 0.8397 | 0.7662 | 0.9046 | 0.0701 | 0.4791 | not resampled |
| distance_beyond_level [SMALL] | 22/22 (11 sessions) | 0.3696 | 0.3075 | 0.2175 | 0.4725 | 18/18 (12 sessions) | 0.1574 | 0.0975 | 0.0700 | 0.1688 | 0.2121 | 0.9360 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 12/22 (9 sessions) | 0.4195 | 0.4264 | 0.3488 | 0.5399 | 9/18 (6 sessions) | 0.2057 | 0.1479 | 0.1328 | 0.2844 | 0.2138 | 1.0617 | not resampled |
| candle_volume [SMALL] | 22/22 (11 sessions) | 677201.1364 | 603643.5000 | 416551.0000 | 804020.2500 | 18/18 (12 sessions) | 658591.6667 | 502213.0000 | 395445.5000 | 751889.0000 | 18609.4697 | 0.0413 | not resampled |
| relative_volume_prior_6 [SMALL] | 17/22 (10 sessions) | 1.2236 | 1.1816 | 0.7432 | 1.5669 | 10/18 (7 sessions) | 1.3719 | 1.1321 | 0.8157 | 1.2646 | -0.1484 | -0.1953 | not resampled |
| atr14 [SMALL] | 12/22 (9 sessions) | 0.6437 | 0.6023 | 0.5737 | 0.7222 | 9/18 (6 sessions) | 0.4694 | 0.4774 | 0.3879 | 0.5271 | 0.1743 | 1.4558 | not resampled |
| minutes_since_open [SMALL] | 22/22 (11 sessions) | 138.8636 | 77.5000 | 41.2500 | 202.5000 | 18/18 (12 sessions) | 178.6111 | 155.0000 | 16.2500 | 330.0000 | -39.7475 | -0.2675 | not resampled |
| minutes_since_ema_cross [SMALL] | 9/22 (7 sessions) | 52.2222 | 60.0000 | 30.0000 | 75.0000 | 9/18 (6 sessions) | 63.8889 | 75.0000 | 35.0000 | 95.0000 | -11.6667 | -0.3202 | not resampled |
| break_attempt_rank [SMALL] | 22/22 (11 sessions) | 7.2273 | 7.0000 | 3.0000 | 10.0000 | 18/18 (12 sessions) | 6.7778 | 5.5000 | 2.2500 | 10.5000 | 0.4495 | 0.0758 | not resampled |
| valid_hold_sequence_rank [SMALL] | 22/22 (11 sessions) | 3.9091 | 3.0000 | 2.2500 | 4.0000 | 18/18 (12 sessions) | 4.1111 | 4.0000 | 1.2500 | 5.7500 | -0.2020 | -0.0638 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 10/22 (8 sessions) | 0.3082 | 0.3239 | 0.1137 | 0.4995 | 9/18 (6 sessions) | 0.2790 | 0.1790 | 0.1064 | 0.3969 | 0.0292 | 0.1277 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 10/22 (8 sessions) | 0.4952 | 0.5512 | 0.1576 | 0.7618 | 9/18 (6 sessions) | 0.5452 | 0.3750 | 0.2744 | 0.7530 | -0.0500 | -0.1338 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 15/22 (10 sessions) | -0.1620 | -0.1163 | -0.2647 | -0.0728 | 9/18 (6 sessions) | -0.0966 | -0.0864 | -0.2075 | -0.0366 | -0.0654 | -0.4335 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 15/22 (10 sessions) | -0.0956 | -0.1034 | -0.1917 | -0.0025 | 9/18 (6 sessions) | -0.0651 | -0.0472 | -0.1671 | -0.0150 | -0.0305 | -0.2306 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 13/22 (10 sessions) | -0.0805 | -0.1292 | -0.1689 | -0.0004 | 9/18 (6 sessions) | -0.0476 | -0.0243 | -0.1418 | -0.0143 | -0.0329 | -0.2846 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 10/22 (8 sessions) | -0.0753 | -0.0965 | -0.1337 | -0.0355 | 9/18 (6 sessions) | -0.0373 | -0.0252 | -0.1230 | -0.0131 | -0.0380 | -0.4020 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 10/22 (8 sessions) | -0.0493 | -0.0724 | -0.1258 | -0.0200 | 9/18 (6 sessions) | -0.0210 | -0.0088 | -0.0972 | 0.0024 | -0.0283 | -0.3239 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 9/22 (7 sessions) | -0.0343 | -0.0427 | -0.1121 | -0.0090 | 9/18 (6 sessions) | -0.0115 | -0.0114 | -0.0665 | 0.0095 | -0.0228 | -0.2747 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 22/22 (11 sessions) | -0.0840 | -0.0552 | -0.0987 | -0.0125 | 18/18 (12 sessions) | -0.0734 | -0.0315 | -0.1443 | -0.0071 | -0.0106 | -0.1050 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 20/22 (10 sessions) | -0.0394 | -0.0263 | -0.0652 | -0.0057 | 15/18 (12 sessions) | -0.0272 | -0.0130 | -0.0426 | 0.0023 | -0.0122 | -0.2421 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 18/22 (10 sessions) | -0.0237 | -0.0108 | -0.0404 | 0.0022 | 13/18 (10 sessions) | -0.0248 | -0.0132 | -0.0531 | -0.0049 | 0.0012 | 0.0320 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 9/22 (7 sessions) | 0.1111 | 0.0000 | 0.0000 | 0.0000 | 9/18 (6 sessions) | 0.2222 | 0.0000 | 0.0000 | 0.0000 | -0.1111 | -0.2843 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 7/22 (6 sessions) | 0.2857 | 0.0000 | 0.0000 | 0.5000 | 9/18 (6 sessions) | 0.5556 | 0.0000 | 0.0000 | 1.0000 | -0.2698 | -0.4247 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 5/22 (5 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9/18 (6 sessions) | 1.4444 | 1.0000 | 1.0000 | 2.0000 | -0.4444 | -0.7493 | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 12/22 (9 sessions) | 0.2500 | 0.0000 | 0.0000 | 0.2500 | 9/18 (6 sessions) | 0.1111 | 0.0000 | 0.0000 | 0.0000 | 0.1389 | 0.3417 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 10/22 (8 sessions) | 0.6000 | 1.0000 | 0.0000 | 1.0000 | 9/18 (6 sessions) | 0.2222 | 0.0000 | 0.0000 | 0.0000 | 0.3778 | 0.7832 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 7/22 (6 sessions) | 0.7143 | 1.0000 | 0.5000 | 1.0000 | 9/18 (6 sessions) | 0.6667 | 1.0000 | 0.0000 | 1.0000 | 0.0476 | 0.0962 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 9/22 (7 sessions) | 0.2222 | 0.0000 | 0.0000 | 0.0000 | 9/18 (6 sessions) | 0.2222 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 7/22 (6 sessions) | 0.4286 | 0.0000 | 0.0000 | 1.0000 | 9/18 (6 sessions) | 0.3333 | 0.0000 | 0.0000 | 1.0000 | 0.0952 | 0.1849 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 5/22 (5 sessions) | 0.6000 | 1.0000 | 0.0000 | 1.0000 | 9/18 (6 sessions) | 0.6667 | 1.0000 | 0.0000 | 1.0000 | -0.0667 | -0.1291 | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 17/22 (10 sessions) | 0.8824 | 1.0000 | 0.0000 | 1.0000 | 11/18 (8 sessions) | 0.3636 | 0.0000 | 0.0000 | 0.5000 | 0.5187 | 0.6181 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 13/22 (10 sessions) | 1.7692 | 1.0000 | 1.0000 | 3.0000 | 9/18 (6 sessions) | 0.7778 | 0.0000 | 0.0000 | 2.0000 | 0.9915 | 0.6547 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 9/22 (7 sessions) | 2.4444 | 3.0000 | 1.0000 | 3.0000 | 9/18 (6 sessions) | 1.6667 | 1.0000 | 0.0000 | 3.0000 | 0.7778 | 0.4225 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 17/22 (10 sessions) | 2.0686 | 1.8400 | 1.4925 | 2.4000 | 11/18 (8 sessions) | 1.5936 | 1.3600 | 0.7700 | 1.9000 | 0.4750 | 0.5155 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 13/22 (10 sessions) | 2.5510 | 2.3500 | 2.1100 | 3.0525 | 9/18 (6 sessions) | 1.6250 | 1.7950 | 1.2199 | 1.9700 | 0.9260 | 1.3398 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 9/22 (7 sessions) | 3.1836 | 3.1625 | 2.3500 | 3.6950 | 9/18 (6 sessions) | 2.7128 | 2.4500 | 1.8300 | 3.4400 | 0.4708 | 0.4071 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 12/22 (9 sessions) | 2.7978 | 2.6894 | 2.2962 | 3.0968 | 9/18 (6 sessions) | 2.5425 | 2.2952 | 1.9502 | 3.0326 | 0.2553 | 0.3288 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 12/22 (9 sessions) | 3.7607 | 3.9133 | 3.2624 | 4.1858 | 9/18 (6 sessions) | 3.4168 | 3.4350 | 3.2589 | 3.7375 | 0.3439 | 0.5002 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 9/22 (7 sessions) | 5.3835 | 5.1710 | 4.0150 | 6.5875 | 9/18 (6 sessions) | 5.5670 | 5.1758 | 4.0072 | 6.5264 | -0.1835 | -0.1172 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 17/22 (10 sessions) | 0.5389 | 0.5625 | 0.2615 | 0.8501 | 11/18 (8 sessions) | 0.5884 | 0.4905 | 0.2993 | 0.9434 | -0.0495 | -0.1444 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 13/22 (10 sessions) | 0.4090 | 0.5313 | 0.1209 | 0.5926 | 9/18 (6 sessions) | 0.3854 | 0.3548 | 0.2573 | 0.4765 | 0.0236 | 0.0903 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 9/22 (7 sessions) | 0.2733 | 0.3147 | 0.0955 | 0.4528 | 9/18 (6 sessions) | 0.3123 | 0.3189 | 0.1363 | 0.4790 | -0.0390 | -0.1931 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 17/22 (10 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 11/18 (8 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 13/22 (10 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9/18 (6 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 9/22 (7 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9/18 (6 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 17/22 (10 sessions) | 0.4706 | 0.5000 | 0.2500 | 0.5000 | 11/18 (8 sessions) | 0.5000 | 0.5000 | 0.3750 | 0.7500 | -0.0294 | -0.1100 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 13/22 (10 sessions) | 0.4846 | 0.5000 | 0.4000 | 0.6000 | 9/18 (6 sessions) | 0.4556 | 0.4000 | 0.4000 | 0.6000 | 0.0291 | 0.1877 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 9/22 (7 sessions) | 0.4798 | 0.5000 | 0.4545 | 0.5455 | 9/18 (6 sessions) | 0.4899 | 0.5000 | 0.4545 | 0.5455 | -0.0101 | -0.0848 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 12/22 (9 sessions) | 1.8542 | 2.1919 | 1.2917 | 2.4082 | 9/18 (6 sessions) | 2.4600 | 2.8097 | 1.8339 | 3.0331 | -0.6058 | -0.6352 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 12/22 (9 sessions) | 0.7880 | 0.7764 | 0.1033 | 1.3432 | 9/18 (6 sessions) | 1.6525 | 1.4456 | 1.1884 | 1.7758 | -0.8645 | -1.2389 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 10/22 (8 sessions) | 0.5989 | 0.5402 | 0.2271 | 0.9484 | 9/18 (6 sessions) | 1.1581 | 1.3715 | 0.8134 | 1.4030 | -0.5593 | -1.1929 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 21/22 (11 sessions) | 1.3271 | 0.6900 | 0.2300 | 1.7399 | 18/18 (12 sessions) | 0.8887 | 0.6575 | 0.2638 | 1.0825 | 0.4384 | 0.3121 | not resampled |
| stage11_2.room_in_atr [SMALL] | 12/22 (9 sessions) | 1.8978 | 0.9472 | 0.3803 | 2.0319 | 9/18 (6 sessions) | 0.9342 | 0.9884 | 0.6755 | 1.2270 | 0.9635 | 0.4326 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 22/22 (11 sessions) | 4.4545 | 5.0000 | 3.2500 | 5.0000 | 18/18 (12 sessions) | 4.0000 | 4.0000 | 3.0000 | 5.0000 | 0.4545 | 0.4996 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 22/22 (11 sessions) | 1.5455 | 1.0000 | 1.0000 | 2.7500 | 18/18 (12 sessions) | 2.0000 | 2.0000 | 1.0000 | 3.0000 | -0.4545 | -0.4996 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 22/22 (11 sessions) | 0.2641 | 0.2500 | 0.0975 | 0.3775 | 18/18 (12 sessions) | 0.1563 | 0.0975 | 0.0700 | 0.1688 | 0.1078 | 0.5964 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 21/22 (11 sessions) | 1.3271 | 0.6900 | 0.2300 | 1.7399 | 18/18 (12 sessions) | 0.8887 | 0.6575 | 0.2638 | 1.0825 | 0.4384 | 0.3121 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 12/22 (9 sessions) | 0.5000 | 0.0000 | 0.0000 | 1.0000 | 9/18 (6 sessions) | 0.2222 | 0.0000 | 0.0000 | 0.0000 | 0.2778 | 0.4140 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 12/22 (9 sessions) | 0.8333 | 0.5000 | 0.0000 | 2.0000 | 9/18 (6 sessions) | 0.6667 | 1.0000 | 0.0000 | 1.0000 | 0.1667 | 0.1965 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 17/22 (10 sessions) | 1.8783 | 1.8300 | 1.1600 | 2.9050 | 10/18 (7 sessions) | 1.2224 | 1.0425 | 0.5992 | 1.8425 | 0.6559 | 0.6979 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 15/22 (9 sessions) | 0.7718 | 0.7300 | 0.4250 | 1.1075 | 10/18 (7 sessions) | 0.6118 | 0.3525 | 0.2469 | 1.1375 | 0.1600 | 0.3310 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 12/22 (9 sessions) | 2.5995 | 2.7327 | 1.4807 | 3.5498 | 9/18 (6 sessions) | 2.3210 | 2.1326 | 1.4668 | 3.5554 | 0.2784 | 0.2050 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 11/22 (8 sessions) | 1.2209 | 1.1601 | 0.7362 | 1.4629 | 9/18 (6 sessions) | 1.0958 | 0.7948 | 0.4089 | 1.9241 | 0.1251 | 0.1463 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | SHORT | 40 | 15 | 22 | 18 | 100.00% | 100.00% | 55.00% |
| time_bucket | 09:35-10:00 [SMALL] | 12 | 10 | 5 | 7 | 22.73% | 38.89% | 41.67% |
| time_bucket | 10:00-10:30 [SMALL] | 6 | 6 | 4 | 2 | 18.18% | 11.11% | 66.67% |
| time_bucket | 10:30-11:00 [SMALL] | 3 | 3 | 3 | 0 | 13.64% | 0.00% | 100.00% |
| time_bucket | 11:00-12:00 [SMALL] | 2 | 2 | 2 | 0 | 9.09% | 0.00% | 100.00% |
| time_bucket | 12:00-13:30 [SMALL] | 3 | 3 | 3 | 0 | 13.64% | 0.00% | 100.00% |
| time_bucket | 13:30-15:00 [SMALL] | 4 | 3 | 1 | 3 | 4.55% | 16.67% | 25.00% |
| time_bucket | 15:00-close [SMALL] | 10 | 8 | 4 | 6 | 18.18% | 33.33% | 40.00% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 11 | 7 | 6 | 5 | 27.27% | 27.78% | 54.55% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 8 | 4 | 4 | 4 | 18.18% | 22.22% | 50.00% |
| ema9_20_alignment | EMA_UNAVAILABLE [SMALL] | 21 | 12 | 12 | 9 | 54.55% | 50.00% | 57.14% |
| price_vwap_alignment | VWAP_ALIGNED | 35 | 15 | 20 | 15 | 90.91% | 83.33% | 57.14% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 5 | 2 | 2 | 3 | 9.09% | 16.67% | 40.00% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED [SMALL] | 18 | 10 | 12 | 6 | 54.55% | 33.33% | 66.67% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 7 | 3 | 4 | 3 | 18.18% | 16.67% | 57.14% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 15 | 10 | 6 | 9 | 27.27% | 50.00% | 40.00% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 12 | 6 | 6 | 6 | 27.27% | 33.33% | 50.00% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 7 | 5 | 4 | 3 | 18.18% | 16.67% | 57.14% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE [SMALL] | 21 | 12 | 12 | 9 | 54.55% | 50.00% | 57.14% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 11 | 7 | 6 | 5 | 27.27% | 27.78% | 54.55% |
| prior_ema_cross | NO_PRIOR_CROSS [SMALL] | 22 | 12 | 13 | 9 | 59.09% | 50.00% | 59.09% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 7 | 3 | 3 | 4 | 13.64% | 22.22% | 42.86% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE [SMALL] | 24 | 11 | 15 | 9 | 68.18% | 50.00% | 62.50% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 16 | 9 | 7 | 9 | 31.82% | 50.00% | 43.75% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 5 | 3 | 2 | 3 | 9.09% | 16.67% | 40.00% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 5 | 2 | 2 | 3 | 9.09% | 16.67% | 40.00% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 2 | 2 | 1 | 1 | 4.55% | 5.56% | 50.00% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 2 | 2 | 2 | 0 | 9.09% | 0.00% | 100.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 1 | 1 | 1 | 0 | 4.55% | 0.00% | 100.00% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 6 | 4 | 4 | 2 | 18.18% | 11.11% | 66.67% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 1 | 1 | 1 | 0 | 4.55% | 0.00% | 100.00% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 18 | 11 | 9 | 9 | 40.91% | 50.00% | 50.00% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 40 | 15 | 22 | 18 | 100.00% | 100.00% | 55.00% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 7 | 5 | 3 | 4 | 13.64% | 22.22% | 42.86% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 6 | 3 | 3 | 3 | 13.64% | 16.67% | 50.00% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 6 | 5 | 4 | 2 | 18.18% | 11.11% | 66.67% |
| stage11_3.structure | UNAVAILABLE [SMALL] | 21 | 14 | 12 | 9 | 54.55% | 50.00% | 57.14% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 7 | 5 | 3 | 4 | 13.64% | 22.22% | 42.86% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 12 | 6 | 7 | 5 | 31.82% | 27.78% | 58.33% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE [SMALL] | 21 | 14 | 12 | 9 | 54.55% | 50.00% | 57.14% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 10 | 5 | 5 | 5 | 22.73% | 27.78% | 50.00% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 10 | 7 | 6 | 4 | 27.27% | 22.22% | 60.00% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 20 | 13 | 11 | 9 | 50.00% | 50.00% | 55.00% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 9 | 4 | 6 | 3 | 27.27% | 16.67% | 66.67% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 10 | 8 | 4 | 6 | 18.18% | 33.33% | 40.00% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 21 | 14 | 12 | 9 | 54.55% | 50.00% | 57.14% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 15 | 12 | 7 | 8 | 31.82% | 44.44% | 46.67% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 1 | 1 | 1 | 0 | 4.55% | 0.00% | 100.00% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 7 | 4 | 3 | 4 | 13.64% | 22.22% | 42.86% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 17 | 11 | 11 | 6 | 50.00% | 33.33% | 64.71% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 40 | 15 | 22 | 18 | 100.00% | 100.00% | 55.00% |


### 2026-06


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 28/28 (14 sessions) | 2.0600 | 2.2000 | 1.6525 | 2.3600 | 5/5 (5 sessions) | 1.9795 | 2.3299 | 1.1775 | 2.3600 | 0.0805 | 0.1162 | not resampled |
| body_size [SMALL] | 28/28 (14 sessions) | 1.3465 | 0.9700 | 0.6099 | 1.8752 | 5/5 (5 sessions) | 0.7691 | 0.5950 | 0.5400 | 0.8600 | 0.5774 | 0.5121 | not resampled |
| directional_body [SMALL] | 28/28 (14 sessions) | 1.3465 | 0.9700 | 0.6099 | 1.8752 | 5/5 (5 sessions) | 0.7691 | 0.5950 | 0.5400 | 0.8600 | 0.5774 | 0.5121 | not resampled |
| candle_range [SMALL] | 28/28 (14 sessions) | 1.7558 | 1.4250 | 0.9862 | 2.3152 | 5/5 (5 sessions) | 1.1786 | 1.0800 | 1.0500 | 1.5230 | 0.5772 | 0.5093 | not resampled |
| body_range_ratio [SMALL] | 28/28 (14 sessions) | 0.7030 | 0.7213 | 0.5934 | 0.8641 | 5/5 (5 sessions) | 0.6442 | 0.5509 | 0.5352 | 0.8190 | 0.0588 | 0.2830 | not resampled |
| directional_body_range_ratio [SMALL] | 28/28 (14 sessions) | 0.7030 | 0.7213 | 0.5934 | 0.8641 | 5/5 (5 sessions) | 0.6442 | 0.5509 | 0.5352 | 0.8190 | 0.0588 | 0.2830 | not resampled |
| close_location [SMALL] | 28/28 (14 sessions) | 0.1592 | 0.1439 | 0.0380 | 0.2366 | 5/5 (5 sessions) | 0.1494 | 0.0857 | 0.0139 | 0.1838 | 0.0099 | 0.0685 | not resampled |
| directional_close_location [SMALL] | 28/28 (14 sessions) | 0.8408 | 0.8561 | 0.7634 | 0.9620 | 5/5 (5 sessions) | 0.8506 | 0.9143 | 0.8162 | 0.9861 | -0.0099 | -0.0685 | not resampled |
| distance_beyond_level [SMALL] | 28/28 (14 sessions) | 0.8953 | 0.5000 | 0.1802 | 1.3456 | 5/5 (5 sessions) | 0.3756 | 0.3501 | 0.3406 | 0.5100 | 0.5196 | 0.5098 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 16/28 (7 sessions) | 0.6764 | 0.3436 | 0.1788 | 0.6146 | 2/5 (2 sessions) | 0.5108 | 0.5108 | 0.3907 | 0.6308 | 0.1657 | 0.1396 | not resampled |
| candle_volume [SMALL] | 28/28 (14 sessions) | 735824.3929 | 607479.5000 | 401935.5000 | 862886.0000 | 5/5 (5 sessions) | 676018.0000 | 594063.0000 | 581735.0000 | 602781.0000 | 59806.3929 | 0.1149 | not resampled |
| relative_volume_prior_6 [SMALL] | 22/28 (11 sessions) | 1.5290 | 1.0018 | 0.7635 | 1.6047 | 2/5 (2 sessions) | 1.4843 | 1.4843 | 1.2945 | 1.6740 | 0.0447 | 0.0255 | not resampled |
| atr14 [SMALL] | 16/28 (7 sessions) | 1.4253 | 1.2834 | 0.9848 | 1.9133 | 2/5 (2 sessions) | 1.1753 | 1.1753 | 0.8208 | 1.5299 | 0.2499 | 0.4529 | not resampled |
| minutes_since_open [SMALL] | 28/28 (14 sessions) | 109.6429 | 90.0000 | 43.7500 | 183.7500 | 5/5 (5 sessions) | 99.0000 | 30.0000 | 30.0000 | 80.0000 | 10.6429 | 0.1119 | not resampled |
| minutes_since_ema_cross [SMALL] | 7/28 (4 sessions) | 27.1429 | 5.0000 | 0.0000 | 35.0000 | 1/5 (1 sessions) | 55.0000 | 55.0000 | 55.0000 | 55.0000 | -27.8571 | N/A | not resampled |
| break_attempt_rank [SMALL] | 28/28 (14 sessions) | 6.3571 | 5.0000 | 2.7500 | 9.0000 | 5/5 (5 sessions) | 4.6000 | 4.0000 | 3.0000 | 5.0000 | 1.7571 | 0.3844 | not resampled |
| valid_hold_sequence_rank [SMALL] | 28/28 (14 sessions) | 3.3571 | 3.0000 | 2.0000 | 5.0000 | 5/5 (5 sessions) | 2.2000 | 2.0000 | 1.0000 | 3.0000 | 1.1571 | 0.6281 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 13/28 (6 sessions) | 0.7066 | 0.5028 | 0.2851 | 1.1158 | 1/5 (1 sessions) | 0.2760 | 0.2760 | 0.2760 | 0.2760 | 0.4307 | N/A | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 13/28 (6 sessions) | 0.4645 | 0.3610 | 0.2895 | 0.7425 | 1/5 (1 sessions) | 0.5919 | 0.5919 | 0.5919 | 0.5919 | -0.1273 | N/A | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 19/28 (9 sessions) | -0.2626 | -0.2163 | -0.3738 | -0.1049 | 2/5 (2 sessions) | -0.2363 | -0.2363 | -0.2705 | -0.2020 | -0.0264 | -0.1017 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 18/28 (8 sessions) | -0.1499 | -0.1430 | -0.3033 | 0.0256 | 2/5 (2 sessions) | -0.2067 | -0.2067 | -0.2404 | -0.1731 | 0.0568 | 0.2611 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 17/28 (7 sessions) | -0.1121 | -0.0619 | -0.2409 | -0.0123 | 2/5 (2 sessions) | -0.1081 | -0.1081 | -0.1205 | -0.0957 | -0.0039 | -0.0188 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 13/28 (6 sessions) | -0.1829 | -0.1163 | -0.2849 | -0.0785 | 1/5 (1 sessions) | -0.0997 | -0.0997 | -0.0997 | -0.0997 | -0.0832 | N/A | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 12/28 (6 sessions) | -0.1084 | -0.0791 | -0.1904 | -0.0369 | 1/5 (1 sessions) | -0.0842 | -0.0842 | -0.0842 | -0.0842 | -0.0243 | N/A | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 11/28 (5 sessions) | -0.1127 | -0.1018 | -0.1880 | -0.0275 | 1/5 (1 sessions) | -0.0788 | -0.0788 | -0.0788 | -0.0788 | -0.0339 | N/A | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 28/28 (14 sessions) | -0.1777 | -0.0689 | -0.2649 | -0.0221 | 5/5 (5 sessions) | -0.1130 | -0.0809 | -0.0849 | -0.0356 | -0.0647 | -0.2779 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 25/28 (12 sessions) | -0.0965 | -0.0451 | -0.1632 | -0.0166 | 4/5 (4 sessions) | -0.0158 | -0.0113 | -0.0183 | -0.0088 | -0.0807 | -0.5841 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 23/28 (11 sessions) | -0.0548 | -0.0255 | -0.1120 | -0.0068 | 4/5 (4 sessions) | 0.0173 | 0.0147 | -0.0048 | 0.0367 | -0.0721 | -0.9879 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 10/28 (5 sessions) | 0.5000 | 0.0000 | 0.0000 | 1.0000 | 1/5 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.5000 | N/A | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 9/28 (5 sessions) | 1.0000 | 1.0000 | 0.0000 | 2.0000 | 1/5 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | N/A | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 3/28 (2 sessions) | 1.3333 | 1.0000 | 0.5000 | 2.0000 | 1/5 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.3333 | N/A | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 16/28 (7 sessions) | 0.1875 | 0.0000 | 0.0000 | 0.0000 | 2/5 (2 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1875 | 0.4804 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 13/28 (6 sessions) | 0.6154 | 1.0000 | 0.0000 | 1.0000 | 1/5 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.6154 | N/A | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 8/28 (5 sessions) | 1.1250 | 1.0000 | 1.0000 | 1.0000 | 1/5 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.1250 | N/A | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 10/28 (5 sessions) | 0.3000 | 0.0000 | 0.0000 | 0.7500 | 1/5 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.3000 | N/A | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 9/28 (5 sessions) | 0.5556 | 0.0000 | 0.0000 | 1.0000 | 1/5 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.5556 | N/A | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 3/28 (2 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1/5 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | N/A | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 23/28 (11 sessions) | 1.0870 | 1.0000 | 0.0000 | 2.0000 | 4/5 (4 sessions) | 1.7500 | 1.5000 | 1.0000 | 2.2500 | -0.6630 | -0.5638 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 17/28 (7 sessions) | 1.7647 | 1.0000 | 0.0000 | 3.0000 | 2/5 (2 sessions) | 1.5000 | 1.5000 | 1.2500 | 1.7500 | 0.2647 | 0.1654 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 11/28 (5 sessions) | 3.0909 | 2.0000 | 1.0000 | 5.0000 | 1/5 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 2.0909 | N/A | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 23/28 (11 sessions) | 3.3230 | 3.1250 | 2.1300 | 4.5950 | 4/5 (4 sessions) | 2.2875 | 1.8400 | 1.6875 | 2.4400 | 1.0355 | 0.7227 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 17/28 (7 sessions) | 4.7250 | 4.3400 | 2.8800 | 6.4650 | 2/5 (2 sessions) | 3.8750 | 3.8750 | 2.8225 | 4.9275 | 0.8500 | 0.3768 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 11/28 (5 sessions) | 6.4063 | 6.3700 | 4.8675 | 8.2325 | 1/5 (1 sessions) | 2.9300 | 2.9300 | 2.9300 | 2.9300 | 3.4763 | N/A | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 16/28 (7 sessions) | 2.3434 | 2.1679 | 1.5998 | 2.6119 | 2/5 (2 sessions) | 2.9674 | 2.9674 | 2.5530 | 3.3818 | -0.6240 | -0.5559 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 16/28 (7 sessions) | 3.2916 | 3.0371 | 2.4864 | 3.7760 | 2/5 (2 sessions) | 3.4848 | 3.4848 | 3.3291 | 3.6405 | -0.1931 | -0.1734 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 11/28 (5 sessions) | 4.8642 | 4.6924 | 4.1522 | 5.4843 | 1/5 (1 sessions) | 6.2840 | 6.2840 | 6.2840 | 6.2840 | -1.4198 | N/A | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 23/28 (11 sessions) | 0.4920 | 0.4006 | 0.2168 | 0.7302 | 4/5 (4 sessions) | 0.5587 | 0.4999 | 0.3634 | 0.6952 | -0.0667 | -0.2084 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 17/28 (7 sessions) | 0.2951 | 0.2104 | 0.1418 | 0.4812 | 2/5 (2 sessions) | 0.2885 | 0.2885 | 0.2031 | 0.3739 | 0.0066 | 0.0294 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 11/28 (5 sessions) | 0.2097 | 0.2154 | 0.0463 | 0.2805 | 1/5 (1 sessions) | 0.5661 | 0.5661 | 0.5661 | 0.5661 | -0.3564 | N/A | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 23/28 (11 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 4/5 (4 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 17/28 (7 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 2/5 (2 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 11/28 (5 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1/5 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 23/28 (11 sessions) | 0.4891 | 0.5000 | 0.5000 | 0.5000 | 4/5 (4 sessions) | 0.4375 | 0.3750 | 0.1875 | 0.6250 | 0.0516 | 0.1962 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 17/28 (7 sessions) | 0.5294 | 0.5000 | 0.4000 | 0.6000 | 2/5 (2 sessions) | 0.4000 | 0.4000 | 0.3500 | 0.4500 | 0.1294 | 0.9503 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 11/28 (5 sessions) | 0.5537 | 0.5455 | 0.5000 | 0.5682 | 1/5 (1 sessions) | 0.4545 | 0.4545 | 0.4545 | 0.4545 | 0.0992 | N/A | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 16/28 (7 sessions) | 1.5286 | 1.3854 | 0.8459 | 1.7730 | 2/5 (2 sessions) | 0.6431 | 0.6431 | 0.5867 | 0.6994 | 0.8856 | 0.7958 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 16/28 (7 sessions) | 0.7879 | 0.6893 | 0.3753 | 1.1845 | 2/5 (2 sessions) | 0.4001 | 0.4001 | 0.2583 | 0.5419 | 0.3878 | 0.6464 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 13/28 (6 sessions) | 0.4509 | 0.2743 | 0.1443 | 0.5043 | 1/5 (1 sessions) | 1.2755 | 1.2755 | 1.2755 | 1.2755 | -0.8247 | N/A | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 27/28 (14 sessions) | 2.5238 | 2.0200 | 0.5458 | 3.5550 | 4/5 (4 sessions) | 2.4038 | 1.8350 | 1.2925 | 2.9462 | 0.1201 | 0.0480 | not resampled |
| stage11_2.room_in_atr [SMALL] | 15/28 (7 sessions) | 1.6390 | 1.4902 | 0.4873 | 1.8377 | 2/5 (2 sessions) | 2.7250 | 2.7250 | 1.7605 | 3.6895 | -1.0860 | -0.6166 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 28/28 (14 sessions) | 4.3214 | 4.0000 | 4.0000 | 5.0000 | 5/5 (5 sessions) | 4.4000 | 4.0000 | 4.0000 | 4.0000 | -0.0786 | -0.1301 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 28/28 (14 sessions) | 1.6786 | 2.0000 | 1.0000 | 2.0000 | 5/5 (5 sessions) | 1.6000 | 2.0000 | 2.0000 | 2.0000 | 0.0786 | 0.1301 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 28/28 (14 sessions) | 0.7592 | 0.3000 | 0.1020 | 1.2075 | 5/5 (5 sessions) | 0.3076 | 0.3501 | 0.1225 | 0.5100 | 0.4515 | 0.4805 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 27/28 (14 sessions) | 2.5238 | 2.0200 | 0.5458 | 3.5550 | 4/5 (4 sessions) | 2.4038 | 1.8350 | 1.2925 | 2.9462 | 0.1201 | 0.0480 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 16/28 (7 sessions) | 0.3125 | 0.0000 | 0.0000 | 0.2500 | 2/5 (2 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.3125 | 0.5361 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 16/28 (7 sessions) | 0.5000 | 0.0000 | 0.0000 | 1.0000 | 2/5 (2 sessions) | 0.5000 | 0.5000 | 0.2500 | 0.7500 | 0.0000 | 0.0000 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 22/28 (11 sessions) | 2.9598 | 2.3900 | 1.6246 | 4.3000 | 4/5 (4 sessions) | 2.1102 | 1.6703 | 1.4250 | 2.3554 | 0.8497 | 0.4536 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 20/28 (8 sessions) | 1.4552 | 0.9410 | 0.4225 | 2.1225 | 3/5 (3 sessions) | 1.1069 | 0.6400 | 0.4503 | 1.5300 | 0.3483 | 0.2368 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 16/28 (7 sessions) | 2.1983 | 2.0734 | 1.2282 | 2.8007 | 2/5 (2 sessions) | 2.5499 | 2.5499 | 2.2700 | 2.8299 | -0.3516 | -0.2947 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 16/28 (7 sessions) | 1.2444 | 0.6126 | 0.3655 | 1.7795 | 2/5 (2 sessions) | 1.3284 | 1.3284 | 1.3063 | 1.3505 | -0.0841 | -0.0644 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | SHORT | 33 | 14 | 28 | 5 | 100.00% | 100.00% | 84.85% |
| time_bucket | 09:35-10:00 [SMALL] | 6 | 6 | 5 | 1 | 17.86% | 20.00% | 83.33% |
| time_bucket | 10:00-10:30 [SMALL] | 8 | 6 | 6 | 2 | 21.43% | 40.00% | 75.00% |
| time_bucket | 10:30-11:00 [SMALL] | 3 | 3 | 2 | 1 | 7.14% | 20.00% | 66.67% |
| time_bucket | 11:00-12:00 [SMALL] | 6 | 4 | 6 | 0 | 21.43% | 0.00% | 100.00% |
| time_bucket | 12:00-13:30 [SMALL] | 7 | 5 | 7 | 0 | 25.00% | 0.00% | 100.00% |
| time_bucket | 13:30-15:00 [SMALL] | 2 | 2 | 2 | 0 | 7.14% | 0.00% | 100.00% |
| time_bucket | 15:00-close [SMALL] | 1 | 1 | 0 | 1 | 0.00% | 20.00% | 0.00% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 13 | 6 | 12 | 1 | 42.86% | 20.00% | 92.31% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 1 | 1 | 1 | 0 | 3.57% | 0.00% | 100.00% |
| ema9_20_alignment | EMA_UNAVAILABLE [SMALL] | 19 | 12 | 15 | 4 | 53.57% | 80.00% | 78.95% |
| price_vwap_alignment | VWAP_ALIGNED | 30 | 14 | 25 | 5 | 89.29% | 100.00% | 83.33% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 3 | 2 | 3 | 0 | 10.71% | 0.00% | 100.00% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED [SMALL] | 14 | 7 | 14 | 0 | 50.00% | 0.00% | 100.00% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 9 | 6 | 7 | 2 | 25.00% | 40.00% | 77.78% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 10 | 9 | 7 | 3 | 25.00% | 60.00% | 70.00% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 9 | 5 | 9 | 0 | 32.14% | 0.00% | 100.00% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 5 | 4 | 4 | 1 | 14.29% | 20.00% | 80.00% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE [SMALL] | 19 | 12 | 15 | 4 | 53.57% | 80.00% | 78.95% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 8 | 5 | 7 | 1 | 25.00% | 20.00% | 87.50% |
| prior_ema_cross | NO_PRIOR_CROSS [SMALL] | 25 | 13 | 21 | 4 | 75.00% | 80.00% | 84.00% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE [SMALL] | 21 | 10 | 18 | 3 | 64.29% | 60.00% | 85.71% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 12 | 6 | 10 | 2 | 35.71% | 40.00% | 83.33% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 3 | 3 | 2 | 1 | 7.14% | 20.00% | 66.67% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 2 | 2 | 2 | 0 | 7.14% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 4 | 2 | 4 | 0 | 14.29% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 1 | 1 | 1 | 0 | 3.57% | 0.00% | 100.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 3 | 2 | 2 | 1 | 7.14% | 20.00% | 66.67% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 4 | 3 | 4 | 0 | 14.29% | 0.00% | 100.00% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 2 | 1 | 1 | 1 | 3.57% | 20.00% | 50.00% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 14 | 10 | 12 | 2 | 42.86% | 40.00% | 85.71% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 33 | 14 | 28 | 5 | 100.00% | 100.00% | 84.85% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 4 | 4 | 3 | 1 | 10.71% | 20.00% | 75.00% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 3 | 3 | 3 | 0 | 10.71% | 0.00% | 100.00% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 8 | 5 | 8 | 0 | 28.57% | 0.00% | 100.00% |
| stage11_3.structure | UNAVAILABLE [SMALL] | 18 | 12 | 14 | 4 | 50.00% | 80.00% | 77.78% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 4 | 4 | 3 | 1 | 10.71% | 20.00% | 75.00% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 11 | 6 | 11 | 0 | 39.29% | 0.00% | 100.00% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE [SMALL] | 18 | 12 | 14 | 4 | 50.00% | 80.00% | 77.78% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 9 | 6 | 8 | 1 | 28.57% | 20.00% | 88.89% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 10 | 7 | 9 | 1 | 32.14% | 20.00% | 90.00% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 14 | 10 | 11 | 3 | 39.29% | 60.00% | 78.57% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 10 | 7 | 10 | 0 | 35.71% | 0.00% | 100.00% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 8 | 5 | 7 | 1 | 25.00% | 20.00% | 87.50% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 15 | 12 | 11 | 4 | 39.29% | 80.00% | 73.33% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 10 | 10 | 8 | 2 | 28.57% | 40.00% | 80.00% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 2 | 1 | 1 | 1 | 3.57% | 20.00% | 50.00% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 3 | 3 | 2 | 1 | 7.14% | 20.00% | 66.67% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 18 | 8 | 17 | 1 | 60.71% | 20.00% | 94.44% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 33 | 14 | 28 | 5 | 100.00% | 100.00% | 84.85% |


### 2026-07


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 30/30 (15 sessions) | 1.5110 | 1.4450 | 1.1169 | 1.6100 | 10/10 (7 sessions) | 1.5860 | 1.4700 | 1.3325 | 1.6200 | -0.0750 | -0.1434 | not resampled |
| body_size [SMALL] | 30/30 (15 sessions) | 0.8284 | 0.7250 | 0.4625 | 1.0888 | 10/10 (7 sessions) | 1.1455 | 1.0950 | 0.6650 | 1.5588 | -0.3171 | -0.5828 | not resampled |
| directional_body [SMALL] | 30/30 (15 sessions) | 0.8277 | 0.7250 | 0.4625 | 1.0888 | 10/10 (7 sessions) | 1.1455 | 1.0950 | 0.6650 | 1.5588 | -0.3178 | -0.5832 | not resampled |
| candle_range [SMALL] | 30/30 (15 sessions) | 1.2450 | 1.0496 | 0.7038 | 1.5188 | 10/10 (7 sessions) | 1.6495 | 1.8175 | 1.0025 | 2.1100 | -0.4045 | -0.4582 | not resampled |
| body_range_ratio [SMALL] | 30/30 (15 sessions) | 0.6659 | 0.7099 | 0.5577 | 0.8540 | 10/10 (7 sessions) | 0.7075 | 0.7193 | 0.5493 | 0.8669 | -0.0416 | -0.1772 | not resampled |
| directional_body_range_ratio [SMALL] | 30/30 (15 sessions) | 0.6641 | 0.7099 | 0.5577 | 0.8540 | 10/10 (7 sessions) | 0.7075 | 0.7193 | 0.5493 | 0.8669 | -0.0434 | -0.1818 | not resampled |
| close_location [SMALL] | 30/30 (15 sessions) | 0.1532 | 0.0915 | 0.0366 | 0.1835 | 10/10 (7 sessions) | 0.1552 | 0.1140 | 0.0179 | 0.2307 | -0.0020 | -0.0116 | not resampled |
| directional_close_location [SMALL] | 30/30 (15 sessions) | 0.8468 | 0.9085 | 0.8165 | 0.9634 | 10/10 (7 sessions) | 0.8448 | 0.8860 | 0.7693 | 0.9821 | 0.0020 | 0.0116 | not resampled |
| distance_beyond_level [SMALL] | 30/30 (15 sessions) | 0.4093 | 0.3800 | 0.1950 | 0.5057 | 10/10 (7 sessions) | 0.2565 | 0.2400 | 0.1025 | 0.3538 | 0.1528 | 0.5341 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 18/30 (11 sessions) | 0.3313 | 0.2885 | 0.0948 | 0.5090 | 8/10 (5 sessions) | 0.1777 | 0.1479 | 0.0737 | 0.2236 | 0.1536 | 0.7000 | not resampled |
| candle_volume [SMALL] | 30/30 (15 sessions) | 593978.9000 | 543035.5000 | 346166.0000 | 612068.5000 | 10/10 (7 sessions) | 739984.5000 | 637002.5000 | 512846.0000 | 897645.7500 | -146005.6000 | -0.3228 | not resampled |
| relative_volume_prior_6 [SMALL] | 20/30 (11 sessions) | 1.2754 | 0.9232 | 0.7020 | 1.0830 | 10/10 (7 sessions) | 1.5642 | 1.0540 | 0.8169 | 1.7187 | -0.2888 | -0.1859 | not resampled |
| atr14 [SMALL] | 18/30 (11 sessions) | 0.9825 | 0.9507 | 0.7699 | 1.0950 | 8/10 (5 sessions) | 1.1334 | 1.2455 | 0.8470 | 1.4017 | -0.1509 | -0.5115 | not resampled |
| minutes_since_open [SMALL] | 30/30 (15 sessions) | 112.8333 | 77.5000 | 25.0000 | 186.2500 | 10/10 (7 sessions) | 144.5000 | 112.5000 | 77.5000 | 202.5000 | -31.6667 | -0.3174 | not resampled |
| minutes_since_ema_cross [SMALL] | 10/30 (7 sessions) | 58.5000 | 65.0000 | 25.0000 | 82.5000 | 4/10 (3 sessions) | 58.7500 | 55.0000 | 30.0000 | 83.7500 | -0.2500 | -0.0057 | not resampled |
| break_attempt_rank [SMALL] | 30/30 (15 sessions) | 5.2000 | 5.5000 | 2.0000 | 8.0000 | 10/10 (7 sessions) | 5.6000 | 5.5000 | 5.0000 | 6.0000 | -0.4000 | -0.1320 | not resampled |
| valid_hold_sequence_rank [SMALL] | 30/30 (15 sessions) | 3.0667 | 3.0000 | 1.2500 | 4.0000 | 10/10 (7 sessions) | 3.4000 | 3.0000 | 3.0000 | 4.0000 | -0.3333 | -0.1800 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 11/30 (8 sessions) | 0.3882 | 0.3297 | 0.2025 | 0.5961 | 6/10 (4 sessions) | 0.4825 | 0.3681 | 0.1423 | 0.6950 | -0.0943 | -0.2735 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 11/30 (8 sessions) | 0.4706 | 0.4298 | 0.2392 | 0.6565 | 6/10 (4 sessions) | 0.3967 | 0.3573 | 0.1933 | 0.5625 | 0.0739 | 0.2350 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 20/30 (11 sessions) | -0.1562 | -0.1354 | -0.2652 | -0.0702 | 10/10 (7 sessions) | -0.2721 | -0.2738 | -0.3763 | -0.1929 | 0.1159 | 0.7248 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 20/30 (11 sessions) | -0.0887 | -0.0859 | -0.2003 | -0.0205 | 9/10 (6 sessions) | -0.1709 | -0.2023 | -0.2405 | -0.0414 | 0.0822 | 0.5774 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 20/30 (11 sessions) | -0.0734 | -0.0433 | -0.1654 | 0.0135 | 8/10 (5 sessions) | -0.1721 | -0.2134 | -0.2468 | -0.0610 | 0.0987 | 0.6565 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 11/30 (8 sessions) | -0.0463 | -0.0534 | -0.0921 | 0.0020 | 6/10 (4 sessions) | -0.1081 | -0.0905 | -0.1771 | -0.0335 | 0.0618 | 0.5822 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 11/30 (8 sessions) | -0.0206 | -0.0143 | -0.0709 | 0.0201 | 5/10 (4 sessions) | -0.0404 | -0.0345 | -0.0913 | -0.0051 | 0.0197 | 0.1866 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 11/30 (8 sessions) | -0.0101 | -0.0207 | -0.0619 | 0.0528 | 5/10 (4 sessions) | -0.0234 | -0.0374 | -0.0855 | -0.0209 | 0.0133 | 0.1175 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 30/30 (15 sessions) | -0.1064 | -0.0422 | -0.1808 | -0.0078 | 10/10 (7 sessions) | -0.0710 | -0.0531 | -0.0959 | -0.0290 | -0.0354 | -0.2487 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 27/30 (14 sessions) | -0.0476 | -0.0126 | -0.0575 | -0.0024 | 10/10 (7 sessions) | -0.0401 | -0.0328 | -0.0849 | -0.0103 | -0.0075 | -0.0931 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 25/30 (12 sessions) | -0.0304 | -0.0159 | -0.0527 | 0.0017 | 10/10 (7 sessions) | -0.0358 | -0.0303 | -0.0868 | -0.0076 | 0.0054 | 0.0892 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 10/30 (7 sessions) | 0.2000 | 0.0000 | 0.0000 | 0.0000 | 4/10 (3 sessions) | 0.2500 | 0.0000 | 0.0000 | 0.2500 | -0.0500 | -0.1130 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 10/30 (7 sessions) | 0.4000 | 0.0000 | 0.0000 | 1.0000 | 4/10 (3 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | -0.1000 | -0.1879 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 5/30 (5 sessions) | 0.8000 | 1.0000 | 1.0000 | 1.0000 | 3/10 (3 sessions) | 0.6667 | 1.0000 | 0.5000 | 1.0000 | 0.1333 | 0.2697 | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 18/30 (11 sessions) | 0.4444 | 0.0000 | 0.0000 | 1.0000 | 8/10 (5 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | -0.0556 | -0.0937 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 11/30 (8 sessions) | 0.9091 | 1.0000 | 1.0000 | 1.0000 | 6/10 (4 sessions) | 0.6667 | 0.5000 | 0.0000 | 1.0000 | 0.2424 | 0.3758 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 10/30 (7 sessions) | 1.4000 | 1.0000 | 1.0000 | 1.7500 | 4/10 (3 sessions) | 1.0000 | 1.0000 | 0.7500 | 1.2500 | 0.4000 | 0.5477 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 10/30 (7 sessions) | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 4/10 (3 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1000 | 0.3651 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 10/30 (7 sessions) | 0.3000 | 0.0000 | 0.0000 | 0.7500 | 4/10 (3 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.3000 | 0.7171 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 5/30 (5 sessions) | 0.6000 | 1.0000 | 0.0000 | 1.0000 | 3/10 (3 sessions) | 0.6667 | 1.0000 | 0.5000 | 1.0000 | -0.0667 | -0.1195 | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 20/30 (11 sessions) | 1.1500 | 1.0000 | 0.0000 | 2.0000 | 10/10 (7 sessions) | 0.8000 | 0.5000 | 0.0000 | 1.0000 | 0.3500 | 0.2923 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 20/30 (11 sessions) | 2.5000 | 2.0000 | 1.0000 | 3.2500 | 8/10 (5 sessions) | 0.8750 | 1.0000 | 0.7500 | 1.0000 | 1.6250 | 0.9389 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 11/30 (8 sessions) | 2.4545 | 1.0000 | 1.0000 | 3.5000 | 5/10 (4 sessions) | 1.2000 | 1.0000 | 1.0000 | 2.0000 | 1.2545 | 0.5712 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 20/30 (11 sessions) | 2.5478 | 2.2500 | 1.6450 | 3.0838 | 10/10 (7 sessions) | 2.9326 | 2.7750 | 2.1575 | 3.7414 | -0.3848 | -0.3006 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 20/30 (11 sessions) | 3.3512 | 3.0125 | 2.3912 | 4.0525 | 8/10 (5 sessions) | 4.0181 | 4.4950 | 2.4025 | 5.0438 | -0.6669 | -0.4440 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 11/30 (8 sessions) | 4.1264 | 3.6105 | 3.2175 | 4.5900 | 5/10 (4 sessions) | 4.4460 | 4.5100 | 2.9900 | 4.7100 | -0.3196 | -0.2118 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 18/30 (11 sessions) | 2.4375 | 2.0435 | 1.8788 | 2.6872 | 8/10 (5 sessions) | 2.4939 | 2.6520 | 2.1552 | 2.7782 | -0.0564 | -0.0636 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 18/30 (11 sessions) | 3.3537 | 3.2670 | 2.5353 | 3.7989 | 8/10 (5 sessions) | 3.3898 | 3.5461 | 3.0001 | 3.6932 | -0.0360 | -0.0386 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 11/30 (8 sessions) | 4.9621 | 4.4159 | 4.1841 | 4.9172 | 5/10 (4 sessions) | 4.4056 | 4.5999 | 3.8323 | 5.0688 | 0.5565 | 0.4710 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 20/30 (11 sessions) | 0.4243 | 0.3403 | 0.2273 | 0.6020 | 10/10 (7 sessions) | 0.4829 | 0.4829 | 0.3867 | 0.6319 | -0.0586 | -0.2193 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 20/30 (11 sessions) | 0.2732 | 0.2084 | 0.0854 | 0.4315 | 8/10 (5 sessions) | 0.3375 | 0.4399 | 0.0805 | 0.5306 | -0.0643 | -0.2881 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 11/30 (8 sessions) | 0.2308 | 0.2475 | 0.0881 | 0.3363 | 5/10 (4 sessions) | 0.1451 | 0.1123 | 0.0950 | 0.2322 | 0.0858 | 0.6318 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 20/30 (11 sessions) | 0.9900 | 1.0000 | 1.0000 | 1.0000 | 10/10 (7 sessions) | 0.9800 | 1.0000 | 1.0000 | 1.0000 | 0.0100 | 0.1945 | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 20/30 (11 sessions) | 0.9909 | 1.0000 | 1.0000 | 1.0000 | 8/10 (5 sessions) | 0.9886 | 1.0000 | 1.0000 | 1.0000 | 0.0023 | 0.0779 | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 11/30 (8 sessions) | 0.9921 | 1.0000 | 1.0000 | 1.0000 | 5/10 (4 sessions) | 0.9913 | 1.0000 | 1.0000 | 1.0000 | 0.0008 | 0.0436 | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 20/30 (11 sessions) | 0.6625 | 0.7500 | 0.5000 | 0.7500 | 10/10 (7 sessions) | 0.6500 | 0.7500 | 0.5000 | 0.7500 | 0.0125 | 0.0530 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 20/30 (11 sessions) | 0.6250 | 0.6000 | 0.6000 | 0.7000 | 8/10 (5 sessions) | 0.5750 | 0.5500 | 0.5000 | 0.7000 | 0.0500 | 0.4714 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 11/30 (8 sessions) | 0.5579 | 0.5455 | 0.4773 | 0.6136 | 5/10 (4 sessions) | 0.5636 | 0.5455 | 0.5455 | 0.6364 | -0.0058 | -0.0618 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 18/30 (11 sessions) | 1.1781 | 1.0326 | 0.5728 | 1.6398 | 8/10 (5 sessions) | 1.4161 | 1.4913 | 1.2093 | 1.7232 | -0.2380 | -0.3251 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 18/30 (11 sessions) | 0.6190 | 0.3455 | 0.1933 | 0.8628 | 8/10 (5 sessions) | 0.7077 | 0.5697 | 0.3784 | 0.7668 | -0.0888 | -0.1506 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 11/30 (8 sessions) | 0.4521 | 0.3227 | 0.1731 | 0.7069 | 6/10 (4 sessions) | 0.4447 | 0.3482 | 0.2450 | 0.4551 | 0.0075 | 0.0190 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 27/30 (14 sessions) | 1.5932 | 1.3320 | 0.4500 | 2.3200 | 9/10 (6 sessions) | 2.1828 | 2.0800 | 0.7900 | 2.8700 | -0.5895 | -0.3863 | not resampled |
| stage11_2.room_in_atr [SMALL] | 15/30 (10 sessions) | 1.6882 | 1.4398 | 0.7961 | 2.2280 | 7/10 (4 sessions) | 2.0239 | 1.7587 | 1.1121 | 3.0120 | -0.3357 | -0.2626 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 30/30 (15 sessions) | 4.1667 | 4.0000 | 4.0000 | 4.0000 | 10/10 (7 sessions) | 4.1000 | 4.0000 | 4.0000 | 4.0000 | 0.0667 | 0.0821 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 30/30 (15 sessions) | 1.8333 | 2.0000 | 2.0000 | 2.0000 | 10/10 (7 sessions) | 1.9000 | 2.0000 | 2.0000 | 2.0000 | -0.0667 | -0.0821 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 30/30 (15 sessions) | 0.3646 | 0.3625 | 0.1950 | 0.4548 | 10/10 (7 sessions) | 0.2565 | 0.2400 | 0.1025 | 0.3538 | 0.1081 | 0.4384 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 27/30 (14 sessions) | 1.5932 | 1.3320 | 0.4500 | 2.3200 | 9/10 (6 sessions) | 2.1828 | 2.0800 | 0.7900 | 2.8700 | -0.5895 | -0.3863 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 18/30 (11 sessions) | 0.0556 | 0.0000 | 0.0000 | 0.0000 | 8/10 (5 sessions) | 0.1250 | 0.0000 | 0.0000 | 0.0000 | -0.0694 | -0.2522 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 18/30 (11 sessions) | 0.2778 | 0.0000 | 0.0000 | 0.7500 | 8/10 (5 sessions) | 0.1250 | 0.0000 | 0.0000 | 0.0000 | 0.1528 | 0.3534 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 20/30 (11 sessions) | 2.0619 | 1.6550 | 1.1270 | 2.5012 | 9/10 (6 sessions) | 2.9462 | 2.3650 | 1.9805 | 4.2500 | -0.8842 | -0.6388 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 20/30 (11 sessions) | 1.1434 | 0.9510 | 0.3500 | 1.6712 | 8/10 (6 sessions) | 0.9644 | 0.5425 | 0.3900 | 1.3625 | 0.1791 | 0.1801 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 18/30 (11 sessions) | 2.1083 | 1.7714 | 1.1257 | 2.9937 | 8/10 (5 sessions) | 2.5816 | 2.9637 | 1.7152 | 3.2142 | -0.4734 | -0.3962 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 18/30 (11 sessions) | 1.2361 | 0.8473 | 0.3390 | 1.8148 | 6/10 (4 sessions) | 1.0544 | 0.9783 | 0.5704 | 1.5884 | 0.1817 | 0.1697 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | SHORT | 40 | 16 | 30 | 10 | 100.00% | 100.00% | 75.00% |
| time_bucket | 09:35-10:00 [SMALL] | 10 | 10 | 10 | 0 | 33.33% | 0.00% | 100.00% |
| time_bucket | 10:00-10:30 [SMALL] | 2 | 2 | 0 | 2 | 0.00% | 20.00% | 0.00% |
| time_bucket | 10:30-11:00 [SMALL] | 9 | 7 | 7 | 2 | 23.33% | 20.00% | 77.78% |
| time_bucket | 11:00-12:00 [SMALL] | 5 | 3 | 3 | 2 | 10.00% | 20.00% | 60.00% |
| time_bucket | 12:00-13:30 [SMALL] | 8 | 4 | 5 | 3 | 16.67% | 30.00% | 62.50% |
| time_bucket | 13:30-15:00 [SMALL] | 4 | 4 | 4 | 0 | 13.33% | 0.00% | 100.00% |
| time_bucket | 15:00-close [SMALL] | 2 | 1 | 1 | 1 | 3.33% | 10.00% | 50.00% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 9 | 4 | 5 | 4 | 16.67% | 40.00% | 55.56% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 8 | 5 | 6 | 2 | 20.00% | 20.00% | 75.00% |
| ema9_20_alignment | EMA_UNAVAILABLE [SMALL] | 23 | 15 | 19 | 4 | 63.33% | 40.00% | 82.61% |
| price_vwap_alignment | VWAP_ALIGNED | 34 | 16 | 25 | 9 | 83.33% | 90.00% | 73.53% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 6 | 5 | 5 | 1 | 16.67% | 10.00% | 83.33% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED [SMALL] | 18 | 8 | 12 | 6 | 40.00% | 60.00% | 66.67% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 12 | 8 | 8 | 4 | 26.67% | 40.00% | 66.67% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 10 | 10 | 10 | 0 | 33.33% | 0.00% | 100.00% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 9 | 5 | 6 | 3 | 20.00% | 30.00% | 66.67% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 8 | 6 | 5 | 3 | 16.67% | 30.00% | 62.50% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE [SMALL] | 23 | 15 | 19 | 4 | 63.33% | 40.00% | 82.61% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 6 | 2 | 4 | 2 | 13.33% | 20.00% | 66.67% |
| prior_ema_cross | NO_PRIOR_CROSS [SMALL] | 26 | 16 | 20 | 6 | 66.67% | 60.00% | 76.92% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 8 | 5 | 6 | 2 | 20.00% | 20.00% | 75.00% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 33 | 12 | 23 | 10 | 76.67% | 100.00% | 69.70% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 7 | 6 | 7 | 0 | 23.33% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 4 | 2 | 4 | 0 | 13.33% | 0.00% | 100.00% |
| stage11_2.room_bucket | ATR_1_0_TO_1_5 [SMALL] | 5 | 4 | 3 | 2 | 10.00% | 20.00% | 60.00% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 2 | 2 | 1 | 1 | 3.33% | 10.00% | 50.00% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 6 | 4 | 5 | 1 | 16.67% | 10.00% | 83.33% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 3 | 2 | 1 | 2 | 3.33% | 20.00% | 33.33% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 2 | 2 | 1 | 1 | 3.33% | 10.00% | 50.00% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 4 | 1 | 3 | 1 | 10.00% | 10.00% | 75.00% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 14 | 12 | 12 | 2 | 40.00% | 20.00% | 85.71% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 40 | 16 | 30 | 10 | 100.00% | 100.00% | 75.00% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 6 | 6 | 5 | 1 | 16.67% | 10.00% | 83.33% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 8 | 6 | 5 | 3 | 16.67% | 30.00% | 62.50% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 8 | 5 | 6 | 2 | 20.00% | 20.00% | 75.00% |
| stage11_3.structure | UNAVAILABLE [SMALL] | 18 | 13 | 14 | 4 | 46.67% | 40.00% | 77.78% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 6 | 6 | 5 | 1 | 16.67% | 10.00% | 83.33% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 16 | 9 | 11 | 5 | 36.67% | 50.00% | 68.75% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE [SMALL] | 18 | 13 | 14 | 4 | 46.67% | 40.00% | 77.78% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 12 | 8 | 7 | 5 | 23.33% | 50.00% | 58.33% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 14 | 7 | 11 | 3 | 36.67% | 30.00% | 78.57% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 14 | 12 | 12 | 2 | 40.00% | 20.00% | 85.71% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 17 | 9 | 12 | 5 | 40.00% | 50.00% | 70.59% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 6 | 6 | 5 | 1 | 16.67% | 10.00% | 83.33% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 17 | 13 | 13 | 4 | 43.33% | 40.00% | 76.47% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 12 | 11 | 10 | 2 | 33.33% | 20.00% | 83.33% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 4 | 1 | 3 | 1 | 10.00% | 10.00% | 75.00% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 6 | 5 | 4 | 2 | 13.33% | 20.00% | 66.67% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 18 | 9 | 13 | 5 | 43.33% | 50.00% | 72.22% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 40 | 16 | 30 | 10 | 100.00% | 100.00% | 75.00% |


### 2026-08


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 46/46 (17 sessions) | 1.3029 | 1.3140 | 1.0200 | 1.5600 | 16/16 (10 sessions) | 1.1446 | 1.0800 | 0.7700 | 1.3297 | 0.1584 | 0.3832 | not resampled |
| body_size [SMALL] | 46/46 (17 sessions) | 0.5470 | 0.4794 | 0.3425 | 0.6950 | 16/16 (10 sessions) | 0.3347 | 0.2975 | 0.1838 | 0.4376 | 0.2123 | 0.6912 | not resampled |
| directional_body [SMALL] | 46/46 (17 sessions) | 0.5470 | 0.4794 | 0.3425 | 0.6950 | 16/16 (10 sessions) | 0.3347 | 0.2975 | 0.1838 | 0.4376 | 0.2123 | 0.6912 | not resampled |
| candle_range [SMALL] | 46/46 (17 sessions) | 0.7948 | 0.7150 | 0.5750 | 1.0088 | 16/16 (10 sessions) | 0.6379 | 0.5550 | 0.3800 | 0.7600 | 0.1569 | 0.3874 | not resampled |
| body_range_ratio [SMALL] | 46/46 (17 sessions) | 0.6685 | 0.7121 | 0.5275 | 0.8265 | 16/16 (10 sessions) | 0.5389 | 0.5502 | 0.3900 | 0.6892 | 0.1296 | 0.5924 | not resampled |
| directional_body_range_ratio [SMALL] | 46/46 (17 sessions) | 0.6685 | 0.7121 | 0.5275 | 0.8265 | 16/16 (10 sessions) | 0.5389 | 0.5502 | 0.3900 | 0.6892 | 0.1296 | 0.5924 | not resampled |
| close_location [SMALL] | 46/46 (17 sessions) | 0.1393 | 0.0817 | 0.0296 | 0.1985 | 16/16 (10 sessions) | 0.2652 | 0.2441 | 0.1047 | 0.3883 | -0.1259 | -0.7153 | not resampled |
| directional_close_location [SMALL] | 46/46 (17 sessions) | 0.8607 | 0.9183 | 0.8015 | 0.9704 | 16/16 (10 sessions) | 0.7348 | 0.7559 | 0.6117 | 0.8953 | 0.1259 | 0.7153 | not resampled |
| distance_beyond_level [SMALL] | 46/46 (17 sessions) | 0.3124 | 0.2338 | 0.1124 | 0.4212 | 16/16 (10 sessions) | 0.1995 | 0.1600 | 0.0988 | 0.2600 | 0.1128 | 0.4332 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 29/46 (12 sessions) | 0.5068 | 0.4467 | 0.1654 | 0.6956 | 10/16 (6 sessions) | 0.3042 | 0.3098 | 0.1776 | 0.4310 | 0.2026 | 0.5121 | not resampled |
| candle_volume [SMALL] | 46/46 (17 sessions) | 388048.1739 | 356423.5000 | 254608.2500 | 513885.0000 | 16/16 (10 sessions) | 561136.9375 | 460581.0000 | 255334.5000 | 591756.5000 | -173088.7636 | -0.6312 | not resampled |
| relative_volume_prior_6 [SMALL] | 37/46 (16 sessions) | 1.0716 | 0.9455 | 0.6783 | 1.4455 | 13/16 (8 sessions) | 1.4692 | 1.0217 | 0.7622 | 1.9603 | -0.3976 | -0.5703 | not resampled |
| atr14 [SMALL] | 29/46 (12 sessions) | 0.6028 | 0.5589 | 0.4572 | 0.7691 | 10/16 (6 sessions) | 0.4780 | 0.4463 | 0.3851 | 0.5748 | 0.1248 | 0.6457 | not resampled |
| minutes_since_open [SMALL] | 46/46 (17 sessions) | 143.4783 | 105.0000 | 36.2500 | 220.0000 | 16/16 (10 sessions) | 193.4375 | 200.0000 | 57.5000 | 348.7500 | -49.9592 | -0.3986 | not resampled |
| minutes_since_ema_cross [SMALL] | 19/46 (9 sessions) | 44.4737 | 30.0000 | 10.0000 | 77.5000 | 10/16 (6 sessions) | 41.5000 | 17.5000 | 11.2500 | 47.5000 | 2.9737 | 0.0654 | not resampled |
| break_attempt_rank [SMALL] | 46/46 (17 sessions) | 7.0652 | 6.5000 | 4.0000 | 9.7500 | 16/16 (10 sessions) | 8.1250 | 8.0000 | 3.0000 | 11.2500 | -1.0598 | -0.2301 | not resampled |
| valid_hold_sequence_rank [SMALL] | 46/46 (17 sessions) | 4.0652 | 3.0000 | 2.0000 | 6.0000 | 16/16 (10 sessions) | 4.8750 | 5.0000 | 2.0000 | 7.0000 | -0.8098 | -0.2850 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 26/46 (11 sessions) | 0.1899 | 0.1480 | 0.0582 | 0.2695 | 10/16 (6 sessions) | 0.1627 | 0.1776 | 0.0316 | 0.2415 | 0.0272 | 0.1741 | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 26/46 (11 sessions) | 0.3094 | 0.3493 | 0.1599 | 0.4151 | 10/16 (6 sessions) | 0.3183 | 0.3469 | 0.0932 | 0.5193 | -0.0088 | -0.0408 | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 32/46 (14 sessions) | -0.1185 | -0.0982 | -0.1668 | -0.0461 | 13/16 (8 sessions) | -0.0951 | -0.0957 | -0.1459 | -0.0155 | -0.0234 | -0.2284 | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 30/46 (13 sessions) | -0.0711 | -0.0452 | -0.1148 | -0.0111 | 12/16 (8 sessions) | -0.0501 | -0.0501 | -0.1020 | 0.0050 | -0.0211 | -0.2288 | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 30/46 (13 sessions) | -0.0640 | -0.0395 | -0.1180 | -0.0052 | 12/16 (8 sessions) | -0.0504 | -0.0312 | -0.1294 | 0.0180 | -0.0136 | -0.1460 | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 23/46 (10 sessions) | -0.0699 | -0.0623 | -0.1092 | -0.0221 | 10/16 (6 sessions) | -0.0460 | -0.0462 | -0.0819 | -0.0111 | -0.0240 | -0.4021 | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 23/46 (10 sessions) | -0.0461 | -0.0322 | -0.0849 | -0.0047 | 10/16 (6 sessions) | -0.0331 | -0.0230 | -0.0771 | 0.0018 | -0.0129 | -0.2396 | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 22/46 (10 sessions) | -0.0402 | -0.0311 | -0.0722 | 0.0036 | 10/16 (6 sessions) | -0.0341 | -0.0224 | -0.0786 | 0.0039 | -0.0061 | -0.1101 | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 46/46 (17 sessions) | -0.0403 | -0.0178 | -0.0465 | -0.0060 | 16/16 (10 sessions) | -0.0500 | -0.0212 | -0.1035 | -0.0071 | 0.0097 | 0.1599 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 45/46 (17 sessions) | -0.0245 | -0.0105 | -0.0346 | -0.0035 | 13/16 (8 sessions) | -0.0169 | -0.0122 | -0.0192 | -0.0041 | -0.0075 | -0.2119 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 44/46 (17 sessions) | -0.0220 | -0.0114 | -0.0292 | -0.0032 | 13/16 (8 sessions) | -0.0183 | -0.0116 | -0.0356 | -0.0043 | -0.0037 | -0.1282 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 22/46 (10 sessions) | 0.5000 | 0.0000 | 0.0000 | 1.0000 | 10/16 (6 sessions) | 0.6000 | 1.0000 | 0.0000 | 1.0000 | -0.1000 | -0.1469 | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 17/46 (10 sessions) | 0.7059 | 1.0000 | 0.0000 | 1.0000 | 10/16 (6 sessions) | 0.9000 | 1.0000 | 0.2500 | 1.0000 | -0.1941 | -0.2753 | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 13/46 (7 sessions) | 1.4615 | 1.0000 | 1.0000 | 2.0000 | 6/16 (5 sessions) | 1.1667 | 1.0000 | 0.2500 | 1.7500 | 0.2949 | 0.2295 | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 29/46 (12 sessions) | 0.3448 | 0.0000 | 0.0000 | 0.0000 | 10/16 (6 sessions) | 0.4000 | 0.0000 | 0.0000 | 1.0000 | -0.0552 | -0.0868 | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 26/46 (11 sessions) | 0.7692 | 0.5000 | 0.0000 | 1.0000 | 10/16 (6 sessions) | 0.7000 | 0.5000 | 0.0000 | 1.0000 | 0.0692 | 0.0728 | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 17/46 (10 sessions) | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 10/16 (6 sessions) | 1.3000 | 1.0000 | 0.0000 | 2.7500 | -0.3000 | -0.2569 | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 22/46 (10 sessions) | 0.0909 | 0.0000 | 0.0000 | 0.0000 | 10/16 (6 sessions) | 0.3000 | 0.0000 | 0.0000 | 0.7500 | -0.2091 | -0.5786 | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 17/46 (10 sessions) | 0.2941 | 0.0000 | 0.0000 | 0.0000 | 10/16 (6 sessions) | 0.5000 | 0.0000 | 0.0000 | 0.7500 | -0.2059 | -0.2968 | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 13/46 (7 sessions) | 0.4615 | 0.0000 | 0.0000 | 1.0000 | 6/16 (5 sessions) | 0.5000 | 0.0000 | 0.0000 | 0.0000 | -0.0385 | -0.0444 | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 40/46 (17 sessions) | 1.2750 | 1.0000 | 0.0000 | 2.0000 | 13/16 (8 sessions) | 0.5385 | 0.0000 | 0.0000 | 1.0000 | 0.7365 | 0.6836 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 30/46 (13 sessions) | 2.2000 | 2.0000 | 1.0000 | 3.7500 | 12/16 (8 sessions) | 1.5000 | 1.0000 | 0.0000 | 2.2500 | 0.7000 | 0.4079 | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 22/46 (10 sessions) | 3.8636 | 4.0000 | 2.0000 | 5.0000 | 10/16 (6 sessions) | 3.0000 | 3.0000 | 1.2500 | 4.0000 | 0.8636 | 0.3501 | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 40/46 (17 sessions) | 1.4237 | 1.2450 | 0.8575 | 1.8862 | 13/16 (8 sessions) | 1.4892 | 1.2550 | 0.6600 | 2.0250 | -0.0655 | -0.0849 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 30/46 (13 sessions) | 1.8700 | 1.6000 | 1.2100 | 2.4100 | 12/16 (8 sessions) | 1.8475 | 1.6575 | 1.0738 | 2.5712 | 0.0225 | 0.0233 | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 22/46 (10 sessions) | 2.3388 | 1.9390 | 1.4925 | 2.8875 | 10/16 (6 sessions) | 2.1165 | 1.8525 | 1.5225 | 2.8938 | 0.2223 | 0.1971 | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 29/46 (12 sessions) | 2.0924 | 1.9903 | 1.6601 | 2.3869 | 10/16 (6 sessions) | 2.5414 | 2.5622 | 1.5267 | 3.4724 | -0.4490 | -0.5532 | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 29/46 (12 sessions) | 3.0288 | 2.8211 | 2.1694 | 3.3719 | 10/16 (6 sessions) | 3.3703 | 3.3741 | 2.4553 | 4.4020 | -0.3415 | -0.3320 | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 22/46 (10 sessions) | 4.0538 | 3.9221 | 3.2021 | 4.7276 | 10/16 (6 sessions) | 4.3092 | 4.2683 | 3.5492 | 4.8074 | -0.2554 | -0.2684 | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 40/46 (17 sessions) | 0.4311 | 0.4062 | 0.1880 | 0.6201 | 13/16 (8 sessions) | 0.4164 | 0.4296 | 0.1299 | 0.5366 | 0.0147 | 0.0499 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 30/46 (13 sessions) | 0.2966 | 0.2517 | 0.1059 | 0.4536 | 12/16 (8 sessions) | 0.3177 | 0.2433 | 0.1794 | 0.4680 | -0.0211 | -0.1033 | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 22/46 (10 sessions) | 0.1402 | 0.1215 | 0.0468 | 0.2209 | 10/16 (6 sessions) | 0.1842 | 0.1397 | 0.0819 | 0.2646 | -0.0440 | -0.3791 | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 40/46 (17 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 13/16 (8 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 30/46 (13 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 12/16 (8 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 22/46 (10 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 10/16 (6 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 40/46 (17 sessions) | 0.5688 | 0.5000 | 0.5000 | 0.7500 | 13/16 (8 sessions) | 0.5000 | 0.5000 | 0.5000 | 0.5000 | 0.0688 | 0.2896 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 30/46 (13 sessions) | 0.5600 | 0.6000 | 0.4000 | 0.7000 | 12/16 (8 sessions) | 0.4667 | 0.4500 | 0.4000 | 0.6000 | 0.0933 | 0.5437 | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 22/46 (10 sessions) | 0.5475 | 0.5909 | 0.4432 | 0.6818 | 10/16 (6 sessions) | 0.5045 | 0.4773 | 0.4205 | 0.6250 | 0.0430 | 0.2942 | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 29/46 (12 sessions) | 1.3410 | 1.3775 | 0.8858 | 1.7918 | 10/16 (6 sessions) | 1.5482 | 1.2925 | 1.1727 | 1.7537 | -0.2072 | -0.2993 | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 29/46 (12 sessions) | 0.6713 | 0.5651 | 0.2958 | 0.9504 | 10/16 (6 sessions) | 0.7822 | 0.9251 | 0.6973 | 1.0477 | -0.1109 | -0.2284 | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 26/46 (11 sessions) | 0.5125 | 0.5680 | 0.1319 | 0.7809 | 10/16 (6 sessions) | 0.6534 | 0.6537 | 0.4006 | 0.9023 | -0.1409 | -0.3753 | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 27/46 (13 sessions) | 1.2920 | 1.3709 | 0.5900 | 1.7825 | 16/16 (10 sessions) | 0.5837 | 0.5750 | 0.1200 | 0.9400 | 0.7083 | 0.9217 | not resampled |
| stage11_2.room_in_atr [SMALL] | 16/46 (8 sessions) | 2.0734 | 1.8915 | 0.7820 | 2.8253 | 10/16 (6 sessions) | 1.0053 | 0.6885 | 0.3039 | 1.7134 | 1.0682 | 0.8028 | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 46/46 (17 sessions) | 4.8696 | 5.0000 | 4.0000 | 6.0000 | 16/16 (10 sessions) | 4.0000 | 4.0000 | 3.0000 | 5.0000 | 0.8696 | 0.8753 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 46/46 (17 sessions) | 1.1087 | 1.0000 | 0.0000 | 2.0000 | 16/16 (10 sessions) | 2.0000 | 2.0000 | 1.0000 | 3.0000 | -0.8913 | -0.8879 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 46/46 (17 sessions) | 0.2571 | 0.1970 | 0.0750 | 0.3975 | 16/16 (10 sessions) | 0.1995 | 0.1600 | 0.0988 | 0.2600 | 0.0576 | 0.2537 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 27/46 (13 sessions) | 1.2920 | 1.3709 | 0.5900 | 1.7825 | 16/16 (10 sessions) | 0.5837 | 0.5750 | 0.1200 | 0.9400 | 0.7083 | 0.9217 | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 29/46 (12 sessions) | 0.0690 | 0.0000 | 0.0000 | 0.0000 | 10/16 (6 sessions) | 0.5000 | 0.5000 | 0.0000 | 1.0000 | -0.4310 | -1.2554 | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 29/46 (12 sessions) | 0.2069 | 0.0000 | 0.0000 | 0.0000 | 10/16 (6 sessions) | 0.6000 | 1.0000 | 0.0000 | 1.0000 | -0.3931 | -0.8937 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 38/46 (17 sessions) | 1.2924 | 0.9650 | 0.6876 | 1.7725 | 13/16 (8 sessions) | 1.1677 | 1.3900 | 0.3800 | 1.7601 | 0.1247 | 0.1338 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 37/46 (16 sessions) | 0.5644 | 0.3909 | 0.3050 | 0.6800 | 12/16 (8 sessions) | 0.5617 | 0.3700 | 0.2912 | 0.8012 | 0.0027 | 0.0054 | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 29/46 (12 sessions) | 2.1015 | 1.8163 | 1.3859 | 2.4689 | 10/16 (6 sessions) | 1.8895 | 1.7109 | 0.5826 | 2.9499 | 0.2121 | 0.1531 | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 29/46 (12 sessions) | 0.9229 | 0.7240 | 0.5062 | 1.1416 | 10/16 (6 sessions) | 1.1190 | 0.9327 | 0.6449 | 1.4285 | -0.1961 | -0.2890 | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | SHORT | 62 | 17 | 46 | 16 | 100.00% | 100.00% | 74.19% |
| time_bucket | 09:35-10:00 [SMALL] | 9 | 7 | 6 | 3 | 13.04% | 18.75% | 66.67% |
| time_bucket | 10:00-10:30 [SMALL] | 11 | 10 | 10 | 1 | 21.74% | 6.25% | 90.91% |
| time_bucket | 10:30-11:00 [SMALL] | 5 | 4 | 3 | 2 | 6.52% | 12.50% | 60.00% |
| time_bucket | 11:00-12:00 [SMALL] | 9 | 6 | 9 | 0 | 19.57% | 0.00% | 100.00% |
| time_bucket | 12:00-13:30 [SMALL] | 11 | 6 | 7 | 4 | 15.22% | 25.00% | 63.64% |
| time_bucket | 13:30-15:00 [SMALL] | 8 | 6 | 7 | 1 | 15.22% | 6.25% | 87.50% |
| time_bucket | 15:00-close [SMALL] | 9 | 6 | 4 | 5 | 8.70% | 31.25% | 44.44% |
| ema9_20_alignment | EMA_ALIGNED | 31 | 11 | 23 | 8 | 50.00% | 50.00% | 74.19% |
| ema9_20_alignment | EMA_NOT_ALIGNED [SMALL] | 5 | 4 | 3 | 2 | 6.52% | 12.50% | 60.00% |
| ema9_20_alignment | EMA_UNAVAILABLE [SMALL] | 26 | 13 | 20 | 6 | 43.48% | 37.50% | 76.92% |
| price_vwap_alignment | VWAP_ALIGNED | 59 | 17 | 44 | 15 | 95.65% | 93.75% | 74.58% |
| price_vwap_alignment | VWAP_NOT_ALIGNED [SMALL] | 3 | 3 | 2 | 1 | 4.35% | 6.25% | 66.67% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED | 40 | 14 | 29 | 11 | 63.04% | 68.75% | 72.50% |
| ema9_vwap_alignment | EMA9_VWAP_NOT_ALIGNED [SMALL] | 6 | 5 | 4 | 2 | 8.70% | 12.50% | 66.67% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 16 | 10 | 13 | 3 | 28.26% | 18.75% | 81.25% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 29 | 9 | 22 | 7 | 47.83% | 43.75% | 75.86% |
| ema20_vwap_alignment | EMA20_VWAP_NOT_ALIGNED [SMALL] | 7 | 6 | 4 | 3 | 8.70% | 18.75% | 57.14% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE [SMALL] | 26 | 13 | 20 | 6 | 43.48% | 37.50% | 76.92% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 24 | 8 | 16 | 8 | 34.78% | 50.00% | 66.67% |
| prior_ema_cross | NO_PRIOR_CROSS | 33 | 16 | 27 | 6 | 58.70% | 37.50% | 81.82% |
| prior_ema_cross | OPPOSING_CROSS [SMALL] | 5 | 4 | 3 | 2 | 6.52% | 12.50% | 60.00% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE | 35 | 11 | 24 | 11 | 52.17% | 68.75% | 68.57% |
| opposite_boundary_broken | NO_OPPOSITE_BREAK_BY_SIGNAL [SMALL] | 27 | 8 | 22 | 5 | 47.83% | 31.25% | 81.48% |
| stage11_2.room_bucket | ATR_0_5_TO_1_0 [SMALL] | 5 | 4 | 4 | 1 | 8.70% | 6.25% | 80.00% |
| stage11_2.room_bucket | ATR_1_5_TO_2_0 [SMALL] | 5 | 4 | 3 | 2 | 6.52% | 12.50% | 60.00% |
| stage11_2.room_bucket | ATR_2_0_TO_3_0 [SMALL] | 5 | 3 | 3 | 2 | 6.52% | 12.50% | 60.00% |
| stage11_2.room_bucket | GT_3_0_ATR [SMALL] | 4 | 2 | 4 | 0 | 8.70% | 0.00% | 100.00% |
| stage11_2.room_bucket | LT_0_5_ATR [SMALL] | 7 | 3 | 2 | 5 | 4.35% | 31.25% | 28.57% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 19 | 5 | 19 | 0 | 41.30% | 0.00% | 100.00% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 17 | 11 | 11 | 6 | 23.91% | 37.50% | 64.71% |
| known_level_coverage | COMPLETE_V1_UNIVERSE | 62 | 17 | 46 | 16 | 100.00% | 100.00% | 74.19% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 9 | 7 | 7 | 2 | 15.22% | 12.50% | 77.78% |
| stage11_3.structure | BULLISH_STRUCTURE [SMALL] | 8 | 7 | 7 | 1 | 15.22% | 6.25% | 87.50% |
| stage11_3.structure | MIXED_STRUCTURE [SMALL] | 18 | 9 | 11 | 7 | 23.91% | 43.75% | 61.11% |
| stage11_3.structure | UNAVAILABLE [SMALL] | 27 | 14 | 21 | 6 | 45.65% | 37.50% | 77.78% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 9 | 7 | 7 | 2 | 15.22% | 12.50% | 77.78% |
| stage11_3.agreement | STRUCTURE_NOT_ALIGNED [SMALL] | 26 | 12 | 18 | 8 | 39.13% | 50.00% | 69.23% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE [SMALL] | 27 | 14 | 21 | 6 | 45.65% | 37.50% | 77.78% |
| stage11_3.high_structure | HIGHER_HIGH [SMALL] | 14 | 11 | 11 | 3 | 23.91% | 18.75% | 78.57% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 27 | 11 | 19 | 8 | 41.30% | 50.00% | 70.37% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 21 | 12 | 16 | 5 | 34.78% | 31.25% | 76.19% |
| stage11_3.low_structure | EQUAL_LOW [SMALL] | 2 | 1 | 1 | 1 | 2.17% | 6.25% | 50.00% |
| stage11_3.low_structure | HIGHER_LOW [SMALL] | 20 | 12 | 14 | 6 | 30.43% | 37.50% | 70.00% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 13 | 9 | 10 | 3 | 21.74% | 18.75% | 76.92% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 27 | 14 | 21 | 6 | 45.65% | 37.50% | 77.78% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 13 | 10 | 9 | 4 | 19.57% | 25.00% | 69.23% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 16 | 5 | 16 | 0 | 34.78% | 0.00% | 100.00% |
| stage11_3.structural_room | SWING_BEYOND_OBJECTIVE_LEVEL [SMALL] | 9 | 4 | 4 | 5 | 8.70% | 31.25% | 44.44% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 24 | 12 | 17 | 7 | 36.96% | 43.75% | 70.83% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE | 62 | 17 | 46 | 16 | 100.00% | 100.00% | 74.19% |


### 2026-09 — PARTIAL / SMALL


| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opening_range_width [SMALL] | 3/3 (2 sessions) | 0.9663 | 0.9695 | 0.9648 | 0.9695 | 2/2 (2 sessions) | 1.1772 | 1.1772 | 1.0734 | 1.2811 | -0.2109 | -1.2430 | not resampled |
| body_size [SMALL] | 3/3 (2 sessions) | 0.4083 | 0.4699 | 0.3649 | 0.4824 | 2/2 (2 sessions) | 0.3150 | 0.3150 | 0.3125 | 0.3175 | 0.0933 | 0.8841 | not resampled |
| directional_body [SMALL] | 3/3 (2 sessions) | 0.4083 | 0.4699 | 0.3649 | 0.4824 | 2/2 (2 sessions) | 0.3150 | 0.3150 | 0.3125 | 0.3175 | 0.0933 | 0.8841 | not resampled |
| candle_range [SMALL] | 3/3 (2 sessions) | 0.6133 | 0.6250 | 0.6000 | 0.6324 | 2/2 (2 sessions) | 0.7200 | 0.7200 | 0.7150 | 0.7250 | -0.1067 | -3.6878 | not resampled |
| body_range_ratio [SMALL] | 3/3 (2 sessions) | 0.6718 | 0.7920 | 0.5991 | 0.8046 | 2/2 (2 sessions) | 0.4377 | 0.4377 | 0.4312 | 0.4442 | 0.2341 | 1.2425 | not resampled |
| directional_body_range_ratio [SMALL] | 3/3 (2 sessions) | 0.6718 | 0.7920 | 0.5991 | 0.8046 | 2/2 (2 sessions) | 0.4377 | 0.4377 | 0.4312 | 0.4442 | 0.2341 | 1.2425 | not resampled |
| close_location [SMALL] | 3/3 (2 sessions) | 0.2443 | 0.1391 | 0.0696 | 0.3665 | 2/2 (2 sessions) | 0.3835 | 0.3835 | 0.3287 | 0.4382 | -0.1391 | -0.5175 | not resampled |
| directional_close_location [SMALL] | 3/3 (2 sessions) | 0.7557 | 0.8609 | 0.6335 | 0.9304 | 2/2 (2 sessions) | 0.6165 | 0.6165 | 0.5618 | 0.6713 | 0.1391 | 0.5175 | not resampled |
| distance_beyond_level [SMALL] | 3/3 (2 sessions) | 0.2650 | 0.3450 | 0.1875 | 0.3825 | 2/2 (2 sessions) | 0.1400 | 0.1400 | 0.0900 | 0.1900 | 0.1250 | 0.6661 | not resampled |
| distance_beyond_level_atr14 [SMALL] | 2/3 (1 sessions) | 0.4562 | 0.4562 | 0.2579 | 0.6544 | 1/2 (1 sessions) | 0.4644 | 0.4644 | 0.4644 | 0.4644 | -0.0082 | N/A | not resampled |
| candle_volume [SMALL] | 3/3 (2 sessions) | 434545.6667 | 339928.0000 | 321364.5000 | 500418.0000 | 2/2 (2 sessions) | 1048488.0000 | 1048488.0000 | 1033331.5000 | 1063644.5000 | -613942.3333 | -3.7741 | not resampled |
| relative_volume_prior_6 [SMALL] | 3/3 (2 sessions) | 1.1703 | 1.1885 | 0.8918 | 1.4579 | 2/2 (2 sessions) | 1.5352 | 1.5352 | 1.4164 | 1.6539 | -0.3648 | -0.7277 | not resampled |
| atr14 [SMALL] | 2/3 (1 sessions) | 0.4974 | 0.4974 | 0.4950 | 0.4998 | 1/2 (1 sessions) | 0.5168 | 0.5168 | 0.5168 | 0.5168 | -0.0194 | N/A | not resampled |
| minutes_since_open [SMALL] | 3/3 (2 sessions) | 236.6667 | 305.0000 | 172.5000 | 335.0000 | 2/2 (2 sessions) | 212.5000 | 212.5000 | 126.2500 | 298.7500 | 24.1667 | 0.1212 | not resampled |
| minutes_since_ema_cross [SMALL] | 2/3 (1 sessions) | 155.0000 | 155.0000 | 140.0000 | 170.0000 | 1/2 (1 sessions) | 205.0000 | 205.0000 | 205.0000 | 205.0000 | -50.0000 | N/A | not resampled |
| break_attempt_rank [SMALL] | 3/3 (2 sessions) | 10.6667 | 12.0000 | 8.5000 | 13.5000 | 2/2 (2 sessions) | 9.0000 | 9.0000 | 5.5000 | 12.5000 | 1.6667 | 0.2352 | not resampled |
| valid_hold_sequence_rank [SMALL] | 3/3 (2 sessions) | 4.0000 | 5.0000 | 3.0000 | 5.5000 | 2/2 (2 sessions) | 4.5000 | 4.5000 | 3.2500 | 5.7500 | -0.5000 | -0.1682 | not resampled |
| stage10_9.ema9_ema20_absolute_separation [SMALL] | 2/3 (1 sessions) | 0.1885 | 0.1885 | 0.1297 | 0.2474 | 1/2 (1 sessions) | 0.0767 | 0.0767 | 0.0767 | 0.0767 | 0.1118 | N/A | not resampled |
| stage10_9.ema9_ema20_separation_atr14 [SMALL] | 2/3 (1 sessions) | 0.3813 | 0.3813 | 0.2611 | 0.5015 | 1/2 (1 sessions) | 0.1485 | 0.1485 | 0.1485 | 0.1485 | 0.2328 | N/A | not resampled |
| stage10_9.ema9_slope_1_bars [SMALL] | 2/3 (1 sessions) | -0.0848 | -0.0848 | -0.1261 | -0.0436 | 1/2 (1 sessions) | -0.0374 | -0.0374 | -0.0374 | -0.0374 | -0.0474 | N/A | not resampled |
| stage10_9.ema9_slope_2_bars [SMALL] | 2/3 (1 sessions) | -0.0530 | -0.0530 | -0.0919 | -0.0140 | 1/2 (1 sessions) | -0.0009 | -0.0009 | -0.0009 | -0.0009 | -0.0521 | N/A | not resampled |
| stage10_9.ema9_slope_3_bars [SMALL] | 2/3 (1 sessions) | -0.0287 | -0.0287 | -0.0588 | 0.0015 | 1/2 (1 sessions) | -0.0032 | -0.0032 | -0.0032 | -0.0032 | -0.0255 | N/A | not resampled |
| stage10_9.ema20_slope_1_bars [SMALL] | 2/3 (1 sessions) | -0.0556 | -0.0556 | -0.0791 | -0.0320 | 1/2 (1 sessions) | -0.0238 | -0.0238 | -0.0238 | -0.0238 | -0.0317 | N/A | not resampled |
| stage10_9.ema20_slope_2_bars [SMALL] | 2/3 (1 sessions) | -0.0406 | -0.0406 | -0.0623 | -0.0189 | 1/2 (1 sessions) | -0.0077 | -0.0077 | -0.0077 | -0.0077 | -0.0329 | N/A | not resampled |
| stage10_9.ema20_slope_3_bars [SMALL] | 2/3 (1 sessions) | -0.0300 | -0.0300 | -0.0471 | -0.0130 | 1/2 (1 sessions) | -0.0094 | -0.0094 | -0.0094 | -0.0094 | -0.0206 | N/A | not resampled |
| stage10_9.vwap_slope_1_bars [SMALL] | 3/3 (2 sessions) | -0.0329 | -0.0288 | -0.0350 | -0.0287 | 2/2 (2 sessions) | -0.1158 | -0.1158 | -0.1520 | -0.0797 | 0.0829 | 1.3968 | not resampled |
| stage10_9.vwap_slope_2_bars [SMALL] | 3/3 (2 sessions) | -0.0282 | -0.0241 | -0.0316 | -0.0228 | 2/2 (2 sessions) | -0.0862 | -0.0862 | -0.1111 | -0.0613 | 0.0580 | 1.4002 | not resampled |
| stage10_9.vwap_slope_3_bars [SMALL] | 3/3 (2 sessions) | -0.0219 | -0.0196 | -0.0232 | -0.0195 | 2/2 (2 sessions) | -0.0627 | -0.0627 | -0.0757 | -0.0496 | 0.0407 | 1.8885 | not resampled |
| stage10_9.ema9_ema20_cross_count_6_bars [SMALL] | 2/3 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1/2 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage10_9.ema9_ema20_cross_count_12_bars [SMALL] | 2/3 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1/2 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage10_9.ema9_ema20_cross_count_24_bars [SMALL] | 2/3 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1/2 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage10_9.ema9_vwap_cross_count_6_bars [SMALL] | 2/3 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1/2 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage10_9.ema9_vwap_cross_count_12_bars [SMALL] | 2/3 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1/2 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage10_9.ema9_vwap_cross_count_24_bars [SMALL] | 2/3 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1/2 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage10_9.ema20_vwap_cross_count_6_bars [SMALL] | 2/3 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1/2 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage10_9.ema20_vwap_cross_count_12_bars [SMALL] | 2/3 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1/2 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage10_9.ema20_vwap_cross_count_24_bars [SMALL] | 2/3 (1 sessions) | 0.5000 | 0.5000 | 0.2500 | 0.7500 | 1/2 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.5000 | N/A | not resampled |
| stage10_9.price_vwap_side_change_count_6_bars [SMALL] | 3/3 (2 sessions) | 0.6667 | 0.0000 | 0.0000 | 1.0000 | 2/2 (2 sessions) | 0.5000 | 0.5000 | 0.2500 | 0.7500 | 0.1667 | 0.1622 | not resampled |
| stage10_9.price_vwap_side_change_count_12_bars [SMALL] | 2/3 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1/2 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage10_9.price_vwap_side_change_count_24_bars [SMALL] | 2/3 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1/2 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage10_9.rolling_high_low_range_6_bars [SMALL] | 3/3 (2 sessions) | 1.0350 | 1.0950 | 0.9725 | 1.1275 | 2/2 (2 sessions) | 1.6500 | 1.6500 | 1.2575 | 2.0425 | -0.6150 | -0.9394 | not resampled |
| stage10_9.rolling_high_low_range_12_bars [SMALL] | 2/3 (1 sessions) | 1.8450 | 1.8450 | 1.7025 | 1.9875 | 1/2 (1 sessions) | 1.4400 | 1.4400 | 1.4400 | 1.4400 | 0.4050 | N/A | not resampled |
| stage10_9.rolling_high_low_range_24_bars [SMALL] | 2/3 (1 sessions) | 2.2350 | 2.2350 | 1.9775 | 2.4925 | 1/2 (1 sessions) | 2.5600 | 2.5600 | 2.5600 | 2.5600 | -0.3250 | N/A | not resampled |
| stage10_9.rolling_range_atr14_6_bars [SMALL] | 2/3 (1 sessions) | 2.0236 | 2.0236 | 1.8580 | 2.1891 | 1/2 (1 sessions) | 1.6737 | 1.6737 | 1.6737 | 1.6737 | 0.3498 | N/A | not resampled |
| stage10_9.rolling_range_atr14_12_bars [SMALL] | 2/3 (1 sessions) | 3.7038 | 3.7038 | 3.4353 | 3.9724 | 1/2 (1 sessions) | 2.7863 | 2.7863 | 2.7863 | 2.7863 | 0.9175 | N/A | not resampled |
| stage10_9.rolling_range_atr14_24_bars [SMALL] | 2/3 (1 sessions) | 4.4835 | 4.4835 | 3.9875 | 4.9794 | 1/2 (1 sessions) | 4.9535 | 4.9535 | 4.9535 | 4.9535 | -0.4700 | N/A | not resampled |
| stage10_9.directional_efficiency_6_bars [SMALL] | 3/3 (2 sessions) | 0.3610 | 0.4830 | 0.2681 | 0.5149 | 2/2 (2 sessions) | 0.6720 | 0.6720 | 0.5080 | 0.8360 | -0.3110 | -0.8985 | not resampled |
| stage10_9.directional_efficiency_12_bars [SMALL] | 2/3 (1 sessions) | 0.3011 | 0.3011 | 0.2477 | 0.3546 | 1/2 (1 sessions) | 0.0860 | 0.0860 | 0.0860 | 0.0860 | 0.2151 | N/A | not resampled |
| stage10_9.directional_efficiency_24_bars [SMALL] | 2/3 (1 sessions) | 0.1906 | 0.1906 | 0.1583 | 0.2229 | 1/2 (1 sessions) | 0.1422 | 0.1422 | 0.1422 | 0.1422 | 0.0484 | N/A | not resampled |
| stage10_9.range_overlap_fraction_6_bars [SMALL] | 3/3 (2 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 2/2 (2 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_12_bars [SMALL] | 2/3 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1/2 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.range_overlap_fraction_24_bars [SMALL] | 2/3 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1/2 (1 sessions) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_6_bars [SMALL] | 3/3 (2 sessions) | 0.5000 | 0.5000 | 0.3750 | 0.6250 | 2/2 (2 sessions) | 0.2500 | 0.2500 | 0.1250 | 0.3750 | 0.2500 | 0.8660 | not resampled |
| stage10_9.close_direction_alternation_fraction_12_bars [SMALL] | 2/3 (1 sessions) | 0.6500 | 0.6500 | 0.6250 | 0.6750 | 1/2 (1 sessions) | 0.7000 | 0.7000 | 0.7000 | 0.7000 | -0.0500 | N/A | not resampled |
| stage10_9.close_direction_alternation_fraction_24_bars [SMALL] | 2/3 (1 sessions) | 0.6591 | 0.6591 | 0.6250 | 0.6932 | 1/2 (1 sessions) | 0.5455 | 0.5455 | 0.5455 | 0.5455 | 0.1136 | N/A | not resampled |
| stage10_9.confirmation_close_vwap_distance_atr14 [SMALL] | 2/3 (1 sessions) | 2.9504 | 2.9504 | 2.5421 | 3.3587 | 1/2 (1 sessions) | 2.2302 | 2.2302 | 2.2302 | 2.2302 | 0.7202 | N/A | not resampled |
| stage10_9.ema9_vwap_distance_atr14 [SMALL] | 2/3 (1 sessions) | 2.2616 | 2.2616 | 2.1884 | 2.3347 | 1/2 (1 sessions) | 1.9403 | 1.9403 | 1.9403 | 1.9403 | 0.3213 | N/A | not resampled |
| stage10_9.ema20_vwap_distance_atr14 [SMALL] | 2/3 (1 sessions) | 1.8803 | 1.8803 | 1.8332 | 1.9273 | 1/2 (1 sessions) | 1.7919 | 1.7919 | 1.7919 | 1.7919 | 0.0884 | N/A | not resampled |
| stage11_2.room_from_confirmation [SMALL] | 1/3 (1 sessions) | 1.0250 | 1.0250 | 1.0250 | 1.0250 | 1/2 (1 sessions) | 1.3800 | 1.3800 | 1.3800 | 1.3800 | -0.3550 | N/A | not resampled |
| stage11_2.room_in_atr [SMALL] | 0/3 (0 sessions) | N/A | N/A | N/A | N/A | 0/2 (0 sessions) | N/A | N/A | N/A | N/A | N/A | N/A | not resampled |
| stage11_2.number_of_known_levels_above [SMALL] | 3/3 (2 sessions) | 5.3333 | 6.0000 | 5.0000 | 6.0000 | 2/2 (2 sessions) | 4.5000 | 4.5000 | 3.7500 | 5.2500 | 0.8333 | 0.5392 | not resampled |
| stage11_2.number_of_known_levels_below [SMALL] | 3/3 (2 sessions) | 0.6667 | 0.0000 | 0.0000 | 1.0000 | 2/2 (2 sessions) | 1.5000 | 1.5000 | 0.7500 | 2.2500 | -0.8333 | -0.5392 | not resampled |
| stage11_2.nearest_level_distance_above [SMALL] | 3/3 (2 sessions) | 0.2650 | 0.3450 | 0.1875 | 0.3825 | 2/2 (2 sessions) | 0.1400 | 0.1400 | 0.0900 | 0.1900 | 0.1250 | 0.6661 | not resampled |
| stage11_2.nearest_level_distance_below [SMALL] | 1/3 (1 sessions) | 1.0250 | 1.0250 | 1.0250 | 1.0250 | 1/2 (1 sessions) | 1.3800 | 1.3800 | 1.3800 | 1.3800 | -0.3550 | N/A | not resampled |
| stage11_2.directional_level_count_within_0_5_atr [SMALL] | 2/3 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1/2 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage11_2.directional_level_count_within_1_0_atr [SMALL] | 2/3 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1/2 (1 sessions) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | N/A | not resampled |
| stage11_3.confirmation_close_to_latest_swing_high [SMALL] | 2/3 (1 sessions) | 0.7750 | 0.7750 | 0.6225 | 0.9275 | 2/2 (2 sessions) | 1.4575 | 1.4575 | 1.0688 | 1.8462 | -0.6825 | -0.8172 | not resampled |
| stage11_3.confirmation_close_to_latest_swing_low [SMALL] | 3/3 (2 sessions) | 0.6550 | 0.2850 | 0.1525 | 0.9725 | 1/2 (1 sessions) | 1.4500 | 1.4500 | 1.4500 | 1.4500 | -0.7950 | N/A | not resampled |
| stage11_3.distance_to_swing_high_in_atr [SMALL] | 2/3 (1 sessions) | 1.5641 | 1.5641 | 1.2499 | 1.8782 | 1/2 (1 sessions) | 1.3158 | 1.3158 | 1.3158 | 1.3158 | 0.2483 | N/A | not resampled |
| stage11_3.distance_to_swing_low_in_atr [SMALL] | 2/3 (1 sessions) | 1.6729 | 1.6729 | 0.8567 | 2.4890 | 1/2 (1 sessions) | 2.8057 | 2.8057 | 2.8057 | 2.8057 | -1.1328 | N/A | not resampled |


| Feature | category | n | sessions | eventual n | never n | % of eventual | % of never | eventual/category % |
|---|---|---|---|---|---|---|---|---|
| direction | SHORT [SMALL] | 5 | 3 | 3 | 2 | 100.00% | 100.00% | 60.00% |
| time_bucket | 10:00-10:30 [SMALL] | 2 | 2 | 1 | 1 | 33.33% | 50.00% | 50.00% |
| time_bucket | 13:30-15:00 [SMALL] | 1 | 1 | 1 | 0 | 33.33% | 0.00% | 100.00% |
| time_bucket | 15:00-close [SMALL] | 2 | 1 | 1 | 1 | 33.33% | 50.00% | 50.00% |
| ema9_20_alignment | EMA_ALIGNED [SMALL] | 3 | 1 | 2 | 1 | 66.67% | 50.00% | 66.67% |
| ema9_20_alignment | EMA_UNAVAILABLE [SMALL] | 2 | 2 | 1 | 1 | 33.33% | 50.00% | 50.00% |
| price_vwap_alignment | VWAP_ALIGNED [SMALL] | 5 | 3 | 3 | 2 | 100.00% | 100.00% | 60.00% |
| ema9_vwap_alignment | EMA9_VWAP_ALIGNED [SMALL] | 3 | 1 | 2 | 1 | 66.67% | 50.00% | 66.67% |
| ema9_vwap_alignment | EMA9_VWAP_UNAVAILABLE [SMALL] | 2 | 2 | 1 | 1 | 33.33% | 50.00% | 50.00% |
| ema20_vwap_alignment | EMA20_VWAP_ALIGNED [SMALL] | 3 | 1 | 2 | 1 | 66.67% | 50.00% | 66.67% |
| ema20_vwap_alignment | EMA20_VWAP_UNAVAILABLE [SMALL] | 2 | 2 | 1 | 1 | 33.33% | 50.00% | 50.00% |
| prior_ema_cross | MATCHING_CROSS [SMALL] | 3 | 1 | 2 | 1 | 66.67% | 50.00% | 66.67% |
| prior_ema_cross | NO_PRIOR_CROSS [SMALL] | 2 | 2 | 1 | 1 | 33.33% | 50.00% | 50.00% |
| opposite_boundary_broken | BOTH_BROKEN_BEFORE_SIGNAL_CLOSE [SMALL] | 5 | 3 | 3 | 2 | 100.00% | 100.00% | 60.00% |
| stage11_2.room_bucket | OPEN_ENDED [SMALL] | 3 | 1 | 2 | 1 | 66.67% | 50.00% | 66.67% |
| stage11_2.room_bucket | UNAVAILABLE_ATR [SMALL] | 2 | 2 | 1 | 1 | 33.33% | 50.00% | 50.00% |
| known_level_coverage | COMPLETE_V1_UNIVERSE [SMALL] | 5 | 3 | 3 | 2 | 100.00% | 100.00% | 60.00% |
| stage11_3.structure | BEARISH_STRUCTURE [SMALL] | 3 | 1 | 2 | 1 | 66.67% | 50.00% | 66.67% |
| stage11_3.structure | UNAVAILABLE [SMALL] | 2 | 2 | 1 | 1 | 33.33% | 50.00% | 50.00% |
| stage11_3.agreement | STRUCTURE_ALIGNED [SMALL] | 3 | 1 | 2 | 1 | 66.67% | 50.00% | 66.67% |
| stage11_3.agreement | STRUCTURE_UNAVAILABLE [SMALL] | 2 | 2 | 1 | 1 | 33.33% | 50.00% | 50.00% |
| stage11_3.high_structure | LOWER_HIGH [SMALL] | 3 | 1 | 2 | 1 | 66.67% | 50.00% | 66.67% |
| stage11_3.high_structure | UNAVAILABLE [SMALL] | 2 | 2 | 1 | 1 | 33.33% | 50.00% | 50.00% |
| stage11_3.low_structure | LOWER_LOW [SMALL] | 3 | 1 | 2 | 1 | 66.67% | 50.00% | 66.67% |
| stage11_3.low_structure | UNAVAILABLE [SMALL] | 2 | 2 | 1 | 1 | 33.33% | 50.00% | 50.00% |
| stage11_3.structural_room | DIRECTIONAL_SWING_UNAVAILABLE [SMALL] | 1 | 1 | 0 | 1 | 0.00% | 50.00% | 0.00% |
| stage11_3.structural_room | OBJECTIVE_LEVEL_OPEN_ENDED [SMALL] | 3 | 1 | 2 | 1 | 66.67% | 50.00% | 66.67% |
| stage11_3.structural_room | SWING_NOT_BEYOND_OBJECTIVE_LEVEL [SMALL] | 1 | 1 | 1 | 0 | 33.33% | 0.00% | 100.00% |
| stage11_1.regime | UNAVAILABLE_CALIBRATION_PROVENANCE [SMALL] | 5 | 3 | 3 | 2 | 100.00% | 100.00% | 60.00% |


