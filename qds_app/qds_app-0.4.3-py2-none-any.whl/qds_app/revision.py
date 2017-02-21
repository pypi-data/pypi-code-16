import imp
import os
import re
import sys


class Revision(object):

    """Represent a single revision file in a ``versions/`` directory.
    """

    def __init__(self, path, filename):
        self.module = self._load_python_file(path, filename)
        self.revision = self.module.revision
        self.path = path

    def __str__(self):
        return "%s" % (
            self.revision)

    @staticmethod
    def _load_python_file(dir_, filename):
        """Load a file from the given path as a Python module."""

        module_id = re.sub(r'\W', "_", filename)
        path = os.path.join(dir_, filename)

        with open(path, 'rb') as fp:
            module = imp.load_source(module_id, path, fp)
        del sys.modules[module_id]
        return module