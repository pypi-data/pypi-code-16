# coding:utf-8
'''
Created on 2017年01月03日

@author: shenlang
'''

from common.Cli import Cli
import time
 
class ShaoerLib(Cli): 
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
     
    def firstGotoDetail(self,ip=None):
        self.adb_shell("pm clear com.yunos.tv.edu",ip=ip) 
        time.sleep(5)
        topActivity = self.getTopActivity(ip)
        if topActivity == 'com.yunos.tv.edu.activity.ChildLauncherActivity':
            self.inputKeyEvent(22, ip)
            self.inputKeyEvent(22, ip)
            self.waitForTopActivity('com.yunos.tv.edu.activity.ChildLauncherActivity',ip)
            time.sleep(5)
            self.adb_shell("am start -W -a android.intent.action.VIEW -d tv_child://child_manager?from=com.yunos.tv.edu_launcher",ip=ip)
            time.sleep(5)
            self.inputKeyEvent(3, ip)
            self.waitForTopActivity('com.yunos.tv.edu.activity.ChildLauncherActivity',ip)
            time.sleep(5)
            
# 
# def aaa():
#     Cli.getUUID()
if __name__ == '__main__':
    l = ShaoerLib('192.168.0.117')
    print l.firstGotoShaoErDetail()
