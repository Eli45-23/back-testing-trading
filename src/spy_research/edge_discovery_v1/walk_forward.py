"""Fixed expanding calendar folds; no fitting against evaluation outcomes."""
from datetime import date

FOLDS = (
    ('Q2',date(2024,1,2),date(2024,3,31),date(2024,4,1),date(2024,6,30)),
    ('Q3',date(2024,1,2),date(2024,6,30),date(2024,7,1),date(2024,9,30)),
    ('Q4',date(2024,1,2),date(2024,9,30),date(2024,10,1),date(2024,12,31)),
)


def training_rows(rows, fold):
    _,start,end,_,_ = fold
    return tuple(r for r in rows if start <= r['observation_date'] <= end and r['label_end_date'] <= end)


def validate_threshold_fit(fit_dates, fold):
    _,start,end,_,_ = fold
    if not fit_dates or any(not start <= d <= end for d in fit_dates): raise ValueError('threshold fitting outside training prefix')
