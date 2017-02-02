
class Base(object):
    """A base command."""

    def __init__(self):
        pass

    def configure(self, **kwargs):
        raise NotImplementedError('You must implement the configure() method.')
