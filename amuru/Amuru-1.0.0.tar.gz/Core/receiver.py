from abc import ABCMeta, abstractmethod
from Core.request import Request

class Receiver(metaclass=ABCMeta):

    @abstractmethod
    def execute(self, request:Request) -> None:
        pass
