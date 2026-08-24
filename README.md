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

## Stage 10.1 controlled EMA directional comparison

Stage 10 comparisons never modify the frozen Stage 9 control group. Stage 10.1
attaches one descriptive EMA label to every confirmed setup and compares the
unchanged Stage 9.2 MFE/MAE outcomes. It does not regenerate setup qualification,
entry references, or excursions.

The EMA source is the accepted daily-reset RTH five-minute EMA9/EMA20 engine.
For a setup known at the end of a completed confirmation candle, alignment uses
only the indicator row keyed to `confirmation_bar_timestamp`. It never uses the
next five-minute row or the one-minute entry timestamp. If either EMA is still
warming up, the setup remains explicitly `EMA_UNAVAILABLE`; values are never
backfilled from an earlier or previous session.

Directional labels are frozen as follows:

- LONG is `EMA_ALIGNED` only when EMA9 is strictly greater than EMA20.
- SHORT is `EMA_ALIGNED` only when EMA9 is strictly less than EMA20.
- Equality is `EMA_NOT_ALIGNED` for either direction.

Stage 10.1 has no recent-cross requirement and no EMA slope, separation,
expansion, distance, or ATR-normalized threshold. It does not use VWAP. The
comparison reports `BASE_ALL`, aligned, not-aligned, and unavailable groups with
the same complete-window Decimal statistics used by Stage 9.3, including simple
median deltas from the baseline.

```bash
spy-research compare-ema-alignment --start 2026-08-03 --end 2026-08-19
```

The command is offline, read-only, and non-persistent. The development sample
contains only 13 sessions, so the output is exploratory descriptive research—not
evidence of statistical significance, stable expectancy, or a validated edge.

## Stage 10.2 exact prior-cross context

Stage 10.2 joins every frozen Stage 9 confirmed setup to the accepted Stage 4
EMA9/EMA20 cross history. It does not redetect crosses. A Stage 4 cross timestamp
is the five-minute bucket start, so its information becomes available only at
`cross_timestamp + 5 minutes`. Only a cross from the same RTH session with
`cross_known_at <= setup.signal_known_at` is eligible. The chronologically most
recent eligible cross is authoritative, even when an older cross would match the
setup direction.

A cross on the setup confirmation candle is contemporaneous, not future data,
and has `bars_since_cross = 0`. LONG setups match bullish crosses; SHORT setups
match bearish crosses. The other direction is `OPPOSING_CROSS`, and a session
with no eligible cross is explicitly `NO_PRIOR_CROSS`; prior sessions are never
bridged.

The annotation stores the exact integer bars since cross and minutes since cross
completion. Stage 10.2 deliberately does not define or optimize a “recent”
cutoff. It reuses unchanged Stage 9 entries and MFE/MAE outcomes, while the Stage
10.1 confirmation-bar EMA alignment remains a separate descriptive dimension.

```bash
spy-research compare-ema-cross-context --start 2026-08-03 --end 2026-08-19
```

The command is offline, read-only, and non-persistent. Its exact-recency rows and
alignment cross-tab describe only the 13-session development sample. Tiny groups
must not be interpreted as statistical significance, stable expectancy, or a
validated strategy filter.

## Stage 10.3 controlled price/VWAP comparison

Stage 10.3 labels every frozen Stage 9 confirmed setup using only the completed
five-minute confirmation candle close and the accepted Stage 3 VWAP at that exact
same bucket timestamp. The setup is already knowable at the candle completion,
five minutes after its bucket-start timestamp; the next five-minute bar and the
one-minute entry reference are never used for this annotation.

The VWAP source remains the daily-reset RTH HLC3/volume calculation. It starts at
09:30 America/New_York each session and excludes premarket and overnight volume.
LONG requires `confirmation close > VWAP`, while SHORT requires
`confirmation close < VWAP`. Equality is `VWAP_NOT_ALIGNED`. A missing exact-row
VWAP remains explicitly `VWAP_UNAVAILABLE` without backfill or another-bar
fallback.

