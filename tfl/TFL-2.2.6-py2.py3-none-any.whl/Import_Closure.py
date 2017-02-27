# -*- coding: utf-8 -*-
# Copyright (C) 1998-2015 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Import_Closure
#
# Purpose
#    Find all files imported by a given python module residing in a list of
#    user-specified directories (i.e., excluding standard Python modules)
#
# Revision Dates
#    25-Nov-1998 (CT)  Creation
#    26-Nov-1998 (CT)  `import_pat` corrected
#     7-Sep-2000 (CT)  `expanded_path` applied
#    12-Apr-2001 (CT)  `import_pat` changed ("[^#]*?" --> "^\s*")
#    12-Apr-2001 (CT)  `-ignore` added
#     8-May-2001 (CT)  Support for package imports added
#    18-May-2001 (CT)  Use `_find_import` everywhere (factoring of
#                      `_find_import` finally completed)
#     2-Jul-2001 (CT)  `pkg_namespace_import_pat` added and used
#     3-Jul-2001 (CT)  `-Pathsep` added
#     3-Jul-2001 (CT)  `pkg_namespace_pat` and `pkg_ns_dict` added and used
#    17-Jul-2001 (CT)  Leading `_` removed from namespace-packages
#    17-Jul-2001 (CT)  `pkg_namespace_pat` renamed to `pkg_namespace_def_pat`
#    17-Jul-2001 (CT)  Global functions replaced by class Import_Finder
#    17-Jul-2001 (CT)  Support for implicit imports from package namespaces
#                      added
#    28-Aug-2001 (MG)  `pkg_namespace_def_pat` extended (match `From_Import`)
#    28-Aug-2001 (MG)  Pass `pkg_path` for recursive calls of `_find_import`
#    13-Nov-2001 (CT)  Adapted to nested packages
#    11-Dec-2001 (CT)  `_import_module` factored
#    11-Dec-2001 (CT)  `prefix` added `path_of` (and `_path_of` factored)
#    11-Dec-2001 (CT)  `modules` handling added to `_import_module_from_pkg`
#                      (along with adding `modules` group to
#                      `pkg_namespace_import_pat` and `pkg_namespace_use_pat`)
#    12-Dec-2001 (CT)  Argument `pkg_import_path` removed from `_find_import*`
#    12-Dec-2001 (CT)  `_import_module_from_pkg` fixed (uses `_import_module`
#                      now and computes `imported` using `pkg_ns_dict [p]`
#                      instead of `p`)
#    12-Dec-2001 (CT)  `pkg_ns_dict` replaced by `pkg_ns_adict` and
#                      `pkg_ns_rdict`
#    12-Dec-2001 (CT)  Argument `rel_name` added to `_find_imports`
#    14-Mar-2002 (CT)  `Package_Namespace` removed
#    14-Mar-2002 (CT)  Nested packages supported properly
#    10-Jul-2002 (MG)  Error in `path_of` corrected (use `prefix` as well)
#    24-Feb-2004 (CT)  Modernizations (e.g., usages of `string` module removed)
#    24-Feb-2004 (CT)  `file_dict` added, `_add` factored and changed as to
#                      not put the same file twice into `import_dict`
#                      (happened for TFL.Generator, because the doc-test
#                      imports `Generator` without package prefix)
#     9-Mar-2004 (CT)  `_add` changed to write mixed relative and absolute
#                      imports to sys.stderr
#     8-Jun-2004 (CT)  `Py_Module` added and used as value in `import_dict`
#     8-Jun-2004 (CT)  `seen` added to avoid multiple lookups of irrelevant
#                      modules
#     8-Jun-2004 (CT)  Debug code changed and extended
#     8-Jun-2004 (CT)  Methods sorted alphabetically
#     8-Jun-2004 (CT)  `__sub__` added to `Import_Finder` (and the `-Diff`
#                      option for testing it)
#     9-Jun-2004 (CT)  s/Py_Module/P_M/
#     9-Jun-2004 (CT)  `P_P` added
#     9-Jun-2004 (CT)  `path_of` changed to return `P_M` instances instead of
#                      tuples
#     9-Jun-2004 (CT)  `pkg_dict` and `tlp_dict` added
#     9-Jun-2004 (CT)  `__sub__` and `__init__` changed so that `__sub__`
#                      returns another instance of `Import_Finder` instead of
#                      a `Record`
#    17-Jun-2004 (CT)  Options `-files`, `-packages`, and `-toplevels` added
#    17-Jun-2004 (CT)  `__sub__` corrected (call `_add` instead of `add`)
#    17-Jun-2004 (CT)  `__sub__` changed to set `pkg_dict` and `tlp_dict` of
#                      result correctly
#    17-Jun-2004 (CT)  s/Import_Finder/Import_Closure/g
#    17-Jun-2004 (CT)  Debug code removed to make code clearer
#    18-Jun-2004 (CT)  s/import_dict/pym_dict/
#    18-Jun-2004 (CT)  Replaced `Import_Closure` attributes `file_name`,
#                      `base_name`, and `path_name` by a single attribute
#                      `root_pym`
#    18-Jun-2004 (CT)  `_import_root` factored from `__init__` and changed so
#                      that `rel_name` and `pkg` are right
#    18-Jun-2004 (CT)  `level` added to `P_M` and used to determine
#                      `is_toplevel`
#    19-Jun-2004 (CT)  s/from_text/new/
#    19-Jun-2004 (CT)  `remove` added
#    19-Jun-2004 (CT)  `__sub__` changed to `_add` packages to delta closure
#                      if some of their modules are in the delta (up to now,
#                      these were only inserted into `pkg_dict` and `tlp_dict`)
#    20-Jun-2004 (CT)  `base_name` added to `P_M`
#    21-Jun-2004 (CT)  `base_path` added and semantics of `base_name` changed
#    22-Jun-2004 (CT)  Creation (factored from find_import_closure.py)
#    22-Jun-2004 (CT)  `as_code` changed to package the `pyms` in a list to
#                      avoid `more than 255 arguments` exception from `new`
#    22-Jun-2004 (CT)  `new` changed to expect list for `pyms` instead of
#                      rest-arguments
#     7-Oct-2004 (CT)  `__sub__` changed to include parent packages into
#                      result (otherwise result contains X.Y.Z, but not X.Y,
#                      if difference doesn't contain any module of X.Y)
#    25-Mar-2005 (MG)  Import of `Filename` changed
#     5-Jul-2006 (CED) `__sub__` adds parent packages recursively
#    11-Jul-2006 (PGO) `script_code` flag added
#    20-Jul-2006 (PGO) `__sub__` doesn`t add parent packages any longer (moved
#                      to TFL.Plugin_Packager)
#    14-Aug-2006 (CED) `Derived_PNS_Finder` added and used
#    16-Aug-2006 (CED) `_path_of` fixed
#    16-Aug-2006 (MSF) `_path_of` really fixed
#     6-Nov-2006 (CED) `pkg_chain` added
#    27-Sep-2007 (CED) Added support for derived PNS import of root file
#    18-Nov-2009 (CT)  3-compatibility
#    16-Jun-2013 (CT)  Use `TFL.CAO`, not `TFL.Command_Line`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _TFL                       import TFL

