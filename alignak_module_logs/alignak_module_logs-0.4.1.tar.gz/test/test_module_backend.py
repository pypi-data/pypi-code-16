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
Test the module with an lignak backend connection
"""

import os
import time
import shlex
import subprocess

import requests

from alignak_test import AlignakTest
from alignak.modulesmanager import ModulesManager
from alignak.objects.module import Module
from alignak.basemodule import BaseModule
from alignak.brok import Brok

from alignak_backend_client.client import Backend

# Set environment variable to ask code Coverage collection
os.environ['COVERAGE_PROCESS_START'] = '.coveragerc'

from alignak_module_logs.logs import get_instance
from alignak_module_logs.logevent import LogEvent


class TestModuleConnection(AlignakTest):

    @classmethod
    def setUpClass(cls):

        # Set test mode for alignak backend
        os.environ['TEST_ALIGNAK_BACKEND'] = '1'
        os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'] = 'alignak-module-logs-backend-test'

        # Delete used mongo DBs
        print ("Deleting Alignak backend DB...")
        exit_code = subprocess.call(
            shlex.split(
                'mongo %s --eval "db.dropDatabase()"' % os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'])
        )
        assert exit_code == 0

        cls.p = subprocess.Popen(['uwsgi', '--plugin', 'python', '-w', 'alignakbackend:app',
                                  '--socket', '0.0.0.0:5000',
                                  '--protocol=http', '--enable-threads', '--pidfile',
                                  '/tmp/uwsgi.pid'])
        time.sleep(3)

        endpoint = 'http://127.0.0.1:5000'

        # Backend authentication
        headers = {'Content-Type': 'application/json'}
        params = {'username': 'admin', 'password': 'admin', 'action': 'generate'}
        # Get admin user token (force regenerate)
        response = requests.post(endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        cls.token = resp['token']
        cls.auth = requests.auth.HTTPBasicAuth(cls.token, '')

        # Get admin user
        response = requests.get(endpoint + '/user', auth=cls.auth)
        resp = response.json()
        cls.user_admin = resp['_items'][0]

        # Get realms
        response = requests.get(endpoint + '/realm', auth=cls.auth)
        resp = response.json()
        cls.realmAll_id = resp['_items'][0]['_id']

        # Add a user
        data = {'name': 'test', 'password': 'test', 'back_role_super_admin': False,
                'host_notification_period': cls.user_admin['host_notification_period'],
                'service_notification_period': cls.user_admin['service_notification_period'],
                '_realm': cls.realmAll_id}
        response = requests.post(endpoint + '/user', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        print("Created a new user: %s" % resp)

    @classmethod
    def tearDownClass(cls):
        cls.p.kill()

    def test_connection_accepted(self):
        """ Test module backend connection accepted """
        mod = get_instance(Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'logger_configuration': './mod-logs-logger.json',
            'api_url': 'http://127.0.0.1:5000',
            'username': 'admin',
            'password': 'admin',
        }))
        self.assertTrue(mod.backend_connected)

    def test_connection_refused(self):
        """ Test module backend connection refused """
        # No backend data defined
        mod = get_instance(Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'logger_configuration': './mod-logs-logger.json',
        }))
        self.assertFalse(mod.backend_connected)

        # Backend bad URL
        mod = get_instance(Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'logger_configuration': './mod-logs-logger.json',
            'api_url': 'http://bad_url',
            'username': 'admin',
            'password': 'admin',
        }))
        self.assertFalse(mod.backend_connected)

        # Backend refused login
        mod = get_instance(Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'logger_configuration': './mod-logs-logger.json',
            'api_url': 'http://127.0.0.1:5000',
            'username': 'fake',
            'password': 'fake',
        }))
        self.assertFalse(mod.backend_connected)

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
            'api_url': 'http://127.0.0.1:5000',
            'username': 'admin',
            'password': 'admin',
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

        instance = get_instance(mod)
        self.assertIsInstance(instance, BaseModule)

        # No more logs because the logger got re-configured... but some files exist
        self.assertTrue(os.path.exists('/tmp/rotating-monitoring.log'))
        self.assertTrue(os.path.exists('/tmp/timed-rotating-monitoring.log'))

        b = Brok({'type': 'monitoring_log', 'data': {'level': 'info', 'message': 'test message'}})
        b.prepare()
        instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {
            'level': 'info',
            'message': 'SERVICE ALERT: cogny;Load;OK;HARD;4;OK - load average: 0.74, 0.89, 1.03'
        }})
        b.prepare()
        instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {
            'level': 'warning',
            'message': 'SERVICE NOTIFICATION: admin;localhost;check-ssh;'
                       'CRITICAL;notify-service-by-email;Connection refused'
        }})
        b.prepare()
        instance.manage_brok(b)

        # Get log file that should contain one line
        with open('/tmp/rotating-monitoring.log', 'r') as f:
            data = f.readlines()
        data = data[5:]
        # self.assertEqual(3, len(data))
        logs = []
        for line in data:
            line = line.replace('ERROR: ', '')
            line = line.replace('WARNING: ', '')
            line = line.replace('INFO: ', '')
            logs.append(line)
        print(logs)

        assert 'test message' in data[0]
        assert 'SERVICE ALERT: cogny;Load;OK;HARD;4;OK - load average: 0.74, 0.89, 1.03' in data[1]
        assert 'SERVICE NOTIFICATION: admin;localhost;check-ssh;' \
               'CRITICAL;notify-service-by-email;Connection refused' in data[2]

        log = logs[2]
        log = log[13:]
        log = '[1480152711] ' + log
        print log
        log = '[1402515279] SERVICE NOTIFICATION: admin;localhost;check-ssh;' \
              'CRITICAL;notify-service-by-email;Connection refused'
        expected = {
            'hostname': 'localhost',
            'event_type': 'NOTIFICATION',
            'service_desc': 'check-ssh',
            'state': 'CRITICAL',
            'contact': 'admin',
            'time': 1402515279,
            'notification_method': 'notify-service-by-email',
            'notification_type': 'SERVICE',
            'output': 'Connection refused',
        }
        event = LogEvent(log)
        print event
        assert event.valid
        assert event.data == expected

        # And we clear all now
        self.modulemanager.stop_all()
        # Stopping module logs

        # Get backend history for the monitoring logs
        backend = Backend('http://127.0.0.1:5000')
        backend.login("admin", "admin", "force")

        r = backend.get('history')
        self.assertEqual(len(r['_items']), 2)
        assert r['_items'][0]['host_name'] == 'cogny'
        assert r['_items'][0]['service_name'] == 'Load'
        assert r['_items'][0]['type'] == 'monitoring.alert'
        assert r['_items'][0]['message'] == 'SERVICE ALERT: cogny;Load;OK;HARD;4;' \
                                            'OK - load average: 0.74, 0.89, 1.03'

        assert r['_items'][1]['host_name'] == 'localhost'
        assert r['_items'][1]['service_name'] == 'check-ssh'
        assert r['_items'][1]['type'] == 'monitoring.notification'
        assert r['_items'][1]['message'] == 'SERVICE NOTIFICATION: admin;localhost;check-ssh;' \
                                            'CRITICAL;notify-service-by-email;Connection refused'
