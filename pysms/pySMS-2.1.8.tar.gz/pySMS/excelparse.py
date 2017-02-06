# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 17:28:07 2016

@author: doarni
"""

import os
import xlrd
from prettytable import PrettyTable
from colorama import init, Fore
from pySMS.ui.tk import widget
init(autoreset=True)

isWorkbookLoaded = False
workbook = None

class listfiles():
    
    def __init__(self):
        self.filelist = []
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.dir = self.path + "\\excel_files"
        
   
    def listdir(self):
        count = 1
        os.chdir(self.dir)
        exts = ['xlsx','xls']        
        
        files = [f for f in os.listdir(os.getcwd()) if f.endswith('')]
        for filename in files:
            if filename.split('.')[1] in exts:
                self.filelist.append(str(count)+";"+filename)
                count += 1
        for item in self.filelist:
            print(item.split(';')[0] + ") "+item.split(';')[1])
        
        print(Fore.RED + 'Choose a file to load?')
        
        num = input('>> ')
        for item in self.filelist:
            if num == item.split(';')[0]:
                print(Fore.RED +"Loading " + self.dir + "\\" + str(item.split(';')[1]) + " ...")
                return self.dir + "\\" + item.split(';')[1]
            
class parse():
        
    
    def loadFile():
        l = listfiles()
        xlFile = l.listdir()
        return xlFile
        
    def readRows( y=1):
        
        productNumber = None
        ediNumber = None
        description = None
        lotNumber = None
        serialNumber = None
        caseNumber = None
        
        dailySnapshot = workbook.sheet_by_index(2)
        for row in range(dailySnapshot.nrows):
            row = dailySnapshot.row_values(y)
            productNumber = str(row[7])
            ediNumber = str(row[8])
            description = str(row[9])
            lotNumber = str(row[10])
            serialNumber = str(row[11])
            caseNumber = str(row[12])
            return productNumber + ";" + ediNumber + ";" + description + ";" + lotNumber + ";" + serialNumber + ";" + caseNumber
            

class evaluate():
    
    def __init__(self, N):
        self.N = N
        self.data = self.getData()
        
    def getData(self):
        pr = parse.readRows(y=self.N)
        data = pr.split(';')
        return data
        
    def getCase(self):
        case = self.data[5]
        return case
    
    def getProd(self):
        prod = self.data[0]
        return prod
        
    def getEdi(self):
        edi = self.data[1]
        return edi

    def getDesc(self):
        desc = self.data[2]
        return desc
        
    def getLotNumber(self):
        lotN = self.data[3]
        return lotN
    
    def getSerial(self):
        serial = self.data[4]
        return serial
          
    def makeCaseData(self):
        caseData = []
        caseData.append(self.getCase() + " " + self.getProd()  + " " + self.getLotNumber() + " " + self.getEdi() + " " + self.getSerial() + " " + self.getDesc())            
        return caseData


def getNewCase(workbook, rowN):
    sheet = workbook.sheet_by_index(2)
    rowCountMax = sheet.nrows - 1
    currentRow = None
    currentCase = None
    currentCaseData = []
    currentRow = rowN
    global lastRow
    lastrow = 0
    
    def get(rN):
        print(Fore.RED +"Items in this case: ")
        x = PrettyTable()
        x.field_names = ["Case", "Product", "Edi", "Lot Number", "Serial Number"]
        for i in range(currentRow, rowCountMax - currentRow):
            row = i
            e = evaluate(row)
            case = e.makeCaseData()
            c = case[0].split(' ')[0]
            p = case[0].split(' ')[1]
            l = case[0].split(' ')[2]
            e = case[0].split(' ')[3]
            s = case[0].split(' ')[4]
            if c == currentCase:
                x.add_row([c, p, e, l, s])
                currentCaseData.append(p + ';' + l)
                lastRow = row
            elif c != currentCase:
                pass
        print(x)
        print(Fore.RED + 'case: ' + currentCase + ' has ' + str(len(currentCaseData)) + ' items associated with it.' \
                ' Lines range began at ' + str(currentRow + 1) + ' and went to ' + str(lastRow) + ' of the excel sheet')
    
    if currentCase == None:
        e = evaluate(currentRow)
        case = e.makeCaseData()
        currentCase = case[0].split(' ')[0]
    else:
        None
    
    get(currentRow)
    return {"Case": currentCase, "Case Data": currentCaseData, "Current Row": currentRow + 1, "Last Row": lastrow }

   
def genCaseData():
    global isWorkbookLoaded 
    global workbook
    w = widget()
    r = int(w.get('Enter Row you are starting at: ')) - 1
    if isWorkbookLoaded == False:
        try:
            workbook = xlrd.open_workbook(parse.loadFile())
            isWorkbookLoaded = True
            return getNewCase(workbook, r)
        except:
            print(Fore.RED +'Could not open file')
        return getNewCase(workbook, r)
    elif workbook == None:
        workbook = xlrd.open_workbook(parse.loadFile())
        isWorkbookLoaded = True
        return getNewCase(workbook, r)
    else:  
        return getNewCase(workbook, r)
