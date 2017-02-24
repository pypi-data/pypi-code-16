# -*- coding: utf-8 -*-
# Copyright (C) 2009-2016 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package CHJ.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    CHJ.Media
#
# Purpose
#    Encapsulate media specific snippets
#
# Revision Dates
#     9-Jul-2009 (CT) Creation
#    10-Jul-2009 (CT) Creation continued
#    10-Jul-2009 (CT) `Script` added and `js_code` removed
#    10-Jul-2009 (CT) `Rel_Link` added
#    13-Jul-2009 (CT) `Rel_Link.attrs` fixed
#    14-Jul-2009 (CT) `Media_List_JSOR` added and used for `js_on_ready`
#    14-Jul-2009 (CT) `__len__` and `__nonzero__` added to `Media_List`
#    21-Aug-2009 (MG) `JS_On_Ready` added and used to support sorting in
#                     `Media_List_JSOR`
#    10-Jan-2010 (MG) Moved into Package `GTW`
#     2-Feb-2010 (MG) `Media_List.add` added
#     4-Feb-2010 (MG) `Media.from_list` added
#    27-Feb-2010 (MG) `sort_key` added to javascript
#     1-May-2010 (MG) Use `M_Unique_If_Named` to support reuse of media
#                     objects
#     7-Dec-2010 (CT) `condition` added to `Script`
#    13-Sep-2011 (MG) `s/sort_key/rank/g`
#    13-Sep-2011 (MG) `Rel_Link`: `__str__` and `__repr__` added
#    14-Oct-2011 (MG) `JS_On_Ready`: parameter `code` can be a `JS_On_Ready`
#                     as well
#     3-Jan-2012 (CT) Factor `_Object_`, add and use `requires` and `objects`
#     4-Jan-2012 (CT) Add `Script.cache_p`
#     5-Jan-2012 (CT) Remove `Script.body`
#     8-Jan-2012 (CT) Use `.pop_to_self` to reduce footprint of media objects
#     9-Jan-2012 (CT) Add `minified_css` and `minified_js`
#    14-Aug-2012 (MG) Add support for domains
#     4-Dec-2012 (MG) Fix media `Domain` handling
#    22-Feb-2013 (CT) Use `TFL.Undef ()` not `object ()`
#    18-Mar-2015 (CT) Add support for debian-packaged `cssmin` and `jsmin`
#    20-Mar-2015 (CT) Change `minified_css`, `minified_js` to never return None
#    20-Mar-2015 (CT) Fix `minified_css`, `minified_js`
#    15-Apr-2015 (CT) Try `rcssmin` and `rjsmin` before `cssmin` and `jsmin`
#                     * On my machine, _GTW/__test__/NAV.py runs in:
#                       -  5 seconds with rcssmin, rjsmin
#                       - 37 seconds with cssmin,  jsmin
#    26-Jun-2015 (CT) Add trailing `;` to `JS_On_Ready.code`, if missing
#     2-Dec-2015 (CT) Add `logging.warning` to `minified_css`, `minified_js`
#    20-Jan-2016 (CT) Add `_clean_minified_js` to remove superfluous `;`
#     5-Feb-2016 (CT) Add encoding dance around `_clean_minified_js` call
#    11-Oct-2016 (CT) Move from `GTW` to `CHJ`
#    30-Dec-2016 (CT) Add `./` to `dont_join` of `Media_List_href._gen_all`
#    ««revision-date»»···
#--

from   __future__                         import print_function

from   _TFL                               import TFL
from   _CHJ                               import CHJ

import _TFL.predicate
import _TFL.Undef

import _TFL._Meta.Object
import _TFL._Meta.M_Unique_If_Named

from   _TFL._Meta.Once_Property           import Once_Property
from   _TFL._Meta.Property                import Alias_Property
from   _TFL.pyk                           import pyk
from   _TFL.Regexp                        import \
    Regexp, Re_Replacer, Multi_Re_Replacer, re

from   posixpath                          import join as pjoin

import logging

