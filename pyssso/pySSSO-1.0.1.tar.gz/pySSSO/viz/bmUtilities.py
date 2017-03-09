#!/usr/bin/env python

#-------------
# Load modules
#-------------
from netCDF4 import Dataset
import matplotlib as mplb
import matplotlib.pyplot as plt            # pyplot module import
import numpy as np                         # Numpy import
import matplotlib.cm as cm
import matplotlib.colors as color
from mpl_toolkits.basemap import Basemap   # basemap import
import sys
import row_cols_decomp


#--------------------------------------
# Multiple plots with contour method
#--------------------------------------
def bmContour_multi_plots(lats, lons, figName, cmap = cm.jet, 
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

    latLow  = lats[0]
    latHigh = lats[-1]
    lonLow  = lons[0]
    lonHigh = lons[-1]

    for i in range(num_vars):
        plt.subplot(nrows, ncols, i+1)

        m = Basemap(projection='mill',
                    llcrnrlat=latLow,
                    urcrnrlat=latHigh,
                    llcrnrlon=lonLow,
                    urcrnrlon=lonHigh,
                    resolution='c')

        # Coastline and axis values
        m.drawcoastlines()
        m.drawparallels(np.arange(latLow,latHigh+1,30.),
                        labels=[True,False,False,False])
        m.drawmeridians(np.arange(lonLow,lonHigh+1,80.),
                        labels=[False,False,False,True])

        longrid,latgrid = np.meshgrid(lons,lats)

        # compute native map projection coordinates of lat/lon grid.
        x, y = m(longrid,latgrid)

        # Masked values
        if (maskedVal == "nan"):
           mask_data = np.ma.masked_where(np.isnan(data[i]),data[i])
        else:
           mask_data = np.ma.masked_values(data[i], maskedVal)

        # Set color for bad values
        cmap.set_bad(badVal_color)
    
        # Do contour plots
        m.contour (x,y,mask_data.squeeze(),cmap=cmap)
        cf = m.contourf(x,y,mask_data.squeeze(),cmap=cmap)

        # Add colorbar and title, and then show the plot
        cbar = plt.colorbar(cf, orientation="vertical", shrink=.7, format="%.3e")
        #cbar = plt.colorbar(cf, orientation="horizontal", shrink=.7, format="%.3e")
        #plt.colorbar(shrink=.7)
        plt.title(plotTitles[i])

    plt.savefig(figName + '.png')
    plt.show()

#--------------------------------------
# Multiple plots with pcolormesh method
#--------------------------------------
def bmColormesh_multi_plots(lats, lons, figName, cmap = cm.jet, 
                     maskedVal = 'nan', badVal_color = 'white', **keywords):
    """
      Function to plot data on map using pcolormesh  method.

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

    #plt.figure( )
    latLow  = lats[0]
    latHigh = lats[-1]
    lonLow  = lons[0]
    lonHigh = lons[-1]

    for i in range(num_vars):
        plt.subplot(nrows, ncols, i+1)

        m = Basemap(projection='mill',
                    llcrnrlat=latLow,
                    urcrnrlat=latHigh,
                    llcrnrlon=lonLow,
                    urcrnrlon=lonHigh,
                    resolution='c')

        # Coastline and axis values
        m.drawcoastlines()
        m.drawparallels(np.arange(latLow,latHigh+1,20.),
                        labels=[True,False,False,False])
        m.drawmeridians(np.arange(lonLow,lonHigh+1,60.),
                        labels=[False,False,False,True])

        longrid,latgrid = np.meshgrid(lons,lats)

        # compute native map projection coordinates of lat/lon grid.
        x, y = m(longrid,latgrid)

        # Masked values
        if (maskedVal == "nan"):
           mask_data = np.ma.masked_where(np.isnan(data[i]),data[i])
        else:
           mask_data = np.ma.masked_values(data[i], maskedVal)

        # Set color for bad values
        cmap.set_bad(badVal_color)

        # plot the field using the fast pcolormesh routine and 
        cs = m.pcolormesh(x, y, mask_data, shading='flat', cmap=cmap)

        # Add colorbar and title, and then show the plot
        cbar = plt.colorbar(cs)
        # cbar = plt.colorbar(cs, orientation="horizontal", shrink=.7, format="%.3e")
        plt.title(plotTitles[i])
        #plt.colorbar(shrink=.7)

    ##plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
    #plt.subplots_adjust(right=0.85)
    #cax = plt.axes([0.875, 0.2, 0.025, 0.61])
    #plt.colorbar(cax=cax)

    plt.savefig(figName + '.png')
    plt.show()

