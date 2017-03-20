__version__ = '1.2'


def try_default(expr, default):
    """
    Function variant of try-except clause with default value on
    exception.

    Allows inline replacement for cases such as:

    .. code-block:: python

        empty_list = []

        try:
            foo = empty_list[1]
        except IndexError:
            foo = 0

    If the raised exception is not in ``default``, it will be
    re-raised.

    :param Function expr: Intended to be a lazy expression,
                          implemented as a function.
    :param dict default: Example: ``{IndexError: 0}``
    :return: Result of calling ``expr``. On exception this will
             be the specified default value.
    """

    import six

    try:
        return expr()
    except BaseException as e:
        # This can't easily be achieved using `__getitem__` without
        # breaking any exception hierarkies. That's why we're
        # looping over `default` instead. That way, we can have
        # Python do the hard OOP work by using `isinstance`.
        for key, value in six.iteritems(default):
            if isinstance(e, key):
                return value

        # Re-raise unhandled exceptions.
        raise