class Media_Base (TFL.Meta.Object) :
    """Base class for media objects."""

    rank         = 0
    requires     = ()

    Domain       = None

    @Once_Property
    def objects (self) :
        def _gen (s) :
            for r in s.requires :
                for o in r.objects :
                    yield o
            yield s
        return tuple (_gen (self))
    # end def objects

    @classmethod
    def _sanitized (cls, mobs, Mob_Type = None) :
        if Mob_Type is None :
            Mob_Type = cls
        for mob in mobs :
            if not isinstance (mob, Mob_Type) :
                mob = Mob_Type (mob)
            yield mob
    # end def _sanitized

# end class Media_Base

class CSS_Link \
        (TFL.Meta.BaM (Media_Base, metaclass = TFL.Meta.M_Unique_If_Named)) :
    """Model a CSS link object."""

    condition     = ""
    media_type    = "all"
    name          = None

    def __init__ (self, href, ** kw) :
        self.href = href
        self.pop_to_self (kw, "condition", "media_type", "name", "rank")
    # end def __init__

    def __eq__ (self, rhs) :
        try :
            rhs = rhs.href, rhs.media_type
        except AttributeError :
            pass
        return (self.href, self.media_type) == rhs
    # end def __eq__

    def __hash__ (self) :
        return hash ((self.href, self.media_type))
    # end def __hash__

    def __repr__ (self) :
        return "%s: %s" % (self.media_type, self.href)
    # end def __repr__

    def __str__ (self) :
        return self.href
    # end def __str__

# end class CSS_Link

class Rel_Link (Media_Base) :
    """Model a `rel` link object."""

    def __init__ (self, ** kw) :
        self.href = kw ["href"]
        self.pop_to_self (kw, "rank")
        self._kw  = kw
    # end def __init__

    def attrs (self) :
        return " ".join \
            (   '''%s="%s"''' % (k, v)
            for (k, v) in sorted (pyk.iteritems (self._kw))
            )
    # end def attrs

    def __repr__ (self) :
        return self.attrs ()
    # end def __repr__

    def __str__ (self) :
        return self.href
    # end def __str__

# end class Rel_Link

class Script \
        (TFL.Meta.BaM (Media_Base, metaclass = TFL.Meta.M_Unique_If_Named)) :
    """Model a script element"""

    href          = Alias_Property ("src")

    condition     = ""
    may_cache     = True
    name          = None
    script_type   = "text/javascript"

    def __init__ (self, src, ** kw) :
        assert src
        self.src  = src
        self.pop_to_self \
            ( kw
            , "condition", "may_cache", "name", "rank", "requires"
            , "script_type"
            )
        if self.requires :
            self.requires = tuple (self._sanitized (self.requires))
    # end def __init__

    @Once_Property
    def absolute_p (self) :
        return self.src.startswith (("//", "http://", "https://"))
    # end def absolute_p

    @Once_Property
    def cache_p (self) :
        return self.may_cache and not (self.condition or self.absolute_p)
    # end def cache_p

    def __eq__ (self, rhs) :
        try :
            rhs = (rhs.src, rhs.script_type)
        except AttributeError :
            pass
        return (self.src, self.script_type) == rhs
    # end def __eq__

    def __hash__ (self) :
        return hash ((self.src, self.script_type))
    # end def __hash__

    def __repr__ (self) :
        return "%s: %s" % (self.src, self.script_type)
    # end def __repr__

    def __str__ (self) :
        return self.src
    # end def __str__

# end class Script

class JS_On_Ready \
        (TFL.Meta.BaM (Media_Base, metaclass = TFL.Meta.M_Unique_If_Named)) :
    """A javascript code which should be executed once the document is loaded"""

    default_rank  = TFL.Undef ("rank")
    name          = None

    def __init__ (self, code, rank = default_rank, ** kw) :
        if isinstance (code, self.__class__) :
            if rank is self.default_rank :
                rank   = code.rank
            code       = code.code
        elif rank is self.default_rank :
            rank       = 0
        code           = code.strip ()
        if not code.endswith (";") :
            code      += ";"
        self.code      = code
        if self.rank :
            self.rank  = rank
        self.pop_to_self (kw, "name")
    # end def __init__

    def __str__ (self) :
        return self.code
    # end def __str__

# end class JS_On_Ready

