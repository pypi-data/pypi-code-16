"""
Visualizer.py

The Visualizer module is responsible for producings statistical graphs
that report on, and analyze various specified metrics from a given
data set.


A compact, scalable, statistical analysis, and reporting package built on top of
pandas, and bokeh.

Author : Rashad Alston <ralston@yahoo-inc.com>
Python : 3.5.1

License: BSD 3 Clause

*************************************************************************
"""

import warnings

import numpy as np
import pandas as pd
from bokeh.io import show
from bokeh.models import DatetimeTickFormatter, HoverTool
from bokeh.models import Range1d, Legend, LinearAxis
from bokeh.models.widgets import Panel, Tabs
from bokeh.plotting import figure

from .functions import frame_from_list
from .functions import generate_timeplot_labels
from .reporter import general_distribution

from ..utils import glyph_fxn
from ..utils import listed_color_map
from ..utils import pckg_check
from ..utils import py_check

pckg_check()
py_check()

__all__ = ['tqstat_plot',
           'time_plot',
           'compare_plot',
           'doubleaxis_plot']


TOOLBAR_TOOLS = 'pan,box_select,resize,wheel_zoom,reset,save,zoom_in,zoom_out,hover,box_zoom'


def tqstat_plot(data, groupby, segby, aggby, xlims, ylims, **kwargs):
    """
    Creates bokeh plot for each tqstat given to groupby param

    Parameters
    ----------
        data : <DataFrame>
            Data set to be used
        groupby : <list>
            Features on which to group sub-DataFrames
        segby : <string>
            Feature on which to segment full DataFrame (data) into sub-DataFrames
        aggby : <dict>
            Aggregation function to be applied
        xlims : <list>
            Xaxis ranges for each plot
        ylims : <list>
            Yaxis ranges for each plot

    Examples
    --------
        >>> import tqpy.analysis.visualizer as tqv
        >>> import tqpy.analysis.functions as tqf
        >>> data = tqf.load_data(file='../test/data/mb_test_data_small.csv', low_memory=False)
        >>> tqv.tqstat_plot(data, ['ttc', 'hour'], segby=None, aggby={'valid_clicks': np.sum}, \
                            xlims=[[0, 120],[0,500],None,None], ylims=[None,None,None,None])


    Notes
    -----
        - 2D lists are passed to xlims if passing actual limits and not None
        - xaxis and yaxis limits are not required
        - The aggby param only supports a single key,value pair (as of version 0.3.0)
    """
    key = list(aggby.keys())[0]
    tabs = []

    for k, group in enumerate(groupby):

        fig = figure(title=group.upper(),
                     x_axis_label='Time',
                     width=[kwargs.pop('size')[0] if 'size' in kwargs else 1000][0],
                     height=[kwargs.pop('size')[1] if 'size' in kwargs else 500][0],
                     y_axis_label='Aggregated Values',
                     toolbar_location='below',
                     toolbar_sticky=False,
                     tools=TOOLBAR_TOOLS)

        if not segby:

            aggdf = data.groupby(group).agg(aggby)

            fig.line(x=aggdf.index.values,
                     y=aggdf[key].values,
                     legend=('{}: {:,.0f} {}'.format(group.upper(), sum(aggdf[key].values), key)),
                     line_width=3.0,
                     alpha=0.6)

        else:

            if 'top_n' in kwargs:
                r = general_distribution(data=data, groupby=segby, aggby=aggby, sortby=key)
                data = frame_from_list(data=data, dist=r, feature=segby, top_n=kwargs.pop('top_n'))

            unis = data[segby].unique()
            cmap = listed_color_map(len(unis))
    
            for i, uni in enumerate(unis):
    
                sdf = data.loc[data[segby] == uni]
                aggdf = sdf.groupby(group).agg(aggby)
    
                fig.line(x=aggdf.index.values,
                         y=aggdf[key].values,
                         legend=('{}: {} | {:,.0f} {}'.format(segby, str(uni), sum(aggdf[key].values), key)),
                         line_width=3.0,
                         alpha=0.6,
                         line_color=cmap[i])
    
        if xlims[k]:
            fig.set(x_range=Range1d(xlims[k][0], xlims[k][1]))
        if ylims[k]:
            fig.set(y_range=Range1d(ylims[k][0], ylims[k][1]))

        legend = Legend(location='top_right')
        fig.add_layout(legend)
        fig.legend.label_text_font_size = '7.5pt'
    
        tab = Panel(child=fig, title=group.upper())
        tabs.append(tab)
    
    plot_tabs = Tabs(tabs=tabs)
    show(plot_tabs)

    return None


