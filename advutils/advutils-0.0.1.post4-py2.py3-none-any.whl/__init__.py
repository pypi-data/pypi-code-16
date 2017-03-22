#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2017 David Toro <davsamirtor@gmail.com>
"""

"""
# compatibility with python 2 and 3
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

#__all__ = []
__author__ = "David Toro"
#__copyright__ = "Copyright 2017, The <name> Project"
#__credits__ = [""]
__license__ = "BSD-3-Clause"
__version__ = "0.0.1.post4"
__maintainer__ = "David Toro"
__email__ = "davsamirtor@gmail.com"
#__status__ = "Pre-release"

# import build-in modules
import sys
import copy
import inspect
from six import reraise as raise_
#from future.utils import raise_
from time import time as _time, gmtime as _gmtime

# ----------------------------Exceptions---------------------------- #


class TimeOutException(Exception):
    """
    Raise an exception when a process surpasses the timeout
    """


class TransferExeption(Exception):
    """
    Raise an exception when transfered data is corrupt
    """


class VariableNotSettable(Exception):
    """
    Exception for property not settable
    """


class VariableNotDeletable(Exception):
    """
    Exception for property not deletable
    """


class VariableNotGettable(Exception):
    """
    Exception for property not gettable
    """


class VariableNotAvailable(Exception):
    """
    Exception for variable that is not available
    """


class NotConvertibleToInt(ValueError):
    """
    Exception to denote that value cannot be represented as int
    """


class ClassNotAllowed(Exception):
    """
    Exception to denote that given class is not allowed
    """


class NotCreatable(Exception):
    """
    Defines objectGetter error: objectGetter cannot create new object.
    """


class NotCallable(Exception):
    """
    Defines objectGetter error: given object is not callable.
    """


class NoParserFound(Exception):
    """
    Raise when no parser is found to use in a shell i.e to interpret user
    input
    """


class CorruptPersistent(EOFError, IOError):
    """
    Used for persistent data read from disk like pickles to denote
    it has been corrupted
    """
# ----------------------------GLOBAL VARIABLES---------------------------- #


class NameSpace(object):
    """
    Used to store variables
    """

# ----------------------------UTILITY FUNCTIONS---------------------------- #


def try_func(func):
    """
    Sandbox to run a function and return its values or any produced error.

    :param func: testing function
    :return: results or Exception
    """
    try:
        return func()
    except Exception as e:
        return e

def _helper_parameters(func, args=(), kwargs=None, onlykeys=False, onlyused=False):
    """
    Helper to get all a function parameters.

    :param func: function to get parameters from
    :param args: arguments to modify
    :param kwargs: key arguments to modify
    :param onlykeys: return only key arguments
    :param onlyused: return only modified arguments
    :param default: default value to assign to key arguments
    :return: adds, params, kwargs
    """
    if kwargs is None:
        kwargs = {}
    # params = list(inspect.signature(self.__init__).parameters.keys())
    params = inspect.getargspec(func).args[1:]  # TODO replace deprecated getargspec to work with py2 and py3, perhaps by getfullargspec

    if onlykeys and not onlyused:  # only add to keywords
        covered = 0  # simulate no args
    else:
        covered = len(args)

    if onlyused and onlykeys:  # only add modified by user
        adds = [(True if i < covered or key in kwargs else False) for i, key in
                enumerate(params)]
        # add keys from args
        for i, val in enumerate(args):
            kwargs[params[i]] = val
    elif onlyused:
        adds = [(True if i >= covered and key in kwargs else False) for i, key
                in
                enumerate(params)]
    else:
        adds = [(True if i >= covered else False) for i, key in
                enumerate(params)]
    return adds, params, kwargs

def get_parameters(func, args=(), kwargs=None, onlykeys=False, onlyused=False,
                   default=None):
    """
    Get all function parameters with default values.

    :param func: function to get parameters from
    :param args: arguments to modify
    :param kwargs: key arguments to modify
    :param onlykeys: return only key arguments
    :param onlyused: return only modified arguments
    :param default: default value to assign to key arguments
    :return: args, kwargs
    """
    # check what parameters to add
    adds, params, kwargs = _helper_parameters(func=func, args=args, kwargs=kwargs,
                                      onlykeys=onlykeys, onlyused=onlyused)
    for add, key in zip(adds, params):
        if add and key not in kwargs:
            kwargs[key] = default

    if onlykeys:
        return kwargs
    return args, kwargs


