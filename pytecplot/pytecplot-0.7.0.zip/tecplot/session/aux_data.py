from builtins import int, super

from collections import namedtuple
from contextlib import contextmanager
from ctypes import c_char_p, c_void_p, cast
from enum import Enum
from six import string_types

from ..tecutil import _tecutil
from ..constant import *
from ..tecutil import lock, lock_attributes


@lock_attributes
class AuxData(c_void_p):
    """Auxiliary data.

    The Tecplot Engine can hold auxiliary data attached to one of the following
    objects:

        - Layout
        - Page
        - Frame
        - Dataset
        - Variable
        - Zone
        - Linemap

    It is an ordered key-value pair that behaves like a dict: keys are strings,
    and a list: keys are ordered and values can be access by index. The keys
    must be alphanumeric (special characters "." and "_" are allow), must not
    contain spaces and must begin with a non-numeric character or underscore.
    The values on the other hand are arbitrary strings and can contain
    anything. In this example, we get the auxiliary data attached to the
    dataset and add some information to it::

        >>> dataset = tp.active_frame().dataset
        >>> aux = dataset.aux_data
        >>> aux['info'] = 'Here is some information.'
        >>> aux['note'] = 'Aux data values are always treated as strings.'
        >>> aux['Xavg'] = '3.14159'
        >>> for k, v in aux.items():
        ...     print('{}: {}'.format(k,v))
        info: Here is some information.
        note: Aux data values are always treated as strings.
        Xavg: 3.14159
    """
    def __init__(self, parent, object_type, object_index=None):
        self.parent = parent
        self.object_type = object_type
        self.getref_args = [] if object_index is None else [object_index + 1]
        super().__init__(self._native_reference)

    @property
    def _native_reference(self):
        _dispatch = {
            AuxDataObjectType.Dataset: _tecutil.AuxDataDataSetGetRef,
            AuxDataObjectType.Frame: _tecutil.AuxDataFrameGetRef,
            AuxDataObjectType.Layout: _tecutil.AuxDataLayoutGetRef,
            AuxDataObjectType.Linemap: _tecutil.AuxDataLineMapGetRef,
            AuxDataObjectType.Page: _tecutil.AuxDataPageGetRef,
            AuxDataObjectType.Variable: _tecutil.AuxDataVarGetRef,
            AuxDataObjectType.Zone: _tecutil.AuxDataZoneGetRef}
        with self._activated_parent():
            return _dispatch[self.object_type](*self.getref_args)

    @contextmanager
    def _activated_parent(self):
        if self.parent:
            with self.parent.activated():
                yield
        else:
            yield

    @contextmanager
    def assignment(self):
        _tecutil.AuxDataBeginAssign()
        try:
            yield
        finally:
            _tecutil.AuxDataEndAssign()

    def index(self, name):
        success, index = _tecutil.AuxDataGetItemIndex(self, name)
        index -= 1
        if not success:
            raise TecplotSystemError
        return index

    _Item = namedtuple('Item', ['name', 'value', 'dtype', 'retain'])

    def _item(self, index):
        res =_tecutil.AuxDataGetItemByIndex(self, index + 1)
        name, value, dtype, retain = res
        if dtype is AuxDataType.String:
            value = cast(c_void_p(value), c_char_p).value.decode()
        else:
            # if we ever add another type to AuxDataType, this would
            # need to be expanded as well as setitem which currently
            # just converts every input to a string.
            raise TecplotNotImplementedError
        return AuxData._Item(name, value, dtype, retain)

    def name(self, index):
        return self._item(index).name

    def __getitem__(self, key):
        if isinstance(key, string_types):
            key = self.index(key)
        return self._item(key).value

    @lock()
    def __setitem__(self, key, value):
        if isinstance(key, int):
            try:
                key = self.name(key)
            except:
                raise IndexError
        if not _tecutil.AuxDataSetItem(self, key, str(value),
                                       AuxDataType.String.value, True):
            raise TecplotSystemError()

    @lock()
    def __delitem__(self, key):
        if isinstance(key, string_types):
            key = self.index(key)
        _tecutil.AuxDataDeleteItemByIndex(self, key + 1)

    def __len__(self):
        return _tecutil.AuxDataGetNumItems(self)

    def __iter__(self):
        self._current_index = -1
        self._current_length = len(self)
        return self

    def __next__(self):
        self._current_index += 1
        if self._current_index < self._current_length:
            return self.name(self._current_index)
        else:
            raise StopIteration

    def items(self):
        for i in range(len(self)):
            item = self._item(i)
            yield item.name, item.value

    def keys(self):
        for key in self:
            yield key

    def values(self):
        for _, value in self.items():
            yield value

    def asdict(self):
        return {k: v for k, v in self.items()}

    def __str__(self):
        return str(self.asdict())
