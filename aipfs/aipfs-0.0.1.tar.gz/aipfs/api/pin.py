class Pin(object):

    base_endpoint = '/pin'

    def __init__(self, transport):
        self.transport = transport

    def add(self, ipfs_path, recursive=True):
        endpoint = self.base_endpoint + '/add'
        params = [
            ('arg', ipfs_path),
            ('recursive', recursive)
        ]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))

    def ls(self, ipfs_path, _type='all', quiet=False):
        endpoint = self.base_endpoint + '/ls'
        params = [
            ('arg', ipfs_path),
            ('type', _type),
            ('quiet', quiet)
        ]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))

    def rm(self, ipfs_path, recursive=True):
        endpoint = self.base_endpoint + '/rm'
        params = [
            ('arg', ipfs_path),
            ('recursive', recursive)
        ]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))
