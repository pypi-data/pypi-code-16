# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2014-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
"""This module implements labels layout on graph axes."""

from __future__ import absolute_import, division, unicode_literals

__authors__ = ["T. Vincent"]
__license__ = "MIT"
__date__ = "18/10/2016"


import math


# utils #######################################################################

def numberOfDigits(tickSpacing):
    """Returns the number of digits to display for text label.

    :param float tickSpacing: Step between ticks in data space.
    :return: Number of digits to show for labels.
    :rtype: int
    """
    nfrac = int(-math.floor(math.log10(tickSpacing)))
    if nfrac < 0:
        nfrac = 0
    return nfrac


# Nice Numbers ################################################################

def _niceNum(value, isRound=False):
    expvalue = math.floor(math.log10(value))
    frac = value/pow(10., expvalue)
    if isRound:
        if frac < 1.5:
            nicefrac = 1.
        elif frac < 3.:
            nicefrac = 2.
        elif frac < 7.:
            nicefrac = 5.
        else:
            nicefrac = 10.
    else:
        if frac <= 1.:
            nicefrac = 1.
        elif frac <= 2.:
            nicefrac = 2.
        elif frac <= 5.:
            nicefrac = 5.
        else:
            nicefrac = 10.
    return nicefrac * pow(10., expvalue)


def niceNumbers(vMin, vMax, nTicks=5):
    """Returns tick positions.

    This function implements graph labels layout using nice numbers
    by Paul Heckbert from "Graphics Gems", Academic Press, 1990.
    See `C code <http://tog.acm.org/resources/GraphicsGems/gems/Label.c>`_.

    :param float vMin: The min value on the axis
    :param float vMax: The max value on the axis
    :param int nTicks: The number of ticks to position
    :returns: min, max, increment value of tick positions and
              number of fractional digit to show
    :rtype: tuple
    """
    vrange = _niceNum(vMax - vMin, False)
    spacing = _niceNum(vrange / nTicks, True)
    graphmin = math.floor(vMin / spacing) * spacing
    graphmax = math.ceil(vMax / spacing) * spacing
    nfrac = numberOfDigits(spacing)
    return graphmin, graphmax, spacing, nfrac


def _frange(start, stop, step):
    """range for float (including stop)."""
    assert step >= 0.
    while start <= stop:
        yield start
        start += step


def ticks(vMin, vMax, nbTicks=5):
    """Returns tick positions and labels using nice numbers algorithm.

    This enforces ticks to be within [vMin, vMax] range.
    It returns at least 2 ticks.

    :param float vMin: The min value on the axis
    :param float vMax: The max value on the axis
    :param int nbTicks: The number of ticks to position
    :returns: tick positions and corresponding text labels
    :rtype: 2-tuple: list of float, list of string
    """
    start, end, step, nfrac = niceNumbers(vMin, vMax, nbTicks)
    positions = [t for t in _frange(start, end, step) if vMin <= t <= vMax]

    # Makes sure there is at least 2 ticks
    if len(positions) < 2:
        positions = [vMin, vMax]
        nfrac = numberOfDigits(vMax - vMin)

    # Generate labels
    format_ = '%g' if nfrac == 0 else '%.{}f'.format(nfrac)
    labels = [format_ % tick for tick in positions]
    return positions, labels


def niceNumbersAdaptative(vMin, vMax, axisLength, tickDensity):
    """Returns tick positions using :func:`niceNumbers` and a
    density of ticks.

    axisLength and tickDensity are based on the same unit (e.g., pixel).

    :param float vMin: The min value on the axis
    :param float vMax: The max value on the axis
    :param float axisLength: The length of the axis.
    :param float tickDensity: The density of ticks along the axis.
    :returns: min, max, increment value of tick positions and
              number of fractional digit to show
    :rtype: tuple
    """
    # At least 2 ticks
    nticks = max(2, int(round(tickDensity * axisLength)))
    tickmin, tickmax, step, nfrac = niceNumbers(vMin, vMax, nticks)

    return tickmin, tickmax, step, nfrac


# Nice Numbers for log scale ##################################################

def niceNumbersForLog10(minLog, maxLog, nTicks=5):
    """Return tick positions for logarithmic scale

    :param float minLog: log10 of the min value on the axis
    :param float maxLog: log10 of the max value on the axis
    :param int nTicks: The number of ticks to position
    :returns: log10 of min, max and increment value of tick positions
    :rtype: tuple of int
    """
    graphminlog = math.floor(minLog)
    graphmaxlog = math.ceil(maxLog)
    rangelog = graphmaxlog - graphminlog

    if rangelog <= nTicks:
        spacing = 1.
    else:
        spacing = math.floor(rangelog / nTicks)

        graphminlog = math.floor(graphminlog / spacing) * spacing
        graphmaxlog = math.ceil(graphmaxlog / spacing) * spacing

    return int(graphminlog), int(graphmaxlog), int(spacing)
