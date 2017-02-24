# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL._pyk2
#
# Purpose
#    Python2 specific implementation of TFL.pyk
#
# Revision Dates
#    16-Jun-2010 (CT) Creation
#     5-Jan-2011 (CT) `pickle` added
#    18-Apr-2012 (CT) Change `fprint` to encode `sep` and `end`, too
#    23-May-2013 (CT) Add `string_types`, `text_type`, `Classic_Class_Type`
#    23-May-2013 (CT) Add class decorator `adapt__bool__`
#    24-May-2013 (CT) Add `adapt__div__`, `adapt__str__`
#    24-May-2013 (CT) Add `iteritems`, `iterkeys`, `itervalues`, `xrange`
#    24-May-2013 (CT) Add `int_types`
#    25-May-2013 (CT) Add `new_instancemethod`, `izip`, `zip`
#    26-May-2013 (CT) Convert to class/instance to allow lazy imports
#     9-Oct-2013 (CT) Add `izip`
#    27-Nov-2013 (CT) Add `number_types`
#     3-Jan-2014 (CT) Factor `encoded`, `user_config`
#    17-Feb-2014 (CT) Add `decoded`
#    22-Aug-2014 (CT) Allow multiple `encodings` for `encoded`
#     7-Oct-2014 (CT) Add `config_parser`, `ifilter`, `reprify`
#     9-Oct-2014 (CT) Add `builtins`
#    10-Oct-2014 (CT) Add `urlencode`, `urlparse`
#    13-Oct-2014 (CT) Add `byte_type`
#    13-Oct-2015 (CT) Add `copyreg`
#    20-Oct-2015 (CT) Add `as_str`
#    25-Oct-2015 (CT) Add `pickle_protocol`
#     3-Nov-2015 (CT) Move argument "replace" to `else` clause of `decoded`
#     4-Nov-2015 (CT) Add `email_as_bytes`, `email_message_from_bytes`
#     2-Oct-2016 (CT) Change `adapt__str__` to import `_TFL.I18N`
#    ««revision-date»»···
#--

import functools
import itertools
import sys

def lazy_property (fct) :
    name = fct.__name__
    @functools.wraps (fct)
    def _ (self) :
        try :
            result = self.__dict__ [name]
        except KeyError :
            result = self.__dict__ [name] = fct (self)
        return result
    return property (_)
# end def lazy_property

class _Pyk_ (object) :
    """Python2 specific implementation of TFL.pyk.

       Use a class instead of module-level definitions to allow lazy imports.
    """

    @staticmethod
    def adapt__bool__ (cls) :
        dct = cls.__dict__
        if "__bool__" in dct and "__nonzero__" not in dct :
            setattr (cls, "__nonzero__", dct ["__bool__"])
        return cls
    # end def adapt__bool__

    @staticmethod
    def adapt__div__ (cls) :
        dct = cls.__dict__
        if "__truediv__" in dct and "__div__" not in dct :
            cls.__div__ = cls.__truediv__
        if "__itruediv__" in dct and "__idiv__" not in dct :
            cls.__idiv__ = cls.__itruediv__
        if "__rtruediv__" in dct and "__rdiv__" not in dct :
            cls.__rdiv__ = cls.__rtruediv__
        return cls
    # end def adapt__div__

    @staticmethod
    def adapt__str__ (cls) :
        dct = cls.__dict__
        if "__str__" in dct and "__unicode__" not in dct :
            from _TFL.I18N import encode_o
            cls.__unicode__ = cls.__str__
            cls.__str__     = lambda s : encode_o (s.__unicode__ ())
        return cls
    # end def adapt__str__

    @lazy_property
    def builtins (self) :
        import __builtin__
        return __builtin__
    # end def builtins

    byte_type  = str
    byte_types = (bytes, str)

    @lazy_property
    def Classic_Class_Type (self) :
        import types
        return types.ClassType
    # end def Classic_Class_Type

    @lazy_property
    def config_parser (self) :
        import ConfigParser
        return ConfigParser
    # end def config_parser

    @lazy_property
    def copyreg (self) :
        import copy_reg
        return copy_reg
    # end def copyreg

    @staticmethod
    def decoded (v, * encodings) :
        if not encodings :
            encodings = [pyk.user_config.input_encoding]
        if isinstance (v, str) :
            for encoding in encodings :
                try :
                    v = v.decode (encoding)
                except Exception as exc :
                    pass
                else :
                    break
            else :
                v = v.decode (encoding, "replace")
        elif not isinstance (v, unicode) :
            v = unicode (v)
        return v
    # end def decoded

    @lazy_property
    def email_as_bytes (self) :
        from email.message import Message
        return Message.as_string
    # end def email_as_bytes

    @lazy_property
    def email_message_from_bytes (self) :
        from email import message_from_string
        return message_from_string
    # end def email_message_from_bytes

    @staticmethod
    def encoded (v, encoding = None) :
        if encoding is None :
            encoding = pyk.user_config.output_encoding
        if not isinstance (v, basestring) :
            v = unicode (v)
        if isinstance (v, unicode) :
            v = v.encode (encoding, "replace")
        return v
    as_str = encoded # end def encoded

    @staticmethod
    def fprint (* values, ** kw) :
        """print(value, ..., sep=' ', end='\\n', file=sys.stdout)

           Prints the values to a stream, or to sys.stdout by default.
           Optional keyword arguments:
           file: a file-like object (stream); defaults to the current sys.stdout.
           sep:  string inserted between values, default a space.
           end:  string appended after the last value, default a newline.
        """
        file = kw.pop ("file", None)
        if file is None :
            file = sys.stdout
        enc      = pyk.user_config.output_encoding
        convert  = pyk.encoded
        sep      = convert (kw.pop ("sep",  " "),  enc)
        end      = convert (kw.pop ("end",  "\n"), enc)
        txt      = sep.join (convert (v, enc) for v in values)
        file.write (txt + end)
    # end def fprint

    ifilter   = itertools.ifilter
    int_types = (int, long)
    izip      = itertools.izip

    @staticmethod
    def iteritems (dct) :
        return dct.iteritems ()
    # end def iteritems

    @staticmethod
    def iterkeys (dct) :
        return dct.iterkeys ()
    # end def iterkeys

    @staticmethod
    def itervalues (dct) :
        return dct.itervalues ()
    # end def itervalues

    @lazy_property
    def izip (self) :
        import itertools
        return itertools.izip
    # end def izip

    long_types = (long, )

    @lazy_property
    def new_instancemethod (self) :
        import new
        return new.instancemethod
    # end def new_instancemethod

    number_types = (int, long, float)

    @lazy_property
    def pickle (self) :
        import cPickle
        return cPickle
    # end def pickle

    pickle_protocol = 2
    range           = staticmethod (range)

    @staticmethod
    def reprify (r) :
        return pyk.encoded (r)
    # end def reprify

    @lazy_property
    def StringIO (self) :
        import cStringIO
        return cStringIO.StringIO
    # end def StringIO

    string_types = (str, unicode)
    text_type    = unicode
    unichr       = unichr

    @lazy_property
    def urlencode (self) :
        from urllib import urlencode
        return urlencode
    # end def urlencode

    @lazy_property
    def urlparse (self) :
        import urlparse
        return urlparse
    # end def urlparse

    @lazy_property
    def user_config (self) :
        from   _TFL.User_Config import user_config
        return user_config
    # end def user_config

    xrange       = staticmethod (xrange)
    zip          = staticmethod (zip)

# end class _Pyk_

pyk = _Pyk_ ()

### __END__ TFL._pyk2
