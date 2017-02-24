from . import Event


class Lock:
    """
    Simple locker
    """

    def __init__(self, key=None):
        self.__locked = False
        self.__key = key

        obj_address = str(hex(id(self)))
        self.id = obj_address[:2] + obj_address[2:].upper()

        self.on_change = Event(name=f'Lock:{self.id}:change')
        self.on_acquire = Event(name=f'Lock:{self.id}:acquire')
        self.on_release = Event(name=f'Lock:{self.id}:release')

    @property
    def status(self):
        return self.__locked

    def __change(self, value):
        if value != self.__locked:
            self.on_change.trigger(value)
            if value:
                self.on_acquire.trigger()
            else:
                self.on_release.trigger()
        self.__locked = value

    def acquire(self, key=None):
        if self.__key and key != self.__key:
            raise LockError('Trying to lock secured Lock')
        if self.status:
            raise LockError('Trying to lock locked Lock')

        self.__change(True)

    def release(self, key=None):
        if self.__key and key != self.__key:
            raise LockError('Trying to unlock secured Lock')
        if not self.status:
            raise LockError('Trying to unlock unlocked Lock')

        self.__change(False)

    def check(self):
        if self.status:
            raise LockError('Resource is locked!')

    def do(self, func, args=None, kwargs=None):
        """
        Threading safe
        :param func:
        :param args:
        :param kwargs:
        :return:
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        def release():
            if not self.status:
                func(*args, **kwargs)
                self.on_release -= release

        if self.status:
            self.on_release += release
        else:
            func(*args, **kwargs)


class LockError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
