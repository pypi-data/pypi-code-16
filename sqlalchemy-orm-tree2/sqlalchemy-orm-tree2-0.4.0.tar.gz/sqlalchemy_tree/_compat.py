import sys

PY2 = sys.version_info[0] == 2

_identity = lambda x: x


if PY2:
    unichr = unichr
    text_type = unicode
    string_types = (str, unicode)
    integer_types = (int, long)
    from urllib import urlretrieve

    text_to_native = lambda s, enc: s.encode(enc)

    iterkeys = lambda d: d.iterkeys()
    itervalues = lambda d: d.itervalues()
    iteritems = lambda d: d.iteritems()

    from cStringIO import StringIO as BytesIO
    from StringIO import StringIO
    import cPickle as pickle
    import ConfigParser as configparser

    from itertools import izip, imap
    range_type = xrange

    cmp = cmp

    py2map = map

    input = raw_input
    from string import lower as ascii_lowercase
    import urlparse

    def console_to_str(s):
        return s.decode('utf_8')

    exec('def reraise(tp, value, tb=None):\n raise tp, value, tb')

else:
    unichr = chr
    text_type = str
    string_types = (str,)
    integer_types = (int, )

    text_to_native = lambda s, enc: s

    iterkeys = lambda d: iter(d.keys())
    itervalues = lambda d: iter(d.values())
    iteritems = lambda d: iter(d.items())

    from io import StringIO, BytesIO
    import pickle
    import configparser

    izip = zip
    imap = map
    range_type = range

    cmp = lambda a, b: (a > b) - (a < b)

    from itertools import starmap, zip_longest

    def py2map(func, *iterables):
        zipped = zip_longest(*iterables)
        if func is None:
            # No need for a NOOP lambda here
            return zipped
        return list(starmap(func, zipped))

    input = input
    from string import ascii_lowercase
    import urllib.parse as urllib
    import urllib.parse as urlparse
    from urllib.request import urlretrieve

    console_encoding = sys.__stdout__.encoding

    def console_to_str(s):
        """ From pypa/pip project, pip.backwardwardcompat. License MIT. """
        try:
            return s.decode(console_encoding)
        except UnicodeDecodeError:
            return s.decode('utf_8')

    def reraise(tp, value, tb=None):
        if value.__traceback__ is not tb:
            raise(value.with_traceback(tb))
        raise value


number_types = integer_types + (float,)
