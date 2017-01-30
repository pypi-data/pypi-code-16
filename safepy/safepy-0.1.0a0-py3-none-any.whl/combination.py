from functools import reduce


def combine(*decorators):
    if not decorators:
        raise ValueError("empty decorators")

    return reduce(lambda x, y: x(y), decorators)
