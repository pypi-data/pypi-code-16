#!/usr/bin/env python

#-------------
# Load modules
#-------------
from netCDF4 import Dataset
import matplotlib as mplb
import matplotlib.pyplot as plt            # pyplot module import
import numpy as np                         # Numpy import
import matplotlib.cm as cm
import matplotlib
import sys
import row_cols_decomp
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

# Define a Cartopy 'ordinary' lat-lon coordinate reference system.
crs_latlon = ccrs.PlateCarree()

eps = 0.0009

#--------------------------------------
# Multiple plots with contour method
#--------------------------------------
def cartContour_multi_plots(lats, lons, figName, cmap = cm.jet, 
                     maskedVal = 'nan', badVal_color = 'white', **keywords):
    """
      Function to plot data on map using contour method.

      Required inputs:
         - lats,lons:    lat/lon information
         - figName:      the figure name
         - cmap:         color map
         - maskedVal:    values to be masked
         - badVal_color: color for the masked values

      Keyword arguments:
         - vars: the data as tuple of numpy arrays
                 vars = (data0, data1, data2,...)
         - plotTitles: tuple variable having the titles of the
                 individual subplots.

      Returns:
         A figure having several subplots.

      Behavior:
         If no data is provided, return no graph.
    """

    if keywords.has_key('vars'):
       data     = keywords['vars']
       num_vars = len (data)
       nrows, ncols = row_cols_decomp.calc_rows_columns(num_vars)
       if keywords.has_key('plotTitles'):
          plotTitles = keywords['plotTitles']
          n = len(plotTitles)
          if (n < num_vars):
             print "Did not provide enough subplot titles"
             plotTitles[n+1:num_vars] = " "
       else:
          print "Did not provide subplot titles"
          plotTitles[0:num_vars] = " "
    else:
       print "No variable to plot"
       return

    latLow  = lats[0]  # + eps
    latHigh = lats[-1] # - eps
    lonLow  = lons[0]   + eps
    lonHigh = lons[-1] # - eps

    fig = plt.figure(figsize=(16,8))
    fig.subplots_adjust(left=0.05, right=1., bottom=0., top=0.9, hspace=.0225, wspace = 0.09)
    #fig.subplots_adjust(left=0., right=1., bottom=0., top=0.9, hspace=.175, wspace = 0.002)

    for i in range(num_vars):
        ax = plt.subplot(nrows, ncols, i+1, projection=ccrs.PlateCarree())
        ax.set_extent([lonLow, lonHigh, latLow, latHigh])

        # Put a background image on for nice sea rendering.
        ax.stock_img()

        # Coastline and axis values
        ax.add_feature(cfeature.COASTLINE)
        #ax.add_feature(cfeature.LAND)
        #ax.add_feature(cfeature.OCEAN)
        #ax.add_feature(cfeature.BORDERS, linestyle=':')
        #ax.add_feature(cfeature.LAKES, alpha=0.5)
        #ax.add_feature(cfeature.RIVERS)

        # Parallels and Meridians
        gl = ax.gridlines(crs=crs_latlon, draw_labels=True, linestyle='-')
        gl.xlabels_top = False
        gl.ylabels_right = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER

        # Masked values
        if (maskedVal == "nan"):
           mask_data = np.ma.masked_where(np.isnan(data[i]),data[i])
        else:
           mask_data = np.ma.masked_values(data[i], maskedVal)

        ncont = 10  # number of contours
        # determine contour levels to be used; default: linear spacing, ncount levels
        rmax = np.max(mask_data)
        rmin = np.min(mask_data)
        clevs = np.linspace(rmin, rmax, ncont)

        # map contour values to colors
        norm=matplotlib.colors.BoundaryNorm(clevs, ncolors=256, clip=False)

        # Set color for bad values
        cmap.set_bad(badVal_color)
    
        # Do contour plots
        plt.contour (lons,lats,mask_data.squeeze(),cmap=cmap)
        cf = plt.contourf(lons,lats,mask_data.squeeze(), 
                          levels=clevs, cmap=cmap, norm=norm,
                          transform=ccrs.PlateCarree())

        # Add colorbar and title, and then show the plot
        cbar = plt.colorbar(cf, orientation="vertical", shrink=.7, ticks=clevs[::2])
        #cbar = plt.colorbar(cf, orientation="vertical", shrink=.7, ticks=clevs[::4], format="%.3e")
        plt.title(plotTitles[i])

    plt.savefig(figName + '.png')
    plt.show()

