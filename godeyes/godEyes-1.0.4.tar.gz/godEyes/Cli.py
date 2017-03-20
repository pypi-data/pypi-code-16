# coding:utf-8
'''
Created on 2016年11月5日

@author: shenlang

'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import platform
import re
import shutil
import socket
import subprocess
import threading
import time
import signal
import json

from psutil import NoSuchProcess as PsNoSuchProcess
import psutil
from robot.libraries.BuiltIn import logger
import xml.etree.ElementTree as ET

import Util
from Validator import validator
from globalVal import rootdir, TAG
from Http import Http








PORTPUBLIC = 9025


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
        
class RetryError(Exception):
    pass

class RetError(RetryError):
    pass

class TimeoutError(RetryError):
    pass

class AdbConnectionError(Exception):
    pass





class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.stdout = None
        self.stderr = None
        self.ret = None

    def kill_process(self):
        pp = psutil.Process(self.process.pid)
        for child in pp.children():
            logger.debug('Terminating child process : %s' % child.pid, html=True)
            child_p = psutil.Process(child.pid)
            child_p.kill()
            logger.debug('Killed child process : %s' % child.pid, html=True)
            child_p.wait()
            logger.debug('Terminated child process : %s' % child.pid)
        try:
            pp.kill()
        except PsNoSuchProcess:
            logger.debug('Process dose not exist already', html=True)
            pass

    def run(self, timeout):
        def target():
            # logger.debug('Thread started', html=True)
            self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            (self.stdout, self.stderr) = self.process.communicate()
            self.ret = self.process.wait()
            # logger.debug('Thread finished', html=True)
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            logger.debug('Terminating process', html=True)
            self.kill_process()
            self.process.wait()
            thread.join()
            logger.debug('Terminated process', html=True)
            raise TimeoutError('%s timeout' % self.cmd)
        return self.stdout, self.ret


class Cli(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self, ip=None, appInfoPath=None):
        self.check_adb = 0
        self.platform = platform.system()
        self.encoding = 'utf-8' if self.platform == 'Linux' or self.platform == 'Darwin' else 'gbk'
        self.deviceModelDict = {}
        self.systemVersionDict = {}
        self.uuidDict = {}
        self.logcatProcessList= []
        self.fileHandlerList= []
        self.appInfoPath = appInfoPath
        
        if ip and '.' in ip:
            if '-' not in ip:
                self.ip = ip
                self.ip_cache = [ip]
                self.adb_connect(ip)
                
            else:
                ips = ip.split('-')
                self.ip = ips[0]
                self.ip_cache = ips
                for tempIp in ips:
                    self.adb_connect(tempIp)
                
        
        
        
        
    
    
    def __del__(self):
        self.stopLogcat()
    
    
    
    def _format(self, info):
        # return info.decode(self.encoding).replace('\r\r', '').strip()
        if self.encoding == 'gbk':
            return info.strip()
        else:
            return info.decode(self.encoding).replace('\r', '').strip()
            
    def shell(self, cmd, timeout=6, splitlines=False, console=True, checkret=False, row=None, column=None, grep=None, pattern=None, level='debug', expect_timeout=False, **kwargs):
        logger.info(cmd, html=True)
        # p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # stdout = _eintr_retry_call(p.stdout.read, timeout, cmd)
        # p.stdout.close()
        # ret = p.wait()
        # result = self._format(stdout)
        # if checkret and ret != 0:
        #     err = '%s | %s' % (ret, result)
        #     raise RetError(err)
        result = None
        
        try:
            stdout, ret = Command(cmd).run(int(timeout))
            print stdout
            result = self._format(stdout)
            if checkret and ret != 0:
                err = '%s | %s' % (ret, result)
                raise RetError(err)
            log(level, result)
            if console:
                logger.console(result)
            if splitlines:
                result = result.splitlines()
            if row or column:
                row, column = int(row) if row else 0, int(column) if column else 0
                lines = result.splitlines()
                if grep:
                    lines = [line for line in lines if grep in line]
                try:
                    result = lines[row].split()[column]
                except:
                    logger.debug('index error %s' % lines, html=True)
                    result = ''
                logger.debug(result, html=True)
            if pattern:
                p = re.compile(pattern)
                result = p.findall(result)
                if len(result) == 1:
                    result = result[0]
                logger.debug(result, html=True)
            if kwargs:
                validator.validate(result, **kwargs)
        except TimeoutError, msg:
            if expect_timeout:
                print 'expect timeout occured: %s' % msg
            else:
                raise TimeoutError('%s timeout' % cmd)
                    
        return result    
    
    

    
    def adb_shell(self, cmd, ip=None, timeout=8, splitlines=False, console=False, row=None, column=None, grep=None, pattern=None, level='info', retry=2, ignore_error=False, **kwargs):
        logger.console(cmd)
        logger.debug(cmd, html=True)
        ip = self._ip_or_self_ip(ip)
        timeout = int(timeout)
        result = ''
        while retry > 0:
            try:
                return self.shell('adb -s %s:5555 shell "%s"' % (ip, cmd), timeout, splitlines, console, True, row, column, grep, pattern, level, **kwargs)
            except RetryError as e:
                result = str(e)
                logger.console(result)
                if ignore_error:
                    return e
                retry -= 1
                self.adb_connect(ip)
        return result
    
    def _ip_or_self_ip(self, ip):
        if ip:
            if ip not in self.ip_cache:
                self.adb_connect(ip)
#             return ip    
            self.ip = ip

        return self.ip
    
    def check_adb_connection(self, ip):
        flag = ip + ':'
        self.check_adb += 1
        devices = self.shell('adb devices', splitlines=True)
        for device in devices:
            if flag in device:
                if 'device' in device:
#                     if 'test' in self.adb_shell('echo test', ip, retry=1):
                    return True
                elif 'offline' in device:
                    if self.check_adb < 5:
                        self.adb_disconnect(ip)
                        time.sleep(1)
                        self._adb_connect(ip)
                        return self.check_adb_connection(ip)
                    raise AdbConnectionError(device)
        return False
    
    
    def _adb_connect(self, ip):
#         ip = self._ip_or_self_ip(ip)
        if ip is None:
            ip = self.ip
        return self.shell('adb connect %s' % ip)
    
    def adb_connect(self, ip=None):
#         ip = self._ip_or_self_ip(ip)
        if ip is None:
            ip = self.ip
        if self.check_adb_connection(ip):
            return
        self._adb_connect(ip)
        time.sleep(1)
        if self.check_adb_connection(ip):
            return
        self.adb_disconnect(ip)
        time.sleep(1)
        self._adb_connect(ip)
        if self.check_adb_connection(ip):
            return
        self.shell('adb kill-server')
        self.shell('adb start-server')
        self._adb_connect(ip)
        if self.check_adb_connection(ip):
            return
        raise AdbConnectionError('adb connect failed and ip is:%s' % ip)
    
    
    
    
    def adb_disconnect(self, ip=None):
#         ip = self._ip_or_self_ip(ip)
        if ip is None:
            ip = self.ip
        return self.shell('adb disconnect %s' % ip)
    
    def adb_bg_shell(self, cmd, duration=3, ip=None):
        ip = self._ip_or_self_ip(ip)
        p = self.popen('adb -s %s:5555 shell "%s"' % (ip, cmd))
        time.sleep(duration)
        p.kill()
        p.wait()
    
    
        
    def adb_shell_akill(self, name, ip=None):
        u'''精确进程名kill
        '''
        pids = self.get_app_pid(name, ip)
        if pids:
            self.adb_shell("kill -9 %s" % ' '.join(pids), ip)
        
    def adb_shell_pkill(self, name, ip=None):
        u'''匹配进程名kill
        '''
        self.adb_shell("busybox pkill %s" % name, ip)
        
    def reboot(self, ip=None):
        self.adb_bg_shell('reboot', ip=ip)
        time.sleep(2)
        assert self.ping(ip) == False, 'reboot failed'
        self.wait_network_available(120, ip)
    
    '''
        休眠唤醒
        仅对支持红外遥控对设备有效，且测试机为windows
    '''
    def resume(self, ip=None):
        partDir = os.getcwd()
        cmd = os.path.join(partDir, 'RR.exe') + ' STB -output ' + os.path.join(partDir, 'DeviceDB.xml') + ' -device M13 -signal power'
        p = os.popen(cmd) 
        ret = p.readline().strip()
        print '[resume] ret:%s' % ret
        if ret:
            time.sleep(25)
            assert self.ping(ip) == True, 'resume failed'
    
    
    
    def ping(self, ip=None):
        ip = self._ip_or_self_ip(ip)
        cmd_prefix = 'ping -n' if self.platform == 'Windows' else 'ping -c'
        return self.popen('%s 1 %s' % (cmd_prefix, ip)).wait() == 0
    
    
    
 
    def wait_network_available(self, timeout=120, ip=None):
        before = time.time()
        while True:
            if time.time() - before > timeout:
                raise Exception('wait network available timeout')
            if self.ping(ip):
                logger.info('network is available now', True, True)
                return
            time.sleep(5)
    
    
        
    def popen(self, cmd, stdout=None):
        logger.debug(cmd, html=True)
        if stdout:
            log_path = os.path.join(rootdir, 'logs/%s' % stdout)
            log_dir = os.path.dirname(log_path)
            if not os.path.isdir(log_dir):
                os.makedirs(log_dir)
            with open(log_path, 'a') as f:
                return subprocess.Popen(cmd, shell=True, stdout=f, stderr=subprocess.STDOUT)
        return subprocess.Popen(cmd, shell=True)
    
    def execmd(self, cmd):
        print cmd
        self.popen(cmd).wait()

        
    def adb_push(self, local, remote='/data/', ip=None, timeout=60, **kwargs):
        ip = self._ip_or_self_ip(ip)
        if local.startswith(rootdir):
            cmd = 'adb -s %s:5555 push %s %s' % (ip, local, remote)
        else:
            cmd = 'adb -s %s:5555 push %s %s' % (ip, os.path.join(rootdir, local).replace('\\', '/'), remote)
        self.shell(cmd, timeout=timeout)
    

    def adb_pull(self, remote, local, ip=None, timeout=60, **kwargs):
        ip = self._ip_or_self_ip(ip)
        cmd = 'adb -s %s:5555 pull %s %s' % (ip, remote, local)
        self.shell(cmd, timeout=timeout)

    def adb_remount(self, ip=None, **kwargs):
        ip = self._ip_or_self_ip(ip)
        cmd = 'adb -s %s:5555 remount' % ip
        self.shell(cmd)
        
    
    def adb_shell_remount(self, part='/cyclone', mode='rw', ip=None, **kwargs):
        self.adb_shell('mount -o %s,remount %s' % (mode, part), ip=ip, **kwargs)


    def adb_install(self, apkPath, ip=None):
        ip = self._ip_or_self_ip(ip)
        cmd = 'adb -s %s:5555 -r install %s' % (ip, apkPath)
        self.shell(cmd)
    

    def adb_uninstall(self, packageName, ip=None):
        ip = self._ip_or_self_ip(ip)
        cmd = 'adb -s %s:5555 uninstall %s' % (ip, packageName)
        self.shell(cmd)
            
    
            
        

    def sendcompletemsg(self, port=None):
        if not port:
            print '---did not get port, use default---'
            port = PORTPUBLIC
        try:
            port = int(port)
            sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sockt.connect(("localhost", port))
            sockt.send('upgrade complete')
            sockt.close()
        except socket.error, msg:
            print '---error socket send---'
            pass


        
   
            
    def _safe_kill(self, process):
        try:
            process.kill()
        except:
            pass
        process.wait()
        

 
    
 
    def get_app_pid(self, name, ip=None):
        ps = self.adb_shell('ps | grep %s' % name, ip)
        p = re.compile(r'^\w+\s+(\d+)\s.+\s%s$' % name, re.M)
        pids = p.findall(ps)
        logger.info('pids: %s' % pids, html=True)
        return pids
    
    
    def screencap(self, localImagePath, remoteImagePath, ip=None):
        flag = False
        try:
            self.adb_shell('screencap -p %s' % (localImagePath), ip, timeout=300)
            self.shell('adb pull %s %s' % (localImagePath, remoteImagePath), timeout=300)
            flag = True
        except Exception:
            pass
        return flag
        
    def adb_shell_screencap(self, localImagePath, ip=None):
        return self.adb_shell('screencap -p %s' % (localImagePath), ip, timeout=300)
    
    
    def mkdir(self, path):
   
        path = path.strip()
        path = path.rstrip("\\")   
        print 'path:%s' % path 
        isExists = os.path.exists(path)
     
        # 判断结果
        if not isExists:
            os.makedirs(path)
            print 'mkdir %s success' % path
            return True
        else:
            print path + '%s already exists' % path
            return False
    
    def rmtree(self, path):
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                
            except OSError as e:
                print e
                self.shell('sudo rm -rf %s' % path)
                
            print 'rmtree %s done' % path
    
    def getUserDir(self):
        return os.path.expanduser('~')
    
    
   
    
    def sendGetdata(self, ip, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            pass
        s.connect((ip , port))
        try :
            s.sendall('hahaha')
        except socket.error:
            pass
        reply = s.recv(1024)
        return reply

 

    def adb_shell_chown(self, ownName, filePath, ip=None):
        self.adb_shell("chown %s %s" % (ownName, filePath), ip)
    

        
    def installSystemApp(self, appName,packageName,ip=None):
        
        
        if self.app_isExist(packageName):
            print 'initial state: app[%s]has installed' % appName
            self.uninstallApp(appName, packageName, ip)
            
        self.adb_shell("mount -o remount,rw /cyclone")
        self.adb_push('res/packagemanager/installapp/%s' % appName,'/cyclone/app')
        self.adb_shell('mount -o remount,ro /cyclone')
        time.sleep(1)
        uid = self.getUidByPackageInstaller(packageName)
        if(uid >= 0 and uid < 100000):
            print '[installSystemApp]app[%s]has installed at system path'  % appName
        elif(uid < 0):
            print '[installSystemApp]app[%s]install at system path fail'  % appName

    def installNormalApp(self, appName,packageName,ip=None):
        
        
        if  self.app_isExist(packageName):
            print 'initial state: app[%s]has installed' % appName
            self.uninstallApp(appName, packageName, ip)

        self.adb_push('res/packagemanager/installapp/%s' % appName)
        self.adb_shell('packageinstaller installw /data/%s' % appName)
        time.sleep(1)
        uid = self.getUidByPackageInstaller(packageName)
            
        if(uid >= 100000):
            print '[installNormalApp]app[%s]has installed at /data/app path'  % appName
        else:
            print '[installNormalApp]app[%s]install at /data/app path fail'  % appName
            
            
    def uninstallApp(self, appName,packageName,ip=None):
        
        
        if self.app_isExist(packageName):
            uid = self.getUidByPackageInstaller(packageName)
            if (uid < 100000 and uid >= 0):
                print '[uninstallApp]initial state: app[%s]has installed at system path' % appName 
                self.adb_shell("mount -o remount,rw /cyclone")
                self.adb_shell("rm -r /cyclone/app/%s" % appName)
                self.adb_shell('mount -o remount,ro /cyclone')
                
                              
                
            elif(uid >= 100000):
                print '[uninstallApp]initial state: app[%s]has installed at /data/app path' % appName 
                self.adb_shell("packageinstaller uninstallw %s" % packageName)
            
#             time.sleep(2)
            
            if not (self.app_isExist(packageName)):
                print '[uninstallApp]app[%s]uninstall success'  % appName
            else:
                print '[uninstallApp]app[%s]uninstall fail'  % appName
            
            
        else:
            print '[uninstallApp]initial state: app[%s]has not installed'  % appName 
      
    
    def waitForProcessCount(self, processName,processCount=1,timeout=4,ip=None):
        begin = time.time()
        retryCount = int(timeout)
        timeout = int(timeout)
        processCount = int(processCount)
        for i in range(1, retryCount):
            print "waitTorProcessCount current retrycount:%d" % i 
            curPidLength = len(self.get_app_pid(processName, ip))
            if (processCount == curPidLength):
                print 'waitForProcessCount %s match' % processName
                break
            time.sleep(1)
            leftTime = time.time() - begin
            assert timeout and  leftTime < timeout, 'waitForProcessCount %s timeout' % processName
            assert i < retryCount - 1, 'waitForProcessCount %s has run out of retry times and not match' % processName    


    

    
    


    

    
    def waitForProcessState(self, processName,expectState,timeout=4,ip=None):
        begin = time.time()
        retryCount = int(timeout)
        timeout = int(timeout)
        for i in range(1, retryCount):
            print "waitForProcessState current retrycount:%d" % i
            currentState = self.adb_shell('ps | grep %s' % processName,column=7)
            if (currentState == expectState):
                print 'waitForProcessState %s match' % processName
                break
            time.sleep(1)
            leftTime = time.time() - begin
            assert timeout and  leftTime < timeout, 'waitForProcessState %s timeout' % processName
            assert i < retryCount - 1, 'waitForProcessState %s has run out of retry times and not match' % processName
    
     
    
    
    def getTopWindow(self,ip=None):
        ip = self._ip_or_self_ip(ip)
        rets = self.adb_shell('dumpsys window windows',ip,pattern=r'mCurrentFocus=Window{.* u0 (.*)}')
        return rets
        
        
    
    def inputKeyEvent(self,keyCode,ip=None):
        return self.adb_shell('input keyevent %s' % keyCode,ip=ip)
    
    def startActivity(self,activityName,ip=None):
        return self.adb_shell("am start -W '%s'" % activityName,ip=ip)
    
    def startActivityAsync(self,activityName,ip=None):
        return self.adb_shell("am start '%s'" % activityName,ip=ip)
    
    def startActivityWithURI(self,uri,ip=None):
        return self.adb_shell("am start -W -a android.intent.action.VIEW -d '%s'" % uri,ip=ip)
    
    def closeApp(self,packageName,ip=None):
        return self.adb_shell('am force-stop %s' % packageName,ip=ip)
        
    
    def closeRecentProcesses(self,ip=None):
        processList = self.adb_shell('dumpsys activity a',ip=ip,pattern=r'realActivity=([a-zA-Z.]*)')
        #去重
        packageNameList = list(set(processList))
        print packageNameList
        if len(packageNameList) > 0:
            for packageName in packageNameList:
                if packageName == 'com.yunos.tv.homeshell':
                    continue
                self.closeApp(packageName, ip)
        
    def waitForTopWindow(self, windowName, timeout=7):
        begin = time.time()
        retryCount = int(timeout)
        timeout = int(timeout)
        for i in range(1, retryCount):
            print "waitForTopWindow current retrycount:%d" % i 
            curTopActivityName = self.getTopWindow()
            if (curTopActivityName == windowName):
                print 'waitForTopWindow %s match' % windowName
                break
            time.sleep(1)
            leftTime = time.time() - begin
            assert timeout and  leftTime < timeout, 'waitForTopWindow %s timeout' % windowName
            assert i < retryCount - 1, 'waitForTopWindow %s has run out of retry times and not match' % windowName    
        time.sleep(5)

    
    def getUUID(self,ip=None,useCache=True):
        ip = self._ip_or_self_ip(ip)
        if self.uuidDict.has_key(ip) and useCache:
            pass
        else:
            self.uuidDict[ip] = self.adb_shell('getprop ro.aliyun.clouduuid',ip=ip)
               
        return self.uuidDict[ip]
    
    def getDeviceModel(self,ip=None,useCache=True):
        ip = self._ip_or_self_ip(ip)
        if self.deviceModelDict.has_key(ip) and useCache:
            pass
        else:
            self.deviceModelDict[ip] = self.adb_shell('getprop ro.product.model',ip=ip)   
        return self.deviceModelDict[ip]
    
    def getReleaseVersion(self,ip=None,useCache=True):
        ip = self._ip_or_self_ip(ip)
        if self.systemVersionDict.has_key(ip) and useCache:
            pass
        else:     
            self.systemVersionDict[ip] = self.adb_shell('getprop ro.build.version.release',ip=ip)
        return self.systemVersionDict[ip]
    
    
    def getSystemVersion(self,ip=None):
        ret = self.getReleaseVersion(ip,False)
        if '-' in ret:
            return ret.split('-')[0]
    
    def getAbi(self,ip=None):
        return self.adb_shell('getprop ro.product.cpu.abi',ip=ip)
    
    
    def getBrand(self,ip=None):
        return self.adb_shell('getprop ro.product.brand',ip=ip)
    
    def clearAppData(self,packageName,ip=None):
        return self.adb_shell('pm clear %s' % packageName,ip=ip)
    
    def getUpMac(self,ip=None):
        rets = self.adb_shell('netcfg',splitlines=True,ip=ip)
        print rets
        for ret in rets:
            if 'UP' in ret and 'lo' not in ret and '0.0.0.0' not in ret:
                m = re.search(r"[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}", ret)
                if m:
                    return m.group()
    
    def getWifiMac(self,ip=None):
        rets = self.adb_shell('netcfg',ip=ip,splitlines=True)
        mac = '00:00:00:00:00:00'
        if self.getNetType(ip) == 'Unknown':
            return mac
        print rets
        for ret in rets:
            if ret.startswith('wlan') and '00:00:00:00:00:00' not in ret:
                m = re.search(r"[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}", ret)
                if m:
                    mac = m.group()   
        return mac        
    
    
  
    
    def getBSSID(self,ip=None,retryTimes=3):
        bssid = '00:00:00:00:00:00'
        if(retryTimes <= 0): 
            return bssid
        
        ret = self.adb_shell('dumpsys wifi | grep BSSID',ip=ip,pattern=r"BSSID\: ([a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}\:[a-f0-9]{2}),")
        if ret:
            if isinstance(ret, list):
                bssid = ret[0]  
            else:
                bssid = ret
        elif isinstance(ret, list) and len(ret) == 0:
            time.sleep(2)
            self.getBSSID(ip,retryTimes-1)
            
        return bssid  
    
    
    def getNetType(self,ip=None):
        rets = self.adb_shell('netcfg',ip=ip,splitlines=True)
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
                
    def hasWifi(self,ip=None):
        rets = self.adb_shell('netcfg',ip=ip,splitlines=True)
        flag = False
        for ret in rets: 
            if ret.startswith('wlan'):
                return True
        return flag           

    def getResolution(self,ip=None):
        
        ret = self.adb_shell('wm size',ip=ip)
        if 'x' in ret:
            return ret.split('Physical size:')[1].lstrip().replace('x','*')
        else:
            ret = self.adb_shell('dumpsys window | grep cur=',ip=ip,pattern=r'cur=(.*) app')
            if type(ret) == 'list':
                return ret[0].replace('x','*')
            return ret.replace('x','*')
   
    def getAppVersionCode(self,packageName,ip=None):
                
        if packageName is None:
            return ''  
        rets = self.adb_shell('dumpsys package %s | grep versionCode' % packageName,ip=ip,pattern=r'versionCode=(\d*)') 
        if type(rets) == list:
            return max(rets)
        else:
            return rets
    
    def getAppVersionName(self,packageName,ip=None):  
        if packageName is None:
            return ''
        rets = self.adb_shell('dumpsys package %s | grep versionName' % packageName,ip=ip,pattern=r'versionName=(.*)') 
        print rets
        
        if type(rets) == list:
            for ret in rets:
                return ret.strip()
                 
        else:
            return rets.strip()
    
    def getMediaAbility(self,ip=None):
        return self.adb_shell('getprop ro.media.ability',ip=ip)
    
    def clearLogcatCache(self,ip=None):
        ip = self._ip_or_self_ip(ip)
        self.execmd("adb -s %s:5555 logcat -c" % ip)
    
    def startLogcat(self, ip=None):
        ip = self._ip_or_self_ip(ip)
        
        self.clearLogcatCache(ip)
        ctime = Util.getCTime()
        
        logcatDir = ''.join((rootdir,os.path.sep,'logs'))
        print 'logcatDir:%s' % logcatDir
        logcatName=logcatDir+ os.path.sep +"logcat" + ctime+ "_" +ip +".log"
        print "logcatname:%s" % logcatName
        logcat_file = open(logcatName, 'w')
        cmd = 'adb -s %s:5555 logcat -v time *:I' % ip
        print cmd
        p = subprocess.Popen(cmd,shell=True,stdout=logcat_file,stderr=subprocess.PIPE)
        self.fileHandlerList.append(logcat_file)
        self.logcatProcessList.append(p)
        
        return logcatName
    

    
    def stopLogcat(self,waitTime=0):
        if waitTime > 0:
            time.sleep(waitTime)
        
        
        if len(self.fileHandlerList) > 0:
            for fileHandler in self.fileHandlerList:
                fileHandler.flush()
                fileHandler.close()
            self.fileHandlerList = []  
        
        if len(self.logcatProcessList) > 0:
            for p in self.logcatProcessList:
                self.killProccessByPlatform(p, self.platform)
            self.logcatProcessList = [] 
    
    
    def killProccessByPlatform(self,p, platform):
        if str(platform).lower() == 'windows':
                        st=subprocess.STARTUPINFO
                        st.dwFlags=subprocess.STARTF_USESHOWWINDOW
                        st.wShowWindow=subprocess.SW_HIDE
                        cmd = "TASKKILL /F /PID {pid} /T".format(pid=p.pid)
                        subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE,startupinfo=st)
        else:
            os.kill(p.pid,signal.SIGKILL)
    
        
           
        
        
        
        

       
    def getTopActivity(self,ip=None,**kwargs):
        ret = self.adb_shell('dumpsys activity | grep mFocusedActivity',ip=ip, pattern=r'u[0-9]* (.*)}')
        if type(ret) == list:
            return None 
        replace_reg = re.compile(r't[0-9]{1,4}')
        ret = replace_reg.sub('', ret).rstrip()
        rets = ret.split('/')
        if rets[1].startswith('.'):
            activityName = rets[0] + rets[1]
        else:
            activityName = rets[1]
            
        print 'topActivity is:%s' % activityName
        validator.validate(activityName, **kwargs)          
        return activityName
    
    
    
    def waitForTopActivity(self, activityName, ip=None,timeout=7):
        begin = time.time()
        retryCount = int(timeout)
        timeout = int(timeout)
        for i in range(1, retryCount):
            print "waitForTopActivity current retrycount:%d" % i 
            curTopActivityName = self.getTopActivity(ip)
            if (curTopActivityName == activityName):
                print 'waitForTopActivity %s match' % activityName
                break
            time.sleep(1)
            leftTime = time.time() - begin
            assert timeout and  leftTime < timeout, 'waitForTopActivity %s timeout' % activityName
            assert i < retryCount - 1, 'waitForTopActivity %s has run out of retry times and not match' % activityName    
        time.sleep(5)
        
    def waitForTopActivityNoPacakge(self, activityName, ip=None,timeout=7):
        begin = time.time()
        retryCount = int(timeout)
        timeout = int(timeout)
        for i in range(1, retryCount):
            print "waitForTopActivity current retrycount:%d" % i 
            curTopActivityName = self.getTopActivity(ip)
            if (activityName in curTopActivityName):
                print 'waitForTopActivity %s match' % activityName
                break
            time.sleep(1)
            leftTime = time.time() - begin
            assert timeout and  leftTime < timeout, 'waitForTopActivity %s timeout' % activityName
            assert i < retryCount - 1, 'waitForTopActivity %s has run out of retry times and not match' % activityName    
        time.sleep(5)
    
    def waitForHomeActivity(self,ip=None,timeout=7):
        homeActivityList = ['com.yunos.tv.homeshell.application.HomeActivity','com.yunos.tv.homeshell.activity.HomeActivity']
        begin = time.time()
        retryCount = int(timeout)
        timeout = int(timeout)
        for i in range(1, retryCount):
            print "waitForHomeActivity current retrycount:%d" % i 
            curTopActivityName = self.getTopActivity(ip)
            if (curTopActivityName in homeActivityList):
                print 'waitForHomeActivity %s match' % curTopActivityName
                break
            time.sleep(1)
            leftTime = time.time() - begin
            assert timeout and  leftTime < timeout, 'waitForHomeActivity timeout'
            assert i < retryCount - 1, 'waitForHomeActivity has run out of retry times and not match'
        time.sleep(5)
    
    def typeText(self, text, ip=None):
        self.adb_shell('input text %s' % text,ip=ip)
    
    
    def checkPostLog(self,formatLog,packageName,pageName,eventId,arg1=None,ip=None,ignoreSessionInfo=False,commonParamsValidatorDict=None, **kwargs):
        ip = self._ip_or_self_ip(ip)
        brand = self.getBrand(ip)
        deviceModel = self.getDeviceModel(ip)
        resolution = self.getResolution(ip)
        netType = self.getNetType(ip)
        if netType == 'WiredNetwork':
            access = 'Unknown'
            
        else:  
            access = netType
        
        mac = self.getWifiMac(ip)
        bssid = self.getBSSID(ip)   
        appVersionName = self.getAppVersionName(packageName,ip)
        osVersion = self.getReleaseVersion(ip)   
             
        abi = self.getAbi(ip)
        
        did = self.getUUID(ip,True)
        
        
        endTime = self.getTimeStampfromDevice(ip)
        
        #时间戳比较在时间范围，运行用例前校验sessionInfo
        
        
           
        try:   
            
            validator.validate(formatLog, _sessionInfo_brand=brand,_sessionInfo_deviceModel=deviceModel,_sessionInfo_resolution=resolution,_sessionInfo_access=access,_sessionInfo_appVersionName=appVersionName,_sessionInfo_osVersion=osVersion,_sessionInfo_timestamp__lt=endTime) 
            
            if self.appInfoPath:
                appKeyValue = Util.getAppKey(self.appInfoPath, packageName)
                validator.validate(formatLog,_sessionInfo_appKey=appKeyValue)
            else:
                validator.validate(formatLog,_sessionInfo_appKey__isNotEmpty=True)
            
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
    
        
    
    def checkUTLogWithFile(self,logcatPath,appPackageName,pageName,eventId,arg1='',beginTime=0L,endTime=0L,ip=None,customFilter='',pid='',ignoreSessionInfo=False,commonParamsValidatorDict=None, **kwargs):
        if not pid:
            pids = self.get_app_pid(appPackageName,ip)
            if pids:
                pid = pids[0]
        
        
        formatLogList = Util.getFormatLogList(logcatPath,pageName,eventId,arg1,beginTime,endTime,customFilter=customFilter,pid=pid)
#         if not Util.is_json(args):
#             argsJson = Util.argsStrToJson(args)
#             
#         else:
#             argsJson = args
#      
   
#         kvArgs = json.dumps(argsJson)
        l = len(formatLogList)
        assert l == 1,'actual has post count:%d' % l
        formatLog = formatLogList[0]
        self.checkPostLog(formatLog,appPackageName,pageName,eventId,arg1,ip=ip,ignoreSessionInfo=ignoreSessionInfo, commonParamsValidatorDict=commonParamsValidatorDict, **kwargs)
#         self._getUTDataFromServer(dk, str(eventId), pageName,**kvArgs)
        print TAG + 'CHECK PASS!!!'
            
    
    
    def checkUTLog(self,logcatPath,appPackageName,pageName,eventId,arg1='',beginTime=0L,endTime=0L,ip=None,customFilter='',ignoreSessionInfo=False, commonParamsValidatorDict=None, **kwargs):
        self.stopLogcat()
        
        formatLogList = Util.getFormatLogList(logcatPath,pageName,eventId,arg1,beginTime,endTime,customFilter=customFilter)
#         if not Util.is_json(args):
#             argsJson = Util.argsStrToJson(args)
#             
#         else:
#             argsJson = args
#      
   
#         kvArgs = json.dumps(argsJson)
        if len(formatLogList) == 1:
            formatLog = formatLogList[0]
            self.checkPostLog(formatLog,appPackageName,pageName,eventId,arg1,ip=ip,ignoreSessionInfo=ignoreSessionInfo, commonParamsValidatorDict=commonParamsValidatorDict, **kwargs)
#         self._getUTDataFromServer(dk, str(eventId), pageName,**kvArgs)
            print TAG + 'CHECK PASS!!!'
    
    def getTimeStampfromDevice(self,ip=None):
        t = self.adb_shell('date +%s000',ip)
        return long(t)       
        
    
    
    

    def openDebugSwitch(self,ip=None):
        
        if ip is None:
            for tempIp in self.ip_cache:
                self.adb_shell('setprop debug.yingshi.config 1',tempIp)
                self.adb_shell('setprop debug.yingshi.config.utrealtime 1',tempIp)
                self.closeApp('com.yunos.tv.yingshi.boutique',tempIp)
        else:
            self.adb_shell('setprop debug.yingshi.config 1',ip)
            self.adb_shell('setprop debug.yingshi.config.utrealtime 1',ip)
            self.closeApp('com.yunos.tv.yingshi.boutique',ip)     

#     def openDebugSwitch(self,ip=None):
#         ip = self._ip_or_self_ip(ip)
#         model = self.getDeviceModel(ip)
#         uuid = self.getUUID(ip)
#         ctime = Util.timestampMillis()
#         randomStr = str(random.randint(1,99))
# 
#         dk = model + uuid + randomStr + str(ctime)
# #         self.execmd('curl http://wapp.m.taobao.com/src/utauto.html?dk=%s' % dk)
#         ret = self.adb_shell('am start -a android.intent.action.UTHelper --es dk %s' % dk)
#         print 'openDebugSwitch:%s' % ret
#         return dk
#     
#     def closeDebugSwitch(self,ip=None):
#         ip = self._ip_or_self_ip(ip)
#         self.closeApp('com.de.test.uthelper', ip)
    
    def getHxml(self,ip=None):
        ip = self._ip_or_self_ip(ip)
        self.getDeviceModel(ip,True)
        dump_str = "uiautomator dump --compressed /dev/tty"
        system_model = self.deviceModelDict[ip]
        if system_model.lower() == "magicbox1s" or system_model.lower() == "magicbox1s_pro":
            dump_str = "uiautomator dump /dev/tty"
        output = self.adb_shell(dump_str, ip=ip)
        # -------------------------------------------
        # 加入output检查，若dump结果为空，则等待10s后继续dump，尝试6次
        count = 0
        while output.find("</hierarchy>") == -1:
            print 'dump失败,重试中...'
            output = self.adb_shell(dump_str)
            if count >= 6:
                print '多次dump失败,请检查环境'
                break
            count = count + 1
            time.sleep(10)
    
        if output.find("</hierarchy>") != -1:
            # xml开始位置，如161会多打印一些非xml的warning log by shiming 20160610
            start = output.rfind("<?xml version=")
            end = output.rfind("</hierarchy>") + len("</hierarchy>")  # 结束位置
            self.xml_sz = output[start:end]
        else:
            self.xml_sz = ""
        return self.xml_sz
    
    def getPageText(self, ip=None):
        all_text=''
        xml_sz = self.getHxml(ip)
        assert xml_sz !='', 'dump失败'
        tree = ET.fromstring(xml_sz)
        for elem in tree.iter(tag='node'):
            if elem.attrib['text']!='':
                all_text=all_text + elem.attrib['text']
        return all_text
    
    def isContainText(self,expectText,ip=None,**kwargs):
        ret = False
        if expectText:
            if expectText in self.getPageText(ip):
                ret = True
        validator.validate(ret, **kwargs)
        return ret
    
    
    
    def _getUTDataFromServer(self,dk,eid=None,page=None,**kwargs):
        http = Http()
        baseUrl = 'http://muvp.alibaba-inc.com/rpc/getLog/byDebugkey.jsonp?dk=%s' % dk
        if eid:
            baseUrl = '%s&eid=%s&' % (baseUrl,eid)
        
        if page:
            baseUrl = '%s&eid=%s&' % (baseUrl,page) 
        
        
        
        partUrl = ''
        for key in kwargs: 
            kv = '%s=%s'% (key,kwargs[key])
            partUrl = partUrl + kv + '&'
         
        url = baseUrl + partUrl
        url = url.rstrip('&')
        
        ret = http.get(url,False)
        return ret
    
    def getSelectedViewText(self, ip = None,**kwargs):
        xml_sz = self.getHxml(ip)
        assert xml_sz != '', 'dump失败'
        tree = ET.fromstring(xml_sz)
        text = ''
        for elem in tree.iter(tag='node'):
            if elem.attrib['selected'] == 'true':
                if elem.attrib['text']!='':
                    text = text+ elem.attrib['text'] + ' '
        text=text.strip()
        assert text != "", "当前选中控件无文字"
        validator.validate(text, **kwargs)
        return text
    
    def getFocusedAndSelectedViewText(self,ip = None,**kwargs):
        xml_sz = self.getHxml(ip)
        if xml_sz == '':
            self.logInfo('dump失败')
            return None
        else:
            tree = ET.fromstring(xml_sz)
            text = ''
            for elem in tree.iter(tag='node'):
                if elem.attrib['selected'] == 'true' and elem.attrib['focused'] == 'true':
                    if elem.attrib['text'] != '':
                        text = text + elem.attrib['text'] + ' '
                    for child in elem:
                        if child.attrib['text'] != '':
                            text = text + child.attrib['text'] + ' '
            text = text.strip()
            validator.validate(text, **kwargs)
            return text
   
    def pressEnter(self, times=1, timeout=0.5, ip=None):
        times = int(times)
        timeout = float(timeout)
        for i in range(times):
            self.inputKeyEvent(23, ip)
            time.sleep(timeout)
            i += 1
        pass
    
    def pressRight(self, times=1, timeout=0.5, ip=None):
        times = int(times)
        timeout = float(timeout)
        for i in range(times):
            self.inputKeyEvent(22, ip)
            time.sleep(timeout)
            i += 1
        pass
    
    def pressLeft(self, times=1, timeout=0.5, ip=None):
        times = int(times)
        timeout = float(timeout)
        for i in range(times):
            self.inputKeyEvent(21)
            time.sleep(timeout)
            i += 1
        pass
    
    def pressDown(self, times=1, timeout=0.5, ip=None):
        times = int(times)
        timeout = float(timeout)
        for i in range(times):
            self.inputKeyEvent(20, ip)
            time.sleep(timeout)
            i += 1
        pass

    def pressUp(self, times=1, timeout=0.5, ip=None):
        times = int(times)
        timeout = float(timeout)
        for i in range(times):
            self.inputKeyEvent(19, ip)
            time.sleep(timeout)
            i += 1
        pass

    def pressMenu(self, timeout=0.5, ip=None):
        timeout = float(timeout)
        self.inputKeyEvent(82,ip)
        time.sleep(timeout)
        pass

    def pressHome(self, times=1, timeout=1, ip=None):
        times = int(times)
        timeout = float(timeout)
        for i in range(times):
            self.inputKeyEvent(3, ip)
            time.sleep(timeout)
            i += 1
        pass
    
    def pressBack(self, times=1, timeout=1, ip=None):
        times = int(times)
        timeout = float(timeout)
        for i in range(times):
            self.inputKeyEvent(4, ip)
            time.sleep(timeout)
            i += 1
        pass
    
    def __keyDown(self, keyCode, ip=None):
        brand = self.getDeviceModel(ip)
        keydownstr1 = 'sendevent /dev/input/event0 1 %d 1'
        keydonwstr2 = 'sendevent /dev/input/event0 0 0 0'
        if brand.lower() == "magicbox1s_pro":
            keydownstr1 = 'sendevent /dev/input/event4 1 %d 1'
            keydonwstr2 = 'sendevent /dev/input/event4 0 0 0'
        self.adb_shell(keydownstr1 % keyCode, ip)
        self.adb_shell(keydonwstr2, ip)
        pass

    def __keyUp(self, keyCode, ip=None):
        brand = self.getDeviceModel(ip)
        keydownstr1 = 'sendevent /dev/input/event0 1 %d 0'
        keydonwstr2 = 'sendevent /dev/input/event0 0 0 0'
        if brand.lower() == "magicbox1s_pro":
            keydownstr1 = 'sendevent /dev/input/event4 1 %d 0'
            keydonwstr2 = 'sendevent /dev/input/event4 0 0 0'
        self.adb_shell(keydownstr1 % keyCode, ip)
        self.adb_shell(keydonwstr2, ip)
        pass
    
    def longPressRight(self, sec=1, ip=None):
        sec = float(sec)
        self.__keyDown(106, ip)
        time.sleep(sec)
        self.__keyUp(106, ip)
        pass

    def longPressLeft(self, sec=1, ip=None):
        sec = float(sec)
        self.__keyDown(105, ip)
        time.sleep(sec)
        self.__keyUp(105, ip)
        pass    
    
       
    
if __name__ == '__main__':
    cli = Cli('30.11.32.135')
    cli.checkPostLog('{"businessInfo": {"eventId": 2001, "args": {"channel_name": "\u6211\u7684", "yt_id": 477049804, "yt_name": "brhao", "channel_id": 147, "type": "unknown", "is_login": "true"}, "arg1": "-", "arg2": "-", "arg3": "9770", "pageName": "Page_desk_home"}, "sessionInfo": {"appKey": "21694316", "sdkVersion": "5.0.0.427732", "deviceModel": "MagicBox_M17", "extra": {"_io": "1", "_mac": "00:00:00:00:00:00", "_did": "F835EEB9A002DFBAEDA756ED7C29C049", "_abi": "armeabi-v7a"}, "appVersionName": "MagicBox_Release_5.2.0.009", "brand": "MBX", "access": "Unknown", "timestamp": "1489647624412", "osVersion": "6.0.2-RS-20161014.1112", "resolution": "1920*1080"}}','')
