"""Scale transformations for viewing and gating flow data.

.. data:: transform_registry

	Dictionary of registered transforms by name.
"""


from abc import ABCMeta, abstractmethod, abstractproperty

import numpy as np

from pycyt.util import FrozenDict


LOG10 = np.log(10)


transform_registry = dict()


def validator(func, template):
	"""Create a parameter validation function.

	:param func: Function with signature ``(value) -> valid``.
	:param str template: Template string for :exc:`ValueError` that will be
		thrown if ``func`` returns ``False``. Formatted with ``param`` as the
		parameter name and ``value`` as the value passed.
	:returns: Function with signature ``(param, value)`` that raises an
		exception if the value is invalid.
	"""
	def validate(param, value):
		if not func(value):
			raise ValueError(template.format(param=param.name, value=value))
	return validate


# Validator for parameters that must be positive
v_positive = validator(lambda x: x > 0, '{param} must be positive')
v_nonneg = validator(lambda x: x >= 0, '{param} must be nonnegative')


class ScaleParameter:
	"""Descriptor for a parameter of a :class:`.ScaleTransform`.

	:param \\*args: Default value as single positional argument, or empty if no
		default.
	:param validators: List of validators to use.
	:param type_: Value of :attr:`type` attribute.

	.. attribute:: default

		Default value if :attr:`has_default` is ``True``.

	.. attribute:: has_default

		If the parameter has a default value.

	.. attribute:: validators

		List of functions with signature ``(parameter, value)`` that raise an
		error if the parameter is given an incorrect value.

	.. attribute:: type

		Primitive type (e.g. ``float``) or any callable that converts its
		parameter into the correct type.
	"""

	def __init__(self, *args, validators=[], type_=float):

		if len(args) == 1:
			self.default, = args
			self.has_default = True
		elif len(args) == 0:
			self.default = None
			self.has_default = False
		else:
			raise TypeError('Constructor takes zero or one positional arguments')

		self.validators = list(validators)
		self.type = type_
		self.name = None

	def __get__(self, obj, cls):
		if obj is not None:
			return obj.params[self.name]
		else:
			return self

	def validate(self, value):
		for validator in self.validators:
			validator(self, value)


class ScaleMeta(ABCMeta):
	"""Metaclass for :class:`ScaleTransform`.

	Collects :class:`.ScaleParameter`\ s present in the class definition in
	the :attr:`.ScaleTransform.__params__` attribute and enables registration
	of transforms by name.

	:param str name: Optional, name to register the scale under (in
		:data:`transform_registry`).
	"""

	def __new__(metacls, clsname, bases, dct, **kwargs):
		return super().__new__(metacls, clsname, bases, dct)

	def __init__(cls, clsname, bases, dct, name=None):
		super().__init__(clsname, bases, dct)

		# Add to registry
		if name is not None:
			transform_registry[name] = cls

		# Populate __params__ attribute
		cls.__params__ = dict()
		for name, value in dct.items():
			if isinstance(value, ScaleParameter):
				value.name = name
				cls.__params__[name] = value


