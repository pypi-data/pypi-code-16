"""vector.py contains the Vector composite resource for Steno3D"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from traitlets import validate

from .base import CompositeResource
from .options import ColorOptions
from .traits import Array, KeywordInstance, Repeated

from .point import Mesh0D, _PointBinder


class _VectorOptions(ColorOptions):
    pass


class Vector(CompositeResource):
    """Contains all the information about a vector field"""

    _resource_class = 'vector'

    mesh = KeywordInstance(
        help='Mesh',
        klass=Mesh0D
    )
    vectors = Array(
        help='Vector',
        shape=('*', 3),
        dtype=float
    )
    data = Repeated(
        help='Data',
        trait=KeywordInstance(klass=_PointBinder),
        allow_none=True
    )
    opts = KeywordInstance(
        help='Options',
        klass=_VectorOptions,
        allow_none=True
    )

    def _nbytes(self):
        return (self.mesh._nbytes() + self.vectors.astype('f4').nbytes +
                sum(d.data._nbytes() for d in self.data))

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

    @validate('vectors')
    def _validate_vectors(self, proposal):
        """Check if vectors is built correctly"""
        valid_length = proposal['owner'].mesh.nN
        if len(proposal['value']) != valid_length:
            raise ValueError(
                'vectors length {datalen} does not match '
                'mesh vertex length {meshlen}'.format(
                    datalen=len(proposal['value']),
                    meshlen=valid_length
                )
            )
        return proposal['value']

    def _get_dirty_files(self, force=False):
        files = {}
        dirty = self._dirty_traits
        if 'vectors' in dirty or force:
            files['vectors'] = \
                self.traits()['vectors'].serialize(self.vectors)
        return files

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        vec = super(Vector, cls)._build_from_json(json, **kwargs)
        vec.vectors = Array.download(
            url=json['vectors'],
            shape=(json['vectorsSize']//12, 3),
            dtype=json['vectorsType']
        )
        return vec


__all__ = ['Vector']
