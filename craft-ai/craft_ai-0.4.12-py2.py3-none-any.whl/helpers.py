from craftai.errors import *


def join_dicts(old_dicts, *new_dicts):
    joined_dicts = old_dicts.copy()

    for dict in new_dicts:
        joined_dicts.update(dict)

    return joined_dicts


def dict_depth(x):
    if type(x) is dict and x:
        return 1 + max(dict_depth(x[a]) for a in x)
    if type(x) is list and x:
        return 1 + max(dict_depth(a) for a in x)
    return 0
