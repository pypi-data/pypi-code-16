# -*- coding: utf-8 -*-

# Author: Hao Wang <wangronin@gmail.com>
#         Bas van Stein <bas9112@gmail.com>


from __future__ import print_function

import pdb
import numpy as np
from numpy import log, pi, log10

from scipy import linalg, optimize
from scipy.linalg import cho_solve
from scipy.optimize import fmin_l_bfgs_b
from scipy.special import kv, gamma

from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.metrics.pairwise import manhattan_distances
from sklearn.utils import check_random_state, check_array, check_X_y
from sklearn.utils.validation import check_is_fitted

import math
import warnings


"""
The built-in regression models submodule for the gaussian_process module.
"""



def constant(x):
    """
    Zero order polynomial (constant, p = 1) regression model.

    x --> f(x) = 1

    Parameters
    ----------
    x : array_like
        An array with shape (n_eval, n_features) giving the locations x at
        which the regression model should be evaluated.

    Returns
    -------
    f : array_like
        An array with shape (n_eval, p) with the values of the regression
        model.
    """
    x = np.asarray(x, dtype=np.float64)
    n_eval = x.shape[0]
    f = np.ones([n_eval, 1])
    return f


def linear(x):
    """
    First order polynomial (linear, p = n+1) regression model.

    x --> f(x) = [ 1, x_1, ..., x_n ].T

    Parameters
    ----------
    x : array_like
        An array with shape (n_eval, n_features) giving the locations x at
        which the regression model should be evaluated.

    Returns
    -------
    f : array_like
        An array with shape (n_eval, p) with the values of the regression
        model.
    """
    x = np.asarray(x, dtype=np.float64)
    n_eval = x.shape[0]
    f = np.hstack([np.ones([n_eval, 1]), x])
    return f


def quadratic(x):
    """
    Second order polynomial (quadratic, p = n*(n-1)/2+n+1) regression model.

    x --> f(x) = [ 1, { x_i, i = 1,...,n }, { x_i * x_j,  (i,j) = 1,...,n } ].T
                                                          i > j

    Parameters
    ----------
    x : array_like
        An array with shape (n_eval, n_features) giving the locations x at
        which the regression model should be evaluated.

    Returns
    -------
    f : array_like
        An array with shape (n_eval, p) with the values of the regression
        model.
    """

    x = np.asarray(x, dtype=np.float64)
    n_eval, n_features = x.shape
    f = np.hstack([np.ones([n_eval, 1]), x])
    for k in range(n_features):
        f = np.hstack([f, x[:, k, np.newaxis] * x[:, k:]])

    return f


"""
The built-in correlation models submodule for the gaussian_process module.
TODO: The grad of the correlation should be implemented in the correlation models
"""

def matern(theta, X, eval_Dx=False, eval_Dtheta=False,
           length_scale_bounds=(1e-5, 1e5), nu=1.5):
    """
    theta = np.asarray(theta, dtype=np.float64)
    d = np.asarray(d, dtype=np.float64)

    if d.ndim > 1:
        n_features = d.shape[1]
    else:
        n_features = 1

    if theta.size == 1:
        return np.exp(-theta[0] * np.sum(d ** 2, axis=1))
    elif theta.size != n_features:
        raise ValueError("Length of theta must be 1 or %s" % n_features)
    else:
        return np.exp(-np.sum(theta.reshape(1, n_features) * d ** 2, axis=1))

    """

    theta = np.asarray(theta, dtype=np.float64)
    X = np.asarray(X, dtype=np.float64)
    if X.ndim > 1:
        n_features = X.shape[1]
    else:
        n_features = 1
    
    if theta.size == 1:
        dists = np.sqrt(theta[0] * np.sum(X ** 2, axis=1))
    else:
        dists = np.sqrt(np.sum(theta.reshape(1, n_features) * X ** 2, axis=1))

    if nu == 0.5:
        K = np.exp(-dists)
    elif nu == 1.5:

        K = dists * math.sqrt(3)
        K = (1. + K) * np.exp(-K)
    elif nu == 2.5:
        K = dists * math.sqrt(5)
        K = (1. + K + K ** 2 / 3.0) * np.exp(-K)
    else:  # general case; expensive to evaluate
        K = dists
        K[K == 0.0] += np.finfo(float).eps  # strict zeros result in nan
        tmp = (math.sqrt(2 * nu) * K)
        K.fill((2 ** (1. - nu)) / gamma(nu))
        K *= tmp ** nu
        K *= kv(nu, tmp)
        
    
    if eval_Dx:
        pass

    # convert from upper-triangular matrix to square matrix
    #K = squareform(K)
    #np.fill_diagonal(K, 1)

    if eval_Dtheta:
        pass
#        # We need to recompute the pairwise dimension-wise distances
#        if self.anisotropic:
#            D = (X[:, np.newaxis, :] - X[np.newaxis, :, :])**2 \
#                / (length_scale ** 2)
#        else:
#            D = squareform(dists**2)[:, :, np.newaxis]
#
#        if self.nu == 0.5:
#            K_gradient = K[..., np.newaxis] * D \
#                / np.sqrt(D.sum(2))[:, :, np.newaxis]
#            K_gradient[~np.isfinite(K_gradient)] = 0
#        elif self.nu == 1.5:
#            K_gradient = \
#                3 * D * np.exp(-np.sqrt(3 * D.sum(-1)))[..., np.newaxis]
#        elif self.nu == 2.5:
#            tmp = np.sqrt(5 * D.sum(-1))[..., np.newaxis]
#            K_gradient = 5.0 / 3.0 * D * (tmp + 1) * np.exp(-tmp)
#        else:
#            # approximate gradient numerically
#            def f(theta):  # helper function
#                return self.clone_with_theta(theta)(X, Y)
#            return K, _approx_fprime(self.theta, f, 1e-10)
#
#        if not self.anisotropic:
#            return K, K_gradient[:, :].sum(-1)[:, :, np.newaxis]
#        else:
#            return K, K_gradient
    return K


