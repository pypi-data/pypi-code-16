'''
Created on 06.09.2016

@author: johanneskinzig
'''
import appdirs
import os
from shutil import copyfile

class FileStorageController():
    '''
    This class holds the information for storing the files on the local drives
    '''
    def __init__(self, application_name, application_author, application_version):
        '''
        Constructor
        '''
        ################################################
        #   Files and folders prefix                   #
        ################################################
        self.data_directory = appdirs.user_data_dir(application_name, application_author)
        self.sqlit_db_location = self.data_directory + "/FlightReportManager_DB.db"
        self.drone_logfile_prefix = self.data_directory + "/puds/"
        
        ## create data_directory if non exisiting
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)
            
        ## create drone logfile folder if non existing
        if not os.path.exists(self.drone_logfile_prefix):
            os.makedirs(self.drone_logfile_prefix)
    
    def getDBLocation(self):
        '''
        Return DB location
        '''
        return self.sqlit_db_location
    
    def getPudfileDataDirectory(self):
        '''
        Return user and system specfic data directory
        '''
        return self.drone_logfile_prefix
    
    def getDataDirectory(self):
        '''
        Return the main DataDirectory used by the application
        '''
        return self.data_directory
    
    def copyFileTo(self, source, destination):
        '''
        Copy the selected file to the puds folder
        '''
        copyfile(source, destination)
        print("Copied file to " + destination)
        
if __name__ == '__main__':
    myStorage = FileStorageController("FlightReportManager", "kinzig", "0.1.alpha")
    print myStorage.getDataDirectory()
    print myStorage.getDBLocation()
    

    
    