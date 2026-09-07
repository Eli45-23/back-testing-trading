# Stage 15.2 — BASE_SHORT Out-of-Sample Exclusion Validation Design

This design was frozen on August 31, 2026 before loading any 2024 or 2025
strategy outcomes.

## Frozen comparison universe

1. `BASE_SHORT_CONTROL`
2. `EXCLUDE_NEG_1`
3. `EXCLUDE_NEG_4`
4. `EXCLUDE_NEG_1_2`
5. `EXCLUDE_NEG_1_4`
6. `EXCLUDE_NEG_1_2_4`

No candidate may be added, removed, redefined, rebucketed, or optimized from
Stage 15.2 results.

## Frozen negative conditions

- NEG_1: `VWAP_ALIGNMENT=ALL_ALIGNED × ROOM_ATR=GT_3_0_ATR`
- NEG_2: `MARKET_STRUCTURE=BULLISH_STRUCTURE × ROOM_ATR=ATR_0_5_TO_1_0`
- NEG_3: `VWAP_ALIGNMENT=NONE_ALIGNED × ROOM_ATR=ATR_0_5_TO_1_0`
- NEG_4: `EMA_ALIGNMENT=EMA_ALIGNED × MARKET_STRUCTURE=BULLISH_STRUCTURE`

## Untouched periods

- Required: January 2–December 31, 2025
- Optional if identically complete: January 2–December 31, 2024

Neither period participated in Stage 12–15 discovery. Each year must be
reported separately; a combined validation may not conceal disagreement.

## Data-quality gate before outcomes

The comparison is prohibited unless the year has complete authoritative XNYS
sessions, every expected RTH minute, zero duplicate timestamps, deterministic
1m→5m reconciliation, compatible level construction, prior-session context,
and identical indicator/signal initialization. Missing data will not be filled.

## Frozen advancement gates

An `OOS_REPLICATED_RESEARCH_CANDIDATE` must improve mean R against its same-year
control, retain at least 70% of realized outcomes, represent at least 80
sessions, preserve month breadth, avoid one-month concentration or heavy month
removal, avoid PF and LOMO deterioration, shift the paired session bootstrap
favorably, agree directionally with Stage 15.1, and retain any claimed
entry-quality effect in fixed five-minute ATR-normalized MFE/MAE.

Other permitted classifications are `FAILED_TO_REPLICATE`,
`DESCRIPTIVELY_REPLICATED`, and `INSUFFICIENT_OOS_DATA`.

After the six candidates are evaluated, the analysis stops. No new exclusions,
thresholds, combinations, or buckets are authorized. Stage 14 remains paused;
this work does not connect to Alpaca PAPER or authorize a live candidate.
