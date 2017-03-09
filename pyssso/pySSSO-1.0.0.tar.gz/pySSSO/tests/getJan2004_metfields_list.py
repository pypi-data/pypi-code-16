#!/usr/bin/env python

from date_time_control import *
import datetime
import sys
from generate_metfields_list import *



template = '/discover/nobackup/jkouatch/%y4/MERRA.%y4%m2%d2_0000z.nc4'


byear  = 2004
bmonth = 1
bday   = 1

eyear  = 2004
emonth = 2
eday   = 1

bdate = datetime.date(byear, bmonth, bday)
edate   = datetime.date(eyear, emonth, eday)

produce_metfields_list('Jan2004.list', template, bdate, edate, 1)
