# coding=utf-8
"""
Mal Runtime environment.
"""
import collections

import malpy.actionrunner

Flags = collections.namedtuple('Flags', ('halt',
                                         'div_by_zero',
                                         'out_of_bounds',
                                         'bad_operand'))


class Runner(malpy.actionrunner.ActionRunner):
    """
    This is a default runtime environment.
    It sets memory on instantiation and zeros the registers with no JIT actions
    """
    def __init__(self):
        super(Runner, self).__init__(dict([]))
