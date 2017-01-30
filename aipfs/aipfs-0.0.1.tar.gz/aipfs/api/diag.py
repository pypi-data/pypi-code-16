class Diag(object):

    base_endpoint = '/diag'

    def __init__(self, transport):
        self.transport = transport

    def cmds_clear(self):
        """Clear inactive requests from the log.

        :return: bytes -- file
        """
        endpoint = self.base_endpoint + '/cmds/clear'
        res = yield from self.transport.request('get', endpoint=endpoint)
        return (yield from res.read())

    def cmds_set_time(self, time):
        """Set how long to keep inactive requests in the log.

        :param time: Time to keep inactive requests in log.
        :type time: str

        :return: bytes -- file
        """
        endpoint = self.base_endpoint + '/cmds/set-time'
        params = {
            'arg': time
        }
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.read())

    def net(self, vis="text"):
        """Generates a network diagnostics report.

        :param vis: Output format. One of: d3, dot, text. Default: "text".
        :type vis: str

        :return: bytes -- file
        """
        endpoint = self.base_endpoint + '/net'
        params = {
            'vis': vis
        }
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.read())

    def sys(self):
        """Prints out system diagnostic information.

        :return: bytes -- file
        """
        endpoint = self.base_endpoint + '/sys'
        res = yield from self.transport.request('get', endpoint=endpoint)
        return (yield from res.read())
