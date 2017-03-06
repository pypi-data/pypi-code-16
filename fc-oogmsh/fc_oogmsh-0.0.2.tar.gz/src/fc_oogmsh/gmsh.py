import numpy
import sys,os,errno
import os.path as op
import  subprocess
from . import sys

class ooGmsh:
  def __init__(self,gmsh_file=None):
    self.q = []
    self.dim = 3
    self.nq = 0
    self.M = []
    self.sElts=[]
    self.toGlobal=[]
    self.partitionnedfile=False
    self.orders = []
    self.types =[]
    if gmsh_file==None:
      return
    try:
       fid = open(gmsh_file, "r")
    except IOError:
       print("File '%s' not found." % (gmsh_file))
       sys.exit()
    line = 'start'
    lineno=0
    while line:
      line = fid.readline()
      lineno+=1
      if line.find('$Nodes') == 0:
        line = fid.readline()
        lineno+=1
        self.nq = int(line.split()[0])
        self.q = numpy.zeros((self.nq, 3), dtype=float)
        self.toGlobal=numpy.zeros((self.nq, ), dtype=int)
        # FC : use numpy.genfromtxt ?
        for i in range(0, self.nq):
            line = fid.readline()
            data = line.split()
            #idx = int(data[0])-1  # fix gmsh 1-based indexing
            #if i != idx:
            #    raise ValueError('problem with vertex ids')
            self.toGlobal[i]=int(data[0])-1
            self.q[i, :] = list(map(float, data[1:])) # FC : fixe to run with Python3
        line = fid.readline()
        if line.find('$EndNodes') != 0:
          raise ValueError('expecting EndNodes')
        if numpy.sum(numpy.abs(self.q[:,2]))==0:
          self.q=self.q[:,0:2]
          self.dim=2
      if line.find('$Elements') == 0:
        line = fid.readline()
        nel = int(line.split()[0])
        self.M=numpy.zeros((nel,55), dtype=int)
        maxcol=0
        for i in range(0, nel):
          line = fid.readline()
          data = line.split()
          nd=len(data)
          maxcol=max(maxcol,nd)
          self.M[i,0:nd]=data
          #idx = int(data[0])-1  # fix gmsh 1-based indexing
          #M=numpy.genfromtxt(gmsh_file,skip_header=29,skip_footer=1)
          #print(M)
        self.M=self.M[:,0:maxcol]
        line = fid.readline()
        #print(line)
        if line.find('$EndElements') != 0:
          raise ValueError('expecting EndElements')    
    self.splitByType()
    self.setOrders()
    self.setTypes()
         
  def splitByType(self):
    nType=NumNodesByEltType()
    getOrder=orderByEltType()
    Ltype=numpy.unique(self.M[:,1])
    for i in range(len(Ltype)):
      M=self.M[self.M[:,1]==Ltype[i]]
      self.sElts.append(ooMs())
      self.sElts[i].type=Ltype[i]
      self.sElts[i].order=getOrder[Ltype[i]]
      self.sElts[i].d=EltTypeSimplex(Ltype[i])
      self.sElts[i].nme=M.shape[0]
      self.sElts[i].values=M[:,4:]
      self.sElts[i].nTags=M[:,2]
      self.sElts[i].phys_lab=M[:,3]
      self.sElts[i].geo_lab=M[:,4]
      self.sElts[i].nb_parts=numpy.zeros(self.sElts[i].nme, dtype=int)
      self.sElts[i].part_lab=[None] * self.sElts[i].nme
      K=(self.sElts[i].nTags>=3).nonzero()[0];
      if len(K)>0:
        Kc=numpy.setdiff1d(range(self.sElts[i].nme),K)
        self.sElts[i].nb_parts[K]=M[K,5]
      else:
        Kc=numpy.arange(self.sElts[i].nme )
      ndfe=int(nType[Ltype[i]])
      self.sElts[i].me=numpy.zeros((ndfe,self.sElts[i].nme), dtype=int)
      if len(Kc)>0: #read elmts without partition ids
       self.sElts[i].me[:,Kc]=M[Kc,5:5+ndfe].transpose()
      #read elmts with partition ids  
      for k in K:
        nt=self.sElts[i].nTags[k]
        istart=6
        iend=3+nt
        self.sElts[i].part_lab[k]=M[k,istart:iend]
        istart=3+nt
        iend=istart+ndfe
        self.sElts[i].me[:,k]=M[k,istart:iend].transpose()
        
      self.sElts[i].me-=1
      
  def setOrders(self):
      Orders=numpy.zeros(len(self.sElts),dtype=int)
      for i in range(len(self.sElts)):
        Orders[i]=self.sElts[i].order
      self.orders=numpy.unique(Orders)
    
  def setTypes(self):
      Types=numpy.zeros(len(self.sElts),dtype=int)
      for i in range(len(self.sElts)):
        Types[i]=self.sElts[i].type
      self.types=Types
      
  def __repr__(self):
    strret = '%s object \n'%(self.__class__.__name__ )
    strret += '    dim : %d\n'%self.dim 
    strret += '  types : %s\n'%str(self.types)
    strret += ' orders : %s\n'%str(self.orders)
    strret += '     nq : %d\n'%self.nq
    strret += repr_object('      q :',self.q)+'\n'
    strret += repr_object('toGlobal:',self.toGlobal)+'\n'
    strret += repr_object('  sElts :',self.sElts)
    #strret += '      q : %s object[%s], size %s\n'%(self.q.__class__.__name__,str(self.q.dtype),str(self.q.shape))
    #strret += 'toGlobal: %s object, size %s\n'%(self.toGlobal.__class__.__name__,str(self.toGlobal.shape))