Signed, absolute, and direction-normalized price/VWAP distances are retained as
exact Decimal descriptions. Stage 10.3 defines no distance threshold, VWAP slope,
price/VWAP cross, EMA/VWAP cross, or combined EMA+VWAP strategy filter. Stage
10.1 EMA alignment and Stage 10.2 prior-cross context remain separate dimensions,
and Stage 9 setups, entries, and outcomes remain unchanged.

```bash
spy-research compare-vwap-alignment --start 2026-08-03 --end 2026-08-19
```

The command is offline, read-only, and non-persistent. Results describe only the
13-session development sample and are not evidence of significance, stable
expectancy, or a validated edge.

## Stage 10.4 controlled EMA9/VWAP comparison

Stage 10.4 compares accepted Stage 3 EMA9 directly with accepted Stage 3 RTH
VWAP on the exact completed five-minute confirmation row. Both values are keyed
to `confirmation_bar_timestamp` and are known at `signal_known_at`, five minutes
after the bucket start. Entry-time, next-bar, later-session, and prior-session
indicator values are never substitutes.

LONG is aligned only when EMA9 is strictly greater than VWAP. SHORT is aligned
only when EMA9 is strictly less than VWAP. Equality is not aligned. The accepted
daily EMA9 warm-up remains intact; a missing same-row EMA9 or VWAP is explicitly
`EMA9_VWAP_UNAVAILABLE` and is never backfilled.

Signed, absolute, and direction-normalized EMA9/VWAP distances remain exact
Decimal descriptions without cutoffs or ATR normalization. Price/VWAP from
Stage 10.3 and EMA9/VWAP are separate dimensions, including explicit agreement
and disagreement counts. Stage 10.4 does not inspect the prior EMA9/VWAP
relationship and does not detect an EMA9/VWAP cross.

```bash
spy-research compare-ema9-vwap-alignment --start 2026-08-03 --end 2026-08-19
```

The command is offline, read-only, and non-persistent. Stage 9 remains immutable,
and the 13-session development sample remains exploratory rather than evidence
of stable expectancy or a validated strategy rule.

## Stage 10.5 EMA9/VWAP cross-event context

Stage 10.5 builds a reusable completed-candle event universe from the accepted
Stage 3 EMA9 and RTH VWAP rows. A bullish event requires `EMA9[t] > VWAP[t]`
after `EMA9[t-1] <= VWAP[t-1]`; a bearish event requires `EMA9[t] < VWAP[t]`
after `EMA9[t-1] >= VWAP[t-1]`. Equality followed by separation counts, while a
persistent same-side relationship does not repeat events.

Detection resets every RTH session and requires valid EMA9 and VWAP on adjacent
same-session five-minute rows. EMA9 warm-up is preserved without backfill or an
overnight bridge. The event timestamp is the five-minute bucket start, and the
event becomes known only at `cross_timestamp + 5 minutes`.

Each frozen Stage 9 setup receives only the latest same-session event satisfying
`cross_known_at <= signal_known_at`. A cross on the confirmation candle is valid
with zero bars of recency. LONG maps to bullish and SHORT to bearish; the latest
opposite event remains authoritative even when an older matching event exists.
No prior event is explicit, and exact bars/minutes since cross are retained.

```bash
spy-research compare-ema9-vwap-cross-context \
  --start 2026-08-03 --end 2026-08-19
```

Current EMA9/VWAP alignment and prior EMA9/VWAP cross context remain separate
descriptive concepts. The command is offline, read-only, and non-persistent. It
defines no recent-cross cutoff, optimization, or cross-only strategy, and the
13-session sample is not evidence of stable expectancy or a validated edge.

## Stage 10.6 controlled EMA20/VWAP comparison

Stage 10.6 compares accepted Stage 3 EMA20 directly with accepted Stage 3 RTH
VWAP on the exact completed five-minute confirmation row. Both values are keyed
to `confirmation_bar_timestamp`; signal-known time and entry time never select a
later indicator row. The accepted daily EMA20 warm-up remains intact, and a
missing same-row EMA20 or VWAP is explicitly `EMA20_VWAP_UNAVAILABLE` without
backfill, alternate-row lookup, or previous-session fallback.

