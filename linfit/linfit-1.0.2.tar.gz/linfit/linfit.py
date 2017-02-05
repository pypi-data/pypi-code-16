import emcee
import corner
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from .mock import *
from .likelihoods import *

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
    def __init__(self, x, y, pRanges, xerr=None, yerr=None, flag=None, nsigma=3,
                 lnlikeType="Nukers"):
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
            xerr = np.zeros_like(x)
            yerr = np.ones_like(y)
        else:
            if xerr is None:
                xerr = np.zeros_like(x)
            if yerr is None:
                yerr = np.zeros_like(y)
        self.xerr = xerr
        self.yerr = yerr
        if lnlikeType == "Nukers":
            self.lnlike = lnlike_Nukers
            self.parNames = ["beta", "alpha", "epsy0"]
        elif lnlikeType == "gcs":
            self.lnlike = lnlike_gcs
            self.parNames = ["m", "b", "lnf"]
        elif lnlikeType == "naive":
            self.lnlike = lnlike_naive
            self.parNames = ["m", "b", "lnf"]
        elif lnlikeType == "perp":
            self.lnlike = lnlike_perp
            self.parNames = ["theta", "bv", "V"]
        elif lnlikeType == "perp2":
            self.lnlike = lnlike_perp2
            self.parNames = ["theta", "b", "V"]
        else:
            raise ValueError("[linfit]: The lnlike function ({0}) is not recognised!".format(lnlike))
        self.lnlikeType = lnlikeType

    def lnprob(self, theta, x, y, xerr, yerr, pRanges, *args, **kwargs):
        """
        The ln of probability function.

        Parameters
        ----------
        lnlike : function
            The lnlike function
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
        return lp + self.lnlike(theta, x, y, xerr, yerr, *args, **kwargs)

    def EnsembleSampler(self, nwalkers, **kwargs):
        """
        Set up the EnsembleSampler of the emcee.
        """
        self.nwalkers = nwalkers
        self.__sampler = "EnsembleSampler"
        if self.lnlikeType == "gcs":
            logpargs = (self.x, self.y, self.xerr, self.yerr, self.pRanges,
                    self.flag, self.nsigma)
        else:
            logpargs = (self.x, self.y, self.xerr, self.yerr, self.pRanges)
        self.sampler = emcee.EnsembleSampler(nwalkers, self.ndim, self.lnprob,
                       args=logpargs, **kwargs)
        print("[linfit]: Use the EnsembleSampler.")
        return self.sampler

    def PTSampler(self, ntemps, nwalkers, **kwargs):
        self.ntemps = ntemps
        self.nwalkers = nwalkers
        self.__sampler = "PTSampler"
        if self.lnlikeType == "gcs":
            loglargs = (self.x, self.y, self.xerr, self.yerr, self.flag, self.nsigma)
        else:
            loglargs = (self.x, self.y, self.xerr, self.yerr)
        self.sampler = emcee.PTSampler(ntemps, nwalkers, self.ndim,
                       logl=self.lnlike, logp=lnprior,
                       loglargs=loglargs, logpargs=[self.pRanges], **kwargs)
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
        parNames = self.parNames
        ndim = self.ndim
        samples = self.posterior_sample(burnin)
        lnlikeType = self.lnlikeType
        BFDict = {
            "Parameters": parNames,
            "samples": samples
        }
        bfList = map(lambda v: (v[1], v[2]-v[1], v[1]-v[0]),
                     zip(*np.percentile(samples, [16, 50, 84], axis=0)))
        fmerge = lambda v: (v[0]-v[2], v[0], v[0]+v[1])
        fdiff  = lambda v: (v[1], v[2]-v[1], v[1]-v[0])
        for loop in range(ndim):
            pn = parNames[loop]
            BFDict[pn] = bfList[loop]
        if lnlikeType == "naive" or lnlikeType == "gcs":
            BFDict["slope"] = BFDict["m"]
            BFDict["intercept"] = BFDict["b"]
            lnf = fmerge(BFDict["lnf"])
            BFDict["IntSc"] = fdiff(np.exp(lnf))
        elif lnlikeType == "Nukers":
            BFDict["slope"] = BFDict["beta"]
            BFDict["intercept"] = BFDict["alpha"]
            BFDict["IntSc"] = BFDict["epsy0"]
        elif lnlikeType == "perp":
            t = fmerge(BFDict["theta"])
            BFDict["slope"] = fdiff(np.tan(t))
            bv = fmerge(BFDict["bv"])
            BFDict["intercept"] = fdiff(bv / np.cos(t))
            V = fmerge(BFDict["V"])
            BFDict["IntSc"] = fdiff(np.sqrt(V) / np.cos(t))
        elif lnlikeType == "perp2":
            t = fmerge(BFDict["theta"])
            BFDict["slope"] = fdiff(np.tan(t))
            BFDict["intercept"] = BFDict["b"]
            V = fmerge(BFDict["V"])
            BFDict["IntSc"] = fdiff(np.sqrt(V) / np.cos(t))
        return BFDict

    def get_lnprob(self, theta):
        if self.lnlikeType == "gcs":
            logpargs = (self.x, self.y, self.xerr, self.yerr, self.pRanges,
                    self.flag, self.nsigma)
        else:
            logpargs = (self.x, self.y, self.xerr, self.yerr, self.pRanges)
        lnP = self.lnprob(theta, *logpargs)
        return lnP

    def get_BFProb(self, burnin=0):
        sampler = self.__sampler
        BFDict = self.get_BestFit(burnin)
        parNames = self.parNames
        theta = []
        for pn in parNames:
            theta.append(BFDict[pn][0])
        lnP = self.get_lnprob(theta)
        return lnP

    def plot_BestFit(self, burnin=0):
        #Plot the data
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
        xl = np.array(ax.get_xlim())
        #Plot the best fit
        BFDict = self.get_BestFit(burnin)
        m_fit = BFDict["slope"]
        b_fit = BFDict["intercept"]
        m_bf = m_fit[0]
        b_bf = b_fit[0]
        yl = m_bf * xl + b_bf
        plt.plot(xl, yl, color="k", linestyle="--", label="{0}".format("Best Fit"))
        return (fig, ax)

    def plot_corner(self, burnin=0):
        BFDict = self.get_BestFit(burnin)
        samples = BFDict["samples"]
        fig = corner.corner(samples, labels=self.parNames,
                            quantiles=[0.16, 0.5, 0.84], show_titles=True,
                            title_kwargs={"fontsize": 12})
        ax = plt.gca()
        return (fig, ax)

    def plot_chain(self):
        ndim = self.ndim
        samplerType = self.__sampler
        sampler = self.sampler
        parNames = self.parNames
        if samplerType == "EnsembleSampler":
            chain  = self.sampler.chain
        elif samplerType == "PTSampler":
            chain  = self.sampler.chain[0, ...]
        fig, axes = plt.subplots(ndim, 1, sharex=True, figsize=(8, 9))
        axes[0].plot(chain[:, :, 0].T, color="k", alpha=0.4)
        axes[0].yaxis.set_major_locator(MaxNLocator(5))
        axes[0].set_ylabel(parNames[0], fontsize=24)
        axes[1].plot(chain[:, :, 1].T, color="k", alpha=0.4)
        axes[1].yaxis.set_major_locator(MaxNLocator(5))
        axes[1].set_ylabel(parNames[1], fontsize=24)
        if ndim == 3:
            axes[2].plot(chain[:, :, 2].T, color="k", alpha=0.4)
            axes[2].yaxis.set_major_locator(MaxNLocator(5))
            axes[2].set_ylabel(parNames[2], fontsize=24)
            axes[2].set_xlabel("step number", fontsize=24)
        fig.tight_layout(h_pad=0.0)
        return (fig, axes)
