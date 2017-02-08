from __future__ import division

import bokeh
import bokeh.plotting
from bokeh.models.sources import ColumnDataSource
from numpy import (append, arange, argsort, flipud, inf, linspace, log10,
                   logspace, partition, searchsorted)
from scipy.special import betaincinv


def qqplot(df,
           figure=None,
           colors=None,
           show=True,
           tools=None,
           nmax_points=1000,
           atleast_points=0.01,
           significance_level=0.01, **kwargs):

    assert nmax_points > 1

    if tools is None:
        tools = []

    if figure is None:
        figure = bokeh.plotting.figure(
            tools=tools,
            x_axis_label="theoretical -log10(p-value)",
            y_axis_label="observed -log10(p-value)",
            **kwargs)

    labels = _labels(df)
    colors = _colors(colors, labels)
    threshold = _threshold(labels, df["p-value"], nmax_points, atleast_points)

    npvals = inf

    for label in labels:
        dfi = df.loc[(label, ), :]

        pv = dfi['p-value'].values
        pv.sort()

        npvals = min(npvals, len(pv))

        lpv = -log10(flipud(pv))
        expected_lpv = _expected(len(lpv))

        i = searchsorted(pv, threshold)

        fill_alpha = 1.0
        figure.circle(
            expected_lpv[-i:],
            lpv[-i:],
            color=colors[label],
            fill_alpha=fill_alpha,
            line_width=0,
            line_color=None,
            legend=label)

    _plot_confidence_band(npvals, nmax_points, atleast_points, figure,
                          significance_level)

    figure.xaxis.axis_label_text_font_size = "24pt"
    figure.yaxis.axis_label_text_font_size = "24pt"
    figure.legend.label_text_font_size = "22pt"
    figure.xaxis.major_label_text_font_size = "18pt"
    figure.yaxis.major_label_text_font_size = "18pt"

    if show:
        bokeh.plotting.show(figure)

    return figure


def _expected(n):
    lnpv = linspace(1 / (n + 1), n / (n + 1), n, endpoint=True)
    return flipud(-log10(lnpv))


def _rank_confidence_band(nranks, nmax_points, atleast_points,
                          significance_level):
    alpha = significance_level

    if nmax_points > nranks - 1:
        k0 = arange(1, nranks + 1)
    else:
        npoints = max(nmax_points, int(atleast_points * (nranks + 1)))
        k0 = linspace(1, nranks + 1, nmax_points, dtype=int)

    k1 = flipud(k0).copy()

    top = betaincinv(k0, k1, 1 - alpha)
    mean = k0 / (nranks + 1)
    bottom = betaincinv(k0, k1, alpha)

    return (bottom, mean, top)


def _labels(df):
    level = df.index.names.index('label')
    assert level == 0
    return list(df.index.get_level_values(level).unique())


def _colors(colors, labels):
    if colors is None:
        colors = dict()
        from bokeh.palettes import brewer
        colors_iter = iter(brewer['Spectral'][11])
        for label in labels:
            colors[label] = next(colors_iter)
    return colors


def _threshold(labels, pvalues, nmax_points, atleast_points):
    thr = 1.0
    for label in labels:
        pv = pvalues.loc[(label, )].values
        pv.sort()
        if len(pv) > nmax_points:
            npoints = max(nmax_points, int(atleast_points * len(pv)))
            npoints = min(len(pv) - 1, npoints)
            thr = min(thr, (pv[npoints - 1] + pv[npoints]) / 2)
    return thr


def _plot_confidence_band(npvals, nmax_points, atleast_points, figure,
                          significance_level):

    (bo, me, to) = _rank_confidence_band(npvals, nmax_points, atleast_points,
                                         significance_level)

    bo = flipud(-log10(bo))
    me = flipud(-log10(me))
    to = flipud(-log10(to))

    figure.line([me[-1], me[0]], [me[-1], me[0]], color='black')
    figure.legend.location = 'top_left'

    band_x = append(me, me[::-1])
    band_y = append(bo, to[::-1])
    figure.patch(
        band_x,
        band_y,
        line_color='black',
        fill_color='black',
        fill_alpha=0.15,
        line_alpha=0.5)
