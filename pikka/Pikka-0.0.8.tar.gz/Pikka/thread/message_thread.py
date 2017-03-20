import threading

import Pyro4

from Pikka.actor.actor_manager import ActorManager


class MessageThread(threading.Thread):

    action = None
    args = None
    kwargs = None

    def __init__(self, action, *args, **kwargs):
        threading.Thread.__init__(self)
        self.action = action
        self.args = args
        self.kwargs = kwargs

    def run(self):
        manager = ActorManager()
        for actor in manager.all_actions():
            uri = Pyro4.URI(actor.uris[self.action])
            try:
                proxy = Pyro4.Proxy(uri)
                async = Pyro4.async(proxy)
                result = async.message(*self.args, **self.kwargs)
                print(result.value)
            except Exception as e:
                print('error message action "{}" to {}'.format(self.action, uri))
                print(e)
