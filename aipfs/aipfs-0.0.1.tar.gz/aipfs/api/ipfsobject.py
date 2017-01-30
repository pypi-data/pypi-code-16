class Patch(object):
    base_endpoint = '/object/patch'

    def __init__(self, transport):
        self.transport = transport

    def add_link(self, hashname, name, ipfsobject, create=False):
        """Add a link to a given object.

        :param hashname: The hash of the node to modify.
        :type hashname: str

        :param name: Name of link to create.
        :type name: str

        :param ipfsobject: IPFS object to add link to.
        :type ipfsobject: str

        :param create: Create intermediary nodes. Default: False
        :type create: bool

        :return: dict -- return
        """
        endpoint = self.base_endpoint + '/add-link'
        params = [
            ("arg", hashname),
            ("arg", name),
            ("arg", ipfsobject),
            ("create", create)
        ]
        res = yield from self.transport.request("get", endpoint=endpoint, params=params)
        return (yield from res.json())

    def append_data(self, filestream, node):
        """Append data to the data segment of a dag node.

        :param filestream: Data to append.
        :type filestream: io.Stream

        :param node: The hash of the node to modify.
        :type node: str

        :return: dict -- return
           ::

              {
                 "Hash": "<string>",
                 "Links": [
                    {
                       "Name": "<string>",
                       "Hash": "<string>",
                       "Size": "<uint64>"
                    }
                 ]
              }

        """
        endpoint = self.base_endpoint + '/append-data'
        params = [('arg', node)]
        data = {
            "file": filestream
        }
        res = yield from self.transport.request("post", endpoint=endpoint, params=params, data=data)
        return (yield from res.json())

    def rm_link(self, hashname, name):
        """Remove a link from an object.

        :param hashname:The hash of the node to modify.
        :type hashname: str

        :param name: Name of the link to remove.
        :type name: str

        :return: dict -- return
           ::

              {
                 "Hash": "<string>",
                 "Links": [
                    {
                       "Name": "<string>",
                       "Hash": "<string>",
                       "Size": "<uint64>"
                    }
                 ]
              }
        """
        endpoint = self.base_endpoint + '/rm-link'
        params = [
            ('arg', hashname),
            ('arg', name)
        ]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))

    def set_data(self, filestream, hashnode):
        endpoint = self.base_endpoint + '/set-data'
        params = [('arg', hashnode)]
        data = {
            "file": filestream
        }
        return (yield from self.transport.request('get', endpoint=endpoint, params=params, data=data))


class Object(object):
    base_endpoint = '/object'

    def __init__(self, transport):
        self.transport = transport
        self.patch = Patch(self.transport)

    def data(self, hash):
        endpoint = self.base_endpoint + '/data'
        params = {
            'arg': hash
        }
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))

    def diff(self, object1, object2, verbose=False):
        endpoint = self.base_endpoint + '/diff'
        params = [
            ('arg', object1),
            ('arg', object2),
            ('verbose', verbose)
        ]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))

    def get(self, key):
        endpoint = self.base_endpoint + '/get'
        params = {
            'arg': key
        }
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))

    def links(self, key, headers=False):
        endpoint = self.base_endpoint + '/links'
        params = {
            'arg': key,
            'headers': headers
        }
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))

    def new(self, template=None):
        endpoint = self.base_endpoint + '/new'
        params = {
            'arg': template
        }
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))

    def put(self, filestream, inputenc='json', datafieldenc='text'):
        endpoint = self.base_endpoint + '/put'
        data = {
            'file': filestream
        }
        params = {
            'inputenc': inputenc,
            'datafieldenc': datafieldenc
        }
        return (yield from self.transport.request('get', endpoint=endpoint, data=data, params=params))

    def stat(self, key):
        endpoint = self.base_endpoint + '/stat'
        params = [('arg', key)]
        return (yield from self.transport.request('get', endpoint=endpoint, params=params))