def absolute_exponential(theta, d):
    """
    Absolute exponential autocorrelation model.
    (Ornstein-Uhlenbeck stochastic process)::

                                          n
        theta, d --> r(theta, d) = exp(  sum  - theta_i * |d_i| )
                                        i = 1

    Parameters
    ----------
    theta : array_like
        An array with shape 1 (isotropic) or n (anisotropic) giving the
        autocorrelation parameter(s).

    d : array_like
        An array with shape (n_eval, n_features) giving the componentwise
        distances between locations x and x' at which the correlation model
        should be evaluated.

    Returns
    -------
    r : array_like
        An array with shape (n_eval, ) containing the values of the
        autocorrelation model.
    """
    theta = np.asarray(theta, dtype=np.float64)
    d = np.abs(np.asarray(d, dtype=np.float64))

    if d.ndim > 1:
        n_features = d.shape[1]
    else:
        n_features = 1

    if theta.size == 1:
        return np.exp(- theta[0] * np.sum(d, axis=1))
    elif theta.size != n_features:
        raise ValueError("Length of theta must be 1 or %s" % n_features)
    else:
        return np.exp(- np.sum(theta.reshape(1, n_features) * d, axis=1))


def squared_exponential(theta, d):
    """
    Squared exponential correlation model (Radial Basis Function).
    (Infinitely differentiable stochastic process, very smooth)::

                                          n
        theta, d --> r(theta, d) = exp(  sum  - theta_i * (d_i)^2 )
                                        i = 1

    Parameters
    ----------
    theta : array_like
        An array with shape 1 (isotropic) or n (anisotropic) giving the
        autocorrelation parameter(s).

    d : array_like
        An array with shape (n_eval, n_features) giving the componentwise
        distances between locations x and x' at which the correlation model
        should be evaluated.

    Returns
    -------
    r : array_like
        An array with shape (n_eval, ) containing the values of the
        autocorrelation model.
    """

    theta = np.asarray(theta, dtype=np.float64)
    d = np.asarray(d, dtype=np.float64)

    if d.ndim > 1:
        n_features = d.shape[1]
    else:
        n_features = 1

    if theta.size == 1:
        return np.exp(-theta[0] * np.sum(d ** 2, axis=1))
    elif theta.size != n_features:
        raise ValueError("Length of theta must be 1 or %s" % n_features)
    else:
        return np.exp(-np.sum(theta.reshape(1, n_features) * d ** 2, axis=1))


def generalized_exponential(theta, d):
    """
    Generalized exponential correlation model.
    (Useful when one does not know the smoothness of the function to be
    predicted.)::

                                          n
        theta, d --> r(theta, d) = exp(  sum  - theta_i * |d_i|^p )
                                        i = 1

    Parameters
    ----------
    theta : array_like
        An array with shape 1+1 (isotropic) or n+1 (anisotropic) giving the
        autocorrelation parameter(s) (theta, p).

    d : array_like
        An array with shape (n_eval, n_features) giving the componentwise
        distances between locations x and x' at which the correlation model
        should be evaluated.

    Returns
    -------
    r : array_like
        An array with shape (n_eval, ) with the values of the autocorrelation
        model.
    """

    theta = np.asarray(theta, dtype=np.float64)
    d = np.asarray(d, dtype=np.float64)

    if d.ndim > 1:
        n_features = d.shape[1]
    else:
        n_features = 1

    lth = theta.size
    if n_features > 1 and lth == 2:
        theta = np.hstack([np.repeat(theta[0], n_features), theta[1]])
    elif lth != n_features + 1:
        raise Exception("Length of theta must be 2 or %s" % (n_features + 1))
    else:
        theta = theta.reshape(1, lth)

    td = theta[:, 0:-1].reshape(1, n_features) * np.abs(d) ** theta[:, -1]
    r = np.exp(- np.sum(td, 1))

    return r


def pure_nugget(theta, d):
    """
    Spatial independence correlation model (pure nugget).
    (Useful when one wants to solve an ordinary least squares problem!)::

                                           n
        theta, d --> r(theta, d) = 1 if   sum |d_i| == 0
                                         i = 1
                                   0 otherwise

    Parameters
    ----------
    theta : array_like
        None.

    d : array_like
        An array with shape (n_eval, n_features) giving the componentwise
        distances between locations x and x' at which the correlation model
        should be evaluated.

    Returns
    -------
    r : array_like
        An array with shape (n_eval, ) with the values of the autocorrelation
        model.
    """

    theta = np.asarray(theta, dtype=np.float64)
    d = np.asarray(d, dtype=np.float64)

    n_eval = d.shape[0]
    r = np.zeros(n_eval)
    r[np.all(d == 0., axis=1)] = 1.

    return r


def cubic(theta, d):
    """
    Cubic correlation model::

        theta, d --> r(theta, d) =
          n
         prod max(0, 1 - 3(theta_j*d_ij)^2 + 2(theta_j*d_ij)^3) ,  i = 1,...,m
        j = 1

    Parameters
    ----------
    theta : array_like
        An array with shape 1 (isotropic) or n (anisotropic) giving the
        autocorrelation parameter(s).

    d : array_like
        An array with shape (n_eval, n_features) giving the componentwise
        distances between locations x and x' at which the correlation model
        should be evaluated.

    Returns
    -------
    r : array_like
        An array with shape (n_eval, ) with the values of the autocorrelation
        model.
    """

    theta = np.asarray(theta, dtype=np.float64)
    d = np.asarray(d, dtype=np.float64)

    if d.ndim > 1:
        n_features = d.shape[1]
    else:
        n_features = 1

    lth = theta.size
    if lth == 1:
        td = np.abs(d) * theta
    elif lth != n_features:
        raise Exception("Length of theta must be 1 or " + str(n_features))
    else:
        td = np.abs(d) * theta.reshape(1, n_features)

    td[td > 1.] = 1.
    ss = 1. - td ** 2. * (3. - 2. * td)
    r = np.prod(ss, 1)

    return r



MACHINE_EPSILON = np.finfo(np.double).eps


