from numpy import array
from numpy.random import RandomState
from numpy.testing import assert_allclose

from limix_genetics import maf

def test_maf():
    random = RandomState(0)
    G = random.randint(0, 3, (50, 30))
    assert_allclose(maf(G), array([ 0.49,  0.48,  0.46,  0.49,  0.47,  0.48,  0.46,  0.42,  0.44,
        0.43,  0.46,  0.38,  0.46,  0.47,  0.48,  0.37,  0.5 ,  0.4 ,
        0.47,  0.49,  0.48,  0.44,  0.5 ,  0.44,  0.47,  0.49,  0.45,
        0.37,  0.45,  0.47]))

if __name__ == '__main__':
    test_maf()
