#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" decoder.py

Unwrap the pyshark packets and put the needed data into the database.

"""
import logging
import multiprocessing as mp


from random import random
from queue import Empty
from multiprocessing import Process, Queue

_logger = logging.getLogger(__name__)

try:
    import sqlitedict
except ImportError as e:
    _logger.error("Decoder: {}".format(e))
    _logger.info("Decoder: Maybe try `pip install -r requirements.txt'")
    sys.exit(1)


class Decoder(Process):
    """ Decode and store the packets for analysis.

    """

    def __init__(self, process_id, q, *args, **kwargs):
        super(Decoder, self).__init__(*args, **kwargs)
        self.process_id = process_id
        self.q = q
        self.exit = mp.Event()


    def run(self):
        """

        """
        _logger.debug("{}: Process started successfully".format(self.process_id))
        while not self.exit.is_set():
            try:
                packet = self.q.get(timeout=10)
                _logger.debug("{}: Consumed packet Queue size is now {}".format(self.process_id, self.q.qsize()))
                self.decode_packet(packet)
                self.store_packet(packet)
            except Empty:
                _logger.info("{}: Queue empty".format(self.process_id))
        _logger.info("{}: Exiting".format(self.process_id))


    def decode_packet(self, packet):
        """ Get only the needed attributes from the packet.

        """
        _logger.debug("{}: Decoding packet {}".format(self.process_id, packet['gsmtap'].frame_nr))
        pass


    def store_packet(self, packet):
        """ Put packet into database.

        """
        _logger.debug("{}: Storing packet {}".format(self.process_id, packet['gsmtap'].frame_nr))
        pass


    def shutdown(self):
        _logger.info("{}: Recieved shutdown command".format(self.process_id))
        self.exit.set()




if __name__ == "__main__":
    Decoder()
