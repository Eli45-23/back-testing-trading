# First Hold quality and executable-entry timing

## Bottom line

The frozen population reconciles: **170 sessions, 1,435 breaks, 733 First Holds, 524 eventual-strong, 209 never-strong**. Using the first eligible minute’s open, waiting for strong confirmation costs **$0.2545 on average**, versus **$0.2554** in the original close-reference comparison. The executable cost’s session-bootstrap 95% interval is **$0.2044–$0.3079**.

Executable paired remaining MFE lost: **$0.2802**; MAE improvement: **$-0.1882** (negative means more adverse excursion). There are 522 pairs with both executable entries and 2 unavailable strong entries at session close. Common-sample close comparisons are included in the tables so this denominator change is visible.

This is an entry-reference study, not a fill guarantee or exit strategy. The exact historical minute open omits order latency, spread, slippage, and costs. A feature’s association with surviving one extra candle is not evidence that it improves tradable outcomes.

## Signal-time differences

The following are the largest absolute pooled standardized mean differences, presented descriptively rather than as significance-selected predictors. Overlapping candle geometry and market-condition fields are correlated; they are not independent discoveries. Full availability, medians, quartiles, uncertainty, both directions and every month are in the tables.

| Feature | eventual available/n | mean | median | Q25 | Q75 | never available/n | mean | median | Q25 | Q75 | mean difference E−N | pooled SMD | 95% session CI Δmean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| distance_beyond_level | 524/524 (170 sessions) | 0.4432 | 0.3225 | 0.1500 | 0.5800 | 209/209 (107 sessions) | 0.2041 | 0.1400 | 0.0600 | 0.2800 | 0.2391 | 0.5793 | 0.1884 to 0.2916 |
| distance_beyond_level_atr14 | 293/524 (112 sessions) | 0.4452 | 0.3413 | 0.1550 | 0.6441 | 107/209 (59 sessions) | 0.2201 | 0.1507 | 0.0773 | 0.2893 | 0.2251 | 0.5571 | 0.1636 to 0.2863 |
| body_range_ratio | 524/524 (170 sessions) | 0.6685 | 0.7078 | 0.5461 | 0.8241 | 209/209 (107 sessions) | 0.5611 | 0.5738 | 0.4233 | 0.7011 | 0.1075 | 0.5143 | 0.0732 to 0.1410 |
| directional_body_range_ratio | 524/524 (170 sessions) | 0.6684 | 0.7078 | 0.5461 | 0.8241 | 209/209 (107 sessions) | 0.5611 | 0.5738 | 0.4233 | 0.7011 | 0.1074 | 0.5132 | 0.0731 to 0.1410 |
| body_size | 524/524 (170 sessions) | 0.8088 | 0.6400 | 0.3875 | 1.0349 | 209/209 (107 sessions) | 0.5779 | 0.4500 | 0.2850 | 0.7589 | 0.2308 | 0.3863 | 0.1575 to 0.3021 |
| directional_body | 524/524 (170 sessions) | 0.8087 | 0.6400 | 0.3875 | 1.0349 | 209/209 (107 sessions) | 0.5779 | 0.4500 | 0.2850 | 0.7589 | 0.2308 | 0.3862 | 0.1574 to 0.3021 |
| stage10_9.ema9_vwap_cross_count_12_bars | 243/524 (101 sessions) | 0.6543 | 1.0000 | 0.0000 | 1.0000 | 85/209 (48 sessions) | 0.4353 | 0.0000 | 0.0000 | 1.0000 | 0.2190 | 0.3052 | 0.0560 to 0.3837 |
| stage10_9.ema20_vwap_distance_atr14 | 243/524 (101 sessions) | 0.5393 | 0.3807 | 0.1678 | 0.7756 | 85/209 (48 sessions) | 0.7227 | 0.5064 | 0.2360 | 0.9061 | -0.1834 | -0.2954 | -0.4220 to -0.0086 |
| stage11_2.room_in_atr | 244/524 (99 sessions) | 2.2185 | 1.5492 | 0.6442 | 3.0013 | 91/209 (54 sessions) | 1.6603 | 1.2270 | 0.4124 | 2.0492 | 0.5582 | 0.2661 | 0.0930 to 1.0396 |
| candle_range | 524/524 (170 sessions) | 1.1641 | 0.9850 | 0.6638 | 1.4500 | 209/209 (107 sessions) | 0.9911 | 0.8200 | 0.5800 | 1.2800 | 0.1731 | 0.2479 | 0.0792 to 0.2662 |


