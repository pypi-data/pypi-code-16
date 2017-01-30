class Repo(object):

    base_endpoint = '/repo'

    def __init__(self, transport):
        self.transport = transport

    def fsck(self):
        endpoint = self.base_endpoint + '/fsck'
        return (yield from self.transport.request('get', endpoint=endpoint))

    def gc(self, quiet=False):
        endpoint = self.base_endpoint + '/gc'
        params = [('quiet', quiet)]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))

    def stat(self, human=False):
        endpoint = self.base_endpoint + '/stat'
        params = [('human', human)]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))

    def verify(self):
        endpoint = self.base_endpoint + '/verify'
        return (yield from self.transport.request('get', endpoint=endpoint))

    def version(self, quiet=None):
        endpoint = self.base_endpoint + '/version'
        params = [('quiet', quiet)]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))
