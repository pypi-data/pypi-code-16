# -*- coding: UTF-8 -*- 
import time
from appium import webdriver

class androidMethod():
    '''appium公共方法封装集'''
    def __init__(self,driver):
        self.driver = driver
    def click(self,locator):
        self.driver.find_element(*locator).click()
    def isExit(self,locator):
        res = True
        try:
            self.driver.find_element(*locator)
        except Exception,e:
            res = False
        return res
    def setText(self,locator,text):
        self.driver.find_element(locator).send_keys(text)
    def getText(self,locator):
        self.driver.find_element(locator).get_attribute('text')