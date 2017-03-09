# coding:utf-8
import os, sys
import tempfile
import thread
from datetime import date

from io import BytesIO

from base import utils
import zipfile, re
from base.scanner import FileScanner, FileScannerQQmusic
from random import random
# from multiprocessing.dummy import Pool as ThreadPool
import threadpool
from lab.settings import JSON_ROOT, PROJECT_ROOT
import json
from analyzer import Analyzer
import logging
from base.scanner import *
import threading, zipfile
from multiprocessing import Pool
import multiprocessing
from time import sleep
import time
import threadpool, platform
# import gevent
# import signal
import warnings

warnings.filterwarnings("ignore")

__author__ = 'creeper'
gsource_path = ""
gdst_path = ""
gsource_zip_file = ""


class DotableDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self


class Tag(object):
    def __init__(self):
        self.tag = False


'''
不经过解压流程，创建DetectUnzip
'''


class DetectUnzip(object):
    def __init__(self, sourcePath, xls, zip):
        self.sourcePath = sourcePath  # 原始数据文件路径
        self.xls = xls  # 要提取的xls文件名称
        self.zip = zip  # 要提取的压缩对象名称
        self.devices = []  # xls要输出的数据结构字典
        self.archive = None  # 压缩文件
        self.items = os.listdir(self.sourcePath)  # 每台设备压缩文件
        # 创建一个临时文件，代表需要导出的zip文件
        self.temp = tempfile.TemporaryFile()  # 要对外提供的临时压缩文件
        self.unvalid_devices, self.valid_deivces = [], []

    def analysis(self):
        start = time.time()
        self.runner_xls()
        logging.info("--------------analysis xls time-----------------" + str(time.time() - start))
        start = time.time()
        self.runner_zip()
        logging.info("--------------analysis zip time-----------------" + str(time.time() - start))

    def runner_xls(self):
        if (self.xls == 'com.kunpeng.creeper.default') or (self.xls.strip() == ''):
            return

        xls_pool = threadpool.ThreadPool(1)
        reqs = threadpool.makeRequests(self._thread_executor_xls, self.items)
        [xls_pool.putRequest(req) for req in reqs]
        xls_pool.wait()

        # gevents = [gevent.spawn(self._thread_executor_xls,device) for device in self.items]
        # gevent.joinall(gevents)

    '''压缩流程主算法'''
    def runner_zip(self):
        self.archive = zipfile.ZipFile(self.temp, 'w', zipfile.ZIP_DEFLATED)
        if (self.zip == 'com.kunpeng.creeper.default') or (self.zip.strip() == ''):
            self.archive.close()
            return
        zip_pool = threadpool.ThreadPool(1)
        reqs = threadpool.makeRequests(self._thread_executor_zip, self.items)
        [zip_pool.putRequest(req) for req in reqs]
        zip_pool.wait()

        # gevents = [gevent.spawn(self._thread_executor_zip,device) for device in self.items]
        # gevent.joinall(gevents)

        content_unvalid, content_valid = "", ""
        content_unvalid = "\n".join(self.unvalid_devices)  # 将所有无效设备的名字以回车换行符拼接在一起
        content_valid = "\n".join(self.valid_deivces)  # 将所有有效设备以回车换行符拼接在一起
        tempfd, filepath = tempfile.mkstemp()  # filepath 是生成的临时文件路径
        with open(filepath, 'wb') as temp:
            temp.write("unvalid devices:\n" + content_unvalid + "\n\n" + "valid_devices:\n" + content_valid)
            temp.seek(0)
        self.archive.write(filepath, 'devicesList.txt')
        # os.remove(filepath)
        os.close(tempfd)
        os.unlink(filepath)
        self.archive.close()

    def _thread_executor_zip(self, device):

        def _recursive_file(mzfile, pattern_file, tag):
            for zitem in mzfile.namelist():
                if zitem.endswith('.zip'):
                    biz = zipfile.ZipFile(BytesIO(mzfile.read(zitem)))
                    _recursive_file(biz, pattern_file, tag)
                elif pattern_file.search(zitem) and (not zitem.endswith("/")):  # 此分支的zitem代表文件，因为结尾没有文件夹标识符"/"
                    tag.tag = True
                    with mzfile.open(zitem, 'r') as f:
                        tempfd, filepath = tempfile.mkstemp()  # path 是创建的临时文件路径
                        with open(filepath, 'wb') as temp:
                            temp.write(f.read())
                            temp.seek(0)
                        self.archive.write(filepath, '%s.txt' % self.getDeviceName(device))
                        # os.remove(filepath)
                        os.close(tempfd)
                        os.unlink(filepath)
                    mzfile.close()
                    return
            mzfile.close()

        def _recursive_path(mzfile, pattern_path, pattern_dot, tag):  # mzfile 代表每个设备的压缩文件

            #todo 此处for循环，用来遍历此设备的压缩文件里的所有文件或者文件夹，文件的形式为xxx/xxx/xxx ; 文件夹的形式为xxx/xxx/xxx/

            for zitem in mzfile.namelist():
                # logging.info('---------------------' + str(zitem))

                #todo 如果遇到压缩文件，就递归
                if zitem.endswith('.zip'):
                    biz = zipfile.ZipFile(BytesIO(mzfile.read(zitem)))
                    _recursive_path(biz, pattern_path, pattern_dot, tag)

                # todo 此分支的zitem代表文件夹,匹配查找文件夹里的文件, 不采用  len(pattern_dot.findall(zitem)) ==1  判断是不是被搜索文件夹下的文件，采用  not zitem.endswith(r"/") 方式
                elif pattern_path.search(zitem) and not zitem.endswith(r"/"):
                    tag.tag = True
                    # todo 首先生成一个临时文件夹路径，此事临时文件夹在系统磁盘上申请了空间
                    tempname = tempfile.mkdtemp()
                    # todo #以设备名作为文件夹的名称写入目标压缩文件
                    self.archive.write(tempname, '%s' % self.getDeviceName(device))
                    # todo #删除系统磁盘上的临时文件夹
                    os.removedirs(tempname)

                    # with os.tmpfile() as tempdir:
                    #     self.archive.write(os.path.abspath(tempdir),'%s' % self.getDeviceName(device))

                    with mzfile.open(zitem, 'r') as f:
                        #todo filepath 是生成的临时文件路径
                        tempfd, filepath = tempfile.mkstemp()
                        with open(filepath, 'wb') as temp:
                            temp.write(f.read())
                            temp.seek(0)
                         # todo 以下方式保留原来的目录层级结构，防止重名； 也可以尝试 os.path.split(zitem)[-1] 就会修改层级结构，只用目标寻路文件的名称决定最终层级结构
                        self.archive.write(filepath, "%s\\%s" % (self.getDeviceName(device),zitem))
                        os.close(tempfd)
                        os.unlink(filepath)
                        # os.remove(filepath)
            mzfile.close()

        def _recursive_path_crash(mzfile, pattern_path, pattern_dot, tag):  # mzfile 代表每个设备的压缩文件

            for zitem in mzfile.namelist():
                # logging.info('---------------------' + str(zitem))
                if zitem.endswith('.zip'):
                    biz = zipfile.ZipFile(BytesIO(mzfile.read(zitem)))
                    _recursive_path_crash(biz, pattern_path, pattern_dot, tag)
                # todo 此分支的zitem代表文件夹,匹配查找文件夹里的文件, 不采用  len(pattern_dot.findall(zitem)) ==1  判断是不是被搜索文件夹下的文件，采用  not zitem.endswith(r"/") 方式
                elif pattern_path.search(zitem) and not zitem.endswith(r"/"):
                    logging.info("zitem:" + zitem + "\t" + str((pattern_dot.findall(zitem))))
                    tag.tag = True
                    # tempname = tempfile.mkdtemp()   #首先生成一个临时文件夹路径，目的是往archive里添加一个以设备名命名的文件夹
                    # self.archive.write(tempname,'%s' % self.getDeviceName(device))
                    # os.removedirs(tempname)

                    with mzfile.open(zitem, 'r') as f:
                        tempfd, filepath = tempfile.mkstemp()  # filepath 是生成的临时文件路径
                        with open(filepath, 'wb') as temp:
                            temp.write(f.read())
                            temp.seek(0)
                        self.archive.write(filepath, "%s" % self.getDeviceName(device) + "_" + os.path.split(zitem)[
                            -1])  # todo这里可以尝试不重新命名 os.path.split(zitem)[-1] ,不改名字，就会保留原来的目录层级结构，防止重名
                        os.close(tempfd)
                        os.unlink(filepath)
                        # os.remove(filepath)
            mzfile.close()

        abspath = os.path.join(self.sourcePath, device)
        mzfile = zipfile.ZipFile(abspath)
        tag = Tag()  # 标志此设备中是否有被搜索字段

        #todo -------此处进入压缩流程入口，通过字符串是否带.来判断要采取哪个分支处理------------------------------------------------------------------------------------------
        if (self.zip.find(".") != -1):
            #文件处理
            pattern_file = re.compile(self.zip.strip() + "$", re.I)
            _recursive_file(mzfile, pattern_file, tag)
        elif (self.zip.strip() == "crash"):
            #crash处理
            pattern_path = re.compile(self.zip.strip() + "/", re.I)
            pattern_dot = re.compile(r'\.')
            _recursive_path_crash(mzfile, pattern_path, pattern_dot, tag)
        else:
            #文件夹处理
            pattern_path = re.compile(self.zip.strip() + "/", re.I)
            pattern_dot = re.compile(r'\.')
            _recursive_path(mzfile, pattern_path, pattern_dot, tag)

        if not tag.tag:  # 如果没有找到，则记录失败设备
            self.unvalid_devices.append(self.getDeviceName(device))
        else:  # 应老板要求，记录有效设备列表
            self.valid_deivces.append(self.getDeviceName(device))
        mzfile.close()

    def _thread_executor_zip_crash(self, device):

        def _recursive_file(mzfile, pattern_file, tag):
            for zitem in mzfile.namelist():
                if zitem.endswith('.zip'):
                    biz = zipfile.ZipFile(BytesIO(mzfile.read(zitem)))
                    _recursive_file(biz, pattern_file, tag)
                elif pattern_file.search(zitem) and (not zitem.endswith("/")):  # 此分支的zitem代表文件，因为结尾没有文件夹标识符"/"
                    tag.tag = True
                    with mzfile.open(zitem, 'r') as f:
                        tempfd, filepath = tempfile.mkstemp()  # path 是创建的临时文件路径
                        with open(filepath, 'wb') as temp:
                            temp.write(f.read())
                            temp.seek(0)
                        self.archive.write(filepath, '%s.txt' % self.getDeviceName(device))
                        # os.remove(filepath)
                        os.close(tempfd)
                        os.unlink(filepath)
                    mzfile.close()
                    return
            mzfile.close()

        def _recursive_path(mzfile, pattern_path, pattern_dot, tag):  # mzfile 代表每个设备的压缩文件

            for zitem in mzfile.namelist():
                # logging.info('---------------------' + str(zitem))
                if zitem.endswith('.zip'):
                    biz = zipfile.ZipFile(BytesIO(mzfile.read(zitem)))
                    _recursive_path(biz, pattern_path, pattern_dot, tag)
                elif pattern_path.search(zitem) and len(pattern_dot.findall(zitem)) == 1:  # 此分支的zitem代表文件夹,匹配查找文件夹里的文件
                    tag.tag = True
                    tempname = tempfile.mkdtemp()  # 首先生成一个临时文件夹路径，目的是往archive里添加一个以设备名命名的文件夹
                    self.archive.write(tempname, '%s' % self.getDeviceName(device))
                    os.removedirs(tempname)

                    # with os.tmpfile() as tempdir:
                    #     self.archive.write(os.path.abspath(tempdir),'%s' % self.getDeviceName(device))

                    with mzfile.open(zitem, 'r') as f:
                        tempfd, filepath = tempfile.mkstemp()  # filepath 是生成的临时文件路径
                        with open(filepath, 'wb') as temp:
                            temp.write(f.read())
                            temp.seek(0)
                        self.archive.write(filepath, "%s\\%s" % (self.getDeviceName(device),
                                                                 zitem))  # todo//这里可以尝试不重新命名 os.path.split(zitem)[-1] ,不改名字，就会保留原来的目录层级结构，防止重名
                        os.close(tempfd)
                        os.unlink(filepath)
                        # os.remove(filepath)
            mzfile.close()

        abspath = os.path.join(self.sourcePath, device)
        mzfile = zipfile.ZipFile(abspath)
        tag = Tag()  # 标志此设备中是否有被搜索字段

        if (self.zip.find(".") != -1):
            pattern_file = re.compile(self.zip + "$", re.I)
            _recursive_file(mzfile, pattern_file, tag)
        else:
            pattern_path = re.compile(self.zip + "/", re.I)
            pattern_dot = re.compile(r'\.')
            _recursive_path(mzfile, pattern_path, pattern_dot, tag)

        if not tag.tag:  # 如果没有找到，则记录失败设备
            self.unvalid_devices.append(self.getDeviceName(device))
        mzfile.close()

    def _thread_executor_xls(self, device):
        def _recursive(mzfile, pattern, device_info):
            for zitem in mzfile.namelist():
                if zitem.endswith('.zip'):
                    biz = zipfile.ZipFile(BytesIO(mzfile.read(zitem)))
                    _recursive(biz, pattern, device_info)
                elif pattern.search(zitem):
                    device_info['solution'] = mzfile.read(zitem).decode('utf-8')
                    device_info['result'] = 'pass'
                    return

        device_info = {"solution": '',
                       "result": 'fail',
                       "device": self.getDeviceName(device),
                       }
        abspath = os.path.join(self.sourcePath, device)
        mzfile = zipfile.ZipFile(abspath)
        pattern = re.compile(self.xls)
        _recursive(mzfile, pattern, device_info)
        self.devices.append(device_info)

    def getDeviceName(self, filename):
        year = "_" + str(date.today().year)
        return filename.split(year)[0].split("/")[-1]


