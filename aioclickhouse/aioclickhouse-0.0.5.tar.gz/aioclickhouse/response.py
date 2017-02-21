from aioclickhouse.tsv import tsv_reader

__all__ = ['Response']


class Response(object):
    def __init__(self, body):
        self._reader = tsv_reader(body)

    def __iter__(self):
        return self._reader

    def __next__(self):
        return next(self._reader)
