"""The base command."""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import


from future import standard_library
standard_library.install_aliases()
class Base(object):
    """A base command."""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        raise NotImplementedError('You must implement the run() method yourself!')
