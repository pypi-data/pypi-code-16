# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Mag. Christian Tanzer All rights reserved
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
#    MOM.DB_Man
#
# Purpose
#    Manager for data bases of MOM
#
# Revision Dates
#    30-Jun-2010 (CT) Creation
#    12-Jul-2010 (CT) Signature changed from `db_url, app_type` to
#                     `app_type, db_url`
#    12-Jul-2010 (CT) `destroy` added
#    15-Jul-2010 (MG) `__str__` added
#    19-Jan-2013 (MG) Add support for `legacy_lifter`
#     7-Jun-2013 (CT) Pass `src.db_meta_data` to `consume`
#     2-Aug-2013 (CT) Add `entity_type` to increase compatibility with `Scope`
#    25-Aug-2013 (CT) Add `reserve_surrogates`
#     8-Jan-2014 (CT) Adapt to change of `Legacy_Lifter`, make it optional
#    ««revision-date»»···
#--

from   _MOM                  import MOM
from   _TFL                  import TFL
from   _TFL.pyk              import pyk

import _TFL._Meta.Object
import _TFL.Record
import _MOM.Legacy_Lifter

@pyk.adapt__str__
class DB_Man (TFL.Meta.Object) :
    """Manager for data bases of MOM."""

    uncommitted_changes    = TFL.Record (pending_attr_changes = {})
    ilk                    = "PC"
    src                    = None

    db_meta_data           = property (TFL.Getter.ems.db_meta_data)
    entity_type            = property (TFL.Getter.app_type.entity_type)
    max_cid                = property (TFL.Getter.ems.max_cid)
    max_pid                = property (TFL.Getter.ems.max_pid)
    max_surrs              = property (TFL.Getter.ems.max_surrs)
    readonly               = property (TFL.Getter.ems.db_meta_data.readonly)
    reserve_surrogates     = False

    ### DB_Man creation methods
    @classmethod
    def connect (cls, app_type, db_url) :
        db_url   = app_type.Url (db_url)
        self     = cls.__new__  (cls, app_type, db_url)
        self.ems = app_type.EMS.connect (self, db_url)
        return self
    # end def connect

    @classmethod
    def create ( cls, app_type, db_url, from_db_man
               , chunk_size    = 10000
               , legacy_lifter = None
               ) :
        db_url          = app_type.Url (db_url)
        self            = cls.__new__  (cls, app_type, db_url)
        self.src        = from_db_man
        self.ems        = app_type.EMS.new (self, db_url)
        self.chunk_size = chunk_size
        self._migrate (chunk_size, legacy_lifter)
        return self
    # end def create

    def __init__ (self) :
        raise TypeError \
            ( "Use {name}.connect or {name}.create to create "
                "new database managers".format (name = self.__class__.__name__)
            )
    # end def __init__

    def __new__ (cls, app_type, db_url) :
        self          = cls.__c_super.__new__ (cls)
        self.db_url   = db_url
        self.app_type = app_type
        return self
    # end def __new__

    ### DB_Man instance methods

    def change_readonly (self, state) :
        """Change `readonly` state of database to `state`."""
        self.ems.change_readonly (state)
    # end def change_readonly

    def destroy (self) :
        self.ems.close ()
        self.__dict__.clear ()
    # end def destroy

    def _migrate (self, chunk_size, legacy_lifter) :
        src    = self.src
        e_iter = src.ems.pcm.produce_entities ()
        c_iter = src.ems.pcm.produce_changes  ()
        if legacy_lifter :
            ll     = MOM.Legacy_Lifter_Wrapper (self, legacy_lifter)
            e_iter = ll.entity_iter (e_iter)
            c_iter = ll.change_iter (c_iter)
        self.ems.pcm.consume (e_iter, c_iter, chunk_size, src.db_meta_data)
    # end def _migrate

    def __str__ (self) :
        return "%s <%s>" % (self.__class__.__name__, self.db_url)
    # end def __str__

# end class DB_Man

if __name__ != "__main__" :
    MOM._Export ("*")
### __END__ MOM.DB_Man
