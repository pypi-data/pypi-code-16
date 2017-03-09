"""
Two populations of neurons shown in 3D space, with some of the connections
shown with arrows.
"""

from __future__ import division
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import pyNN.mock as sim
from pyNN.space import Grid2D, RandomStructure, Space, Cuboid
from pyNN.random import RandomDistribution

Uniform = lambda x,y: RandomDistribution("uniform", [x, y])

N = 121
layer1 = RandomStructure(Cuboid(100, 100, 50.0), origin=(0, 0, -50))
layer2 = RandomStructure(Cuboid(100, 100, 50.0), origin=(0, 0, 50))
p1 = sim.Population(N, sim.IF_cond_exp(tau_m=Uniform(10.0, 20.0),
                                       cm=lambda i: 0.8+0.01*i),
                    structure=layer1)
p2 = sim.Population(N, sim.IF_cond_exp(tau_m=Uniform(10.0, 20.0),
                                       cm=lambda i: 0.8+0.01*i),
                    structure=layer2)

prj = sim.Projection(p1, p2, sim.DistanceDependentProbabilityConnector("exp(-d/30.0)"),
                     sim.StaticSynapse(weight=Uniform(0.4, 0.6),
                                       delay=lambda d: 0.1 + 0.1*d),
                     space=Space(axes='xy'))

source_index = 60
targets = [c[1] for c in prj.get('delay', 'list') if c[0] == source_index]
weights = [c[2] for c in prj.get('delay', 'list') if c[0] == source_index]
target_positions = prj.post.positions.T[targets]
xs, ys, zs = prj.pre[source_index].position
xt, yt, zt = target_positions.T

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
for population, colour in ((p1, 'r'), (p2, 'b')):
    ax.scatter(*population.positions, c=colour)
for x,y,z,w in zip(xt, yt, zt, weights):
    ax.plot([xs, x], [ys, y], [zs, z], 'g')
plt.xlabel('x')
plt.ylabel('y')

plt.show()


