# -*- coding: UTF-8 -*-
__author__ = "chenshancang@163.com"
__version__ = '0.1.0'

import datetime


class GotoDate(object):
	def __init__(self,date):
		self.date = date

	def is_valid_date(self):
		#判断日期有效性
		if isinstance(self.date,basestring):
			try:
				datetime.datetime.strptime(self.date,'%Y-%m-%d')
			except Exception:
				return False
			return True
		return True

	def _clean_date(self):
		#字符串转行成日期类型
		if self.is_valid_date():
			if isinstance(self.date,basestring):
				return datetime.datetime.strptime(self.date,'%Y-%m-%d').date()
			return self.date

	def before(self,num):
		#输出几天前
		days = datetime.timedelta(days=num)
		return self._clean_date() - days


	def after(self,num):
		#输出几天后
		days = datetime.timedelta(days=num)
		return self._clean_date() + days

	def week(self):
		#返回周几
		return self._clean_date().weekday()

	def week_range(self,china=False):
		#返回本周的所有日期
		if china == True:
			index = 2
			#输出中文
		else:
			#输出英文
			index =0
		week = (	('Monday',		0	,u'周一'),
					('Tuesday',		1	,u'周二'),
					('Wednesday',	2	,u'周三'),
					('Thursday',	3	,u'周四'),
					('Friday',		4	,u'周五'),
					('Saturday',	5	,u'周六'),
					('Sunday',		6	,u'周日')
				)
		weekday_range={}
		for weekday in week:
			weekday_range[weekday[index]] = self.before(self.week() - weekday[1])
			if weekday[1] == self.week():
				weekday_range[weekday[index]] = self.after(weekday[1] - self.week())

		return weekday_range