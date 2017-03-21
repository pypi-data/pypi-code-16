# -*- coding: UTF-8 -*- 
from yixinPyLib.testcaseupload import uploadTestcase 
import time

class AppMethod():
    logger = None
    pid = 0
    #初始化
    def __init__(self,driver):
        self.driver = driver
    #日志处理
    def __setlog__(self,log):
        self.logger = log
    def __log__(self,msg):
        if self.logger == None:
            try:
                print msg
            except:
                pass
        else:
            self.logger.info(msg)
    def __setpid__(self,p):
        self.pid = p
    #有延迟的完成完成一个测试用例
    def FinishTestCase_timeout(self,caseid,resstr,t):
        if self.pid != 0:
            time.sleep(t)
            self.FinishTestCase(caseid,resstr)

    #完成一个测试用例
    def FinishTestCase(self,caseid,resstr):
        if self.pid != 0:
            http = uploadTestcase.uploadTestcase(self.pid)
            testcase = http.gettestcase(caseid)
            self.__log__(u'记录测试用例：' + testcase[u'name'])
            picpath = "temp.png"
            self.driver.get_screenshot_as_file(picpath)
            picurl = http.uploadPic(picpath,caseid)
            #result = http.uploadResult(caseid,picurl)
            result = http.uploadResultAssertRes(caseid,picurl,resstr)
            self.__log__(u'当前测试用例：' +result)
    
    def FinishTestCase_attachment_timeout(self,caseid,resstr,step,t):
        if self.pid != 0:
            time.sleep(t)
            http = uploadTestcase.uploadTestcase(self.pid)
            testcase = http.gettestcase(caseid)
            self.__log__(u'记录测试用例：' + testcase[u'name'])
            picpath = "temp.png"
            self.driver.get_screenshot_as_file(picpath)
            picurl = http.uploadPic_attachment(picpath,caseid,step)
            result = http.uploadResultAssertRes_attachment(caseid,picurl,resstr,step)
            self.__log__(u'当前测试用例：' +result)


