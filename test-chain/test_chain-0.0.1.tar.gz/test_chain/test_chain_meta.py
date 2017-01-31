"""
    This module will create a metaclass that enables automatic chaining
    of unittests within other functions, done by wrapping each function
    within the class that begins with 'test_' with the decorator
    @skip_if_already_done
"""
__author__ = 'Michael Christenson'
__date__ = "1/3/2017"
import os
import sys
import inspect
from functools import wraps
import unittest

def currentframe():
    """Return the frame of the caller or None if this is not possible."""
    return sys._getframe(1) if hasattr(sys, "_getframe") else None


def function_arguments(func):
    """
    :param func: callable object
    :return: list of str of the arguments for the function
    """
    if getattr(inspect, 'signature', None) is None:
        return inspect.getargspec(func).args
    else:
        return list(inspect.signature(func).parameters.keys())


def skip_if_already_done(func, skip_args=1):
    """ This will store the results and return them if the function is called twice """
    results = {}
    func_args = function_arguments(func)

    @wraps(func)
    def done_decorators(*args, **kwargs):
        hash_kwargs = dict([[func_args[i], args[i]] for i in range(skip_args, len(args))])
        hash_kwargs.update(kwargs)
        hash_ = ', '.join(['%s=%s' % (arg, hash_kwargs[arg]) for arg in sorted(hash_kwargs.keys())])
        if hash_ not in results:
            try:
                results[hash_] = func(*args, **kwargs)
            except unittest.SkipTest as e:
                results[hash_] = e
                raise
            except Exception as e:
                results[hash_] = e
                history = function_history()
                if history.count('done_decorators') == 1:  # determine if this is the original test
                    raise

        if isinstance(results[hash_], Exception):
            history = function_history()
            if history.count('done_decorators') != 1:  # determine if this is the original test
                raise unittest.SkipTest('%s threw the exception %s' % (func.__name__, results[hash_]))
            raise results[hash_]
        return results[hash_]

    return done_decorators


def function_history():
    """
    This will return a list of all function calls going back to the beginning
    :return: list of str of function name
    """
    ret = []
    frm = currentframe()
    for i in range(100):
        try:
            if frm.f_code.co_name != 'run_code':  # this is pycharm debugger inserting middleware
                ret.append(frm.f_code.co_name)
            frm = frm.f_back
        except Exception as e:
            break
    return ret


class TestChainMeta(type):
    def __new__(cls, name, bases, attrs):
        """
        This will search for the functions within the class that begin with 'test_' and wrap them with
        @skip_if_already_done if a class uses this one as a metaclass
        :return: the modified class
        """
        class_ = type.__new__(cls, name, bases, attrs)
        ref = class_.__dict__
        ring = list(ref.keys())
        for i in range(len(ring)):
            key = ring[i]
            original_func = getattr(class_, key, None)
            if (key.startswith('test_') and getattr(original_func, 'original_func', None) is None and
                    (inspect.ismethod(original_func) or inspect.isfunction(original_func))):
                new_func = skip_if_already_done(original_func)
                new_func.original_func = original_func
                setattr(class_, key, new_func)
        return class_
