# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Mag. Christian Tanzer All rights reserved
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
#    GTW.Werkzeug.deploy
#
# Purpose
#    Provide an extendable Command for the deployment of applications based
#    on GTW.Werkzeug
#
# Revision Dates
#    23-May-2012 (CT) Creation
#    24-May-2012 (CT) Add sub-command `setup_cache`
#     1-Jun-2012 (CT) Factor `_app_call` from `setup_cache`
#     1-Jun-2012 (CT) Add sub-command `fcgi`
#     1-Jun-2012 (CT) Add `py_options` to `_FCGI_._defaults`
#     1-Jun-2012 (CT) Derive from `GTW.OMP.deploy`, not `GTW.deploy`
#     1-Jun-2012 (CT) Add sub-command `ubycms`
#     3-Jun-2012 (CT) Add sub-command `fcgi_script`
#     3-Jun-2012 (CT) Use `self.lib_dir`, not `P.lib_dir`, in
#                     `_handle_fcgi_script`
#     5-Jun-2012 (CT) Add `exec` to output of `_handle_fcgi_script`
#    12-Dec-2013 (CT) Add `-script_path`, execute `chmod +x` on `fcgi_script`
#    16-Dec-2013 (CT) Add sub-command `create_config`,
#                     factor `_create_fcgi_script`
#    17-Dec-2013 (CT) Remove `lstrip_blocks` to allow jinja 2.6
#    17-Dec-2013 (CT) Add `verbose` to `_handle_create_config`
#    18-Dec-2013 (CT) Add `ca_path`, `ca_key_name` to `_handle_create_config`
#    20-Dec-2013 (CT) Split `addr_port` into `address` and `port`
#     7-Jan-2014 (CT) Use `-quiet`, not `-verbose`, for `create_config`
#     7-Jan-2014 (CT) Move `-quiet` to `_FCGI_Script_`
#     9-Jul-2014 (CT) Fix `_create_fcgi_script`: catch KeyError;
#                     recognize stdout; use `P.lib_dir`, not `self.lib_dir`
#     9-Jul-2014 (CT) Use `P.py_path`, not `P.lib_dir`
#     1-Sep-2014 (CT) Add `lib_dirs` to arguments of `templateer.call_macro`
#     2-Sep-2014 (CT) Add and use `template_package_dirs`
#     2-Sep-2014 (CT) Change `dynamic_defaults` to check `combined`
#    17-Mar-2015 (CT) Add sub-command `wsgi_script`, remove sub-command `fcgi`
#    17-Mar-2015 (CT) Add option `use_wsgi` to `create_config`
#    19-Mar-2015 (CT) Add `-apache2_4`, `-document_root` to `create_config`
#                     put `config_options` into `globals` of `templateer `
#    19-Mar-2015 (CT) Add option `-cert_extension` to `create_config`
#    26-Feb-2016 (CT) Add option `-ssl_chain` to `create_config`
#    15-Jun-2016 (CT) Rename handler argument `cmd` to `cao`
#     2-Nov-2016 (CT) Fix `_wsgi_script_format`
#                     + leave `sys.path` augmented
#                     + add `py_path`
#     9-Nov-2016 (CT) Add sub-command `uwsgi_config`, `_handle_uwsgi_config`
#    13-Nov-2016 (CT) Factor `_create_config_http`
#                     + Rename `fcgi_script` to `fcgi_config`,
#                       `wsgi_script` to `wsgi_config`
#                     + Call `_create_config_http` in `_handle_*gi_config`
#                     + Remove sub-command `create_config`
#    14-Nov-2016 (CT) Improve `_create_config_http`
#                     + Add option `-HTTP2`
#                     + Use macro `config_file`
#                     + Allow multiple `host_macro` values
#    14-Nov-2016 (CT) Factor `_write_config`
#    14-Nov-2016 (CT) Add `_create_config_uwsgi`
#    16-Nov-2016 (CT) Change options for SSL to `ssl_certificate`...
#    17-Nov-2016 (CT) Change `ssl_ciphers` [https://weakdh.org/sysadmin.html]
#    17-Nov-2016 (CT) Move all option defaults to `_defaults`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function #, unicode_literals

from   _GTW                   import GTW
from   _TFL                   import TFL

