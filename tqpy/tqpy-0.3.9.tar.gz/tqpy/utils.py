"""
Utils.py

The Utils module contains various utility functions that serve as helper
functions to various aspects of the reporter and visualizer modules.


A compact, scalable, statistical analysis, and reporting package built on top of
pandas, and bokeh.

Author : Rashad Alston <ralston@yahoo-inc.com>
Python : 3.5.1

License: BSD 3 Clause

*************************************************************************
"""

import random
import sys
import os
import warnings
import pkgutil

import pandas as pd

from bokeh.io import output_notebook

import matplotlib.colors as mplc
import matplotlib.cm as cm


__all__ = ['surpress_framecopy_warning',
           'full_frame_display',
           'reset_frame_display',
           'display_bokeh_inline',
           'listed_color_map',
           'display_cellwidth_full',
           'hide_code_cells']


def pckg_check():
    """
    Checks to make sure that the required packages are installed. Serves
    as a double-check to 'pip install requirements.txt'

    Returns
    -------
        res : <bool>, True
            If all necessary packages are successfully found

    Raises
    ------
        ImportError:
            If any required package can not be found via pkgutil
    """
    res = True
    for pckg in ['pandas', 'numpy', 'matplotlib', 'bokeh']:
        if not pkgutil.find_loader(pckg):
            raise ImportError("%s package not found. Please check requirements.txt and install the "
                              "suggested version of %s." % (pckg, pckg))
    return res


def py_check():
    """
    Checks to make sure that version of Python being used is >= 3.2

    Returns
    -------
        res: <bool>, True
            If all necessary packages are successfully found

    Raises
    ------
        EnvironmentError:
            If PYTHONPATH environment variable is not set in .bash_profile
        ImportError:
            If version of Python found is not >= 3.2
    """
    res = True
    pypath = os.getenv('PYTHONPATH', None)
    if not pypath:
        raise EnvironmentError("'PYTHONPATH' environment variable is not set. Make sure PYTHONPATH is set "
                               "is set in .bash_profile.")
    req_version = (3, 2)
    curr_version = (sys.version_info.major, sys.version_info.minor)
    if curr_version < req_version:
        raise ImportError("tqpy package requires at least Python 3.2. Version %d.%d found." % curr_version)
    return res


def surpress_framecopy_warning():
    """
    Surpresses pandas 'manipulating copy of DataFrame' warning
    """
    pd.options.mode.chained_assignment = None  # default='warn'
    return None


def full_frame_display(data):
    """
    Overloads the default pandas set_option() for the data frame, in
    order to display the 'full' frame

    Parameters
    ----------
        data : <DataFrame>
            DataFrame object to be manipulated and printed to console

    Examples
    --------
        >>> import tqpy.analysis.functions as tqf
        >>> data = tqf.load_data("../test/data/mb_test_data_small.csv", low_memory=False)
        >>> full_frame_display(data)
        >>> print(data)
    """
    pd.set_option('display.max_rows', data.shape[0])
    pd.set_option('display.max_columns', data.shape[1])
    return None


def reset_frame_display():
    """
    Resets the option set by full_frame_display()
    """
    pd.reset_option('display.max_rows', 15)
    pd.set_option('display.max_columns', 15)
    return None


def display_bokeh_inline():
    """
    Displays bokeh plots inline (with Jupyter). Used as an alternative
    to output_notebook command in jupyter (makes use of command more
    uniform by not having user import bokeh.io separately in notebook)
    """
    return output_notebook()


def glyph_fxn():
    """
    Surpresses BokehDeracationWarning: Can't supply user-defined source
    AND iterables to glyph
    * Note : current visualizer module's time_plot function supplies a
    user-defined source ONLY, yet this warning still persists - so surpress
    it. https://github.com/bokeh/bokeh/issues/2056
    """
    return warnings.warn('deprecated', DeprecationWarning)


def mplc_fxn():
    """
    Docstring
    """
    return warnings.warn('runtime', RuntimeWarning)


def format_cells(report, style):
    """
    Takes a DataFrame object and formats its cells depending on a cell's value
    (functionality is similar to Excel's conditional formatting (pandas >= 0.17.1)

    Parameters
    ----------
        report : <DataFrame>
            DataFrame object to be formatted

        style : <string>
            Conditional formatting to be applied to report
            Options : 'bar' or 'shade'

    Returns
    -------
        report : <pandas Styler object>
            Styled DataFrame object

    Raises
    ------
        AttributeError : If value passed to style param isn't 'bar' or 'shade'
    """

    if style == 'bar':
        return report.style.bar(color='#FCA09A')
    elif style == 'shade':
        cmap = shade_color_map()
        return report.style.background_gradient(cmap=cmap)
    else:
        raise AttributeError("'conditional_highlight' param takes either 'bar' or 'shade'. '%s' given.\n"
                             % style)


