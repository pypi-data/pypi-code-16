""" Contains RMSSD and normalization algorithms for HRV. """

import math
from collections import deque
from statistics import mean

def _sum_of_squares_of_successive_differences(values):
    """ Helper function: calculates the 'SSD' part of 'RMSSD' "" 
 
    :param values: (list)
    :return sum_of_squares: (float)
    """
    squares = []
    for idx in range(0,len(values)-1):
        squares.append(math.pow((values[idx] - values[idx+1]), 2))
    return sum(squares)

def _sum_of_squares_of_difference_from_mean(values):
    """ Helper function: calculates the inner sum of squares for the sdnn function.

    :param values: (list)
    :return sum_of_squares: (float)
    """
    squares = []
    for idx in range(0,len(values)-1):
        squares.append(math.pow((values[idx] - mean(values)), 2))
    return sum(squares)

def nn50(values):
    """ Returns the mean number of times per hour in which the change in consecutive normal 
    sinus (NN) intervals exceeds 50 milliseconds.
    
    :param values: (list)
    :return diff_gt_50: (int)
    """
    # https://www.physionet.org/physiotools/pNNx/ """
    # calculate the variance in the difference between successive NN intervals.
    diff_gt_50 = 0
    for idx in range(0,len(values)-1):
        diff = abs(values[idx+1]-values[idx])
        if diff > 50:
            diff_gt_50 += 1
    return diff_gt_50 

def pnn50(values):
    """ Returns the *proportion* of intervals in the series that exceeded 50 milliseconds.

    :param values: (list)
    :return pNN50: (float)
    """
    return float(nn50(values)) / float(len(values))

def sdnn(values):
    """ SDNN, the standard deviation of NN intervals. Often calculated over a 24-hour period. SDANN, the standard deviation of the average NN intervals calculated over short periods, usually 5 minutes. SDANN is therefore a measure of changes in heart rate due to cycles longer than 5 minutes. SDNN reflects all the cyclic components responsible for variability in the period of recording, therefore it represents total variability.
    """
    return math.sqrt( (1/(len(values)-1)) * _sum_of_squares_of_difference_from_mean(values) )

def rmssd(values):
    """ Given a list of values (int or float), returns a single value calculated as the
    root of the sum of the squares of the successive differences between values. 

    :param values: (list)
    :return rmmsd: (float)
    """
    # https://bestguessorbetter.wordpress.com/2014/11/26/rmssd-and-sdnn/
    return math.sqrt( (1/len(values)) * _sum_of_squares_of_successive_differences(values) ) 

def normalize_rr(values, normalization=20.0, max_gap=2100, min_gap=200, fill_gaps=False, drop_values=True):
    """ Smooths RR values by doing two-pass check across each value, comparing it to the values
    before and after it:

    1a) checking for gaps: any value falling above max_gap.  When encountered, 
       we determine the length of the absence of heartbeat data by dividing the average RR 
       into the length of the gap.

        IF fill_gaps is True, resultant array contains -1 values for each "missing" value.
        (Otherwise, these too-large "gap" values are simply dropped.)

    1b) checking for too-small values: any value falling below min_gap. These values
        are discarded.

    2) checking for successive differences that are greater than `normalization` percentage.
       When such a value is found, it is replaced by the average of the previous (n) and the 
       following (n+2) value.

        IF drop_values is True, these abnormal values are dropped from the resultant list.
        If drop_values is False, these values are "smoothed" by replacing the abberant value with
            a value equal to the mean of the aberrance and the current RR average.

    :param values: (list) integers or floats
    :param normalization: (float) percentage value (0 to 100) [default: 20.0]
    :param max_gap: (float) millisecond threshold above which we consider this a "gap" in heartbeat detection [default: 2100]
    :param min_gap: (float) discard values under this millisecond threshold [default: 200]
    :param fill_gaps: (bool) [default: False]
    :param drop_values: (bool) [default: True]
    """
    # convenience values to make code look neater.
    norm_plus = (100+normalization)/100
    norm_minus = (100-normalization)/100

    # PASS 1: gaps
    new_vals = []

    rr_avg = 800        # a reasonable starting point
    vals_for_avg = [rr_avg]

    # detect "gaps" by assuming that any heartbeat interval greater than 2 seconds
    # probably means we missed something.
    for idx in range(0,len(values)):
        if values[idx] > max_gap:
            if fill_gaps:
                # fill -1s for all presumably missing rrs
                new_vals = new_vals + [-1 for item in range(int(values[idx]/rr_avg))]
        elif values[idx] < min_gap:
            # toss out very low values
            continue
        else:
            new_vals.append(values[idx])
            vals_for_avg.append(values[idx])
            # recalc rr_avg
            rr_avg = mean(vals_for_avg)

    # PASS 1.5: Drop any first-values too far outside the average.
    if new_vals[0] > (rr_avg * norm_plus) or new_vals[0] < (rr_avg * norm_minus):
        values = new_vals[1:]
    else:
        values = new_vals

    out_values = []
    # PASS 2: normalization
    for idx in range(1,len(values)):
        preval = values[idx-1]
        curval = values[idx]
        try:
            nextval = values[idx]
        except IndexError:
            # we're at the end of the list; fudge it.
            nextval = curval

        # if this is a gap (-1), keep it and move to the next one.
        if curval == -1:
            out_values.append(curval)
            continue

        # if this appears to be a misreading, normalize it to its surrounding values.
        if curval > (norm_plus * preval) or curval < (norm_minus * preval):
            # make sure we're not adjacent to a gap.
            if preval > 0 and nextval > 0:
                if not drop_values:
                    # replace this value with a value equal to the average between preval and nextval
                    out_values.append(mean((preval, nextval)))
            elif preval > 0 and nextval == -1:
                if not drop_values: 
                    # we're on the LEFT edge of a gap; fill with preval averaged against rr_avg
                    out_values.append(mean((preval, rr_avg)))
            elif preval == -1 and nextval > 0:
                if not drop_values:
                    # we're on the RIGHT edge of a gap; fill with rr_avg averaged against nextval
                    out_values.append(mean((rr_avg, nextval)))

        else:
            out_values.append(curval)

    return out_values

def nn_to_rolling_hrv(nn_values, window=12):
    """ Takes a list of numbers representing NN intervals and returns a list of RMSSD-based
    values representing a rolling HRV calculated across a subsequence of values whose 
    length can be controlled via the `window` parameter.

    -1 values in the sequence are interpreted as gaps in measurement and transferred 
    directly into the resultant rolling hrv calculation verbatim.

    :param nn_values: (list)
    :param window: (int) [default: 12]
    :return: (list) rolling hrv calculations suitable for graphing HRV over time.
    """

    # keep track of our current average RR -- part of how we deduce how to "fill" apparent
    # gaps in rr coverage.
    rrs = deque(nn_values[:window-1])
    hrvs = []
    for idx in range(window,len(nn_values)-1):
        if nn_values[idx] == -1:
            try:
                rrs.popleft()
            except IndexError:
                # long gap!
                pass
            hrvs.append(nn_values[idx])

        else:
            rrs.append(nn_values[idx])
            if len(rrs) > window:
                rrs.popleft()
            hrvs.append(rmssd(rrs))

    return hrvs


def hrv_baseline(hrv_sequence):
    # http://www.hrv4training.com/blog/interpreting-hrv-trends

    return mean([float(hrv) for hrv in hrv_sequence])


