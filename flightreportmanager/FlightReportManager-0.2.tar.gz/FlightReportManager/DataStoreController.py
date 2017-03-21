'''
Created on Jun 29, 2016

@author: johanneskinzig
'''

import sqlite3
import os

# TODO: possibly add sqlcipher component????

class DataStoreController():
    '''Handle the sqlite DataBase'''

    def __init__(self, sqlitedatafile):
        '''open sqlite db file'''
        self.sqlitedatafile = sqlitedatafile
        # check if file exists and set a flag
        if os.path.isfile(self.sqlitedatafile):
            db_exists = True
        else:
            db_exists = False
        # try to open the DB file; it will be opened when it exists, otherwise it will be created
        self.connectToDB()
        # only create tables if file_exists_flag == False
        if db_exists == False:
            self.createTable()
    
    def connectToDB(self):
        ''' Open sqlite datafile for CRUD operations
        '''
        try:
            self.connection = sqlite3.connect(self.sqlitedatafile)
            self.db_cursor = self.connection.cursor()
        except:
            print("Error reading/creating DB") # we need to be ready for python3
        
    def commitCloseDB(self):
        ''' Commit and close DB file
        '''
        # commit and close
        self.connection.commit()
        self.connection.close()
        
    def createTable(self):
        '''
        Create tables, only called when DB is  not existing yet
        '''
        print "Creating tables..."
        # Create table and columns for flight data
        self.db_cursor.execute('''CREATE TABLE `flights` (
        `FlightID`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        `event_name`    TEXT NOT NULL,
        `city_nearby`    TEXT,
        `pilot_location`    TEXT,
        `date_time`    TEXT,
        `total_distance`    REAL,
        `max_altitude`    REAL,
        `avg_speed`    REAL,
        `flight_duration`    REAL,
        `controller_type` TEXT,
        `drone_type`    TEXT,
        `battery_usage`    INTEGER,
        `raw_data_file_name`    TEXT NOT NULL UNIQUE
        );''')
        # commit and close
        self.commitCloseDB
        print "Done creating tables"
        
    
    def insertIntoTable(self, event_name, data_as_string):
        '''
        Insert new data into table
        (only performed when importing)
        '''
        self.connectToDB()
        self.db_cursor.execute("insert into flights (event_name, city_nearby, pilot_location, date_time, total_distance, max_altitude, avg_speed, flight_duration, controller_type, drone_type, battery_usage, raw_data_file_name) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (event_name, data_as_string[0].decode('utf-8'), data_as_string[1], data_as_string[2], data_as_string[3], data_as_string[4], data_as_string[5], data_as_string[6], data_as_string[7], data_as_string[8], data_as_string[9], data_as_string[10]))
        self.commitCloseDB()
        
    def updatRowNameInTable(self, flightid, new_name):
        '''
        Update name of flight in table
        '''
        self.connectToDB()
        self.db_cursor.execute("UPDATE flights SET event_name=? WHERE FlightID=?", (new_name, flightid))
        self.commitCloseDB()
        
    def deleteRowFromTable(self, flightid):
        '''
        Delete selected row from table
        '''
        self.connectToDB()
        self.db_cursor.execute("DELETE from flights WHERE FlightID=?", (flightid, ))
        self.commitCloseDB()
    
    def readDataFromTable(self):
        ''' Read whole data from table --> aim: display in GUI
        '''
        # connect to DB
        self.connectToDB()
        self.db_cursor.execute("SELECT * FROM flights")
        # get the rows!
        rows = self.db_cursor.fetchall()
        # close connection
        self.commitCloseDB()        
        return rows
    
    def getRowFromID(self, flightid):
        '''
        Returns the row for a given flight id
        '''
        # connect to DB
        self.connectToDB()
        self.db_cursor.execute("SELECT * FROM flights WHERE FlightID=?", (flightid, ))
        # get the row! -- only one row because FlightID is primary key and therefore unique
        row = self.db_cursor.fetchone()
        # close connection
        self.commitCloseDB()
        return row
        
            
if __name__ == '__main__':
    print "Init, start!"
    # generate test db
    mydb = DataStoreController('test-gui.db')
    
    #from DroneDataConversion import BebopFlightDataManager 
    
    #filepath = "DroneDataFiles/BebopThirdFlight_2016_06_26.json"
    #print("File: " + filepath)
    #testFlightManager = BebopFlightDataManager(filepath)
    #mydb.insertIntoTable(testFlightManager.diagnostic_information_raw())
    #print "Done writing Data to table"
    
    test = mydb.readDataFromTable()
    for row in test:
        print row
    
    mydb.updatRowNameInTable(1, "super1")