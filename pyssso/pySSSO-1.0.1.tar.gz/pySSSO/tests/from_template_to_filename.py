#!/usr/bin/env python

from template_to_name import *
from date_time_control import *
import sys



template = '/discover/nobackup/jkouatch/%y4/MERRA.%y4%m2%d2_0000z.nc4'

yyyy, mm, dd = split_data_time(20040221)
fname = tmpl_2_name(template, YYYY=yyyy, MM=mm, DD=dd)

print template
print fname

