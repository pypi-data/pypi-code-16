import matplotlib.pyplot as plt

from fc_tools.colors import str2rgb
from fc_hypermesh.OrthMesh import OrthMesh
from fc_tools.graphics import DisplayFigures,SaveAllFigsAsFiles,set_axes_equal

oTh=OrthMesh(3,5,type='orthotope',box=[[-1,1],[-1,1],[-1,1]])

plt.ion()
plt.figure(1)
plt.clf()
oTh.plotmesh(legend=True)
set_axes_equal()

plt.figure(2)
plt.clf()
oTh.plotmesh(m=2,legend=True,edgecolor=[0,0,0])
set_axes_equal()
plt.axis('off')

plt.figure(3)
plt.clf()
oTh.plotmesh(m=2,facecolor=None,edgecolor=str2rgb('LightGray'))
oTh.plotmesh(m=1,legend=True,linewidth=2)
set_axes_equal()
plt.axis('off')

plt.figure(4)
plt.clf()
oTh.plotmesh(m=1,color='black')
oTh.plotmesh(m=0,legend=True,s=55) # see matplotlib.pyplot.scatter options
set_axes_equal()
plt.axis('off')

DisplayFigures(screen=1)
SaveAllFigsAsFiles('demo01',format='png',tag=True,dir='./toto/tata',verbose=True)