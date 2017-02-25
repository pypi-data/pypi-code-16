# -*- coding: utf-8 -*-
"""

Author
------
Bo Zhang

Email
-----
bozhang@nao.cas.cn

Created on
----------
- Wed Jan  18 13:00:00 2017

Modifications
-------------
-

Aims
----
- the configuration class of twodspec

"""

DC_BIAS = dict(

)

DEFAULT_BACKGROUND = dict(
    # the extrapolation method, {median, average, percentile
    method='median',
    # the smoothing filter adopted {median, gaussian, box}
    smooth_filter='median',
    )

DEFAULT_EXTRACT = dict(
    # the extraction strategy {simple, optimal}
    method='simple',
)


class Config(object):
    background = {''}
    combine = {''}
    extract = {''}

    def __init__(self):
        pass

    def __repr__(self):
        pass


def test():
    cfg = Config()
    cfg.pprint()


if __name__ == "__main__":
    test()