'''
Created on 2012-6-29

@author: lihao
'''
import os
import sys
lib_path = os.path.abspath(os.path.join('taobao'))
# make import top api possible
sys.path.append(lib_path)

from top.api.base import sign


class appinfo(object):
    def __init__(self,appkey,secret):
        self.appkey = appkey
        self.secret = secret

def getDefaultAppInfo():
    pass


def setDefaultAppInfo(appkey,secret):
    default = appinfo(appkey,secret)
    global getDefaultAppInfo
    getDefaultAppInfo = lambda: default







