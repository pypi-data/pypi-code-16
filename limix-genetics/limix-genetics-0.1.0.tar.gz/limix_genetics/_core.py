from __future__ import division

from numpy import asarray, minimum

def maf(X):
    r"""Compute minor allele frequencies.

    It assumes that `X` encodes 0, 1, and 2 representing the number
    of alleles.

    Args:
        X (array_like): Genotype matrix.

    Returns:
        array_like: minor allele frequencies.
    """
    X = asarray(X, float)
    s0 = X.sum(0)
    s0 /= 2*X.shape[0]
    s1 = 1 - s0
    return minimum(s0, s1)

# import matplotlib.pyplot as plt
import pandas as pd
# import urllib.request
from numpy import arange

# def kinship_plot(K, row_labels=None, col_labels=None, ax=None, fig=None):
#     r"""Plots a heat map of given kinship matrix.
#
#     Args:
#         K (array_like): kinship matrix.
#         row_labels (array_like): row labels.
#         col_labels (array_like): column labels.
#         ax (:class:`matplotlib.axes.Axes`): axes.
#         fig (:class:`matplotlib.figure.Figure`): axes.
#
#     Returns:
#         tuple: containing `fig` and `ax`.
#     """
#
#     if row_labels is None:
#         row_labels = range(K.shape[0])
#
#     if col_labels is None:
#         col_labels = range(K.shape[1])
#
#     if ax is None:
#         if fig is None:
#             fig = plt.figure()
#             fig.set_size_inches(8, 11)
#         ax = fig.add_subplot(111)
#
#     heatmap = ax.imshow(K, cmap=plt.cm.Blues, alpha=0.8)
#
#
#     ax.set_frame_on(False)
#
#     ax.set_yticks(arange(K.shape[0]) + 0.5, minor=False)
#     ax.set_xticks(arange(K.shape[1]) + 0.5, minor=False)
#
#     ax.invert_yaxis()
#     ax.xaxis.tick_top()
#
#     ax.set_xticklabels(col_labels, minor=False, rotation=90)
#     ax.set_yticklabels(row_labels, minor=False)
#
#     ax.grid(False)
#
#     for t in ax.xaxis.get_major_ticks():
#         t.tick1On = False
#         t.tick2On = False
#     for t in ax.yaxis.get_major_ticks():
#         t.tick1On = False
#         t.tick2On = False
#
#     return fig, ax
