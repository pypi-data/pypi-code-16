# -*- coding: utf-8 -*-
# Copyright (C) Cameron Poe 2017

import socket

def get_ipv4(host):
    str(host)
    ip = socket.gethostbyname(host)
    return ip

def get_ipv6(host, port=80):
    str(host)
    alladdr = list(
        set(
            map(
                lambda x: x[4],
                socket.getaddrinfo(host, port)
            )
        )
    )
    ipv6 = filter(
        lambda x: ':' in x[0], alladdr
    )
    return "{}".format(ipv6)

def netblock_owner(host):
    ip = socket.gethostbyname(str(host))
    from cymruwhois import Client
    c = Client()
    r = c.lookup(ip)
    nbowner = r.owner
    return nbowner

def get_asn(host):
    ip = socket.gethostbyname(str(host))
    from cymruwhois import Client
    c = Client()
    r = c.lookup(ip)
    asn = r.asn
    return "{}".format(asn)

def dns_reverse_ptr(ip):
    from dns import resolver, reversename
    addr = reversename.from_address(str(ip))
    results = resolver.query(addr, "PTR")[0]
    return "{}".format(results)


def dns_mx(host):
    import dns.resolver
    answers = dns.resolver.query(str(host), 'MX')
    for rdata in answers:
        return '{}'.format(rdata.exchange)

def dns_reversename(ip):
    import dns.reversename
    n = dns.reversename.from_address(str(ip))
    return n
