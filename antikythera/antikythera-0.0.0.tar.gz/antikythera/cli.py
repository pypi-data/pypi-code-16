#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" cli.py

This is the Antikythera console script. It provides the
entry points that are used to run the program when it is
installed. To install the program run ``python setup.py install``
and it will be installed on the system.

"""
import os
import sys
import logging

from antikythera import __version__
from antikythera.antikythera import Anti, create_parser

_logger = logging.getLogger(__name__)

try:
    import appdirs
except ImportError as e:
    _logger.error("CLI: {}".format(e))
    _logger.info("CLI: Maybe try `pip install -r requirements.txt'")
    sys.exit(1)

__author__= "Finding Ray"
__copyright__ = "Finding Ray"
__license__ = "GNU GPLv3+"


# Define numerical value for a logging level
# that is one numerical value lower than DEBUG
logging.TRACE = 9


def main(args):
    """Main entry point allowing external calls.

    Collects command line arguments, sets up the logs, and logs information
    about them. Then it starts the program loop.

    Args:
      args ([str]): command line parameter list

    """
    parser = create_parser()
    args = parser.parse_args(args)

    # Gather args
    threads = args.threads
    pcap = args.pcap
    interface = args.interface
    qsize = args.qsize
    headless = args.headless

    # Set up logs, default to warning
    if args.loglevel:
        setup_logs(args.loglevel)
    else:
        setup_logs(logging.WARNING)

    # Save input parameters to logfile and set them
    _logger.info("Setting arguments")
    _logger.info("Threads Requested: {}".format(threads))
    if pcap is not None:
        _logger.info("Input Source: {}".format(pcap))
        if qsize is not None:
            IMSI_detector = anti(threads, headless, capturefile=pcap, max_qsize=qsize)
        else:
            IMSI_detector = anti(threads, headless, capturefile=pcap)
    else:
        _logger.info("Input Source: {}".format(interface))
        if args.qsize is not None:
            IMSI_detector = anti(threads, headless, interface=interface, max_qsize=qsize)
        else:
            IMSI_detector = anti(threads, headless, interface=interface)

    # Start Subprocesses
    _logger.info("Setup complete starting program")
    IMSI_detector.start()

    # Wait
    IMSI_detector.join()
    
    _logger.info("All done, shutting down.")
    logging.shutdown()


def setup_logs(loglevel):
    """ Set up logger to be used between all modules.

    Set logging root and file handler configuration to default to
    ``INFO`` and write output to ``main.log``. Set console
    handler to default to ``INFO``.

    Args:
        loglevel str: A string of one of the Default Python logging levels.
            See the `Python logging level documentation <https://docs.python.org/3/howto/logging.html#logging-levels>`_
            for more information.

    """
    # Setup Logging Directory
    logdir = appdirs.user_log_dir(__name__, __author__)
    if not os.path.exists(logdir):
        try:
            os.makedirs(logdir)
        except OSError as e:
            print("{}".format(e))
    logfile = logdir + ".txt"
    print("[*] Logfile: {}".format(logfile))

    # Add logging level TRACE
    logging.addLevelName(logging.TRACE, "TRACE")
    logging.Logger.trace = trace # Set Logger.trace to the trace function

    # Convert `logging' string to a level that can be set
    logging.basicConfig(level=loglevel, filename=logfile, filemode='w')

    # create file handler which logs messages
    fh = logging.FileHandler(logfile)
    fh.setLevel(loglevel)

    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(loglevel)

    # add the handlers to the logger
    _logger.addHandler(fh)
    _logger.addHandler(ch)


def trace(self, message, *args, **kws):
    """ Define trace logging level

    Yes, logger takes its '*args' as 'args'.

    """
    self._log(logging.TRACE, message, args, **kws) 


def run():
    """ Entry point for console_scripts.

    """
    main(sys.argv[1:])
    return 0


if __name__ == "__main__":
    sys.exit(run())
