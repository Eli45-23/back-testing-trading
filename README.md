# SPY Strategy Research

This project is a research system for objectively testing a discretionary SPY
strategy. It establishes the structure and configuration needed for repeatable
market-data research without implementing trading behavior.

## Current development stage

The project is in **Phase 1: foundation**. The current code provides a modern
Python package, validated research configuration, safe environment-based secret
handling, reusable console logging, and a basic test suite.

The Phase 1 research will eventually answer:

> For every SPY 5-minute EMA9/EMA20 cross, what happens afterward?

## Current scope

This repository currently contains foundation code only. Its layout is ready to
later support the frozen Phase 1 research design. None of the data collection,
indicator, outcome, or storage behavior described below is implemented yet.

## Frozen Phase 1 research rules

- Research SPY only.
- Use Alpaca historical one-minute bars from the SIP feed.
- Construct five-minute candles locally from those one-minute bars.
- Calculate indicators using regular trading hours (RTH) only.
- Calculate EMA9 and EMA20 from completed five-minute candle closes.
- Recognize a cross only after its five-minute candle is complete.
- Reset RTH VWAP daily at 09:30 in `America/New_York`.
- Calculate ATR14 with Wilder smoothing.
- Calculate MFE and MAE using future one-minute highs and lows.
- Store research results in SQLite.
- Submit no orders and perform no paper or live trading.
- Use no look-ahead or future information when calculating features or signals.

The configured 5, 15, 30, and 60-minute outcome horizons and end-of-day outcome
are **unresolved Phase 1 assumptions**, not confirmed research rules. They remain
visible in `config/research.yaml` for later review and must not be treated as
final without explicit confirmation.

The following are explicitly out of scope right now:

- Live trading
- Paper orders
- Options trading
- Machine learning
- AI market prediction
- A dashboard
- Discretionary strategy automation

## Reproducible research runs

A research run is an immutable manifest identifying a future research or
backtest execution. It records the requested date range, lifecycle status,
application and Git versions when available, and a complete snapshot of the
validated non-secret research configuration.

The configuration hash is a SHA-256 digest of deterministic JSON. Identical
effective configuration produces the same hash regardless of dictionary order;
changing a result-affecting setting changes the hash. Credentials come from a
separate settings model and are never included in the snapshot or hash.

Create a local JSON manifest with:

```bash
spy-research run-manifest --start 2026-08-03 --end 2026-08-19
```

This command only reads local configuration and optional local Git metadata. It
does not persist a manifest, load credentials, request market data, contact
Alpaca, or make any network request.

## Stage 1.1 historical data client

The historical client retrieves raw SPY one-minute stock bars from Alpaca's SIP
feed with raw price adjustment. These Phase 1 values come from the validated
research configuration and cannot be overridden by the downloader. Responses
are fully paginated, parsed into timezone-aware typed bars, checked for duplicate
timestamps, and returned in chronological order.

Prices and VWAP are represented with Python `Decimal` values to preserve the
decimal representation supplied by Alpaca. Volume and trade count are integers.
No RTH filtering, candle aggregation, indicators, or derived values are applied.

Configure credentials in the ignored local `.env` file:

```text
ALPACA_API_KEY=your-key-id
ALPACA_SECRET_KEY=your-secret-key
```

Then request an inclusive calendar-date range with:

```bash
spy-research fetch-bars --start 2026-08-03 --end 2026-08-04
```

Date boundaries are interpreted in `America/New_York` and sent to Alpaca as
explicit UTC timestamps. The command prints only a concise count/timestamp/page
summary. Bars are held in memory and are not currently written to files or
SQLite. The command contacts Alpaca; the test suite uses mocked HTTP transports
and requires neither credentials nor network access.

## Stage 1.2 raw Parquet storage

Raw downloaded bars are stored separately from future processed/derived data at:

```text
data/raw/alpaca/spy/1min/YYYY/MM/YYYY-MM-DD.parquet
```

Partitions use the bar's `America/New_York` calendar date, while timestamps are
stored as timezone-aware UTC microseconds. OHLC and VWAP use exact Arrow
`decimal128(28,12)` fixed-point columns. Source, symbol, feed, timeframe, and
adjustment are explicit columns as well as non-secret schema metadata.

