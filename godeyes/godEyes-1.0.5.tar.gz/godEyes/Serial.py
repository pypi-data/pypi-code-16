# coding:utf-8
'''
Created on 2017年2月13日

@author: shenlang
'''
import serial
import time
import sys
import os
import Util
from multiprocessing import Process
import signal
import json
import re

from Validator import validator
from globalVal import rootdir, TAG
from robot.libraries.BuiltIn import logger


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

class Serial(object):
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, port=0):
        if port:
            self.port = serial.Serial(port=port, baudrate=115200)
        else:
            self.port = None
        self.prefix = None
        self.logcatProcessList= []
        self.deviceModelDict = {}
        self.systemVersionDict = {}
        self.uuidDict = {}
        
    def signal(self, sig, timeout=2):
        self.write(chr(sig))
        return self.readall(timeout)
    
    
    
    
    def set_prefix(self):
        if not self.prefix:
            self.input('echo', timeout=0.3)
            self.prefix = self.input(timeout=0.3).strip()
            self.s_shell('echo 0 > /proc/sys/kernel/printk')
    
    def s_shell(self, cmd='',splitlines=False, pattern=None):
        self.set_prefix()
        self.write(cmd)
        result = ''
        retry = 1000
        while retry > 0:
            retry -= 1
            size = self.port.inWaiting()
            if size == 0:
                time.sleep(0.1)
            else:
                data = self.port.read(size)
                result += data
                if self.prefix in result:
                    break
        print result
        result = result.replace(cmd, '').replace(self.prefix, '').strip()
        if splitlines:
                result = result.splitlines()
        
        if pattern:
            p = re.compile(pattern)
            result = p.findall(result)
            if len(result) == 1:
                result = result[0]
        
        return result
    
    def d_shell(self, cmd='', duration=10):
        self.set_prefix()
        self.write(cmd)
        result = ''
        while duration > 0:
            size = self.port.inWaiting()
            if size == 0:
                time.sleep(0.1)
                duration -= 0.1
            else:
                data = self.port.read(size)
                result += data
                if self.prefix in result:
                    break
        print result
        if duration > 0:
            raise Exception(result.replace(cmd, '').replace(self.prefix, '').strip())
        self.signal(3)
        self.input('echo', timeout=0.3)
    
        
    def input(self, cmd='', timeout=2):
        self.write(cmd)
        return self.readall(timeout=timeout)
    
 
    def wait_startup(self, timeout=900):
        console_log = ''
        t = time.time()
        while True:
            if time.time() - t > timeout:
                return False
            console_log += self.readall(3)
            if "dhcpcd" in console_log:
                time.sleep(30)
                return True
            if '938_dev' in self.build_type:
                if "TVOS *checkPoint*" in console_log:
                    time.sleep(60)
                    return True

    
  
    
    def uboot(self):
        self.write('reboot')
        for unused in range(300):
            time.sleep(0.01)
            self.write()
        self.readall()
        
    def write(self, cmd=''):
        return self.port.write(str(cmd) + '\n')
        
    def read(self):
        size = self.port.inWaiting()
        data = self.port.read(size)
        print data
        return data
    
    
    
    def readall(self, timeout=1):
        result = ''
        cur = time.time()
        while True:
            size = self.port.inWaiting()
            if size == 0:
                if time.time() - cur > timeout:
                    break
                time.sleep(0.1)
            else:
                cur = time.time()
                data = self.port.read(size)
                sys.stdout.write(data)
                logger.console(data, newline=False)
                result += data
        sys.stdout.write(os.linesep)
        sys.stdout.flush()
        logger.console('')
        return result
    
    def reboot(self):
        pid1 = self.s_shell('ps | grep system_server')
        self.s_shell('reboot')
        time.sleep(30)
        pid2 = self.s_shell('ps | grep system_server')
        assert pid1 <> pid2,'system_server pid在重启后发生变化'
    
    def inputKeyEvent_M(self):
        pass
    
    def clearLogcatCacheBySerial(self):
        self.write('logcat -c')
        
   
    
    def runLogcat(self,logcatName):
        cmd = 'logcat -v time *:I'
        self.write(cmd)
    
        while True:      
            data = self.port.readline()
            if data == '\n':
                break;
            if 'logcat -c' in data or 'logcat -v time' in data:
                continue
            with open(logcatName, 'a') as f:
                f.write(data)
    
    
    def startLogcatBySerial(self):
        
        self.clearLogcatCache()
        ctime = Util.getCTime()
        
        logcatDir = ''.join((rootdir,os.path.sep,'logs'))
        print 'logcatDir:%s' % logcatDir
        portName = self.port.port.replace(os.sep,'_')
        logcatName=logcatDir+ os.path.sep +"logcat" + ctime+ "_" +portName +".log"
        print "logcatname:%s" % logcatName

        logcatProcess = Process(target=self.runLogcat,args=(logcatName,))
        logcatProcess.daemon = True
        logcatProcess.start()
