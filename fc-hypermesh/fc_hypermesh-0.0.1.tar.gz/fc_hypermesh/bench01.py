import time
from pyHyperMesh.OrthMesh import OrthMesh

d=3
ctype='simplicial'
Box=[[-1,1],[-1,1],[-1,1]]
print('# BENCH in dimension %d with %s mesh'%(d,ctype))
print('#d: %d'%d)
print('#type: %s'%ctype)
print('#box: %s'%str(Box))
print('#desc:  N        nq       nme    time(s)')
for N in range(20,170,20):
  tstart=time.time()
  Oh=OrthMesh(d,N,type=ctype,box=Box)
  t=time.time()-tstart
  print('     %4d  %8d  %8d     %2.3f'%(N,Oh.Mesh.nq,Oh.Mesh.nme,t))