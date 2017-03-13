# -*- coding: utf-8 -*-
from datetime import timedelta
from django.utils import timezone
from random import randrange
import datetime
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware

def years_ago(years, from_date = None):
    if from_date is None:
        from_date = timezone.now()
    try:
        return from_date.replace(year = from_date.year - years)
    except:
        return from_date.replace(month = 2, day = 28, year = from_date.year - years)

# @og slabe rozwiazanie - do przebudowy
def get_default_start_date():
    return timezone.now().date

# @og nie mozna podawac arg, do przebudowy!
def get_default_end_date(days_active):
    return (timezone.now() + datetime.timedelta(days = days_active)).date

def str_to_hour(hour_str):
    return datetime.datetime.strptime(hour_str, '%H:%M').time()

def hour_to_str(hour):
    return datetime.time.strftime(hour, '%H:%M')

def date_to_str(date):
    return datetime.datetime.strftime(date, '%Y-%m-%d')

def datetime_to_str(date):
    return datetime.datetime.strftime(date, '%Y-%m-%d %H:%M')

def str_to_aware_datetime(date_str):
    result = parse_datetime(date_str)
    if not is_aware(result):
        result = make_aware(result)
    return result

def get_random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds = random_second)
