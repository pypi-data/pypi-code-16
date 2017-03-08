"""
Functions.py

Functions module contains various functions that act as helper functions
to other tqpy modules. Unlike the utility functions found in utils.py,
the functions module's helper functions manipulate and interact with data
directly.

A compact, scalable, statistical analysis, and reporting package built on top of
pandas, and bokeh.

Author : Rashad Alston <ralston@yahoo-inc.com>
Python : 3.5.1

License: BSD 3 Clause

*************************************************************************
"""

import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource, LabelSet

from ..utils import pckg_check
from ..utils import py_check

pckg_check()
py_check()


def remove_aliases(headers, acros=False):
    """
    Sanitizes the Dataframe column values [useful when using
    database alias is in SQL/Hive/Pig query (e.g., "alias.column_name")]

    Parameters
    ----------
        headers : <DataFrame>
            Data set to be manipulated
        acros : <bool>, default=False
            Whether or not to convert column names to acronyms

    Returns
    -------
        names : <list>
            List of filtered column names

    Example
    -------
        >>> data = load_data('../test/data/mb_test_data_small.csv', low_memory=False)
        >>> data.columns = remove_aliases(headers=data.columns.values, acros=False)
    """

    names = list(headers)

    for i in range(len(names)):

        split = list(names[i])
        if '.' in split:
            idx = split.index('.')
            names[i] = names[i][idx + 1:]

    if acros:

        new_cols = []

        """
         Note
         -----
         Block below is supposed to keep "ip_ts" feature name from being
         filtered into an acronym (as 'it'). Isn't 'completely' necessary
         so for now it's commented out (may be uncommented later)

         if 'ip_ts' in names:
             idx = np.where(names == 'ip_ts')
             names[idx] = 'ipts'
        """

        for i in range(len(names)):

            # If the the feature name is able to be split then do so
            split = names[i].split('_')
            if len(split) > 1:

                # Keep 'id' at the end of the acronymed feature name
                if split[-1] == 'id':
                    name_list = [val[0] for val in split[:-1]] + [split[-1]]
                else:
                    name_list = [val[0] for val in split]

                new_name = ''.join([item for item in name_list])
            else:
                new_name = split[0]

            new_cols.append(new_name)
        return new_cols
    return names


def frame_from_list(data, dist, feature, top_n):
    """
    Creates a DataFrame from a distribution report featuring the top n
    values from that distribution

    Parameters
    ----------
        data : <DataFrame>
            Data set to be manipulated
        dist : <DataFrame>
            Distribution report returned by general_distribution()
        feature : <string>
            Feature on which to segment data
        top_n : <int>
            Top n values to take from distribution


    Returns
    -------
        frame : <DataFrame>
            DataFrame object containing the top n features from the
            given distribution report

    Example
    -------
        >>> import tqpy.analysis.functions as tqf
        >>> import tqpy.analysis.reporter as tqr
        >>> data = load_data('../test/data/mb_test_data_small.csv', low_memory=False)
        >>> r = tqr.general_distribution(data, groupby=['publisher_id'], aggby={'clicks':np.sum} \
                                         sortby='clicks')
        >>> top_10_pubs = tqf.frame_from_list(data=data, dist=r, feature='publisher_id', top_n=10)
    """

    report = dist.head(top_n)
    vals = list(report.index.values)

    bucket = []
    for v in vals:
        sdf = data.loc[data[feature] == v]
        bucket.append(sdf)

    frame = pd.concat([f for f in bucket])

    return frame


def shuffle_frame(data):
    """
    Randomly shuffles a given Dataframe object

    Parameters
    ----------
        data : DataFrame
            DataFrame object to be manipulated

    Returns
    -------
        data : DataFrame
            Original Dataframe with randomly shuffled rows

    Raises
    ------
        TypeError : If data param isn't type Dataframe

    Example
    -------
        >>> import tqpy.analysis.functions as tqf
        >>> data = tqf.load_data('../test/data/mb_test_data_small.csv', low_memory=False)
        >>> data = tqf.shuffle_frame(data)
    """

    if not isinstance(data, pd.DataFrame):
        raise TypeError("data param must be type Dataframe. Type %s given.\n" % type(data))

    return data.reindex(np.random.permutation(data.index))


def load_data(file, sanitize_cols=True, **kwargs):
    """
    Loads data file using pandas I/O and calls remove_aliases()
    function automatically when data is loaded

    Parameters
    ----------
        file : <string>
            Path (and name) of file being loaded
        sanitize_cols : <boolean>, default=True
            Whether or not to call the sanitize_cols function on load

            kwargs
            ------
                Any additional kwargs passed to pandas I/O

    Returns
    -------
        df : <DataFrame>
            Data set loaded into a DataFrame object

    Raises
    ------
        FileNotFoundError : If file can't be found

    Example
    -------
        >>> import tqpy.analysis.functions as tqf
        >>> data = tqf.load_data('../test/data/mb_test_data_small.csv', low_memory=False)
    """

    print("Loading data...\n")

    try:
        df = pd.read_csv(file, **kwargs)

        if sanitize_cols:
            df.columns = remove_aliases(headers=df.columns.values)

        print("Data shape: %d x %d\n" % df.shape)

        return df

    except FileNotFoundError:
        raise FileNotFoundError("Couldn't find file : '%s'.\n" % file)
        

def generate_timeplot_labels(frame, key, show_labels):
    """
    Generates glyph labels to be used in visualizer.time_plot

    Parameters
    ----------
        frame : <DataFrame>
            DataFrame object to base labels on
        key : <string>
            The key in the time_plot's 'aggby' feature
        show_labels : <boolean>.,
            Whether or not to create LabelSet for plot

    Returns
    -------
        source : <bokeh ColumnDataSouce>
            bokeh source object created based on 'frame' param

        labels : <bokeh LabelSet>
            bokeh label set

    Examples
    --------
        *See use of this function in the visualizer module's
        time_plot function
    """
    frame[key] = [round(val, 2) for val in frame[key]]
    labels = [str(val) for val in frame[key]]
    s = pd.DataFrame({'x': [v[0] for v in list(frame.index.values)],  # pdate
                      'y': frame[key].values,                         # aggregated values
                      'z': [v[1] for v in list(frame.index.values)],  # date
                      'labels': labels})                              # labels (i.e., rounded y values)
    source = ColumnDataSource(s)

    # Set labels for each plot according to the key
    if show_labels:
        labels = LabelSet(x='x', y='y', text='labels', y_offset=16, text_font_size='7pt',
                          text_color='#555555', source=source, text_align='center')

    return source, labels



