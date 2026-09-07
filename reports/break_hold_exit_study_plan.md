# Frozen First Hold exit/risk study — predeclared protocol

Declared September 6, 2026 before new exit outcomes were computed. No entry filter, new sample, signal change, or numerical optimization.

## Population and reference

Use all 733 canonical First Holds from 170 SPY sessions, January 2–September 4, 2026 (requested January 1 is a holiday). Preserve 1,435 breaks, V1 definition/hash and every existing artifact. Read the accepted executable reference: first validated same-session SIP RTH minute open at/after signal-known time. Include that minute. Six session-close entries remain unavailable. No direction exclusions. Keep all overlapping events; this is an event-level exit comparison, not a capital-constrained portfolio simulation.

## Exactly 21 variants

1. Initial dollar risk $0.25 × targets 1R, 1.5R, 2R, 2.5R, 3R (five).
2. Initial dollar risk $0.30 × the same five targets (five).
3. Initial dollar risk 0.5 × exact confirmation ATR14 × the same five targets (five). Reuse session-reset ATR; unavailable warm-up stays unavailable, without substitution. Freeze initial R for the entire trade.
4. $0.30 hard stop; exit on completed OR-boundary reclaim, no target (one).
5. $0.30 hard stop; time exits after 15, 30, or 60 elapsed minutes from entry, no target (three).
6. $0.30 initial hard stop; confirmed-structure trail, no target (one): reuse Stage 11.3 strict 2-left/2-right five-minute pivots. Only pivots becoming known after entry can update the stop. LONG uses confirmed swing lows, SHORT swing highs. Updates can only tighten, never loosen, and first apply at the minute open at/after pivot known-at. No buffer or optimized lookback.
7. $0.30 hard stop, 2R target; after +1R is touched, move stop to the original entry price starting with the **next** minute (one). No same-minute retroactive breakeven activation.

The fixed $0.30 / 2R variant is the designated comparison anchor, not an assumed winner. Management variants share $0.30 so no full cross-product is searched. No model can be added/removed or changed after viewing outcomes.

## Order and fill semantics

- Stop-market proxy: opening gaps beyond the currently active stop fill at the minute open; otherwise stop touch fills at the stop. Stop gaps can lose more than 1R.
- Resting target-limit proxy: an opening gap through the target fills at the target, with no assumed improvement. Otherwise a touch fills at the target. Neither proxy guarantees a real fill.
- A known reclaim/time exit acts at the first minute open at/after its availability, never at a close learned afterward. LONG reclaim is a completed close <= ORH5; SHORT is >= ORL5, reusing canonical reclaim times. Protective opening-gap exits take precedence (same observed open); otherwise scheduled market exit precedes that minute's unknown high/low path.
- Trailing updates known at a minute open apply before testing that open. If the new stop is already crossed, use that open, not an unavailable historical price.
- If neither opening price resolves the exit and stop and target both touch inside the same minute, record AMBIGUOUS_STOP_TARGET with both possible prices/R values and no exact realized R. Do not guess ordering. Stop-first/target-first scenarios are sensitivity cases, not reconstructed facts. Breakeven next-minute activation avoids another within-minute assumption; an active stop hit before activation still exits the trade.
- EOD fallback is the final RTH minute close, explicitly an idealized scheduled-close fill. Reclaim/time signals at session close also use this fallback; never a next-session price.
- Exact Decimal prices/R, no broker tick rounding or new order submission. Primary outcomes gross of friction; fixed $0.01 and $0.02 per-share round-trip cost sensitivities are reported without selecting a cost assumption to favor a variant.

## Reporting and selection limits

Report membership, unavailable entry/ATR, resolved/ambiguous counts, win rate, average winner/loser (R and dollars), expectancy, median R, profit factor, drawdown, losing streak, exit reasons, LONG/SHORT and every month. Zero R is neither winner nor loser and resets a strict losing streak. Undefined profit factor (no losses) is explicit.

For unresolved ordering, keep exact realized R null; provide resolved-only diagnostics plus all-eligible stop-first and target-first scenarios. Main comparison uses clearly labeled stop-first-scenario metrics, with both scenario expectancies and ambiguity counts adjacent. Drawdown is the peak-to-trough sum of constant-initial-R event outcomes ordered by signal time/event ID; overlapping trades and variable dollar risk mean this is **not account drawdown**. Also show drawdown of chronological session sums. Neither is a mark-to-market equity curve. Losing streak uses the same deterministic event order.

ATR models are compared on their own available population and on the common available-ATR identities across all 21 models. Missing ATR must not masquerade as an exit advantage.

Use 10,000 whole-session bootstrap draws, seed 20260908, shared across variants. Report scenario mean-R and win-rate intervals, and paired mean-R differences versus the anchor on common identities. Intervals are pointwise exploratory, not multiplicity-adjusted validation. Monthly means, positive/negative months, worst month and leave-one-month-out minimum diagnose concentration; September is partial. No month is excluded.

Recommend at most three variants for independent testing, if any, weighing expectancy, drawdown, win rate, costs, monthly/directional consistency, ambiguity and common-sample comparisons—not simply maximizing gross return. It is permissible that none merits advancement. No automatic combined score or live change. All current results remain in-sample; any selected variant requires separately frozen unseen post–September 4 dates and a one-time OOS evaluation before live-process changes.

Run focused boundary/leakage tests, full suite, independent outcome/metric audit, hash preservation and whitespace checks. No PAPER connection, download, Stage 14 edit, commit or push.
