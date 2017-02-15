from ..tecutil import (_tecutil, Index, IndexRange, IndexSet, color_spec,
                       flatten_args, lock_attributes, sv)
from .. import session
from ..constant import *

@lock_attributes
class ReferenceVector(object):
    pass

@lock_attributes
class Vector2D(object):
    def __init__(self, plot):
        self.plot = plot
        self._sv = [sv.GLOBALTWODVECTOR]

    def _get_style(self, rettype, *svargs):
        svargs = self._sv + list(svargs)
        return session.get_style(rettype, *svargs, uniqueid=self.plot.frame.uid)

    def _set_style(self, value, *svargs):
        svargs = self._sv + list(svargs)
        session.set_style(value, *svargs, uniqueid=self.plot.frame.uid)

    @property
    def u_variable_index(self):
        return self._get_style(Index, sv.UVAR)
    @u_variable_index.setter
    def u_variable_index(self, index):
        self._set_style(Index(index), sv.UVAR)

    @property
    def u_variable(self):
        return self.plot.frame.dataset.variable(self.u_variable_index)
    @u_variable.setter
    def u_variable(self, variable):
        self.u_variable_index = variable.index

    @property
    def v_variable_index(self):
        return self._get_style(Index, sv.VVAR)
    @v_variable_index.setter
    def v_variable_index(self, index):
        self._set_style(Index(index), sv.VVAR)

    @property
    def v_variable(self):
        return self.plot.frame.dataset.variable(self.v_variable_index)
    @v_variable.setter
    def v_variable(self, variable):
        self.v_variable_index = variable.index

class Vector3D(Vector2D):
    def __init__(self, plot):
        self.plot = plot
        self._sv = [sv.GLOBALTHREEDVECTOR]

    @property
    def w_variable_index(self):
        return self._get_style(Index, sv.WVAR)
    @w_variable_index.setter
    def w_variable_index(self, index):
        self._set_style(Index(index), sv.WVAR)

    @property
    def w_variable(self):
        return self.plot.frame.dataset.variable(self.w_variable_index)
    @w_variable.setter
    def w_variable(self, variable):
        self.w_variable_index = variable.index