def shade_color_map(start='#46B546', mid='#FABB6D', end='#DA4646'):
    """
    Creates matplotlib color map object to be used by format_cells()

    Parameters
    ---------
        start : <string>, default="#46B546"
            Starting color value for color map
        mid : <string>, default="#FABB6D"
            Middle color value for color map
        end : <string>, default="#DA4646"
            Ending color value for color map

    Returns
    -------
        cmap : <matplotlib colormap object>
            The color map the used for 'shade' option in
            format_cells() function
    """
    cmap = mplc.LinearSegmentedColormap.from_list('custom2', [start, mid, end])
    cm.register_cmap(cmap=cmap)
    return cmap


def listed_color_map(n_colors, seed=None):
    """
    Creates a color map of type list to be used by bokeh plots

    Note : This cmap is used for bokeh only, which works better with
    lists of colors, unlike matplotlib, which works better with cmap objs.

    Parameters
    ----------
        n_colors : <int>
            Number of colors to be returned in cmap
        seed : <int>, default=None
            Random seed to be used when randomly selecting colors

    Returns
    -------
        cmap : <list>
            Color map to be used by bokeh plots

    Raises
    ------
        IndexError:
            If number of colors requested exceeds number of colors
            available

    Examples
    --------
        >>> cmap = listed_color_map(10, seed=42422)
        >>> _ = cmap[7]
    """
    if seed:
        random.seed(seed)
    else:
        num = random.randint(1, 1000000)
        random.seed(num)

    pool = '#DC143C, #DB7093, #FF6347, #FFD700, #E6E6FA, #ADFF2F, #00FFFF, #BC8F8F, #F0FFF0, #FF0000,\
            #FFB6C1, #FFA500, #F0E68C, #FF00FF, #8A2BE2, #6A5ACD, #00FF00, #006400, #9ACD32, #8FBC8B,\
            #008080, #7FFFD4, #4682B4, #B0C4DE, #7B68EE, #000080, #BC8F8F, #B8860B, #D2691E, #8B4513,\
            #98FB98, #D8BFD8, #8B0000, #17202A, #979A9A, #CD5C5C, #7B68EE, #483D8B, #4B0082, #9932CC,\
            #8A2BE2, #663399, #9370DB, #FF00FF, #DDA0DD, #BDB76B, #EEE8AA, #FFFF00, #FFA07A, #D8BFD8,\
            #FF4500, #17202A, #979A9A, #FF69B4, #B8860B, #D2691E, #8B4513, #98FB98, #D8BFD8, #8B0000,\
            #17202A, #979A9A, #CD5C5C, #7B68EE, #483D8B, #4B0082, #9932CC, #8A2BE2, #663399, #9370DB,\
            #FF00FF, #DDA0DD, #BDB76B, #EEE8AA, #FFFF00, #FFA07A, #D8BFD8, #FF4500, #17202A, #979A9A'

    color_pool = [c.strip() for c in pool.split(",")]
    if n_colors < len(color_pool):
        cmap = random.sample(color_pool, n_colors)
        return cmap
    else:
        raise IndexError("Number of requested colors must be <= number of available colors. %s > %s"
                         % (n_colors, len(color_pool)))


def display_cellwidth_full():
    """
    Displays Jupyter Notebook cells with with = 100% of screen size
    """
    from IPython.core.display import display, HTML
    display(HTML('<style>.container { width:100% !important; }</style>'))
    return None


def check_spark_home():
    """
    Checks to make sure that the SPARK_HOME variable is set
    in .bash_profile

    Raises
    ------
        KeyError :
            If SPARK_HOME variable is not set
            (i.e., if the current working system does not have Apache
            Spark access)
    """
    spark_home = os.getenv('SPARK_HOME', None)
    if not spark_home:
        raise EnvironmentError("'SPARK_HOME' environment variable is not set. The tqpy.yspark package can "
                               "only be used on a system that has Apache Spark access.")
    return spark_home


def hide_code_cells():
    """
    Hides the code cells of a notebook (for exporting notebooks without code)

    Returns
    -------
        button : <HTML button>
            Button that toggles code cells on/off
    """
    from IPython.display import HTML

    button = HTML('''<script>
                        code_show=true; 
                        function code_toggle() {
                            if (code_show){
                                $('div.input').hide();
                            } else {
                                $('div.input').show();
                            }
                        code_show = !code_show
                        } 
                        $( document ).ready(code_toggle);
                    </script>
    <form action="javascript:code_toggle()">
        <input style="background-color:#441297;
                      color:#FFFFFF;
                      padding:15px;
                      font-family:Calibri, Arial;
                      border:None;
                      border-radius:2px"
               type="submit" value="Click here to toggle code cells.">
    </form>''')
    
    return button
