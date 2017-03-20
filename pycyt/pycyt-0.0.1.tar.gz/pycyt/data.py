"""Core classes for describing and storing flow data."""

from collections.abc import Sequence

import numpy as np


# Types for integer indices. Can be used as second argument to isinstance().
INTEGER_TYPES = (int, np.integer)

# Array-like types which trigger numpy advanced indexing
ARRAY_TYPES = (list, tuple, np.ndarray)


class Parameter:
	"""A single dimension of a raw Flow Cytometer measurement.

	This class encapsulates the concept of a parameter as it is used in the
	FCS 3.1 standard - in a list mode data file there is exactly one recorded
	value per parameter per event. This typically corresponds to a single
	detector on a flow cytometer and is synonymous with the term "channel",
	but also includes the "Time" parameter. Parameters form the basis
	for a data space.

	:param str name: Name of parameter.

	.. attribute:: name

		A string which uniquely defines the parameter.
	"""

	def __init__(self, name):
		if not isinstance(name, str):
			raise TypeError('Name must be string')
		self._name = name

	@property
	def name(self):
		return self._name

	def __hash__(self):
		return hash(self._name)

	def __eq__(self, other):
		return isinstance(other, Parameter) and self._name == other._name

	def __repr__(self):
		return '{0}({1!r})'.format(type(self).__name__, self._name)

	def __getnewargs__(self):
		return (self.name,)


class Dimension:
	"""A parameter with a corresponding scale transformation.

	.. attribute:: parameter

		The base :class:`Parameter` for the dimension - where the raw
		measurement came from.

	.. attribute:: scale

		:class:`pycyt.scale.ScaleTransform` that has been applied to the
		raw measurement.
	"""

	def __init__(self, parameter, scale=None):
		if isinstance(parameter, str):
			parameter = Parameter(parameter)
		elif not isinstance(parameter, Parameter):
			raise TypeError(parameter)

		self._parameter = parameter
		self._scale = scale

	def __eq__(self, other):
		return (self._parameter, self._scale) == \
			(other._parameter, other._scale)

	def __hash__(self):
		return hash((self._parameter, self._scale))

	@property
	def parameter(self):
		return self._parameter

	@property
	def scale(self):
		return self._scale

	def __repr__(self):
		if self._scale is None:
			args = (self.parameter.name,)
		else:
			args = (self.parameter.name, self._scale)

		return '{0}({1})'.format(
			type(self).__name__,
			', '.join(map(repr, args))
		)


class DataSpace(tuple):
	"""A tuple of :class:`.Dimension`\ s along with optional compensation.

	Essentially defines a transformation from a vector of raw flow
	measurements (an event) to another vector suitable for viewing or
	analysis.

	.. attribute:: parameters

		The corresponding :class:`.Parameter` for each :class:`.Dimension`.

	.. attribute:: compensation

		TODO
	"""

	def __new__(cls, dimensions, **kwargs):
		if not all(isinstance(d, Dimension) for d in dimensions):
			raise TypeError('dimensions must be sequence of Dimension')
		return tuple.__new__(cls, dimensions)

	def __init__(self, dimensions, compensation=None):
		self._dimensions = tuple(dimensions)

	def __eq__(self, other):
		return tuple.__eq__(self, other)

	def __repr__(self):
		return '<{0} [{1}]>'.format(
			type(self).__name__,
			', '.join(dim.parameter.name for dim in self)
		)

	def __getitem__(self, index):
		if isinstance(index, INTEGER_TYPES):
			return tuple.__getitem__(self, index)

		if isinstance(index, slice):
			dims = tuple.__getitem__(self, index)
		else:
			dims = [tuple.__getitem__(self, i) for i in index]

		return DataSpace(dims, compensation=self.compensation)

	@property
	def parameters(self):
		return tuple(dimension.parameter for dimension in self)

	@property
	def compensation(self):
		# TODO
		return None

	def same_dimensions(self, other):
		"""Check if the space has the same dimensions as another space.

		:param other: Data space to compare to.
		:type other: .DataSpace
		:rtype: bool
		"""
		return set(self) == set(other)

	def same_parameters(self, other):
		"""Check if the space has the same parameters as another space.

		:param other: Data space to compare to.
		:type other: .DataSpace
		:rtype: bool
		"""
		return set(self.parameters) == set(other.parameters)

	def is_subspace(self, other):
		"""Check all of the space's dimensions are contained in another.

		:param other: Data space to compare to.
		:type other: .DataSpace
		:rtype: bool
		"""
		return set(self).issubset(other)

	def is_permutation(self, other):
		"""
		Check if the space has the same dimensions as another space and the
		same compensation.

		:param other: Data space to compare to.
		:type other: .DataSpace
		:rtype: bool
		"""
		return self.same_parameters(other)  # TODO

	def has_param(self, param):
		"""Check if the space has the same dimensions as another space.

		:param other: Data space to compare to.
		:type other: .DataSpace
		:rtype: bool
		"""
		if isinstance(param, str):
			name = param
		else:
			name = param.name

		for dim in self:
			if dim.parameter.name == name:
				return True

		return False

	def map_to(self, other):
		"""Get a mapping of dimensions in this space to dimensions of another.

		:type other: .DataSpace
		:returns: Index of dimension in ``other`` for each dimension in the
			frame.
		:rtype: list
		"""
		return np.asarray(
			[other.index(dim) for dim in self],
			dtype=np.int
		)

	def get_index(self, index):
		"""Get the index of a dimension in the space, by parameter or name.

		Like :meth:`tuple.index`, but instead of getting indices of proper
		elements also allows getting indices of dimension by their parameter
		or parameter name.

		:param index: :class:`str`, :class:`.Parameter`, :class:`.Dimension`,
			or iterable of these.
		:returns: :class:`int` or :class:`list` of :class:`int`.
		:raises IndexError:
		"""
		if isinstance(index, Dimension):
			# Just get the index of the dimension
			try:
				return self.index(index)
			except ValueError:
				raise IndexError('{0!r} not in DataSpace'.format(index))

		elif isinstance(index, (str, Parameter)):
			# Find dimension by parameter name
			name = index if isinstance(index, str) else index.name
			for i, dim in enumerate(self):
				if name == dim.parameter.name:
					return i
			raise IndexError('{0!r} not in DataSpace'.format(index))

		else:
			# Interpret as iterable
			return [self.get_index(i) for i in index]


