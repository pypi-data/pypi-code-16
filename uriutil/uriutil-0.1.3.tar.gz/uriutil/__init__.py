from urllib.parse import (urlparse, urlencode, quote, parse_qsl, unquote)
from os import path

def parse(url):
    return Uri(url)

def encode_userpass(*args):
    # i'm not sure if this is too clever to be good?
    if len(args) is 1:
        u = args[0]
        if hasattr(u, "username") and hasattr(u, "password"):
            return encode_userpass(u.username, u.password)
    if len(args) is 2 and None not in args:
        return "{}:{}@".format(*args)
    return ""

def encode_querystring_value(val):
    if val is None:
        return ""
    return quote(str(val))

def decode_querystring_value(val):
    if val is "":
        return None
    return unquote(val)


def encode_query(qstring):
    if hasattr(qstring, "query"):
        return encode_query(qstring.query)
    if qstring == "":
        return ""
    if isinstance(qstring, str):
        return "?" + qstring
    if isinstance(qstring, dict):
        pairs = []
        for (key, val) in qstring.items():
            value_string = encode_querystring_value(val)
            pair = "{key}={val}".format(key=key, val=value_string)
            pairs.append(pair)
        joined = "&".join(pairs)
        return "?" + joined
    return ""

def encode_fragment(thing):
    if hasattr(thing, "fragment"):
        return encode_fragment(thing.fragment)
    if isinstance(thing, list):
        return encode_fragment(encode_path(thing))
    if not thing or thing == "":
        return ""
    return "#" + str(thing)

def encode_port(thing):
    if hasattr(thing, "port"):
        return encode_port(thing.port)
    if thing == 80:
        return ""
    if isinstance(thing, int):
        return ":{}".format(thing)
    raise Exception("Invalid Port")

def encode_path(thing):
    if hasattr(thing, "path"):
        return encode_path(thing.path)
    if isinstance(thing, list):
        return "/".join([quote(x) for x in thing])
    return thing

def decode_path(thing):
    if isinstance(thing, list):
        return [unquote(x) for x in thing]
    return thing

def encode_scheme(thing):
    if hasattr(thing, "scheme"):
        return encode_scheme(thing.scheme)
    if isinstance(thing, str) and thing is not "":
        return thing + "://"
    return "//"

def decode_query(query):
    if query is None:
        return dict()
    if not isinstance(query, str):
        raise Exception("Cannot decode invalid query string")
    pairs = parse_qsl(str(query))
    return {key: unquote(val) for (key, val) in pairs}

class Uri(object):
    def __init__(self, url):
        parts = urlparse(url)
        self.scheme = parts.scheme
        self.username = parts.username
        self.password = parts.password
        self.query = decode_query(parts.query)
        self.hostname = parts.hostname
        self.port = int(parts.port or 80)
        self.path = decode_path(parts.path.split("/"))
        self.fragment = decode_path(parts.fragment.split("/"))

    def __str__(self):
        parts = dict(
            scheme=encode_scheme(self),
            upass=encode_userpass(self),
            host=self.hostname,
            port=encode_port(self),
            path=encode_path(self),
            query=encode_query(self),
            fragment=encode_fragment(self),
        )
        tmp = "{scheme}{upass}{host}{port}{path}{query}{fragment}"
        return tmp.format(**parts)

    def __repr__(self):
        return self.__class__.__name__ + "(" + str(self) + ")"
