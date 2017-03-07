import numpy as np


class BSpline(object):
    def __init__(self, index, degree, knots):
        """
        :param index: which basis spline to represent
        :param degree: the basis spline degree
        :param knots: the given knot vector
        """

        self.i = index
        self.p = degree
        self.t = np.array(knots, dtype=np.float64)
        self.a = knots[index]
        self.b = knots[index + 1]

    def __call__(self, x):
        if self.p == 0:
            return self._degree_zero(x)
        else:
            return self._recursive(x)

    def _degree_zero(self, x):
        if self.a <= x < self.b:
            return 1.0
        else:
            return 0.0

    def _recursive(self, x):
        t = self.t
        p = self.p
        i = self.i
        denom_one = t[i + p] - t[i]
        denom_two = t[i + p + 1] - t[i + 1]

        eps = 1.0e-14
        if denom_one < eps or denom_two < eps:
            # if the denominator is essentially zero, return zero
            return 0.0

        lambda_one = (x - t[i]) / float(denom_one)
        lambda_two = (t[i + 1 + p] - x) / float(denom_two)

        return lambda_one * BSpline(i, p - 1, t)(x) + lambda_two * BSpline(i + 1, p - 1, t)(x)

    def dual_polynomial(self, y):
        """
        returns the dual polynomial of the B-spline, evaluated at the point y.
        That is, the product of (y - t_i)'s for i = j, ..., j+p
        y can be any real number.
        """
        i = self.i
        t = self.t
        p = self.p

        # dual polynomials of degree 0 are identically 1.
        if p == 0:
            return 1

        dual_poly = 1
        for j in range(i, i+ p + 1):
            dual_poly *= (y - t[j])
        return dual_poly

    def __str__(self):
        return """
        Basis Spline:
            number = {i}
            degree = {p}

        """.format(p=self.p, i=self.i)
