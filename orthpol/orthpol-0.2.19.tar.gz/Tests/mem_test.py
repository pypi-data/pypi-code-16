import matplotlib.pyplot as plt
import numpy as np
import numpy.random as npr
import os
import psutil
import SpectralToolbox.Spectral1D as S1D
mem = []

npoints = 10000
order = 100
N = 10000

P = S1D.HermiteProbabilistsPolynomial()

(x, w) = P.GaussQuadrature(order)
for i in range(N):
    (x, w) = P.GaussQuadrature(order)
    process = psutil.Process(os.getpid())
    mem.append( process.memory_info().rss )

plt.figure()
plt.plot(mem)
plt.title("Quadrature points")
plt.show(False)

mem = []

x = npr.randn(npoints)
V = P.GradVandermonde(x, order)
for i in range(N):
    print("Iteration %d" %i)
    V = P.GradVandermonde(x, order)
    process = psutil.Process(os.getpid())
    mem.append( process.memory_info().rss )

plt.figure()
plt.plot(mem)
plt.title("Polynomial evaluation")
plt.show(False)