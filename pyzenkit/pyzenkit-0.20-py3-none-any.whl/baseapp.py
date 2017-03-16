#!/usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Copyright (C) since 2016 Jan Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------

"""
Implementation of generic processing script/daemon/application.

This class provides base implementation of generic processing application with many
usefull features including (but not limited to) following:

* Optional configuration via external JSON configuration file
* Optional configuration via configuration directory
* Optional configuration via command line arguments and options
* Optional logging to console
* Optional logging to text file
* Optional persistent state storage between script executions
* Optional runlog saving after each script execution
* Integrated runlog analysis tools

"""

import os
import sys
import pwd
import grp
import re
import shutil
import glob
import math
import time
import json
import argparse
import logging
import logging.handlers
import pprint
import subprocess
import datetime
import traceback

# Generate the path to custom 'lib' directory
lib = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.insert(0, lib)

#
# Custom libraries.
#
import pyzenkit.jsonconf
import pydgets.widgets

#
# Global variables.
#

# Global flag, that turns on additional debugging messages.
FLAG_DEBUG = False

def _json_default(o):
    return repr(o)

class ZenAppException(Exception):
    """
    Base class for all ZenApp specific exceptions.

    These exceptions will be catched, error will be displayed to the user and
    script will attempt to gracefully terminate without dumping the traceback
    to the user. These exceptions should be used for anticipated errors, which
    can occur during normal script execution and do not mean there is anything
    wrong with the script itself, for example missing configuration file, etc...
    """
    def __init__(self, description):
        self._description = description
    def __str__(self):
        return repr(self._description)

class ZenAppSetupException(ZenAppException):
    """
    Describes problems or errors during the script 'setup' phase.
    """
    pass

class ZenAppProcessException(ZenAppException):
    """
    Describes problems or errors during the script 'process' phase.
    """
    pass

class ZenAppEvaluateException(ZenAppException):
    """
    Describes problems or errors during the script 'evaluate' phase.
    """
    pass

class ZenAppTeardownException(ZenAppException):
    """
    Describes problems or errors during the script 'teardown' phase.
    """
    pass

