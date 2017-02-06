#!/usr/bin/env python
"""graph_training.py: visualize training process"""
__author__ = "Fabien Cromieres"
__license__ = "undecided"
__version__ = "1.0"
__email__ = "fabien.cromieres@gmail.com"
__status__ = "Development"

import sqlite3

def commandline():
        
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("data")
    args = parser.parse_args()
        
        
    import pandas
    import numpy as np
    
    df = pandas.DataFrame.from_csv(args.data)
    
    xname = df.index.name
    xvals = np.array(list(df.index))
    
    yvals = [None] * 3
    ynames = [None] * 3
    for i in xrange(3):
        ynames[i] = df.keys()[i]
        yvals[i] = df.icol(i).values
    
    if 0:
        import matplotlib.pyplot as plt
    
    #     yvals[2] = np.log10(yvals[2])
    
        fig, ax = plt.subplots()
        
        # Twin the x-axis twice to make independent y-axes.
        axes = [ax, ax.twinx(), ax.twinx()]
        
        axes[2].set_yscale('log')
    #     axes[2].yaxis.tick_right() 
    #     import matplotlib.ticker as plticker
    #     loc = plticker.MultipleLocator(base=1.0)
    #     axes[2].yaxis.set_major_locator(loc)
    #     axes[2].set_ylim(ymin=10000, ymax = 250000)
    #     axes[2].set_yticks([10000, 100000])
    #     axes[2].get_yaxis().set_major_formatter(plticker.ScalarFormatter())
    #     axes[0].set_navigate(False)
    #     axes[1].set_navigate(False)
        # Make some space on the right side for the extra y-axis.
        fig.subplots_adjust(right=0.75)
        
        # Move the last y-axis spine over to the right by 20% of the width of the axes
        axes[-1].spines['right'].set_position(('axes', 1.2))
        
        # To make the border of the right-most axis visible, we need to turn the frame
        # on. This hides the other plots, however, so we need to turn its fill off.
        axes[-1].set_frame_on(True)
        axes[-1].patch.set_visible(False)
    
        # And finally we get to plot things...
        colors = ('Green', 'Red', 'Blue')
        for ax, yn, yval, color in zip(axes, ynames, yvals, colors):
    #         data = np.array()
            mask = np.isfinite(yval)
            ax.plot(xvals[mask], yval[mask], marker='o', linestyle='-', color=color)
            ax.set_ylabel(yn, color=color)
            ax.tick_params(axis='y', colors=color, which='minor')
        axes[0].set_xlabel(xname)
        
        plt.show()
        
        return
    
    else:
        import plotly
        #         import plotly.plotly as py
        import plotly.graph_objs as go
        
        trace0 = go.Scatter(
        #             x = random_x,
            x = xvals,
            y = yvals[0],
            mode = 'lines',
            name = ynames[0],
            line = dict(
                        color = ('rgb(205, 12, 24)'),
                        width = 2),
            connectgaps = True
            )
        trace1 = go.Scatter(
        #             x = random_x,
            x = xvals,
            y = yvals[1],
            mode = 'lines',
            name = ynames[1],
            yaxis='y2',
                line = dict(
        color = ('rgb(205, 128, 24)'),
        width = 2),
            connectgaps = True
        )
        trace2 = go.Scatter(
        #             x = random_x,
            x = xvals,
            y = yvals[2],
            mode = 'lines',
            name = ynames[2],
            yaxis='y3',
                line = dict(
        color = ('rgb(22, 96, 167)'),
        width = 2,),
            connectgaps = True
        )
        
        layout = go.Layout(
            title='Training evolution',
    #         xaxis = dict(
    #             span = (1,3)
    #                      ),
            xaxis = dict(
                title = xname,
                         ),
            yaxis=dict(
                title=ynames[0],
                gridcolor='#bdbdbd'
            ),
            yaxis2=dict(
                title=ynames[1],
                overlaying='y',
                side='right'
            ),
                           
            yaxis3=dict(
                title=ynames[2],
                overlaying='y',
                side='right',
                anchor = "free",
                position = 4
            )
                           
        )
        
        data = [trace0, trace1, trace2]
        fig = go.Figure(data=data, layout=layout)
        # Plot and embed in ipython notebook!
        plotly.offline.plot(fig, filename = "testrodi.html", auto_open = True)
    
if __name__ == '__main__':
    commandline()