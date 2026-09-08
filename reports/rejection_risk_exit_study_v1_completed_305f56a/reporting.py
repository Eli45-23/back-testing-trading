"""Run-artifact reporting adapter for the unchanged frozen risk/exit kernel.

Consumes computed outcome records only. Does not load market data or call a broker.
All price, R, cost and percentile arithmetic uses Decimal at precision 80.
"""

from collections import Counter, defaultdict
from decimal import Decimal as D, localcontext, ROUND_HALF_EVEN
import csv
import json
from pathlib import Path
import random

from spy_research.rejection_risk_exit_v1.protocol import ENTRIES, MODELS, EXITS, PROTOCOL

COSTS = (D('0'), D('0.01'), D('0.02'))
SENSITIVITIES = ('stop_first', 'target_first')
UNAVAILABLE = ('UNAVAILABLE_ATR', 'UNAVAILABLE_PATH', 'UNAVAILABLE_ENTRY', 'INVALID_RISK')


def _ratio(a, b):
    return D(a) / D(b) if b else None


def _mean(values):
    return sum(values, D(0)) / D(len(values)) if values else None


def _percentile(values, p):
    if not values:
        return None
    ordered = sorted(values)
    index = D(len(ordered) - 1) * p
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - D(lower))


def _write_csv(outdir, name, rows):
    rows = list(rows)
    fields = list(dict.fromkeys(key for row in rows for key in row))
    path = outdir / name
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    return {'file': name, 'rows': len(rows), 'bytes': path.stat().st_size}


def _write_json(outdir, name, data):
    path = outdir / name
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + '\n', encoding='utf-8')
    return {'file': name, 'bytes': path.stat().st_size}


def _prepare(row):
    result = dict(row)
    result['session_date'] = str(result['session_date'])
    result['entry_timestamp'] = str(result['entry_timestamp'])
    for name in ('risk', 'low_r', 'high_r'):
        result[name] = None if result.get(name) is None else D(result[name])
    result['_usable'] = all(result.get(name) is not None for name in ('risk', 'low_r', 'high_r'))
    if result['_usable']:
        if result['risk'] <= 0 or not all(result[name].is_finite() for name in ('risk', 'low_r', 'high_r')):
            raise ValueError('invalid executable numeric result')
        if result['status'] in UNAVAILABLE:
            raise ValueError('unavailable status has executable values')
        if result['high_r'] < result['low_r']:
            raise ValueError('sensitivity values reversed')
        result['_inverse_risk'] = D(1) / result['risk']
    elif result['status'] not in UNAVAILABLE:
        raise ValueError('unknown unavailable result')
    result['_identity'] = (result['interaction_id'], result['session_date'])
    return result


def _value(row, cost, sensitivity):
    return row['low_r' if sensitivity == 'stop_first' else 'high_r'] - cost / row['risk']


