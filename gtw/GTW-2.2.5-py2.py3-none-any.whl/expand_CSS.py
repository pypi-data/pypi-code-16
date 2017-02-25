# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.expand_CSS
#
# Purpose
#    Expand a CSS template via the Python `%s` operator
#
# Revision Dates
#    14-Dec-2007 (CT) Creation
#    15-Dec-2007 (MG) `eval_paremeters` factored to support included files
#    15-Dec-2007 (MG) Fix single `%` to avoid having `%%` in the templates
#    15-Dec-2007 (MG) `watch_directories` added
#    16-Dec-2007 (MG) Exception handling added
#    19-Apr-2008 (MG) Template handling moved into a class to support
#                     dependency tracking and automatic css file recreation
#                     based on changes of a parameter file
#    23-Jul-2010 (MG) Polling based `watch_directories` support added for
#                     platforms where `pyinotify` is not supported (OS X,
#                     Windows, ...)
#    24-Nov-2010 (CT) Option `-template_extension` added
#    ««revision-date»»···
#--

from   __future__             import print_function, unicode_literals

from   _TFL                   import TFL

from   _TFL.Caller            import Scope
from   _TFL.pyk               import pyk

import _TFL.CAO
import _TFL.Filename
import _TFL.Record
import _TFL._Meta.Object
import _TFL.defaultdict
import _TFL.sos               as     os

import re
import stat
import traceback

class CSS_Template (TFL.Meta.Object) :
    """Models a css template and teh dependencies to parameter files."""


    parameter_files    = TFL.defaultdict (set)
    template_extension = ".css_template"
    templates          = {}
    fix_percent_pat    = re.compile ("%([^(])")

    def __init__ ( self, template
                 , parameter_file = None
                 , css_file       = None
                 , polling        = False
                 ) :
        self.count    = 0
        self.polling  = polling
        self.template = TFL.Filename \
            (template, self.template_extension, absolute = True)
        self.css_file = TFL.Filename (css_file or ".css", self.template)
        self.pdict    = {}
        if not os.path.isfile (self.template.name) :
            raise ValueError ("`%s` does not exist" % (self.template.name, ))
        self.templates [self.template.name] = self
        self.parameter_file = TFL.Filename \
            (parameter_file or ".parameters", self.template)
        if os.path.isfile (self.parameter_file.name) :
            self._update_dependencies    ()
        else :
            print ("*** no parameter file for", self.template.name)
            self.parameter_file = None
    # end def __init__

    def check_for_update (self) :
        update = False
        if self.parameter_file :
            p_m_time = os.stat (self.parameter_file.name) [stat.ST_MTIME]
            update   = p_m_time != self.p_m_time
        t_m_time = os.stat (self.template.name) [stat.ST_MTIME]
        update   = update or (t_m_time != self.t_m_time)
        if update :
            self.create_css_file ()
    # end def check_for_update

    def create_css_file (self, overrides = {}) :
        try :
            self.pdict = {} ### lets clear it again before we read everything
            self._update_dependencies ()
            filename   = self.template.name
            ct    = open         (filename).read ()
            if self.polling :
                self.t_m_time = os.stat (filename) [stat.ST_MTIME]
            ct, _ = self.fix_percent_pat.subn \
                (lambda m : "%%%s" % (m.group (0), ), ct)
            outf  = open  (self.css_file.name, "wb")
            outf.write    (ct % Scope (globs = self.pdict, locls = overrides))
            outf.close    ()
            print \
                ( "[%04d] CSS file created `%s`"
                % (self.count, self.css_file.name, )
                )
            self.count += 1
        except :
            traceback.print_exc ()
    # end def create_css_file

    @classmethod
    def find_templates (cls, polling, directory, recursive = False) :
        for file in os.listdir_full (directory) :
            if os.path.isdir (file) :
                if recursive :
                    cls.find_templates (file, recursive = True)
            if file.endswith (".css_template") and not "#" in file :
                cls (file, polling = polling)
    # end def find_templates

    def _update_dependencies (self, filename = None) :
        if filename is None :
            filename = self.parameter_file.name
        self.parameter_files [os.path.abspath (filename)].add (self)
        new_dir = TFL.Filename (filename).directory
        if new_dir :
            old_dir = os.getcwd ()
            os.chdir (new_dir)
        if self.polling :
            self.p_m_time = os.stat (filename) [stat.ST_MTIME]
        execfile \
             ( filename
             , dict
                 ( R       = TFL.Record
                 , include = self._update_dependencies
                 )
             , self.pdict
             )
        if new_dir :
            os.chdir (old_dir)
    # end def _update_dependencies

