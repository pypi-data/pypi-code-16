# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016: Alignak contrib team, see AUTHORS.txt file for contributors
#
# This file is part of Alignak contrib projet.
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

"""
This module is an Alignak Broker module that collects the `monitoring_log` broks to send
them to a Python logger configured in the module configuration file
"""

import os
import json
import time
import logging
from logging import Formatter
from logging.handlers import TimedRotatingFileHandler
from logging.config import dictConfig as logger_dictConfig

from alignak.basemodule import BaseModule
from alignak_module_logs.logevent import LogEvent

try:
    from alignak_backend_client.client import Backend, BackendException
except ImportError:
    pass

logger = logging.getLogger('alignak.module')

properties = {
    'daemons': ['broker'],
    'type': 'logs',
    'external': True,
    'phases': ['running'],
}


def get_instance(mod_conf):
    """
    Return a module instance for the modules manager

    :param mod_conf: the module properties as defined globally in this file
    :return:
    """
    logger.info("Give an instance of %s for alias: %s", mod_conf.python_name, mod_conf.module_alias)

    return MonitoringLogsCollector(mod_conf)


class MonitoringLogsCollector(BaseModule):
    """
    Monitoring logs module main class
    """
    def __init__(self, mod_conf):
        # pylint: disable=global-statement
        """
        Module initialization

        mod_conf is a dictionary that contains:
        - all the variables declared in the module configuration file
        - a 'properties' value that is the module properties as defined globally in this file

        :param mod_conf: module configuration file as a dictionary
        """
        BaseModule.__init__(self, mod_conf)

        global logger
        logger = logging.getLogger('alignak.module.%s' % self.alias)

        logger.debug("inner properties: %s", self.__dict__)
        logger.debug("received configuration: %s", mod_conf.__dict__)

        # Internal logger for the monitoring logs
        self.logger = None

        # Logger configuration file
        self.logger_configuration = os.getenv('ALIGNAK_MONITORING_LOGS_CFG', None)
        if not self.logger_configuration:
            self.logger_configuration = getattr(mod_conf, 'logger_configuration', None)

        # Logger default parameters (used if logger_configuration is not defined)
        self.default_configuration = True
        self.log_logger_name = getattr(mod_conf, 'log_logger_name', 'monitoring-logs')
        self.log_dir = getattr(mod_conf, 'log_dir', '/tmp')
        self.log_file = getattr(mod_conf, 'log_file', 'monitoring-logs.log')
        self.log_filename = os.path.join(self.log_dir, self.log_file)
        self.log_rotation_when = getattr(mod_conf, 'log_rotation_when', 'midnight')
        self.log_rotation_interval = int(getattr(mod_conf, 'log_rotation_interval', '1'))
        self.log_rotation_count = int(getattr(mod_conf, 'log_rotation_count', '7'))
        self.log_level = getattr(mod_conf, 'log_level', 'INFO')
        self.log_level = getattr(logging, self.log_level, None)
        self.log_format = getattr(mod_conf, 'log_format ',
                                  '[%(created)i] %(levelname)s: %(message)s')
        self.log_date = getattr(mod_conf, 'log_date', '%Y-%m-%d %H:%M:%S %Z')

        if self.logger_configuration:
            logger.info("logger configuration defined in %s",
                        self.logger_configuration)
            self.default_configuration = False
            if not os.path.exists(self.logger_configuration):
                self.default_configuration = True
                logger.warning("defined logger configuration file does not exist! "
                               "Using default configuration.")

        if self.default_configuration:
            logger.info("logger default configuration:")
            logger.info(" - rotating logs in %s", self.log_filename)
            logger.info(" - log level: %s", self.log_level)
            logger.info(" - rotation every %d %s, keeping %s files",
                        self.log_rotation_interval, self.log_rotation_when, self.log_rotation_count)

        self.setup_logging()

        # Alignak backend part
        # -----
        # Try to login the Alignak backend if an api_url is defined.
        self.backend_connected = False
        self.url = getattr(mod_conf, 'api_url', None)
        logger.info("The module will not use the Alignak backend: %s", self.url)
        if self.url is None or not self.url:
            logger.info("The module will not use the Alignak backend")
            return

        try:
            self.backend = Backend(self.url)
        except Exception as exp:
            logger.exception("Exception: %s", exp)
            return

        self.backend.token = getattr(mod_conf, 'token', '')
        if self.backend.token == '':
            self.getToken(getattr(mod_conf, 'username', ''), getattr(mod_conf, 'password', ''),
                          getattr(mod_conf, 'allowgeneratetoken', False))

    def init(self):
        """Handle this module "post" init ; just before it'll be started.
        Like just open necessaries file(s), database(s),
        or whatever the module will need.

        :return: None
        """
        return True

    def setup_logging(self):
        """Setup logging configuration

        :return: none
        """
        self.logger = logging.getLogger(self.log_logger_name)

        if self.default_configuration:
            # Set logger level
            self.logger.setLevel(self.log_level)

            file_handler = TimedRotatingFileHandler(self.log_filename,
                                                    when=self.log_rotation_when,
                                                    interval=self.log_rotation_interval,
                                                    backupCount=self.log_rotation_count)
            file_handler.setFormatter(Formatter(self.log_format, self.log_date))
            self.logger.addHandler(file_handler)
        else:
            with open(self.logger_configuration, 'rt') as f:
                config = json.load(f)
            try:
                logger_dictConfig(config)
            except ValueError as exp:
                logger.error("Logger configuration file is not parsable correctly!")
                logger.exception(exp)

    def getToken(self, username, password, generatetoken):
        """
        Authenticate and get the token

        :param username: login name
        :type username: str
        :param password: password
        :type password: str
        :param generatetoken: if True allow generate token, otherwise not generate
        :type generatetoken: bool
        :return: None
        """
        generate = 'enabled'
        if not generatetoken:
            generate = 'disabled'

        try:
            self.backend_connected = self.backend.login(username, password, generate)
        except BackendException as exp:
            logger.warning("Alignak backend is not available for login. "
                           "No backend connection.")
            logger.exception("Exception: %s", exp)
            self.backend_connected = False

    def do_loop_turn(self):
        """This function is present because of an abstract function in the BaseModule class"""
        logger.info("In loop")
        time.sleep(1)

    def manage_brok(self, b):
        """
        We get the data to manage

        :param b: Brok object
        :type b: object
        :return: None
        """
        # Ignore all except 'monitoring_log' broks...
        if b.type not in ['monitoring_log']:
            return

        if b.data['level'].lower() not in ['debug', 'info', 'warning', 'error', 'critical']:
            return

        logger.debug("Got monitoring log brok: %s", b)

        # Send to configured logger
        func = getattr(self.logger, b.data['level'])
        func(b.data['message'])

        if not self.backend_connected:
            return

        # Try to get a monitoring event
        event = LogEvent(('[%s] ' % int(time.time())) + b.data['message'])
        if event.valid:
            # -------------------------------------------
            # Add an history event
            data = {}
            if event.event_type == 'NOTIFICATION':
                data = {
                    "host_name": event.data['hostname'],
                    "service_name": event.data['service_desc'],
                    "user_name": "Alignak",
                    "type": "monitoring.notification",
                    "message": b.data['message'],
                }

            if event.event_type == 'ALERT':
                data = {
                    "host_name": event.data['hostname'],
                    "service_name": event.data['service_desc'],
                    "user_name": "Alignak",
                    "type": "monitoring.alert",
                    "message": b.data['message'],
                }

            if event.event_type == 'DOWNTIME':
                downtime_type = "monitoring.downtime_start"
                if event.data['state'] == 'STOPPED':
                    downtime_type = "monitoring.downtime_end"
                if event.data['state'] == 'CANCELLED':
                    downtime_type = "monitoring.downtime_cancelled"

                data = {
                    "host_name": event.data['hostname'],
                    "service_name": event.data['service_desc'],
                    "user_name": "Alignak",
                    "type": downtime_type,
                    "message": b.data['message'],
                }

            if event.event_type == 'FLAPPING':
                flapping_type = "monitoring.flapping_start"
                if event.data['state'] == 'STOPPED':
                    flapping_type = "monitoring.flapping_stop"

                data = {
                    "host_name": event.data['hostname'],
                    "service_name": event.data['service_desc'],
                    "user_name": "Alignak",
                    "type": flapping_type,
                    "message": b.data['message'],
                }

            if not data:
                return
            try:
                self.backend.post('history', data)
            except BackendException as exp:
                logger.exception("Exception: %s", exp)

    def main(self):
        """
        Main loop of the process

        This module is an "external" module
        :return:
        """
        # Set the OS process title
        self.set_proctitle(self.alias)
        self.set_exit_handler()

        logger.info("starting...")

        while not self.interrupted:
            logger.debug("queue length: %s", self.to_q.qsize())
            start = time.time()

            # Get message in the queue
            l = self.to_q.get()
            for b in l:
                # Prepare and manage each brok in the queue message
                b.prepare()
                self.manage_brok(b)

            logger.debug("time to manage %s broks (%d secs)", len(l), time.time() - start)

        logger.info("stopping...")

        # Properly close all the Python logging stuff
        logging.shutdown()

        logger.info("stopped")
