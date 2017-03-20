# coding:utf-8
'''
Created on 2016年11月5日

@author: shenlang
'''
import urllib2
import subprocess
import signal
import os
import time
import platform
from robot.libraries.BuiltIn import logger


baseUrl = 'http://127.0.0.1'


def log(level, msg):
    if level == 'error':
        logger.error(msg, html=True)
    elif level == 'warn':
        logger.warn(msg, html=True)
    elif level == 'info':
        logger.info(msg, html=True)
    elif level == 'debug':
        logger.debug(msg, html=True)
    elif level == 'trace':
        logger.trace(msg, html=True)


class AppiumService:
    
    def __init__(self):
        self.processDic = {}
        
    def __del__(self):
        self.stopServer()
        self.processDic.clear()
    
    def isRunnnig(self,port=4723):
        """Determine whether server is running
        :return:True or False
        """
        response = None
        url = baseUrl+ ':' + str(port) + "/wd/hub/status"
        try:
            response = urllib2.urlopen(url, timeout=5)
 
            if str(response.getcode()).startswith("2"):
                return True
            else:
                return False
        except:
            return False
        finally:
            if response:
                response.close()
                
                
    def startServer(self,port=4723):
        if not self.processDic.has_key(port):
            cmd = 'appium'
            if port != 4273:
                cmd = cmd + ' -p %d' % port
            cmd = cmd + ' --no-reset'
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.processDic[port] = process
        ret = False
        for i in range(1, 6):
            log('info','query appium service isRunning times:%d' % i)
            time.sleep(1)
            isRunning = self.isRunnnig(port)
            if isRunning:
                log('info','Appium Service start success!!!') 
                ret = True
                break
        if not ret:
            log('warn','Appium Service start fail!!!') 
    
    
    def killProcess(self, process):
        
        if platform.system().lower() == 'windows':
            st=subprocess.STARTUPINFO
            st.dwFlags=subprocess.STARTF_USESHOWWINDOW
            st.wShowWindow=subprocess.SW_HIDE
            cmd = "TASKKILL /F /PID {pid} /T".format(pid=process.pid)
            subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE,startupinfo=st)
        else:
            os.kill(process.pid,signal.SIGKILL)
             
    def stopServer(self,port=0):
        if port:
            if self.processDic.has_key(port):
                p = self.processDic[port]
                self.killProcess(p.pid,signal.SIGKILL)
                self.processDic.pop(port)
        else:
            if len(self.processDic) > 0:
                for i in self.processDic.keys():
                    
                    self.killProcess(self.processDic[i])     
                         
                    self.processDic.pop(i)
                    
    
    

    
    
if __name__ == '__main__':
    appiumService = AppiumService()
    appiumService.startServer()
    time.sleep(10)
    appiumService.stopServer()

