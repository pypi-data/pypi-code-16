# -*- coding: utf-8 -*-
# Copyright (C) 2010-2017 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.Werkzeug.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.Werkzeug.Command
#
# Purpose
#    Provide an extendable Command for creating instances of MOM.App_Type
#    and MOM.Scope, managing their databases, and creating a WSGI application
#    or starting a development web server based on the werkzeug framework
#
# Revision Dates
#    27-Jan-2012 (CT) Recreation (re-factored from SC-AMS specific code)
#    27-Jan-2012 (CT) Factor `_wsgi_app`
#    30-Jan-2012 (CT) Change `_wsgi_app` to `cao.GET ("cookie_salt")`
#     1-Feb-2012 (CT) Use newly factored `GTW.AFS.MOM.Form_Cache`
#    30-Apr-2012 (MG) Allow none existing `Auth`
#     3-May-2012 (CT) Pass `languages` to `HTTP.Application`
#     4-May-2012 (CT) Use `nav.login_url` instead of home-grown code
#    15-May-2012 (CT) Implement sub-command `setup_cache`, factor `cache_path`
#    17-May-2012 (CT) Derive from `GTW.OMP.Command` instead of `.Scaffold`,
#                     rename from `Scaffold` to `Command`
#    22-May-2012 (CT) Remove unused imports
#    22-May-2012 (CT) Use `app_dir`, not `app_path`
#     1-Jun-2012 (CT) Add sub-command `fcgi`
#     2-Jun-2012 (CT) Rename `suppress_translation_loading` to `load_I18N`
#     4-Jun-2012 (CT) Add `-log_level`, pass to `HTTP.Application`
#     4-Jun-2012 (MG) `_handle_run_server` support for `host` added
#    20-Jun-2012 (CT) Use `cao.UTP` instead of hard-coded `GTW.NAV`
#    21-Jun-2012 (CT) Factor `_load_I18N`, `_static_handler`
#    22-Jun-2012 (CT) Remove dependency on `HTTP.Application`,
#                     use `Static_File_App`, not `Static_File_Handler`
#    28-Jun-2012 (CT) Factor `App_Cache`, `_get_root`
#     9-Jul-2012 (CT) Pass `static_handler` to `_get_root`
#    17-Jul-2012 (MG) Change `_wsgi_app` to `Break` after `init_app_cache`
#    20-Jul-2012 (CT) Change `nav_admin_group` to use `GTW.RST`, not `GTW.NAV`
#    26-Jul-2012 (CT) Redefine `-UTP` as `Opt.Key` for `RST_App`, `TOP_App`
#    29-Jul-2012 (MG) Add and use `external_media_path`
#    30-Jul-2012 (CT) Move defaults to `_defaults`, merge `external_media_path`
#    30-Jul-2012 (CT) Add option `-port` (was in GTW.OMP.Command)
#     2-Aug-2012 (MG) Close database connections before starting the server
#     2-Aug-2012 (CT) Change `_wsgi_app` to avoid loading of `scope`
#     2-Aug-2012 (MG) Correct implementation of `watch_media_files`
#     5-Aug-2012 (MG) Change handling of `watch_media_files`
#     6-Aug-2012 (CT) Move `-watch_media_files` to `_GT2W_Server_Base_`
#    10-Aug-2012 (CT) Pass `verbose` to `root.Cacher` and `App_Cache`
#    14-Aug-2012 (MG) Add option `media_domain`
#    19-Aug-2012 (MG) Commit scope after cache init
#    25-Aug-2012 (CT) Import `_MOM.inspect` if `cao.debug`
#     6-Sep-2012 (CT) Pass `verbose` to `GTW.AFS.MOM.Form_Cache`
#     6-Sep-2012 (CT) Add and use `_create_cache_p`
#    13-Sep-2012 (CT) Redefine `app_type` to call
#                     `GTW.AFS.MOM.Spec.setup_defaults`, if the module is loaded
#    25-Sep-2012 (CT) Add `_get_smtp` to honor `<Tester>` and `<Logger>`
#    25-Sep-2012 (CT) Pass `cao.log_level` to `I18N.load`
#     8-Jan-2013 (CT) Add `-cert_auth_path`
#    15-Jan-2013 (CT) Add `-cc_domain`
#     3-Dec-2013 (CT) Change `_load_I18N` to log warnings about exceptions
#    10-Dec-2013 (CT) Add `-s_domain`
#    11-Dec-2013 (CT) Add `-Setup_Cache` to `_GT2W_Server_Base_._opts`,
#                     remove `DEBUG` from `init_app_cache`
#    11-Dec-2013 (CT) Add `-CSRF_check`
#     7-Apr-2014 (CT) Add `-ACAO`
#     2-May-2014 (CT) Add option `webmaster`
#     9-Jul-2014 (CT) Add `_template_prefixes`
#    20-Aug-2014 (CT) Remove `_GTW._AFS._MOM.Form_Cache`
#    21-Aug-2014 (CT) Reify `after_app_type` as method of `RST_App`, `TOP_App`
#     7-May-2015 (CT) Add support for `journal_dir`
#    14-Jun-2015 (CT) Add `-force_HSTS` to enable Strict Transport Security
#    16-Jun-2015 (CT) Change default of `webmaster`
#                     (`@gmail.com` was a bad choice)
#    29-Jun-2015 (CT) Add `preload` to `Strict Transport Security` header
#    12-Oct-2015 (CT) Use `logging.exception`, not `logging.warning`
#                     in `_load_I18N`
#    18-Nov-2015 (CT) Add sub-command `generate_static_pages`
#    26-Nov-2015 (CT) Add `robots` to sub-command `generate_static_pages`
#     1-Dec-2015 (CT) Add guard for `scope` to `init_app_cache`
#     1-Dec-2015 (CT) Add `.lstrip ("/")` to `_handle_generate_static_pages`
#    12-May-2016 (CT) Guard `asp is not None` in `_handle_generate_static_pages`
#    15-Jun-2016 (CT) Rename handler argument `cmd` to `cao`
#    11-Oct-2016 (CT) Use `CHJ.Media`, not `GTW.Media`
#    17-Jan-2017 (CT) Add `css_nav_side`, `css_nav_type`
#    24-Feb-2017 (CT) Import `MOM.Inspect`, not `MOM.inspect`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _TFL                     import TFL
from   _GTW                     import GTW

