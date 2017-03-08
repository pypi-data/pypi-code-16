from NucleusApp.chest import Chest
from NucleusApp.chest.container import Container


class ChestContext:
    chest = 'root'

    @classmethod
    def get_container(cls) -> Container:
        return Chest()[cls.chest]

    def __enter__(self):
        return self.get_container()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class ContainerContext:
    chest = 'root'
    element = 'app'

    @classmethod
    def get_object(cls):
        return Chest()[cls.chest][cls.element]

    def __enter__(self):
        return self.get_object()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
