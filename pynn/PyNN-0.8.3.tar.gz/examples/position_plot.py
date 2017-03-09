"""
Plot neuron positions, and colour the neurons according to their parameter
values.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import pyNN.mock as sim
from pyNN.space import Grid2D
from pyNN.random import RandomDistribution

Uniform = lambda x,y: RandomDistribution("uniform", [x, y])

N = 49
grid = Grid2D(x0=123.4)
p = sim.Population(N, sim.IF_cond_exp(tau_m=Uniform(10.0, 20.0),
                                      cm=lambda i: 0.8+0.01*i),
                   structure=grid)

x, y = p.positions[:2]

 
plt.scatter(x, y, s=400, c=p.get("cm"), cmap=cm.hot)
#plt.scatter(x, y, s=400, c=p.get("tau_m"), cmap=cm.hot)
plt.xlabel('x')
plt.ylabel('y')
ax = plt.gca()
plt.colorbar()
plt.show()


