#coding:utf-8

'''
Created on 2015年10月12日
@author: creeper
'''
import os,re,sys
import threadpool
import logging
from utils import AbsPath

from base.analyzer import Analyzer

'''
FileScanner 用来继承实现不同项目特定的分析需求，覆盖父类的接口满足特定业务
'''

class FileScanner(object):
    def __init__(self, path, devices, mUtil, lifecycle):
        self.devices = devices
        self.path = path
        self.mUtil = mUtil
        self.CONSOLE = "autoTest_console_logcat.txt"
        self.ERROR = "error.txt"
        self.LOGCAT = "autoTest_logcat.txt"
        self.LUALOG = "Log.txt"
        self.LIFECYCLE = lifecycle
        self.pool = threadpool.ThreadPool(10)
        self.suffix_process_devices = []

        #0:字符串或者带变量的字符串; 1: #正则表达式或者带变量的正则表达式; 2: #字符串或者带变量的字符串（取反）; 3:#正则表达式或者带变量的正则表达式(取反)

    def addConfig(self,configItem,config):
        try:
            if not configItem.has_key('keyword'):
                raise NameError('配置项里没有keyword字段')
            if not configItem.has_key('live'):
                raise NameError('配置项里没有live字段')
            if configItem['keyword'] in [item['keyword'] for item in config]:
                raise NameError("配置表里已经有相同关键字，不能添加重复关键字")
            else:
                config.append(configItem)
        except NameError:
            raise
        return config

    def deleteConfigByKeyword(self,keyword,config):
        for idx,item in enumerate(config):
            if keyword == item['keyword']:
                config.pop(idx)
                break
        else:
            raise NameError("配置表里没有找到预删除配置项")
        return config



    def editConfigByKeyword(self,configItem,config):
        #先删除
        for idx,item in enumerate(config):
            if configItem['keyword'] == item['keyword']:
                config.pop(idx)
                break
        else:
            raise NameError("发生编辑错误")
        #再添加
        config.append(configItem)
        return config

    def guidepage_analysis(self,device,kat_id):
        kat_id = None
        kat_uid = None
        maplist= []
        mfile = open(os.path.join(self.path,device,"Result",self.guidepage),'r')
        #分析guidepage 日志逻辑：
        content = mfile.read()
        # for config_item in self.LUALOG_CONFIG:
        #     maplist = self.handleConfigItem(content,maplist,kat_id,kat_uid,config_item)
        # mfile.close()
        # content = ''
        maplist.append(("guidepage", content))
        return maplist

    def _process_executer(self,device_info):
        device = device_info['device']
        if device.find('logcat') != -1:
            #如果device的名字包含了错误的logcat字段，则直接返回，不做处理
            return
        kat_id = "<kat_id>"
        #device_info 的键会自动去重，如果发现相同的键 ，则会用新的键值覆盖旧键值
        #处理autoTest_console_logcat.txt
        if device_info.has_key("hasFile_" + self.CONSOLE.replace('.','_')):
            if device_info["hasFile_" + self.CONSOLE.replace('.','_')] == 'pass':
                #调用处理console方法
                maplist,kat_id = self.console_analysis(device,kat_id)
                for key,value in maplist:
                    device_info[key] = value
                pass
        else:
            if self.mUtil.hasFile(os.path.join(self.path,device),self.CONSOLE) == True:
                device_info["hasFile_" + self.CONSOLE.replace('.','_')] = 'pass'
                maplist,kat_id = self.console_analysis(device,kat_id)
                for key,value in maplist:
                    device_info[key] = value
                pass
            else:
                device_info["hasFile_" + self.CONSOLE.replace('.','_')] = 'fail'

        #处理error.txt
        if device_info.has_key("hasFile_" + self.ERROR.replace('.','_')):
            if device_info["hasFile_" + self.ERROR.replace('.','_')] == 'fail':
                #调用处理error方法
                maplist = self.error_analysis(device)
                for key,value in maplist:
                    device_info[key] = value
        else:
            if self.mUtil.hasFile(os.path.join(self.path,device),self.ERROR) == True:
                device_info["hasFile_" + self.ERROR.replace('.','_')] = 'fail'
                maplist = self.error_analysis(device)
                for key,value in maplist:
                    device_info[key] = value
            else:
                device_info["hasFile_" + self.ERROR.replace('.','_')] = 'pass'

        #处理autoTest_logcat.txt
        if device_info.has_key("hasFile_" + self.LOGCAT.replace('.','_')):
            if device_info["hasFile_" + self.LOGCAT.replace('.','_')] == 'pass':
                #调用处理LOGCAT方法
                maplist = self.logcat_analysis(device,kat_id)
                for key,value in maplist:
                    device_info[key] = value

                #调用处理accessmanager方法
                maplist = self.accessmanager_analysis(device)
                for key,value in maplist:
                    device_info[key] = value

        else:
            if self.mUtil.hasFile(os.path.join(self.path,device),self.LOGCAT) == True:
                device_info["hasFile_" + self.LOGCAT.replace('.','_')] = 'pass'
                #调用处理LOGCAT方法
                maplist = self.logcat_analysis(device,kat_id)
                for key,value in maplist:
                    device_info[key] = value

                #调用处理accessmanager方法
                maplist = self.accessmanager_analysis(device)
                for key,value in maplist:
                    device_info[key] = value

            else:
                device_info["hasFile_" + self.LOGCAT.replace('.','_')] = 'fail'

        #处理Log.txt
        if device_info.has_key("hasFile_" + self.LUALOG.replace('.','_')):
            if device_info["hasFile_" + self.LUALOG.replace('.','_')] == 'pass':
                #调用处理lualog方法
                maplist = self.lualog_analysis(device)
                for key,value in maplist:
                    device_info[key] = value
        else:
            if self.mUtil.hasFile(os.path.join(self.path,device),self.LUALOG) == True:
                device_info["hasFile_" + self.LUALOG.replace('.','_')] = 'pass'
                maplist = self.lualog_analysis(device)
                for key,value in maplist:
                    device_info[key] = value
            else:
                device_info["hasFile_" + self.LUALOG.replace('.','_')] = 'fail'

        #处理生命周期文件：
        if device_info.has_key("hasFile_" + self.LIFECYCLE.replace('.','_')):
            if device_info["hasFile_" + self.LIFECYCLE.replace('.','_')] == 'pass':
                #调用处理lifecycle方法
                maplist = self.lifecycle_analysis(device)
                for key,value in maplist:
                    device_info[key] = value
        else:
            if self.mUtil.hasFile(os.path.join(self.path,device),self.LIFECYCLE) == True:
                device_info["hasFile_" + self.LIFECYCLE.replace('.','_')] = 'pass'
                maplist = self.lifecycle_analysis(device)
                for key,value in maplist:
                    device_info[key] = value
            else:
                device_info["hasFile_" + self.LIFECYCLE.replace('.','_')] = 'fail'

        self.suffix_process_devices.append(device_info)

    def process(self):
        reqs = threadpool.makeRequests(self._process_executer, self.devices)
        [self.pool.putRequest(req) for req in reqs]
        self.pool.wait()

    def variable_replace(self,kat_id,kat_uid,source):
        variables ={"<kat_id>":kat_id,"<kat_uid>":kat_uid}
        for key in variables:
            if source.find(key)!= -1:
                source = source.replace(key,variables[key])
        return source

    def handleConfigItem(self,content,maplist,kat_id,kat_uid,config_item):
        for tag,item in config_item['live']:
            item =item.encode(sys.getfilesystemencoding())
            item = self.variable_replace(kat_id,kat_uid,item)
            if tag == 0: #字符串或者带变量的字符串
                if content.find(item)!=-1:
                    pass
                else:
                    return maplist
            elif tag == 1: #正则表达式或者带变量的正则表达式
                if re.search(item,content):
                    pass
                else:
                    return maplist
            elif tag == 2: #字符串或者带变量的字符串（取反）
                if content.find(item)==-1:
                    pass
                else:
                    return maplist
            elif tag == 3:#正则表达式或者带变量的正则表达式(取反)
                if re.search(item,content)==None:
                    pass
                else:
                    return maplist
            elif tag == 4:#字符串或者带变量的字符串出现次数>=4次,或者 正则表达式或者带变量的正则表达式出现次数>=4次
                if len(set(re.findall(item,content))) >= 4:
                    pass
                else:
                    return maplist
            elif tag == 5:#content的内容结尾是item
                item = item.strip("\n")
                pattern5 = re.compile(item+"$")
                if re.search(pattern5, content.strip("\n")):
                    pass
                else:
                    return maplist
        maplist.append((config_item['keyword'],'fail'))
        return maplist

    def logcat_analysis(self,device,kat_id):
        maplist= []
        kat_uid = "<kat_uid>"
        mfile = open(os.path.join(self.path,device,self.LOGCAT),'r')
        content = mfile.read()
        #在处理LOGCAT_CONFIG之前，需要先在logcat中再次尝试获取kat_id的真实值
        tmp = re.search(r"Start proc com.kunpeng.kapalai.kat.*pid=\d*",content)
        if tmp:
            kat_id = re.search(r'\d+',tmp.group()).group()
        else:
            tmp = re.search(r"TestRunner(\d*): started: test(com.kunpeng.kapalai.kat.TestMainInstrumentation)",content)
            if tmp:
                kat_id = re.search(r'\d+',tmp.group()).group()
        #在logcat中尝试获取kat_uid的真实值
        tmp = re.search(r"Start proc com.kunpeng.kapalai.kat.*uid=\d*",content)
        if tmp:
            kat_uid = re.search(r'\d+',tmp.group()).group()
        for config_item in self.LOGCAT_CONFIG:
            maplist = self.handleConfigItem(content,maplist,kat_id,kat_uid,config_item)
        mfile.close()
        content = ''
        return maplist

    def lualog_analysis(self, device):
        kat_id = None
        kat_uid = None
        maplist= []
        mfile = open(os.path.join(self.path,device,"Result",self.LUALOG),'r')
        #分析lualog 日志逻辑：
        content = mfile.read()
        for config_item in self.LUALOG_CONFIG:
            maplist = self.handleConfigItem(content,maplist,kat_id,kat_uid,config_item)
        mfile.close()
        content = ''
        return maplist


    def console_analysis(self,device,kat_id):
        maplist= []
        kat_uid = None
        mfile = open(os.path.join(self.path,device,self.CONSOLE),'r')
        #分析console日志逻辑：
        content = mfile.read()
        for config_item in self.CONSOLE_CONFIG:
            maplist = self.handleConfigItem(content,maplist,kat_id,kat_uid,config_item)
        tmp = re.search(r"find_proc pid = \d+",content)
        if tmp:
            kat_id = re.search(r'\d+',tmp.group()).group()
        content = ''
        mfile.close()
        return maplist,kat_id

    def error_analysis(self,device):
        kat_id = None
        kat_uid = None
        maplist= []
        mfile = open(os.path.join(self.path,device,"Result",self.ERROR),'r')
        #分析error 日志逻辑：
        content = mfile.read()
        for config_item in self.ERROR_CONFIG:
            maplist = self.handleConfigItem(content,maplist,kat_id,kat_uid,config_item)
        mfile.close()
        content = ''
        return maplist

    def lifecycle_analysis(self,device):
        kat_id = None
        kat_uid = None
        maplist = []
        mfile = open(os.path.join(self.path,device,"logs", self.LIFECYCLE), 'r')
        #分析lifecycle 日志逻辑：
        content = mfile.read()
        for config_item in self.LIFECYCLE_CONFIG:
            maplist = self.handleConfigItem(content,maplist,kat_id,kat_uid,config_item)
        mfile.close()
        content = ''
        return maplist

    def accessmanager_analysis(self,device):
        kat_id = None
        kat_uid = None
        maplist = []
        mfile = open(os.path.join(self.path,device,self.LOGCAT),'r')
        #分析accessmanger 日志逻辑：
        content = mfile.read()
        for config_item in self.ACCESSMANAGER_CONFIG:
            maplist = self.handleConfigItem(content,maplist,kat_id,kat_uid,config_item)
        mfile.close()
        content = ''
        return maplist

    def setConfig(self,JsonConfig):
        if JsonConfig.getType().find("logcat_json") != -1:
            self.LOGCAT_CONFIG = JsonConfig.getValue()
        elif JsonConfig.getType().find("console_json") != -1:
            self.CONSOLE_CONFIG = JsonConfig.getValue()
        elif JsonConfig.getType().find("error_json") != -1:
            self.ERROR_CONFIG = JsonConfig.getValue()
        elif JsonConfig.getType().find("lualog_json") != -1:
            self.LUALOG_CONFIG = JsonConfig.getValue()
        elif JsonConfig.getType().find("lifecycle_json") != -1:
            self.LIFECYCLE_CONFIG = JsonConfig.getValue()
        elif JsonConfig.getType().find("accessmanager_json") != -1:
            self.ACCESSMANAGER_CONFIG = JsonConfig.getValue()

    def analysisEmpl(self,device):
        #fail_detail 是个生成器，注意生成器消耗掉了，需要重新创建
        generator_fail_detail = (key for (key, value) in device.iteritems() if value == 'fail')
        device_name = device['device']
        #分析详细结果，给出测试结论
        mAnalyzer = Analyzer(generator_fail_detail,device_name)
        solution = mAnalyzer.run()
        #每个问题间隔符
        SEPARATOR = ","
        device['solution'] = ''
        device['solution'] = SEPARATOR.join(solution).decode('utf-8')
        if device['solution'] == '':
            device['result'] = 'pass'
        else:
            device['result'] = 'fail'

