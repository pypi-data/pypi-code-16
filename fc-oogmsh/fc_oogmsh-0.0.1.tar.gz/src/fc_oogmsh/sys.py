import numpy
import sys,os,errno
import os.path as op
import subprocess

def getLocalConfFile():
  fullname=op.dirname(op.abspath(__file__))
  fulldir=fullname[:fullname.rfind(os.sep)]
  conffile=op.join(fulldir,'configure_loc.py')
  return conffile,os.path.isfile(conffile)

def configure(**kwargs):
  [conffile,isFileExists]=getLocalConfFile()
  if isFileExists:
    import imp
    f = open(conffile)
    env = imp.load_source('env', 'sys', f)
    gmsh_bin=env.gmsh_bin
    mesh_dir=env.mesh_dir
    geo_dir=env.geo_dir
    f.close()
  else:
    fullname=op.dirname(op.abspath(__file__))
    Path=fullname[:fullname.rfind(os.sep)]
    gmsh_bin=getDefaultGmshBin()
    mesh_dir=os.path.join(Path,'meshes')
    geo_dir=os.path.join(Path,'fc_oogmsh','geodir')
  gmsh_bin=kwargs.get('gmsh_bin', gmsh_bin )
  mesh_dir=kwargs.get('mesh_dir', mesh_dir )
  geo_dir=kwargs.get('geo_dir', geo_dir )
  if not os.path.isdir(mesh_dir):
    mkdir_p(mesh_dir)
  if not os.path.isdir(geo_dir):
    raise NameError('Not a directory :\n''geo_dir''=%s\n'%geo_dir)
  
  if not os.path.isfile(gmsh_bin):
    from tkinter.filedialog import askopenfilename
    print('     -> Select gmsh binary ...\n');
    if platform.system() == 'Windows':
      ext='.exe'
      gmsh_bin = askopenfilename(defaultextension='.exe',title='Select GMSH binary')
    elif platform.system() == 'Linux':
      gmsh_bin = askopenfilename(title='Select GMSH binary')
    else:
      raise NameError('Not yet implemented for OS X \n')
  print('     -> Using GMSH binary : %s\n'%gmsh_bin)
  print('Write in %s ...\n'%conffile)
  fid=open(conffile,'w')
  fid.write('## Automaticaly generated with fc_oogmsh.configure()\n');
  fid.write('gmsh_bin="%s"\n'%gmsh_bin)
  fid.write('mesh_dir="%s"\n'%mesh_dir)
  fid.write('geo_dir="%s"\n'%geo_dir)
  fid.close()
  print('  -> done\n');
  return conffile
    
def environment():
  [conffile,isFileExists]=getLocalConfFile()
  #print('1->'+conffile)
  #print('1->'+str(os.path.isfile(conffile)))
  #print('1->'+str(isFileExists))
  if not isFileExists:
    print('Try to use default parameters!\n Use fc_oogmsh.configure to configure.\n')
    configure()
  import imp
  f = open(conffile)
  env = imp.load_source('env', 'sys', f)
  f.close()
  return env

def getDefaultGmshBin():
  import platform
  if platform.system() == 'Windows':
    default_gmsh_bin=os.path.join(os.environ['HOMEDRIVE'],os.environ['HOMEPATH'],'Softwares','GMSH','gmsh.exe');
  elif platform.system() == 'Darwin': # For OS X
    default_gmsh_bin=os.path.join(os.environ['HOME'],'GMSH','Gmsh.app','Contents','MacOS','gmsh');
  elif platform.system() == 'Linux':
    default_gmsh_bin=os.path.join(os.environ['HOME'],'bin','gmsh');
  else:
    default_gmsh_bin=''
  return default_gmsh_bin

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise