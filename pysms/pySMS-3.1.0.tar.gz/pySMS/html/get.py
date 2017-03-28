# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 13:16:34 2016

@author: doarni
"""

import os

class openFile():
    def __init__(self):   
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.loginData = None
        self.mainData = None
        self.caseData = None
        self.orderData = None
        self.orderpagelineData = None
        self.userpageData = None
        self.adjustmentsPageData = None
        self.htmlFiles = ['login.html','main.html', 'casepage.html', 'orderpage.html','orderpageline.html','userpage.html', 'adjustment.html']

    def loadFiles(self):
#        os.chdir('..')
#        os.chdir(self.path)
        with open(self.path + '\\login.html','r') as f:
            self.loginData = f.read().replace('\n','')
        with open(self.path + '\\main.html','r') as f:
            self.mainData = f.read().replace('\n','')
            
    def getLoginData(self):
        return self.loginData
        
    def getMainData(self):
        return self.mainData
        
    def getCaseData(self):
        with open(self.path + '\\casepage.html', 'r') as f:
            self.caseData = f.read().replace('\n','')
        return self.caseData
    
    def getOrderData(self):
        with open(self.path + '\\orderpage.html', 'r') as f:
            self.orderData = f.read().replace('\n','')
        return self.orderData
        
    def getOrderLineData(self):
        with open(self.path + '\\orderpageline.html', 'r') as f:
            self.orderpagelineData = f.read().replace('\n','')
        return self.orderpagelineData
        
    def getUserPageData(self):
        with open(self.path + '\\userpage.html', 'r') as f:
            self.userpageData = f.read().replace('\n','')
        return self.userpageData
        
    def getAdjustmentPageData(self):
        with open(self.path + '\\adjustment.html', 'r') as f:
            self.adjustmentsPageData = f.read().replace('\n','')
        return self.adjustmentsPageData
    
    def cleanUp(self):
        os.system("")
        
if __name__ == '__main__':
    filelist = ['login.html',
                'main.html',
                'orderpage.html',
                'orderpageline.html',
                'casepage.html',
                'userpage.html']
    for file in filelist:
        if os.path.isfile(file) == False:
            with open(file, 'w')as f:
                f.close()