##    strret += '      M : dimension %s\n'%str(self.M.shape)
    #strret += '  sElts : list of (%d) %s objects'%(len(self.sElts),self.sElts[0].__class__.__name__)
    return strret
      
class ooMs:
  def __init__(self):
    self.type = 0
    self.order = 0
    self.d = 0
    self.nme = [] # N -> nme
    self.values=[]
    self.nTags=[]
    self.phys_lab=[] # PhysicalLabel -> phys_lab
    self.geo_lab = [] # GeometricalLabel -> geo_lab
    self.nb_parts =[] # nMeshPart -> nb_parts
    self.part_lab =[] #  MeshPart -> part_lab
    self.me =[]    
    
  def __repr__(self):
    strret = '%s object \n'%self.__class__.__name__ 
    strret += '      d : %d, type : %d, order : %d\n'%(self.d,self.type,self.order)
    strret += '    nme : %d\n'%self.nme
    strret += repr_object('     me :',self.me)+'\n'
    strret += repr_object('phys_lab:',self.phys_lab)+'\n'
    strret += repr_object('geo_lab :',self.geo_lab)+'\n'
    strret += repr_object('part_lab:',self.part_lab)+'\n'
    strret += repr_object('nb_parts:',self.nb_parts)+'\n'
    strret += repr_object('  nTags :',self.nTags)
    #strret += repr_object(' values :',self.values)+'\n'
    #strret += 'phys_lab: %s object[%s], size %s\n'%(self.phys_lab.__class__.__name__,str(self.phys_lab.dtype),str(self.phys_lab.shape))
    #strret += 'geo_lab : %s object[%s], size %s\n'%(self.geo_lab.__class__.__name__,str(self.geo_lab.dtype),str(self.geo_lab.shape))
    #strret += 'part_lab: %s of %d elements\n'%(self.part_lab.__class__.__name__,len(self.part_lab))
    #strret += 'nb_parts: %s object[%s], size %s\n'%(self.part_lab.__class__.__name__,str(self.part_lab.dtype),str(self.part_lab.shape))
    #strret += 'nb_parts: %s object[%s], size %s\n'%(self.nb_parts.__class__.__name__,str(self.nb_parts.dtype),str(self.nb_parts.shape))
    #strret += '  nTags : %s object[%s], size %s\n'%(self.nTags.__class__.__name__,str(self.nTags.dtype),str(self.nTags.shape))
    #strret += ' values : %s object[%s], size %s'%(self.values.__class__.__name__,str(self.values.dtype),str(self.values.shape))
    return strret
 
