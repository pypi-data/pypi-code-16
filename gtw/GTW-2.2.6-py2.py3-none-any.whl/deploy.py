# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.deploy
#
# Purpose
#    Provide an extendable Command for the deployment of applications based
#    on GTW
#
# Revision Dates
#    22-May-2012 (CT) Creation
#    23-May-2012 (CT) Continue creation
#    24-May-2012 (CT) Factor `_app_cmd`, add `print` to `_handle_...` methods
#    24-May-2012 (CT) Add `PYTHONPATH` to `.pbl.env`
#    25-May-2012 (CT) Add sub-command `shell`
#    25-May-2012 (CT) Add `path` to `_app_cmd`
#    30-May-2012 (CT) Add sub-command `app`
#    31-May-2012 (CT) Factor `-config` option to `TFL.Command`
#    31-May-2012 (CT) Change `_handle_app` to allow multiple arguments
#     1-Jun-2012 (CT) Move `-apply_to_version` to `_Sub_Command_` to allow
#                     sub-command specific defaults
#     1-Jun-2012 (CT) Factor `_app_call`
#     1-Jun-2012 (CT) Factor `P.app_dir`
#     1-Jun-2012 (CT) Add option `-py_path`; factor `P.python`
#     1-Jun-2012 (CT) Add `-py_options` to `_Sub_Command_`,
#                     remove `-python_options` from `_Pycompile_`
#     3-Jun-2012 (CT) Factor `Config` to `Root_Command`
#     3-Jun-2012 (CT) Add optional `_args` to `_app_cmd`
#     4-Jun-2012 (CT) Fix `app_dir` in `_handle_babel_compile`
#     4-Jun-2012 (CT) Change `Shell.handler` to `_handle_shell`
#     4-Jun-2012 (CT) Rewrite `_handle_update` to use `_handle_vc`
#    11-Sep-2012 (CT) Fix `_handle_babel_extract` (assign `P`)
#    27-Jul-2013 (CT) Remove old `.pyc` and `.pyo` files in `_handle_pycompile`
#    20-Dec-2013 (CT) Fix `_P` to handle non-standard `apply_to_version`
#    15-Jan-2014 (CT) Change `_P` to set `.python` after `env ["PYTHONPATH"]`
#     1-Sep-2014 (CT) Convert `prefix` to `pbl.path`
#     1-Sep-2014 (CT) Use `pjoin`, not `plumbum.path` operator `/`
#     1-Sep-2014 (CT) Use `P.cmd.apply_to_version` as default version for
#                     `_python_path` (need symbolic link in path)
#     2-Sep-2014 (CT) Change `dynamic_defaults` to check `combined`
#    26-Jan-2015 (CT) Derive `_Meta_Base_` from `M_Auto_Update_Combined`,
#                     not `M_Auto_Combine`
#    17-Mar-2015 (CT) Factor `_app_path`
#     8-Apr-2015 (CT) Add `compile_options = "-q"` to `_defaults`
#     5-Aug-2015 (CT) Remove `_handler_prefix` (obsoleted by `handler_name`)
#    10-Feb-2016 (CT) Adapt `_handle_babel_compile` to changed `TFL.Babel`
#    10-Feb-2016 (CT) Change `_P` to apply `normpath` to `app_dir`
#    15-Jun-2016 (CT) Rename handler argument `cmd` to `cao`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function #, unicode_literals

from   _TFL                   import TFL
from   _GTW                   import GTW

from   _TFL                   import sos

import _TFL.Command

from   itertools              import chain as ichain
import sys

pjoin = sos.path.join

class _GTWD_Command_ (TFL.Command.Command) :

    _rn_prefix = "_GTWD"

_Command_ = _GTWD_Command_ # end class

class _GTWD_Sub_Command_ (TFL.Command.Sub_Command) :

    _rn_prefix              = "_GTWD"

    _defaults               = dict \
        ( apply_to_version  = "passive"
        , py_options        = "-O"
        )
    _opts                   = \
        ( "-apply_to_version:S?Name of version to apply command to"
        , "-py_options:T ?Options passed to python interpreter, e.g., -O"
        )

_Sub_Command_ = _GTWD_Sub_Command_ # end class

