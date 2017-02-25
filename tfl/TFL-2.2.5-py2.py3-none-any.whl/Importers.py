# -*- coding: utf-8 -*-
# Copyright (C) 2006-2014 Christian Eder, Philipp Gortan <{ced,pgo}@tttech.com>
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Importers
#
# Purpose
#    Provide Custom import hooks
#
# Revision Dates
#    25-Jul-2006 (PGO) Creation
#    28-Jul-2006 (PGO) Creation continued
#    31-Jul-2006 (PGO) `register` added, `_find_module` for builtin import fixed
#     3-Aug-2006 (PGO) `_find_module` for TTP-View fixed
#     4-Aug-2006 (PGO) `load_module` fixed if `realmodule` was already imported
#     7-Aug-2006 (PGO) `_get_zipimporter` added
#     8-Aug-2006 (PGO) Filter sys.path to contain files only
#    10-Aug-2006 (PGO) `_find_module` doesn't rely on package being in
#                      sys.modules any more
#    14-Aug-2006 (CED) `get_filename` added
#    25-Aug-2006 (CED) Support for multiple lib/pythons added :-), fixed
#     6-Nov-2006 (CED) `Plugin_Importer` added
#    10-Nov-2006 (CED) Use path hooks for Plugin_Importer
#    15-Nov-2006 (CED) `register_at_sys_path` added
#    14-Jun-2007 (CED) [24566] `load_module` resets package's __path__
#    18-Jun-2007 (CT)  `find_module` changed back to be 2.4 compatible
#    24-Sep-2009 (CT)  `_load_module` changed to not rely on tuple unpacking
#                      in the argument list (3.x doesn't support that anymore)
#    11-Nov-2009 (CT)  Use `print` as function, not statement (3-compatibility)
#    16-Jun-2010 (CT)  s/print/pyk.fprint/
#     8-Aug-2012 (CT) Use `parent._._module_name`, not `parent._._name`
#    23-May-2013 (CT) Use `TFL.Meta.BaM` for Python-3 compatibility
#    ««revision-date»»···
#--

from   _TFL              import TFL
from   _TFL.pyk          import pyk

import _TFL._Meta.M_Class

import imp
import os
import sys
import zipimport

DERIVED_PNS_TOKEN = "?Derived"
PIM_TOKEN         = "?Plugin"

class M_DPN_Importer (type) :
    """Metaclass for derived package namespace importer.
       When called with a path item that marks derived package namespaces,
       it returns the appropriate DPN importer.
    """

    def __call__ (cls, path) :
        if path.startswith (DERIVED_PNS_TOKEN) :
            token_lst = path.split (",")
            name      = token_lst [1 ]
            pns_chain = token_lst [2:]
            i         = \
                (   getattr (sys, "frozen", False)
                and _DPN_ZipImporter_ or _DPN_Builtin_Importer_
                )
            return super (M_DPN_Importer, i).__call__ (name, pns_chain)
        else :
            raise ImportError ### not derived - pass on to next importer
    # end def __call__

# end class M_DPN_Importer

class DPN_Importer (TFL.Meta.BaM (object, metaclass = M_DPN_Importer)) :
    """Implements an import hook for derived package namesapces,
       according to PEP 302. For the derived and all parent namespaces,
       try to find the module.
    """

    def __init__ (self, name, pns_chain) :
        self.name      = name
        self.pns_chain = pns_chain
        self._cache    = {}
    # end def __init__

    def find_module (self, fullmodule, path = None) :
        assert not path
        for pns in self.pns_chain :
            cand = fullmodule.replace (self.name, pns, 1)
            i    = self._find_module (cand, fullmodule)
            if i :
                return i
        raise ImportError
    # end def find_module

    def get_filename (self, module) :
        res = self._cache.get (module)
        if res :
            return res [0], res [1] [1]
    # end def get_filename

    def load_module (self, fullmodule) :
        realmodule, finder_info = self._cache.pop (fullmodule)
        if realmodule in sys.modules :
            mod = sys.modules [realmodule]
        else :
            mod = self._load_module (realmodule, finder_info)
        mod.__loader__ = self
        sys.modules [fullmodule] = mod
        return mod
    # end def load_module

    @classmethod
    def register (cls, mod, name, parent) :
        if not hasattr (mod, "__path__") :
            return ### a Package_Namespace is not always a package *argh*
        token = [DERIVED_PNS_TOKEN, name]
        while parent :
            token.append (parent._._module_name)
            parent = getattr (parent, "_parent", None)
        mod.__path__.append (",".join (token))
    # end def register

    def __repr__ (self) :
        return \
            ( "<%s for %s p=[%s]>"
            % (self.__class__.__name__, self.name, " ".join (self.pns_chain))
            )
    # end def __repr__

# end class DPN_Importer

class _DPN_Builtin_Importer_ (DPN_Importer) :
    """Use the builtin import mechanism (as exposed by the imp module) for
       importing.
    """
    _path = sys.path

    def _find_module (self, cand, fullmodule) :
        pkg, mod = cand.rsplit (".", 1)
        for p in self._path :
            path     = [os.path.join (p, * pkg.split ("."))]
            try :
                res = imp.find_module (mod, path)
                break
            except ImportError :
                continue
        else :
            return
        self._cache [fullmodule] = (cand, res)
        return self
    # end def _find_module

    def _load_module (self, realmodule, res) :
        return imp.load_module (realmodule, * res)
    # end def _load_module

# end class _DPN_Builtin_Importer_

