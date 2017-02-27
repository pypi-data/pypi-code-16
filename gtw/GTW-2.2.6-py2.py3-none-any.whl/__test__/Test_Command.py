# -*- coding: utf-8 -*-
# Copyright (C) 2012-2017 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.__test__.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.__test__.Test_Command
#
# Purpose
#    Test-specific descendent of GTW.Werkzeug.Command
#
# Revision Dates
#    18-Sep-2012 (CT) Creation (factored from _GTW/__test__/model.py)
#    18-Sep-2012 (CT) Redefine `__init__` to set `ANS.Version`
#    25-Sep-2012 (CT) Add `smtp_server` default `<Tester>`
#     9-Jan-2013 (CT) Factor in `GTW_RST_Test_Command` from `RST`
#    21-Jan-2013 (CT) Add `reset`
#    31-Jan-2013 (CT) Add `bn` to `_backend_spec`
#    27-Mar-2013 (CT) Add `test_request`, reorder methods alphabetically
#    28-Mar-2013 (CT) Add and call `reset_callbacks`
#     3-May-2013 (CT) Rename `login_required` to `auth_required`
#     3-May-2013 (CT) Add `GTW_RST_Test_Command.v1_auth_required`
#    13-May-2013 (CT) Fix `RAT` handling in `create_rst`
#    26-May-2013 (CT) Import `pyk`
#     3-Jun-2013 (CT) Commit and compact `scope` in `do_create`
#    27-Jun-2013 (CT) Add `SAW`-based backends
#    25-Sep-2013 (CT) Add `debug`
#    26-Sep-2013 (CT) Add `_backend_reset`
#    27-Aug-2014 (CT) Remove import of `_GTW._AFS._MOM.Spec`
#     7-Oct-2015 (CT) Encapsulate `pyquery` in `_PQ_`, placate its insane 2/3 difference
#    21-Oct-2015 (CT) Use `pyk.as_str`, not home-grown code
#     1-Jun-2016 (CT) Add `fake_request`
#     3-Jun-2016 (CT) Add `esf_completer`, `show_esf_form`
#    24-Feb-2017 (CT) Import `MOM.Inspect`, not `MOM.inspect`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division
from   __future__  import print_function, unicode_literals

from   _GTW                     import GTW
from   _JNJ                     import JNJ
from   _MOM                     import MOM
from   _TFL                     import TFL

from   _MOM.import_MOM          import *
from   _MOM.Inspect             import show_ref_map, show_ref_maps
from   _MOM.Product_Version     import Product_Version, IV_Number

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL._Meta.Property      import Class_Property
from   _TFL.formatted_repr      import formatted_repr as formatted
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.portable_repr       import portable_repr
from   _TFL.pyk                 import pyk
from   _TFL.Record              import Record
from   _TFL.Sorted_By           import Sorted_By
from   _TFL                     import sos

import _GTW.Request_Data
import _GTW._Werkzeug.Command
import _GTW._RST._TOP.import_TOP
import _GTW._RST._TOP._MOM.import_MOM

import _JNJ.Templateer

import _TFL.Filename
import _TFL.Generators

from    werkzeug.test     import Client, EnvironBuilder
from    werkzeug.wrappers import BaseResponse

def esf_completer (scope, AQ, trigger, value, qdct = {}) :
    ESW    = AQ.ESW
    values = dict (qdct)
    values.update ({ trigger : value })
    return ESW.completer (scope, trigger, values)
# end def esf_completer

def fake_request (** kw) :
    return Record \
        ( req_data      = GTW.Request_Data      (kw)
        , req_data_list = GTW.Request_Data_List (kw)
        )
# end def fake_request

def prepr (* args) :
    print (* (portable_repr (a) for a in args))
# end def prepr

def show_esf_form (nav_root, etn, attr_name) :
    adm = nav_root.ET_Map [etn].admin
    aq  = getattr (adm.E_Type.AQ, attr_name)
    ETT = adm.Templateer.get_template ("e_type_selector")
    print (ETT.call_macro ("form", adm, aq, aq.ESW))
# end def show_esf_form

model_src        = sos.path.dirname (__file__)

Version = Product_Version \
    ( productid           = u"MOM/GTW Test Cases"
    , productnick         = u"MOM-Test"
    , productdesc         = u"Test application for the regressiontest"
    , date                = "21-Apr-2010 "
    , major               = 0
    , minor               = 1
    , patchlevel          = 2
    , author              = u"Martin Glueck/Christian Tanzer"
    , copyright_start     = 2010
    , db_version          = IV_Number
        ( "db_version"
        , ("MOMT", )
        , ("MOMT", )
        , program_version = 1
        , comp_min        = 0
        , db_extension    = ".momt"
        )
    )

