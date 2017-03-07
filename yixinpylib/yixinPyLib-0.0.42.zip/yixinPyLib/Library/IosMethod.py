# -*- coding: UTF-8 -*- 
import time
from appium import webdriver
import AppMethod

class iosMethod(AppMethod.AppMethod):
    logger = None
    '''appium公共方法封装集'''
    def __init__(self,driver):
        self.driver = driver
    def __setlog__(self,log):
        self.logger = log
    def __log__(self,msg):
        if self.logger == None:
            print msg
        else:
            self.logger.info(msg)
    def click(self,locator):
        self.wait(locator)
        self.__log__("click " + str(locator[1]))
        self.driver.find_element(*locator[0]).click()
            
    def isExit(self,locator):
        res = True
        try:
            self.wait(locator)
            self.__log__("isExit " + str(locator[1]))
            self.driver.find_element(*locator[0])
        except Exception,e:
            res = False
        return res
    def setText(self,locator,text):
        self.wait(locator)
        self.__log__("setText " + str(locator[1]))
        self.driver.find_element(*locator[0]).set_value(text)
        return
    def getText(self,locator):
        self.wait(locator)
        self.__log__("getText " + str(locator[1]))
        return self.driver.find_element(*locator[0]).get_attribute('label')
    def getValue(self,locator):
        self.wait(locator)
        self.__log__("getText " + str(locator[1]))
        return self.driver.find_element(*locator[0]).get_attribute('value')
    def Sleep(self,t):
        time.sleep(t)
    #轻触一个界面元素
    def tap(self,locator):
        self.wait(locator)
        a = self.driver.find_element(*locator[0])
        l = a.location
        x = int(l.get('x'))+20
        y = int(l.get('y'))+20
        self.driver.tap([(x,y)],1000)
    def tap2(self,locator,time=500):
        self.wait(locator)
        a = self.driver.find_element(*locator[0])
        l = a.location
        x = int(l.get('x'))+20
        y = int(l.get('y'))+20
        self.driver.tap([(x,y)],time)
    #获取一个列表的数量
    def getLength(self,locator):
        self.wait(locator)
        return len(self.driver.find_elements(*locator[0]))
    #判断一个列表中的元素对应个数的位置是否存在
    def isExit2(self,locator,count):
        self.wait(locator)
        res = False
        try:
            list = self.driver.find_elements(*locator[0])
            for i,one in enumerate(list):
                if i == count:
                    res = True
        except Exception,e:
            res = False
        return res
    def getText2(self,locator,count):
        self.wait(locator)
        result =''
        if len(locator) == 3:
            list = self.driver.find_elements(*locator[0])
            for i,one in enumerate(list):
                if i == count:
                    result = one.get_attribute('name')
                    break
        elif len(locator) == 4:
            list = self.driver.find_elements(*locator[0])
            for i,one in enumerate(list):
                if i == count:
                    result = one.find_element(*locator[3]).get_attribute('name')
                    break
        if len(result) > 0 :
            pass
            #self.logger.info(u'查找到信息：'+result)
        else:
            pass
            #self.logger.info(u'未找到信息')
        return result
    def click2(self,locator,count):
        self.wait(locator)
        if len(locator) == 3:
            list = self.driver.find_elements(*locator[0])
            for i,one in enumerate(list):
                if i == count:
                    one.click()
                    break
        elif len(locator) == 4:
            list = self.driver.find_elements(*locator[0])
            for i,one in enumerate(list):
                if i == count:
                    one.find_element(*locator[3]).click()
                    break
        return
    def setText2(self,locator,count,text):
        self.wait(locator)
        result =''
        list = self.driver.find_elements(*locator[0])
        for i,one in enumerate(list):
            if i == count:
                self.DeleteStr()
                one.set_value(text)
                break
        return
    def findelement(self,locator):
        ele = None
        try:
            ele = self.driver.find_elements(*locator[0])
        except:
            print traceback.print_exc()
        return ele
    def clearText(self, locator):
        self.wait(locator)
        ele = self.driver.find_elements(*locator[0])
        ele.set_value("")
        return
    def wait(self, locator):
        self.__log__("wait time:" + str(locator[2]))
        self.driver.implicitly_wait(locator[2])

    def MoveUp(self):
        self.__log__(u'向上移动')
        time.sleep(1)
        windows = self.driver.get_window_size()
        width = windows["width"]
        height = windows["height"]
        self.driver.swipe(start_x=width/2, start_y=height-200, end_x=width/2, end_y=200, duration=1000)
    
    def MoveDown(self):
        self.__log__(u'向下移动')
        windows = self.driver.get_window_size()
        width = windows["width"]
        height = windows["height"]
        self.driver.swipe(start_x=width/2, start_y=height/2, end_x=width/2, end_y=height-200, duration=1000)
        time.sleep(1)

    def CancelBtn(self):
        time.sleep(1)
        xpath = "//UIANavigationBar[1]/UIAButton[contains(@label,'取消')]"
        res = True
        try:
            self.driver.find_element_by_xpath(xpath)
        except Exception,e:
            res = False
            self.__log__(e)
        if res:
            ele = self.driver.find_element_by_xpath(xpath)
            ele.click()
        time.sleep(2)

    def BackBtn(self):
        xpath = "//UIANavigationBar[1]/UIAButton[contains(@label,'返回')]"
        time.sleep(1)
        res = True
        try:
            self.driver.find_element_by_xpath(xpath)
        except Exception,e:
            res = False
            self.__log__(e)
        if res:
            ele = self.driver.find_element_by_xpath(xpath)
            self.__log__(ele.location.get('x'))
            self.driver.tap([(15,35)],500)
        time.sleep(2)