from __future__ import print_function
class A(object):
    def __init__(self, *args):
        print("init",*args)
        args[0].g = self.g
        self._cls = args[0]
    def g(self, *args):
        print("overriden g", self, args)

    def __call__(self, *args):
        print("call", *args)
        return self._cls(args[0])

@A
class B(object):
    def __init__(self, *args):
        print("Init of B", *args)

    def g(self):
        print("real g")

b = B(1,2,3)
b.g()
