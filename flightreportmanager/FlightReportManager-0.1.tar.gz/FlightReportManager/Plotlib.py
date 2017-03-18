'''
Created on 08.09.2016

@author: johanneskinzig
'''

from DroneDataConversion import DroneDataConversion
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


class Plotlib():
    '''
    Uses matplotlib to plot the necessary graphs
    '''

    def __init__(self, pud_file):
        '''
        Get instances and prepare vars
        '''        
        ## normal control flow
        # get instance
        flightDataProvider = DroneDataConversion.BebopFlightDataManager(pud_file)
        # store data
        self.sec, self.lat, self.lon, self.alt, self.spe, self.bat = flightDataProvider.passFlightData()
        
    def plotBatteryUsage(self):
        '''
        Plot battery usage against time
        '''
        battery_plt = plt
        fig_bat = battery_plt.figure("Battery Usage")
        battery_plt.title('Battery Usage (%)')
        battery_plot = fig_bat.add_subplot(111)
        battery_plot.plot(self.sec, self.bat, color='#A901DB', linewidth=2.0)
        battery_plot.set_xlabel('Time (ms)')
        battery_plot.set_ylabel('Battery Usage (%)')
        battery_plt.show(block=False)
        
    def plotAltitude(self):
        '''
        Plot altitude against time
        '''
        altitude_plt = plt
        fig_alt = altitude_plt.figure('Altitude (m)')
        plt.title('Altitude (m)')
        altitude_plot = fig_alt.add_subplot(111)
        altitude_plot.plot(self.sec, self.alt, color='#00BFFF', linewidth=2.0)
        altitude_plot.set_xlabel('Time (ms)')
        altitude_plot.set_ylabel('Altitude (m)')
        plt.show(block=False)
    
    def plotSpeed(self):
        '''
        Plot speed against time
        '''
        speed_plt = plt
        fig_speed = speed_plt.figure('Speed (m/s)')
        speed_plt.title('Speed (m/s)')
        speed_plot = fig_speed.add_subplot(111)
        speed_plot.plot(self.sec, self.spe, color='#01DFA5', linewidth=2.0)
        speed_plot.set_xlabel('Time (ms)')
        speed_plot.set_ylabel('Speed (m/s)')
        speed_plt.show(block=False)
        
    def plotTrack(self):
        '''
        Plot Track -- experimental only
        '''
        track_plt = plt
        fig_track = track_plt.figure('Track, lat against lon')
        track_plt.title('Track, lat against lon')
        track_plot = fig_track.add_subplot(111)
        track_plot.plot(self.lon, self.lat, color='#01DFA5', linewidth=2.0)
        track_plot.set_xlabel('lon')
        track_plot.set_ylabel('lat')
        track_plt.show(block=False)
        
if __name__ == "__main__":
    filepath = "DroneDataFiles/BebopFourthFlight_2016_08_01.json"
    print("File: " + filepath)
    plot_data = Plotlib(filepath)
    plot_data.plotAltitude()
    plot_data.plotBatteryUsage()
    plot_data.plotSpeed()
    plot_data.plotTrack()