def debug (** kw) :
    from _TFL.Record import Record
    X = Record (** kw)
    import pdb; pdb.set_trace ()
# end def debug

class Test_Response (BaseResponse) :
    """Enhance the reponse for the test setup"""

    class _PQ_ (TFL.Meta.Object) :

        def __init__ (self, data) :
            self._pq = self.PyQuery (pyk.as_str (data))
        # end def __init__

        def __call__ (self, filter) :
            return self._pq (pyk.as_str (filter))
        # end def __call__

        @Once_Property
        def PyQuery (self) :
            import lxml.html
            def _as_string (self) :
                return pyk.decoded (lxml.html.tostring (self))
            lxml.html.HtmlElement.string = Once_Property (_as_string)
            import pyquery
            return pyquery.PyQuery
        # end def PyQuery

    # end class _PQ_

    @Once_Property
    def PQ (self) :
        return self._PQ_ (self.data)
    # end def PQ

# end class Test_Response

_Ancestor = GTW.Werkzeug.Command

class GTW_Test_Command (_Ancestor) :

    ANS                   = GTW
    nick                  = u"MOMT"
    default_db_name       = "test"
    reset_callbacks       = []

    SALT                  = b"4418c024-c51f-42b5-9032-be3ef10b1a61"

    _defaults             = dict \
        ( config          = "~/.gtw-test.config"
        , smtp_server     = "<Tester>"
        )

    Backend_Parameters    = dict \
        ( HPS             = "'hps://'"
        , SQL             = "'sqlite://'"
        , POS             = "'postgresql://regtest:regtest@localhost/regtest'"
        , MYS             = "'mysql://:@localhost/test'"
        , MYST            = "'mysql://:@localhost/test?unix_socket=/var/run/mysqld/mysqld-ram.sock'"
        , my              = "'mysql://:@localhost/test'"
        , pg              = "'postgresql://regtest:regtest@localhost/regtest'"
        , sq              = "'sqlite://'"
        )
    Backend_Default_Path  = dict \
        ( (k, None) for k in Backend_Parameters)

    class _Create_ (_Ancestor._Create_) :

        _opts             = \
            ( "fixtures:B?Run the fixtures after the scope has been created"
            ,
            )

    # end class _Create_

    class _WSGI_ (_Ancestor._WSGI_) :

        _opts             = \
            ( "create:B=Create a new scope during WSGI application creation"
            , "fixtures:B?Run the fixtures after the scope has been created"
            )

    # end class _WSGI_

    @Once_Property
    def src_dir (self) :
        return "/tmp/test"
    # end def src_dir

    @Once_Property
    def Test_Client (self) :
        return Client (self.root, Test_Response)
    # end def Test_Client

    @Once_Property
    def web_src_root (self) :
        return "/tmp/test"
    # end def web_src_root

    def __init__ (self, * args, ** kw) :
        self.ANS.Version = Version
        self.__super.__init__ (* args, ** kw)
    # end def __init__

    def combiner (self, backends, bpt) :
        if bpt > 1 :
            backends = backends + [backends [0]]
        return TFL.window_wise (backends, bpt)
    # end def combiner

    def create_top (self, cmd, ** kw) :
        RST            = GTW.RST
        TOP            = RST.TOP
        result         = TOP.Root \
            ( language = "de"
            , ** kw
            )
        result.add_entries \
            ( TOP.MOM.Admin.Site
                ( name            = "Admin"
                , short_title     = "Admin"
                , pid             = "Admin"
                , title           = u"Verwaltung der Homepage"
                , head_line       = u"Administration der Homepage"
                , auth_required   = True
                , entries         = self._nav_admin_groups ()
                )
            , TOP.Auth
                ( name            = _ ("Auth")
                , pid             = "Auth"
                , short_title     = _ ("Authorization and Account handling")
                , hidden          = True
                )
            , TOP.L10N
                ( name            = _ ("L10N")
                , short_title     =
                    _ ("Choice of language used for localization")
                , country_map     = dict (de = "AT")
                )
            )
        return result
    # end def create_top

    def create_test_dict \
            ( self, test_spec
            , backends = None
            , bpt      = 1
            , combiner = None
            , ignore   = set ()
            ) :
        result = {}
        if backends is None :
            backends = sos.environ.get ("GTW_test_backends", ("HPS:SQL"))
            if backends == "*" :
                backends = sorted (self.Backend_Parameters)
            else :
                backends = list (p.strip () for p in backends.split (":"))
        if combiner is None :
            combiner = self.combiner
        if isinstance (ignore, pyk.string_types) :
            ignore   = set ((ignore, ))
        elif not isinstance (ignore, set) :
            ignore   = set (ignore)
        if not isinstance (test_spec, dict) :
            test_spec = {"" : test_spec}
        for w in combiner ((b for b in backends if b not in ignore), bpt) :
            for name, code in pyk.iteritems (test_spec) :
                key  = "_".join (p for p in (name, ) + w if p)
                bsd  = dict (self._backend_spec (w))
                test = "%s\n\n    %s\n" % \
                    ( code % bsd
                    , "\n    ".join \
                        ( ( ">>> try :"
                          , "...     Scaffold.reset ()"
                          , "... except Exception :"
                          , "...     pass"
                          )
                        )
                    )
                result [key] = test
        return result
    # end def create_test_dict

    def do_create (self, cmd) :
        scope = self.scope (cmd.db_url, cmd.db_name, create = True)
        self.fixtures      (scope)
        scope.commit       ()
        scope.ems.compact  ()
        scope.destroy      ()
    # end def do_create

    def fixtures (self, scope) :
        pass
    # end def fixtures

    def reset (self) :
        self._backend_reset ()
        for cb in self.reset_callbacks :
            try :
                cb ()
            except Exception :
                pass
        self.root = None
        try :
            del self.Test_Client
        except AttributeError :
            pass
        MOM.Scope.destroy_all ()
        self.reset_callbacks = []
    # end def reset

    def scope (self, * args, ** kw) :
        verbose = kw.pop ("verbose", True)
        return self.__super.scope (* args, verbose = verbose, ** kw)
    # end def scope

    def test_get (self, url, ** options) :
        return self.Test_Client.get (url, ** options)
    # end def test_get

    def test_post (self, url, ** options) :
        return self.Test_Client.post (url, ** options)
    # end def test_post

    def test_request (self, * args, ** kw) :
        """Return a request object corresponding to `args` and `kw`. All
           arguments supported by `werkzeug.test.EnvironBuilder` plus
           `request_class` are allowed.
        """
        request_class = kw.pop ("request_class", self.root.Request)
        env_builder   = EnvironBuilder (* args, ** kw)
        return env_builder.get_request (request_class)
    # end def test_request

    def test_request_get (self, * args, ** kw) :
        kw ["method"] = "GET"
        return self.test_request (* args, ** kw)
    # end def test_request_get

    def test_request_post (self, * args, ** kw) :
        kw ["method"] = "POST"
        return self.test_request (* args, ** kw)
    # end def test_request_post

    def _backend_reset (self) :
        for apt in pyk.itervalues (MOM.App_Type.Table) :
            for apt_d in pyk.itervalues (apt.derived) :
                try :
                    SAW = apt_d._SAW
                except AttributeError :
                    pass
                else :
                    ### reset caches to avoid sequence dependencies between
                    ### different test cases
                    SAW.reset_cache ()
    # end def _backend_reset

    def _backend_spec (self, backends) :
        for i, b in enumerate (backends) :
            p  = self.Backend_Parameters   [b]
            n  = self.Backend_Default_Path [b]
            BN = repr (b)
            bn = BN.lower ()
            for k, v in (("p", p), ("n", n), ("BN", BN), ("bn", bn)) :
                yield ("%s%d" % (k, i + 1), v)
    # end def _backend_spec

    def _create_templateer (self, cmd, ** kw) :
        return self.__super._create_templateer \
            (cmd, load_path = [self.src_dir], ** kw)
    # end def _create_templateer

    def _nav_admin_groups (self) :
        return []
    # end def _nav_admin_groups

    def _wsgi_app (self, cmd) :
        self._handle_create (cmd)
        result = self.__super._wsgi_app (cmd)
        return result
    # end def _wsgi_app

# end class GTW_Test_Command

class GTW_RST_Test_Command (GTW_Test_Command) :

    _defaults               = dict \
        ( fixtures          = "yes"
        , port              = 9090
        , UTP               = "RST"
        )

    v1_auth_required        = False

    def create_rst (self, cmd, ** kw) :
        import _GTW._RST._MOM.Doc
        import _GTW._RST._MOM.Scope
        result = GTW.RST.Root \
            ( language          = "de"
            , entries           =
                [ GTW.RST.MOM.Scope
                    ( name          = "v1"
                    , auth_required = self.v1_auth_required
                    )
                , GTW.RST.MOM.Doc.App_Type (name = "Doc")
                , GTW.RST.Raiser           (name = "RAISE")
                ]
            , ** kw
            )
        if self.v1_auth_required :
            ### `secure` and `httponly` break the test --> clear `cookie_kw`
            import _GTW._RST.RAT
            GTW.RST.RAT.cookie_kw = {}
            result.add_entries (GTW.RST.RAT (name = "RAT"))
        if cmd.log_level :
            print (formatted (result.Table))
        return result
    # end def create_rst

# end class GTW_RST_Test_Command

### __END__ GTW.__test__.Test_Command
