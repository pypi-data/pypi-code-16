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
modDir = curDir+'/../io'
sys.path.append(modDir)

modDir = curDir+'/../utils'
sys.path.append(modDir)

import ncFileManipulation_class as ncWrite
import stats_functions as stats


#ncfi._print_dataset_info()
#ncfi._print_dimensions_info()

spNames = [ 'lowtrsp', 'lowtrshem', 'lowtreq', 'lowtrnhem', 'lowtrnp', 
            'midtrsp', 'midtrshem', 'midtreq', 'midtrnhem', 'midtrnp',
            'uprtrsp', 'uprtrshem', 'uprtreq', 'uprtrnhem', 'uprtrnp', 
            'midstsp', 'midstshem', 'midsteq', 'midstnhem', 'midstnp', 
            'topsp',   'topshem',   'topeq',   'topnhem',   'topnp'  ]

oFile = open('outputMass.txt', 'w')

dir = '/discover/nobackup/jkouatch/GEOSctm/GEOS5ref/pTracersTest/scratch/'
#dir = '/discover/nobackup/jkouatch/GEOSctm/testCTM/holding/geosgcm_pT/'


iMonth = [03, 04, 05]
begDay = [03, 01, 01]
endDay = [31, 30, 02]

iYear = 2013
year  = str(iYear).zfill(4)

for im in range(len(iMonth)):
    month = str(iMonth[im]).zfill(2)

    for iDay in range(begDay[im], endDay[im]+1):
        day = str(iDay).zfill(2)
        file = dir+'paTracers2x2.5.geosgcm_pT.'+year+month+day+'_1200z.nc4'
        #print file

        nf = ncWrite.ncFileCreate(file, mode='r', format='NETCDF4')

        var1 = nf.fid.variables['MASS'][:]
  
        oFile.write(" \n")
        oFile.write("Date: %4s/%2s/%2s \n" %(year,month,day))
        oFile.write("------------------------------------------ \n")
        oFile.write(" %2s %15s %22s \n" %("ID", "Specie Name", "Total Mass"))
        oFile.write("------------------------------------------ \n")

        for ic in range(len(spNames)):
            var2 = nf.fid.variables[spNames[ic]][:]
            #print " %3d %-15s %22.3f " %(ic+1, spNames[ic], np.sum(var1*var2))
            oFile.write(" %3d %15s %22.3f \n" %(ic+1, spNames[ic], np.sum(var1*var2)))

        nf.close_file()


oFile.close()
