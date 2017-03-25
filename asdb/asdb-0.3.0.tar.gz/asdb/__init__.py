import socket
import errno
import sys
from os.path import join
import re
import inspect
from pprint import pprint


def find_port(host="127.0.0.1", port=6950, search_limit=100):
    for i in xrange(search_limit):
        _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        this_port = port + i
        try:
            _sock.bind((host, this_port))
        except socket.error as exc:
            if exc.errno in [errno.EADDRINUSE, errno.EINVAL]:
                continue
            raise
        else:
            save_port(this_port)
            return _sock, this_port
    else:
        raise NoAvailablePortException


def debugger():
    try:
        from celery import current_task
        print current_task
        if current_task:
            from celery.contrib.rdb import Rdb

            class Rdb2(Rdb):
                def get_avail_port(self, host, port_p, search_limit=100, skew=+0):
                    return find_port(host, port_p, search_limit)

            return Rdb2(port=6950)
    except ImportError:
        pass
    import rpdb
    sock, port = find_port()
    sock.close()
    return rpdb.Rpdb(port=port)


def save_port(port):
    path = join("/tmp/.asdb_port")
    with open(path, 'w') as portfile:
        portfile.write(str(port))
        portfile.flush()


def t():
    if not sys.gettrace():
        db = debugger()
        db.set_trace(sys._getframe(1))


set_trace = t


class NoAvailablePortException(Exception):
    pass


class _MagicPrinter(object):
    """
    >>> a = 'hello world how are you today'
    >>> b = [{1: 2}, a, [3] * 20]
    >>> magic_print('a b', x=1+2)
    <BLANKLINE>
    =================== a : ===================
    <BLANKLINE>
    'hello world how are you today'
    <BLANKLINE>
    <BLANKLINE>
    =================== b : ===================
    <BLANKLINE>
    [{1: 2},
     'hello world how are you today',
     [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]]
    <BLANKLINE>
    <BLANKLINE>
    =================== x : ===================
    <BLANKLINE>
    3
    <BLANKLINE>
    >>> magic_print.a.b  # doctest:+ELLIPSIS
    <BLANKLINE>
    =================== a : ===================
    <BLANKLINE>
    'hello world how are you today'
    <BLANKLINE>
    <BLANKLINE>
    =================== b : ===================
    <BLANKLINE>
    [{1: 2},
     'hello world how are you today',
     [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]]
    <BLANKLINE>
    <...._MagicPrinter object at ...>
    """

    @staticmethod
    def _print_variable(name):
        value = helpful_error_dict_get(inspect.currentframe().f_back.f_back.f_locals, name)
        _MagicPrinter._print_named_value(name, value)

    @staticmethod
    def _print_named_value(name, value):
        print('\n=================== %s : ===================\n' % name)
        pprint(value)
        print('')

    def __getattr__(self, item):
        try:
            self._print_variable(item)
        except KeyError as e:
            raise AttributeError(e.message)
        return self

    def __call__(self, names, **kwargs):
        for name in ensure_list_if_string(names):
            self._print_variable(name)
        for name, value in kwargs.items():
            self._print_named_value(name, value)


magic_print = _MagicPrinter()


def _helpful_dict_error(d, key):
    raise KeyError('Tried to access %r, only keys are: %s' % (key, str(sorted(d.keys()))[:1000]))


def helpful_error_dict_get(d, key):
    """
    >>> d = {1: 2, 3: 4}
    >>> helpful_error_dict_get(d, 'a')
    Traceback (most recent call last):
    ...
    KeyError: "Tried to access 'a', only keys are: [1, 3]"
    """
    try:
        return d[key]
    except KeyError:
        _helpful_dict_error(d, key)


def ensure_list_if_string(x):
    """
    >>> assert (ensure_list_if_string(['abc', 'def', '123']) ==
    ...         ensure_list_if_string('abc,def,123') ==
    ...         ensure_list_if_string('abc def 123') ==
    ...         ensure_list_if_string(', abc , def , 123  , ,') ==
    ...         ['abc', 'def', '123'])
    """
    if isinstance(x, basestring):
        x = list(filter(None, re.split('[,\s]+', x)))
    return x
