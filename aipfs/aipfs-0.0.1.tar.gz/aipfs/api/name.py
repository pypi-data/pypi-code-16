class Name(object):

    base_endpoint = '/name'

    def __init__(self, transport):
        self.transport = transport

    def publish(self, ipfs_path, resolve=True, lifetime='24h', ttl=None):
        endpoint = self.base_endpoint + '/publish'
        params = [
            ('arg', ipfs_path),
            ('resolve', resolve),
            ('lifetime', lifetime),
            ('ttl', ttl)
        ]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))

    def resolve(self, ipns_name, recursive, nocache):
        endpoint = self.base_endpoint + '/resolve'
        params = [
            ('arg', ipns_name),
            ('recursive', recursive),
            ('nocache', nocache)
        ]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))
