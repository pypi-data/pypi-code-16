# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#
import argparse
import collections
import datetime
from fdscli.model.fds_error import FdsError
from fdscli.plugins.abstract_plugin import AbstractPlugin

class DatetimeFunctions(AbstractPlugin):
    '''Functions for sub-commands that supply datetime options.

    This class represents a unit of reuse that could be leveraged by any sub-command
    that lists entries by date.
    '''

    begin_date_key = "begin_date"
    begin_time_key = "begin_time"
    end_date_key = "end_date"
    end_time_key = "end_time"

    def __init__(self):
        AbstractPlugin.__init__(self)

    def add_datetime_range_options(self, parser):
        '''Adds command line options to enable user to specify a datetime range.

        For example, the ``exports list`` sub-command allows filtering of results
        by datetime range.

        Parameters
        ----------
        :type parser: ``argparse.ArgumentParser``
        '''
        if parser is None:
            return
        if not isinstance(parser, argparse.ArgumentParser):
            return

        help_begin_date = ("A date in YYYY-MM-DD format. Specifies the beginning of a date "
            "range for filtering the result.")
        parser.add_argument("-bd", "--begin-date", help=help_begin_date)

        help_begin_time = ("A time in HH:MM format. When combined with begin-date, specifies "
            "the beginning of a range for filtering the result.")
        parser.add_argument("-bt", "--begin-time", help=help_begin_time)

        help_end_date = ("A date in YYYY-MM-DD format. Specifies the end of a date range "
            "for filtering the result.")
        parser.add_argument("-ed", "--end-date", help=help_end_date)

        help_end_time = ("A time in HH:MM format. When combined with end-date, specifies "
            "the end of a range for filtering the result.")
        parser.add_argument("-et", "--end-time", help=help_end_time)

    def validate_timestamp_filter(self, args):
        '''Builds and validates a datetime range given command arguments.

        Parameters
        ----------
        :type args: dict

        Returns
        -------
        :type list(long) or FdsError. A list with a begin timestamp and end timestamp, or empty list.
        '''
        timestamp_range = []

        begin_timestamp = None
        end_timestamp = None

        if DatetimeFunctions.begin_date_key in args and args[DatetimeFunctions.begin_date_key] is not None:
            try:
                year, month, day = map(int, args[DatetimeFunctions.begin_date_key].split('-'))
                date1 = datetime.datetime(year, month, day, 0, 0)

                begin_timestamp = (date1 - datetime.datetime(1970,1,1)).total_seconds()

            except ValueError as ve:
                print "Begin date {} not in YYYY-MM-DD format.".format(args[DatetimeFunctions.begin_date_key])
                return FdsError("Invalid date entry")

            except Exception as ex:
                print( "\nException reported: \n{}".format( ex ) )
                return FdsError("Exception for begin date processing.")

        if DatetimeFunctions.begin_time_key in args and args[DatetimeFunctions.begin_time_key] is not None:
            if begin_timestamp is None:
                print "Begin time supplied, begin date is also required."
                return FdsError("Date range error.")

            try:
                hour, minute = map(int, args[DatetimeFunctions.begin_time_key].split(':'))
                time1 = datetime.time(hour, minute)

                begin_timestamp = (begin_timestamp + datetime.timedelta(hours=time1.hour, minutes=time1.minute, seconds=0).total_seconds())

            except ValueError as ve:
                print "Begin time {} not in HH:MM format.".format(args[DatetimeFunctions.begin_time_key])
                return FdsError("Invalid time entry")

            except Exception as ex:
                print( "\nException reported: \n{}".format( ex ) )
                return FdsError("Exception for begin time processing.")

        if DatetimeFunctions.end_date_key in args and args[DatetimeFunctions.end_date_key] is not None:
            try:
                year, month, day = map(int, args[DatetimeFunctions.end_date_key].split('-'))
                date2 = datetime.datetime(year, month, day, 0, 0)

                end_timestamp = (date2 - datetime.datetime(1970,1,1)).total_seconds()

            except ValueError as ve:
                print "End date {} not in YYYY-MM-DD format.".format(args[DatetimeFunctions.end_date_key])
                return FdsError("Improper date-time entry")
            except Exception as ex:
                print( "\nException reported: \n{}".format( ex ) )
                return FdsError("Exception for end date processing.")

        if DatetimeFunctions.end_time_key in args and args[DatetimeFunctions.end_time_key] is not None:
            if end_timestamp is None:
                print "End time supplied, end date is also required."
                return FdsError("Date range error.")

            try:
                hour, minute = map(int, args[DatetimeFunctions.end_time_key].split(':'))
                time2 = datetime.time(hour, minute)

                end_timestamp = (end_timestamp + datetime.timedelta(hours=time2.hour, minutes=time2.minute, seconds=0).total_seconds())

            except ValueError as ve:
                print "End time {} not in HH:MM format.".format(args[DatetimeFunctions.end_time_key])
                return FdsError("Invalid time entry")

            except Exception as ex:
                print( "\nException reported: \n{}".format( ex ) )
                return FdsError("Exception for end time processing.")

        if begin_timestamp is None:
            if end_timestamp is not None:
                print "End date supplied with no begin date."
                return FdsError("End date supplied with no begin date.")
        else:
            if end_timestamp is None:
                # Supply an end date automatically
                date2 = datetime.datetime.now()
                end_timestamp = (date2 - datetime.datetime(1970,1,1)).total_seconds()

        if (begin_timestamp > end_timestamp):
            print "Invalid date range. Begin time is later than end time."
            return FdsError("Invalid date range.")

        if begin_timestamp is not None:
            timestamp_range.append(begin_timestamp)
        if end_timestamp is not None:
            timestamp_range.append(end_timestamp)

        return timestamp_range

    @staticmethod
    def in_range(timestamp, datetime_range):
        '''Returns True if the given timestamp satisfies the datetime range, False otherwise.

        Parameters
        ----------
        :type timestamp: long
        :type datetime_range: list(long)
        :param datetime_range: A list where the first element is begin datetime, the optional
            second element is end datetime.

        Returns
        -------
        :type bool
        '''
        if not isinstance(datetime_range, collections.Iterable):
            return False
        if len(datetime_range) == 0:
            return True
        result = True
        if long(timestamp) < datetime_range[0]:
            result = False
        else:
            if len(datetime_range) > 1:
                if long(timestamp) > datetime_range[1]:
                    result = False
        return result

