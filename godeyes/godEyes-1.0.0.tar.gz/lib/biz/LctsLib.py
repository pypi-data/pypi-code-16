# coding:utf-8
'''
Created on 2016年02月09日

@author: shenlang
'''

from common.Cli import Cli
import time

 
class LctsLib(Cli): 
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
     
    def showScreensaver(self,ip=None):
        self.adb_shell('settings put system screensaver_starttime 1000',ip=ip)
        self.pressHome(1, 1, ip)
        
    def closeScreensaver(self,ip=None): 
        self.adb_shell('settings put system screensaver_starttime 864000000',ip=ip)  
        self.pressHome(1, 1, ip)
        
    def RestoreEnv(self,ip=None): 
        self.pressHome(1, 1, ip)
        time.sleep(3)
        self.adb_shell('am force-stop com.yunos.tv.tvosd',ip=ip)
        time.sleep(5)
        self.adb_shell('am force-stop com.yunos.tv.homeshell',ip=ip)
        time.sleep(2)
        topActivity = self.getTopActivity(ip)
        if topActivity == 'com.yunos.tv.homeshell.activity.MainActivity':
            print("Restore Env success!")
            return True
        else:
            return False
 
    def firstGotoHome(self,ip=None):
        self.adb_shell('pm clear com.yunos.tv.homeshell',ip=ip)
        time.sleep(2)  
        self.pressRight(4,1,ip)
        self.waitForTopActivity('com.yunos.tv.homeshell.activity.MainActivity',ip)
        time.sleep(30)
        temp_txt = self.getPageText(ip)
        if temp_txt == "":
            self.pressBack(1,1, ip)    
                

if __name__ == '__main__':
    ic = LctsLib('30.11.32.134')
#     ic.showScreensaver()
    ic.closeScreensaver()
 
