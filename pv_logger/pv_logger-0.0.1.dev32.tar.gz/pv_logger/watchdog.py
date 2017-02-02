"""watch some system metrics"""

import datetime
import socket
from urllib2 import urlopen
import logging
import os

from sqlite_influx import sqlite, Config

logger = logging.getLogger(__name__)

def test_internet_connection():
    """test internet connection

    Returns:
        working (bool): If internet is working, return True
    """

    socket.setdefaulttimeout( 23 )
    try:
        response = urlopen('http://google.com/')
        return True
    except Exception as e:
        logger.exception("seems like no internet connection")
        return False

def get_freemem():
    """get free ram in kbytes of computer"""
    mem = os.popen("awk '/MemFree/{print $2}' /proc/meminfo").read()
    return int(mem)

def get_uptime():
    """get uptime of computer

    Returns:
        uptime (:obj:`datetime.timedelta`)
    """

    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime = datetime.timedelta(seconds = uptime_seconds)

        return uptime


def reboot():
    """try to reboot the system in 3 minutes

    Returns:
        success (bool): If reboot command was successfull
    """
    # shutdown now, rpi has no realtime clock
    # therefore future shutdowns might become a problem
    res = os.system("sudo -n shutdown -r now")
    if res == 0:
        return True
    else:
        return False

class Manager(object):
    """register checks which will be overseen
    if check fails, then system will reboot, if other conditios are met

    Example:
        wdog_manager = Manager()
        wdog_manager.register_check('internet_connection',
            datetime.timedelta(seconds=30), 3, test_internet_connection)

        while True:
            wdog_manager.run()
            time.sleep(30)
    """

    def __init__(self):
        # use uptime, because it also works on read only systems
        self.start_time = get_uptime()
        logger.info('uptime at app start is: {}'.format(
                self.start_time
            ))

        self.checks = {}

        if 'min_uptime_seconds_before_reboot' in Config.config:
            min_seconds = Config.config['min_uptime_seconds_before_reboot']
        else:
            logger.info('use default min uptime seconds before reboot of 3600'
                ' because not found in config')
            min_seconds = 3600

        min_uptime_for_reboot = datetime.timedelta(
            seconds=min_seconds)
        assert isinstance(min_uptime_for_reboot, datetime.timedelta)
        self.min_uptime_for_reboot = min_uptime_for_reboot

    def register_check(self, name, interval, min_fails_in_row, callback=None):
        item = {
            'interval': interval,
            'min_fails_in_row': min_fails_in_row,
            'results': [],
            'callback': callback
        }
        self.checks[name] = item

    def update_checks(self):
        for name in self.checks:
            check = self.checks[name]

            # update value
            if check['callback']:
                # but only if interval is over
                now = get_uptime()

                # check if not first run
                if len(check['results']) < 1:
                    interval_over = True
                else:
                    last_time = check['results'][-1][0]
                    interval_over = (last_time + check['interval'] < now)

                if interval_over:
                    # interval since last check is over
                    # do update result
                    value = check['callback']()
                    self.update_result(name, value)

            # keep only latest x results
            x = check['min_fails_in_row']
            self.checks[name]['results'] = self.checks[name]['results'][-x:]

    def update_result(self, name, value):
        """update result of a check

        must be done manually, if no callback was provided
        """
        check = (get_uptime(), bool(value))
        self.checks[name]['results'].append(check)
        logger.info("update watchdog result of %s with %s", name, check)

    def log_reboot(self, failed):
        """log reboot reason"""

        message = 'Reboot system because of failed checks:\n'
        message += '\n'.join([item[1] for item in failed])

        logger.error(message)
        measurements = {
            'watchdog_message': {
                'message': message
            }
        }
        sqlite.store_dicts(measurements)

    def run(self):
        logger.debug("manager:run()")
        self.update_checks()

        failed = self.find_failed()
        if len(failed) > 0:
            # check other conditions
            uptime = get_uptime()
            logger.info("uptime is {}, {} needed before reboot".format(
                uptime, self.min_uptime_for_reboot))
            if uptime > self.min_uptime_for_reboot:
                # now we can reboot
                self.log_reboot(failed)
                reboot()

    def find_failed(self):
        """find failed checks

        Returns:
            failed_checks (list of tuples): list of tuples (name, message)
        """
        failed_checks = []
        for name in self.checks:
            results = self.checks[name]['results']
            logger.debug("results of check {} are {}".format(name, results))

            # we only keep no of min_fails_in_row results
            # therefore we need only count how many of them are failed
            failed_count = sum([1 for item in results if item[1] is False])

            if failed_count >= self.checks[name]['min_fails_in_row']:
                # test failed too often
                message = ("check {} failed due to {} fails in a row".format(
                    name, failed_count))
                failed_checks.append((name, message))

                # ignore other checks
                continue

            # check can also fail, if not updated too long
            if len(results) > 0:
                last_time = results[-1][0]
                used_start_time = ''
            else:
                last_time = self.start_time
                used_start_time = ' never, checked against start time instead '

            now = get_uptime()
            interval_over = (last_time + self.checks[name]['interval'] < now)
            if interval_over:
                # test not updated for too long
                message = ("check {} failed due to missing "
                            "update in interval. Should update every "
                            "{}, but last was {}{}".format(
                            name, self.checks[name]['interval'],
                            used_start_time, last_time))
                failed_checks.append((name, message))

        return failed_checks
