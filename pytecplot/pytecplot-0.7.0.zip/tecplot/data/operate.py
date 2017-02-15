from collections import namedtuple
from six import string_types

from ..tecutil import _tecutil, ArgList, IndexSet, Index, sv, lock
from .. import layout
from ..constant import ValueLocation, FieldDataType
from ..exception import *
from collections import Iterable

Range = namedtuple('Range', 'min max step')
"""Limit the data altered by the `execute_equation` function.

The Range specification of I,J,K range indices for `execute_equation`
follow these rules:

    * All indices start with 0 and go to some maximum index *m*.
    * Negative values represent the indexes starting with the maximum at -1
      and continuing back to the beginning of the range.
    * A step of None, 0 and 1 are all equivalent and mean that no elements
      are skipped.
    * A negative step indicates a skip less than the maximum.

Example:

    Add one to variable 'X' for a zone 'Rectangular' for data points
    in I Range 1 to max, skipping every three points:

    >>> execute_equation('{X} = {X}+1', i_range=Range(min=1, max=None, step=3),
    ...                  zone_set='Rectangular')
"""
Range.__new__.__defaults__ = (None, None, None)


@lock()
def execute_equation(equation, zones=None, i_range=None, j_range=None,
                     k_range=None, value_location=None, variable_data_type=None,
                     ignore_divide_by_zero=None):
    """The execute_equation function operates on a data set within the
    |Tecplot Engine| using FORTRAN-like equations.

    Parameters:
        equation (`string <str>`): String containing the equation.
            Multiple equations can be processed by separating each equation
            with a newline. See Section 20 - 1 "Data Alteration through
            Equations" in the Tecplot User's Manual for more information on
            using equations. Iterable container of `Zone <data_access>` objects
            to operate on. May be a list, set, tuple, or any iterable
            container. If `None`, the equation will be applied to all zones.

            .. note:: In the equation string, variable names should be enclosed
                in curly braces. For example, '{X} = {X} + 1'

        zones: (Iterable container of `Zone <data_access>` objects, optional):
            Iterable container of `Zone <data_access>` objects to operate on.
            May be a list, set, tuple, or any iterable container. If `None`,
            the equation will be applied to all zones.
        i_range (`Range`, optional):
            Tuple of integers for I:  (min, max, step). If `None`, then the
            equation will operate on the entire range.
            Not used for finite element nodal data.
        j_range (`Range`, optional):
            Tuple of integers for J:  (min, max, step). If `None`, then the
            equation will operate on the entire range.
            Not used for finite element nodal data.
        k_range (`Range`, optional):
            Tuple of integers for K:  (min, max, step). If `None`, then the
            equation will operate on the entire range.
            Not used for finite element nodal data.
        value_location (`ValueLocation`, optional):
            Variable `ValueLocation` for the variable on the left hand side.
            This is used only if this variable is being created for the first
            time.
            If `None`, |Tecplot Engine| will choose the location for you.
        variable_data_type (`FieldDataType`, optional):
            Data type for the variable on the left hand side.
            This is used only if this variable is being created for the first
            time.
            If `None`, |Tecplot Engine| will choose the type for you.
        ignore_divide_by_zero (`bool`, optional):
            `bool` value which instructs |Tecplot Engine| to ignore
            divide by zero errors. The result is clamped
            such that 0/0 is clamped to zero and (+/-N)/0
            where N != 0 clamps to +/-maximum value for the given type.

    Raises:
        `TecplotSystemError`

    .. warning:: Zero-based Indexing

        It is important to know that all indexing in |PyTecplot| scripts are
        zero-based. This is a departure from the macro language which is
        one-based. This is to keep with the expectations when working in the
        python language. However, |PyTecplot| does not modify strings that are
        passed to the |Tecplot Engine|. This means that one-based indexing
        should be used when running macro commands from python or when using
        `execute_equation() <tecplot.data.operate.execute_equation>`.

    Add one to variable 'X' for zones 'Rectangular' and 'Circular' for every
    data point:
    >>> import tecplot
    >>> dataset = tecplot.active_frame().dataset
    >>> execute_equation('{X} = {X} + 1', zones=[dataset.zone('Rectangular'),
    >>>                  dataset.zone('Circular')])

    Create a new, double precision variable called DIST:

    >>> execute_equation('{DIST} = SQRT({X}**2 + {Y}**2)',
    ...                  variable_data_type=FieldDataType.double)

    Set a variable called **P** to zero along the boundary of an IJ-ordered
    zone:

    >>> execute_equation('{P} = 0', i_range=Range(step=-1))
    >>> execute_equation('{P} = 0', j_range=Range(step=-1))
    """
    if __debug__:
        if not isinstance(equation, string_types):
            raise TecplotTypeError('Equation must be a string')
        elif len(equation) == 0:
            raise TecplotValueError('Equation can not be empty')
        if not isinstance(value_location, (ValueLocation, type(None))):
            msg = 'value_location must be a ValueLocation'
            raise TecplotTypeError(msg)
        if not isinstance(variable_data_type, (FieldDataType, type(None))):
            msg = 'variable_data_type must be a FieldDataType'
            raise TecplotTypeError(msg)
        if not isinstance(ignore_divide_by_zero, (bool, type(None))):
            raise TecplotTypeError('ignore_divide_by_zero must be a bool')

        # Check that all zones belong to the active dataset
        # (which is currently the only dataset option available)
        if zones:
            try:
                current_dataset = layout.active_frame().dataset
                parent_ids = {U.dataset.uid for U in zones} if isinstance(
                    zones, Iterable) else {zones.dataset.uid}

                if {current_dataset.uid} != parent_ids:
                    raise TecplotValueError(
                        'All zones must have the same parent dataset')

            except AttributeError:
                # At least one member of the input zone set was not
                # a Zone object
                raise TecplotTypeError(
                    'All zones must be Zone objects')

    with ArgList() as arglist:
        allocd = []
        arglist[sv.EQUATION] = equation
        if zones is not None:
            s = IndexSet(zones)
            allocd.append(s)
            arglist[sv.ZONESET] = s

        for dim, rng in zip(['I', 'J', 'K'], [i_range, j_range, k_range]):
            if rng is not None:
                if not isinstance(rng, Range):
                    rng = Range(*rng)
                if rng.min is not None:
                    arglist[dim+'MIN'] = Index(rng.min)
                if rng.max is not None:
                    arglist[dim+'MAX'] = Index(rng.max)
                if rng.step is not None:
                    step = int(rng.step)
                    if step != 0:
                        arglist[dim+'SKIP'] = rng.step

        if value_location is not None:
            arglist[sv.VALUELOCATION] = value_location

        if variable_data_type is not None:
            arglist[sv.VARDATATYPE] = variable_data_type

        if ignore_divide_by_zero is not None:
            arglist[sv.IGNOREDIVIDEBYZERO] = ignore_divide_by_zero

        try:
            if not _tecutil.DataAlterX(arglist):
                raise TecplotSystemError()
        finally:
            for a in allocd:
                a.dealloc()
