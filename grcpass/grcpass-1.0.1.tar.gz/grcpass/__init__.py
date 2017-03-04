#!/usr/bin/env python

from sys import version_info
from collections import namedtuple

if version_info[0] < 3:
    from HTMLParser import HTMLParser
    import urllib2 as urllib
else:
    from html.parser import HTMLParser
    from urllib import request as urllib


class PasswordParser(HTMLParser):
    def __init__(self, passwords):
        HTMLParser.__init__(self)
        self.tag = False
        self.counter = 0
        self.passwords = passwords

    def handle_starttag(self, tag, attrs):
        if tag == 'font':
            self.tag = True

    def handle_data(self, data):
        if self.tag:
            self.tag = False
            self.counter += 1

            if self.counter in [6, 8, 10]:
                self.passwords.append(data)


URL = 'https://www.grc.com/passwords.htm'

def generate():
    """Fetch passwords from grc.com and return them in named tuple.

    Returns:
        named tuple: Passwords(hex, ascii, alpha)

    Raises:
        URLError: when urllib fails to fetch `URL`.

    Usage:
        import grcpass

        passwords = grcpass.generate()

        print(passwords.hex)
        print(passwords.ascii)
        print(passwords.alpha)
    """

    html = urllib.urlopen(URL).read().decode('utf-8')

    passwords = []
    parser = PasswordParser(passwords)
    parser.feed(html)

    Passwords = namedtuple('Passwords', 'hex ascii alpha')
    return Passwords(passwords[0], passwords[1], passwords[2])
