"""
This file contains a CypressBase class. Inherit
"""
import os
from .logger_helper import get_logger


class CypressBase(object):

    def __init__(self):
        self.debug_mode = self.__is_debug_mode()
        self.logger = get_logger(__name__, verbose=self.is_verbose())

    def get_debug_mode(self):
        return self.debug_mode

    def __is_debug_mode(self):
        return self.get_value_from_env('DEBUG', default=False)

    def is_verbose(self):
        return self.debug_mode or self.get_value_from_env('VERBOSE', default=False)

    def get_value_from_env(self, key, default=None):
        val = default
        try:
            v = os.environ.get(key)
            if v.lower() == 'true':
                val = True
            elif v.lower() == 'false':
                val = False
            else:   # if v is integer, or
                val = v
                try:
                    val = int(v)
                except ValueError:
                    try:
                        val = float(v)
                    except ValueError:
                        pass
        except AttributeError:
            pass

        return val
