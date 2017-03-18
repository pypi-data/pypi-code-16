# -*- coding: utf-8 -*-

import codecs
import io
import sys


IS_PY2 = (sys.version_info[0] == 2)
IS_PY3 = (sys.version_info[0] == 3)

if IS_PY2:
    def u(text):
        if isinstance(text, str):
            return text.decode('utf-8')
        return unicode(text)

    def utf8_encode(text):
        if isinstance(text, unicode):
            return text.encode('utf-8')
        return text
    open = codecs.open
    basestring = basestring
    file = (file, codecs.Codec, codecs.StreamReaderWriter)

elif IS_PY3:
    def u(text):
        if isinstance(text, bytes):
            return text.decode('utf-8')
        return str(text)

    def utf8_encode(text):
        if isinstance(text, str):
            return text.encode('utf-8')
        return text
    open = open
    basestring = (str, bytes)
    file = io.IOBase
