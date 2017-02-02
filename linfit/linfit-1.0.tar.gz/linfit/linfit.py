import emcee
import corner
import numpy as np
from scipy.special import erf
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

def MockData(m, b, lnf=None, x=None, ndata=None, xep=[0.0, 0.0], yep=[0.0, 0.0]):
    """
    Generate the mock data.

    Parameters
    ----------
    m : float
        The slope.
    b : float
        The intercept.
    lnf : float, optional
        The intrinsic scatter. The default is None.
    x : float array, optional
        The x of the data. The default is None.
    ndata : float, optional
        If x is not provided, ndata should be given to provide the number of the
        data randomly generated. The default is None.
    xep : list
        The lower and upper boundaries of the x error. The uncertainties are assumed
        to be Gaussian. The default is [0.0, 0.0].
    yep : list
        The lower and upper boundaries of the y error. The uncertainties are assumed
        to be Gaussian. The default is [0.0, 0.0].
    """
    if x is None:
        assert not ndata is None
        x = np.sort(10*np.random.rand(ndata))
    else:
        if (not ndata is None) & (ndata != len(x)):
            raise Warning("[linfit]: The input ndata ({0}) is not used.".format(ndata))
        ndata = len(x)
    if lnf is None:
        f = 0
    else:
        f = np.exp(lnf)
    xerr = xep[0] + (xep[1] - xep[0]) * np.random.rand(ndata)
    yerr = yep[0] + (yep[1] - yep[0]) * np.random.rand(ndata)
    x += xerr * np.random.randn(ndata)
    y = m * x + b
    y += np.abs(f * y) * np.random.randn(ndata)
    y += yerr * np.random.randn(ndata)
    retDict = {
        "x": x,
        "y": y,
        "xerr": xerr,
        "yerr": yerr
    }
    return retDict

