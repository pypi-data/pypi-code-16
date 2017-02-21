# -*- coding: utf-8 -*-


class ConfigValidation(object):
    def __init__(self, config, errors=None):
        self.config = config
        self.errors = errors

    @property
    def has_error(self):
        return bool(self.errors)


class MissingBlingConfig(Exception):
    pass


class MalformedBlingConfig(Exception):
    pass


class InvalidBlingConfig(Exception):
    pass
