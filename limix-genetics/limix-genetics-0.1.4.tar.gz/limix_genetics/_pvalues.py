from __future__ import division, absolute_import

import numpy as np
import colour
from limix_plot import cycler_ as cycler
from collections import OrderedDict

def _expected(n):
    lnpv = np.linspace(1/(n+1), n/(n+1), n, endpoint=True)
    return np.flipud(-np.log10(lnpv))

def _xy(self, label):
    lpv = -np.log10(self._pv[label])
    lpv.sort()

    return (_expected(len(lpv)), lpv)

(lnpv, lpv) = self._xy(label)
        n = int(len(lnpv) * plot_top/100)

# axes.plot(lnpv[-n:], lpv[-n:], 'o', markeredgecolor=ec,
#                   clip_on=False, zorder=100, **rest)
