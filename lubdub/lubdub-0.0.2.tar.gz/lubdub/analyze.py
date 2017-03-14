from statistics import mean

from .load import load_EliteHRV_rrs, load_HRV4Training_rrs
from .calc import sdnn, rmssd, pnn50, nn50, normalize_rr
from .graph import PlotHRV


def calculate_calm_time(nns, hrv_plot, hrv_baseline, calm_threshold=1.2):
    """ Calculates the approximate time (in seconds) spent "calm" by observing
    how many rolling HRV calculations occur above the given HRV baseline.
    How far above the baseline they need to be to count is set by the 
    calm_threshold parameter (e.g. 1.2x means 120% above baseline). 
    
    :param nns: (list)
    :param hrv_plot: (list)
    :param hrv_baseline: (float)
    :param calm_threshold: (float) [default: 1.2]
    :return calm_time: (float) approximate time in seconds spent with HRV above baseline (+threshold %)
    """
    # how long, on average, was the distance between heartbeat peaks?
    avg_heartbeat_time = mean(nns)

    # grab all values that occur above baseline (+threshold %) 
    pct_above_baseline = []
    for item in hrv_plot:
        if item > hrv_baseline * calm_threshold:
            pct_above_baseline.append(item)
    calm_time = 0
    for item in pct_above_baseline:
        calm_time += avg_heartbeat_time
    return calm_time / 1000


def calculate_stress_time(nns, hrv_plot, hrv_baseline, stress_threshold=.8):
    """ Calculates the approximate time (in seconds) spent "stressed out" by
    observing how many rolling HRV calculations occur under the given HRV 
    baseline, modulated by the stress_threshold parameter (e.g. .8x means
    80% of baseline). 
    
    :param nns: (list)
    :param hrv_plot: (list)
    :param hrv_baseline: (float)
    :param stress_threshold: (float) [default: .8]
    :return stress_time: (float) approximate time in seconds spent with HRV below baseline (-threshold %)
    """
    # how long, on average, was the distance between heartbeat peaks?
    avg_heartbeat_time = mean(nns)

    # grab all values that occur below baseline (-threshold %) 
    pct_below_baseline = []
    for item in hrv_plot:
        if item < hrv_baseline * stress_threshold:
            pct_below_baseline.append(item)
    stress_time = 0
    for item in pct_below_baseline:
        stress_time += avg_heartbeat_time
    return stress_time / 1000


class Measurement(object):

    @classmethod
    def from_EliteHRV(cls, filepath, **kwargs):
        rrs = load_EliteHRV_rrs(filepath)
        return cls(rrs, **kwargs)

    @classmethod
    def from_HRV4Training(cls, filepath, **kwargs):
        rrs = load_HRV4Training_rrs(filepath)
        return cls(rrs, **kwargs)

    def __init__(self, rr_intervals, *, normalization=50.0, drop_values=True, **kwargs):
        self.rrs = rr_intervals
        self.nns = normalize_rr(self.rrs, normalization=normalization, fill_gaps=False, drop_values=drop_values)
        self.normalization = normalization
        self.drop_values = drop_values
        self.calm_threshold = kwargs.get('calm_threshold', 1.2)
        self.stress_threshold = kwargs.get('stress_threshold', .8)

        # all the calculations
        self.plot = PlotHRV(nn_intervals=self.nns)
        self.sdnn = sdnn(self.nns)
        self.nn50 = nn50(self.nns)
        self.rmssd = rmssd(self.nns)
        self.pnn50 = pnn50(self.nns)

        self.mean_hrv = mean(self.plot['y_values'])

        self.hrv_baseline = kwargs.get('hrv_baseline', None)
        if self.hrv_baseline:
            self.calm_time = calculate_calm_time(self.nns, self.plot['y_values'], self.hrv_baseline, self.calm_threshold)
            self.stress_time = calculate_stress_time(self.nns, self.plot['y_values'], self.hrv_baseline, self.stress_threshold)
        else:
            self.calm_time = None
            self.stress_time = None

    def analysis(self):
        return {
                'sdnn': self.sdnn,
                'rmssd': self.rmssd,
                'nn50': self.nn50,
                'mean_hrv': self.mean_hrv,
               }                

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return '''Sample length: {rr_length}\n\nRMSSD: {a.rmssd}\n\nSDNN: {a.sdnn}\n\nNN50: {a.nn50}\n\nMean HRV: {a.mean_hrv}\n'''.format(a=self, rr_length=len(self.rrs))

