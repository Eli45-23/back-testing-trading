"""Approved V1 constants. No historical runner is enabled."""
from .canonical import canonical_bytes, canonical_hash
import json

_PROTOCOL = {
    'version': 'spy-autonomous-edge-discovery-v1-phase1',
    'historical_outcomes_enabled': False,
    'dates': {'DISCOVERY': ['2024-01-02', '2024-12-31'], 'VALIDATION': ['2025-01-02', '2025-12-31'], 'INTERNAL_CONFIRMATION': ['2026-01-02', '2026-09-04'], 'CONTEXT': ['2023-12-29', '2023-12-29']},
    'outcome_partition_counts': {'2024': 252, '2025': 250, '2026': 170},
    'outcome_rth_minutes': 261000,
    'budgets': {'hypotheses': 100, 'strategies': 60, 'validation_candidates': 3},
    'phase_order': ['DESIGN_FROZEN', 'DISCOVERY', 'VALIDATION_BATCH_FROZEN', 'VALIDATION_COMPLETE', 'INTERNAL_CONFIRMATION', 'FINAL_REPORT'],
    'thresholds': {'max_conditions': 3, 'modes': ['natural_reference', 'training_only_quantile'], 'quantile_grid': 'must_be_registered_before_any_corresponding_outcome'},
    'predictive_horizons': [5, 15, 30, 60, 'EOD'],
    'predictive_measurements': ['directional_return', 'MFE', 'MAE', 'favorable_before_adverse'],
    'baselines': ['same_eligible_unconditional', 'month_minute_direction_availability_matched'],
    'predictive_admission': {'observations': 200, 'sessions': 80, 'positive_evaluation_folds': 2, 'nominal_BY_q_max': '0.10'},
    'stops': ['USD030', 'USD050', 'ATR050', 'ATR100'],
    'exits': ['TARGET_1R', 'TARGET_1.5R', 'TARGET_2R', 'TIME_15', 'TIME_30', 'TIME_60'],
    'execution': {'entry': 'first_same_session_minute_open_at_or_after_completed_signal', 'one_position': True, 'pyramiding': False, 'overnight': False, 'opposing_simultaneous': 'NO_ENTRY_CONFLICT', 'while_open': 'IGNORE_AND_RECORD', 'reentry_exit_minute': False, 'stop_gap': 'observed_open', 'target_gap': 'target_price', 'ambiguity': 'stop_first_primary_target_first_sensitivity', 'zero_r_win': False, 'eod': 'last_RTH_minute_close', 'atr': 'existing_same_session_completed_5m_Wilder14_no_fallback', 'prices': 'Decimal'},
    'costs': ['0', '0.01', '0.02'],
    'cost_label': 'SPY_equivalent_per_share_roundtrip_not_options_costs',
    'gates': {'net_cost': '0.02', 'net_mean_r_min': '0.05', 'net_pf_min': '1.10', 'positive_active_month_fraction_min': '2/3', 'net_drawdown_r_max': '40', 'net_total_to_drawdown_min': '1', 'top_positive_month_share_max': '0.35', 'top5_positive_session_share_max': '0.25', 'net_lomo_min_strictly_positive': True, 'expected_direction_unchanged': True,
              'DISCOVERY': {'trades': 200, 'sessions': 80}, 'VALIDATION': {'trades': 200, 'sessions': 80}, 'INTERNAL_CONFIRMATION': {'trades': 150, 'sessions': 60}},
    'bootstrap': {'draws': 10000, 'seed': 20260909, 'unit': 'whole_session', 'shared_resamples': True, 'confidence': '0.95', 'bonferroni_reserved_slots': 3, 'adjusted_two_sided_alpha': '0.05/3', 'validation_confirmation_lower_bound_strictly_positive': True},
    'multiple_testing': {'predictive': 'Benjamini_Yekutieli', 'adaptive_caveat': 'nominal_diagnostic_not_proof_of_selection_bias_removal', 'atomic_count': 'every_inspected_threshold_horizon_direction_subgroup_contrast', 'effective_independent_count': 'not_claimed_without_justification'},
    'selection_order': ['chronological_fold_net_stability', 'net_bootstrap_lower_bound', 'lower_drawdown', 'fewer_conditions', 'stable_specification_id'],
    'validation': {'batch_simultaneous': True, 'replacement': False, 'unused_slots': 'remain_unused', 'complete_batch_before_confirmation': True, '2025_globally_untouched': False},
    'historical_survivor_label': 'ROBUST_EDGE_CANDIDATE',
    'no_survivor_label': 'NO ROBUST EDGE DISCOVERED',
    'prohibited': ['network', 'broker', 'post_2026_09_04_market_access', 'live_promotion', 'options_optimization', 'prior_research_changes'],
}
PROTOCOL_BYTES = canonical_bytes(_PROTOCOL)
PROTOCOL_SHA256 = canonical_hash(_PROTOCOL)


def protocol():
    return json.loads(PROTOCOL_BYTES)