def l1_cross_distances(X):
    """
    Computes the nonzero componentwise L1 cross-distances between the vectors
    in X.

    Parameters
    ----------

    X: array_like
        An array with shape (n_samples, n_features)

    Returns
    -------

    D: array with shape (n_samples * (n_samples - 1) / 2, n_features)
        The array of componentwise L1 cross-distances.

    ij: arrays with shape (n_samples * (n_samples - 1) / 2, 2)
        The indices i and j of the vectors in X associated to the cross-
        distances in D: D[k] = np.abs(X[ij[k, 0]] - Y[ij[k, 1]]).
    """
    X = check_array(X)
    n_samples, n_features = X.shape
    n_nonzero_cross_dist = n_samples * (n_samples - 1) // 2
    ij = np.zeros((n_nonzero_cross_dist, 2), dtype=np.int)
    D = np.zeros((n_nonzero_cross_dist, n_features))
    ll_1 = 0
    for k in range(n_samples - 1):
        ll_0 = ll_1
        ll_1 = ll_0 + n_samples - k - 1
        ij[ll_0:ll_1, 0] = k
        ij[ll_0:ll_1, 1] = np.arange(k + 1, n_samples)
        D[ll_0:ll_1] = np.abs(X[k] - X[(k + 1):n_samples])

    return D, ij


