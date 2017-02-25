# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.Mime_Type
#
# Purpose
#    Model mime type renderers
#
# Revision Dates
#    15-Jun-2012 (CT) Creation
#    24-Jul-2012 (CT) Add `TXT`
#    31-Jul-2012 (CT) Add and use `mime_type_parameters`
#     8-Aug-2012 (CT) Add `rst_cargo` to `_Template_Mixin_.rendered`
#    10-Aug-2012 (CT) Consider `resource.ext` in `Render_Man.__call__`
#    10-Aug-2012 (CT) Fix `Render_Man.render_acceptable`
#    25-Sep-2012 (CT) Add `SVG`
#     5-Oct-2012 (CT) Add and use `JSON.json_dump_kw`
#    14-Jan-2013 (CT) Add `User_Cert`
#    14-Jun-2013 (CT) Add default implementation for `CSV.rendered`
#    15-Jun-2013 (CT) Guard `CSV.rendered` against empty `body`
#    30-Jan-2014 (CT) Add exception information to `CSV.rendered`
#     6-May-2015 (CT) Use `TFL.json_dump.to_string`
#    17-Nov-2015 (CT) Add `not_picky` to `Render_Man.__call__`
#                     + Consider `not request.accept_mimetypes` as `not_picky`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.multimap            import mm_list
from   _TFL.pyk                 import pyk
from   _TFL                     import sos

import _TFL._Meta.M_Class
import _TFL._Meta.Object
import _TFL.Accessor
import _TFL.json_dump
import _TFL.Record

from   posixpath import splitext as pp_splitext

class _Meta_ (TFL.Meta.M_Class) :
    """Meta class for mime type renderers."""

    Table = {}

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        name = cls.__name__
        if not name.startswith ("_") :
            if name not in cls.Table :
                cls.name = name
                cls.Table [name] = cls
            if not cls.extensions :
                cls.extensions = (name.lower (), )
    # end def __init__

# end class _Meta_

class _Base_ (TFL.Meta.BaM (TFL.Meta.Object, metaclass = _Meta_)) :
    """Base class for mime type renderers.

       http://tools.ietf.org/html/rfc4287
    """

    ### to be defined by subclasses
    extensions                 = ()
    force_charset              = None
    mime_types                 = ()
    mime_type_parameters       = ()

    def __init__ (self, method, resource, mime_type = None) :
        if mime_type is None :
            mime_type = self.mime_types [0]
        else :
            assert mime_type in self.mime_types, (mime_type, mime_types)
        self.method    = method
        self.resource  = resource
        self.mime_type = mime_type
    # end def __init__

    def __call__ (self, request, response, body) :
        self.set_mime_type (request, response, body)
        result = self.rendered (request, response, body)
        if result :
            response.write (result)
        return result
    # end def __call__

    @property
    def charset (self) :
        if self.force_charset :
            return self.force_charset
        else :
            return self.resource.encoding
    # end def charset

    def rendered (self, request, response, body) :
        raise NotImplementedError \
            ( "%s.%s.%s.rendered needs to be implemented"
            % ( self.resource.__class__.__name__
              , request.method
              , self.__class__.__name__
              )
            )
    # end def rendered

    def set_mime_type (self, request, response, body) :
        mime_type = self.mime_type
        if self.mime_type_parameters :
            mime_type = "; ".join \
                ((mime_type, ) + tuple (self.mime_type_parameters))
        response.charset  = self.charset
        response.mimetype = mime_type
    # end def set_mime_type

# end class _Base_

class _Template_Mixin_ (_Base_) :
    """Mixin for rendering using a template."""

    template_attr_name = "template"

    @Once_Property
    def render_context (self) :
        return getattr (self.method, "render_context", {})
    # end def render_context

    @Once_Property
    def template (self) :
        tan = self.template_attr_name
        try :
            return getattr (self.method,   tan)
        except AttributeError :
            return getattr (self.resource, tan)
    # end def template

    def rendered (self, request, response, body) :
        context = self.render_context
        context.setdefault ("rst_cargo", body)
        context.setdefault ("resource",  self.resource)
        return self.template.render (context)
    # end def rendered

# end class _Template_Mixin_

class RST_ATOM (_Base_) :
    """Renderer for mime type ATOM.

       http://tools.ietf.org/html/rfc4287
    """

    _real_name                 = "ATOM"
    mime_types                 = ("application/atom+xml", )

ATOM = RST_ATOM # end class

class RST_CSV (_Base_) :
    """Renderer for mime type CSV.

       http://tools.ietf.org/html/rfc4180
    """

    _real_name                 = "CSV"
    mime_types                 = ("text/csv", )

    def rendered (self, request, response, body) :
        if isinstance (body, dict) :
            import csv
            names = body.get ("names")
            if names :
                rs  = body ["rows"]
                nm  = dict ((n, n) for n in names)
                f   = pyk.StringIO   ()
                dw  = csv.DictWriter (f, names)
                dw.writerow          (nm)
                try :
                    dw.writerows (rs)
                except Exception as exc :
                    msg = "%s\n    Names: %s\n    Rows:\n        %s" % \
                        ( exc, names
                        , "\n        ".join
                            (str (sorted (r.items ())) for r in rs)
                        )
                    raise exc.__class__ (msg)
                return f.getvalue    ()
    # end def rendered

