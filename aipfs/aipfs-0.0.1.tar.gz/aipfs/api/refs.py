class Refs(object):
    base_endpoint = '/refs'

    def __init__(self, transport):
        self.transport = transport

    def local(self):
        endpoint = self.base_endpoint + '/local'
        return (yield from self.transport.request('get', endpoint=endpoint))
