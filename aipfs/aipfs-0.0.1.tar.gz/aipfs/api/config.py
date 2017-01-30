class Config(object):

    base_endpoint = '/config'

    def __init__(self, transport):
        self.transport = transport

    def replace(self, configfile):
        """Replaces the config with .

        :param configfile: file to use as the new config.

        :return: bytes -- file
        """
        endpoint = self.base_endpoint + '/replace'
        data = {
            'file': configfile
        }
        res = yield from self.transport.request('post', endpoint=endpoint, data=data)
        return (yield from res.read())

    def show(self):
        """Outputs the content of the config file.

        :return: bytes -- file config
        """
        endpoint = self.base_endpoint + '/show'
        res = yield from self.transport.request('get', endpoint=endpoint)
        return (yield from res.read())
