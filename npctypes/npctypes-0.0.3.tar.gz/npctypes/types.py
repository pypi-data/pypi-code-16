__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$Oct 03, 2016 14:19$"


import numpy


def tinfo(a_type):
    """
        Takes a ``numpy.dtype`` or any type that can be converted to a
        ``numpy.dtype`` and returns its info.

        Args:
            a_type(type):                  the type to find info for.

        Returns:
            (np.core.getlimits.info):      info about the type.

        Examples:
            >>> tinfo(float)
            finfo(resolution=1e-15, min=-1.7976931348623157e+308, max=1.7976931348623157e+308, dtype=float64)

            >>> tinfo(numpy.float64)
            finfo(resolution=1e-15, min=-1.7976931348623157e+308, max=1.7976931348623157e+308, dtype=float64)

            >>> tinfo(numpy.float32)
            finfo(resolution=1e-06, min=-3.4028235e+38, max=3.4028235e+38, dtype=float32)

            >>> tinfo(complex)
            finfo(resolution=1e-15, min=-1.7976931348623157e+308, max=1.7976931348623157e+308, dtype=float64)

            >>> tinfo(int)
            iinfo(min=-9223372036854775808, max=9223372036854775807, dtype=int64)
    """

    a_type = numpy.dtype(a_type).type

    if issubclass(a_type, numpy.integer):
        return(numpy.iinfo(a_type))
    else:
        return(numpy.finfo(a_type))


def ctype(a_type):
    """
        Takes a numpy.dtype or any type that can be converted to a numpy.dtype
        and returns its equivalent ctype.

        Args:
            a_type(type):      the type to find an equivalent ctype to.

        Returns:
            (ctype):           the ctype equivalent to the dtype provided.

        Examples:
            >>> ctype(float)
            <class 'ctypes.c_double'>

            >>> ctype(numpy.float64)
            <class 'ctypes.c_double'>

            >>> ctype(numpy.float32)
            <class 'ctypes.c_float'>

            >>> ctype(numpy.dtype(numpy.float32))
            <class 'ctypes.c_float'>

            >>> ctype(int)
            <class 'ctypes.c_long'>
    """

    return(type(numpy.ctypeslib.as_ctypes(numpy.array(0, dtype=a_type))))


def get_ndpointer_type(a):
    """
        Takes a numpy.ndarray and gets a pointer type for that array.

        Args:
            a(ndarray):        the ndarray to get the pointer type for.

        Returns:
            (PyCSimpleType):   the pointer type associated with this array.

        Examples:
            >>> a = numpy.zeros((3, 4), dtype=float)
            >>> a_ptr = get_ndpointer_type(a)

            >>> a_ptr
            <class 'numpy.ctypeslib.ndpointer_<f8_2d_3x4_C_CONTIGUOUS_ALIGNED_WRITEABLE_OWNDATA'>

            >>> a_ptr._dtype_
            dtype('float64')
            >>> a_ptr._ndim_
            2
            >>> a_ptr._shape_
            (3, 4)
            >>> a_ptr._flags_
            1285
            >>> numpy.ctypeslib.flagsobj(a_ptr._flags_)
              C_CONTIGUOUS : True
              F_CONTIGUOUS : True
              OWNDATA : True
              WRITEABLE : False
              ALIGNED : True
              UPDATEIFCOPY : False
    """

    return(numpy.ctypeslib.ndpointer(
        dtype=a.dtype,
        ndim=a.ndim,
        shape=a.shape,
        flags=a.flags
    ))
