import Pyro4
import psutil

from Pikka.actor.actor import Actor
from Pikka.actor.actor_manager import ActorManager


@Pyro4.expose
class BaseAction(object):

    def heartbeat(self):
        memory_info = psutil.virtual_memory()
        cpu_times_info = psutil.cpu_times()
        disk_info = psutil.disk_usage('/')
        return {'memory_info': memory_info,
                'cpu_times_info': cpu_times_info,
                'disk_info': disk_info}

    def register(self, uris):
        actor_manager = ActorManager()
        actor = Actor(host=uris['_BASE'], uris=uris)
        return actor_manager.register(actor)
