# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 14:07:30 2016

@author: doarni
"""

try:
    import pySMS.html.get as get
    import pySMS.html.parse as parse
except:
    import get
    import parse



class stringBuilder():
    def buildStringPath(htmlData, path, index):
        return parse.parse.returnClassName(htmlData, path, index)

class buildPaths():
    
    class buildDataFromPath():
        def __init__(self):
            self.g = get.openFile()
            self.g.loadFiles()
            self.l = self.g.getLoginData()
            self.m = self.g.getMainData()
        
        def bClass(self, path, isLogin, isMain):
            if isLogin == True:
                return parse.parse.returnClassData(self.l, path)
            if isMain == True:
                return parse.parse.returnClassData(self.m, path)
        
    
    class buildCustom():
        
        def __init__(self):
            self.g = get.openFile()
            self.g.loadFiles()
            self.l = self.g.getLoginData()
            self.m = self.g.getMainData()
            
        def bLoginPageElement(self, path, indexNumber):
            return parse.parse.returnClassName(self.l, path, indexNumber)
        
        def bMainPageElement(self, path, indexNumber):
            return parse.parse.returnClassName(self.m, path, indexNumber)

    
    class buildLoginPaths():
        
        def __init__(self):
            self.g = get.openFile()
            self.g.loadFiles()
            self.l = self.g.getLoginData()

        
        def bUsername(self):
            path = 'body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > table > tbody > tr > td > table > tbody > tr > td > div'
            p1 = parse.parse.returnClassName(self.l, path, 0)
            path2 = path + '.' + p1 + ' > table > tbody > tr:nth-child(2) > td'
            p2 = parse.parse.returnClassName(self.l, path2, 1)
            return path2 + '.' + p2 + ' > input'
        
        def bPassword(self):
            path = 'body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > table > tbody > tr > td > table > tbody > tr > td > div'
            p1 = parse.parse.returnClassName(self.l, path, 0)
            path2 = path + '.' + p1 + ' > table > tbody > tr:nth-child(3) > td'
            p2 = parse.parse.returnClassName(self.l, path2, 1)
            return path2 + '.' + p2 + ' > input'
            
        def bLoginButton(self):
            path = 'body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > table > tbody > tr > td > table > tbody > tr > td > div'
            p1 = parse.parse.returnClassName(self.l, path, 0)
            path2 = path + '.' + p1 + ' > table > tbody > tr:nth-child(5) > td > table > tbody > tr > td > span > div > div'
            p2 = parse.parse.returnClassName(self.l, path2, 1)
            p2l = p2.split(' ')
            p2j = '.'.join(p2l)
            return path2 + '.' + p2j

    class buildMainPaths(object):
        
        def __init__(self):
            self.g = get.openFile()
            self.g.loadFiles()
            self.u = self.g.getUserPageData()
            self.m = self.g.getMainData()
            self.c = self.g.getCaseData()
            self.co = self.g.getOrderData()
            self.col = self.g.getOrderLineData()
            
            
        #Paths that do not require a class
        def bStockTab(self):
            return "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(2) > div > table > tbody > tr > td:nth-child(2) > table > tbody > tr > td:nth-child(1) > table > tbody > tr > td:nth-child(2) > div"
        
        #Paths that require classes
        def bCheckSite(self):
            path = 'body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div > div > table > tbody > tr > td'
            p1 = parse.parse.returnClassName(self.m, path, 0)
            path2 = path + '.' + p1 + ' > table > tbody > tr > td'
            p2 = parse.parse.returnClassName(self.m, path2, 1)
            return path2 + '.' + p2 + ' > span'
            
        def bCaseTab(self):
            path = 'body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div > div > table > tbody > tr > td'
            p1 = parse.parse.returnClassName(self.m, path, 1)
            return path + '.' + p1 + ' > img:nth-child(1)'
        
        def bInventoryTab(self):
            path = 'body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div > div > table > tbody > tr > td'
            p1 = parse.parse.returnClassName(self.m, path, 1)
            return path + '.' + p1 + ' > img:nth-child(2)'
            
    #Adjustments Page
    class buildAdjustments():
        
        def __init__(self):
            self.g = get.openFile()
            self.adj = self.g.getAdjustmentPageData()
            
        def adjAdjustButton(self):
            path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(5) > div > div:nth-child(2) > div > div:nth-child(2) > div > table > tbody > tr > td"
            p1 = parse.parse.returnClassName(self.adj, path, 1)
            path2 = path + '.' + p1 + " > table > tbody > tr > td"
            p2 = parse.parse.returnClassName(self.adj, path2, 9)
            return path2 + '.' + p2 + " > span"

            
        def adjMenuQuantity(self):
            path = "body > div.gwt-PopupPanel > div > div > div > table > tbody > tr > td > div > div"
            p1 = parse.parse.returnClassName(self.adj, path, 1)
            path2 = path + '.' + p1 + " > div > table > tbody > tr:nth-child(1) > td > table > tbody > tr:nth-child(1) > td"
            p2 = parse.parse.returnClassName(self.adj, path2, 1)
            return path2 + '.' + p2 + " > input"
            
        def adjMenuNote(self):
            path = "body > div.gwt-PopupPanel > div > div > div > table > tbody > tr > td > div > div"
            p1 = parse.parse.returnClassName(self.adj, path, 1)
            path2 = path + '.' + p1 + " > div > table > tbody > tr:nth-child(1) > td > table > tbody > tr:nth-child(2) > td"
            p2 = parse.parse.returnClassName(self.adj, path2, 1)
            return path2 + '.' + p2 + " > textarea"
            
        def adjMenuCancelButton(self):
            path = "body > div.gwt-PopupPanel > div > div > div > table > tbody > tr > td > div > div"
            p1 = parse.parse.returnClassName(self.adj, path, 1)
            path2 = path + '.' + p1 + " > div > table > tbody > tr:nth-child(2) > td > table > tbody > tr > td"
            p2 = parse.parse.returnClassName(self.adj, path2, 0)
            path3 = path2 + '.' + p2 + " > span > div > div"
            p3 = parse.parse.returnClassName(self.adj, path3, 1)
            return path3 + "." + '.'.join(p3.split(' ')) 
            
        def adjMenuSaveButton(self):    
            path = "body > div.gwt-PopupPanel > div > div > div > table > tbody > tr > td > div > div"
            p1 = parse.parse.returnClassName(self.adj, path, 1)
            path2 = path + '.' + p1 + " > div > table > tbody > tr:nth-child(2) > td > table > tbody > tr > td:nth-child(2) > span > div > div"
            p2 = parse.parse.returnClassName(self.adj, path2, 1)
            return path2 + '.' + '.'.join(p2.split(' ')) 
            
    #User Page
    class buildUserPage(buildMainPaths):
        def __init__(self):
            super(buildPaths.buildUserPage, self).__init__()
            
        def uUser(self):
            path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div > div > table > tbody > tr > td"
            p1 = parse.parse.returnClassName(self.u, path, 2)
            path2 = path + '.' + p1 + " > table > tbody > tr > td"
            p2 = parse.parse.returnClassName(self.u, path2, 0)
            return path2 + '.' + p2 + " > span"
        
        def uUserSettingsButton(self):
            path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div > div > div > div"
            p1 = parse.parse.returnClassName(self.u, path, 0)
            path2 = path + '.' + p1 + " > table > tbody > tr:nth-child(1) > td:nth-child(2) > table > tbody > tr > td"
            p2 = parse.parse.returnClassName(self.u, path2, 2)
            return path2 + '.' + p2 + " > span"
            
        def uUserSettingsMenu(self):
            def saveButton():
                path = "body > div.gwt-PopupPanel > div > div > div > table > tbody > tr > td > div > div"
                p1 = parse.parse.returnClassName(self.u, path, 1)
                path2 = path + '.' + p1 + " > div > div > table > tbody > tr:nth-child(8) > td > table > tbody > tr > td:nth-child(2) > span > div > div"
                p2 = parse.parse.returnClassName(self.u, path2, 1)
                return path2 + "." + '.'.join(p2.split(' '))
            
            def listBoxSites():
                dict = {}
                path = "body > div.gwt-PopupPanel > div > div > div > table > tbody > tr > td > div > div"
                p1 = parse.parse.returnClassName(self.u, path, 1)
                path2 = path + '.' + p1 + " > div > div > table > tbody > tr:nth-child(1) > td"
                p2 = parse.parse.returnClassName(self.u, path2, 1)
                for i in range(52, 108):
                    path3 = path2 + '.' + p2 + " > select > option:nth-child(" + str(i + 1) + ")"
                    value = str(parse.parse.returnTextInfo(self.u, path3)[1])
                    name = (parse.parse.returnTextInfo(self.u, path3)[0]).split(' ')
                    name = ('_'.join(name)).rstrip('_' + name[-1])
                    if 'OSTEO' in name:
                        pass
                    else:
                        dict[name] = {'value': value, 'path': path3}
                return dict

            dict = {'listBoxSites': listBoxSites()}
            dict['listBoxSites']['saveButton'] = {'value': '0', 'path': saveButton()}

            return dict
          

    #StockTab
    class buildStockTab(buildMainPaths):
        def __init__(self):
            super(buildPaths.buildStockTab, self).__init__()
       
        def stStockTabButton(self):
            return "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(2) > div > table > tbody > tr > td:nth-child(2) > table > tbody > tr > td:nth-child(1) > table > tbody > tr > td:nth-child(2) > div"
        
        def stStockTabSearchButton(self):
            path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > table > tbody > tr > td:nth-child(1) > span > div > div"
            p1 = parse.parse.returnClassName(self.m, path, 1)
            return path + "." + '.'.join(p1.split(' '))
            
        def stStockTabResults(self):
            path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(2) > div > table > tbody > tr > td:nth-child(1) > div > table > tbody > tr > td > table > tbody > tr > td"
            p1 = parse.parse.returnClassName(self.m, path, 1)
            return path + "." + p1
            
        #Stock Tab Table
       
        #Checkboxes, because they are a pain in the ass, classes are different on odd and even rows
        def stTable_CheckBox_Init(self):
            path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(1) > td"
            p1 = parse.parse.returnClassName(self.m, path, 0)
            p1j = '.'.join(p1.split(' '))          
            return path + "." + p1j + " > div > span > img"
        
        def stTable_CheckBox_Row_Even(self):
            path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(2) > td"
            p1 = parse.parse.returnClassName(self.m, path, 0)
            p1j = '.'.join(p1.split(' '))  
            pathFront = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child("
            pathBack = ") > td." + p1j + " > div > span > img"
            return [pathFront, pathBack]
            
        def stTable_CheckBox_Row_Odd(self):
            path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(3) > td"
            p1 = parse.parse.returnClassName(self.m, path, 0)
            p1j = '.'.join(p1.split(' '))         
            pathFront = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child("
            pathBack = ") > td." + p1j + " > div > span > img"            
            return [pathFront, pathBack]
            
        #Table Data
        def stTableData(self):
            #Returns a dictionary of split css seletors which are meant to be joined with a row number in between. Ex; dict['product'][0] + str(number) + dict['product'][1]
            def dataDict():
                
                dict = {'product': ["body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(",
                            ") > td:nth-child(2) > span"],
                        'description': ["body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(",
                                        ") > td:nth-child(3) > div"],
                        'lot_serial': ["body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(",
                                       ") > td:nth-child(4) > div"],
                        'QOH': ["body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(",
                                ") > td:nth-child(7) > div"],
                        'QAV': ["body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(",
                                ") > td:nth-child(8) > div"],
                        'QR': ["body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(",
                               ") > td:nth-child(9) > div"],
                        'ZSMS_hold': zsms_Data(),
                        'location': location_Data(),
                        'contained_in': conatainedIn_Data()}  
                
                return dict
            
            def conatainedIn_Data():
                path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(1) > td:nth-child(5) > div > table > tbody > tr > td"
                
                p1 = parse.parse.returnClassName(self.m, path, 1)
                p2 = parse.parse.returnClassName(self.m, path, 0)
                
                pathFront = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child("
                pathBackInfo = ") > td:nth-child(5) > div > table > tbody > tr > td" + "." + p1 + " > span"
                pathBackType = ") > td:nth-child(5) > div > table > tbody > tr > td" + "." + p2
                pathInit = path + "." + p1
                return {'init': pathInit, 'front': pathFront, 'backInfo': pathBackInfo, 'backType': pathBackType}
            
            def location_Data():
                path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(1) > td:nth-child(6) > div > table > tbody > tr > td"
 
                p1 = parse.parse.returnClassName(self.m, path, 0)
                p2 = parse.parse.returnClassName(self.m, path, 1)
                pathFront = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(" 
                pathBackInfo = ") > td:nth-child(6) > div > table > tbody > tr > td" + "." + p2 + " > span"
                pathBackLocType = ") > td:nth-child(6) > div > table > tbody > tr > td" + "." + p1
                return {'front': pathFront, 'backInfo': pathBackInfo, 'backLocType': pathBackLocType}
             
            def zsms_Data():
                path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(1) > td"
                path2 = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(2) > td"
                path3 = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(3) > td"
                
                p1 = parse.parse.returnClassName(self.m, path, 9)
                p2 = parse.parse.returnClassName(self.m, path2, 9)
                p3 = parse.parse.returnClassName(self.m, path3, 9)
                
                pathInit = path + "." + '.'.join(p1.split(' ')) + " > div"
                pathFront = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child("
                pathBackEven = ") > td" + "." + p2 + " > div"
                pathBackOdd = ") > td" + "." + p3 + " > div"
                return {'init': pathInit, 'front': pathFront, 'backEven': pathBackEven, 'backOdd': pathBackOdd}
            
            return dataDict()
            
        
        def stMutate(self):
            
            def mutateButton():
                return "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > table > tbody > tr > td:nth-child(7) > table > tbody > tr > td > span"
                        
            def mutateQuantityBox():
                path = "body > div.gwt-PopupPanel > div > div > div > table > tbody > tr > td > div > div"
                p1 = parse.parse.returnClassName(self.m, path, 1)
                path2 = path + "." + p1 + " > div > table > tbody > tr:nth-child(1) > td > table > tbody > tr:nth-child(2) > td"
                p2 = parse.parse.returnClassName(self.m, path2, 1)
                return path2 + "." + p2 + " > input"
            
            def mutateNoteBox():
                path = "body > div.gwt-PopupPanel > div > div > div > table > tbody > tr > td > div > div"
                p1 = parse.parse.returnClassName(self.m, path, 1)
                path2 = path + "." + p1 + " > div > table > tbody > tr:nth-child(1) > td > table > tbody > tr:nth-child(4) > td"
                p2 = parse.parse.returnClassName(self.m, path2, 1)
                return path2 + "." + p2 + " > textarea"
            
            def mutateAllAvailableCheckBox():
                path = "body > div.gwt-PopupPanel > div > div > div > table > tbody > tr > td > div > div"
                p1 = parse.parse.returnClassName(self.m, path, 1)
                path2 = path + "." + p1 + " > div > table > tbody > tr:nth-child(1) > td > table > tbody > tr:nth-child(3) > td"
                p2 = parse.parse.returnClassName(self.m, path2, 1)
                return path2 + "." + p2 + " > div > span > img"
            
            def mutateSaveButton():
                path = "body > div.gwt-PopupPanel > div > div > div > table > tbody > tr > td > div > div"
                p1 = parse.parse.returnClassName(self.m, path, 1)
                path2 = path + "." + p1 + " > div > table > tbody > tr:nth-child(2) > td > table > tbody > tr > td:nth-child(2) > span > div > div"
                p2 = parse.parse.returnClassName(self.m, path2, 1)
                return path2 + "." + '.'.join(p2.split(' '))
                
            def mutateCancelButton():
                path = "body > div.gwt-PopupPanel > div > div > div > table > tbody > tr > td > div > div"
                p1 = parse.parse.returnClassName(self.m, path, 1)
                path2 = path + "." + p1 + " > div > table > tbody > tr:nth-child(2) > td > table > tbody > tr > td"
                p2 = parse.parse.returnClassName(self.m, path2, 0)
                path3 = path2 + "." + p2 + " > span > div > div"
                p3 = parse.parse.returnClassName(self.m, path3, 1)
                return path3 + "." + '.'.join(p3.split(' '))
                
            def mutateAlert():
                path = "body > div.gwt-PopupPanel > div > div > table > tbody > tr > td > div > table > tbody > tr > td > span > div > div"
                p1 = parse.parse.returnClassName(self.m, path, 1)
                return path + "." + '.'.join(p1.split(' '))
                
            def mutateError():
                path = "body > div:nth-child(13) > div > div > table > tbody > tr > td > div > table > tbody > tr > td > span > div > div"
                p1 = parse.parse.returnClassName(self.m, path, 1)
                return path + "." + '.'.join(p1.split(' '))

            def mutateMenu():
                dict = {'mutateButton': mutateButton(),
                        'mutateQuantity': mutateQuantityBox(),
                        'mutateNote': mutateNoteBox(),
                        'mutateAllAvailable': mutateAllAvailableCheckBox(),
                        'mutateSaveButton': mutateSaveButton(),
                        'mutateCancelButton': mutateCancelButton(),
                        'mutateAlert': mutateAlert(),
                        'mutateError': mutateError()}
                
                return dict
                
            return mutateMenu()
        
        #Case Page
        def cDistribution(self):
            
            def paybackOrders():
                path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(8) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > div > table > tbody > tr > td"
                p1 = parse.parse.returnClassName(self.c, path, 1)
                path2 = path + '.' + p1 + " > div:nth-child(1) > div"
                p2 = parse.parse.returnClassName(self.c, path2, 1)
                path3 = path2 + '.' + p2 + " > table > tbody > tr > td > table > tbody > tr:nth-child(5) > td"
                p3 = parse.parse.returnClassName(self.c, path3, 1)
                return path3 + '.' + p3 + " > table > tbody > tr > td > span"
                
            dict = {'cDistributionPaybackOrders': paybackOrders()}
            
            return dict
        
        #Case Page, Payback Order
        def cpbTableData(self):
            
            
            def checkBoxes():
                def initPath():
                    path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(5) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > div > div"
                    p1 = parse.parse.returnClassName(self.co, path, 2)
                    path2 = path + '.' + p1 + " > div > div"
                    p2 = parse.parse.returnClassName(self.co, path2, 1)
                    path3 = path2 + '.' + p2 + " > div > div > div:nth-child(2) > div"
                    p3 = parse.parse.returnClassName(self.co, path3, 1)
                    return path3 + '.' + p3

                def firstRow():
                    path = initPath() + " > div > table > tbody > tr:nth-child(1) > td"
                    p1 = parse.parse.returnClassName(self.co, path, 0)
                    return path + '.' + '.'.join(p1.split(' ')) + " > div > span > img"
                    
                def evenRow():
                    path = initPath() + " > div > table > tbody > tr:nth-child(2) > td"
                    p1 = parse.parse.returnClassName(self.co, path, 0)
                    front = initPath() + " > div > table > tbody > tr:nth-child("
                    back = ") > td" + '.' + p1 + " > div > span > img"
                    return {'front': front, 'back': back}
                    
                def oddRow():
                    path = initPath() + " > div > table > tbody > tr:nth-child(3) > td"
                    p1 = parse.parse.returnClassName(self.co, path, 0)
                    front = initPath() + " > div > table > tbody > tr:nth-child("
                    back = ") > td" + '.' + p1 + " > div > span > img"
                    return {'front': front, 'back': back}
                    
                dict = {'Init': firstRow(),
                        'Even': evenRow(),
                        'Odd': oddRow()}
                
                return dict
            
            def refNumber():
                path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(5) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > div > div"
                p1 = parse.parse.returnClassName(self.co, path, 2)
                path2 = path + '.' + p1 + " > div > div"
                p2 = parse.parse.returnClassName(self.co, path2, 1)
                path3 = path2 + '.' + p2 + " > div > div > div:nth-child(2) > div"
                p3 = parse.parse.returnClassName(self.co, path3, 1)
                front = path3 + '.' + p3 + " > div > table > tbody > tr:nth-child("
                back = ") > td:nth-child(2) > span"
                return {'Front': front,'Back': back}

            def product():
                path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(5) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > div > div"
                p1 = parse.parse.returnClassName(self.co, path, 2)
                path2 = path + '.' + p1 + " > div > div"
                p2 = parse.parse.returnClassName(self.co, path2, 1)
                path3 = path2 + '.' + p2 + " > div > div > div:nth-child(2) > div"
                p3 = parse.parse.returnClassName(self.co, path3, 1)
                front = path3 + '.' + p3 + " > div > table > tbody > tr:nth-child("
                back = ") > td:nth-child(3) > span"
                return {'Front': front,'Back': back}
                
            def description():
                path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(5) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > div > div"
                p1 = parse.parse.returnClassName(self.co, path, 2)
                path2 = path + '.' + p1 + " > div > div"
                p2 = parse.parse.returnClassName(self.co, path2, 1)
                path3 = path2 + '.' + p2 + " > div > div > div:nth-child(2) > div"
                p3 = parse.parse.returnClassName(self.co, path3, 1)
                front = path3 + '.' + p3 + " > div > table > tbody > tr:nth-child("
                back = ") > td:nth-child(4) > div"
                return {'Front': front,'Back': back}
            
            def qtyRequested():
                path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(5) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > div > div"
                p1 = parse.parse.returnClassName(self.co, path, 2)
                path2 = path + '.' + p1 + " > div > div"
                p2 = parse.parse.returnClassName(self.co, path2, 1)
                path3 = path2 + '.' + p2 + " > div > div > div:nth-child(2) > div"
                p3 = parse.parse.returnClassName(self.co, path3, 1)
                front = path3 + '.' + p3 + " > div > table > tbody > tr:nth-child("
                back = ") > td:nth-child(6) > div"
                return {'Front': front,'Back': back}

            def qtyOpen():
                path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(5) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > div > div"
                p1 = parse.parse.returnClassName(self.co, path, 2)
                path2 = path + '.' + p1 + " > div > div"
                p2 = parse.parse.returnClassName(self.co, path2, 1)
                path3 = path2 + '.' + p2 + " > div > div > div:nth-child(2) > div"
                p3 = parse.parse.returnClassName(self.co, path3, 1)
                front = path3 + '.' + p3 + " > div > table > tbody > tr:nth-child("
                back = ") > td:nth-child(7) > div"
                return {'Front': front,'Back': back}

            def qtyReserved():
                path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(5) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > div > div"
                p1 = parse.parse.returnClassName(self.co, path, 2)
                path2 = path + '.' + p1 + " > div > div"
                p2 = parse.parse.returnClassName(self.co, path2, 1)
                path3 = path2 + '.' + p2 + " > div > div > div:nth-child(2) > div"
                p3 = parse.parse.returnClassName(self.co, path3, 1)
                front = path3 + '.' + p3 + " > div > table > tbody > tr:nth-child("
                back = ") > td:nth-child(8) > div"
                return {'Front': front,'Back': back}

            def qtyOnMovement():
                path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(5) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > div > div"
                p1 = parse.parse.returnClassName(self.co, path, 2)
                path2 = path + '.' + p1 + " > div > div"
                p2 = parse.parse.returnClassName(self.co, path2, 1)
                path3 = path2 + '.' + p2 + " > div > div > div:nth-child(2) > div"
                p3 = parse.parse.returnClassName(self.co, path3, 1)
                front = path3 + '.' + p3 + " > div > table > tbody > tr:nth-child("
                back = ") > td:nth-child(9) > div"
                return {'Front': front,'Back': back}
            
            dict = {'cpbTableDataCheckBoxes': checkBoxes(),
                    'cpbTableDataRefNumber': refNumber(),
                    'cpbTableDataProductNumber': product(),
                    'cpbTableDataDescription': description(),
                    'cpbTableDataQTYRequested': qtyRequested(),
                    'cpbTableDataQTYOpen': qtyOpen(),
                    'cpbTableDataQTYReserved': qtyReserved(),
                    'cpbTableDataQTYOnMovement': qtyOnMovement()}
            
            return dict

            
        #Product Chooser
        def pcSelect(self):
            path = "body > div:nth-child(8) > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(6) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(3) > div > div > div > div:nth-child(1) > div:nth-child(2) > div"
            p1 = parse.parse.returnClassName(self.m, path, 1)            
            return path + '.' + p1 + " > table > tbody > tr > td > table > tbody > tr > td:nth-child(2) > span"
                
        def pcSearchBar(self):
            path = "body > div"
            p1 = parse.parse.returnClassName(self.m, path, 3)
            path2 = path + "." + p1 + " > div > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(2) > div > table > tbody > tr:nth-child(1) > td"
            p2 = parse.parse.returnClassName(self.m, path2, 0)
            return path2 + "." + p2 + " > input"
        
        def pcSearchButton(self):
            path = "body > div"
            p0 = parse.parse.returnClassName(self.m, path, 3)
            path0 = path + "." + p0 + " > div > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(2) > div > div:nth-child(2) > div > table > tbody > tr:nth-child(1) > td"
            p1 = parse.parse.returnClassName(self.m, path0, 1)
            path2 = path0 + '.' + p1 + "  > span > div > div"
            p2 = parse.parse.returnClassName(self.m, path2, 1)
            p2j = '.'.join(p2.split(' '))
            return path2 + '.' + p2j
            
        def pcFinishButton(self):
            path = "body > div"
            p1 = parse.parse.returnClassName(self.m, path, 3)
            path2 = path + "." + p1 + " > div > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(4) > div > div:nth-child(3) > div > table > tbody > tr > td"
            p2 = parse.parse.returnClassName(self.m, path2, 1)
            path3 = path2 + "." + p2 + " > span > div > div"
            p3 = parse.parse.returnClassName(self.m, path3, 1)
            p3j = '.'.join(p3.split(' '))
            return path3 + '.' + p3j

        def pcTable(self):
            path = "body > div"
            p1 = parse.parse.returnClassName(self.m, path, 3)
            path2 = path + "." + p1 + " > div > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div > table > tbody"
            return path2

        def pcAdd(self):
            path = "body > div"
            p1 = parse.parse.returnClassName(self.m, path, 3)
            path2 = path + "." + p1 + " > div > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div > table > tbody > tr > td"
            p2 = parse.parse.returnClassName(self.m, path2, 0)
            p2j = '.'.join(p2.split(' '))
            path3 = path2 + "." + p2j + " > div > table > tbody > tr > td > table > tbody > tr > td"
            p3 = parse.parse.returnClassName(self.m, path3, 0)
            return path3 + "." + p3 + " > span"

        def pcAddLast(self):
            path = "body > div"
            p1 = parse.parse.returnClassName(self.m, path, 3)
            path2 = path + "." + p1 + " > div > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(6) > td"
            p2 = parse.parse.returnClassName(self.m, path2, 0)
            p2j = '.'.join(p2.split(' '))
            path3 = path2 + "." + p2j + " > div > table > tbody > tr > td > table > tbody > tr > td"
            p3 = parse.parse.returnClassName(self.m, path3, 0)
            front = path + "." + p1 + "> div > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(" \
                                      "2) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(3) " \
                                      "> div > div:nth-child(3) > div > div > table > tbody > tr:nth-child( "
            back = ") > td" + "." + p2j + " > div > table > tbody > tr > td > table > tbody > tr > td" + "." + p3 + " > span"
            return [front, back]

        def pcAddFront(self):
            path = "body > div"
            p1 = parse.parse.returnClassName(self.m, path, 3)
            path2 = path + "." + p1 + " > div > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child("
            return path2 
        
        def pcAddOddBack(self):
            path = "body > div"
            p1 = parse.parse.returnClassName(self.m, path, 3)
            path2 = path + "." + p1 + " > div > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(2) > td"
            p2 = parse.parse.returnClassName(self.m, path2, 0)
            p2j = '.'.join(p2.split(' '))
            path3 = path2 + "." + p2j + " > div > table > tbody > tr > td > table > tbody > tr > td"
            p3 = parse.parse.returnClassName(self.m, path3, 0)
            return ") > td" + "." + p2j + " > div > table > tbody > tr > td > table > tbody > tr > td" + "." + p3 + " > span"
        
        def pcAddEvenBack(self):
            path = "body > div"
            p1 = parse.parse.returnClassName(self.m, path, 3)
            path2 = path + "." + p1 + " > div > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(3) > td"
            p2 = parse.parse.returnClassName(self.m, path2, 0)
            p2j = '.'.join(p2.split(' '))
            path3 = path2 + "." + p2j + " > div > table > tbody > tr > td > table > tbody > tr > td"
            p3 = parse.parse.returnClassName(self.m, path3, 0)
            return ") > td" + "." + p2j + " > div > table > tbody > tr > td > table > tbody > tr > td" + "." + p3 + " > span"
            
        def pcTableData(self):
            path = "body > div"
            p1 = parse.parse.returnClassName(self.m, path, 3)
            front = path + "." + p1 + " > div > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child("
            back = ") > td:nth-child(3) > div"
            return [front, back]
            
        def pcResults(self):
            path = "body > div"
            p1 = parse.parse.returnClassName(self.m, path, 3)
            path2 = path + "." + p1 + " > div > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(2) > div > table > tbody > tr > td > table > tbody > tr > td"
            p2 = parse.parse.returnClassName(self.m, path2, 1)
            return path2 + "." + p2

        def pcTRPaths(self):
            path = "body > div"
            p1 = parse.parse.returnClassName(self.m, path, 3)
            front = path + "." + p1 + " > div > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(2) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(3) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child("
            back = ")"
            return [front, back]
            
                
# b = buildPaths()
# bm = b.buildStockTab()
# print(bm.stMutate())
