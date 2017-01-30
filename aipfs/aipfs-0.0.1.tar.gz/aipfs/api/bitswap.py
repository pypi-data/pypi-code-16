class Bitswap(object):
    """Bitswap agent."""

    base_endpoint = '/bitswap'

    def __init__(self, transport):
        self.transport = transport

    def stat(self):
        """Show some diagnostic information on the bitswap agent.

        :return: dict -- return
           ::

              {
                 "ProvideBufLen": "<int>",
                 "Wantlist": [
                    "<string>"
                 ],
                 "Peers": [
                    "<string>"
                 ],
                 "BlocksReceived": "<int>",
                 "DupBlksReceived": "<int>",
                 "DupDataReceived": "<uint64>"
               }

        """
        endpoint = self.base_endpoint + '/stat'
        res = yield from self.transport.request('get', endpoint=endpoint)
        return (yield from res.json())

    def unwant(self, key):
        """Remove a given block from your wantlist.

        :param key: Key(s) to remove from your wantlist.
        :type key: str

        :return: bytes -- file

        """
        params = {
            'arg': key
        }
        endpoint = self.base_endpoint + '/unwant'
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.read())

    def wantlist(self, peer: str):
        """Show blocks currently on the wantlist.

        :param peer: Specify which peer to show wantlist for

        :return: dict -- return
           ::

              {
                 "Keys": [
                    "<string>"
                 ]
              }
        """
        params = {
            'peer': peer
        }
        endpoint = self.base_endpoint + '/wantlist'
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.json())
