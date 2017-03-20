
class Actor:

    uris = {}
    host = None
    info = {}

    def __init__(self, uris, host):
        self.uris = uris
        self.host = host

    def __repr__(self):
        return "host: {0} \n info {1} \n actions {2}".format(self.host, self.info, self.uris)

    def __str__(self):
        return self.__repr__()
