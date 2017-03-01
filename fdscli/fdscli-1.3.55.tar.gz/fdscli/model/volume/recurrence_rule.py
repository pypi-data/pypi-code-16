# Copyright (c) 2015, Formation Data Systems, Inc. All Rights Reserved.
#
from enum import Enum, unique

@unique
class Frequency(Enum):
    SECONDLY = 0
    MINUTELY = 1
    HOURLY   = 2
    DAILY    = 3
    WEEKLY   = 4
    MONTHLY  = 5
    YEARLY   = 6

    def __str__(self):
        return self.name

class RecurrenceRule(object):
    '''A rule or repeating pattern for recurring events.

    An empty recurrence rule is allowed.
    The meaning of an empty recurrence rule depends on the client semantics.

    Attributes
    ----------
    :type __frequency: ``model.volume.Frequency``
    '''
    def __init__(self, frequency=None, byday=None, bymonthday=None, bymonth=None, byyearday=None, byhour=None, byminute=None):
        self.__frequency = None
        if frequency is not None:
            self.frequency = frequency
        self.byday = byday
        self.byhour = byhour
        self.bymonthday = bymonthday
        self.byyearday = byyearday
        self.bymonth = bymonth
        self.byminute = byminute

    def is_empty(self):
        '''Returns true if empty recurrence rule, false otherwise.

        Returns
        -------
        :type bool
        '''
        if self.frequency is None:
            return True
        return False
        
    @property
    def frequency(self):
        return self.__frequency
    
    @frequency.setter
    def frequency(self, frequency):
        '''
        Parameters
        ----------
        :type frequency: ``model.volume.Frequency``, str, or None
        :param frequency: A value of None means that the recurrence rule is empty
        '''
        if frequency is None:
            raise TypeError()

        if isinstance(frequency, (str, unicode)):
            for s in Frequency:
                if s.name == str(frequency.upper()):
                    frequency = s
                    break;

        if not isinstance(frequency, Frequency):
            raise TypeError()

        self.__frequency = frequency

    @property
    def byday(self):
        return self.__byday
    
    @byday.setter
    def byday(self, days):
        self.__byday = days
        
    @property
    def byhour(self):
        return self.__byhour
    
    @byhour.setter
    def byhour(self, hours):
        self.__byhour = hours
        
    @property
    def bymonthday(self):
        return self.__bymonthday
    
    @bymonthday.setter
    def bymonthday(self, monthdays):
        self.__bymonthday = monthdays
        
    @property
    def byyearday(self):
        return self.__byyearday
    
    @byyearday.setter
    def byyearday(self, yeardays):
        self.__byyearday = yeardays
        
    @property
    def bymonth(self):
        return self.__bymonth
    
    @bymonth.setter
    def bymonth(self, months):
        self.__bymonth = months
        
    @property
    def byminute(self):
        return self.__byminute
    
    @byminute.setter
    def byminute(self, byminutes):
        self.__byminute = byminutes
