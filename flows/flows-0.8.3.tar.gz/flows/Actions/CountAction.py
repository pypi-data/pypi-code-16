#!/usr/bin/env python

'''
CountAction.py
--------------

Copyright 2016 Davide Mastromatteo
License: Apache-2.0
'''

import datetime
from flows.Actions.Action import Action


class CountAction(Action):
    """
    CountAction Class
    Count the input and pass the counter to the output.
    Can work in association with a TIMER event.
    """

    timed_counter = False
    type = "count"
    counter = 0
    timer_start = datetime.datetime.now()
    timeout = 0
    partial_counter = False

    def on_init(self):
        super().on_init()
        if "timeout" in self.configuration:
            self.timed_counter = True
            self.timeout = int(self.configuration["timeout"])
        if "partial" in self.configuration:
            self.partial_counter = True

    def on_cycle(self):
        super().on_cycle()
        if (datetime.datetime.now() - self.timer_start).total_seconds() > self.timeout:
            self.send_message(str(self.counter))
            self.timer_start = datetime.datetime.now()
            if self.partial_counter:
                self.counter = 0

    def on_input_received(self, action_input=None):
        super().on_input_received(action_input)
        self.counter = self.counter + 1
        if not self.timed_counter:
            self.send_message(str(self.counter))