from   _TFL.Composition           import Composition
from   _TFL.Filename              import Filename
from   _TFL.Importers             import DPN_Importer, DERIVED_PNS_TOKEN
from   _TFL.Regexp                import Regexp, re
from   _TFL.predicate             import *
from   _TFL.pyk                   import pyk
from   _TFL._Meta.totally_ordered import totally_ordered

import _TFL._Meta.Object
import _TFL.CAO
import _TFL.sos

import sys

@totally_ordered
class P_M (TFL.Meta.Object) :
    """Encapsulate a python module found by Import_Closure"""

    is_package = False

    _rel_split  = lambda s : s.rel_name.split  (TFL.sos.sep) [:-1]
    _path_split = lambda s : s.path_name.split (TFL.sos.sep) [:-1]
    _pkg_split  = lambda s : s.pkg.split       (".")

    def __init__ (self, rel_name, path_name, pkg) :
        self.rel_name     = rel_name
        self.path_name    = path_name
        _, self.base_path = TFL.sos.path.split    (path_name)
        self.base_name, _ = TFL.sos.path.splitext (self.base_path)
        self.pkg          = pkg
        self.level        = pkg.count (".")
    # end def __init__

    def pkg_chain (self) :
        for rel_name, path_name, pkg in zip \
            ( * map
              ( Composition (list, Composition (reversed, head_slices))
              , ( self._rel_split  ()
                , self._path_split ()
                , self._pkg_split  ()
                )
              )
            ) :
            yield \
               ( P_P
                 ( TFL.sos.sep.join (rel_name)
                 , TFL.sos.sep.join (path_name + ["__init__.py"])
                 , ".".join         (pkg)
                 )
               )
    # end def pkg_chain

    def __eq__ (self, rhs) :
        try :
            rhs = rhs.path_name
        except AttributeError :
            pass
        return self.path_name == rhs
    # end def __eq__

    def __hash__ (self) :
        return hash (self.path_name)
    # end def __hash__

    def __lt__ (self, rhs) :
        try :
            rhs = rhs.path_name
        except AttributeError :
            pass
        return self.path_name < rhs
    # end def __lt__

    def __repr__ (self) :
        return "%s (%r, %r, %r)" % \
            (self.__class__.__name__, self.rel_name, self.path_name, self.pkg)
    # end def __repr__

    def __str__ (self) :
        return self.path_name
    # end def __str__