### Month-by-month mean differences for these fields


| feature | 2026-01 | 2026-02 | 2026-03 | 2026-04 | 2026-05 | 2026-06 | 2026-07 | 2026-08 | 2026-09 |
|---|---|---|---|---|---|---|---|---|---|
| distance_beyond_level | 0.0708 | 0.2288 | 0.3183 | 0.1568 | 0.2274 | 0.5622 | 0.1658 | 0.1399 | 0.1377 |
| distance_beyond_level_atr14 | 0.2573 | 0.1561 | 0.1203 | 0.1385 | 0.2517 | 0.4266 | 0.1956 | 0.2393 | 0.0521 |
| body_range_ratio | 0.1017 | 0.1089 | 0.1290 | 0.0700 | 0.1693 | 0.0960 | 0.0614 | 0.1235 | -0.0559 |
| directional_body_range_ratio | 0.1017 | 0.1089 | 0.1290 | 0.0700 | 0.1693 | 0.0960 | 0.0605 | 0.1235 | -0.0559 |
| body_size | 0.0147 | 0.2778 | 0.3801 | 0.1691 | 0.2665 | 0.3753 | 0.0143 | 0.1791 | 0.1390 |
| directional_body | 0.0147 | 0.2778 | 0.3801 | 0.1691 | 0.2665 | 0.3753 | 0.0139 | 0.1791 | 0.1390 |
| stage10_9.ema9_vwap_cross_count_12_bars | 0.3750 | 0.4978 | -0.1802 | -0.1013 | 0.4259 | 0.4224 | 0.2826 | 0.0917 | -0.6667 |
| stage10_9.ema20_vwap_distance_atr14 | -0.1600 | 0.0034 | -0.0095 | 0.2925 | -0.3503 | -0.1723 | -0.7591 | -0.0225 | 1.0794 |
| stage11_2.room_in_atr | 1.6300 | 0.7343 | -0.4539 | 0.4060 | 0.8483 | 0.6598 | 0.0065 | 0.3790 | N/A |
| candle_range | -0.1544 | 0.1412 | 0.3364 | 0.1707 | 0.2061 | 0.2477 | -0.0482 | 0.1330 | 0.3659 |


## Decision: six answers

1. **Most different:** deeper First Hold closes beyond ORH5/ORL5 and a larger body relative to candle range. Mean directional distance is $0.4432 for eventual-strong versus $0.2041 for never-strong (SMD 0.579). Mean body/range is 0.6685 versus 0.5611 (SMD 0.514). ATR-normalized distance also differs (SMD 0.557), but only 400/733 observations have a warmed-up ATR.
2. **Monthly consistency:** pooled dollar distance and ATR-normalized distance differences are positive in every displayed month. Pooled body/range differences are positive in January–August but reverse in small, partial September. Direction splits reveal exceptions: dollar distance reverses for shorts in January; body/range reverses for shorts in July. These are broad descriptive patterns, not universal rules.
3. **Weak/noisy:** opening width has effectively zero pooled SMD (0.001), volume −0.040, relative volume −0.014, and ATR 0.153 with a mean-difference interval crossing zero. Several EMA/VWAP cross and room measurements appear different in aggregate but reverse by month or direction and have substantial warm-up unavailability. Do not promote them because one interval excludes zero.
4. **Long versus short:** eventual-strong rates are 70.75% (283/400) for longs and 72.37% (241/333) for shorts. Dollar distance effects exist in both directions but are larger standardized effects for longs (0.706 versus 0.488); body/range is likewise stronger for longs (0.598 versus 0.408). Relative-volume differences have opposing signs and uncertainty spanning zero. Executable waiting costs are $0.2284 for longs and $0.2855 for shorts. Do not impose symmetric feature rules.
5. **Promising enough for a future predeclared test:** distance beyond the boundary and body/range merit a limited continuous-variable replication study of survival. They are not ready as entry-quality filters. Deeper distance mechanically gives more room before a close-reclaim, while a later/farther entry can worsen adverse geometry. Separate survival from the four fixed path outcomes in any follow-up.
6. **Do not turn into filters:** no numeric cutoff, favorable time bucket, alignment state, room bucket, or composite score is supported for deployment here. Body/range is associated with survival but has near-zero executable clean-threshold correlations (−0.012 to +0.014 across the four requested pairs). Distance’s executable clean-threshold correlations are only +0.053 to +0.094, whereas its pre-reclaim MAE association is much larger (Spearman +0.498). These are correlations, not predictive accuracy or incremental edge.