import _GTW.File_Session
import _GTW._OMP.Command
import _GTW._Werkzeug.App_Cache
import _GTW._Werkzeug.Static_File_App
import _CHJ.Media

import _JNJ.Templateer

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.pyk                 import pyk
from   _TFL                     import sos

import _TFL.SMTP

import logging

pjoin = sos.path.join

class RST_App (TFL.Meta.Object) :

    cache_prefix   = "rst_"
    use_templateer = False

    def after_app_type (self, command, app_type) :
        pass
    # end def after_app_type

    def cachers (self, command, cao) :
        return []
    # end def cachers

    def create (self, command, cao, * args, ** kw) :
        return command.create_rst (cao, * args, ** kw)
    # end def create

    def do_import (self) :
        import _GTW._RST.import_RST
    # end def do_import

    def __repr__ (self) :
        self.do_import ()
        return repr (GTW.RST)
    # end def __repr__

# end class RST_App

class TOP_App (TFL.Meta.Object) :

    cache_prefix   = ""
    use_templateer = True

    def after_app_type (self, command, app_type) :
        pass
    # end def after_app_type

    def cachers (self, command, cao) :
        return []
    # end def cachers

    def create (self, command, cao, * args, ** kw) :
        return command.create_top (cao, * args, ** kw)
    # end def create

    def do_import (self) :
        import _GTW._RST._TOP._MOM.import_MOM
    # end def do_import

    def __repr__ (self) :
        self.do_import ()
        return repr (GTW.RST.TOP)
    # end def __repr__

# end class TOP_App

class _GT2W_Sub_Command_ (GTW.OMP._Sub_Command_) :

    _rn_prefix              = "_GT2W"

_Sub_Command_ = _GT2W_Sub_Command_ # end class

