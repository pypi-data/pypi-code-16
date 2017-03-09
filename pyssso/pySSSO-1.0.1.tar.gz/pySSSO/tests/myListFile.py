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
import glob

listFiles = glob.glob('/discover/nobackup/jkouatch/gmiMetFields/MERRA/2x2.5/*.2x2.5x72.nc')

f = open('srun_ncMyExecutableFile', 'w')
#f = open('ncMyExecutableFile', 'w')

for l in listFiles:
    f.write("srun -n 1 -c 1 --exclusive /discover/nobackup/jkouatch/PoDS/Compare/ncReadWrite/fileProc.sh " + l +" & \n")
    #f.write("/discover/nobackup/jkouatch/PoDS/Compare/ncReadWrite/fileProc.sh " + l +"\n")

f.close()

