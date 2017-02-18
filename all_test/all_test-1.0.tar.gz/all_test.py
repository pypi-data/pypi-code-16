#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@contact:    mijiawei@baixing.com
@desc:       执行test_case目录下的测试用例
"""
import unittest
import os
import time
import sys
from public import HTMLTestRunner


def gen_test_suite():
    testunit = unittest.TestSuite()
    # 测试文件查找的目录
    test_dir = os.path.abspath(os.path.dirname(__file__)) + os.sep + 'test_case'
    # pattern用来匹配/test_case目录下哪些用例加入本次运行
    discover = unittest.defaultTestLoader.discover(test_dir, pattern='test_*.py',
                                                   top_level_dir=None)
    # discover 方法筛选出来的用例，循环添加到测试套件中
    for test_suite in discover:
        for test_case in test_suite:
            testunit.addTests(test_case)
            print testunit
    return testunit


def main():
    # 将项目的目录加载到系统变量中
    cur_dir = os.getcwd()
    sys.path.append(cur_dir)
    now = time.strftime("%Y-%m-%d %H_%M_%S")

    os.environ['WEBSERVICE_ITERATION_RUN_TIME'] = now

    report_folder = cur_dir + os.sep + 'report' + os.sep
    filename = report_folder + now + '_result.html'  # 测试报告的路径名
    fp = file(filename, 'wb+')
    runner = HTMLTestRunner.HTMLTestRunner(
        stream=fp,
        title=u'SmokeTest自动化测试报告',
        description=u'用例执行情况：',
        )
    all_test_units = gen_test_suite()
    # 获得报错数
    err_num = runner.run(all_test_units).__repr__()
    fp.close()  # 关闭生成的报告

    if err_num == 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