LONG is aligned only when EMA20 is strictly above VWAP. SHORT is aligned only
when EMA20 is strictly below VWAP. Equality is not aligned. Signed, absolute,
and direction-normalized EMA20/VWAP distances use exact Decimal arithmetic with
no cutoff or ATR normalization.

EMA20/VWAP remains separate from EMA9/VWAP. The report preserves their full
cross-tab and every naturally observed descending EMA9/EMA20/VWAP stack order,
including equality or unavailable values if present. Stack states are
descriptive annotations only and do not qualify setups or rank configurations.

```bash
spy-research compare-ema20-vwap-alignment \
  --start 2026-08-03 --end 2026-08-19
```

The command is offline, read-only, and non-persistent. It does not detect
EMA20/VWAP crosses, create combined confirmation rules, or alter the frozen
Stage 9 setups, entries, and outcomes. The 13-session development sample remains
exploratory rather than evidence of stable expectancy or a validated edge.

## Stage 10.7 EMA20/VWAP cross-event context

Stage 10.7 detects completed-candle EMA20/VWAP reversals from accepted Stage 3
rows. A bullish event requires `EMA20[t] > VWAP[t]` after
`EMA20[t-1] <= VWAP[t-1]`; a bearish event requires `EMA20[t] < VWAP[t]` after
`EMA20[t-1] >= VWAP[t-1]`. Equality followed by separation counts, while a
persistent relationship does not produce repeated events.

Detection requires adjacent valid RTH five-minute rows in the same session.
EMA20 warm-up remains unchanged, sessions never bridge overnight, and an event
on the bucket beginning at `cross_timestamp` becomes known only at
`cross_timestamp + 5 minutes`.

Each frozen Stage 9 setup receives the latest same-session event satisfying
`cross_known_at <= signal_known_at`. LONG matches bullish and SHORT matches
bearish. A cross on the confirmation candle is valid with zero bars of recency;
future events and events from other sessions cannot annotate the setup.

```bash
spy-research compare-ema20-vwap-cross-context \
  --start 2026-08-03 --end 2026-08-19
```

The command is offline, read-only, and non-persistent. It reports the event
universe, matching/opposing/no-prior populations, exact recency, unchanged
five-horizon outcomes, and EMA9/VWAP-versus-EMA20/VWAP cross context. It defines
no cutoff, score, filter, optimization, or trading rule.

## Stage 10.8 combined context matrix

Stage 10.8 joins the accepted Stage 10.1–10.7 annotations by immutable Stage 9
setup identity. Each record retains direction, level, confirmation and
signal-known timestamps, EMA9/EMA20 alignment and prior-cross context,
price/VWAP alignment, EMA9/VWAP alignment and prior-cross context, and
EMA20/VWAP alignment and prior-cross context. All three cross systems preserve
their exact bars-since-cross value or explicit no-prior state.

Exact matrix groups use direction, all seven context states, and all three
recencies. Level and session are reported as composition and coverage; they are
not qualification fields. Every group retains the unchanged Stage 9 outcomes at
5, 15, 30, and 60 minutes and EOD, including complete and incomplete counts.

The report reconciles every marginal state to its accepted source stage and
reproduces Stage 9.3 `BASE_ALL` exactly. It also exposes percentage of BASE_ALL,
singletons, and groups with `n <= 5`. These are neutral sparsity disclosures,
not significance tests or minimum-sample rules.

```bash
spy-research compare-combined-context-matrix \
  --start 2026-08-03 --end 2026-08-19
```

The matrix is offline, read-only, deterministic, and non-persistent. It does
not label combinations as good, bad, trend, transition, chop, or qualified; it
does not rank, score, filter, optimize, or create a trading strategy.

## Stage 10.9 market-condition feature measurements

Stage 10.9 measures chart conditions at each frozen Stage 9 confirmation without
classifying a regime. Every rolling window ends at the completed confirmation
candle, contains exactly the latest 6, 12, or 24 same-session candles, and never
bridges an RTH session boundary. Future candles and entry data are not inputs.

The immutable annotation contains absolute EMA9/EMA20 separation; separation
divided by confirmation-row ATR14; per-bar EMA9, EMA20, and VWAP slopes over 1,
2, and 3 bars; EMA9/EMA20, EMA9/VWAP, and EMA20/VWAP cross counts; price/VWAP
side-change counts; rolling high-low range; range divided by ATR14; directional
efficiency; candle-range overlap; close-direction alternation; and absolute
confirmation-close, EMA9, and EMA20 distances from VWAP in ATR14 units.

