from .entity import Entity


class Request(Entity):
    public_fields = ('method', 'data', ('id', 'index'))

    def __init__(self, server, client, method, data, index):
        self.server = server
        self.client = client
        self.method = method
        self.data = data
        self.index = index


class Response(Entity):
    public_fields = (['type', 'get_reference'], 'data', ('id', 'index'))
    reference = ['response']

    def __init__(self, data=None, index=None):
        self.data = data
        self.index = index