class FlowFrameIndexer:
	"""
	Utility class for indexing a :class:`.FlowFrame`'s events and dimensions
	simultaneously.
	"""

	def __init__(self, frame):
		self.frame = frame

	def __getitem__(self, index):
		"""
		:param index: Data space index preceded by zero or more event indices.

		:returns: :class:`.FlowFrame` if more than a single data space
			dimension and event was given, otherwise :class:`numpy.ndarray`
			or a scalar.
		"""
		space_index, event_index = self._parse_index_arg(index)

		# If either index type yields a scalar
		single_event = self.frame._yields_scalar_event(event_index)
		single_dim = not isinstance(space_index, (slice, *ARRAY_TYPES))

		# Continue based on whether advanced indexing is triggered for
		# space_index
		if not isinstance(space_index, ARRAY_TYPES):
			# Can do indexing all at once

			np_index = self.frame.numpy_index(space_index, event_index)
			subarray = self.frame.array[np_index]

		else:
			# Advanced indexing used for space_index, do in two steps

			# This should be a more efficient order?
			if self.frame.events_first:
				subarray = self.frame.array[space_index, ...]
				if single_dim:
					subarray = subarray[event_index]
				else:
					subarray = subarray[(slice(None), *event_index)]

			else:
				subarray = self.frame.array[(*event_index, slice(None))]
				if single_event:
					subarray = subarray[space_index]
				else:
					subarray = subarray[..., space_index]

		if single_dim or single_event:
			# Got "scalar" dimensions or events, return simple numpy array of
			# values (or single value)
			return subarray

		else:
			# Multiple dimensions and events, return FlowFrame
			subspace = self.frame.dataspace[space_index]
			frame = FlowFrame(subarray, subspace,
			                  events_first=self.frame.events_first)
			frame.has_own_data = subarray.base is not self.frame.array.base
			return frame

	def __setitem__(self, index, value):
		"""
		:param index: Data space index followed by zero or more event indices.
		:param value: Value to assign to array.
		"""
		space_index, event_index = self._parse_index_arg(index)

		# Right now, support slice-based indexing only
		space_advanced = isinstance(space_index, ARRAY_TYPES)
		events_advanced = any(isinstance(i, ARRAY_TYPES) for i in event_index)
		if events_advanced or space_advanced:
			raise TypeError('Advanced indexing not supported for assignment')

		np_index = self.frame.numpy_index(space_index, event_index)
		self.frame.array[np_index] = value

	def _parse_index_arg(self, arg):
		"""Parse index argument into indices for dataspace dims and events.

		:returns: Tuple of ``(space_index, event_index)``, as arguments to
			:meth:`.FlowFrame.numpy_index`.
		"""

		# Split into spatial and event parts
		if isinstance(arg, tuple):
			event_index = arg[:-1]
			space_index = arg[-1]
		else:
			event_index = ()
			space_index = arg

		# Extract an element of space_index to test its type
		if isinstance(space_index, Sequence):
			space_index_elem = space_index[0]
		else:
			space_index_elem = space_index

		# If space_index is not an integer, sequence of ints, or slice, assume
		# argument to DataSpace.get_index()
		if not isinstance(space_index_elem, (slice, *INTEGER_TYPES)):
			space_index = self.frame.dataspace.get_index(space_index)

		return space_index, event_index