For an N-bar window, directional efficiency is
`abs(close[-1] - close[0]) / sum(abs(close[i] - close[i-1]))`. A zero path is
unavailable. Range overlap is the fraction of the N-1 adjacent bar pairs whose
closed high-low intervals intersect. Close-direction alternation is the fraction
of the N-2 adjacent move pairs with nonzero opposite signs. Crosses and strict
price/VWAP side changes are counted only between adjacent rows inside the exact
window; equality itself is not a side change. Slopes are
`(value[t] - value[t-k]) / k` per completed bar.

ATR-normalized fields use only ATR14 on the confirmation row. Missing ATR,
nonpositive ATR, indicator warm-up, an insufficient same-session window, or a
zero directional path remains explicitly unavailable—there is no backfill.
All applicable calculations use Decimal arithmetic.

```bash
spy-research market-condition-features \
  --start 2026-08-03 --end 2026-08-19
```

The offline, read-only report gives each feature's available and unavailable
count, minimum, quartiles, median, and maximum. Q1-Q4 boundaries use deterministic
linear `(n-1)` sample percentiles and are stored only in the report. Each quartile
reuses unchanged Stage 9 outcomes and reports setup/executable counts, direction
composition, session coverage, and median MFE, MAE, and MFE-minus-MAE at all five
horizons. Quartiles are descriptive sample partitions, not persistent settings,
strategy thresholds, ranks, filters, scores, or evidence of causation.

## Stage 11.1 predeclared market-regime hypotheses

Stage 11.1 projects the accepted Stage 10.9 confirmation-time measurements into
a deliberately small set of research labels. Assignment is outcome-blind: the
classifier accepts only an immutable Stage 10.9 annotation and the exact
quartile boundaries already stored in its report. Outcomes are joined only
after every label has been assigned.

The individual hypotheses are frozen as follows:

- 24-bar directional efficiency: Q4 `HIGH_EFFICIENCY`, Q2-Q3
  `MID_EFFICIENCY`, Q1 `LOW_EFFICIENCY`.
- EMA9/EMA20 separation divided by ATR14: Q4 `WIDE_SEPARATION`, Q2-Q3
  `MID_SEPARATION`, Q1 `TIGHT_SEPARATION`.
- 24-bar close-direction alternation: Q4 `HIGH_ALTERNATION`, Q2-Q3
  `MID_ALTERNATION`, Q1 `LOW_ALTERNATION`.
- Confirmation-close distance from VWAP divided by ATR14: Q4
  `FAR_FROM_VWAP`, Q2-Q3 `MID_DISTANCE`, Q1 `NEAR_VWAP`.

Unavailable Stage 10.9 values remain `UNAVAILABLE`. The four accepted 24-bar
cross-activity measurements—EMA9/EMA20, EMA9/VWAP, EMA20/VWAP, and strict
price/VWAP side changes—retain both their exact integer count categories and a
separate neutral Q1/Q2-Q3/Q4 description. No new count cutoff is introduced.

Exactly two combined hypotheses are declared:

```text
TREND_LIKE_A = HIGH_EFFICIENCY and WIDE_SEPARATION
CHOP_LIKE_A  = LOW_EFFICIENCY and HIGH_ALTERNATION
```

All three inputs used by the combined hypothesis—efficiency, separation, and
alternation—must be available; otherwise the combined state is `UNAVAILABLE`.
An available setup matching neither declaration is `OTHER`. The names are
hypotheses only, not market facts, setup qualifications, or trading filters.

```bash
spy-research compare-regime-hypotheses \
  --start 2026-08-03 --end 2026-08-19
```

The command is offline, read-only, deterministic, and non-persistent. It reports
unchanged five-horizon Stage 9 outcomes, direction/level/session composition,
session concentration, and overlap with accepted Stage 10 alignment and cross
context. States below 10 executable setups or five represented sessions are
flagged as sparse disclosures. The 13-session development sample is not used
for significance tests, threshold searches, optimization, promotion, scoring,
or filtering.

