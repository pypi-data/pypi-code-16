from uuid import UUID, uuid4
from abc import ABCMeta, abstractmethod



class Request(metaclass=ABCMeta):
    
    def __init__(self) -> None:
        self._requestid = uuid4()
    
    @property
    def id(self) -> UUID:
        return self._requestid
    
    @staticmethod
    def is_aCommand() -> bool:
        return False
    
