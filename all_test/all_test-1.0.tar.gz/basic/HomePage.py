#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@contact:    mijiawei@baixing.com
"""
from selenium.webdriver.common.by import By


class HomePage(object):
    """
        首页
    """
    homepage = 'http://www.shanghai.baixing.com'
    # 定位器
    ERSHOUCHE_TAB_LOC = (By.XPATH, "//h3/a[text()='二手车']")
    FUWU_TAB_LOC = (By.XPATH, "//h3/a[text()='本地生活服务']")
    FANGWU_TAB_LOC = (By.XPATH, "//h3/a[text()='房产']")
    ZHAOPIN_TAB_LOC = (By.XPATH, "//h3/a[text()='招聘']")

    ERSHOUCHE_POST_BTN = (By.XPATH, "html/body/header/div[2]/div/a")
    ZHAOPIN_POST_BTN = (By.XPATH, "html/body/header/div[2]/div/div[3]/a[2]")
    FANGWU_POST_BTN = (By.XPATH, "html/body/header/div[2]/div/a")
    FUWU_POST_BTN = (By.XPATH, "html/body/header/div[2]/div/div[3]/a")

def switch_browse(browser):
    # browser = self.driver
    # print browser.current_window_handle # 输出当前窗口句柄
    handles = browser.window_handles # 获取当前窗口句柄集合

    for handle in handles:# 切换窗口
        if handle!=browser.current_window_handle:
            browser.switch_to.window(handle)
            # print browser.current_window_handle
            break