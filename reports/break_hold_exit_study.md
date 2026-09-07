# Frozen First Hold exit/risk-management study

## Decision

**There is no established best exit yet.** The $0.30 stop / 1.5R target is the most balanced **full-population research reference** among the tested choices: a relatively higher win rate, modest gross expectancy, and less event-level drawdown than the $0.30 / 2R anchor. Its edge does not survive the predeclared $0.02 round-trip cost sensitivity, however.

The 0.5 ATR stop / 1R target has the most interesting win-rate/drawdown balance **on the ATR-available subset**. It is not a whole-population winner: warm-up leaves 333 otherwise executable signals without ATR, and its paired expectancy advantage over the anchor on identical entries is uncertain. The study does not introduce an ATR-availability entry filter or a fallback stop.

Do not change the live process. Retain at most three unchanged specifications for a separately frozen, genuinely unseen validation: **$0.30 / 1.5R; 0.5 ATR / 1R with missing availability explicit; $0.30 / 2R with next-minute breakeven after +1R.** These are exploratory comparisons, not validated trading recommendations. No numerical optimization or additional entry filter was performed.

## Scope and denominator

- Frozen V1 First Hold: 733 signals from 170 SPY sessions, January 2–September 4, 2026; January 1 was not a trading session.
- Exactly 21 predeclared variants. Entry is the saved first eligible minute **open at or after signal completion**, with that minute included.
- Fixed-stop models: 727 executable entries, 397 LONG / 330 SHORT, 170 contributing sessions. Six session-close signals have no executable same-session entry.
- ATR models: 394 executable entries, 212 LONG / 182 SHORT, 112 contributing sessions. The same six entry-unavailable records plus 333 ATR-unavailable records are retained explicitly per ATR variant.
- 15,393 signal/variant records: 13,602 available outcome scenarios and 1,791 explicit unavailable records. No unavailable record was silently dropped from membership.
- All events, including overlaps, remain. R uses each event's frozen initial risk. This is not a position-sizing or portfolio study.

The complete protocol was declared before outcomes in [the frozen plan](break_hold_exit_study_plan.md). All 21 results, monthly and directional tables, scenario and cost sensitivities, and matched-population comparisons are in [the complete tables](break_hold_exit_study_tables.md). [JSON](break_hold_exit_study.json) and [trade-level CSV](break_hold_exit_study_trades.csv) retain the underlying records.

## Main comparison

Numbers below use the **stop-first sensitivity scenario** for unresolved same-minute ordering. They are not an assertion that the stop actually happened first. All outcomes are modeled, gross of execution friction unless noted.

| Exit | Available n | Win rate | Mean R | Median R | PF | Event DD R | Longest losing streak | Mean R after $0.02 RT |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| $0.30 / 1.5R | 727 | 42.09% | 0.0523 | -1.0000 | 1.0903 | 37.50 | 10 | -0.0144 |
| 0.5 ATR / 1R | 394 | 55.08% | 0.1028 | 1.0000 | 1.2294 | 13.00 | 6 | 0.0473 |
| $0.30 / 2R + BE after 1R | 727 | 27.51% | 0.0404 | -1.0000 | 1.0796 | 33.28 | 10 | -0.0263 |
| $0.30 / 2R anchor | 727 | 33.98% | 0.0171 | -1.0000 | 1.0259 | 49.00 | 13 | -0.0495 |
| $0.30 / 3R | 727 | 26.41% | 0.0529 | -1.0000 | 1.0719 | 35.00 | 13 | -0.0138 |
| $0.30 structure trail | 727 | 15.96% | 0.1189 | -1.0000 | 1.1431 | 76.19 | 33 | 0.0522 |

**DD is not account drawdown.** It is peak-to-trough cumulative constant-initial-R outcomes in signal/event-ID order. It includes overlapping trades and does not mark open positions to market. Session-sum drawdowns are also supplied. Do not convert these directly into required account capital. Losing streaks use the same deterministic event order; zero-R trades reset a strict losing streak.

### Why the shortlist is small

**$0.30 / 1.5R:** average winner +1.5R ($0.45), average loser -1R (-$0.30); gross mean-R session-bootstrap 95% interval [-0.0401, 0.1470]. Six positive and three negative months; LOMO minimum +0.0175R. LONG +0.0264R versus SHORT +0.0833R. Compared with 3R, it gives up a little drawdown performance and almost no gross expectancy for a substantially higher win rate. This is a judgment about balance, not a fitted score or statistically proven ranking.