class ScaleTransform(metaclass=ScaleMeta):
	"""ABC for a scale transformation for viewing or gating flow data.

	:param \\**kwargs: Keyword arguments containing parameter values by name.

	.. attribute:: __params__

		Class attribute, dictionary of all :class:`.ScaleParameter`\\ s in the
		class definition by name.

	.. attribute:: params

		:class:`pycyt.util.FrozenDict` of parameter values by name.
	"""

	def __init__(self, **kwargs):
		params = dict()

		# Get parameter values from kwargs
		for param in self.__params__.values():

			try:
				value = kwargs.pop(param.name)

			except KeyError:

				if param.default is not None:
					value = param.default

				else:
					raise TypeError(
						'"{}" is a required parameter'
						.format(param.name)
					)

			value = param.type(value)
			param.validate(value)
			params[param.name] = value

		# Error for unknown keyword args
		for key in kwargs:
			raise TypeError(
				'{} has no parameter "{}"'
				.format(type(self).__name__, key)
			)

		self.params = FrozenDict(params)

	@abstractmethod
	def __call__(self, values):
		"""Transform a scalar or array of values.

		Values which are outside of the domain should be transformed to ``NaN``.

		:param values: Scalar or :class:`numpy.ndarray` of floats.
		:returns: Transformed values in same form/shape as input.
		"""
		pass

	@abstractmethod
	def inverse(self, values):
		"""Calculate the inverse transform of a scalar or array of values.

		:param values: Scalar or :class:`numpy.ndarray` of floats.
		:returns: Inverse-transformed values in same form/shape as input.
		"""
		pass

	def __eq__(self, other):
		"""
		Two scales equal if they are of the same type and their parameters are
		equal.
		"""
		return isinstance(other, type(self)) and self.params == other.params

	def __hash__(self):
		return hash(self.params)

	def in_domain(self, values):
		"""Get which values are within the transform's domain.

		``scale.in_domain(val)`` should be equivalent to
		``numpy.isfinite(scale(val))``.

		:param values: Scalar or :class:`numpy.ndarray` of floats.
		:returns: Booleans in same form/shape as input.
		"""
		if np.isscalar(values):
			return True
		else:
			return np.ones_like(values, dtype=bool)

	def __repr__(self):
		param_reprs = [
			'{}={!r}'.format(name, self.params[name])
			for name in sorted(self.params)
		]
		return '{}({})'.format(
			type(self).__name__,
			', '.join(param_reprs)
		)


class LinScale(ScaleTransform, name='lin'):
	r"""Linear scale transform.

	.. math::

		\mathrm{LinScale}(x; \; T, A) = \frac{x + A}{T + A}

	See the Gating-ML documentation on the *flin* transform.

	.. attribute:: T

		Float parameter. The value that will be mapped to :math:`1.0`. The
		Gating-ML standard states this must be positive but the transformation
		is valid for any value.

	.. attribute:: A

		Float parameter, :math:`A \gt -T`. The negative of this value will be
		mapped to :math:`0.0`. The Gating-ML standard states that it should be
		between :math:`0` and :math:`T` but that is not necessary for the
		transformation to be defined and increasing.
	"""

	T = ScaleParameter(2 ** 18)
	A = ScaleParameter(0)

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		if self.A <= -self.T:
			raise ValueError('A must be > -T')

		self._slope = 1 / (self.A + self.T)

	def __call__(self, values):
		return (values + self.A) * self._slope

	def inverse(self, values):
		return values / self._slope - self.A

	@classmethod
	def from_range(cls, minimum, maximum):
		"""Create from (``min, max)`` range.

		:param float minimum: Value that will be mapped to 0.0, equal to -A.
		:param float maximum: Value that will be mapped to 1.0, equal to T.
		:rtype: .LinScale
		"""
		return cls(T=maximum, A=-minimum)


class LogScale(ScaleTransform, name='log'):
	r"""Scaled and shifted logarithmic scale transform.

	.. math::

		\mathrm{LogScale}(x; \; T, D) = \frac{\log_{10} \frac{x}{T}}{D} + 1

	See the Gating-ML documentation on the *flog* transform.

	.. attribute:: T

		Positive float parameter. The value that will be mapped to :math:`1.0`.

	.. attribute:: M

		Positive float parameter. The number of decades in the domain that
		will be mapped to the range :math:`[0, 1]`.
	"""

	M = ScaleParameter(4, validators=[v_positive])
	T = ScaleParameter(2 ** 18, validators=[v_positive])

	def __call__(self, values):
		return np.log10(values / self.T) / self.M + 1

	def in_domain(self, values):
		return values > 0

	def inverse(self, values):
		return np.power(10., (values - 1) * self.M) * self.T