# end class P_M

class P_P (P_M) :
    """Encapsulate a python package found by Import_Closure"""

    is_package   = True
    is_toplevel  = property (lambda s : s.level == 0)

    _path_split = lambda s : s.path_name.split (TFL.sos.sep) [:-2]
    _pkg_split  = lambda s : s.pkg.split       (".")         [:-1]
# end class P_P

class Derived_PNS_Finder (TFL.Meta.Object) :
    d_pns_pat = Regexp \
        ( r"^(?P<base_name>\w+) *= *Derived_Package_Namespace *"
          r"\( *parent *= *(?P<parent>(?:\w+\.)*\w+) *\)"
        )
    exp_pat   = Regexp \
        ( r"^(?P<path_name>(?:\w+\.)*\w+)\._Export *"
          r"\( *\"(?P<base_name>\w+)\" *\)"
        )

    def __init__ (self, import_path = (".", )) :
        res = []
        for p in import_path :
            TFL.sos.walk (p, self.dir_visitor, res)
        self.tokens = self._build_closure (res)
    # end def __init__

    def dir_visitor (self, res, dirname, names) :
        res.extend \
            (   self._build_pns_token (TFL.sos.path.join (dirname, n))
            for n in names
            if  n == "__init__.py"
            )
    # end def dir_visitor

    def _build_closure (self, res) :
        dct    = dict (filter (None, res))
        result = {}
        for key, val in pyk.iteritems (dct) :
            token = [DERIVED_PNS_TOKEN, key]
            while val :
                token.append (val)
                val = dct.get (val)
            result ["_%s" % key.replace (".","._")] = ",_".join (token).replace (".", "._")
        return result
    # end def _build_closure

    def _build_pns_token (self, fn) :
        f = file (fn, "r")
        try :
            for line in f :
                pns = self.d_pns_pat.match (line)
                if pns :
                    dns_dict = pns.groupdict ()
                    assert "_" not in dns_dict ["parent"], dns_dict ["parent"]
                    break
            else :
                return
            for line in f : ### consecutive lines only
                exp = self.exp_pat.match (line)
                if exp :
                    exp_dict = exp.groupdict ()
                    bname    = exp_dict ["base_name"]
                    assert \
                        dns_dict ["base_name"] == bname, \
                        ( "Inconsistent base_names (%s <-> %s) found in %s"
                        % (dns_dict ["base_name"], bname, fn)
                        )
                    absname  = "%s.%s" % (exp_dict ["path_name"], bname)
                    return (absname, dns_dict ["parent"])
            else :
                return (dns_dict ["base_name"], dns_dict ["parent"])
        finally :
            f.close ()
    # end def _build_pns_token

# end class Derived_Package_Namespace