## Outcome quality is a separate question

In the executable-reference analysis, distance beyond the level has Spearman correlations of +0.256 with pre-reclaim MFE and +0.498 with pre-reclaim MAE. Body/range has +0.131 and +0.164 respectively. Thus the strongest survival descriptors are not clearly favorable-risk descriptors. Pre-reclaim duration and distance-to-boundary geometry are partly built into the evaluation; no exit performance is inferred.

All 733 observations remain. Six First Holds occurring at session close have no future outcome and cannot be observed progressing to strong that day; they remain in the requested never-strong label, explicitly censored rather than called failed trades. Stage 10.9/11.3 availability also depends on time of day, so available-only comparisons are not full-population effects.

## Future Hypotheses — not implemented

- Freeze an independent post–September 4, 2026 evaluation of continuous boundary distance and body/range, preserving First Hold and Strong Hold controls, direction splits, missingness and the four fixed threshold pairs. Do not choose cutoffs from this sample.
- Predeclare that stronger survival association alone is insufficient: any proposed entry rule must independently improve path quality without an unacceptable adverse-excursion tradeoff. Account for time-of-day, warm-up availability, volatility and session-close censoring in the future design.
- Freeze dates/sample requirements and a single evaluation schedule before inspecting new outcomes. No repeated peeking, arbitrary combinations, model training, score, or new candidate now. Only after entry policy is separately reviewed should an exit-model study begin.


## Timing and leakage safeguards

- Stored five-minute timestamp = candle start; signal-known time = start + five minutes. The executable selector requires a validated SPY SIP raw RTH minute starting at or after that completion; its open is the separate reference. Its high/low path is included. No confirming-candle constituent minute is eligible.
- Original REFERENCE_CLOSE_V1 signals, prices, paths, definition hash, and files remain unchanged. New outcomes retain original signal records plus separate entry price/time/status fields.
- Feature construction accepts no event outcome or label. Indicators and confirmed swings are recomputed with accepted pure engines using only the completed same-session prefix, ending at the exact First Hold row. Future bars are cut off before indicator computation.
- Session-reset EMA/ATR warm-up is retained. Relative volume excludes confirmation and requires six prior completed bars. Known-level omissions remain flagged; Stage 11.2 uses the original V1 level universe, which does not introduce PDC.
- **Stage 11.1 limitation:** no saved calibration artifact with causal availability was found. Regime labels are UNAVAILABLE_CALIBRATION_PROVENANCE for all 733 observations. Its continuous Stage 10.9 inputs are included. Rebuilding full-period quartiles and calling them signal-time predictors would violate the requested leakage constraint.
- All feature values are computed before the EVENTUAL_STRONG / NEVER_STRONG label join. Outcome quality is evaluated in a separate layer. No labels, reclaim, strong candle, EOD values or threshold results enter a feature.

## Interpretation limits

All comparisons are descriptive in-sample associations. Whole-session bootstrap uses 10,000 shared cluster draws, seed 20260907, with event-weighted estimates. Intervals are pointwise, not adjusted confirmation across 70 correlated numeric fields. Missingness and group composition can confound results. Direction splits and monthly tables are diagnostics, not an unrestricted combination search. September is partial and small.

## Artifacts and verification

Full suite: **1,137 passed**, including **25 new focused tests**. Independent raw-minute audit and frozen-file integrity checks passed. [Verification and limitations](break_hold_first_hold_quality_verification.md).
[Complete tables](break_hold_first_hold_quality_tables.md) · [Machine-readable results](break_hold_first_hold_quality_analysis.json) · [Signal-time feature records](break_hold_first_hold_quality_features.csv) · [Executable pairs](break_hold_first_hold_quality_executable_pairs.csv) · [Frozen analysis plan](break_hold_first_hold_quality_plan.md)

Canonical SHA-256: `6aaf9980ecd7798420151a8b97436311eca6429e9f31fdb33be1ed86c8c47148`. V1 definition hash: `92b8c227e32c4fd43001da58fa0865fc61e868faa53c0bab2199c258e91f5f4d`. Original input-manifest hash: `2caffada233ed08d9cec0da158c46ae56b6874ab979cc2d9d54aec844bd8c8cd`.

