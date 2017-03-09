#!/usr/bin/env python

#-------------
# Load modules
#-------------
import numpy as np                         # Numpy import
import matplotlib.cm as cm
import matplotlib.colors as color
import matplotlib.pyplot as plt            # pyplot module import
from mpl_toolkits.mplot3d import Axes3D
import sys
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

#-------------------
# Load local modules
#-------------------
import row_cols_decomp

#--------------------------------
# Single plot with contour method
#--------------------------------
def mpSingle_3Dsurf_plot(X, Y, Z, figName, figTitle):
    """
      Function for a 3D plot (slices of 3D surfaces).

      Required inputs:
         - X,Y:       variables generated with Numpy meshgrid
         - Z:         Z = f(X,Y)
         - figName:   the figure name
         - figTitle:  the title of the plot
    """

    fig = plt.figure( )
    ax = Axes3D(fig)
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.jet)

    plt.savefig(figName + '.png')
    plt.show()

#-----------------------------------
# Multiple plots
#-----------------------------------

def mpXY_multi_plots(figName, **keywords):
    """
      Function to plot data on map using contour method.

      Required inputs:
         - figName:      the figure name

      Keyword arguments:
         - Xvars: x-axis data as tuple of numpy arrays
                  Xvars = (data0, data1, data2,...)
         - Yvars: y-axis data as tuple of numpy arrays
                  Yvars = (data0, data1, data2,...)
         - plotTitles: tuple variable having the titles of the
                 individual subplots.

      Returns:
         A figure having several subplots.

      Behavior:
         If no data is provided, return no graph.
    """

    if keywords.has_key('Xvars'):
       Xdata     = keywords['Xvars']
       num_Xvars = len (Xdata)
    else:
       print "No X variable was provided"
       return

    if keywords.has_key('Yvars'):
       Ydata     = keywords['Yvars']
       num_Yvars = len (Ydata)
    else:
       print "No Y variable was provided"
       return

    if (num_Xvars != num_Yvars):
       print "Should have exactly the same number of Xs and Ys"
       return

    nrows, ncols = row_cols_decomp.calc_rows_columns(num_Xvars)

    if keywords.has_key('plotTitles'):
       plotTitles = keywords['plotTitles']
       n = len(plotTitles)
       if (n < num_Xvars):
          print "Did not provide enough subplot titles"
          plotTitles[n+1:num_Xvars] = " "
    else:
       print "Did not provide subplot titles"
       plotTitles[0:num_Xvars] = " "

    for i in range(num_Xvars):
        plt.subplot(nrows, ncols, i+1)

        plt.plot(Xdata[i], Ydata[i])

        plt.title(plotTitles[i])

    plt.savefig(figName + '.png')
    plt.show()

####
# Need to implement this
# http://mancoosi.org/~abate/matplotlib-and-multiple-yaxis-scales
#
# Time series
# http://stackoverflow.com/questions/11067368/annotate-time-series-plot-in-matplotlib
# http://blog.mafr.de/2012/03/11/time-series-data-with-matplotlib/

# Time Series Plots

def ts_multi_plots(Xvar, figName, nColumns = None, **keywords):
    """
      Function to do several time series plots on a single figure.
      Only the x-axis is a time series, and the bottom plot has
      the x-axis labeled. 

      Required inputs:
         - Xvar:     time series for the x-coordinate
         - figName:  figure name
         - nColumns: number of columns for the plots
               if nColumns = 1, then only bottom plot has the x-axis labeled.

      Keyword arguments:
         - Yvars: y-axis data as tuple of numpy arrays
                  Yvars = (data0, data1, data2,...)
         - plotTitles: tuple variable having the titles of the
                 individual subplots.

      Returns:
         A figure having several subplots.

      Behavior:
         If no data is provided, return no graph.
    """

    if keywords.has_key('Yvars'):
       Ydata     = keywords['Yvars']
       num_Yvars = len (Ydata)
    else:
       print "No Y variable was provided"
       return

    if keywords.has_key('plotTitles'):
       plotTitles = keywords['plotTitles']
       n = len(plotTitles)
       if (n < num_Yvars):
          print "Did not provide enough subplot titles"
          plotTitles[n+1:num_Yvars] = " "
    else:
       print "Did not provide subplot titles"
       plotTitles[0:num_Yvars] = " "

    # Determine the number of rows and columns.
    if (nColumns == None):
        nrows, ncols = row_cols_decomp.calc_rows_columns(num_Yvars)
    else:
        nrows, ncols = row_cols_decomp.calc_rows_columns(num_Yvars, nColumns)

    # matplotlib date format object
    hfmt = mdates.DateFormatter('%Y/%m/%d')

    fig = plt.figure()

    # set date formatting. This is important to have dates pretty printed 
    fig.autofmt_xdate()

    for i in range(num_Yvars):
        ax = fig.add_subplot(nrows, ncols, i+1, title=plotTitles[i])

        #ax.plot(Xvar, Ydata[i])
        ax.plot_date(Xvar, Ydata[i])

        if (ncols == 1):
           # Only the bottom plot has the x-axis labeled
           if (i < num_Yvars - 1):
              ax.xaxis.set_visible(False)
           else:
              ax.xaxis.set_major_formatter(hfmt)
              plt.setp(ax.xaxis.get_majorticklabels(), rotation=30)
        else:
           ax.xaxis.set_major_formatter(hfmt)
           plt.setp(ax.xaxis.get_majorticklabels(), rotation=30)

    plt.savefig(figName + '.png')
    plt.show()

def single_timeSeies_plot(timeSeries, Ydata, figName, figTitle = None):

    fig, ax = plt.subplots()

    ax.plot_date(timeSeries, Ydata)

    #ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))

    if (figTitle != None):
       plt.title(figTitle)

    # matplotlib date format object
    hfmt = mdates.DateFormatter('%y/%m/%d')

    fig.autofmt_xdate()
    ax.xaxis.set_major_formatter(hfmt)


    plt.savefig(figName + '.png')
    plt.show()


#-----------------------------------
# Different plots on a single figure
#-----------------------------------

def mpXY_multi_plots(X, figName, **keywords):
    """
      Function to plot data on map using contour method.

      Required inputs:
         - X:       x-axis data as a numpy array
         - figName: the figure name

      Keyword arguments:
         - Yvars: y-axis data as tuple of numpy arrays
                  Yvars = (data0, data1, data2,...)
         - plotLegends: tuple variable having the legends of the
                 individual plots.

      Returns:
         A figure.

      Behavior:
         If no data is provided, return no graph.
    """

    if keywords.has_key('Yvars'):
       Xdata     = keywords['Yvars']
       num_Yvars = len (Ydata)
    else:
       print "No Y variable was provided"
       return

    if keywords.has_key('plotLegends'):
       plotLegends = keywords['plotLegends']
       n = len(plotLegends)
       if (n < num_Yvars):
          print "Did not provide enough plot legends"
          plotTitles[n+1:num_Yvars] = " "
    else:
       print "Did not provide plot legends"
       plotLegends[0:num_Yvars] = " "

    colormap = plt.cm.gist_ncar
    plt.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 0.9, num_Yvars)])

    labels = []

    for i in range(num_Yvars):
        plt.plot(X, Ydata[i])
        labels.append(plotLegends[i])

    plt.legend(labels, ncol=4, loc='upper center', 
               bbox_to_anchor=[0.5, 1.1], 
               columnspacing=1.0, labelspacing=0.0,
               handletextpad=0.0, handlelength=1.5,
               fancybox=True,     shadow=True)

    plt.savefig(figName + '.png')
    plt.show()


