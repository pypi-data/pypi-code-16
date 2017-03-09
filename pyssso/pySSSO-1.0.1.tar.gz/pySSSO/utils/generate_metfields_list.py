#!/usr/bin/env python

from template_to_name import *
from date_time_control import *
import datetime


def produce_metfields_list(out_file, file_template, bdate, edate, do_MEGAN=0):
    """
      Produces the list of metFields files for the provided date range.

      Required Inputs:
        - output_file: output file where the list will written into
        - file_template: file template to be used to derive each file 
                         on the list
        - bdate:         beginning date
        - edate:         ending date

      Optional input:
        - do_MEGAN: do MEGAN emission? 
                    0 is the default value otherwsie set it to 1.
    """
    
    if (do_MEGAN == 1):
        curdate = date_increment(bdate, -15)
    else:
        curdate = bdate

    num_days = days_between_dates(curdate, edate)

    f = open(out_file, 'w+')

    for i in range(num_days):
        curdate = date_increment(curdate, 1)
        fname = tmpl_2_name(file_template, 
                            YYYY = curdate.year, 
                            MM   = curdate.month, 
                            DD   = curdate.day)
        f.write("'"+ fname + "'" + "\n")

    f.close()
