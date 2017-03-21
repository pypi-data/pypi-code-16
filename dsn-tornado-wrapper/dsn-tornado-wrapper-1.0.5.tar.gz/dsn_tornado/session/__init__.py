# coding=utf-8


class Session:
    """define HttpSession"""

    def __init__(self, session_id: str):
        assert session_id, 'session id is None'
        self.__id = session_id

    def __getitem__(self, item: str):
        return self.get(item)

    def __setitem__(self, key: str, value):
        return self.set(key, value)

    def contains_key(self, key: str) -> bool:
        pass

    def get_string(self, key: str, encoding='UTF-8') -> str:
        pass

    def get_integer(self, key: str, base: int = 10) -> int:
        pass

    def get(self, key: str):
        pass

    def set(self, key: str, value):
        pass

    def remove(self, key: str):
        pass

    def available(self) -> bool:
        pass

    @property
    def id(self):
        return self.__id


class SessionManager:
    def __init__(self, time_to_live: int = 7200):
        """
        define Http SessionManager
        :param time_to_live:  session time to live in seconds,default is 7200
        """
        self.__time_to_live = time_to_live

    @property
    def time_to_live(self):
        return self.__time_to_live

    def exists(self, session_id: str) -> bool:
        pass

    def create(self) -> Session:
        pass

    def get(self, session_id: str):
        pass

    def remove(self, session_id: str):
        pass


class SessionError(RuntimeError):
    pass


class SessionStorageError(SessionError):
    pass
