#!/usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Copyright (C) since 2016 Jan Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------

"""
Base implementation of generic daemon.
"""

import os
import re
import sys
import pwd
import grp
import json
import time
import copy
import signal
import collections
import subprocess
import heapq
import math
import glob
import pprint

# Generate the path to custom 'lib' directory
lib = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.insert(0, lib)

#
# Custom libraries.
#
import pyzenkit.baseapp
import pyzenkit.daemonizer

# Translation table to translate signal numbers to their names.
SIGNALS_TO_NAMES_DICT = dict((getattr(signal, n), n) \
    for n in dir(signal) if n.startswith('SIG') and '_' not in n )

# Simple method for JSON serialization
def _json_default(o):
    if isinstance(o, ZenDaemonComponent):
        return "COMPONENT({})".format(o.__class__.__name__)
    elif callable(o):
        return "CALLBACK({}:{})".format(o.__self__.__class__.__name__, o.__name__)
    else:
        raise TypeError(o)

class QueueEmptyException(Exception):
    """
    Exception representing empty event queue.
    """

    def __init__(self, description):
        self._description = description
    def __str__(self):
        return repr(self._description)

class EventQueueManager:
    """
    Implementation of event queue manager.

    This implementation supports scheduling of both generic sequential events and
    timed events.
    """

    def __init__(self, **kwargs):
        """

        """
        self.events    = collections.deque()
        self.events_at = []

    def __del__(self):
        """
        Default script object destructor. Perform generic cleanup.
        """
        pass

    def schedule(self, event, args = None):
        """
        Schedule new event to the end of the event queue.
        """
        self.events.append((event, args))

    def schedule_next(self, event, args = None):
        """
        Schedule new event to the beginning of the event queue.
        """
        self.events.appendleft((event, args))

    def schedule_at(self, ts, event, args = None):
        """
        Schedule new event for a specific time.
        """
        heapq.heappush(self.events_at, (ts, event, args))

    def schedule_after(self, delay, event, args = None):
        """
        Schedule new event after a given.
        """
        ts = time.time() + delay
        heapq.heappush(self.events_at, (ts, event, args))

    def next(self):
        """
        Fetch next event from event queue.
        """
        l1 = len(self.events_at)
        if l1:
            if self.events_at[0][0] <= time.time():
                (ts, event, args) = heapq.heappop(self.events_at)
                return (event, args)
        l2 = len(self.events)
        if l2:
            return self.events.popleft()
        if (l1 + l2) == 0:
            raise QueueEmptyException("Event queue is empty")
        return (None, None)

    def when(self):
        """
        Determine the time when the next event is scheduled.
        """
        return self.events_at[0][0]

    def wait(self):
        """
        Calculate the waiting period until the next even is due.
        """
        return self.events_at[0][0] - time.time()

    def count(self):
        """
        Count the total number of scheduled events.
        """
        return len(self.events_at) + len(self.events)

class ZenDaemonComponentException(Exception):
    """

    """
    def __init__(self, description):
        self._description = description
    def __str__(self):
        return repr(self._description)