## Stage 11.2 objective room to the next level

Stage 11.2 measures directional space from each frozen Stage 9 confirmation
close to the nearest known objective Stage 7 level. The candidate universe is
limited to PDH, PDL, PDC, PMH, PML, ORH5, and ORL5. Previous-day and finalized
premarket values are available from the XNYS RTH open; ORH5/ORL5 retain their
accepted `available_from_timestamp` at 09:35 America/New_York. A level with an
availability timestamp after `setup.signal_known_at` is never eligible.

For LONG, the selector chooses the minimum eligible level price strictly above
the confirmation close. For SHORT, it chooses the maximum eligible price
strictly below. Equality is excluded, and the triggering level type is removed
from the directional candidate set. Multiple level types at the selected price
are retained in deterministic `LevelType` order. No directional candidate is
reported as `OPEN_ENDED`; no HOD, LOD, target, or fabricated level is substituted.

Confirmation room is `next - confirmation` for LONG and `confirmation - next`
for SHORT. The accepted Stage 9.2 entry reference never selects the next level;
when available, its separate descriptive value reports the remaining signed
distance to that already selected confirmation-time level. ATR normalization
uses only accepted ATR14 at the confirmation timestamp. Missing or nonpositive
ATR remains unavailable without later substitution.

The fixed confirmation-room/ATR buckets are:

```text
[0, 0.5)   LT_0_5_ATR
[0.5, 1.0) ATR_0_5_TO_1_0
[1.0, 1.5) ATR_1_0_TO_1_5
[1.5, 2.0) ATR_1_5_TO_2_0
[2.0, 3.0] ATR_2_0_TO_3_0
> 3.0      GT_3_0_ATR
```

`OPEN_ENDED` and `UNAVAILABLE_ATR` remain separate. Stacked-level descriptions
count eligible directional level records at distances less than or equal to
0.5 and 1.0 confirmation-time ATR; tied level types count separately. These
counts are not congestion scores.

```bash
spy-research compare-room-to-next-level \
  --start 2026-08-03 --end 2026-08-19
```

The command is offline, read-only, deterministic, and non-persistent. It reports
raw and normalized distributions, unchanged Stage 9 outcomes by fixed bucket,
trigger-to-next-level counts, and count/EOD cross-tabs against accepted Stage
10 alignment and Stage 11.1 regime context. Nothing in the report filters,
ranks, scores, targets, or changes a setup.

## Stage 11.3 confirmed five-minute swing structure

Stage 11.3 detects one frozen swing definition from the accepted Stage 2 RTH
five-minute candles. Detection resets at every session and uses exactly two
left bars and two right bars. A swing high requires the pivot high to be
strictly greater than both left highs and greater than or equal to both right
highs. A swing low requires the pivot low to be strictly less than both left
lows and less than or equal to both right lows. Thus a tie on the left rejects
the pivot while a tie on the right is accepted. Pivot width is not optimized.

A candle timestamp identifies the start of its five-minute interval. The pivot
candle completes at `t+5`, the first right candle at `t+10`, and the second right
candle at `t+15`; consequently `pivot_known_at = pivot_timestamp + 15 minutes`.
A setup can see only same-session swings whose `pivot_known_at` is no later than
its frozen `signal_known_at`. Prior-session, next-session, and future-confirmed
swings never participate.

The latest two visible highs classify as `HIGHER_HIGH`, `LOWER_HIGH`, or
`EQUAL_HIGH`; the latest two lows classify as `HIGHER_LOW`, `LOWER_LOW`, or
`EQUAL_LOW`. Missing either pair is `UNAVAILABLE`. `BULLISH_STRUCTURE` means
higher high plus higher low, `BEARISH_STRUCTURE` means lower high plus lower
low, and every other fully available pair is `MIXED_STRUCTURE`. Mixed is not a
synonym for chop. LONG/bullish and SHORT/bearish are separately annotated as
`STRUCTURE_ALIGNED`; this is descriptive and cannot qualify a setup.

