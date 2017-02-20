"""surface.py contains the Surface composite resource for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from json import dumps

from numpy import max as npmax
from numpy import min as npmin
from numpy import ndarray
from six import string_types
from traitlets import observe, validate

from .base import BaseMesh
from .base import CompositeResource
from .data import DataArray
from .options import ColorOptions
from .options import MeshOptions
from .texture import Texture2DImage
from .traits import (Array, HasSteno3DTraits, KeywordInstance, Renamed,
                     Repeated, String, Union, Vector)


class _Mesh2DOptions(MeshOptions):
    pass


class _SurfaceOptions(ColorOptions):
    pass


class Mesh2D(BaseMesh):
    """class steno3d.Mesh2D

    Contains spatial information about a 2D surface defined by
    triangular faces.
    """
    vertices = Array(
        help='Mesh vertices',
        shape=('*', 3),
        dtype=float
    )
    triangles = Array(
        help='Mesh triangle vertex indices',
        shape=('*', 3),
        dtype=int
    )
    opts = KeywordInstance(
        help='Mesh2D Options',
        klass=_Mesh2DOptions,
        allow_none=True
    )

    @property
    def nN(self):
        """ get number of nodes """
        return len(self.vertices)

    @property
    def nC(self):
        """ get number of cells """
        return len(self.triangles)

    def _nbytes(self, arr=None):
        if arr is None:
            return self._nbytes('vertices') + self._nbytes('triangles')
        if isinstance(arr, string_types) and arr in ('vertices', 'triangles'):
            arr = getattr(self, arr)
        if isinstance(arr, ndarray):
            return arr.astype('f4').nbytes
        raise ValueError('Mesh2D cannot calculate the number of '
                         'bytes of {}'.format(arr))

    @observe('triangles', 'vertices')
    def _reject_large_files(self, change):
        try:
            self._validate_file_size(change['name'], change['new'])
        except ValueError as err:
            setattr(change['owner'], change['name'], change['old'])
            raise err

    @validate('triangles')
    def _validate_tri(self, proposal):
        if npmin(proposal['value']) < 0:
            raise ValueError('Triangles may only have positive integers')
        if npmax(proposal['value']) >= len(proposal['owner'].vertices):
            raise ValueError('Triangles expects more vertices than provided')
        proposal['owner']._validate_file_size('triangles', proposal['value'])
        return proposal['value']

    @validate('vertices')
    def _validate_vert(self, proposal):
        if npmax(proposal['owner'].triangles) >= len(proposal['value']):
            raise ValueError('Triangles expects more vertices than provided')
        proposal['owner']._validate_file_size('vertices', proposal['value'])
        return proposal['value']

    def _get_dirty_files(self, force=False):
        files = {}
        dirty = self._dirty_traits
        if 'vertices' in dirty or force:
            files['vertices'] = \
                self.traits()['vertices'].serialize(self.vertices)
        if 'triangles' in dirty or force:
            files['triangles'] = \
                self.traits()['triangles'].serialize(self.triangles)
        return files

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        mesh = Mesh2D(
            title=kwargs['title'],
            description=kwargs['description'],
            vertices=Array.download(
                url=json['vertices'],
                shape=(json['verticesSize']//12, 3),
                dtype=json['verticesType']
            ),
            triangles=Array.download(
                url=json['triangles'],
                shape=(json['trianglesSize']//12, 3),
                dtype=json['trianglesType']
            ),
            opts=json['meta']
        )
        return mesh

    @classmethod
    def _build_from_omf(cls, omf_geom, omf_project):
        mesh = Mesh2D(
            vertices=(omf_geom.vertices.array +
                      omf_geom.origin +
                      omf_project.origin),
            triangles=omf_geom.triangles.array
        )
        return mesh


class Mesh2DGrid(BaseMesh):
    """Contains spatial information of a 2D grid."""
    h1 = Array(
        help='Grid cell widths, U-direction',
        shape=('*',),
        dtype=(float, int)
    )
    h2 = Array(
        help='Grid cell widths, V-direction',
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
    Z = Array(
        help='Node topography',
        shape=('*',),
        dtype=float,
        default_value=[],
        allow_none=True
    )
    opts = KeywordInstance(
        help='Mesh2D Options',
        klass=_Mesh2DOptions,
        allow_none=True
    )

    @property
    def nN(self):
        """ get number of nodes """
        return (len(self.h1)+1) * (len(self.h2)+1)

    @property
    def nC(self):
        """ get number of cells """
        return len(self.h1) * len(self.h2)

    def _nbytes(self, arr=None):
        filenames = ('h1', 'h2', 'O', 'U', 'V', 'Z')
        if arr is None:
            return sum(self._nbytes(fn) for fn in filenames)
        if isinstance(arr, string_types) and arr in filenames:
            if getattr(self, arr, None) is None:
                return 0
            arr = getattr(self, arr)
        if isinstance(arr, ndarray):
            return arr.astype('f4').nbytes
        raise ValueError('Mesh2DGrid cannot calculate the number of '
                         'bytes of {}'.format(arr))

    @observe('Z')
    def _reject_large_files(self, change):
        try:
            self._validate_file_size(change['name'], change['new'])
        except ValueError as err:
            setattr(change['owner'], change['name'], change['old'])
            raise err

    @validate('Z')
    def _validate_Z(self, proposal):
        """Check if mesh content is built correctly"""
        if len(proposal['value']) == 0:
            return proposal['value']
        if len(proposal['value']) != proposal['owner'].nN:
            raise ValueError(
                'Length of Z, {zlen}, must equal number of nodes, '
                '{nnode}'.format(
                    zlen=len(proposal['value']),
                    nnode=proposal['owner'].nN
                )
            )
        proposal['owner']._validate_file_size('Z', proposal['value'])
        return proposal['value']

    def _get_dirty_data(self, force=False):
        datadict = super(Mesh2DGrid, self)._get_dirty_data(force)
        dirty = self._dirty_traits
        if ('h1' in dirty or 'h2' in dirty) or force:
            datadict['tensors'] = dumps(dict(
                h1=self.h1.tolist(),
                h2=self.h2.tolist(),
            ))
        if ('O' in dirty or 'U' in dirty or 'V' in dirty) or force:
            datadict['OUV'] = dumps(dict(
                O=self.O.tolist(),
                U=Vector.as_length(self.U, self.h1.sum()).tolist(),
                V=Vector.as_length(self.V, self.h2.sum()).tolist()
            ))
        return datadict

    def _get_dirty_files(self, force=False):
        files = super(Mesh2DGrid, self)._get_dirty_files(force)
        dirty = self._dirty_traits
        if 'Z' in dirty or (force and getattr(self, 'Z', []) != []):
            files['Z'] = self.traits()['Z'].serialize(self.Z)
        return files

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        mesh = Mesh2DGrid(
            title=kwargs['title'],
            description=kwargs['description'],
            h1=json['tensors']['h1'],
            h2=json['tensors']['h2'],
            O=json['OUV']['O'],
            U=json['OUV']['U'],
            V=json['OUV']['V'],
            opts=json['meta']
        )
        if json['ZExists']:
            mesh.Z = Array.download(
                url=json['Z'],
                shape=json['ZSize']//4,
                dtype=json['ZType']
            )

        return mesh

    @classmethod
    def _build_from_omf(cls, omf_geom, omf_project):
        mesh = Mesh2DGrid(
            h1=omf_geom.tensor_u,
            h2=omf_geom.tensor_v,
            O=omf_geom.origin + omf_project.origin,
            U=omf_geom.axis_u,
            V=omf_geom.axis_v
        )
        if omf_geom.offset_w is not None:
            mesh.Z = omf_geom.offset_w.array
        return mesh


class _SurfaceBinder(HasSteno3DTraits):
    """Contains the data on a 2D surface with location information"""
    location = String(
        help='Location of the data on mesh',
        choices={
            'CC': ('FACE', 'CELLCENTER'),
            'N': ('NODE', 'VERTEX', 'CORNER')
        }
    )
    data = KeywordInstance(
        help='Data',
        klass=DataArray
    )


class Surface(CompositeResource):
    """Contains all the information about a 2D surface"""
    mesh = Union(
        help='Mesh',
        trait_types=[
            KeywordInstance(klass=Mesh2D),
            KeywordInstance(klass=Mesh2DGrid)
        ]
    )
    data = Repeated(
        help='Data',
        trait=KeywordInstance(klass=_SurfaceBinder),
        allow_none=True
    )
    textures = Repeated(
        help='Textures',
        trait=KeywordInstance(klass=Texture2DImage),
        allow_none=True
    )
    opts = KeywordInstance(
        help='Options',
        klass=_SurfaceOptions,
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
            assert dat.location in ('N', 'CC')
            valid_length = (
                proposal['owner'].mesh.nC if dat.location == 'CC'
                else proposal['owner'].mesh.nN
            )
            if len(dat.data.array) != valid_length:
                raise ValueError(
                    'surface.data[{index}] length {datalen} does not match '
                    '{loc} length {meshlen}'.format(
                        index=ii,
                        datalen=len(dat.data.array),
                        loc=dat.location,
                        meshlen=valid_length
                    )
                )
        return proposal['value']


__all__ = ['Surface', 'Mesh2D', 'Mesh2DGrid']