class ZenDaemonComponent:
    """
    Base implementation of all daemon components.
    """

    def __init__(self, **kwargs):
        """

        """
        self.statistics_cur  = {}
        self.statistics_prev = {}
        self.statistics_ts   = time.time()
        self.pattern_stats = "{}\n\t{:15s}  {:12,d} (+{:8,d}, {:8,.2f} #/s)"

    def inc_statistics(self, key, increment = 1):
        """
        Raise given statistics key with given increment.
        """
        self.statistics_cur[key] = self.statistics_cur.get(key, 0) + increment

    def get_events(self):
        """
        Get the list of event names and their appropriate callback handlers.
        """
        raise Exception("This method must be implemented in subclass")

    def get_state(self, daemon):
        """
        Get the current internal state of component (for debugging).
        """
        return {}

    def calc_statistics(self, daemon, stats_cur, stats_prev, tdiff):
        """

        """
        result = {}
        for k in stats_cur:
            if isinstance(stats_cur[k], int):
                result[k] = {
                    'cnt':  stats_cur[k],
                    'inc':  stats_cur[k] - stats_prev.get(k, 0),
                    'spd': (stats_cur[k] - stats_prev.get(k, 0)) / tdiff
                }
            elif isinstance(stats_cur[k], dict):
                result[k] = self.calc_statistics(daemon, stats_cur[k], stats_prev.get(k, {}), tdiff)
        return result

    def get_statistics(self, daemon):
        """
        Calculate processing statistics
        """
        ct = time.time()
        tdiff = ct - self.statistics_ts

        stats = self.calc_statistics(daemon, self.statistics_cur, self.statistics_prev, tdiff)

        self.statistics_prev = copy.copy(self.statistics_cur)
        self.statistics_ts = ct
        return stats

    def setup(self, daemon):
        """
        Perform component setup.
        """
        pass

    def setup_dump(self, daemon):
        """
        Dump component setup.
        """
        pass

class ZenDaemonException(pyzenkit.baseapp.ZenAppException):
    """
    Describes problems specific to daemons.
    """
    pass

