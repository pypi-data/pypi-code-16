class Block(object):
    """IPFS block"""

    base_endpoint = '/block'

    def __init__(self, transport):
        self.transport = transport

    def get(self, multihash: str):
        """Get a raw IPFS block.

        :param multihash: The base58 multihash of an existing block to get.

        :return: bytes -- file
        """
        endpoint = self.base_endpoint + '/get'
        params = {
            'arg': multihash
        }
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.read())

    def put(self, filestream):
        """Stores input as an IPFS block.

        :param filestream: The data to be stored as an IPFS block.

        :return: dict -- return
           ::

              {
                 "Key": "<string>",
                 "Size": "<int>"
              }

        """
        endpoint = self.base_endpoint + '/put'
        data = {
            "file": filestream
        }
        res = yield from self.transport.request('post', endpoint=endpoint, data=data)
        return (yield from res.json())

    def stat(self, multihash):
        """Print information of a raw IPFS block.

        :param multihash: The base58 multihash of an existing block to stat

        :return: dict -- return
           ::

             {
                "Key": "<string>",
                "Size": "<int>"
             }

        """
        endpoint = self.base_endpoint + '/stat'
        params = {
            'arg': multihash
        }
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.json())
