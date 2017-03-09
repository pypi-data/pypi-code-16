from twisted.python import usage
from twisted.internet import endpoints
from twisted.application import service as taservice, internet
from twisted.web import server

from remotemath import operations

class Options(usage.Options):

    def __init__(self):
        usage.Options.__init__(self)
        self.ports = []

    def opt_port(self, port):
        self.ports.append(port)

def makeService(opt):
    from twisted.internet import reactor
    ops_instance = operations.Operations(reactor)
    resource = ops_instance.app.resource()
    site = server.Site(resource)
    ret = taservice.MultiService()
    for port in opt.ports:
        ep = endpoints.serverFromString(reactor, port)
        serv = internet.StreamServerEndpointService(ep, site)
        serv.setServiceParent(ret)
    return ret
