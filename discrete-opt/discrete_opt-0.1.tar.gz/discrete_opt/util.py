import numpy as np


def make_hashable(o):
    """
    Makes a hashable object from a dictionary, list, tuple or set to any level, that contains
    only other hashable types (including any lists, tuples, sets, and
    dictionaries).
    Based on http://stackoverflow.com/questions/5884066/hashing-a-python-dictionary
    """
    if isinstance(o, (tuple, list, np.ndarray)):
        return tuple((make_hashable(e) for e in o))
    if isinstance(o, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in o.items()))
    if isinstance(o, (set, frozenset)):
        return tuple(sorted(make_hashable(e) for e in o))
    return o


class CachedFunction(object):
    """Caches function calls with the same arguments."""

    def __init__(self, fun, record_history=False):
        self.fun = fun
        self.cached_points = {}
        self.record_history = record_history
        self.history = []       # ordered history of uncached function evaluations
        self.uncached_fev = 0   # number of actual uncached function evaluations (cache misses)
        self.cached_fev = 0     # number of cached function calls (cache hits)

    def __call__(self, *args, **kwargs):
        cache_key = make_hashable((args, kwargs))
        try:
            y = self.cached_points[cache_key]
            self.cached_fev += 1
            return y
        except KeyError:
            self.uncached_fev += 1
            y = self.fun(*args, **kwargs)
            self.cached_points[cache_key] = y
            if self.record_history:
                self.history.append(args + (kwargs, y))
            return y


class SmoothedDiscreteFunction(object):
    """Smoothes a scalar function of a single discrete variable by linear interpolation between points."""

    def __init__(self, fun, x_domain):
        """
        Args:
            x_domain (np.ndarray): Array of values that represent the discrete domain of the function.
                Values can have type int or float.
        """
        self.fun = fun
        self.x_domain = np.sort(x_domain)

    def __call__(self, x):
        if x < self.x_domain[0] or x > self.x_domain[-1]:
            raise ValueError('x=%s is outside the domain [%s,%s]' % (x, self.x_domain[0], self.x_domain[-1]))
        x0_index = np.searchsorted(self.x_domain, x, side='right') - 1
        if self.x_domain[x0_index] == x:
            y = self.fun(x)
            logging.info('SmoothedDiscreteFunction(%f) = fun(%f) = %f' % (x, x, y))
            return y
        X = self.x_domain[x0_index:x0_index+2]
        Y = np.array([self.fun(xx) for xx in X])
        ifun = scipy.interpolate.interp1d(X, Y, assume_sorted=True, copy=False)
        y = ifun([x])[0]
        logging.info('SmoothedDiscreteFunction(%f) ~ fun(%s) = %f' % (x, X, y))
        return y


class SteppedDiscreteFunction(object):
    """Provided with a scalar function of multiple discrete variables, this will extend the domain
    to all real numbers by rounding down to the nearest value in the domain. This is performed for each
    dimension separately. This will create multi-dimensional "step" functions that are flat (zero gradient)
    except at the points in the original domain, where the gradients may be undefined.
    This can be used with `CachedFunction` to round down to the nearest point and cache that point."""

    def __init__(self, fun, x_domain):
        """
        Args:
            x_domain (list(np.ndarray)): Array of values that represent the discrete domain of the function.
                Values can have type int or float.
        """
        self.fun = fun
        self.x_domain = [np.sort(xi_domain) for xi_domain in x_domain]

    def convert_x(self, x):
        x = np.atleast_1d(x)
        assert(len(x) == len(self.x_domain))
        x_nearest = np.zeros(len(self.x_domain))
        for i in range(len(self.x_domain)):
            if x[i] <= self.x_domain[i][0]:
                x_nearest[i] = self.x_domain[i][0]
            elif x[i] >= self.x_domain[i][-1]:
                x_nearest[i] = self.x_domain[i][-1]
            else:
                xi0_index = np.searchsorted(self.x_domain[i], x[i], side='right') - 1
                x_nearest[i] = self.x_domain[i][xi0_index]
        return x_nearest

    def __call__(self, x):
        x_nearest = self.convert_x(x)
        y = self.fun(x_nearest)
        # logging.info('SteppedDiscreteFunction(%s) ~ fun(%s) = %f' % (x, x_nearest, y))
        return y


class PandasSeriesFunction(object):
    """Make a function out of a Pandas Series object."""
    def __init__(self, series):
        self.series = series

    def __call__(self, x):
        return self.series.ix[tuple(np.atleast_1d(x))]


class LoggingFunction(object):
    """This function wrapper will log all function calls."""
    def __init__(self, fun=None, name=None):
        self.fun = fun
        if name is None:
            try:
                name = fun.__name__
            except:
                name = 'LoggingFunction'
        self.name = name

    def __call__(self, *args, **kwargs):
        arg_str = [repr(a) for a in args]
        kwarg_str = ['%s=%s' % (k,repr(v)) for k, v in kwargs.items()]
        both_str = arg_str + kwarg_str
        joined_str = ', '.join(both_str)
        if self.fun is None:
            logging.info('%s(%s)' % (self.name, joined_str))
        else:
            result = self.fun(*args, **kwargs)
            logging.info('%s(%s) -> %s' % (self.name, joined_str, result))
            return result


def fit_parabola(X, Y):
    if not (len(X) == 3 and len(Y) == 3):
        raise ValueError()
    M = np.matrix(np.array([X**2, X, np.ones(3)]).T)
    a, b, c = np.linalg.solve(M, Y)  # coefficients of ax**2 + bx + c
    return a, b, c


def find_vertex_x_of_positive_parabola(X, Y):
    a, b, c = fit_parabola(X, Y)
    if a <= 0:
        raise ValueError('Parabola not positive')
    min_x = -b / (2.0*a)
    return min_x