def repr_object(strname,value):
  if isinstance(value,numpy.ndarray):
    return strname + ' %s object[%s], size %s'%(value.__class__.__name__,str(value.dtype),str(value.shape))
  if isinstance(value,list):
    return strname + ' %s of %d elements'%(value.__class__.__name__,len(value))
  return strname + ' unknown'
    
def NumNodesByEltType():
  elm_type=numpy.zeros((32,),dtype=int)
  elm_type[0] = 2   # not used
  elm_type[1] = 2   # 2-node line
  elm_type[2] = 3   # 3-node triangle
  elm_type[3] = 4   # 4-node quadrangle
  elm_type[4] = 4   # 4-node tetrahedron
  elm_type[5] = 8   # 8-node hexahedron
  elm_type[6] = 6   # 6-node prism
  elm_type[7] = 5   # 5-node pyramid
  elm_type[8] = 3   # 3-node second order line
                     # (2 nodes at vertices and 1 with edge)
  elm_type[9] = 6   # 6-node second order triangle
                      # (3 nodes at vertices and 3 with edges)
  elm_type[10] = 9   # 9-node second order quadrangle
                      # (4 nodes at vertices,
                      #  4 with edges and 1 with face)
  elm_type[11] = 10   # 10-node second order tetrahedron
                      # (4 nodes at vertices and 6 with edges)
  elm_type[12] = 27   # 27-node second order hexahedron
                      # (8 nodes at vertices, 12 with edges,
                      #  6 with faces and 1 with volume)
  elm_type[13] = 18   # 18-node second order prism
                      # (6 nodes at vertices,
                      #  9 with edges and 3 with quadrangular faces)
  elm_type[14] = 14   # 14-node second order pyramid
                      # (5 nodes at vertices,
                      #  8 with edges and 1 with quadrangular face)
  elm_type[15] = 1  # 1-node point
  elm_type[16] = 8   # 8-node second order quadrangle
                      # (4 nodes at vertices and 4 with edges)
  elm_type[17] = 20   # 20-node second order hexahedron
                      # (8 nodes at vertices and 12 with edges)
  elm_type[18] = 15   # 15-node second order prism
                      # (6 nodes at vertices and 9 with edges)
  elm_type[19] = 13   # 13-node second order pyramid
                      # (5 nodes at vertices and 8 with edges)
  elm_type[20] = 9   # 9-node third order incomplete triangle
                      # (3 nodes at vertices, 6 with edges)
  elm_type[21] = 10   # 10-node third order triangle
                      # (3 nodes at vertices, 6 with edges, 1 with face)
  elm_type[22] = 12   # 12-node fourth order incomplete triangle
                      # (3 nodes at vertices, 9 with edges)
  elm_type[23] = 15   # 15-node fourth order triangle
                      # (3 nodes at vertices, 9 with edges, 3 with face)
  elm_type[24] = 15   # 15-node fifth order incomplete triangle
                      # (3 nodes at vertices, 12 with edges)
  elm_type[25] = 21   # 21-node fifth order complete triangle
                      # (3 nodes at vertices, 12 with edges, 6 with face)
  elm_type[26] = 4   # 4-node third order edge
                      # (2 nodes at vertices, 2 internal to edge)
  elm_type[27] = 5   # 5-node fourth order edge
                      # (2 nodes at vertices, 3 internal to edge)
  elm_type[28] = 6   # 6-node fifth order edge
                      # (2 nodes at vertices, 4 internal to edge)
  elm_type[29] = 20   # 20-node third order tetrahedron
                      # (4 nodes at vertices, 12 with edges,
                      #  4 with faces)
  elm_type[30] = 35   # 35-node fourth order tetrahedron
                      # (4 nodes at vertices, 18 with edges,
                      #  12 with faces, 1 in volume)
  elm_type[31] = 56   # 56-node fifth order tetrahedron
                      # (4 nodes at vertices, 24 with edges,
                      #  24 with faces, 4 in volume)
  return elm_type