class FileScannerQQmusic(FileScanner):
    def __init__(self,path,devices,mUtil,lifecycle):
        FileScanner.__init__(self,path,devices,mUtil,lifecycle)
        self.guidepage = "qqmusic_guidepage_kapalai.log"

    def _process_executer(self,device_info):
        device = device_info['device']
        if device.find('logcat') != -1:
            #如果device的名字包含了错误的logcat字段，则直接返回，不做处理
            return
        kat_id = "<kat_id>"
        #device_info 的键会自动去重，如果发现相同的键 ，则会用新的键值覆盖旧键值

        #处理qqmusic_guidepage_kapalai.log.txt
        if device_info.has_key("hasFile_" + self.guidepage.replace('.','_')):
            if device_info["hasFile_" + self.guidepage.replace('.','_')] == 'pass':
                #调用处理guidepage方法
                maplist,kat_id = self.guidepage_analysis(device,kat_id)
                for key,value in maplist:
                    device_info[key] = value
                pass
        else:
            if self.mUtil.hasFile(os.path.join(self.path,device,"Result"),self.guidepage) == True:
                device_info["hasFile_" + self.guidepage.replace('.','_')] = 'pass'
                #调用处理guidepage方法
                maplist = self.guidepage_analysis(device,kat_id)
                for key,value in maplist:
                    device_info[key] = value
                pass
            else:
                device_info["hasFile_" + self.guidepage.replace('.','_')] = 'fail'

        self.suffix_process_devices.append(device_info)

    def guidepage_analysis(self,device,kat_id):
        kat_id = None
        kat_uid = None
        maplist= []
        mfile = open(os.path.join(self.path,device,"Result",self.guidepage),'r')
        #分析guidepage 日志逻辑：
        content = mfile.read()
        maplist.append(("guidepage", content))
        return maplist

    def analysisEmpl(self,device):
        device['solution'] = device["guidepage"].decode('utf-8')
        device['result'] = 'pass'

