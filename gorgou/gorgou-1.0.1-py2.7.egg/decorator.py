#!/usr/bin/env python
# -*- coding: utf8 -*-

'''
@timeout(5) #限定下面的slowfunc函数如果在5s内不返回就强制抛TimeoutError Exception结束
def slowfunc(sleep_time):
  import time
  time.sleep(sleep_time) #这个函数就是休眠sleep_time秒
slowfunc(3) #sleep 3秒，正常返回 没有异常
slowfunc(10) #被终止
## 输出
---------------------------------------------------------------------------
TimeoutError                              Traceback (most recent call last)
'''

import signal
import functools  # 下面会用到的两个库


class TimeoutError(Exception):
    pass  # 定义一个Exception，后面超时抛出


def timeout(seconds, error_message='Function call timed out'):
    def decorated(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
        return functools.wraps(func)(wrapper)
    return decorated

'''
@trace
def xxx():
  print 1
  print 22
  print 333
xxx() #调用
## 输出
<ipython-input-4-da50741ac84e>(3):     print 1 # @trace 的输出
<ipython-input-4-da50741ac84e>(4):     print 22 # @trace 的输出
<ipython-input-4-da50741ac84e>(5):     print 333 # @trace 的输出
'''

import sys
import os
import linecache


def trace(f):
    def globaltrace(frame, why, arg):
        if why == "call":
            return localtrace
        return None

    def localtrace(frame, why, arg):
        if why == "line":
            # record the file name and line number of every trace
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            bname = os.path.basename(filename)
            print "{}({}): {}".format(bname,
                                      lineno,
                                      linecache.getline(filename, lineno)),
        return localtrace

    def _f(*args, **kwds):
        sys.settrace(globaltrace)
        result = f(*args, **kwds)
        sys.settrace(None)
        return result
    return _f