Use `fetch-bars` for an in-memory, non-persistent check. Use `download-bars` only
when raw Parquet persistence is intended:

```bash
spy-research download-bars --start 2026-08-19 --end 2026-08-19
```

Persistence is idempotent by symbol, timestamp, feed, and timeframe. Identical
bars are not duplicated; differing content under the same key is reported as a
conflict and never silently overwritten. Changed partitions use temporary files
and atomic replacement. Raw market-data files are ignored by Git.

## Stage 1.3 exchange sessions

Raw bars are classified with the authoritative `exchange_calendars` XNYS
calendar. The calendar supplies each trading date's actual market open and
close, including holidays and early closes, while `America/New_York` conversion
handles daylight-saving changes. A bar is classified by its interval-start
timestamp using these half-open boundaries:

- `PREMARKET`: 04:00 New York time through, but not including, the actual open.
- `RTH`: actual exchange open through, but not including, the actual close.
- `AFTER_HOURS`: actual close through, but not including, 20:00 New York time.
- `OUTSIDE_SESSION`: a trading-day bar before 04:00 or at/after 20:00.
- `NON_SESSION`: any bar whose New York calendar date is not an XNYS session.

Classification creates a typed wrapper around each immutable raw record. It
does not rewrite, filter, or add columns to the raw Parquet partitions. In
particular, an early-close day begins after-hours classification at its actual
close rather than at the usual 16:00 close.

Summarize already-stored local partitions with:

```bash
spy-research session-summary --start 2026-08-19 --end 2026-08-19
```

The command reports the calendar boundaries, early-close status, classification
counts, and key RTH/after-hours timestamps for every requested date. It reads
only local configuration and Parquet files; it does not load Alpaca credentials
or make a network request.

## Stage 1.4 raw-data validation

The read-only validation layer checks persisted raw bars before any future
aggregation. It verifies strict input ordering and unique keys, finite and
internally consistent OHLC/VWAP values, non-negative volume and trade count,
one-minute timestamp alignment, frozen Phase 1 provenance, partition dates,
session classification, expected session coverage, and exact RTH minute starts
from the XNYS schedule. Zero volume and zero trade count remain valid because no
unsupported assumption is made that every supplied bar must have positive
values.

Findings have three severities:

- `ERROR` makes the report fail, including missing RTH minutes, missing trading
  days, malformed values, duplicate keys, non-session bars, or corrupt data.
- `WARNING` preserves visibility without failing validation. A trading-day bar
  before 04:00 or at/after 20:00 is currently handled this way.
- `INFO` records expected calendar characteristics such as an early close.

Sparse premarket or after-hours data is not itself an error or warning because
Alpaca need not produce bars for minutes without trades. RTH coverage is strict:
every minute start from the actual exchange open through the minute before the
actual close must exist.

Run the human-readable or JSON validation report with:

```bash
spy-research validate-data --start 2026-08-19 --end 2026-08-19
spy-research validate-data --start 2026-08-19 --end 2026-08-19 --json
```

Both forms read local Parquet only and never repair or rewrite it. Exit code `0`
means validation passed, `1` means the data failed validation, and `2` means the
command could not run. A later research pipeline can use the typed `passed`
field as a gate, but no downstream aggregation or backtesting is implemented.

## Stage 2.1 deterministic five-minute candles

Validated RTH one-minute bars can be transformed in memory into exact
five-minute buckets aligned to the actual XNYS open. Every candle requires the
five consecutive minute starts in its bucket: open comes from the first source
bar, high and low are the extrema, close comes from the fifth bar, and volume
and trade count are summed. Premarket, after-hours, outside-session, and
non-session bars are excluded. Actual exchange closes govern the final bucket,
so a normal session produces 78 candles and a 13:00 early close produces 42.

Aggregation is blocked unless the existing raw-data validator passes. Partial,
duplicate, misaligned, or otherwise incorrect buckets fail explicitly. The
immutable derived model preserves decimal OHLC values and provenance but omits
a five-minute VWAP field: Alpaca's minute-bar VWAP is not the future Phase 1
daily-reset research VWAP indicator, and omitting it prevents semantic overlap.

