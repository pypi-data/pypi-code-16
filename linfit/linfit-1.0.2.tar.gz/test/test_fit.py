import numpy as np
import matplotlib.pyplot as plt
from linfit import LinFit

# Reproducible results!
np.random.seed(123)

# Choose the "true" parameters.
m_true = -0.9594
b_true = 4.294
f_true = 0.534

# Generate some synthetic data from the model.
N = 50
x = np.sort(10*np.random.rand(N))
yerr = 0.1+0.5*np.random.rand(N)
y = m_true*x+b_true
y += np.abs(f_true*y) * np.random.randn(N)
y += yerr * np.random.randn(N)

# Plot the dataset and the true model.
xl = np.array([0, 10])
plt.errorbar(x, y, yerr=yerr, fmt=".k")
plt.plot(xl, m_true*xl+b_true, "k", lw=3, alpha=0.6)
plt.ylim(-9, 9)
plt.xlabel("$x$")
plt.ylabel("$y$")
plt.tight_layout()
plt.savefig("line-data.png")
plt.close()

pRanges = [[-10, 10], [-20, 20], [-10, 1]]
lf = LinFit(x, y, pRanges, yerr=yerr)
lf.EnsembleSampler(nwalkers=100)
#lf.PTSampler(ntemps=10, nwalkers=100)
print("Start fitting!")
lf.fit(nrun=1000, nburnin=500, psigma=0.01)
print("Finish fitting!")
burnin = 200
BFDict = lf.get_BestFit(burnin)

lf.plot_BestFit(burnin)
plt.savefig("best-fit.png")
plt.close()

lf.plot_corner(burnin)
plt.savefig("corner.png")
plt.close()

lf.plot_chain()
plt.savefig("chain.png")
plt.close()
