# coding=utf-8

from abc import ABCMeta
from abc import abstractmethod


class Session(metaclass=ABCMeta):
    """define HttpSession"""

    def __init__(self, session_id: str):
        assert session_id, 'session id is None'
        self.__id = session_id

    def __getitem__(self, item: str):
        return self.get(item)

    def __setitem__(self, key: str, value):
        return self.set(key, value)

    @abstractmethod
    def get(self, key: str):
        pass

    @abstractmethod
    def set(self, key: str, value):
        pass

    @abstractmethod
    def remove(self, key: str):
        pass

    @abstractmethod
    def available(self) -> bool:
        pass

    @property
    def id(self):
        return self.__id


class SessionManager(metaclass=ABCMeta):
    def __init__(self, time_to_live: int = 7200):
        """
        define Http SessionManager
        :param time_to_live:  session time to live in seconds,default is 7200
        """
        self.__time_to_live = time_to_live

    @property
    def time_to_live(self):
        return self.__time_to_live

    @abstractmethod
    def exists(self, session_id: str) -> bool:
        pass

    @abstractmethod
    def create(self) -> Session:
        pass

    @abstractmethod
    def get(self, session_id: str):
        pass

    @abstractmethod
    def remove(self, session_id: str):
        pass


class SessionError(RuntimeError):
    pass


class SessionStorageError(SessionError):
    pass
