from functools import update_wrapper

import inspect

import six

from spyne.decorator import rpc as original_rpc
from spyne.service import ServiceBase, ServiceBaseMeta

__all__ = ('rpc', 'DelegateBase', 'ExtensibleServiceBase')


class SpyneMethodWrapper(object):
    """
    This class wraps a spyne service method.
    It can be used to access the original undecorated method, as well as
    retrieve the spyne rpc decorated method, using ``get_spyne_rpc``
    """
    def __init__(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def get_spyne_rpc(self, delegate_class):
        # determine the arguments of the original method, and cut off
        # ``self`` and ``ctx``.
        _args = inspect.getargspec(self.func)[0][1:]

        # create a local variable to be referenced in the wrapper closure
        func = self.func

        # define a wrapper function that will serve as the rpc endpoint.
        # this function will be called for each spyne request.
        # it will instantiate a delegate instance and call the corresponding
        # method on it.
        def wrapper(ctx, *args, **kwargs):
            delegate_instance = delegate_class(ctx)
            return func.__get__(
                delegate_instance, delegate_class)(*args, **kwargs)

        # build a bound function, whose function signature will be copied to
        # our wrapper function, so spyne will see it as the original method
        bound_func = func.__get__(delegate_class(), delegate_class)

        # update the wrapper function with the bound function signature.
        func_with_sig = update_wrapper(wrapper, bound_func)

        # decorate our new wrapper function with the spyne rpc decorator.
        # use the original aruments to our replacement decorator.
        return original_rpc(
            _args=_args, *self.args, **self.kwargs)(func_with_sig)


class rpc(object):  # noqa
    """
    This is our replacement for the spyne rpc decorator.
    It can be used on ``DelegateBase`` methods instead of ``spyne.Service``
    methods
    """
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        self.wrapped_func = func
        return SpyneMethodWrapper(self.wrapped_func, self.args, self.kwargs)


class DelegateMetaClass(type):
    """
    This metaclass removes the ``rpc`` decorator from the methods in
    our delegate, but stores the decorated methods in a class variable
    called ``_spyne_cls_dict``. We can use this class dict to pass to
    the original spyne ``ServiceBaseMeta`` class and obtain a spyne
    service class all created new!
    """
    def __new__(cls, name, bases, attrs):
        delegate_attrs = {}
        spyne_attrs = {}

        # collect spyne methods from base classes.
        if attrs.get('collect_base_methods', True):
            for base in reversed(bases):
                spyne_attrs.update(getattr(base, '_spyne_cls_dict', {}))

        # collect spyne methods in the delegate class.
        for k, v in attrs.items():
            if isinstance(v, SpyneMethodWrapper):
                spyne_attrs[k] = v  # collect spyne method
                delegate_attrs[k] = v.func  # remove decorator for normal use.
            else:
                delegate_attrs[k] = v  # this is a regular method

        # set spyne methods to class variable.
        delegate_attrs['_spyne_cls_dict'] = spyne_attrs

        # create new type using the original methods, with the decorator
        # removed.
        return type.__new__(cls, name, bases, delegate_attrs)


@six.add_metaclass(DelegateMetaClass)
class DelegateBase(object):
    """
    Use this as the base class for delegate objects.

    It get's the ctx as a parameter when it is initialized, so now
    you can leave that shit out of the service declaration and acces it as:

    ``self.ctx``

    """
    def __init__(self, ctx=None):
        self.ctx = ctx

    @classmethod
    def get__spyne_cls_dict(cls):
        # create a class dict of the same shape a you would get when typing
        # code in a file. The class dict will be used to create a spyne
        # service class.
        return {
            k: v.get_spyne_rpc(cls) for k, v in cls._spyne_cls_dict.items()}


class DelegateServiceMetaClass(ServiceBaseMeta):
    """
    This metaclass will initialize a spyne service class with the methods on
    the delegate object. if you are crazy you can also still
    define methods in this service class and they will override the delegate
    methods.
    """
    def __init__(cls, name, bases, attrs):  # noqa
        delegate = attrs.get('delegate')
        if delegate is not None:

            # I think we don't need the delegate in the spyne class definition
            del attrs['delegate']

            # build cls_dict with spyne service methods from the delegate
            delegate_service_methods = delegate.get__spyne_cls_dict()

            # add all attributes defined in the class definition.
            delegate_service_methods.update(attrs)

            # call original spyne metoclass to construct spyne service class,
            # with all our delegate methids included! HOW PWN!!!
            return super(
                DelegateServiceMetaClass, cls).__init__(
                    name, bases, delegate_service_methods)

        else:  # there is no delegate, act normal
            return super(
                DelegateServiceMetaClass, cls).__init__(name, bases, attrs)


@six.add_metaclass(DelegateServiceMetaClass)
class ExtensibleServiceBase(ServiceBase):
    """
    Use this class instead of ``spyne.ServiceBase``.
    """
    pass
