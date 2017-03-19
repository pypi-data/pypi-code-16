from . import TeleSocket as ts, ADDRESS
from . import types


class TeleSocket(ts):
    def __init__(self, address=ADDRESS, daemonic=True, start=True):
        super(TeleSocket, self).__init__(address, daemonic, start)

    def generate_codes(self, count):
        payload = {'count': count}
        codes = self.request('generate_codes', payload).wait()
        return codes

    def clients_list(self):
        req = self.request('clients_list')
        clients = [types.Client.serialize(**raw_client) for raw_client in req.wait().get('clients')]
        return clients
