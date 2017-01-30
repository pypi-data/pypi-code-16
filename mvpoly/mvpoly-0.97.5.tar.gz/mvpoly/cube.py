"""

.. class:: MVPolyCube
   :synopsis: Multivariate polynomial class whose
   coefficient representation is an ND-array

.. moduleauthor:: J.J. Green <j.j.green@gmx.co.uk>

"""

import mvpoly.base
import mvpoly.util.cube
import mvpoly.util.dtype

import numbers
import numpy as np


class MVPolyCube(mvpoly.base.MVPoly):
    """
    Return an object of class :class:`MVPolyCube` with
    the coefficient array set to the optional *coef*
    argument, a :class:`numpy.ndarray`.
    """
    def __init__(self, arg=None, **kwd):
        if isinstance(arg, mvpoly.base.MVPoly):
            coef = self.init_from_nonzero(arg, arg.dtype).coef
            kwd['dtype'] = arg.dtype
        else:
            coef = arg
        super(MVPolyCube, self).__init__(**kwd)
        self._coef = np.array([] if coef is None else np.atleast_1d(coef),
                              dtype=self.dtype)

    def __getitem__(self, key):
        """
        The get-index method which returns the coefficients of the
        polynomial by their (zero-based) indices. For the polynomial
        :math:`p(x,y) = 2x^2 + y + 3` we would access the coefficient of
        :math:`x^2` with ``p[2]`` or ``p[2, 0]`` or ``p[2, 0, 0]`` ...
        (trailing zeros are ignored), the coefficient of
        :math:`y` with ``p[0, 1]``, ``p[0, 1, 0]``, ... and the constant
        term with  ``p[()]``, ``p[0]``, ``p[0, 0]``, ... (Note that ``p[]``
        is a Python syntax error).  Indices outside the shape of the
        underlying NumPy array will return zero (without changing shape of
        the array).

        Note that slice indexing will not work here, ``p[1:3]`` will
        result in an error: instead use the
        :py:meth:`~mvpoly.cube.MVPolyCube.coef`
        method to access the underlying array, ``p.coef[1:3]``.
        """
        key1d = np.atleast_1d(key)
        narg = len(key1d)
        coef1d = np.atleast_1d(self.coef)
        nvar = len(coef1d.shape)
        if narg > nvar:
            if (key1d[nvar:] == 0).all():
                key1d = key1d[:nvar]
            else:
                return 0
        elif narg < nvar:
            zeropad = np.zeros(nvar - narg, dtype=int)
            if narg == 0:
                key1d = zeropad
            else:
                key1d = np.hstack((key1d, zeropad))
        try:
            val = coef1d[tuple(key1d)]
        except IndexError:
            val = 0
        return val

    def __setitem__(self, key, value):
        """
        As :py:meth:`~mvpoly.cube.MVPolyCube.__getitem__`,
        but setting the coefficient. The underlying array is
        grown to accomodate the new coefficient if needed.
        """
        A = self.coef
        key = mvpoly.util.common.coerce_tuple(key)
        # coerce dimensional agreement
        dd = len(A.shape) - len(key)
        if dd > 0:
            key = key + tuple(0 for _ in range(dd))
        elif dd < 0:
            newshape = mvpoly.util.cube.dimension_pad(A.shape, len(key))
            A = np.reshape(A, newshape)
        # minimal shape which contains A and the key
        newshape = tuple(max(A.shape[n], key[n] + 1) for n in range(len(key)))
        if newshape != A.shape:
            A = mvpoly.util.cube.array_enlarge(A, newshape)
        A[key] = value
        self.coef = A

    def __add__(self, other):
        """
        Add an :class:`MVPolyCube` to another, or to a :class:`numpy.ndarray`,
        or to a number; return an :class:`MVPolyCube`.
        """
        a = self.coef
        if isinstance(other, MVPolyCube):
            b = other.coef
        elif isinstance(other, (numbers.Number, np.generic)):
            b = np.array([other])
        else:
            msg = "cannot add MVPolyCube to {0!s}".format(type(other))
            raise TypeError(msg)
        dtype = mvpoly.util.dtype.dtype_add(a.dtype, b.dtype)
        return MVPolyCube(mvpoly.util.cube.padded_sum(a, b), dtype=dtype)

    def __radd__(self, other):
        """
        As add, but with the types in the opposite order -- this is
        routed to add.
        """
        return self.__add__(other)

    def __neg__(self):
        """
        Negation of a polynomial, return the polynomial with negated
        coefficients.
        """
        return MVPolyCube(-(self.coef), dtype=self.dtype)

    def __mul__(self, other):
        """
        Convolve our coefficient array with that of *other*
        and return an :class:`MVPolyCube` object initialised with
        the result.
        """
        if isinstance(other, MVPolyCube):
            coef = mvpoly.util.cube.convn(self.coef, other.coef)
        else:
            if isinstance(other, numbers.Number):
                other = mvpoly.util.common.as_numpy_scalar(other)
            if isinstance(other, np.generic):
                coef = self.coef * other
            else:
                msg = "cannot multiply MVPolyCube by {0!s}".format(type(other))
                raise TypeError(msg)
        return MVPolyCube(coef, dtype=coef.dtype)

    def __rmul__(self, other):
        """
        Reverse order multiply, as add
        """
        return self.__mul__(other)

    def __eq__(self, other):
        """
        Equality of polynomials.
        """
        return ((self - other).coef == 0).all()

    def astype(self, dtype):
        """
        Return a polynomial using the specified *dtype* for the
        coefficients.
        """
        return MVPolyCube(self.coef.astype(dtype), dtype=dtype)

    @property
    def coef(self):
        """
        The NumPy array of coefficients.
        """
        return self._coef

    @coef.setter
    def coef(self, value):
        self._coef = np.array(value, dtype=self.dtype)

    @property
    def degrees(self):
        """
        Return the maximal degree of each of the variables of
        the polynomial as a tuple of integers. For a constant
        (including a zero) polynomial, returns the empty tuple.
        """
        if self.coef.any() and self.coef.shape != (1,):
            return tuple(n - 1 for n in self.coef.shape)
        else:
            return ()

    @property
    def degree(self):
        """
        The (total, homogeneous) *degree*, the maximal sum of the
        monomial degrees of monomials with nonzero coefficients.
        Returns :math:`-1` for the zero polynomial, :math:`0` for
        a constant polynomial.
        """
        nzis = np.nonzero(self.coef)
        degs = [sum(t) for t in zip(*nzis)]
        if not degs:
            return -1
        return np.max(degs)

    def eval(self, *args):
        """
        Evaluate the polynomial at the points given by *args*.
        There should be as many arguments as the polynomial
        has variables.  The argument can be numbers, or arrays
        (all of the same shape).
        """
        deg = self.degree
        if deg == -1:
            shape = np.array(args[0]).shape
            return np.zeros(shape, dtype=self.dtype)
        elif deg == 0:
            shape = np.array(args[0]).shape
            return self.coef * np.ones(shape, dtype=self.dtype)
        else:
            return mvpoly.util.cube.horner(self.coef, self.dtype, *args)

    def compose(self, *args):
        """
        Compose polynomials. The arguments, which should be
        :class:`MVPolyCube` polynomials, are substituted
        into the corresponding variables of the polynomial.
        """

        dims = self.coef.shape
        N = len(dims)

        if N != len(args):
            fmt = "bad number of args ({0:d}) for a {1:d}-variable polynomial"
            raise ValueError(fmt.format(len(args), N))
        C = self.coef.flat

        # generate list-of-list of powers of monomials

        X = [0] * N
        for i in range(N):
            order = dims[i] - 1
            if not order > 0:
                continue
            Xi = [0] * order
            Xi0 = args[i]
            Xi[0] = Xi0
            for n in range(1, order):
                Xi[n] = Xi[n - 1] * Xi0
            X[i] = Xi

        # iterate through coefficients of p, accumulating
        # the monomials in the output q

        q = MVPolyCube([0], dtype=self.dtype)

        for i in range(np.prod(dims)):
            if C[i] == 0:
                continue
            M = MVPolyCube([1], dtype=self.dtype)
            idx = np.unravel_index(i, dims)
            for j, idxj in enumerate(idx):
                n = idxj - 1
                if n >= 0:
                    M = M * X[j][n]
            q += C[i] * M

        return q

    def diff(self, *args):
        """
        Differentiate polynomial. The integer arguments
        should indicate the number to times to differentiate
        with respect to the corresponding polynomial variable,
        hence ``p.diff(0,1,1)`` would correspond to
        :math:`\partial^2 p / \partial y \partial z`.
        """
        coef = mvpoly.util.cube.diff(np.atleast_1d(self.coef), args)
        return MVPolyCube(coef, dtype=self.dtype)

    def int(self, *args, **kwargs):
        """
        Indefinite integral of polynomial. The arguments are as for
        :py:meth:`~mvpoly.cube.MVPolyCube.diff`,
        but an optional *dtype* keyword argument can be appended to
        specify the *dtype* of the output polynomial.
        """
        dtype = np.dtype(kwargs.get('dtype', self.dtype))
        coef = mvpoly.util.cube.int(np.atleast_1d(self.coef), args, dtype)
        return MVPolyCube(coef, dtype=dtype)

    def maxmodnb(self, **kwargs):
        """
        Maximum modulus of the polynomial on the unit ball, this
        method is only available if the :mod:`maxmodnb` package
        is installed (and that is in an early stage of development).
        """
        return mvpoly.util.cube.maxmodnb(self.coef, **kwargs)

    @property
    def nonzero(self):
        """
        Returns a list of 2-element tuples, for each the first
        being a (monomial) index, the second the corresponding
        coefficient. The indices have trailing zeros, so the return
        value for the polynomial
        :math:`p(x,y) = 2 + 3x + 4y` would be
        ``[((0, 0), 2), ((1, 0), 3), ((0, 1), 4)]``.
        """
        dt = self.dtype
        nzidx = np.nonzero(self.coef)
        return list(zip((tuple(idx) for idx in np.transpose(nzidx)),
                        (np.array(c, dtype=dt) for c in self.coef[nzidx])))

    def norm(self, order):
        """
        Returns the *norm* of the coefficients.  The *order*
        can be a float (for the p-norm) or any other value
        accepted by the :meth:`numpy.linalg.norm` method.
        """
        if self.coef.size > 0:
            return np.linalg.norm(self.coef.flat, order)
        else:
            return 0

    @classmethod
    def monomials(cls, n, k, **kwd):
        """
        Return an array of all of the *n*-variate monomials of
        (homogeneous) degree less than or equal to *k*.
        """
        def monomial_from_index(index, **kwd):
            deg = sum(index) + 1
            m = np.zeros([deg] * len(index), **kwd)
            m[index] = 1
            return cls(m, **kwd)

        return [monomial_from_index(idx, **kwd)
                for idx in
                mvpoly.util.common.monomial_indices(n, k)]

    @classmethod
    def init_from_nonzero(cls, p, dtype):
        """
        Create a polynomial from a polynomial of any subclass; this is
        used internally by the
        :py:meth:`~mvpoly.cube.MVPolyCube.__init__` constructor, but
        may be useful for direct application.
        """
        shp = tuple(1 + d for d in p.degrees)
        nvar = len(shp)
        coef = np.zeros(shp, dtype=dtype)
        for pair in p.nonzero:
            idx, val = pair
            idx = idx + tuple(0 for _ in range(nvar - len(idx)))
            coef[idx] = val
        return cls(coef, dtype=dtype)

    @classmethod
    def variables(cls, n, **kwd):
        """
        Return a *n*-tuple of each of the variables (*x*, *y*, ..)
        as monomials of an *n*-variate system.
        """
        return [cls.variable(i, n, **kwd) for i in range(n)]

    @classmethod
    def variable(cls, i, n, **kwd):
        """
        Return the *i*-th variable of an *n*-variate system,
        (*i* = 0, ..., *n*-1).
        """
        shp = tuple((1 if j == i else 0) for j in range(n))
        m = np.zeros([s + 1 for s in shp], **kwd)
        m.itemset(shp, 1)
        return cls(m, **kwd)

    @classmethod
    def zero(cls, **kwd):
        """
        Return the zero polynomial.
        """
        return cls(**kwd)

    @classmethod
    def one(cls, **kwd):
        """
        Return the unit (1) polynomial.
        """
        return cls(1, **kwd)

    @classmethod
    def lehmer(cls, **kwargs):
        """
        Returns the
        `Lehmer polynomial <http://en.wikipedia.org/wiki/Lehmer%27s_conjecture>`_
        (univariate of degree 10), notable as the polynomial
        whose Mahler measure is the smallest known measure larger than
        1 of a polynomial with integer coefficients.
        """  # noqa
        dtype = kwargs.get('dtype', int)
        kwargs['dtype'] = dtype
        coef = np.array([1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1], dtype=dtype)
        return cls(coef, **kwargs)

    @classmethod
    def rudin_shapiro(cls, n, **kwargs):
        """
        Returns the *n*-th
        `Rudin-Shapiro polynomial <http://en.wikipedia.org/wiki/Rudin-Shapiro_polynomials>`_
        (univariate, of degree :math:`2^n-1`). These dense polynomials have
        coefficients which are :math:`\pm1` and have a small
        maximum modulus on the unit disk.
        """  # noqa
        dtype = kwargs.get('dtype', int)
        kwargs['dtype'] = dtype

        p = np.array([1], dtype=dtype)
        q = np.array([1], dtype=dtype)

        for i in range(n):
            p1 = p
            p = np.hstack((p1, q))
            q = np.hstack((p1, -q))

        return cls(p, **kwargs)

    @classmethod
    def wendland(cls, d, k, **kwargs):
        r"""
        The *k*-th Wendland polynomial :math:`p_{d, k}(r)` for dimension
        *d*, this univariate polynomial of degree
        :math:`\lfloor d/2 \rfloor + 3k + 1` is used to define a compactly
        supported radial basis function with continuous derivatives up to
        order :math:`2k`.  The calculation of the coefficients uses the
        recursive method described by Wendland in [#HW1]_.

        .. [#HW1]
            Holger Wendland,
            *Error estimates for interpolation by compactly supported radial
            basis functions of minimal degree*,
            J. Approx. Theory,
            93 (2), 1998, 258--272
        """

        def m1p(k):
            if k % 2:
                return -1
            else:
                return 1

        def dL(L, j, s, cache):
            key = (j, s)
            if key in cache:
                return cache[key]

            if s == 0:
                val = m1p(j) * mvpoly.util.common.binom(L, j)
            elif j == 1:
                val = 0
            elif j == 0:
                val = 0
                for k in range(0, L + 2 * s - 1):
                    val += dL(L, k, s - 1, cache) / float(k + 2)
            else:
                val = - dL(L, j - 2, s - 1, cache) / float(j)

            cache[key] = val

            return val

        L = (d // 2) + k + 1
        M = L + 2 * k + 1

        cache = dict()
        coefs = np.array([dL(L, j, k, cache) for j in range(M)], dtype=float)
        cache.clear()

        return cls(coefs, **kwargs)