Absolute confirmation-close distances use only the latest visible swing high
and low. ATR-normalized distances use only accepted ATR14 at the confirmation
timestamp; later ATR is never substituted. A separate structural-room field
compares the latest directional swing with the already-selected Stage 11.2
objective level without changing that level or creating a target.

```bash
spy-research compare-market-structure \
  --start 2026-08-03 --end 2026-08-19
```

The offline, read-only, non-persistent report includes the complete confirmed
swing universe, structure and direction-agreement populations, unchanged
five-horizon Stage 9 outcomes, and count/EOD cross-tabs against accepted regime,
room, and alignment context. It does not create alternative pivot widths,
filters, scores, trades, stops, targets, exits, or persistent output.

## Stage 12.2 expanded frozen-rule stability analysis

Stage 12.2 analyzes the accepted January 2–August 19 population without
changing any setup, context, outcome, threshold, or source object. The Stage
11.1 quartile boundaries remain the exact values derived from the isolated
August 3–19 development snapshot. Applying those boundaries backward to
January–July is an **expanded frozen-rule stability analysis**, not a
chronological out-of-sample test, predictive validation, statistical
significance claim, or demonstration of stable expectancy.

The deterministic report separates the isolated development snapshot,
January–July pre-development observations, the complete expanded sample, and
each represented calendar month. It reports accepted Stage 9–11 groups,
direction- and level-controlled views, session concentration, only the three
predeclared Stage 11 two-way relationships, leave-one-month-out sensitivity,
and development-versus-expanded differences. Sample-size labels are disclosure
only: `<10` is `VERY_SMALL`, `10–29` is `SMALL`, `30–99` is `MODERATE`, and
`>=100` is `LARGE`.

Bootstrap uncertainty resamples complete sessions rather than individual
setups. It uses seed `12022026` and exactly 10,000 resamples for BASE_ALL and
eligible groups with at least 100 executable observations across at least 20
sessions. The 2.5th/50th/97.5th percentiles are labeled bootstrap uncertainty
intervals, not formal confidence intervals about future profitability.

```bash
spy-research validate-expanded-stability \
  --start 2026-01-02 --end 2026-08-19
```

The command is offline, read-only, deterministic, and non-persistent. It does
not rank groups, produce a trade or quality score, optimize parameters, create
filters, or calculate stops, targets, exits, win rate, realized P/L,
expectancy, sizing, option results, or live/paper signals.

## Stage 12.3 controlled strategy-variant selection

Stage 12.3 freezes exactly ten research candidates before joining the accepted
Stage 9 outcomes: `BASE_ALL`, `BASE_LONG`, `BASE_SHORT`, `EMA_STACK_ALIGNED`,
`STRUCTURE_ALIGNED`, `ROOM_GE_1_ATR`, `EMA_STACK_AND_STRUCTURE`,
`EMA_STACK_AND_ROOM_GE_1_ATR`, `STRUCTURE_AND_ROOM_GE_1_ATR`, and
`FULL_CONFLUENCE`. The closed candidate enum prevents arbitrary combination
search. EMA stack membership requires all four accepted directional alignment
states. Room membership requires an exact finite Stage 11.2 `room_in_atr >=
1.0`; open-ended or ATR-unavailable room never receives a substitute value.

Membership consumes only context already known at `signal_known_at`. Outcomes
are joined afterward for descriptive five-horizon, chronological partition,
monthly, leave-one-month-out, and session-bootstrap reporting. A scorecard
requires at least 30 executable setups across at least 20 executable sessions.
`BASE_ALL` always remains `RETAIN_AS_CONTROL`; every other eligible candidate
must pass all seven documented mechanical criteria to receive
`ADVANCE_TO_STAGE_13`. The bootstrap uses the frozen seed `12022026` and 10,000
whole-session resamples. Its output remains an uncertainty interval, not a
formal confidence interval.

```bash
spy-research select-stage13-variants \
  --start 2026-01-02 --end 2026-08-19
```

The command is offline, read-only, deterministic, and non-persistent. Selection
does not execute a strategy and does not calculate stops, targets, exits,
first-hit order, realized P/L, win rate, expectancy, sizing, options, live
signals, or paper trades.

## Stage 13.1 deterministic realized-trade simulation

