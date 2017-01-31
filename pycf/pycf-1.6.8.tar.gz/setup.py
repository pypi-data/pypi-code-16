#!/usr/bin/env python
#
# Python installation script
# $Id: setup.py.in 944 2016-09-05 03:16:31Z pletzer $
#
# Python installation script. Will install the shared library 
# and libCFConfig.py in the directory where python puts its 
# modules (generally /usr/lib/python<VERSION>/site-packages. 
#

from __future__ import print_function
from setuptools import setup, Extension
import glob
import os.path
import sys
import subprocess
import re
import argparse

logging = False
if "--logging" in sys.argv:
  logging = True
  sys.argv.remove('--logging')

def getVersion():
  lines = open('py/__init__.py').read()
  m = re.search(r'__version__\s*=\s*[\"\']([\d\.]+)[\"\']', lines)
  return m.group(1) 

def getValuesFromOption(opt, cmd):
  """
  Get the values from a given option in a command
  @param opt e.g. -L or -l
  @param cmd e.g. "-L/usr/local/myLib -lmyLib"
  @return list of values (e.g. ['/usr/local/myLib'])
  """
  values = []
  pat = opt + r'\s*([\w\_\/\\\.\-]+)'
  m = re.search(pat, cmd)
  while m:
    # found
    val = m.group(1)
    values.append(val)
    # remove the option-value pair
    cmd = re.sub(opt + '\s*' + val, '', cmd)
    m = re.search(pat, cmd)
  return values

def parseLinkCommand(cmd):
  """
  Find all the library paths and library names deom the link command
  @param cmd e.g. "-L/usr/local/myLib -lmyLib"
  @return list of library directories and list of library names
  """
  libdirs = getValuesFromOption('-L', cmd)
  libs = getValuesFromOption('-l', cmd)
  return libdirs, libs

def breakLibraryPath(path):
  """
  Break a library path into -L and -l parts
  @param path e.g. /usr/lib/liblapack.so
  @return library directory (e.g. '/usr/lib') and library name (e.g. 'lapack')
  """
  dirname, libname = os.path.split(path)
  # remove the suffix
  libname = re.sub(r'\..*$', '', libname)
  # remove leading 'lib' if on UNIX
  if sys.platform is not 'win32':
    libname = re.sub(r'^\s*lib', '', libname)
  return dirname, libname


def findLibrary(dirs, name):
  """
  Find library by searching a few common directories
  @param dirs list of directories
  @param name name of the library, without lib and without suffix
  @return full path to the library or '' if not found
  """
  for directory in dirs:
    libname = directory + '/lib' + name + '.*'
    libs = glob.glob(libname)
    if len(libs) > 0:
      # use the first occurrence
      return libs[0]
  return ''

# Find out how netcdf was compiled. Must have nc-config in the path.
try:
	netcdf_incdir = subprocess.check_output(['nc-config', '--includedir']).decode("utf-8")
	# remove trailing \n and leading spaces
	netcdf_incdir = re.sub(r"\n\s*$", "", netcdf_incdir)
except:
	print('ERROR: could not find command nc-config. Most likely, netcdf was not installed.')
	print('conda install netcdf4')
	print('will install netcdf under Anaconda')
	sys.exit(1)

cmd = subprocess.check_output(['nc-config', '--libs']).decode("utf-8")
netcdf_libdirs, netcdf_libs = parseLinkCommand(cmd)


# Get LAPACK and BLAS. If not set then search common locations
dirs = (os.path.dirname(sys.executable) + '/../lib', '/usr/local/lib', '/usr/lib', '/usr/lib64')
blas_libraries = []
# prefer MKL
lapack_libraries = findLibrary(dirs, 'mkl_core')
if not lapack_libraries:
  lapack_libraries = os.environ.get('LAPACK_LIBRARIES', findLibrary(dirs, 'lapack'))
  blas_libraries = os.environ.get('BLAS_LIBRARIES', findLibrary(dirs, 'blas'))
  if not blas_libraries:
    print('ERROR: could not find blas -- set environment variable BLAS_LIBRARIES and rerun')
    sys.exit(2)

if not lapack_libraries:
  print('ERROR: could not find lapack -- set environment variable LAPACK_LIBRARIES and rerun')
  sys.exit(1)

# generate cf_config.h
cfg = open('cf_config.h', mode='w')
print('#define VERSION "{}"'.format(getVersion()), file=cfg)
print('#define HAVE_LAPACK_LIB', file=cfg)
print('#define HAVE_CONFIG_H', file=cfg)
cfg.close()

lapack_dir, lapack_lib = breakLibraryPath(lapack_libraries)
libdirs = netcdf_libdirs + [lapack_dir]
libs = netcdf_libs + [lapack_lib]
if blas_libraries:
  blas_dir, blas_lib = breakLibraryPath(blas_libraries)
  libdirs += [blas_dir]
  libs += [blas_lib]

# list all the directories that contain source file to be compiled 
# into a shared library
dirs = ['src', 
        'gridspec_api/global',
        'gridspec_api/axis',
        'gridspec_api/coord',
        'gridspec_api/grid',
        'gridspec_api/data',
        'gridspec_api/regrid',
        'gridspec_api/mosaic',
        'gridspec_api/host',
]

# list all the include directories
incdirs = [netcdf_incdir, 'include', './'] + dirs

srcs = []
for d in dirs:
  for filePat in ('/*.cpp', '/*.c'):
    for s in glob.glob(d + filePat):
      if re.search('tst_', s):
        # filter out the unit tests
        continue
      srcs.append(s)

# generate the configuration file
subprocess.call(["python", "py/generateLibCFConfig.py",
                 "--netcdf_libdir={}".format(netcdf_libdirs[0]),
                 "--netcdf_incdir={}".format(netcdf_incdir),
                 "--srcdir=./", "--builddir=./", 
                 "--config=py/libCFConfig.py"])

def_macs = [('HAVE_LAPACK_UNDERSCORE', 1)]
if logging:
  def_macs += [('LOGGING', 1)]
ext_modules = [Extension("pycf/libcf", # name of the shared library
                          srcs,
                          define_macros=def_macs,
                          include_dirs=incdirs,
                          libraries=libs,
                          library_dirs=libdirs)]

#sys.exit(1)

setup(name = "pycf",
      version = getVersion(),
      long_description = """LibCF - A library to aid in the creation, processing and sharing of 
#scientific data files that conform to the Climate and Forecast (CF) conventions""",
      author_email      = "alexander.pletzer@nesi.org.nz",
      url               = "http://www.unidata.ucar.edu/software/libcf/",
      download_url      = "http://python.org/pypi/pylibcf",
      platforms         = ["any"],
      license           = "UCAR/Unidata",
      description = "Python access to the LibCF library",
      packages=['pycf'],
      package_dir={'pycf': 'py'}, # expect the python files to be under pycf
      ext_modules=ext_modules)