#         logcatProcess.join(3)
         
        self.logcatProcessList.append(logcatProcess)
#         self.runLogcat(logcatName)
        return logcatName
        
    def stopLogcatBySerial(self,waitTime=0):
        if waitTime > 0:
            time.sleep(waitTime)
        
        
        if len(self.logcatProcessList) > 0:
            for p in self.logcatProcessList:
                    os.kill(p.pid,signal.SIGKILL)
            self.logcatProcessList = [] 
    
    def getFormatLogListBySerial(self,logcatPath,pageName,eventId,arg1='',beginTime=0L,endTime=0L,needSequenceCheck=True,customFilter='',pid=''):
        
        utLogList,utVersion = Util.readFile(logcatPath,pageName,eventId,arg1,beginTime,endTime,customFilter,pid)
        print TAG + 'utVersion:' + str(utVersion)
        if utVersion < 5:
            needSequenceCheck = False
            
        initialPostLogList = Util.sequenceCheckUtLog(utLogList,eventId,arg1, needSequenceCheck)
        print '%sinitialPostLogList:%s' % (TAG,initialPostLogList)
        
        formatLogList = []
        for initialPostLog in initialPostLogList:
            formatLog = Util.formatUTLog(initialPostLog)
            print '%sformatLog:%s' % (TAG,formatLog)
            formatLogList.append(formatLog)
        
        return formatLogList
    
    
    def getDeviceModelBySerial(self, useCache=True):
        port = self.getPort()
        if self.deviceModelDict.has_key(port) and useCache:
            pass
        else:
            self.deviceModelDict[port] = self.s_shell('getprop ro.product.model')   
        return self.deviceModelDict[port]
    
    
    def getResolutionBySerial(self):
        ret = self.s_shell('wm size')
        if 'x' in ret:
            return ret.split('Physical size:')[1].lstrip().replace('x','*')
        else:
            ret = self.s_shell('dumpsys window | grep cur=',pattern=r'cur=(.*) app')
            print ret
            if type(ret) == 'list':
                return ret[0].replace('x','*')
            return ret.replace('x','*')
    
    def changePort(self,port):
        cPort = self.getPort()
        if cPort != port:
            self.port.port(port)    
    
    def getNetTypeBySerial(self):
        rets = self.s_shell('netcfg',splitlines=True)
        netTypeList = []
        for ret in rets:
            if 'UP' in ret and 'lo' not in ret and '0.0.0.0' not in ret:
                if ret.startswith('eth'):
                    netTypeList.append('WiredNetwork')
                elif ret.startswith('wlan'):
                    netTypeList.append('Wi-Fi')
                else:
                    netTypeList.append('other')
        
        if len(netTypeList) > 1:
            return 'Unknown'
        else:
            return netTypeList[0] 
    
    def getBrandBySerial(self,port=None):
        
        
        return self.s_shell('getprop ro.product.brand')
    
    
    def getWifiMacBySerial(self):
        rets = self.s_shell('netcfg',splitlines=True)
        mac = '00:00:00:00:00:00'
        if self.getNetTypeBySerial() == 'Unknown':
            return mac
        print rets
        for ret in rets:
            if ret.startswith('wlan') and '00:00:00:00:00:00' not in ret:
                m = re.search(r"[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}", ret)
                if m:
                    mac = m.group()   
        return mac
    
    def getBSSIDBySerial(self,retryTimes=3):
        bssid = '00:00:00:00:00:00'
        if(retryTimes <= 0): 
            return bssid
        
        ret = self.s_shell('dumpsys wifi | grep BSSID',pattern=r"BSSID\: ([a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}),")
        if ret:
            if isinstance(ret, list):
                bssid = ret[0]  
            else:
                bssid = ret
        elif isinstance(ret, list) and len(ret) == 0:
            time.sleep(2)
            self.getBSSIDBySerial(retryTimes-1)
            
        return bssid 
    
    
    def getAppVersionCodeBySerial(self,packageName,ip=None):
                
        if packageName is None:
            return ''  
        rets = self.s_shell('dumpsys package %s | grep versionCode' % packageName,ip=ip,pattern=r'versionCode=(\d*)') 
        if type(rets) == list:
            return max(rets)
        else:
            return rets
    
    
    def getAppVersionNameBySerial(self,packageName):
        if packageName is None:
            return ''  
        rets = self.s_shell('dumpsys package %s | grep versionCode' % packageName, pattern=r'versionCode=(\d*)') 
        if type(rets) == list:
            return max(rets)
        else:
            return rets
    
    def getReleaseVersionBySerial(self,useCache=True):
        port = self.getPort()
        if self.systemVersionDict.has_key(port) and useCache:
            pass
        else:     
            self.systemVersionDict[port] = self.s_shell('getprop ro.build.version.release')
        return self.systemVersionDict[port]
    
    def getAbiBySerial(self):
        return self.s_shell('getprop ro.product.cpu.abi')
    
    def hasWifiBySerial(self):
        rets = self.s_shell('netcfg',splitlines=True)
        flag = False
        for ret in rets: 
            if ret.startswith('wlan'):
                return True
        return flag 
    
    def getPort(self):
        return self.port.port
    
    def getUUIDBySerial(self,useCache=True):
        port = self.getPort()
        if self.uuidDict.has_key(port) and useCache:
            pass
        else:
            self.uuidDict[port] = self.s_shell('getprop ro.aliyun.clouduuid')
               
        return self.uuidDict[port]
    
    def getTimeStampfromDeviceBySerial(self):
        t = self.s_shell('date +%s000')
        return long(t) 
    
    def get_app_pid_by_serial(self,appPackageName):
        ps = self.s_shell('ps | grep %s' % appPackageName)
        p = re.compile(r'^\w+\s+(\d+)\s.+\s%s$' % appPackageName, re.M)
        pids = p.findall(ps)
        return pids
    
    def checkPostLogBySerial(self,formatLog,packageName,pageName,eventId,arg1=None,ignoreSessionInfo=False, commonParamsValidatorDict=None, **kwargs):
        brand = self.getBrandBySerial()
        deviceModel = self.getDeviceModelBySerial()
        resolution = self.getResolutionBySerial()
        netType = self.getNetTypeBySerial()
        if netType == 'WiredNetwork':
            access = 'Unknown'
            
        else:  
            access = netType
        
        mac = self.getWifiMacBySerial()
        bssid = self.getBSSIDBySerial()   
        appVersionName = self.getAppVersionNameBySerial(packageName)
        osVersion = self.getReleaseVersionBySerial()   
             
        abi = self.getAbiBySerial()
        if self.hasWifiBySerial():
            did = self.getUUIDBySerial(True)
        else:
            did = 'false'
        
        endTime = self.getTimeStampfromDeviceBySerial()
        
        #时间戳比较在时间范围，运行用例前校验sessionInfo
        
        
           
        try:   
            
            validator.validate(formatLog, _sessionInfo_brand=brand,_sessionInfo_deviceModel=deviceModel,_sessionInfo_resolution=resolution,_sessionInfo_access=access,_sessionInfo_appVersionName=appVersionName,_sessionInfo_osVersion=osVersion,_sessionInfo_timestamp__lt=endTime) 
            extraJson = '{"_mac": "%s","_did": "%s"}' % (mac,did)
            extraJson = {}
            extraJson['_mac'] = mac
            extraJson['_did'] = did
            
            if '_bssid' in formatLog:
                extraJson['_bssid'] = bssid
            if '_abi' in formatLog: 
                extraJson['_abi'] = abi
            extraJsonStr = json.dumps(extraJson)
            validator.validate(formatLog,_sessionInfo_extra__include=extraJsonStr)
        
        except AssertionError, e:
            if ignoreSessionInfo:
                log('warn',e)
            else:
                raise
        
        validator.validate(formatLog,_businessInfo_eventId=eventId,_businessInfo_pageName=pageName)
        
        if arg1:
            validator.validate(formatLog,_businessInfo_arg1=arg1)
        
        if commonParamsValidatorDict and len(commonParamsValidatorDict) > 0:
            kwargs=dict(commonParamsValidatorDict, **kwargs)
        
        if len(kwargs) > 0:
            validator.validate(formatLog, **kwargs)
        
    
    def checkUTLogWithFileBySerial(self,logcatPath,appPackageName,pageName,eventId,arg1='',beginTime=0L,endTime=0L,customFilter='',pid='',ignoreSessionInfo=False, commonParamsValidatorDict=None, **kwargs):
        if not pid:
            pids = self.get_app_pid_by_serial(appPackageName)
            if pids:
                pid = pids[0]
        
        
        formatLogList = Util.getFormatLogList(logcatPath,pageName,eventId,arg1,beginTime,endTime,customFilter=customFilter,pid=pid)

        l = len(formatLogList)
        assert l == 1,'actual has post count:%d' % l
        self.checkPostLogBySerial(formatLogList[0],appPackageName,pageName,eventId,arg1,ignoreSessionInfo=ignoreSessionInfo, commonParamsValidatorDict=commonParamsValidatorDict, **kwargs)
