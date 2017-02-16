##################################
# table.py
# handles table, using a worksheet
##################################

from errors import *
from functions import *
from worksheet import Worksheet

class Table(object):

    # main Table class
    ## takes worksheet (Worksheet object),
    ## parent (required): Database object,
    def __init__(self, worksheet, parent):
        self._sheet = worksheet
        self.name = self.sheet.ID
        self._parent = parent
        self.headerRow = self.fetchFromParent("HEADER")[0]
        if self.headerRow is "": 
            self.headerRow = 1
        else: self.headerRow = int(self.headerRow)
        self.updateHeader()
        self.refRow = self.fetchFromParent("REFROW")[0]
        if self.refRow is "":
            self.refRow = None
        else: self.refRow = int(self.refRow)
        self.updateConstraints()
        self.ignoredRows = set([int(x) for x in 
                               self.fetchFromParent("IGNOREDROWS")
                               if isInteger(x)])
        self.ignoredRows.add(self.headerRow)
        if self.refRow is not None: self.ignoredRows.add(self.refRow)
        self.ignoredCols = set([int(x) for x in 
                               self.fetchFromParent("IGNOREDCOLS")
                               if isInteger(x)])
        self._acceptableConstraints = {"UNIQUE", "POSITIVE", "NONNEGATIVE",
                                       "NONNEG", "STRING", "ALPHA", 
                                       "ALPHANUMERIC", "ALPHANUM",
                                       "ARRAY", "LIST", "BOOL", "BOOLEAN",
                                       "FORMULA", "INT", "NUMERIC"}

    ## parent
    @property
    def parent(self):
        return self._parent

    ## sheet
    @property
    def sheet(self):
        return self._sheet

    ## fetchFromParent
    ### fetches a constant from the parent
    def fetchFromParent(self, label):
        label = self.name + "_" + label
        return self.parent.fetchConstant(label)

    ## removeFromParent
    ### removes a constant from the parent
    def removeFromParent(self, label):
        label = self.name + "_" + label
        self.parent.removeConstant(label)

    ## updateHeader
    ### updates local records of header
    def updateHeader(self):
        self.header = self.fetchRowLabels(self.headerRow, False)
        self.reverseHeader = reverseDict(self.header)

    ## updateConstraints
    ### updates local records of constraints
    def updateConstraints(self):
        if self.refRow is None:
            self.constraints = dict()
            for i in xrange(1, self.sheet.colCount+1):
                self.constraints[i] = ""
        else:
            self.constraints = self.fetchRowLabels(self.refRow)

    ## setRefRow
    ### sets refRow locally and on parent
    def setRefRow(self, row):
        if (row is not None and 
            (row <= 0 or row > self.sheet.rowCount)):
            raise SheetError("Invalid row!")
        if self.refRow in self.ignoredRows:
            self.ignoredRows.remove(self.refRow)
        self.parent.setConstant(self.name + "_" + "REFROW", row)
        self.refRow = row
        self.ignoredRows.add(self.refRow)
        self.updateConstraints()

    ## addRefRow
    ### adds a refRow and updates constraints
    ### adds to the bottom to minimize disruption of other records
    def addRefRow(self):
        self.sheet.addRows(1)
        self.setRefRow(self.sheet.rowCount) # newest row

    ## setHeader
    ### sets the header to a new row
    def setHeader(self, row):
        if (row <= 0 or row > self.sheet.rowCount):
            raise SheetError("Invalid row!")
        self.parent.setConstant(self.name + "_" + "HEADER", row)
        if self.headerRow in self.ignoredRows:
            self.ignoredRows.remove(self.headerRow)
        self.headerRow = row
        self.ignoredRows.add(self.headerRow)
        self.updateHeader()

    ## ignoreRows
    ### ignore rows
    def ignoreRows(self, *rows):
        for row in rows:
            self.parent.addToConstantList(self.name + "_" + "IGNOREDROWS",
                                          row)
            self.ignoredRows.add(row)

    ## unignoreRows
    ### unignore rows
    def unignoreRows(self, *rows):
        if self.headerRow in rows:
            raise DataError("Header must remain ignored!")
        if self.refRow in rows:
            raise DataError("Ref row must remain ignored!")
        for row in rows:
            self.parent.removeFromConstantList(self.name + "_" + "IGNOREDROWS",
                                               row)
            self.ignoredRows.remove(row)

    ## ignoreCols
    ### ignore columns
    def ignoreCols(self, *cols):
        for col in cols:
            self.parent.addToConstantList(self.name + "_" + "IGNOREDCOLS",
                                          col)
            self.ignoredCols.add(col)

    ## unignoreCols
    ### unignore columns
    def unignoreCols(self, *cols):
        for col in cols:
            self.parent.removeFromConstantList(self.name + "_" + "IGNOREDCOLS",
                                               col)
            self.ignoredCols.remove(col)

    ## constrain
    ### given a column (int)
    ### adds a constraint (string) to the sheet
    ### optional: erase (default False) - to overwrite previous constraints
    def constrain(self, col, constraint, erase=False):
        if (constraint not in self._acceptableConstraints
            and constraint[0] != "="):
            raise DataError("Invalid constraint!")
        if self.refRow is None:
            self.addRefRow()
        if erase:
            self.sheet.updateCell((self.refRow, col), constraint)
        else:
            self.sheet.addToCell((self.refRow, col), constraint)
        self.updateConstraints()

    ## updateConstraint
    ### given a header label (string)
    ### adds/updates a constraint (string) to the sheet
    ### optional: erase (default False) - to overwrite previous constraints
    def updateConstraint(self, label, constraint, erase=False):
        if label not in self.reverseHeader:
            raise DataError("Nonexistent label!")
        col = self.reverseHeader[label]
        self.constrain(col, constraint, erase=erase)

    ## expandHeader
    ### adds new labels (strings or tuples w/ constraints)
    ### to the header
    def expandHeader(self, *labels):
        for label in labels:
            if (type(label) not in {list, tuple, str}):
                raise DataError("Invalid label!")
            elif label in self.reverseHeader:
                raise DataError("Duplicate label!")
        if len(labels) != len(set(labels)):
            raise DataError("Duplicate label!")
        oldLen = self.sheet.colCount
        self.sheet.addCols(len(labels))
        col = oldLen
        for label in labels:
            col += 1
            if (type(label) == str):
                self.sheet.updateCell((self.headerRow, col), label)
            else: # list or tuple
                self.sheet.updateCell((self.headerRow, col), label[0])
                self.constrain(col, label[1])
        self.updateHeader()
        self.updateConstraints()

    ## setHeaderLabels
    ### given new header labels,
    ### updates the header
    def setHeaderLabels(self, *labels):
        self.sheet.fillRow(self.headerRow, labels)
        self.updateHeader()

    ## setConstraints(self, *labels):
    ### given new constraints,
    ### updates constraints
    def setConstraints(self, *labels):
        if self.refRow is None:
            self.addRefRow()
        self.sheet.fillRow(self.refRow, labels)
        self.updateConstraints()

    ## fetchRowLabels
    ### given target row (int),
    ### returns a dict mapping col numbers
    ### and their corresponding values in the row
    ### also takes, optionally, whether to fetch raw values
    ### (default True)
    def fetchRowLabels(self, rowNum, raw=True):
        if raw: rowVals = self.sheet.getRawRow(rowNum)
        else: rowVals = self.sheet.getRow(rowNum)
        results = dict()
        for i in xrange(1, len(rowVals) + 1): # 1 through length
            results[i] = rowVals[i-1]
        return results

    ## _addRowToResults
    ### adds a row as an entity to a results dict
    ### optional: unignore (default False)
    ###     whether to return ignored values
    def _getRowAsDict(self, row, unignore=False):
        results = dict()
        for i in xrange(1, len(row) + 1): # 1 through length
            if (unignore or i not in self.ignoredCols):
                results[self.header[i]] = self.getConstrained(row[i-1], 
                                          self.constraints[i])
        return results

    ## fetchEntity
    ### given a target row (int),
    ### returns a dict mapping header labels
    ### to corresponding values in that row
    ### optional: unignore (default False)
    ###     whether to fetch values in ignored columns
    def fetchEntity(self, rowNum, unignore=False):
        rowVals = self.sheet.getRow(rowNum)
        return self._getRowAsDict(rowVals, unignore)

    ## fetchEntities
    ### given a list of target rows (ints),
    ### returns a list of dicts mapping header labels
    ### to corresponding values in that row
    ### optional: unignore (default False)
    ###    whether to fetch values in ignored colums
    def fetchEntities(self, rows, unignore=False):
        if (len(rows) > 0 and
            (min(rows) <= 0 or max(rows) > self.sheet.rowCount)):
            raise SheetError("Invalid row!")
        allVals = self.sheet.getAll()
        results = list()
        for row in rows:
            results.append(self._getRowAsDict(allVals[row-1], unignore))
        return results

    ## findEntityRows
    ### given a dictionary that maps labels to
    ### desired values ("value" or "values" (list)) and a boolean ("type")
    ### indicating whether to check for "positive" or "negative" matches
    ### fetches all rows that match (or don't match) these pairs,
    ### returning a set of rows
    ### if matchDict is empty, returns all rows
    def findEntityRows(self, matchDict):
        results = set(range(1, self.sheet.rowCount+1))
        for label in matchDict:
            if label not in self.reverseHeader:
                raise DataError("Invalid label!")
        for label in matchDict:
            if "value" in matchDict[label]:
                matchKey = [str(matchDict[label]["value"]),]
            else: matchKey = [str(value) for value in matchDict[label]["values"]]
            matchType = (matchDict[label]["type"].lower() 
                         == "positive")
            colNum = self.reverseHeader[label]
            col = self.sheet.getCol(colNum)
            if matchType:
                validRows = set([i+1 for i in xrange(len(col)) if col[i] 
                                in matchKey])
            else:
                validRows = set([i+1 for i in xrange(len(col)) if col[i] 
                                not in matchKey])
            results = set.intersection(results, validRows)
        return (results - self.ignoredRows)

    ## findEntities
    ### given a dictionary of label (string)-{value/type} pairs,
    ### fetches all rows that match these pairs,
    ### returning a list of dictionaries
    ### if matchDict is empty, returns all entities
    ### optional: keyLabel- label to use as a key (default None)
    ### optional: allowDuplicates- if a keyLabel is used, whether
    ###     duplicate values should be expected (default False)
    def findEntities(self, matchDict, keyLabel=None, allowDuplicates=False):
        rows = sorted(self.findEntityRows(matchDict))
        results = self.fetchEntities(rows)
        if keyLabel is not None:
            results = convertToKeyed(results, keyLabel, allowDuplicates)
        return results

    ## getAllEntities
    ### returns all entities in the table
    ### can also take a keyLabel for easier result indexing
    def getAllEntities(self, keyLabel=None, allowDuplicates=False):
        return self.findEntities(dict(), keyLabel, allowDuplicates)

    ## findValues
    ### given a dictionary of label-value pairs to match,
    ### and a list or set of attributes to check,
    ### returns a list of dictionaries of attribute-value
    ### pairs in matching entities
    def findValues(self, matchDict, attributes):
        matching = self.findEntities(matchDict)
        results = list()
        for entity in matching:
            result = dict()
            for attribute in attributes:
                if attribute not in entity:
                    raise DataError("Checking label not in header: " +
                                    str(attribute))
                result[attribute] = entity[attribute]
            results.append(result)
        return results

    ## findValue
    ### given a matching dict,
    ### finds a value for a single attribute
    ### returns a list of values of that attribute
    def findValue(self, matchDict, attribute):
        return [val[attribute] for val in 
                self.findValues(matchDict, [attribute,])]

    ## _hideIgnored
    ### given a list of row or column values
    ### and a string indicating whether it's a row or a column,
    ### returns a list containing only non-ignored rows/columns
    def _hideIgnored(self, data, rowOrCol):
        if "row" in rowOrCol.lower():
            ignore = self.ignoredRows
        else:
            ignore = self.ignoredCols
        indices = set([i-1 for i in ignore])
        return dropIndices(data, indices)

    ## checkConstraint
    ### given a value,
    ### a constraint (string),
    ### and a column (integer, optional outside UNIQUE checks),
    ### determines whether the value meets the constraint
    def checkConstraint(self, value, constraint, col=None):
        if value == "" or constraint == "":
            return True # vacuously true
        constraint = constraint.upper()
        if (constraint == "UNIQUE"):
            if col is None: raise DataError("Need column for UNIQUE check!")
            colValues = set(self._hideIgnored(self.sheet.getCol(col), "col"))
            return (str(value) not in colValues)
        elif (constraint == "POSITIVE"):
            return isPositive(str(value))
        elif (constraint == "NONNEGATIVE" or 
              constraint == "NONNEG"):
            return isNonnegative(str(value))
        elif (constraint == "INT"):
            return isInteger(str(value))
        elif (constraint == "NUMERIC"):
            return isNumeric(str(value))
        elif (constraint == "STRING"):
            return (isinstance(value, str))
        elif (constraint == "ALPHA"):
            return isAlpha(str(value))
        elif (constraint == "ALPHANUMERIC" or
              constraint == "ALPHANUM"):
            return isAlphanumeric(str(value))
        elif (constraint == "ARRAY" or
              constraint == "LIST"):
            return (isArray(value))
        elif ((constraint == "BOOL") or
              (constraint == "BOOLEAN")):
            return (type(value) == bool or
                    value == "TRUE" or
                    value == "FALSE")
        elif ((constraint == "FORMULA")):
            return (isinstance(value, str) and 
                    value[0] == "=")
        else:
            raise DataError("Unrecognized constraint: ", constraint)

    ## checkConstraints
    ### given a value (string),
    ### a constraint string (string),
    ### and a column (integer),
    ### determines whether any constraints are held by the value
    def checkConstraints(self, value, constraintStr, col=None):
        if (len(constraintStr) == 0 or constraintStr[0] == "="):
            return True
        else:
            constraints = constraintStr.split(" ")
            for constraint in constraints:
                if (self.checkConstraint(value, constraint, col)\
                    == False):
                    return False
            return True

    ## getConstrained
    ### given a value (string),
    ### and a constraint string (string),
    ### returns the value in the proper type
    ### if value is "", "" is returned
    def getConstrained(self, value, constraint):
        if constraint == "" or value == "":
            return value
        constraint = constraint.upper()
        if "LIST" in constraint or "ARRAY" in constraint:
            if not isinstance(value, str):
                return [value,]
            if value[0] == "[": value = value[1:]
            if value[-1] == "]": value = value[:-1]
            split = value.split(",")
            conStr = constraint.replace("ARRAY", "")
            conStr = conStr.replace("LIST", "")
            conStr = conStr.replace("  ", " ")
            return [self.getConstrained(val, conStr)
                    for val in split]
        elif "INT" in constraint:
            return int(value)
        elif ("NUMERIC" in constraint and 
            (constraint.count("NUMERIC") > 
             constraint.count("ALPHANUMERIC"))):
            return float(value)
        elif "BOOL" in constraint or "BOOLEAN" in constraint:
            return (value == "TRUE")
        else:
            return value

    ## addEntity
    ### given a mapping of labels to values (dict),
    ### adds an entity to the table
    def addEntity(self, entity):
        values = ["",] * self.sheet.colCount
        for i in xrange(len(self.constraints)): # recognize formulas
            if (len(self.constraints[i+1]) > 0 and 
                self.constraints[i+1][0] == "="):
                values[i] = self.constraints[i+1]
        for label in entity:
            if label not in self.reverseHeader:
                self.expandHeader(label)
                values.append("")
            col = self.reverseHeader[label]
            if col in self.ignoredCols:
                raise DataError("Attemping to modify an ignored column!")
            constraintStr = self.constraints[col]
            if (self.checkConstraints(entity[label], \
                constraintStr, col) == False):
                raise DataError("Constraint violation! Label: " 
                                + str(label) + ", value: " +
                                str(entity[label]))
            values[col-1] = entity[label]
        self.sheet.appendRow(values)

    ## removeEntity
    ### given a row, removes the entity at that row
    ### updating ignoreRows, header, etc. accordingly
    def removeEntity(self, row):
        if row in self.ignoredRows:
            raise DataError("Attempting to delete protected row!")
        self.sheet.deleteRow(row)
        if self.headerRow > row:
            self.setHeader(self.headerRow-1)
        if self.refRow > row:
            self.setRefRow(self.refRow-1)
        ignoredRows = [int(x) for x in 
                       self.fetchFromParent("IGNOREDROWS")
                       if isInteger(x)]
        for iRow in ignoredRows:
            if (iRow > row):
                self.unignoreRows(iRow)
                self.ignoreRows(iRow-1)

    ## updateEntity
    ### given a mapping of labels to values (dict),
    ### and a row to modify,
    ### modifies an existing entity in the table
    def updateEntity(self, updates, row):
        if row in self.ignoredRows:
            raise DataError("Attempting to modify an ignored row!")
        for label in updates:
            if label not in self.reverseHeader:
                self.expandHeader(label)
            col = self.reverseHeader[label]
            if col in self.ignoredCols:
                raise DataError("Attemping to modify an ignored column!")
            constraintStr = self.constraints[col]
            if (self.checkConstraints(updates[label], \
                constraintStr, col) == False):
                raise DataError("Constraint violation! Label: " 
                                + str(label) + ", value: " +
                                str(updates[label]))
            self.sheet.updateCell((row, col), updates[label])

    ## updateMatchingEntities
    ### given a dictionary of labels to check and values
    ### to match & types of matches ('positive'/'negative')
    ### and another dictionary of labels to modify
    ### and values to set them to in the matching
    ### entities,
    ### updates the corresponding entities with the new
    ### values
    def updateMatchingEntities(self, matchDict, updates):
        for row in self.findEntityRows(matchDict):
            self.updateEntity(updates, row)

    ## removeMatchingEntities
    ### given a dictionary of labels to check and values
    ### to match & types of matches ('positive'/'negative')
    ### deletes corresponding entities
    def removeMatchingEntities(self, matchDict):
        for row in self.findEntityRows(matchDict):
            self.removeEntity(row)

    ## delete
    ### deletes self
    def delete(self):
        self.removeFromParent("HEADER")
        self.removeFromParent("REFROW")
        self.removeFromParent("IGNOREDROWS")
        self.removeFromParent("IGNOREDCOLS")
        self.sheet.delete()