"""
Plot the neurons in a population that receive connections from a given
presynaptic neuron, coloured according to the connection delay.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import pyNN.mock as sim
from pyNN.space import Grid2D, Space
from pyNN.random import RandomDistribution

Uniform = lambda x,y: RandomDistribution("uniform", [x, y])

N = 121
grid = Grid2D(x0=123.4)
p = sim.Population(N, sim.IF_cond_exp(tau_m=Uniform(10.0, 20.0),
                                      cm=lambda i: 0.8+0.01*i),
                   structure=grid)

prj = sim.Projection(p, p, sim.FixedProbabilityConnector(0.8),
                     sim.StaticSynapse(weight=Uniform(0.4, 0.6),
                                       delay=lambda d: 0.1 + 0.1*d),
                     space=Space(periodic_boundaries=(None, (0, 11), None)))

source_index = 0
targets = [c[1] for c in prj.get('delay', 'list') if c[0] == source_index]
delays = [c[2] for c in prj.get('delay', 'list') if c[0] == source_index]
target_positions = prj.post.positions.T[targets]
source_position = prj.pre[source_index].position

x, y = p.positions[:2]
xt, yt = target_positions.T[:2]

plt.scatter(x, y, s=36, c='w')  # all neurons
plt.scatter(xt, yt, s=400, c=delays, cmap=cm.Oranges)  # neurons receiving connections from the given source neuron
plt.xlabel('x')
plt.ylabel('y')
plt.colorbar()
plt.show()