@pyk.adapt__bool__
class Media_List (TFL.Meta.Object) :
    """Model a list of media objects"""

    def __init__ (self, name, media, mobs) :
        self.name  = name
        self.media = media
        self.mobs  = list (mobs)
    # end def __init__

    def add (self, * mob) :
        self.mobs.extend (self._sanitized (mob))
    # end def add

    @Once_Property
    def values (self) :
        return tuple (self._gen_all ())
    # end def values

    def _gen_all (self) :
        for mob in self._gen_own () :
            for o in mob.objects :
                yield o
        name = self.name
        for child in self.media.children :
            for mob in getattr (child, name) :
                yield mob
    # end def _gen_all

    def _gen_own (self) :
        for mob in self.mobs :
            yield mob
    # end def _gen_own

    def __len__ (self) :
        return len (self.values)
    # end def __len__

    def __bool__ (self) :
        return bool (self.values)
    # end def __bool__

    def __iter__ (self) :
        return iter (self.values)
    # end def __iter__

    def __str__ (self) :
        return "\n".join (str (v) for v in self)
    # end def __str__

    def _sanitized (self, mobs) :
        Mob_Type = self.Mob_Type
        if Mob_Type :
            return Mob_Type._sanitized (mobs)
        else :
            return mobs
    # end def _sanitized

# end class Media_List

class Media_List_Unique (Media_List) :
    """Model a list of unique media objects (filters duplicates)."""

    def _gen_all (self) :
        return TFL.uniq (self.__super._gen_all ())
    # end def _gen_all

# end class Media_List_Unique

class Media_List_href (Media_List) :
    """Model a list of media objects with href"""

    prefix   = None
    Mob_Type = None

    def __init__ (self, name, media, mobs) :
        self.__super.__init__ (name, media, tuple (self._sanitized (mobs)))
    # end def __init__

    def _gen_own (self) :
        prefix    = self.prefix
        url       = self.media.url
        dont_join = ("http://", "https://", "/", "./")
        for mob in self.__super._gen_own () :
            href  = mob.href
            if href and not href.startswith (dont_join) :
                href = pjoin \
                    (* (x for x in (url, prefix, href) if x is not None))
            if (   href
               and not href.startswith (("http://", "https://"))
               and mob.Domain
               ) :
                sep  = "" if href [0] == "/" else "/"
                href = sep.join ((mob.Domain, href))
            mob.href = href
            yield mob
    # end def _gen_own

# end class Media_List_href

class Media_List_CSSL (Media_List_href, Media_List_Unique) :
    """Model a list of CSS_Link objects"""

    prefix   = "styles"
    Mob_Type = CSS_Link

# end class Media_List_CSSL

class Media_List_JSOR (Media_List_Unique) :
    """Model a list of javascript on-ready objects"""

    Mob_Type = JS_On_Ready

    def __init__ (self, name, media, mobs) :
        self.__super.__init__ (name, media, tuple (self._sanitized (mobs)))
    # end def __init__

    @Once_Property
    def values (self) :
        return tuple (sorted (self._gen_all (), key = lambda mob : mob.rank))
    # end def values

# end class Media_List_JSOR

class Media_List_Rell (Media_List_href) :

    prefix   = None
    Mob_Type = Rel_Link

# end class Media_List_Rell

class Media_List_Script (Media_List_href, Media_List_Unique) :
    """Model a list of script objects"""

    prefix   = "js"
    Mob_Type = Script

    @Once_Property
    def values (self) :
        return tuple (sorted (self._gen_all (), key = lambda mob : mob.rank))
    # end def values

# end class Media_List_Script

