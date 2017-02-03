#!/usr/bin/env python

'''
MessageDispatcher.py
Class to handle the dispatching of zmq messages
-----------------------------------------------

Copyright 2016 Davide Mastromatteo
License: Apache-2.0
'''

import datetime
import pickle
import sys
import threading
import time

import zmq

from flows import Global


class MessageDispatcher:
    """
    MessageDispatcher class
    Messages broadcaster
    """

    _instance = None
    _instance_lock = threading.Lock()
    context = None
    socket = None
    dispatched = 0
    last_stat = datetime.datetime.now()

    @classmethod
    def default_instance(cls):
        """For use like a singleton, return the existing instance of the object
        or a new instance"""
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = MessageDispatcher()

        return cls._instance

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Global.LOGGER.debug(
            "The message dispatcher is going to be initialized")

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)

        Global.LOGGER.info(
            "Configuring the socket address for messaging subsystem")
        for attempt in range(0, 6):
            try:
                Global.CONFIG_MANAGER.set_socket_address()
                self.socket.bind(
                    Global.CONFIG_MANAGER.publisher_socket_address)
                break
            except zmq.error.ZMQError:
                if attempt == 5:
                    Global.LOGGER.error(
                        "Can't find a suitable tcp port to connect. "
                        + "The execution will be terminated")
                    sys.exit(8)

                Global.LOGGER.warning(
                    str.format("An error occured trying to connect to {0} ",
                               Global.CONFIG_MANAGER.publisher_socket_address))

                Global.LOGGER.warning(
                    str.format("retrying... ({0}/{1})",
                               attempt + 1, 5))

                time.sleep(1)

        time.sleep(0.2)

        Global.LOGGER.debug("The message dispatcher has been initialized")

    def send_message(self, message):
        """
        Dispatch a message using 0mq
        """

        with self._instance_lock:
            if message is None:
                return

            if message.sender is None:
                Global.LOGGER.error("sender NOT set!")
                return

            if message.receiver is None:
                Global.LOGGER.error("receiver NOT set!")
                return

            if message.message is None:
                Global.LOGGER.debug("be careful, the message from "
                                      + str(message.sender)
                                      + " to "
                                      + str(message.receiver)
                                      + " has NOT been set")
                return
            # print("-> " + message.sender + "-" + message.message + "-" + message.to)
            sender = "*" + message.sender + "*"
            self.socket.send_multipart(
                [bytes(sender, 'utf-8'), pickle.dumps(message)])

            # if message.message.strip() != "*** loopback ***":
            Global.LOGGER.debug("Dispatched : "
                                + message.sender
                                + "-"
                                + message.message
                                + "-"
                                + message.receiver)

            self.dispatched = self.dispatched + 1
            if self.dispatched % 1000 == 0:
                Global.LOGGER.debug(str.format("zmq has dispatched {0} messages",
                                               self.dispatched))
                self.adapt_sleep_interval()

    def adapt_sleep_interval(self):
        '''adapt sleep time based on the number of the messages dispatched'''
        Global.LOGGER.debug("Adjusting sleep interval")
        now = datetime.datetime.now()
        seconds = (now - self.last_stat).total_seconds()

        sleep_time = (seconds / self.dispatched) * 0.75

        if sleep_time > 0.09:
            sleep_time = 0.09

        if sleep_time < 0.0001:
            sleep_time = 0.0001

        self.last_stat = now
        self.dispatched = 0

        Global.CONFIG_MANAGER.sleep_interval = sleep_time
        Global.LOGGER.info(str.format("New sleep_interval = {0} ",
                                       Global.CONFIG_MANAGER.sleep_interval))
