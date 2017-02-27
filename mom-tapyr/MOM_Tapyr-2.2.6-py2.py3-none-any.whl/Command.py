# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.Command
#
# Purpose
#    Provide an extendable Command for applications based on MOM
#
# Revision Dates
#    27-Apr-2010 (CT) Creation
#    19-May-2010 (CT) `app_type_and_uri` factored
#    20-May-2010 (CT) `scope` corrected (guard for `if` modifying `create`)
#    24-Jun-2010 (CT) Use `MOM.EMS.Backends` and `DBS.Url`
#    25-Jun-2010 (CT) Command handlers added
#    29-Jun-2010 (CT) `-copyright_start` added
#     1-Jul-2010 (CT) `-overwrite` added to `cmd__migrate__opts`
#    12-Jul-2010 (CT) `do_migrate` changed to use `DB_Man`
#     2-Aug-2010 (CT) `cmd__buns` added
#     3-Aug-2010 (MG) Sub-command `shell` added
#    10-Aug-2010 (CT) Command `description` defined as doc-string of `handler`
#    11-Aug-2010 (CT) `cmd__info` and friends added
#    13-Aug-2010 (CT) `-readonly` added to command `migrate`
#    16-Aug-2010 (CT) `cmd__readonly` and friends added
#    16-Aug-2010 (CT) `-verbose` added
#    16-Aug-2010 (MG) `verbose` handling in `scope` fixed
#    16-Aug-2010 (CT) `cmd__delete` and friends added
#    27-Jan-2012 (CT) `app_path` added
#    24-Apr-2012 (CT) Add call to `db_man_t.ems.compact` to `_do_migration`
#    17-May-2012 (CT) Derive from `TFL.Command`,
#                     rename from `Scaffold` to `Command`
#    22-May-2012 (CT) Remove unused imports
#    22-May-2012 (CT) Factor `app_path` to `TFL.Command.app_dir`
#    22-May-2012 (CT) Factor `TFL.Sub_Command`
#    31-May-2012 (CT) Factor `-config` option to `TFL.Command`
#    31-May-2012 (CT) Call `scope.ems.compact` in `_handle_create`
#     2-Jun-2012 (CT) Add `Config` derived from `Config_Option`
#     3-Jun-2012 (CT) Factor `Config` to `Root_Command`
#     4-Jun-2012 (CT) Add `default` "yes" to `_Readonly_.state`
#    21-Jan-2013 (MG) Add support for project specific legacy lifter
#    28-Jan-2013 (CT) Print `Url (...).path` in `_handle_migrate`
#    26-May-2013 (CT) Change `_cro_context` to use `try/finally`, not `/except`
#    26-May-2013 (CT) Add support for authorization migration
#    27-May-2013 (CT) Add optional argument `mig_auth_file` to
#                     `_handle_load_auth_mig` and `_read_auth_mig`
#    28-May-2013 (CT) Move `-Auth_Migrate` to `MOM_Command._opts`
#                     (some descendents call `_handle_create` from handlers
#                     of other commands)
#    28-May-2013 (CT) Use `sos.expanded_path` in `_read_auth_mig`
#    13-Jun-2013 (CT) Remove `PNS_Aliases`
#     6-Aug-2013 (CT) Add exception handler to `_handle_auth_mig`,
#                     `_handle_load_auth_mig`
#    23-Aug-2013 (CT) Add option `-Engine_Echo`
#    25-Aug-2013 (CT) Add and use `_cleaned_url` to avoid leaking DB passwords
#    25-Aug-2013 (CT) Change `_print_info` to elide commits, if too many
#     2-Sep-2014 (CT) Change `dynamic_defaults` to check `combined`
#    22-Sep-2014 (CT) Add sub-command `_Script_`,
#                     methods `_handle_script` and `_handle_script_globals`
#    12-Oct-2014 (CT) Add option `-sha` with default `sha224`
#    14-Oct-2014 (CT) Add sub-command `version_hash`
#    17-Oct-2014 (CT) Pass globals to `py_shell`
#     7-May-2015 (CT) Fix initialization of `scope` in `_handle_script`
#     7-May-2015 (CT) Add options `-journal_dir`, `-keep_journal`
#     6-Aug-2015 (CT) Add `__doc__`
#    28-Oct-2015 (CT) Use `pyk.pickle_protocol`
#    15-Jun-2016 (CT) Add option `-debug` to sub-command `_Create_`
#    15-Jun-2016 (CT) Rename handler argument `cmd` to `cao`
#    ««revision-date»»···
#--

