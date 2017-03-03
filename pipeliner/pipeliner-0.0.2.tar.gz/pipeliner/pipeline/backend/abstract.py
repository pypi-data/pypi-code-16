from abc import ABCMeta, abstractmethod, abstractproperty
from six import with_metaclass


class AbstractBackend(with_metaclass(ABCMeta, object)):
    @abstractmethod
    def run(self, target, *args, **kwargs):
        pass

    @abstractmethod
    def wait_until_complete(self):
        pass