class Media (TFL.Meta.Object) :
    """
       >>> class Media (Media) :
       ...     url = "/test/"
       ...
       >>> NL = chr (10)

       >>> m = Media (css_links = ("a.css", "/b/c.css"),
       ...       scripts = ("foo.js", "bar.js", "http://baz.js"))
       >>> print (NL.join (repr (l) for l in m.css_links))
       all: /test/styles/a.css
       all: /b/c.css
       >>> tuple (str (l) for l in m.scripts)
       ('/test/js/foo.js', '/test/js/bar.js', 'http://baz.js')
       >>> n = Media (("/test/styles/a.css", CSS_Link ("c.css", media_type = "screen")))
       >>> print (NL.join (repr (l) for l in n.css_links))
       all: /test/styles/a.css
       screen: /test/styles/c.css
       >>> tuple (str (l) for l in n.scripts)
       ()
       >>> q = Media (scripts = ("qux.js", ), children = (m, n))
       >>> print (NL.join (repr (l) for l in q.css_links))
       all: /test/styles/a.css
       all: /b/c.css
       screen: /test/styles/c.css
       >>> "; ".join (str (l) for l in q.scripts)
       '/test/js/qux.js; /test/js/foo.js; /test/js/bar.js; http://baz.js'
       >>> m = Media (css_links = ("a.css", "/b/c.css"),
       ...       scripts = ("foo.js", "bar.js", "http://baz.js"))
       >>> Script.Domain   = "http://js.example.com"
       >>> CSS_Link.Domain = "http://css.example.com"
       >>> tuple (str (l) for l in m.scripts)
       ('http://js.example.com/test/js/foo.js', 'http://js.example.com/test/js/bar.js', 'http://baz.js')
       >>> tuple (str (l) for l in m.css_links)
       ('http://css.example.com/test/styles/a.css', 'http://css.example.com/b/c.css')
    """

    url = "/media"

    def __init__ (self, css_links = (), scripts = (), js_on_ready = (), rel_links = (), children = (), ** kw) :
        self.__dict__.update (kw)
        self.css_links   = Media_List_CSSL   ("css_links",   self, css_links)
        self.scripts     = Media_List_Script ("scripts",     self, scripts)
        self.js_on_ready = Media_List_JSOR   ("js_on_ready", self, js_on_ready)
        self.rel_links   = Media_List_Rell   ("rel_links",   self, rel_links)
        self.children    = list              (children)
    # end def __init__

    @classmethod
    def from_list (cls, medias, ** kw) :
        to_add = dict ((n, v) for n, v in pyk.iteritems (kw) if v)
        if len (medias) == 1 and not to_add :
            result = medias [0]
        else :
            result = \
                CHJ.Media (children = medias) if (medias or to_add) else None
        for n, v in pyk.iteritems (to_add) :
            getattr (result, n).add (* v)
        return result
    # end def from_list

# end class Media

def minified_css (style, keep_bang_comments = True) :
    """Return minified CSS `style`.

       If neither `cssmin`_ nor `rcssmin`_ is installed, `style` is returned
       unchanged.

       .. _`cssmin`: https://github.com/zacharyvoase/cssmin
       .. _`rcssmin`: http://opensource.perlig.de/rcssmin/
    """
    cssmin = None
    try :
        from rcssmin import cssmin
    except ImportError :
        try :
            ### https://packages.qa.debian.org/c/cssmin.html
            from cssmin import cssmin as _cssmin
            cssmin = lambda style, keep_bang_comments : _cssmin (style)
        except ImportError :
            logging.warning ("Couldn't import either rcssmin nor cssmin")
    if cssmin is not None :
        try :
            return cssmin (style, keep_bang_comments = keep_bang_comments)
        except Exception as exc :
            logging.error ("Exception during minified_css\n    %s" % (exc, ))
    return style
# end def minified_css

_clean_minified_js = Multi_Re_Replacer \
    ( Re_Replacer (r";+\}",    "}")
    , Re_Replacer (r";+\(",    ";(")
    , Re_Replacer (r";?\s*\Z", "\n")
    , Re_Replacer (r"\A;\s*",  "")
    )

def minified_js (code) :
    """Return minified javascript `code`.

       If neither `jsmin`_ nor `rjsmin`_ is installed, `code` is returned
       unchanged.

       .. _`jsmin`: https://bitbucket.org/dcs/jsmin/
       .. _`rjsmin`: http://opensource.perlig.de/rjsmin/
    """
    jsmin  = None
    result = code
    try :
        from rjsmin import jsmin
    except ImportError :
        try :
            ### https://packages.debian.org/sid/python/python-jsmin
            from jsmin import jsmin
        except ImportError :
            logging.warning ("Couldn't import either rjsmin nor jsmin")
    if jsmin is not None :
        try :
            result = jsmin (code)
        except Exception as exc :
            logging.error ("Exception during minified_js\n    %s" % (exc, ))
    return pyk.encoded \
        ( _clean_minified_js (pyk.decoded (result, "utf-8", "latin-1"))
        , "utf-8"
        )
# end def minified_js

if __name__ != "__main__":
    CHJ._Export ("*")
### __END__ CHJ.Media