class Import_Closure :
    """Find all imports from a given python module"""

    import_pat = Regexp \
        ( r"^\s* (?: from | import) \s* "
          r"(?P<imported> [_A-Za-z0-9]+)"
          r"(?: \. (?P<modules> [_A-Za-z0-9.]+))?"
        , re.X
        )

    script_pat = Regexp \
        ( """^if \s+ __name__ \s* == \s* "__[a-z]+__" \s* : $"""
        , re.X
        )

    def __init__ \
        ( self, file_name = None, import_path = ("./", ), ignore = None
        , debug = False, script_code = False
        ) :
        self.import_path     = tuple (import_path)
        self.pym_dict        = {} ### rel-name-sans-extension --> P_M
        self.file_dict       = {} ### path --> rel-name-sans-extension
        self.pkg_dict        = {}
        self.tlp_dict        = {}
        self.seen            = {}
        self.derived_modules = {}
        self.d_pns_chains    = Derived_PNS_Finder (self.import_path).tokens
        self.ignore          = ignore or {}
        self.debug           = debug
        self.script_code     = script_code
        self.root_pym        = None
        if file_name :
            self.root_pym = pym = self._import_root (file_name)
            if not pym :
                print ("Where is %s?" % (file_name, ))
                print ("...didn't find it in %s" % (self.import_path, ))
                raise ValueError
    # end def __init__

    def as_code (self) :
        pyps = self.pkg_dict.values ()
        pyms = [m for m in self.pym_dict.values ()
                  if not (m.is_package or m == self.root_pym)
               ]
        return "\n    ".join \
            ( [ "%s.new \\"   % (self.__class__.__name__, )
              , "( %r"        % (self.root_pym, )
              , ", %r"        % (self.import_path, )
              , ", %r"        % (self.ignore, )
              , ", ["
              ]
            + sorted
              (["%s   %r" % ([" ", ","] [i>0], m) for i,m in enumerate (pyps)])
            + sorted ([",   %r" % (m, ) for m in pyms])
            + [ "]"
              , ")"
              ]
            )
    # end def as_code

    def _add (self, pym) :
        if pym.path_name not in self.file_dict :
            self.pym_dict  [pym.rel_name]  = pym
            self.file_dict [pym.path_name] = pym.rel_name
            if pym.is_package :
                self.pkg_dict [pym.pkg] = pym
                if pym.is_toplevel :
                    self.tlp_dict [pym.pkg] = pym
            return True
        else :
            if self.debug :
                print \
                    ( "%s is imported absolutely and relatively: `%s` vs. `%s`"
                    % ( pym.path_name
                      , self.file_dict [pym.path_name], pym.rel_name
                      )
                    , file = sys.stderr
                    )
    # end def _add

    def _find_import (self, imported, prefix = "") :
        if imported in self.seen :
            return True
        else :
            self.seen [imported] = True
            pym = self.path_of (imported, prefix)
            if pym :
                file = Filename (pym.path_name, absolute = True)
                if file.base not in self.ignore :
                    if self._add (pym) :
                        self._find_imports (pym.path_name, imported, pym.pkg)
                        return True
    # end def _find_import

    def _find_imports (self, file_name, rel_name, prefix = "") :
        file = open (file_name, "r")
        try :
            import_pat = self.import_pat
            for line in file :
                if (not self.script_code) and self.script_pat.match (line) :
                    break
                if import_pat.match (line) :
                    imported = import_pat.imported
                    self._import_module \
                        (imported, import_pat.last_match, prefix)
        finally :
            file.close ()
    # end def _find_imports

    def _import_module (self, imported, match, prefix) :
        self._find_import (imported, prefix)
        try :
            modules = match.group ("modules")
        except (IndexError, AttributeError) :
            pass
        else :
            package = self.pym_dict.get (imported)
            if modules and package :
                for m in modules.split (".") :
                    imported = TFL.sos.path.join (imported, m)
                    if not self._find_import (imported, prefix) :
                        break
    # end def _import_module

    def _import_root (self, file_name) :
        if file_name.startswith (TFL.sos.path.sep) :
            for dir in self.import_path :
                if file_name.startswith (dir) :
                    file_name = file_name [len (dir) + 1:]
                    break
        base, _ = TFL.sos.path.splitext (file_name)
        name    = base.replace (TFL.sos.path.sep, ".")
        line    = "import %s" % (name, )
        match   = self.import_pat.match (line)
        if match :
            self._import_module (match.group ("imported"), match, "")
            if name in self.derived_modules :
                base = self.derived_modules [name].replace (".", TFL.sos.path.sep)
            return self.pym_dict.get (base)
        else :
            print (name, "doesn't match import pattern")
    # end def _import_root

    def new (cls, root_pym, import_path, ignore, pyms = ()) :
        result           = cls (import_path = import_path, ignore = ignore)
        result.root_pym  = root_pym
        result._add (root_pym)
        for pym in pyms :
            result._add (pym)
        return result
    new = classmethod (new)

    def path_of (self, py_name, prefix = "") :
        """Return the full path of `py_name` in the list of directories
           `import_path` or `None`.
        """
        if prefix :
            py_names = (py_name, TFL.sos.path.join (prefix, py_name))
        else :
            py_names = (py_name, )
        for py_name in py_names :
            for imp_dir in self.import_path :
                result = self._path_of (imp_dir, py_name)
                if result :
                    return result
    # end def path_of

    def _path_of (self, dir, py_name) :
        b_name = TFL.sos.path.join (dir, py_name)
        m_name = b_name + ".py"
        p_name = TFL.sos.path.join (b_name, "__init__.py")
        m_prefix = ".".join (py_name.split (TFL.sos.sep) [:-1])
        if TFL.sos.path.isfile (m_name) :
            return P_M (py_name, m_name, m_prefix)
        if TFL.sos.path.isfile (p_name) :
            prefix = ".".join (py_name.split (TFL.sos.sep))
            return P_P (py_name, p_name, prefix)
        if m_prefix in self.d_pns_chains :
            fullmodule = py_name.replace (TFL.sos.path.sep, ".")
            try :
                i = DPN_Importer (self.d_pns_chains [m_prefix])
                i.find_module (fullmodule)
            except ImportError :
                pass
            else :
                mod, fname = i.get_filename (fullmodule)
                if TFL.sos.path.isdir (fname) :
                    return
                ml         = mod.split (".")
                pkg        = ".".join  (ml [:-1])
                result = P_M (TFL.sos.sep.join (ml), fname, pkg)
                assert self.derived_modules.get (fullmodule, mod) == mod
                self.derived_modules [fullmodule] = mod
                return result
    # end def _path_of

    def remove (self, pym) :
        """Remove `pym` from import closure"""
        if isinstance (pym, str) :
            pym = self.pym_dict [pym]
        del self.pym_dict [pym.rel_name]
        if pym.pkg in self.pkg_dict :
            del self.pkg_dict [pym.pkg]
        if pym.pkg in self.tlp_dict :
            del self.tlp_dict [pym.pkg]
    # end def remove

    def __sub__ (self, rhs) :
        result = self.__class__.new \
            (self.root_pym, self.import_path, self.ignore)
        for k, pym in pyk.iteritems (self.pym_dict) :
            if k not in rhs.pym_dict :
                result._add (pym)
                pn = pym.pkg
                if pn in self.pkg_dict and pn not in result.pkg_dict :
                    result._add (self.pkg_dict [pn])
        return result
    # end def __sub__