**0.5 ATR / 1R:** average winner +1R (about $0.4418), average loser -0.9972R (about -$0.4196); mean-R 95% interval [0.0049, 0.2088]. Six positive and three negative months; LOMO minimum +0.0585R. LONG expectancy is only +0.0189R versus SHORT +0.2005R: directional robustness is not established. The pointwise positive interval does **not** establish an edge after examining 21 models.

**Breakeven variant:** mean-R 95% interval [-0.0434, 0.1290]; five positive/four negative months, LOMO +0.0125R. Average winner +1.9922R, average loser -0.9764R; 149 zero-R outcomes are not wins. It reduces event DD relative to the anchor but has lower win rate and negative cost-sensitive expectancy. Its value is a distinct risk-management hypothesis, not stronger evidence of profit.

### The matched-entry check matters

On the exact same 394 available-ATR entries:

| Exit | Mean R | Win rate | Event DD R |
|---|---:|---:|---:|
| 0.5 ATR / 1R | 0.1028 | 55.08% | 13.0 |
| $0.30 / 1.5R | 0.1231 | 44.92% | 14.0 |
| $0.30 / 1R | 0.0558 | 52.79% | 11.0 |
| $0.30 / 2R anchor | 0.0925 | 36.55% | 28.0 |

ATR / 1R's paired mean-R improvement over the anchor is only +0.0103R, 95% CI [-0.1071, 0.1238]. It does not dominate the fixed models: $0.30 / 1.5R has higher matched expectancy, and $0.30 / 1R has lower event drawdown. Comparing ATR's 394 entries directly with another model's 727 would confound exit behavior with the different available population.

## Models not advanced in this shortlist

- Structure trailing has the highest full-population gross mean (+0.1189R), but its 15.96% win rate, 33-loss streak, 76.19R event DD, and wide [-0.1318, 0.4092] interval make it an unattractive balance. Its matched-sample LOMO minimum is negative (-0.0424R). Higher gross return alone is insufficient.
- Reclaim-only produces a 10.18% win rate and a 51-loss streak. The few large winners do not establish a stable management advantage.
- Time exits give no clear balance improvement: 30-minute event DD is 91.61R; 60-minute is 78.82R. Their mean-R intervals cross zero.
- The $0.25 / 1R result is particularly ordering-sensitive: -0.0591R stop-first versus +0.0646R target-first, with 45 ambiguous trades. A favorable ordering assumption would reverse its apparent sign.
- Larger fixed targets mostly exchange win rate for larger winners without demonstrating reliable expectancy improvement. No targets or stops were retuned after these results.

## Ambiguity, realism, and uncertainty

Ambiguous same-minute stop/target records have **null exact realized R and price**. The known stop and target prices and both R scenarios remain in exports. For the three shortlisted variants, ambiguity counts are respectively 13, 1, and 10; mean-R stop-first/target-first ranges are 0.0523–0.0970, 0.1028–0.1079, and 0.0404–0.0748. Resolved-only summaries are a selection diagnostic, not a preferred estimator.

Stops fill at the minute open if gapped through, otherwise at stop touch. Targets fill at the target without gap improvement. Time/reclaim exits use the next eligible open after their known time. Breakeven begins next minute, never retroactively inside the trigger minute. Structure updates use only completed, confirmed 2-left/2-right five-minute pivots, tighten only, and first apply when known. EOD uses an idealized last-RTH-minute close. Touch fills, no queue model, fixed friction sensitivities, and no intraminute path data all limit realism. Prices use Decimal with sufficient precision to preserve the source ATR; bootstrap summaries use numerical arrays.

Session clustering is respected by 10,000 whole-session bootstrap draws, seed 20260908. Intervals are exploratory and pointwise, not multiplicity-adjusted. January–September is development evidence, not independent validation; September has only four trading sessions. Months and directions were not used to add filters. Portfolio constraints, financing, and actual execution costs are not modeled.

## Next step — stop here pending review

Freeze any accepted shortlist and its missing-data policy before observing the new sample. Select truly unseen post–September 4 dates, verify coverage and identical initialization, and run one OOS evaluation without changing exits or entries. The ATR model must retain unavailable observations and use matched comparisons; it is not yet a complete exit policy for early signals. Do not change Stage 14 or begin live execution on this evidence.

No new sample was loaded, no orders submitted, and no source committed or pushed. See [verification](break_hold_exit_study_verification.md).
