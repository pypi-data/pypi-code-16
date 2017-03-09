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

spNames = [ 'GOCART::CO', 'OX', 'O3', 'O3PPMV', 'CH4', 
            'N2O', 'CFC11', 'CFC12', 'HCFC22']

oFile = open('outputMass_CO.txt', 'w')

dir = '/discover/nobackup/jkouatch/GEOS_CTM/newCode/GOCARTrun/scratch_goCO/'


#iMonth = [03, 04, 05]
#begDay = [03, 01, 01]
#endDay = [31, 30, 02]

iMonth = [07]
begDay = [02]
endDay = [30]

iYear = 2013
year  = str(iYear).zfill(4)

for im in range(len(iMonth)):
    month = str(iMonth[im]).zfill(2)

    for iDay in range(begDay[im], endDay[im]+1):
        day = str(iDay).zfill(2)
        file = dir+'GOCART_CO.gocart_co.'+year+month+day+'_0000z.nc4'
        if (day == '02'):
           file = dir+'GOCART_CO.gocart_co.'+year+month+day+'_0600z.nc4'
        #print file

        nf = ncWrite.ncFileCreate(file, mode='r', format='NETCDF4')

        t = nf.fid.variables['time'][:]
        t2 = t[1]/60
        t= t/60 + t2

        var1 = nf.fid.variables['MASS'][:]
        #print np.size(var1,0)
  
        oFile.write(" \n")
        oFile.write("Date: %4s/%2s/%2s \n" %(year,month,day))
        oFile.write("------------------------------------------ \n")
        oFile.write(" %2s %15s %22s \n" %("ID", "Specie Name", "Total Mass"))
        oFile.write("------------------------------------------ \n")

        for it in range(np.size(t)):
            oFile.write("Hour: %i \n" %(t[it]))
            for ic in range(len(spNames)):
                var2 = nf.fid.variables[spNames[ic]][:]
                #print " %3d %-15s %22.3f " %(ic+1, spNames[ic], np.sum(var1*var2))
                oFile.write(" %3d %15s %22.3f \n" %(ic+1, spNames[ic], np.sum(var1[it,:,:,:]*var2[it,:,:,:])))

        nf.close_file()


oFile.close()
