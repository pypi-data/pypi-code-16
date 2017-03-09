#!/usr/bin/env python

"""
  This script is meant to compare common variables in two netCDF files.
  It does the following:
     - takes two netCDF files
     - Identifies the variables that are common to both files
     - Creates two text files (for their related netCDF files) that contain
       the min/mean/max values of each variable per vertical level.
"""

#-------------
# Load modules
#-------------
from netCDF4 import Dataset
import numpy as np                         # Numpy import
import sys

#-----------------------------------------------
# Get the two netCDF files from the command line
#-----------------------------------------------
fileA = sys.argv[1]
fileB = sys.argv[2]

print "-" *100
print "Comparing the two files:"
print "    * ", fileA
print "    * ", fileB
print "-" *100

#----------------------
# Open the netCDF files
#----------------------
fidA = Dataset(fileA, mode='r', format='NETCDF4')
fidB = Dataset(fileB, mode='r', format='NETCDF4')

#----------------------------------------
# Get the list of variables in both files
#----------------------------------------
listVarsA = fidA.variables.keys()
listVarsB = fidB.variables.keys()

#-----------------------------------------------------------
# Create the list of variables that are common to both files
#-----------------------------------------------------------
dimVars  = fidA.dimensions.keys()  # list of dimension variables not to include
listVars = [var for var in list(set(listVarsA).intersection(set(listVarsB))) if var not in dimVars]

#------------------------------------------------------------------
# Get the the length (number of records) of the unlimited dimension
#------------------------------------------------------------------
nrecs = 0
for dimobj in fidA.dimensions.values():
    if dimobj.isunlimited():
       nrecs = len(dimobj)

#--------------------------------------
# Create text files to write statistics
#--------------------------------------
fA = open("fileA.txt", 'w')
fB = open("fileB.txt", 'w')

format3 = "{:<13} {:<5} {:>21} {:>21} {:>21} \n"
format4 = "{:<13} {:<5} {:>21.12e} {:>21.12e} {:>21.12e} \n"

format1 = "{:<13} {:<5} {:<5} {:>21} {:>21} {:>21} \n"
format2 = "{:<13} {:<5} {:<5} {:>21.12e} {:>21.12e} {:>21.12e} \n"

#-------------------------------------------------------------------------------
# Read common variables, compute min/mean/max for each level and time record and
# write the data into the file
#-------------------------------------------------------------------------------

for varName in listVars:
    valsA = fidA.variables[varName][:]
    valsB = fidB.variables[varName][:]

    if (nrecs == 0):
       #------------------
       # No time dimension
       #------------------
       fA.write("%s \n" %("-"*100) )
       fA.write(format3.format(varName.strip()+":", "Lev", "Min", "Mean", "Max"))
       fA.write("%s \n" %("-"*100) )

       fB.write("%s \n" %("-"*100) )
       fB.write(format3.format(varName.strip()+":", "Lev", "Min", "Mean", "Max"))
       fB.write("%s \n" %("-"*100) )

       if (valsA.ndim == 2):
          fA.write(format4.format("",0, np.min(valsA[:,:]),  np.mean(valsA[:,:]),  np.max(valsA[:,:])))
          fB.write(format4.format("", 0, np.min(valsB[:,:]),  np.mean(valsB[:,:]),  np.max(valsB[:,:])))
       elif (valsA.ndim == 3):
          nlevs = valsA.shape[0]
          for l in range(nlevs):
              fA.write(format4.format("", l, np.min(valsA[l,:,:]),  np.mean(valsA[l,:,:]),  np.max(valsA[l,:,:])))
              fB.write(format4.format("", l, np.min(valsB[l,:,:]),  np.mean(valsB[l,:,:]),  np.max(valsB[l,:,:])))
    else:
       #--------------------
       # At least one record
       #--------------------
       fA.write("%s \n" %("-"*100) )
       fA.write(format1.format(varName.strip()+":","Rec", "Lev", "Min", "Mean", "Max"))
       fA.write("%s \n" %("-"*100) )

       fB.write("%s \n" %("-"*100) )
       fB.write(format1.format(varName.strip()+":","Rec", "Lev", "Min", "Mean", "Max"))
       fB.write("%s \n" %("-"*100) )

       for n in range(nrecs):
           if (valsA.ndim == 3):
              fA.write(format2.format("",n, 0, np.min(valsA[n,:,:]),  np.mean(valsA[n,:,:]),  np.max(valsA[n,:,:])))
              fB.write(format2.format("",n, 0, np.min(valsB[n,:,:]),  np.mean(valsB[n,:,:]),  np.max(valsB[n,:,:])))
           elif (valsA.ndim == 4):
              nlevs = valsA.shape[1]
              for l in range(nlevs):
                  fA.write(format2.format("",n, l, np.min(valsA[n,l,:,:]),  np.mean(valsA[n,l,:,:]),  np.max(valsA[n,l,:,:])))
                  fB.write(format2.format("",n, l, np.min(valsB[n,l,:,:]),  np.mean(valsB[n,l,:,:]),  np.max(valsB[n,l,:,:])))
           if (n < nrecs-1):
              fA.write("%s \n" %("."*100) )
              fB.write("%s \n" %("."*100) )

    fA.write(" \n")
    fB.write(" \n")

#------------
# Close files
#------------
fA.close()
fB.close()

fidA.close()
fidB.close()
