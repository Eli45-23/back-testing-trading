# SPY break-and-hold V1: findings and verification

The baseline is complete for January 1–September 4, 2026: 170 expected and
analyzed XNYS sessions, zero missing or invalid sessions. The evidence is mixed;
this study does not establish a tradeable edge or options profitability.

The complete tables are in [the research report](break_hold_2026_v1.md).
Canonical event/measurement records are in [JSON](break_hold_2026_v1.json), with
[CSV](break_hold_2026_v1.csv) and [coverage inventory](break_hold_2026_coverage.json).

## Population and principal comparison

| Measure | First hold | Strong hold |
|---|---:|---:|
| Signals | 733 | 524 |
| Long / short | 400 / 333 | 283 / 241 |
| Measurable EOD outcomes | 727 | 522 |
| Median EOD MFE | $1.9900 | $1.8737 |
| Mean EOD MFE | $2.6403 | $2.5289 |
| Median EOD MAE | $1.7701 | $1.7075 |
| Mean EOD MAE | $2.5310 | $2.5044 |
| Ratio of mean MFE to mean MAE | 1.0432 | 1.0098 |
| Median directional EOD return | −$0.0300 | +$0.0350 |
| +$0.50 before −$0.25, clean | 37.38% | 38.36% |
| Same-minute ambiguity for that pair | 1.09% | 0.57% |

There were 745 upside and 690 downside break sequences. Of the 1,435 total
sequences, 702 failed immediately (48.92%); 733 reached first hold (51.08%).
524/733 first holds reached strong confirmation (71.49%). There were 585
post-hold reclaims. 154 sessions broke the upper boundary, 144 broke the lower,
and 128 broke both. Signals without future minutes remain counted.

The full report includes every predeclared threshold pair, with clean favorable,
adverse, same-minute ambiguous, neither, and no-future outcomes. Percentages use
all signals in the respective entry-style population. Ambiguity is never
converted to a win. For the symmetric $0.25/$0.25 pair, ambiguity is higher:
5.18% first-hold and 4.77% strong-hold.

## Does stronger confirmation help?

The evidence does not support a general claim that waiting improves expectancy.
No realized exit strategy or transaction-cost model was specified. Small
improvements in some clean threshold rates do not translate to uniform
improvement: +$1.00/−$0.30 falls from 27.01% to 25.38%, for example.

Within the 524 events that eventually achieved strong hold, the first-entry
reference has mean EOD MFE $2.8068 and MAE $2.3060. Entering at the later strong
reference has MFE $2.5289 and MAE $2.5044. Waiting incurs an average $0.2554
directional entry-price deterioration. The +$0.50/−$0.25 clean rate on these
matched events falls from 50.19% at first hold to 38.36% at strong hold.

That matched subset uses future survival to select events. It is useful for
describing the cost of waiting, but cannot be an executable first-entry filter
or evidence that the earlier entry could identify those survivors in advance.

## Stronger and weaker descriptive groups

The following use the same illustrative +$0.50/−$0.25 pair shown in the fixed
subgroup report. They do not select or optimize a new threshold or trading rule.

- First-hold shorts: 41.14% clean, n=333, versus longs 34.25%, n=400. Shorts also
  have higher median EOD MFE ($2.1589 versus $1.8900) and lower median MAE
  ($1.5300 versus $2.0500). This is descriptive directional evidence only.
- First holds at 11:00–12:00: 41.90%, n=105, compared with 34.33%, n=67, in
  15:00–close. EOD opportunity time differs, so excursion sizes are not directly
  comparable without accounting for horizon. The fixed-horizon tables help
  separate this from simply having more time to move.
- Strong holds at 10:30–11:00: 43.64%, n=55, versus 26.67%, n=60, at
  13:30–15:00. These modest subgroups require independent confirmation.
- Tuesday is stronger than Thursday on this pair for both entry styles:
  first hold 41.18% (n=136) versus 33.91% (n=174); strong hold 47.37% (n=95)
  versus 31.54% (n=130). Weekday associations have not been adjusted for other
  context or multiple comparisons.

## Is room to the next level meaningful?