class BaseApp:
    """
    Base implementation of generic executable script.

    This class attempts to provide robust and stable framework, which can be used
    to writing all kinds of scripts or daemons. This is however low level framework
    and should not be used directly, use the zenscript.py or zendaemon.py
    modules for writing custom scripts or daemons respectively.
    """

    # List of all possible return codes
    RC_SUCCESS = os.EX_OK
    RC_FAILURE = 1

    # List of possible result codes.
    RESULT_SUCCESS = 'success'
    RESULT_FAILURE = 'failure'

    # String patterns
    PTRN_ACTION_CBK  = 'cbk_action_'

    # Paths
    PATH_BIN = 'bin'
    PATH_CFG = 'cfg'
    PATH_LOG = 'log'
    PATH_RUN = 'run'
    PATH_TMP = 'tmp'

    # List of core configuration keys.
    CORE                = '__core__'
    CORE_LOGGING        = 'logging'
    CORE_LOGGING_TOFILE = 'tofile'
    CORE_LOGGING_TOCONS = 'toconsole'
    CORE_LOGGING_LEVEL  = 'level'
    CORE_LOGGING_LEVELF = 'level_file'
    CORE_LOGGING_LEVELC = 'level_console'
    CORE_PSTATE         = 'pstate'
    CORE_PSTATE_SAVE    = 'save'
    CORE_RUNLOG         = 'runlog'
    CORE_RUNLOG_SAVE    = 'save'

    # List of possible configuration keys.
    CONFIG_DEBUG       = 'debug'
    CONFIG_QUIET       = 'quiet'
    CONFIG_VERBOSITY   = 'verbosity'
    CONFIG_RUNLOG_DUMP = 'runlog_dump'
    CONFIG_PSTATE_DUMP = 'pstate_dump'
    CONFIG_NAME        = 'name'
    CONFIG_ACTION      = 'action'
    CONFIG_INPUT       = 'input'
    CONFIG_LIMIT       = 'limit'
    CONFIG_USER        = 'user'
    CONFIG_GROUP       = 'group'
    CONFIG_CFG_FILE    = 'config_file'
    CONFIG_CFG_DIR     = 'config_dir'
    CONFIG_LOG_FILE    = 'log_file'
    CONFIG_LOG_LEVEL   = 'log_level'
    CONFIG_PSTATE_FILE = 'pstate_file'
    CONFIG_RUNLOG_DIR  = 'runlog_dir'

    # Runlog keys
    RLKEY_NAME    = 'name'
    RLKEY_PID     = 'pid'
    RLKEY_ARGV    = 'argv'
    RLKEY_COMMAND = 'command'
    RLKEY_TS      = 'ts'
    RLKEY_TSFSF   = 'ts_fsf'
    RLKEY_TSSTR   = 'ts_str'
    RLKEY_RESULT  = 'result'
    RLKEY_RC      = 'rc'
    RLKEY_ERRORS  = 'errors'
    RLKEY_TMARKS  = 'time_marks'

    # Runlog analysis keys
    RLANKEY_LABEL       = 'label'
    RLANKEY_COMMAND     = 'command'
    RLANKEY_AGE         = 'age'
    RLANKEY_RESULT      = 'result'
    RLANKEY_RUNLOG      = 'runlog'
    RLANKEY_DURRUN      = 'dur_run'
    RLANKEY_DURPRE      = 'dur_pre'
    RLANKEY_DURPROC     = 'dur_proc'
    RLANKEY_DURPOST     = 'dur_post'
    RLANKEY_DURATIONS   = 'durations'
    RLANKEY_EFFECTIVITY = 'effectivity'

    # Runlog evaluation keys
    RLEVKEY_ANALYSES = 'analyses'

    def __init__(self, **kwargs):
        """
        Default script object constructor.

        Only defines core internal variables. The actual object initialization,
        during which command line arguments and configuration files are parsed,
        is done during the configure() stage of the run() sequence.
        """
        # [PUBLIC] Default script help description.
        self.description = kwargs.get('description', 'BaseApp - Simple generic script')

        # [PUBLIC] Initialize command line argument parser.
        self.argparser = self._init_argparser(**kwargs)

        # Parse CLI arguments immediatelly, we need to check for a few priority
        # flags and switches
        self._config_cli = self._parse_cli_arguments()

        # [PUBLIC] Detect name of the script.
        self.name = self._init_name(**kwargs)
        # [PUBLIC] Script paths.
        self.paths  = self._init_paths(**kwargs)
        # [PUBLIC] Script processing runlog.
        self.runlog = self._init_runlog(**kwargs)
        # [PUBLIC] Storage for script configurations.
        self.config = self._init_config(**kwargs)
        # [PUBLIC] Logger object.
        self.logger = None
        # [PUBLIC] Persistent state object.
        self.pstate = None
        # [PUBLIC] Final return code.
        self.rc    = self.RC_SUCCESS

        # Perform subinitializations on default configurations and argument parser.
        self._init_custom(self.config, self.argparser, **kwargs)

    def __del__(self):
        """
        Default script object destructor. Perform generic cleanup.
        """
        pass

    #---------------------------------------------------------------------------
    # Object initialization helper methods
    #---------------------------------------------------------------------------

    def _init_argparser(self, **kwargs):
        """
        Initialize script command line argument parser.
        """
        argparser = argparse.ArgumentParser(description = self.description)

        # Option flag indicating that script is running in debug mode. This option
        # will enable displaying of additional helpful debugging messages. The
        # messages will be printed directly to terminal, without the use of
        # logging framework.
        argparser.add_argument('--debug', help = 'run in debug mode (flag)', action = 'store_true', default = None)

        # Option flag indicating that script is running in quiet mode. This option
        # will prevent script from displaying information to console.
        argparser.add_argument('--quiet', help = 'run in quiet mode (flag)', action = 'store_true', default = None)

        # Option for setting the output verbosity level.
        argparser.add_argument('--verbosity', help = 'increase output verbosity', action = 'count', default = None)

        # Option flag indicating that the script should dump the runlog to logger,
        # when the processing is done.
        argparser.add_argument('--runlog-dump', help = 'dump runlog when done processing (flag)', action = 'store_true', default = None)

        # Option flag indicating that the script should dump the persistent state to logger,
        # when the processing is done.
        argparser.add_argument('--pstate-dump', help = 'dump persistent state when done processing (flag)', action = 'store_true', default = None)

        # Option for overriding the name of the component.
        argparser.add_argument('--name', help = 'name of the component')

        # Option for setting the desired action.
        argparser.add_argument('--action', help = 'choose which action should be performed', choices = self._utils_detect_actions())

        # Option for setting the desired operation.
        argparser.add_argument('--input', help = 'file to be used as source file in action')

        # Option for setting the result limit.
        argparser.add_argument('--limit', help = 'apply given limit to the result', type = int)

        # Option for overriding the process UID.
        argparser.add_argument('--user', help = 'process UID or user name')

        # Option for overriding the process GID.
        argparser.add_argument('--group', help = 'process GID or group name')

        # Option for overriding the name of the configuration file.
        argparser.add_argument('--config-file', help = 'name of the config file')

        # Option for overriding the name of the configuration directory.
        argparser.add_argument('--config-dir', help = 'name of the config directory')

        # Option for overriding the name of the log file.
        argparser.add_argument('--log-file', help = 'name of the log file')

        # Option for setting the level of logging information.
        argparser.add_argument('--log-level', help = 'set logging level', choices = ['debug', 'info', 'warning', 'error', 'critical'])

        # Option for overriding the name of the persistent state file.
        argparser.add_argument('--pstate-file', help = 'name of the persistent state file')

        # Option for overriding the name of the runlog directory.
        argparser.add_argument('--runlog-dir', help = 'name of the runlog directory')

        #argparser.add_argument('args', help = 'optional additional arguments', nargs='*')

        return argparser

    def _parse_cli_arguments(self):
        """
        Load and initialize script configuration received from command line.

        Use the configured ArgumentParser object for parsing CLI arguments.
        """
        # Finally actually process command line arguments.
        cli_args = vars(self.argparser.parse_args())

        # Check for debug flag
        if cli_args.get(self.CONFIG_DEBUG, False):
            global FLAG_DEBUG
            FLAG_DEBUG = True
            self.dbgout("[STATUS] FLAG_DEBUG set to 'True' via command line argument")

        self.dbgout("[STATUS] Parsed command line arguments: '{}'".format(' '.join(sys.argv)))
        return cli_args

    def _init_name(self, **kwargs):
        """
        Initialize script name.
        """
        cli_name = self._config_cli.get(self.CONFIG_NAME)
        if cli_name:
            if re.fullmatch('^[_a-zA-Z][-_a-zA-Z0-9.]*$', cli_name):
                self.dbgout("[STATUS] Using custom script name '{}".format(cli_name))
                return cli_name
            else:
                raise ZenAppException("Invalid script name '{}'. Valid pattern is '^[a-zA-Z][-_a-zA-Z0-9]*$'".format(cli_name))
        elif 'name' in kwargs:
            if re.fullmatch('^[_a-zA-Z][-_a-zA-Z0-9.]*$', kwargs['name']):
                self.dbgout("[STATUS] Using custom script name '{}".format(kwargs['name']))
                return kwargs['name']
            else:
                raise ZenAppException("Invalid script name '{}'. Valid pattern is '^[a-zA-Z][-_a-zA-Z0-9]*$'".format(cli_name))
        else:
            scr_name = os.path.basename(sys.argv[0])
            self.dbgout("[STATUS] Using default script name '{}".format(scr_name))
            return scr_name

    def _init_paths(self, **kwargs):
        """
        Initialize various script paths.
        """
        return {
            self.PATH_BIN: kwargs.get('path_bin', "/usr/local/bin"),  # Application executable directory.
            self.PATH_CFG: kwargs.get('path_cfg', "/etc"),            # Configuration directory.
            self.PATH_LOG: kwargs.get('path_log', "/var/log"),        # Log directory.
            self.PATH_RUN: kwargs.get('path_run', "/var/run"),        # Runlog directory.
            self.PATH_TMP: kwargs.get('path_tmp', "/var/tmp"),        # Temporary file directory.
        }

    def _init_runlog(self, **kwargs):
        """
        Initialize script runlog.
        """
        runlog = {
            self.RLKEY_NAME:   self.name,
            self.RLKEY_PID:    os.getpid(),
            self.RLKEY_ARGV:   sys.argv,
            self.RLKEY_TS:     time.time(),
            self.RLKEY_RESULT: self.RESULT_SUCCESS,
            self.RLKEY_ERRORS: [],
            self.RLKEY_TMARKS: [],
        }
        # Timestamp as one string (usefull for generating sortable file names).
        runlog[self.RLKEY_TSFSF] = time.strftime('%Y%m%d%H%M',  time.localtime(runlog[self.RLKEY_TS]))
        # Timestamp as readable string.
        runlog[self.RLKEY_TSSTR] = time.strftime('%Y-%m-%d %X', time.localtime(runlog[self.RLKEY_TS]))

        return runlog

    def _init_config(self, **kwargs):
        """
        Initialize script configurations to default values.
        """
        cfgs = (
            (self.CONFIG_DEBUG,       False),
            (self.CONFIG_QUIET,       False),
            (self.CONFIG_VERBOSITY,   0),
            (self.CONFIG_RUNLOG_DUMP, False),
            (self.CONFIG_PSTATE_DUMP, False),
            (self.CONFIG_ACTION,      None),
            (self.CONFIG_INPUT,       None),
            (self.CONFIG_LIMIT,       None),
            (self.CONFIG_USER,        None),
            (self.CONFIG_GROUP,       None),
            (self.CONFIG_CFG_FILE,    os.path.join(self.paths.get(self.PATH_CFG), "{}.conf".format(self.name))),
            (self.CONFIG_CFG_DIR,     os.path.join(self.paths.get(self.PATH_CFG), "{}".format(self.name))),
            (self.CONFIG_LOG_FILE,    os.path.join(self.paths.get(self.PATH_LOG), "{}.log".format(self.name))),
            (self.CONFIG_LOG_LEVEL,   'info'),
            (self.CONFIG_PSTATE_FILE, os.path.join(self.paths.get(self.PATH_RUN), "{}.pstate".format(self.name))),
            (self.CONFIG_RUNLOG_DIR,  os.path.join(self.paths.get(self.PATH_RUN), "{}".format(self.name))),
        )
        config = {}
        for c in cfgs:
            config[c[0]] = kwargs.get('default_' + c[0], c[1])
        return config

    def _init_custom(self, config, argparser, **kwargs):
        """
        Perform subinitializations on default configurations and argument parser.
        """
        pass

    #---------------------------------------------------------------------------
    # Template method hooks (intended to be used by subclassess)
    #---------------------------------------------------------------------------

    def _sub_runlog_analyze(self, runlog, analysis):
        """
        Analyze given runlog (hook for subclasses).
        """
        return analysis

    def _sub_runlog_format_analysis(self, analysis):
        """
        Format given runlog analysis (hook for subclasses).
        """
        pass

    def _sub_runlogs_evaluate(self, runlogs, evaluation):
        """
        Evaluate given runlog analyses (hook for subclasses).
        """
        return evaluation

    def _sub_runlogs_format_evaluation(self, evaluation):
        """
        Format given runlogs evaluation (hook for subclasses).
        """
        pass

    #---------------------------------------------------------------------------
    # Helpers and shortcut methods
    #---------------------------------------------------------------------------

    def get_fn_runlog(self):
        """
        Return the name of the runlog file for current process.
        """
        return os.path.join(self.c(self.CONFIG_RUNLOG_DIR), "{}.runlog".format(self.runlog[self.RLKEY_TSFSF]))

    def get_fn_pstate(self):
        """
        Return the name of the persistent state file for current process.
        """
        return self.c(self.CONFIG_PSTATE_FILE)

    def c(self, key, default = None):
        """
        Shortcut method: Get given configuration value.
        """
        if default is None:
            return self.config.get(key)
        else:
            return self.config.get(key, default)

    def cc(self, key, default = None):
        """
        Shortcut method: Get given CORE configuration value.
        """
        if default is None:
            return self.config[self.CORE].get(key)
        else:
            return self.config[self.CORE].get(key, default)

    def p(self, string, level = 0):
        """
        Shortcut method: Print given string.
        """
        if not self.c(self.CONFIG_QUIET) and self.c(self.CONFIG_VERBOSITY) >= level:
            print(string)

    def error(self, error, rc = None, tb = None):
        """
        Method for registering error, that occured during script run.
        """
        self.rc = rc if rc is not None else self.RC_FAILURE

        errstr = "{}".format(error)
        self.logger.error(errstr)

        if tb:
            tbexc = traceback.format_tb(tb)
            self.logger.error("\n" + "".join(tbexc))

        self.runlog[self.RLKEY_ERRORS].append(errstr)
        self.runlog[self.RLKEY_RESULT] = self.RESULT_FAILURE
        self.runlog[self.RLKEY_RC] = self.rc

    def dbgout(self, message):
        """
        Routine for printing additional debug messages.

        The given message is printed only in case the global 'FLAG_DEBUG' flag is
        set to True.
        """
        if FLAG_DEBUG:
            print("*DBG* {} {}".format(time.strftime('%Y-%m-%d %X', time.localtime()), message), file=sys.stderr)

    def errout(self, exception):
        """
        Routine for printing error messages.
        """
        print("*ERR* {} {}".format(time.strftime('%Y-%m-%d %X', time.localtime()), exception), file=sys.stderr)
        sys.exit(self.RC_FAILURE)

    #---------------------------------------------------------------------------
    # Internal utilities
    #---------------------------------------------------------------------------

    def _utils_detect_actions(self):
        """
        Returns the sorted list of all available actions current script is capable
        of performing. The detection algorithm is based on string analysis of all
        available methods. Any method starting with string 'cbk_action_' will
        be appended to the list, lowercased and with '_' characters replaced with '-'.
        """
        ptrn = re.compile(self.PTRN_ACTION_CBK)
        attrs = sorted(dir(self))
        result = []
        for a in attrs:
            if not callable(getattr(self, a)):
                continue
            match = ptrn.match(a)
            if match:
                result.append(a.replace(self.PTRN_ACTION_CBK,'').replace('_','-').lower())
        return result

    #---------------------------------------------------------------------------
    # CONFIGURATION RELATED METHODS (SETUP CONFIGURATION SUBSTAGE)
    #---------------------------------------------------------------------------

    def _configure_cli(self):
        """
        Load and initialize script configuration received from command line.

        Use the configured ArgumentParser object for parsing CLI arguments.
        """
        # IMPORTANT! Immediatelly rewrite the default value for configuration file
        # and configuration directory names, if the value was received as command
        # line argument.
        if self._config_cli[self.CONFIG_CFG_FILE] is not None:
            self.dbgout("[STATUS] Config file option override from '{}' to '{}'".format(self.config[self.CONFIG_CFG_FILE], self._config_cli[self.CONFIG_CFG_FILE]))
            self.config[self.CONFIG_CFG_FILE] = self._config_cli[self.CONFIG_CFG_FILE]
        if self._config_cli[self.CONFIG_CFG_DIR] is not None:
            self.dbgout("[STATUS] Config directory option override from '{}' to '{}'".format(self.config[self.CONFIG_CFG_DIR], self._config_cli[self.CONFIG_CFG_DIR]))
            self.config[self.CONFIG_CFG_DIR] = self._config_cli[self.CONFIG_CFG_DIR]

        return self._config_cli

    def _configure_file(self):
        """
        Load and initialize script configuration received from configuration file.
        """
        try:
            self._config_file = pyzenkit.jsonconf.config_load(self.c(self.CONFIG_CFG_FILE))
            self.dbgout("[STATUS] Loaded configuration file '{}'".format(self.c(self.CONFIG_CFG_FILE)))
        except FileNotFoundError as exc:
            raise ZenAppSetupException("Configuration file '{}' does not exist".format(self.c(self.CONFIG_CFG_FILE)))

    def _configure_dir(self):
        """
        Load and initialize script configuration received from configuration directory.
        """
        try:
            self._config_dir = pyzenkit.jsonconf.config_load_dir(self.c(self.CONFIG_CFG_DIR))
            self.dbgout("[STATUS] Loaded configuration directory '{}'".format(self.c(self.CONFIG_CFG_DIR)))
        except FileNotFoundError as exc:
            raise ZenAppSetupException("Configuration directory '{}' does not exist".format(self.c(self.CONFIG_CFG_DIR)))

    def _configure_merge(self):
        """
        Configure script and produce final configuration by merging all available
        configuration values in appropriate order ('default' <= 'dir' <= 'file' <= 'cli').
        """
        # Merge configuration directory values with current config, if possible.
        if self.c(self.CONFIG_CFG_DIR, False):
            self.dbgout("[STATUS] Merging global config with DIRECTORY configurations")
            self.config.update((k, v) for k, v in self._config_dir.items() if v is not None)

        # Merge configuration file values with current config, if possible.
        if self.c(self.CONFIG_CFG_FILE, False):
            self.dbgout("[STATUS] Merging global config with FILE configurations")
            self.config.update((k, v) for k, v in self._config_file.items() if v is not None)

        # Merge command line values with current config, if possible.
        self.dbgout("[STATUS] Merging global config with CLI configurations")
        self.config.update((k, v) for k, v in self._config_cli.items() if v is not None)

    def _configure_postprocess(self):
        """
        Perform configuration postprocessing.
        """
        self.config[self.CORE] = {}

        cc = {}
        cc[self.CORE_LOGGING_TOCONS] = True
        cc[self.CORE_LOGGING_TOFILE] = True
        cc[self.CORE_LOGGING_LEVEL]  = self.c(self.CONFIG_LOG_LEVEL).upper()
        cc[self.CORE_LOGGING_LEVELF] = cc[self.CORE_LOGGING_LEVEL]
        cc[self.CORE_LOGGING_LEVELC] = cc[self.CORE_LOGGING_LEVEL]
        self.config[self.CORE][self.CORE_LOGGING] = cc

        cc = {}
        cc[self.CORE_PSTATE_SAVE] = True
        self.config[self.CORE][self.CORE_PSTATE] = cc

        cc = {}
        cc[self.CORE_RUNLOG_SAVE] = True
        self.config[self.CORE][self.CORE_RUNLOG] = cc

        if self.config[self.CONFIG_USER]:
            u = self.config[self.CONFIG_USER]
            res = None
            if not res:
                try:
                    res = pwd.getpwnam(u)
                    self.config[self.CONFIG_USER] = [res[0], res[2]]
                except:
                    pass
            if not res:
                try:
                    res = pwd.getpwuid(int(u))
                    self.config[self.CONFIG_USER] = [res[0], res[2]]
                except:
                    pass
            if not res:
                raise ZenAppSetupException("Unknown user account '{}'".format(u))

        if self.config[self.CONFIG_GROUP]:
            g = self.config[self.CONFIG_GROUP]
            res = None
            if not res:
                try:
                    res = grp.getgrnam(g)
                    self.config[self.CONFIG_GROUP] = [res[0], res[2]]
                except:
                    pass
            if not res:
                try:
                    res = grp.getgrgid(int(g))
                    self.config[self.CONFIG_GROUP] = [res[0], res[2]]
                except:
                    pass
            if not res:
                raise ZenAppSetupException("Unknown group account '{}'".format(g))

    def _configure_check(self):
        """
        TODO: Implement config checking mechanism.
        """
        pass

    #---------------------------------------------------------------------------
    # "SETUP" STAGE RELATED METHODS
    #---------------------------------------------------------------------------

    def _stage_setup_configuration(self):
        """
        Setup script configurations.
        """
        # Load configurations from command line.
        self._configure_cli()

        # Load configurations from config file, if the appropriate feature is enabled.
        if self.c(self.CONFIG_CFG_FILE, False):
            self._configure_file()

        # Load configurations from config directory, if the appropriate feature is enabled.
        if self.c(self.CONFIG_CFG_DIR, False):
            self._configure_dir()

        # Merge all available configurations together with default.
        self._configure_merge()

        # Postprocess loaded configurations
        self._configure_postprocess()

        # Check all loaded configurations.
        self._configure_check()

    def _stage_setup_privileges(self):
        """
        Adjust the script privileges according to the configration.
        """
        g = self.c(self.CONFIG_GROUP, None)
        if g and g[1] != os.getgid():
            cg = grp.getgrgid(os.getgid())
            self.dbgout("[STATUS] Dropping group privileges from '{}':'{}' to '{}':'{}'".format(cg[0], cg[2], g[0], g[1]))
            os.setgid(g[1])
        u = self.c(self.CONFIG_USER, None)
        if u and u[1] != os.getuid():
            cu = pwd.getpwuid(os.getuid())
            self.dbgout("[STATUS] Dropping user privileges from '{}':'{}' to '{}':'{}'".format(cu[0], cu[2], u[0], u[1]))
            os.setuid(u[1])

    def _stage_setup_logging(self):
        """
        Setup terminal and file logging facilities.
        """
        cc = self.cc(self.CORE_LOGGING, {})
        if cc[self.CORE_LOGGING_TOCONS] or cc[self.CORE_LOGGING_TOFILE]:
            # [PUBLIC] Register the logger object as internal attribute.
            self.logger = logging.getLogger('zenlogger')
            self.logger.setLevel(cc[self.CORE_LOGGING_LEVEL])

            # Setup console logging
            if cc[self.CORE_LOGGING_TOCONS]:
                logging_level = getattr(logging, cc[self.CORE_LOGGING_LEVELC], None)
                if not isinstance(logging_level, int):
                    raise ValueError("Invalid log level: '{}'".format(cc[self.CORE_LOGGING_LEVELC]))

                # Initialize console logging handler.
                fm1 = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
                ch1 = logging.StreamHandler()
                ch1.setLevel(logging_level)
                ch1.setFormatter(fm1)
                self.logger.addHandler(ch1)
                self.dbgout("[STATUS] Logging to console with level threshold '{}'".format(cc[self.CORE_LOGGING_LEVELC]))

            # Setup file logging
            if cc[self.CORE_LOGGING_TOFILE]:
                logging_level = getattr(logging, cc[self.CORE_LOGGING_LEVELF], None)
                if not isinstance(logging_level, int):
                    raise ValueError("Invalid log level: '{}'".format(cc[self.CORE_LOGGING_LEVELF]))

                lfn = self.c(self.CONFIG_LOG_FILE)
                fm2 = logging.Formatter('%(asctime)s {} [%(process)d] %(levelname)s: %(message)s'.format(self.name))
                #ch2 = logging.FileHandler(lfn)
                ch2 = logging.handlers.WatchedFileHandler(lfn)
                ch2.setLevel(logging_level)
                ch2.setFormatter(fm2)
                self.logger.addHandler(ch2)
                self.dbgout("[STATUS] Logging to log file '{}' with level threshold '{}'".format(lfn, cc[self.CORE_LOGGING_LEVELF]))

    def _stage_setup_pstate(self):
        """
        Setup persistent state.

        Load persistent script state from external file (JSON).
        """
        if os.path.isfile(self.c(self.CONFIG_PSTATE_FILE)):
            self.dbgout("[STATUS] Loading persistent state from file '{}'".format(self.c(self.CONFIG_PSTATE_FILE)))
            self.pstate = self.json_load(self.c(self.CONFIG_PSTATE_FILE))
        else:
            self.dbgout("[STATUS] Setting default persistent state".format(self.c(self.CONFIG_PSTATE_FILE)))
            self.pstate =  {}

    def _stage_setup_custom(self):
        """
        Custom setup.
        """
        pass

    def _stage_setup_dump(self):
        """
        Dump script setup information.

        This method will display information about script system paths, configuration
        loaded from CLI arguments or config file, final merged configuration.
        """
        self.logger.debug("Script name detected as '{}'".format(self.name))
        self.logger.debug("System paths >>>\n{}".format(self.json_dump(self.paths, default=_json_default)))
        if self.c(self.CONFIG_CFG_DIR, False):
            self.logger.debug("Loaded DIRECTORY configurations >>>\n{}".format(self.json_dump(self._config_dir, default=_json_default)))
        if self.c(self.CONFIG_CFG_FILE, False):
            self.logger.debug("Loaded FILE configurations >>>\n{}".format(self.json_dump(self._config_file, default=_json_default)))
        self.logger.debug("Loaded CLI configurations >>>\n{}".format(self.json_dump(self._config_cli, default=_json_default)))
        self.logger.debug("Script configurations >>>\n{}".format(self.json_dump(self.config, default=_json_default)))
        self.logger.debug("Loaded persistent state >>>\n{}".format(self.json_dump(self.pstate, default=_json_default)))

    #---------------------------------------------------------------------------
    # "TEARDOWN" STAGE RELATED METHODS
    #---------------------------------------------------------------------------

    def _stage_teardown_custom(self):
        """
        Custom teardown.
        """
        pass

    def _stage_teardown_pstate(self):
        """
        Teardown state.

        Save persistent script state to external file (JSON).
        """
        if self.cc(self.CORE_PSTATE, {}).get(self.CORE_PSTATE_SAVE):
            self.pstate_save(self.pstate)
        if self.c(self.CONFIG_PSTATE_DUMP):
            self.pstate_dump(self.pstate)

    def _stage_teardown_runlog(self):
        """
        Teardown runlog.

        Save runlog to external file (JSON) and dump runlog to log.
        """
        if self.cc(self.CORE_RUNLOG, {}).get(self.CORE_RUNLOG_SAVE):
            self.runlog_save(self.runlog)
        if self.c(self.CONFIG_RUNLOG_DUMP):
            self.runlog_dump(self.runlog)

    #---------------------------------------------------------------------------
    # MAIN STAGE METHODS
    #---------------------------------------------------------------------------

    def stage_setup(self):
        """
        Script lifecycle stage: SETUP
        """
        self.time_mark('stage_setup_start', 'Start of the setup stage')

        try:
            # Setup configurations.
            self._stage_setup_configuration()

            # Setup script privileges
            self._stage_setup_privileges()

            # Setup logging, if the appropriate feature is enabled.
            if self.c(self.CONFIG_LOG_FILE):
                self._stage_setup_logging()

            # Setup persistent state, if the appropriate feature is enabled.
            if self.c(self.CONFIG_PSTATE_FILE):
                self._stage_setup_pstate()

            # Perform custom setup operations.
            self._stage_setup_custom()

            # Finally dump information about the script setup.
            self._stage_setup_dump()

        except ZenAppSetupException as exc:
            # At this point the logging facilities are not yet configured, so we must
            # use other means of diplaying the error to the user. Use custom function
            # to suppres the backtrace print for known issues and errors.
            self.errout(exc)

        self.time_mark('stage_setup_stop', 'End of the setup stage')

    def stage_action(self):
        """
        Script lifecycle stage: ACTION

        Perform some quick action. Following method will call appropriate
        callback method to service the selected action.
        """
        self.time_mark('stage_action_start', 'Start of the action stage')

        try:
            # Determine, which operation to execute.
            self.runlog[self.CONFIG_ACTION] = self.c(self.CONFIG_ACTION)
            opname = self.c(self.CONFIG_ACTION)
            opcbkname = self.PTRN_ACTION_CBK + opname.lower().replace('-','_')

            cbk = getattr(self, opcbkname, None)
            if cbk:
                cbk()
            else:
                raise ZenAppProcessException("Invalid action '{}', callback '{}' does not exist".format(opname, opcbkname))

        except subprocess.CalledProcessError as err:
            self.error("System command error: {}".format(err))

        except ZenAppProcessException as exc:
            self.error("ZenAppProcessException: {}".format(exc))

        except ZenAppException as exc:
            self.error("ZenAppException: {}".format(exc))

        self.time_mark('stage_action_stop', 'End of the action stage')

    def stage_process(self):
        """
        Script lifecycle stage: PROCESSING

        Perform some real work (finally). Following method will call appropriate
        callback method operation to service the selected operation.
        """
        #self.time_mark('stage_process_start', 'Start of the processing stage')

        raise Exception("stage_process() method must be implemented in subclass")

        #self.time_mark('stage_process_stop', 'End of the processing stage')

    def stage_evaluate(self):
        """
        Script lifecycle stage: EVALUATE

        Perform script runlog evaluation.
        """
        self.time_mark('stage_evaluate_start', 'Start of the evaluation stage')

        try:
            pass

        except ZenAppEvaluateException as exc:
            self.error("ZenAppEvaluateException: {}".format(exc))

        self.time_mark('stage_evaluate_stop', 'End of the evaluation stage')

    def stage_teardown(self):
        """
        Script lifecycle stage: TEARDOWN

        Main teardown routine. This method will call the sequence of all configured
        teardown routines.
        """
        try:
            # Perform custom teardown operations.
            self._stage_teardown_custom()

            # Teardown persistent state, if the appropriate feature is enabled and
            # also we are running in regular mode.
            if self.c(self.CONFIG_PSTATE_FILE):
                self._stage_teardown_pstate()

            # Teardown runlog.
            if self.c(self.CONFIG_RUNLOG_DIR):
                self._stage_teardown_runlog()

        except ZenAppTeardownException as exc:
            self.error("ZenAppTeardownException: {}".format(exc))

    #---------------------------------------------------------------------------
    # MAIN RUN METHODS
    #---------------------------------------------------------------------------

    def run(self):
        """
        Standalone script mode - Main processing method.

        Run as standalone script, performs all stages of script object life cycle:
            1. setup stage
            2.1 action processing stage
            2.2.1 script processing stage
            2.2.2 script evaluation stage
            2.2.3 script teardown stage
        """
        self.stage_setup()

        if self.c(self.CONFIG_ACTION):
            self.stage_action()
        else:
            self.stage_process()
            self.stage_evaluate()
            self.stage_teardown()

        self.dbgout("[STATUS] Exiting with return code '{}'".format(self.rc))
        sys.exit(self.rc)

    def plugin(self):
        """
        Plugin mode - Main processing method.

        This method allows the object to be used as plugin within larger framework.
        Only the necessary setup is performed.
        """
        self.stage_setup()

    #---------------------------------------------------------------------------
    # BUILT-IN ACTION CALLBACK METHODS
    #---------------------------------------------------------------------------

    def cbk_action_config_view(self):
        """
        Parse and view script configurations.
        """
        print("Script configurations:")
        tree = pydgets.widgets.TreeWidget()
        tree.display(self.config)

    def cbk_action_runlog_dump(self):
        """
        Dump given script runlog.
        """
        rld = self.c(self.CONFIG_RUNLOG_DIR)
        input_file = self.c(self.CONFIG_INPUT, False)
        if not input_file:
            rlfn = os.path.join(rld, '*.runlog')
            runlog_files = sorted(glob.glob(rlfn), reverse = True)
            if len(runlog_files):
                input_file = runlog_files.pop(0)
            else:
                print("There are no runlog files")
                return

        print("Viewing script runlog '{}':".format(input_file))
        runlog = self.json_load(input_file)
        print("")
        tree = pydgets.widgets.TreeWidget()
        tree.display(runlog)

    def cbk_action_runlog_view(self):
        """
        View details of given script runlog.
        """
        rld = self.c(self.CONFIG_RUNLOG_DIR)
        input_file = self.c(self.CONFIG_INPUT, False)
        if not input_file:
            rlfn = os.path.join(rld, '*.runlog')
            runlog_files = sorted(glob.glob(rlfn), reverse = True)
            if len(runlog_files):
                input_file = runlog_files.pop(0)
            else:
                print("There are no runlog files")
                return

        print("Viewing script runlog '{}':".format(input_file))
        runlog = self.json_load(input_file)
        print("")
        analysis = self.runlog_analyze(runlog)

        self.runlog_format_analysis(analysis)

    def cbk_action_runlogs_list(self):
        """
        View the list of all available script runlogs.
        """
        rld = self.c(self.CONFIG_RUNLOG_DIR)
        limit = self.c(self.CONFIG_LIMIT)
        (runlog_files, rlcount) = self.runlogs_list(reverse = True, limit = limit)
        runlogtree = {}
        runlogtree[rld] = []
        for rlf in runlog_files:
            runlogtree[rld].append(rlf)

        print("Listing script runlogs in directory '{}':".format(rld))
        print("  Runlog(s) found: {:,d}".format(rlcount))
        if limit:
            print("  Result limit: {:,d}".format(limit))
        if len(runlogtree[rld]):
            print("")
            tree = pydgets.widgets.TreeWidget()
            tree.display(runlogtree)

    def cbk_action_runlogs_dump(self):
        """
        View the list of all available script runlogs.
        """
        rld = self.c(self.CONFIG_RUNLOG_DIR)
        limit = self.c(self.CONFIG_LIMIT)
        (runlog_files, rlcount) = self.runlogs_list(reverse = True, limit = limit)
        runlogs = []
        for rlf in runlog_files:
            runlogs.append((rlf, self.json_load(rlf)))

        print("Dumping script runlog(s) in directory '{}':".format(rld))
        print("  Runlog(s) found: {:,d}".format(rlcount))
        if limit:
            print("  Result limit: {:,d}".format(limit))
        if len(runlogs):
            print("")
            tree = pydgets.widgets.TreeWidget()
            for rl in runlogs:
                print("Runlog '{}':".format(rl[0]))
                tree.display(rl[1])

    def cbk_action_runlogs_evaluate(self):
        """
        Evaluate previous script runlogs.
        """
        rld = self.c(self.CONFIG_RUNLOG_DIR)
        limit = self.c(self.CONFIG_LIMIT)
        (runlog_files, rlcount) = self.runlogs_list(reverse = True, limit = limit)
        runlogs = []
        for rlf in runlog_files:
            runlogs.append(self.json_load(rlf))

        print("Evaluating script runlogs in directory '{}':".format(rld))
        print("  Runlog(s) found: {:,d}".format(rlcount))
        if limit:
            print("  Result limit: {:,d}".format(limit))
        if len(runlogs):
            print("")
            evaluation = self.runlogs_evaluate(runlogs)
            self.runlogs_format_evaluation(evaluation)

    #---------------------------------------------------------------------------
    # ACTION HELPERS
    #---------------------------------------------------------------------------

    def runlog_analyze(self, runlog):
        """
        Analyze given runlog.
        """
        ct = int(time.time())
        tm_tmp = {}
        analysis = {self.RLANKEY_DURPRE: 0, self.RLANKEY_DURPROC: 0, self.RLANKEY_DURPOST: 0, self.RLANKEY_DURATIONS: {}}
        analysis[self.RLANKEY_RUNLOG]  = runlog
        analysis[self.RLANKEY_LABEL]   = runlog[self.RLKEY_TSSTR]
        analysis[self.RLANKEY_AGE]     = ct - runlog[self.RLKEY_TS]
        analysis[self.RLANKEY_RESULT]  = runlog[self.RLKEY_RESULT]
        analysis[self.RLANKEY_COMMAND] = runlog.get(self.RLANKEY_COMMAND, runlog.get('operation', 'unknown'))
        # Calculate script processing duration
        analysis[self.RLANKEY_DURRUN]  = runlog[self.RLKEY_TMARKS][-1]['time'] - runlog[self.RLKEY_TMARKS][0]['time']

        # Calculate separate durations for all stages
        for tm in runlog[self.RLKEY_TMARKS]:
            ptrna = re.compile('^(.*)_start$')
            ptrnb = re.compile('^(.*)_stop$')
            m = ptrna.match(tm['ident'])
            if m:
                mg = m.group(1)
                tm_tmp[mg] = tm['time']
                continue
            m = ptrnb.match(tm['ident'])
            if m:
                mg = m.group(1)
                analysis[self.RLANKEY_DURATIONS][mg] = tm['time'] - tm_tmp[mg]
                if mg in ('stage_configure', 'stage_check', 'stage_setup'):
                    analysis[self.RLANKEY_DURPRE] += analysis[self.RLANKEY_DURATIONS][mg]
                elif mg in ('stage_process'):
                    analysis[self.RLANKEY_DURPROC] += analysis[self.RLANKEY_DURATIONS][mg]
                elif mg in ('stage_evaluate', 'stage_teardown'):
                    analysis[self.RLANKEY_DURPOST] += analysis[self.RLANKEY_DURATIONS][mg]
                continue

        analysis[self.RLANKEY_EFFECTIVITY] = ((analysis[self.RLANKEY_DURPROC]/analysis[self.RLANKEY_DURRUN])*100)
        return self._sub_runlog_analyze(runlog, analysis)

    def runlog_format_analysis(self, analysis):
        """
        Format given runlog analysis.
        """
        tablew = pydgets.widgets.TableWidget()
        tcols = [
            { 'label': 'Statistics', 'data_formating': '{:s}', 'align': '<' },
            { 'label': 'Value',      'data_formating': '{:s}', 'align': '>' },
        ]
        tbody = [
                ['Label:',   analysis[self.RLANKEY_LABEL]],
                ['Age:',     str(datetime.timedelta(seconds=int(analysis[self.RLANKEY_AGE])))],
                ['Command:', analysis[self.RLANKEY_COMMAND]],
                ['Result:',  analysis[self.RLANKEY_RESULT]],
            ]
        tablew.display(tbody, columns = tcols, enumerate = False, header = False)

        #treew = pydgets.widgets.TreeWidget()
        #treew.display(analysis)

        self._sub_runlog_format_analysis(analysis)

    def runlogs_evaluate(self, runlogs):
        """
        Evaluate given runlogs.
        """
        evaluation = {self.RLEVKEY_ANALYSES: []}
        for rl in runlogs:
            rslt = self.runlog_analyze(rl)
            evaluation[self.RLEVKEY_ANALYSES].append(rslt)
        return self._sub_runlogs_evaluate(runlogs, evaluation)

    def runlogs_format_evaluation(self, evaluation):
        """
        Format runlog evaluation.
        """
        table_columns = [
                { 'label': 'Date' },
                { 'label': 'Age',     'data_formating': '{}',      'align': '>' },
                { 'label': 'Runtime', 'data_formating': '{}',      'align': '>' },
                { 'label': 'Process', 'data_formating': '{}',      'align': '>' },
                { 'label': 'E [%]',   'data_formating': '{:6.2f}', 'align': '>' },
                { 'label': 'Errors',  'data_formating': '{:,d}',   'align': '>' },
                { 'label': 'Command', 'data_formating': '{}',      'align': '>' },
                { 'label': 'Result',  'data_formating': '{}',      'align': '>' },
            ]
        table_data = []
        for an in evaluation[self.RLEVKEY_ANALYSES]:
            table_data.append(
                [
                    an[self.RLANKEY_LABEL],
                    str(datetime.timedelta(seconds=int(an[self.RLANKEY_AGE]))),
                    str(datetime.timedelta(seconds=int(an[self.RLANKEY_DURRUN]))),
                    str(datetime.timedelta(seconds=int(an[self.RLANKEY_DURPROC]))),
                    an[self.RLANKEY_EFFECTIVITY],
                    len(an[self.RLANKEY_RUNLOG][self.RLKEY_ERRORS]),
                    an[self.RLANKEY_COMMAND],
                    an[self.RLANKEY_RESULT],
                ]
            )
        print("General script processing statistics:")
        tablew = pydgets.widgets.TableWidget()
        tablew.display(table_data, columns = table_columns)

        self._sub_runlogs_format_evaluation(evaluation)

    def runlog_dump(self, runlog, **kwargs):
        """
        Dump runlog.

        Dump script runlog to terminal (JSON).
        """
        # Dump current script runlog.
        #self.logger.debug("Script runlog >>>\n{}".format(json.dumps(runlog, sort_keys=True, indent=4)))
        print("Script runlog >>>\n{}".format(self.json_dump(runlog, default=_json_default)))

    def runlog_save(self, runlog, **kwargs):
        """
        Save runlog.

        Save script runlog to external file (JSON).
        """
        # Attempt to create script runlog directory.
        if not os.path.isdir(self.c(self.CONFIG_RUNLOG_DIR)):
            self.logger.info("Creating runlog directory '{}'".format(self.c(self.CONFIG_RUNLOG_DIR)))
            os.makedirs(self.c(self.CONFIG_RUNLOG_DIR))
        rlfn = self.get_fn_runlog()
        self.dbgout("[STATUS] Saving script runlog to file '{}'".format(rlfn))
        self.json_save(rlfn, runlog)
        self.logger.info("Script runlog saved to file '{}'".format(rlfn))

    def runlogs_list(self, **kwargs):
        """
        List all available runlogs.
        """
        reverse = kwargs.get('reverse', False)
        limit = kwargs.get('limit', None)
        rlfn = os.path.join(self.c(self.CONFIG_RUNLOG_DIR), '*.runlog')
        rllist = sorted(glob.glob(rlfn), reverse = reverse)
        rlcount = len(rllist)
        if limit:
            return (rllist[:limit], rlcount)
        else:
            return (rllist, rlcount)

    def pstate_dump(self, state, **kwargs):
        """
        Dump persistent state.

        Dump script persistent state to terminal (JSON).
        """
        # Dump current script state.
        #self.logger.debug("Script state >>>\n{}".format(json.dumps(state, sort_keys=True, indent=4)))
        print("Script state >>>\n{}".format(self.json_dump(state, default=_json_default)))

    def pstate_save(self, state, **kwargs):
        """
        Save persistent state.

        Save script persistent state to external file (JSON).
        """
        sfn = self.get_fn_pstate()
        self.dbgout("[STATUS] Saving script persistent state to file '{}'".format(sfn))
        self.json_save(sfn, state)
        self.logger.info("Script persistent state saved to file '{}'".format(sfn))

    #---------------------------------------------------------------------------
    # TOOLS
    #---------------------------------------------------------------------------

    def execute_command(self, command, can_fail=False):
        """
        Execute given shell command
        """
        self.logger.info("Executing system command >>>\n{}".format(command))
        #result = subprocess.run(command)
        result = None
        if can_fail:
            result = subprocess.call(command, shell=True)
        else:
            result = subprocess.check_output(command, shell=True)
        self.logger.debug("System command result >>>\n{}".format(pprint.pformat(result,indent=4)))
        return result

    def time_mark(self, ident, descr):
        """
        Mark current time with additional identifiers and descriptions
        """
        mark = {
                'ident': ident,
                'descr': descr,
                'time':  time.time()
            }
        self.runlog[self.RLKEY_TMARKS].append(mark)
        return mark

    @staticmethod
    def json_dump(data, **kwargs):
        """
        Dump given data structure into JSON string.
        """
        return pyzenkit.jsonconf.json_dump(data, **kwargs)

    @staticmethod
    def json_save(json_file, data, **kwargs):
        """
        Save given data structure into given JSON file.
        """
        return pyzenkit.jsonconf.json_save(json_file, data, **kwargs)

    @staticmethod
    def json_load(json_file, **kwargs):
        """
        Load data structure from given json file.
        """
        return pyzenkit.jsonconf.json_load(json_file, **kwargs)

    def format_progress_bar(self, percent, done, barLen = 50):
        """
        Format progress bar from given values
        """
        progress = ""
        for i in range(barLen):
            if i < int(barLen * percent):
                progress += "="
            else:
                progress += " "
        return " [%s] %.2f%%" % (progress, percent * 100)

    def draw_progress_bar(self, percent, done, barLen = 50):
        """
        Draw progress bar on standard output terminal
        """
        sys.stdout.write("\r")
        sys.stdout.write(self.format_progress_bar(percent, done, barLen))
        sys.stdout.flush()