class ZenDaemon(pyzenkit.baseapp.BaseApp):
    """
    Base implementation of generic daemon.
    """

    # Event loop processing flags.
    FLAG_CONTINUE = 1
    FLAG_STOP     = 0

    EVENT_SIGNAL_HUP     = 'signal_hup'
    EVENT_SIGNAL_USR1    = 'signal_usr1'
    EVENT_SIGNAL_USR2    = 'signal_usr2'
    EVENT_LOG_STATISTICS = 'log_statistics'

    # List of core configuration keys.
    CORE_STATE          = 'state'
    CORE_STATE_SAVE     = 'save'

    # List of possible configuration keys.
    CONFIG_COMPONENTS     = 'components'
    CONFIG_NODAEMON       = 'no_daemon'
    CONFIG_CHROOT_DIR     = 'chroot_dir'
    CONFIG_WORK_DIR       = 'work_dir'
    CONFIG_PID_FILE       = 'pid_file'
    CONFIG_STATE_FILE     = 'state_file'
    CONFIG_UMASK          = 'umask'
    CONFIG_USER           = 'user'
    CONFIG_GROUP          = 'group'
    CONFIG_STATS_INTERVAL = 'stats_interval'
    CONFIG_PARALEL        = 'paralel'

    def __init__(self, **kwargs):
        """
        Default script object constructor.
        """
        super().__init__(**kwargs)

        self.queue      = EventQueueManager()
        self.components = []
        self.callbacks  = {}

        self._init_callbacks(**kwargs)
        self._init_components(**kwargs)
        self._init_schedule(**kwargs)

    def _init_config(self, **kwargs):
        """
        Initialize script configurations to default values.
        """
        config = super()._init_config(**kwargs)

        cfgs = (
            (self.CONFIG_NODAEMON,       False),
            (self.CONFIG_CHROOT_DIR,     None),
            (self.CONFIG_WORK_DIR,       '/'),
            (self.CONFIG_PID_FILE,       os.path.join(self.paths.get(self.PATH_RUN), "{}.pid".format(self.name))),
            (self.CONFIG_STATE_FILE,     os.path.join(self.paths.get(self.PATH_RUN), "{}.state".format(self.name))),
            (self.CONFIG_UMASK,          None),
            (self.CONFIG_USER,           None),
            (self.CONFIG_GROUP,          None),
            (self.CONFIG_STATS_INTERVAL, 300),
            (self.CONFIG_PARALEL,        False),
        )
        for c in cfgs:
            config[c[0]] = kwargs.pop('default_' + c[0], c[1])
        return config

    def _init_argparser(self, **kwargs):
        """
        Initialize script command line argument parser.
        """
        argparser = super()._init_argparser(**kwargs)

        # Option flag indicating that the script should not daemonize and stay
        # in foreground (usefull for debugging or testing).
        argparser.add_argument('--no-daemon', help = 'do not daemonize, stay in foreground (flag)', action='store_true', default = None)

        # Option for overriding the name of the chroot directory.
        argparser.add_argument('--chroot-dir', help = 'name of the chroot directory')

        # Option for overriding the name of the work directory.
        argparser.add_argument('--work-dir', help = 'name of the work directory')

        # Option for overriding the name of the PID file.
        argparser.add_argument('--pid-file', help = 'name of the pid file')

        # Option for overriding the name of the state file.
        argparser.add_argument('--state-file', help = 'name of the state file')

        # Option for overriding the default umask.
        argparser.add_argument('--umask', help = 'default file umask')

        # Option for overriding the process UID.
        argparser.add_argument('--user', help = 'process UID or user name')

        # Option for overriding the process GID.
        argparser.add_argument('--group', help = 'process GID or group name')

        # Option for defining processing statistics display interval.
        argparser.add_argument('--stats-interval', help = 'define processing statistics display interval')

        # Option flag indicating that the script may run in paralel processes.
        argparser.add_argument('--paralel', help = 'run in paralel mode (flag)', action = 'store_true', default = None)

        return argparser

    def _init_event_callback(self, event, callback, prepend = False):
        """
        Set given callback as handler for given event.
        """
        if event not in self.callbacks:
            self.callbacks[event] = []
        if not prepend:
            self.callbacks[event].append(callback)
        else:
            self.callbacks[event].insert(0, callback)

    def _init_callbacks(self, **kwargs):
        """
        Initialize internal event callbacks.
        """
        for event in self.get_events():
            self._init_event_callback(event['event'], event['callback'], event['prepend'])

    def _init_components(self, **kwargs):
        """
        Initialize daemon components.
        """
        components = kwargs.get(self.CONFIG_COMPONENTS, [])
        for component in components:
            self.components.append(component)
            elist = component.get_events()
            for event in elist:
                self._init_event_callback(event['event'], event['callback'], event['prepend'])

    def _init_schedule(self, **kwargs):
        """
        Schedule initial events.
        """
        initial_events = kwargs.get('schedule', [])
        for event in initial_events:
            self.queue.schedule(*event)
        initial_events = kwargs.get('schedule_next', [])
        for event in initial_events:
            self.queue.schedule_next(*event)
        initial_events = kwargs.get('schedule_at', [])
        for event in initial_events:
            self.queue.schedule_at(*event)
        initial_events = kwargs.get('schedule_after', [])
        for event in initial_events:
            self.queue.schedule_after(*event)

    #---------------------------------------------------------------------------

    def _configure_postprocess(self):
        """
        Setup internal script core mechanics. Config postprocessing routine.
        """
        super()._configure_postprocess()

        cc = {}
        cc[self.CORE_STATE_SAVE]  = True
        self.config[self.CORE][self.CORE_STATE] = cc

        if self.c(self.CONFIG_NODAEMON):
            self.dbgout("[STATUS] Console log output is enabled via '--no-daemon' configuration")
            self.config[self.CORE][self.CORE_LOGGING][self.CORE_LOGGING_TOCONS] = True
        else:
            self.config[self.CORE][self.CORE_LOGGING][self.CORE_LOGGING_TOCONS] = False

        self.config[self.CORE][self.CORE_LOGGING][self.CORE_LOGGING_TOFILE] = True
        self.config[self.CORE][self.CORE_RUNLOG][self.CORE_RUNLOG_SAVE] = True
        self.config[self.CORE][self.CORE_PSTATE][self.CORE_PSTATE_SAVE] = True

        if self.config[self.CONFIG_USER]:
            u = self.config[self.CONFIG_USER]
            res = None
            if not res:
                try:
                    res = pwd.getpwnam(u)
                    self.config[self.CONFIG_USER] = res[2]
                except:
                    pass
            if not res:
                try:
                    res = pwd.getpwuid(int(u))
                    self.config[self.CONFIG_USER] = res[2]
                except:
                    pass
            if not res:
                raise ZenDaemonException("Unknown user '{}'".format(u))

        if self.config[self.CONFIG_GROUP]:
            g = self.config[self.CONFIG_GROUP]
            res = None
            if not res:
                try:
                    res = grp.getgrnam(g)
                    self.config[self.CONFIG_GROUP] = res[2]
                except:
                    pass
            if not res:
                try:
                    res = grp.getgruid(int(g))
                    self.config[self.CONFIG_GROUP] = res[2]
                except:
                    pass
            if not res:
                raise ZenDaemonException("Unknown group '{}'".format(g))


    def _stage_setup_custom(self):
        """
        Perform custom daemon related setup.
        """
        for component in self.components:
            component.setup(self)

    def _stage_setup_dump(self):
        """
        Dump script setup information.

        This method will display information about script system paths, configuration
        loaded from CLI arguments or config file, final merged configuration.
        """
        super()._stage_setup_dump()

        self.logger.debug("Daemon component list >>>\n{}".format(json.dumps(self.components, sort_keys=True, indent=4, default=_json_default)))
        self.logger.debug("Registered event callbacks >>>\n{}".format(json.dumps(self.callbacks, sort_keys=True, indent=4, default=_json_default)))
        self.logger.debug("Daemon component setup >>>\n")
        for component in self.components:
            self.logger.debug(">>> {} >>>\n".format(component.__class__.__name__))
            component.setup_dump(self)

    #---------------------------------------------------------------------------

    def _hnd_signal_wakeup(self, signum, frame):
        """
        Minimal signal handler - wakeup after sleep/pause.
        """
        self.logger.info("Wakeup after pause")

    def _hnd_signal_hup(self, signum, frame):
        """
        Minimal signal handler - SIGHUP

        Implementation of the handler is intentionally brief, actual signal
        handling is done via scheduling and handling event 'signal_hup'.
        """
        self.logger.warning("Received signal 'SIGHUP'")
        self.queue.schedule_next('signal_hup')

    def _hnd_signal_usr1(self, signum, frame):
        """
        Minimal signal handler - SIGUSR1

        Implementation of the handler is intentionally brief, actual signal
        handling is done via scheduling and handling event 'signal_usr1'.
        """
        self.logger.info("Received signal 'SIGUSR1'")
        self.queue.schedule_next('signal_usr1')

    def _hnd_signal_usr2(self, signum, frame):
        """
        Minimal signal handler - SIGUSR2

        Implementation of the handler is intentionally brief, actual signal
        handling is done via scheduling and handling event 'signal_usr2'.
        """
        self.logger.info("Received signal 'SIGUSR2'")
        self.queue.schedule_next('signal_usr2')

    #---------------------------------------------------------------------------

    def cbk_event_signal_hup(self, daemon, args = None):
        """
        Event callback to handle signal - SIGHUP
        """
        self.logger.warning("Handling event for signal 'SIGHUP'")
        return (self.FLAG_CONTINUE, None)

    def cbk_event_signal_usr1(self, daemon, args = None):
        """
        Event callback to handle signal - SIGUSR1
        """
        self.logger.info("Handling event for signal 'SIGUSR1'")
        self.runlog_save(self.runlog)
        return (self.FLAG_CONTINUE, None)

    def cbk_event_signal_usr2(self, daemon, args = None):
        """
        Event callback to handle signal - SIGUSR2
        """
        self.logger.info("Handling event for signal 'SIGUSR2'")
        if self.c(self.CONFIG_NODAEMON):
            self.state_dump(self._get_state())
        else:
            self.state_save(self._get_state(), indent=4, default=_json_default)
        return (self.FLAG_CONTINUE, None)

    def cbk_event_log_statistics(self, daemon, args):
        """
        Periodical processing statistics logging.
        """
        self.queue.schedule_after(self.c(self.CONFIG_STATS_INTERVAL), self.EVENT_LOG_STATISTICS)
        return (self.FLAG_CONTINUE, None)

    #---------------------------------------------------------------------------

    def send_signal(self, s):
        """
        Send given signal to currently running daemon(s).
        """
        pid = None
        try:
            pidfl = None # PID file list
            if not self.c(self.CONFIG_PARALEL):
                pidfl = [self.get_fn_pidfile()]
            else:
                pidfl = self.pidfiles_list()

            for pidfn in pidfl:
                pid = pyzenkit.daemonizer.read_pid(pidfn)
                if pid:
                    print("Sending signal '{}' to process '{}' [{}]".format(SIGNALS_TO_NAMES_DICT.get(s, s), pid, pidfn))
                    os.kill(pid, s)

        except FileNotFoundError:
            print("PID file '{}' does not exist".format(self.c(self.CONFIG_PID_FILE)))

        except ValueError:
            print("Malformed PID file '{}'".format(self.c(self.CONFIG_PID_FILE)))

        except ProcessLookupError:
            print("Process with PID '{}' does not exist".format(pid))

        except PermissionError:
            print("Insufficient permissions to send signal '{}' to process '{}'".format(SIGNALS_TO_NAMES_DICT.get(s, s), pid))

    def cbk_action_signal_check(self):
        """
        Send signal '0' to currently running daemon.
        """
        self.send_signal(0)

    def cbk_action_signal_alrm(self):
        """
        Send signal 'SIGALRM' to currently running daemon.
        """
        self.send_signal(signal.SIGALRM)

    def cbk_action_signal_int(self):
        """
        Send signal 'SIGINT' to currently running daemon.
        """
        self.send_signal(signal.SIGINT)

    def cbk_action_signal_hup(self):
        """
        Send signal 'SIGHUP' to currently running daemon.
        """
        self.send_signal(signal.SIGHUP)

    def cbk_action_signal_usr1(self):
        """
        Send signal 'SIGUSR1' to currently running daemon.
        """
        self.send_signal(signal.SIGUSR1)

    def cbk_action_signal_usr2(self):
        """
        Send signal 'SIGUSR2' to currently running daemon.
        """
        self.send_signal(signal.SIGUSR2)

    #---------------------------------------------------------------------------

    def _get_state(self):
        """

        """
        state = {
            'time':           time.time(),
            'rc':             self.rc,
            'config':         self.config,
            'paths':          self.paths,
            'pstate':         self.pstate,
            'callbacks':      self.callbacks,
            'component_list': self.components,
            'components':     {},
            'runlog':         self.runlog,
        }
        for component in self.components:
            state['components'][component.__class__.__name__] = component.get_state(self)
        return state

    def _get_statistics(self):
        """

        """
        statistics = {
            'time':           time.time(),
            'components':     {},
        }
        for component in self.components:
            statistics['components'][component.__class__.__name__] = component.get_statistics(self)
        return statistics

    def state_dump(self, state, **kwargs):
        """
        Dump current daemon state.

        Dump current daemon state to terminal (JSON).
        """
        # Dump current script state.
        #self.logger.debug("Current daemon state >>>\n{}".format(json.dumps(state, sort_keys=True, indent=4)))
        print("Current daemon state >>>\n{}".format(self.json_dump(state, default=_json_default, **kwargs)))

    def state_save(self, state, **kwargs):
        """
        Save current daemon state.

        Save current daemon state to external file (JSON).
        """
        sfn = self.get_fn_state()
        self.dbgout("[STATUS] Saving current daemon state to file '{}'".format(sfn))
        pprint.pprint(state)
        self.dbgout("[STATUS] Current daemon state:\n{}".format(self.json_dump(state, default=_json_default, **kwargs)))
        self.json_save(sfn, state, default=_json_default, **kwargs)
        self.logger.info("Current daemon state saved to file '{}'".format(sfn))

    def pidfiles_list(self, **kwargs):
        """
        List all available pidfiles.
        """
        reverse = kwargs.get('reverse', False)
        pfn = os.path.join(self.paths['run'], '{}*.pid'.format(self.name))
        return sorted(glob.glob(pfn), reverse = reverse)

    def get_fn_state(self):
        """
        Return the name of the state file for current process.
        """
        if not self.c(self.CONFIG_PARALEL):
            return self.c(self.CONFIG_STATE_FILE)
        else:
            fn = re.sub("\.state$",".{:05d}.state".format(os.getpid()), self.c(self.CONFIG_STATE_FILE))
            self.dbgout("[STATUS] Paralel mode: using '{}' as state file".format(fn))
            return fn

    def get_fn_pidfile(self):
        """
        Return the name of the pidfile for current process.
        """
        if not self.c(self.CONFIG_PARALEL):
            return self.c(self.CONFIG_PID_FILE)
        else:
            fn = re.sub("\.pid$",".{:05d}.pid".format(os.getpid()), self.c(self.CONFIG_PID_FILE))
            self.dbgout("[STATUS] Paralel mode: using '{}' as pid file".format(fn))
            return fn

    def get_fn_runlog(self):
        """
        Return the name of the runlog file for current process.
        """
        if not self.c(self.CONFIG_PARALEL):
            return os.path.join(self.c(self.CONFIG_RUNLOG_DIR), "{}.runlog".format(self.runlog[self.RLKEY_TSFSF]))
        else:
            fn = os.path.join(self.c(self.CONFIG_RUNLOG_DIR), "{}.{:05d}.runlog".format(self.runlog[self.RLKEY_TSFSF], os.getpid()))
            self.dbgout("[STATUS] Paralel mode: using '{}' as runlog file".format(fn))
            return fn

    def get_events(self):
        """
        Get list of internal event callbacks.
        """
        return [
            { 'event': self.EVENT_SIGNAL_HUP,     'callback': self.cbk_event_signal_hup,     'prepend': False },
            { 'event': self.EVENT_SIGNAL_USR1,    'callback': self.cbk_event_signal_usr1,    'prepend': False },
            { 'event': self.EVENT_SIGNAL_USR2,    'callback': self.cbk_event_signal_usr2,    'prepend': False },
            { 'event': self.EVENT_LOG_STATISTICS, 'callback': self.cbk_event_log_statistics, 'prepend': False },
        ]

    def wait(self, period):
        """
        Wait/pause for given amount of seconds.
        """
        period = math.ceil(period)
        if period > 0:
            self.logger.info("Waiting for '{}' seconds until next scheduled event".format(period))
            signal.signal(signal.SIGALRM, self._hnd_signal_wakeup)
            signal.alarm(period)
            signal.pause()
            signal.alarm(0)

    def done(self):
        """
        Set the DONE flag to True.
        """
        self.done = True

    def _daemonize(self):
        """
        Perform daemonization.
        """
        # Perform full daemonization
        if not self.c(self.CONFIG_NODAEMON):
            self.dbgout("[STATUS] Performing full daemonization")
            self.logger.info("Performing full daemonization")

            logs = pyzenkit.daemonizer.get_logger_files(self.logger)
            pyzenkit.daemonizer.daemonize(
                chroot_dir     = self.c(self.CONFIG_CHROOT_DIR),
                work_dir       = self.c(self.CONFIG_WORK_DIR),
                pidfile        = self.get_fn_pidfile(),
                umask          = self.c(self.CONFIG_UMASK),
                uid            = self.c(self.CONFIG_USER),
                gid            = self.c(self.CONFIG_GROUP),
                files_preserve = logs,
                signals        = {
                    signal.SIGHUP:  self._hnd_signal_hup,
                    signal.SIGUSR1: self._hnd_signal_usr1,
                    signal.SIGUSR2: self._hnd_signal_usr2,
                },
            )

            self.logger.info("Full daemonization done")
            self.runlog[self.RLKEY_PID] = os.getpid()

        # Perform simple daemonization
        else:
            self.dbgout("[STATUS] Performing simple daemonization")
            self.logger.info("Performing simple daemonization")

            pyzenkit.daemonizer.daemonize_lite(
                chroot_dir     = self.c(self.CONFIG_CHROOT_DIR),
                work_dir       = self.c(self.CONFIG_WORK_DIR),
                pidfile        = self.get_fn_pidfile(),
                umask          = self.c(self.CONFIG_UMASK),
                uid            = self.c(self.CONFIG_USER),
                gid            = self.c(self.CONFIG_GROUP),
                signals        = {
                    signal.SIGHUP:  self._hnd_signal_hup,
                    signal.SIGUSR1: self._hnd_signal_usr1,
                    signal.SIGUSR2: self._hnd_signal_usr2,
                },
            )

            self.logger.info("Simple daemonization done")
            self.runlog[self.RLKEY_PID] = os.getpid()


    def _event_loop(self):
        """
        Main event processing loop.
        """
        self.done = False
        while not self.done:
            try:
                (event, args) = self.queue.next()
                if event:
                    if event not in self.callbacks:
                        raise ZenDaemonException("There is no callback to handle event '{}'".format(event))
                    for handler in self.callbacks[event]:
                        (flag, args) = handler(self, args)
                        if flag != self.FLAG_CONTINUE:
                            break
                else:
                    w = self.queue.wait()
                    if w > 0:
                        self.wait(w)
                    pass
            except QueueEmptyException:
                self.logger.info("Event queue is empty, terminating")
                self.done = True
                pass

    def stage_process(self):
        """
        Script lifecycle stage: PROCESSING

        Perform some real work (finally). Following method will call appropriate
        callback method operation to service the selected operation.
        """
        self.time_mark('stage_process_start', 'Start of the processing stage')

        try:
            self._daemonize()
            self._event_loop()

        except KeyboardInterrupt:
            pass

        except subprocess.CalledProcessError as err:
            self.error("System command error: {}".format(err))

        except pyzenkit.baseapp.ZenAppProcessException as exc:
            self.error("ZenAppProcessException: {}".format(exc))

        except pyzenkit.baseapp.ZenAppException as exc:
            self.error("ZenAppException: {}".format(exc))

        except:
            (t, v, tb) = sys.exc_info()
            self.error("Exception: {}".format(v), tb = tb)

        self.time_mark('stage_process_stop', 'End of the processing stage')