CSV = RST_CSV # end class

class RST_HTML (_Base_) :
    """Renderer for mime type HTML.

       http://tools.ietf.org/html/rfc2854
    """

    _real_name                 = "HTML"
    extensions                 = ("html", "htm")
    mime_types                 = ("text/html", )

HTML = RST_HTML # end class

class RST_HTML_T (_Template_Mixin_, HTML) :
    """Renderer for mime type HTML using a template to render."""

    _real_name                 = "HTML_T"

HTML_T = RST_HTML_T # end class

class RST_JSON (_Base_) :
    """Renderer for JSON mime types.

       http://tools.ietf.org/html/rfc4627
    """

    _real_name                 = "JSON"
    force_charset              = "utf-8"
    json_dump_kw               = {}
    mime_types                 = ("application/json", )

    def rendered (self, request, response, body) :
        if isinstance (body, (dict, list, tuple)) :
            result = TFL.json_dump.to_string (body, ** self.json_dump_kw)
            return result
    # end def rendered

JSON = RST_JSON # end class

class RST_SVG (_Base_) :
    """Renderer for XML mime types.

       http://tools.ietf.org/html/rfc3023
    """

    _real_name                 = "SVG"
    mime_types                 = ("image/svg+xml", )

    def rendered (self, request, response, body) :
        if not isinstance (body, pyk.string_types) :
            raise TypeError ("Expected string; got: %r" % (body, ))
        return body
    # end def rendered

SVG = RST_SVG # end class

class RST_TXT (_Base_) :
    """Renderer for mime type text."""

    _real_name                 = "TXT"
    mime_types                 = ("text/plain", )

    def rendered (self, request, response, body) :
        if isinstance (body, dict) :
            body = \
                ["%s = %r" % (k, v) for k, v in sorted (pyk.iteritems (body))]
        if isinstance (body, (list, tuple)) :
            body = "\n".join (body)
        elif not isinstance (body, pyk.string_types) :
            raise TypeError \
                ("Expected string, list, or dict; got: %r" % (body, ))
        return body
    # end def rendered

TXT = RST_TXT # end class RST_TXT

class RST_User_Cert (_Base_) :
    """Renderer for mime type x509-user-cert."""

    _real_name                = "User_Cert"
    mime_types                = ("application/x-x509-user-cert", )

    def rendered (self, request, response, body) :
        return body
    # end def rendered

User_Cert = RST_User_Cert # end class

class RST_XHTML (_Base_) :
    """Renderer for mime type XHTML.

       http://tools.ietf.org/html/rfc3023
    """

    _real_name                 = "XHTML"
    mime_types                 = ("application/xhtml+xml", )

XHTML = RST_XHTML # end class

class RST_XML (_Base_) :
    """Renderer for XML mime types.

       http://tools.ietf.org/html/rfc3023
    """

    _real_name                 = "XML"
    mime_types                 = ("text/xml", "application/xml")

XML = RST_XML # end class

class Render_Man (TFL.Meta.Object) :
    """Encapsulate the mime type renderers supported by a HTTP_Method/Resource."""

    def __init__ (self, renderers) :
        self.renderers = tuple (renderers)
    # end def __init__

    @Once_Property
    def by_extension (self) :
        result = mm_list ()
        for r in self.renderers :
            for ext in r.extensions :
                result [ext].append (r)
        return result
    # end def by_extension

    @Once_Property
    def by_mime_type (self) :
        result = mm_list ()
        for r in self.renderers :
            for mt in r.mime_types :
                result [mt].append (r)
        return result
    # end def by_mime_type

    def __call__ (self, method, resource, request) :
        result = None
        _, ext = pp_splitext (request.path)
        ext    = (ext or resource.ext or "").strip (".")
        if ext :
            rs = self.by_extension [ext]
            if rs :
                result    = rs [0]
                mime_type = None
        if result is None :
            matches = sorted \
                ( self._matches (request.accept_mimetypes)
                , key     = TFL.Getter.priority
                , reverse = True
                )
            if matches :
                match     = matches [0]
                result    = match.render
                mime_type = match.mime_type
        not_picky = \
            resource.ignore_picky_accept or not request.accept_mimetypes
        if result is None and not_picky and self.renderers :
            result    = self.renderers [0]
            mime_type = None
        if result is not None :
            return result (method, resource, mime_type)
    # end def __call__

    def render_acceptable (self, method, resource, request, response) :
        l = []
        body = dict (accept_mimetypes = l)
        urlb, ext = pp_splitext (request.url)
        for r in self.renderers :
            url = ".".join ((urlb, r.extensions [0])) if r.extensions else urlb
            l.append \
                ( dict
                    ( extensions = r.extensions
                    , mime_types = r.mime_types
                    , url        = url
                    )
                )
        renderer = getattr (method, "accept_mimetypes_renderer", JSON) \
            (method, resource)
        response.status_code = 406
        renderer (request, response, body)
    # end def render_acceptable

    def _matches (self, accept) :
        for r in self.renderers :
            for mt in r.mime_types :
                p = accept [mt]
                if p :
                    yield TFL.Record (render = r, mime_type = mt, priority = p)
    # end def _matches

# end class Render_Man

if __name__ != "__main__" :
    GTW.RST._Export_Module ()
### __END__ GTW.RST.Mime_Type
