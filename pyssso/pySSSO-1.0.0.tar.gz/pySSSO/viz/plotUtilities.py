#!/usr/bin/env python

#-------------
# Load modules
#-------------
import os
import sys
from netCDF4 import Dataset
import numpy
from numpy.random import uniform
import numpy as np
import matplotlib.pyplot as plt            # pyplot module import
import matplotlib.cm as cm
import matplotlib
#import matplotlib.colors as color
from matplotlib import colors, ticker
from mpl_toolkits.basemap import Basemap, shiftgrid

# Determine the location (absolute path) of this script
curDir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curDir+'/../io')
sys.path.append(curDir+'/../utils')

import ncFileManipulation_class as ncWrite
import vertLevels_GEOS5 as pressLevels

def plotZM(data, x, y, coef, figName, plotTitle, cbarLabel=None, logScale=None, clevs=None):
    """
      Plot the zonal mean height

      Arguments
        data:      data to display
        x:         the x-axis meshgrid
        y:         the y-axis meshgrid
        coef:      coefficient to scale data
        figName:   figure name
        plotTitle: title of the plot
        cbarLabel: colorbar label
        logScale:  do we use log scale
        clevs:     user's prescribed countour levels
    """

    fig = plt.figure()
    ax1=fig.add_subplot(111)

    labelFontSize = "small"

    var = coef*data[:,:]

    ncont = 10  # number of contours
    # determine contour levels to be used; default: linear spacing, ncount levels
    if (clevs == None):
       rmax = np.max(var)
       rmin = np.min(var)
       clevs = np.linspace(rmin, rmax, ncont)

    # map contour values to colors
    norm=matplotlib.colors.BoundaryNorm(clevs, ncolors=256, clip=False)

    # draw the contours with contour labels
    CS = ax1.contour(x, y, var, levels=clevs)
    ax1.clabel(CS,inline=1, fontsize=10)
    # draw the (filled) contours
    contour = ax1.contourf(x, y, var, levels=clevs, norm=norm)

    # add colorbar
    # Note: use of the ticks keyword forces colorbar to draw all labels
    fmt = matplotlib.ticker.FormatStrFormatter("%5.4g")
    cbar = fig.colorbar(contour, ax=ax1, orientation='horizontal', shrink=0.8,
                        #ticks=clevs, format=fmt)
                        ticks=clevs[::2], format=fmt)

    if (cbarLabel == None):
       cbarLabel = 'ppm'
    cbar.set_label(cbarLabel)

    for t in cbar.ax.get_xticklabels():
        t.set_fontsize(labelFontSize)
    # set up y axes: log pressure labels on the left y axis, altitude labels
    # according to model levels on the right y axis
    ax1.set_xlabel("Latitude (degrees)")
    ax1.set_ylabel("Pressure [hPa]")
    if (logScale == 'Y'):
       ax1.set_yscale('log')
    ax1.set_ylim(10.*np.ceil(y.max()/10.), y.min()) # avoid truncation of 1000 hPa
    subs = [1,2,5]
    if y.max()/y.min() < 30.:
        subs = [1,2,3,4,5,6,7,8,9]
    if (logScale == 'Y'):
       y1loc = matplotlib.ticker.LogLocator(base=10., subs=subs)
    else:
       y1loc = matplotlib.ticker.LinearLocator()
    ax1.yaxis.set_major_locator(y1loc)
    fmt = matplotlib.ticker.FormatStrFormatter("%5.2f")
    ax1.yaxis.set_major_formatter(fmt)
    for t in ax1.get_yticklabels():
        t.set_fontsize(labelFontSize)
    # calculate altitudes from pressure values (use fixed scale height)
    #z0 = 8.400    # scale height for pressure_to_altitude conversion [km]
    #if (logScale == 'Y'):
    #   altitude = z0 * np.log(1015.23/y)
    #else:
    #   altitude = z0 * (1015.23/y)
    ## add second y axis for altitude scale 
    #ax2 = ax1.twinx()
    ## change values and font size of x labels
    #ax1.set_xlabel('Latitude [degrees]')
    #xloc = matplotlib.ticker.FixedLocator(np.arange(-90.,91.,30.))
    #ax1.xaxis.set_major_locator(xloc)
    #for t in ax1.get_xticklabels():
    #    t.set_fontsize(labelFontSize)
    ## draw horizontal lines to the right to indicate model levels
    #axr = ax2
    #label_xcoor = 1.05
    #axr.set_ylabel("Altitude [km]")
    #axr.yaxis.set_label_coords(label_xcoor, 0.5)
    #axr.set_ylim(altitude.min(), altitude.max())
    #yrloc = matplotlib.ticker.MaxNLocator(steps=[1,2,5,10])
    #axr.yaxis.set_major_locator(yrloc)
    #axr.yaxis.tick_right()
    #for t in axr.yaxis.get_majorticklines():
    #    t.set_visible(False)
    #for t in axr.get_yticklabels():
    #    t.set_fontsize(labelFontSize)

    plt.title(plotTitle)

    plt.savefig(figName + '.png')

