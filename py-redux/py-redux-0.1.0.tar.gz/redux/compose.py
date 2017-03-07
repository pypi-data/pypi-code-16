from functools import reduce


def compose(*funcs):
    if len(funcs) == 0:
        return lambda arg: arg
    if len(funcs) == 1:
        return funcs[0]

    def composer(a, b):
        def applier(*args):
            return a(b(*args))
        return applier

    return reduce(composer, funcs)
