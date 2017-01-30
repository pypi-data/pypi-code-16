class File(object):
    base_endpoint = '/file'

    def __init__(self, transport):
        self.transport = transport

    def ls(self, path):
        """List directory contents for Unix filesystem objects.

        :param path: path to the IPFS object(s) to list links from
        :type path: str

        :return: dict -- return
           ::

              {
                 "Arguments": {
                    "<string>": "<string>"
                 },
                 "Objects": {
                    "<string>": {
                       "Hash": "<string>",
                       "Size": "<uint64>",
                       "Type": "<string>",
                       "Links": [
                          {
                             "Name": "<string>",
                             "Hash": "<string>",
                             "Size": "<uint64>",
                             "Type": "<string>"
                          }
                       ]
                    }
                 }
              }
        """
        endpoint = self.base_endpoint + '/ls'
        params = {
            "arg": path
        }
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.json())
