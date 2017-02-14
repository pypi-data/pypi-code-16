from limix_genetics import mvn_ecdf, mvn_eicdf

from numpy.testing import assert_allclose

def test_mvnorm():
    x = [1, 2]
    mean = [1.0, -0.3]
    cov = [[1.5, 0.2],
           [0.2, 0.7]]

    cdf = mvn_ecdf(x, mean, cov)
    icdf = mvn_eicdf(cdf, mean, cov)

    assert_allclose(cdf, 0.98032128770733662)
    assert_allclose(cdf, mvn_ecdf(icdf, mean, cov))