Run the local, read-only transformation with:

```bash
spy-research aggregate-bars --start 2026-08-19 --end 2026-08-19
```

The command makes no network request and does not persist processed data.

## Stage 2.2 processed five-minute storage

Verified five-minute RTH candles are stored separately from raw source data:

```text
data/processed/spy/5min/rth/YYYY/MM/YYYY-MM-DD.parquet
```

The fixed-point schema preserves OHLC, volume, trade count, UTC bucket start,
New York session date, and the full non-secret lineage: Alpaca SIP raw `1Min`
source bars, processed `5Min` timeframe, `RTH_ONLY` session mode, five source
bars per candle, and aggregation method `rth_1m_to_5m_v1`. No indicator columns
or credentials are stored.

Processed persistence is atomic and idempotent. Identical candles are not
rewritten; differing content under the same symbol/timestamp/timeframe/session
identity is a conflict and is never silently overwritten. Dedicated validation
checks ordering, identity, schema, prices, provenance, XNYS-aligned timestamps,
session completeness, and partition dates. Reconciliation reruns the Stage 2.1
aggregation from local validated raw bars and requires exact candle equality.

Build or read-only validate the processed range with:

```bash
spy-research build-5m --start 2026-08-03 --end 2026-08-19
spy-research validate-5m --start 2026-08-03 --end 2026-08-19
spy-research validate-5m --start 2026-08-03 --end 2026-08-19 --json
```

These commands are offline. Processed Parquet files remain ignored by Git, and
the validation report provides a `passed` gate for future indicator stages.

## Stage 3.1 EMA9 and EMA20

EMA9 and EMA20 are calculated in memory from completed RTH-only five-minute
closes after processed validation and raw reconciliation pass. Each trading
session resets independently; no EMA state carries overnight. Before the ninth
or twentieth bar, respectively, the value is explicitly unavailable.

For period `N`, the first value is the exact SMA of the first `N` closes. Later
values use `alpha = Decimal(2) / Decimal(N + 1)` and
`EMA = alpha × close + (1 - alpha) × previous EMA` under a deterministic
50-digit Decimal context. Values are not rounded during calculation.

```bash
spy-research calculate-ema --start 2026-08-19 --end 2026-08-19
```

The command is offline and read-only. Indicator rows are not persisted, and no
cross, separation, ATR, signal, or strategy calculations are performed.

## Stage 3.2 daily RTH VWAP

The Phase 1 research VWAP is calculated in memory from each processed
five-minute candle's `HLC3 = (high + low + close) / 3`, weighted by that
candle's volume. Price-volume and volume accumulate only within the current RTH
session and reset at the next exchange open. Premarket, after-hours, prior-day,
and Alpaca vendor VWAP values never participate.

If cumulative volume is zero, VWAP is unavailable. Once positive volume exists,
later zero-volume candles retain the cumulative value. Computation uses a local
50-digit Decimal context without calculation-time rounding.

```bash
spy-research calculate-vwap --start 2026-08-19 --end 2026-08-19
```

The command validates and reconciles local processed bars, makes no network
request, writes no indicator data, and performs no cross/event calculations.

## Stage 3.3 ATR14 with Wilder smoothing

ATR14 is calculated in memory from validated RTH-only five-minute candles and
resets independently at the start of every session. True range is
`max(high - low, abs(high - previous_close), abs(low - previous_close))`. The
first bar deliberately has no overnight previous close, so its true range is
only `high - low`.

ATR14 is unavailable for the first 13 bars. Bar 14 is seeded with the exact
arithmetic mean of the first 14 true ranges. Every later value uses Wilder's
recurrence: `ATR = ((previous ATR × 13) + current TR) / 14`. Calculation uses a
local 50-digit Decimal context with no calculation-time rounding.

```bash
spy-research calculate-atr --start 2026-08-19 --end 2026-08-19
```

The command is offline and read-only. ATR rows are not persisted, prior-day
close and ATR state are not carried forward, and no cross, signal, or strategy
logic is performed.

## Stage 3.4 EMA separation metrics