##########################################################################
# BaseCopySupporter class and copy_support class decorator
##########################################################################

def get_arguments(self, args=(), kwargs=None, onlykeys=False, onlyused=False,
                  func=None):
    """
    Get all function parameters configured in this instance mixed with
    additional arguments.

    :param self: instance object
    :param args: arguments to modify
    :param kwargs: key arguments to modify
    :param onlykeys: return only key arguments
    :param onlyused: return only modified arguments
    :param func: function to get parameters from. If None it uses self.__init__
    :return: args, kwargs
    """
    if func is None:
        func = self.__init__

    # check what parameters to add
    adds, params, kwargs = _helper_parameters(func=func, args=args, kwargs=kwargs,
                                      onlykeys=onlykeys, onlyused=onlyused)

    _map_parameters = getattr(self, "_map_parameters", None)
    for add, key in zip(adds, params):
        if add and key not in kwargs:
            try:
                if _map_parameters is not None and key in _map_parameters:
                    mapped_key = _map_parameters[key]
                    # if mapped_key is None then it means variable is not
                    # assigned in the __init__ of the instance so ignore it
                    if mapped_key is not None:
                        kwargs[key] = getattr(self, mapped_key)
                else:
                    kwargs[key] = getattr(self, key)
            except AttributeError:
                e, msg, traceback = sys.exc_info()
                msg.args = (
                    msg.args[0] + ". Review @copy_support decorator or "
                    "BaseCopySupporter class for more info.",)
                raise_(e, msg, traceback)

    if onlykeys:
        return kwargs
    return args, kwargs


def clone(self, *args, **kwargs):
    """
    Clones instance with modifying parameters. Not that this creates a new
    instance.

    :return: new_instance
    """
    new_self = copy.copy(self)
    kwargs = self.get_arguments(args, kwargs, onlykeys=True, onlyused=True)
    _map_parameters = getattr(self, "_map_parameters", None)
    for key in kwargs:
        if _map_parameters is not None and key in _map_parameters:
            setattr(new_self, _map_parameters[key], kwargs[key])
        else:
            setattr(new_self, key, kwargs[key])
    return new_self


def spawn(self, *args, **kwargs):
    """
    Creates new Carrier of the same class with parameters of this instance.

    :return: new_instance
    """
    args, kwargs = self.get_arguments(args, kwargs)
    new_self = type(self)(*args, **kwargs)
    return new_self


def _repr(self):
    """
    Object representation
    """
    args, kwargs = self.get_arguments()
    params = []
    for k in kwargs:
        params.append("{} = {}".format(k, repr(kwargs[k])))

    return "{}({})".format(type(self).__name__, ", ".join(params))
    # return "{}({})".format(type(self).__name__,repr(self.data))


_convert = {
    'get_arguments': get_arguments,
    'clone': clone,
    'spawn': spawn,
    '__repr__': _repr,
    '__call__': spawn
}


