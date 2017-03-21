# -*- coding: utf-8 -*-

import logging
import os


class reloadable(object):

    def __init__(self, message):
        self._message = message
        self._values = {}
        self._lastmods = {}
        self.logger = logging.getLogger('wt.reloadable')

    def __call__(self, fn):

        def inner(filename):
            v = self._values.get(filename)
            m = self._lastmods.get(filename)
            try:
                modified = os.stat(filename).st_mtime
            except FileNotFoundError:
                self.logger.warn(
                    'File not found "%s", skipping stat', filename)
                pass
            else:
                if m is None or modified > m:
                    self.logger.debug(
                        'File "%s" modified, %s', filename, self._message)
                    self._lastmods[filename] = modified
                    v = None

            if v is None:
                self._values[filename] = v = fn(filename)
            return v
        return inner
