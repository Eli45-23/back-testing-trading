# Frozen execution and accounting

One open SPY position per strategy; LONG or SHORT, no pyramiding or overnight holdings. Signals become usable only after all input bars complete. Enter at the first same-session one-minute OPEN at or after availability, including that minute in the path. Confirming-bar constituents cannot fill an entry.

While a position is open, ignore and record signals without queuing. Opposing simultaneous signals produce NO_ENTRY_CONFLICT. Equivalent same-direction simultaneous signals use stable ID order for one entry and record the others separately. No reentry in the minute of an exit.

Stops: USD030 ($0.30), USD050 ($0.50), ATR050 (0.5 ATR) and ATR100 (1 ATR). ATR uses the existing same-session completed-five-minute Wilder14 calculation, with no prior-session inheritance or fallback. Unavailable ATR is explicit. Each complete signal/stop/exit configuration consumes one of the 60 slots.

Exits: TARGET_1R, TARGET_1.5R, TARGET_2R, TIME_15, TIME_30 or TIME_60. Every variant has its initial protective stop. No trails, breakeven changes, partials or next-level targets. Time exits occur at the first open at the elapsed deadline; any remaining position exits at the last RTH minute CLOSE, including early closes.

Evaluate observed open first: adverse stop gaps fill at the open; favorable target gaps fill at the target. Then apply scheduled time exits and minute extrema. If both stop and target are touched with unknown ordering, preserve ambiguity: stop-first is primary and target-first is sensitivity. Never claim that either sensitivity is observed ordering.

Initial risk remains the R denominator. Prices, ATR and execution accounting use Decimal; repeating divisions use 80-digit local precision. Zero-R outcomes are not wins. Gross, $0.01 and $0.02 per-share roundtrip scenarios deduct cost / initial risk once per trade; net-zero trades count separately. Costs represent SPY-equivalent underlying movement, not 0DTE option execution costs. Drawdown/streak follow chronological closed trades for the one-position strategy; no mark-to-market/account-return claim is made.
