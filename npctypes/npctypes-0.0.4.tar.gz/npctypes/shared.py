__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$Oct 04, 2016 16:17$"


import contextlib
import multiprocessing.sharedctypes

import numpy

from npctypes import types


# Used to initiate the array from the shared process heap.
_new_value = multiprocessing.sharedctypes._new_value

_ndarray_cache = {}
def ndarray(shape, dtype, order=None):
    """
        Factory to generate N-D Arrays shared across process boundaries.

        This creates a custom dynamic type (if one doesn't already exist) that
        is a ``ctypes.Array`` instance. If one does already exist, we reuse it
        so that things like type comparisons work. In addition to the typical
        properties that ``ctypes.Array``s have, this tracks its number of
        dimensions, shape, and order ('C' or 'F' for C and Fortran
        respectively). Having this information allows us to easily construct a
        NumPy ndarray in other processes.

        Args:
            shape(tuple of ints):       Shape of the array to allocate.
            dtype(type):                Type of the array to allocate.
            order(char or None):        Order of the array ('C', 'F', or None).
                                        Defaults to None.

        Returns:
            ctypes.Array:               Custom Array (NDArray) instance
                                        allocated on the shared process heap.

        Examples:
            >>> ndarray((2,3), float)               # doctest: +ELLIPSIS
            <npctypes.shared.NDArray_<f8_2d_2x3_C object at 0x...>

            >>> ndarray((2,3), float, order='F')    # doctest: +ELLIPSIS
            <npctypes.shared.NDArray_<f8_2d_2x3_F object at 0x...>
    """

    global _ndarray_cache

    # Ensure all args are in working order.
    assert isinstance(shape, tuple), \
        "`shape` must be a `tuple`"

    dtype = numpy.dtype(dtype)

    if order is None:
        order = 'C'
    else:
        assert order in ['C', 'F'], \
            "`order` must be `'C'` or `'F'`."

    ndim = len(shape)

    # Get the C type values
    ctype = types.ctype(dtype)
    size = int(numpy.prod(shape))

    try:
        NDArray = _ndarray_cache[(ctype, size, ndim, shape, order)]
    except KeyError:
        # Create an NDArray that inherits from the C type array.
        array_type = size * ctype
        NDArray = type(
            "_".join([
                "NDArray",
                dtype.str,
                "%id" % ndim,
                "x".join([str(_) for _ in shape]),
                order
            ]),
            (array_type,),
            dict(
                _type_ = ctype,
                _length_ = size,
                _ndim_ = ndim,
                _shape_ = shape,
                _order_ = order,
            )
        )

        _ndarray_cache[(ctype, size, ndim, shape, order)] = NDArray

    # Create a new instance of the NDArray type on shared storage.
    a = _new_value(NDArray)

    return a


@contextlib.contextmanager
def as_ndarray(a, writeable=True):
    """
        Context manager to provide NumPy ndarray views of NDArray instances.

        Args:
            shape(tuple of ints):       Shape of the array to allocate.
            dtype(type):                Type of the array to allocate.
            order(char or None):        Order of the array ('C', 'F', or None).
                                        Defaults to None.

        Returns:
            ctypes.Array:               Custom Array instance allocated on the
                                        shared process heap.

        Examples:
            >>> a = ndarray((2,3), float)
            >>> with as_ndarray(a) as nd_a:
            ...     nd_a[...] = 0
            ...     print(nd_a)
            [[ 0.  0.  0.]
             [ 0.  0.  0.]]

            >>> a = ndarray((2,3), float)
            >>> with as_ndarray(a) as nd_a:
            ...     for i in range(nd_a.size):
            ...         nd_a.flat[i] = i
            ...
            ...     print(nd_a)
            [[ 0.  1.  2.]
             [ 3.  4.  5.]]
    """

    # Construct the NumPy array object.
    nd_a = numpy.frombuffer(a, dtype=a._type_)
    nd_a = nd_a.reshape(a._shape_, order=a._order_)
    nd_a.flags["WRITEABLE"] = writeable

    yield nd_a
