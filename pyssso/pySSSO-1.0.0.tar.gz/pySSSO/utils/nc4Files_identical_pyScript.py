#!/usr/bin/env python

"""
  This script takes two netCDF files and finds out if they are bit-wise identical.
"""


#-------------
# Load modules
#-------------
from netCDF4 import Dataset
import numpy as np                         # Numpy import
import sys
import shutil

def rms(V):
    return np.sqrt(np.mean(np.square(V)))

fileA = sys.argv[1]
fileB = sys.argv[2]

machine_eps = np.finfo(float).eps # sys.float_info.epsilon

machine_eps = 1.0e-25

print "-" *100
print "Comparing the two files:"
print "  * ", fileA
print "  * ", fileB
print "-" *100

fidA = Dataset(fileA, mode='r', format='NETCDF4')
fidB = Dataset(fileB, mode='r', format='NETCDF4')

listVars = fidA.variables.keys()
dimVars  = fidA.dimensions.keys()

print "            Machine precision: ", machine_eps
same = True
for varName in listVars:
    if varName not in dimVars:
       valsA = fidA.variables[varName][:]
       valsB = fidB.variables[varName][:]
       diff = np.sum(valsA - valsB)
       print "Variable Name and Sum of Difference: %-15s %30.27f" %(varName, diff)
       varSize = valsA.size
       err = rms(valsA - valsB)
       if (err > machine_eps):
          print "     The variable %s differs in the two files" %(varName)
          same = False


print "-" *100
if same:
   print " -----> The two files are identical!"
else:
   print " -----> The two files are different!"

print "-" *100

fidA.close()
fidB.close()
