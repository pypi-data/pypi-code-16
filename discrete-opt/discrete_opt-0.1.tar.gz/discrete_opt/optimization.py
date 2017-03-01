import logging
import itertools

import numpy as np
from scipy.optimize import OptimizeResult, minimize_scalar
import scipy.constants

from .util import find_vertex_x_of_positive_parabola


def scalar_discrete_gap_filling_minimizer(
        fun, bracket, args=(), tol=1.0, maxfev=None, maxiter=100, callback=None, verbose=False,
        parabolic_method=False, golden_section_method=False, best_x_aggregator=None, **options):
    """Find a local minimum of a scalar function of a single integer variable.
    The domain of the function is all integers between, and including, the bracket.
    The function may have flat spots where f(a) == f(b) for a != b and this method will
    attempt to search around and within the flat spots.
    The function must have exactly one local minimum in the bracket.
    This method maintains a left and right bracket, where the function value is greater than the best known minimum.
    It also maintains a list of best x values, and the function values at all of these x values equals the best known
    minimum.
    At each iteration, it finds the largest gap in these x values (including the brackets) and selects
    the point in the center of the largest gap.
    It will then either adjust the bracket or add to the list of best x values.
    The method terminates when the largest gap is less than or equal to tol.

    Args:
        bracket (tuple): A tuple of the bounds of the function (x_min, x_max).
            Optionally, a middle point can be specified and it will be the initial best point.
        tol (float): The method terminates when the largest gap is less than or equal to this value.

    """
    # bestx is a list.
    # besty is a scalar and equals f(x) for all x in bestx.

    funcalls = 0

    # print('parabolic_method=%s,golden_section_method=%s' % (parabolic_method,golden_section_method))

    if len(bracket) == 2:
        bracket_left_x = bracket[0]
        bracket_right_x = bracket[1]
        bestx = [np.round(np.mean([bracket_left_x, bracket_right_x]))]
        a = bracket_left_x
        b = bracket_right_x
        if golden_section_method:
            bestx = [np.round(b - (b - a) / scipy.constants.golden)]
        else:
            bestx = [np.round(np.mean([a, b]))]
    elif len(bracket) == 3:
        bracket_left_x = bracket[0]
        bracket_right_x = bracket[2]
        bestx = [bracket[1]]
    else:
        raise ValueError('Invalid bracket')

    assert isinstance(bestx, list)

    if not (bracket_left_x <= bestx[0] <= bracket_right_x):
        raise ValueError('Invalid bracket')

    if best_x_aggregator is None:
        best_x_aggregator = lambda x: x[int((len(x)-1)/2)]

    # Evaluate function at bestx.
    besty = fun(bestx[0])
    funcalls += 1
    assert np.isscalar(besty)

    # Evaluate function at brackets to determine if they are better than the initial bestx.
    bracket_left_y = fun(bracket_left_x, *args)
    bracket_right_y = fun(bracket_right_x, *args)
    funcalls += 2
    if bracket_left_y < besty:
        bestx = [bracket_left_x]
        besty = bracket_left_y
    if bracket_right_y < besty:
        bestx = [bracket_right_x]
        besty = bracket_right_y

    if verbose: logging.info('bracket=(%f,%s,%f); besty=%f' % (bracket_left_x, str(bestx), bracket_right_x, besty))

    niter = 0
    while niter < maxiter:
        niter += 1

        X = np.array([bracket_left_x] +  bestx               + [bracket_right_x])
        Y = np.array([bracket_left_y] + [besty] * len(bestx) + [bracket_right_y])

        # if verbose:
        #     logging.info('X=%s' % str(X))
        #     logging.info('Y=%s' % str(Y))

        testx = None
        testx_index = None

        #
        #  Step 1: Determine the value of x to test next (testx).
        #

        # If we have exactly one bestx, then fit a parabola to the 3 points and test the vertex.
        if parabolic_method and len(bestx) == 1:
            if verbose: logging.info('Attempting parabolic method')
            try:
                # Attempt to fit a parabola to the 3 points and find the vertex.
                testx = find_vertex_x_of_positive_parabola(X, Y)
                if verbose: logging.info('Parabolic method returned testx=%f' % testx)
                testx = np.round(testx)
                if testx <= bracket_left_x or testx >= bracket_right_x or testx == bestx[0]:
                    testx = None
                elif testx <= bestx[0]:
                    testx_index = 0
                else:
                    testx_index = 1
            except:
                # This will happen if a parabola can't be fit through the 3 points.
                # Ignore error and use the gap method below.
                testx = None
        if testx is None:
            # Measure gaps in brackets and bestx and find the largest one.
            if verbose: logging.info('Attempting gap method')
            gaps = np.diff(X)
            testx_index = np.argmax(gaps)
            gapsize = gaps[testx_index]
            if gapsize <= tol:
                if verbose: logging.info('Achieved gap size tol')
                break

            # Pick a point between the largest gap.
            a = X[testx_index]
            b = X[testx_index + 1]
            if golden_section_method:
                golden_distance = (b - a) / scipy.constants.golden
                if bool(np.random.randint(low=0, high=2)):
                    testx = np.round(b - golden_distance)
                else:
                    testx = np.round(a + golden_distance)
            else:
                testx = np.round(np.mean([a, b]))

            if verbose: logging.info('gapsize=%f, len(bestx)=%d, testx=%f' % (gapsize, len(bestx), testx))

        assert(testx is not None)
        assert(testx_index is not None)
        assert(bracket_left_x <= testx <= bracket_right_x)

        #
        #  Step 2: Evaluate function at testx.
        #

        testy = fun(testx, *args)
        funcalls += 1

        #
        #  Step 3: Update bracket, etc. based on function value testy at testx.
        #

        add_to_bestx = False

        if testy < besty:
            # Found a point better than all others so far.
            # The new bracket will be the points to the immediate left and right of the test point.
            bestx = [testx]
            besty = testy
            bracket_left_x = X[testx_index]
            bracket_left_y = Y[testx_index]
            bracket_right_x = X[testx_index + 1]
            bracket_right_y = Y[testx_index + 1]
        elif testy > besty:
            # Point is worse than best. Reduce bracket.
            if testx_index == 0:
                # Test point was adjacent to left bracket.
                bracket_left_x = testx
                bracket_left_y = testy
            elif testx_index == len(X) - 2:
                # Test point was adjacent to right bracket.
                bracket_right_x = testx
                bracket_right_y = testy
            else:
                # Test point was inside the set of bestx points but is worse than besty.
                # This indicates more than one local minima or a round off error.
                # We will assume a round off error and handle it as if it had the same besty.
                add_to_bestx = True
        else:
            # Point is same as best. Add it to the bestx list.
            add_to_bestx = True

        if add_to_bestx:
            bestx = sorted(bestx + [testx])

        if verbose: logging.info('bracket=(%f,%s,%f); besty=%f' % (bracket_left_x, str(bestx), bracket_right_x, besty))
        if callback is not None:
            callback(bestx)
        if maxfev is not None and funcalls >= maxfev:
            break

    # Return the x that is in the median of bestx.
    bestx = best_x_aggregator(np.array(bestx))

    return OptimizeResult(fun=besty, x=bestx, nit=niter, nfev=funcalls, success=(niter > 1))


