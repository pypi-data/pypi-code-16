import sys
import urllib

if sys.version[0]=='2':
    import urlparse
else:
    import urllib.parse as urlparse


def canonurl(url):
    # turn string into unicode
    if sys.version[0]=='2':
        if not isinstance(url, unicode):
            url = url.decode('utf8')

    # parse it
        parsed = urlparse.urlsplit(url)

        # divide the netloc further
        userpass, at, hostport = parsed.netloc.rpartition('@')
        user, colon1, pass_ = userpass.partition(':')
        host, colon2, port = hostport.partition(':')

        # encode each component
        scheme = parsed.scheme.encode('utf8')
        user = urllib.quote(user.encode('utf8'))
        colon1 = colon1.encode('utf8')
        pass_ = urllib.quote(pass_.encode('utf8'))
        at = at.encode('utf8')
        host = host.encode('idna')
        colon2 = colon2.encode('utf8')
        port = port.encode('utf8')
        path = '/'.join(  # could be encoded slashes!
            pce.encode('idna') if i==0 else pce
            for i,pce in enumerate(parsed.path.split('/')))
        query = urllib.quote(urllib.unquote(parsed.query).encode('utf8'), '=&?/')
        fragment = urllib.quote(urllib.unquote(parsed.fragment).encode('utf8'))

        # put it back together
        netloc = ''.join((user, colon1, pass_, at, host, colon2, port))
        return urlparse.urlunsplit((scheme, netloc, path, query, fragment))

    else:
        # parse it
        parsed = urlparse.urlsplit(url)

        # divide the netloc further
        userpass, at, hostport = parsed.netloc.rpartition('@')
        user, colon1, pass_ = userpass.partition(':')
        host, colon2, port = hostport.partition(':')

        # encode each component
        scheme = parsed.scheme
        user = urlparse.quote(user)
        pass_ = urlparse.quote(pass_)

        host = host.encode('idna').decode('utf-8')

        path = '/'.join(  # could be encoded slashes!
            pce.encode('idna').decode('utf-8') if i == 0 else pce
            for i, pce in enumerate(parsed.path.split('/')))

        query = urlparse.quote(urlparse.unquote(parsed.query).encode('utf8'), '=&?/')
        fragment = urlparse.quote(urlparse.unquote(parsed.fragment).encode('utf8'))

        # put it back together
        netloc = ''.join((user, colon1, pass_, at, host, colon2, port))
        return urlparse.urlunsplit((scheme, netloc, path, query, fragment))

def cut_http_from_str(url):
    url = url.lstrip('https://')
    url = url.lstrip('http://')
    return url