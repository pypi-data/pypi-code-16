#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = 'Colin'


def printLog(string):
	"""
	func: greenPrint
	return: log with green color for info log
	"""
	print("\033[32m " + string + "\033[0m")

def warnLog(string):
	"""
	func: warnLog
	return: log with yellow color for warning message show
	"""
	print("\033[33m " + string + "\033[0m")

def errorLog(string):
	"""
	func: warnLog
	return: log with yellow color for error message show
	"""
	print("\033[31m " + string + "\033[0m")