#         self._getUTDataFromServer(dk, str(eventId), pageName,**kvArgs)
        print TAG + 'CHECK PASS!!!'
    
    
    def checkUTLogBySerial(self,logcatPath,appPackageName,pageName,eventId,arg1='',beginTime=0L,endTime=0L,customFilter='',ignoreSessionInfo=False, commonParamsValidatorDict=None, **kwargs):
        self.stopLogcatBySerial()
        
        formatLogList = Util.getFormatLogList(logcatPath,pageName,eventId,arg1,beginTime,endTime,customFilter=customFilter)

        if len(formatLogList) == 1:
            formatLog = formatLogList[0]
            self.checkPostLogBySerial(formatLog,appPackageName,pageName,eventId,arg1,ignoreSessionInfo=ignoreSessionInfo, commonParamsValidatorDict=commonParamsValidatorDict, **kwargs)
            print TAG + 'CHECK PASS!!!'
    
    
if __name__ == '__main__':
    s = Serial('/dev/tty.SLAB_USBtoUART')
    ret = s.get_app_pid_by_serial('com.yunos.tv.homeshell')
    print ret
#     s.input('ps')
#     print s.execCommand('ps | grep net')
#     print s.port.readline()
#     ret ='' 
#     print ret
#     print s.execCmd('netcfg');
#     ret = s.execCmd('dumpsys wifi | grep BSSID',pattern=r"BSSID\: ([a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}),")
#     print ret
#     a =  s.getBSSIDBySerial()
#     print a

#     print s.startLogcat()
#     print 'do'
#     time.sleep(10)
#     print 'fuck'
#     s.stopLogcat()
#     print 'oh ye'
#     ctime = Util.getCTime()
#         
#     logcatDir = ''.join((rootdir,os.path.sep,'logs'))
#     print 'logcatDir:%s' % logcatDir
#     ip = s.port.port.replace(os.sep,'_')
#     logcatName=logcatDir+ os.path.sep +"logcat" + ctime+ "_" +ip +".log"
#     print "logcatname:%s" % logcatName
#     s.runLogcat(logcatName)


