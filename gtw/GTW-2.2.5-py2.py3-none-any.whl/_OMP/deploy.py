# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.deploy
#
# Purpose
#    Provide an extendable Command for the deployment of applications based
#    on GTW.OMP
#
# Revision Dates
#    23-May-2012 (CT) Creation
#    24-May-2012 (CT) Factor `_app_cmd`
#    24-May-2012 (CT) Set correct `PYTHONPATH` for `Active` and `Passive`
#    24-May-2012 (CT) Use `migrate` instead of `@mig1`, `@mig2`; print
#    25-May-2012 (CT) Fix `db_url` in `migrate` (needs `///`)
#    31-May-2012 (CT) Change default of `_Migrate_.db_name` to `/tmp/migrate`
#    31-May-2012 (CT) Use `cwd` in `_handle_migrate` (again!)
#     1-Jun-2012 (CT) Factor `_app_call` from `_handle_migrate`
#     1-Sep-2014 (CT) Use `pjoin`, not `plumbum.path` operator `/`
#    15-Jun-2016 (CT) Rename handler argument `cmd` to `cao`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function#, unicode_literals

from   _GTW                   import GTW
from   _MOM                   import MOM
from   _TFL                   import TFL

from   _TFL                   import sos

import _GTW.deploy

pjoin = sos.path.join

class _GTW_OMP_Sub_Command_ (GTW.deploy._Sub_Command_) :

    _rn_prefix = "_GTW_OMP"

_Sub_Command_ = _GTW_OMP_Sub_Command_ # end class

class GTW_OMP_Command (GTW.deploy.Command) :
    """Manage deployment applications based on GTW.OMP."""

    _rn_prefix              = "GTW_OMP_"

    class _GTW_OMP_Babel_ (_Sub_Command_, GTW.deploy.Command._Babel_) :

        _package_dirs           = \
            [ "_MOM"
            , "_GTW"
            , "_GTW/_OMP/_Auth"
            , "_GTW/_OMP/_PAP"
            , "_GTW/_OMP/_SWP"
            , "_GTW/_OMP/_SRM"
            , "_GTW/_OMP/_EVT"
            ]

    _Babel_ = _GTW_OMP_Babel_ # end class

    class _GTW_OMP_Migrate_ (_Sub_Command_) :
        """Migrate database from `active` or file to file or `passive`."""

        _opts                   = \
            ( "-Active:B?Migrate database from `active_name`"
            , "-Passive:B?Migrate database to `passive_name`"
            , "-db_name:Q=/tmp/migration?Name of migration database"
            )

    _Migrate_ = _GTW_OMP_Migrate_ # end class

    def _handle_migrate (self, cao) :
        P      = self._P (cao)
        db_url = "hps:///" + cao.db_name
        def _do (version, args) :
            app  = self._app_cmd (cao, P, version)
            args = ("migrate", "-overwrite") + args
            with self.pbl.env (PYTHONPATH = self._python_path (P, version)) :
                self._app_call \
                    (cao, P, app, args, pjoin (P.prefix, version, cao.app_dir))
        if cao.Active :
            _do (P.active,  ("-target_db_url", db_url, "-readonly"))
        if cao.Passive :
            _do (P.passive, ("-db_url",        db_url))
    # end def _handle_migrate

Command = GTW_OMP_Command # end class

if __name__ != "__main__" :
    GTW.OMP._Export_Module ()
### __END__ GTW.OMP.deploy
