from biokit.stats import mixture
import pandas as pd
from easydev import Progress
import numpy as np

data = pd.read_csv("test.csv", index_col=0, header=None)


# Generate a random mixture model

# ############################################### Create data set to be tested
# symetric case
def get_data_case1():
    return mixture.GaussianMixture(mu=[-1, 0, 1], sigma=[0.3,0.3,0.3], 
        mixture=[0.1,.8,.1], N=100000)

# asymetric. Note mu slightly shifted to the left
class Data(object):
    def __init__(self):
        self.mus = [8.8, 10, 11]
        self.sigmas = [0.3, 0.3, 0.3]
        self.mixtures = [.2, .7, .1]
        self.N = 100000

    def __call__(self):
        xx =  mixture.GaussianMixture(
            mu=self.mus, 
            sigma=self.sigmas,
            mixture=self.mixtures, N=self.N)
        return xx.data


class Data2(Data):
    def __init__(self):
        self.mus = [9, 10, 11]
        self.mixture = [.1, .8, .1]


class Benchmark(object):

    def __init__(self):
        self.generator = Data()
        self.N = 100
        self.k = 3

    def run_biokit(self):
        results = {"mus":[], "sigmas": [], "pis": []}
        pb = Progress(self.N)
        for i in range(self.N):
            data = self.generator()
            em = mixture.EM(data)
            em.estimate(k=self.k)

            results['mus'].append(em.results['mus'])
            results["sigmas"].append(em.results['sigmas'])
            results["pis"].append(em.results['pis'])
            pb.animate(i+1) 
        self.results_biokit = results 

    def run_biokit2(self):
        results = {"mus":[], "sigmas": [], "pis": []}
        pb = Progress(self.N)
        for i in range(self.N):
            data = self.generator()
            em = mixture.GaussianMixtureFitting(data)
            em.estimate(k=self.k)
  
            mus = em.results['mus']
            pis = em.results['pis']
            sigmas = em.results['sigmas']
            indices = np.argsort(mus)

            results['mus'].append([mus[x] for x in indices])
            results["sigmas"].append([sigmas[x] for x in indices])
            results["pis"].append([pis[x] for x in indices])
            pb.animate(i+1)
        self.results_biokit2 = results 

    def run_gmm(self):
        from sklearn.mixture import gmm

        results = {"mus":[], "sigmas": [], "pis": []}
        pb = Progress(self.N)
        g = gmm.GMM(n_components=self.k)
        for i in range(self.N):
            g.fit(np.matrix(self.generator()).T)
            
            pis = g.weights_
            mus = g.means_.T[0]
            sigmas = np.sqrt(g.covars_.T[0])

            indices = np.argsort(mus)

            results['pis'].append([pis[x] for x in indices])
            results['mus'].append([mus[x] for x in indices])
            results['sigmas'].append([sigmas[x] for x in indices])
            pb.animate(i+1) 

        self.results_sklearn = results















