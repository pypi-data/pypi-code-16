"""

"""

import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import pyNN.mock as sim
from pyNN.space import Grid2D, RandomStructure, Sphere, Cuboid
from pyNN.random import RandomDistribution

Uniform = lambda x,y: RandomDistribution("uniform", [x, y])

N = 121
grid = Grid2D(x0=123.4)
glomerulus = RandomStructure(Sphere(radius=20.0), origin=(50, 0, 0))
layer1 = RandomStructure(Cuboid(100, 100, 50.0), origin=(0, 0, -50))
layer2 = RandomStructure(Cuboid(100, 100, 50.0), origin=(0, 0, 50))
p1 = sim.Population(N, sim.IF_cond_exp(tau_m=Uniform(10.0, 20.0),
                                       cm=lambda i: 0.8+0.01*i),
                    structure=layer1)
p2 = sim.Population(N, sim.IF_cond_exp(tau_m=Uniform(10.0, 20.0),
                                       cm=lambda i: 0.8+0.01*i),
                    structure=layer2)
p3 = sim.Population(N, sim.SpikeSourcePoisson(rate=100.0),
                    structure=glomerulus)

def plot_positions(ax, populations):
    colours = iter('rbgymck')
    for population, colour in zip(populations, colours):
        ax.scatter(*population.positions, c=colour)
    plt.xlabel('x')
    plt.ylabel('y')


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
plot_positions(ax, [p1, p2, p3])
plt.show()
