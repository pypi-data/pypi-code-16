#!/usr/bin/env python

"""
    - Read an ASCII file containing the latitudes, longitudes and
      city names of various locations over the globe
    - Construct lists of latitudes, longitudes and city names
    - Using the latitide/longitude data, plot on a map all the locations
      over the selected area only
    - Interactively display the city names over the same map.
    """

#-----------------
# Load the modules
#-----------------
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

import matplotlib.pyplot as plt           # pyplot module import
from mpl_toolkits.basemap import Basemap  # basemap import
import numpy as np                        # Numpy import

class stationMap:
    def __init__(self, stationFile, area=None, plotTitle=None, mapBackgd='Standard'):
        
        # ASCII file name containing the stations (lat/lon/name)
        self.stationFile = stationFile
        
        if (area == None):
           self.area = 'Globle'
        else:
           self.area = area
        
        if (plotTitle == None):
            self.plotTitle = "Plotting stations over " + self.area
        else:
            self.plotTitle   = plotTitle

        self.mapBackground = mapBackgd

        # Set the domain boundary
        #------------------------
        self.set_boundaries()

        # Initialize the stations information
        self.stations = []
        self.lat      = []
        self.lon      = []
    
        # Read all the stations information
        #----------------------------------
        self.get_stations()

        # Select the stations that are in the provided area
        #--------------------------------------------------
        self.select_stations()

        # Map the stations
        #-----------------
        self.map_stations()

    def set_boundaries(self):
        """
          Set the boundaries of the selected region:
             l_lat: lower latitude
             u_lat: upper latitude
             l_lon: lower longitude
             u_lon: upper longitude
             
          The regions include:
             * 'Globe': the entire globe
             * 'US':    United States
             * 'North America'
             * 'Central America'
             * 'South America'
             * 'Asia'
             * 'Europe'
             * 'Africa'
             * 'Australia/Oceania'
        """
        if (self.area == 'Globe'):
           print "You selected to plot stations over the entire %s" %(self.area)
           self.l_lat = - 90.0
           self.u_lat =   90.0
           self.l_lon = -180.0
           self.u_lon =  180.0
        elif (self.area == 'US'):
           print "You selected to plot stations in %s" %(self.area)
           self.l_lat =   24.0
           self.u_lat =   51.0
           self.l_lon = -130.0
           self.u_lon = - 65.0
        elif (self.area == 'North America'):
            print "You selected to plot stations in %s" %(self.area)
            self.l_lat =    8.0
            self.u_lat =   83.0
            self.l_lon = -170.0
            self.u_lon = - 53.0
        elif (self.area == 'South America'):
            print "You selected to plot stations in %s" %(self.area)
            self.l_lat = -58.0
            self.u_lat =   8.0
            self.l_lon = -90.0
            self.u_lon = -32.0
        elif (self.area == 'Central America'):
            print "You selected to plot stations in %s" %(self.area)
            self.l_lat =   6.0
            self.u_lat =  20.0
            self.l_lon = -93.0
            self.u_lon = -77.0
        elif (self.area == 'Africa'):
           print "You selected to plot stations in %s" %(self.area)
           self.l_lat = -34.80
           self.u_lat =  37.33
           self.l_lon = -17.50
           self.u_lon =  51.45
        elif (self.area == 'Europe'):
           print "You selected to plot stations in %s" %(self.area)
           self.l_lat =  30.0
           self.u_lat =  72.0
           self.l_lon = -30.00
           self.u_lon =  60.00
        elif (self.area == 'Asia'):
           print "You selected to plot stations in %s" %(self.area)
           self.l_lat = - 12.0
           self.u_lat =   75.0
           self.l_lon =   28.00
           self.u_lon =  160.00
        elif (self.area == 'Australia/Oceania'):
           print "You selected to plot stations in %s" %(self.area)
           # Here the longitudes are from 0 to 360
           self.l_lat = - 54.0
           self.u_lat =   12.0
           self.l_lon =  105.00
           self.u_lon = 360.0-108.00 # no negative longitude

    def get_stations(self):
        """
            Open the station file and store the station data
            (lat, lon and name) into lists.
        """
        f = open(self.stationFile, 'r')

        for line in f:
            if (line[0] == "#"):
               pass
            else:
                # get rid of the \n character
               line             = line.strip()
               # split the line into a list
               columns          = line.split(None, 3)

               self.lat.append(float(columns[1]))
               self.lon.append(float(columns[2]))
               self.stations.append(columns[3])

        f.close()
    

    def select_stations(self):
        """
            Only consider the stations over the selected area.
        """
        names = []
        lat   = []
        lon   = []

        for i in range(len(self.lat)):
            if (self.area == 'Australia/Oceania'):
               if (self.lon[i] < 0.0):
                  self.lon[i] = 360.0 + self.lon[i]

            if ((self.lat[i] > self.l_lat) and
                (self.lat[i] < self.u_lat) and
                (self.lon[i] > self.l_lon) and
                (self.lon[i] < self.u_lon)):
               names.append(self.stations[i])
               lat.append(self.lat[i])
               lon.append(self.lon[i])
        
        self.lon = lon
        self.lat = lat
        self.stations = names
        
        print "%d Stations will be plotted over %s" %(len(self.stations), self.area)
        
        names = []
        lat   = []
        lon   = []
        
        #self.stations = ['Aberdeen Md', 'New York', 'Washington DC',
        #           'Los Angeles', 'Chicago', 'Austin Tx', 'Atlanta Ga']
        #self.lat = [39.516666, 40.716667, 38.90000, 34.6666,
        #        41.95, 30.283, 33.7500]
        #self.lon = [-76.16666, -74.00000, -77.0333, -118.25,
        #        -87.63, -97.75, -84.383]

    def map_stations(self):
        """
            Plot the stations over the selected area.
        """
        
        import annoteFinderClass
        
        self.figure = plt.figure()
        self.axes = self.figure.add_axes([0,0,1,1],frameon=False)
    
        self.m = Basemap(projection='mill',
                    llcrnrlat=self.l_lat,
                    urcrnrlat=self.u_lat,
                    llcrnrlon=self.l_lon,
                    urcrnrlon=self.u_lon )

        self.m.drawcoastlines(linewidth=0.25)
        self.m.drawcountries(linewidth=0.25)
        if ((self.area == 'US') or (self.area == 'North America')):
           self.m.drawstates()

        # Set the map background
        self.set_map_background()

        # map station coordinates to map coordinates
        #-------------------------------------------
        x, y = self.m(self.lon, self.lat)

        # convert back to lat/lon
        lonpt, latpt = self.m(x,y,inverse=True)
        
        # Draw a red dot at station coordinates
        #--------------------------------------
        plt.plot(x, y, 'ro')
        plt.title(self.plotTitle)

        af = annoteFinderClass.AnnoteFinder(x,y, self.stations)
        plt.connect('button_release_event', af)
        #plt.connect('button_press_event', af)

        #plt.savefig('fig_stationsOverMap.png')
        plt.show()

    def set_map_background(self):
        """
          Select the map background:
           - Standard:
           - Land-Sea Mask:         land-sea mask as image
           - Blue Marble:           blue marble image
           - Shade Relief:          shaded relief image
           - Etopo:                 etopo image 
           - Etopo & Land-Sea Mask: etopo image through land
        """

        if (self.mapBackground == 'Standard'):
           self.m.drawmapboundary(fill_color='aqua')
           self.m.fillcontinents(color='white',lake_color='aqua')
        elif (self.mapBackground == 'Land-Sea Mask'):
           self.m.drawmapboundary()
           self.m.drawlsmask(ocean_color='aqua',land_color='coral', lakes=True)
        elif (self.mapBackground == 'Blue Marble'):
           self.m.drawmapboundary()
           self.m.bluemarble()
        elif (self.mapBackground == 'Shaded Relief'):
           self.m.drawmapboundary()
           self.m.shadedrelief()
        elif (self.mapBackground == 'Etopo'):
           self.m.drawmapboundary()
           self.m.etopo()
        elif (self.mapBackground == 'Etopo & Land-Sea Mask'):
           # use etopo image as map background overlaid with
           # land-sea mask image where land areas are transparent 
           # (so etopo image shows through over land).
           self.m.drawmapboundary()
           self.m.etopo()
           self.m.drawlsmask(ocean_color='DarkBlue',land_color=(255,255,255,1))


if __name__ == '__main__':
   myMap = stationMap('colDiagStationList.asc', area='US')