'''
经过解压流程,创建Detect对象
'''


class Detect(object):
    def __init__(self, path, mUtil):
        self.path = path
        self.mUtil = mUtil
        self.devices = []
        self.blackListOfFile = ['error.txt', 'crashlog.txt']
        self.luaunit_name = "LuaUnit.txt"
        self.sessionId = ''
        self.luaunit_invalid_devices = {"Result": 0, "LuaUnit": 0, "SessionId": 0, "LifeCycle": 0}
        self.LIFECYCLE = "com.kunpeng.kapalai.kat.log"
        self.pool = threadpool.ThreadPool(10)
        self.checkDevices_pool = threadpool.ThreadPool(10)

    def setSessionId(self, sessionId):
        self.sessionId = sessionId

    def getLuaunitInvalidDevices(self):
        return DotableDict(self.luaunit_invalid_devices)

    def luaunit(self, apis):
        for device in os.listdir(self.path):
            # 统计LuaUnit单元测试中有效设备的方法: 有Result文件夹，有LuaUnit.txt文件，SessionId正确，生命周期正确
            if self.mUtil.hasDirectory(os.path.join(self.path, device), "Result"):
                if self.mUtil.hasFile(os.path.join(self.path, device, "Result"), self.luaunit_name):
                    with open(os.path.join(self.path, device, "Result", self.luaunit_name), 'r') as luaunit:
                        content = luaunit.read().decode("utf-8")
                        with open(os.path.join(JSON_ROOT, "luaunit_lifecycle_json.txt"), 'r') as luaunit_lifecycle_json:
                            luaunit_lifecycle_config = json.load(luaunit_lifecycle_json)
                            try:
                                with open(os.path.join(self.path, device, "logs", self.LIFECYCLE), 'r') as logs:
                                    logs_content = logs.read()
                            except:
                                pass
                            if (False not in (self.handleConfigItem(logs_content, config_item) for config_item in
                                              luaunit_lifecycle_config)):
                                device_info = {"device": device}
                                apis_fail, apis_pass = [], []
                                for api in apis.split("|"):
                                    # api:valid 与 api:pass
                                    if api + ":valid" in content:
                                        if api + ":pass" in content:
                                            apis_pass.append(api)
                                        else:
                                            apis_fail.append(api)
                                device_info['luaunit_pass'] = "|".join(apis_pass)
                                device_info['luaunit_fail'] = "|".join(apis_fail)
                                if self.mUtil.hasFile(os.path.join(self.path, device, "Result"), "error.txt"):
                                    device_info['fail_detail'] = 'fail'
                                else:
                                    device_info['fail_detail'] = 'pass'
                                self.devices.append(device_info)
                            else:
                                # lifecycle failed
                                self.luaunit_invalid_devices["LifeCycle"] += 1
                                # if (self.sessionId in content) or ("SessionId" not in content):
                                #     pass
                                # else:
                                #     self.luaunit_invalid_devices["SessionId"] += 1
                else:
                    self.luaunit_invalid_devices["LuaUnit"] += 1
            else:
                self.luaunit_invalid_devices["Result"] += 1

    def handleConfigItem(self, content, config_item):
        for tag, item in config_item['live']:
            item = item.encode(sys.getfilesystemencoding())
            if tag == 0:  # 字符串或者带变量的字符串
                if content.find(item) != -1:
                    pass
                else:
                    return True
            elif tag == 1:  # 正则表达式或者带变量的正则表达式
                if re.search(item, content):
                    pass
                else:
                    return True
            elif tag == 2:  # 字符串或者带变量的字符串（取反）
                if content.find(item) == -1:
                    pass
                else:
                    return True
            elif tag == 3:  # 正则表达式或者带变量的正则表达式(取反)
                if re.search(item, content) == None:
                    pass
                else:
                    return True
            elif tag == 4:  # 字符串或者带变量的字符串出现次数>=4次,或者 正则表达式或者带变量的正则表达式出现次数>=4次
                if len(set(re.findall(item, content))) >= 4:
                    pass
                else:
                    return True

        return False

    def hasDirectory(self, Rfoldernames):
        for device in os.listdir(self.path):
            device_info = {"device": device}
            for Rfoldername in Rfoldernames:
                if "hasDirectory_" + str(Rfoldername) not in device_info.keys():
                    if self.mUtil.hasDirectory(os.path.join(self.path, device), Rfoldername) == True:
                        device_info["hasDirectory_" + str(Rfoldername.replace('.', '_'))] = 'pass'
                    else:
                        device_info["hasDirectory_" + str(Rfoldername.replace('.', '_'))] = 'fail'

            self.devices.append(device_info)

    def hasFile(self, Rfilenames):
        for device_info in self.devices:
            device = device_info['device']
            for Rfilename in Rfilenames:
                if "hasFile_" + str(Rfilename) not in device_info.keys():
                    if self.mUtil.hasFile(os.path.join(self.path, device), Rfilename) == True:
                        if Rfilename in self.blackListOfFile:
                            device_info["hasFile_" + str(Rfilename.replace('.', '_'))] = 'fail'
                        else:
                            device_info["hasFile_" + str(Rfilename.replace('.', '_'))] = 'pass'
                    else:
                        if Rfilename in self.blackListOfFile:
                            device_info["hasFile_" + str(Rfilename.replace('.', '_'))] = 'pass'
                        else:
                            device_info["hasFile_" + str(Rfilename.replace('.', '_'))] = 'fail'

    def contentNumOfDir(self, title_rdirname):
        for device_info in self.devices:
            device = device_info['device']
            title, rdirname = title_rdirname
            if self.mUtil.contentNumOfDir(os.path.join(self.path, device, rdirname)) >= 1:
                device_info[title] = 'pass'
            else:
                device_info[title] = 'fail'

    def getFileScanner(self, scanner, xls):
        self.fs = scanner(self.path, self.devices, self.mUtil, self.LIFECYCLE, xls)
        return self.fs

    def getLuaUnitDevices(self):
        return self.devices

    def checkDevices(self):
        for idx, device in enumerate(self.devices):
            if device['device'].find('logcat') != -1:
                self.devices.pop(idx)

    def getRootPath(self):
        return self.path

    def analysis(self):
        self.fs.process()
        self.devices = self.fs.suffix_process_devices
        reqs = threadpool.makeRequests(self.analysisEmpl, self.devices)
        [self.pool.putRequest(req) for req in reqs]
        self.pool.wait()

    def analysisEmpl(self, device):
        self.fs.analysisEmpl(device)

    def getDevicesByKeyword(self, keyword):
        return [device_info['device'] for device_info in self.devices if keyword in device_info.keys()]

    def getFailDetailByDeviceName(self, name):
        for device_info in self.devices:
            if name == device_info['device']:
                return device_info['fail_detail']

        return "没有找到被测设备"

    def getAllKeywords(self):
        titles = []
        for device_info in self.devices:
            for item in device_info.keys():
                if item not in titles:
                    titles.append(item)
        return titles

    def getAllDevicesName(self):
        return [device_info['device'] for device_info in self.devices]


