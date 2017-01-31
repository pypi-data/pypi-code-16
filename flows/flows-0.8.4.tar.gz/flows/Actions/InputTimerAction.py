#!/usr/bin/env python

'''
TimerAction.py
--------------

Copyright 2016 Davide Mastromatteo
'''

import datetime
from flows.Actions.Action import Action


class TimerAction(Action):
    """
    TimerAction Class
    """

    type = "timer"
    delay = 0
    #capture_own_messages = True
    #need_warmup = True
    start_time = None

    def on_init(self):
        super().on_init()
        self.delay = int(self.configuration["delay"])
        self.start_time = datetime.datetime.now()

    def on_cycle(self):
        super().on_cycle()
        now = datetime.datetime.now()
        diff = now - self.start_time

        if diff.total_seconds() >= self.delay:
            self.start_time = now
            self.send_message("TIMER : " + self.name)
