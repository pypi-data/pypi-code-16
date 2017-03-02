import matplotlib.pyplot as plt
import numpy as np
from fc_hypermesh.OrthMesh import OrthMesh
from fc_tools.graphics import DisplayFigures

trans=lambda q: np.array([20*q[0],2*(2*q[1]-1+np.cos(2*np.pi*q[0]))])

oTh=OrthMesh(2,[100,20],type='simplicial',mapping=trans)#box=[[-1,1],[-1,1],[-1,1]])

plt.close('all')
plt.ion()
plt.figure(1)
plt.clf()
oTh.plotmesh(legend=True)
plt.axis('equal')

plt.figure(2)
plt.clf()
oTh.plotmesh(color='lightgray')
oTh.plotmesh(m=1,legend=True,linewidth=3)
plt.axis('equal')
plt.axis('off')

plt.figure(3)
plt.clf()
oTh.plotmesh(color='lightgray')
oTh.plotmesh(m=1,color='black')
oTh.plotmesh(m=0,legend=True,s=105) # see matplotlib.pyplot.scatter options
plt.axis('equal')
plt.axis('off')

DisplayFigures(screen=1)