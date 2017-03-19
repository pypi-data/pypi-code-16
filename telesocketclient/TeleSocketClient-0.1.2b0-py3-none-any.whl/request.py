from NucleusUtils.jProtocol.client import RequestsManagerBase
from NucleusUtils.jProtocol.helper import clean


class RequestManager(RequestsManagerBase):
    def __init__(self, telesocket):
        self.telesocket = telesocket
        super(RequestManager, self).__init__()

    def send(self, data):
        self.telesocket.send(clean(data))
