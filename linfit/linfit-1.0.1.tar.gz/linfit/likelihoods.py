import numpy as np
from scipy.special import erf

#--> The lnlikes
#-> The lnlike calculated with generalized chi square
#The generalized chi-square function
def ChiSq(data, model, unct=None, flag=None, nsigma=3):
    '''
    This is a generalized chi-square function that allows y to be upperlimits. The
    upper limits are properly deal with using the method mentioned by Sawicki (2012).

    Parameters
    ----------
    data : float array
        The observed data and upperlimits.
    model : float array
        The model.
    unct : float array or Nobe by default
        The uncertainties.
    flag : float array or None by default
        The flag of upperlimits, 0 for detection and 1 for upperlimits.
    nsigma : float; default: 3
        The provided upperlimits are nsigma times of the uncertainties.

    Returns
    -------
    chsq : float
        The Chi square

    Notes
    -----
    This chi-square form consider the x and y asymmetrically except for some special
    situations.
    '''
    if unct is None:
        unct = np.ones_like(data)
    if flag is None:
        flag = np.zeros_like(data)
    fltr_dtc = flag == 0
    fltr_non = flag == 1
    if np.sum(fltr_dtc)>0:
        wrsd_dtc = (data[fltr_dtc] - model[fltr_dtc])/unct[fltr_dtc] #The weighted residual
        chsq_dtc = np.sum(wrsd_dtc**2) + np.sum( np.log(2 * np.pi * unct[fltr_dtc]**2.0) )
    else:
        chsq_dtc = 0.
    if np.sum(fltr_non)>0:
        unct_non = data[fltr_non]/nsigma #The nondetections are 3 sigma upper limits.
        wrsd_non = (data[fltr_non] - model[fltr_non])/(unct_non * 2**0.5)
        chsq_non = np.sum( -2.* np.log( 0.5 * (1 + erf(wrsd_non)) ) )
    else:
        chsq_non = 0.
    chsq = chsq_dtc + chsq_non
    return chsq

def lnlike_gcs(theta, x, y, xerr, yerr, *args, **kwargs):
    """
    The ln of likelihood function use the generalized chi-square function. The y
    of the data could be upperlimits.

    Parameters
    ----------
    theta : list
        The list of the model parameters, [m, b, lnf (optional)].
    x : float array
        The data of x.
    y : float array
        The data of y.
    xerr : float array
        The uncertainty of the x data.
    yerr : float array
        The uncertainty of the y data.
    args and kwargs : for the ChiSq function.

    Returns
    -------
    The ln likelihood.

    Notes
    -----
    None.
    """
    if len(theta) == 2:
        m, b = theta
        model = m * x + b
        s = np.sqrt(yerr**2 + (m*xerr)**2)
    if len(theta) == 3:
        m, b, lnf = theta
        model = m * x + b
        s = np.sqrt(yerr**2 + (m*xerr)**2 + model**2*np.exp(2*lnf))
    lnL = -0.5 * ChiSq(y, model, s, *args, **kwargs)
    return lnL

#-> The Nukers' lnlike
def lnlike_Nukers(theta, x, y, epsx, epsy):
    """
    This is the ln likelihood function resembling the Nukers' estimate from
    Tremaine et al. (2002). One of the merits of this form is that the x and y
    are symmetric (see the paper for the details). The symbols of the parameters
    also follow the paper.

    Parameters
    ----------
    theta : list
        The list of model parameters, [beta, alpha, epsy0 (optional)].
        beta is the slope, alpha is the intercept and epsy0 is the intrinsic
        scatter along the y direction.
    x : float array
        The x data.
    y : float array
        The y data.
    epsx : float array
        The uncertainty of x data.
    epsy : float array
        The uncertainty of y data.

    Returns
    -------
    lnL : float
        The ln of the likelihood.

    Notes
    -----
    The lnlike penalizes the very broad intrinsic dispersion assuming it is a
    Gaussian distribution. Therefore, the optimization is to seek the maximum of
    the lnlike instead of the Nukers' estimate ~1.
    """
    if len(theta) == 2:
        beta, alpha = theta
        inv_sigma2 = 1.0/(epsy**2 + (beta * epsx)**2)
    if len(theta) == 3:
        beta, alpha, epsy0 = theta
        inv_sigma2 = 1.0/(epsy**2 + epsy0**2 + (beta * epsx)**2)
    lnL = -0.5*(np.sum((y - alpha - beta * x)**2*inv_sigma2 - np.log(inv_sigma2)))
    return lnL

