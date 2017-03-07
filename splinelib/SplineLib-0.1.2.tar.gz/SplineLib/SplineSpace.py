import numpy as np

from SplineLib.BSpline import BSpline


class TooShortKnotVectorError(Exception):
    pass


class TooFewCoefficients(Exception):
    pass


class TooHighDerivativeRequested(Exception):
    pass


class SplineSpace(object):
    def __init__(self, degree, knots, dimension):
        """
        Creates a spline space of given degree and knot vector.
        :param degree: int - degree of basis functions
        :param knots: 1D list/vector/array - knot values
        :param dimension: tells the spline functions what space their coefficients are in
        """
        self.p = degree
        self.t = knots
        self.n = len(knots) - degree - 1
        self.s = dimension

        # TODO: Should this be n < 1, and not n <= 1? Make a test.
        if self.n < 1:
            raise TooShortKnotVectorError(
                "The knot vector has to be of at least length n + p + 1 = {l}, where n is the number of basis functions.".format(
                    l=self.n + self.p + 1))
        self.basis = [BSpline(j, self.p, self.t) for j in range(self.n)]

    def evaluate_basis(self, res=100):
        """
        Evaluates the basis functions over the
        interval with full support.
        :return: nd.array of basis values
        """
        t = self.t
        n = self.n
        x_values = self.x_values(res, knot_range='all')
        s_values = []
        for i in range(n):
            c = [0] * n
            c[i] = 1
            f = self.function(c)
            s_values.append(f(x_values))
        return x_values, s_values

    def evaluate_dual_polynomials(self, res=1000, knot_range='active'):
        """
        Evaluates the basis dual polynomials over the
        :param res:
        :param knot_range:
        :return:
        """
        t = self.t
        n = self.n
        x_values = self.x_values(res, knot_range)
        s_values = []
        for i in range(n):
            result = np.zeros(res)
            B = self.basis[i]
            for j, x in enumerate(x_values):
                result[j] = B.dual_polynomial(x)
            s_values.append(result)
        return x_values, np.array(s_values)

    def evaluate_non_zero_basis_splines(self, x, mu, derivative=0, eps=1.0e-14):
        """
        Evaluates the p+1 non-zero b-splines in the interval t_mu, t_mu+1 at the point x.
        Note, this only holds for p <= mu <= n.
        :param x:
        :param mu:
        :param derivative: denotes the number of differentiations to perform. 0 denotes no diff.
        :return:
        """

        t = np.array(self.t, dtype=np.float64)
        p = self.p
        b = 1
        r = derivative

        if r > p:
            raise TooHighDerivativeRequested(
                'Cannot differentiate a degree {d} spline more than {d} times. {r} requested'.format(d=p, r=r))
        for k in range(1, p - r + 1):
            # extract relevant knots
            t1 = t[mu - k + 1: mu + 1]
            t2 = t[mu + 1: mu + k + 1]
            # append 0 to end of first term, and insert 0 to start of second term
            omega = np.divide((x - t1), (t2 - t1), out=np.zeros_like(t1), where=((t2 - t1) != 0))
            b = np.append((1 - omega) * b, 0) + np.insert((omega * b), 0, 0)

        if r == 0:
            # if no derivatives requested, just return b
            return b

        for k in range(p - r + 1, p + 1):
            # augment old vector
            b = np.append(b, 0)
            b = np.insert(b, 0, 0)
            b_new = np.zeros(k + 1)
            for i, j in enumerate(range(mu - k, mu + 1)):
                denom_1 = (t[j + k] - t[j])
                denom_2 = (t[j + k + 1] - t[j + 1])
                if denom_1 > eps:
                    b_new[i] += b[i] / denom_1
                if denom_2 > eps:
                    b_new[i] -= b[i + 1] / denom_2
            b = b_new
        return np.math.factorial(p) / np.math.factorial(p - r) * b

    def index(self, x):
        """
        Finds the index mu, such that t_mu <= x < t_mu+1.
        If x is larger than the last knot, the last index is returned
        :param x: parameter value
        :return: index mu
        """
        t = self.t
        for i in range(len(t) - 1):
            if t[i] <= x < t[i + 1]:
                return i

    class SplineFunction(object):

        def __init__(self, coefficients, knots, degree, n, callable_function):
            self.c = coefficients
            self.t = knots
            self.p = degree
            self.n = n
            self.f = callable_function

        def get_control_points(self):
            """
            :return: returns the set of control points (t_j*, c_j)
            for the spline function.
            """

            p = self.p
            t = self.t
            c = self.c
            n = self.n
            control_points = []
            for j in range(0, n):
                t_average = sum(t[j + 1: j + p + 1]) / float(p)
                control_points.append((t_average, c[j]))
            return control_points

        def __call__(self, x):
            return self.f(x)

    def function(self, coefficients, derivative=0):
        """
        Given coefficients, return the corresponding spline function.
        :param coefficients: a vector length n containing s-tuples
        :return: a callable function object representing the spline function. Is vectorized, so can be called with a numpy array.
        """

        if len(coefficients) != self.n:
            raise TooFewCoefficients(
                'This spline space requires {n} coefficients. Was given {m}'.format(n=self.n, m=len(coefficients)))

        coefficients = np.array(coefficients)

        def f(x):
            # TODO: Do this more elegantly, refactor into two separate functions

            if isinstance(x, (float, int)):
                mu = self.index(x)
                non_zero_b_splines = self.evaluate_non_zero_basis_splines(x, mu, derivative=derivative)
                non_zero_coefficients = coefficients[mu - self.p: mu + 1]

                total = sum([c * b for c, b in zip(non_zero_coefficients, non_zero_b_splines)])
                return total

            elif isinstance(x, (list, tuple, np.ndarray)):

                f_values = np.zeros(len(x))
                for i, X in enumerate(x):
                    mu = self.index(X)
                    non_zero_b_splines = self.evaluate_non_zero_basis_splines(X, mu, derivative=derivative)
                    non_zero_coefficients = coefficients[mu - self.p: mu + 1]

                    total = sum([c * b for c, b in zip(non_zero_coefficients, non_zero_b_splines)])
                    f_values[i] = total
                return f_values

        return self.SplineFunction(coefficients, self.t, self.p, self.n, f)

    def x_values(self, n=100, knot_range='active', eps=1.0e-14):
        """
        Returns a set of n x_values, either over the whole
        knot vector, or over the knots where p + 1 basis splines are active.
        :param n: number of x_values
        :param knot_range: string, either 'active' or 'all'
        :return:
        """
        if knot_range == 'all':
            return np.linspace(self.t[0], self.t[-1] - eps, n)
        elif knot_range == 'active':
            return np.linspace(self.t[self.p], self.t[self.n] - eps, n)

    def __str__(self):
        return """
        Spline Space:
            dimension          = {s}
            basis degree       = {p}
            number of knots    = {knots}
            number of bsplines = {n}
        """.format(p=self.p, knots=len(self.t), s=self.s, n=self.n)
