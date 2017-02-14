#!/usr/bin/env python
#-*- coding: utf-8 -*-
# Author: Colin
# Date: 2017-02-10
# Desc: Python 监控系统基本性能，包括内存，磁盘，CPU等等
#

from __future__ import division
import commands
from ..opslogs import errorLog
from ..opscommon import get_ip_address


def getMem(host=None):
	"""
	内存按kb显示
	"""
	result = {}
	memfile = '/proc/meminfo'
	if host is None:
		host = get_ip_address('eth0')
		cmd = 'cat %s > /tmp/ops_meminfo.txt' % memfile
	else:
		#cmd = '''ssh % 'cat %s' > /tmp/ops_meminfo.txt''' % (host, memfile)
		cmd = 'ssh ' +  host +  ' "cat ' + memfile +  '" > /tmp/ops_meminfo.txt'

	status = commands.getstatusoutput(cmd)[0]
	if status == 0:
		with open('/tmp/ops_meminfo.txt') as f:
			memtotal = int(f.readline().split()[1])
			memfree = int(f.readline().split()[1])
			memavail = int(f.readline().split()[1])
			membuffer = int(f.readline().split()[1])
			memcache = int(f.readline().split()[1])
			memused = int(memtotal - memfree - membuffer - memcache)
			rate = round((memused / memtotal) * 100 + 0.00,2)
			#rate = ((memused / memtotal) * 100 + 0.00)
			#rate = int('%.2f' % )
		
		result = {"host": host, "total": memtotal, "free": memfree, "available": memavail, "used": memused, "rate(%)": rate}
		#result = """{"host": %s, "total": %d, "free": %d, "available": %d, "used": %d, "rate": %.2f}""" % (host, memtotal, memfree, memavail, memused, rate)
	else:
		errorLog("Get meminfo file content failed!")
	return result

def getDisk(host=None):
	"""
	磁盘大小按KB显示
	"""
	re = []
	if host is None:
		host = get_ip_address('eth0')
		cmd = 'df -l |egrep -E "/dev/s[a-z][a-z][1-9]{1}"'
	else:
		cmd = "ssh " + host + """ 'df -l |egrep -E "/dev/s[a-z][a-z][1-9]{1}"' """

	result = commands.getstatusoutput(cmd)
	if result[0] == 0:
		res = result[1].split('\n')
		#for i in len(res):
		for i in range(len(res)):
			record = res[i].split()
			dname = record[5]
			dtotal = int(record[1])
			dused = int(record[2])
			dfree = int(record[3])
			drate= int(record[4].split('%')[0])
			tmp = {"host": host, "devicename": dname, "total": dtotal, "used": dused, "free": dfree, "percent(%)": drate}	
			re.append(tmp)
	return re