class GT2W_Command (GTW.OMP.Command) :

    _rn_prefix              = "GT2W"

    SALT                    = \
        b"Needs to defined uniquely for each application"

    base_template_dir       = sos.path.dirname (_JNJ.__file__)
    root                    = None

    _after_app_type         = None
    _create_cache_p         = False
    _defaults               = dict \
        ( CSRF_check        = "yes"
        , host              = "localhost"
        , load_I18N         = "yes"
        , log_level         = 1
        , port              = 8090
        )

    _template_prefixes      = {}

    ### Sub-commands defined as class attributes to allow redefinition by
    ### derived classes; meta class puts their names into `_sub_commands`
    class _GT2W_Server_Base_ (_Sub_Command_, GTW.OMP.Command._Server_Base_) :
        ### Base for server-related commands

        is_partial              = True
        _opts                   = \
            ( "-ACAO:S?Add option value as Access-Control-Allow-Origin header"
            , "-cc_domain:S"
                "?Domain used for authorization with client certificates"
            , "-cert_auth_path:P"
                "?Path of certification authority .crt and .key files"
            , "-CSRF_check:B?Perform checks to protect against CSRF"
            , "-css_nav_side:S"
                "?Side where navigation is displayed. "
                "Values: 'left', 'right', 'bottom'."
            , "-css_nav_type:S"
                "?Navigation type of CSS style. "
                "Values: 'header', 'long', 'short'."
            , "-external_media_path:P"
                "?Path where the /media/X url should be bound to"
            , "-force_HSTS:B?Include HSTS header"
            , "-host:S?Host name or IP-Address the server should be bound to"
            , "-max_age_HSTS:I=31557600"
                "?The time, in seconds, that the browser should remember "
                "that this site is only to be accessed using HTTPS "
                "(default: one year [86400 * 365.25 seconds])"
            , "-load_I18N:B"
                "?Load the translation files during startup"
            , "-log_level:I?Verbosity of logging"
            , "-port:I?Port the server should use"
            , "-Setup_Cache:B?Setup the cache of the application"
            , "-s_domain:S?Domain configured for HTTPS"
            , "-watch_media_files:B"
                "?Add the .media files to list files watched by "
                "automatic reloader"
            , "-webmaster:S=tanzer@swing.co.at"
            , TFL.CAO.Opt.Key
                ( name        = "UTP"
                , dct         = dict
                    ( RST     = RST_App ()
                    , TOP     = TOP_App ()
                    )
                , default     = "TOP"
                , description = "Select Url Tree Package to use."
                )
            )

    # end class _GT2W_Server_Base_

    class _GT2W_Run_Server_ (_GT2W_Server_Base_, GTW.OMP.Command._Run_Server_) :

        pass

    _Run_Server_ = _GT2W_Run_Server_ # end class

    class _GT2W_FCGI_ (_GT2W_Server_Base_, GTW.OMP.Command._FCGI_) :
        pass
    _FCGI_ = _GT2W_FCGI_ # end class

    class _GT2W_Generate_Static_Pages_ (_GT2W_Server_Base_) :
        """Generate HTML files for static pages."""

        _defaults               = dict \
            ( Setup_Cache       = True
            , static_root       = "../static"
            )
        _args                   = \
            ( "url:S"
                "?Url(s) of resources for which static pages are "
                "generated (default: /)"
            ,
            )
        _opts                   = \
            ( "-dynamic_nav:B?Include dynamic links in nav-bar of static pages"
            ,
            )

        class Static_Root (TFL.Command.Rel_Path_Option) :
            """Root path of static HTML files"""

            auto_split              = None
            max_number              = 1
            single_match            = True
            skip_missing            = False

        # end class Static_Root

    _Generate_Static_Pages_ = _GT2W_Generate_Static_Pages_ # end class

    class _GT2W_Setup_Cache_ (_GT2W_Server_Base_, GTW.OMP.Command._Setup_Cache_) :

        _defaults               = dict \
            ( Setup_Cache       = True
            )

    _Setup_Cache_ = _GT2W_Setup_Cache_ # end class

    class _GT2W_Shell_ (_GT2W_Server_Base_, GTW.OMP.Command._Shell_) :
        pass
    _Shell_ = _GT2W_Shell_ # end class

    class _GT2W_WSGI_ (_GT2W_Server_Base_, GTW.OMP.Command._WSGI_) :
        pass
    _WSGI_ = _GT2W_WSGI_ # end class

    def app_type (self, * ems_dbw) :
        result = self.__super.app_type (* ems_dbw)
        _after_app_type = self._after_app_type
        if _after_app_type is not None :
            _after_app_type (self, result)
        return result
    # end def app_type

    def cache_path (self, UTP) :
        return pjoin (self.src_dir, UTP.cache_prefix + "app_cache.pck")
    # end def cache_path

    def fixtures (self, scope) :
        pass
    # end def fixtures

    def init_app_cache (self) :
        def load_cache () :
            try :
                self.cacher.load ()
            except IOError :
                pass
        if self._create_cache_p :
            try :
                self.cacher.store ()
            except EnvironmentError as exc :
                load_cache ()
        else :
            load_cache ()
        try :
            scope = self.root.scope
        except AttributeError :
            pass
        else :
            if scope is not None :
                scope.commit ()
    # end def init_app_cache

    def nav_admin_group (self, name, title, * pnss, ** kw) :
        return GTW.RST.TOP.MOM.Admin.Group \
            ( name           = name
            , short_title    = kw.pop ("short_title", name)
            , title          = title
            , head_line      = kw.pop ("head_line", title)
            , PNSs           = pnss
            , ** kw
            )
    # end def nav_admin_group

    def _create_scope (self, apt, url, verbose = False, journal_dir = None) :
        result = self.__super._create_scope (apt, url, verbose, journal_dir)
        self.fixtures (result)
        return result
    # end def _create_scope

    def _create_templateer \
            (self, cao, trim_blocks = True, version = "html/5.jnj", ** kw) :
        if cao.UTP.use_templateer :
            from   _JNJ import JNJ
            import _JNJ.Templateer
            from   _JNJ.Media_Defaults import Media_Defaults
            globs = kw.pop ("globals", {})
            media = kw.get ("Media_Parameters", None)
            if media is None :
                kw ["Media_Parameters"] = Media_Defaults ()
            result = JNJ.Templateer \
                ( encoding    = cao.input_encoding
                , globals     = dict (site_base = cao.template_file, ** globs)
                , i18n        = cao.load_I18N
                , prefixes    = self._template_prefixes
                , trim_blocks = trim_blocks
                , version     = version
                , ** kw
                )
            return result
    # end def _create_templateer

    def _get_root (self, cao, apt, url, ** kw) :
        result = self.root
        if result is None :
            cookie_salt = cao.GET ("cookie_salt", self.SALT)
            if cao.css_nav_side :
                kw.update (css_nav_side = cao.css_nav_side)
            if cao.css_nav_type :
                kw.update (css_nav_type = cao.css_nav_type)
            if cookie_salt == Command.SALT :
                warnings.warn \
                    ( "Cookie salt should be specified for every application! "
                      "Using default `cookie_salt`!"
                    , UserWarning
                    )
            UTP = cao.UTP
            UTP.do_import ()
            cachers       = UTP.cachers (self, cao)
            journal_dir   = cao.keep_journal and cao.journal_dir
            result        = self.root = UTP.create \
                ( self, cao
                , ACAO                = cao.ACAO
                , App_Command         = self
                , App_Type            = apt
                , Create_Scope        = lambda apt, url :
                    self._load_scope (apt, url, journal_dir)
                , DB_Url              = url
                , DEBUG               = cao.debug
                , HTTP                = cao.HTTP
                , Session_Class       = GTW.File_Session
                , Templateer          = self._create_templateer (cao)
                , TEST                = cao.TEST
                , cc_domain           = cao.cc_domain
                , cert_auth_path      = cao.cert_auth_path
                , cookie_salt         = cookie_salt
                , copyright_start     = cao.copyright_start
                , csrf_check_p        = cao.CSRF_check
                , default_locale_code = cao.locale_code
                , edit_session_ttl    = cao.edit_session_ttl.date_time_delta
                , email_from          = cao.email_from or None
                , encoding            = cao.output_encoding
                , i18n                = cao.load_I18N
                , input_encoding      = cao.input_encoding
                , languages           = set (cao.languages)
                , log_level           = cao.log_level
                , page_template_name  = cao.template_file
                , s_domain            = cao.s_domain
                , session_id          = b"SESSION_ID"
                , smtp                = self._get_smtp (cao)
                , use_www_debugger    = cao.debug
                , user_session_ttl    = cao.user_session_ttl.date_time_delta
                , ** kw
                )
            if result.Cacher :
                mc_fix = "media/v"
                mc_dir = pjoin (self.web_src_root, mc_fix)
                cachers.append \
                    ( result.Cacher
                        ( mc_dir, mc_fix
                        , cache_filenames = cao.watch_media_files
                        , verbose         = cao.verbose
                        )
                    )
                self._tmc_filenames = cachers [-1].tmc.filenames
            self.cacher = GTW.Werkzeug.App_Cache \
                ( self.cache_path (UTP)
                , * cachers
                , root    = result
                , DEBUG   = result.DEBUG
                , verbose = cao.verbose
                )
        return result
    # end def _get_root

    def _get_smtp (self, cao) :
        name   = cao.smtp_server
        result = None
        if name == "<Tester>" :
            result = TFL.SMTP_Tester ()
        elif name == "<Logger>" :
            result = TFL.SMTP_Logger ()
        elif name :
            result = TFL.SMTP (name)
        return result
    # end def _get_smtp

    def _handle_generate_static_pages (self, cao) :
        app  = self._wsgi_app \
            (cao, dynamic_p = False, dynamic_nav_p = cao.dynamic_nav)
        root = cao.static_root
        urls = cao.argv
        if not urls :
            urls = ["/"]
            if sos.path.isdir (root) :
                sos.rmdir (root, deletefiles = True)
        robots = app.resource_from_href ("robots")
        if robots is not None :
            robots.hidden = robots.static_p
        def _generate (cao, p, root, tail = None) :
            name = pjoin (root, tail or p.href_static.lstrip ("/"))
            dir  = sos.path.dirname (name)
            if not sos.path.exists (dir) :
                sos.mkdir_p  (dir)
            if cao.verbose :
                print (name, "...", end = " ")
            asp = p.as_static_page ()
            if asp is not None :
                with open (name, "wb") as f :
                    f.write (pyk.encoded (asp))
            if cao.verbose :
                print ("done")
        for url in urls :
            resource = app.resource_from_href (url)
            if resource.static_p and not resource.auth_required :
                _generate (cao, resource, root)
            for p in resource.static_pages :
                _generate (cao, p, root)
        if not cao.argv :
            for r, url in sorted (pyk.iteritems (app.redirects)) :
                p = app.resource_from_href (url)
                if p.static_p and not p.auth_required :
                    _generate (cao, p, root, r + p.static_page_suffix)
    # end def _handle_generate_static_pages

    def _handle_run_server (self, cao) :
        import werkzeug.serving
        app = self._wsgi_app (cao)
        kw  = dict \
            ( application  = app
            , hostname     = cao.host
            , port         = cao.port
            , use_debugger = cao.debug
            , use_reloader = cao.auto_reload
            )
        kw ["extra_files"] = self._tmc_filenames
        werkzeug.serving.run_simple (** kw)
    # end def _handle_run_server

    def _handle_setup_cache (self, cao) :
        self._create_cache_p = True
        self._wsgi_app    (cao)
    # end def _handle_setup_cache

    def _handle_wsgi (self, cao) :
        return self._wsgi_app (cao)
    # end def _handle_wsgi

    def _load_I18N (self, cao) :
        result = None
        if cao.load_I18N :
            try :
                result = TFL.I18N.load \
                    ( * cao.languages
                    , domains    = ("messages", )
                    , use        = cao.locale_code or "en"
                    , locale_dir = pjoin (self.app_dir, "locale")
                    , log_level  = cao.log_level
                    )
            except Exception as exc :
                logging.exception ("Exception during I18N.load: %r" % (exc, ))
        return result
    # end def _load_I18N

    def _static_file_app (self, cao) :
        prefix  = "media"
        dir_map = []
        if cao.external_media_path :
            dir_map.append \
                ( ("X",   sos.path.abspath (cao.external_media_path)))
        dir_map.extend \
            ( (   ("GTW", pjoin (self.lib_dir,      "_GTW", prefix))
              ,   ("",    pjoin (self.web_src_root,         prefix))
              )
            )
        return GTW.Werkzeug.Static_File_App (dir_map, prefix = prefix)
    # end def _static_file_app

    def _wsgi_app (self, cao, ** kw) :
        if cao.media_domain :
            CHJ.Media_Base.Domain = cao.media_domain
        self._create_cache_p = self._create_cache_p or cao.Setup_Cache
        self._after_app_type = cao.UTP.after_app_type
        apt, url = self.app_type_and_url (cao.db_url, cao.db_name)
        self._load_I18N (cao)
        sf_app = self._static_file_app (cao)
        result = root = self._get_root \
            (cao, apt, url, static_handler = sf_app, ** kw)
        if cao.force_HSTS :
            GTW.RST.Response._auto_headers.update \
                ( { "Strict-Transport-Security"
                  : "max-age=%d; includeSubDomains;preload;" % cao.max_age_HSTS
                  }
                )
        if cao.serve_static_files :
            sf_app.wrap = root
            result      = sf_app
        if root.Templateer is not None :
            root.Templateer.env.static_handler = sf_app
        self.init_app_cache ()
        scope = root.__dict__.get ("scope")
        if scope is not None :
            scope.close_connections ()
        if cao.debug :
            import _MOM.Inspect
        if cao.Break :
            TFL.Environment.py_shell (vars ())
        return result
    # end def _wsgi_app

Command = GT2W_Command # end class

if __name__ != "__main__" :
    GTW.Werkzeug._Export ("*")
### __END__ GTW.Werkzeug.Command
