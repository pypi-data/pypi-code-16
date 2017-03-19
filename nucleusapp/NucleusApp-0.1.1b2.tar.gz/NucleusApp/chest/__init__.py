import uuid

from NucleusUtils.singleton import Singleton

from .container import Container


class Chest(Singleton):
    """
    Is storage for containers
    """

    def __init__(self):
        self.__containers = {}

    def get(self, name):
        """
        Get container by name
        :param name:
        :return:
        """
        if name not in self.__containers:
            self.__containers[name] = Container(name, self)
        return self.__containers.get(name)

    def destroy(self, key):
        """
        Remove container
        :param key:
        :return:
        """
        if key not in self.__containers:
            raise KeyError(key)

        container = self.get(key)
        container.lock.check()
        del self.__containers[key]

    def remove_trash(self):
        """
        Remove empty unlocked containers
        :return:
        """
        for container in self.__containers:
            if not container.lock.status and not len(container):
                self.destroy(container.name)

    @property
    def root(self) -> Container:
        """
        Get root container
        :return:
        """
        return self.get('$root')

    @property
    def temp(self, name) -> Container:
        """
        Get temporary container. It may be conflict with multi threading
        :return:
        """
        return self.get(f'#{name}::{str(uuid.uuid4())}')

    def items(self):
        """
        Iter items
        :return:
        """
        return self.__containers.items()

    def iter_all(self):
        """
        Iter all elements
        :return:
        """
        for name, container in self.items():
            for key, value in container.items():
                yield name, key, value

    def __call__(self, name=None):
        if name is not None:
            return self.get(name)

    def __iter__(self):
        return self.__containers.values()

    def __getitem__(self, item) -> Container:
        return self.get(item)

    def __delitem__(self, key):
        self.destroy(key)

    def __len__(self):
        return sum(len(container) for container in self.__containers.values())

    def __str__(self):
        return 'Сhest(' + str(len(self.__containers)) + ':' + str(len(self)) + ')'
