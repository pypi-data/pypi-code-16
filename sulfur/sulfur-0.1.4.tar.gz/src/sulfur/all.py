"""
API and initialized objects useful for interactive use.
"""


from sulfur.delayed import Delayed as _delay
from sulfur.driver import Driver
from sulfur.testserver import TestServer
from sulfur.client import Client


# Web browsers
chrome = _delay(Driver, 'chrome')
firefox = _delay(Driver, 'firefox')


# File Client
server = _delay(TestServer, port=8080)


# File _client
client = _delay(Client)