import _GTW._OMP.deploy

from   _TFL                   import sos
from   _TFL.Filename          import Filename
from   _TFL.import_module     import import_module
from   _TFL.predicate         import uniq
from   _TFL.pyk               import pyk
from   _TFL.Regexp            import Re_Replacer, re

import sys

strip_empty_lines = Re_Replacer ("^( *\n)( *\n)+", r"\1", re.MULTILINE)

class _GT2W_Sub_Command_ (GTW.OMP.deploy._Sub_Command_) :

    _rn_prefix = "_GT2W"

_Sub_Command_ = _GT2W_Sub_Command_ # end class

_Ancestor = GTW.OMP.deploy.Command

class GT2W_Command (_Ancestor) :
    """Manage deployment applications based on GTW.Werkzeug."""

    _rn_prefix                  = "GT2W"

    _defaults                   = dict \
        ( template_package_dirs = ["_JNJ"]
        )

    _extra_locations            = {}

    _fcgi_script_format         = """\
#!/bin/sh
### fcgi script for `%(server_name)s`
export PYTHONPATH=%(py_path)s
exec %(app)s
"""

    _uwsgi_script_format_tail   = """\
from %(app_mod)s import command
application = command (%(args)s)
"""

    _uwsgi_script_format        = """\
### uwsgi script for `%(server_name)s`
""" + _uwsgi_script_format_tail

    _wsgi_script_format         = """\
### wsgi script for `%(server_name)s`
import sys
sys.path [0:0] = %(py_path)s
""" + _uwsgi_script_format_tail

    class _GT2W_HTTP_Config_ (TFL.Command.Root_Command.Config) :
        """Config file for HTTP-config specific options"""

        rank                    = -80
        _name                   = "HTTP_Config"

    HTTP_Config = _GT2W_HTTP_Config_ # end class

    class _GT2W_Babel_ (_Sub_Command_, _Ancestor._Babel_) :

        _package_dirs           = [ "_JNJ", "_ReST"]

    _Babel_ = _GT2W_Babel_ # end class

    class _GT2W_xxGI_ (_Sub_Command_) :

        is_partial              = True

        _defaults               = dict \
            ( address           = "*"
            , apply_to_version  = "active"
            , ca_key_name       = "CA_crt"
            , ca_path           = "~/CA"
            , document_root     = "~/"
            , host_macro        = "gtw_host"
            , http_user         = "www-data"
            , macro_module      = "httpd_config/apache.m.jnj"
            , port              = "80"
            , processes         = 2
            , root_dir          = "~/active"
            , ssl_ciphers       =
                "ECDHE-RSA-AES128-GCM-SHA256:"
                "ECDHE-ECDSA-AES128-GCM-SHA256:"
                "ECDHE-RSA-AES256-GCM-SHA384:"
                "ECDHE-ECDSA-AES256-GCM-SHA384:"
                "DHE-RSA-AES128-GCM-SHA256:"
                "DHE-DSS-AES128-GCM-SHA256:"
                "kEDH+AESGCM:"
                "ECDHE-RSA-AES128-SHA256:"
                "ECDHE-ECDSA-AES128-SHA256:"
                "ECDHE-RSA-AES128-SHA:"
                "ECDHE-ECDSA-AES128-SHA:"
                "ECDHE-RSA-AES256-SHA384:"
                "ECDHE-ECDSA-AES256-SHA384:"
                "ECDHE-RSA-AES256-SHA:"
                "ECDHE-ECDSA-AES256-SHA:"
                "DHE-RSA-AES128-SHA256:"
                "DHE-RSA-AES128-SHA:"
                "DHE-DSS-AES128-SHA256:"
                "DHE-RSA-AES256-SHA256:"
                "DHE-DSS-AES256-SHA:"
                "DHE-RSA-AES256-SHA:"
                "AES128-GCM-SHA256:"
                "AES256-GCM-SHA384:"
                "AES128-SHA256:"
                "AES256-SHA256:"
                "AES128-SHA:"
                "AES256-SHA:"
                "AES:"
                "CAMELLIA:"
                "DES-CBC3-SHA:"
                "!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:"
                "!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA"
                ### 17-Nov-2016: https://weakdh.org/sysadmin.html
            , ssl_protocols     = "TLSv1.2 TLSv1.1 TLSv1"
            )

        _opts                   = \
            ( "-address:S?Address of virtual host"
            , "-apache2_4:B?Create config for Apache 2.4"
            , "-ca_key_name:S?Name of CA key file"
            , "-ca_path:Q?Path for server-specific CA for client certificates"
            , "-config_path:Q?Path for config file"
            , "-document_root:Q?"
                "Path for DocumentRoot of virtual host. For Apache 2.4, "
                "`DocumentRoot` must include both `root_dir` and `script_path`."
            , "-group:S?Unix group that the wsgi process should be run as"
            , "-host_macro:T,?Name(s) of macro(s) to create virtual host"
            , "-http_user:S?Unix user that the http server runs as"
            , "-HTTP2:B?Support http2 protocol"
            , "-macro_module:S"
                "?Name of jinja module providing config-generation macros"
            , "-port:S?Port for virtual host"
            , "-processes:I?Number of worker processes"
            , "-quiet:B?Don't write information about files created"
            , "-root_dir:Q?Root directory of the web app. This is the path "
                "to the directory containing www/app and the library "
                "directories specified by the option `-lib_dir`."
            , "-script_path:Q?Path of script created"
            , "-server_admin:S?Email address of server admin of virtual host"
            , "-server_aliases:T#8?Alias names for virtual host"
            , "-server_name:S?Fully qualified domain name of virtual host"
            , "-ssl_certificate:S"
                "?Name of file containing SSL certificate(s)"
            , "-ssl_certificate_chain:T#4"
                "?Names of files containing intermediate SSL certificates "
                "(obsolete; use only for Apache < 2.4.8)"
            , "-ssl_certificate_key:S"
                "?Name of file containing SSL certificate secret key"
            , "-ssl_ciphers:S?List of SSL ciphers to use"
            , "-ssl_protocols:S?List of SSL protocols to use"
            , "-template_dirs:P?Directories containing templates for config"
            , "-user:S?Unix user that the wsgi process should be run as"
            )

        def dynamic_defaults (self, defaults) :
            def _gen_template_dirs (self, defaults) :
                yield self.app_dir
                tpds = defaults.get ("template_package_dirs", ["_JNJ"])
                for tpd in tpds :
                    mod = import_module (tpd)
                    yield sos.path.dirname (mod.__file__)
            result   = self.__super.dynamic_defaults (defaults)
            combined = dict (defaults, ** result)
            tdirs    = list (combined.get ("template_dirs", ()))
            tdirs.extend  (_gen_template_dirs (self, combined))
            result ["template_dirs"] = tuple (uniq (tdirs))
            return result
        # end def dynamic_defaults

    _GT2W_xxGI_ # end class

    class _GT2W_FCGI_Config_ (_GT2W_xxGI_) :
        """Create script for running the application as a FastCGI server."""

    _FCGI_Config_ = _GT2W_FCGI_Config_ # end class

    class _GT2W_Setup_Cache_ (_Sub_Command_) :
        """Setup the cache of the application."""

    _Setup_Cache_ = _GT2W_Setup_Cache_ # end class

    class _GT2W_UBYCMS_ (TFL.Command.Sub_Command_Combiner) :
        """Update, Babel compile, pYcompile, setup Cache, Migrate, Switch."""

        _rn_prefix       = "_GT2W"

        _sub_command_seq = \
            [ "update"
            , "pycompile"
            , ["babel", "compile"]
            , ["migrate", "-Active", "-Passive"]
            , "setup_cache"
            , "switch"
            ]

    _UBYCMS_ = _GT2W_UBYCMS_ # end class

    class _GT2W_UWSGI_Config_ (_GT2W_xxGI_) :
        """Create script for running the application as a uwsgi server."""

        _defaults               = dict \
            ( document_root     = "~/active"
            , macro_module      = "httpd_config/nginx.m.jnj"
            )

        _opts                   = \
            ( "-lazy_apps:B?Start app lazily"
            , "-socket:S"
                "?Socket to use for communication between webserver and uwsgi"
            , "-static_pages:B?Serve static pages"
            , "-stats_server:S"
                "?Enable the stats server on the specified address/socket"
            , "-virtualenv:S?Path of virtualenv to use"
            )

    _UWSGI_Config_ = _GT2W_UWSGI_Config_ # end class

    class _GT2W_WSGI_Config_ (_GT2W_xxGI_) :
        """Create script for running the application as a wsgi server."""


    _WSGI_Config_ = _GT2W_WSGI_Config_ # end class

    def _create_config_http (self, cao, xxgi_macro_name, ** kw) :
        from   _JNJ import JNJ
        import _JNJ.Templateer
        ssl_certificate = \
            (  Filename
                 ( cao.ssl_certificate, ".pem", "/etc/ssl/certs/"
                 , absolute = True
                 ).name
            if cao.ssl_certificate else ""
            )
        ssl_certificate_chain = tuple \
            (  Filename
                 ( ssc, ".pem", "/etc/ssl/certs/"
                 , absolute = True
                 ).name
            for ssc in cao.ssl_certificate_chain
            )
        ssl_certificate_key = \
            (  Filename
                 ( cao.ssl_certificate_key, ".key", "/etc/ssl/private/"
                 , absolute = True
                 ).name
            if cao.ssl_certificate_key else ""
            )
        config_options         = dict \
            ( kw
            , address                = cao.address
            , admin                  = cao.server_admin
            , aliases                = cao.server_aliases
            , apache2_4              = cao.apache2_4
            , app_root               = cao.root_dir
            , ca_key_name            = cao.ca_key_name
            , ca_path                = cao.ca_path
            , cmd                    = cao
            , config_name            = cao.config_path
            , doc_root               = cao.document_root
            , extra_locations        = dict
                (cao.GET ("extra_locations", {}), ** self._extra_locations)
            , group                  = cao.group
            , host_macros            = cao.host_macro
            , HTTP2                  = cao.HTTP2
            , lib_dirs               = cao.lib_dir
            , macro_name             = "config_file"
            , macro_module           = cao.macro_module
            , port                   = cao.port
            , script                 = cao.script_path
            , server_name            = cao.server_name
            , ssl_certificate        = ssl_certificate
            , ssl_certificate_chain  = ssl_certificate_chain
            , ssl_certificate_key    = ssl_certificate_key
            , ssl_ciphers            = cao.ssl_ciphers
            , ssl_protocols          = cao.ssl_protocols
            , templ_name             = cao.macro_module
            , user                   = cao.user
            )
        templateer             = JNJ.Templateer \
            ( encoding         = cao.input_encoding
            , globals          = dict (config_options = config_options)
            , load_path        = cao.template_dirs
            , trim_blocks      = True
            )
        xxgi_macro             = templateer.GTW.get_macro \
            (xxgi_macro_name, templ_name = cao.macro_module)
        config_options.update (xxgi_macro = xxgi_macro)
        config   = templateer.call_macro (** config_options)
        config_s = strip_empty_lines (config)
        c_path   = cao.config_path
        self._write_config (cao, c_path, config_s, "Created http  config")
        return config_options, templateer
    # end def _create_config_http

    def _create_config_uwsgi (self, cao, config_options, templateer) :
        P            = self._P (cao)
        app_dir      = sos.path.dirname  (self._app_path (cao, P))
        macro        = templateer.GTW.get_macro \
            ("uwsgi_config_ini", templ_name = config_options ["templ_name"])
        script_name  = Filename (".ini", cao.script_path, absolute = True)
        c_path       = script_name.name \
            if script_name.base not in ("-", "stdout") else ""
        socket       = config_options ["socket"]
        if socket.startswith ("unix:") :
            socket   = socket [5:]
        stats_server = config_options ["stats_server"]
        if stats_server.startswith ("unix:") :
            stats_server     = stats_server [5:]
        kw     = dict \
            ( chdir          = script_name.directory
            , chmod_socket   = "660"
            , chown_socket   = "%s:%s"
                % (cao.user or cao.http_user, cao.http_user)
            , config_name    = c_path
            , gid            = cao.group or cao.http_user
            , lazy_apps      = ["false", "true"] [cao.lazy_apps]
            , master         = "true"
            , module         = script_name.base
            , need_threads   = "true"
            , processes      = cao.processes
            , py_path        = reversed
                  ([pyk.encoded (app_dir)] + P.py_path.split (":"))
            , server_name    = config_options ["server_name"]
            , socket         = socket
            , stats_server   = stats_server
            , threads        = 0
            , uid            = cao.user or cao.http_user
            , virtualenv     = cao.virtualenv
            )
        config   = macro (** kw)
        config_s = strip_empty_lines (config)
        self._write_config \
            (cao, c_path, config_s, "Created uwsgi config")
    # end def _create_config_uwsgi

    def _create_fcgi_script (self, cao, argv = (), script_path = None) :
        P      = self._P (cao)
        a_conf = cao.app_config
        try :
            h_conf = cao._spec ["HTTP_Config"].pathes
        except KeyError :
            h_conf = []
        config = self.App_Config.auto_split.join (a_conf + h_conf)
        args   = ("fcgi", "-config", config) + tuple (argv)
        app    = self._app_cmd (cao, P, args = args)
        s_path = script_path or cao.script_path
        script = self._fcgi_script_format % dict \
            ( app         = app
            , py_path     = P.py_path
            , server_name = cao.server_name
            )
        self._write_config (cao, s_path, script, "Created fcgi  script")
    # end def _create_fcgi_script

    def _create_wsgi_script \
            (self, cao, argv = (), script_path = None, script_format = None) :
        P      = self._P (cao)
        a_conf = cao.app_config
        try :
            h_conf = cao._spec ["HTTP_Config"].pathes
        except KeyError :
            h_conf = []
        config   = self.App_Config.auto_split.join (a_conf)
        app_dir  = sos.path.dirname  (self._app_path (cao, P))
        app_mod  = sos.path.splitext (sos.path.basename (cao.app_module)) [0]
        args     = ("wsgi", "-config", config) + tuple (argv)
        s_path   = script_path or cao.script_path
        if script_format is None :
            script_format = self._wsgi_script_format
        script = script_format % dict \
            ( app_dir     = app_dir
            , app_mod     = app_mod
            , args        = list (args) if args else ""
            , py_path     = [pyk.encoded (app_dir)] + P.py_path.split (":")
            , server_name = cao.server_name
            )
        self._write_config (cao, s_path, script, "Created wsgi  script")
    # end def _create_wsgi_script

    def _handle_fcgi_config (self, cao) :
        self._create_fcgi_script (cao, cao.argv, cao.script_path)
        self._create_config_http (cao, "use_fcgi")
    # end def _handle_fcgi_config

    def _handle_setup_cache (self, cao) :
        P    = self._P (cao)
        app  = self._app_cmd (cao, P)
        args = ("setup_cache", ) + tuple (cao.argv)
        self._app_call (cao, P, app, args)
    # end def _handle_setup_cache

    def _handle_uwsgi_config (self, cao) :
        app_name = "%s__%s" % (cao.server_name.replace (".", "_"), cao.port)
        socket   = cao.socket
        if not socket :
            socket = "unix:/tmp/%s.sock" % (app_name, )
        stats_server = cao.stats_server
        if not stats_server :
            stats_server = "unix:/tmp/%s.stats-server" % (app_name, )
        config_options, templateer = self._create_config_http \
            ( cao, "use_uwsgi"
            , app_name     = app_name
            , socket       = socket
            , static_pages = cao.static_pages
            , stats_server = stats_server
            )
        self._create_config_uwsgi (cao, config_options, templateer)
        self._create_wsgi_script \
            (cao, cao.argv, cao.script_path, self._uwsgi_script_format)
    # end def _handle_uwsgi_config

    def _handle_wsgi_config (self, cao) :
        self._create_wsgi_script (cao, cao.argv, cao.script_path)
        self._create_config_http (cao, "use_wsgi")
    # end def _handle_wsgi_config

    def _write_config (self, cao, c_path, config, msg) :
        def write (f, config) :
            f.write (config.strip ())
            f.write ("\n")
        if c_path and not c_path.endswith (("-", "stdout")) :
            with open (c_path, "w") as f :
                write (f, config)
            if not cao.quiet :
                print (msg, c_path)
        else :
            write (sys.stdout, config)
    # end def _write_config

Command = GT2W_Command # end class

if __name__ != "__main__" :
    GTW.Werkzeug._Export_Module ()
### __END__ GTW.Werkzeug.deploy