class GaussianProcess(BaseEstimator, RegressorMixin):
    """The Gaussian Process model class.

    Read more in the :ref:`User Guide <gaussian_process>`.

    Parameters
    ----------
    regr : string or callable, optional
        A regression function returning an array of outputs of the linear
        regression functional basis. The number of observations n_samples
        should be greater than the size p of this basis.
        Default assumes a simple constant regression trend.
        Available built-in regression models are::

            'constant', 'linear', 'quadratic'

    corr : string or callable, optional
        A stationary autocorrelation function returning the autocorrelation
        between two points x and x'.
        Default assumes a squared-exponential autocorrelation model.
        Built-in correlation models are::

            'absolute_exponential', 'squared_exponential',
            'generalized_exponential', 'cubic', 'linear', 'matern'

    beta0 : double array_like, optional
        The regression weight vector to perform Ordinary Kriging (OK).
        Default assumes Universal Kriging (UK) so that the vector beta of
        regression weights is estimated using the maximum likelihood
        principle.

    storage_mode : string, optional
        A string specifying whether the Cholesky decomposition of the
        correlation matrix should be stored in the class (storage_mode =
        'full') or not (storage_mode = 'light').
        Default assumes storage_mode = 'full', so that the
        Cholesky decomposition of the correlation matrix is stored.
        This might be a useful parameter when one is not interested in the
        MSE and only plan to estimate the BLUP, for which the correlation
        matrix is not required.

    verbose : boolean, optional
        A boolean specifying the verbose level.
        Default is verbose = False.

    theta0 : double array_like, optional
        An array with shape (n_features, ) or (1, ).
        The parameters in the autocorrelation model.
        If thetaL and thetaU are also specified, theta0 is considered as
        the starting point for the maximum likelihood estimation of the
        best set of parameters.
        Default assumes isotropic autocorrelation model with theta0 = 1e-1.

    thetaL : double array_like, optional
        An array with shape matching theta0's.
        Lower bound on the autocorrelation parameters for maximum
        likelihood estimation.
        Default is None, so that it skips maximum likelihood estimation and
        it uses theta0.

    thetaU : double array_like, optional
        An array with shape matching theta0's.
        Upper bound on the autocorrelation parameters for maximum
        likelihood estimation.
        Default is None, so that it skips maximum likelihood estimation and
        it uses theta0.

    normalize : boolean, optional
        Input X and observations y are centered and reduced wrt
        means and standard deviations estimated from the n_samples
        observations provided.
        Default is normalize = True so that data is normalized to ease
        maximum likelihood estimation.
    
    TODO: the nugget behaves differently than what is described here... 
    nugget : double or ndarray, optional
        Introduce a nugget effect to allow smooth predictions from noisy
        data.  If nugget is an ndarray, it must be the same length as the
        number of data points used for the fit.
        The nugget is added to the diagonal of the assumed training covariance;
        in this way it acts as a Tikhonov regularization in the problem.  In
        the special case of the squared exponential correlation function, the
        nugget mathematically represents the variance of the input values.
        Default assumes a nugget close to machine precision for the sake of
        robustness (nugget = 10. * MACHINE_EPSILON).

    optimizer : string, optional
        A string specifying the optimization algorithm to be used.
        Default uses 'fmin_cobyla' algorithm from scipy.optimize.
        Available optimizers are::

            'fmin_cobyla', 'Welch'

        'Welch' optimizer is dued to Welch et al., see reference [WBSWM1992]_.
        It consists in iterating over several one-dimensional optimizations
        instead of running one single multi-dimensional optimization.

    random_start : int, optional
        The number of times the Maximum Likelihood Estimation should be
        performed from a random starting point.
        The first MLE always uses the specified starting point (theta0),
        the next starting points are picked at random according to an
        exponential distribution (log-uniform on [thetaL, thetaU]).
        Default does not use random starting point (random_start = 1).

    random_state: integer or numpy.RandomState, optional
        The generator used to shuffle the sequence of coordinates of theta in
        the Welch optimizer. If an integer is given, it fixes the seed.
        Defaults to the global numpy random number generator.


    Attributes
    ----------
    theta_ : array
        Specified theta OR the best set of autocorrelation parameters (the \
        sought maximizer of the reduced likelihood function).

    reduced_likelihood_function_value_ : array
        The optimal reduced likelihood function value.

    Examples
    --------
    >>> import numpy as np
    >>> from sklearn.gaussian_process import GaussianProcess
    >>> X = np.array([[1., 3., 5., 6., 7., 8.]]).T
    >>> y = (X * np.sin(X)).ravel()
    >>> gp = GaussianProcess(theta0=0.1, thetaL=.001, thetaU=1.)
    >>> gp.fit(X, y)                                      # doctest: +ELLIPSIS
    GaussianProcess(beta0=None...
            ...

    Notes
    -----
    The presentation implementation is based on a translation of the DACE
    Matlab toolbox, see reference [NLNS2002]_.

    References
    ----------

    .. [NLNS2002] `H.B. Nielsen, S.N. Lophaven, H. B. Nielsen and J.
        Sondergaard.  DACE - A MATLAB Kriging Toolbox.` (2002)
        http://imedea.uib-csic.es/master/cambioglobal/Modulo_V_cod101615/Lab/lab_maps/krigging/DACE-krigingsoft/dace/dace.pdf

    .. [WBSWM1992] `W.J. Welch, R.J. Buck, J. Sacks, H.P. Wynn, T.J. Mitchell,
        and M.D.  Morris (1992). Screening, predicting, and computer
        experiments.  Technometrics, 34(1) 15--25.`
        http://www.jstor.org/stable/1269548
    """

    _regression_types = {
        'constant': constant,
        'linear': linear,
        'quadratic': quadratic}

    _correlation_types = {
        'absolute_exponential': absolute_exponential,
        'squared_exponential': squared_exponential,
        'generalized_exponential': generalized_exponential,
        'cubic': cubic,
        'matern': matern,
        'linear': linear}

    _optimizer_types = [
        'BFGS',
        'fmin_cobyla',
        'Welch']

    def __init__(self, regr='constant', corr='squared_exponential', beta0=None,
                 storage_mode='full', verbose=False, theta0=1e-1,
                 thetaL=None, thetaU=None, optimizer='fmin_cobyla',
                 random_start=1, normalize=False,
                 nugget=10. * MACHINE_EPSILON, random_state=None):

        self.regr = regr
        self.corr = corr
        self.beta0 = beta0
        self.storage_mode = storage_mode
        self.verbose = verbose
        self.theta0 = theta0
        self.thetaL = thetaL
        self.thetaU = thetaU
        self.normalize = normalize
        self.nugget = nugget
        self.optimizer = optimizer
        self.random_start = random_start
        self.random_state = random_state

    def fit(self, X, y):
        """
        The Gaussian Process model fitting method.

        Parameters
        ----------
        X : double array_like
            An array with shape (n_samples, n_features) with the input at which
            observations were made.

        y : double array_like
            An array with shape (n_samples, ) or shape (n_samples, n_targets)
            with the observations of the output to be predicted.

        Returns
        -------
        gp : self
            A fitted Gaussian Process model object awaiting data to perform
            predictions.
        """
        # Run input checks
        
        self._check_params()

        self.random_state = check_random_state(self.random_state)

        # Force data to 2D numpy.array
        X, y = check_X_y(X, y, multi_output=True, y_numeric=True)
        self.y_ndim_ = y.ndim
        if y.ndim == 1:
            y = y[:, np.newaxis]

        # Check shapes of DOE & observations
        n_samples, n_features = X.shape
        _, n_targets = y.shape

        # Run input checks
        self._check_params(n_samples)

        # Normalize data or don't
        if self.normalize:
            X_mean = np.mean(X, axis=0)
            X_std = np.std(X, axis=0)
            y_mean = np.mean(y, axis=0)
            y_std = np.std(y, axis=0)
            X_std[X_std == 0.] = 1.
            y_std[y_std == 0.] = 1.
            # center and scale X if necessary
            X = (X - X_mean) / X_std
            y = (y - y_mean) / y_std
        else:
            X_mean = np.zeros(1)
            X_std = np.ones(1)
            y_mean = np.zeros(1)
            y_std = np.ones(1)

        # Calculate matrix of distances D between samples
        D, ij = l1_cross_distances(X)
        if (np.min(np.sum(D, axis=1)) == 0.
                and self.corr != pure_nugget):
            raise Exception("Multiple input features cannot have the same"
                            " target value.")

        # Regression matrix and parameters
        F = self.regr(X)
        n_samples_F = F.shape[0]
        if F.ndim > 1:
            p = F.shape[1]
        else:
            p = 1
        if n_samples_F != n_samples:
            raise Exception("Number of rows in F and X do not match. Most "
                            "likely something is going wrong with the "
                            "regression model.")
        if p > n_samples_F:
            raise Exception(("Ordinary least squares problem is undetermined "
                             "n_samples=%d must be greater than the "
                             "regression model size p=%d.") % (n_samples, p))
        if self.beta0 is not None:
            if self.beta0.shape[0] != p:
                raise Exception("Shapes of beta0 and F do not match.")

        # Set attributes
        self.X = X
        self.y = y
        self.D = D
        self.ij = ij
        self.F = F
        self.X_mean, self.X_std = X_mean, X_std
        self.y_mean, self.y_std = y_mean, y_std

        # Determine Gaussian Process model parameters
        if self.thetaL is not None and self.thetaU is not None:
            # Maximum Likelihood Estimation of the parameters
            if self.verbose:
                print("Performing Maximum Likelihood Estimation of the "
                      "autocorrelation parameters...")
            self.theta_, self.reduced_likelihood_function_value_ = \
                self._arg_max_reduced_likelihood_function()
            if np.isinf(self.reduced_likelihood_function_value_):
                raise Exception("Bad parameter region. "
                                "Try increasing upper bound")
            
        else:
            # Given parameters
            if self.verbose:
                print("Given autocorrelation parameters. "
                      "Computing Gaussian Process model parameters...")
            self.theta_ = self.theta0
            self.reduced_likelihood_function_value_ = \
                self.reduced_likelihood_function()
            if np.isinf(self.reduced_likelihood_function_value_):
                raise Exception("Bad point. Try increasing theta0.")
        
        # compute for beta and gamma
        self.compute_aux_variables()

        if self.storage_mode == 'light':
            # Delete heavy data (it will be computed again if required)
            # (it is required only when MSE is wanted in self.predict)
            if self.verbose:
                print("Light storage mode specified. "
                      "Flushing autocorrelation matrix...")
            self.D = None
            self.ij = None
            self.F = None
            self.C = None
            self.Ft = None
            self.G = None

        return self

    def predict(self, X, eval_MSE=False, batch_size=None):
        """
        This function evaluates the Gaussian Process model at x.

        Parameters
        ----------
        X : array_like
            An array with shape (n_eval, n_features) giving the point(s) at
            which the prediction(s) should be made.

        eval_MSE : boolean, optional
            A boolean specifying whether the Mean Squared Error should be
            evaluated or not.
            Default assumes evalMSE = False and evaluates only the BLUP (mean
            prediction).

        batch_size : integer, optional
            An integer giving the maximum number of points that can be
            evaluated simultaneously (depending on the available memory).
            Default is None so that all given points are evaluated at the same
            time.

        Returns
        -------
        y : array_like, shape (n_samples, ) or (n_samples, n_targets)
            An array with shape (n_eval, ) if the Gaussian Process was trained
            on an array of shape (n_samples, ) or an array with shape
            (n_eval, n_targets) if the Gaussian Process was trained on an array
            of shape (n_samples, n_targets) with the Best Linear Unbiased
            Prediction at x.

        MSE : array_like, optional (if eval_MSE == True)
            An array with shape (n_eval, ) or (n_eval, n_targets) as with y,
            with the Mean Squared Error at x.
        """
        check_is_fitted(self, "X")

        # Check input shapes
        X = check_array(X)
        n_eval, _ = X.shape
        n_samples, n_features = self.X.shape
        n_samples_y, n_targets = self.y.shape

        # Run input checks
        self._check_params(n_samples)

        if X.shape[1] != n_features:
            raise ValueError(("The number of features in X (X.shape[1] = %d) "
                              "should match the number of features used "
                              "for fit() "
                              "which is %d.") % (X.shape[1], n_features))

        if batch_size is None:
            # No memory management
            # (evaluates all given points in a single batch run)

            # Normalize input
            X = (X - self.X_mean) / self.X_std

            # Initialize output
            y = np.zeros(n_eval)
            if eval_MSE:
                MSE = np.zeros(n_eval)

            # Get pairwise componentwise L1-distances to the input training set
            dx = manhattan_distances(X, Y=self.X, sum_over_features=False)
            # Get regression function and correlation
            f = self.regr(X)
            r = self.corr(self.theta_, dx).reshape(n_eval, n_samples)

            # Scaled predictor
            y_ = np.dot(f, self.beta) + np.dot(r, self.gamma)

            # Predictor
            y = (self.y_mean + self.y_std * y_).reshape(n_eval, n_targets)

            if self.y_ndim_ == 1:
                y = y.ravel()

            # Mean Squared Error
            if eval_MSE:
                C = self.C
                if C is None:
                    # Light storage mode (need to recompute C, F, Ft and G)
                    if self.verbose:
                        print("This GaussianProcess used 'light' storage mode "
                              "at instantiation. Need to recompute "
                              "autocorrelation matrix...")
                    reduced_likelihood_function_value, par = \
                        self.reduced_likelihood_function()
                    self.C = par['C']
                    self.Ft = par['Ft']
                    self.G = par['G']

                rt = linalg.solve_triangular(self.C, r.T, lower=True)

                if self.beta0 is None:
                    # Universal Kriging
                    u = linalg.solve_triangular(self.G.T,
                                                np.dot(self.Ft.T, rt) - f.T,
                                                lower=True)
                else:
                    # Ordinary Kriging
                    u = np.zeros((n_targets, n_eval))

                MSE = np.dot(self.sigma2.reshape(n_targets, 1),
                             (1. - (rt ** 2.).sum(axis=0)
                              + (u ** 2.).sum(axis=0))[np.newaxis, :])
                MSE = np.sqrt((MSE ** 2.).sum(axis=0) / n_targets)

                # Mean Squared Error might be slightly negative depending on
                # machine precision: force to zero!
                MSE[MSE < 0.] = 0.

                if self.y_ndim_ == 1:
                    MSE = MSE.ravel()

                return y, MSE

            else:

                return y

        else:
            # Memory management

            if type(batch_size) is not int or batch_size <= 0:
                raise Exception("batch_size must be a positive integer")

            if eval_MSE:

                y, MSE = np.zeros(n_eval), np.zeros(n_eval)
                for k in range(max(1, n_eval / batch_size)):
                    batch_from = k * batch_size
                    batch_to = min([(k + 1) * batch_size + 1, n_eval + 1])
                    y[batch_from:batch_to], MSE[batch_from:batch_to] = \
                        self.predict(X[batch_from:batch_to],
                                     eval_MSE=eval_MSE, batch_size=None)

                return y, MSE

            else:

                y = np.zeros(n_eval)
                for k in range(max(1, n_eval / batch_size)):
                    batch_from = k * batch_size
                    batch_to = min([(k + 1) * batch_size + 1, n_eval + 1])
                    y[batch_from:batch_to] = \
                        self.predict(X[batch_from:batch_to],
                                     eval_MSE=eval_MSE, batch_size=None)

                return y
                
                
    def corr_grad_theta(self, theta, X, R, nu=1.5):
        # Check input shapes                                                          
        X = np.atleast_2d(X)                                                            
        n_eval, _ = X.shape                                                           
        n_features = self.X.shape[1]
        
        if _ != n_features:
            raise Exception('x does not have the right size!')
        
        diff = (X[:, np.newaxis, :] - X[np.newaxis, :, :]) ** 2.
        
        if self.corr_type == 'squared_exponential':
            grad = -diff * R[..., np.newaxis] 
            
        elif self.corr_type == 'matern':
            c = np.sqrt(3)
            D = np.sqrt(np.sum(theta * diff, axis=-1))
            
            if nu == 0.5:
                grad = - diff * theta / D * R
            elif nu == 1.5:
                grad = -3 * np.exp(-c * D)[..., np.newaxis] * diff / 2.
            elif nu == 2.5:
                pass

        elif self.corr_type == 'absolute_exponential':
            pass
        elif self.corr_type == 'generalized_exponential':
            pass
        elif self.corr_type == 'cubic':
            pass
        elif self.corr_type == 'linear':
            pass
        
        return grad
        
    def compute(self):
        pass

    def reduced_likelihood_function(self, theta=None, sigma2=None, eval_grad=False):