class _DPN_ZipImporter_ (DPN_Importer) :
    """Use the executable itself in conjunction with Python's zipimporter
       for importing.
    """

    _path = list (p for p in sys.path if os.path.isfile (p))

    def _get_zipimporter (self, zip_path) :
        zi = sys.path_importer_cache.get (zip_path)
        if not zi :
            try :
                zi = zipimport.zipimporter (zip_path)
            except ImportError :
                pass
        return zi
    # end def _get_zipimporter

    def _find_module (self, cand, fullmodule) :
        cand_lst = cand.split (".")
        for p in self._path :
            zip_path = os.sep.join ([p] + cand_lst [:-1])
            zi = self._get_zipimporter (zip_path)
            if zi :
                break
        else :
            return
        mod = cand_lst [-1]
        res = zi.find_module (mod)
        if res :
            self._cache [fullmodule] = (cand, (mod, res))
            return self
    # end def _find_module

    def _load_module (self, realmodule, res) :
        (module, loader) = res
        mod = loader.load_module (module)
        sys.modules [realmodule] = mod
        return mod
    # end def _load_module

# end class _DPN_ZipImporter_

class Plugin_Importer (object) :

    plain_to_version = {}
    tag_dict         = {}
    pending          = {}

    @classmethod
    def new_plugin (cls, name) :
        from   _TFL.Environment    import script_path, frozen
        from   _TFL.Filename       import Filename
        from   _TFL.import_module  import import_module
        if frozen () :
            plain_name             = name.rsplit ("_", 3) [0] ### XXX
            cls.plain_to_version [plain_name] = name
            pkg_name               = "_Plugins._%s" % (plain_name, )
            tooldir                = script_path ()
            plugin_dir             = os.path.join (tooldir, "_Plugins")
            if not hasattr (cls, plugin_dir) :
                cls.plugin_dir = plugin_dir
            directory              = os.path.join (plugin_dir, "_%s" % name)
            cls._run_setup         (directory, name)
            module                 = import_module (pkg_name)
            return directory, module, plain_name
        else :
            pkg_name               = "_Plugins._%s" % (name, )
            module                 = import_module (pkg_name)
            directory              = Filename (module.__file__).directory
            return directory, module, name
    # end def new_plugin

    @classmethod
    def register (cls, plugin_name, pns_name) :
        if pns_name in sys.modules :
            path_list = sys.modules [pns_name].__path__
            cls._register (path_list, plugin_name)
        else :
            cls.pending.setdefault (pns_name, []).append (plugin_name)
    # end def register

    @classmethod
    def register_at_sys_path (cls, plugin_name) :
        cls._register (sys.path, plugin_name)
    # end def register_at_sys_path

    @classmethod
    def _register (cls, path_list, plugin_name) :
        token     = "%s,%s" % (PIM_TOKEN, plugin_name)
        if token not in path_list :
            path_list.append (token)
    # end def _register

    @classmethod
    def tag_module (cls, plugin_name, module_name, tag) :
        if module_name in cls.tag_dict :
            old_pname, old_tag = cls.tag_dict [module_name]
            if old_tag != tag :
               raise RuntimeError \
                   ( "Tag mismatch for module %s (plugins %s and %s)"
                   % (module_name, old_pname, plugin_name)
                   )
        cls.tag_dict [module_name] = (plugin_name, tag)
    # end def tag_module

    @classmethod
    def _run_setup (cls, directory, plugin_name) :
        fname = os.path.join (directory, "_%s.t3p" % plugin_name)
        try :
            zim = zipimport.zipimporter (fname)
        except ImportError :
            if __debug__ :
                pyk.fprint ("Could not import from %s" % fname)
            return
        sname     = "_setup"
        setup_mod = zim.find_module (sname)
        if not setup_mod :
            if __debug__ :
                pyk.fprint ("Could not find '%s' in %s" % (sname, fname))
            return
        zim.load_module (sname)
    # end def _run_setup

    def __init__ (self, path) :
        if path.startswith (PIM_TOKEN) :
            self.plugin_name = path.split (",") [1]
            self._cache      = {}
        else :
            raise ImportError
    # end def __init__

    def find_module (self, fullname, path = None) :
        assert not path
        mod    = fullname.split  (".")    [-1]
        path   = ""
        if mod != fullname :
            path = fullname.rsplit (".", 1) [0]
        loader = self._find_module (path, mod, self.plugin_name)
        if loader :
            self._cache [fullname] = loader
            return self
    # end def find_module

    def load_module (self, fullmodule) :
        loader = self._cache.pop    (fullmodule)
        result = loader.load_module (fullmodule)
        if hasattr (result, "__path__") :
            result.__path__ = p = [] ### remove zipimporter's token
            pending             = self.pending.pop (fullmodule, ())
            for plugin_name in pending :
                self._register (p, plugin_name)
        return result
    # end def load_module

    def _find_module (self, path, mod, plugin_name) :
        fname    = self._plugin_file (plugin_name)
        if path :
            zip_path = os.path.join (fname, path.replace (".", os.path.sep))
        else :
            zip_path = fname
        try :
            zim  = zipimport.zipimporter (zip_path)
        except ImportError :
            pass
        else :
            result = zim.find_module (mod)
            return result
    # end def _find_module

    def _plugin_file (self, plugin_name) :
        plugin_with_version = "_%s" % self.plain_to_version [plugin_name]
        return os.path.join \
               ( self.plugin_dir
               , plugin_with_version
               , "%s.t3p" % plugin_with_version
               )
    # end def _plugin_file

# end class Plugin_Importer

if __name__ != '__main__' :
    if DPN_Importer not in sys.path_hooks :
        sys.path_hooks.insert (0, DPN_Importer)
    ### cannot import _TFL.Environment here :-(
    if getattr (sys, "frozen", False) :
        if Plugin_Importer not in sys.path_hooks :
            sys.path_hooks.insert (1, Plugin_Importer)
### __END__ TFL.Importers