#-> The lnlike calculated from the distance perpendicular to the line following
#Hogg et al. (2010; arXiv:1008.4686)
def lnlike_perp(theta, x, y, sigx, sigy):
    """
    This is the ln likelihood function considering the 2-dimensional uncertainties
    and calculated based on the distance of the points perpendicular to the line.
    It follows the equation (35) of Hogg et al. (2010; arXiv:1008.4686).

    Parameters
    ----------
    theta : list
        The list of model parameters, [t, bv, V (optional)]. t (in radian) is
        the angle (theta = arctan slope), bv is the perpendicular distance of
        the line from the origin and V is intrinsic Gaussian variance orthogonal
        to the line.
    x : float array
        The x data.
    y : float array
        The y data.
    sigx : float array
        The uncertainty of x data.
    sigy : float array
        The uncertainty of y data.

    Returns
    -------
    lnL : float
        The ln likelihood.

    Notes
    -----
    None.
    """
    if len(theta) == 2:
        t, bv = theta
        V = 0
    if len(theta) == 3:
        t, bv, V = theta
    delta = y * np.cos(t) - x * np.sin(t) - bv
    Sigma2 = (sigx * np.sin(t))**2 + (sigy * np.cos(t))**2
    lnL = -0.5 * np.sum(delta**2 / (Sigma2 + V) + np.log(Sigma2 + V))
    return lnL

def lnlike_perp2(theta, x, y, sigx, sigy):
    """
    This is the ln likelihood function considering the 2-dimensional uncertainties
    and calculated based on the distance of the points perpendicular to the line.
    It follows the equation (35) of Hogg et al. (2010; arXiv:1008.4686).

    Parameters
    ----------
    theta : list
        The list of model parameters, [t, b, V (optional)]. t (in radian) is
        the angle (theta = arctan slope), b is the intercept and V is intrinsic
        Gaussian variance orthogonal
        to the line.
    x : float array
        The x data.
    y : float array
        The y data.
    sigx : float array
        The uncertainty of x data.
    sigy : float array
        The uncertainty of y data.

    Returns
    -------
    lnL : float
        The ln likelihood.

    Notes
    -----
    None.
    """
    if len(theta) == 2:
        t, b = theta
        V = 0
    if len(theta) == 3:
        t, b, V = theta
    delta = (y - b) * np.cos(t) - x * np.sin(t)
    Sigma2 = (sigx * np.sin(t))**2 + (sigy * np.cos(t))**2
    lnL = -0.5 * np.sum(delta**2 / (Sigma2 + V) + np.log(Sigma2 + V))
    return lnL

#-> The lnlike that considers the model imperfectness naively as a fraction of
#the model values.
def lnlike_naive(theta, x, y, xerr, yerr):
    """
    The ln of likelihood function using all detected data.

    Parameters
    ----------
    theta : list
        The list of the model parameters, [m, b, lnf (optional)].
    x : float array
        The data of x.
    y : float array
        The data of y.
    xerr : float array
        The uncertainty of the x data.
    yerr : float array
        The uncertainty of the y data.

    Returns
    -------
    The ln likelihood.

    Notes
    -----
    None.
    """
    if len(theta) == 2:
        m, b = theta
        model = m * x + b
        inv_sigma2 = 1.0/(yerr**2 + (m*xerr)**2)
        return -0.5*(np.sum((y-model)**2*inv_sigma2 - np.log(inv_sigma2)))
    if len(theta) == 3:
        m, b, lnf = theta
        model = m * x + b
        inv_sigma2 = 1.0/(yerr**2 + (m*xerr)**2 + model**2*np.exp(2*lnf))
        return -0.5*(np.sum((y-model)**2*inv_sigma2 - np.log(inv_sigma2)))
    else:
        raise ValueError("[linfit]: The length of parameters ({0}) is incorrect!".format(len(theta)))

def lnprior(theta, pRanges):
    """
    The ln of prior function.

    Parameters
    ----------
    theta : list
        The list of the model parameters, [m, b, lnf (optional)].
    pRanges : list
        The list of the parameter prior ranges.

    Returns
    -------
    The ln prior.

    Notes
    -----
    None.
    """
    assert len(theta) == len(pRanges)
    if len(theta) == 2:
        m, b = theta
        mR, bR = pRanges
        if mR[0] < m < mR[1] and bR[0] < b < bR[1]:
            return 0.0
        return -np.inf
    if len(theta) == 3:
        m, b, lnf = theta
        mR, bR, lnfR = pRanges
        if mR[0] < m < mR[1] and bR[0] < b < bR[1] and lnfR[0] < lnf < lnfR[1]:
            return 0.0
        return -np.inf
    else:
        raise ValueError("[linfit]: The length of parameters ({0}) is incorrect!".format(len(theta)))

def lnprob(theta, x, y, xerr, yerr, pRanges, *args, **kwargs):
    """
    The ln of probability function.

    Parameters
    ----------
    theta : list
        The list of the model parameters, [m, b, lnf (optional)].
    x : float array
        The data of x.
    y : float array
        The data of y.
    xerr : float array
        The uncertainty of the x data.
    yerr : float array
        The uncertainty of the y data.
    pRanges : list
        The list of the parameter prior ranges.
    args and kwargs : for the ChiSq function.

    Returns
    -------
    The ln probability.

    Notes
    -----
    None.
    """
    lp = lnprior(theta, pRanges)
    if not np.isfinite(lp):
        return -np.inf
    return lp + lnlike(theta, x, y, xerr, yerr, *args, **kwargs)