class _DemoBaseApp(BaseApp):
    """
    Minimalistic class for demonstration purposes.
    """

    def stage_process(self):
        """
        Script lifecycle stage: PROCESSING

        Perform some real work (finally). Following method will call appropriate
        callback method operation to service the selected operation.
        """
        self.time_mark('stage_process_start', 'Start of the processing stage')

        # Log something to show we have reached this point of execution.
        self.logger.info("Demo implementation for default command")

        # Test direct console output with conjunction with verbosity
        self.p("Hello world")
        self.p("Hello world, verbosity level 1", 1)
        self.p("Hello world, verbosity level 2", 2)
        self.p("Hello world, verbosity level 3", 3)

        # Update the persistent state to view the changes.
        self.pstate['counter'] = self.pstate.get('counter', 0) + 1

        self.time_mark('stage_process_stop', 'End of the processing stage')

if __name__ == "__main__":
    """
    Perform the demonstration.
    """
    # Prepare the environment
    if not os.path.isdir('/tmp/baseapp.py'):
        os.mkdir('/tmp/baseapp.py')
    BaseApp.json_save('/tmp/baseapp.py.conf', {'test_a':1})

    script = _DemoBaseApp(
            path_cfg = '/tmp',
            path_log = '/tmp',
            path_tmp = '/tmp',
            path_run = '/tmp',
            description = 'DemoBaseApp - generic base script (DEMO)'
        )
    script.run()