Raw EMA distance metrics are derived directly from the verified EMA9 and EMA20
rows. When both values exist, `signed separation = EMA9 - EMA20` and absolute
separation is its non-negative magnitude. The signed value is positive when
EMA9 is above EMA20, negative when it is below, and zero when they are equal.

One-, two-, and three-bar deltas are `signed separation[t]` minus the signed
separation one, two, or three completed candles earlier. Separation begins with
EMA20 at 11:05 ET; the respective deltas begin at 11:10, 11:15, and 11:20 ET.
All history resets each RTH session and uses the EMA engine's 50-digit Decimal
precision without calculation-time rounding.

```bash
spy-research calculate-ema-separation --start 2026-08-19 --end 2026-08-19
```

The command is offline and read-only. Separation rows are not persisted, and
the raw metrics do not detect or interpret crosses, classify trends, or produce
signals.

## Stage 4.1 completed-candle EMA cross events

EMA9/EMA20 crosses are detected only from adjacent completed five-minute EMA
rows within the same RTH session. A bullish event requires
`EMA9[t] > EMA20[t]` and `EMA9[t-1] <= EMA20[t-1]`; a bearish event requires
`EMA9[t] < EMA20[t]` and `EMA9[t-1] >= EMA20[t-1]`. Equality followed by strict
separation therefore counts, while equality alone and persistent ordering do
not create events.

The event retains the timestamp of the candle whose completed close produced
the cross; it is not shifted to the next candle. Sessions reset independently,
so no overnight comparison is allowed. Each immutable event includes current
and previous EMA values, raw separation metrics, same-timestamp RTH VWAP and
ATR14, exact price/VWAP differences, and the cross-bar close as its reference
price.

```bash
spy-research detect-ema-crosses --start 2026-08-03 --end 2026-08-19
```

The command is offline and read-only. Events are not persisted or filtered, and
no outcomes, scoring, returns, MFE/MAE, or backtesting are calculated.

## Stage 5.1 post-cross MFE/MAE outcomes

Each Stage 4 event keeps the cross-bar close as its reference price. Because a
five-minute event timestamp is the candle start, outcome measurement begins
exactly five minutes later at the first eligible one-minute bar. No high or low
from the cross candle itself participates.

Outcomes use future raw RTH one-minute highs and lows from the event's own XNYS
session. Bullish MFE/MAE are `max(high) - reference` and
`reference - min(low)`; bearish MFE/MAE reverse those directions. Magnitudes
are floored at zero, and tied extremes use the earliest minute timestamp.

The fixed 5-, 15-, 30-, and 60-minute windows use exact elapsed minute starts.
EOD runs through the final RTH minute, including authoritative early closes.
Truncated horizons retain their available excursion but are explicitly marked
incomplete; a window with no future bars has unavailable excursion values.

```bash
spy-research calculate-cross-outcomes --start 2026-08-03 --end 2026-08-19
```

The command is offline and read-only. Outcomes are not persisted, and no
stops, targets, opposite-cross termination, scoring, statistics, or strategy
assumptions are applied.

Stage 5.2 additionally records the first later opposite-direction Stage 4
event from the same RTH session, its direction, and elapsed clock minutes and
five-minute bars between candle-start timestamps. This metadata is descriptive
only: every fixed Stage 5.1 horizon, extreme, completeness flag, reference
price, and outcome start remains unchanged. If no reversal occurs before the
session ends, opposite-cross context is unavailable; lookup never continues
overnight.

## Stage 6.1 descriptive cross-theory statistics

Phase 1 statistics describe the frozen cross outcomes without optimizing or
selecting rules. Fixed 5-, 15-, 30-, and 60-minute summaries include only
complete horizons; EOD includes every available outcome. Reports always expose
eligible and excluded counts. Percentiles use exact Decimal linear
interpolation at rank `(n - 1) × q`.

Factual MFE hit rates use the predeclared dollar thresholds `$0.25`, `$0.50`,
`$0.75`, `$1.00`, `$1.50`, `$2.00`, and `$3.00`, plus normalized thresholds
`0.5`, `1.0`, `1.5`, and `2.0` times event-time ATR14. Percentages retain their
numerator and eligible denominator.

