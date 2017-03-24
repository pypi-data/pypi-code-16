#!/usr/bin/python
# coding:utf8

"""
异常类定义
created by : xiaochun
date : 2015-05-20
"""

class HzfException(Exception):
    """
    hzf异常基类
    """

    def __init__(self, err_code, err_msg):
        '''
        err = (error_code, error_msg)
        '''
        super(HzfException, self).__init__(err_code, err_msg)
        self.__err = (err_code, err_msg)
    
    def msg(self):
        return self.__err[1]
    
    def code(self):
        return self.__err[0]
    
    def __str__(self):
        return '(%s %s)' %(self.__err[0], self.__err[1])
    
    def __tuple__(self):
        return self.__err

    

