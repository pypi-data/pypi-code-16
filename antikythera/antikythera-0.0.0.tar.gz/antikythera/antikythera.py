#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" antikythera.py

The main program manager.

"""
import os
import logging
import argparse
import appdirs
import multiprocessing as mp

from time import sleep
from multiprocessing import Process, Queue
from sqlitedict import SqliteDict

import antikythera.pysharkpatch

from antikythera.capture import Capture
from antikythera.decoder import Decoder
from antikythera.metrics import Metrics

_logger = logging.getLogger(__name__)

__author__= "Finding Ray"
__copyright__ = "Finding Ray"
__license__ = "GNU GPLv3+"


class Anti(Process):
    """ Start and monitor the worker processes.

    """
    def __init__(self, num_processes, headless, interface=None,
                 capturefile=None, max_qsize=100000, *args, **kwargs):
        """

        """
        super(Anti, self).__init__(*args, **kwargs)
        self.MAX_QUEUE_SIZE = max_qsize
        self.pkt_queue = Queue(self.MAX_QUEUE_SIZE)
        self.error_queue = Queue()
        self.NUMBER_OF_PROCESSES = num_processes
        self.workers = []
        self.interface = interface
        self.capturefile = capturefile
        self.headless = headless
        self.exit = mp.Event()
        #_logger.info(self)

    def __str__(self):
        s = ("Initial Process Manager State:\n" +
             "[*] Headless: {}\n".format(self.headless) +
             "[*] Queue: {}\n".format(self.queue) +
             "[*] Queue Size: {}\n".format(self.queue.qsize()) +
             "[*] Max Queue Size: {}\n".format(self.MAX_QUEUE_SIZE) +
             "[*] Number of Processes to Create: {}\n".format(self.NUMBER_OF_PROCESSES) +
             "[*] Number of Processes Created: {}\n".format(len(self.workers)) +
             "[*] Network Interface: {}\n".format(self.interface) +
             "[*] Capture File: {}".format(self.capturefile)
            )
        return s


    def run(self):
        """

        """
        try:
            cpus = mp.cpu_count()
            _logger.info("Anti: system has {} CPUs available".format(cpus))
        except NotImplementedError as e:
            _logger.info("Anti: could not get number of available CPUs")

        for i in range(self.NUMBER_OF_PROCESSES):
            name = "decoder-" + str(i)
            _logger.info("Anti: Creating decoder process {}".format(name))
            decoder_worker = Decoder(name, self.pkt_queue, name=name, daemon=True)
            self.workers.append(decoder_worker)

        _logger.info("Anti: Creating capture process capture")
        if self.interface != None:
            _logger.debug("Anti: Creating capture process with network interface")
            capture_worker = Capture("capture", self.pkt_queue, interface=self.interface, name="capture", daemon=True)
        elif self.capturefile != None:
            _logger.debug("Anti: Creating capture process with capture file")
            capture_worker = Capture("capture", self.pkt_queue, capturefile=self.capturefile, name="capture", daemon=True)
        else:
            _logger.critical("Anti: no capture method supplied aborting!")

        self.workers.append(capture_worker)

        metrics_worker = Metrics("metrics", name="metrics", daemon=True)
        self.workers.append(metrics_worker)

        for worker in self.workers:
            _logger.info("Anti: Starting process {}".format(worker))
            worker.start()

        _logger.info("Anti: spawned {} child processes".format(len(mp.active_children())))
        _logger.info("Anti: successfully started")

        self.wait()

    def shutdown(self):
        _logger.info("Anti: received shutdown command")
        self.exit.set()


    def exit_process(self, p):
        """

        """
        _logger.debug("Anti: shutting down {} pid {}".format(p, p.pid))
        p.shutdown()
        _logger.info("Anti: waiting for process {} pid {}".format(p.process_id, p.pid))
        p.join(60)
        if p.is_alive():
            _logger.warning("Anti: process {} pid {} still alive calling terminate()".format(p.process_id, p.pid))
            p.terminate()
            if p.is_alive():
                _logger.critical("Anti: could not terminate process {} pid {}".format(p.process_id, p.pid))


    def wait(self):
        """

        """
        _logger.info("Anti: waiting for shutdown")
        while not self.exit.is_set():
            sleep(1)
        
        _logger.info("Anti: shutting down child processes")
        _logger.debug("Anti: Active children {}".format(mp.active_children()))

        for p in mp.active_children():
            if p.name == "capture":
                self.exit_process(p)

        for p in mp.active_children():
            if p.name == "decoder-0":
                self.exit_process(p)

        for p in mp.active_children():
            if p.name == "metrics":
                self.exit_process(p)

        _logger.debug("Anti: Active children {}".format(mp.active_children()))
        for p in mp.active_children():
            p.terminate()
            _logger.critical("Anti: waiting forever on process {} pid {}".format(p.process_id, p.pid))
            p.join()

        _logger.info("Anti: Exiting")


    def create_db():
        """ Create the database if needed.

        """
        pass


def create_parser():
    """ Parse command line parameters.

    :return: command line parameters as :obj:`argparse.Namespace`
    Args:
        args ([str]): List of strings representing the command line arguments.

    Returns:
        argparse.Namespace: Simple object with a readable string
        representation of the argument list.

    """
    parser = argparse.ArgumentParser(
        description="IMSI Catcher Detector.")
    source=parser.add_mutually_exclusive_group()
    logs=parser.add_mutually_exclusive_group()
    parser.add_argument(
        '-t',
        '--threads',
        nargs='?',
        type=int,
        default=1,
        dest="threads",
        help="Number of threads to use.",
        action='store'),
    parser.add_argument(
        '-q',
        '--qsize',
        nargs='?',
        type=int,
        default=None,
        dest="qsize",
        help="The maximum queue size for packets waiting to be processed.",
        action='store'),
    parser.add_argument(
        '--headless',
        default=False,
        dest="headless",
        help="Run in headless mode without GUI.",
        action='store_true'),
    logs.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO),
    logs.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="set loglevel to DEBUG",
        action='store_const',
        const=logging.DEBUG),
    logs.add_argument(
        '-vvv',
        '--trace',
        dest="loglevel",
        help="set loglevel to TRACE",
        action='store_const',
        const=logging.TRACE),
    source.add_argument(
        '-c',
        '--capture',
        nargs='?',
        type=str,
        default=None,
        dest="pcap",
        help="Path to a capture file to use as input.",
        action='store'),
    source.add_argument(
        '-i',
        '--interface',
        nargs='?',
        type=str,
        default=None,
        dest="interface",
        help="The identifier of the network interface to use.",
        action='store')

    return parser


if __name__ == '__main__':
    a = anti(0)
