#!/usr/bin/env python

#-------------
# Load modules
#-------------
import os
import sys
from netCDF4 import Dataset
import numpy
from numpy.random import uniform
import numpy as np

# Determine the location (absolute path) of this script
curDir = os.path.dirname(os.path.abspath(__file__))
modDir = curDir+'/../ioUtils'
sys.path.append(modDir)

modDir = curDir+'/../utils'
sys.path.append(modDir)

import ncFileManipulation_class as ncWrite
import stats_functions as stats


AREA = 510064471910250
#ncfi._print_dataset_info()
#ncfi._print_dimensions_info()

spNames = [ 'CO', 'NO', 'N2O', 'O3', 'CH4', 'OH']

oFile = open('outputMass_CTMold.txt', 'w')
dir = '/discover/nobackup/jkouatch/GEOS_CTM/newCode/refGMIrun/holding/gmi_inst/'

#oFile = open('outputMass_CTMnew.txt', 'w')
#dir = '/discover/nobackup/jkouatch/GEOS_CTM/CTM_globSum/refGMIrun/holding/gmi_inst/'

import glob
listFiles = glob.glob(dir+"GEOSctm.gmi_inst.201307*.nc4")

for file in listFiles:
    fileName = os.path.basename(file)
    if ('20130727' not in fileName):
       nf    = ncWrite.ncFileCreate(file, mode='r', format='NETCDF4')
       var1  = nf.fid.variables['MASS'][:]

       nrec = var1[:,0,0,0].size

       oFile.write(" \n")
       oFile.write("------------------------------------------ \n")
       oFile.write(" %15s %22s \n" %("Tracer", "Total Mass"))
       oFile.write("------------------------------------------ \n")

       for ic in range(len(spNames)):
           var2 = nf.fid.variables[spNames[ic]][:]
           for rec in range(nrec):
               oFile.write(" %-7s %20.19f \n" %(spNames[ic], np.sum(var1[rec,:,:,:]*var2[rec,:,:,:])/AREA))
           oFile.write(" \n")

       nf.close_file()


oFile.close()
