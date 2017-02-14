#################################
# credentials.py
# handles gspread credentials
# and returns/generates databases
#################################

# imports
import gspread
import json
from sheet import Sheet
from database import Database
from errors import *
from functions import *
from oauth2client.service_account import ServiceAccountCredentials \
    as OAuthCreds

# main class
class Credentials(object):

    ## constructor
    ### needs a path to a keyfile
    ### (Google service account JSON file)
    def __init__(self, keyfile):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive'] 
                # allows creation of new sheets
        credentials = OAuthCreds.from_json_keyfile_name(keyfile, scope)
        self.__client = gspread.authorize(credentials)

    ## client
    ### retrieves gspread client
    ### ensures client isn't expired
    @property
    def client(self):
        if (self.__client.auth.access_token_expired):
            self.__client.login()
        return self.__client

    ## fetchDatabase
    ### retrieves a database given a title (str)
    ### returns a Database object
    ### optionally checks format 
    ### (raising a DataError if sheet is not a proper database)
    @updateClient
    def fetchDatabase(self, title, checkFormat=True):
        sheet = Sheet(self.client.open(title))
        return Database(sheet, reformat=(not checkFormat))

    ## getDatabase
    ### retrieves a database given a key (str)
    ### returns a Database object
    ### optionally checks format
    ### (raising a DataError if sheet is not a proper database)
    @updateClient
    def getDatabase(self, key, checkFormat=True):
        sheet = Sheet(self.client.open_by_key(key))
        return Database(sheet, reformat=(not checkFormat))

    ## getDatabaseFromURL
    ### retrieves a database given a URL (str)
    ### returns a Database object
    ### optionally checks format
    ### (raising a DataError if sheet is not a proper database)
    @updateClient
    def getDatabaseFromURL(self, URL, checkFormat=True):
        sheet = Sheet(self.client.open_by_URL(URL))
        return Database(sheet, reformat=(not checkFormat))

    ## getAllDatabases
    ### returns all databases this client has access to
    ### optional param checkFormat (default True)
    ### only returns databases that are properly formatted
    @updateClient
    def getAllDatabases(self, checkFormat=True):
        allSheets = [Sheet(obj) for obj in self.client.openall()]
        results = list()
        for sheet in allSheets:
            try:
                db = Database(sheet, reformat=(not checkFormat))
            except DataError:
                continue
            except:
                raise
            else:
                results.append(db)
        return results

    ## deleteDatabase
    ### given a key, deletes a database
    @updateClient
    def deleteDatabase(self, key):
        db = self.getDatabase(key)
        db.delete()

    ## deleteDatabaseFromURL
    ### given a URL, deletes a database
    @updateClient
    def deleteDatabaseFromURL(self, URL):
        db = self.getDatabaseFromURL(URL)
        db.delete()

    ## wipeDatabase
    ### given a title, deletes a database
    @updateClient
    def wipeDatabase(self, title):
        db = self.fetchDatabase(title)
        db.delete()

    ## createDatabase
    ### given a title, makes a new database
    @updateClient
    def createDatabase(self, title):
        sheet = Sheet(self.client.create(title))
        return Database(sheet)