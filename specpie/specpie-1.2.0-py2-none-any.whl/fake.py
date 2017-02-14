# -*- coding: utf-8 -*-

import sys


class Fake:
    def __init__(self, what, replacer):
        self.what = what
        self.replacer = replacer

    def __call__(self, f):
        def deco(*args, **kwargs):
            parts = self.what.split('.')
            func_name = parts[-1]
            module = '.'.join(parts[:-1])
            setattr(sys.modules[module], func_name, self.replacer)
            f(self.replacer, *args, **kwargs)

        return deco
