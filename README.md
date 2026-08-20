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
```

These commands do not make network requests. The feed is configured only in
`config/research.yaml`; environment files contain credentials only and cannot
override the frozen SIP feed.

Non-secret research settings live in `config/research.yaml`. The typed loader is
available through `spy_research.load_research_config()`; combined YAML and
optional environment settings are available through
`spy_research.load_settings()`.