class FileScannerQQmail(FileScanner):
    def __init__(self,path,devices,mUtil, lifecycle):
        FileScanner.__init__(self,path,devices,mUtil, lifecycle)
        self.qqmail = "qqmail.txt"

    def _process_executer(self,device_info):
        device = device_info['device']
        if device.find('logcat') != -1:
            #如果device的名字包含了错误的logcat字段，则直接返回，不做处理
            return
        kat_id = "<kat_id>"
        #device_info 的键会自动去重，如果发现相同的键 ，则会用新的键值覆盖旧键值

        #处理qqmusic_guidepage_kapalai.log.txt
        if device_info.has_key("hasFile_" + self.qqmail.replace('.','_')):
            if device_info["hasFile_" + self.qqmail.replace('.','_')] == 'pass':
                #调用处理mail方法
                maplist = self.mail_analysis(device,kat_id)
                for key,value in maplist:
                    device_info[key] = value
                pass
        else:
            if self.mUtil.hasFile(os.path.join(self.path,device,"Result"),self.qqmail) == True:
                device_info["hasFile_" + self.qqmail.replace('.','_')] = 'pass'
                #调用处理mail方法
                maplist = self.mail_analysis(device,kat_id)
                for key,value in maplist:
                    device_info[key] = value
                pass
            else:
                device_info["hasFile_" + self.qqmail.replace('.','_')] = 'fail'

        self.suffix_process_devices.append(device_info)

    def mail_analysis(self,device,kat_id):
        kat_id = None
        kat_uid = None
        maplist= []
        mfile = open(os.path.join(self.path,device,"Result",self.qqmail),'r')
        #分析guidepage 日志逻辑：
        content = mfile.read()
        maplist.append(("qqmail", content))
        return maplist

    def analysisEmpl(self,device):
        device['solution'] = device["qqmail"].decode('utf-8')
        device['result'] = 'pass'

