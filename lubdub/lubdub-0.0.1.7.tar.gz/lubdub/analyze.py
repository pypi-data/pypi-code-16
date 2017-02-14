from statistics import mean

from .load import load_EliteHRV_rrs, load_HRV4Training_rrs
from .calc import sdnn, rmssd, pnn50, nn50, normalize_rr
from .graph import PlotHRV

class Measurement(object):

    @classmethod
    def from_EliteHRV(cls, filepath, **kwargs):
        rrs = load_EliteHRV_rrs(filepath)
        return cls(rrs)

    @classmethod
    def from_HRV4Training(cls, filepath, **kwargs):
        rrs = load_HRV4Training_rrs(filepath)
        return cls(rrs)

    def __init__(self, rr_intervals, *, normalization=50.0, drop_values=True, **kwargs):
        self.rrs = rr_intervals
        self.nns = normalize_rr(self.rrs, normalization=normalization, fill_gaps=False, drop_values=drop_values)
        self.normalization = normalization
        self.drop_values = drop_values

        # all the calculations
        self.plot = PlotHRV(nn_intervals=self.nns)
        self.sdnn = sdnn(self.nns)
        self.nn50 = nn50(self.nns)
        self.rmssd = rmssd(self.nns)
        self.pnn50 = pnn50(self.nns)

        self.mean_hrv = mean(self.plot['y_values'])

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