#        (par)
        # TODO: change name, this is Log-likelihood function instead of 'reduced'...
        """
        This function determines the BLUP parameters and evaluates the reduced
        likelihood function for the given autocorrelation parameters theta.

        Maximizing this function wrt the autocorrelation parameters theta is
        equivalent to maximizing the likelihood of the assumed joint Gaussian
        distribution of the observations y evaluated onto the design of
        experiments X.

        Parameters
        ----------
        theta : array_like, optional
            An array containing the autocorrelation parameters at which the
            Gaussian Process model parameters should be determined.
            Default uses the built-in autocorrelation parameters
            (ie ``theta = self.theta_``).

        Returns
        -------
        reduced_likelihood_function_value : double
            The value of the reduced likelihood function associated to the
            given autocorrelation parameters theta.

        par : dict
            A dictionary containing the requested Gaussian Process model
            parameters:

                sigma2
                        Gaussian Process variance.
                beta
                        Generalized least-squares regression weights for
                        Universal Kriging or given beta0 for Ordinary
                        Kriging.
                gamma
                        Gaussian Process weights.
                C
                        Cholesky decomposition of the correlation matrix [R].
                Ft
                        Solution of the linear equation system : [R] x Ft = F
                G
                        QR decomposition of the matrix Ft.
        """
        check_is_fitted(self, "X")

        if theta is None:
            # Use built-in autocorrelation parameters
            theta = self.theta_

        # Initialize output
        LL = -np.inf
        
        # Retrieve data
        n_samples, n_features = self.X.shape
        D = self.D
        ij = self.ij
        F = self.F

        if D is None:
            # Light storage mode (need to recompute D, ij and F)
            D, ij = l1_cross_distances(self.X)
            if (np.min(np.sum(D, axis=1)) == 0.
                    and self.corr != pure_nugget):
                raise Exception("Multiple X are not allowed")
            F = self.regr(self.X)

        # Set up R
        r = self.corr(theta, D)
        R = np.eye(n_samples) * (1. + self.nugget)
        R[ij[:, 0], ij[:, 1]] = r
        R[ij[:, 1], ij[:, 0]] = r
        R0 = R - np.eye(n_samples) * self.nugget
        
        # Cholesky decomposition of R: Note that this matrix R can be singular
        try:
            C = linalg.cholesky(R, lower=True)
        except linalg.LinAlgError:
            return (-np.inf, np.zeros_like(theta)) \
                if eval_grad else -np.inf
        
        # Get generalized least squares solution
        Ft = linalg.solve_triangular(C, F, lower=True)
        Yt = linalg.solve_triangular(C, self.y, lower=True)
        
        # compute rho
        Q, G = linalg.qr(Ft, mode='economic')
        rho = Yt - np.dot(Q.dot(Q.T), Yt)
        
        # compute the MLE of sigma2
        sigma2 = (rho ** 2.).sum(axis=0) / n_samples
        
