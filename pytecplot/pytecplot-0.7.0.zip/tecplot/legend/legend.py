from ..tecutil import sv
from .. import session


class Legend(object):
    @property
    def show(self):
        return self._get_style(bool, sv.SHOW)
    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)


class ContourLegend(Legend):
    def __init__(self, contour):
        self.contour = contour
        self._sv = contour._sv + [sv.LEGEND]

    def _get_style(self, rettype, *svargs):
        svargs = self._sv + list(svargs)
        return session.get_style(rettype, *svargs,
                                 offset1=self.contour.index,
                                 uniqueid=self.contour.plot.frame.uid)
    def _set_style(self, value, *svargs):
        svargs = self._sv + list(svargs)
        session.set_style(value, *svargs, offset1=self.contour.index,
                          uniqueid=self.contour.plot.frame.uid)


class LineLegend(Legend):
    def __init__(self, plot):
        self.plot = plot
        self._sv = [sv.GLOBALLINEPLOT, sv.LEGEND]

    def _get_style(self, rettype, *svargs):
        svargs = self._sv + list(svargs)
        return session.get_style(rettype, *svargs, uniqueid=self.plotframe.uid)
    def _set_style(self, value, *svargs):
        svargs = self._sv + list(svargs)
        session.set_style(value, *svargs, uniqueid=self.plot.frame.uid)
