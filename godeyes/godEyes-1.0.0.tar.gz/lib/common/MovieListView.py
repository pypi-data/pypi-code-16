# coding:utf-8
'''
Created on 2017年3月3日

@author: panluhai
'''


from common.BasePO import BasePO
from common import Util
from common.AppiumService import AppiumService
from biz.YingshiLib import YingshiLib
from selenium.webdriver.common import by


class MovieListView(BasePO, YingshiLib):
    
    def __init__(self, ip, ymlPath):
        YingshiLib.__init__(self, ip)
        BasePO.__init__(self, ymlPath)
        
    def __del__(self):
        YingshiLib.__del__(self)
        
    def goToSearch(self):
        self.clickELementById('com.yunos.tv.yingshi.boutique:id/left_btn')
    
    def goToSearchXpath(self):
        self.clickELementByXpath('//com.yunos.tv.app.widget.LinearLayout[contains(@resource-id,"com.yunos.tv.yingshi.boutique:id/top_buttons")]/com.yunos.tv.app.widget.FrameLayout[@index=0]')
    
    def goToSearchXpath2(self):
        self.clickELementByXpath('//com.yunos.tv.app.widget.LinearLayout[@resource-id="com.yunos.tv.yingshi.boutique:id/top_buttons")]/com.yunos.tv.app.widget.FrameLayout[0]')
    
    def goToSearchUseUtil(self):
        by, locator = Util.cherryBestLocatorTuple(self.getConfigPath(), 'com.yunos.tv.yingshi.boutique/.bundle.subject.YingshiActivity', 'searchButton')
        print by
        print locator
        self.clickElement(by, locator)
    
    def try_goToSearch(self):
        self.try_click_element('com.yunos.tv.yingshi.boutique/.bundle.subject.YingshiActivity', 'searchButton')
        
if __name__ == '__main__':
    s = AppiumService()
    s.startServer()
    
    m = MovieListView('30.11.32.135', '/Users/panluhai/Documents/workspace/uttest/robot_case/yingshi/pageObject/POConfig/appName_UIElements.yml')
    m.openClient(platformName='Android',deviceName='magicbox2',appPackage='com.yunos.tv.yingshi.boutique', appActivity='com.yunos.tv.yingshi.activity.YingshiHomeActivity' ,noReset='true')
    import time
    time.sleep(5)
    m.jumpToMovieListView()
    
    time.sleep(5)
#     m.goToSearchUseUtil()
    m.try_goToSearch()
    print 'done'
#     m.goToSearch()
    