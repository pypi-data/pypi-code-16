import os

from zope.interface import implementer

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet, service
from twisted.names import dns, server

from ipdns.ipdns import Resolver

class Options(usage.Options):
  optParameters = [["domain", "d", None, "The top domain serving ipdns for. (required)"],
                   ["server", "s", None, "DNS for this mail server. (required)"],
                   ["email", "e", None, "Email address of domain admin. (required)"],
                   ["nsrecords", "n", None, "NS records for the hosted domain. Eg: ns1:94.23.35.208,ns2:37.187.30.26 (required)"]]

@implementer(IServiceMaker, IPlugin)
class MyServiceMaker(object):
  tapname = "ipdns"
  description = "Responds with an ip for each dns request alla [ip as a number].anydomain.anyextension"

  options = Options

  def makeService(self, options):
    application = service.MultiService()

    factory = server.DNSServerFactory(clients=[Resolver(options["domain"], options["server"], options["email"], options["nsrecords"])])

    tcp_dns_server = internet.TCPServer(53, factory)
    tcp_dns_server.setServiceParent(application)

    protocol = dns.DNSDatagramProtocol(controller=factory)

    udp_dns_server = internet.UDPServer(53, protocol)
    udp_dns_server.setServiceParent(application)

    return application

serviceMaker = MyServiceMaker()