Directional VWAP alignment means bullish reference price above event-time VWAP
or bearish reference price below it; equality and unavailable VWAP are not
aligned. Directional expansion means positive separation delta-1 for bullish
events or negative delta-1 for bearish events; equality and unavailable delta
are not expanding. These groups and their combination are descriptive only.

```bash
spy-research cross-stats --start 2026-08-03 --end 2026-08-19
```

The command is offline, read-only, and non-persistent. This 29-event development
sample is too small to establish a robust edge. No optimization, scoring,
inference, strategy selection, or trading simulation is performed.

## Stage 7.1 previous-day key levels

For each requested XNYS trading session, the previous-day level engine uses the
immediately preceding XNYS session—not the previous calendar date. From that
validated raw one-minute RTH session it calculates:

- PDH: maximum RTH one-minute high.
- PDL: minimum RTH one-minute low.
- PDC: close of the final chronological completed RTH one-minute bar.

Equal highs or lows retain the earliest source timestamp. Exchange-calendar
boundaries determine the final minute, so early closes are handled without a
hard-coded 16:00 close. Weekends and holidays are skipped automatically.

The source session is loaded automatically even when it falls before the
requested start date. Each value is therefore fixed before the target session
opens; premarket, after-hours, target-session bars, and vendor daily bars cannot
influence it. Missing source sessions are reported and present-but-invalid raw
sessions fail the validation gate rather than producing fabricated levels.

```bash
spy-research previous-day-levels --start 2026-08-03 --end 2026-08-19
```

The command is offline, read-only, and non-persistent. Stage 7.1 constructs
levels only: it does not implement touches, breaks, holds, sweeps, rejection,
premarket levels, opening-range levels, zones, signals, or trading logic.

## Stage 7.2 premarket key levels

For each XNYS trading session, the premarket engine uses same-day raw one-minute
bars classified as `PREMARKET` by the existing exchange-calendar session layer:

- PMH: maximum high from `04:00:00 America/New_York <= timestamp < RTH open`.
- PML: minimum low from the same interval.

The exchange calendar supplies the RTH open boundary. The 09:30 minute-start bar
on a normal session is therefore excluded, as are prints before 04:00, RTH bars,
after-hours bars, and prior-day data. Equal highs or lows retain the earliest
source timestamp. Final PMH/PML values are fully knowable at the RTH open.

```bash
spy-research premarket-levels --start 2026-08-03 --end 2026-08-19
```

The command is offline, read-only, and non-persistent. Sessions without local
premarket bars or without a local raw partition receive an explicit unavailable
status; values are never fabricated. Stage 7.2 does not implement touches,
breaks, holds, sweeps, opening-range levels, signals, or trading logic.

## Stage 7.3 opening five-minute key levels

For each XNYS RTH session, the opening-range engine consumes the already
persisted and raw-reconciled Stage 2 five-minute candles:

- ORH5: high of the first completed RTH five-minute candle.
- ORL5: low of that same candle.

The first candle must begin at the calendar-provided XNYS session open. On a
normal session it is timestamped 09:30 America/New_York and covers the five
minute-start intervals from 09:30 through 09:34. The range is not available at
09:30; `available_from_timestamp` is explicitly 09:35, after candle completion.

```bash
spy-research opening-5m-levels --start 2026-08-03 --end 2026-08-19
```

The command is offline, read-only, and non-persistent. Only the first candle can
influence ORH5/ORL5, so later session bars cannot change the levels. Stage 7.3
does not implement breaks, holds, sweeps, retests, or other interaction logic.

## Stage 8.1 level interaction classification

Each completed RTH five-minute candle is compared with every available Stage 7
level using exact Decimal prices. The pure classifier returns one primary type:

- `NO_INTERACTION`: the candle range never reaches the level.
- `TOUCH`: the range reaches the level only by equality and does not trade
  strictly through it.
- `WICK_THROUGH_ABOVE` / `WICK_THROUGH_BELOW`: price trades strictly through a
  side but does not establish a new close from the opposite/equal opening side.
- `CLOSE_THROUGH_ABOVE` / `CLOSE_THROUGH_BELOW`: the candle encounters the
  level, opens on the opposite/equal side, and closes strictly through it.

