#!/usr/bin/env python

"""
Created on 17.06.2016

@author: johanneskinzig
"""

from Tkinter import *
import ttk
from tkFileDialog import askopenfilename, asksaveasfilename     
from DroneDataConversion import DroneDataConversion # now imported from site-packages because package is provided externally
import DataStoreController
import FileStorageController
import os
import Plotlib

class MainView():
    def __init__(self, master):
        ''' Setup Tkinter and all necessary properties.
            Generate instances of classes.
        '''
# TODO: from settings tab <- user can decide where to put the flight db
# TODO: use module which provides OS dependent user locations
        ################################################
        #   instances from other modules               #
        ################################################
        ## FileStorage Controller
        self.FileStorage = FileStorageController.FileStorageController("FlightReportManager", "JoKi", "0.1_alpha")
        print("Data directory: " + self.FileStorage.getDataDirectory())
        
        ## DataStoreController
        self.DataStore = DataStoreController.DataStoreController(self.FileStorage.getDBLocation())
    
        
        ################################################
        #   setup tkinter                              #
        ################################################
        master.title("FlightReportManager Bebop")
        master.resizable(width=False, height=False)
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        #master.geometry("600x320")
        
        ## not necessary, because I embed the ttk.Notebook inside master and then embed a ttk.Frame inside each Notebook
        ## but not deleting it from here because of educational purpose
        # mainWindow = ttk.Frame(master, padding="3 3 12 12")
        # mainWindow.grid(column=0, row=0, sticky=(N+E+W+S))

        ## place the widgets where they belong
        self.initialize_widgets(master)
        
        ## generate right click context menu
        self.generateTreeViewContextMenu(master)

        ## update view with data from DB
        self.updateDataInView()

    def initialize_widgets(self, master):
        '''Holds all the information necessary to place the widgets in the frame. Including callbacks and methods.
        '''
        tabbar = ttk.Notebook(master)
        flight_tab = ttk.Frame(tabbar)   # first page, which get widgets gridded into it
        import_tab = ttk.Frame(tabbar)   # second page
        settings_tab = ttk.Frame(tabbar)
        tabbar.add(flight_tab, text='Flights')
        tabbar.add(import_tab, text='Import')
        tabbar.add(settings_tab, text='Settings')
        tabbar.grid(row=0, column=0, sticky=(N+E+W+S))
        
    #####################################################################
    #         "Flights" tab Widgets                                     #
    #####################################################################
        
        ################################################
        #         TreeView for Flight data             #
        ################################################
        columns = ("event_name", "city_nearby", "pilot_location", "datetime", "total_distance", "max_altitude", "avg_speed", "flight_duration", "controller_type", "Drone_type", "battery_usage")
        self.flights_treeView = ttk.Treeview(flight_tab, columns=columns, selectmode='browse', height=15, padding=(0,0,0,0))
        self.flights_treeView.grid(row=0, column=0, rowspan = 5, columnspan = 4, sticky=N+S+W)

        #################################################
        #         Scrollbars for treeview               #
        #################################################
        vsb_treeview = ttk.Scrollbar(flight_tab, orient="vertical", command = self.flights_treeView.yview)
        hsb_treeview = ttk.Scrollbar(flight_tab, orient="horizontal", command = self.flights_treeView.xview)

        ## Link scrollbars activation to top-level object
        self.flights_treeView.configure(yscrollcommand=vsb_treeview.set, xscrollcommand=hsb_treeview.set)
        vsb_treeview.grid(row=0, column=4, rowspan = 5, sticky=(N+S))
        hsb_treeview.grid(row=5, column=0, columnspan = 4, sticky=(E+W))
        
        ## name treeview columns
        self.flights_treeView.heading("#0", text="FlightID")
        self.flights_treeView.column("#0", minwidth=50, width=50)
        
        self.flights_treeView.heading("event_name", text="Event Name")
        self.flights_treeView.heading("city_nearby", text="City nearby")
        self.flights_treeView.heading("pilot_location", text="Pilot Location")
        self.flights_treeView.heading("datetime", text="Time")
        self.flights_treeView.heading("total_distance", text="Distance (m)")
        self.flights_treeView.heading("max_altitude", text="max Alt. (m)")
        self.flights_treeView.heading("avg_speed", text="avg. Speed (m/s)")
        self.flights_treeView.heading("flight_duration", text="Duration (min)")
        self.flights_treeView.heading("controller_type", text="Controller Type")
        self.flights_treeView.heading("Drone_type", text="Drone Type")
        self.flights_treeView.heading("battery_usage", text="Battery Usage (%)")
        
        self.flights_treeView.column("event_name", minwidth=90, width=100)
        self.flights_treeView.column("city_nearby", minwidth=80, width=110)
        self.flights_treeView.column("pilot_location", minwidth=160, width=170, anchor=CENTER)
        self.flights_treeView.column("datetime", minwidth=120, width=165)
        self.flights_treeView.column("total_distance", minwidth=70, width=70, anchor=CENTER)
        self.flights_treeView.column("max_altitude", minwidth=70, width=70, anchor=CENTER)
        self.flights_treeView.column("avg_speed", minwidth=95, width=95)
        self.flights_treeView.column("flight_duration", minwidth=80, width=85)
        self.flights_treeView.column("controller_type", minwidth=105, width=105, anchor=CENTER)
        self.flights_treeView.column("Drone_type", minwidth=80, width=80)
        self.flights_treeView.column("battery_usage", minwidth=95, width=95)
        
        
        ################################################
        #         Buttons for flight management        #
        ################################################
        ttk.Button(flight_tab, text="Export gpx-Track", command=self.exportAsGPXInvocation, width = 12).grid(row=1, column = 5)
        ttk.Button(flight_tab, text="Export kml-Track", command=self.action, width = 12).grid(row=2, column = 5)
        ttk.Button(flight_tab, text="Export csv-Flight", command=self.exportAsCSVInvocation, width = 12).grid(row=3, column = 5)
        ttk.Button(flight_tab, text="Delete Flight", command=self.deleteRowInvocation, width = 12).grid(row=4, column = 5)
        
        ################################################
        #     Buttons for displaying flight data       #
        ################################################
        ttk.Button(flight_tab, text="Plot Track", command=self.plotTrackInvocation, width = 10).grid(row = 6, column = 0)
        ttk.Button(flight_tab, text="Plot Altitude", command=self.plotAltitudeInvocation, width = 10).grid(row = 6, column = 1)
        ttk.Button(flight_tab, text="Plot Speed", command=self.plotSpeedInovaction, width = 10).grid(row=6, column = 2)
        ttk.Button(flight_tab, text="Plot Battery", command=self.plotBatteryUsageInvocation, width = 10).grid(row = 6, column = 3)
        
    #####################################################################
    #         "Import" tab Widgets                                      #
    #####################################################################

        ################################################
        #    Label and Textfield to set event name     #
        ################################################
        ttk.Label(import_tab, text="Event Name: ").grid(column = 0, row = 0)
        self.event_name_entry = ttk.Entry(import_tab, width=30)
        self.event_name_entry.grid(column = 1, row= 0)
        
        ################################################
        # Label, Textentry, Button to get pud/json file#
        ################################################
        ttk.Label(import_tab, text="PUD/JSON File location: ").grid(column=0, row = 1, sticky = W)
        self.file_location_entry = ttk.Entry(import_tab, width=30)
        self.file_location_entry.grid(column = 1, row = 1)
        ttk.Button(import_tab, text = "Choose...", command=self.openFileChooser, width = 7).grid(column = 2, row = 1, sticky = E)
        
        ################################################
        # Label, Textfield, Button to import data      #
        ################################################
        ttk.Label(import_tab, text = "Import Log: ").grid(column = 0, row = 2, sticky = W)
        ttk.Button(import_tab, text = "Import", command = self.importInvocation, width = 7).grid(column = 2, row = 2, sticky = E)
        self.log_textfield = Text(import_tab, height=15)
        self.log_textfield.grid(column = 0, row = 3, columnspan = 3, sticky=EW)
        
        #################################################
        #        Scrollbars for log_textfield           #
        #################################################
        vsb_log = ttk.Scrollbar(import_tab, orient="vertical", command =  self.log_textfield.yview)
        hsb_log = ttk.Scrollbar(import_tab, orient="horizontal", command =  self.log_textfield.xview)
        
        ## Link scrollbars activation to top-level object
        self.log_textfield.configure(yscrollcommand=vsb_log.set, xscrollcommand=hsb_log.set)
        vsb_log.grid(row=3, column=4, rowspan = 1, sticky=N+S)
        hsb_log.grid(row=4, column=0, columnspan = 3, sticky=E+W)
    

    def generateTreeViewContextMenu(self, master):
        ''' Generate Menu which opens when right-clicking on treeview entry
        '''
        self.tv_cont_men = Menu(master, tearoff=0)
        #self.tv_cont_men.add_command(label="Export Takeoff gpx-Wpt", command=self.action)
        self.tv_cont_men.add_command(label="Export gpx-Track", command=self.exportAsGPXInvocation)
        self.tv_cont_men.add_separator()
        self.tv_cont_men.add_command(label="Edit", command=lambda: self.editRowWindowInvocation(master))
        self.tv_cont_men.add_command(label="Delete", command=self.deleteRowInvocation)
        self.tv_cont_men.add_separator()
        
        # bind action to mouse button
        self.flights_treeView.bind("<Button-2>", self.showTreeViewContextMenu)
    
    def showTreeViewContextMenu(self, event):
        ''' Show context menu and store selected row
        '''
        try:
            #self.tv_cont_men.selection = self.flights_treeView.set(self.flights_treeView.identify_row(event.y))
            self.tv_cont_men.selection = self.flights_treeView.item(self.flights_treeView.focus())
            self.tv_cont_men.post(event.x_root, event.y_root)
        finally:
            # release the grab (version 8.0 and higher only)
            self.tv_cont_men.grab_release()
    
        
    def editRowWindowInvocation(self, master):
        ''' Generate second Tkinter window, directly generate a ttk-Frame to have similar styles for all windows
        '''
        def editRowInvocation(window, flight_id, newName):
            ''' Actively edit the selected row (treeview) in DB
            '''
            # update
            self.DataStore.updatRowNameInTable(flight_id, str(newName.get()))
            # quit window
            window.destroy()
            self.updateDataInView()