#        sv = linalg.svd(G, compute_uv=False)
#        rcondG = sv[-1] / sv[0]
#        if rcondG < 1e-10:
#            # Check F
#            sv = linalg.svd(F, compute_uv=False)
#            condF = sv[0] / sv[-1]
#            if condF > 1e15:
#                raise Exception("F is too ill conditioned. Poor combination "
#                                "of regression model and observations.")
#            else:
#                # Ft is too ill conditioned, get out (try different theta)
#                return reduced_likelihood_function_value, par

        
#        if self.beta0 is None:
#            # Universal Kriging
#            beta = linalg.solve_triangular(G, np.dot(Q.T, Yt))
#        else:
#            # Ordinary Kriging
#            beta = np.array(self.beta0)

#        rho = Yt - np.dot(Ft, beta)  #  variable z in DiceKriging
        
        # The determinant of R is equal to the squared product of the diagonal
        # elements of its Cholesky decomposition C
        
#        detR_ = detR ** (1. / n_samples)
        
        # Compute/Organize output
        # Log-likelihood function
        LL = -0.5 * (n_samples * log(2.*pi*sigma2) \
            + 2 * np.log(np.diag(C)).sum() + n_samples)
        
            
        self.sigma2 = sigma2 * self.y_std ** 2.
        self.rho = rho
        self.Yt = Yt
        self.C = C
        self.Ft = Ft
        self.G = G
        self.Q = Q
        
        if np.exp(LL) > 1:
            return (-np.inf, np.zeros_like(theta)) \
                if eval_grad else -np.inf
        
        if eval_grad:
            
            gamma = linalg.solve_triangular(C.T, rho).reshape(-1, 1)
            
            # The grad tensor of R w.r.t. theta
            R_grad_tensor = self.corr_grad_theta(theta, self.X, R0)
            
            Rinv = cho_solve((C, True), np.eye(n_samples))
            Rinv_upper = Rinv[np.triu_indices(n_samples, 1)]
            _upper = gamma.dot(gamma.T)[np.triu_indices(n_samples, 1)]
            
            LL_grad = np.zeros(n_features)
            
            for i in range(n_features): 
                R_grad_upper = R_grad_tensor[:, :, i][np.triu_indices(n_samples, 1)]
                LL_grad[i] = np.sum(_upper * R_grad_upper) / self.sigma2  \
                    - np.sum(Rinv_upper * R_grad_upper)
            LL_grad = LL_grad.reshape(-1, 1)
            
            return LL, LL_grad

        return LL
        
    def compute_aux_variables(self):
        if self.beta0 is None:
            # Universal Kriging
            self.beta = linalg.solve_triangular(self.G, np.dot(self.Q.T, self.Yt))
        else:
            # Ordinary Kriging
            self.beta = np.array(self.beta0)
        self.gamma = linalg.solve_triangular(self.C.T, self.rho).reshape(-1, 1)
        

    def _arg_max_reduced_likelihood_function(self):
        """
        This function estimates the autocorrelation parameters theta as the
        maximizer of the reduced likelihood function.
        (Minimization of the opposite reduced likelihood function is used for
        convenience)

        Parameters
        ----------
        self : All parameters are stored in the Gaussian Process model object.

        Returns
        -------
        optimal_theta : array_like
            The best set of autocorrelation parameters (the sought maximizer of
            the reduced likelihood function).

        optimal_reduced_likelihood_function_value : double
            The optimal reduced likelihood function value.

        optimal_par : dict
            The BLUP parameters associated to thetaOpt.
        """
        
        import numpy as np
        import pdb
        # Initialize output
        best_optimal_theta = []
        best_optimal_rlf_value = []
        
        if self.verbose:
            print("The chosen optimizer is: " + str(self.optimizer))
            if self.random_start > 1:
                print(str(self.random_start) + " random starts are required.")

        percent_completed = 0.

        # Force optimizer to fmin_cobyla if the model is meant to be isotropic
        if self.optimizer == 'Welch' and self.theta0.size == 1:
            self.optimizer = 'fmin_cobyla'

        if self.optimizer == 'fmin_cobyla':
