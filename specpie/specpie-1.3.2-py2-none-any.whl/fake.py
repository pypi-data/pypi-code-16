# -*- coding: utf-8 -*-

import sys


class Fake:
    def __init__(self, what, replacer, name=None):
        self.name = name
        self.what = what
        self.fake = replacer
        self.real = None

    def fake_it(self):
        parts = self.what.split('.')
        func_name = parts[-1]
        module = '.'.join(parts[:-1])
        self.real = getattr(sys.modules[module], func_name)
        setattr(sys.modules[module], func_name, self.fake)

    def legitimize_it(self):
        parts = self.what.split('.')
        func_name = parts[-1]
        module = '.'.join(parts[:-1])
        setattr(sys.modules[module], func_name, self.real)

    def __enter__(self):
        self.fake_it()
        return self.fake

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.legitimize_it()
        return exc_type == AssertionError

    def __call__(self, f):
        def deco(*args, **kwargs):
            self.fake_it()
            try:
                if self.name is not None:
                    kwargs[self.name] = self.fake
                f(*args, **kwargs)
            except Exception as e:
                raise e
            finally:
                self.legitimize_it()

        return deco
