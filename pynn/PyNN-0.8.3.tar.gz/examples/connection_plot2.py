"""
Connections from a given source neuron to target neurons in the same
population shown with arrows.
"""

from __future__ import division
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

prj = sim.Projection(p, p, sim.DistanceDependentProbabilityConnector("max(0, 1-d/5.0)"),
                     sim.StaticSynapse(weight=Uniform(0.4, 0.6),
                                       delay=lambda d: 0.1 + 0.1*d),
                     space=Space(periodic_boundaries=(None, (0, 11), None)))

source_index = 60
targets = [c[1] for c in prj.get('delay', 'list') if c[0] == source_index]
weights = [c[2] for c in prj.get('delay', 'list') if c[0] == source_index]
target_positions = prj.post.positions.T[targets]
xs, ys = prj.pre[source_index].position[:2]

xp, yp = p.positions[:2]
xt, yt = target_positions.T[:2]


plt.scatter(xp, yp, s=36, c='w')
for x,y,w in zip(xt, yt, weights):
    plt.arrow(xs, ys, x-xs, y-ys, width=0.1*w) #, length_includes_head=True)
plt.xlabel('x')
plt.ylabel('y')
plt.show()