#        if 1 < 2:
            def minus_reduced_likelihood_function(log10t):
                
                return - self.reduced_likelihood_function(
                    theta=10. ** log10t, eval_grad=False)
                    
            constraints = []
            for i in range(self.theta0.size):
                constraints.append(lambda log10t, i=i:
                                   log10t[i] - np.log10(self.thetaL[0, i]))
                constraints.append(lambda log10t, i=i:
                                   np.log10(self.thetaU[0, i]) - log10t[i])
                                   
            for k in range(self.random_start):

                if k == 0:
                    # Use specified starting point as first guess
                    theta0 = self.theta0
                else:
                    # Generate a random starting point log10-uniformly
                    # distributed between bounds
                    log10theta0 = (np.log10(self.thetaL)
                                   + self.random_state.rand(*self.theta0.shape)
                                   * np.log10(self.thetaU / self.thetaL))
                    theta0 = 10. ** log10theta0

                # Run Cobyla
                try:
                    _ = np.log10(theta0).ravel()
                    log10_optimal_theta = \
                        optimize.fmin_cobyla(minus_reduced_likelihood_function,
                                             _, constraints,
                                             iprint=0)
                except ValueError as ve:
                    print("Optimization failed. Try increasing the ``nugget``")
                    raise ve

                optimal_theta = 10. ** log10_optimal_theta
                optimal_rlf_value = \
                    self.reduced_likelihood_function(theta=optimal_theta)

                # Compare the new optimizer to the best previous one
                if k > 0:
                    if optimal_rlf_value > best_optimal_rlf_value:
                        best_optimal_rlf_value = optimal_rlf_value
                        best_optimal_theta = optimal_theta
                else:
                    best_optimal_rlf_value = optimal_rlf_value
                    best_optimal_theta = optimal_theta
                if self.verbose and self.random_start > 1:
                    if (20 * k) / self.random_start > percent_completed:
                        percent_completed = (20 * k) / self.random_start
                        print("%s completed" % (5 * percent_completed))

            optimal_rlf_value = best_optimal_rlf_value
            optimal_theta = best_optimal_theta

        elif self.optimizer == 'Welch':

            # Backup of the given attributes
            theta0, thetaL, thetaU = self.theta0, self.thetaL, self.thetaU
            corr = self.corr
            verbose = self.verbose

            # This will iterate over fmin_cobyla optimizer
            self.optimizer = 'fmin_cobyla'
            self.verbose = False

            # Initialize under isotropy assumption
            if verbose:
                print("Initialize under isotropy assumption...")
            self.theta0 = check_array(self.theta0.min())
            self.thetaL = check_array(self.thetaL.min())
            self.thetaU = check_array(self.thetaU.max())
            theta_iso, optimal_rlf_value_iso, par_iso = \
                self._arg_max_reduced_likelihood_function()
            optimal_theta = theta_iso + np.zeros(theta0.shape)

            # Iterate over all dimensions of theta allowing for anisotropy
            if verbose:
                print("Now improving allowing for anisotropy...")
            for i in self.random_state.permutation(theta0.size):
                if verbose:
                    print("Proceeding along dimension %d..." % (i + 1))
                self.theta0 = check_array(theta_iso)
                self.thetaL = check_array(thetaL[0, i])
                self.thetaU = check_array(thetaU[0, i])

                def corr_cut(t, d):
                    return corr(check_array(np.hstack([optimal_theta[0][0:i],
                                                       t[0],
                                                       optimal_theta[0][(i +
                                                                         1)::]])),
                                d)

                self.corr = corr_cut
                optimal_theta[0, i], optimal_rlf_value, optimal_par = \
                    self._arg_max_reduced_likelihood_function()

            # Restore the given attributes
            self.theta0, self.thetaL, self.thetaU = theta0, thetaL, thetaU
            self.corr = corr
            self.optimizer = 'Welch'
            self.verbose = verbose
        
        elif self.optimizer == 'BFGS':
            def obj_func(theta):
                try:
                    theta = np.array(theta)
                    __ = self.reduced_likelihood_function(theta, eval_grad=True)
                    return -__[0], -__[1]
                except:
                    pdb.set_trace()
            
            dim = self.thetaL.shape[1]
            LL_opt = np.inf
            eval_budget = 100*dim
            n_restarts_optimizer = 10
            thetaL = np.atleast_2d(self.thetaL)
            thetaU = np.atleast_2d(self.thetaU)
            bounds = np.c_[thetaL.T, thetaU.T]
            
            if not np.isfinite(bounds).all() and n_restarts_optimizer > 1:
                raise ValueError(
                        "Multiple optimizer restarts (n_restarts_optimizer>0) "
                        "requires that all bounds are finite.")
            
            # L-BFGS-B algorithm with restarts
            for iteration in range(n_restarts_optimizer):
                
                x0 = np.random.uniform(bounds[:, 0], bounds[:, 1])
                
                theta_opt_, LL_opt_, convergence_dict = \
                    fmin_l_bfgs_b(obj_func, x0, pgtol=1e-8, factr=1e7,
                                  bounds=bounds, maxfun=eval_budget)
                
                if convergence_dict["warnflag"] != 0 and self.verbose:
                    warnings.warn("fmin_l_bfgs_b terminated abnormally with the "
                          " state: %s" % convergence_dict)
                          
                if LL_opt_ < LL_opt:
                    if self.verbose:
                        print('iteration: ', iteration+1, convergence_dict['funcalls'])
                        
                    theta_opt, LL_opt = theta_opt_, LL_opt_
                eval_budget -= convergence_dict['funcalls']
                
                if eval_budget <= 0:
                    break
                
            optimal_theta = theta_opt
            optimal_rlf_value = optimal_rlf_value = \
                    self.reduced_likelihood_function(theta=optimal_theta)
            
        else:

            raise NotImplementedError("This optimizer ('%s') is not "
                                      "implemented yet. Please contribute!"
                                      % self.optimizer)
                                      
        
        
        # diagostic plots of gradient field 
        def plot_contour_gradient(ax, f, grad, x_lb, x_ub, title='f', 
                                  f_data=None, grad_data=None,n_per_axis=200):
            import pdb
            import matplotlib.pyplot as plt
            import matplotlib.colors as colors
            import numpy as np
            from matplotlib import cm
            from mpl_toolkits.mplot3d import axes3d
            
            fig = ax.figure
            x_lb = x_lb.flatten()
            x_ub = x_ub.flatten()
            def seq(a0, aN, N):
                s = (aN / a0) ** (1.0 / (N-1))
                return np.array([a0 * s ** i for i in np.arange(0, N)])
                
            x = seq(x_lb[0], x_ub[0], n_per_axis)
            y = seq(x_lb[1], x_ub[1], n_per_axis)
            X, Y = np.meshgrid(x, y)
            
            fitness = np.array([f(p) for p in np.c_[X.flatten(), Y.flatten()]]).reshape(-1, len(x))
                
            CS = ax.contour(X, Y, fitness, 80, cmap=plt.cm.cool, linewidths=1)
            plt.clabel(CS, inline=1, fontsize=7)
            fig.colorbar(CS)
            
            # calculate function gradients   
            x1 = seq(x_lb[0], x_ub[0], n_per_axis/10)
            x2 = seq(x_lb[1], x_ub[1], n_per_axis/10)
            X1, X2 = np.meshgrid(x1, x2)     
           
            ax.set_xlabel('$x_1$')
            ax.set_ylabel('$x_2$')
            ax.grid(True)
            ax.set_title(title, y=1.05)
            ax.set_xlim(x_lb[0], x_ub[0])
            ax.set_ylim(x_lb[1], x_ub[1])
        
        fig_width = 22
        fig_height = fig_width * 9 / 16
        