class AsinhScale(ScaleTransform, name='asinh'):
	r"""Scaled and shifted hyperbolic arcsine scale transform.

	.. math::

		\mathrm{AsinhScale}(x; \; T, M, A) &= \frac{\mathrm{asinh}(a x) + b}{c}, \\

		a &= \frac{ \sinh{( M \ln{10} )} }{T} \\
		b &= A \ln{10} \\
		c &= (M + A) \ln{10}

	See the Gating-ML documentation on the *fasinh* transform.

	.. attribute:: T

		Positive float parameter. The value that will be mapped to :math:`1.0`.

	.. attribute:: A

		Positive float parameter. The additional number of negative decades
		that will be "brought to scale."

	.. attribute:: M

		Nonnegative float parameter. Large inputs are mapped to values similar
		to a ``(M + A)``-decade logarithmic scale.
	"""

	T = ScaleParameter(2 ** 18, validators=[v_positive])
	M = ScaleParameter(4, validators=[v_positive])
	A = ScaleParameter(0, validators=[v_nonneg])

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self._a = np.sinh(self.M * LOG10) / self.T
		self._b = self.A * LOG10
		self._c = 1. / (LOG10 * (self.M + self.A))

	def __call__(self, values):
		return (np.arcsinh(values * self._a) + self._b) * self._c

	def inverse(self, values):
		return np.sinh(values / self._c - self._b) / self._a


class InverseScaleTransform(ScaleTransform):
	r"""ABC for a scale transform defined in terms of its inverse.

	The logicle and hyperlog transforms to not have a nice closed form, but
	their inverses do. This base class creates a lookup table over
	approximately the 0-1 output range of the scale and uses interpolation to
	find the output value. Input values that fall outside the interpolation
	range are transformed using Newton's method.

	:param int n: Size of internal lookup table.
	:param tuple ybounds: Tuple of ``(min, max)``. Range of the output the
		lookup table should cover. Defaults to covering an extra 5% outside
		the 0 - 1 range.
	:param \**kwargs: Keyword arguments containing parameter values by name.
	"""

	def __init__(self, n=256, ybounds=(-0.05, 1.05), **kwargs):
		super().__init__(**kwargs)

		ymin, ymax = ybounds
		if ymax <= ymin:
			raise ValueError('ybounds[0] must be < ybounds[1]')

		self._process_params()
		self._calc_lut(n, ybounds)

	def _process_params(self):
		"""
		Used by child class to process parameter values before lookup table
		is calculated.

		After this method is called in the constructor the :meth:`inverse`
		method should work.
		"""
		pass

	def _calc_lut(self, n, ybounds):
		"""Calculate the lookup table for interpolating values.

		:param int n: Size of table.
		:param tuple ybounds: Tuple of ``(min, max)``. Range of the output the
			lookup table should cover.
		"""
		self._xbounds = tuple(map(self.inverse, ybounds))
		self._lut_y = np.linspace(*ybounds, n)
		self._lut_x = self.inverse(self._lut_y)

	def _interp(self, values):
		"""Calculate transformation by interpolating lookup table."""
		return np.interp(values, self._lut_x, self._lut_y)

	@abstractmethod
	def _newton_guess(self, x):
		"""Generate an initial guess to kick off newton's method.

		To be implemented by child class.

		:param x: Input values to transform, always as an array.
		:returns: Guess for output value.
		"""
		pass

	@abstractmethod
	def _newton_iter(self, y):
		"""
		Get function inverse value and derivative for an iteration of Newton's
		method.

		Returns a two-tuple for	the value of the inverse transform evaluated
		at ``y`` and the derivative of the inverse transform evaluated at
		``y``.

		:param x: Input value to transform, always as an array.
		:param x: Current guess for the output in the same shape as x.
		:returns: Tuple ``(finv, finvprime)``.
		"""
		pass

	def newton(self, values, maxiter=50):
		"""Calculate transformation using Newton's method.

		May be more accurate than lookup table method depending on iterations,
		but definitely slower.

		:param values: Scalar or numpy array of values to transform.
		:param int maxiter: Maximum number of iterations.
		:returns: Transformed array in same format as ``values``.
		"""

		x = np.asarray(values)

		# Get initial guess
		y = self._newton_guess(x)

		# Iteratively improve the guess
		for i in range(maxiter):
			f, fprime = self._newton_iter(y)

			y -= (f - x) / fprime

			if np.allclose(f, 0):
				break

		# Return scalar if needed
		if np.isscalar(values):
			return y[()]
		else:
			return y

	def __call__(self, values):
		# Check values are within interpolation range
		outside = (values < self._xbounds[0]) | (values > self._xbounds[1])

		# Calculate through interpolation or Newton's method as appropriate
		if np.isscalar(values):
			if outside:
				return self.newton(values)
			else:
				return self._interp(values)

		else:
			y = self._interp(values)
			if np.any(outside):
				y[outside] = self.newton(values[outside])

			return y


