#!/usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Copyright (C) since 2016 Jan Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------

"""
Base implementation of generic one time execution script with cron support.
"""

import os
import re
import sys
import json
import time
import math
import subprocess
import pprint

# Generate the path to custom 'lib' directory
lib = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.insert(0, lib)

#
# Custom libraries.
#
import pyzenkit.baseapp

#
# Predefined constants for runtime intervals
#
RUN_INTERVALS = {
    'hourly':        3600,
    '2_hourly':   (2*3600),
    '3_hourly':   (3*3600),
    '4_hourly':   (4*3600),
    '6_hourly':   (6*3600),
    '12_hourly': (12*3600),
    'daily':        86400,
    'weekly':    (7*86400),
    '2_weekly': (14*86400),
    '4_weekly': (28*86400),
}

class ZenScriptException(pyzenkit.baseapp.ZenAppException):
    """
    Describes problems specific to scripts.
    """
    pass

class ZenScript(pyzenkit.baseapp.BaseApp):
    """
    Base implementation of generic one time execution script with cron support.
    """

    #
    # Class constants.
    #

    # String patterns
    PTRN_COMMAND_CBK = 'cbk_command_'

    # List of possible configuration keys.
    CONFIG_REGULAR  = 'regular'
    CONFIG_SHELL    = 'shell'
    CONFIG_INTERVAL = 'interval'
    CONFIG_COMMAND  = 'command'

    def _init_argparser(self, **kwargs):
        """
        Initialize script command line argument parser.
        """
        argparser = super()._init_argparser(**kwargs)

        # Setup mutually exclusive group.
        group_a = argparser.add_mutually_exclusive_group()
        # Option flag indicating that the script was executed via CRON tool.
        # This option will make sure, that no output will be produced to terminal.
        group_a.add_argument('--regular', help = 'regular script execution (flag)', action='store_true', default = None)

        # Option flag indicating that the script was executed manually via terminal.
        # This optional will make sure, that no changes will be made in 'log',
        # 'runlog' or 'state' files.
        group_a.add_argument('--shell', help = 'manual script execution from shell (flag)', action = 'store_true', default = None)

        # Option for setting the interval for regular script runs.
        argparser.add_argument('--interval', help = 'define interval for regular executions', choices = RUN_INTERVALS.keys())

        # Option for setting the desired command.
        argparser.add_argument('--command', help = 'choose which command should be performed', choices = self._utils_detect_commands())

        return argparser

    def _init_config(self, **kwargs):
        """
        Initialize script configurations to default values.
        """
        config = super()._init_config(**kwargs)

        cfgs = (
            (self.CONFIG_REGULAR,  False),
            (self.CONFIG_SHELL,    False),
            (self.CONFIG_INTERVAL, None),
            (self.CONFIG_COMMAND, self.get_default_command()),
        )
        for c in cfgs:
            config[c[0]] = kwargs.pop('default_' + c[0], c[1])
        return config

    #---------------------------------------------------------------------------

    def _utils_detect_commands(self):
        """
        Returns the sorted list of all available commands current script is capable
        of performing. The detection algorithm is based on string analysis of all
        available methods. Any method starting with string 'cbk_command_' will
        be appended to the list, lowercased and with '_' characters replaced with '-'.
        """
        ptrn = re.compile(self.PTRN_COMMAND_CBK)
        attrs = sorted(dir(self))
        result = []
        for a in attrs:
            if not callable(getattr(self, a)):
                continue
            match = ptrn.match(a)
            if match:
                result.append(a.replace(self.PTRN_COMMAND_CBK,'').replace('_','-').lower())
        return result

    def get_default_command(self):
        """
        Return the name of the default operation. This method must be present and
        overriden in subclass and must return the name of desired default operation.
        Following code is just a reminder for programmer to not forget to implement
        this method.
        """
        raise Exception("get_default_command() method must be implemented in subclass")

    def calculate_interval_thresholds(self, thr_type = 'daily', time_cur = None, flag_floor = False, merge_count = 1, skip_count = 0, last_ts = None):
        """
        Calculate time thresholds based on following optional arguments:
        """
        if not thr_type in RUN_INTERVALS:
            raise Exception("Invalid threshold interval '{}'".format(thr_type))
        interval = RUN_INTERVALS[thr_type]

        time_l = 0  # Lower threshold.
        time_h = 0  # Upper threshold.

        # Define the upper interval threshold as current timestamp, or use the
        # one given as argument.
        time_h = time_cur
        if not time_h:
            time_h = math.floor(time.time());

        # Adjust the upper interval threshold.
        if flag_floor:
            time_h = time_h - (time_h % interval)

        # Calculate the lower time threshold.
        time_l = time_h - interval

        return (time_l, time_h);

    #---------------------------------------------------------------------------

    def _configure_postprocess(self):
        """
        Setup internal script core mechanics.
        """
        super()._configure_postprocess()

        if self.c(self.CONFIG_SHELL):
            self.dbgout("[STATUS] Logging to log file is suppressed via '--shell' configuration")
            self.config[self.CORE][self.CORE_LOGGING][self.CORE_LOGGING_TOFILE] = False
            self.dbgout("[STATUS] Runlog saving is suppressed via '--shell' configuration")
            self.config[self.CORE][self.CORE_RUNLOG][self.CORE_RUNLOG_SAVE] = False
            self.dbgout("[STATUS] Persistent state saving is suppressed via '--shell' configuration")
            self.config[self.CORE][self.CORE_PSTATE][self.CORE_PSTATE_SAVE] = False
        else:
            self.config[self.CORE][self.CORE_LOGGING][self.CORE_LOGGING_TOFILE] = True
            self.config[self.CORE][self.CORE_RUNLOG][self.CORE_RUNLOG_SAVE] = True
            self.config[self.CORE][self.CORE_PSTATE][self.CORE_PSTATE_SAVE] = True

    def stage_process(self):
        """
        Script lifecycle stage: PROCESSING

        Perform some real work (finally). Following method will call appropriate
        callback method operation to service the selected operation.
        """
        self.time_mark('stage_process_start', 'Start of the processing stage')

        try:
            # Determine, which command to execute.
            self.runlog[self.RLKEY_COMMAND] = self.c(self.CONFIG_COMMAND)
            opname = self.c(self.CONFIG_COMMAND)
            opcbkname = self.PTRN_COMMAND_CBK + opname.lower().replace('-','_')
            self.logger.debug("Performing script command '{}' with method '{}'".format(opname, opcbkname))

            cbk = getattr(self, opcbkname, None)
            if cbk:
                self.logger.info("Executing command '{}'".format(opname))
                self.runlog[opname] = cbk()
            else:
                raise pyzenkit.baseapp.ZenAppProcessException("Invalid command '{}', callback '{}' does not exist".format(opname, opcbkname))

        except subprocess.CalledProcessError as err:
            self.error("System command error: {}".format(err))

        except pyzenkit.baseapp.ZenAppProcessException as exc:
            self.error("ZenAppProcessException: {}".format(exc))

        except pyzenkit.baseapp.ZenAppException as exc:
            self.error("ZenAppException: {}".format(exc))

        self.time_mark('stage_process_stop', 'End of the processing stage')