# end class CSS_Template

def watch_directories (pyinotify, timeout, overrides, * directories) :
    if pyinotify :
        _watch_directories_pyinotify (pyinotify, overrides, * directories)
    else :
        import time
        print ("Polling fallback, interval %dms" % (timeout, ))
        while True :
            time.sleep (1000. / timeout)
            for template in pyk.itervalues (CSS_Template.templates) :
                template.check_for_update ()
# end def watch_directories

def _watch_directories_pyinotify (pyinotify, overrides, * directories) :
    watch  = pyinotify.WatchManager ()
    events = \
        pyinotify.IN_MODIFY | pyinotify.IN_CREATE

    class Event_Prcoessor (pyinotify.ProcessEvent) :

        def process_IN_MODIFY (self, event) :
            self.update_changed_files (event)
        # end def process_IN_MODIFY

        def process_IN_CREATE (self, event) :
            self.update_changed_files (event)
        # end def process_IN_MODIFY

        def update_changed_files (self, event) :
            fn = TFL.Filename (os.path.join (event.path, event.name))
            if not fn.base.startswith (".#") :
                fn = os.path.abspath (fn.name)
                # we ignore temp files created by emacs
                if fn in CSS_Template.templates :
                    self.changed_files.add (CSS_Template.templates [fn])
                elif fn in CSS_Template.parameter_files :
                    self.changed_files.update \
                        (CSS_Template.parameter_files [fn])
        # end def update_changed_files

    # end class Event_Prcoessor

    event_processor               = Event_Prcoessor ()
    event_processor.changed_files = set ()
    notifier                      = pyinotify.Notifier (watch, event_processor)
    for d in directories :
        watch.add_watch (d, events, rec = False)

    while True:  # loop forever
        try:
            # process the queue of events as explained above
            notifier.process_events ()
            for fn in event_processor.changed_files :
                fn.create_css_file (overrides)
            event_processor.changed_files = set ()
            if notifier.check_events ():
                # read notified events and enqeue them
                notifier.read_events ()
        except KeyboardInterrupt :
            # destroy the inotify's instance on this interrupt (stop monitoring)
            notifier.stop ()
            break
# end def _watch_directories_pyinotify

def main (cmd) :
    keywords    = {} ### XXX cmd.keywords
    directories = set ()
    if cmd.template_extension :
        CSS_Template.template_extension = cmd.template_extension
    if cmd.template :
        for f in cmd.argv :
            CSS_Template (f).create_css_file (keywords)
    if cmd.watch_directories :
        try :
            import pyinotify
        except ImportError :
            pyinotify = None
            print ("pyinotify not found, fall back to polling")
        for d in cmd.watch_directories :
            CSS_Template.find_templates (pyinotify is None, d, False)
        for t in pyk.itervalues (CSS_Template.templates) :
            t.create_css_file (keywords)
        watch_directories \
            (pyinotify, cmd.poll_timeout, keywords, * cmd.watch_directories)
# end def main

Command = TFL.CAO.Cmd \
    ( main
    , args = ("template:P", )
    , opts =
          ( "poll_timeout:I=1000?Microseconds timeout if pyinotify is not "
              "availabe"
          , "template_extension:S=.css_template?Extension of template file"
          , "watch_directories:P,?List of directories to watch for changes"
          )
    )

if __name__ == "__main__":
    Command ()
### __END__ GTW.expand_CSS
