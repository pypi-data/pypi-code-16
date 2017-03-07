import numpy as np

from SplineLib import BSpline
from SplineLib.SplineSpace import TooShortKnotVectorError, SplineSpace, TooFewCoefficients


class TensorProductSplineSpace(object):
    def __init__(self, degrees, knots):
        """
        Initialize a tensor product spline space
        :param degrees: a 1x2 tuple of degrees
        :param knots: a 1x2 tuple containing a 1xn and 1xm array of knots
        :param dimension: the coefficient dimension
        """

        self.px, self.py = degrees
        self.tx, self.ty = knots
        self.nx, self.ny = len(knots[0]) - degrees[0] - 1, len(knots[1]) - degrees[1] - 1

        if self.nx < 1 or self.ny < 1:
            raise TooShortKnotVectorError(
                "The knot vectors have to be of at least length n + p + 1 , where n is the number of basis functions")

        self.basis_x = [BSpline(j, self.px, self.tx) for j in range(self.nx)]
        self.basis_y = [BSpline(j, self.py, self.ty) for j in range(self.ny)]

        self.S_x = SplineSpace(self.px, self.tx, dimension=1)
        self.S_y = SplineSpace(self.py, self.ty, dimension=1)

    def __str__(self):
        return """
        Tensor Product Spline Space:
                                 x  y
            basis degrees      = {px}, {py}
            number of knots    = {tx}, {ty}
            number of bsplines = {nx}, {ny}
        """.format(px=self.px, py=self.py, tx=len(self.tx), ty=len(self.ty), nx=self.nx, ny=self.ny)

    def evaluate_basis(self):

        raise NotImplementedError("This is not implemented yet")

    def xy_values(self, n=(100, 100), knot_range='active', eps=1.0e-14):
        """
        Returns a mesh of xy_values
        :param n: 1x2 tuple containing resolution in x, y direction respectively
        :param knot_range: whether to use the whole knot vectors, or just the range with full support
        :return: two nd numpy arrays
        """

        x_values = self.S_x.x_values(n[0], knot_range, eps)
        y_values = self.S_y.x_values(n[1], knot_range, eps)

        return x_values, y_values

    class TensorProductSplineFunction(object):
        def __init__(self, coefficients, knots, degree, n, callable_function):
            self.c = coefficients
            self.t = knots
            self.p = degree
            self.n = n
            self.f = callable_function

        def __call__(self, x, y):
            return self.f(x, y)

    def function(self, coefficients, derivative=0):
        coefficients = np.array(coefficients)
        n, m = coefficients.shape
        if n != self.nx or m != self.ny:
            raise TooFewCoefficients(
                "This spline space requires {n}x{m} coefficients, was given {nn}x{mm}".format(n=self.nx, m=self.ny,
                                                                                              nn=n, mm=m))

        def f(x, y):

            if isinstance(x, (list, tuple, np.ndarray)) and isinstance(y, (list, tuple, np.ndarray)):
                f_values = np.zeros(shape=(len(x), len(y)))
                for i, X in enumerate(x):
                    for j, Y in enumerate(y):
                        mu_x = self.S_x.index(X)
                        mu_y = self.S_y.index(Y)

                        non_zero_b_splines_x = self.S_x.evaluate_non_zero_basis_splines(X, mu_x, derivative=0)
                        non_zero_b_splines_y = self.S_y.evaluate_non_zero_basis_splines(Y, mu_y, derivative=0)

                        non_zero_coefficients_x = coefficients[mu_x - self.px: mu_x + 1, mu_y - self.py: mu_y + 1]

                        f_values[i, j] = non_zero_b_splines_x.dot(non_zero_coefficients_x).dot(non_zero_b_splines_y)
            return f_values

        return self.TensorProductSplineFunction(coefficients, [self.tx, self.ty], [self.px, self.py],
                                                [self.nx, self.ny], f)
