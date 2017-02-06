# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 12:30:48 2016

@author: doarni
"""


import xlrd


class parse():
    
    def readRows(filename, y, sheetIndex):

        if sheetIndex == 2:
            productNumber = None
            ediNumber = None
            description = None
            lotNumber = None
            serialNumber = None
            caseNumber = None

            workbook = xlrd.open_workbook(filename)
            book = workbook.sheet_by_index(sheetIndex - 1)

            row = book.row_values(y + 1)
            tNumber = str(row[1])
            siteName = str(row[2])
            productNumber = str(row[7])
            ediNumber = str(row[8])
            description = str(row[9])
            lotNumber = str(row[10])
            serialNumber = str(row[11])
            caseNumber = str(row[12])

            return {'totalRows': book.nrows - 1,
                    'territoryNumber': tNumber,
                    'territoryName': siteName,
                    'productNumber': productNumber,
                    'ediNumber': ediNumber,
                    'description': description,
                    'lotNumber': lotNumber,
                    'serialNumber': serialNumber,
                    'caseNumber': caseNumber,
                    'bin?': "No"}

        if sheetIndex == 3:

            productNumber = None
            ediNumber = None
            description = None
            lotNumber = None
            serialNumber = None
            caseNumber = None
            bin = None

            workbook = xlrd.open_workbook(filename)
            book = workbook.sheet_by_index(sheetIndex - 1)

            row = book.row_values(y + 1)
            tNumber = str(row[1])
            siteName = str(row[2])
            bin = str(row[5])
            productNumber = str(row[6])
            ediNumber = str(row[7])
            description = str(row[8])
            lotNumber = str(row[9])
            serialNumber = str(row[10])
            caseNumber = "None"

            return {'totalRows': book.nrows - 1,
                    'territoryNumber': tNumber,
                    'territoryName': siteName,
                    'productNumber': productNumber,
                    'ediNumber': ediNumber,
                    'description': description,
                    'lotNumber': lotNumber,
                    'serialNumber': serialNumber,
                    'caseNumber': caseNumber,
                    'binlocation': bin,
                    "bin?": "Yes"}
