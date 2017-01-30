class Tar(object):
    base_endpoint = '/tar'

    def __init__(self, transport):
        self.transport = transport

    def add(self, filestream):
        endpoint = self.base_endpoint + '/add'
        data = {
            'file': filestream
        }
        return (yield from self.transport.request('post', endpoint=endpoint, data=data))

    def cat(self, ipfs_path):
        endpoint = self.base_endpoint + '/cat'
        params = [('arg', ipfs_path)]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))
