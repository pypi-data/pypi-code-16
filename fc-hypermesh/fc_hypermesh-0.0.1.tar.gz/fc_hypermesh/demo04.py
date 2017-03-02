import matplotlib.pyplot as plt

from fc_hypermesh.OrthMesh import OrthMesh
from fc_tools.graphics import DisplayFigures

oTh=OrthMesh(2,5,type='simplicial',box=[[-1,1],[-1,1],[-1,1]])

plt.close('all')
plt.ion()
plt.figure(1)
plt.clf()
oTh.plotmesh(legend=True)

plt.figure(2)
plt.clf()
oTh.plotmesh(m=1,legend=True,linewidth=3)
plt.axis('off')

plt.figure(3)
plt.clf()
oTh.plotmesh(m=1,color='black')
oTh.plotmesh(m=0,legend=True,s=105) # see matplotlib.pyplot.scatter options
plt.axis('off')

DisplayFigures(screen=1)