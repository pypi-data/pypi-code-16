""" HRV: Submodule providing standalone calculations, graphing utilities, etc. """

from .calc import nn_to_rolling_hrv, rmssd, normalize_rr
from .exceptions import LubDubError
from .load import load_plaintext_rrs


def PlotHRV(rr_intervals=None, nn_intervals=None):
    """ Takes a list of un-normalized rr_intervals and returns a dictionary containing 
    'y_values' (array) and 'y_range' (tuple) plotting HRV over time.

    :param rr_intervals: (list) 
    :return graph: (dict)
    """
    if rr_intervals:
        rolling_hrv = nn_to_rolling_hrv(normalize_rr(rr_intervals))
    elif nn_intervals:
        rolling_hrv = normalize_rr(rr_intervals)
    else:
        raise LubDubError('Missing argument: supply either rr_intervals or nn_intervals to PlotHRV.')

    return {'y_values': rolling_hrv,
            'y_range': (min(rolling_hrv), max(rolling_hrv))
           }