Equality is never a break. Same-side candles entirely beyond a level are
`NO_INTERACTION`; same-side encounters that recover remain wick-throughs or
touches rather than repeated close-through events. Dual-side candles retain
both `traded_above` and `traded_below` facts even though the model has one
primary classification. Previous-close side is descriptive context only.

PDH/PDL/PDC and available PMH/PML are eligible beginning with the first RTH
candle. ORH5/ORL5 become eligible at 09:35 America/New_York on a normal session,
so their 09:30 source candle cannot interact with itself.

```bash
spy-research level-interactions --start 2026-08-19 --end 2026-08-19
```

The service emits only non-`NO_INTERACTION` records by default while retaining
complete eligible-pair counts for audit. It is offline, read-only, and
non-persistent. Stage 8.1 does not infer confirmation or strategy action from a
close-through.

## Stage 8.2 post-break hold and retest context

Only Stage 8.1 `CLOSE_THROUGH_ABOVE` and `CLOSE_THROUGH_BELOW` records seed this
stage. The original interaction remains unchanged. For the first completed
five-minute candle after a break, a close on the break side is `HOLD`, a close
back through the exact level is `FAILURE`, and an equal close is `EQUAL`. When
no same-session next candle exists, the immediate state is `UNAVAILABLE`.

Retest context is separate from the immediate state. The engine searches only
completed same-session bars +1 through +3 and uses the first candle that
encounters the exact level. After a break above, encounter means `low <= level`;
after a break below, it means `high >= level`. A close back on the break side is
`RETEST_HOLD`, a close through to the opposite side is `RETEST_FAILURE`, and an
equal close is `RETEST_EQUAL`. An earlier result is never replaced by a later
bar. If none of the available bars encounters the level, the state is
`NO_RETEST`, which is descriptive and is not a failure.

Near the RTH close, the result records how many of the requested three bars
were available and marks the window incomplete. A final-bar break has both
states unavailable. The engine never bridges overnight and never inspects bar
+4. It uses exact prices only: ATR tolerance is intentionally not implemented.

```bash
spy-research break-follow-through --start 2026-08-19 --end 2026-08-19
```

The command is offline, read-only, and non-persistent. These classifications
are research context only; they do not imply an entry, signal, order, sweep
label, stop, target, or any other trading action.

## Stage 8.3 liquidity-sweep pattern labels

Stage 8.3 derives mechanical labels only from immutable Stage 8.1
`WICK_THROUGH_ABOVE` and `WICK_THROUGH_BELOW` records. It does not rescan the
candle universe or accept touches and close-throughs as seeds.

- `SWEEP_ABOVE` requires `high > level` and `close < level`.
- `SWEEP_BELOW` requires `low < level` and `close > level`.
- A wick-through that closes exactly at the level is explicitly
  `WICK_EQUAL_ABOVE` or `WICK_EQUAL_BELOW`, never a completed sweep.

Excursion distance is `high - level` for an above wick and `level - low` for a
below wick. Reclaim distance is `level - close` for `SWEEP_ABOVE` and
`close - level` for `SWEEP_BELOW`; equality cases retain a zero reclaim
distance. All calculations use exact Decimal prices without tolerance or a
minimum-size threshold. Opening side and both Stage 8.1 `traded_above` and
`traded_below` facts remain attached as descriptive context.

```bash
spy-research sweep-patterns --start 2026-08-19 --end 2026-08-19
```

No future candles are required or accepted. A Stage 8.2 failed completed break
remains distinct from a same-candle wick/reclaim pattern. The label is purely
mechanical and does not demonstrate institutional liquidity activity or imply
a signal, entry, order, stop, or target.

## Stage 8.4 parallel 0.10 event-ATR tolerance

The Stage 8.2 exact-price result remains the permanent baseline. Stage 8.4 adds
an explicitly separate comparison using exactly `0.10 × ATR14` from the
original close-through candle. ATR14 is the accepted Stage 3 session-reset
Wilder value; later-bar, daily, vendor, and fallback ATR values are never used.
The fraction is frozen and is not optimized.

