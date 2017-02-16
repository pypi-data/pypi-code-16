##############################
# sheet.py
# handles a whole spreadsheet
##############################

from functions import *
from errors import *
from worksheet import Worksheet
import gspread

# main class
class Sheet(object):

    ## constructor
    ### takes a gspread Spreadsheet object
    def __init__(self, sheet):
        self._sheet = sheet

    ## built-in methods

    ## equality check
    ### uses sheet ID
    def __eq__(self, other):
        return (isinstance(other, Sheet) and 
                self.sheet.id == other.sheet.id)

    ## hash function
    ### uses sheet ID
    def __hash__(self):
        return hash(self.sheet.id)

    ## read operations

    ## client
    ### returns the client
    @property
    def client(self):
        if self.sheet.client.auth.access_token_expired:
            self.sheet.client.login()
        return self.sheet.client

    ## sheet
    ### returns the sheet
    @property
    def sheet(self):
        return self._sheet

    ## fetchWorksheet
    ### fetches a worksheet as a Worksheet object
    ### given its index within the Spreadsheet
    @updateClient
    def fetchWorksheet(self, index):
        return Worksheet(self.sheet.get_worksheet(index))

    ## getWorksheet
    ### fetches a worksheet given its title
    @updateClient
    def getWorksheet(self, title):
        return Worksheet(self.sheet.worksheet(title))

    ## getWorksheets
    ### fetches all worksheets in the sheet
    @updateClient
    def getWorksheets(self):
        return [Worksheet(worksheet) for worksheet
                in self.sheet.worksheets()]

    ## getWorksheetTitles
    ### fetches all worksheet titles in the sheet
    @updateClient
    def getWorksheetTitles(self):
        return [worksheet.title for worksheet in
                self.sheet.worksheets()]

    ## firstSheet
    ### fetches sheet at index 0
    @property
    def firstSheet(self):
        return Worksheet(self.sheet.sheet1)

    ## ID
    ### returns spreadsheet ID
    @property
    def ID(self):
        return self.sheet.id

    ## updateTime
    ### returns (RFC 3339) latest update time
    @property
    def updateTime(self):
        return self.sheet.updated

    ## title
    ### returns the spreadsheet title
    @property
    def title(self):
        return self.sheet.title

    ## permissions
    ### returns all spreadsheet permissions
    ### as a list of dictionaries
    @property
    @updateClient
    def permissions(self):
        return self.sheet.list_permissions()

    ## fetchRole
    ### fetches role belonging to a specified
    ### value (string) corresponding to an attribute (string)
    ### returns role string or None if user
    ### has no role in this spreadsheet
    ### if the user has no specified role
    ### but 'anyone' has a role, then
    ### the 'anyone' role is returned
    @updateClient
    def fetchRole(self, attribute, value):
        permissions = self.permissions
        applicable = [perm for perm in permissions if attribute
                      in perm and perm[attribute] == value]
        if (len(applicable) == 0):
            if (attribute == "id" and value == "anyone"):
                return None
            elif (attribute == "id" and value == "anyoneWithLink"):
                return self.fetchRole(attribute="id",
                                      value="anyone")
            else:
                return self.fetchRole(attribute="id",
                                      value="anyoneWithLink")
        return applicable[0]['role']

    ## fetchRoles
    ### given attribute-value pairs (as a list of tuples)
    ### returns a dictionary of attribute/value-role pairs
    @updateClient
    def fetchRoles(self, matchList):
        results = list()
        for item in matchList:
            attribute = item[0]
            value = item[1]
            role = self.fetchRole(attribute, value)
            result = dict()
            result[attribute] = value
            result['role'] = role
            results.append(result)
        return results

    ## write operations

    ## wipePermissions
    ### removes all permissions associated with a given value
    ### value is typically an e-mail address
    @updateClient
    def wipePermissions(self, value):
        self.sheet.remove_permissions(value)

    ## addPermissions
    ### gives a user a new role
    ### needs a value (typically an e-mail address),
    ### None if you want to adjust the default setting
    ### a perm ('user' (default), 'group', 'domain', 'anyone')
    ### a role to set ('owner', 'writer' (default), 'reader')
    ### whether to notify (default True)
    ### email message to send them if notified (default None)
    @updateClient
    def addPermissions(self, value, perm='user', role='writer',
                       notify=True, message=None):
        self.sheet.share(value, perm, role, notify, message)

    ## setDefaultRole
    ### sets the default role for the spreadsheet
    ### just needs the role (default 'reader')
    ### and whether a link is needed (default False)
    @updateClient
    def setDefaultRole(self, role='reader', link=False):
        if role is None:
            self.wipePermissions(None)
        elif link:
            self.addPermissions('anyoneWithLink', perm='anyone', 
                                 role=role, notify=False)
        else:
            self.addPermissions(None, perm='anyone', role=role,
                                notify=False)

    ## swapPermissions
    ### gives a user a new role
    ### needs their value (typically e-mail)
    ### and a new role to assign them to ('owner', 'writer', 'reader')
    @updateClient
    def swapPermissions(self, value, newRole):
        permissions = self.sheet.list_permissions()
        existing = [perm for perm in permissions if 
                   (('id' in perm and perm['id'] == value) or
                   ('emailAddress' in perm and perm['emailAddress']
                    == value))]
        if len(existing) == 0:
            raise SheetError("No permissions associated with this value!: " + value)
        permission = existing[0]
        perm_type = permission['type']
        self.wipePermissions(value)
        self.addPermissions(value, perm=perm_type, role=newRole)

    ## wipeAllPermissions
    ### wipes all non-owner permissions related to the sheet
    @updateClient
    def wipeAllPermissions(self):
        self.setDefaultRole(None)
        permissions = self.sheet.list_permissions()
        for permission in permissions:
            if permission['role'] == 'owner': continue # spare owner
            elif 'emailAddress' in permission:
                self.wipePermissions(permission['emailAddress'])
            else:
                self.wipePermissions(permission['id'])

    ## wipeOwnPermissions
    ### wipes own permissions
    ### only do this if you don't need any further access
    @updateClient
    def wipeOwnPermissions(self):
        ownEmail = self.client.auth._service_account_email
        self.wipePermissions(ownEmail)

    ## importCSV
    ### imports a CSV to the first worksheet
    @updateClient
    def importCSV(self, CSV):
        self.client.import_csv(self.ID, CSV)

    ## importCSVFromFile
    ### imports a CSV to the first worksheet
    ### given a file
    @updateClient
    def importCSVFromFile(self, CSVFile):
        with open(CSVFile, "rt") as fin:
            CSV = fin.read()
        self.importCSV(CSV)

    ## createWorksheet
    ### creates a new worksheet
    ### given a title (string) and specified size
    ### in terms of rows (int) and cols (int)
    ### default is 26 cols by 1000 rows
    @updateClient
    def createWorksheet(self, title, rows=1000, cols=26):
        return Worksheet(self.sheet.add_worksheet(title, rows, cols))

    ## wipeWorksheet
    ### given an index,
    ### deletes a worksheet
    @updateClient
    def wipeWorksheet(self, index):
        worksheet = self.fetchWorksheet(index)
        worksheet.delete()

    ## deleteWorksheet
    ### given a title,
    ### deletes a worksheet
    @updateClient
    def deleteWorksheet(self, title):
        worksheet = self.getWorksheet(title)
        worksheet.delete()

    ## delete
    ### deletes the spreadsheet
    @updateClient
    def delete(self):
        self.client.del_spreadsheet(self.ID)