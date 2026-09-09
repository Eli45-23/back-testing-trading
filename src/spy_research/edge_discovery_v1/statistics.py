"""Frozen cluster bootstrap and nominal BY diagnostics; synthetic use in Phase 1."""
from decimal import Decimal
import numpy as np


def by_adjusted(pvalues):
    p = [float(x) for x in pvalues]
    if any(not np.isfinite(x) or not 0 <= x <= 1 for x in p): raise ValueError('invalid p value')
    n = len(p)
    if not n: return ()
    order = sorted(range(n), key=lambda i:p[i]); harmonic = sum(1/i for i in range(1,n+1))
    result = [0.0]*n; minimum = 1.0
    for rank in range(n,0,-1):
        i = order[rank-1]; minimum = min(minimum,p[i]*n*harmonic/rank); result[i]=minimum
    return tuple(result)


class SessionBootstrap:
    def __init__(self, sessions):
        if not sessions or list(sessions) != sorted(set(sessions)): raise ValueError('complete ordered unique calendar required')
        self.sessions = tuple(sessions)
        n = len(sessions)
        self.weights = np.random.default_rng(20260909).multinomial(n, np.full(n,1/n),size=10000)

    def interval(self, observations):
        # Numerical resampling uses floats; execution and accounting use Decimal.
        sums = np.zeros(len(self.sessions)); counts = np.zeros(len(self.sessions)); lookup = {d:i for i,d in enumerate(self.sessions)}
        for day,value in observations:
            if day not in lookup or not isinstance(value,Decimal) or not value.is_finite(): raise ValueError('invalid cluster observation')
            sums[lookup[day]] += float(value); counts[lookup[day]] += 1
        denominators = self.weights @ counts
        estimates = (self.weights @ sums)[denominators>0] / denominators[denominators>0]
        if not len(estimates): return {'status':'INSUFFICIENT','valid_draws':0}
        regular = np.quantile(estimates,[.025,.975]); adjusted = np.quantile(estimates,[.05/6,1-.05/6])
        return {'status':'AVAILABLE','valid_draws':len(estimates),'mean':str(float(sums.sum()/counts.sum())),'ci95':list(map(str,regular)),'bonferroni3':list(map(str,adjusted))}

    def paired(self, left, right):
        # key -> (session, outcome); callers must explicitly select common identities.
        if set(left) != set(right): raise ValueError('exact paired identities required')
        observations = []
        for key in sorted(left):
            a,b = left[key],right[key]
            if a[0] != b[0]: raise ValueError('paired session mismatch')
            observations.append((a[0],a[1]-b[1]))
        return self.interval(observations)
