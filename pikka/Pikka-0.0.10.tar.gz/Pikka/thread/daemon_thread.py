import threading
import Pyro4
from Pikka.action.base_action import BaseAction


class ServerThread(threading.Thread):
    daemon = None
    config = None
    uris = {}

    def __init__(self, actions, **kwargs):
        threading.Thread.__init__(self)
        self._config = kwargs
        self.actions = actions

    def run(self):
        self.daemon = Pyro4.Daemon(**self._config)
        base_uri = self.daemon.register(BaseAction, objectId='base')
        self.uris['_BASE'] = Pyro4.URI(base_uri)

        # register actions
        for key in self.actions:
            uri = self.daemon.register(self.actions[key], objectId=key)
            self.uris[key] = Pyro4.URI(uri)

        print("Ready. Object uri = {0}".format(base_uri))
        print(self.uris)

        self.config = Pyro4.config
        self.daemon.requestLoop()
