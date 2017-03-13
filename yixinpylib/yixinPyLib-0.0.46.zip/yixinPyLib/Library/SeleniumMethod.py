# _*_ coding:utf-8 _*_
"""
Created on 2016年10月21日

@author: wuyunpeng
"""
# class SeleniumMethod():



import traceback

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait


class seleniumMethod:
    """selenium公共方法封装集"""

    def __init__(self, driver):
        self.driver = driver

    """
        封装点击,文本输入,查找元素方法
    """

    def public_click(self, locator):
        """入参，元组(By.ID,"locator")"""
        # 点击元素方法
        try:
            self.wait(locator)
            self.findElement(*locator).click()
        except:
            print traceback.print_exc()

    def public_clicks(self, locator):
        # 公共点击菜单方法
        try:
            list1 = self.findElements(*locator)
            for i in list1:
                i.click()
        except:
            print traceback.print_exc()

    def input_text(self, input_locator, text):
        """入参，元组(By.ID,"locator")"""
        # 文本框输入方法
        try:
            self.wait(input_locator)
            e = self.findElement(*input_locator)
            e.clear()
            e.send_keys(text)
        except:
            print traceback.print_exc()

    def findElement( self, *loc):
        """入参，元组(By.ID,"locator")"""
        # 查找单元素
        try:
            return self.driver.find_element(*loc)
        except:
            print traceback.print_exc()

    def findElements(self, loc):
        """入参，元组(By.ID,"locator")"""
        # 查找多元素
        try:
            return self.driver.find_elements(*loc)
        except:
            print traceback.print_exc()

    def get_ele_text(self, locator):
        """入参，元组(By.ID,"locator")"""
        # 获取元素文本
        try:
            self.wait(locator)
            text1 = self.findElement(*locator).text
            return text1
        except:
            print traceback.print_exc()

    def get_public_value_text(self, locator, value):
        """入参value_locator，元组(By.ID,"locator")
        value:要获取值的属性名
            """
        # 公共获取value属性值
        try:
            self.wait(locator)
            text = self.findElement(*locator).get_attribute(value)
            return text
        except:
            print traceback.print_exc()

    def get_public_select(self, select_locator, text):
        """入参value_locator，元组(By.ID,"locator")
        text:下拉框文本值
            """
        # 选择下拉框
        try:
            self.wait(select_locator)
            Select(self.findElement(*select_locator)).select_by_visible_text(text)
        except:
            print traceback.print_exc()

    """=============================================="""
    """
        键盘事件
    """

    def Tab(self, loc):
        """Tab键  
        @loc 元素地址，格式：元组(By.ID,"地址") """
        self.findElement(*loc).send_keys(Keys.TAB)

    def Enter(self, loc):
        """Enter回车键
        @loc 元素地址，格式：元组(By.ID,"地址")"""
        self.findElement(*loc).send_keys(Keys.ENTER)

    def SelectAll(self, loc):
        """Ctrl+a全选
        @loc 元素地址，格式：元组(By.ID,"地址")"""
        self.findElement(*loc).send_keys(Keys.CONTROL, 'a')

    def Cut(self, loc):
        """Ctrl+x剪切
        @loc 元素地址，格式：元组(By.ID,"地址")"""
        self.findElement(*loc).send_keys(Keys.CONTROL, 'x')

    def Copy(self, e):
        """Ctrl+c复制
        @loc 元素地址，格式：元组(By.ID,"地址")"""
        e.send_keys(Keys.CONTROL, 'c')

    def Paste(self, loc):
        """Ctrl+v粘贴
        @loc 元素地址，格式：元组(By.ID,"地址")"""
        self.findElement(*loc).send_keys(Keys.CONTROL, 'V')

    def pageDown(self, loc):
        """下一页pagedown
        @loc 元素地址，格式：元组(By.ID,"地址")"""
        self.findElement(*loc).send_keys(Keys.PAGE_DOWN)

    def pageUp(self, loc):
        """上一页pageUp
        @loc 元素地址，格式：元组(By.ID,"地址")"""
        self.findElement(*loc).send_keys(Keys.PAGE_UP)

    """=============================================="""
    """
        鼠标事件
    """

    def RightClick(self, loc):
        """鼠标右键
        @loc 元素地址，格式：元组(By.ID,"地址")"""
        ActionChains(self.driver).context_click(self.findElement(*loc)).perform()

    def DoubleClick(self, loc):
        """鼠标双击
        @loc 元素地址，格式：元组(By.ID,"地址")"""
        ActionChains(self.driver).double_click(self.driver.findElement(*loc)).perform()

    def DragAndDrop(self, loc1, loc2):
        """鼠标拖动
        @loc 元素地址，格式：元组(By.ID,"地址")"""
        ActionChains(self.driver).drag_and_drop(self.driver.findElement(*loc1),
                                                self.driver.findElement(*loc2)).perform()

    def mouse_hover(self, loc):
        """鼠标悬停事件
        @loc 元素地址，格式：元组(By.ID,"地址")"""
        ActionChains(self.driver).move_to_element(self.driver.findElement(*loc)).perform()

    """
    *********切换窗口************
    """

    def swithToWindow(self):
        """切换下一个窗口，只适用于两个窗口的情况"""
        # 获取当前窗口句柄
        nowhandle = self.driver.current_window_handle()
        # 获取所有窗口句柄
        allhandles = self.driver.window_handles()
        for handle in allhandles:
            if nowhandle != handle:
                self.driver.switch_to_window(handle)

    def swithTowindow(self, driver, windowtitle):
        """切换到指定窗口，适用于存在多个窗口的情况，传入要切换的窗口标题"""
        """获取所有窗口句柄"""
        allhandles = driver.window_handles()
        for handle in allhandles:
            driver.switch_to_window(handle)
            title = driver.title()
            if title == windowtitle:
                break

    def isElementExist(self, locator):
        """
                    判断元素是否存在
        """
        flag = False
        try:
            if locator == 'id':
                self.driver.findElement(*locator)
                flag = True
        except Exception, ex:
            print Exception, ":", ex
        return flag

    def wait(self, loc, time=10):
        """等待元素出现，默认10s
        @loc 元素地址，格式：元组(By.ID,"地址")"""
        WebDriverWait(self.driver, time).until(EC.visibility_of_element_located(loc))

    def toElement(self, loc):
        """适用于被挡住的元素，如滚动条底部元素定位
                            滑动到元素位置，使之可视，可点击
        @loc 元素地址，格式：元组(By.ID,"地址")s"""
        self.driver.execute_script("arguments[0].scrollIntoView();", self.driver.findElement(*loc))

    def toTop(self):
        js = "var q=document.documentElement.scrollTop=10000"
        self.driver.execute_script(js)

    def editvalue(self, loc, str1="display: block;"):
        element = self.findElement(*loc)
        print element
        self.driver.execute_script("arguments[0].style=arguments[1]", element, str1)
        print "修改了属性"
