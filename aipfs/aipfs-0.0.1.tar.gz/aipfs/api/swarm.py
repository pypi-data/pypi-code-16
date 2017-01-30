class Addrs(object):
    base_endpoint = '/swarm/addrs'

    def __init__(self, transport):
        self.transport = transport

    def local(self, show_peer_id=False):
        endpoint = self.base_endpoint + '/local'
        params = [('id', show_peer_id)]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))


class Filters(object):
    base_endpoint = '/swarm/filters'

    def __init__(self, transport):
        self.transport = transport

    def add(self, addrs):
        endpoint = self.base_endpoint + '/add'
        params = [('arg', addrs)]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))

    def rm(self, addrs):
        endpoint = self.base_endpoint + '/rm'
        params = [('arg', addrs)]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))


class Swarm(object):
    base_endpoint = '/swarm'

    def __init__(self, transport):
        self.transport = transport

        self.addrs = Addrs(self.transport)

        self.filters = Filters(self.transport)

    def connect(self, addrs):
        endpoint = self.base_endpoint + '/connect'
        params = [('arg', addrs)]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))

    def disconnect(self, addrs):
        endpoint = self.base_endpoint + '/disconnect'
        params = [('arg', addrs)]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))

    def peers(self, verbose=None):
        endpoint = self.base_endpoint + '/peers'
        params = [('verbose', verbose)]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))
