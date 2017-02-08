from sklearn.mixture import GMM
import numpy as np
import pandas as pd




class GMMSK(object):
    def __init__(self, means=[60,100,140], sigmas=[10,10,10], weights=[.1,.8,.1]):
        n_component = len(means)
        self.gmm = GMM(n_component, n_iter=100)
        self.gmm.means_ = np.array([[x] for x in means])
        self.gmm.covars_ = np.array([[x] for x in sigmas])**2
        self.gmm.weights_ = np.array(weights)

    def sample(self, N=10000):
        return self.gmm.sample(N)

    def fit(self, X, k=3):
        model = GMM(k).fit(X)
        return model

    def fit2(self, X, k=3):
        from biokit.stats import mixture
        self.mf = mixture.EM(X[:,0])
        self.mf.estimate(k=3)
        return self.mf.results
    
    def fit3(self, X, k=3):
        from biokit.stats import mixture
        self.mf = mixture.GaussianMixtureFitting(X[:,0])
        self.mf.estimate(k=3)
        return self.mf.results

    def error(self, n=10, N=10000):
        error_mu = []
        error_sigma = []
        error_weight = []
        for this in range(n):
            model = self.fit(self.sample(N))

            index = np.argmax(model.weights_)

            error = self.gmm.means_[1] - model.means_[index]
            error = 100*abs(error/self.gmm.means_[1])
            error_mu.append(error)

            error = np.sqrt(self.gmm.covars_[1]) - np.sqrt(model.covars_[index])
            error = 100*abs(error/np.sqrt(self.gmm.covars_[1]))
            error_sigma.append(error)

            error = self.gmm.weights_[1] - model.weights_[index]
            error = 100*abs(error/self.gmm.weights_[1])
            error_weight.append(error)
        df = pd.DataFrame({'mu': [x[0] for x in error_mu], 
            'sigma': [x[0] for x in error_sigma], 
            'weight': error_weight})
        df = df[['mu', 'sigma', 'weight']]
        return df

    def error_biokit(self, n=10, N=10000, mode='em'):
        # we look at the central distribution only
        error_mu = []
        error_sigma = []
        error_weight = []
        for this in range(n):
            if mode == "em":
                estimation = self.fit2(self.sample(N))
            else:
                estimation = self.fit3(self.sample(N))
            error = self.gmm.means_[1] - estimation.mus[1]
            error = 100*abs(error/self.gmm.means_[1])
            error_mu.append(error)

            error = np.sqrt(self.gmm.covars_[1]) - estimation.sigmas[1]
            error = 100*abs(error/np.sqrt(self.gmm.covars_[1]))
            error_sigma.append(error)
            
            error = self.gmm.weights_[1] - estimation.pis[1]
            error = 100*abs(error/self.gmm.weights_[1])
            error_weight.append(error)
        df = pd.DataFrame({'mu': [x[0] for x in error_mu], 
            'sigma': [x[0] for x in error_sigma], 
            'weight': error_weight})
        df = df[['mu', 'sigma', 'weight']]
        return df

    def error2(self, n=10, N=10000):
        return self.error_biokit(n, N)
    def error3(self, n=10, N=10000):
        return self.error_biokit(n, N, mode="gmf")



