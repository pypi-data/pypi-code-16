import matplotlib.pyplot as plt

from fc_hypermesh.OrthMesh import OrthMesh
from fc_tools.graphics import set_axes_equal,DisplayFigures

oTh=OrthMesh(3,5,type='simplicial',box=[[-1,1],[-1,1],[-1,1]])

plt.close('all')
plt.ion()
plt.figure(1)
plt.clf()
oTh.plotmesh(legend=True,linewidth=0.5)
#fig.canvas.draw()
#ax=plt.gca()
#ax.set_aspect('equal')
set_axes_equal()

plt.figure(2)
plt.clf()
oTh.plotmesh(m=2,legend=True,edgecolor=[0,0,0])
set_axes_equal()

plt.figure(3)
plt.clf()
oTh.plotmesh(m=2,edgecolor=[0,0,0],color='none')
oTh.plotmesh(m=1,legend=True,linewidth=2,alpha=0.3)
set_axes_equal()

plt.figure(4)
plt.clf()
oTh.plotmesh(m=1,color='black',alpha=0.3)
oTh.plotmesh(m=0,legend=True,s=55) # see matplotlib.pyplot.scatter options
set_axes_equal()
plt.axis('off')


DisplayFigures(screen=1)
