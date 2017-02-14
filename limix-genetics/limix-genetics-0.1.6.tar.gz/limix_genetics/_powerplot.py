from __future__ import division

import bokeh
import bokeh.plotting
from bokeh.models.sources import ColumnDataSource
from numba import jit
from numpy import (append, arange, argsort, empty, flipud, inf, linspace,
                   log10, logspace, partition, searchsorted, sort, asarray)
from scipy.special import betaincinv

from ._colors import get_colors
from ._config import set_figure_for_paper


def hitsplot(df,
             figure=None,
             colors=None,
             show=True,
             tools=None,
             min_threshold=1e-5,
             max_threshold=1e-2,
             paper_settings=False,
             perc=False,
             **kwargs):
    r"""Plot number of significant hits across p-value thresholds.

    Args:
        df (:class:`pandas.DataFrame`): Columns `label` and `p-value`
            define labeled curves.

    Example:

        .. bokeh-plot::

            from limix_genetics import hitsplot
            import pandas as pd
            import numpy as np
            random = np.random.RandomState(0)

            snp_ids = np.arange(1000)

            data1 = np.stack((['method1']*1000, random.rand(1000) * 0.1),
                             axis=1)
            df1 = pd.DataFrame(data1, columns=['label', 'p-value'],
                               index=snp_ids)

            data2 = np.stack((['method2']*1000, random.rand(1000) * 0.05),
                             axis=1)
            df2 = pd.DataFrame(data2, columns=['label', 'p-value'],
                               index=snp_ids)

            df = pd.concat([df1, df2])

            hitsplot(df)
    """

    if tools is None:
        tools = ['save']

    if figure is None:
        figure = bokeh.plotting.figure(
            title='hitsplot',
            tools=tools,
            x_axis_label="p-value threshold",
            y_axis_label="number of hits",
            **kwargs)

    x = linspace(min_threshold, max_threshold, 100)


    labels = df['label'].unique()
    p_values = {m: df[df['label'] == m]['p-value'].astype(float).values
                for m in labels}
    nhits = {m: empty(len(x), int) for m in labels}

    for l in labels:
        _get_nhits(sort(p_values[l]), nhits[l], x)

    ntests = df.groupby('label').count().to_dict()['p-value']

    if perc:
        for l in labels:
            nhits[l] = asarray(nhits[l], float)
            nhits[l] /= ntests[l]
            nhits[l] *= 100
        figure.yaxis.axis_label = "percentage of hits"

    colors = get_colors(colors, labels)
    for l in labels:
        figure.line(x, nhits[l], legend=l, color=colors[l])

    figure.legend.location = "bottom_right"

    if paper_settings:
        set_figure_for_paper(figure)

    if show:
        bokeh.plotting.show(figure)

    return figure


@jit('void(float64[:], int64[:], float64[:])', nopython=True, nogil=True)
def _get_nhits(p_values, nhits, thresholds):
    j = 0
    nhits[0] = 0
    for i in range(len(thresholds)):
        while j < len(p_values) and p_values[j] <= thresholds[i]:
            nhits[i] += 1
            j += 1
        if i + 1 < len(thresholds):
            nhits[i + 1] = nhits[i]
