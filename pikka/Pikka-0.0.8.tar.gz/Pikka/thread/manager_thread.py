import threading
import time
from Pikka.actor.actor_manager import ActorManager


class ManagerThread(threading.Thread):
    manager = None

    def __init__(self):
        super().__init__()
        self.daemon = True
        self.manager = ActorManager()

    def run(self):
        while True:
            time.sleep(5)
            self.manager.check_heartbeat()
            print(self.manager.all_actions())
            pass


