# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.package_imports
#
# Purpose
#    Find all external imports of a package
#
# Revision Dates
#    11-Oct-2016 (CT) Creation
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _TFL                import TFL

from   _TFL.Regexp         import Regexp, re
from   _TFL.pyk            import pyk
from   _TFL                import sos
from   _TFL.subdirs        import subdirs_transitive

import _TFL.CAO

ignore_imports = set (("__builtin__", "__future__"))
import_pat     = Regexp \
    ( r"^\s* (?: from | import)\s+ "
      r"(?P<imported> [_A-Za-z0-9]+)"
      r"(?: \. (?P<modules> [_A-Za-z0-9.]+))?"
    , re.X | re.MULTILINE
    )
pns_pat        = Regexp (r"^_[A-Z]\w+$")

def external_imports (pkg_name, pkg_path, ignore_imports = ignore_imports) :
    """Return the set of external imports of package at `pkg_path`"""
    result = set ()
    for m in sos.listdir_ext (pkg_path, ".py") :
        result.update (external_module_imports (pkg_name, m, ignore_imports))
    for s in subdirs_transitive (pkg_path) :
        result.update (external_imports (pkg_name, s, ignore_imports))
    return result
# end def external_imports

def external_module_imports \
        (pkg_name, mod_path, ignore_imports = ignore_imports) :
    """Return the set of external imports of module at `mod_path`."""
    result = set ()
    with open (mod_path, "rb") as f :
        code = pyk.decoded (f.read (), pyk.user_config.input_encoding, "utf-8")
        for match in import_pat.search_iter (code) :
            i = match.group ("imported")
            if not i.startswith (pkg_name) and i not in ignore_imports :
                result.add (i)
    return result
# end def external_module_imports

def package_namespace_imports (imports) :
    """Return elements of `imports` that are Package_Namespaces"""
    return set (i for i in imports if pns_pat.match (i))
# end def package_namespace_imports

def site_package_imports (imports) :
    """Return elements of `imports` that are installed in site-packages"""
    def gen (imports) :
        for i in imports :
            try :
                m = __import__ (i)
            except Exception :
                pass
            else :
                mp = getattr (m, "__file__", None)
                if mp is not None :
                    if "/site-packages/" in mp :
                        yield i
    return set (gen (imports))
# end def site_package_imports

def _main (cmd) :
    """Find all external imports of a package"""
    nop = sos.expanded_path (cmd.package)
    if sos.path.exists (nop) :
        if not sos.path.isdir (nop) :
            nop = sos.path.dirname (nop)
        pkg_path    = sos.path.abspath (nop)
        _, pkg_name = sos.path.split   (pkg_path)
    else :
        try :
            pkg = __import__ (nop)
        except Exception as exc :
            print \
                ( "%s is not the name or path of a proper python package\n  %s"
                % (nop, exc)
                )
            raise SystemExit (9)
        pkg_name = pkg.__name__
        pkg_path = sos.path.dirname (pkg.__file__)
    imports = external_imports (pkg_name, pkg_path)
    result  = set ()
    if cmd.Package_Namespaces :
        result.update (package_namespace_imports (imports))
    if cmd.Site_Packages :
        result.update (site_package_imports (imports))
    if not (cmd.Package_Namespaces or cmd.Site_Packages) :
        result = imports
    print (* sorted (result))
# end def _main

_Command = TFL.CAO.Cmd \
    ( handler       = _main
    , args          =
        ( "package:S?Name or path of package"
        ,
        )
    , opts          =
        ( "-Package_Namespaces:B"
            "?Restrict imports shown to top-level package namespaces"
        , "-Site_Packages:B"
            "?Restrict imports shown to those located in site-packages"
        , TFL.CAO.Opt.Input_Encoding
            ( description   = "Module encoding"
            )
        )
    , min_args      = 1
    , max_args      = 1
    )

if __name__ != "__main__" :
    TFL._Export_Module ()
else :
    _Command ()
### __END__ TFL.package_imports
