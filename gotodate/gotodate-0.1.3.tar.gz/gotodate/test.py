# -*- coding: UTF-8 -*-
__author__ = "chenshancang@163.com"

from gotodate import GotoDate
a = '2016-10-11'
d = GotoDate(date=a)
print d.get_date()
print d.before(1)
print d.after(2)
print d.to_format('%Y/%m/%d')
print d.week_range()

d = GotoDate()
print d.get_date()
print d.before(1)
print d.after(2)
print d.to_format('%Y年%m月%d日')
print d.week_range()


a = '2017年03月24日'
d = GotoDate(date=a,format='%Y年%m月%d日')
print d.get_date()
print d.before(1)
print d.after(2)
print d.to_format('%Y-%m-%d')
print d.week_range()




