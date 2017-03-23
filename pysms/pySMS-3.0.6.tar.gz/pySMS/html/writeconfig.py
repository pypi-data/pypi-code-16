# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 14:35:05 2016

@author: doarni
"""

import os
import json

try:
    from build import buildPaths
except:
    from pySMS.html.build import buildPaths


#===============================================================================================

class writer():
   
    def __init__(self):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.bl = buildPaths.buildLoginPaths()
        self.bm = buildPaths.buildMainPaths()
        self.bs = buildPaths.buildStockTab()
        self.bu = buildPaths.buildUserPage()
        self.ba = buildPaths.buildAdjustments()
        self.dict = {}

    #CSS Path builders, called when correct page html is saved. Return dicts of paths
    def loginPage(self):
        dict = {'url': "http://www.zimmersms.com",
                'username': self.bl.bUsername(),
                'password': self.bl.bPassword(),
                'loginbutton': self.bl.bLoginButton()}
        return dict
    def mainPage(self):
        dict = {'CaseTab': self.bm.bCaseTab(),
                'InventoryTab': self.bm.bInventoryTab(),
                'checkSite': self.bm.bCheckSite()}
        return dict
    def prodChooserPage(self):
        dict = {'prodchooserSelect': self.bs.pcSelect(),
                'prodchooserSearchButton': self.bs.pcSearchButton(),
                'prodchooserSearchBar': self.bs.pcSearchBar(),
                'prodchooserFinishButton': self.bs.pcFinishButton(),
                'prodchooserAdd': self.bs.pcAdd(),
                'prodChooserAddLastFront': self.bs.pcAddLast()[0],
                'prodChooserAddLastBack': self.bs.pcAddLast()[1],
                'prodChooserAddFront': self.bs.pcAddFront(),
                'prodChooserAddOddBack': self.bs.pcAddOddBack(),
                'prodChooserAddEvenBack': self.bs.pcAddEvenBack(),
                'prodChooserDescFront': self.bs.pcTableData()[0],
                'prodChooserDescBack': self.bs.pcTableData()[1],
                'prodChooserResults': self.bs.pcResults(),
                'prodChooserTableData': self.bs.pcTable(),
                'prodChooserTRpathFront': self.bs.pcTRPaths()[0],
                'prodChooserTRpathBack': self.bs.pcTRPaths()[1]}

        return dict

    def stockTab(self):
        dict = {'stStockTabButton': self.bs.stStockTabButton(),
                'stStockTabSearchButton': self.bs.stStockTabSearchButton(),
                'stStockTabResults': self.bs.stStockTabResults()}        
        return dict
        
    def stockTabTable(self):
        d = self.bs.stTableData()
        dict = {'stTableProductFront': d['product'][0],
                'stTableProductBack': d['product'][1],
                'stTableDescriptionFront': d['description'][0],
                'stTableDescriptionBack': d['description'][1],
                'stTableLotSerialFront': d['lot_serial'][0],
                'stTableLotSerialBack': d['lot_serial'][1],
                'stTableQOHFront': d['QOH'][0],
                'stTableQOHBack': d['QOH'][1],
                'stTableQAVFront': d['QAV'][0],
                'stTableQAVBack': d['QAV'][1],
                'stTableQRFront': d['QR'][0],
                'stTableQRBack': d['QR'][1],
                'stTableContainerInit': d['contained_in']['init'],
                'stTableContainerFront': d['contained_in']['front'],
                'stTableContainerBackInfo': d['contained_in']['backInfo'],
                'stTableContainerBackType': d['contained_in']['backType'],
                'stTableLocationFront': d['location']['front'],
                'stTableLocationBackInfo': d['location']['backInfo'],
                'stTableLocationBackLocType': d['location']['backLocType'],
                'stTableZSMSHoldInit': d['ZSMS_hold']['init'],
                'stTableZSMSHoldFront': d['ZSMS_hold']['front'],
                'stTableZSMSHoldBackEven': d['ZSMS_hold']['backEven'],
                'stTableZSMSHoldBackOdd': d['ZSMS_hold']['backOdd'],
                'stTableCheckBoxInit': self.bs.stTable_CheckBox_Init(),
                'stTableCheckBoxRowEvenFront': self.bs.stTable_CheckBox_Row_Even()[0],
                'stTableCheckBoxRowEvenBack': self.bs.stTable_CheckBox_Row_Even()[1],
                'stTableCheckBoxRowOddFront': self.bs.stTable_CheckBox_Row_Odd()[0],
                'stTableCheckBoxRowOddBack': self.bs.stTable_CheckBox_Row_Odd()[1]}
        
        return dict
    
    def stockTableMutate(self):
        d = self.bs.stMutate()
        dict = {'stMutateButton': d['mutateButton'],
                'stMutateQuantity': d['mutateQuantity'],
                'stMutateNote': d['mutateNote'],
                'stMutateAllAvailable': d['mutateAllAvailable'],
                'stMutateSavebutton': d['mutateSaveButton'],
                'stMutateCancelButton': d['mutateCancelButton'],
                'stMutateAlert': d['mutateAlert'],
                'stMutateError': d['mutateError'],
                'stnote': 'CI-ZDI Mutation, Loaners Late Debit Policy'}  
        return dict

    def userSettings(self):
        d = self.bu.uUserSettingsMenu()
        dictMain = {}
        dictMain['upUser'] = self.bu.uUser()
        dictMain['upSaveButton'] = d['listBoxSites']['saveButton']['path']
        dictMain['upUserSettingsButton'] = self.bu.uUserSettingsButton()
        return dictMain

    def userSettingsSites(self):
        d = self.bu.uUserSettingsMenu()
        return d

    def adjustStock(self):  
        dict = {'adjAdjustButton': self.ba.adjAdjustButton(),
                'adjMenuQuantity': self.ba.adjMenuQuantity(),
                'adjMenuNote': self.ba.adjMenuNote(),
                'adjMenuCancelButton': self.ba.adjMenuCancelButton(),
                'adjMenuSaveButton': self.ba.adjMenuSaveButton()}
        
        return dict
    #Config writers, make py files and ini files    
                              
    def writeJsonFromListOfDict(self, list, filename):
        with open(self.path + '\\pathdata\\json\\' + filename + '.json', 'w') as fp:
            for dict in list:
                json.dump(dict, fp, sort_keys=True, indent=4)                

    def writeConfigFromListOfDict(self, list, filename):
        with open(self.path + '\\pathdata\\' + filename + '.py', 'w') as configfile:
            for dict in list:
                for key, value in dict.items():
                    print('Writing Key: ' + key + ' Value: {!s} \n'.format(str(value)))
                    configfile.write(key + ' = ' + "'" + value + "'" + '\n')
                
    def writeConfigWithDictionary(self, list):
        with open('htmlpaths.py', 'w') as configfile:
            for dict in list:
                for key, value in dict.items(): 
                    print('Writing Key: ' + key + ' Value: {!s} \n'.format(str(value)))
                    configfile.write(key + ' = ' + "'" + value + "'" + '\n')
 
#===============================================================================================


w = writer()

def makeloginPageConfig():
    list = []
    print('Preparing Login Config \n')
    list.append(w.loginPage())
    w.writeConfigFromListOfDict(list, 'loginPage')
    w.writeJsonFromListOfDict(list, 'loginPage')

def makemainPageConfig():
    list = []
    print('Preparing Main Page Config \n')
    list.append(w.mainPage())
    w.writeConfigFromListOfDict(list, 'mainPage')
    w.writeJsonFromListOfDict(list, 'mainPage')


def makeprodChooserPageConfig():
    list = []
    print('Preparing ProdChooser Config \n')
    list.append(w.prodChooserPage())
    w.writeConfigFromListOfDict(list, 'prodChooser')
    w.writeJsonFromListOfDict(list, 'prodChooser')

def makestockTabTableConfig():
    list = []
    print('Preparing Stock Tab Table Config \n')
    list.append(w.stockTabTable())    
    w.writeConfigFromListOfDict(list, 'stockTabTable')
    w.writeJsonFromListOfDict(list, 'stockTabTable')


def makestockTableMutateConfig():
    list = []
    print('Preparing Mutation Config \n')
    list.append(w.stockTableMutate())  
    w.writeConfigFromListOfDict(list, 'stockTabMutate')
    w.writeJsonFromListOfDict(list, 'stockTabMutate')


def makestockTabConfig():
    list = []
    print('Preparing Stock Tab Config \n')
    list.append(w.stockTab())  
    w.writeConfigFromListOfDict(list, 'stockTab')
    w.writeJsonFromListOfDict(list, 'stockTab')


def makeuserSettingsConfig():
    list = []
    print('Preparing User Settings Config \n')
    list.append(w.userSettings())
    w.writeConfigFromListOfDict(list, 'userSettings')
    w.writeJsonFromListOfDict(list, 'userSettings')

 
def makeuserSettingsSitesConfig():
    list = []
    list.append(w.userSettingsSites())
    w.writeJsonFromListOfDict(list, 'siteSettings')

  
def makeadjustStockConfig():
    list = []
    print('Preparing Adjustments Config \n')
    list.append(w.adjustStock())
    w.writeConfigFromListOfDict(list, 'adjustStock')
    w.writeJsonFromListOfDict(list, 'adjustStock')



#===============================================================================================

    
if __name__ == '__main__':
    # makemainPageConfig()

   # makeadjustStockConfig()
#    makeprodChooserPageConfig()
#    makestockTableMutateConfig()
#     makestockTabConfig()
#     makestockTabTableConfig()

#    makeuserSettingsConfig()
   makeloginPageConfig()
#    makeuserSettingsSitesConfig()