from   __future__             import print_function

from   _MOM.import_MOM        import *

import _MOM.DB_Man
import _MOM._EMS.Backends

from   _TFL.formatted_repr    import formatted_repr, formatted_repr_compact
from   _TFL.I18N              import _, _T, _Tn
from   _TFL.portable_repr     import portable_repr
from   _TFL.pyk               import pyk
from   _TFL.Regexp            import Re_Replacer, re
from   _TFL                   import sos

import _TFL.CAO
import _TFL.Command
import _TFL.Context
import _TFL.Environment
import _TFL.Filename
import _TFL.Secure_Hash
import _TFL.Undef
import _TFL._Meta.Once_Property

import contextlib
import logging
import stat

_cleaned_url = Re_Replacer (r"(://\w+:)(\w+)@", r"\1<elided>@")

class SA_WE_Opt (TFL.CAO.Bool) :
    """Turn SA warnings into errors"""

    def __init__ (self, ** kw) :
        assert "name" not in kw
        kw ["name"] = self.__class__.__name__
        if "description" not in kw :
            kw ["description"] = self.__class__.__doc__
        self.__super.__init__ (** kw)
    # end def __init__

    def cook (self, value, cao = None) :
        result = self.__super.cook (value, cao)
        if result :
            import warnings
            from sqlalchemy import exc as sa_exc
            warnings.filterwarnings \
                (action = "error", category = sa_exc.SAWarning)
        return result
    # end def cook

# end class SA_WE_Opt

class _MOM_Sub_Command_ (TFL.Command.Sub_Command) :

    _rn_prefix              = "_MOM"

_Sub_Command_ = _MOM_Sub_Command_ # end class

