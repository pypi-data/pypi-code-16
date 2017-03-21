'''
Created on 20.03.2017

@author: johanneskinzig

@description: Use geoplotlib to plot the flight on a map
'''
from DroneDataConversion import DroneDataConversion

class PlotGPSTrack():
    '''Plot the flight track on a map - plot as a static track'''
    def __init__(self, pud_file):
        '''
        Get instances and prepare vars
        '''        
        ## normal control flow
        # get instance
        flightDataProvider = DroneDataConversion.BebopFlightDataManager(pud_file)
        # store data
        self.sec, self.lat, self.lon, self.alt, self.spe, self.bat = flightDataProvider.passFlightData()
    
    def prepareDataFrame(self):
        '''Put data into dictionary; then geoplotlib is able to draw it onto the map'''
        track_dataframe = {"lat" : self.lat, "lon" : self.lon, "name" : self.sec}
        return track_dataframe
    
    def plotTrackOnMap(self):
        '''Plot the track onto the map - engine is based on pyglet - right now it is just a point cloud'''
        import geoplotlib
        geoplotlib.dot(self.prepareDataFrame())
        geoplotlib.show()
        
        
    def plotTrackOnMap_MP(self):
        '''Do the same like PlotTrackOnMap but do it as a separate process. Recommended when calling the method from another GUI library.'''
        from multiprocessing import Process
        nproc = Process(target=self.plotTrackOnMap())
        nproc.start()

#class ReflyTrack():
'''Replay/Refly flight on map'''
    
    
if __name__ == '__main__':
    print "Hi"
    myflight = PlotGPSTrack("../../DroneDataConversion/DroneDataFiles/BebopTenthFlight_2016_12_10.json")
    myflight.plotTrackOnMap()