def time_plot(data, date, segby, aggby, convert_to_pdates=True, title='Time Plot', show_labels=True,
              **kwargs):
    """
    Shows the performance of a data set feature (aggby) over time

    Parameters
    ----------
        data : <DataFrame>
            Data set to be used
        date : <string>
            DataFrame column name featuring the dates to be used
        segby : <string>
            Data set feature on which to segment the original data set into sub-data sets
        aggby : <dict>
            Aggregation function to be applied
        convert_to_pdates : <bool>, default=True
            Whether or not to convert the date feature into pandas datetime
        title : <string>
            Title of plot
        show_labels : <boolean>, default=True
            Whether or not to show aggregated value labels on plot

    Raises
    ------
        AttributeError : If number of unique values given to dates param is 0

    Examples
    --------
        >>> import tqpy.analysis.visualizer as tqv
        >>> import tqpy.analysis.functions as tqf
        >>> data = tqf.load_data(file='../test/data/mb_test_data_small.csv', low_memory=False)
        >>> tqv.time_plot(data, date='datestamp', segby='ua_os', aggby={'valid_clicks': np.sum}, \
                          convert_to_pdates=True, title='Native Click Time-Series')

    Alternatively


    Notes
    -----
        - If using this function on a data set that has already had its 'datestamp'
        feature converted to 'pdates', then setting pdates=False will prevent the
        function from computing a replacement for pdates (which is already in the data)
        - The aggby param supports multiple key,value pairs
        - The value(s) supplied to the 'date' param must 'at least' be of format YYYYmmdd.
        Anything extra (e.g., YYYYmmddhhmmss) will be sliced after YYYYmmdd
    """
    u_dates = len(data['datestamp'].unique())

    if u_dates == 0:
        raise AttributeError("Number of unique dates must be > 0.\n")

    keys = list(aggby.keys())
    line_dashes = ['solid', 'dashed', 'dotted', 'dotdash', 'dashdot']
    template = 'YYYYmmdd'

    if convert_to_pdates:
        str_dates = [str(val)[:len(template)] for val in data[date].values]
        data['pdates'] = pd.to_datetime(str_dates, yearfirst=True)

    # If dates have already been converted (pdates=False) OR if
    # pdates are just now being converted (pdates=True)
    pdate = 'pdates'

    if not segby:

        # Determine how to aggregate the unique feature sub-DataFrame
        # based, on how many unique date values are found
        if u_dates > 1:
            aggdf = data.groupby([pdate, date]).agg(aggby)
        elif u_dates == 1:
            aggdf = data.groupby(['hour', 'hour']).agg(aggby)

        fig = figure(title=title,
                     x_axis_label=['Date' if u_dates > 1 else 'Hour'][0],
                     y_axis_label='Aggregated Values',
                     width=[kwargs.pop('size')[0] if 'size' in kwargs else 1000][0],
                     height=[kwargs.pop('size')[1] if 'size' in kwargs else 500][0],
                     toolbar_location='below',
                     toolbar_sticky=False,
                     tools=TOOLBAR_TOOLS)

        cmap = listed_color_map(len(keys))

        for i, key in enumerate(keys):

            # Note: See ..utils.glyph_fxn() for warning surpression explanation
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                glyph_fxn()

                source, labels = generate_timeplot_labels(aggdf, key=key, show_labels=show_labels)

                fig.line(x='x',
                         y='y',
                         line_width=3.0,
                         alpha=0.6,
                         line_color=cmap[i],
                         source=source,
                         legend=('{} : {:,.0f}'.format(key.upper(), sum(aggdf[key].values))))

                # Create white-filled circles (glyphs) and enlarge their size
                r = fig.circle(x='x',
                               y='y',
                               line_width=3.0,
                               alpha=1.0,
                               fill_color='white',
                               legend=False,
                               line_color=cmap[i],
                               source=source)
                glyph = r.glyph
                glyph.size = 7

                if show_labels:
                    fig.add_layout(labels)

        if u_dates == 1:
            pass
        elif u_dates > 1:
            fig.xaxis.formatter = DatetimeTickFormatter(hours=['%b %d %Y'],
                                                        days=['%b %d %Y'],
                                                        months=['%b %d %Y'],
                                                        years=['%b %d %Y'])
        legend = Legend(location='top_right', label_text_font_size='6pt')
        fig.add_layout(legend)
        fig.legend.label_text_font_size = '7.5pt'

        # Hover tool using ColumnSource
        hover = fig.select(dict(type=HoverTool))
        hover.tooltips = [('Time', '@z'), ('Value', '@labels')]
        hover.mode = 'mouse'

        show(fig)

    elif segby:

        if 'top_n' in kwargs:
            r = general_distribution(data=data, groupby=segby, aggby=aggby, sortby=keys)
            data = frame_from_list(data=data, dist=r, feature=segby, top_n=kwargs.pop('top_n'))

        tabs = []

        unis = data[segby].unique()
        cmap = listed_color_map(len(unis))

        for i, uni in enumerate(unis):

            # Accounting for unique values of type null
            if str(uni) == 'nan':
                sdf = data.loc[pd.isnull(data[segby])]
            else:
                sdf = data.loc[data[segby] == uni]

            uni_dates_len = len(sdf['datestamp'].unique())

            # Determine how to group the unique feature sub-DataFrame
            # based, on how many unique date values are found
            if uni_dates_len == 1:
                aggdf = sdf.groupby(['hour', 'hour']).agg(aggby)
            elif uni_dates_len > 1:
                aggdf = sdf.groupby([pdate, date]).agg(aggby)

            fig = figure(title=title,
                         x_axis_label=['Date' if uni_dates_len > 1 else 'Hour'][0],
                         y_axis_label='Aggregated Values',
                         width=[kwargs.pop('size')[0] if 'size' in kwargs else 1000][0],
                         height=[kwargs.pop('size')[1] if 'size' in kwargs else 500][0],
                         toolbar_location='below',
                         toolbar_sticky=False,
                         tools=TOOLBAR_TOOLS)

            for k, key in enumerate(keys):
                aggdf[key] = [round(val, 2) for val in aggdf[key]]

                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', DeprecationWarning)
                    glyph_fxn()

                    source, labels = generate_timeplot_labels(aggdf, key=key, show_labels=show_labels)

                    fig.line(x='x',
                             y='y',
                             line_width=1.5,
                             alpha=0.6,
                             line_color=cmap[i],
                             line_dash=line_dashes[k],
                             legend=('{}: {} | {:,.0f} {}'.format(segby, uni, sum(aggdf[key].values),
                                     key.upper())),
                             source=source)

                    # Create white-filled circles (glyphs) and enlarge their size
                    r = fig.circle(x='x',
                                   y='y',
                                   line_width=3.0,
                                   alpha=1.0,
                                   fill_color='white',
                                   legend=False,
                                   line_color=cmap[i],
                                   source=source)
                glyph = r.glyph
                glyph.size = 7

                if show_labels:
                    fig.add_layout(labels)

            if uni_dates_len == 1:
                pass
            elif uni_dates_len > 1:
                fig.xaxis.formatter = DatetimeTickFormatter(hours=['%b %d %Y'],
                                                            days=['%b %d %Y'],
                                                            months=['%b %d %Y'],
                                                            years=['%b %d %Y'])

            legend = Legend(location='top_right', label_text_font_size='6pt')
            fig.add_layout(legend)
            fig.legend.label_text_font_size = '7.5pt'

            # Hover tool using ColumnSource
            hover = fig.select(dict(type=HoverTool))
            hover.tooltips = [('Time', '@z'), ('Value', '@labels')]
            hover.mode = 'mouse'

            tab = Panel(child=fig, title=str(uni))
            tabs.append(tab)

        plot_tabs = Tabs(tabs=tabs)
        show(plot_tabs)

    return None


