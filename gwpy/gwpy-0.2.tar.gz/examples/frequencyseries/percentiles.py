#!/usr/bin/env python

# Copyright (C) Duncan Macleod (2016)
#
# This file is part of GWpy.
#
# GWpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWpy.  If not, see <http://www.gnu.org/licenses/>.

"""Plot a `FrequencySeries` with percentiles

While the Amplitude Spectral Density `FrequencySeries` is the standard
measure of interferometer sensitivity in the frequency-domain, it tells
nothing of the time-domain stability of that ASD.

One easy way to display that is to use a `~gwpy.spectrogram.Spectrogram`
to estimate an ASD every minute, then calculate percentiles of that to
esimate the variability.
"""

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'
__currentmodule__ = 'gwpy.timeseries'

# To demonstrate, we can download some strain data from the LIGO-Hanford
# instrument around the
# `GW150914 <www.ligo.org/science/Publication-GW150914/>`_ event:

from gwpy.timeseries import TimeSeries
data = TimeSeries.fetch_open_data('H1', 1135136228, 1135140324)

# Next we can make an ASD `~TimeSeries.spectrogram` with an ASD calculated
# for each minute of data:

ampgram = data.spectrogram(60, 4, 2) ** (1/2.)

# .. note::
#
#    The `TimeSeries.spectrogram` method by default returns a Power Spectral
#    Density `~gwpy.spectrogram.Spectrogram`, so we use the ``** (1/2.)``
#    operation to convert that to an ASD spectrogram.

# The `~gwpy.spectrogram.Spectrogram.percentile` method allows us to extract
# the median ASD, and two extremes:

a = ampgram.percentile(50)
b = ampgram.percentile(5)
c = ampgram.percentile(95)

# Finally, we can create a `~gwpy.plotter.FrequencySeriesPlot` object and
# use the `~gwpy.plotter.FrequencySeriesAxes.plot_frequencyseries_mmm` to
# display the three spectra as a 'median-min-max` trio:

from gwpy.plotter import FrequencySeriesPlot
plot = FrequencySeriesPlot()
ax = plot.gca()
ax.plot_frequencyseries_mmm(a, b, c, color='#ee0000')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim(10, 1500)
ax.set_ylim(5e-24,5e-21)
ax.set_title('LIGO-Hanford amplitude sensitivity around GW150914')
plot.show()

# The result is the median spectrogram ``a`` shown as a solid curve, with
# the 5th and 9th percentiles (``b`` and ``c``) shown as a shaded region
# around the median.
