#!/usr/bin/env python

from template_to_name import *
from date_time_control import *
import datetime
import sys

yyyy, mm, dd = split_data_time(20040221)

hh = 0
nn = 0
ss = 0

curdate = datetime.datetime(yyyy, mm, dd, hh, nn, ss)
print curdate

num_days = -12
newdate = date_increment(curdate, num_days)

print newdate.year, newdate.month, newdate.day

num_months = 25
newdate = month_increment(curdate, num_months)
print newdate.year, newdate.month, newdate.day

num_years = 1
newdate = year_increment(curdate, num_years)
print newdate.year, newdate.month, newdate.day

print days_between_dates(curdate, newdate)