class unzipSource(object):
    # 创建临时文件夹用来承接之前dst_path的工作
    dtemp = tempfile.mkdtemp()

    def __init__(self, source_zip_file, source_path, dst_path, mUtil, process_num=1):
        assert isinstance(mUtil, utils.Util)
        self.mUtil = mUtil
        self.source_zip_file = source_zip_file
        global gsource_zip_file
        gsource_zip_file = source_zip_file
        self.source_path = source_path
        global gsource_path
        gsource_path = source_path
        self.dst_path = dst_path
        global gdst_path
        gdst_path = dst_path
        self.PROCESS_NUM = process_num
        self.createPath(dst_path)
        self.pattern = re.compile(r"\d*.jpg")
        self.zipfile = {'num': 0, 'comment': "Total compressed file provided by the platform", 'device': '-'}
        self.valid_zipfile = {'num': 0,
                              'comment': "Effective compressed files number,\nUnvalid compressed files don't have any content in it",
                              'device': ''}
        self.resultzip = {'num': 0,
                          'comment': "Number of effective compressed files where\n we can find Result.zip in it",
                          'device': ''}
        self.valid_resultzip = {'num': 0, 'comment': "Total effective result.zip in all Result.zip devices",
                                'device': ''}
        self.task_id = ''
        # self.pool = ThreadPool(8)
        self.pool = threadpool.ThreadPool(1000)
        self.mylock = thread.allocate_lock()
        self.zipitem = None

    def unzip_process(self, mfile):
        APK_PATTERN = re.compile(r"apk$")
        if mfile.endswith(".zip"):
            file_name = self.getDeviceName(mfile)
            # 创建临时文件夹用来承接之前sourc_path的工作
            dtemp = tempfile.mkdtemp()
            self.zipfile['num'] += 1
            self.zipitem.extract(mfile, dtemp)
            if self.mUtil.isZipFile(os.path.join(dtemp, mfile)):
                self.valid_zipfile['num'] += 1
                tmp_zipfile_object = zipfile.ZipFile(os.path.join(dtemp, mfile))
                if len(tmp_zipfile_object.namelist()) == 0:
                    # 创建目录
                    os.mkdir(os.path.join(self.dst_path, file_name))
                else:
                    tmp_zipfile_object.extractall(os.path.join(self.dst_path, file_name))

                if "Result.zip" in os.listdir(os.path.join(self.dst_path, file_name)):
                    self.resultzip['num'] += 1
                    if self.mUtil.isZipFile(os.path.join(self.dst_path, file_name, "Result.zip")):
                        self.valid_resultzip['num'] += 1
                        resultzipfile = zipfile.ZipFile(os.path.join(self.dst_path, file_name, "Result.zip"))
                        for item in resultzipfile.namelist():
                            if (re.search(APK_PATTERN, item) == None) or (item.find('res.zip') == -1):
                                try:
                                    resultzipfile.extract(item, os.path.join(self.dst_path, file_name))
                                except:
                                    # Result.zip 里面还有Result.zip
                                    pass

                    else:
                        self.valid_resultzip['device'] += self.getDeviceName(mfile) + '\n'

                else:
                    self.resultzip['device'] += self.getDeviceName(mfile) + '\n'

            else:
                self.valid_zipfile['device'] += file_name + '\n'

    def unzip_process2(self, mfile):
        APK_PATTERN = re.compile(r"apk$")
        if mfile.endswith(".zip"):
            file_name = self.getDeviceName(mfile)
            self.zipfile['num'] += 1
            if self.mUtil.isZipFile(os.path.join(self.source_zip_file, mfile)):
                self.valid_zipfile['num'] += 1
                tmp_zipfile_object = zipfile.ZipFile(os.path.join(self.source_zip_file, mfile))
                if len(tmp_zipfile_object.namelist()) == 0:
                    os.mkdir(os.path.join(unzipSource.dtemp, file_name))
                else:
                    tmp_zipfile_object.extractall(os.path.join(unzipSource.dtemp, file_name))
                if "Result.zip" in os.listdir(os.path.join(unzipSource.dtemp, file_name)):
                    self.resultzip['num'] += 1
                    if self.mUtil.isZipFile(os.path.join(unzipSource.dtemp, file_name, "Result.zip")):
                        self.valid_resultzip['num'] += 1
                        resultzipfile = zipfile.ZipFile(os.path.join(unzipSource.dtemp, file_name, "Result.zip"))
                        for item in resultzipfile.namelist():
                            if (re.search(APK_PATTERN, item) == None) or (item.find('res.zip') == -1):
                                try:
                                    resultzipfile.extract(item, os.path.join(unzipSource.dtemp, file_name))
                                except:
                                    # Result.zip 里面还有Result.zip
                                    pass
                    else:
                        self.valid_resultzip['device'] += self.getDeviceName(mfile) + '\n'
                else:
                    self.resultzip['device'] += self.getDeviceName(mfile) + '\n'
            else:
                self.valid_zipfile['device'] += file_name + '\n'

    def unzip(self):
        # 首先删除source_path 和 dst_path
        self.mUtil.delete_file_folder(self.source_path)
        self.mUtil.delete_file_folder(self.dst_path)

        if zipfile.is_zipfile(self.source_zip_file):
            self.task_id = os.path.basename(self.source_zip_file).split(".")[0]  # os.path.splitext(path)[0]
            self.zipitem = zipfile.ZipFile(self.source_zip_file)
            zipfiles = self.zipitem.namelist()
            # reqs = threadpool.makeRequests(self.unzip_process, zipfiles)
            # [self.pool.putRequest(req) for req in reqs]
            # self.pool.wait()
            # gevent.signal(signal.SIGINT, gevent.kill)
            # gevent.signal(signal.SIGTERM, gevent.kill)
            # gevents = [gevent.spawn(self.unzip_process, item) for item in zipfiles]
            # gevent.joinall(gevents)
        else:
            self.task_id = os.path.basename(self.source_zip_file)
            zipfiles = os.listdir(self.source_zip_file)
            # gevents = [gevent.spawn(self.unzip_process2,item) for item in zipfiles]
            # gevent.joinall(gevents)

    def createPath(self, path):
        if os.path.exists(path):
            self.mUtil.delete_file_folder(path)
        os.mkdir(path)

    def getDeviceName(self, filename):
        year = "_" + str(date.today().year)
        return filename.split(year)[0].split("/")[-1]


