# Data-validity rules

- The calendar is exactly the first 60 full XNYS sessions beginning 2026-09-08.
- Every planned session must have complete Alpaca SIP SPY RTH 1-minute coverage.
- Minute timestamps must be unique, minute-aligned, ordered, and exactly span the
  exchange's left-closed RTH interval (including actual early-close boundaries).
- Missing, duplicate, malformed, or conflicting data blocks the endpoint. No
  replacement day, forward fill, interpolation, or later-data reconstruction is
  allowed.
- Data access must be allowlisted by the exact planned session date before a file
  is opened. Development dates and sessions outside the 60-date plan fail closed.
- Aggregation and ATR initialization reuse the frozen implementations unchanged;
  no alternative source, prior-session ATR inheritance, or fallback is permitted.
- Coverage receipts must include each session, RTH minute count, duplicate/missing
  counts, early-close flag, and deterministic aggregation/indicator checks.
- This design has no loader, network client, or broker path. Outcome generation is
  disabled until a separately reviewed validation-run instruction.
