#!/usr/bin/env python
"""
interface for Reflector backends
"""

def notimplemented(func):
    """
    mark a function as not implemented
    TODO: calling should raise a NotImplementedError 
    """
    func.notimplemented = True
    return func

class Reflector(object):

    def __init__(self):
        pass
    
    ### API

    @notimplemented
    def sync(self):
        """
        synchronize
        """

### for testing notimplemented decorator

class Foo(object):

    @notimplemented
    def bar(self):
        "stufff"

    @notimplemented
    def fleem(self):
        pass

    @notimplemented
    def foox(self):
        pass

class Bar(Foo):

    def bar(self):
        return 1

    @notimplemented
    def fleem(self):
        pass

if __name__ == '__main__':
    foo = Foo()
    bar = Bar()
    import pdb; pdb.set_trace()