class _DemoDaemonComponent(ZenDaemonComponent):
    """
    Minimalistic class for demonstration purposes.
    """

    def get_events(self):
        """
        Get list of internal event callbacks.
        """
        return [
            { 'event': 'default', 'callback': self.cbk_event_default, 'prepend': False }
        ]

    def cbk_event_default(self, daemon, args = None):
        """
        Callback handler for default event.
        """
        daemon.queue.schedule('default')
        daemon.logger.info("Working")
        time.sleep(1)
        return (daemon.FLAG_CONTINUE, None)

class _DemoZenDaemon(ZenDaemon):
    """
    Minimalistic class for demonstration purposes.
    """

    pass

if __name__ == "__main__":
    """
    Perform the demonstration.
    """
    # Prepare the environment
    if not os.path.isdir('/tmp/zendaemon.py'):
        os.mkdir('/tmp/zendaemon.py')
    pyzenkit.baseapp.BaseApp.json_save('/tmp/zendaemon.py.conf', {'test_a':1})

    daemon = _DemoZenDaemon(
            path_cfg = '/tmp',
            path_log = '/tmp',
            path_tmp = '/tmp',
            path_run = '/tmp',
            description = 'DemoZenDaemon - generic daemon (DEMO)',
            schedule = [('default',)],
            components = [
                _DemoDaemonComponent()
            ]
        )
    daemon.run()
