# coding:utf-8
'''
Created on 2017年02月09日

@author: shenlang
'''

from common.Cli import Cli
 
class IcLib(Cli): 
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
     
    def showScreensaver(self,ip=None):
        self.adb_shell('settings put system screensaver_starttime 1000',ip=ip)
        self.pressHome(1, 1, ip)
        
    def closeScreensaver(self,ip=None): 
        self.adb_shell('settings put system screensaver_starttime 864000000',ip=ip)  
        self.pressHome(1, 1, ip)
    
            

if __name__ == '__main__':
    ic = IcLib('30.11.32.134')
#     ic.showScreensaver()
    ic.closeScreensaver()
 
