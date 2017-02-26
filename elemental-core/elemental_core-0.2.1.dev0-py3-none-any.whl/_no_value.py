class NoValue(object):
    def __bool__(self):
        # Python 3.x
        return False

    def __nonzero__(self):
        # Python 2.x
        return False
