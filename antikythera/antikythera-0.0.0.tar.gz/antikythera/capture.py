#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" capture.py

Interface to the radio and Pcap files.

"""
import logging
import multiprocessing as mp

from random import random
from time import sleep
from queue import Full
from multiprocessing import Process, Queue
from queue import Empty

_logger = logging.getLogger(__name__)

try:
    import pyshark
except ImportError as e:
    _logger.error("Capture: {}".format(e))
    _logger.info("Capture: Maybe try `pip install -r requirements.txt'")
    sys.exit(1)

DEFAULT_DELAY = 0.2


class Capture(Process):
    """ Grab the packets from the radio interface.

    """

    def __init__(self, process_id, q, *args, interface=None, capturefile=None,
                 delay=None, **kwargs):

        super(Capture, self).__init__(*args, **kwargs)
        self.process_id = process_id
        self.q = q
        self.interface = interface
        self.capturefile = capturefile
        self.delay = delay
        self.exit = mp.Event()


    def run(self):
        """

        """
        try:

            sleep(2)

            _logger.debug("{}: Process started successfully".format(self.process_id))
            # Todo: use exception, maybe in init
            if self.interface != None:
                self.radio_capture()
            elif self.capturefile != None:
                self.pcap_capture()
            else:
                _logger.critical("{}: no capture method supplied aborting!".format(self.process_id))


            if self.exit.is_set():
                self.flush_queue()

            self.q.close()
                
        except Exception as e:
            _logger.error("{}: Exception in pid {}\n{}".format(self.process_id, self.pid, e))

        _logger.info("{}: Exiting".format(self.process_id))


    def radio_capture(self):
        """

        """
        capture = pyshark.LiveCapture(interface=self.interface)
        for packet in capture.sniff_continuously():
            try:
                self.q.put(packet, timeout=10)
                _logger.debug("{}: produced packet {} Queue size is now {}".format(self.process_id, packet['gsmtap'].frame_nr, self.q.qsize()))
            except Full:
                _logger.warning("{}: cannot write to full Queue".format(self.process_id))
                sleep(1)


    def pcap_capture(self):
        """

        """
        if self.delay == None:
            _logger.warning("{}: no delay specified setting to default {}".format(self.process_id, DEFAULT_DELAY))
            self.delay = DEFAULT_DELAY

        capture = pyshark.FileCapture(self.capturefile)
        for packet in capture:
            if self.exit.is_set():
                _logger.debug("{}: Exit set aborting capture".format(self.process_id, packet['gsmtap'].frame_nr, self.q.qsize()))
                break

            try:
                self.q.put(packet, block=True, timeout=10)
                _logger.debug("{}: produced packet {} Queue size is now {}".format(self.process_id, packet['gsmtap'].frame_nr, self.q.qsize()))
                sleep(self.delay) # simulate wait
            except Full:
                _logger.warning("{}: cannot write to full Queue".format(self.process_id))

        _logger.info("{}: Capture Terminated".format(self.process_id))


    def shutdown(self):
        _logger.info("Anti: received shutdown command")
        self.exit.set()


    def flush_queue(self):
        _logger.debug("{}: Flushing the Queue".format(self.process_id))
        while True:
            try:
                self.q.get_nowait()
            except Empty:
                _logger.debug("{}: Queue empty".format(self.process_id))
                return



if __name__ == "__main__":
    Capture()
