"""Parse requirements.

Extends the behavior of pkg_resources.Requirement
"""
from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import sys

import pkg_resources


class Requirement(object):
    """A proxy of pkg_resources.Requirement that supports some extensions.

    Namely, it supports "environment checks."
    """

    def __init__(self, req_str):
        req_str = str(req_str)
        try:
            req_str, self.conditional = req_str.split(';', 1)
        except ValueError:  # Not enough parts to unpack
            self.conditional = ''
        self.__requirement = pkg_resources.Requirement.parse(req_str)

    def is_needed_for(self, environment):
        """Check if this requirement applies to the current environment.

        Environment is a dictionary.
        """
        if not self.conditional:
            return True
        environment['__builtins__'] = None
        try:
            return eval(self.conditional, {'__builtins__': None}, environment)
        except Exception:
            import pprint
            print("Failed to evaluate conditional:",
                  self.conditional,
                  file=sys.stderr)
            pprint.pprint(environment, stream=sys.stderr)
            raise

    def __getattr__(self, attr):
        return getattr(self.__requirement, attr)

    def __str__(self):
        return str(self.__requirement)
