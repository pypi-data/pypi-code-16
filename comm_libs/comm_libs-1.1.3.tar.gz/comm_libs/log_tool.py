#!/usr/bin/python
# coding:utf8

"""
日志工具类函数

create by: xiaochun
date : 2015-05-20
"""

import logging
import logging.config 

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

logging.config.fileConfig(BASE_DIR+"/confs/logging.conf")

applog = logging.getLogger('applog')
accesslog = logging.getLogger('accesslog')


def write_debug_log(content):
    """
    """
    applog.debug(content)


def write_info_log(content):
    """
    """
    applog.info(content)
    
    
def write_warn_log(content):
    """
    """
    applog.warn(content)

def write_error_log(content):
    """
    """
    applog.error(content)

def write_access_log(content):
    """
    """
    accesslog.info(content)
 


if __name__ == "__main__":

    write_debug_log("debug_test")

    write_info_log("info_test")

    write_warn_log("warn_test")

    write_error_log("error_test")

    write_access_log("accesslog_test")

    
