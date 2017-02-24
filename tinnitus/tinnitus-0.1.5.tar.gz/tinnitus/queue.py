import threading


class Queue(object):

    __lock = threading.Lock()
    __items = dict({})
    __queue = []
    __current = None

    def __init__(self): pass

    @property
    def current(self):
        mrl = backend = None

        with self.__lock:
            resource_id = self.__current

            if resource_id is not None:
                mrl = self.__items[resource_id]["mrl"]
                backend = self.__items[resource_id]["backend"]

        return resource_id, mrl, backend

    @property
    def queue(self):
        with self.__lock:
            queue = self.__queue
        return queue

    def add(self, resource_id: int, mrl: str, backend: str) -> None:
        with self.__lock:
            self.__queue.append(resource_id)
            self.__items[resource_id] = {"mrl": mrl, "backend": backend}

    def remove(self, resource_id: int) -> None:
        with self.__lock:
            if resource_id in self.__items.keys():
                self.__queue.remove(resource_id)
                del self.__items[resource_id]

    def clear(self):
        with self.__lock:
            self.__items = dict({})
            self.__queue = []
            self.__current = None

    def next(self):
        with self.__lock:
            if self.__current is not None:
                del self.__items[self.__current]

            if len(self.__queue) > 0:
                self.__current = self.__queue.pop(0)

            else:
                self.__current = None

    def put_back(self):

        with self.__lock:
            self.__queue.insert(0, self.__current)
            self.__current = None
