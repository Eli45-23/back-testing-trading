"""Predeclared finite candidate universe."""
from hashlib import sha256
import json

ENTRIES = ('IMMEDIATE_CLOSE_BACK_1M', 'MOMENTUM_AWAY_025')
STOPS = ('USD025', 'USD030', 'USD040', 'ATR050')
EXITS = ('TARGET_1R', 'TARGET_1.5R', 'TARGET_2R', 'TARGET_2R_BE1R')
MODELS = tuple(f'{stop}_{exit}' for stop in STOPS for exit in EXITS)
PROTOCOL = {
    'version': 'rejection-risk-exit-v1', 'entries': ENTRIES, 'models': MODELS,
    'source_commit': 'a3909eaa0271a381fd6e05756628c07148bac65c',
    'archive_commit': '311f4ada80b4739c207cbdf4a8dda4cef703c632',
    'outcome_dates': ('2026-01-02', '2026-09-04'),
    'costs': ('0', '0.01', '0.02'), 'bootstrap_seed': 20260908,
    'bootstrap_draws': 10000, 'decimal_precision': 80,
    'atr': 'calculate_session_atr: completed consecutive same-session RTH 5m prefix at signal_known_at; no fallback',
    'ambiguity': 'retain flag; stop-first primary; target-first sensitivity',
    'breakeven': 'after first +1R minute completes, active next minute only',
    'gaps': 'stop at open; target at limit; evaluate open before high/low',
    'end': 'last RTH minute close; complete entry-to-close grid required',
    'event_order': ('entry_timestamp', 'interaction_id'),
    'historical_runner_enabled': False,
}

def protocol_hash():
    return sha256(json.dumps(PROTOCOL, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
