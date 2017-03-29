from unittest import TestCase
from nose.tools import qe_
from ...holidays import *

class TestHolidays(TestCase):
    '''
    placeholder
    '''
    begin_year = pd.to_datetime('2017-12-01')
    end_year = pd.to_datetime('2017-12-27')
    holiday_cal = USHolidayCalendar()


    def test_if_none(self):

        holidays = self.get_us_holidays(begin_year, end_year)

        self.assertIsNotNone(holidays)



