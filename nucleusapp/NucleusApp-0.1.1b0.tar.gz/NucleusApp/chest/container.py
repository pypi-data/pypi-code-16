from NucleusUtils.events import Event
from NucleusUtils.events.lock import Lock

ROOT_MARK = '$'
TEMP_MARK = '#'


class Container:
    def __init__(self, name, chest=None):
        self.name = name
        self.chest = chest

        self.lock = Lock(self)
        self.__data = {}
        self.__locked_fields = []

        self.on_put = Event(name=str(self) + ':on_put', threaded=not name.startswith(ROOT_MARK))
        self.on_get = Event(name=str(self) + ':on_get', threaded=not name.startswith(ROOT_MARK))
        self.on_drop = Event(name=str(self) + ':on_drop', threaded=not name.startswith(ROOT_MARK))

        if self.name.startswith(TEMP_MARK):
            self.lock.acquire(self)

    def put(self, name, value):
        self.lock.check()
        if name in self.__locked_fields:
            raise KeyError(name)

        self.__data[name] = value
        self.on_put(name, value)

    def get(self, name, default=None):
        self.on_get(name, self.__data.get(name, default))
        return self.__data.get(name, default)

    def drop(self, name):
        """
        Drop element by name
        :param name:
        :return:
        """
        self.lock.check()
        if name in self.__locked_fields:
            raise KeyError(name)

        del self.__data[name]
        self.on_drop(name)

    def clear(self):
        """
        Clear container
        :return:
        """
        self.lock.check()
        self.lock.acquire(self)
        for key in self.__data:
            if key not in self.__locked_fields:
                del self.__data[key]
        self.lock.release(self)

    def items(self):
        return self.__data.items()

    def keys(self):
        return self.__data.keys()

    def values(self):
        return self.__data.values()

    def lock_filed(self, field_name):
        self.lock.check()
        if field_name not in self.__locked_fields:
            self.__locked_fields.append(field_name)

    def lock_fields(self, *field_names):
        for field_name in field_names:
            self.lock_filed(field_name)

    def unlock_field(self, field_name):
        self.lock.check()
        if field_name not in self.__locked_fields:
            raise KeyError(field_name)
        self.__locked_fields.remove(field_name)

    def unlock_fields(self, *field_names):
        for field_name in field_names:
            self.unlock_field(field_name)

    def __enter__(self):
        if self.name.startswith(TEMP_MARK):
            self.lock.release(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.name.startswith(TEMP_MARK):
            self.lock.acquire(self)
            self.clear()
            if self.chest:
                self.chest.destroy(self.name)

    def __call__(self, name, default=None):
        return self.get(name, default)

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.put(key, value)

    def __delitem__(self, key):
        self.drop(key)

    def __iter__(self):
        return self.__data.items()

    def __str__(self):
        if self.lock.status:
            lock_status = ':locked'
        else:
            lock_status = ''

        if self.chest:
            chest = str(self.chest) + '.'
        else:
            chest = ''
        return f"Container: {chest}{self.name}({len(self)}){lock_status}"

    def __len__(self):
        return len(self.__data)
