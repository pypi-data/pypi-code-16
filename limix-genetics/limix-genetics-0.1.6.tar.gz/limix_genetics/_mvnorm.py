from numpy.linalg import eigvalsh
from numpy import ascontiguousarray
from numpy import sqrt
from numpy import ones
from numpy import dot
from scipy.stats import chi2
from numpy_sugar.linalg import solve

def mvn_ecdf(x, mean, cov):
    x = ascontiguousarray(x, float)
    radius = x - mean
    mean = ascontiguousarray(mean, float)
    cov = ascontiguousarray(cov, float)

    r2 = dot(radius, solve(cov, radius))
    ndim = cov.shape[0]
    return chi2.cdf(r2, df=ndim)

def mvn_eicdf(q, mean, cov):
    mean = ascontiguousarray(mean, float)
    cov = ascontiguousarray(cov, float)

    ndim = cov.shape[0]
    r2 = chi2.isf(1-q, df=ndim)

    p = eigvalsh(cov)

    d = sqrt(r2 / dot(p, solve(cov, p)))

    return d * p + mean
