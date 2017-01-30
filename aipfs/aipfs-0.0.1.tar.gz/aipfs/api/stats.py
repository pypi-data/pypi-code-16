class Stats(object):

    base_endpoint = '/stats'

    def __init__(self, transport):
        self.transport = transport

    def bitswap(self):
        endpoint = self.base_endpoint + '/bitswap'
        return (yield from self.transport.request('get', endpoint=endpoint))

    def bw(self, peer=None, proto=None, poll=False, interval=None):
        endpoint = self.base_endpoint + '/bw'
        params = [
            ('peer', peer),
            ('proto', proto),
            ('poll', poll),
            ('interval', interval)
        ]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))

    def repo(self, human=False):
        endpoint = self.base_endpoint + '/repo'
        params = [('human', human)]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))
