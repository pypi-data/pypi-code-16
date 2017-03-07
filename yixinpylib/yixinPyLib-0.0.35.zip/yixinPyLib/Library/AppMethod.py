# -*- coding: UTF-8 -*- 
from testcaseupload import uploadTestcase 

class AppMethod():
    logger = None
    #初始化
    def __init__(self,driver):
        self.driver = driver
    #日志处理
    def __setlog__(self,log):
        self.logger = log
    def __log__(self,msg):
        if self.logger == None:
            print msg
        else:
            self.logger.info(msg)
    #完成一个测试用例
    def FinishTestCase(self,caseid,resstr):
        testcaseupload
        http = uploadTestcase.uploadTestcase()
        testcase = http.gettestcase(caseid)
        self.__log__(u'记录测试用例：' + testcase[u'name'])
        picpath = "temp.png"
        self.driver.get_screenshot_as_file(picpath)
        picurl = http.uploadPic(picpath,caseid)
        #result = http.uploadResult(caseid,picurl)
        result = http.uploadResultAssertRes(caseid,picurl,resstr)
        self.__log__(u'当前测试用例：' +result)