There is no monotonic larger-room improvement in clean threshold success.
First holds with >$2 room have 38.69% clean (n=199), compared with 40.66%
(n=91) at ≤$0.25. Strong holds with >$2 have 32.61% (n=138), versus 45.65%
(n=46) in the ($0.25,$0.50] bucket. Other buckets vary rather than following a
consistent increasing pattern. The full table labels each disjoint bucket by
its inclusive upper bound.

No known directional level is represented as unavailable, not infinite room.
Incomplete prior-day context on January 2 affects four entry-style records;
those records remain in the sample and explicitly lack PDH/PDL. This run does
not support turning room into a V1 filter.

## Exact timestamp semantics and regression proof

`FiveMinuteBar.timestamp` is the inclusive **start** of the candle. The existing
aggregator assigns `timestamp=bucket_start`. Completion and signal availability
are `timestamp + timedelta(minutes=5)`.

| Candle interval, New York time | Stored timestamp | Constituent minute starts | Available at |
|---|---|---|---|
| Opening 09:30–09:35 | 09:30 | 09:30–09:34 | 09:35; levels only, no hold signal |
| Later 09:35–09:40 | 09:35 | 09:35–09:39 | 09:40 |
| Later 09:40–09:45 | 09:40 | 09:40–09:44 | 09:45 |

The model docstring and README now state this explicitly. Existing
`calculate_opening_five_minute_levels` already sets its availability to 09:35.
The break/hold detector sets every first/strong confirmation, failure, and
reclaim to the completed candle's close time.

`test_opening_timestamp_is_start_levels_available_only_at_completion` verifies
opening-bar start stamps, all five constituent starts, unavailability at
09:34:59, availability at 09:35, and absence of a signal from the opening candle.
`test_completion_not_stored_start_gates_every_outcome_minute` runs four cases:
first and strong confirmations in two later locations. It injects extreme
highs/lows into every minute at or before the signal timestamp and proves every
outcome is unchanged. A confirming-candle-only input produces zero observed
future minutes, and every reported hit/extreme time must follow completion.

This V1 intentionally uses the user's strict minute-start `>` rule, excluding
even the minute starting exactly at confirmation. This is stricter than merely
excluding constituent minutes and creates a documented one-minute gap. No
result should be described as an immediate executable close-entry simulation.

## Verification

- New break/hold, coverage, and integration tests: 34 passing.
- Targeted run including existing opening-range tests: 52 passing.
- Full project suite: 1,094 passing, zero failures.
- Independent saved-report audit: all 1,257 signals, 7,542 windows, and 11,313
  threshold results reconciled directly against raw prices, without calling the
  production outcome calculators. Run `python scripts/verify_break_hold_run.py
  reports/break_hold_2026_v1.json` from the configured project environment.
- Small-period CLI smoke run: August 17–19, successful JSON export.
- All 12 originally missing sessions were downloaded separately using the
  existing historical SIP client; no conflicts. Existing valid partitions were
  skipped. Final raw coverage is 170/170, or 66,300/66,300 RTH minutes.
- Existing processed files cover the earlier 158 sessions. The research builds
  all required 5-minute candles directly from validated raw minutes using the
  existing aggregator; it does not depend on missing processed partitions.
- Dependency check and compilation/import pass. The local macOS environment
  can mark editable-install `.pth` files hidden; the documented `PYTHONPATH`
  setup provides a reproducible working invocation.
- Credential scan across all 38 changed/untracked text artifacts passed with
  zero matches to configured secrets. Market-data partitions are ignored by
  Git. `git diff --check` passed. Stage 14 paper/live/shadow/replay source has
  no changes relative to the current commit.
- No PAPER connection, live service, order, strategy optimization, commit, or
  push was performed for this research. Outstanding Stage 15.2 edits remain
  separate and uncommitted.

## Research limitations

The first/strong cohorts differ, repeated events overlap within sessions, and
the sample is one partial calendar year. No costs, execution fills, sizing,
options pricing, or realized exit policy are included. EOD MFE and MAE do not
establish which excursion happened first; the threshold results address that
separately at one-minute resolution. Same-minute ordering remains unknowable.
Results are suitable as a documented descriptive baseline with these caveats,
not a demonstrated edge or a guarantee of future profitability.
