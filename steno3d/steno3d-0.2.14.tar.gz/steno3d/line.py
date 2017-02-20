"""line.py contains the Line composite resource for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from numpy import max as npmax
from numpy import min as npmin
from numpy import ndarray
from six import string_types
from traitlets import observe, validate

from .base import BaseMesh
from .base import CompositeResource
from .data import DataArray
from .options import ColorOptions
from .options import Options
from .traits import Array, HasSteno3DTraits, KeywordInstance, Repeated, String


class _Mesh1DOptions(Options):
    view_type = String(
        help='Display 1D lines or tubes/boreholes/extruded lines',
        choices={
            'line': ('lines', 'thin', '1d'),
            'tube': ('tubes', 'extruded line', 'extruded lines',
                     'borehole', 'boreholes')
        },
        default_value='line',
        lowercase=True,
        allow_none=True
    )


class _LineOptions(ColorOptions):
    pass


class Mesh1D(BaseMesh):
    """Contains spatial information of a 1D line set"""
    vertices = Array(
        help='Mesh vertices',
        shape=('*', 3),
        dtype=float
    )
    segments = Array(
        help='Segment endpoint indices',
        shape=('*', 2),
        dtype=int
    )
    opts = KeywordInstance(
        help='Options',
        klass=_Mesh1DOptions,
        allow_none=True
    )

    @property
    def nN(self):
        """ get number of nodes """
        return len(self.vertices)

    @property
    def nC(self):
        """ get number of cells """
        return len(self.segments)

    def _nbytes(self, arr=None):
        if arr is None:
            return self._nbytes('segments') + self._nbytes('vertices')
        if isinstance(arr, string_types) and arr in ('segments', 'vertices'):
            arr = getattr(self, arr)
        if isinstance(arr, ndarray):
            return arr.astype('f4').nbytes
        raise ValueError('Mesh1D cannot calculate the number of '
                         'bytes of {}'.format(arr))

    @observe('segments', 'vertices')
    def _reject_large_files(self, change):
        try:
            self._validate_file_size(change['name'], change['name'])
        except ValueError as err:
            setattr(change['owner'], change['name'], change['old'])
            raise err

    @validate('segments')
    def _validate_seg(self, proposal):
        if npmin(proposal['value']) < 0:
            raise ValueError('Segments may only have positive integers')
        if npmax(proposal['value']) >= len(proposal['owner'].vertices):
            raise ValueError('Segments expects more vertices than provided')
        proposal['owner']._validate_file_size('segments', proposal['value'])
        return proposal['value']

    @validate('vertices')
    def _validate_vert(self, proposal):
        if npmax(proposal['owner'].segments) >= len(proposal['value']):
            raise ValueError('Segments expects more vertices than provided')
        proposal['owner']._validate_file_size('vertices', proposal['value'])
        return proposal['value']

    def _get_dirty_files(self, force=False):
        files = super(Mesh1D, self)._get_dirty_files(force)
        dirty = self._dirty_traits
        if 'vertices' in dirty or force:
            files['vertices'] = \
                self.traits()['vertices'].serialize(self.vertices)
        if 'segments' in dirty or force:
            files['segments'] = \
                self.traits()['segments'].serialize(self.segments)
        return files

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        mesh = Mesh1D(
            title=kwargs['title'],
            description=kwargs['description'],
            vertices=Array.download(
                url=json['vertices'],
                shape=(json['verticesSize']//12, 3),
                dtype=json['verticesType']
            ),
            segments=Array.download(
                url=json['segments'],
                shape=(json['segmentsSize']//8, 2),
                dtype=json['segmentsType']
            ),
            opts=json['meta']
        )
        return mesh

    @classmethod
    def _build_from_omf(cls, omf_geom, omf_project):
        mesh = Mesh1D(
            vertices=(omf_geom.vertices.array +
                      omf_geom.origin +
                      omf_project.origin),
            segments=omf_geom.segments.array
        )
        return mesh


class _LineBinder(HasSteno3DTraits):
    """Contains the data on a 1D line set with location information"""
    location = String(
        help='Location of the data on mesh',
        choices={
            'CC': ('LINE', 'FACE', 'CELLCENTER', 'EDGE', 'SEGMENT'),
            'N': ('VERTEX', 'NODE', 'ENDPOINT')
        }
    )
    data = KeywordInstance(
        help='Data',
        klass=DataArray
    )


class Line(CompositeResource):
    """Contains all the information about a 1D line set"""
    mesh = KeywordInstance(
        help='Mesh',
        klass='Mesh1D'
    )
    data = Repeated(
        help='Data',
        trait=KeywordInstance(klass=_LineBinder),
        allow_none=True
    )
    opts = KeywordInstance(
        help='Options',
        klass=_LineOptions,
        allow_none=True
    )

    def _nbytes(self):
        return self.mesh._nbytes() + sum(d.data._nbytes() for d in self.data)

    @validate('data')
    def _validate_data(self, proposal):
        """Check if resource is built correctly"""
        for ii, dat in enumerate(proposal['value']):
            assert dat.location in ('N', 'CC')
            valid_length = (
                proposal['owner'].mesh.nC if dat.location == 'CC'
                else proposal['owner'].mesh.nN
            )
            if len(dat.data.array) != valid_length:
                raise ValueError(
                    'line.data[{index}] length {datalen} does not match '
                    '{loc} length {meshlen}'.format(
                        index=ii,
                        datalen=len(dat.data.array),
                        loc=dat.location,
                        meshlen=valid_length
                    )
                )
        return proposal['value']


__all__ = ['Line', 'Mesh1D']
