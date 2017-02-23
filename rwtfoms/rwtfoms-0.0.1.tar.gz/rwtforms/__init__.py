import rw.scope


class TornadoMultiDict(object):
    def __init__(self, handler):
        self.handler = handler

    def __iter__(self):
        return iter(self.handler.request.arguments)

    def __len__(self):
        return len(self.handler.request.arguments)

    def __contains__(self, name):
        # We use request.arguments because get_arguments always returns a
        # value regardless of the existence of the key.
        return (name in self.handler.request.arguments)

    def getlist(self, name):
        # get_arguments by default strips whitespace from the input data,
        # so we pass strip=False to stop that in case we need to validate
        # on whitespace.
        return self.handler.get_arguments(name, strip=False)


@rw.scope.inject
def create_form(name, Form, handler, db=None, **kwargs):
    """
    :rtype: wtforms.Form
    """
    handler[name] = Form(**kwargs)
    if db:
        handler[name].process(obj=db)
    else:
        handler[name].process(TornadoMultiDict(handler))
    return handler[name]