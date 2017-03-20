import Pyro4
from Pyro4.errors import CommunicationError
from Pikka.core.singleton import Singleton


class ActorManager(metaclass=Singleton):

    def __init__(self):
        self.actors = []

    def register(self, actor):

        # check same actor
        for _actor in self.actors:
            if _actor.host == actor.host:
                return "already has this actor"

        # register actor
        self.actors.append(actor)
        print("register {0}".format(actor))

        return "success"

    def check_heartbeat(self):
        for actor in self.actors:
            try:
                # Success
                proxy = Pyro4.Proxy(actor.uris['_BASE'])
                result = proxy.heartbeat()
                actor.info = result
            except CommunicationError as e:
                self.actors.remove(actor)
                print("lost actor {0}".format(actor))
            except KeyError as e:
                self.actors.remove(actor)
                print("actor has no _heartbeat action".format(actor))


    def all_actions(self):
        return self.actors
