#!/usr/bin/env python

'''
MessageForwarder.py
zmq Device for forwarding messages
----------------------------------

Copyright 2016 Davide Mastromatteo
License: Apache-2.0
'''

import threading

import zmq
from zmq.devices import ThreadDevice

import flows.Global


class MessageForwarder():
    """
    MessageForwarder class
    Messages forwarder device for 0mq
    """
    _instance = None
    _instance_lock = threading.Lock()
    context = None
    frontend = None
    backend = None

    @classmethod
    def default_instance(cls):
        """For use like a singleton, return the existing instance of the object or a new instance"""
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = MessageForwarder()

        return cls._instance

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def start_forwarder(self):
        """
        Start 0mq forwarder device
        """
        try:
            self.context = zmq.Context()
            my_device = ThreadDevice(
                zmq.FORWARDER, zmq.SUB, zmq.PUB)
            my_device.daemon = True
            my_device.bind_in(
                flows.Global.CONFIG_MANAGER.publisher_socket_address)
            my_device.setsockopt_in(
                zmq.SUBSCRIBE, b'')
            my_device.bind_out(
                flows.Global.CONFIG_MANAGER.subscriber_socket_address)
            my_device.start()
        except Exception as exc:
            print("***" + exc)
        finally:
            if self.frontend is not None:
                self.frontend.close()

            if self.backend is not None:
                self.backend.close()

    def stop_forwarder(self):
        """
        Stop 0mq forwarder device
        """
        if self.frontend is not None:
            self.frontend.close()

        if self.backend is not None:
            self.backend.close()