def _metrics(rows, cost, sensitivity, session_dates):
    usable = [row for row in rows if row['_usable']]
    values = [_value(row, cost, sensitivity) for row in usable]
    wins = [value for value in values if value > 0]
    losses = [value for value in values if value < 0]
    zero = sum(value == 0 for value in values)
    cumulative = peak = drawdown = D(0)
    streak = max_streak = 0
    for row in sorted(usable, key=lambda x: (x['entry_timestamp'], x['interaction_id'])):
        value = _value(row, cost, sensitivity)
        cumulative += value
        peak = max(peak, cumulative)
        drawdown = max(drawdown, peak - cumulative)
        streak = streak + 1 if value < 0 else 0
        max_streak = max(max_streak, streak)
    monthly = defaultdict(list)
    for row, value in zip(usable, values):
        monthly[row['session_date'][:7]].append(value)
    month_keys = sorted({day[:7] for day in session_dates})
    month_means = {month: _mean(monthly[month]) for month in month_keys}
    nonempty_months = {key: value for key, value in month_means.items() if value is not None}
    lomo = []
    for month in month_keys:
        retained = [value for row, value in zip(usable, values) if row['session_date'][:7] != month]
        if retained:
            lomo.append(_mean(retained))
    unavailable_counts = Counter(row['status'] for row in rows if not row['_usable'])
    pf = sum(wins, D(0)) / abs(sum(losses, D(0))) if losses else None
    result = {
        'eligible_entries': len(rows), 'executable_outcomes': len(usable),
        'unavailable_outcomes': len(rows) - len(usable),
        'atr_unavailable': unavailable_counts['UNAVAILABLE_ATR'],
        'path_unavailable': unavailable_counts['UNAVAILABLE_PATH'],
        'entry_unavailable': unavailable_counts['UNAVAILABLE_ENTRY'],
        'invalid_risk': unavailable_counts['INVALID_RISK'],
        'ambiguous_outcomes': sum(row['status'] == 'AMBIGUOUS_STOP_TARGET' for row in usable),
        'eligible_sessions': len({row['session_date'] for row in rows}),
        'contributing_sessions': len({row['session_date'] for row in usable}),
        'calendar_sessions': len(session_dates),
        'zero_outcome_sessions': len(session_dates) - len({row['session_date'] for row in usable}),
        'wins': len(wins), 'losses': len(losses), 'zero_r_outcomes': zero,
        'win_rate': _ratio(len(wins), len(values)), 'average_win_r': _mean(wins),
        'average_loss_r': _mean(losses), 'mean_r': _mean(values),
        'median_r': _percentile(values, D('.5')), 'profit_factor': pf,
        'profit_factor_status': 'AVAILABLE' if losses else ('NO_LOSSES' if wins else 'UNDEFINED'),
        'sum_positive_r': sum(wins, D(0)), 'sum_negative_r': sum(losses, D(0)),
        'event_order_max_drawdown_r': drawdown if values else None,
        'longest_losing_streak': max_streak if values else None,
        'positive_months': sum(value > 0 for value in nonempty_months.values()),
        'negative_months': sum(value < 0 for value in nonempty_months.values()),
        'zero_months': sum(value == 0 for value in nonempty_months.values()),
        'empty_months': len(month_keys) - len(nonempty_months),
        'worst_month': min(nonempty_months, key=nonempty_months.get) if nonempty_months else None,
        'worst_month_mean_r': min(nonempty_months.values()) if nonempty_months else None,
        'lomo_minimum_mean_r': min(lomo) if lomo else None,
        'numeric_status': 'AVAILABLE' if values else 'NO_EXECUTABLE_OUTCOMES',
        'average_win_status': 'AVAILABLE' if wins else 'NO_WINS',
        'average_loss_status': 'AVAILABLE' if losses else 'NO_LOSSES',
    }
    if result['eligible_entries'] != result['executable_outcomes'] + result['unavailable_outcomes']:
        raise ValueError('eligible denominator mismatch')
    if result['executable_outcomes'] != result['wins'] + result['losses'] + result['zero_r_outcomes']:
        raise ValueError('classification denominator mismatch')
    return result


class _Bootstrap:
    """Identical frozen session draws; exact integer dot products, Decimal ratios.

    Decimal session aggregates are converted losslessly to common-scale integers.
    This only accelerates resampling; no floating point values enter calculations.
    Costs share the sampled risk reciprocals and sensitivities share session draws.
    """

    def __init__(self, session_dates):
        import numpy as np
        self.np = np
        self.sessions = tuple(session_dates)
        self.index = {value: index for index, value in enumerate(self.sessions)}
        rng = random.Random(PROTOCOL['bootstrap_seed'])
        frequencies = []
        for _ in range(PROTOCOL['bootstrap_draws']):
            counts = [0] * len(self.sessions)
            for _ in self.sessions:
                counts[rng.randrange(len(self.sessions))] += 1
            frequencies.append(counts)
        self.frequencies = np.array(frequencies, dtype=np.int64)
        self.cache = {}

    @staticmethod
    def _integer(value, exponent):
        sign, digits, value_exponent = value.as_tuple()
        coefficient = 0
        for digit in digits:
            coefficient = coefficient * 10 + digit
        return (-coefficient if sign else coefficient) * (10 ** (value_exponent - exponent))

    def calculate(self, rows, paired=False):
        # Paired rows contain per-identity low/high differences and reciprocal-risk
        # differences; the mean therefore remains an exact common-identity mean.
        records = []
        for row in rows:
            if paired:
                records.append((row['session_date'], row['low_difference'], row['high_difference'], row['inverse_risk_difference']))
            elif row['_usable']:
                records.append((row['session_date'], row['low_r'], row['high_r'], row['_inverse_risk']))
        aggregates = [[D(0), D(0), D(0), 0] for _ in self.sessions]
        for session, low, high, inverse_risk in records:
            aggregate = aggregates[self.index[session]]
            aggregate[0] += low
            aggregate[1] += high
            aggregate[2] += inverse_risk
            aggregate[3] += 1
        cache_key = tuple(tuple(value for value in aggregate) for aggregate in aggregates)
        if cache_key in self.cache:
            return self.cache[cache_key]
        exponent = min(value.as_tuple().exponent for aggregate in aggregates for value in aggregate[:3])
        integer_data = self.np.array([
            [self._integer(value, exponent) for value in aggregate[:3]] + [aggregate[3]]
            for aggregate in aggregates
        ], dtype=object)
        sampled = self.frequencies @ integer_data
        scale = D(10) ** exponent
        distributions = {(sensitivity, cost): [] for sensitivity in SENSITIVITIES for cost in COSTS}
        null_draws = 0
        for low, high, inverse_risk, count in sampled:
            if not count:
                null_draws += 1
                continue
            for sensitivity, total in (('stop_first', low), ('target_first', high)):
                for cost in COSTS:
                    # Use exact integer cents to avoid loss before cancellation.
                    cents = int(cost * D(100))
                    numerator = (int(total) * 100 - int(inverse_risk) * cents)
                    distributions[(sensitivity, cost)].append(D(numerator) * scale / D(int(count) * 100))
        results = {}
        for key, distribution in distributions.items():
            results[key] = {
                'bootstrap_draws': PROTOCOL['bootstrap_draws'],
                'bootstrap_seed': PROTOCOL['bootstrap_seed'],
                'bootstrap_valid_draws': len(distribution),
                'bootstrap_null_draws': null_draws,
                'mean_r_ci_low': _percentile(distribution, D('.025')),
                'mean_r_ci_high': _percentile(distribution, D('.975')),
                'bootstrap_probability_mean_above_zero': _ratio(sum(value > 0 for value in distribution), len(distribution)),
                'bootstrap_status': 'AVAILABLE' if distribution else 'NO_NON_NULL_DRAWS',
                'bootstrap_unit': 'WHOLE_SESSION',
            }
        self.cache[cache_key] = results
        return results