Stage 13.1 simulates SPY-share trade paths for only the accepted `BASE_ALL`
control and `BASE_SHORT` Stage 12.3 candidate. It does not requalify setups.
Entry is the exact Stage 9.2 first same-session RTH one-minute open at or after
`signal_known_at`, and the entry minute is included in the path.

The frozen stop family is `ATR_0_50`, `ATR_0_75`, and `ATR_1_00`, using ATR14
from the confirmation five-minute candle only. The frozen targets are `1R`,
`1.5R`, `2R`, `2.5R`, and `3R`, producing exactly fifteen stop/target variants.
Missing or nonpositive confirmation ATR makes the trade unavailable. No later
ATR may backfill it.

First-hit sequencing uses same-session RTH one-minute highs and lows. A bar that
touches both stop and target is retained as `AMBIGUOUS_BOTH_TOUCHED`; its OHLC
is audited and it is excluded from primary realized statistics. If neither
level is touched, the exit is the final same-session RTH one-minute close.
Exact stops are `-1R`, exact targets equal their requested R, and EOD exits use
exact Decimal price P/L divided by initial risk.

```bash
spy-research simulate-fixed-risk-trades \
  --start 2026-01-02 --end 2026-08-19
```

The command is offline, read-only, deterministic, and non-persistent. It reports
all fifteen variants without ranking or recommending one. Stage 13.1 does not
include slippage, commissions, position sizing, options, next-level targets,
trailing stops, breakeven logic, optimization, live orders, or paper trading.

## Stage 13.2 controlled exit-model comparison

Stage 13.2 keeps the accepted `BASE_ALL` and `BASE_SHORT` memberships, Stage
9.2 entry timestamp, and entry price unchanged. It compares all fifteen Stage
13.1 fixed-risk controls with twenty-one predeclared exits: three ATR stops for
each of opposite EMA9/20, EMA9/VWAP, and EMA20/VWAP crosses; three ATR stops at
15-, 30-, and 60-minute exits; and three ATR stops paired with the frozen Stage
11.2 next objective level. It does not rank or select an exit.

An opposite cross can act only after its completed five-minute candle is
knowable (`cross_timestamp + 5 minutes`) and strictly after entry. Cross and
time exits use the first same-session one-minute open at or after that time.
When an open exit and a stop touch share a minute, the open exit occurs before
that minute's high/low. A stop touched in an earlier minute wins. Objective
targets retain Stage 13.1 first-hit behavior, including an explicit ambiguous
state when stop and target touch in the same one-minute bar. Open-ended Stage
11.2 room is unavailable and is never replaced with another target. Every
remaining trade exits at the final RTH close; nothing carries overnight.

```bash
spy-research compare-exit-models \
  --start 2026-01-02 --end 2026-08-19
```

The offline, read-only report includes exact Decimal SPY-share P/L and R,
monthly and leave-one-month-out descriptions, and deterministic 10,000-draw
session-clustered bootstrap uncertainty intervals for mean and median R. Those
intervals are descriptive, not predictive confidence intervals. Stage 13.2
does not add costs, sizing, options, persistence, optimization, orders, or a
recommendation.

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
spy-research compare-ema-alignment --start 2026-08-03 --end 2026-08-19
spy-research market-condition-features --start 2026-08-03 --end 2026-08-19
spy-research compare-regime-hypotheses --start 2026-08-03 --end 2026-08-19
spy-research compare-room-to-next-level --start 2026-08-03 --end 2026-08-19
spy-research compare-market-structure --start 2026-08-03 --end 2026-08-19
spy-research validate-expanded-stability --start 2026-01-02 --end 2026-08-19
spy-research select-stage13-variants --start 2026-01-02 --end 2026-08-19
spy-research simulate-fixed-risk-trades --start 2026-01-02 --end 2026-08-19
spy-research compare-exit-models --start 2026-01-02 --end 2026-08-19
```

These commands do not make network requests. The feed is configured only in
`config/research.yaml`; environment files contain credentials only and cannot
override the frozen SIP feed.

Non-secret research settings live in `config/research.yaml`. The typed loader is
available through `spy_research.load_research_config()`; combined YAML and
optional environment settings are available through
`spy_research.load_settings()`.
