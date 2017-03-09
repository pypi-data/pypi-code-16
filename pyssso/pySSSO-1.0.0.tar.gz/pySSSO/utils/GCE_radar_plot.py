#!/usr/bin/env python

"""
  - Reads a binary single precision file
  - There are 30 3D variables
  - There are 48 time records
  - Plot the radar reflectivity for the time record selected

  Need to type:
     ./GCE_radar_plot.py recNum

  where recNum is the record number you want to use for plotting.
"""

#-------------
# Load modules
#-------------
import os
import sys
from numpy.random import uniform
import numpy as np
import matplotlib.pyplot as plt            # pyplot module import
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D

# Determine the location (absolute path) of this script
curDir = os.path.dirname(os.path.abspath(__file__))
modDir = curDir+'/../io'
sys.path.append(modDir)

modDir = curDir+'/../viz'
sys.path.append(modDir)

modDir = curDir+'/../utils'
sys.path.append(modDir)

import binFileManipulation as binFiles
import bmUtilities
import registerColormaps


#---------------
# Set parameters
#---------------
itime   = 48
colcl   = 0.23105e-06
ni      = 260
nj      = 260
nk      = 43
nkr     = 33
ixstart = 2
ixend   = 257
idiff   = ixend-ixstart+1
diff    = float(ni+nj)

iend    = 20

#--------------
# Define arrays
#--------------

x_dir           = np.zeros(ni,      dtype=np.float)
height          = np.zeros(nk,      dtype=np.float)
temp_base       = np.zeros(nk,      dtype=np.float)
plot_array_2dxz = np.zeros((ni,nk), dtype=np.float)
plot_array_2dxy = np.zeros((ni,nj), dtype=np.float)
plot_array_2d   = np.zeros((ni,nj), dtype=np.float)
radar_top       = np.zeros((ni,nj), dtype=np.float)
color_top       = np.zeros((ni,nj), dtype=np.int)
con_color       = np.zeros(( 3, 7), dtype=np.int)

#---------------------
# Determine the height
#---------------------
y11 = np.zeros(nk,      dtype=np.float)
dz = 20.e2
cc1 = 3.4
cc2 = 0.03
dz1 = dz/100.
height[0] = 0.
for k in range(1,43):
    y11[k] = (cc1 + cc2*(k-0.5)*dz1)*(k-0.5)*dz1*100.

# change the unit to km
height[1]=42.5e2
for k in range(1,42):
    height[k+1] = y11[k]+85.e2

height = height/1000./100.
print height

y11 = 1.0

#---------------------
# Open the binary file
#---------------------
dir = '/discover/nobackup/jkouatch/forTom/GCE/'
fName = dir+'GRADS_MOV.DAT'
fileobj = open(fName, mode = 'rb')

#------------------------------------------------
# Read data from the file and manipulate the data
#------------------------------------------------

try:
   iframe = int(sys.argv[1])
   if (iframe > itime):
      print "There are only %d records in the file" %(itime)
      print "Will produce the plot for the last record"
      iframe = itime
except:
   print "By default we will produce the plot for Record 10"
   iframe = 10


for i in range(1, itime+1):
    print "Reading Record %d" %(i)
    cu           = binFiles.read_3d_float(fileobj, ni, nj, nk)
    cv           = binFiles.read_3d_float(fileobj, ni, nj, nk)
    cw           = binFiles.read_3d_float(fileobj, ni, nj, nk)
    supwafad_1p  = binFiles.read_3d_float(fileobj, ni, nj, nk)
    supiafad_1p  = binFiles.read_3d_float(fileobj, ni, nj, nk)
    SUPWMICRO_1P = binFiles.read_3d_float(fileobj, ni, nj, nk)
    SUPIMICRO_1P = binFiles.read_3d_float(fileobj, ni, nj, nk)
    DELSUPW_1P   = binFiles.read_3d_float(fileobj, ni, nj, nk)
    DELSUPI_1P   = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gtemp        = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gtempp       = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gconcl       = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gconcs       = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gconcg       = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gconch       = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gconci1      = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gconci2      = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gconci3      = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gconcccn     = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gmassl1      = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gmassl2      = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gmasss       = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gmassg       = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gmassh       = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gmassi1      = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gmassi2      = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gmassi3      = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gmass_crys   = binFiles.read_3d_float(fileobj, ni, nj, nk)
    gmassice     = binFiles.read_3d_float(fileobj, ni, nj, nk)
    greflall     = binFiles.read_3d_float(fileobj, ni, nj, nk)

    # Unit change
    gmassi1    = gmassi1/1.e3
    gmassi2    = gmassi2/1.e3
    gmassi3    = gmassi3/1.e3

    gmass_crys = gmass_crys/1.e3
    gmasss     = gmasss/1.e3
    gmassg     = gmassg/1.e3
    gmassh     = gmassh/1.e3

    if (i == iframe):
       for ix in range(ni):
           for iy in range(nj):
               radar_top[ix,iy] = 0.
               color_top[ix,iy] = 0
               icloud_found = 0
               for iz in range(nk-1, -1, -1):
                   if (icloud_found == 0):
                      if (greflall[ix,iy,iz] > 0. ):
                         radar_top[ix,iy] = height[iz]
                         icloud_found = 1
               # find the color for surface showing strength of the core
               if (icloud_found > 0):
                  aa = greflall[ix,iy,1]
                  color_top[ix,iy] = aa

       aa_max = np.max(color_top)
       print "aa_max = ", aa_max
       if (aa_max > 0):
          color_top = color_top*256/aa_max
          color_top = color_top.astype(int)

       registerColormaps.register_own_cmaps()
       cmap = cm.get_cmap('wbr')

       X = np.arange(0,ni)
       Y = np.arange(0,nj)
       X, Y = np.meshgrid(X, Y)

       fig = plt.figure( )
       ax = Axes3D(fig)
       surf = ax.plot_surface(X, Y, radar_top, rstride=1, cstride=1, cmap=cmap, 
                      linewidth=0, antialiased=False)
       fig.colorbar(surf, shrink=0.5, aspect=5)
       plt.title('Radar reflectivity for Time Record %d'%(iframe))
       plt.savefig('radarReflectivityPlot.png')
       plt.show()
       break

fileobj.close()

