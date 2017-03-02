# -*- coding: utf-8 -*-

from .compat import basestring


class StrSnippets(object):
    def strip(self, s):
        return s.strip() if isinstance(s, basestring) else s


_global_instance = StrSnippets()
strip = _global_instance.strip
