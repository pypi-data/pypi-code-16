# -*- coding: utf-8 -*-
'''
f-strings...sorta
=================
'''
__all__ = ['f', 'fdocstring', 'printf']
__author__ = 'Dan Bradham'
__email__ = 'danielbradham@gmail.com'
__license__ = 'MIT'
__title__ = 'fstrings'
__url__ = 'https://github.com/danbradham/fstrings'
__version__ = '0.1.0'

import sys
from inspect import currentframe, getmro, isclass, isfunction


def f(s, *args, **kwargs):
    '''
    Sort of f-strings. Passes the calling frames globals and locals to
    str.format instead of evaluating code in braces. Also supports positional
    arguments and keyword arguments via str.format. If kwargs are passed in
    they will take precedence over globals and locals.

    :param args: Optional positional format args
    :param kwargs: Optional format kwargs
    :param _frame_: Optional kwarg - frame used to retrieve locals and globals

    Usage::

        >>> x = "Hello, World!"
        >>> f('{x}')
        'Hello, World!'
    '''

    frame = kwargs.pop('_frame_', currentframe().f_back)
    return s.format(*args, **dict(frame.f_globals, **dict(frame.f_locals, **kwargs)))


def fdocstring(*args, **kwargs):
    '''
    Formats the docstrings of the decorated function or class using globals
    and locals. Also supports positional arguments and keyword arguments
    via str.format. If kwargs are passed in they will take precedence over
    globals and locals. Runs once at execution time, so it has ZERO impact
    on the performance of your class or function.

    :param args: Optional positional format args
    :param kwargs: Option keyword format args
    :param _frame_: Optional kwarg - frame used to retrieve locals and globals

    Usage::

        >>> x = 'Hello from fdocstring'
        >>> @fdocstring()
        ... def func():
        ...     \'\'\'{x}\'\'\'
        ...
        >>> func.__doc__
        'Hello from fdocstring'
    '''

    def do_fdocstring(obj):

        frame = kwargs.pop('_frame_', currentframe().f_back)
        fkwargs = dict(frame.f_globals, **frame.f_locals)

        if isfunction(obj):
            obj.__doc__ = obj.__doc__.format(*args, **dict(fkwargs, **kwargs))

        if isclass(obj):
            bases = getmro(obj)
            for cls in bases[::-1]:
                fkwargs.update(cls.__dict__)
            fkwargs.update(**kwargs)
            attrs = dict(obj.__dict__)
            attrs['__doc__'] = obj.__doc__.format(*args, **fkwargs)

            for k, v in attrs.items():
                if isfunction(v):
                    v.__doc__ = v.__doc__.format(*args, **fkwargs)

            obj = type(obj.__name__, tuple(bases[1:]), attrs)
        return obj

    return do_fdocstring


def printf(s, *args, **kwargs):
    '''
    Write `f(s, *args, **kwargs)` to sys.stdout

    :param args: Optional positional format args
    :param kwargs: Option keyword format args
    :param _stream_: Optional kwarg - Write to this stream instead of sys.stdout

    Usage::

        >>> x = 'Hello from printf'
        >>> printf('{x}')
        Hello from printf
    '''

    kwargs['_frame_'] = currentframe().f_back
    stdout = kwargs.pop('_stream_', sys.stdout)
    stdout.write(f(s + '\n', *args, **kwargs))
