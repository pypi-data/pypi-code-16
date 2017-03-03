import logging
import threading

from ws4py.client import WebSocketBaseClient


log = logging.getLogger('m2m')


class M2MSocket(WebSocketBaseClient):
    pass


class WSThread(object):

    def __init__(self, url, exit_event):
        self.url = url
        self.exit_event = exit_event

    def run(self):
        while True:
            ws = M2MSocket()
            ws.connect()

            ws.sock.recv()





