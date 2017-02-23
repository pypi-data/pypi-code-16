# -*- coding:utf-8 -*-

class ValidationError(Exception):

    def __init__(self, message, code=None, params=None):

        super(ValidationError, self).__init__(message, code, params)
        self.message = message
        self.params = params

    def __str__(self):
        return self.message.format(**self.params)