from ..fnTK import reduce
from .merge2 import merge2


def merge(dicts):
    """Merge many dictionaries into one
    Args:
        dicts (list): a list of dictionaries
    Returns:
        a dict
    """
    if len(dicts) == 0:
        return {}
    elif len(dicts) == 1:
        return dicts[0]
    else:
        return reduce(merge2, dicts, {})