def unzip_process_multi_step1(dictmfile):
    d, mfile = dictmfile
    if mfile.endswith(".zip"):
        zipitem = zipfile.ZipFile(d['gsource_zip_file'])
        zipitem.extract(mfile, d['gsource_path'])


def unzip_process_multi_step2(mfile):
    APK_PATTERN = re.compile(r"apk$")
    year = "_" + str(date.today().year)
    file_name = mfile.split(year)[0].split("/")[-1]
    if zipfile.is_zipfile(os.path.join(r"d:\source", mfile)):
        tmp_zipfile_object = zipfile.ZipFile(os.path.join(r"d:\source", mfile))
        if len(tmp_zipfile_object.namelist()) == 0:
            # 创建目录
            os.mkdir(os.path.join(r"d:\dst", file_name))
        else:
            tmp_zipfile_object.extractall(os.path.join(r"d:\dst", file_name))

        if "Result.zip" in os.listdir(os.path.join(r"d:\dst", file_name)):
            if zipfile.is_zipfile(os.path.join(r"d:\dst", file_name, "Result.zip")):
                resultzipfile = zipfile.ZipFile(os.path.join(r"d:\dst", file_name, "Result.zip"))
                for item in resultzipfile.namelist():
                    if (re.search(APK_PATTERN, item) == None) or (item.find('res.zip') == -1):
                        try:
                            resultzipfile.extract(item, os.path.join(r"d:\dst", file_name))
                        except:
                            # Result.zip 里面还有Result.zip
                            pass
            else:
                pass
        else:
            pass
    else:
        pass


