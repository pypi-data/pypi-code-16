import threading

import Pyro4
import time


class RegisterThread(threading.Thread):

    master_host = None
    uris = {}

    def __init__(self, master_host, uris):
        threading.Thread.__init__(self)
        self.master_host = master_host
        self.uris = uris

    def run(self):
        time.sleep(3)
        try:
            proxy = Pyro4.Proxy(Pyro4.URI('PYRO:base@{0}'.format(self.master_host)))
            result = proxy.register(uris=self.uris)
            print('register actor to {} : {}'.format(self.master_host, result))
        except Exception as e:
            print('error register actor to {} : {}'.format(self.master_host, e))