def compare_plot(goodset, badset, groupby, aggby, xlims, ylims, **kwargs):
    """
    Compares two data sets on a groupby feature

    Parameters
    ----------
        goodset : <DataFrame>
            DataFrame containing OK traffic
        badset : <DataFrame>
            DataFrame containing suspicious traffic
        groupby : <list>
            Feature(s) on which to group data sets
        aggby : <dict>
            Aggregation function to be applied
        xlims : <list>
            Xaxis ranges for each plot
        ylims : <list>
            Yaxis ranges for each plot

    Raises
    ------
        KeyError : If value passed to groupby param or aggby param (keys()) is not a column
        in the data set

    Examples
    --------
        >>> import tqpy.analysis.visualizer as tqv
        >>> import tqpy.analysis.functions as tqf
        >>> data = tqf.load_data(file='../test/data/mb_test_data_small.csv', low_memory=False)
        >>> gs,bs = data.loc[data['ad_id']!=4321], data.loc[data['ad_id']==1234],
        >>> tqv.compare_plot(gs, bs, groupby=['ttc','hour'], aggby={'clicks':np.sum}, xlims=[[0,120],None],\
                             ylims=[None, None])
    """
    key = list(aggby.keys())[0]
    cols = groupby + list(aggby.keys())
    tabs = []

    for c in cols:
        if c not in goodset.columns.values and c not in badset.columns.values:
            raise KeyError("'%s' feature is not included in both data sets.\n" % c)

    for i, group in enumerate(groupby):

        oksdf = goodset.groupby(group).agg(aggby)
        badsdf = badset.groupby(group).agg(aggby)

        fig = figure(title=('Comparing %s' % group.upper()),
                     y_axis_label=key.upper(),
                     x_axis_label=group.upper(),
                     width=[kwargs.pop('size')[0] if 'size' in kwargs else 1000][0],
                     height=[kwargs.pop('size')[1] if 'size' in kwargs else 500][0],
                     toolbar_sticky=False,
                     tools=TOOLBAR_TOOLS)

        fig.line(badsdf.index.values,
                 badsdf[key].values,
                 alpha=0.6,
                 color='#FF471A',
                 legend=('Suspicious Set: {:,.0f} {}'.format(sum(badsdf[key].values), key)),
                 line_color='#DC143C',
                 line_width=5.0)

        fig.line(oksdf.index.values,
                 oksdf[key].values,
                 alpha=0.6,
                 color='#3CB371',
                 legend=('Okay Set: {:,.0f} {}'.format(sum(oksdf[key].values), key)),
                 line_color='#3CB371',
                 line_width=5.0)

        if xlims[i]:
            fig.set(x_range=Range1d(xlims[i][0], xlims[i][1]))
        if ylims[i]:
            fig.set(y_range=Range1d(ylims[i][0], ylims[i][1]))

        legend = Legend(location='top_right')
        fig.add_layout(legend)
        fig.legend.label_text_font_size = '7.5pt'

        tab = Panel(child=fig, title=group.upper())
        tabs.append(tab)

    plot_tabs = Tabs(tabs=tabs)
    show(plot_tabs)

    return None