class FileScannerXls(FileScanner):
    def __init__(self,path,devices,mUtil, lifecycle,xls):
        FileScanner.__init__(self,path,devices,mUtil, lifecycle)
        self.xls = xls


    def _process_executer(self,device_info):
        device = device_info['device']
        if device.find('logcat') != -1 or self.xls == 'com.kunpeng.creeper.default':
            #如果device的名字包含了错误的logcat字段，则直接添加设备并返回，不做额外处理
            self.suffix_process_devices.append(device_info)
            return
        kat_id = "<kat_id>"
        #device_info 的键会自动去重，如果发现相同的键 ，则会用新的键值覆盖旧键值


        if device_info.has_key("hasFile_" + self.xls.replace('.','_')):
            if device_info["hasFile_" + self.xls.replace('.','_')] == 'pass':

                maplist = self.xls_analysis(device,kat_id)
                for key,value in maplist:
                    device_info[key] = value
                pass
        else:
            if self.mUtil.hasFile(os.path.join(self.path,device),self.xls) == True:
                device_info["hasFile_" + self.xls.replace('.','_')] = 'pass'

                maplist = self.xls_analysis(device,kat_id)
                for key,value in maplist:
                    device_info[key] = value
                pass
            else:
                device_info["hasFile_" + self.xls.replace('.','_')] = 'fail'

        self.suffix_process_devices.append(device_info)

    def xls_analysis(self,device,kat_id):
        kat_id = None
        kat_uid = None
        maplist= []
        pattern = re.compile("^"+self.xls+"$")
        # xls_absolute_path = self.mUtil.getAbsoluteFilePath(os.path.join(self.path,device),self.xls)
        xlsAbsPath = AbsPath(pattern)
        if xlsAbsPath.hasFile(os.path.join(self.path,device)):
            xls_absolute_path = xlsAbsPath.getAbsoluteFilePath()
            mfile = open(xls_absolute_path,'r')
            #分析xls 日志逻辑：
            content = mfile.read()
            maplist.append(("xls", content))
            mfile.close()
            return maplist
        else:
            return maplist

    def analysisEmpl(self,device):
        if device.has_key('xls'):
            device['solution'] = device["xls"].decode('utf-8')
            device['result'] = 'pass'
        else:
            device['result'] = 'fail'

if __name__ == '__main__':
    pass