class MOM_Command (TFL.Command.Root_Command) :
    "" ### """Extendable Command for applications based on MOM"""

    _rn_prefix              = "MOM_"

    ANS                     = None
    DB_Man                  = MOM.DB_Man
    nick                    = "NN"
    Scope                   = MOM.Scope
    undef                   = TFL.Undef ()

    _buns                   = \
        ( TFL.CAO.Bundle
            ( "mig1"
            , "Migrate from `db_url` to `target_db_url`"
            , command       = "migrate"
            , target_db_url = "hps:///migration"
            )
        , TFL.CAO.Bundle
            ( "mig2"
            , "Migrate from `target_db_url` to `db_url`"
            , command       = "migrate"
            , db_url        = "hps:///migration"
            , Auth_Migrate  = "yes"
            )
        ### Application needs to define `db_url = target_db_url = XXX` for
        ### the bundles `mig1` and `mig2` to work conventiently
        )
    _default_db_name        = "" ### used by `default_db_name`
    _defaults               = dict \
        ( copyright_start   = 2010
        , sha               = TFL.Secure_Hash.sha224
        )
    _opts                   = \
        ( "-Auth_Migrate:B?Migrate authorization objects"
        , "-copyright_start:I?Start of copyright for this application"
        , TFL.CAO.Abs_Path
            ( name        = "db_name"
            , description = "Default name of database"
            , max_number  = 1
            )
        , "-db_url:S=hps://"
            "?Database url (form: `dialect://user:password@host:port/db_name`)"
        , "-Engine_Echo:B"
             "?Set the echo flag of the database engine, if appropriate for "
             "the backend"
        , TFL.CAO.Abs_Path
            ( name        = "journal_dir"
            , description =
                "Directory where journal of database changes is kept "
                "if enabled by `-keep_journal`"
            , max_number  = 1
            )
        , "-keep_journal:B?Keep a journal of database changes"
        , TFL.CAO.Abs_Path
            ( name        = "mig_auth_file"
            , description = "Default name of auth migration file"
            , max_number  = 1
            )
        , TFL.CAO.SHA ()
        , SA_WE_Opt ()
        , "-verbose:B"
        )

    ### Sub-commands defined as class attributes to allow redefinition by
    ### derived classes; meta class puts their names into `_sub_commands`
    class _MOM_Auth_Mig_ (_Sub_Command_) :
        """Create a migration of the authorization objects"""

    _Auth_Mig_ = _MOM_Auth_Mig_ # end class

    class _MOM_Create_ (_Sub_Command_) :
        """Create the database specified by `-db_url`."""

        _opts                   = \
            ( "-debug:B=no"
            ,
            )

    _Create_ = _MOM_Create_ # end class

    class _MOM_Delete_ (_Sub_Command_) :
        """Delete the database specified by `-db_url`."""

    _Delete_ = _MOM_Delete_ # end class

    class _MOM_Info_ (_Sub_Command_) :
        """Display info about the database specified by `-db_url`."""

    _Info_ = _MOM_Info_ # end class

    class _MOM_Load_ (_Sub_Command_) :
        """Load database specified by `-db_url`."""

    _Load_ = _MOM_Load_ # end class

    class _MOM_Load_Auth_Mig_ (_Sub_Command_) :
        """Load a migration of the authorization objects."""

    _Load_Auth_Mig_ = _MOM_Load_Auth_Mig_ # end class

    class _MOM_Migrate_ (_Sub_Command_) :
        """Migrate database specified by `-db_url` to `-target_db_url`."""

        _opts                   = \
            ( "chunk_size:I=10000?Number of entities in one chunk"
            , "overwrite:B?Overwrite `target_db_url` if necessary"
            , "readonly:B?Mark database `db_url` as readonly"
            , "target_db_url:S?Database url for target database"
            , "legacy_lifter:P?Module containing project specific lifter code"
            )

    _Migrate_ = _MOM_Migrate_ # end class

    class _MOM_Readonly_ (_Sub_Command_) :
        """Change readonly-state of database."""

        _args                   = \
            ( TFL.CAO.Arg.Key
                ( name          = "state"
                , dct           = dict
                    ( yes       = True
                    , no        = False
                    )
                , default       = "yes"
                )
            ,
            )

    _Readonly_ = _MOM_Readonly_ # end class

    class _MOM_Script_ (_Sub_Command_) :
        """Run one or more scripts."""

        _args                   = \
            ( "script:P?Name of script(s) to run"
            ,
            )
        min_args                = 1
        _opts                   = \
            ( "-load:B=yes?Load database before running script(s)"
            , "-commit:B=yes?Commit changes to database after running script(s)"
            )

    _Script_ = _MOM_Script_ # end class

    class _MOM_Shell_ (_Sub_Command_) :
        """Open an interactive python shell."""

    _Shell_ = _MOM_Shell_ # end class

    class _MOM_Version_Hash_ (_Sub_Command_) :
        """Show version-hash of program or database or both."""

        _opts                   = \
            ( "database:B?Show hash of database version"
            , "code:B?Show hash of program version"
            )

    _Version_Hash_ = _MOM_Version_Hash_ # end class

    @TFL.Meta.Once_Property
    def default_db_name (self) :
        return sos.path.join \
            ( self.app_dir
            , self._default_db_name or self.ANS.__name__.lower ()
            )
    # end def default_db_name

    @TFL.Meta.Once_Property
    def default_mig_auth_file (self) :
        return "".join (("~/.AM_", self.ANS.__name__.lower (), ".sam"))
    # end def default_mig_auth_file

    def app_type (self, * ems_dbw) :
        """Return app_type named `self.nick` for application namespace
           `self.ANS`.
        """
        assert self.ANS is not None
        result = MOM.App_Type.Table.get (self.nick)
        if result is None :
            result = MOM.App_Type   (self.nick, self.ANS)
        if ems_dbw :
            result = result.Derived (* ems_dbw)
        return result
    # end def app_type

    def app_type_and_url (self, db_url = "hps://", default_path = None) :
        assert self.ANS is not None
        EMS, DBW, DBS = MOM.EMS.Backends.get (db_url)
        apt = self.app_type (EMS, DBW)
        url = DBS.Url (db_url, self.ANS, default_path)
        return apt, url
    # end def app_type_and_url

    def dynamic_defaults (self, defaults) :
        result   = self.__super.dynamic_defaults (defaults)
        combined = dict (defaults, ** result)
        if "db_name" not in combined :
            result ["db_name"] = self.default_db_name
        if "mig_auth_file" not in combined :
            result ["mig_auth_file"] = self.default_mig_auth_file
        return result
    # end def dynamic_defaults

    def scope ( self
              , db_url       = "hps://"
              , default_path = None
              , create       = True
              , verbose      = False
              , engine_echo  = False
              , journal_dir  = None
              ) :
        apt, url = self.app_type_and_url (db_url, default_path)
        if engine_echo :
            try :
                EP = apt.DBW.PNS.DBS.Engine_Parameter
            except AttributeError :
                pass
            else :
                EP ["echo"] = True
        create = create or url.create
        if create :
            if verbose :
                print ("Creating new scope", apt, url.path or "in memory")
            scope = self._create_scope (apt, url, verbose, journal_dir)
        else :
            if verbose :
                print ("Loading scope", apt, _cleaned_url (str (url)))
            scope = self._load_scope (apt, url, journal_dir)
        return scope
    # end def scope

    def _create_scope (self, apt, url, verbose = False, journal_dir = None) :
        if url :
            apt.delete_database (url)
        result = self.Scope.new (apt, url)
        if journal_dir :
            self._setup_journal (result, journal_dir)
        return result
    # end def _create_scope

    @TFL.Contextmanager
    def _cro_context (self, db_man, state) :
        old_state = db_man.db_meta_data.readonly
        db_man.change_readonly (state)
        try :
            yield
        finally :
            db_man.change_readonly (old_state)
    # end def _cro_context

    def _do_migration (self, cao, apt_s, url_s, apt_t, url_t, db_man_s) :
        if cao.overwrite :
            apt_t.delete_database (url_t)
        db_man_t = self.DB_Man.create \
            (apt_t, url_t, db_man_s, cao.chunk_size, cao.legacy_lifter)
        if cao.verbose :
            self._print_info  (apt_s, url_s, db_man_s.db_meta_data, "    ")
            self._print_info  (apt_t, url_t, db_man_t.db_meta_data, "    ")
        db_man_t.ems.compact ()
        db_man_t.destroy ()
    # end def _do_migration

    def _handle_auth_mig (self, cao) :
        try :
            scope = self._handle_load (cao, journal_dir = None)
            mig   = pyk.pickle.dumps \
                (scope.Auth.Account.migration (), pyk.pickle_protocol)
            with open (cao.mig_auth_file, "wb") as f :
                sos.fchmod (f.fileno (), stat.S_IRUSR | stat.S_IWUSR)
                f.write (mig)
            if cao.verbose :
                print ("Wrote authorization objects to", cao.mig_auth_file)
            scope.commit      ()
            scope.ems.compact ()
            scope.destroy     ()
        except Exception as exc :
            print ("Saving auth-migration failed with exception\n   ", exc)
    # end def _handle_auth_mig

    def _handle_create (self, cao) :
        scope = self.scope \
            ( cao.db_url, cao.db_name
            , create      = True
            , verbose     = cao.verbose
            , engine_echo = cao.Engine_Echo
            , journal_dir = cao.keep_journal and cao.journal_dir
            )
        if cao.Auth_Migrate :
            self._read_auth_mig (cao, scope)
        scope.commit      ()
        scope.ems.compact ()
        scope.destroy     ()
    # end def _handle_create

    def _handle_delete (self, cao) :
        apt, url = self.app_type_and_url (cao.db_url, cao.db_name)
        if cao.verbose :
            print ("Deleting scope", apt, url.path)
        apt.delete_database (url)
    # end def _handle_delete

    def _handle_info (self, cao) :
        apt, url = self.app_type_and_url (cao.db_url, cao.db_name)
        db_man   = self.DB_Man.connect   (apt, url)
        self._print_info (apt, url, db_man.db_meta_data)
        db_man.destroy   ()
    # end def _handle_info

    def _handle_load (self, cao, url = None, journal_dir = undef) :
        if TFL.is_undefined (journal_dir) :
            journal_dir = cao.keep_journal and cao.journal_dir
        return self.scope \
            ( url or cao.db_url, cao.db_name
            , create      = False
            , engine_echo = cao.Engine_Echo
            , journal_dir = journal_dir
            )
    # end def _handle_load

    def _handle_load_auth_mig (self, cao, url = None, mig_auth_file = None) :
        try :
            scope = self._handle_load (cao, url)
            self._read_auth_mig       (cao, scope, mig_auth_file)
            scope.commit              ()
            scope.ems.compact         ()
            scope.destroy             ()
        except Exception as exc :
            print ("Loading auth-migration failed with exception\n   ", exc)
    # end def _handle_load_auth_mig

    def _handle_migrate (self, cao) :
        if cao.Auth_Migrate :
            self._handle_auth_mig (cao)
        if cao.verbose :
            print \
                ( "Migrating scope", _cleaned_url (cao.db_url), cao.db_name
                , "-->", _cleaned_url (cao.target_db_url)
                )
        apt_s, url_s = self.app_type_and_url (cao.db_url,        cao.db_name)
        apt_t, url_t = self.app_type_and_url (cao.target_db_url, cao.db_name)
        if cao.verbose :
            print \
                ( "   ", apt_s, apt_s.Url (url_s).path
                , "to",  apt_t, apt_t.Url (url_t).path
                )
        db_man_s = self.DB_Man.connect (apt_s, url_s)
        cmgr = self._cro_context if cao.readonly else TFL.Context.relaxed
        with cmgr (db_man_s, True) :
            self._do_migration (cao, apt_s, url_s, apt_t, url_t, db_man_s)
        db_man_s.destroy ()
        if cao.Auth_Migrate :
            self._handle_load_auth_mig (cao, cao.target_db_url)
    # end def _handle_migrate

    def _handle_readonly (self, cao) :
        apt, url = self.app_type_and_url (cao.db_url, cao.db_name)
        db_man   = self.DB_Man.connect   (apt, url)
        db_man.change_readonly (cao.state)
        if cao.verbose :
            self._print_info (apt, url, db_man.db_meta_data)
        db_man.destroy ()
    # end def _handle_readonly

    def _handle_script (self, cao) :
        scope = self._handle_load (cao) if cao.load else None
        globs = self._handle_script_globals (cao = cao, scope = scope)
        for script_path in cao.argv :
            local  = {}
            try :
                with open (script_path, "rb") as f :
                    exec (f.read (), globs, local)
            except Exception as exc :
                head = _T ("Script %s triggered exception" % (script_path, ))
                tail = "    \n".join (pyk.text_type (exc).split ("\n"))
                pyk.fprint (head)
                pyk.fprint ("   ", tail)
                raise SystemExit (1)
        if cao.commit :
            scope.commit      ()
            scope.ems.compact ()
            scope.destroy     ()
    # end def _handle_script

    def _handle_script_globals (self, cao, scope, ** kw) :
        return dict \
            ( kw
            , cao               = cao
            , cmd               = cao ### backwards compatibility
            , formatted         = formatted_repr
            , formatted_compact = formatted_repr_compact
            , MOM               = MOM
            , portable_repr     = portable_repr
            , Q                 = Q
            , scope             = scope
            , TFL               = TFL
            )
    # end def _handle_script_globals

    def _handle_shell (self, cao) :
        scope = self._handle_load (cao)
        globs = self._handle_script_globals (cao = cao, scope = scope)
        TFL.Environment.py_shell (globs)
    # end def _handle_shell

    def _handle_version_hash (self, cao) :
        both     = cao.database and cao.code
        verbose  = cao.verbose or both
        apt, url = self.app_type_and_url (cao.db_url, cao.db_name)
        dbv      = apt.db_version_hash
        fmt      = "%(dbv)s"
        if verbose :
            dbv  = portable_repr (dbv)
            fmt  = "%(kind)s = %(dbv)s"
        if cao.code or not cao.database :
            kind = "code_version_hash" if both else "dbv_hash"
            print (fmt % dict (kind = kind, dbv = dbv))
        if cao.database :
            try :
                db_man = self.DB_Man.connect (apt, url)
            except MOM.Error.Incompatible_DB_Version as exc :
                db_meta_data = exc.db_meta_data
            else :
                db_meta_data = db_man.db_meta_data
            dbv  = portable_repr (db_meta_data.dbv_hash)
            print (fmt % dict (kind = "database_version_hash", dbv = dbv))
    # end def _handle_version_hash

    def _load_scope (self, apt, url, journal_dir = None) :
        result = self.Scope.load (apt, url)
        if journal_dir :
            self._setup_journal (result, journal_dir)
        return result
    # end def _load_scope

    def _print_info (self, apt, url, dbmd, indent = "") :
        print ("%sInfo for database" % (indent, ), apt, _cleaned_url (str (url)))
        for k in sorted (dbmd) :
            v = dbmd [k]
            if k == "commits" and isinstance (v, list) :
                lv = len (v)
                if lv > 5 :
                    v = [v [0], "... %s commits..." % (lv, ), v [-1]]
            print ("%s%-12s : %s" % (indent, k, v))
        print ("%s%-12s : %s" % (indent, "dbv_hash/apt", apt.db_version_hash))
        print ()
    # end def _print_info

    def _read_auth_mig (self, cao, scope, mig_auth_file = None) :
        if mig_auth_file is None :
            mig_auth_file = cao.mig_auth_file
        try :
            f = open (sos.expanded_path (mig_auth_file), "rb")
        except IOError as exc :
            print \
                ( "Couldn't open", mig_auth_file, "due to exception\n    "
                , exc
                )
        else :
            with contextlib.closing (f) :
                cargo = f.read ()
            mig = pyk.pickle.loads (cargo)
            scope.Auth.Account.apply_migration (mig)
            if cao.verbose :
                print ("Loaded authorization objects from", mig_auth_file)
    # end def _read_auth_mig

    def _setup_journal (self, scope, journal_dir) :
        try :
            import _MOM._SCM.Journal
            journal = MOM.SCM.Journal (journal_dir, scope = scope)
        except Exception as exc :
            logging.exception \
                ("Error setting up journal of scope %s in %r"
                % (scope, journal_dir)
                )
    # end def _setup_journal

