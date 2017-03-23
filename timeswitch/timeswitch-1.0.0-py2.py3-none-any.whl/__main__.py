"""
Work with Timeswitch expressions on the command-line.
"""

import argparse
import calendar
import sys
import time
from datetime import datetime, time as datetime_time, timedelta
from timeswitch import timeswitch, InvalidExpression


class bcolors:
    """
    Terminal colour codes.
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class timer(object):
    """
    Context manager to time the duration of operation(s).
    """
    def __init__(self):
        self._start = None
        self._end = None

    def __enter__(self):
        self._start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end = time.time()

    def duration(self):
        return None if self._end is None else self._end - self._start


class TimeswitchTextCalendar(object):
    """
    This class can be used to generate plain text calendars, showing dates/times where the provided
    timeswitch function is matched.
    """

    def __init__(
            self, timeswitch_function, firstweekday=0,
            color_on=bcolors.FAIL, color_off=bcolors.ENDC):
        self._switch = timeswitch_function
        self._firstweekday = firstweekday
        self._color_on = color_on
        self._color_off = color_off

    def print_year(
            self, year,
            date_column_width=None, lines_per_week=None, month_column_spaces=6, columns=3,
            out=sys.stdout, time_of_day=datetime.min.time()):

        cal = calendar.Calendar(self._firstweekday).yeardatescalendar(year, columns)
        month_gap = " " * month_column_spaces

        # Year header
        width = (20*len(cal[0]) + len(month_gap)*(len(cal[0])-1))
        out.write(("{:^" + str(width) + "}\n\n").format(year))
        for month_row in cal:
            # Month headers
            out.write(
                month_gap.join([
                                   ("{:^20}").format(month_weeks[1][0].strftime("%B"))
                                   for month_weeks in month_row]) + "\n")
            # Week day headers (use first week of each month only)
            out.write(
                month_gap.join([
                                   " ".join(day.strftime("%a")[:2] for day in month_weeks[0])
                                   for month_weeks in month_row
                                   ]) + "\n"
            )
            # Iterate through the month row by week (using month with maximum number of weeks)
            for week in range(max(len(month_weeks) for month_weeks in month_row)):
                for month_column, month_weeks in enumerate(month_row):
                    month = month_weeks[1][0]
                    week_days = month_weeks[week] if week < len(month_weeks) else [None] * 7

                    # space from previous column
                    month_column and out.write(month_gap)
                    # body
                    for day_of_week, day in enumerate(week_days):
                        out.write("{color}{day:2}{reset}{space}".format(
                            color=self._color_on
                            if day and self._switch(datetime.combine(day, time_of_day))
                            else self._color_off,
                            day=day.day if day and day.month == month.month else '',
                            reset=bcolors.ENDC,
                            space='' if day_of_week == 6 else ' '))
                out.write("\n")
            out.write("\n")

    def print_day(self, date, out=sys.stdout):
        out.write(
            "{:^66}\n      {}  |\n".format(
                date.strftime("%a %d %b %Y"),
                "  ".join(":{:02}".format(m) for m in range(0, 60, 5))))
        for hour in range(24):
            out.write("{:02}:00 ".format(hour))
            for minute in range(60):
                out.write(
                    '-' if self._switch(datetime.combine(date, datetime_time(hour, minute)))
                    else ' ')
            out.write("|\n")

    def print_week(self, date, hour_width=4, out=sys.stdout):
        # adjust to start of week
        date_start = date - timedelta(days=date.weekday() - self._firstweekday)
        # Main week header
        out.write(("{:^" + str(11+hour_width*24) + "}\n").format("{} ({} - {})".format(
            date_start.strftime("Week %W of %Y"),
            date_start.strftime("%a %d %b"),
            (date_start + timedelta(days=6)).strftime("%a %d %b"))))
        # Time header
        time_headers = hour_width*24/6
        out.write("           {}\n".format(
            " ".join(
                (datetime.utcfromtimestamp(60*60*24/time_headers*i)).strftime("%H:%M")
                for i in range(time_headers))))
        for day in range(7):
            day_date = date_start + timedelta(days=day)
            out.write("{:>10} ".format(day_date.strftime("%A")))
            for hour in range(24):
                for hour_inc in range(hour_width):
                    minute = 60.0 / hour_width * hour_inc
                    dt = datetime.combine(
                        day_date,
                        datetime_time(hour, int(minute), int((minute-int(minute))*60)))
                    out.write(
                        '-' if self._switch(dt)
                        else ' ')
            out.write("|\n")


def iso_datetime(date_string):
    return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")


def main(arg_list=None):
    arg_parser = argparse.ArgumentParser(
        description=
        "Parse, check and visualise timeswitch expressions.")

    arg_parser.add_argument(
        "expression", help=
        "Timeswitch expression to parse and check dates against.")

    arg_parser.add_argument(
        "date", nargs="?", type=iso_datetime,
        default=datetime.now(), help=
        "Date and time to check against the timeswitch expression. "
        "Format as ISO timestamp, i.e. 'YYYY-mm-ddTHH:MM:SS'. "
        "If omitted, the current date/time is used.")

    arg_parser.add_argument(
        "-d", "--day", action="store_true", help=
        "Produce a day view for the date provided (matches expression against minutes and hours).")

    arg_parser.add_argument(
        "-w", "--week", action="store_true", help=
        "Produce a week view for the date provided (matches expression against hours and week "
        "days).")

    arg_parser.add_argument(
        "-y", "--year", action="store_true", help=
        "Produce a year calendar for the date provided (matches expression against days of the "
        "year, using the provided dates time component).")

    arg_parser.add_argument(
        "-a", "--all", action="store_true", help=
        "Produce all views for the date provided - day, week and year.")

    arg_parser.add_argument(
        "-p", "--parsetime", action="store_true", help=
        "Report parsing time in seconds.")

    args = arg_parser.parse_args(arg_list)

    with timer() as parse_time:
        try:
            switch = timeswitch(args.expression)
        except InvalidExpression as e:
            return "{}".format(e)

    if args.parsetime:
        print("{}".format(parse_time.duration()))

    date = args.date
    result = switch(date)

    print("{}".format("on" if result else "off"))

    if len({'day', 'week', 'year', 'all'} & set(vars(args).keys())) > 0:
        text_cal = TimeswitchTextCalendar(switch)

        if args.day or args.all:
            print("")
            text_cal.print_day(date.date())

        if args.week or args.all:
            print("")
            text_cal.print_week(date.date())

        if args.year or args.all:
            print("")
            text_cal.print_year(date.year, time_of_day=date.time())

    return 0 if result else 1

if __name__ == '__main__':
    sys.exit(main())
