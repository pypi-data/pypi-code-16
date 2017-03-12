from ea.event.transport.base import BaseTransport
from ea.event.transport.delivery import NullDelivery
from ea.event.transport.adapter import DictAdapter


class NullTransport(BaseTransport):

    def __init__(self):
        super(NullTransport, self).__init__(DictAdapter())

    def send(self, event):
        return NullDelivery()
