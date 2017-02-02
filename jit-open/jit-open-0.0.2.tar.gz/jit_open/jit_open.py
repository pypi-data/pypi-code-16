class JITOpen(object):
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._handle = None
        self.write = self._open

    def _open(self, *args, **kwargs):
        self._handle = open(*self._args, **self._kwargs)
        self.write = self._handle.write
        self.write(*args, **kwargs)
