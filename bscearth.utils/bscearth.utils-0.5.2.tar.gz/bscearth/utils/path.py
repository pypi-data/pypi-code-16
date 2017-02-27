import os


def expand_path(path):
    """
    Expands character ~ and system variables on the given path
    :param path: path to expand
    :type path: str
    :return: path after the expansion
    """
    return os.path.expandvars(os.path.expanduser(path))
