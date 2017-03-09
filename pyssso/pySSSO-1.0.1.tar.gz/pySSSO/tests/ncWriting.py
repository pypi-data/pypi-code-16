#!/usr/bin/env python

#-------------
# Load modules
#-------------
from netCDF4 import Dataset
import numpy
from numpy.random import uniform

import ncFileManipulation_class as ncWrite

#------------------
# Creating the file
#------------------
file_name = 'myFile.nc4'
ncfi = ncWrite.ncFileCreate(file_name, mode='w', format='NETCDF4')

latitudes  = ncfi.define_dimension('lat', 'f4', 91, units='degrees north')
longitudes = ncfi.define_dimension('lon', 'f4',144, units='degrees east')
levels     = ncfi.define_dimension('lev', 'i4', 72, units='hPa')
times      = ncfi.define_dimension('time', 'f4', None, 
                                   units='hours since 0001-01-01 00:00:00.0', 
                                   calendar = 'gregorian')

#times = ncfi.define_time('time', 
                 #units = 'hours since 0001-01-01 00:00:00.0',
                 #calendar = 'gregorian')

temp = ncfi.define_var('temp', 'f4', ('time','lev','lat','lon',),
                       units = 'K',
                       long_name = 'Temperature')

ncfi.add_file_attributes(Description ='Sample netCDF file',
                         Source = 'netCDF4 python tutorial',
                         History = 'Created for GISS on November 29, 2012')

ncfi._print_dataset_info()
ncfi._print_dimensions_info()

#---------------
# Setting values
#---------------
latitudes[:]  =  numpy.arange(-90,91,2.0)
longitudes[:] =  numpy.arange(-180,180,2.5)
levels[:]     =  numpy.arange(0,72,1)
 
temp[0:5,:,:,:] = 300*uniform(size=(5,levels.size,latitudes.size, longitudes.size))

#-----------------
# Closing the file
#-----------------
ncfi.close_file()


