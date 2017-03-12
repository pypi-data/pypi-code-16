import collections

import dsnparse


def group_channels(channels):
    """Group channels by the address of the remote host.
    Return a dictionary mapping hosts to lists of
    channels.
    """
    hosts = collections.defaultdict(set)
    for dsn in channels:
        p = dsnparse.parse(dsn)

        # Reconstruct the host address.
        host = "%s://%s" % (p.scheme, p.netloc)
        link = p.path.lstrip('/')
        hosts[host].add(link)

    return tuple((x, tuple(sorted(y)), None) for x,y in hosts.items())