def _base(entry, model, cost, sensitivity, population='NATURAL'):
    return {'entry_variant': entry, 'model': model, 'population': population,
            'cost_per_share_roundtrip': cost, 'ambiguity_sensitivity': sensitivity}


def _paired_records(left, right):
    left_map = {row['_identity']: row for row in left}
    right_map = {row['_identity']: row for row in right}
    common = set(left_map) & set(right_map)
    usable = sorted(identity for identity in common if left_map[identity]['_usable'] and right_map[identity]['_usable'])
    records = []
    for identity in usable:
        primary, control = left_map[identity], right_map[identity]
        records.append({'interaction_id': identity[0], 'session_date': identity[1],
                        'low_difference': primary['low_r'] - control['low_r'],
                        'high_difference': primary['high_r'] - control['high_r'],
                        'inverse_risk_difference': primary['_inverse_risk'] - control['_inverse_risk'],
                        'left': primary, 'right': control})
    return records, {
        'left_eligible_entries': len(left), 'right_eligible_entries': len(right),
        'left_missing_partner': len(set(left_map) - set(right_map)),
        'right_missing_partner': len(set(right_map) - set(left_map)),
        'common_eligible_identities': len(common), 'common_usable_identities': len(usable),
        'common_unavailable_attrition': len(common) - len(usable),
        'left_common_atr_unavailable': sum(left_map[key]['status'] == 'UNAVAILABLE_ATR' for key in common),
        'right_common_atr_unavailable': sum(right_map[key]['status'] == 'UNAVAILABLE_ATR' for key in common),
        'common_contributing_sessions': len({identity[1] for identity in usable}),
    }


def build_reports(rows, session_dates, outdir):
    """Write the frozen descriptive reporting matrix; no data loading/simulation."""
    with localcontext() as context:
        context.prec = 80
        context.rounding = ROUND_HALF_EVEN
        return _build_reports(rows, session_dates, Path(outdir))