def multivariate_discrete_gap_filling_minimizer(
        fun, x0, bounds, args=(), tol=1.0, maxfev=None, maxiter=2, callback=None, verbose=False,
        scalar_options={}, axes=None, **options):
    """It is assumed that there is exactly one local minimum in the domain.
    For each dimension, the domain of the function consists of all integers between, and including, the bounds.
    The function may have flat spots where f(a) == f(b) for a != b and this method will
    attempt to search around and within the flat spots.
    This multivariate method uses `scalar_gap_filling_minimizer` repeatedly along each dimension
    for a fixed number of iterations. There is currently no other stopping criteria.

    Args:
        fun: Function of a single variable of a list-type.
        x0 (np.ndarray): Initial guess.
        bounds: List-type of (min, max) pairs for each element in x, defining the bounds in that dimension.
        tol: See `scalar_discrete_gap_filling_minimizer`.
        axes (np.ndarray): Number of columns must equal length of x0.
            The rows will determine the set of axes that this function will optimize along.
            Leave as None to use unit axes along each dimension.
    """

    ndims = len(x0)

    bounds = np.array(bounds)
    if bounds.shape != (ndims, 2):
        raise ValueError()

    if axes is None:
        axes = np.eye(ndims)

    if axes.shape[1] != ndims:
        raise ValueError()

    naxes = len(axes)
    if naxes <= 0:
        raise ValueError()

    bestx = x0
    besty = np.inf
    niter = 0
    funcalls = 0

    while niter < maxiter:
        niter += 1
        for i in range(naxes):
            axis = axes[i]
            if verbose:
                logging.info('multivariate_discrete_gap_filling_minimizer: axis %d, %s' % (i, str(axis)))

            def transform(t):
                return bestx + t*axis

            # Function of single variable (t) that we will optimize during this iteration.
            def scalar_fun(t):
                testx = transform(t)
                return fun(testx)

            # logging.info(transform(0.0))
            # logging.info(scalar_fun(0.0))

            # Determine bracket along optimization axis (for t).
            # All axes must remain within their respective bounds.
            bracket = np.array([-np.inf, 0.0, np.inf])
            for j in range(ndims):
                if axis[j] != 0.0:
                    btj = np.sort((bounds[j] - bestx[j]) / axis[j])
                    if bracket[0] < btj[0]:
                        bracket[0] = btj[0]
                    if bracket[2] > btj[1]:
                        bracket[2] = btj[1]
            # if verbose:
            #     logging.info('multivariate_discrete_gap_filling_minimizer: bracket=%s' % str(bracket))

            optresult = minimize_scalar(
                scalar_fun, bracket=bracket, tol=tol, method=scalar_discrete_gap_filling_minimizer,
                options=scalar_options)
            if verbose:
                logging.info('minimize_scalar returned t=%f, y=%f' % (optresult.x, optresult.fun))
            bestx = transform(optresult.x)
            besty = optresult.fun
            if verbose:
                logging.info(
                    'multivariate_gap_filling_minimizer: niter=%d, axis=%d, best f(%s) = %f'
                    % (niter, i, str(bestx), besty))
            funcalls += optresult.nfev
        if maxfev is not None and funcalls >= maxfev:
            break

    return OptimizeResult(fun=besty, x=bestx, nit=niter, nfev=funcalls, success=(niter > 1))


def simple_global_minimizer_spark(
        fun, x0, bounds, sc=None, verbose=True, **options):
    """Exhaustive global minimizer with same calling convention as `multivariate_discrete_gap_filling_minimizer`.

    Args:
        fun: Function of a single variable of a list-type.
        x0: Unused but kept for compatibility.
        bounds: List-type of (min, max) pairs for each element in x, defining the bounds in that dimension.
        sc (SparkContext)
    """
    axis_domains = [range(a, b+1) for a, b in bounds]
    domain_size = np.product([len(d) for d in axis_domains])
    if verbose:
        logging.info('simple_global_minimizer_spark: domain_size=%d' % domain_size)
    domain = itertools.product(*axis_domains)
    domain_rdd = sc.parallelize(domain)

    # Evaluate function at each point in parallel using Spark.
    fun_eval_rdd = domain_rdd.map(lambda x: (fun(x), x))

    # Find the minimum y value. Secondary sort on the x value for tie breaking.
    best_y, best_x = fun_eval_rdd.min(lambda yx: (yx[0][0], yx[1]) if isinstance(yx[0], tuple) else (yx[0], yx[1]))

    return OptimizeResult(fun=best_y, x=best_x, nfev=domain_size, success=True)