For a break above, the tolerant boundary is `level - tolerance`; for a break
below, it is `level + tolerance`. A close strictly on the break side remains
`HOLD_EXACT`. A close at the level or at/inside the tolerance boundary becomes
`HOLD_WITHIN_TOLERANCE`; a close strictly beyond the boundary remains
`FAILURE`. Boundary equality therefore counts within tolerance.

The immediate comparison uses the same Stage 8.2 next candle. Retest discovery
is never widened: Stage 8.4 reinterprets only the close of the already selected
Stage 8.2 first exact-price encounter within bars +1 through +3. `NO_RETEST`
remains `NO_RETEST` when ATR exists. A seed before the daily ATR14 warm-up is
explicitly `UNAVAILABLE_ATR`; no exact-price fallback is presented as a
tolerant result. Missing future RTH bars remain separately `UNAVAILABLE` and
never bridge sessions.

```bash
spy-research atr-tolerance --start 2026-08-19 --end 2026-08-19
```

The command is offline, read-only, and non-persistent. This tolerance layer is
a descriptive comparison only and does not alter interaction detection,
signals, entries, orders, stops, targets, or performance outcomes.

## Stage 9.1 base price-action setup candidates

Stage 9.1 is the first strategy-candidate layer, but it still assigns no entry
price or performance result. A Stage 8.1 completed close-through is only a
break seed: break alone is not a setup. Primary qualification uses only the
Stage 8.2 exact-price baseline; Stage 8.4 ATR tolerance cannot create a base
candidate.

One break can produce at most one confirmed candidate. The earliest exact
confirmation wins:

1. Stage 8.2 immediate `HOLD` confirms through `IMMEDIATE_HOLD` on bar +1.
2. Otherwise, an already selected Stage 8.2 `RETEST_HOLD` confirms through
   `RETEST_HOLD` at its frozen +1, +2, or +3 retest candle.
3. Equality, failure, no-retest, and unavailable states do not confirm.

Breaks above map to `LONG`; breaks below map to `SHORT`, independently of the
level name. Confirmation is knowable only at the completed confirming candle's
end: `signal_known_at = confirmation_bar_timestamp + 5 minutes`. The earliest
possible future execution timestamp equals that signal-known time. A signal
known exactly at the RTH close is retained but marked not same-session
executable and is never carried overnight.

```bash
spy-research base-setups --start 2026-08-19 --end 2026-08-19
```

The command accounts for every Stage 8.2 break seed and is offline, read-only,
and non-persistent. Stage 9.1 does not assign fills, entry prices, stops,
targets, P&L, or position size and does not use EMA, VWAP, EMA crosses, ATR
tolerance, room-to-next-level, chop, or regime filters.

## Stage 9.2 executable underlying reference and excursions

Stage 9.2 leaves the frozen Stage 9.1 setup population unchanged. For each
confirmed setup that remains executable before the same RTH session ends, it
selects the first validated SPY SIP one-minute RTH bar whose timestamp is at or
after `signal_known_at`. The reference timestamp is that minute's timestamp and
the `entry_reference_price` is its exact stored open. Any delay from the frozen
signal-known timestamp is recorded in whole minutes. A setup known at the
session close remains explicitly unavailable; entry selection never bridges
overnight.

This price is a deterministic underlying backtest reference, not a guaranteed
or slippage-adjusted live fill. It is not an option price and is never selected
using later favorable price action.

Because the reference is the entry minute's open, that same minute participates
in excursion measurement. The 5-, 15-, 30-, and 60-minute windows contain the
entry minute plus the next 4, 14, 29, or 59 same-session RTH minutes. EOD runs
from the entry minute through the final RTH minute. A short fixed window near
the close is calculated from the available minutes and marked incomplete; it
is not extended into another session.

LONG MFE/MAE use `max(high) - entry` and `entry - min(low)`; SHORT reverses the
directional interpretation. Both are clamped at zero, preserve the earliest
tied extreme timestamp, and remain descriptive potential excursions—not
realized P/L, fills, exits, stops, targets, or win/loss results.

```bash
spy-research base-setup-outcomes --start 2026-08-19 --end 2026-08-19
```