def _build_reports(rows, session_dates, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    sessions = tuple(sorted(str(value) for value in session_dates))
    if len(set(sessions)) != len(sessions) or len(sessions) != 170:
        raise ValueError('frozen full 170-session calendar required')
    if sessions[0] != '2026-01-02' or sessions[-1] != '2026-09-04':
        raise ValueError('frozen calendar boundary mismatch')
    prepared = [_prepare(row) for row in rows]
    groups = defaultdict(list)
    identities = set()
    for row in prepared:
        key = (row['entry_variant'], row['model'], row['_identity'])
        if key in identities:
            raise ValueError('duplicate outcome identity')
        identities.add(key)
        if row['entry_variant'] not in ENTRIES or row['model'] not in MODELS or row['session_date'] not in sessions:
            raise ValueError('outcome outside frozen universe')
        groups[(row['entry_variant'], row['model'])].append(row)
    if set(groups) != {(entry, model) for entry in ENTRIES for model in MODELS}:
        raise ValueError('expected exactly 32 populated model-entry combinations')
    for entry in ENTRIES:
        baseline = {row['_identity'] for row in groups[(entry, MODELS[0])]}
        if any({row['_identity'] for row in groups[(entry, model)]} != baseline for model in MODELS):
            raise ValueError('model-dependent eligible population')
    bootstrap = _Bootstrap(sessions)
    inventory = []
    all_metrics, bootstrap_rows, month_rows, session_rows, lomo_rows = [], [], [], [], []
    direction_rows, context_rows, reconciliations = [], [], []
    month_keys = sorted({session[:7] for session in sessions})
    natural_lookup = {}
    for entry in ENTRIES:
        for model in MODELS:
            group = groups[(entry, model)]
            print(f'Reporting natural {entry} {model}', flush=True)
            uncertainty = bootstrap.calculate(group)
            context_groups = defaultdict(list)
            for row in group:
                for field, value in row.get('context', {}).items():
                    context_groups[(field, 'UNKNOWN' if value is None else str(value))].append(row)
            for cost in COSTS:
                for sensitivity in SENSITIVITIES:
                    base = _base(entry, model, cost, sensitivity)
                    metrics = _metrics(group, cost, sensitivity, sessions)
                    record = base | metrics | uncertainty[(sensitivity, cost)]
                    all_metrics.append(record)
                    natural_lookup[(entry, model, cost, sensitivity)] = record
                    bootstrap_rows.append(base | uncertainty[(sensitivity, cost)])
                    reconciliations.append({key: record[key] for key in (
                        'entry_variant', 'model', 'cost_per_share_roundtrip', 'ambiguity_sensitivity',
                        'eligible_entries', 'executable_outcomes', 'unavailable_outcomes',
                        'ambiguous_outcomes', 'wins', 'losses', 'zero_r_outcomes')})
                    for direction in ('LONG', 'SHORT'):
                        subset = [row for row in group if row['direction'] == direction]
                        direction_rows.append(base | {'direction': direction} | _metrics(subset, cost, sensitivity, sessions))
                    for month in month_keys:
                        subset = [row for row in group if row['session_date'].startswith(month)]
                        month_sessions = [session for session in sessions if session.startswith(month)]
                        month_rows.append(base | {'month': month, 'partial_month': month == '2026-09'} | _metrics(subset, cost, sensitivity, month_sessions))
                        retained = [row for row in group if not row['session_date'].startswith(month)]
                        retained_sessions = [session for session in sessions if not session.startswith(month)]
                        lomo_rows.append(base | {'omitted_month': month} | _metrics(retained, cost, sensitivity, retained_sessions))
                    per_session = defaultdict(list)
                    for row in group:
                        per_session[row['session_date']].append(row)
                    for session in sessions:
                        subset = per_session[session]
                        values = [_value(row, cost, sensitivity) for row in subset if row['_usable']]
                        session_rows.append(base | {'session_date': session, 'eligible_entries': len(subset),
                            'executable_outcomes': len(values), 'unavailable_outcomes': len(subset) - len(values),
                            'mean_r': _mean(values), 'sum_r': sum(values, D(0)),
                            'wins': sum(value > 0 for value in values), 'losses': sum(value < 0 for value in values),
                            'zero_r_outcomes': sum(value == 0 for value in values),
                            'status': 'AVAILABLE' if values else 'NO_EXECUTABLE_OUTCOMES'})
                    for (field, value), subset in sorted(context_groups.items()):
                        context_rows.append(base | {'context_field': field, 'context_value': value,
                            'evidence_label': 'SPARSE_INSUFFICIENT' if value in ('PMH', 'PML') else 'DESCRIPTIVE_ONLY'}
                            | _metrics(subset, cost, sensitivity, sessions))
    inventory.append(_write_csv(outdir, 'model_results_32.csv', [row for row in all_metrics if row['cost_per_share_roundtrip'] == 0 and row['ambiguity_sensitivity'] == 'stop_first']))
    inventory.append(_write_csv(outdir, 'cost_sensitivity.csv', all_metrics))
    inventory.append(_write_csv(outdir, 'ambiguity_sensitivity.csv', all_metrics))
    inventory.append(_write_csv(outdir, 'direction_results.csv', direction_rows))
    inventory.append(_write_csv(outdir, 'monthly_results.csv', month_rows))
    inventory.append(_write_csv(outdir, 'session_results.csv', session_rows))
    inventory.append(_write_csv(outdir, 'leave_one_month_out.csv', lomo_rows))
    inventory.append(_write_csv(outdir, 'context_tables.csv', context_rows))
    inventory.append(_write_json(outdir, 'denominator_reconciliation.json', {
        'eligible_identity_population_invariant_across_models': True,
        'eligible_equals_executable_plus_unavailable': True,
        'executable_equals_wins_plus_losses_plus_zero': True,
        'ambiguity_is_subset_of_executable': True,
        'full_calendar_sessions': len(sessions), 'combinations': len(groups), 'rows': reconciliations}))

    availability_rows, common_rows, common_comparisons = [], [], []
    for entry in ENTRIES:
        atr_base = groups[(entry, 'ATR050_TARGET_1R')]
        availability_groups = [('TOTAL', 'ALL', atr_base)]
        availability_groups += [('MONTH', month, [row for row in atr_base if row['session_date'].startswith(month)]) for month in month_keys]
        availability_groups += [('DIRECTION', direction, [row for row in atr_base if row['direction'] == direction]) for direction in ('LONG', 'SHORT')]
        for field, value, subset in availability_groups:
            usable = [row for row in subset if row['_usable']]
            availability_rows.append({'entry_variant': entry, 'group': field, 'value': value,
                'eligible_entries': len(subset), 'atr_available_outcomes': len(usable),
                'atr_unavailable': sum(row['status'] == 'UNAVAILABLE_ATR' for row in subset),
                'other_unavailable': sum(not row['_usable'] and row['status'] != 'UNAVAILABLE_ATR' for row in subset),
                'eligible_sessions': len({row['session_date'] for row in subset}),
                'contributing_sessions': len({row['session_date'] for row in usable}),
                'availability_rate': _ratio(len(usable), len(subset))})
        for exit_name in EXITS:
            atr_model = 'ATR050_' + exit_name
            atr_group = groups[(entry, atr_model)]
            atr_ids = {row['_identity'] for row in atr_group if row['_usable']}
            matching_models = [model for model in MODELS if model.split('_', 1)[1] == exit_name]
            # Exact intersection also carries fixed-model path unavailability explicitly.
            for model in matching_models:
                subset = [row for row in groups[(entry, model)] if row['_identity'] in atr_ids]
                uncertainty = bootstrap.calculate(subset)
                for cost in COSTS:
                    for sensitivity in SENSITIVITIES:
                        base = _base(entry, model, cost, sensitivity, 'COMMON_AVAILABLE_ATR_IDENTITIES')
                        record = base | {'atr_reference_model': atr_model} | _metrics(subset, cost, sensitivity, sessions) | uncertainty[(sensitivity, cost)]
                        common_rows.append(record)
                        bootstrap_rows.append(base | uncertainty[(sensitivity, cost)])
                if model == atr_model:
                    continue
                paired, attrition = _paired_records(subset, [row for row in atr_group if row['_identity'] in atr_ids])
                uncertainty = bootstrap.calculate(paired, paired=True)
                for cost in COSTS:
                    for sensitivity in SENSITIVITIES:
                        differences = [_value(row['left'], cost, sensitivity) - _value(row['right'], cost, sensitivity) for row in paired]
                        common_comparisons.append(_base(entry, model, cost, sensitivity, 'COMMON_AVAILABLE_ATR_IDENTITIES')
                            | {'atr_reference_model': atr_model, 'comparison': 'FIXED_MINUS_ATR', 'paired_mean_r_difference': _mean(differences)}
                            | attrition | uncertainty[(sensitivity, cost)])
    inventory.append(_write_csv(outdir, 'atr_availability.csv', availability_rows))
    inventory.append(_write_csv(outdir, 'common_atr_population_results.csv', common_rows))
    inventory.append(_write_csv(outdir, 'common_atr_comparisons.csv', common_comparisons))

    paired_rows = []
    for model in MODELS:
        print(f'Reporting paired primary/control {model}', flush=True)
        primary = groups[(ENTRIES[0], model)]
        control = groups[(ENTRIES[1], model)]
        paired, attrition = _paired_records(primary, control)
        uncertainty = bootstrap.calculate(paired, paired=True)
        for cost in COSTS:
            for sensitivity in SENSITIVITIES:
                left = [row['left'] for row in paired]
                right = [row['right'] for row in paired]
                differences = [_value(row['left'], cost, sensitivity) - _value(row['right'], cost, sensitivity) for row in paired]
                left_metrics = _metrics(left, cost, sensitivity, sessions)
                right_metrics = _metrics(right, cost, sensitivity, sessions)
                record = {'model': model, 'cost_per_share_roundtrip': cost, 'ambiguity_sensitivity': sensitivity,
                    'comparison': 'IMMEDIATE_MINUS_MOMENTUM',
                    'natural_primary_mean_r': natural_lookup[(ENTRIES[0], model, cost, sensitivity)]['mean_r'],
                    'natural_control_mean_r': natural_lookup[(ENTRIES[1], model, cost, sensitivity)]['mean_r'],
                    'common_primary_mean_r': left_metrics['mean_r'], 'common_control_mean_r': right_metrics['mean_r'],
                    'paired_mean_r_difference': _mean(differences),
                    'population_warning': 'COMMON_CONTROL_AVAILABILITY_IS_LATER_INFORMATION_NOT_A_PRIMARY_ENTRY_FILTER'}
                record |= {f'common_primary_{key}': value for key, value in left_metrics.items()}
                record |= {f'common_control_{key}': value for key, value in right_metrics.items()}
                paired_rows.append(record | attrition | uncertainty[(sensitivity, cost)])
                bootstrap_rows.append({'entry_variant': 'IMMEDIATE_MINUS_MOMENTUM', 'model': model,
                    'population': 'COMMON_USABLE_IDENTITIES', 'cost_per_share_roundtrip': cost,
                    'ambiguity_sensitivity': sensitivity} | uncertainty[(sensitivity, cost)])
    inventory.append(_write_csv(outdir, 'immediate_momentum_comparisons.csv', paired_rows))
    inventory.append(_write_csv(outdir, 'bootstrap_results.csv', bootstrap_rows))

    be_rows = []
    for entry in ENTRIES:
        for stop in ('USD025', 'USD030', 'USD040', 'ATR050'):
            for cost in COSTS:
                for sensitivity in SENSITIVITIES:
                    original = natural_lookup[(entry, stop + '_TARGET_2R', cost, sensitivity)]
                    managed = natural_lookup[(entry, stop + '_TARGET_2R_BE1R', cost, sensitivity)]
                    be_rows.append(_base(entry, stop + '_TARGET_2R_BE1R', cost, sensitivity) | {
                        'reference_model': stop + '_TARGET_2R', 'reference_mean_r': original['mean_r'],
                        'be_mean_r': managed['mean_r'],
                        'be_minus_unmanaged_mean_r': managed['mean_r'] - original['mean_r'] if managed['mean_r'] is not None and original['mean_r'] is not None else None,
                        'reference_win_rate': original['win_rate'], 'be_win_rate': managed['win_rate'],
                        'reference_drawdown_r': original['event_order_max_drawdown_r'], 'be_drawdown_r': managed['event_order_max_drawdown_r'],
                        'reference_zero_r_outcomes': original['zero_r_outcomes'], 'be_zero_r_outcomes': managed['zero_r_outcomes'],
                        'eligible_identity_set_equal': True})
    inventory.append(_write_csv(outdir, 'breakeven_comparisons.csv', be_rows))
    inventory.append(_write_json(outdir, 'reporting_receipt.json', {
        'decimal_precision': 80, 'decimal_rounding': 'ROUND_HALF_EVEN',
        'bootstrap_draws': 10000, 'bootstrap_seed': 20260908, 'calendar_sessions': 170,
        'bootstrap_percentile_method': 'Decimal linear interpolation at .025 and .975',
        'bootstrap_population': 'Full session calendar with zero-event sessions retained',
        'bootstrap_acceleration': 'Lossless Decimal session aggregates to integer matrix; no floating point arithmetic',
        'cost_disclaimer': 'SPY-equivalent underlying roundtrip research scenarios; not actual 0DTE option execution costs',
        'drawdown_disclaimer': 'Cumulative event-order research diagnostic; not account-equity simulation',
        'interval_disclaimer': 'Pointwise descriptive intervals; unadjusted for selection among frozen models',
        'no_model_selection': True,
        'inventory': inventory}))
    return inventory
