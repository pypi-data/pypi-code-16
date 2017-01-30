class Log(object):

    base_endpoint = '/log'

    def __init__(self, transport):
        self.transport = transport

    def level(self, subsystem, level):
        endpoint = self.base_endpoint + '/level'
        params = [
            ('arg', subsystem),
            ('arg', level)
        ]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))

    def ls(self):
        endpoint = self.base_endpoint + '/ls'
        return (yield from self.transport.request('get', endpoint=endpoint))

    def tail(self):
        endpoint = self.base_endpoint + '/tail'
        return (yield from self.transport.request('get', endpoint=endpoint))