def orderByEltType():
  order=numpy.zeros((32,),dtype=int)
  order[1] = 1   # 2-node line
  order[2] = 1   # 3-node triangle
  order[3] = 1   # 4-node quadrangle
  order[4] = 1   # 4-node tetrahedron
  order[5] = 1   # 8-node hexahedron
  order[6] = 1  # 6-node prism
  order[7] = 1   # 5-node pyramid
  order[8] = 2   # 3-node second order line
                     # (2 nodes at vertices and 1 with edge)
  order[9] = 2   # 6-node second order triangle
                      # (3 nodes at vertices and 3 with edges)
  order[10] = 2   # 9-node second order quadrangle
                      # (4 nodes at vertices,
                      #  4 with edges and 1 with face)
  order[11] = 2   # 10-node second order tetrahedron
                      # (4 nodes at vertices and 6 with edges)
  order[12] = 2   # 27-node second order hexahedron
                      # (8 nodes at vertices, 12 with edges,
                      #  6 with faces and 1 with volume)
  order[13] = 2   # 18-node second order prism
                      # (6 nodes at vertices,
                      #  9 with edges and 3 with quadrangular faces)
  order[14] = 2   # 14-node second order pyramid
                      # (5 nodes at vertices,
                      #  8 with edges and 1 with quadrangular face)
  order[15] = 1   # 1-node point
  order[16] = 2  # 8-node second order quadrangle
                      # (4 nodes at vertices and 4 with edges)
  order[17] = 2   # 20-node second order hexahedron
                      # (8 nodes at vertices and 12 with edges)
  order[18] = 2   # 15-node second order prism
                      # (6 nodes at vertices and 9 with edges)
  order[19] = 2   # 13-node second order pyramid
                      # (5 nodes at vertices and 8 with edges)
  order[20] = 3   # 9-node third order incomplete triangle
                      # (3 nodes at vertices, 6 with edges)
  order[21] = 3   # 10-node third order triangle
                      # (3 nodes at vertices, 6 with edges, 1 with face)
  order[22] = 4   # 12-node fourth order incomplete triangle
                      # (3 nodes at vertices, 9 with edges)
  order[23] = 4   # 15-node fourth order triangle
                      # (3 nodes at vertices, 9 with edges, 3 with face)
  order[24] = 5   # 15-node fifth order incomplete triangle
                      # (3 nodes at vertices, 12 with edges)
  order[25] = 5   # 21-node fifth order complete triangle
                      # (3 nodes at vertices, 12 with edges, 6 with face)
  order[26] = 3   # 4-node third order edge
                      # (2 nodes at vertices, 2 internal to edge)
  order[27] = 4  # 5-node fourth order edge
                      # (2 nodes at vertices, 3 internal to edge)
  order[28] = 5   # 6-node fifth order edge
                      # (2 nodes at vertices, 4 internal to edge)
  order[29] = 3   # 20-node third order tetrahedron
                      # (4 nodes at vertices, 12 with edges,
                      #  4 with faces)
  order[30] = 4   # 35-node fourth order tetrahedron
                      # (4 nodes at vertices, 18 with edges,
                      #  12 with faces, 1 in volume)
  order[31] = 5   # 56-node fifth order tetrahedron
                      # (4 nodes at vertices, 24 with edges,
                      #  24 with faces, 4 in volume)
  return order

def EltTypeSimplex(elmtype):
  if elmtype in [15]:
    return 0
  if elmtype in [1,8]:
    return 1
  if elmtype in [2,9,10,15,21]:
    return 2
  if elmtype in [4,11]:
    return 3  
  return None

