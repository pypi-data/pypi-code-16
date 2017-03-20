# coding:utf-8
'''
Created on 2017年3月2日

@author: panluhai
'''
from . import Util
from globalVal import rootdir
from AppiumClient import AppiumClient
from AppiumClient import InvalidOperationException
from selenium.common.exceptions import TimeoutException




class BasePO(AppiumClient):
    
    def __init__(self,ymlPath=None):
        AppiumClient.__init__(self)
        self.ymlPath = ymlPath

    
    def setConfigPath(self, ymlPath):
        self.ymlPath = ymlPath
        
    
    def getConfigPath(self):
        return self.ymlPath
            
    def _try_many_time_do(self, pageName, elementName, operationLocatorFun, *args):
        locatorsList = self.getByAndLocatorsByConfig(pageName, elementName)
        locatorsIndex = len(locatorsList) - 1
        for i, locatorTuple in enumerate(locatorsList):
            try:
                l = len(locatorTuple)
                assert l == 2, 'actual len(locatorTuple) is:%d' % l
                    
                by = locatorTuple[0]
                locator = locatorTuple[1]
                operationLocatorFun(by, locator, *args)
                break
            except InvalidOperationException:
                if i == locatorsIndex:
                    raise
            except TimeoutException:
                if i == locatorsIndex:
                    raise
            except AssertionError:
                if i == locatorsIndex:
                    raise    
    
    
    def _try_many_time_do_by_locator(self, pageName, elementName, operationLocatorFun, *args):
        locatorsList = self.getLocatorsByConfig(pageName, elementName)
        locatorsIndex = len(locatorsList) - 1
        for i, locatorTuple in enumerate(locatorsList):
            try:
                l = len(locatorTuple)
                assert l == 2, 'actual len(locatorTuple) is:%d' % l
                    
                by = locatorTuple[0]
                locator = locatorTuple[1]
                operationLocatorFun(by, locator, *args)
                break
            except InvalidOperationException:
                if i == locatorsIndex:
                    raise
            except TimeoutException:
                if i == locatorsIndex:
                    raise
            except AssertionError:
                if i == locatorsIndex:
                    raise
    
    
    def try_clear_text(self, pageName, elementName, index=0):
        def operationLocatorFun(by, locator, index):
            AppiumClient.clearText(self, by, locator, index)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, index)
       
    def try_click_button(self, pageName, elementName):
        def operationLocatorFun(locator):
            AppiumClient.clickButton(self,locator)
        self._try_many_time_do_by_locator(pageName, elementName,operationLocatorFun)
       
    def try_click_element(self, pageName, elementName, index=0):
        def operationLocatorFun(by, locator, index):
            AppiumClient.clickElement(self, by, locator, index)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, index)
    
    def try_click_element_by_class_name(self, pageName, elementName, index_or_name):
        def operationLocatorFun(locator,index_or_name):
            AppiumClient.clickElementByClassName(self,locator,index_or_name)
        self._try_many_time_do_by_locator(pageName, elementName,operationLocatorFun,index_or_name)
    
    
    def try_element_name_should_be(self, pageName, elementName, index=0, expected=''):
        def operationLocatorFun(by, locator, index, expected):
            AppiumClient.elementNameShouldBe(self, by, locator, index,expected)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, index, expected)
    
    def try_element_should_be_disable(self, pageName, elementName, index=0):
        def operationLocatorFun(by, locator, index):
            AppiumClient.elementShouldBeDisabled(self, by, locator, index)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, index)
    
    def try_element_should_be_enable(self, pageName, elementName, index=0):
        def operationLocatorFun(by, locator, index):
            AppiumClient.elementShouldBeEnabled(self, by, locator, index)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, index)
    
    
    def try_element_should_contain_text(self, pageName, elementName, index=0, expected='', message=''):
        def operationLocatorFun(by, locator, index, expected, message):
            AppiumClient.elementShouldContainText(self, by, locator, index, expected, message)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, index, expected, message)
    
    def try_element_should_not_contain_text(self, pageName, elementName, index=0, expected='', message=''):
        def operationLocatorFun(by, locator, index, expected, message):
            AppiumClient.elementShouldNotContainText(self, by, locator, index, expected, message)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, index, expected, message)
    
    def try_element_text_should_be(self, pageName, elementName, index=0, expected='', message=''):
        def operationLocatorFun(by, locator, index, expected, message):
            AppiumClient.elementTextShouldBe(self, by, locator, index, expected, message)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, index, expected, message)
    
    def try_element_value_should_be(self, pageName, elementName, index=0, expected=''):
        def operationLocatorFun(by, locator, index, expected):
            AppiumClient.elementValueShouldBe(self, by, locator, index, expected)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, index, expected)
    
    
    def try_input_text(self, pageName, elementName, index=0, text=''):
        def operationLocatorFun(by, locator, index, text):
            AppiumClient.inputText(self, by, locator, index, text)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, index, text)
    
    def try_input_value(self, pageName, elementName, index=0, text=''):
        def operationLocatorFun(by, locator, index, text):
            AppiumClient.inputValue(self, by, locator, index, text)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, index, text)
        
    
    def try_long_press_element(self, pageName, elementName, index=0):
        def operationLocatorFun(by, locator, index):
            AppiumClient.longPressElement(self, by, locator, index)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, index)
    
    def try_page_should_contain_element(self, pageName, elementName):
        def operationLocatorFun(by, locator):
            AppiumClient.pageShouldContainElement(self, by, locator)
        self._try_many_time_do(pageName, elementName,operationLocatorFun)
        
    def try_page_should_not_contain_element(self, pageName, elementName):
        def operationLocatorFun(by, locator):
            AppiumClient.pageShouldNotContainElement(self, by, locator)
        self._try_many_time_do(pageName, elementName,operationLocatorFun)
    
    
    def try_pinch(self, pageName, elementName, index=0, percent=200, steps=1):
        def operationLocatorFun(by, locator, index, percent, steps):
            AppiumClient.pinch(self, by, locator, index, percent, steps)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, index, percent, steps)
    
    def try_scroll_down(self, pageName, elementName, index=0):
        def operationLocatorFun(by, locator, index):
            AppiumClient.scrollDown(self, by, locator, index)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, index)
    
    def try_scroll_up(self, pageName, elementName, index=0):
        def operationLocatorFun(by, locator, index):
            AppiumClient.scrollUp(self, by, locator, index)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, index)
    
    def try_tap(self, pageName, elementName, index=0, x_offset=None, y_offset=None, count=1):
        def operationLocatorFun(by, locator, index, x_offset, y_offset, count):
            AppiumClient.tap(self, by, locator, index, x_offset, y_offset, count)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, index, x_offset, y_offset, count)
    
    def try_wait_until_element_is_visible(self, pageName, elementName, index=0, timeout=7, error=None):
        def operationLocatorFun(by, locator, timeout, error):
            AppiumClient.waitUntilElementIsVisible(self, by, locator, index, timeout, error)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, index, timeout, error)
    
    
    def try_wait_until_page_contains_element(self, pageName, elementName, timeout, error):
        def operationLocatorFun(by, locator, timeout, error):
            AppiumClient.waitUntilPageContainsElement(self, by, locator, timeout, error)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, timeout, error)
    
    def try_wait_until_page_does_not_contains_element(self, pageName, elementName, timeout, error):
        def operationLocatorFun(by, locator, timeout, error):
            AppiumClient.waitUntilPageDoesNotContainElement(self, by, locator, timeout, error)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, timeout, error)
    
    
    def try_xpath_should_match_X_Times(self, pageName, elementName, count, error):
        def operationLocatorFun(locator, count, error):
            AppiumClient.xpathShouldMatchXTimes(self, locator, count, error)
        self._try_many_time_do_by_locator(pageName, elementName,operationLocatorFun, count, error)
    
    
    def try_zoom(self, pageName, elementName, index=0, percent=200, steps=50):
        def operationLocatorFun(by, locator, index, percent, steps):
            AppiumClient.zoom(self, by, locator, index, percent, steps)
        self._try_many_time_do(pageName, elementName,operationLocatorFun, index, percent, steps)
    
        
        
    def getByAndLocatorsByConfig(self, pageName,elementName):
        r = Util.loadYamlFromFile(self.ymlPath) 
        
        print r
        
        elementsList = []
        
        locatorList = []
        
        sameNameElementList = []
        
        for d in r:
            pageDict = d['page']
            if pageDict['pageName'] == pageName:
                
                elementsList = pageDict['elements']
                
                for element in elementsList:
                    if element['name'] == elementName:
                        sameNameElementList.append(element)
                        
        
        sameNameElementList.sort(key=lambda obj:obj.get('priority'),reverse=True)   
        
        for element in sameNameElementList:
            tempBy = element['findBy'].lower().strip()
            tempValue = element['value']
            locatorList.append((tempBy, tempValue))               
                
        return locatorList
    
    
    def getLocatorsByConfig(self, pageName,elementName):
        r = Util.loadYamlFromFile(self.ymlPath) 
        
        print r
        
        elementsList = []
        
        locatorList = []
        
        sameNameElementList = []
        
        for d in r:
            pageDict = d['page']
            if pageDict['pageName'] == pageName:
                
                elementsList = pageDict['elements']
                
                for element in elementsList:
                    if element['name'] == elementName:
                        sameNameElementList.append(element)
                        
        
        sameNameElementList.sort(key=lambda obj:obj.get('priority'),reverse=True)   
        
        for element in sameNameElementList:
            tempValue = element['value']
            locatorList.append(tempValue)               
                
        return locatorList
                        
if __name__ == '__main__':
    print rootdir + '/robot_case/yingshi/pageObject/POConfig/appName_UIElements.yml'
    bo = BasePO(rootdir + '/robot_case/yingshi/pageObject/POConfig/appName_UIElements.yml')
    a = bo.getLocatorsByConfig(rootdir + '/robot_case/yingshi/pageObject/POConfig/appName_UIElements.yml', 'org.webdriver.patatiumappui.pageObject.StartPage','xx')
    print a
