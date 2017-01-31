import re
import netaddr

from twisted.internet import defer
from twisted.names import dns, error
from twisted.logger import Logger

log = Logger()

class Resolver(object):

    def __init__(self, domain, ns_server, ns_email, ns_records):
        self.domain = domain
        self.ns_server = ns_server
        self.ns_email = ns_email
        self._matcher = re.compile(r'^.*?-?(\d+)\.%s$' % domain.replace('.', '\\.'))
        self.ns_records = dict()
        for record in ns_records.split(','):
            ns, ip = record.split(':', 1)
            name = "%s.%s" % (ns, domain)
            self.ns_records[name] = dns.RRHeader(name=name,
                payload=dns.Record_A(address=ip))
        self.authority = dns.RRHeader(name=self.domain, type=dns.SOA,
            payload=dns.Record_SOA(mname=self.ns_server, rname=self.ns_email,
                                   serial = 1, refresh = "1H", retry = "1H",
                                   expire = "1H", minimum = "1H"))

    def query(self, query, timeout=None):

        if not query.type in (dns.A, dns.SOA):
            log.debug('Received incompatible query for type %s record' % query.type)
            return defer.fail(error.DomainError())

        name = query.name.name.decode("utf8")

        if name in self.ns_records:
            return [self.ns_records[name]], [self.authority], []

        match = self._matcher.match(name)

        try:
            answers = []
            if match:
                answer = dns.RRHeader(name=name,
                    payload=dns.Record_A(address=str(netaddr.IPAddress(int(match.group(1))))))
                answers.append(answer)

            authorities = [self.authority]
            additional = []
            return answers, authorities, additional
        except:
            log.failure("Failure in serving address for query %s" % name)
            return defer.fail(error.DomainError())
