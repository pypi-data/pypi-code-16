""" HRV: Submodule providing standalone calculations, graphing utilities, etc. """

from .calc import nn_to_rolling_hrv, rmssd, normalize_rr
from .exceptions import LubDubError
from .load import load_plaintext_rrs


def PlotHRV(rr_intervals=None, nn_intervals=None, window=12):
    """ Takes a list of un-normalized rr_intervals OR normalized nn_intervals, and 
    returns a dictionary containing 'y_values' (array) and 'y_range' (tuple) plotting HRV over time.

    Specify window param to change length of values to use for each successive RMSSD 
    in the rolling HRV calculation.

    :param rr_intervals: (list) [default: None]
    :param nn_intervals: (list) [default: None]
    :param window: (int) [default: 12]
    :return graph: (dict)
    """
    if rr_intervals:
        rolling_hrv = nn_to_rolling_hrv(normalize_rr(rr_intervals), window=window)
    elif nn_intervals:
        rolling_hrv = normalize_rr(rr_intervals, window=window)
    else:
        raise LubDubError('Missing argument: supply either rr_intervals or nn_intervals to PlotHRV.')

    return {'y_values': rolling_hrv,
            'y_range': (min(rolling_hrv), max(rolling_hrv))
           }

