##########################
# worksheet.py
# handles single worksheet
##########################

from functions import *
from errors import *
import gspread

# main class
class Worksheet(object):

    ## constructor
    ### takes a gspread worksheet objecect
    def __init__(self, worksheet):
        self._sheet = worksheet

    ## built-in methods

    ## equality check
    ### uses sheet id
    def __eq__(self, other):
        return (isinstance(other, Worksheet) and
                self.sheet.id == other.sheet.id)

    ## hash function
    ### uses sheet id
    def __hash__(self):
        return hash(self.sheet.id)

    ## read operations

    ## colCount
    ### teturns (int) number of columns
    ### note that this is the length of any given row
    @property
    def colCount(self):
        return self.sheet.col_count

    ## rowCount
    ### returns (int) number of rows
    ### note that this is the length of any given col
    @property
    def rowCount(self):
        return self.sheet.row_count

    ## title
    ### returns (string) sheet title
    @property
    def title(self):
        return self.sheet.title

    ## ID
    ### returns (string) sheet ID
    @property
    def ID(self):
        return self.sheet.id

    ## updateTime
    ### returns RFC 3339 latest update time
    @property
    def updateTime(self):
        return self.sheet.updated

    ## client
    ### returns gspread Client object
    @property
    def client(self):
        if self.sheet.client.auth.access_token_expired:
            self.sheet.client.login()
        return self.sheet.client

    ## sheet
    ### returns gspread Worksheet object
    @property
    def sheet(self):
        return self._sheet

    ## getRow
    ### returns a list of values (str) in a given row (int)
    @updateClient
    def getRow(self, row):
        if (row > 0 and row <= self.rowCount):
            return self.sheet.row_values(row)
        else:
            raise SheetError("Nonexistent row!")

    ## getCol
    ### returns a list of values (str) in a given col (int)
    @updateClient
    def getCol(self, col):
        if (col > 0 and col <= self.colCount):
            return self.sheet.col_values(col)
        else:
            raise SheetError("Nonexistent column!")

    ## getRawRow
    ### returns a list of raw values (str) in a given row (int)
    ### note that this returns formulas
    ### also note that formula references are stored as
    ### R[relative]C[relative] or RabsoluteCabsolute
    @updateClient
    def getRawRow(self, row):
        if (row > 0 and row <= self.rowCount):
            values = list()
            colCount = self.colCount
            for col in xrange(1, colCount+1): # 1 through colCount
                cell = (row, col)
                values.append(self.fetchCellInputValue(cell))
            return values
        else:
            raise SheetError("Nonexistent row!")

    ## getRawCol
    ### returns a list of raw values (str) in a given col
    @updateClient
    def getRawCol(self, col):
        if (col > 0 and col <= self.colCount):
            values = list()
            rowCount = self.rowCount
            for row in xrange(1, rowCount+1): # 1 through rowCount
                cell = (row, col)
                values.append(self.fetchCellInputValue(cell))
            return values
        else:
            raise SheetError("Nonexistent column!")

    ## getNumericRow
    ### returns a list of numeric values (float) in a given row
    ### non-numeric values are represented as None
    @updateClient
    def getNumericRow(self, row):
        if (row > 0 and row <= self.rowCount):
            values = list()
            colCount = self.colCount
            for col in xrange(1, colCount+1): # 1 through colCount
                cell = (row, col)
                values.append(self.fetchCellNumericValue(cell))
            return values
        else:
            raise SheetError("Nonexistent row!")

    ## getNumericCol
    ### returns a list of numeric values (float) in a given col
    ### non-numeric values are represented as None
    @updateClient
    def getNumericCol(self, col):
        if (col > 0 and col <= self.colCount):
            values = list()
            rowCount = self.rowCount
            for row in xrange(1, rowCount+1): # 1 through rowCount
                cell = (row, col)
                values.append(self.fetchCellNumericValue(cell))
            return values
        else:
            raise SheetError("Nonexistent column!")

    ## export
    ### given a format, returns
    ### a (string) export of the sheet
    @updateClient
    def export(self, format="csv"):
        return self.sheet.export(format)

    ## exportCSV
    ### returns a (string) CSV export of the sheet
    @updateClient
    def exportCSV(self):
        return self.export("csv")

    ## findAll
    ### given a query (string, including regex patterns)
    ### returns a list of cells that match the query
    ### as row, col pair tuples
    @updateClient
    def findAll(self, query):
        return [(cell.row, cell.col) for cell in 
                self.sheet.findall(query)]

    ## updateAll
    ### given a query (string, including regex patterns)
    ### and a new value to set cells to
    ### sets all cells that match the query to the new value
    @updateClient
    def updateAll(self, query, newValue):
        found = self.findAll(query)
        for find in found:
            self.updateCell(find, newValue)

    ## getRecords
    ### returns the rows of the sheet as dictionary records
    ### in a list
    ### takes a head (int, default 1) representing a header row
    ### and zero (bool) - whether or not to interpret empty cells
    ### as zeros (default to False)
    @updateClient
    def getRecords(self, zero=False, head=1):
        return self.sheet.get_all_records(empty2zero=zero,
                                          head=head)

    ## getLabel
    ### given a row (int) and a col (int),
    ### returns a corresponding label (alphanumeric)
    def getLabel(self, row, col):
        return self.sheet.get_addr_int(row, col)

    ## getRowCol
    ### given a label, returns corresponding row (int)
    ### and col (int) as a tuple
    def getRowCol(self, label):
        return self.sheet.get_int_addr(label)

    ## getAll
    ### gets a list of lists (rows) containing all
    ### values in the worksheet
    @updateClient
    def getAll(self):
        return self.sheet.get_all_values()

    ## getLabeledRange
    ### gets a list of lists (rows) containing all values
    ### in a specified labeled range (string)
    @updateClient
    def getLabeledRange(self, rangeLabel):
        return self.sheet.range(rangeLabel)

    ## getRangeLabel
    ### returns a range label given row col pairs
    def getRangeLabel(self, row1, col1, row2, col2):
        return (self.getLabel(row1, col1) + ":" +
                self.getLabel(row2, col2))

    ## getRangeRowCol
    ### returns row col pairs given a range label
    def getRangeRowCol(self, rangeLabel):
        rangeLabels = rangeLabel.split(":")
        return (self.getRowCol(rangeLabels[0]),
                self.getRowCol(rangeLabels[1]))

    ## getNumberedRange
    ### gets a list of lists (rows) containing all values
    ### in a specificed numbered range (row col pairs)
    @updateClient
    def getNumberedRange(self, row1, col1, row2, col2):
        return self.getLabeledRange(self.getRangeLabel(row1,
                                    col1, row2, col2))

    ## getRange
    ### given either a list/tuple of row-col pair tuples,
    ### or a string range label
    ### returns a list of lists (rows) containing all values
    ### in said range
    @updateClient
    def getRange(self, rangeLabel):
        if (type(rangeLabel) == str):
            return self.getLabeledRange(rangeLabel)
        elif (type(rangeLabel) == list or 
              type(rangeLabel) == tuple):
            if (len(rangeLabel) == 2):
                row1 = rangeLabel[0][0]
                col1 = rangeLabel[0][1]
                row2 = rangeLabel[1][0]
                col2 = rangeLabel[1][1]
            elif (len(rangeLabel) == 4):
                row1 = rangeLabel[0]
                col1 = rangeLabel[1]
                row2 = rangeLabel[2]
                col2 = rangeLabel[3]
            else: raise SheetError("Improper range label!")
            return self.getNumberedRange(row1, col1, row2, col2)
        else:
            raise SheetError("Improper range label!")

    ## setNumberedRange
    ### given starting/ending row/col combinations (int)
    ### and a (flattened) list containing values to set
    ### goes top->bottom, left->right through the range
    ### (going left->right through each row)
    ### and sets values from the list
    ### end row/col numbers are treated as inclusive
    @updateClient
    def setNumberedRange(self, row1, col1, row2, col2, values):
        if (row1 < 1 or col1 < 1 or row2 < row1 or col2 < col1 or
            row2 > self.rowCount or col2 > self.colCount):
            raise SheetError("Invalid range!")
        if (len(values) != (row2-row1+1) * (col2-col1+1)):
            raise SheetError("Values do not match range size!")
        for r in xrange(row1, row2+1):
            for c in xrange(col1, col2+1):
                # value index = (row #, starting from 0) *
                # (# of colums per row) + (col#, starting from 0)
                valIndex = (r-row1) * (col2-col1+1) + (c-col1)
                self.updateCell((r, c), values[valIndex])

    ## setLabeledRange
    ### given starting/ending labels in a string
    ### and a (flattened) list containing values to set
    ### goes top->bottom, left->right through the range
    ### (going left->right through each row)
    ### and sets values from the list
    @updateClient
    def setLabeledRange(self, rangeLabel, values):
        rangeRowCols = self.getRangeRowCol(rangeLabel)
        row1, col1 = rangeRowCols[0]
        row2, col2 = rangeRowCols[1]
        self.setNumberedRange(row1, col1, row2, col2, values)

    ## setRange
    ### given a rangeLabel (list of ints/tuples or string)
    ### and a list of values to set
    ### goes left->right through the rows and
    ### sets the cell values to the provided values
    @updateClient
    def setRange(self, rangeLabel, values):
        values = flattenList(values)
        if (type(rangeLabel) == str):
            self.setLabeledRange(rangeLabel, values)
        elif (type(rangeLabel) == list or type(rangeLabel) == tuple):
            if (len(rangeLabel) == 2):
                self.setNumberedRange(rangeLabel[0][0], rangeLabel[0][1],
                                      rangeLabel[1][0], rangeLabel[1][1],
                                      values)
            elif (len(rangeLabel) == 4):
                self.setNumberedRange(rangeLabel[0], rangeLabel[1],
                                      rangeLabel[2], rangeLabel[3],
                                      values)
            else: raise SheetError("Invalid range label!")
        else: raise SheetError("Invalid range label!")

    ## fetchCell
    ### fetches a cell given a location (string or row/col tuple)
    @updateClient
    def fetchCell(self, loc):
        if (type(loc) == tuple or type(loc) == list):
            return self.sheet.cell(loc[0], loc[1])
        elif (type(loc) == str):
            return self.sheet.acell(loc)
        else: raise SheetError("Invalid cell location!")

    ## fetchCellValue
    ### fetches the displayed value (str) of a given cell
    @updateClient
    def fetchCellValue(self, loc):
        cell = self.fetchCell(loc)
        return cell.value

    ## fetchCellInputValue
    ### fetches the raw value (str) of a given cell
    ### preserves formulas as RxCx references
    @updateClient
    def fetchCellInputValue(self, loc):
        cell = self.fetchCell(loc)
        return cell.input_value

    ## fetchCellNumericValue
    ### fetches the numeric output value (float) of a given cell
    ### returns None for non-numeric cells
    @updateClient
    def fetchCellNumericValue(self, loc):
        cell = self.fetchCell(loc)
        return cell.numeric_value

    ## write operations

    ## addCols
    ### given a number of columns to add
    ### adds that number of columns to the sheet
    @updateClient
    def addCols(self, count):
        self.sheet.add_cols(count)

    ## addRows
    ### given a number of rows to add
    ### adds that number of rows to the sheet
    @updateClient
    def addRows(self, count):
        self.sheet.add_rows(count)

    ## appendRow
    ### given a row as a list of values (str),
    ### appends that row to the bottom of the sheet
    @updateClient
    def appendRow(self, row):
        self.sheet.append_row(row)

    ## appendRows
    ### given rows as a list of lists of values,
    ### apends those rows to the bottom of the sheet
    @updateClient
    def appendRows(self, *rows):
        for row in rows:
            self.appendRow(row)

    ## insertRow
    ### given a target index (int, default 1)
    ### and values to insert (list)
    ### adds a new row with the given values
    ### at that point in the sheet
    @updateClient
    def insertRow(self, values, index=1):
        self.sheet.insert_row(values, index)

    ## fillRow
    ### given a target row (int)
    ### and new values (list) to insert there
    ### inserts the new values at that row
    ### overwriting existing values and expanding
    ### the sheet as necessary
    @updateClient
    def fillRow(self, rowNum, newValues):
        if (len(newValues) > self.colCount):
            self.addCols(len(newValues) - self.colCount)
        for x in xrange(len(newValues)): # col num starts at 1
            self.updateCell((rowNum, x+1), newValues[x])

    ## fillCol
    ### given a target column (int)
    ### and new values (list) to insert there
    ### inserts the new values at that column
    ### overwriting existing values and expanding
    ### the sheet as necessary
    @updateClient
    def fillCol(self, colNum, newValues):
        if (len(newValues) > self.rowCount):
            self.addRows(len(newValues) - self.rowCount)
        for x in xrange(len(newValues)):
            self.updateCell((x+1, colNum), newValues[x])

    ## moveRow
    ### moves an existing row (int) to a new location (int)
    @updateClient
    def moveRow(self, srcRow, destRow):
        if (destRow > self.rowCount or destRow <= 0):
            raise SheetError("Nonexistent destination row!")
        data = self.getRawRow(srcRow)
        self.fillRow(destRow, data)

    ## moveCol
    ### moves an existing col (int) to a new location (int)
    @updateClient
    def moveCol(self, srcCol, destCol):
        if (destCol > self.colCount or destCol <= 0):
            raise SheetError("Nonexistent destination col!")
        data = self.getRawCol(srcCol)
        self.fillCol(destCol, data)

    ## swapRows
    ### given row1 (int) and row2 (int), swaps the
    ### values at those two rows
    @updateClient
    def swapRows(self, row1, row2):
        if (max(row1, row2) > self.rowCount
            or min(row1, row2) <= 0):
            raise SheetError("Nonexistent row!")
        newRow2 = self.getRawRow(row1)
        self.fillRow(row1, self.getRawRow(row2))
        self.fillRow(row2, newRow2)

    ## swapCols
    ### given col1 (int) and col2 (int), swaps the
    ### values at those two columns
    @updateClient
    def swapCols(self, col1, col2):
        if (max(col1, col2) > self.colCount
            or min(col1, col2) <= 0):
            raise SheetError("Nonexistent col!")
        newCol2 = self.getRawCol(col1)
        self.fillCol(col1, self.getRawCol(col2))
        self.fillCol(col2, newCol2)

    ## appendCol
    ### given a list of values to add
    ### adds a new column to the end of the sheet
    @updateClient
    def appendCol(self, col):
        rowCount = self.rowCount
        colNum = self.colCount + 1
        self.addCols(1)
        self.fillCol(colNum, col)

    ## appendCols
    ### given lists of values to add
    ### appends new columns to the end of the sheet
    @updateClient
    def appendCols(self, *cols):
        rowCount = self.rowCount
        colNum = self.colCount
        self.addCols(len(cols))
        for col in cols:
            colNum += 1
            self.fillCol(colNum, col)

    ## updateCell
    ### given a cell location (tuple or string)
    ### updates that cell with a new value
    @updateClient
    def updateCell(self, loc, value):
        if (type(loc) == tuple or
            type(loc) == list):
            self.sheet.update_cell(loc[0], loc[1], value)
        elif (type(loc) == str):
            self.sheet.update_acell(loc, value)
        else: raise SheetError("Invalid cell location!")

    ## addToCell
    ### given a cell location (tuple or string)
    ### adds a new value to the cell's existing values
    ### with a separator in between (default is " ")
    @updateClient
    def addToCell(self, loc, value, separator=" "):
        newVal = self.fetchCellValue(loc)
        if len(newVal) > 0:
            newVal += separator + value
        else:
            newVal = value
        self.updateCell(loc, newVal)

    ## resize
    ### resizes the entire sheet
    ### given a new rowCount and colCount
    @updateClient
    def resize(self, rowCount, colCount):
        self.sheet.resize(rowCount, colCount)

    ## deleteRow
    ### given a row number to target
    ### deletes that row from the sheet
    @updateClient
    def deleteRow(self, rowNum):
        self.sheet.delete_row(rowNum)

    ## deleteCol
    ### given a col number to target
    ### deletes that column from the sheet
    @updateClient
    def deleteCol(self, colNum):
        # shift columns on right to the left
        for col in xrange(colNum+1, self.colCount+1):
            colVals = self.getCol(col)
            self.fillCol(col-1, colVals)
        self.resize(self.rowCount, self.colCount-1)

    ## deleteSheet
    ### deletes the entire worksheet
    @updateClient
    def deleteSheet(self):
        self.client.del_worksheet(self.sheet)

    ## delete
    ### deletes the entire worksheet
    @updateClient
    def delete(self):
        self.deleteSheet()