class _DemoZenScript(ZenScript):
    """
    Minimalistic class for demonstration purposes.
    """

    def get_default_command(self):
        """
        Return the name of a default script operation.
        """
        return 'default'

    def cbk_command_default(self):
        """
        Default script operation.
        """
        # Log something to show we have reached this point of execution.
        self.logger.info("Demo implementation for default command")

        # Test direct console output with conjunction with verbosity
        self.p("Hello world")
        self.p("Hello world, verbosity level 1", 1)
        self.p("Hello world, verbosity level 2", 2)
        self.p("Hello world, verbosity level 3", 3)

        # Update the persistent state to view the changes.
        self.pstate['counter'] = self.pstate.get('counter', 0) + 1

        return self.RESULT_SUCCESS

if __name__ == "__main__":
    """
    Perform the demonstration.
    """
    # Prepare the environment
    if not os.path.isdir('/tmp/zenscript.py'):
        os.mkdir('/tmp/zenscript.py')
    pyzenkit.baseapp.BaseApp.json_save('/tmp/zenscript.py.conf', {'test_a':1})

    script = _DemoZenScript(
            path_cfg = '/tmp',
            path_log = '/tmp',
            path_tmp = '/tmp',
            path_run = '/tmp',
            description = 'DemoZenScript - generic script (DEMO)'
        )
    script.run()