# end class Import_Closure

def _main (cmd) :
    import_path = map \
        (TFL.sos.expanded_path, cmd.import_path.split (cmd.Pathsep))
    ignore      = dict_from_list (cmd.ignore)
    out_opts    = sum \
        (   bool (o) for o
        in (cmd.as_code, cmd.files, cmd.packages, cmd.toplevels)
        )
    result = finder = Import_Closure \
        ( file_name   = cmd.python_module
        , import_path = import_path
        , ignore      = ignore
        , debug       = cmd.debug
        , script_code = cmd.script_code
        )
    if cmd.Diff :
        result = finder - Import_Closure \
            ( file_name   = cmd.Diff
            , import_path = import_path
            , ignore      = ignore
            , debug       = cmd.debug
            , script_code = cmd.script_code
            )
    sep = cmd.separator
    if sep == r"\n" :
        sep = "\n"
    if cmd.as_code :
        print (result.as_code ())
    if cmd.toplevels :
        print (sep.join (sorted (m.pkg for m in result.tlp_dict.values ())))
    if cmd.packages :
        print (sep.join (sorted (m.pkg for m in result.pkg_dict.values ())))
    if cmd.files or not out_opts :
        print (sep.join (sorted (str (m) for m in result.pym_dict.values ())))
# end def _main

_Command = TFL.CAO.Cmd \
    ( handler       = _main
    , args          =
        ( "python_module:S"
        , "import_path:P=./"
        , "separator:S= "
        )
    , opts          =
        ( "-as_code:B?Print import closure as executable python code"
        , "-debug:I=0"
        , "-Diff:S"
              "?Name of python_module which import closure gets subtracted"
        , "-files:B?Show all files in import closure"
        , "-ignore:S,=U_Test?Ignore modules specified"
        , "-packages:B?Show all packages in import closure"
        , "-Pathsep:S=:?Path separator used by `import_path`"
        , "-toplevels:B?Show all toplevel packages in import closure"
        , "-script_code:B?Add imports following the "
          "__name__ == '__main__' line"
        )
    , min_args      = 1
    , max_args      = 3
    )

if __name__ != "__main__":
    TFL._Export ("Import_Closure", "Derived_PNS_Finder")
else :
    _Command ()
### __END__ TFL.Import_Closure
