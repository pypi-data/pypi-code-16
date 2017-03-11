#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016: Alignak team, see AUTHORS.txt file for contributors
#
# This file is part of Alignak.
#
# Alignak is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Alignak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Alignak.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Test the module
"""

import re
import os
import time
from alignak_test import AlignakTest, time_hacker
from alignak.modulesmanager import ModulesManager
from alignak.objects.module import Module
from alignak.basemodule import BaseModule
from alignak.brok import Brok

# Set environment variable to ask code Coverage collection
os.environ['COVERAGE_PROCESS_START'] = '.coveragerc'

import alignak_module_logs


class TestModules(AlignakTest):
    """
    This class contains the tests for the module
    """

    def test_module_loading(self):
        """
        Test module loading

        Alignak module loading

        :return:
        """
        self.print_header()
        self.setup_with_file('./cfg/cfg_default.cfg')
        self.assertTrue(self.conf_is_correct)
        self.show_configuration_logs()

        # No arbiter modules created
        modules = [m.module_alias for m in self.arbiter.myself.modules]
        self.assertListEqual(modules, [])

        # The only existing broker module is logs declared in the configuration
        modules = [m.module_alias for m in self.brokers['broker-master'].modules]
        self.assertListEqual(modules, ['logs'])

        # No poller module
        modules = [m.module_alias for m in self.pollers['poller-master'].modules]
        self.assertListEqual(modules, [])

        # No receiver module
        modules = [m.module_alias for m in self.receivers['receiver-master'].modules]
        self.assertListEqual(modules, [])

        # No reactionner module
        modules = [m.module_alias for m in self.reactionners['reactionner-master'].modules]
        self.assertListEqual(modules, [])

        # No scheduler modules
        modules = [m.module_alias for m in self.schedulers['scheduler-master'].modules]
        self.assertListEqual(modules, [])

        # Loading module logs
        # self.assert_any_log_match(re.escape(
        #     "Importing Python module 'alignak_module_example' for Example..."
        # ))
        # self.assert_any_log_match(re.escape(
        #     "Module properties: {'daemons': ['arbiter', 'broker', 'scheduler', 'poller', "
        #     "'receiver', 'reactionner'], 'phases': ['configuration', 'late_configuration', "
        #     "'running', 'retention'], 'type': 'example', 'external': True}"
        # ))
        # self.assert_any_log_match(re.escape(
        #     "Imported 'alignak_module_example' for Example"
        # ))
        # self.assert_any_log_match(re.escape(
        #     "Give an instance of alignak_module_example for alias: Example"
        # ))
        # self.assert_any_log_match(re.escape(
        #     "I correctly loaded my modules: [Example]"
        # ))

    def test_module_manager(self):
        """
        Test if the module manager manages correctly all the modules
        :return:
        """
        self.print_header()
        self.setup_with_file('cfg/cfg_default.cfg')
        self.assertTrue(self.conf_is_correct)

        time_hacker.set_real_time()

        # Create an Alignak module
        mod = Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs'
        })

        # Create the modules manager for a daemon type
        self.modulemanager = ModulesManager('broker', None)

        # Load an initialize the modules:
        #  - load python module
        #  - get module properties and instances
        self.modulemanager.load_and_init([mod])

        # Loading module logs
        self.assert_any_log_match(re.escape(
            "Importing Python module 'alignak_module_logs' for logs..."
        ))
        self.assert_any_log_match(re.escape(
            "Module properties: {'daemons': ['broker'], 'phases': ['running'], "
            "'type': 'logs', 'external': True}"
        ))
        self.assert_any_log_match(re.escape(
            "Imported 'alignak_module_logs' for logs"
        ))
        self.assert_any_log_match(re.escape(
            "Loaded Python module 'alignak_module_logs' (logs)"
        ))
        self.assert_any_log_match(re.escape(
            "Give an instance of alignak_module_logs for alias: logs"
        ))

        my_module = self.modulemanager.instances[0]

        # Get list of not external modules
        self.assertListEqual([], self.modulemanager.get_internal_instances())
        for phase in ['configuration', 'late_configuration', 'running', 'retention']:
            self.assertListEqual([], self.modulemanager.get_internal_instances(phase))

        # Get list of external modules
        self.assertListEqual([my_module], self.modulemanager.get_external_instances())
        for phase in ['configuration', 'late_configuration', 'retention']:
            self.assertListEqual([], self.modulemanager.get_external_instances(phase))
        for phase in ['running']:
            self.assertListEqual([my_module], self.modulemanager.get_external_instances(phase))

        # Clear logs
        self.clear_logs()

        # Start external modules
        self.modulemanager.start_external_instances()

        # Starting external module logs
        self.assert_log_match("Trying to initialize module: logs", 0)
        self.assert_log_match("Starting external module logs", 1)
        self.assert_log_match("Starting external process for module logs", 2)
        self.assert_log_match("logs is now started", 3)

        # Check alive
        self.assertIsNotNone(my_module.process)
        self.assertTrue(my_module.process.is_alive())

        # Clear logs
        self.clear_logs()

        # Kill the external module (normal stop is .stop_process)
        my_module.kill()
        time.sleep(0.1)
        self.assert_log_match("Killing external module", 0)
        self.assert_log_match("External module killed", 1)

        # Should be dead (not normally stopped...) but we still know a process for this module!
        self.assertIsNotNone(my_module.process)

        # Nothing special ...
        self.modulemanager.check_alive_instances()
        self.assert_log_match("The external module logs died unexpectedly!", 2)
        self.assert_log_match("Setting the module logs to restart", 3)

        # Try to restart the dead modules
        self.modulemanager.try_to_restart_deads()
        self.assert_log_match("Trying to initialize module: logs", 4)

        # In fact it's too early, so it won't do it
        # The module instance is still dead
        self.assertFalse(my_module.process.is_alive())

        # So we lie, on the restart tries ...
        my_module.last_init_try = -5
        self.modulemanager.check_alive_instances()
        self.modulemanager.try_to_restart_deads()
        self.assert_log_match("Trying to initialize module: logs", 5)

        # The module instance is now alive again
        self.assertTrue(my_module.process.is_alive())
        self.assert_log_match("I'm stopping module 'logs'", 6)
        self.assert_log_match("Starting external process for module logs", 7)
        self.assert_log_match("logs is now started", 8)

        # There is nothing else to restart in the module manager
        self.assertEqual([], self.modulemanager.to_restart)

        # Clear logs
        self.clear_logs()

        # Now we look for time restart so we kill it again
        my_module.kill()
        time.sleep(0.2)
        self.assertFalse(my_module.process.is_alive())
        self.assert_log_match("Killing external module", 0)
        self.assert_log_match("External module killed", 1)

        # Should be too early
        self.modulemanager.check_alive_instances()
        self.assert_log_match("The external module logs died unexpectedly!", 2)
        self.assert_log_match("Setting the module logs to restart", 3)

        self.modulemanager.try_to_restart_deads()
        self.assert_log_match("Trying to initialize module: logs", 4)

        # In fact it's too early, so it won't do it
        # The module instance is still dead
        self.assertFalse(my_module.process.is_alive())

        # So we lie, on the restart tries ...
        my_module.last_init_try = -5
        self.modulemanager.check_alive_instances()
        self.modulemanager.try_to_restart_deads()
        self.assert_log_match("Trying to initialize module: logs", 5)

        # The module instance is now alive again
        self.assertTrue(my_module.process.is_alive())
        self.assert_log_match("I'm stopping module 'logs'", 6)
        self.assert_log_match("Starting external process for module logs", 7)
        self.assert_log_match("logs is now started", 8)

        # And we clear all now
        self.modulemanager.stop_all()
        # Stopping module logs

        self.assert_log_match("Request external process to stop for logs", 9)
        self.assert_log_match(re.escape("I'm stopping module 'logs' (pid="), 10)
        self.assert_log_match(
            re.escape("'logs' is still alive after normal kill, I help it to die"), 11
        )
        self.assert_log_match("Killing external module ", 12)
        self.assert_log_match("External module killed", 13)
        self.assert_log_match("External process stopped.", 14)

    def test_module_start_default(self):
        """
        Test the module initialization function, no parameters, using default
        :return:
        """
        self.print_header()
        # Obliged to call to get a self.logger...
        self.setup_with_file('cfg/cfg_default.cfg')
        self.assertTrue(self.conf_is_correct)

        # -----
        # Default initialization
        # -----
        # Clear logs
        self.clear_logs()

        # Create an Alignak module
        mod = Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs'
        })

        instance = alignak_module_logs.get_instance(mod)
        self.assertIsInstance(instance, BaseModule)

        self.assert_log_match(
            re.escape("Give an instance of alignak_module_logs for alias: logs"), 0)
        self.assert_log_match(
            re.escape("logger default configuration:"), 1)
        self.assert_log_match(
            re.escape(" - rotating logs in /tmp/monitoring-logs.log"), 2)
        self.assert_log_match(
            re.escape(" - log level: 20"), 3)
        self.assert_log_match(
            re.escape(" - rotation every 1 midnight, keeping 7 files"), 4)

    def test_module_start_parameters_1(self):
        """
        Test the module initialization function, no parameters, provide parameters
        :return:
        """
        self.print_header()
        # Obliged to call to get a self.logger...
        self.setup_with_file('cfg/cfg_default.cfg')
        self.assertTrue(self.conf_is_correct)

        # -----
        # Provide parameters
        # -----
        # Clear logs
        self.clear_logs()

        # Create an Alignak module
        mod = Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'log_dir': '/tmp',
            'log_file': 'test.log',
            'log_level': 'WARNING',
            'log_rotation_when': 'd',
            'log_rotation_interval': 5,
            'log_rotation_count': 10,
            'log_format': '[%(created)i] %(levelname)s: %(message)s',
            'log_date': '%Y-%m-%d %H:%M:%S %Z',
        })

        instance = alignak_module_logs.get_instance(mod)
        self.assertIsInstance(instance, BaseModule)

        self.assert_log_match(
            re.escape("Give an instance of alignak_module_logs for alias: logs"), 0)
        self.assert_log_match(
            re.escape("logger default configuration:"), 1)
        self.assert_log_match(
            re.escape(" - rotating logs in /tmp/test.log"), 2)
        self.assert_log_match(
            re.escape(" - log level: 30"), 3)
        self.assert_log_match(
            re.escape(" - rotation every 5 d, keeping 10 files"), 4)

    def test_module_start_parameters_2(self):
        """
        Test the module initialization function, no parameters, provide parameters
        :return:
        """
        self.print_header()
        # Obliged to call to get a self.logger...
        self.setup_with_file('cfg/cfg_default.cfg')
        self.assertTrue(self.conf_is_correct)

        # -----
        # Provide parameters - logger configuration file (does no exist)
        # -----
        # Clear logs
        self.clear_logs()

        # Create an Alignak module
        mod = Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'logger_configuration': 'not_found.json',
        })

        instance = alignak_module_logs.get_instance(mod)
        self.assertIsInstance(instance, BaseModule)

        self.assert_log_match(
            re.escape("Give an instance of alignak_module_logs for alias: logs"), 0)
        self.assert_log_match(
            re.escape("logger configuration defined in not_found.json"), 1)
        self.assert_log_match(
            re.escape("defined logger configuration file does not exist! "
                      "Using default configuration."), 2)
        self.assert_log_match(
            re.escape("logger default configuration:"), 3)
        self.assert_log_match(
            re.escape(" - rotating logs in /tmp/monitoring-logs.log"), 4)
        self.assert_log_match(
            re.escape(" - log level: 20"), 5)
        self.assert_log_match(
            re.escape(" - rotation every 1 midnight, keeping 7 files"), 6)

        # -----
        # Provide parameters - logger configuration file (exists)
        # -----
        # Clear logs
        self.clear_logs()

        # Create an Alignak module
        mod = Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'logger_configuration': './mod-logs-logger_syntax.json',
        })

        instance = alignak_module_logs.get_instance(mod)
        self.assertIsInstance(instance, BaseModule)

        self.assert_log_match(
            re.escape("Give an instance of alignak_module_logs for alias: logs"), 0)
        self.assert_log_match(
            re.escape("logger configuration defined in ./mod-logs-logger_syntax.json"), 1
        )
        self.assert_log_match(
            re.escape("Logger configuration file is not parsable correctly!"), 2)
        self.assert_log_match(
            re.escape("Unable to configure logger 'alignak.module.logs': "
                      "Unable to add handler u'console': u'console'"), 3)

        # -----
        # Provide parameters - logger configuration file (exists)
        # -----
        # Clear logs
        self.clear_logs()

        # Create an Alignak module
        mod = Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'logger_configuration': './mod-logs-logger.json',
        })

        instance = alignak_module_logs.get_instance(mod)
        self.assertIsInstance(instance, BaseModule)

        # No more logs because the logger got re-configured... but some files exist
        self.assertTrue(os.path.exists('/tmp/rotating-monitoring.log'))
        self.assertTrue(os.path.exists('/tmp/timed-rotating-monitoring.log'))

    def test_module_zzz_get_logs(self):
        """
        Test the module log collection functions
        :return:
        """
        self.print_header()
        # Obliged to call to get a self.logger...
        self.setup_with_file('cfg/cfg_default.cfg')
        self.assertTrue(self.conf_is_correct)

        # -----
        # Provide parameters - logger configuration file (exists)
        # -----
        # Clear logs
        self.clear_logs()

        if os.path.exists('/tmp/rotating-monitoring.log'):
            os.remove('/tmp/rotating-monitoring.log')

        if os.path.exists('/tmp/timed-rotating-monitoring.log'):
            os.remove('/tmp/timed-rotating-monitoring.log')

        # Create an Alignak module
        mod = Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'logger_configuration': './mod-logs-logger.json',
        })

        # Create the modules manager for a daemon type
        self.modulemanager = ModulesManager('receiver', None)

        # Load an initialize the modules:
        #  - load python module
        #  - get module properties and instances
        self.modulemanager.load_and_init([mod])

        my_module = self.modulemanager.instances[0]

        # Clear logs
        self.clear_logs()

        # Start external modules
        self.modulemanager.start_external_instances()

        # Starting external module logs
        self.assert_log_match("Trying to initialize module: logs", 0)
        self.assert_log_match("Starting external module logs", 1)
        self.assert_log_match("Starting external process for module logs", 2)
        self.assert_log_match("logs is now started", 3)
        # self.assert_log_match("Process for module logs is now running", 4)

        time.sleep(1)

        # Check alive
        self.assertIsNotNone(my_module.process)
        self.assertTrue(my_module.process.is_alive())

        time.sleep(1)

        instance = alignak_module_logs.get_instance(mod)
        self.assertIsInstance(instance, BaseModule)

        # No more logs because the logger got re-configured... but some files exist
        self.assertTrue(os.path.exists('/tmp/rotating-monitoring.log'))
        self.assertTrue(os.path.exists('/tmp/timed-rotating-monitoring.log'))

        b = Brok({'type': 'monitoring_log', 'data': {'level': 'info', 'message': 'test message'}})
        b.prepare()
        instance.manage_brok(b)

        # Get log file that should contain one line
        with open('/tmp/rotating-monitoring.log', 'r') as f:
            data = f.readlines()
            self.assertEqual(6, len(data))
            print(data)


        # And we clear all now
        self.modulemanager.stop_all()
        # Stopping module logs
