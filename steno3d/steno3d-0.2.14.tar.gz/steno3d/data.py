"""data.py contains resource data structures"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from six import string_types

from numpy import ndarray
from traitlets import observe, validate

from .base import BaseData
from .traits import Array, String


class DataArray(BaseData):
    """Data array with unique values at every point in the mesh"""
    _resource_class = 'array'
    array = Array(
        help='Data, unique values at every point in the mesh',
        shape=('*',),
        dtype=(float, int)
    )

    order = String(
        help='Data array order, for data on grid meshes',
        choices={
            'c': ('C-STYLE', 'NUMPY', 'ROW-MAJOR', 'ROW'),
            'f': ('FORTRAN', 'MATLAB', 'COLUMN-MAJOR', 'COLUMN', 'COL')
        },
        default_value='c',
        lowercase=True
    )

    def __init__(self, array=None, **kwargs):
        super(DataArray, self).__init__(**kwargs)
        if array is not None:
            self.array = array

    def _nbytes(self, arr=None):
        if arr is None or (isinstance(arr, string_types) and arr == 'array'):
            arr = self.array
        if isinstance(arr, ndarray):
            return arr.astype('f4').nbytes
        raise ValueError('DataArray cannot calculate the number of '
                         'bytes of {}'.format(arr))

    @observe('array')
    def _reject_large_files(self, change):
        try:
            self._validate_file_size(change['name'], change['new'])
        except ValueError as err:
            setattr(change['owner'], change['name'], change['old'])
            raise err

    @validate('array')
    def _validate_array(self, proposal):
        proposal['owner']._validate_file_size('array', proposal['value'])
        return proposal['value']

    def _get_dirty_data(self, force=False):
        datadict = super(DataArray, self)._get_dirty_data(force)
        dirty = self._dirty_traits
        if 'order' in dirty or force:
            datadict['order'] = self.order
        return datadict

    def _get_dirty_files(self, force=False):
        files = super(DataArray, self)._get_dirty_files(force)
        dirty = self._dirty_traits
        if 'array' in dirty or force:
            files['array'] = self.traits()['array'].serialize(self.array)
        return files

    @classmethod
    def _build_from_json(cls, json, **kwargs):
        data = DataArray(
            title=kwargs['title'],
            description=kwargs['description'],
            order=json['order'],
            array=Array.download(
                url=json['array'],
                shape=json['arraySize']//4,
                dtype=json['arrayType']
            )
        )
        return data

    @classmethod
    def _build_from_omf(cls, omf_data):
        assert omf_data.__class__.__name__ in ('ScalarData', 'MappedData')
        data = dict(
            location='N' if omf_data.location == 'vertices' else 'CC',
            data=DataArray(
                title=omf_data.name,
                description=omf_data.description,
                array=omf_data.array.array
            )
        )
        return data

__all__ = ['DataArray']
