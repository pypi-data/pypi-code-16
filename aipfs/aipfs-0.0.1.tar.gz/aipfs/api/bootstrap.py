class Bootstrap(object):

    base_endpoint = '/bootstrap'

    def __init__(self, transport):
        self.transport = transport

    def add_default(self):
        """Add default peers to the bootstrap list.

        :return: dict -- return
           ::

              {
                 "Peers": [
                    "<string>"
                 ]
              }

        """
        endpoint = self.base_endpoint + '/add/default'
        res = yield from self.transport.request('get', endpoint=endpoint)
        return (yield from res.json())

    def list(self):
        """Show peers in the bootstrap list.

        :return: dict -- return
           ::

              {
                 "Peers": [
                    "<string>"
                 ]
              }

        """
        endpoint = self.base_endpoint + '/list'
        res = yield from self.transport.request('get', endpoint=endpoint)
        return (yield from res.json())

    def rm_all(self):
        """Removes all peers from the bootstrap list.

        :return: dict -- return
           ::

              {
                 "Peers": [
                    "<string>"
                 ]
              }

        """
        endpoint = self.base_endpoint + '/rm/all'
        res = yield from self.transport.request('get', endpoint=endpoint)
        return (yield from res.json())