def threadworker(d, L):
    dictlist = [d] * len(L)
    maplist = zip(dictlist, L)
    if "64" in ",".join(platform.architecture()):
        threadNum = 1000
    else:
        threadNum = 500
    tpool = threadpool.ThreadPool(threadNum)
    requests = threadpool.makeRequests(unzip_process_multi_step1, maplist)
    [tpool.putRequest(req) for req in requests]
    tpool.wait()
    # requests = threadpool.makeRequests(unzip_process_multi_step2, L)
    # [tpool.putRequest(req) for req in requests]
    # tpool.wait()


def master(itemsource):
    cpu_count = multiprocessing.cpu_count()
    mgr = multiprocessing.Manager()
    d = mgr.dict()
    global gsource_path
    global gdst_path
    global gsource_zip_file
    d['gsource_path'] = gsource_path
    d['gdst_path'] = gdst_path
    d['gsource_zip_file'] = gsource_zip_file
    slice_itemsource = div_list(itemsource, cpu_count)
    itemsource = None
    jobs = []
    for itemsource in slice_itemsource:
        jobs.append(multiprocessing.Process(target=threadworker, args=(d, itemsource)))
    for j in jobs:
        j.start()
    for j in jobs:
        j.join()


def div_list(ls, n):
    ls_len = len(ls)
    if n > ls_len:
        return ls
    elif n == ls_len:
        return [[i] for i in ls]
    else:
        j = ls_len / n
        k = ls_len % n
        ls_return = []
        for i in xrange(0, (n - 1) * j, j):
            ls_return.append(ls[i:i + j])
        ls_return.append(ls[(n - 1) * j:])
        return ls_return


if __name__ == "__main__":
    mUtil = utils.Util()
    process = unzipSource(source_zip_file=r"C:\Users\SJKP\Desktop\3339.zip", \
                          source_path=r"d:\source", dst_path=r"d:\dst_path", mUtil=mUtil)
    import time

    start = time.time()
    process.unzip()
    end = time.time()
    print 'end-start:', end - start