def ChiSq(data, model, unct=None, flag=None, nsigma=3):
    '''
    This function calculate the Chi square of the observed data and
    the model. The upper limits are properly deal with using the method
    mentioned by Sawicki (2012).

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
    None.
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

def lnlike(theta, x, y, err, *args, **kwargs):
    """
    The ln of likelihood function for the general data. The y of the data could
    be upperlimits.

    Parameters
    ----------
    theta : list
        The list of the model parameters, [m, b, lnf (optional)].
    x : float array
        The data of x.
    y : float array
        The data of y.
    err : float array
        The uncertainty of the data.
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
        s = err
    if len(theta) == 3:
        m, b, lnf = theta
        model = m * x + b
        s = (err**2 + model**2*np.exp(2*lnf))**0.5
    lnL = -0.5 * ChiSq(y, model, s, *args, **kwargs)
    return lnL

def lnlike_simple(theta, x, y, err):
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
    err : float array
        The uncertainty of the data.

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
        inv_sigma2 = 1.0/err**2
        return -0.5*(np.sum((y-model)**2*inv_sigma2 - np.log(inv_sigma2)))
    if len(theta) == 3:
        m, b, lnf = theta
        model = m * x + b
        inv_sigma2 = 1.0/(err**2 + model**2*np.exp(2*lnf))
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

def lnprob(theta, x, y, err, pRanges, *args, **kwargs):
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
    err : float array
        The uncertainty of the data.
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
    return lp + lnlike(theta, x, y, err, *args, **kwargs)

def posRange(pRanges):
    """
    Generate a position in the parameter space randomly from the prior.

    Parameters
    ----------
    pRange : list
        The ranges of the parameters.

    Returns
    -------
    m : float
        The slope.
    b : float
        The intercept.
    lnf : float (optional)
        The fraction of the model values describing the uncertainty of the model.

    Notes
    -----
    None.
    """
    ndim = len(pRanges)
    if ndim == 2:
        mR, bR = pRanges
        m = (mR[1]-mR[0]) * np.random.rand() + mR[0]
        b = (bR[1]-bR[0]) * np.random.rand() + bR[0]
        return [m, b]
    if ndim == 3:
        mR, bR, lnfR = pRanges
        m = (mR[1]-mR[0]) * np.random.rand() + mR[0]
        b = (bR[1]-bR[0]) * np.random.rand() + bR[0]
        lnf = (lnfR[1]-lnfR[0]) * np.random.rand() + lnfR[0]
        return [m, b, lnf]
    else:
        raise ValueError("[linfit]: The ndim value ({0}) is incorrect!".format(ndim))

def posBall(theta, sigma=0.01):
    """
    Generate a position in the parameter space randomly from a ball centering
    at the given paramters.

    Parameters
    ----------
    theta : float array
        The given parameters.
    sigma : float
        The radius of the ball which is the fraction of the given parameters.

    Returns
    -------
    m : float
        The slope.
    b : float
        The intercept.
    lnf : float (optional)
        The fraction of the model values describing the uncertainty of the model.

    Notes
    -----
    None.
    """
    ndim = len(theta)
    p = np.array(theta) * (1 + (np.random.rand(ndim)-0.5)*2*sigma)
    return p

class LinFit(object):
    """
    Linear regression with MCMC method. The MCMC backend is emcee.
    The y of the data could be upperlimits. The upper limits are properly deal
    with using the method mentioned by Sawicki (2012).
    """
    def __init__(self, x, y, pRanges, xerr=None, yerr=None, flag=None, nsigma=3):
        """
        To initiate the object.

        Parameters
        ----------
        x : float array
            The x data.
        y : float array
            The y data.
        pRanges : list
            The ranges of the linear model.
            [
              [m(min), m(max)],
              [b(min), b(max)],
              [lnf(min), lnf(max)](optional)
            ]
        xerr : float array
            The uncertainty of x data.
        yerr : float array
            The uncertainty of y data.
        flag : float array
            The upperlimit flag of the y data; 0 for the detection and 1 for the
            upperlimit.
        nsigma : float
            The upperlimits are nsigma times of the uncertainties, respectively.

        Notes
        -----
        None.
        """
        self.x = x
        self.y = y
        self.xerr = xerr
        self.yerr = yerr
        self.pRanges = pRanges
        self.flag = flag
        self.nsigma = nsigma
        ndim = len(pRanges)
        if ndim == 2:
            print("[linfit]: The model uncertainty is NOT considered!")
        elif ndim == 3:
            print("[linfit]: The model uncertainty is considered!")
        else:
            raise ValueError("[linfit]: The parameter number ({0}) is incorrect!".format(ndim))
        self.ndim = ndim
        if (xerr is None) & (yerr is None):
            self.err = np.ones_like(x)
        else:
            if xerr is None:
                xerr = np.zeros_like(x)
            if yerr is None:
                yerr = np.zeros_like(y)
            self.err = (xerr**2. + yerr**2.)**0.5

    def EnsembleSampler(self, nwalkers, **kwargs):
        """
        Set up the EnsembleSampler of the emcee.
        """
        self.nwalkers = nwalkers
        self.__sampler = "EnsembleSampler"
        self.sampler = emcee.EnsembleSampler(nwalkers, self.ndim, lnprob,
                       args=(self.x, self.y, self.err, self.pRanges, self.flag, self.nsigma),
                       **kwargs)
        print("[linfit]: Use the EnsembleSampler.")
        return self.sampler

    def PTSampler(self, ntemps, nwalkers, **kwargs):
        self.ntemps = ntemps
        self.nwalkers = nwalkers
        self.__sampler = "PTSampler"
        self.sampler = emcee.PTSampler(ntemps, nwalkers, self.ndim,
                       logl=lnlike, logp=lnprior,
                       loglargs=[self.x, self.y, self.err, self.flag, self.nsigma],
                       logpargs=[self.pRanges], **kwargs)
        print("[linfit]: Use the PTSampler.")
        return self.sampler

    def run_mcmc(self, p, nrun):
        """
        Run the MCMC sampling.

        Parameters
        ----------
        p : float array
            The initial positions of the walkers.
        nrun : float
            The steps to run the sampling.

        Returns
        -------
        None.

        Notes
        -----
        None.
        """
        samplerType = self.__sampler
        nwalkers = self.nwalkers
        ndim = self.ndim
        p = np.array(p)
        if samplerType == "EnsembleSampler":
            assert p.shape == (nwalkers, ndim)
        elif samplerType == "PTSampler":
            assert p.shape == (self.ntemps, nwalkers, ndim)
        sampler = self.sampler
        sampler.run_mcmc(p, nrun)

    def reset(self):
        self.sampler.reset()

    def p_prior(self):
        """
        Generate the positions of the walkers in the parameter space randomly
        from the prior.

        Parameters
        ----------
        None.

        Returns
        -------
        p : float array
            The positions of the walkers.

        Notes
        -----
        None.
        """
        sampler  = self.__sampler
        nwalkers = self.nwalkers
        pRanges = self.pRanges
        if sampler == "EnsembleSampler":
            p = [posRange(pRanges) for i in range(nwalkers)]
        elif sampler == "PTSampler":
            ntemps = self.ntemps
            p = np.zeros((ntemps, nwalkers, self.ndim))
            for loop_t in range(ntemps):
                for loop_w in range(nwalkers):
                    p[loop_t, loop_w, :] = posRange(pRanges)
        return p

    def p_ball(self, theta, sigma=0.01):
        """
        Generate the position of the walkers in the parameter space randomly from
        a ball centering at the given paramters.

        Parameters
        ----------
        theta : float array
            The given parameters.
        sigma : float
            The radius of the ball which is the fraction of the given parameters.

        Returns
        -------
        p : float array
            The positions of the walkers.

        Notes
        -----
        None.
        """
        sampler  = self.__sampler
        nwalkers = self.nwalkers
        if sampler == "EnsembleSampler":
            p = [posBall(theta) for i in range(nwalkers)]
        elif sampler == "PTSampler":
            ntemps = self.ntemps
            p = np.zeros((ntemps, nwalkers, self.ndim))
            for loop_t in range(ntemps):
                for loop_w in range(nwalkers):
                    p[loop_t, loop_w, :] = posBall(theta)
        return p

    def p_logl_max(self):
        """
        Find the position in the sampled parameter space that the likelihood is
        the highest.
        """
        sampler = self.__sampler
        if sampler == "EnsembleSampler":
            chain  = self.sampler.chain
            lnlike = self.sampler.lnprobability
        elif sampler == "PTSampler":
            chain  = self.sampler.chain[0, ...]
            lnlike = self.sampler.lnlikelihood[0, ...]
        else:
            raise ValueError("[linfit]: The sampler type ({0}) is unrecognised!".format(sampler))
        idx = lnlike.ravel().argmax()
        p   = chain.reshape(-1, self.ndim)[idx]
        return p

    def fit(self, nrun=1000, nburnin=500, psigma=0.01):
        self.__nrun = nrun
        self.__nburnin = nburnin
        ndim = self.ndim
        p = self.p_prior()
        self.run_mcmc(p, nburnin)
        pmax = self.p_logl_max()
        p = self.p_ball(pmax, psigma)
        self.reset()
        self.run_mcmc(p, nrun)

    def posterior_sample(self, burnin=0):
        """
        Return the samples merging from the chains of all the pertinent walkers.

        Parameters
        ----------
        burnin : float
            The number of initial samplings that would be dropped as burn-in run.

        Returns
        -------
        samples : float array
            The samples of the parameter space according to the posterior probability.

        Notes
        -----
        None.
        """
        self.__burnin = burnin
        sampler  = self.sampler
        nwalkers = self.nwalkers
        if self.__sampler == "EnsembleSampler":
            chain = sampler.chain
            lnprob = sampler.lnprobability[:, -1]
        elif self.__sampler == "PTSampler":
            chain = np.squeeze(sampler.chain[0, ...])
            lnprob = np.squeeze(sampler.lnprobability[0, :, -1])
        samples = chain[:, burnin:, :].reshape((-1, self.ndim))
        return samples

    def get_BestFit(self, burnin=0):
        parNames = ["m", "b", "lnf"]
        ndim = self.ndim
        samples = self.posterior_sample(burnin)
        BFDict = {
            "samples": samples
        }
        if ndim == 2:
            m_mcmc, b_mcmc = map(lambda v: (v[1], v[2]-v[1], v[1]-v[0]),
                                     zip(*np.percentile(samples, [16, 50, 84],
                                                        axis=0)))
            BFDict["m"] = m_mcmc
            BFDict["b"] = b_mcmc
            BFDict["lnf"] = None
        elif ndim == 3:
            m_mcmc, b_mcmc, lnf_mcmc = map(lambda v: (v[1], v[2]-v[1], v[1]-v[0]),
                                     zip(*np.percentile(samples, [16, 50, 84],
                                                        axis=0)))
            BFDict["m"] = m_mcmc
            BFDict["b"] = b_mcmc
            BFDict["lnf"] = lnf_mcmc
        return BFDict

    def plot_BestFit(self, burnin=0):
        BFDict = self.get_BestFit(burnin)
        samples = BFDict["samples"]
        m_mcmc  = BFDict["m"]
        b_mcmc  = BFDict["b"]
        lnf_mcmc  = BFDict["lnf"]
        fig = plt.figure()
        x = self.x
        y = self.y
        xerr = self.xerr
        yerr = self.yerr
        flag = self.flag
        if flag is None:
            plt.errorbar(x, y, xerr=xerr, yerr=yerr, linestyle="none", marker=".",
                         color="k")
        else:
            fltr = flag == 0
            plt.errorbar(x[fltr], y[fltr], xerr=xerr[fltr], yerr=yerr[fltr],
                         fmt=".k")
            fltr = flag == 1
            plt.errorbar(x[fltr], y[fltr], xerr=xerr[fltr], yerr=0.5, uplims=True,
                         fmt=".k")
        ax = plt.gca()
        ax.tick_params(axis='both', labelsize=20)
        m_bf = m_mcmc[0]
        b_bf = b_mcmc[0]
        xl = np.array(ax.get_xlim())
        yl = m_bf * xl + b_bf
        plt.plot(xl, yl, color="k", linestyle="--", label="Best Fit")
        return (fig, ax)

    def plot_corner(self, burnin=0):
        BFDict = self.get_BestFit(burnin)
        samples = BFDict["samples"]
        fig = corner.corner(samples, quantiles=[0.16, 0.5, 0.84], show_titles=True,
                            title_kwargs={"fontsize": 12})
        ax = plt.gca()
        return (fig, ax)

    def plot_chain(self):
        ndim = self.ndim
        samplerType = self.__sampler
        sampler = self.sampler
        if samplerType == "EnsembleSampler":
            chain  = self.sampler.chain
        elif samplerType == "PTSampler":
            chain  = self.sampler.chain[0, ...]
        else:
            raise ValueError("[linfit]: The sampler type ({0}) is unrecognised!".format(sampler))
        fig, axes = plt.subplots(ndim, 1, sharex=True, figsize=(8, 9))
        axes[0].plot(chain[:, :, 0].T, color="k", alpha=0.4)
        axes[0].yaxis.set_major_locator(MaxNLocator(5))
        axes[0].set_ylabel("$m$", fontsize=24)
        axes[1].plot(chain[:, :, 1].T, color="k", alpha=0.4)
        axes[1].yaxis.set_major_locator(MaxNLocator(5))
        axes[1].set_ylabel("$b$", fontsize=24)
        if ndim == 3:
            axes[2].plot(chain[:, :, 2].T, color="k", alpha=0.4)
            axes[2].yaxis.set_major_locator(MaxNLocator(5))
            axes[2].set_ylabel("$\mathrm{ln}\,f$", fontsize=24)
            axes[2].set_xlabel("step number", fontsize=24)
        fig.tight_layout(h_pad=0.0)
        return (fig, axes)
