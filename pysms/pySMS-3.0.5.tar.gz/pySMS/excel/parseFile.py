# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 12:30:48 2016

@author: doarni
"""


import xlrd
from pySMS.utils.logic.webpage import Webpage
from colorama import init, Fore


init(autoreset=True)

skipped = []

class parse():

    @staticmethod
    def readRows(filename, y, sheetIndex):
        w = Webpage.Logic()

        def is_tray(item):
            try:
                if w.get_item_info(item)['data_parent'].split('_')[0] == 'tray':
                    return True
                else:
                    return False
            except Exception as e:
                print(e)
                return True

        if sheetIndex == 2:
            productNumber = None
            ediNumber = None
            description = None
            lotNumber = None
            serialNumber = None
            caseNumber = None
            _pass = False

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
            _pass = False

            if (lotNumber == '' and serialNumber == '') or (is_tray(productNumber) == True):
                print(Fore.LIGHTRED_EX + productNumber + " at row " + str(y + 1) + " has no lot or serial or is a tray! It was not added to the mutation queue")
                skipped.append(productNumber + ';' + str(y + 1))
                _pass = True
            else:
                print(Fore.LIGHTYELLOW_EX  +'Adding to queue: \tProduct: [{:<15s}] \t\tlot\serial: [{:<15s}]'.format(Fore.LIGHTCYAN_EX + productNumber + Fore.LIGHTYELLOW_EX, Fore.LIGHTCYAN_EX + (lotNumber if lotNumber != '' else serialNumber)) + Fore.LIGHTYELLOW_EX)

            return {'totalRows': book.nrows - 1,
                    'territoryNumber': tNumber,
                    'territoryName': siteName,
                    'productNumber': productNumber,
                    'ediNumber': ediNumber,
                    'description': description,
                    'lotNumber': lotNumber,
                    'serialNumber': serialNumber,
                    'caseNumber': caseNumber,
                    'bin?': "No",
                    "pass": _pass}

        if sheetIndex == 3:

            productNumber = None
            ediNumber = None
            description = None
            lotNumber = None
            serialNumber = None
            caseNumber = None
            bin = None
            _pass = False

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
            _pass = False

            if (lotNumber == '' and serialNumber == '') or (is_tray(productNumber) == True):
                print(Fore.LIGHTRED_EX + productNumber + " at row " + str(y + 1) + " has no lot or serial or is a tray! It was not added to the mutation queue")
                skipped.append(productNumber + ';' + str(y + 1))
                _pass = True
            else:
                print(Fore.LIGHTYELLOW_EX  +'Adding to queue: \tProduct: [{:<15s}] \t\tlot\serial: [{:<15s}]'.format(Fore.LIGHTCYAN_EX + productNumber + Fore.LIGHTYELLOW_EX, Fore.LIGHTCYAN_EX + (lotNumber if lotNumber != '' else serialNumber)) + Fore.LIGHTYELLOW_EX)

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
                    "bin?": "Yes",
                    "pass": _pass}