# TODO: implement button for refreshing "nearby city"; in case of not being connected to the Internet, the string is -- service not available --; this can be fixed by implementing a button which is invocating the request again
        editNameWindowTL = Toplevel(master)
        editNameWindowTL.resizable(width=False, height=False)
        editNameWindowTL.title("Rename Flight")
        editNameWindowTL.minsize(60,30)
        editNameWindowFr = ttk.Frame(editNameWindowTL, padding="3 3 12 12")
        editNameWindowFr.grid(column=0, row=0, sticky=(N+E+W+S))
        ttk.Label(editNameWindowFr, text="New Name:").grid(column=0, row=0)
        newName = ttk.Entry(editNameWindowFr)
        newName.grid(column=1, row = 0, columnspan = 2)
        # get selected row --> used as primary key in DB
        flight_id = int(self.tv_cont_men.selection['text'])
        print("Selected Row --> Flight_ID: " + str(flight_id))
        # Buttons and their functions
        ttk.Button(editNameWindowFr, text="Cancel", command=editNameWindowTL.destroy).grid(column=1, row=1)
        ttk.Button(editNameWindowFr, text="Rename", command=lambda: editRowInvocation(editNameWindowTL, flight_id, newName)).grid(column=2, row=1)
    
    def deleteRowInvocation(self):
        ''' the procedures necessary to delete the row
        '''
