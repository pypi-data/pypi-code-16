from __future__ import absolute_import
from ..adapters.csv import CSVAdapter as DefaultAdapter  # NOQA

import csv


class Connection(object):
    def __init__(self, path, **opts):
        self.opts = opts
        self.path = path


def connect(path, **opts):
    return Connection(path, **opts)


class DictResult(object):
    def __init__(self, reader):
        try:
            self._colnames = next(reader)
        except StopIteration:
            self._colnames = None
            self._rows = []
        else:
            self._rows = reader

    def __iter__(self):
        for row in self._rows:
            yield dict(zip(self._colnames, row))


def reader(connection):
    fh = open(connection.path, 'r')
    return DictResult(csv.reader(fh, *connection.opts))
