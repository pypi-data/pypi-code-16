#!/usr/bin/env python

#-------------
# Load modules
#-------------
import os
import sys
import numpy as np
import matplotlib.pyplot as plt            # pyplot module import
import matplotlib.cm as cm
import datetime as dt


# Determine the location (absolute path) of this script
curDir = os.path.dirname(os.path.abspath(__file__))
modDir = curDir+'/../io'
sys.path.append(modDir)

modDir = curDir+'/../viz'
sys.path.append(modDir)

modDir = curDir+'/../utils'
sys.path.append(modDir)

import mplibUtilities
import registerColormaps

hh = 12
nn = 0
ss = 0

timeSeries = [dt.date(2012, 04, 18), dt.date(2012, 04, 19), 
              dt.date(2012, 04, 20), dt.date(2012, 04, 21),
              dt.date(2012, 04, 22)]

#timeSeries = [2012-04-18, 2012-04-19, 2012-04-20, 2012-04-21, 2012-04-22]

Ydata1 = [0.0, 0.0001, 0.0009, 0.0020, 0.0032]
Ydata2 = [0.0, 0.0002, 0.0012, 0.0023, 0.0034]
Ydata3 = [0.0, 0.0004, 0.0027, 0.0067, 0.0086]

figName = 'RME_withTendencies'
title1 = 'RME for one tile'
title2 = 'RME for two identical tiles'
title3 = 'RME for three different tiles'

#mplibUtilities.single_timeSeies_plot(timeSeries, Ydata1, figName, figTitle = figTitle)
mplibUtilities.ts_multi_plots(timeSeries, figName, nColumns = 1, Yvars = (Ydata1, Ydata2, Ydata3), plotTitles = (title1, title2, title3))

