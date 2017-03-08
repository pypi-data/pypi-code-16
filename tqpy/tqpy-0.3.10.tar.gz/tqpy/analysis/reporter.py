"""
Reporter.py

Reporter module is responsible for generating various statistical reports
on a given data set, grouped and aggregated as needed. Built on top of pandas,
the Reporter module gives scalable, Excel-like functionality to a data set


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

from ..utils import format_cells
from ..utils import mplc_fxn
from ..utils import pckg_check
from ..utils import py_check

pckg_check()
py_check()


def general_distribution(data, groupby, aggby, sortby=None, styling=None, shuffle=False, show_percents=True):
    """
    Captures a general distribution of the data set grouping data on a 'groupby' index, and
    aggregating on aggby.

    Parameters
    ----------
        data : <DataFrame>
            Data set to be manipulated
        groupby : <list>
            Values on which to group DataFrame
        aggby : <dict>
            Aggregation function to be applied
        sortby : <string>, default=None
            Report key on which to sort returned report
        styling : <string>, default=None
            The conditional formatting to apply to the DataFrame
            cells
        shuffle : <boolean>, default=False
            Whether or not to shuffle the distribution report
        show_percents: <boolean>, default=True
            Whether or not to include the distribution percentage
            of the total 'aggy' value in the report frame

    Returns
    -------
        report : <pandas Styler object>, (if styling parameter is passed)
            Distribution report (conditional formatting)
        report : <DataFrame object>, (if styling parameter is not passed)
            Distribution report (no formatting)

    Raises
    ------
        TypeError :
            If groupby param isn't or can't be converted to type list
        AttributeError :
            If both sortby and shuffle params are passed (do one or the other)
        KeyError :
            If value passed to groupby param or aggby param (keys()) is not a column
            in the data set

    Examples
    --------
        >>> import tqpy.analysis.functions as tqf
        >>> import tqpy.analysis.reporter as tqr
        >>> data = tqf.load_data(file='../test/data/mb_test_data_small.csv', low_memory=False)
        >>> r = general_distribution(data=data, groupby=['datestamp'], styling=None, \
                shuffle=False)
        >>> r.head()

                   valid_clicks  pcntg_of_total_valid_clicks
        datestamp                                           
        20161002             55                         5.71
        20161001             51                         5.30
        20160926             49                         5.09
        20161003             49                         5.09
        20160930             42                         4.36

    Alternatively
    >>> r = tqr.general_distribution(data=data, groupby=['ttc','ipts','min'], \
            aggby={'clicks':np.sum}, sortby=None, styling='bar', shuffle=True)
    >>> r

    Note
    -----
        Passing a value to the 'styling' param will require printing the entire 
        returned report, else an AttributeError will be raised if one tries to use 'r.head(10)', 
        since a pandas Styler object has no attribute 'head'
    """
    agg_d = {}
    keys = list(aggby.keys())

    for val in keys:
        agg_d[val] = sum(data[val].values)

    if not isinstance(groupby, list):
        try:
            groupby = [groupby]
        except:
            raise TypeError("'groupby' param requires type list. Type %s given.\n" % type(groupby))

    if sortby and shuffle:
        raise AttributeError("Can't shuffle AND sort DataFrame. Select one or the other.\n")

    colnames = groupby + keys

    for c in colnames:
        if c not in data.columns.values:
            raise KeyError("'%s' is not a column in the data set." % c)

    report = data.groupby(groupby).agg(aggby)

    if show_percents:
        for k in keys:
            dists = [round(max(0, (val / agg_d[k] * 100)), 3) for val in report[k].values]
            dist_dict = {i: j for i, j in zip(report[k].values, dists)}
            dist_name = 'pcntg_of_total_{}'.format(k)
            report[dist_name] = report[k].map(dist_dict)

    if sortby:
        report = report.sort_values(by=sortby, ascending=False)
    elif shuffle:
        report = report.reindex(np.random.permutation(report.index))
    else:
        pass

    if styling:
        return format_cells(report=report, style=styling)
    else:
        return report


def pivot_table(data, grouprows, values, aggby, groupcols=None, styling=None, margins=False, **kwargs):
    """
    Creates a pivot table of the given data set. 
    Note : 'values' and 'aggby' params must include same features

    Parameters
    ----------
        data : <DataFrame>
            Data set to be manipulated
        grouprows : <list>
            DataFrame features on which to use as the returned report's horizontal index
        values : <list>
            DataFrame features on which the report will aggregate
        aggby : <dict>
            Aggregation function to be applied
        fill_na : <float>
            Value used to fill NaN values in DataFrame
        groupcols : <list>, default=None
            DataFrame features on which to use as the returned report's vertical index
        styling : <string>, default=None
            The conditional formatting to apply to the DataFrame
            cells (pandas >= 0.17.1)
        margins : <bool>, default=True
            Whether or not to show 'Grand Totals' at edges of report

    Returns
    -------
        pt : <pandas Styler object>, (conditionally formatted)
            Conditionally formatted general distribution report
        pt : <DataFrame object>, (without formatting)
            General distribution report

    Raises
    ------
        TypeError : If grouprows, groupcols, values params aren't and can't be
        converted to type list
        KeyError : If a given param is not a feature in the given DataFrame

    Examples
    --------
        >>> import tqpy.analysis.functions as tqf
        >>> import tqpy.analysis.reporter as tqr
        >>> data = tqf.load_data(file='../test/data/mb_test_data_small.csv', low_memory=False)
        >>> r = tqr.pivot_table(data=data, grouprows=['advertiser_acct_id', 'datestamp'], \
                    values=['total_clicks'], aggby={'total_clicks':np.sum}, fill_na=0, \
                    groupcols=['ua_os'], styling=None, margins=False)
        >>> r.head(10)

                                         total_clicks                                 \
            ua_os                             android blackberry chrome os ios linux   
            advertiser_acct_id datestamp                                               
            172                20161001             0          0         0   1     0   
                               20161006             0          0         0   1     0   
                               20161020             1          0         0   0     0   
                               20161021             0          0         0   0     0   
            766                20160923             2          0         0   0     0   
                               20160926             1          0         0   0     0   
                               20161004             2          0         0   0     0   
                               20161010             1          0         0   0     0   
                               20161012             0          0         0   0     0   
            1163               20161008             0          0         0   0     0 
    """
    for val in [grouprows, groupcols, values]:
        if val:
            if not isinstance(val, list):
                raise TypeError("'%s' must be of type list.\n" % val)

    col_names = grouprows + values + list(aggby.keys())

    for c in col_names:
        if c not in data.columns.values:
            raise KeyError("'%s' is not a column in the data set.\n" % c)

    table = pd.pivot_table(data, index=grouprows, values=values, aggfunc=aggby, columns=groupcols,
                           margins=margins)
    if 'fill_na' in kwargs:
        table.replace([np.nan, np.inf], kwargs.pop('fill_na'), inplace=True)

    if styling:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', RuntimeWarning)
            mplc_fxn()
        return format_cells(report=table, style=styling)
    else:
        return table


def pd_default(data, func, fill_na, subset=None):
    """
    Returns various statistics (correlation/describe) for the 
    given data set. These statistics come via pandas' default
    describe and correlation methods

    Parameters
    ----------
        data : <DataFrame>
            Data set to be manipulated
        func : <string>
            Native pandas descriptive function to be used
        fill_na : <float>
            Value to be used when filling in the data's NaN values
        subset : <list>
            Subset of columns to be returned

    Returns
    -------
        A statistical description of the original data set provided,
        featuring either stats describing how each data set feature
        correlates to others ('correlation'), or descriptive stats
        of each feature per sé ('describe')

    Raises
    ------
        AttributeError:
            If value other than correlation/describe is given to 'func'
        KeyError:
            If any column in subset param is not a column in the data set

    Examples
    --------
        >>> import tqpy.analysis.functions as tqf
        >>> import tqpy.analysis.reporter as tqr
        >>> data = tqf.load_data(file='../test/data/mb_test_data_small.csv', low_memory=False)
        >>> r = tqr.pd_default(data=data, func='correlation', fill_na=None)
        >>> r.head()

                            ttc      ipts      hour       min  test_flag  \
            ttc        1.000000 -0.005948  0.050419  0.034304        NaN   
            ipts      -0.005948  1.000000 -0.108605 -0.051671        NaN   
            hour       0.050419 -0.108605  1.000000  0.026037        NaN   
            min        0.034304 -0.051671  0.026037  1.000000        NaN   
            test_flag       NaN       NaN       NaN       NaN        NaN

        Alternatively
        >>> r = tqr.pd_default(data=data, func='describe', fill_na=-999.0, subset=['ttc','ipts'])
        >>> r.head()

                           ttc         ipts
            count  1000.000000  1000.000000
            mean    139.140000   514.897000
            std    1714.012505  4342.645426
            min       0.000000    -1.000000
            25%       8.000000    -1.000000
    """
    if subset:
        for c in subset:
            if c not in list(data.columns.values):
                raise KeyError("'%s' is not a column in the data set.\n" % c)

    if fill_na:
        data.replace([np.nan, np.inf], fill_na, inplace=True)
    elif not fill_na:
        data.replace([np.nan, np.inf], -999.0, inplace=True)

    if subset:
        data = data[subset]

    if func.lower() == 'correlation':
        return data.corr()
    elif func.lower() == 'describe':
        return data.describe()
    else:
        raise AttributeError("'func' param requires either 'correlation' or 'describe'. %s given.\n" % func)


def data_check(data):
    """
    Returns descriptive stats of each data set feature and prints
    these stats to the console

    Parameters
    ----------
        data : <DataFrame>
            Data set to be manipulated

    Returns
    -------
        aggvals : <list>
            An aggregated list featuring [n_positions, n_names, n_uniques, n_dtypes]

    Examples
    --------
        >>> import tqpy.analysis.functions as tqf
        >>> import tqpy.analysis.reporter as tqr
        >>> data = tqf.load_data(file="../test/data/mb_test_data_small.csv", low_memory=False)
        >>> r = tqr.data_check(data=data)
        >>> r.head()

                Size: 249999 x 41

                   Position       Name  Unique Values Data Type
                0         0        ttc           2707     int64
                1         1       ipts           6080     int64
                2         2       hour             24     int64
                3         3        min             60     int64
                4         4  test_flag              1     int64
    """
    print("Size: %d x %d\n" % data.shape)

    col_pos = list(map(lambda x: x, range(data.shape[1])))
    col_names = list(map(lambda x: x, data.columns.values))
    col_unis = list(map(lambda x: len(data[x].unique()), data.columns.values))
    col_types = list(map(lambda x: data[x].dtype, data.columns.values))

    report_names = ['Position', 'Name', 'Unique Values', 'Data Type']

    report_frame = pd.DataFrame(dict(zip(report_names, [col_pos, col_names, col_unis, col_types])))
    report_frame = report_frame.ix[:, ['Position', 'Name', 'Unique Values', 'Data Type']]

    return report_frame
