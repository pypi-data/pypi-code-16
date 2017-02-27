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
#    GTW.RST.__test__
#
# Purpose
#    Doctest for package GTW.RST
#
# Revision Dates
#    11-Jun-2012 (CT) Creation
#    29-Oct-2015 (CT) Improve Python 3 compatibility
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _GTW._RST.Resource       import *

from   _TFL.formatted_repr      import formatted_repr
from   _TFL.portable_repr       import portable_repr

def show_1 (resource, level) :
    p = resource.parent.abs_href if resource.parent else "-"
    t = resource.top.abs_href
    print ("%s%s parent = %s, top = %s" % ("  " * level, resource, p, t))
# end def show_1

def show (resource, level = 0) :
    show_1 (resource, level)
    for e in resource.entries :
        show (e, level + 1)
# end def show

__doc__ = """

    >>> e_types = ( Dir
    ...         ( name          = "PAP-Company"
    ...         , description   = "Legal person"
    ...         , entries       =
    ...             ( Leaf (name = "1", implicit = True)
    ...             ,
    ...             )
    ...         )
    ...     , Dir
    ...         ( name          = "PAP-Person"
    ...         , description   = "Natural person"
    ...         )
    ...     ,
    ...     )
    >>> root = Root ( HTTP = None
    ...     , language          = "en"
    ...     , entries           =
    ...         ( Leaf
    ...             ( name          = "about"
    ...             , implicit      = True
    ...             )
    ...         , Dir
    ...             ( name          = "v1"
    ...             , description   = "Version 1 of test RESTful api"
    ...             , entries       =
    ...                 ( Dir
    ...                     ( name          = "Meta"
    ...                     , description   = "Meta information about RESTful api"
    ...                     )
    ...                 ,
    ...                 ) + e_types
    ...             )
    ...         , Dir
    ...             ( name          = "v2"
    ...             )
    ...         )
    ...     )
    >>> print (formatted_repr (e_types))
    ( ( <class '_GTW._RST.Resource.Dir'>
      , ()
      , { 'description' : 'Legal person'
        , 'entries' :
            ( ( <class '_GTW._RST.Resource.Leaf'>
              , ()
              , { 'implicit' : True
                , 'name' : '1'
                }
              )
            ,
            )
        , 'name' : 'PAP-Company'
        }
      )
    , ( <class '_GTW._RST.Resource.Dir'>
      , ()
      , { 'description' : 'Natural person'
        , 'name' : 'PAP-Person'
        }
      )
    )
    >>> root
    <Root : />
    >>> root.entries
    [<Leaf about: /about>, <Dir v1: /v1>, <Dir v2: /v2>]

    >>> ets = tuple (root.entries_transitive)
    >>> ets
    (<Leaf about: /about>, <Dir v1: /v1>, <Dir Meta: /v1/Meta>, <Dir PAP-Company: /v1/PAP-Company>, <Leaf 1: /v1/PAP-Company/1>, <Dir PAP-Person: /v1/PAP-Person>, <Dir v2: /v2>)

    >>> print (portable_repr ([e.name for e in ets]))
    ['about', 'v1', 'Meta', 'PAP-Company', '1', 'PAP-Person', 'v2']
    >>> print (portable_repr ([e.href for e in ets]))
    ['about', 'v1', 'v1/Meta', 'v1/PAP-Company', 'v1/PAP-Company/1', 'v1/PAP-Person', 'v2']

    >>> print (root.href_pat_frag)
    v2|v1(?:/(?:PAP\-Person|PAP\-Company|Meta))?

    >>> for e in ets :
    ...     print (e.href, e.href_pat_frag)
    about None
    v1 v1(?:/(?:PAP\-Person|PAP\-Company|Meta))?
    v1/Meta Meta
    v1/PAP-Company PAP\-Company
    v1/PAP-Company/1 None
    v1/PAP-Person PAP\-Person
    v2 v2

    >>> root.entries [1]
    <Dir v1: /v1>

    >>> root.entries [1].entries
    [<Dir Meta: /v1/Meta>, <Dir PAP-Company: /v1/PAP-Company>, <Dir PAP-Person: /v1/PAP-Person>]

    >>> c = root.resource_from_href("/v1/PAP-Company")
    >>> c
    <Dir PAP-Company: /v1/PAP-Company>
    >>> sorted (c.SUPPORTED_METHODS)
    ['GET', 'HEAD', 'OPTIONS']

    >>> show (root)
    <Root : /> parent = -, top = /
      <Leaf about: /about> parent = /, top = /
      <Dir v1: /v1> parent = /, top = /
        <Dir Meta: /v1/Meta> parent = /v1, top = /
        <Dir PAP-Company: /v1/PAP-Company> parent = /v1, top = /
          <Leaf 1: /v1/PAP-Company/1> parent = /v1/PAP-Company, top = /
        <Dir PAP-Person: /v1/PAP-Person> parent = /v1, top = /
      <Dir v2: /v2> parent = /, top = /

    >>> print (portable_repr (root.GET.render_man.by_extension))
    mm_list(<class 'builtins.list'>, {'json' : [<class '_GTW._RST.Mime_Type.JSON'>]})
    >>> print (portable_repr (root.GET.render_man.by_mime_type))
    mm_list(<class 'builtins.list'>, {'application/json' : [<class '_GTW._RST.Mime_Type.JSON'>]})

    >>> print (portable_repr (GTW.RST.Mime_Type.JSON))
    <class '_GTW._RST.Mime_Type.JSON'>
    >>> print (portable_repr (GTW.RST.Mime_Type.JSON.extensions))
    ('json',)
    >>> print (portable_repr (GTW.RST.Mime_Type.JSON.mime_types))
    ('application/json',)

    >>> for n, r in sorted (pyk.iteritems (GTW.RST.Mime_Type.JSON.Table)) :
    ...     print (portable_repr ((r.name, r.extensions, r.mime_types)))
    ('ATOM', ('atom',), ('application/atom+xml',))
    ('CSV', ('csv',), ('text/csv',))
    ('HTML', ('html', 'htm'), ('text/html',))
    ('HTML_T', ('html', 'htm'), ('text/html',))
    ('JSON', ('json',), ('application/json',))
    ('SVG', ('svg',), ('image/svg+xml',))
    ('TXT', ('txt',), ('text/plain',))
    ('User_Cert', ('user_cert',), ('application/x-x509-user-cert',))
    ('XHTML', ('xhtml',), ('application/xhtml+xml',))
    ('XML', ('xml',), ('text/xml', 'application/xml'))


    >>> root2 = Root ( HTTP = None
    ...     , language          = "en"
    ...     , entries           =
    ...         ( Leaf
    ...             ( name          = "about"
    ...             , implicit      = True
    ...             )
    ...         , Dir
    ...             ( name          = "v1"
    ...             , description   = "Version 1 of test RESTful api"
    ...             , entries       =
    ...                 ( Dir
    ...                     ( name          = "Meta"
    ...                     , description   = "Meta information about RESTful api"
    ...                     )
    ...                 ,
    ...                 ) + e_types
    ...             )
    ...         , Dir
    ...             ( name          = "v2"
    ...             , entries       = list (e_types)
    ...             )
    ...         )
    ...     )
    >>> ets2 = tuple (root2.entries_transitive)
    >>> ets2
    (<Leaf about: /about>, <Dir v1: /v1>, <Dir Meta: /v1/Meta>, <Dir PAP-Company: /v1/PAP-Company>, <Leaf 1: /v1/PAP-Company/1>, <Dir PAP-Person: /v1/PAP-Person>, <Dir v2: /v2>, <Dir PAP-Company: /v2/PAP-Company>, <Leaf 1: /v2/PAP-Company/1>, <Dir PAP-Person: /v2/PAP-Person>)

    >>> print (portable_repr ([e.name for e in ets2]))
    ['about', 'v1', 'Meta', 'PAP-Company', '1', 'PAP-Person', 'v2', 'PAP-Company', '1', 'PAP-Person']
    >>> print (portable_repr ([e.href for e in ets2]))
    ['about', 'v1', 'v1/Meta', 'v1/PAP-Company', 'v1/PAP-Company/1', 'v1/PAP-Person', 'v2', 'v2/PAP-Company', 'v2/PAP-Company/1', 'v2/PAP-Person']

    >>> print (root2.href_pat_frag)
    v2(?:/(?:PAP\-Person|PAP\-Company))?|v1(?:/(?:PAP\-Person|PAP\-Company|Meta))?

    >>> for e in ets2 :
    ...     r = root2.resource_from_href (e.href)
    ...     if r is None :
    ...         print ("No resource_from_href for", e.href, e)

"""

interactive_code = """

from _GTW._RST.Resource import *

e_types = \
    ( Dir
        ( name          = "PAP-Company"
        , description   = "Legal person"
        )
    , Dir
        ( name          = "PAP-Person"
        , description   = "Natural person"
        )
    ,
    )
root2 = Root ( HTTP = None
    , language          = "en"
    , entries           =
        ( Leaf
            ( name          = "about"
            , implicit      = True
            )
        , Dir
            ( name          = "v1"
            , description   = "Version 1 of test RESTful api"
            , entries       =
                ( Dir
                    ( name          = "Meta"
                    , description   = "Meta information about RESTful api"
                    )
                ,
                ) + e_types
            )
        , Dir
            ( name          = "v2"
            , entries       = list (e_types)
            )
        )
    )

"""

### __END__ GTW.RST.__test__
