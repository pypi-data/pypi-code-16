import types
from collections import namedtuple


def freeze_data(obj, *, allow=frozenset(), keep_instances_of=frozenset()):
    """Convert 'obj' recursively to a read-only object but selectively
    allow functions and other hashables. This means that recursively:
        lists are converted to tuples
        dicts are converted to types.MappingProxyType
        sets are converted to frozensets
        classes and other instances of 'type' are converted to namedtuples
        collections.namedtuple are created anew and values recursively made read-only
        ints, floats, strings, bytes, None and bools are kept unchanged

    Functions are not read-only (e.g. you can access func.__globals__), and if a function is found,
    a ValueError is raised. However, functions are often useful, and if 'functions' is
    found in 'allow', the function is *copied* to a new function. The user of the data structure
    *will* be allowed access to the original function's .__globals__ attributes etc.

    Other hashable objects are not necessarily read-only and will raise ValueErrors.
    However, if 'hashables' is in 'allow', these objects will be kept unchanged.
    The user of the data structure will be allowed access to the object's .__globals__ attributes
    etc.

    If non-hashable objects (other than lists, etc mentioned above) are found, a ValueError
    will be raised.

    Notice: The created read-only objects is not hashable if the original object contains dicts, as
    types.MappingProxyType is not hashable.
    """
    if isinstance(allow, (str)):
        allow = frozenset((allow,))
    elif not isinstance(allow, (set, frozenset)):
        allow = frozenset(allow)
    allowed_ = {'functions', 'hashables', 'modules'}
    if not allow <= allowed_:
        raise ValueError("'allow' must be in %r" % (allowed_))

    # check type and recursively return a new read-only object
    if isinstance(obj, (str, int, float, bytes, type(None), bool)):
        return obj
    elif isinstance(obj, tuple) and not type(obj) == tuple:  # assumed namedtuple
        return type(obj)(
            *(freeze_data(i, allow=allow, keep_instances_of=keep_instances_of) for i in obj))
    elif isinstance(obj, (tuple, list)):
        return tuple(freeze_data(i, allow=allow, keep_instances_of=keep_instances_of) for i in obj)
    elif isinstance(obj, dict):
        return types.MappingProxyType(
            {k: freeze_data(v, allow=allow, keep_instances_of=keep_instances_of) for k, v in
             obj.items()})
    elif isinstance(obj, (set, frozenset)):
        return frozenset(
            freeze_data(i, allow=allow, keep_instances_of=keep_instances_of) for i in obj)
    elif isinstance(obj, types.FunctionType):
        if 'functions' not in allow:
            raise ValueError(("Functions not allowed, %s used."
                              "To allow functions, set allow = {'functions'}") % (
                                 obj,))
        func = _copy_function(obj)
        for i in (j for j in dir(obj) if not j.startswith('__')):
            val = getattr(obj, i)
            setattr(func, i, freeze_data(val, allow=allow, keep_instances_of=keep_instances_of))
        return func
    elif isinstance(obj, types.ModuleType):
        if 'modules' not in allow:
            raise ValueError(("Modules not allowed, %s used."
                              "To allow functions, set allow = {'modules'}") % (
                                 obj,))
        return obj
    elif isinstance(obj, (type, types.SimpleNamespace, *keep_instances_of)):
        obj_name = obj.__name__ if hasattr(obj, '__name__') else obj.__class__.__name__
        obj_tuple = namedtuple(obj_name, [i for i in dir(obj) if not i.startswith('_')])
        return obj_tuple(
            **{i: freeze_data(getattr(obj, i), allow=allow, keep_instances_of=keep_instances_of) for
               i in dir(obj) if not i.startswith('_')})
    elif getattr(obj, '__hash__') is not None:
        if not 'hashables' in allow:
            raise ValueError(
                "non-standard hashables not allowed, %s used. To allow, set allow_hashables = True" % (
                    obj,))
        return obj

    raise ValueError(obj)


def freeze_module(obj, *, allow=frozenset(), keep_instances_of=frozenset()):
    obj_name = obj.__name__
    obj_tuple = namedtuple(obj_name, [i for i in dir(obj) if not i.startswith('_')])
    return obj_tuple(
        **{i: freeze_data(getattr(obj, i), allow=allow, keep_instances_of=keep_instances_of) for
           i in dir(obj) if not i.startswith('_')})


def _copy_function(obj):
    """Copy function 'obj' into new new function."""
    import functools

    func = types.FunctionType(obj.__code__, obj.__globals__, name=obj.__name__,
                              argdefs=obj.__defaults__,
                              closure=obj.__closure__)
    func = functools.update_wrapper(func, obj)
    func.__kwdefaults__ = obj.__kwdefaults__

    return func
