import os


def get_source(page):
    """
    Return source for the given file at the /tests/data dir.
    """

    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, 'data', page)
    with open(path) as F:
        data = F.read()
    return data