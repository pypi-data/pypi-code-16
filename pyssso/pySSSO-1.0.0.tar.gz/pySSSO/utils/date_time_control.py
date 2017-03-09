#!/usr/bin/env python

import sys
import datetime
from dateutil.relativedelta import relativedelta

def split_data_time(nlmr):
    """
      Extracts the three fields from either nymd (year, month, day) or 
      nhms (hours, minutes, seconds).
      
      Required input:
        nlmr: YYYYMMDD or HHMMSS ("lmr" = "left" "middle" "right") 

      Returned values:
        left (year  or hours), middle (month or minutes), right (day or seconds)
    """
    left   = nlmr / 10000
    middle = (nlmr % 10000) / 100
    right  = (nlmr % 100)

    return left, middle, right

def date_increment(curdate, num_days):
    """
      Increments the date by a given number of days.

      Required input:
        curdate:  current date
        num_days: number of days to increment (might be negative)

      Returned value:
        curdate incremented by num_days
    """
    return curdate + relativedelta(days=num_days)
    #return curdate + datetime.timedelta(days=num_days)

def month_increment(curdate, num_months):
    """
      Increments the date by a given number of months.

      Required input:
        curdate:  current date
        num_months: number of months to increment (might be negative)

      Returned value:
        curdate incremented by num_months
    """
    return curdate + relativedelta(months=num_months)

def year_increment(curdate, num_years):
    """
      Increments the date by a given number of years.

      Required inputs:
        curdate:  current date
        num_years: number of years to increment (might be negative)

      Returned value:
        curdate incremented by num_years
    """
    return curdate + relativedelta(years=num_years)

def days_between_dates(date1, date2):
    """
      Determines the number of days between two dates.

      Required inputs:
         date1: first date
         date2: second date
         It is assumed that date2 is ahead of date1.

      Returned value:
         number of days
    """
    return (date2-date1).days

