#!/usr/bin/env python

'''
flows.py
Starter module
--------------

Copyright 2016 Davide Mastromatteo
License: Apache-2.0
'''

import logging
import sys
import time

import flows.Global


__author__ = "Davide Mastromatteo"
__copyright__ = "Copyright 2016, Davide Mastromatteo"
__credits__ = [""]
__license__ = "Apache-2.0"
__version__ = flows.Global.VERSION
__maintainer__ = "Davide Mastromatteo"
__email__ = "dave35@me.com"
__status__ = "Beta"

def start():
    '''Entry point'''

    # cli.main(sys.argv)
    args = sys.argv
    if args is None:
        return

    _parse_input_parameters(args)
    _read_configuration()

    flows.Global.PROCESS_MANAGER.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        flows.Global.LOGGER.info("Quit command received")
        flows.Global.PROCESS_MANAGER.stop()




def _read_configuration():
    configuration = flows.Global.CONFIG_MANAGER
    configuration.read_configuration()


def _parse_input_parameters(args):
    """Set the configuration for the Logger"""

    log_level = logging.INFO
    filename = ""

    # set the logging to "ERROR" level

    if len(args) >= 2:
        for i in range(1, len(args)):
            arg = args[i]

            if arg == "--VERSION":
                print("Version = " + str(flows.Global.VERSION))
            if arg == "--INFO":
                log_level = logging.INFO

            if arg == "--WARN":
                log_level = logging.WARN

            if arg == "--DEBUG":
                log_level = logging.DEBUG

            if arg == "--ERROR":
                log_level = logging.ERROR

            if arg == "--version":
                print("\nversion " + str(__version__) + "\n")

            if not arg.startswith("--"):
                filename = arg
                flows.Global.CONFIG_MANAGER.recipes.append(filename)

    flows.Global.CONFIG_MANAGER.log_level = log_level
    flows.Global.LOGGER_INSTANCE.reconfigure_log_level()


if __name__ == "__main__":
    start()