# TODO: also delete file from puts when deleting from DB
        self.DataStore.deleteRowFromTable(int(self.flights_treeView.item(self.flights_treeView.focus())['text']))
        self.updateDataInView()
    
    def updateDataInView(self):
        '''Update data in GUI
        '''
        ## sample to see how treeview is filled with data 
        #self.flights_treeView.insert("", 0, "dir1", text="Dir 1", values=("1A","1b"))
        #self.flights_treeView.insert("", 1, "dir2", text="Dir 2", values=("2A","2b"))
        
        ## delete all fields
        self.flights_treeView.delete(*self.flights_treeView.get_children())
        ## and fill treeview with data
        data = self.DataStore.readDataFromTable()
        for data_set in data:
            # TODO: include in logger
            # print data_set
            # insert at next position
            #self.flights_treeView.insert("", int(data_set[0]), str(data_set[0]), text=str(data_set[0]), values=(data_set[1], data_set[2], data_set[3], data_set[4], data_set[5], data_set[6], data_set[7], data_set[8], data_set[9], data_set[10], data_set[11]))
            # insert at position 0 (= first row)
            self.flights_treeView.insert("", 0, str(data_set[0]), text=str(data_set[0]), values=(data_set[1], data_set[2], data_set[3], data_set[4], round(data_set[5], 2), data_set[6], round(data_set[7], 2), round(data_set[8], 2), data_set[9], data_set[10], data_set[11]))
    
    def importInvocation(self):
        ''' Get the user input for the "event_name_entry" and "file_location_entry" text entry field
            Store the data inside DB
        '''
        event_name_value = self.event_name_entry.get()
        file_location_value = self.file_location_entry.get()
        
