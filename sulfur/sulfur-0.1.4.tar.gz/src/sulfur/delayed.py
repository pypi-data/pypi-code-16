def delayed_method(name):
    def method(self, *args, **kwargs):
        self._touch()
        method = getattr(self, name)
        return method(*args, **kwargs)

    return method


class Inert:
    """
    A class that does nothing
    """


class Delayed:
    """
    Delayed initialization of object.

    It may not work will all objects.
    """
    __subclasses = {}

    def __init__(self, cls, *args, **kwargs):
        self.__cls = cls
        self.__args = args
        self.__kwargs = kwargs

    def _touch(self):
        cls = self.__cls
        obj = cls(*self.__args, **self.__kwargs)
        cls = obj.__class__
        for k, v in list(obj.__dict__.items()):
            setattr(self, k, v)
            delattr(obj, k)

        try:
            obj.__del__()
        except:
            pass
        finally:
            obj.__class__ = Inert

        self.__class__ = cls

    def __getattr__(self, attr):
        self._touch()
        return getattr(self, attr)


for _name in ['repr', 'str', 'getitem', 'setitem', 'len', 'iter']:
    _name = '__%s__' % _name
    setattr(Delayed, _name, delayed_method(_name))
