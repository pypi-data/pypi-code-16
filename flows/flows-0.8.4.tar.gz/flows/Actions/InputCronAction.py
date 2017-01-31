#!/usr/bin/env python

'''
CronAction.py
--------------

Execute an action when the schedule criterion is met.
The parameter crontab_schedule has to be in the crontab format:

.---------------- [m]inute: (0 - 59)
|  .------------- [h]our: (0 - 23)
|  |  .---------- [d]ay of month: (1 - 31)
|  |  |  .------- [mon]th: (1 - 12)
|  |  |  |  .---- [w]eek day: (0 - 6)
|  |  |  |  |
*  *  *  *  *

Copyright 2016 Davide Mastromatteo
'''

import datetime
import croniter
from flows.Actions.Action import Action


class CronAction(Action):
    """
    CronAction Class
    """

    type = "cron"

    crontab_schedule = "* * * * *"
    next = None
    cron = None

    def on_init(self):
        super().on_init()

        if "crontab_schedule" not in self.configuration:
            raise ValueError(str.format("The cron action {0} is not properly configured."
                                        "The crontab_schedule parameter is missing",
                                        self.name))

        self.crontab_schedule = self.configuration["crontab_schedule"]

        now = datetime.datetime.now()
        now = now.replace(microsecond=0)

        self.cron = croniter.croniter(self.crontab_schedule, now)
        self.next = self.cron.get_next(datetime.datetime)

    def on_cycle(self):
        super().on_cycle()

        now = datetime.datetime.now()
        now = now.replace(microsecond=0)

        if now >= self.next:
            self.next = self.cron.get_next(datetime.datetime)
            self.send_message("CRON")
