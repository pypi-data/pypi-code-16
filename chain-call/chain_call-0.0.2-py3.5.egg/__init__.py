from functools import partial


class Call():

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __getattr__(self, name):
        return Param(self.func, name)


class Param():

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def __call__(self, parm):
        parms = {}
        parms[self.name] = parm
        return Call(partial(self.parent, **parms))

def main():
    print("This is the chain-call module.")
    print("You can use it like this:")
    print("> Call(print).sep('.').end('\\n*****')(1,2,'aaa')")
    Call(print).sep('.').end('\n*****')(1,2,'aaa')