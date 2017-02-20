"""volume.py contains the Volume composite resource for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from json import dumps
from numpy import ndarray
from six import string_types
from traitlets import validate

from .base import BaseMesh
from .base import CompositeResource
from .data import DataArray
from .options import ColorOptions
from .options import MeshOptions
from .traits import (Array, HasSteno3DTraits, KeywordInstance, Renamed,
                     Repeated, String, Vector)


class _Mesh3DOptions(MeshOptions):
    pass


class _VolumeOptions(ColorOptions):
    pass


class Mesh3DGrid(BaseMesh):
    """Contains spatial information of a 3D grid volume."""

    h1 = Array(
        help='Tensor cell widths, x-direction',
        shape=('*',),
        dtype=(float, int)
    )
    h2 = Array(
        help='Tensor cell widths, y-direction',
        shape=('*',),
        dtype=(float, int)
    )
    h3 = Array(
        help='Tensor cell widths, z-direction',
        shape=('*',),
        dtype=(float, int)
    )
    x0 = Renamed('O')
    O = Vector(
        help='Origin vector',
        default_value=[0., 0., 0.]
    )
    U = Vector(
        help='Orientation of h1 axis',
        default_value='X'
    )
    V = Vector(
        help='Orientation of h2 axis',
        default_value='Y'
    )
    W = Vector(
        help='Orientation of h3 axis',
        default_value='Z'
    )
    opts = KeywordInstance(
        help='Mesh3D Options',
        klass=_Mesh3DOptions,
        allow_none=True
    )

    @property
    def nN(self):
        """ get number of nodes """
        return (len(self.h1)+1) * (len(self.h2)+1) * (len(self.h3)+1)

    @property
    def nC(self):
        """ get number of cells """
        return len(self.h1) * len(self.h2) * len(self.h3)

    def _nbytes(self, arr=None):
        filenames = ('h1', 'h2', 'h3', 'O', 'U', 'V', 'W')
        if arr is None:
            return sum(self._nbytes(fn) for fn in filenames)
        if isinstance(arr, string_types) and arr in filenames:
            if getattr(self, arr, None) is None:
                return 0
            arr = getattr(self, arr)
        if isinstance(arr, ndarray):
            return arr.astype('f4').nbytes
        raise ValueError('Mesh3DGrid cannot calculate the number of '
                         'bytes of {}'.format(arr))

    def _get_dirty_data(self, force=False):
        datadict = super(Mesh3DGrid, self)._get_dirty_data(force)
        dirty = self._dirty_traits
        if force or ('h1' in dirty or 'h2' in dirty or 'h3' in dirty):
            datadict['tensors'] = dumps(dict(
                h1=self.h1.tolist(),
                h2=self.h2.tolist(),
                h3=self.h3.tolist()
            ))
        if force or any([item in dirty for item in
                         ['O', 'U', 'V', 'W', 'h1', 'h2', 'h3']]):
            datadict['OUVZ'] = dumps(dict(
                O=self.O.tolist(),
                U=Vector.as_length(self.U, self.h1.sum()).tolist(),
                V=Vector.as_length(self.V, self.h2.sum()).tolist(),
                Z=Vector.as_length(self.W, self.h3.sum()).tolist()
            ))
        return datadict

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        mesh = Mesh3DGrid(
            title=kwargs['title'],
            description=kwargs['description'],
            h1=json['tensors']['h1'],
            h2=json['tensors']['h2'],
            h3=json['tensors']['h3'],
            O=json['OUVZ']['O'],
            U=json['OUVZ']['U'],
            V=json['OUVZ']['V'],
            W=json['OUVZ']['Z'],
            opts=json['meta']
        )
        return mesh

    @classmethod
    def _build_from_omf(cls, omf_geom, omf_project):
        mesh = Mesh3DGrid(
            h1=omf_geom.tensor_u,
            h2=omf_geom.tensor_v,
            h3=omf_geom.tensor_w,
            O=omf_geom.origin + omf_project.origin,
            U=omf_geom.axis_u,
            V=omf_geom.axis_v,
            W=omf_geom.axis_w
        )
        return mesh


class _VolumeBinder(HasSteno3DTraits):
    """Contains the data on a 3D volume with location information"""
    location = String(
        help='Location of the data on mesh',
        choices={
            'CC': ('CELLCENTER'),
            # 'N': ('NODE', 'VERTEX', 'CORNER')
        }
    )
    data = KeywordInstance(
        help='Data',
        klass=DataArray
    )


class Volume(CompositeResource):
    """Contains all the information about a 3D volume"""
    mesh = KeywordInstance(
        help='Mesh',
        klass=Mesh3DGrid,
    )
    data = Repeated(
        help='Data',
        trait=KeywordInstance(klass=_VolumeBinder)
    )
    opts = KeywordInstance(
        help='Options',
        klass=_VolumeOptions,
        allow_none=True
    )

    def _nbytes(self):
        return self.mesh._nbytes() + sum(d.data._nbytes() for d in self.data)

    @validate('data')
    def _validate_data(self, proposal):
        """Check if resource is built correctly"""
        for ii, dat in enumerate(proposal['value']):
            assert dat.location == 'CC'  # in ('N', 'CC')
            valid_length = (
                proposal['owner'].mesh.nC if dat.location == 'CC'
                else proposal['owner'].mesh.nN
            )
            if len(dat.data.array) != valid_length:
                raise ValueError(
                    'volume.data[{index}] length {datalen} does not match '
                    '{loc} length {meshlen}'.format(
                        index=ii,
                        datalen=len(dat.data.array),
                        loc=dat.location,
                        meshlen=valid_length
                    )
                )
        return proposal['value']


__all__ = ['Volume', 'Mesh3DGrid']