def doubleaxis_plot(data, groupby, aggby, xlims, **kwargs):
    """
    Visualize two separate aggregate features relative to a
    the standard TQStat group by features


    Parameters
    ----------
        data : <DataFrame>
            Data set to be used
        groupby : <list>
            Features on which to group sub-DataFrames
        segby : <string>
            Feature on which to segment full DataFrame (data) into sub-DataFrames
        aggby : <dict>
            Aggregation function to be applied
        xlims : <list>
            Xaxis ranges for each plot
        ylims : <list>
            Yaxis ranges for each plot

    Raises
    ------
        KeyError : If value passed to groupby param or aggby param (keys()) is not a column
        in the data set

    Examples
    --------
        >>> import tqpy.analysis.visualizer as tqv
        >>> import tqpy.analysis.functions as tqf
        >>> data = tqf.load_data(file='../test/data/mb_test_data_small.csv', low_memory=False)
        >>> tqv.doubleaxis_plot(data=data, groupby=['ttc'], segby=None, \
                                aggby={'total_clicks':np.sum, 'converted_clicks':np.sum}, xlims=[[0,500]])
    """
    keys = list(aggby.keys())
    tabs = []

    cols = groupby + keys
    for c in cols:
        if c not in data.columns.values:
            raise KeyError("'%s' is not a feature in the data set.\n" % c)

    if len(keys) <= 1:
        raise ValueError("1 or less aggregate features detected. doubleaxis_plot() requires >= 2 features "
                         "in the 'aggby' param.\n")

    for i, group in enumerate(groupby):

        sdf = data.groupby(group).agg(aggby)
        x = sdf.index.values

        # Note : Due to a Bokeh bug which shuffles the 'aggby' keys
        # on a given iteration, and then sets the ymax of both
        # axes to the max of the 2nd y axis if the 2nd y axis has
        # the highest aggregate values - each aggregate value needs
        # to be set according to whichever has the largest values so
        # that the largest set of values is always the left (main) axis

        if sdf[keys[0]].sum() > sdf[keys[1]].sum():
            y = (sdf[keys[0]].values, keys[0])
            y2 = (sdf[keys[1]].values, keys[1])
        else:
            y = (sdf[keys[1]].values, keys[1])
            y2 = (sdf[keys[0]].values, keys[0])

        fig = figure(title=('{} by {} and {}'.format(group.upper(), keys[0].upper(), keys[1].upper())),
                     y_axis_label=y[1].upper(),
                     x_axis_label=group.upper(),
                     width=[kwargs.pop('size')[0] if 'size' in kwargs else 1000][0],
                     height=[kwargs.pop('size')[1] if 'size' in kwargs else 500][0],
                     toolbar_sticky=False,
                     tools=TOOLBAR_TOOLS)

        fig.line(x=x,
                 y=y[0],
                 color='#800080',
                 line_width=3.0,
                 alpha=0.75,
                 legend='{}  |  {:,.0f}'.format(y[1].upper(), sum(y[0])))

        fig.extra_y_ranges = {y2[1]: Range1d(start=0, end=max(y2[0]))}
        fig.add_layout(LinearAxis(y_range_name=y2[1], axis_label=y2[1].upper()), 'right')

        fig.line(x=x,
                 y=y2[0],
                 y_range_name=y2[1],
                 color='#FFD700',
                 line_width=3.0,
                 alpha=0.75,
                 legend='{}  |  {:,.0f}'.format(y2[1].upper(), sum(y2[0])))

        tab = Panel(child=fig, title=group.upper())
        tabs.append(tab)

        if xlims[i]:
            fig.set(x_range=Range1d(xlims[i][0], xlims[i][1]))

        legend = Legend(location='top_right')
        fig.add_layout(legend)
        fig.legend.label_text_font_size = '7.5pt'

    plot_tabs = Tabs(tabs=tabs)
    show(plot_tabs)

    return None
