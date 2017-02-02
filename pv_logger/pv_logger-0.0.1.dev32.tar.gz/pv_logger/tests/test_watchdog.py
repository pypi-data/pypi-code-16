import unittest as unittest
import datetime
import os
import time
try:
    from unittest import mock
except ImportError:
    import mock

from pv_logger import watchdog

class WatchdogTest(unittest.TestCase):
    def test_internet(self):
        internet = watchdog.test_internet_connection()

        self.assertEqual(internet, True)

    def test_uptime(self):
        uptime = watchdog.get_uptime()

        self.assertTrue(uptime > datetime.timedelta(seconds=5))

    def test_reboot(self):
        watchdog.reboot()

        print("cancel reboot again")
        os.system("shutdown -c")

    def test_freemem(self):
        mem = watchdog.get_freemem()

        self.assertTrue(isinstance(mem, int))

class WatchdogManagerTest(unittest.TestCase):
    callback_1_count = 0
    fail = True

    @mock.patch('pv_logger.watchdog.reboot')
    def test_ok_fail(self, reboot_mock):
        for self.fail in [False, True]:
            print("shoudl fail?", self.fail)
            self.callback_1_count = 0
            wdog_manager = watchdog.Manager()
            # set min uptime of watchdog to 0, so reboot is always called
            wdog_manager.min_uptime_for_reboot = datetime.timedelta(
                seconds=0)

            wdog_manager.register_check('callback_1',
                datetime.timedelta(seconds=0.2), 3, self.callback_1)

            # testing of 3 fails takes 0.2*2 = 0.4 seconds
            # run at 0.s0, 0.1s, 0.2s, 0.3s, 0.4s
            for i in range(1,6):
                wdog_manager.run()
                # check callback is only called when interval is over
                print("waited since start:", (i-1)*0.1)
                if i in [1, 2]:
                    self.assertEqual(self.callback_1_count, 1)
                if i in [3, 4]:
                    self.assertEqual(self.callback_1_count, 2)
                time.sleep(0.2)

            self.assertEqual(reboot_mock.call_count, int(self.fail))

    @mock.patch('pv_logger.watchdog.get_uptime')
    @mock.patch('pv_logger.watchdog.reboot')
    def test_no_reboot_not_enough_uptime(self, reboot_mock, uptime_mock):
        uptime_mock.return_value = datetime.timedelta(seconds=10)

        self.fail = True
        wdog_manager = watchdog.Manager()
        wdog_manager.register_check('callback_1',
            datetime.timedelta(seconds=0.1), 2, self.callback_1)

        for i in [1,2]:
            wdog_manager.run()
            time.sleep(0.1)

        self.assertEqual(reboot_mock.call_count, 0)

    @mock.patch('pv_logger.watchdog.reboot')
    def test_check_result_not_set(self, reboot_mock):
        wdog_manager = watchdog.Manager()
        # set min uptime of watchdog to 0, so reboot is always called
        wdog_manager.min_uptime_for_reboot = datetime.timedelta(
            seconds=0)

        wdog_manager.register_check('check_manual',
            datetime.timedelta(seconds=0.2), 2)

        # set result once
        wdog_manager.update_result('check_manual', True)

        time.sleep(0.2)
        # set again
        wdog_manager.update_result('check_manual', True)
        wdog_manager.run()
        self.assertEqual(reboot_mock.call_count, 0)

        time.sleep(0.3)
        # now not updated too long
        wdog_manager.run()
        self.assertEqual(reboot_mock.call_count, 1)

    @mock.patch('pv_logger.watchdog.reboot')
    def test_check_result_history(self, reboot_mock):
        """check that test result history is stored correctly
        and that always the latest x results are kept, in order,
        and no others..."""
        wdog_manager = watchdog.Manager()
        # set min uptime of watchdog to 0, so reboot is always called
        wdog_manager.min_uptime_for_reboot = datetime.timedelta(
            seconds=0)

        wdog_manager.register_check('check_manual',
            datetime.timedelta(seconds=0.4), 3)

        # set result once
        wdog_manager.update_result('check_manual', True)
        time.sleep(0.1)
        wdog_manager.update_result('check_manual', False)
        time.sleep(0.1)
        wdog_manager.update_result('check_manual', True)
        time.sleep(0.1)

        wdog_manager.run()
        wdog_manager.update_result('check_manual', False)
        wdog_manager.run()

        # check that last update_result is False
        checks = wdog_manager.checks
        last_check_result = checks['check_manual']['results'][-1][-1]
        self.assertEqual(last_check_result, False)

    def callback_1(self):
        # if we want to fail, return False (check function failed)
        self.callback_1_count += 1
        return not self.fail