# TODO: check if file is already existing
# TODO: include in log file
        print("EVENT NAME USER INPUT: " + event_name_value)
        print("PUD/JSON FILE LOCATION: " + file_location_value)
        
        ## copy pudfile to application data
        # extract filename from complete file path 
        pud_path, pud_name = os.path.split(file_location_value)
        self.raw_file_name = pud_name
        
        file_location_destination_value = self.FileStorage.getPudfileDataDirectory() + pud_name
        print("PUD/JSON FILE DESTINATION: " + file_location_destination_value)
        
        self.FileStorage.copyFileTo(file_location_value, file_location_destination_value)
        
        ## then parse it!
        ## generate instance of BebopFlightDataManager
        flightManager = DroneDataConversion.BebopFlightDataManager(file_location_destination_value)
        ## debug output for console
        flightManager.display_diagnostic_information_debug()
        ## import data into DB
        self.DataStore.insertIntoTable(event_name_value, flightManager.diagnostic_information_raw())
        ## clear log
        self.log_textfield.delete('1.0', END)
        ## and insert into log afterwards
        self.log_textfield.insert(END, ("\n".join(flightManager.display_diagnostic_information_debug())))
        ## refresh view which presents data
        self.updateDataInView()
    
    def openFileChooser(self):
        '''Open tkaskopenfilename and return filename/absolute filepath of user's selection
        '''
        # define file options
        file_options = {}
        file_options['defaultextension'] = '.json'
        file_options['filetypes'] = [('JSON Files', '.json'), ('PUD Files', '.pud')]
        file_options['title'] = "Choose Bebop's json/pud File..."
        
        # open file chooser dialog and get filename (just get the path, this is not an object of type file)
        filepath_absolute = askopenfilename(**file_options)
# TODO: include in log file
        print("FILENAME: " + filepath_absolute)
        # clear textfield before filling it again
        self.file_location_entry.delete(0, END)
        self.file_location_entry.insert(END, filepath_absolute)
    
    def getFilenameForSelectedItem(self):
        '''
        Makes a request to the DB and returns the location/filename for the selected item
        '''
        # get selected item
        flight_id = int(self.flights_treeView.item(self.flights_treeView.focus())['text'])
        # get filename of selected item
        # request from DB
        row = self.DataStore.getRowFromID(flight_id)
        print("PUD/JSON File for parsing: " + str(row[12]))
        file_location = self.FileStorage.getPudfileDataDirectory() + str(row[12])
        return str(file_location)
    
    def exportAsGPXInvocation(self):
        '''
        Export as GPX file invocation
        '''
        # generate instance of DroneDataConversion
        flightManager = DroneDataConversion.BebopFlightDataManager(self.getFilenameForSelectedItem())
        # ask filename to save to
        # define file options
        file_options = {}
        file_options['defaultextension'] = '.gpx'
        file_options['title'] = "Export GPX to ..."
        file_options['initialfile'] = 'FlightTrack.gpx'
        filename = asksaveasfilename(**file_options)
        # convert to gpx
        # adding track name to gpx is not working, don't know why
        flightManager.export_as_gpx(filename, gpx_track_name=str(os.path.basename(os.path.splitext(filename)[0])))
        print("Done")
        
    def exportTakeoffGpxWptInvocation(self):
        '''
        Export the takeoff location as gpx waypoint
        '''
# TODO: implement
        pass
    
    def exportAsKMLInvocation(self):
        '''
        Export as kml file invocation
        '''
        pass
        
    def exportAsCSVInvocation(self):
        '''
        Export as csv file invocation
        '''
                # generate instance of DroneDataConversion
        flightManager = DroneDataConversion.BebopFlightDataManager(self.getFilenameForSelectedItem())
        # ask filename to save to
        # define file options
        file_options = {}
        file_options['defaultextension'] = '.csv'
        file_options['title'] = "Export CSV to ..."
        file_options['initialfile'] = 'FlightTrack.csv'
        filename = asksaveasfilename(**file_options)
        # convert to gpx
        # adding track name to gpx is not working, don't know why
        flightManager.export_as_csv(filename)
        print("Done")
    
    
    def plotBatteryUsageInvocation(self):
        '''
        Invocation of battery plot
        '''
        ## plotting instance
        plot_flight = Plotlib.Plotlib(self.getFilenameForSelectedItem())
        plot_flight.plotBatteryUsage()
        
    def plotAltitudeInvocation(self):
        '''
        Invocation of altitude plot
        '''
        ## plotting instance
        plot_flight = Plotlib.Plotlib(self.getFilenameForSelectedItem())
        plot_flight.plotAltitude()
        
    def plotSpeedInovaction(self):
        '''
        Invocation of speed Plot
        '''
        ## plotting instance
        plot_flight = Plotlib.Plotlib(self.getFilenameForSelectedItem())
        plot_flight.plotSpeed()
        
    def plotTrackInvocation(self):
        '''
        Plot the flight track - experimental only!
        '''
        ## plot the flight gps track
        plot_flight = Plotlib.Plotlib(self.getFilenameForSelectedItem())
        plot_flight.plotTrack()
        
    
    def action(self):
        print "Not yet implemented"
        
if __name__ == '__main__':
    root = Tk()
    root.columnconfigure(0, weight=2)
    root.rowconfigure(0, weight=2)
    app=MainView(root)
    root.mainloop()