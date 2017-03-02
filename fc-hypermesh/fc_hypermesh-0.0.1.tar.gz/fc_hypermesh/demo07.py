import matplotlib.pyplot as plt
import numpy as np

from fc_tools.graphics import set_axes_equal
from fc_hypermesh.OrthMesh import OrthMesh
from fc_tools.graphics import set_axes_equal,DisplayFigures

N1=3;N2=25;N3=3
d=3
trans=lambda q: np.array([q[0]+np.sin(4*np.pi*q[1]), 10*q[1]-1, q[2]+np.cos(4*np.pi*q[1])])

oTh=OrthMesh(3,[3,25,3],type='simplicial',mapping=trans)

plt.close('all')
plt.ion()
plt.figure(1)
plt.clf()
oTh.plotmesh(legend=True)
set_axes_equal()

plt.figure(2)
plt.clf()
oTh.plotmesh(m=2,legend=True,edgecolor=[0,0,0])
set_axes_equal()

plt.figure(3)
plt.clf()
oTh.plotmesh(m=2,edgecolor='lightgray',facecolor=None,alpha=0.3)
oTh.plotmesh(m=1,legend=True,linewidth=2)
set_axes_equal()

plt.figure(4)
plt.clf()
oTh.plotmesh(m=1,color='black')
oTh.plotmesh(m=0,legend=True,s=55) # see matplotlib.pyplot.scatter options
set_axes_equal()

DisplayFigures(screen=1)