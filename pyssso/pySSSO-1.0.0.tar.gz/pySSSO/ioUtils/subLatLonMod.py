#!/usr/bin/env python

"""
  This module has the following functions:
   - sliceLatLon: extracting a slice of Lat/Lon indices.
   - ind_maxValues: indices where the maximal value of array occurs
   - ind_minValues: indices where the minimal value of array occurs
   - closest_point: return the index of the grid point closest to a provided value.
"""

#-------------
# Load modules
#-------------
import numpy as np                         # Numpy import

def sliceLatLon(lat, lon, (minLat,maxLat),(minLon,maxLon)):
    """
      Extracts a subset of Lat/Lon indices.
      Given lat & lon arrays of latitudes and longitudes, 
      we want to determine the arrays inxdex_lat and
      index_lon of indices where the latitudes and longitudes
      fall in the provided ranges ([minLat,maxLat] and [minLon,maxLon])

            lat[:]>=minLat and lat[:]<=maxLat
            lon[:]>=minLon and lon[:]<=maxLon

      indexLat, indexLon = sliceLatLon(lat, lon, (-45.0,45.0), (-90.0,90.0))
      tempSlice = temp[indexLat[0]:indexLat[-1]+1,indexLon[0]:indexLon[-1]+1]
    """
    indexLat = np.nonzero((lat[:]>=minLat) & (lat[:]<=maxLat))[0]
    indexLon = np.nonzero((lon[:]>=minLon) & (lon[:]<=maxLon))[0]
    return indexLat, indexLon

def ind_maxValues(myArray):
    """
      Returns the indices where the maximum value of myArray occurs
    """
    return np.where((myArray == (myArray.max())

def ind_minValues(myArray):
    """
      Returns the indices where the minimum value of myArray occurs
    """
    return np.where((myArray == (myArray.min())

def closest_point(myArray, val):
    """
      Returns the index i where myArray[i] is closest to val.
    """
    return  (np.abs(myArray - val)).argmin()


