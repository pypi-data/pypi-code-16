from .graphObject import GraphObject


class DataObjectSingleton(GraphObject):
    instance = None

    def __init__(self, *args, **kwargs):
        if type(self)._gettingInstance:
            super(DataObjectSingleton, self).__init__(*args, **kwargs)
        else:
            raise Exception(
                "You must call getInstance to get " +
                type(self).__name__)

    @classmethod
    def getInstance(cls):
        if cls.instance is None:
            cls._gettingInstance = True
            cls.instance = cls()
            cls._gettingInstance = False

        return cls.instance


