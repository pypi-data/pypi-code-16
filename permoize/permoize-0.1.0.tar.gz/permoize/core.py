# -*- coding: utf-8 -*-

from functools import wraps
from inspect import getargspec, getmodule
from diskcache import Cache


def qualified_name(x):
    return '{}.{}'.format(getmodule(x).__name__, x.__name__)


def permoize(cache_dir, explicit=False):
    def decorator(fn):
        arg_spec = getargspec(fn)

        nb_pos_args = len(arg_spec.args)

        @wraps(fn)
        def wrapper(*args, **kwargs):
            nb_args = len(args)
            nb_pos_args_without_val = nb_pos_args - nb_args

            if arg_spec.defaults and nb_pos_args_without_val > 0:
                args += arg_spec.defaults[-nb_pos_args_without_val:]

            desc = {'fn': qualified_name(fn),
                    'args': args,
                    'kwargs': kwargs}

            val, fn_was_executed = None, False

            with Cache(cache_dir) as cache:
                try:
                    val = cache[desc]
                except KeyError:
                    val = fn(*args, **kwargs)
                    fn_was_executed = True
                    cache[desc] = val

            if explicit:
                return val, fn_was_executed

            return val

        return wrapper

    return decorator
