# -*- coding: utf-8 -*-
# Copyright (C) 2006 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Text_Translation_Cacher
#
# Purpose
#    Provide caching for text translations
#
# Revision Dates
#    14-Jun-2006 (CT) Creation
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    ««revision-date»»···
#--



from   _TFL import TFL
import _TFL._Meta.Object

class Text_Translation_Cacher (TFL.Meta.Object) :
    """Provide caching for text translations.

       >>> ttc = Text_Translation_Cacher (
       ...     dict (foo = "bar", bar = "baz", qux = "hu?").get)
       >>> sorted (ttc._cache.items ())
       []
       >>> ttc ("wibble")
       'wibble'
       >>> sorted (ttc._cache.items ())
       [('wibble', 'wibble')]
       >>> ttc ("foo")
       'bar'
       >>> sorted (ttc._cache.items ())
       [('foo', 'bar'), ('wibble', 'wibble')]
       >>> ttc ("bar")
       'baz'
       >>> sorted (ttc._cache.items ())
       [('bar', 'baz'), ('foo', 'bar'), ('wibble', 'wibble')]
       >>> ttc ("42")
       '42'
       >>> sorted (ttc._cache.items ())
       [('42', '42'), ('bar', 'baz'), ('foo', 'bar'), ('wibble', 'wibble')]
    """

    def __init__ (self, translator = None) :
        if translator is not None :
            self.translator = translator
        self._cache = {}
    # end def __init__

    def __call__ (self, text) :
        cache  = self._cache
        result = cache.get (text)
        if result is None :
            t = self.translator (text)
            if t is None :
                t = text
            result = cache [text] = t
        return result
    # end def __call__

# end class Text_Translation_Cacher

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Text_Translation_Cacher
