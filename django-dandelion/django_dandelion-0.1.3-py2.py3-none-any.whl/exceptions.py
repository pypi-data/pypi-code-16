# -*- coding: utf-8

from __future__ import unicode_literals


class DandelionException(Exception):
    def __init__(self, message, **kwargs):
        self.message = message
        self.code = kwargs.get('code')
        self.data = kwargs.get('data')

        super(DandelionException, self).__init__(self.message)


class DandelionSettingsException(Exception):
    """Raised when settings be bad."""
