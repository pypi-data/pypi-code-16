#! python3
# encoding: utf-8

# Copyright Tim Littlefair 2016
# This work is licensed under the MIT License.
# https://opensource.org/licenses/MIT


"""
This module implements an object which can be fed a sequence
of point-in-time version control commit events and can use
this to infer an estimate of overall time spent on the code
based on assumptions about how frequently the author's pattern
of work.
"""

import collections
import datetime

_HOURS_PER_DAY = 24.0
_SECONDS_PER_HOUR = 3600.0
_SUPPORTED_ROUND_TO = (1.0, 0.5, 0.25, 0.1)

Assumptions = collections.namedtuple('Assumptions', 'before between after')
DEFAULT_ASSUMPTIONS = Assumptions(0.75, 2.00, 0.25)

class WorkDayEntry:
    """Each object of this class represents a sequence of VCS timetamps for events on a single day

    For the sake of simplicity, timestamps occurring withing the same 24 hour
    perido but reported from different timezones are treated as timestamps on
    two separate days.
    """
    def __init__(self, contributor, event_dt):
        self.contributor = contributor
        self.date = event_dt.date()
        self.tzname = event_dt.tzname()
        self.event_times = [event_dt]
    def key(self):
        """Primary key of the record consists of the date, timezone and contributor name"""
        return self.date, self.tzname, self.contributor,
    def add_event(self, event_dt):
        """Add an instantaneous event entry to the record"""
        if str(event_dt.date()) != str(self.date):
            raise RuntimeError("WorkDayEntry.add_event(): attempt to add event to wrong day")
        if event_dt.tzname() != self.tzname:
            raise RuntimeError(
                "WorkDayEntry.add_event(): attempt to add event to day with wrong timezone"
            )
        self.event_times += [event_dt]
        self.event_times.sort()
    def work_hours(self, assumptions, round_to=1.0):
        """Iterate the instantaneous event entries, to estimate the sum of hours worked"""
        if round_to not in _SUPPORTED_ROUND_TO:
            raise RuntimeError("WorkDayEntry.work_hours(): Unsupported round_to parameter")
        hours = 0.0
        td_before = datetime.timedelta(assumptions.before/_HOURS_PER_DAY)
        td_between = datetime.timedelta(assumptions.between/_HOURS_PER_DAY)
        td_after = datetime.timedelta(assumptions.after/_HOURS_PER_DAY)
        event_start = self.event_times[0] - td_before
        for i in range(0, len(self.event_times)):
            event_time = self.event_times[i]
            if i == 0:
                # First event of day
                # Must be a new group
                # event_start initialized before loop is valid
                pass
            elif event_start - td_after > event_time - td_between:
                # Separation since middle of last event is less than between param
                # event_start value set at end of last iteration is valid
                pass
            elif event_start > event_time - td_before:
                # Separation since end of last event is less than before param
                # event_start value set at end of last iteration is valid
                pass
            else:
                # First event of a new group
                event_start = event_time - td_before
            event_end = event_time + td_after
            hours += (event_end - event_start).total_seconds()/_SECONDS_PER_HOUR
            event_start = event_end
        return round(round_to*round(hours/round_to), 2)

class WorkLog:
    """This class implements reporting based on a collection of WorkDayEntry records"""
    def __init__(self):
        self.work_day_entries = {}
    def add_event(self, contributor, event_dt):
        """Add an instantantous VCS log event to the collection

        If this is the first event for the contributor/day it occurs on,
        a new WorkDayEntry record will be created.
        If a WorkDayEntry already exists, the event will be added to it.
        """
        new_wde = WorkDayEntry(contributor, event_dt)
        key = new_wde.key()
        if key in self.work_day_entries:
            self.work_day_entries[new_wde.key()].add_event(event_dt)
        else:
            self.work_day_entries[key] = new_wde
    def report(self, stream, assumptions=DEFAULT_ASSUMPTIONS, round_to=0.1):
        """Once all events ahve been added to the colleciton, a report is generated"""
        total_days = 0
        total_hours = 0.0
        print("Entries:", file=stream)
        print("--------", file=stream)
        for key in sorted(self.work_day_entries):
            wde = self.work_day_entries[key]
            hours = wde.work_hours(assumptions, round_to)
            print(key[0], key[1], hours, key[2], file=stream)
            total_days += 1
            total_hours += hours
        print("========", file=stream)
        print("Summary:", file=stream)
        print("--------", file=stream)
        print("Total active contributor days:", total_days, file=stream)
        print("Total hours worked:", round(total_hours, 3), file=stream)
        print("Mean hours per day:", round(total_hours/total_days, 3), file=stream)
