# -*- coding: utf-8 -*-
# Copyright (C) 2009-2016 Martin Glueck. All rights reserved
# Langstrasse 4, 2244 Spannberg, Austria. martin@mangari.org
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    Generate_POT_Files
#
# Purpose
#    Generate_POT_Files
#
# Revision Dates
#    28-Oct-2009 (MG) Creation
#     7-Jun-2012 (CT) Use `TFL.r_eval`
#    10-Oct-2016 (CT) Make Python-3 compatible
#    ««revision-date»»···
#--

"""This is the module doc string which, as a test is long enough to span at
   least two lines in the source file.
"""
from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function

from   _TFL                  import TFL

from   _TFL.I18N             import _, _T
from   _TFL.predicate        import any_true
from   _TFL.pyk              import pyk

import _TFL._Meta.Object
import _TFL.defaultdict
import _TFL.r_eval

import  datetime
import  re
import  sys
import  tokenize

class Test :
    """This is a class docstring"""

    message = _("Foo")

    def _test (self) :
        """This is a method doc string"""
        print (_T (ckw.title or "Baz"))
        print (_T ("Foo"))
        foo = _("Markup %d")
        print (_T(foo) % 42)
        print (_Tn ("Singular", "Plural", 4))
    # end def _test

# end class Test

class Collect_Translation_Strings (TFL.Meta.Object) :

    ignore        = set \
        ( ( tokenize.COMMENT
          , tokenize.NL, tokenize.NEWLINE
          , tokenize.INDENT
          , tokenize.COMMENT
          )
        )
    class_or_def  = set (("class", "def"))

    pot_header = r"""
# %(title)s
# Copyright (C) %(year)s %(company)s
# %(authors)s
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: %(version)s\n"
"PO-Revision-Date: %(time)s\n"
"Last-Translator: %(translator)s\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=%(encoding)s\n"
"Content-Transfer-Encoding: 8bit\n"
""".strip ()

    msg_entry_pat = re.compile \
        ( '(?P<location>^\#:.+?)^msgid (?P<id>.+?)^msgstr (?P<str>.+?)^\w*$'
        , re.DOTALL | re.MULTILINE | re.X
        )

    def __init__ (self, markup, docstrings = True, * file_or_package_names) :
        self._markups         = markup
        self._mark_docstrings = docstrings
        self._translations    = TFL.defaultdict (list)
        for file in self._filenames (file_or_package_names) :
            for toknum, tokval, (sline, srow), (erow, ecol), line \
                                   in tokenize.generate_tokens (file) :
                self._handle_tokens (toknum, tokval, sline)
    # end def __init__

    def create_pot_file (self, filename, ** kw) :
        authors     = kw.pop ("authors", ("no.author@unknow.where", ))
        now         = datetime.datetime.now ()
        kw ["time"] = now.strftime ("%Y-%m-%d %H:%M %Z")
        kw ["year"] = now.year
        for key, default in pyk.iteritems \
                ( dict
                    ( title      = "Project Dummy"
                    , company    = "My Company"
                    , translator = authors [0]
                    , version    = "0.1"
                    , encoding   = "UTF-8"
                    )
                ) :
            if key not in kw :
                kw [key] = default
        kw ["authors"] = ", ".join (authors)
        if filename :
            file       = open (filename, "w")
        else :
            file       = sys.stdout
        file.write (self.pot_header % kw)
        file.write ("\n")
        for (singular, plural), locations in sorted \
                (pyk.iteritems (self._translations)) :
            locs = ["%s:%s" % (fn, ln) for (fn, ln, _) in sorted (locations)]
            file.write ("\n")
            file.write ("#: %s\n"      % (" ".join (locs), ))
            if any_true (d for (_, _, d) in locations) :
                file.write ("#. docstring\n")
            if ("%" in singular) or ("%" in plural) :
                file.write ("#, c-format\n")
            file.write     ('msgid "%s"\n' % (self._format_key (singular), ))
            if plural :
                file.write \
                    ('msgid_plural "%s"\n' % (self._format_key (plural), ))
                file.write ('msgstr[0] ""\n')
                file.write ('msgstr[1] ""\n')
            else :
                file.write ('msgstr ""\n')
        if filename :
            file.close     ()
    # end def create_pot_file

    def _add_translation ( self, singular, line_no
                         , plural    = ""
                         , docstring = False
                         ) :
        self._translations [singular, plural].append \
            ((self._module_name, line_no, docstring))
    # end def _add_translation

    def _collect_strings (self, toknum, tokval, line_no) :
        if toknum == tokenize.OP and tokval == "," and self._plural_markup :
            if not self._collect_plural :
                self._collect_plural = True
                return
            else :
                tokval = ")" ### simulate a end of the translation call
        append = (self._singular, self._plural) [self._collect_plural].append
        if toknum == tokenize.OP and tokval == ")" :
            ### that's the end of the markup
            self._handle_tokens = self._check_token
            if self._singular:
                self._add_translation \
                    ( "".join (self._singular), line_no, "".join (self._plural))
        elif toknum == tokenize.STRING :
            append (self._eval (tokval))
        elif toknum not in self.ignore :
            if toknum != tokenize.NAME or not self._translation_call :
                print \
                    ( _T ("*** %s:%d Unexpekted token %s, %r")
                    % (self._module_name, line_no, toknum, tokval)
                    , file = sys.stderr
                    )
    # end def _collect_strings

    def _check_token (self, toknum, tokval, line_no) :
        if toknum == tokenize.STRING and self._wait_for_docstring :
            self._plural_markup = False
            self._add_translation \
                (self._eval (tokval), line_no, docstring = True)
        if toknum not in self.ignore :
            self._wait_for_docstring = False
        if (toknum == tokenize.NAME) :
            if tokval in self.class_or_def :
                self._handle_tokens = self._wait_for_colon
            elif tokval in self._markups :
                self._translation_call = len (tokval) > 1
                self._plural_markup = "n" in tokval
                self._handle_tokens = self._handle_markup
    # end def _check_token

    def _eval (self, tokval) :
        return TFL.r_eval (tokval).strip ()
    # end def _eval

    def _filenames (self, file_or_package_names) :
        for f in file_or_package_names :
            self._new_module         = True
            self._wait_for_docstring = self._mark_docstrings
            self._module_name        = f
            self._handle_tokens      = self._check_token
            yield open (f).readline
    # end def _filenames

    def _format_key (self, key) :
        lines  = key.split ("\n")
        result = '\\n"\n"'.join (lines)
        if len (lines) > 1 :
            result = '"\n"' + result
        return result
    # end def _format_key

    def _handle_markup (self, toknum, tokval, line_no) :
        if toknum == tokenize.OP and tokval == "(" :
            ### looks like we have found a markup
            self._singular       = []
            self._plural         = []
            self._collect_plural = False
            self._handle_tokens  = self._collect_strings
        else :
            self._handle_tokens  = self._check_token
    # end def _handle_markup

    def _wait_for_colon (self, toknum, tokval, line_no) :
        if toknum == tokenize.OP and tokval == ":" :
            self._wait_for_docstring = self._mark_docstrings
            self._handle_tokens      = self._check_token
    # end def _wait_for_colon

# end class Collect_Translation_Strings

def command_line (argsv = None) :
    """Defines the command line"""
    from _TFL.Command_Line import Command_Line
    return Command_Line \
        ( arg_spec    = ( "src_file:P", )
        , option_spec =
            ( "skip_docstrings:B?Do not mark docstrings for translation"
            , "translation_markup:S,=_,_T,_Tn,_Tl,_Tln"
            )
        , help_on_err = True
        )
# end def command_line

def main (cmd) :
    ts = Collect_Translation_Strings \
        ( cmd.translation_markup
        , not cmd.skip_docstrings
        , cmd.src_file
        )
    ts.create_pot_file (None)
# end def main

if __name__ == "__main__" :
    main (command_line ())
### __END__ Generate_POT_Files