def copy_support(_map=None, convert=None, overwrite=()):
    """
    Class decorator that fills spawn and clone methods. Be careful when using
    this decorator as it can give unexpected results if __init__ arguments
    and instance variables do not correspond to each other. Be very wary of
    property methods since they change the behaviour of calling a variable.
    You must ensure that classes abide the rules or decorator adapts to class
    to ensure good behaviour. It implements methods like "__repr__" to represent
    instance creation, "get_arguments" to get __init__ parameters with
    overwriting arguments, "clone" to copy instance with overwriting arguments
    and "spawn", to create new instance with constructor __init__ and its
    overwriting arguments.

    example::

        # simple example
        @copy_support
        class Klass(object)
            def __init__(data):
                self.data = data

        arguments = {"data":"Original"}
        instanceA = Klass(**arguments)
        for key, val in arguments.items():
            assert val == getattr(instanceA,key)

        instanceB = instanceA.spawn("Spawned")
        instanceC = instanceA.clone("Cloned")
        print(repr(instanceA))
        print(repr(instanceB))
        print(repr(instanceC))

        # example mapping parameters
        _map = {"data":"_data"}
        @copy_support(_map = _map)
        class Klass2(object)
            def __init__(data):
                self._data = data

        arguments = {"data":"Original"}
        instanceA2 = Klass2(**arguments)
        for key, val in arguments.items():
            assert val == getattr(instanceA2,_map[key])

        instanceB2 = instanceA.spawn("Spawned")
        instanceC2 = instanceA.clone("Cloned")
        print(repr(instanceA2))
        print(repr(instanceB2))
        print(repr(instanceC2))

    :param _map: dictionary to map __init__ arguments with the instance
        variable names e.g. if in __init__ an argument is "data" but is
        assigned as "_data" then use {"data":"_data"}.
    :param convert: dictionary with the copying functions to add to class
    :param overwrite: force list of parameters to overwrite
    :return: class

    .. note::

        There is not risk from inheritance and they can be overwritten
         applying the decorator again. Classes with no __init__ or no
         parameters in them do not have risk of bad behaviour.
    """
    if convert is None:
        convert = _convert
    else:  # update passed dictionary with global conversion
        if "__call__" in _convert:
            if "spawn" in convert:  # use call from provided conversions
                convert["__call__"] = convert["spawn"]
            else:  # use call from global
                convert["__call__"] = _convert["__call__"]
        # fill in other required methods
        for key in _convert:
            if key not in convert:
                convert[key] = _convert[key] # fill in necessary methods

    def assign(cls):
        # if not (getattr(cls, "__init__", None) is not getattr(object, "__init__", None)):
        # do i really need to implement __init__ ?
        # TODO check that instances will have the same arguments as __init__
        #    raise ValueError('must define __init__')

        # Find user-defined comparisons (not those inherited from object).
        class_members = dict(
            inspect.getmembers(
                cls, lambda x: inspect.isroutine(x)))
        roots = [op for op in convert if op not in overwrite and
                 op in class_members and getattr(cls, op, None) is not
                 getattr(object, op, None)]
        # roots = [op for op in convert if op not in overwrite and
        #         getattr(cls, op, None) is not getattr(object, op, None)]
        for opname, opfunc in convert.items():
            if opname not in roots:
                opfunc.__name__ = opname
                setattr(cls, opname, opfunc)
        if _map is not None:  # set mapper for the parameters
            setattr(cls, "_map_parameters", _map)
        return cls

    # if @copy_support is used
    if inspect.isclass(_map):
        cls = _map
        _map = None
        return assign(cls)

    # if @copy_support() is used
    return assign


class BaseCopySupporter(object):
    """
    Base class for classes supporting cloning and spawning of itself.
    This same behaviour can be obtained using @copy_support decorator.
    """
    _map_parameters = None
    spawn = spawn
    clone = clone
    get_arguments = get_arguments
    __call__ = spawn
    __repr__ = _repr


##########################################################################
# BaseCreation class
##########################################################################

class BaseCreation(object):
    """
    Base class Carrier used to convey data reliably in PriorityQueues
    """
    #step = 0.0000000000000000000000000000000000000000000000000000000000001
    #order = count(step=1)

    def __init__(self):
        self._creation_time = _time()
        # self._creation_order = next(Carrier.order)

    @property
    def creation_time(self):
        return self._creation_time

    @creation_time.setter
    def creation_time(self, value):
        raise VariableNotSettable("creation_time is not settable")

    @creation_time.deleter
    def creation_time(self):
        raise VariableNotDeletable("creation_time is not deletable")

    @property
    def creation_time_struct(self):
        """
        Creation time structure
        """
        return _gmtime(self.creation_time)

    @property
    def creation_time_str(self):
        """
        Creation time formated string
        """
        return "%Y/%m/%d %I:%M:%S".format(self.creation_time)

    @property
    def creation_order(self):
        raise NotImplementedError
        # return self._creation_order*Carrier.step

    @creation_order.setter
    def creation_order(self, value):
        raise VariableNotSettable("creation_order is not settable")

    @creation_order.deleter
    def creation_order(self):
        raise VariableNotDeletable("creation_order is not deletable")