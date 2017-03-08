# -*- coding: utf-8 -*-


import inspect
import importlib
import traceback


def load_class(uri):
    if inspect.isclass(uri):
        return uri

    components = uri.split('.')
    cls = components.pop(-1)

    try:
        mod = importlib.import_module('.'.join(components))
    except:
        exc = traceback.format_exc()
        msg = "class uri %r invalid or not found: \n\n[%s]"
        raise RuntimeError(msg % (uri, exc))
    return getattr(mod, cls)