#        fitness = lambda x: self.reduced_likelihood_function(x)[0]
#        grad = lambda x: self.reduced_likelihood_function(x, eval_grad=True)[1]
#        
#        fig = plt.figure(figsize=(fig_width, fig_height))
#        ax0 = fig.add_subplot(111)
#        plot_contour_gradient(ax0, fitness, grad, thetaL, thetaU, title='LL', 
#                              n_per_axis=50)
#                              
#        
#        ax0.set_xscale('log')
#        ax0.set_yscale('log')
        
#        ax0.plot(theta_opt[0], theta_opt[1], 'r*', ms=15, mfc='none') 
#        ax0.plot(optimal_theta[0], optimal_theta[1], 'ks', ms=15, mfc='none')
        
#        plt.show()
        
#        pdb.set_trace()
        print(optimal_theta, optimal_rlf_value)
        return optimal_theta, optimal_rlf_value
        

    def _check_params(self, n_samples=None):

        # Check regression model
        if not callable(self.regr):
            if self.regr in self._regression_types:
                self.regr = self._regression_types[self.regr]
            else:
                raise ValueError("regr should be one of %s or callable, "
                                 "%s was given."
                                 % (self._regression_types.keys(), self.regr))

        # Check regression weights if given (Ordinary Kriging)
        if self.beta0 is not None:
            self.beta0 = np.atleast_2d(self.beta0)
            if self.beta0.shape[1] != 1:
                # Force to column vector
                self.beta0 = self.beta0.T

        # Check correlation model
        if not callable(self.corr):
            if self.corr in self._correlation_types:
                self.corr = self._correlation_types[self.corr]
            else:
                raise ValueError("corr should be one of %s or callable, "
                                 "%s was given."
                                 % (self._correlation_types.keys(), self.corr))

        # Check storage mode
        if self.storage_mode != 'full' and self.storage_mode != 'light':
            raise ValueError("Storage mode should either be 'full' or "
                             "'light', %s was given." % self.storage_mode)

        # Check correlation parameters
        self.theta0 = np.atleast_2d(self.theta0)
        lth = self.theta0.size

        if self.thetaL is not None and self.thetaU is not None:
            self.thetaL = np.atleast_2d(self.thetaL)
            self.thetaU = np.atleast_2d(self.thetaU)
            if self.thetaL.size != lth or self.thetaU.size != lth:
                raise ValueError("theta0, thetaL and thetaU must have the "
                                 "same length.")
            if np.any(self.thetaL <= 0) or np.any(self.thetaU < self.thetaL):
                raise ValueError("The bounds must satisfy O < thetaL <= "
                                 "thetaU.")

        elif self.thetaL is None and self.thetaU is None:
            if np.any(self.theta0 <= 0):
                raise ValueError("theta0 must be strictly positive.")

        elif self.thetaL is None or self.thetaU is None:
            raise ValueError("thetaL and thetaU should either be both or "
                             "neither specified.")

        # Force verbose type to bool
        self.verbose = bool(self.verbose)

        # Force normalize type to bool
        self.normalize = bool(self.normalize)

        # Check nugget value
        self.nugget = np.asarray(self.nugget)
        if np.any(self.nugget) < 0.:
            raise ValueError("nugget must be positive or zero.")
        if (n_samples is not None
                and self.nugget.shape not in [(), (n_samples,)]):
            raise ValueError("nugget must be either a scalar "
                             "or array of length n_samples.")

        # Check optimizer
        if self.optimizer not in self._optimizer_types:
            raise ValueError("optimizer should be one of %s"
                             % self._optimizer_types)

        # Force random_start type to int
        self.random_start = int(self.random_start)