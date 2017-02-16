###################################
# database.py
# handles a database, using a sheet
###################################

import constants
from gspread import WorksheetNotFound
from errors import *
from functions import *
from worksheet import Worksheet
from sheet import Sheet
from table import Table

class Database(object):

    # main Database class
    ## takes spreadsheet 
    ## (Sheet object)
    ## optional: reformat (bool, default True)
    ## formats the database if it isn't properly formatted
    def __init__(self, spreadsheet, reformat=True):
        self.constants = None
        self._constantsTitle = constants.constantsTitle
        self._constantHeader = constants.constantHeader
        self._sheet = spreadsheet
        if (self._constantsTitle not in self._sheet.getWorksheetTitles()):
            if reformat:
                cnst = self._sheet.createWorksheet(self._constantsTitle, cols=2,
                                                   rows=2)
                cnst.fillRow(1, self._constantHeader)
                cnstID = cnst.ID
                cnst.fillRow(2, [cnstID + "_HEADER", 1])
            else:
                raise DataError("Not a database!")
        self.constantsSheet = self._sheet.getWorksheet(self._constantsTitle)
        self.constants = Table(self.constantsSheet, self)

    ## sheet
    ### fetches the sheet
    @property
    def sheet(self):
        return self._sheet

    ## fetchConstant
    ### fetches a named constant
    ### returns None if the constant doesn't exist
    def fetchConstant(self, label):
        if (self.constants is None):
            return self._fetchConstantFromSheet(label)
        match = dict()
        match[self._constantHeader[0]] = {'value': label,
                                         'type': 'positive'}
        matching = self.constants.findValue(match, 
                   self._constantHeader[1])
        if len(matching) == 0:
            return ["",]
        return matching[0].split(",") # returns first instance

    ## _fetchConstantFromSheet
    ### fetches constant using constants Worksheet instead of Table
    ### (necessary when creating the constants Table
    ### to avoid a circular reference)
    def _fetchConstantFromSheet(self, label):
        labelName = self._constantHeader[0]
        valueName = self._constantHeader[1]
        labelCol = self.constantsSheet.findAll(labelName)[0][1]
        valueCol = self.constantsSheet.findAll(valueName)[0][1]
        labels = self.constantsSheet.getCol(labelCol)
        values = self.constantsSheet.getCol(valueCol)
        if label in labels:
            index = labels.index(label)
            return values[index].split(",")
        else:
            return ["",]

    ## setConstant
    ### sets a named constant
    ### given a label and its corresponding value
    def setConstant(self, label, value):
        if isinstance(value, list):
            self.setConstantList(label, value)
            return
        match = dict()
        match[self._constantHeader[0]] = {'value': label, 
                                         'type': 'positive'}
        matching = self.constants.findEntityRows(match)
        setDict = dict()
        setDict[self._constantHeader[1]] = value
        if len(matching) > 0:
            for row in matching:
                if value is None:
                    self.constants.removeEntity(row)
                else:
                    self.constants.updateEntity(setDict, row)
        else:
            setDict[self._constantHeader[0]] = label
            self.constants.addEntity(setDict)

    ## addToConstantList
    ### adds a constant to a named list
    def addToConstantList(self, label, value):
        if value is None: return
        old = self.fetchConstant(label)
        new = old + "," + value
        self.setConstant(label, new)

    ## setConstantList
    ### sets a list to a constant
    def setConstantList(self, label, value):
        value = ','.join([str(i) for i in value])
        self.setConstant(label, value)

    ## removeFromConstantList
    ### removes a constant from a named list
    def removeFromConstantList(self, label, value):
        if value is None: return
        old = self.fetchConstant(label).split(",")
        while str(value) in old:
            old.remove(str(value))
        new = ",".join(old)
        self.setConstant(label, new)

    ## removeConstant
    ### removes all constants with a given label
    def removeConstant(self, label):
        match = dict()
        match[self._constantHeader[0]] = {'value': label,
                                         'type': "positive"}
        self.constants.removeMatchingEntities(match)

    ## isRecognized
    ### returns True if a table with a ID is recognized
    def isRecognized(self, ID):
        headerTitle = ID + "_HEADER"
        return (self.fetchConstant(headerTitle) != ["",])

    ## tableExists
    ### returns True if a Table exists with a given title
    ### getUnrecognized (optional, default False):
    ### whether to acknowledge unrecognized tables
    def tableExists(self, title, getUnrecognized=False):
        try:
            worksheet = self.sheet.getWorksheet(title)
            if getUnrecognized: return True
            else:
                return self.isRecognized(worksheet.ID)
        except WorksheetNotFound:
            return False

    ## _getSheets
    ### retrieves worksheets
    def _getSheets(self):
        return self.sheet.getWorksheets()

    ## getTables
    ### retrieves all recognized tables
    ### getAll (optional, default False): 
    ### etrieve non-recognized Tables
    def getTables(self, getAll=False):
        results = dict()
        worksheets = self._getSheets()
        for worksheet in worksheets:
            if getAll or self.isRecognized(worksheet.ID):
                results[worksheet.title] = Table(worksheet, self)
        return results

    ## getTable
    ### returns a Table given a title (str)
    def getTable(self, title):
        return Table(self.sheet.getWorksheet(title),
                     self)

    ## createTable
    ### creates and returns a new table
    ### given a title (string),
    ### a header (list, default empty),
    ### and some initial entries (list of dicts, default empty)
    def createTable(self, title, header=list(), constraints=list(),
                    entities=list()):
        worksheet = self.sheet.createWorksheet(title, rows=1, 
                                 cols=max(1, len(header)))
        table = Table(worksheet, self)
        table.setHeaderLabels(*header)
        table.setConstraints(*constraints)
        for entity in entities:
            table.addEntity(entity)
        return table

    ## recognizeTable
    ### recognizes an existing sheet as a table
    ### and returns said table
    ### given a title (string),
    ### a header row number (int, default 1),
    ### a ref row number (int, default "" [no ref row]),
    ### and lists of ignored rows/columns (default empty)
    def recognizeTable(self, title, headerRow=1, refRow="",
                       ignoredRows=list(), ignoredCols=list()):
        if refRow is None: refRow = ""
        sheet = self.sheet.getWorksheet(title)
        self.setConstant(sheet.ID + "_HEADER", headerRow)
        self.setConstant(sheet.ID + "_REFROW", refRow)
        self.setConstant(sheet.ID + "_IGNOREDROWS", ignoredRows)
        self.setConstant(sheet.ID + "_IGNOREDCOLS", ignoredCols)
        return Table(sheet, self)

    ## fetchTable
    ### gets, recognizes, or retrieves table
    ### PARAMS: see getTable, createTable, recognizeTable
    def fetchTable(self, title, headerRow=1, refRow="",
                   ignoredRows=list(), ignoredCols=list(),
                   header=list(), constraints=list(),
                   entities=list()):
        try:
            worksheet = self.sheet.getWorksheet(title)
            if self.isRecognized(worksheet.ID):
                return Table(worksheet, self)
            else:
                return self.recognizeTable(title, headerRow, refRow,
                                           ignoredRows, ignoredCols)
        except WorksheetNotFound:
            return self.createTable(title, header, constraints, entities)

    ## removeTable
    ### given a title, removes a table
    def removeTable(self, title):
        table = Table(self.sheet.getWorksheet(title),
                      self)
        table.delete()

    ## delete
    ### deletes self
    def delete(self):
        self.sheet.delete()