class LogicleScale(InverseScaleTransform, name='logicle'):
	r"""Logicle scale transform.

	The logicle is the inverse of the biexponential function:

	.. math::

		\mathrm{Biexp}(y; \; T, W, M, A) = a e^{b y} - c e^{-d y} - f

	where :math:`a, b, c, d, f` are functions of the alternate
	parameterization ``T, W, M, A`` used in the implementation.

	See the Gating-ML documentation on the *logicle* transform.

	Internally uses a lookup table to interpolate values within approximately
	the :math:`[0, 1]` range due to the lack of a closed-form inverse to the
	above function. Values outside this range are calculated using Newton's
	method.

	.. attribute:: T

		Positive float parameter. The value that will be mapped to :math:`1.0`.

	.. attribute:: M

		Positive float parameter. The number of decades that the true
		logarithmic scale approached at the high end of the Logicle scale
		would cover in the plot range.

	.. attribute:: W

		Float parameter, :math:`0 \leq W \leq M / 2`. Number of decades in the
		approximately linear region of the plot.

	.. attribute:: A

		Float parameter, :math:`-W \leq W \leq M - 2W`. Number of additional
		negative decades to include.
	"""

	T = ScaleParameter(2 ** 18, validators=[v_positive])
	M = ScaleParameter(4, validators=[v_positive])
	W = ScaleParameter(1, validators=[v_nonneg])
	A = ScaleParameter(0)

	def _process_params(self):
		"""Calculate the parameters for the biexponential function."""

		if self.W > self.M / 2:
			raise ValueError('W must be between 0 and M/2')
		if not -self.W <= self.A <= self.M - 2 * self.W:
			raise ValueError('A must be between -W and M - 2W')

		# This is all from the Gating-ML 2.0 standard:
		w = self.W / (self.M + self.A)
		x2 = self.A / (self.M + self.A)
		x1 = x2 + w
		x0 = x2 + 2 * w
		b = (self.M + self.A) * LOG10

		# Next we must find d such that 2(ln(d) - ln(b)) + w(d + b) = 0
		# Using the derivative:
		#     2/d + w
		# use Newton's methods to find a good approximation to d

		# Initial guess for d
		d = 1

		# Refine guess through Newton's method
		for i in range(200):
			f = 2 * (np.log(d) - np.log(b)) + w * (d + b)
			fprime = 2 / d + 1
			d -= f / fprime

			# Some arbitrary convergence tolerance (probably good enough)
			if abs(f) < 1e-7:
				break

		else:
			raise RuntimeError('Calculation did not converge')

		# The rest is straightforward
		ca = np.exp(x0 * (b + d))
		fa = np.exp(b * x1) - ca * np.exp(-d * x1)

		self._a = self.T / (np.exp(b) - fa - ca * np.exp(-d))
		self._b = b
		self._c = ca * self._a
		self._d = d
		self._f = fa * self._a

	def _newton_guess(self, x):
		"""
		Generate initial guess for y values based on which of the terms in the
		biexponential function will dominate.
		"""
		y = np.zeros_like(x)

		xf = x + self._f
		inv0 = self.inverse(0)

		r_p = (x > inv0) & (xf > 0)
		y[r_p] = np.log(xf[r_p] / self._a) / self._b

		r_n = (x < inv0) & (xf < 0)
		y[r_n] = -np.log(-xf[r_n] / self._c) / self._d

		return y

	def _newton_iter(self, y):

		term1 = self._a * np.exp(self._b * y)
		term2 = self._c * np.exp(-self._d * y)

		f = term1 - term2 - self._f
		fprime = self._b * term1 + self._d * term2

		return f, fprime

	def inverse(self, values):
		return self._a * np.exp(self._b * values) \
			- self._c * np.exp(-self._d * values) \
			- self._f
