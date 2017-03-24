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
#
#

"""
This module is an Alignak Receiver module that collects the external commands and builds
an external command object for the Alignak scheduler.
"""

import os
import time
import select
import errno

import logging

from alignak.basemodule import BaseModule
from alignak.external_command import ExternalCommand

logger = logging.getLogger('alignak.module')  # pylint: disable=C0103

# pylint: disable=C0103
properties = {
    'daemons': ['receiver'],
    'type': 'external-commands',
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

    return ExternalCommandsCollector(mod_conf)


class ExternalCommandsCollector(BaseModule):
    """
    External commands collector module main class
    """
    def __init__(self, mod_conf):
        """
        Module initialization

        mod_conf is a dictionary that contains:
        - all the variables declared in the module configuration file
        - a 'properties' value that is the module properties as defined globally in this file

        :param mod_conf: module configuration file as a dictionary
        """
        BaseModule.__init__(self, mod_conf)

        # pylint: disable=global-statement
        global logger
        logger = logging.getLogger('alignak.module.%s' % self.alias)

        logger.debug("inner properties: %s", self.__dict__)
        logger.debug("received configuration: %s", mod_conf.__dict__)

        self.file_path = getattr(mod_conf, 'file_path', '/tmp/alignak.cmd')

        self.file_descriptor = None
        self.parts = ''

        logger.info("configuration, getting external commands from: %s", self.file_path)

    def open_named_pipe(self):
        """
        Open (or re-open_named_pipe) the external commands file and create a named pipe for reading
        :return:
        """
        # At the first open_named_pipe del and create the fifo
        if self.file_descriptor is None:
            if os.path.exists(self.file_path):
                os.unlink(self.file_path)

            if not os.path.exists(self.file_path):
                logger.info("creating the external commands file...")
                os.umask(0)
                try:
                    if not os.path.exists(os.path.dirname(self.file_path)):
                        logger.info("creating the external commands file folder...")
                        os.mkdir(os.path.dirname(self.file_path))
                    logger.info("created external commands file folder")
                    os.mkfifo(self.file_path, 0660)
                    open(self.file_path, 'w+', os.O_NONBLOCK)
                except OSError as exp:
                    logger.error("External commands file creation failed")
                    logger.exception("Exception: %s", exp)
                    return None
                logger.info("created external commands file")

        logger.info("opening named pipe...")
        self.file_descriptor = os.open(self.file_path, os.O_NONBLOCK)
        logger.info("named pipe opened")
        return self.file_descriptor

    def read_named_pipe(self):
        """
        Read the named pipe
        :return:
        """
        bytes_read = os.read(self.file_descriptor, 8096)
        commands = []
        full_buffer = len(bytes_read) == 8096 and True or False

        # If the buffer ended with a partial command, prepend it here...
        bytes_read = self.parts + bytes_read
        buffer_length = len(bytes_read)
        self.parts = ''

        if full_buffer and bytes_read[-1] != '\n':
            # The buffer is full but ends with a partial command...
            commands.extend([ExternalCommand(s) for s in (bytes_read.split('\n'))[:-1] if s])
            self.parts = (bytes_read.split('\n'))[-1]
        elif buffer_length:
            # The buffer is either half-filled or full with a '\n' at the end.
            commands.extend([ExternalCommand(s) for s in bytes_read.split('\n') if s])
        else:
            # The buffer is empty. Reset the pipe that will be re-opened in the main loop.
            os.close(self.file_descriptor)

        return commands

    def do_loop_turn(self):
        pass

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

        readings = [self.open_named_pipe()]

        while not self.interrupted:
            if not readings:
                time.sleep(1)
                continue

            inputready = []
            try:
                inputready, _, _ = select.select(readings, [], [], 1)
            except select.error, e:
                if e.args[0] == errno.EINTR:
                    os.unlink(self.file_path)
                    logger.info("received exit signal")
                    return

            for _ in inputready:
                # Read from named pipe
                ext_cmds = self.read_named_pipe()
                if ext_cmds:
                    for ext_cmd in ext_cmds:
                        self.from_q.put(ext_cmd)
                else:
                    readings = [self.open_named_pipe()]

        logger.info("stopping...")
        logger.info("stopped")