class FlowFrame:
	"""High-level container for flow data.

	Contains flow data in the form of a multidimensional array of "events",
	which are vectors of measurement values in a :class:`.DataSpace`. The
	axes of the event array do not include the elements of the events
	themselves - for example, standard list mode data in an FCS file is a
	one-dimensional array (list) of events. This class will probably be	used
	in a similar fashion most of the time but the array may be of any
	arbitrary dimension.

	The data is stored in an underlying :class:`numpy.ndarray` having one
	additional axis compared to the conceptual event array, the indices	of
	which correspond to the dimensions within the data space (or measurement
	values within each event). This axis may lie in either the first or last
	position in the numpy array (see the :attr:`events_first` attribute) which,
	also considering whether the array is in C or Fortran order, may
	significantly affect performance because of differences in memory access
	patterns.

	:param numpy.ndarray array: Numpy array of data.
	:param .DataSpace dataspace: Data space of frame. Length must match
		size of first/last axis of ``array`` (according to ``events_first``).
	:param bool events_first:  See :attr:`events_first`.

	.. attribute:: array

		:class:`numpy.ndarray` containing raw data.

	.. attribute:: dataspace

		:class:`.DataSpace` describing the events.

	.. attribute:: events_first

		If the first (``True``) or last (``False``) axis of the underlying
		array corresponds to the data space and indexes the parameters within
		an event.

	.. attribute:: shape

		Shape of event array, :class:`tuple` of sizes of each axis.

	.. attribute:: ndim

		Number of axes in event array.

	.. attribute:: dtype

		:class:`numpy.dtype` of the underlying array.

	.. attribute:: has_own_data

		If the frame's data array is not a view of another frame's data array.
		This is only ever set to ``False`` when the frame was created as the
		result of an indexing operation of another frame where indexing the
		numpy array returned a view. Note that this is always set to ``True``
		when a frame is constructed from an existing array in a normal manner,
		which may not always be correct.

	.. attribute:: ix

		:class:`.FlowFrameIndexer` to perform indexing on the event array
		and the data space simultaneously.
	"""

	def __init__(self, array, dataspace, events_first=False):

		space_index = 0 if events_first else -1
		if array.shape[space_index] != len(dataspace):
			raise ValueError(
				'Shape of array does not match size of data space.'
			)

		self.array = array
		self.dataspace = dataspace
		self.events_first = events_first
		self.has_own_data = True

	@property
	def shape(self):
		if self.events_first:
			return self.array.shape[1:]
		else:
			return self.array.shape[:-1]

	@property
	def size(self):
		return self.array.size // len(self.dataspace)

	@property
	def ndim(self):
		return self.array.ndim - 1

	@property
	def dtype(self):
		return self.array.dtype

	@property
	def ix(self):
		return FlowFrameIndexer(self)

	def __repr__(self):
		return '<{0} {1!r}x[{2}]>'.format(
			type(self).__name__,
			self.shape,
			', '.join(dim.parameter.name for dim in self.dataspace)
		)

	def __len__(self):
		"""Number of events in the frame."""
		return self.size

	def __iter__(self):
		"""Iterate over events in the frame."""
		# This implementation is probably pretty slow
		for index in np.ndindex(self.shape):
			yield self[index]

	def __getitem__(self, event_index):
		"""Get a subset of events from the frame.

		:param event_index: Index of event(s) in same format accepted by
			:class:`numpy.ndarray`.
		:returns: :class:`.FlowFrame` with identical :class:`.DataSpace`, or
			:class:`numpy.ndarray` if only a single event.
		"""
		if not isinstance(event_index, tuple):
			event_index = (event_index,)

		np_index = self.numpy_index(event_index=event_index)
		subarray = self.array[np_index]

		if self._yields_scalar_event(event_index):
			# Return numpy array
			return subarray
		else:
			# Return sub-frame
			frame = FlowFrame(subarray, self.dataspace,
			                  events_first=self.events_first)
			frame.has_own_data = subarray.base is not self.array.base
			return frame

	def __setitem__(self, event_index, value):
		"""Assign event values to the frame.

		TODO - value parameter should accept FlowFrame.

		:param event_index: Index of event(s) in same format accepted by
			:class:`numpy.ndarray`.
		:param numpy.ndarray value: Array of values to assign to events. Shape
			must match index.
		"""
		np_index = self.numpy_index(event_index=event_index)
		self.array[np_index] = value

	def numpy_index(self, space_index=None, event_index=None):
		"""
		Get index for underlying :class:`numpy.ndarray` from indices of
		dimensions in data space and indices of events.

		``space_index`` must not be a value that would trigger advanced
		indexing on a numpy array.

		:param space_index: Index for spatial axis of numpy array (within
			individual events), must be a ``slice`` or single integer,
			:class:`.Dimension`, :class:`.Parameter` or ``str`` parameter
			name (lists/arrays of these are not supported). Defaults to a full
			slice (``:``).
		:param event_index: Index for remaining axes of numpy array
			(ignoring measurements within events), in any format accepted by a
			multidimensional :class:`numpy.ndarray`. Defaults to keeping all
			events.

		:returns: tuple suitable for indexing the underlying numpy array.
		"""

		if event_index is None:
			# Simple case of not having to deal with the array portion

			if space_index is None:
				# Simplest case
				return (Ellipsis,)

			else:
				# Still pretty simple
				if self.events_first:
					return (space_index, Ellipsis)
				else:
					return (Ellipsis, space_index)

		# Convert event_index to tuple
		if not isinstance(event_index, tuple):
			event_index = (event_index,)

		# Default space index to full slice
		if space_index is None:
			space_index = slice(None)

		# This is needed over "Ellipsis in event_index" due to an obscure
		# error if one of the elements of event_index is a numpy boolean array.
		events_has_ellipsis = any(i is Ellipsis for i in event_index)

		# For this implementation, there might be an existing numpy function
		# that does it better.
		if self.events_first:
			# Just append to space index because numpy applies partial indices
			# to the earliest axes.
			return (space_index, *event_index)

		elif len(event_index) >= self.ndim or events_has_ellipsis:
			# Two different conditions that yield the same result:

			# If the length of the event index is equal to the number of
			# event axes (or possibly longer, due to np.newaxis objects), just
			# append the space index and we have indices for all elements of
			# the underlying array.

			# If an Ellipsis was in the event index then we can also just
			# append the space index and numpy will handle the expansion
			# on its own. An Ellipsis typically implies some unindexed axes
			# left over so a single event should never be returned in this
			# case.

			return (*event_index, space_index)

		else:
			# Add an ellipsis to fill in indices for the missing axes. Do this
			# after the event indices so that the event axes are indexed from
			# the beginning like numpy does with partial indices by default.
			return (*event_index, Ellipsis, space_index)

	def _yields_scalar_event(self, event_index):
		"""Check if an event index yields a single "scalar" event.

		This is true if the index is a sequence containing an integer for
		each event axis.

		Note that if ``false`` the result of indexing still have one or even
		zero events - this is the difference between ``a[0]`` returning a
		scalar element of a 1D array and ``a[:1]`` and ``a[:0]`` returning
		arrays containing one and zero elements.

		:param tuple event_index: Any index accepted by :meth:`__getitem__`,
			wrapped in a tuple if a singleton.
		:rtype: bool
		"""
		return (
			len(event_index) == self.ndim and
			all(isinstance(i, INTEGER_TYPES) for i in event_index)
		)

	def copy(self, events_first=None, array_order='C'):
		"""Get a copy of the frame with a copied data array.

		:param bool events_first: Value of the :attr:`events_first` attribute
			of the copy. If ``None`` (default) will keep the value of the
			source array.
		:param str array_order: Memory layout of data array, passed to
			:meth:`numpy.ndarray.copy`.
		:rtype: .FlowFrame
		"""
		if events_first is None or events_first == self.events_first:
			events_first = self.events_first
			src_array = self.array

		else:
			if events_first:
				src_array = np.rollaxis(self.array, -1)
			else:
				src_array = np.transpose(self.array, (*range(1, self.ndim + 1), 0))

		array_copy = src_array.copy(order=array_order)
		return FlowFrame(array_copy, self.dataspace, events_first=events_first)

	def with_own_data(self):
		"""Get a version of the frame with its own data array.

		:returns: This frame if :attr:`has_own_data` is ``True``, otherwise
			result of :meth:`copy`.
		:rtype: .FlowFrame
		"""
		return self if self.has_own_data else self.copy()

	def use_own_data(self):
		"""
		Ensure the frame's data array does not share memory with another frame.

		If :attr:`has_own_data` is ``False``, assigns :attr:`array` to a copy
		of itself with its own data. Otherwise does nothing. Afterwards
		:attr:`has_own_data` will always be ``True``.

		:rtype: .FlowFrame
		"""
		if not self.has_own_data:
			self.array = self.array.copy()
