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
```

These commands do not make network requests. The feed is configured only in
`config/research.yaml`; environment files contain credentials only and cannot
override the frozen SIP feed.

Non-secret research settings live in `config/research.yaml`. The typed loader is
available through `spy_research.load_research_config()`; combined YAML and
optional environment settings are available through
`spy_research.load_settings()`.
