# coding=utf-8
"""Mal Runtime environment.

"""
import malpy.actionrunner


class Runner(malpy.actionrunner.ActionRunner):
    """This is a default runtime environment.

    It sets memory on instantiation and zeros the registers with no JIT actions

    """
    def __init__(self):
        super(Runner, self).__init__(dict([]))
