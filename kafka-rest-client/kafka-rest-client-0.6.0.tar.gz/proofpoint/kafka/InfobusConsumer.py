import abc

import six


@six.add_metaclass(abc.ABCMeta)
class InfobusConsumer():
    def __init__(self):
        pass

    @abc.abstractmethod
    def subscribe(self, topic):
        pass

    @abc.abstractmethod
    def poll(self):
        pass

    @abc.abstractmethod
    def commit(self):
        pass

    @abc.abstractmethod
    def close(self):
        pass