class GTWD_Command (TFL.Command.Root_Command) :
    """Extendable deployment command for applications based on GTW"""

    _rn_prefix              = "GTWD_"

    min_args                = 1

    _defaults               = dict \
        ( active_name       = "active"
        , app_dir           = "app"
        , bugs_address      = "tanzer@swing.co.at,martin@mangari.org"
        , compile_options   = "-q"
        , copyright_holder  = "Mag. Christian Tanzer, Martin Glück"
        , lib_dir           = "lib"
        , output_encoding   = "utf-8"
        , passive_name      = "passive"
        , py_path           = sys.executable
        , root_path         = "./"
        , skip_modules      = "_pyk3.py"
        , vcs               = "git"
        )

    _opts                   = \
        ( "-active_name:S?Name of symbolic link for active version"
        , "-app_dir:S?Name of directory holding the application"
        , "-app_module:S=app.py?Name of main module of application"
        , "-bugs_address:S?Email address to send bug reports to"
        , "-copyright_holder:S?Name of copyright holders"
        , "-dry_run:B?Don't run the command, just print what would be done"
        , "-lib_dir:P:"
            "?Name of directory with the library used by the application"
        , "-passive_name:S?Name of symbolic link for passive version"
        , "-project_name:S?Name of project"
        , "-py_path:P?Path for nested python interpreter"
        , "-root_path:P?Root path of application versioning"
        , "-verbose:B"
        , "-vcs:S?Name of version control system used"
        , TFL.CAO.Opt.Input_Encoding ()
        , TFL.CAO.Opt.Output_Encoding
            ( description   = "Default encoding for generated files"
            )
        )

    _vcs_update_map         = dict \
        ( git               = "pull"
        , hg                = "pull"
        , svn               = "update"
        )

    class _GTWD_App_ (_Sub_Command_) :
        """Run a command of the web application."""

        min_args            = 1

    _App_ = _GTWD_App_ # end class

    class _GTWD_Babel_ (_Command_) :
        """Extract or compile translations."""

        _attrs_uniq_to_update_combine = ("_package_dirs", )

        min_args            = 1

        _defaults           = dict \
            ( languages     = "en"
            )

        _opts               = \
            ( "-babel_config:S?File with global babel configuration"
            , "-languages:S,?Languages to extract/compile translations for"
            , "-package_dirs:P,"
                "?Package directories (relative to Python path) to "
                "include in extraction/compilation of translations"
            )

        _babel_config       = "_MOM/base_babel.cfg"
        _package_dirs       = []

        class _GTWD_Extract_ (_Sub_Command_) :
            """Extract strings to translate."""

        _Extract_ = _GTWD_Extract_ # end class

        class _GTWD_Compile_ (_Sub_Command_) :
            """Compile translations."""

        _Compile_ = _GTWD_Compile_ # end class

        def dynamic_defaults (self, defaults) :
            result   = self.__super.dynamic_defaults (defaults)
            combined = dict (defaults, ** result)
            if "babel_config" not in combined :
                bc = self._babel_config
                if bc :
                    if not sos.path.isabs (bc) :
                        bc = pjoin (self.lib_dir, bc)
                    result ["babel_config"] = bc
            if "package_dirs" not in combined :
                result ["package_dirs"] = self._package_dirs
            return result
        # end def dynamic_defaults

    _Babel_ = _GTWD_Babel_ # end class

    class _GTWD_Info_ (_Sub_Command_) :
        """Show info about the application."""

    _Info_ = _GTWD_Info_     # end class

    class _GTWD_Pycompile_ (_Sub_Command_) :
        """Compile python bytecode of the application."""

        _opts               = \
            ( "-compile_options:S,?Options passed to compileall, e.g., -q"
            , "-skip_modules:S,?Python modules to skip compilation for"
            )

    _Pycompile_ = _GTWD_Pycompile_ # end class

    class _GTWD_Shell_ (_Sub_Command_) :
        """Open interactive python shell."""

    _Shell_ = _GTWD_Shell_ # end class

    class _GTWD_Switch_ (_Sub_Command_) :
        """Switch links to active and passive version."""

    _Switch_ = _GTWD_Switch_ # end class

    class _GTWD_Update_ (_Sub_Command_) :
        """Update the source code of the application."""

    _Update_ = _GTWD_Update_ # end class

    class _GTWD_VC_ (_Sub_Command_) :
        """Run a command of the version control system."""

        min_args            = 1

    _VC_ = _GTWD_VC_ # end class

    @TFL.Meta.Once_Property
    def pbc (self) :
        import plumbum
        return sys.modules ["plumbum.cmd"]
    # end def pbc

    @TFL.Meta.Once_Property
    def pbl (self) :
        from plumbum import local
        return local
    # end def pbl

    def _app_call (self, cao, P, app, args = (), app_dir = None) :
        pbl = self.pbl
        cwd = pbl.cwd
        if not args :
            args = tuple (cao.argv)
        if app_dir is None :
            app_dir = P.app_dir
        with cwd (app_dir) :
            if cao.verbose or cao.dry_run :
                print ("cd", pbl.path ())
                print (app, " ".join (args))
            if not cao.dry_run :
                print (app (* args))
    # end def _app_call

    def _app_cmd (self, cao, P, version = None, args = ()) :
        result = P.python [self._app_path (cao, P, version)]
        if cao.verbose :
            result = result ["-verbose"]
        if args :
            result = result [args]
        return result
    # end def _app_cmd

    def _app_path (self, cao, P, version = None) :
        if version is None :
            version = cao.apply_to_version
        result = pjoin (str (P.root), version, cao.app_dir, cao.app_module)
        return sos.path.normpath (result)
    # end def _app_path

    def _handle_app (self, cao, * args) :
        P   = self._P (cao)
        app = self._app_cmd (cao, P)
        self._app_call (cao, P, app, args)
    # end def _handle_app

    def _handle_babel_compile (self, cao) :
        P       = self._P (cao)
        cwd     = self.pbl.cwd
        args    = \
             ( "-m", "_TFL.Babel", "compile"
             , "-combine"
             , "-import_file", cao.app_module
             , "-use_fuzzy"
             )
        app_module_dir = sos.path.dirname (cao.app_module)
        with cwd (P.app_dir) :
            if cao.verbose or cao.dry_run :
                print ("cd", self.pbl.path ())
            for l in cao.languages :
                l_dir  = pjoin (app_module_dir, "locale", l, "LC_MESSAGES")
                l_args = args + \
                    ( "-languages",   l
                    , "-output_file", pjoin (l_dir, "messages.mo")
                    )
                if cao.verbose or cao.dry_run :
                    print ("mkdir -p", l_dir)
                    print ("python", " ".join (l_args))
                if not cao.dry_run :
                    if not sos.path.isdir (l_dir) :
                        sos.makedirs (l_dir)
                    print (P.python (* l_args))
    # end def _handle_babel_compile

    def _handle_babel_extract (self, cao) :
        P       = self._P (cao)
        head_args = ("-m", "_TFL.Babel")
        tail_args = ("-sort", ) + tuple (cao.package_dirs)
        extr_args = \
            ( head_args
            + ( "extract"
              , "-bugs_address",     cao.bugs_address
              , "-charset",          cao.output_encoding
              , "-copyright_holder", cao.copyright_holder
              , "-global_config",    cao.babel_config
              , "-project",          cao.project_name
              )
            + tail_args
            )
        lang_args = \
            ( head_args
            + ( "language", ",".join (cao.languages))
            + tail_args
            )
        if cao.verbose or cao.dry_run :
            print ("python", " ".join (extr_args))
            print ("python", " ".join (lang_args))
        if not cao.dry_run :
            print (P.python (* extr_args))
            print (P.python (* lang_args))
    # end def _handle_babel_extract

    def _handle_info (self, cao) :
        P       = self._P (cao)
        fmt     = "%-15s : %s"
        print (fmt % (cao.active_name,  P.active))
        print (fmt % (cao.passive_name, P.passive))
        print (fmt % ("selected",       P.selected))
        print (fmt % ("prefix",         P.prefix))
        print (fmt % ("app-dir",        P.app_dir))
        print (fmt % ("lib-dirs",       P.lib_dirs))
        print (fmt % ("python",         P.python))
        print (fmt % ("python-library", self.lib_dir))
        print (fmt % ("nested-library", P.py_path))
        print (fmt % ("PYTHONPATH",     sys.path))
        print \
            ( fmt
            % ( "NESTEDPATH"
              , P.python ("-c", "import sys; print sys.path")
              )
            )
    # end def _handle_info

    def _handle_pycompile (self, cao) :
        P    = self._P (cao)
        cwd  = self.pbl.cwd
        root = pjoin (cao.root_path, cao.apply_to_version)
        dirs = [cao.app_dir] + cao.lib_dir
        args = tuple \
            ( ichain
                ( ["-m", "compileall"]
                , cao.compile_options
                , ((["-x"] + cao.skip_modules) if cao.skip_modules else [])
                , dirs
                )
            )
        clean = self.pbl ["find"] \
            [tuple (dirs + ["-name", "*.py[co]", "-delete"])]
        with cwd (root) :
            if cao.verbose or cao.dry_run :
                print ("cd", self.pbl.path ())
                print (clean)
                print (P.python, " ".join (args))
            if not cao.dry_run :
                clean ()
                P.python (* args)
    # end def _handle_pycompile

    def _handle_shell (self, cao) :
        import _TFL.Environment
        P       = self._P (cao)
        command = self._root
        TFL.Environment.py_shell ()
    # end def _handle_shell

    def _handle_switch (self, cao) :
        P    = self._P (cao)
        ln_s = self.pbl ["ln"] ["-f", "-s", "-T" ]
        cmda = ln_s [P.active,  cao.passive_name]
        cmdp = ln_s [P.passive, cao.active_name]
        cwd  = self.pbl.cwd
        with cwd (P.root) :
            if cao.verbose or cao.dry_run :
                print (cmda, ";", cmdp)
            if not cao.dry_run :
                cmda ()
                cmdp ()
    # end def _handle_switch

    def _handle_update (self, cao) :
        return self._handle_vc (cao, self._vcs_update_map [cao.vcs])
    # end def _handle_update

    def _handle_vc (self, cao, * args) :
        P    = self._P (cao)
        cwd  = self.pbl.cwd
        vcs  = self.pbl [cao.vcs] [args]
        argv = tuple (cao.argv)
        for d in P.dirs :
            with cwd (d) :
                p = self.pbl.path ()
                if cao.verbose or cao.dry_run :
                    print ("cd", p)
                    print (vcs, " ".join (argv))
                if not cao.dry_run :
                    if not cao.verbose :
                        print ("*" * 3, p, "*" * 20)
                    print (vcs (* argv))
    # end def _handle_vc

    def _P (self, cao) :
        pbl     = self.pbl
        active  = sos.path.realpath     (cao.active_name)
        passive = sos.path.realpath     (cao.passive_name)
        root    = sos.path.realpath     (cao.root_path)
        prefix  = sos.path.commonprefix ([active, passive, root])
        atv     = cao.apply_to_version
        if prefix :
            active     = active  [len (prefix):].lstrip ("/")
            passive    = passive [len (prefix):].lstrip ("/")
        result = TFL.Record \
            ( active   = active
            , cao      = cao
            , cmd      = cao ### backwards compatibility
            , passive  = passive
            , prefix   = prefix
            , root     = pbl.path (root)
            )
        result.selected = getattr (result, atv, atv)
        result.app_dir  = sos.path.normpath \
            (pjoin (result.prefix, result.selected, cao.app_dir))
        result.py_path  = pbl.env ["PYTHONPATH"] = self._python_path (result)
        result.lib_dirs = result.py_path.split (":")
        result.python   = pbl [cao.py_path] \
            [tuple (o for o in cao.py_options if o)]
        result.dirs     = [result.app_dir] + result.lib_dirs
        return result
    # end def _P

    def _python_path (self, P, version = None) :
        if version is None :
            version = P.cao.apply_to_version
        return ":".join (pjoin (P.prefix, version, p) for p in P.cao.lib_dir)
    # end def _python_path

Command = GTWD_Command # end class

if __name__ != "__main__" :
    GTW._Export_Module ()
if __name__ == "__main__" :
    Command () ()
### __END__ GTW.deploy
