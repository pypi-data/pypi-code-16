# -*- coding: utf-8 -*-
# Copyright (C) 2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.SCM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.SCM.Journal
#
# Purpose
#    Write change summaries to journal on disk
#
# Revision Dates
#     6-May-2015 (CT) Creation
#     8-May-2015 (CT) Put journal files in date-specific directories
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _MOM                  import MOM
from   _TFL                  import TFL

import _MOM._SCM.Summary

from   _TFL.pyk              import pyk
from   _TFL                  import sos

import _TFL._Meta.Property
import _TFL._Meta.Once_Property
import _TFL.Filename
import _TFL.json_dump

import datetime
import logging

class Journal (TFL.Meta.Object) :
    """Write change summaries to journal on disk"""

    def __init__ (self, directory, error_cb = None, scope = None) :
        self.directory = directory
        self.error_cb  = error_cb
        if not sos.path.exists (directory) :
            sos.mkdir_p (directory)
        elif not sos.path.isdir (directory) :
            raise ValueError ("Path %r is not a directory" % (directory, ))
        if scope is not None :
            scope.add_after_commit_callback (self)
    # end def __init__

    def __call__ (self, scope, change_summary) :
        if change_summary :
            directory = self.directory + datetime.datetime.now ().strftime \
                ("/%Y/%m/%d/")
            try :
                if not sos.path.exists (directory) :
                    sos.mkdir_p (directory)
                elif not sos.path.isdir (directory) :
                    raise ValueError \
                        ("Path %r is not a directory" % (directory, ))
                max_cid = scope.max_cid
                fn      = TFL.Filename \
                    ("%08d" % (max_cid, ), default_dir = directory)
                cargo   = change_summary.as_json_cargo
                TFL.json_dump.to_file (cargo, fn.name, indent = 2)
            except Exception as exc :
                error_cb = self.error_cb
                if error_cb is not None :
                    error_cb (self, scope, change_summary, exc)
                else :
                    logging.exception \
                        ("Exception during change journal callback")
    # end def __call__

    def load (self, file_name) :
        fn = TFL.Filename (file_name, default__dir = self.directory)
        with open (fn.name, "rb") as file :
            cargo = json.load (file)
        result = MOM.SCM.Summary.from_json_cargo (cargo)
        return result
    # end def load

# end class Journal

if __name__ != "__main__" :
    MOM.SCM._Export ("*")
### __END__ MOM.SCM.Journal
