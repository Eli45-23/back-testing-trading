"""Allowed labels and required output fields; no historical results generated."""
ALLOWED_LABELS = frozenset(('DISCOVERY_RESULTS','VALIDATION_FAILED','VALIDATION_PASS','INSUFFICIENT','INTERNAL_CONFIRMATION_PASS','INTERNAL_CONFIRMATION_FAIL','ROBUST_EDGE_CANDIDATE','NO ROBUST EDGE DISCOVERED'))
REPORT_FIELDS = ('candidate_id','specification_hash','phase','label','signals','trades','unavailable','ignored_while_open','conflicts','sessions','zero_signal_sessions','wins','losses','zero_r','win_rate','average_win_r','average_loss_r','mean_r','median_r','profit_factor','drawdown_r','losing_streak','monthly','direction','cost_scenarios','ambiguity_sensitivity','bootstrap','multiplicity','search_ledger_hash','input_inventory_hash','batch_hash','validation_receipt_hash','weaknesses')


def validate_label(label):
    if label not in ALLOWED_LABELS: raise ValueError('forbidden result label')
    return label