Command = MOM_Command # end class

### «text» ### start of documentation
__doc__ = r"""
.. class:: Command

  `MOM.Command` defines an extensible command for applications based on MOM.

  `MOM.Command` defines sub-commands for managing object models and the
  databases where they are stored, including:

  .. class:: Command._Auth_Mig_

    Sub-command ``auth_mig`` to create a migration of the authorization
    objects.

  .. class:: Command._Create_

    Sub-command ``create`` to create a new database specified by `-db_url`.

  .. class:: Command._Delete_

    Sub-command ``delete`` to delete the existing database specified by
    `-db_url`.

  .. class:: Command._Info_

    Sub-command ``info`` to display info about the database specified by
    `-db_url`.

  .. class:: Command._Load_Auth_Mig_

    Sub-command ``load_auth_mig`` to load a migration of the authorization
    objects.

  .. class:: Command._Migrate_

    Sub-command to migrate the database specified by `-db_url` to
    `-target_db_url`.

  .. class:: _Readonly_

    Sub-command to change readonly-state of database.

  .. class:: _Script_

    Sub-command to run one or more scripts.

    The scripts are run in a context providing the variables:

    .. data:: cao

      The :class:`~_TFL.CAO.CAO` instance of the command. One can access
      argument and option values via ``cao``, e.g., ``cao.target_db_url``.

    .. data:: Q

      The query expression generator. ``Q`` is an instance of
      :class:`~_MOM.Q_Exp.Base` and allows the specification of symbolic
      queries.

      For instance::

        Q.last_name == "tanzer"

      is a query expression that selects all objects with a value of "tanzer"
      for the attribute ``last_name``.

    .. data:: scope

      The scope connected to the currently open database, if any. ``scope`` is
      an instance of :class:`~_MOM.Scope.Scope`. Via ``scope``, one can query
      and change the object model.

      For instance::

        scope.PAP.Person.query (Q.last_name.STARTSWITH ("tan")).all ()

      returns all instances of the essential type ``PAP.Person`` whose
      ``last_name`` starts with the value "tan".

      To create a new instance of ``PAP.Person``, one can use::

        scope.PAP.Person \
            ( "Tanzer", "Christian"
            , lifetime = ("19590926", )
            , raw      = True
            )

      ``scope.etypes`` maps the names of essential types to the corresponding
      classes and can be used to find the names of all essential types.

  .. class:: _Shell_

    Sub-command to open an interactive python shell.

    The shell runs in the same context as described for :class:`_Script_`.

  .. class:: _Version_Hash_

    Sub-command to show version-hash of program or database or both.

  :class:`Command` provides ther API:

  .. attribute:: default_db_name

    The default name for a database of this application.

  .. attribute:: default_mig_auth_file

    Default name for auth migrations, used by :meth:`dynamic_defaults` to set
    `mig_auth_file`.

  .. method:: app_type

    Returns a derived app-type, an instance of
    :class:`~_MOM.App_Type._App_Type_D_`.

  .. method:: app_type_and_url

    Returns a derived app-type and database url.

  .. method:: dynamic_defaults

    Calculates dynamic default values for the options `db_name` and
    `mig_auth_file`, in addition to the dynamic defaults computed by the
    super-method :meth:`~_TFL.Command.Command.dynamic_defaults`.

  .. method:: scope

    Creates or loads a scope.

  The final application specific class derived from :class:`Command` need to
  define the class variables

  .. attribute:: ANS

    Refers to the package namespace defining the application specific object
    model.

  .. attribute:: nick

    The nick name of the application.

  .. attribute:: _default_db_name

    The default name for a database of this application (used by the property
    computing :attr:`default_db_name`).



.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

"""

if __name__ != "__main__" :
    MOM._Export ("Command", "_Sub_Command_")
### __END__ MOM.Command
