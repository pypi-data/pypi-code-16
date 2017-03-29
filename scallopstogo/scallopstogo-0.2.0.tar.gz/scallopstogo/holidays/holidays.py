import pandas as pd
from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday, nearest_workday, \
    USMartinLutherKingJr, USMemorialDay, USLaborDay, USThanksgivingDay, FR

class USHolidayCalendar(AbstractHolidayCalendar):
    '''
    doc later
    '''

    rules = [
        Holiday('NewYearsDay', month=1, day=1, observance=nearest_workday),
        USMartinLutherKingJr,
        USMemorialDay,
        Holiday('USIndependenceDay', month=7, day=4, observance=nearest_workday),
        USLaborDay,
        USThanksgivingDay,
        Holiday("Black Friday", month=11, day=1, offset=pd.DateOffset(weekday=FR(4))),
        Holiday('Christmas', month=12, day=25, observance=nearest_workday)
        ]

    def __init__(self, **kwargs):
        '''
        placeholder
        '''

        for key, value in kwargs.iteritems():
            if key == 'add_holidays':
                if isinstance(value, list):
                    for holiday in value:
                        self.rules += [holiday]
                else:
                    self.rules += [value]

    def get_us_holidays(self, start_time, end_time):
        '''
        placeholder
        '''

        inst = USHolidayCalendar()

        return inst.holidays(start_time, end_time)
