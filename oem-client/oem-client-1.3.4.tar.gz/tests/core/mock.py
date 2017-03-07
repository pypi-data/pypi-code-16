from __future__ import absolute_import, division, print_function


class MockService(object):
    def __init__(self, source, target):
        self._source = source
        self._target = target

    @property
    def source_key(self):
        return self._source

    @property
    def target_key(self):
        return self._target
