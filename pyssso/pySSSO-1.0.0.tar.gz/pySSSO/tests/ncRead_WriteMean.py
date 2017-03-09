#!/usr/bin/env python

"""
  - Open a netCDF file
  - Read a set of variables with multiple time records
  - Compute the time average of the variables read
  - Write the variables in a new file
"""

#-------------
# Load modules
#-------------
import os
import numpy as np
import sys

try:
  from netCDF4 import Dataset
  import netCDF4 as nc
except ImportError:
  print "netCDF4 not installed on this computer."

def copyDimensions(f1, f2):
    for name in f1.dimensions.keys():
        if (name != 'time'):
           data1 = f1.variables[name]
           ndim2 = f2.createDimension(name, size=data1.size)
           data2 = f2.createVariable(name, data1.dtype, (name,))
           data2.units = data1.units
           data2[:] = data1[:]

def copyVariable(f1, f2, var):
    data = f1.variables[var]
    # Only consider the variable that have the time dimension
    if (data.dimensions[0] == 'time'):
       dataMean = np.mean(data,0)
       dims = [(dim) for dim in data.dimensions]
       dims = dims[1:]
       dims = tuple(dims)
       dat = f2.createVariable(var, data.dtype, dims)
       dat.units = data.units
       dat.long_name = data.long_name
       dat.missing_value = data.missing_value
       dat[:] = dataMean[:]

#fileRead = '/discover/nobackup/jkouatch/gmiMetFields/MERRA/2x2.5/MERRA300.prod.assim.20080430.2x2.5x72.nc'

fileRead = sys.argv[1]

base = os.path.basename(fileRead)
fileWrite = os.path.splitext(base)[0]+'_mean'+os.path.splitext(base)[1]

#------------------
# Opening the file
#------------------
fRd = Dataset(fileRead, mode='r')

fWr = Dataset(fileWrite, mode='w')

copyDimensions(fRd, fWr)

#for att in fRd.ncattrs():
#    print att+':', getattr(fRd,att)
#    setattr(fWr,att,getattr(fRd,att))

for name in fRd.variables.keys():
    if (name not in fRd.dimensions.keys()):
       #data = fRd.variables[name]
       #print name, data.units, data.size, data.dtype, data.dimensions
       copyVariable(fRd, fWr, name)
       

fRd.close()

#data = fWr.variables['lat']
#print data.units, data.size, data.dtype, data.dimensions
#
#data = fWr.variables['temp']
#print data.units, data.size, data.dtype, data.dimensions

print "Done with file ", fileWrite
fWr.close()

