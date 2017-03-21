# -*- coding: UTF-8 -*- 
import AppMethod
import urllib2

class ScriptMethod():
    def __init__(self,driver):
        self.driver = driver
        url ='https://code.jquery.com/jquery-3.2.0.min.js'  
        data = urllib2.urlopen(url)
        result = data.read()
        self.driver.execute_script(result)
    def executeJS(self,strjs):
        self.driver.execute_script(strjs)
    def getValue(self,strjs):
        allStr = "var temp = " + strjs + ";"
        allStr += "return temp;"
        result = self.driver.execute_script(allStr)
        return result