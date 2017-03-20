from Pikka.core.singleton.singleton import Singleton
from Pikka.thread.daemon_thread import ServerThread

from Pikka.thread.manager_thread import ManagerThread
from Pikka.thread.message_thread import MessageThread
from Pikka.thread.register_thread import RegisterThread


class Pikka(metaclass=Singleton):

    server_thread = None
    manager_thread = None

    def __init__(self, actions, master=False, master_host='localhost:9000', **kwargs):
        self.__server__(actions=actions, **kwargs)
        if master_host and master:
            self.__manager__()
        else:
            self.__register_action(master_host)

    def __server__(self, actions, **kwargs):
        # server thread
        self.server_thread = ServerThread(actions=actions, **kwargs)
        # self.server_thread.daemon = True
        self.server_thread.start()
        print("Pyro4 Daemon Server start")

    def __manager__(self):
        self.manager_thread = ManagerThread()
        self.manager_thread.start()
        print("manager thread start")

    def __register_action(self, master_host):
        register_thread = RegisterThread(master_host=master_host, uris=self.server_thread.uris)
        register_thread.start()

    def message(self, action, *args, **kwargs):
        message_thread = MessageThread(action, *args, **kwargs)
        message_thread.start()


