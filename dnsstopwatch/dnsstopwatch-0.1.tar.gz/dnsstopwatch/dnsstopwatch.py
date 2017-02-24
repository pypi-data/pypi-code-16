import socket
import time

class DnsStopwatch(object):

    def __init__(self):
        self.executed_queries = []

    def __call__(self, host="www.example.com"):
        start_time = time.time()
        ip_address = socket.gethostbyname(host)
        delta_time = "{0:.5f}".format(time.time() - start_time)
        self.executed_queries.append((host, ip_address, delta_time))
        return delta_time

    def history(self):
        return self.executed_queries

    def clear_history(self):
        self.executed_queries = []