def gmsh_run(geofile,**kwargs):
  env=sys.environment()
  dim=kwargs.get('dim', 2)
  meshdir=kwargs.get('meshdir',env.mesh_dir)
  meshfile=kwargs.get('meshfile','')
  options=kwargs.get('options','')
  force=kwargs.get('force',False)
  verbose=kwargs.get('verbose',True)
  #gmsh_cmd='export LD_LIBRARY_PATH=;/home/cuvelier/lib/gmsh-2.11.0-svn-Linux/bin/gmsh';
  #gmsh_cmd='export LD_LIBRARY_PATH=;'+env.gmsh_bin
  gmsh_cmd=env.gmsh_bin
  try:
    fid = open(geofile, "r")
  except IOError:
    print("File '%s' not found." % (geofile))
    sys.exit()
  filewoext=op.splitext(op.basename(geofile))[0] # file without extension
  mkdir_p(meshdir)
  if len(meshfile)==0:
    meshfile=meshdir+op.sep+filewoext+".msh"
  if op.isfile(meshfile):
    if force:
      print(' Overwritting mesh file %s'%(meshfile))
    else:
      print(' Mesh file %s already exist.\n  -> Use "force" flag to rebuild if needed.'%(meshfile))
      return meshfile 
  gmsh_str="%s -%d %s %s -o %s"%(gmsh_cmd,round(dim),options,geofile,meshfile)
  print(' Running gmsh. Be patient...')
  try:
    out=subprocess.check_output(gmsh_str,shell=True, stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError:
    print(' -> Execution of %s failed!\n'%gmsh_str)
    Out=out.decode("utf-8")
    for line in Out.splitlines():
      print(line)
    sys.exit()  
  if verbose:
    Out=out.decode("utf-8")
    for line in Out.splitlines():
      print(line)
  print('  -> done!')
  return meshfile

def buildmesh(d,geofile,N,**kwargs):
  env=sys.environment()
  options=kwargs.get('options','')
  meshdir=kwargs.get('meshdir',env.mesh_dir)
  force=kwargs.get('force',False)
  verbose=kwargs.get('verbose',False)
  options="-setnumber N %d %s"%(N,options)
  ngeofile=checkgeofile(d,geofile)
  filewoext=op.splitext(op.basename(ngeofile))[0] # file without extension
  meshfile=meshdir+op.sep+filewoext+"-"+str(N)+".msh"
  gmsh_run(ngeofile,dim=d,meshdir=meshdir,options=options,meshfile=meshfile,force=force,verbose=verbose)
  return meshfile

def checkgeofile(d,filename):
  geofile=filename
  if os.path.splitext(filename)[1] == '':
    geofile=filename+'.geo'
  if os.path.isfile(geofile):
    return geofile
  if os.path.dirname(filename) != '':
    raise NameError('Unable to find geofile :\n   %s\n'%geofile)
  env=sys.environment()
  ngeofile=os.path.join(env.geo_dir,geofile)
  if os.path.isfile(ngeofile):
    return ngeofile
  if d==2.5:
    sd='3ds'
  else:
    sd='%dd'%d
  ngeofile=os.path.join(env.geo_dir,sd,geofile)
  if os.path.isfile(ngeofile):
    return ngeofile
  raise NameError('Unable to find geofile :\n   %s\n'%geofile)
    
  
    
  
def buildmesh2d(geofile,N,**kwargs):
  return buildmesh(2,geofile,N,**kwargs)

def buildmesh3d(geofile,N,**kwargs):
  return buildmesh(3,geofile,N,**kwargs)

def buildmesh3ds(geofile,N,**kwargs):
  return buildmesh(2.5,geofile,N,**kwargs)

def buildpartmesh(meshfile,np,**kwargs):
  #env=sys.environment()
  options=kwargs.get('options','')
  #meshdir=kwargs.get('meshdir',env.mesh_dir)
  force=kwargs.get('force',False)
  verbose=kwargs.get('verbose',False)
  options='-saveall -part %d %s'%(np,options)
  filewoext=op.splitext(op.basename(meshfile))[0] # file without extension
  filedir=op.dirname(meshfile)
  meshpartfile=filedir+op.sep+filewoext+'-part%d.msh'%np
  gmsh_run(meshfile,options=options,meshfile=meshpartfile,force=force,verbose=verbose)
  return meshpartfile
  
def buildpartrectangle(Lx,Ly,Nx,Ny,N,**kwargs):
  options=kwargs.pop('options','')
  meshfile=kwargs.pop('meshfile',None)
  filename='rectanglepart';
  #geofile='geodir/2d/'+filename+'.geo'
  geofile=checkgeofile(2,filename)
  if meshfile is None:
    meshfile='%s-Lx%.3f-Ly%.3f-Nx%d-Ny%d-N%d.msh'%(filename,Lx,Ly,Nx,Ny,N)
  options=options+' -setnumber N %d'%N + ' -setnumber NX %d'%Nx + ' -setnumber NY %d'%Ny + ' -setnumber LX %d'%Lx + ' -setnumber LY %d'%Ly 
  gmsh_run(geofile,options=options,meshfile=meshfile,**kwargs)
  return meshfile
  
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise