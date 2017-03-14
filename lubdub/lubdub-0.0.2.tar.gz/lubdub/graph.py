from .calc import normalize_rr, nn_to_rolling_hrv
from .exceptions import LubDubError

def PlotHRV(rr_intervals=None, nn_intervals=None, window=12, fill_gaps=True, drop_values=False):
    """ Takes a list of un-normalized rr_intervals OR normalized nn_intervals, and 
    returns a dictionary containing 'y_values' (array) and 'y_range' (tuple) plotting HRV over time.

    Specify window param to change length of values to use for each successive RMSSD 
    in the rolling HRV calculation.

    :param rr_intervals: (list) [default: None]
    :param nn_intervals: (list) [default: None]
    :param window: (int) [default: 12]
    :param fill_gaps: (bool) [default: True]
    :param drop_values: (bool) [default: False]
    :return graph: (dict)
    """
    if rr_intervals:
        rolling_hrv = nn_to_rolling_hrv(normalize_rr(rr_intervals, fill_gaps=fill_gaps, drop_values=drop_values), 
                                        window=window)
    elif nn_intervals:
        rolling_hrv = nn_to_rolling_hrv(nn_intervals, window=window)
    else:
        raise LubDubError('Missing argument: supply either rr_intervals or nn_intervals to PlotHRV.')

    return {'y_values': rolling_hrv,
            'y_range': (min(rolling_hrv), max(rolling_hrv))
           }

