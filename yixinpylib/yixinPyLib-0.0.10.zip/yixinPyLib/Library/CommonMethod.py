# _*_ coding:utf-8 _*_
'''
Created on 2016年10月21日

@author: wuyunpeng
'''
'''
    获取当前系统时间：格式2016-10-20 08_03_04
'''
from random import Random
import ConfigParser
import inspect
import os
import time

import xlrd


def getNowTime():
    '''获取当前系统时间'''
    return time.strftime("%Y-%m-%d %H_%M_%S", time.localtime(time.time()))
def getNowTime2():
    '''获取当前系统时间'''
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
def getnow():
    return time.strftime("%y%m%d%H%M%S", time.localtime(time.time()))
def get_current_function_name():
    '''获取当前运行的方法名称'''
    return inspect.stack()[1][3]

def getProPath():
    '''获取项目路径'''
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
def getDir(path):
    '''获取某目录下的用例文件名@param path 文件所在路径'''
    fileslist = []
    files = os.listdir(path)
    print files
    for fl in files:
        fm = fl.split('.')
        if fm[1]=='py'and (fm[0]!='__init__' and fm[0]!='test' and fm[0] !='Basecase') :
            fileslist.append(fm[0])
    return fileslist

def getConf(var):
    #读取配置文件
    cf = ConfigParser.ConfigParser()
    cf.read(getProPath()+r"\\config\\config.ini")
    return cf.get("config", var)
def getdbconf(var):
    #读取配置文件
    cf = ConfigParser.ConfigParser()
    cf.read(getProPath()+r"\\config\\config.ini")
    return cf.get("mysqldb", var)
def getfiles(path):
    '''传入cases下的包名
                获取程序下某目录下的除__init__外的其他py文件名称'''
    fileslist = []
    files = os.listdir(getProPath()+"\\cases\\"+path)
    print files
    for fi in files:
        fm = fi.split('.')
        if fm[1]=='py'and fm[0]!='__init__' :
            fileslist.append(fm[0])
    return  fileslist
def randomfunc(lenth):
    '''返回固定长度的字符串'''
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(lenth):
        str+=chars[random.randint(0, length)]
    return str
def randomfunc2(lenth):
    '''返回固定长度的数字'''
    str = ''
    chars = '0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(lenth):
        str+=chars[random.randint(0, length)]
    return str
if __name__ =="__main__":
#     a = readsheets(r"E:\Workspace\AutoTestForCC\data\1.xlsx")
#     print a
#     for i in range(len(a)):
#         print a[i]
    print getProPath()
    
