class DHT(object):

    base_endpoint = '/dht'

    def __init__(self, transport):
        self.transport = transport

    def findpeer(self, peer_id, verbose=False):
        """Query the DHT for all of the multiaddresses associated with a Peer ID.

        :param peer_id: ID of the peer to search for
        :type peer_id: str

        :param verbose: Print extra information. Default: False
        :type verbose: bool

        :return: dict -- return
           ::

              {
                 "ID": "<string>",
                 "Type": "<int>",
                 "Responses": None,
                 "Extra": "<string>"
              }

        """
        endpoint = self.base_endpoint + '/findpeer'
        params = {
            'arg': peer_id,
            'verbose': verbose
        }
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.json())

    def findprovs(self, key, verbose=False):
        """Find peers in the DHT that can provide a specific value, given a key.

        :param key: key to find providers for
        :type key: str

        :param verbose: Print extra information. Default: False
        :type verbose: bool

        :return: dict -- return
           ::

              {
                 "ID": "<string>",
                 "Type": "<int>",
                 "Responses": null,
                 "Extra": "<string>"
              }

        """
        endpoint = self.base_endpoint + '/findprovs'
        params = {
            'arg': key,
            'verbose': verbose
        }
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.json())

    def get(self, key, verbose=False):
        """Given a key, query the DHT for its best value.

        :param key: key to find a value for
        :type key: str

        :param verbose: Print extra information
        :type verbose: bool

        :return: dict -- return
           ::

              {
                 "ID": "<string>",
                 "Type": "<int>",
                 "Responses": None,
                 "Extra": "<string>"
              }

        """
        endpoint = self.base_endpoint + '/get'
        params = {
            'arg': key,
            'verbose': verbose
        }
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.json())

    def put(self, key, value, verbose=False):
        """Write a key/value pair to the DHT.

        :param key: The key to store the value at
        :type key: str

        :param value: value to store
        :type value: str

        :param verbose: Print extra information. Default: False
        :type verbose: bool

        :return: dict -- return
           ::

              {
                 "ID": "<string>",
                 "Type": "<int>",
                 "Responses": None,
                 "Extra": "<string>"
              }
        """
        endpoint = self.base_endpoint + '/put'
        params = [('arg', key), ('arg', value), ('verbose', verbose)]
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.json())

    def query(self, peer_id, verbose=False):
        """Find the closest Peer IDs to a given Peer ID by querying the DHT.

        :param peer_id: The peerID to run the query against.
        :type peer_id: str

        :param verbose: Print extra information. Default: False
        :type verbose: bool

        :return: dict -- return
           ::

              {
                 "ID": "<string>",
                 "Type": "<int>",
                 "Responses": None,
                 "Extra": "<string>"
              }
        """
        endpoint = self.base_endpoint + '/query'
        params = {
            'arg': peer_id,
            'verbose': verbose
        }
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.json())