The command reads validated local raw and processed data only. It makes no
network requests and writes no market data or outcome artifacts.

## Stage 9.3 base price-action statistical baseline

Stage 9.3 freezes the unfiltered exact-price price-action population as the
control group for later Stage 10 EMA/VWAP comparisons. The development funnel
is 214 completed break seeds, 142 confirmed setups, and 140 executable
same-session entry references. The two session-close confirmations remain
non-executable rather than being carried overnight.

Primary 5-, 15-, 30-, and 60-minute statistics include only complete windows;
incomplete counts remain explicit. EOD uses complete remaining-session windows.
For every horizon the report preserves Decimal mean, median, minimum, and
maximum MFE and MAE, plus descriptive `MFE - MAE`, paired magnitude counts, and
the median MFE/MAE ratio where MAE is nonzero. Zero-MAE observations are counted
separately and never represented as infinity.

The same schema is reported overall and by direction, objective level,
confirmation type, and frozen ET entry-time bucket. Empty groups such as the
current `RETEST_HOLD` population are retained. Groups are not ranked and no
thresholds, parameter cutoffs, or filters are inferred from the sample.

```bash
spy-research base-strategy-stats --start 2026-08-03 --end 2026-08-19
```

The August 3–19 development sample contains only 13 sessions. These results are
descriptive baseline research, not evidence of stable expectancy or statistical
significance. MFE, MAE, `MFE - MAE`, and MFE/MAE ratios are potential excursion
descriptions—not realized returns, winning trades, or execution results. Stage
9 contains no stop, target, exit, position-sizing, EMA, VWAP, ATR-tolerance,
room, chop, or regime logic.

## Local setup

Python 3.12 or newer is required.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
```

Create a local environment file from the placeholder template:

```bash
cp .env.example .env
```

Credentials are not required to load the research configuration or run the
tests. If credentials are added later for historical data access, keep them in
the untracked `.env` file. Never commit or log them.

Run the test suite with:

```bash
pytest
```

Validate only the local, non-secret research configuration with:

```bash
spy-research --help
spy-research config-check
spy-research run-manifest --start 2026-08-03 --end 2026-08-19
spy-research session-summary --start 2026-08-19 --end 2026-08-19
spy-research validate-data --start 2026-08-19 --end 2026-08-19
spy-research aggregate-bars --start 2026-08-19 --end 2026-08-19
spy-research build-5m --start 2026-08-03 --end 2026-08-19
spy-research validate-5m --start 2026-08-03 --end 2026-08-19
spy-research calculate-ema --start 2026-08-19 --end 2026-08-19
spy-research calculate-vwap --start 2026-08-19 --end 2026-08-19
spy-research calculate-atr --start 2026-08-19 --end 2026-08-19
spy-research calculate-ema-separation --start 2026-08-19 --end 2026-08-19
spy-research detect-ema-crosses --start 2026-08-03 --end 2026-08-19
spy-research calculate-cross-outcomes --start 2026-08-03 --end 2026-08-19
spy-research cross-stats --start 2026-08-03 --end 2026-08-19
spy-research previous-day-levels --start 2026-08-03 --end 2026-08-19
spy-research premarket-levels --start 2026-08-03 --end 2026-08-19
spy-research opening-5m-levels --start 2026-08-03 --end 2026-08-19
spy-research level-interactions --start 2026-08-19 --end 2026-08-19
spy-research break-follow-through --start 2026-08-19 --end 2026-08-19
spy-research sweep-patterns --start 2026-08-19 --end 2026-08-19
spy-research atr-tolerance --start 2026-08-19 --end 2026-08-19
spy-research base-setups --start 2026-08-19 --end 2026-08-19
spy-research base-setup-outcomes --start 2026-08-19 --end 2026-08-19
spy-research base-strategy-stats --start 2026-08-03 --end 2026-08-19
```

These commands do not make network requests. The feed is configured only in
`config/research.yaml`; environment files contain credentials only and cannot
override the frozen SIP feed.

Non-secret research settings live in `config/research.yaml`. The typed loader is
available through `spy_research.load_research_config()`; combined YAML and
optional environment settings are available through
`spy_research.load_settings()`.
