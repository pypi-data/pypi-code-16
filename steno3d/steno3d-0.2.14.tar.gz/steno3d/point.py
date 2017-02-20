"""point.py contains the Point composite resource for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from six import string_types

from numpy import ndarray
from traitlets import observe, validate

from .base import BaseMesh
from .base import CompositeResource
from .data import DataArray
from .options import ColorOptions
from .options import Options
from .texture import Texture2DImage
from .traits import Array, HasSteno3DTraits, KeywordInstance, Repeated, String


class _Mesh0DOptions(Options):
    pass


class _PointOptions(ColorOptions):
    pass


class Mesh0D(BaseMesh):
    """Contains spatial information of a 0D point cloud."""
    vertices = Array(
        help='Point locations',
        shape=('*', 3),
        dtype=float
    )
    opts = KeywordInstance(
        help='Mesh0D Options',
        klass=_Mesh0DOptions,
        allow_none=True
    )

    @property
    def nN(self):
        """ get number of nodes """
        return len(self.vertices)

    def _nbytes(self, arr=None):
        if arr is None or (isinstance(arr, string_types) and
                           arr == 'vertices'):
            arr = self.vertices
        if isinstance(arr, ndarray):
            return arr.astype('f4').nbytes
        raise ValueError('Mesh0D cannot calculate the number of '
                         'bytes of {}'.format(arr))

    @observe('vertices')
    def _reject_large_files(self, change):
        try:
            self._validate_file_size(change['name'], change['new'])
        except ValueError as err:
            setattr(change['owner'], change['name'], change['old'])
            raise err

    @validate('vertices')
    def _validate_verts(self, proposal):
        """Check if mesh content is built correctly"""
        proposal['owner']._validate_file_size('vertices', proposal['value'])
        return proposal['value']

    def _get_dirty_files(self, force=False):
        files = super(Mesh0D, self)._get_dirty_files(force)
        dirty = self._dirty_traits
        if 'vertices' in dirty or force:
            files['vertices'] = \
                self.traits()['vertices'].serialize(self.vertices)
        return files

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        mesh = Mesh0D(
            title=kwargs['title'],
            description=kwargs['description'],
            vertices=Array.download(
                url=json['vertices'],
                shape=(json['verticesSize']//12, 3),
                dtype=json['verticesType']
            ),
            opts=json['meta']
        )
        return mesh

    @classmethod
    def _build_from_omf(cls, omf_geom, omf_project):
        mesh = Mesh0D(
            vertices=(omf_geom.vertices.array +
                      omf_geom.origin +
                      omf_project.origin)
        )
        return mesh


class _PointBinder(HasSteno3DTraits):
    """Contains the data on a 0D point cloud"""
    location = String(
        help='Location of the data on mesh',
        default_value='N',
        choices={
            'N': ('NODE', 'CELLCENTER', 'CC', 'VERTEX')
        }
    )
    data = KeywordInstance(
        help='Data',
        klass=DataArray
    )


class Point(CompositeResource):
    """Contains all the information about a 0D point cloud"""
    mesh = KeywordInstance(
        help='Mesh',
        klass=Mesh0D
    )
    data = Repeated(
        help='Data',
        trait=KeywordInstance(klass=_PointBinder),
        allow_none=True
    )
    textures = Repeated(
        help='Textures',
        trait=KeywordInstance(klass=Texture2DImage),
        allow_none=True
    )
    opts = KeywordInstance(
        help='Options',
        klass=_PointOptions,
        allow_none=True
    )

    def _nbytes(self):
        return (self.mesh._nbytes() +
                sum(d.data._nbytes() for d in self.data) +
                sum(t._nbytes() for t in self.textures))

    @validate('data')
    def _validate_data(self, proposal):
        """Check if resource is built correctly"""
        for ii, dat in enumerate(proposal['value']):
            assert dat.location == 'N'
            valid_length = proposal['owner'].mesh.nN
            if len(dat.data.array) != valid_length:
                raise ValueError(
                    'point.data[{index}] length {datalen} does not match '
                    '{loc} length {meshlen}'.format(
                        index=ii,
                        datalen=len(dat.data.array),
                        loc=dat.location,
                        meshlen=valid_length
                    )
                )
        return proposal['value']


__all__ = ['Point', 'Mesh0D']
