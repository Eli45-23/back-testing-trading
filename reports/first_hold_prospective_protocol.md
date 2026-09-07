# First Hold prospective exit validation — frozen protocol

Declared September 7, 2026, before any completed post–September 4 session outcomes were inspected. This is validation, not another search. Stage 14 remains unchanged; no PAPER/live execution or broker connections are authorized by this protocol.

## Fixed candidates and control

1. `USD030_TARGET_1.5R`
2. `ATR050_TARGET_1R`
3. `USD030_TARGET_2R_BE1R`

Control: `USD030_TARGET_2R`. The control is a comparison reference, not a fourth replacement candidate. Reuse these exact entries from the existing exit engine; do not evaluate the other development variants prospectively for selection.

No changes to First Hold, entry eligibility, stop sizes, target multiples, breakeven timing, direction membership, or entry filters. Entry remains the first eligible same-session minute open at/after signal-known-at, including that minute. The First Hold candle must be complete. Reuse the existing session-reset ATR14, signal pipeline, Decimal price arithmetic, opening-gap handling, same-minute ambiguity, and EOD fallback without reinterpretation. Breakeven starts next minute after +1R, never retroactively. No ATR fallback, inherited prior-session ATR or new warm-up eligibility filter.

The machine-readable [freeze manifest](first_hold_prospective_freeze.json) records the 174 pre-existing source/config/development artifacts and their SHA-256 values, candidate identities, sample gates, and complete session inventory. Changed baseline bytes fail closed; they are not silently reaccepted. No existing source file was modified to establish this protocol.

## Fixed primary endpoint and sufficiency

Use the **first 60 XNYS trading sessions strictly after September 4, 2026**, including every session regardless of signal count or performance. The locally installed exchange calendar specifies **September 8–December 1, 2026 inclusive**, ending after the December 1 regular close. September 7 is not a trading session. November 27's shortened session counts once, using its actual close. Weekends and holidays do not count. The frozen calendar inventory is authoritative for this plan; unexpected exchange closures require a documented calendar-only reconciliation, not a performance-driven date change.

No selection or ranking decisions before all 60 sessions have closed **and** all 60 have validated data. The 40th session is not an early stopping opportunity. Zero-signal sessions count toward the calendar endpoint and bootstrap sampling.

Each candidate and the control additionally require:

- At least **200 executable trade outcomes** (including explicitly ambiguous scenario records, excluding unavailable entries/ATR).
- At least **40 distinct sessions contributing executable trades**.

These are minimum descriptive sufficiency gates, not a statistical power guarantee. If a candidate fails at the fixed endpoint, label it `INSUFFICIENT_PROSPECTIVE_DATA`; do not invent a fallback, substitute another model, or extend until its results improve. Directional subgroups below 50 trades or 20 contributing sessions are flagged sparse, without changing entry membership. No direction-specific candidate may be selected in this study.

All completed sessions after the development cutoff remain outside discovery. The primary decision dataset stops at the fixed 60-session endpoint: later sessions may be stored separately but cannot be added to improve the primary result. A subsequent validation extension would require a separately reviewed protocol, not an automatic rolling endpoint.

## Data and interim handling

Before outcome computation, validate complete SIP/raw SPY RTH 1-minute coverage against each session's expected minutes, unique ordered timestamps, no conflicts, deterministic completed 5-minute aggregation, and compatible prior/premarket context and indicator initialization. Do not fill missing prices. Preserve unavailable context explicitly exactly as the frozen pipeline does. Missing required session data blocks the primary report; do not replace it with another day. Record each input partition hash and retrieval/validation timestamps; subsequent corrections must be logged, never silently overwrite the evidence.

Reconcile actual future data provenance before claiming it was unseen. If any post-cutoff outcomes were previously used for research, stop and disclose the contamination rather than relabeling them prospective.

Interim artifacts may contain session coverage, signal identity, entry reference, ATR availability, exact stop/target, breakeven update times, exit record, ambiguity and per-session audit details. Label any interim performance `INTERIM_NO_SELECTION`. No winner labels, retuning, candidate replacement, subgroup search, filters, performance-based stopping, or live actions. Unexpected defects are reported and evaluation paused; code fixes affecting semantics need review, not quiet reruns as though nothing changed.

As of protocol creation, there are **zero completed prospective sessions**; no prospective market data or outcomes were loaded. There is therefore no prospective trade count or performance estimate to report (unknown, not zero trades). This task sets the protocol and readiness guards; it does not install a recurring collector or background execution service.

## Endpoint report, fixed before outcomes

For each candidate and control, report membership, unavailable entry, unavailable ATR, executable trade count, contributing sessions, resolved/ambiguous counts, win rate, average winner/loser R and dollars, mean R, median R, profit factor, maximum event drawdown, longest losing streak, LONG/SHORT breakdown, monthly results, positive/negative months, worst month and leave-one-month-out minimum. Monthly breakdowns include partial September and December, labeled explicitly.

Provide gross metrics and the unchanged **$0.01 and $0.02 per-share round-trip cost sensitivities**. These are scenarios, not measured execution costs. R always uses original risk; a breakeven gross outcome can lose after costs. Do not count zero-R outcomes as wins.

Show resolved-only diagnostics and both stop-first/target-first sensitivity outcomes. Ambiguous exact R remains null; no favorable ordering inference. Drawdown/streak use the same deterministic signal/event-ID order and constant-initial-R convention as development. They include overlapping signals and are not account or mark-to-market drawdown. Also retain chronological session-sum drawdown.

For `ATR050_TARGET_1R`, report unavailable ATR on the full First Hold population, by session, direction and month. Compare all four models both on their natural available populations and the exact common ATR-available identities. Never imply that the 394-entry development subset is equivalent to the 727-entry full development population.

Compare against the frozen [2026 development results](break_hold_exit_study.json), not a rerun with new settings. Provide prospective minus development mean R and descriptive metric changes, with different sample lengths and month composition explicit. Also provide within-prospective paired candidate-minus-control mean R on identical available event IDs.

Use **10,000 whole-session bootstrap draws, seed 20260909**, shared across models and including all 60 sessions. Provide pointwise 95% intervals for mean R, win rate and paired candidate/control differences; keep ambiguity scenarios separate. To limit overstatement across the three paired candidate comparisons, also show conservative **98.3333% Bonferroni percentile intervals** (three prespecified comparisons; exploratory bootstrap approximation, not an exact test). Do not select a model merely because one pointwise interval is positive. Development comparisons are descriptive; all confirmatory claims concern the fixed prospective window.

At the endpoint, the report may discuss expectancy, drawdown, win rate, costs, month/direction consistency and uncertainty together. Sample eligibility is not automatic statistical success or deployment permission. No automatic selection score or live promotion is authorized. Until then, **no strategy-selection decisions**.

## Reproducible guard

`spy_research.break_hold.prospective_freeze.verify_freeze()` checks the frozen baseline; `readiness()` rejects invalid session inventories, prevents early endpoint reporting, blocks missing session coverage, and labels insufficient candidate counts without extending the window. Future outcome collection must supply independently validated records and counts; the readiness helper alone is not a data-quality validator or prospective backtest runner.
