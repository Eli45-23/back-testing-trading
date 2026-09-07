# Stage 15.2 Out-of-Sample Data-Quality Gate

This gate was completed before any 2024 or 2025 strategy outcomes were loaded.
Both years are eligible for the frozen Stage 15.2 candidate comparison.

## Historical entitlement

- Source: Alpaca historical stock-data API
- Symbol/feed/timeframe/adjustment: `SPY / SIP / 1Min / raw`
- 2025 entitlement probe: pass
- 2024 entitlement probe: pass
- Alpaca PAPER connection or order activity: none
- Storage isolation: dedicated ignored `data/oos/raw` and `data/oos/processed`
  roots; accepted 2026 stores are not extended with prior-year context

## Raw SIP coverage

| Period | XNYS sessions | Raw bars | Expected RTH | Observed RTH | Missing | Extra | Duplicates | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2025 | 250/250 | 211,613 | 96,960 | 96,960 | 0 | 0 | 0 | PASS |
| 2024 | 252/252 | 197,013 | 97,740 | 97,740 | 0 | 0 | 0 | PASS |
| 2023-12-29 context | 1/1 | 711 | 390 | 390 | 0 | 0 | 0 | PASS |

The validator reported 12 out-of-session warnings in 2025 and five in 2024
for prints outside the configured 04:00–20:00 window. They do not overlap RTH,
are not repaired or filled, and are not used by the RTH research pipeline.

## Deterministic aggregation

- Combined sessions: 502
- Raw RTH minutes: 194,700
- Generated five-minute bars: 38,940
- New processed bars: 38,940
- Conflicts: 0
- Reconciliation errors: 0
- 2025 processed coverage: 19,392/19,392, no missing or duplicates
- 2024 processed coverage: 19,548/19,548, no missing or duplicates

## Level and initialization compatibility

| Year | Previous-day levels | Missing prior sources | Premarket levels | Premarket unavailable | Opening 5m levels |
|---|---:|---:|---:|---:|---:|
| 2025 | 250 | 0 | 250 | 0 | 250 |
| 2024 | 252 | 0 | 252 | 0 | 252 |

The services are the same frozen implementations used by the accepted 2026
pipeline. Indicator initialization remains RTH-only with the accepted EMA,
VWAP, and Wilder ATR configuration; level construction and signal timing are
unchanged. No missing market data was filled.
