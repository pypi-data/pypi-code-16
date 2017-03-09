# -*- coding: utf-8 -*-


import random

from .compat import range


class Placeholder(object):
    def __init__(self):
        # https://en.wikipedia.org/wiki/Zero_width
        self.holders = ['&#8203;', '&#8204;', '&zwnj;', '&#8205;', '&zwj;', '&#8288;']

    def strholder(self, s, n=None):
        # String => List
        l = list(s)
        # ZW Number
        n = n or random.randint(1, len(l))
        # Insert ZW Character
        [l.insert(random.randint(0, len(l)), random.choice(self.holders)) for _ in range(n)]
        # List => String
        return ''.join(l)

    def listholder(self, l, n=None):
        return [self.strholder(_l, n) for _l in l]


_global_instance = Placeholder()
strholder = _global_instance.strholder
listholder = _global_instance.listholder
