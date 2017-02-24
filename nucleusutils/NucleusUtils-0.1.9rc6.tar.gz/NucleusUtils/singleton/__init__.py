class Singleton(type):
    """
    Simple metaclass for writing code with singleton pattern.

    example:
    >>> class Test(metaclass=Singleton):
    >>>     def __init__(self, name):
    >>>         self.name = name
    >>>
    >>>     def __str__(self):
    >>>         return self.name
    >>>
    >>>
    >>> foo = Test('foo')
    >>> bar = Test('bar')
    >>>
    >>> print(foo)
    >>> print(bar)
        out:
        foo
        foo
    """
    __instances__ = {}

    @property
    def instance(cls):
        if cls not in cls.__instances__:
            raise RuntimeError('Singleton instance is not inited!')
        return cls.__instances__[cls]

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances__:
            cls.__instances__[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance
