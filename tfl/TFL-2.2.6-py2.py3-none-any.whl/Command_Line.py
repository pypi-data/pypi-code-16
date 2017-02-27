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
#    TFL.Command_Line
#
# Purpose
#    Provide easy access to command line arguments and options in sys.argv
#
# Features provided
#    - Automatic type conversions for arguments and options
#    - Default values for arguments and options
#    - Options can be abbreviated (as long as the abbreviation is unique)
#    - Bounds checks on number of arguments and options
#    - Support for positional matching of options to arguments (rudimentary)
#    - Help
#
# Revision Dates
#    31-Oct-1998 (CT) Creation
#     1-Nov-1998 (CT) Creation continued
#     2-Nov-1998 (CT) Creation finished
#     5-Nov-1998 (CT) `min_args' added
#     5-Nov-1998 (CT) Handling of default options changed
#     5-Nov-1998 (CT) `max_occur' for options added
#     5-Nov-1998 (CT) Option abbreviations added
#     6-Nov-1998 (CT) `string.upper' used to canonize `Opt.type'
#     6-Nov-1998 (CT) `arg_spec' introduced to allow format conversion for
#                     arguments, too
#     6-Nov-1998 (CT) `help' added
#     7-Nov-1998 (CT) `Error' renamed to `Cmd_Error'
#    17-Nov-1998 (CT) `Pl_Array.__setitem__' corrected (use `deepcopy')
#    17-Nov-1998 (CT) `Command_Line._handle_arg' corrected
#    17-Nov-1998 (CT) Don't print `Command_Line.help' in case of errors
#    21-Nov-1998 (CT) `handle_arg' corrected
#                     (set `argv [j]' to `argument [j].value')
#    21-Nov-1998 (CT) `_setup_arg' corrected (analogous to `handle_arg')
#    25-Nov-1998 (CT) Removed "\s" from arg_spec_pat and opt_spec_pat
#    26-Nov-1998 (CT) Errors in `Command_Line.copy' corrected
#    14-Jan-1999 (CT) Option-type `B' added and made default
#                     (and don't display `type' and `default' for `B' options)
#    26-Jan-1999 (CT) Added `B' to `opt_spec_pat'
#     4-Feb-1999 (CT) `help_on_err' added
#    16-Feb-1999 (CT) Factored `Environment.script_name' and
#                     `Environment.script_path'
#    26-Feb-1999 (CT) Use Abbr_Key_Dict for option dictionary
#    26-Feb-1999 (CT) `exc_on_err' added
#    26-Feb-1999 (CT) Implicit options `-help' and `-?' added
#    10-Mar-1999 (CT) Restrict help to 8 arguments
#    10-Mar-1999 (CT) `Opt.values' added
#     1-Apr-1999 (CT) `Opt.auto_split' added
#     1-Apr-1999 (CT) `Opt.values' renamed to `Opt.joined_values'
#     1-Apr-1999 (CT) `Opt.values' added
#     6-Apr-1999 (CT) `Opt.set_value' corrected (don't try to split `None')
#     6-Apr-1999 (CT) `Command_Line.arg_dict' added
#     6-Apr-1999 (CT) PL_Array replaced by PL_List
#    23-Apr-1999 (CT) Parameter `help' added to Command_Line constructor
#    23-Apr-1999 (CT) `?' added to `option_spec'
#    21-Jul-1999 (CT) `Command_Line.argd' added
#    26-Jul-1999 (CT) Allow ' ' as separator for `auto_split'
#    26-Jul-1999 (CT) Argument help added
#    28-Sep-1999 (CT) Removed arguments `value' and `pos' from
#                     `Arg.__init__'
#    28-Sep-1999 (CT) `Arg._cook_default' instead of argument `cook' for
#                     `Arg.__init__'
#    28-Sep-1999 (CT) Allow instances of `Arg' and `Opt' for
#                     `arg_spec' and `option_spec', respectively
#    28-Sep-1999 (CT) `Argument' renamed to `Arg'
#    28-Sep-1999 (CT) `Option'   renamed to `Opt'
#    29-Sep-1999 (CT) `Arg_L' and `Opt_L' added
#     6-Oct-1999 (CT) `hide' added to `Opt'
#    27-Oct-1999 (CT) `and value' added to `List_Selection_._set_value'
#    27-Oct-1999 (CT) `max_arg' set to maximum of `max_arg' and
#                     `len (arg_spec)'
#     9-Dec-1999 (CT) `re.S' added to `arg_spec_pat'
#    21-Feb-2000 (CT) Convert `option_spec' and `arg_spec' from string to
#                     tuple, if necessary
#    20-Jun-2000 (CT) `__getattr__' and `__getitem__' added to `Command_Line'
#                     (implemented in terms of new `_attribute_value')
#    20-Jun-2000 (CT) `max_args', `min_args', and `description' renamed to
#                     `_max_args', `_min_args', and `_description',
#                     respectively
#    03-Jul-2000 (RM) 'keywords' attribute added to Command_Line. Now
#                     all parameters with key=value will be available
#                     in the keywords dictionary
#    04-Jul-2000 (RM) Additional parameter process_keywords in
#                     Command_Line
#     4-Jul-2000 (CT) `key_value' added
#     4-Jul-2000 (CT) Don't show matches for options starting with `__'
#     5-Jul-2000 (RM) Changed sos.enviroment to sos.environ in key_value
#     7-Aug-2000 (CT) `_attribute_value' changed to handle boolean (or rather
#                     unvalued) options correctly
#    12-Sep-2000 (CT) Use `Regexp' instead of plain `re'
#     4-Oct-2000 (CT) s/keyword_arg/keyw_arg_pat/g
#     4-Oct-2000 (CT) `_handle_arg' returns new `j' (index into `argv')
#     4-Oct-2000 (CT) `keyw_arg_pat' improved
#    10-Oct-2000 (CT) `keyw_arg_pat' improved (`.*' for <value>)
#    15-Jan-2001 (CT) `range_pat' added and used
#    12-Dec-2000 (CT) Removed `:' from `keyw_arg_pat'
#    22-Feb-2001 (CT) Use `raise' instead of `raise exc' for re-raise
#    26-Feb-2001 (CT) `_cooked_value' changed to allow input `08' for ints
#                     (meant as decimal)
#    26-Feb-2001 (CT) `joined_values': pass `self.value.body' to
#                     `string.join' (in Python 2.0, passing `self.value'
#                     leads to infinite recursion)
#    29-Mar-2001 (CT) `-' added to option help
#    12-Apr-2001 (CT) `max_args' changed to use `-1' for unlimited number of
#                     arguments and `0' for no arguments
#     4-May-2001 (CT) `:' added to possible `auto_split' characters in
#                     `opt_spec_pat'
#     9-Sep-2001 (CT) Exception handler of `Command_Line.__init__` corrected
#    12-Apr-2002 (CT) Use `StandardError` instead of `Exception`
#     1-Jul-2002 (CT) `__cmp__` added to `Arg`
#    22-May-2003 (CT) Arg/Opt type `X` added and done some refactorings
#                     (added `cooks` and used it appropriately)
#    11-Jun-2003 (CT) s/== None/is None/
#    11-Jun-2003 (CT) s/!= None/is not None/
#     5-Jul-2003 (CT) `range_delta` added
#     6-Jul-2003 (CT) `_cook_F` added
#     9-Dec-2003 (CT) Option type `T` added (same semantics as `S`, but
#                     allows `auto_split`)
#    29-Jan-2004 (CT) `_Help_` factored
#    18-Feb-2004 (CT) `_cmd_name` factored
#    19-Feb-2004 (CT) `Arg.hash` added
#    23-Mar-2004 (CT) `Command_Line.__init__` changed to not interpret
#                     an option as a value of a preceeding option (otherwise
#                     one gets rather confusing error messages or none at all)
#    23-Mar-2004 (CT) Some esthetics
#    29-Mar-2004 (CT) `_fmt_arg` moved from `Command_Spec` to `_Help_`
#    19-Apr-2004 (CT) `_attribute_value` changed to use
#                     `option.really_has_key` instead of `option.has_key`
#                     (otherwise sick clients get confused when they use an
#                     argument name `foo` and an option name `foobar`)
#     9-Jun-2004 (CT) `Command_Line.__init__` changed to allow option-like
#                     option values if specified as `-option=-value`
#    24-Oct-2004 (CT) `T` added to `type_specifiers` dict
#    24-Mar-2005 (CT) Moved into package `TFL`
#     3-Jun-2005 (MG) `_usage`: missing call parameter `result` added to the
#                     call of `_add_rest_args`
#    30-Aug-2005 (CT) Use `in` instead of `find`
#     1-May-2006 (MG) Use `dict` instead of `d_dict`
#     9-Aug-2006 (CT) `Command_Spec.__cmp__` and `Command_Spec.__hash__`
#                     removed (definition didn't make any sense)
#    17-Sep-2007 (CT) Argument `cook` added to `Arg` and `Opt`
#    17-Sep-2007 (CT) Argument/option type `P` (path) added
#    15-Feb-2008 (CT) `_Help_._opts` robustified
#     8-May-2008 (CT) Changed to use new-style classes
#     8-May-2008 (CT) Cleanups
#    30-Jun-2008 (CT) `Opt_L.__init__` added
#    30-Jun-2008 (CT) `Opt_D` added
#     8-Jan-2009 (CT) `raw_value` added
#     7-Jun-2012 (CT) Use `TFL.r_eval`
#    16-Jun-2013 (CT) Fix option matching in `Command_Line.__init__`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    ««revision-date»»···
#--

"""
Provides easy access to command line arguments and options in sys.argv

Features provided:
    - Automatic type conversions for arguments and options
    - Default values for arguments and options
    - Options can be abbreviated (as long as the abbreviation is unique)
    - Bounds checks on number of arguments and options
    - Support for positional matching of options to arguments (rudimentary)
    - Help
"""

from   __future__                 import print_function

from   _TFL                       import TFL
from   _TFL.predicate             import *
from   _TFL.pyk                   import pyk
from   _TFL.Regexp                import Regexp, re
from   _TFL._Meta.totally_ordered import totally_ordered

import _TFL.Abbr_Key_Dict
import _TFL.Environment
import _TFL.PL_Dict
import _TFL.PL_List
import _TFL.r_eval
import _TFL.sos
import _TFL._Meta.Object

import sys

class Cmd_Error (Exception) :

    def __init__ (self, * args) :
        self.args = args
    # end def __init__

    def __str__ (self) :
        return "Command_Line error: %s" % (" ".join (self.args), )
    # end def __str__

    __repr__ = __str__
# end class Cmd_Error

class _List_Selection_ (TFL.Meta.Object):
    """Mixin class for `Arg' and `Opt'.

       Provide for arguments/options which must have a value out of a list of
       possible selections.

    """

    def __init__ (self, selection, strict = 1, * args, ** kw) :
        self.selection = selection
        self.strict    = strict
        self.__super.__init__ (* args, ** kw)
        if self.description :
            self.description = "%s\nPossible values are: %s" % \
                (self.description, ", ".join (self.selection))
    # end def __init__

    def _set_value (self, value, pos) :
        if self.strict and value and value not in self.selection :
            one_of = ", ".join (self.selection)
            if len (one_of) > 60 :
                one_of = one_of [:60] + "..."
            raise Cmd_Error \
                ( "Invalid value `%s' for %s `%s' of type `%s'"
                  "\nChoose one of\n    %s"
                % (value, self.kind, self.name, self.type, one_of)
                )
        self.__super._set_value (value, pos)
    # end def _set_value

# end class _List_Selection_

def _cook_F (value) :
    return float (TFL.r_eval (value))
# end def _cook_F

def _cook_X (value) :
    if isinstance (value, pyk.string_types) :
        return long (value, 0)
    else :
        return long (value)
# end def _cook_X

@totally_ordered
class Arg (TFL.Meta.Object) :

    kind         = "argument"
    paren_pat    = Regexp ("""^(.*)$""")
    range_pat    = Regexp \
        ( r"""^\s*"""
          r"""(?P<head> (?: 0[xX])? \d+)"""
          r"""\s*"""
          r"""\.\."""
          r"""\s*"""
          r"""(?P<tail> (?: 0[xX])? \d+)"""
          r"""\s*"""
          r"""(?: : (?P<delta> \d+))?"""
          r"""\s*$"""
        , re.X
        )
    cooks        = dict \
        ( B      = bool
        , F      = _cook_F
        , I      = int
        , L      = TFL.r_eval
        , P      = TFL.sos.expanded_path
        , S      = identity
        , T      = identity
        , U      = long
        , X      = _cook_X
        )

    def __init__ (self, name = "", type = "", default = "", description = "", explanation = "", cook = None) :
        self.name        = name
        self.type        = (type or "S") [0].upper ()
        self.default     = self.cooked_default = default
        self.description = description
        self.explanation = explanation
        self.value       = None
        self.pos         = 0
        self.cook        = cook or self.cooks [self.type]
        self._cook_default (default)
    # end def __init__

    def _cook_default (self, default) :
        self.value = self._cooked_value (default)
    # end def _cook_default

    def set_value (self, value, pos) :
        self.raw_value = value
        self._set_value (value, pos)
    # end def set_value

    def _set_value (self, value, pos) :
        self.value = self._cooked_value (value)
        self.pos   = pos
    # end def _set_value

    def _cooked_value (self, value) :
        if value in ("", None) :
            value = self.cooked_default
        if isinstance (value, pyk.string_types) :
            try :
                cook = self.cook
                if self.type in "L" and not self.paren_pat.match (value) :
                    value = "(%s)" % (value, )
                try :
                    value = cook (value)
                except ValueError :
                    ### `eval' handles expressions
                    value = cook (TFL.r_eval (value))
            except Exception as exc :
                print (exc)
                raise Cmd_Error \
                    ( "Invalid value `%s' for %s `%s' of type `%s'"
                    % (value, self.kind, self.name, self.type)
                    )
        return value
    # end def _cooked_value

    def __eq__ (self, rhs) :
        if hasattr (rhs, "name") :
            rhs = rhs.name
        return self.name == rhs
    # end def __eq__

    def __hash__ (self) :
        return hash (self.name)
    # end def __hash__

    def __lt__ (self, rhs) :
        if hasattr (rhs, "name") :
            rhs = rhs.name
        return self.name < rhs
    # end def __lt__

    def __repr__ (self) :
        return "%s (%s, %s, %s, %s, %d)" % \
            ( self.__class__.__name__
            , self.name, self.type, self.cooked_default, self.value, self.pos
            )
    # end def __repr__

# end class Arg

class Arg_L (_List_Selection_, Arg) :
    pass
# end class Arg_L

class Opt (Arg) :

    kind         = "option"
    default_type = "B"

    def __init__ ( self, name, type = "", default = "", description = ""
                 , explanation = ""
                 , valued = 0, max_occur = None, auto_split = None, hide = 0
                 , range_delta = 1, cook = None
                 ) :
        self.__super.__init__ \
            ( name, type or self.default_type, default
            , description, explanation, cook
            )
        self.value       = TFL.PL_List (undefined = '')
        self.valued      = valued or   (self.type != "B")
        if max_occur is None :
            max_occur    = [1, 0] [auto_split is not None]
        self.max_occur   = max_occur
        self.list_p      = auto_split
        self.auto_split  = auto_split or [",", None] [self.type == "S"]
        self.hide        = hide or name [:2] == "__"
        self.range_delta = range_delta
        if default :
            self._cook_default_opt (default)
    # end def __init__

    def _cook_default (self, default) :
        pass
    # end def _cook_default

    def _cook_default_opt (self, default) :
        if self.auto_split and self.auto_split in default :
            self.cooked_default = []
            for v in default.split (self.auto_split) :
                self.cooked_default.append (self._cooked_value (v))
    # end def _cook_default

    def value_1 (self) :
        """Returns first value of option specified in command line or default"""
        if len (self.value) :
            return self.value [0]
        elif isinstance (self.cooked_default, (list, tuple)) :
            return self.cooked_default [0]
        else :
            return self._cooked_value (self.default)
    # end def value_1

    def values (self) :
        """Returns a list of all option values specified on the command-line
           or a single-element list with the default value (if any) or an
           empty list.
        """
        if len (self.value) :
            return self.value.body
        elif self.default :
            if isinstance (self.cooked_default, (list, tuple)) :
                return self.cooked_default
            else :
                return (self._cooked_value (self.default), )
        return ()
    # end def values

    def joined_values (self, sep = ",") :
        """Returns all values of option specified in command line or default
           as a single string. The values are separated by `sep'.
        """
        if len (self.value) :
            return sep.join (self.value.body)
        return self._cooked_value (self.default)
    # end def values

    def set_value (self, value, pos) :
        self.raw_value = value
        if self.auto_split and value :
            if self.type in "IUX" and self.range_pat.match (value) :
                cook = self.cook
                rp   = self.range_pat
                vals = range \
                    ( cook (rp.head)
                    , cook (rp.tail) + 1
                    , int (rp.delta or self.range_delta)
                    )
                for v in vals :
                    self._set_value (v, pos)
            else :
                for v in value.split (self.auto_split) :
                    self._set_value (v, pos)
        else :
            self._set_value (value, pos)
    # end def set_value

    def _set_value (self, value, pos) :
        if self.max_occur and len (self.value.body) >= self.max_occur :
            raise Cmd_Error \
                ( "Option `%s' must not be specified more than %d times"
                % (self.name, self.max_occur)
                )
        self.value.append (self._cooked_value (value))
        if not self.pos :
            self.pos = pos
        if value and not self.valued :
            raise Cmd_Error \
                ( ( "Option `%s' doesn't require any value "
                    "(offending value: `%s')"
                  ) % (self.name, value)
                )
        elif pos and self.valued and not value :
            raise Cmd_Error \
                ( "%s `%s' requires a value of type `%s'"
                % (self.kind, self.name, self.type)
                )
    # end def _set_value

    def __len__ (self) :
        if self.valued :
            return len (self.value)
        else :
            return self.pos
    # end def __len__

    def __repr__ (self) :
        return "%s (%s, %d)" % \
            (self.__class__.__name__, self.value, self.pos)
    # end def __repr__

# end class Opt

class Opt_L (_List_Selection_, Opt) :

    default_desc  = ""
    default_name  = ""
    default_value = ""
    default_type  = "S"

    def __init__ (self, selection, name = None, ** kw) :
        kw.setdefault ("default",     self.default_value)
        kw.setdefault ("description", self.default_desc)
        kw.setdefault ("type",        self.default_type)
        self.__super.__init__ \
            ( selection = selection
            , name      = name or self.default_name
            , ** kw
            )
    # end def __init__

# end class Opt_L

class Opt_D (Opt_L) :

    def __init__ (self, dict, ** kw) :
        self._dict = dict
        self.__super.__init__ \
            ( selection = sorted (pyk.iterkeys (dict))
            , cook      = self._cooked_key
            , ** kw
            )
    # end def __init__

    def _cooked_key (self, value) :
        return self._dict [value]
    # end def _cooked_key

# end class Opt_D

class _Help_ (TFL.Meta.Object) :

    item_sep            = "\n"

    usage_format        = "Usage     :\n    %s"
    usage_format_option = "[option]..."
    usage_sep           = " "

    arg_title           = "Arguments :"
    arg_head_format     = "    %-*s"
    arg_desc_format     = "        %s"
    arg_desc_leader     = "\n        "
    arg_sep             = "\n"

    opt_title           = "Options   :"
    opt_head_format     = "    -%-*s : %s = %s"
    opt_head_format_B   = "    -%-*s"
    opt_desc_format     = "        %s"
    opt_desc_leader     = "\n        "
    opt_sep             = "\n"

    nl_pat              = Regexp ("\n\\s*")

    def __init__ (self, cmd) :
        self.cmd         = cmd
        self.usage       = self._usage       (cmd)
        self.description = self._description (cmd)
        self.args        = self._args        (cmd)
        self.opts        = self._opts        (cmd)
    # end def __init__

    def __str__ (self) :
        result = [self.usage]
        for t in (self.description, self.args, self.opts) :
            if t :
                result.append (t)
        return self.item_sep.join (result)
    # end def __str__

    def _formatted (self, format, * args) :
        return format % args
    # end def _formatted

    def _cmd_name (self, cmd) :
        return cmd.script_name
    # end def _cmd_name

    def _usage (self, cmd) :
        result = [self._formatted (self.usage_format, self._cmd_name (cmd))]
        if cmd.option :
            result.append (self.usage_format_option)
        if cmd.argument :
            for i, a in enumerate (cmd.argument) :
                result.append (self._fmt_arg_usage (cmd, a.name, i))
            self._add_rest_args (cmd, result)
        elif cmd._min_args > 0 or cmd._max_args > 0 :
            self._add_rest_args (cmd, result)
        return self.usage_sep.join (result)
    # end def _usage

    def _description (self, cmd) :
        if cmd._description :
            leader = "\n    "
            result = self._formatted \
                ( "%s%s", leader, self.nl_pat.sub (leader, cmd._description))
        else :
            result = ""
        return result
    # end def _description

    def _max_length (self, names) :
        return max (names)
    # end def _max_length

    def _args (self, cmd) :
        result = []
        args   = [a for a in cmd.argument if a.description or a.explanation]
        if args :
            result.append (self.arg_title)
            leader = self.arg_desc_leader
            alen   = self._max_length ([len (a.name) for a in args])
            for a in sorted (args) :
                result.append \
                    (self._formatted (self.arg_head_format, alen, a.name))
                for t in (a.description, a.explanation) :
                    if t :
                        result.append \
                            ( self._formatted
                                  ( self.arg_desc_format
                                  , self.nl_pat.sub (leader, t)
                                  )
                            )
        return self.arg_sep.join (result)
    # end def _args

    def _opts (self, cmd) :
        result = []
        opts   = \
             [ (n, o) for (n, o) in pyk.iteritems (cmd.option)
                      if n == o.name and not o.hide
             ]
        if opts :
            result.append (self.opt_title)
            leader = self.opt_desc_leader
            olen   = self._max_length ([len (o.name) for (n, o) in opts])
            for n, o in sorted (opts) :
                if o.type == "B" :
                    result.append \
                        (self._formatted (self.opt_head_format_B, olen, n))
                else :
                    result.append \
                        ( self._formatted
                              ( self.opt_head_format
                              , olen, n
                              , cmd.type_specifiers.get (o.type, "<string>")
                              , o.default or "<None>"
                              )
                        )
                for t in (o.description, o.explanation) :
                    if t :
                        result.append \
                            ( self._formatted
                                  ( self.opt_desc_format
                                  , self.nl_pat.sub (leader, t)
                                  )
                            )
        return self.opt_sep.join (result)
    # end def _opts

    def _fmt_arg_usage (self, cmd, name, i, header = "") :
        if i < cmd._min_args :
            return name
        else :
            return "%s[%s]" % (header, name)
    # end def _fmt_arg_usage

    def _fmt_arg (self, cmd, name, i, header = "") :
        if i < cmd._min_args :
            return name
        else :
            return "%s[%s]" % (header, name)
    # end def _fmt_arg

    def _add_rest_args (self, cmd, result) :
        max_args = cmd._max_args
        for i in range (len (cmd.argument), min (8, max_args)) :
            result.append (self._fmt_arg (cmd, "arg-%d" % (i + 1), i))
        if max_args > 8 :
            result.append \
                ( self._fmt_arg
                      (cmd, "arg-%d" % (max_args), max_args - 1, "...")
                )
        elif max_args == -1 :
            result [-1] = result [-1] + "..."
    # end def _add_rest_args

# end class _Help_

@pyk.adapt__bool__
class Command_Spec (TFL.Meta.Object) :
    """Define syntax for command-line options and arguments.

       The constructor takes the arguments:

       - the list of possible options `option_spec'
       - the list of possible arguments `arg_spec' (matched positionaly)
             This is optional. If given, it is used for providing default
             arguments, converting arguments to internal data types and
             providing help
       - the minimum number of arguments required `min_args'
       - the maximum number of arguments allowed  `max_args'
         (the default -1 means an unlimited number is allowed)
       - a description of the command to be included in the `help'
         (this can be a string or a list of strings which will be joined
         by `\n')

       An option spec can be a string or an instance of `Opt'.

       Each string-valued option_spec starts with a name. If the option
       requires an argument, the name must be followed by `:', `=', `#' or
       `?' (if all are given, `:' must be first, `=' second, `#' third, and
       `?' last). If the option value must be of a certain type, a type
       specifier must follow the `:' (the value is automatically converted to
       this type in this case). A default value for the option can follow the
       `='. If the option cannot occur more than `n' times in the command
       line, the maximum number `n' must follow the `#' (the default is that
       an option can occur only once, `#0' means that there is no
       constraint). Any text following the `?' is used for providing help for
       the option.

       Possible type specifiers are:

           'B'  : boolean
           'F'  : float
           'I'  : integer
           'L'  : list
           'P'  : path (file or directory name)
           'S'  : string
           'T,' : string (will be split at `,' to give a list)
           'T ' : string (will be split at ` ' to give a list)
           'U'  : unsigned
           'X'  : long converted with `long (<value>, 0)`

       For instance, `foo:I=bar#3' specifies an option named `foo' requiring
       an argument with default `bar' which must not occur more than 3 times.

       For all option types except `S', if the value specified on the command
       line contains commas, it is assumed to be a list of values. To be able
       to use this feature, `#' must be specified for the option, too.

       Appending a `,' or a ` ' to a type specifier allows autosplitting (the
       specified character is used for splitting). In this case `#0' is
       automatically assumed.

       The options are available in the attribute `option'. This is a hash
       table providing one entry of type `Opt' per option.

       An arg_spec can be a string or an instance of `Arg'.
       Each string-valued arg_spec has the same structure as an option_spec
       with the exception of `#', `?' and `S,'.
    """

    type_specifiers = dict \
        ( B         = "boolean"
        , F         = "float"
        , I         = "integer"
        , L         = "list"
        , P         = "path"
        , S         = "string"
        , T         = "string (with auto-split)"
        , U         = "unsigned"
        , X         = "long"
        )

    arg_spec_pat = Regexp \
        ( """ (?P<name> [^:= ]+) """
          """ (?: :  (?P<type> [FILPSUX])?)? """
          """ (?: =  (?P<default> [^?]*))? """
          """ (?: \? (?P<help>    .+   ))? """
          """ $ """
        , re.X | re.I | re.S
        )
    opt_pat      = Regexp \
        ( """ -{1,2} (?P<name> [^:= ]+) """
          """ (?: = ["']? (?P<value> .*) ['"]? )? """
          """ $ """
        , re.X | re.I
        )
    opt_spec_pat = Regexp \
        ( """ -{0,2} (?P<name> [^:=# ]+) """
          """ (?:         : """
          """    (?P<type> [FILPSUXB]"""
          """       (?P<auto_split> [, :]?) """
          """    )? """
          """ )? """
          """ (?P<valued> = (?P<default>   [^\#?]* ))? """
          """ (?:        \# (?P<max_occur> \d+     ))? """
          """ (?:        \? (?P<help>      .+      ))? """
          """ $ """
        , re.X | re.I | re.S
        )
    keyw_arg_pat = Regexp \
        ( """\s*"""
          """(?P<name> [^= ]+)"""
          """\s* [=] \s* """
          """(?P<value> .*)"""
        , re.X | re.I
        )

    def __init__ ( self
                 , option_spec  = ()
                 , arg_spec     = ()
                 , min_args     = 0
                 , max_args     = -1
                 , description  = ""
                 ) :
        if not isinstance (description, pyk.string_types) :
            description= "\n".join (description)
        if isinstance (option_spec, pyk.string_types) :
            option_spec       = (option_spec, )
        if isinstance (arg_spec, pyk.string_types) :
            arg_spec          = (arg_spec, )
        self._min_args        = min_args
        self._max_args        = \
            (-1, max (max_args, len (arg_spec))) [max_args >= 0]
        self._description     = description
        self._setup (arg_spec, option_spec)
    # end def __init__

    def _setup (self, arg_spec, option_spec) :
        self._setup_arg  (arg_spec)
        self._setup_opt  (option_spec)
    # end def _setup

    def _setup_arg (self, arg_spec) :
        self.argn        = 0
        self.argument    = TFL.PL_List (undefined = Arg ())
        self.arg_dict    = TFL.PL_Dict (undefined = Arg ())
        self.argv        = TFL.PL_List (undefined = "")
        self.argd        = TFL.PL_Dict (undefined = "")
        for a in arg_spec :
            if isinstance (a, Arg) :
                arg  = a
            else :
                if self.arg_spec_pat.match (a) :
                    match_group = self.arg_spec_pat.group
                    arg = Arg \
                        ( name        = match_group ("name")
                        , type        = match_group ("type")
                        , default     = match_group ("default")
                        , description = match_group ("help")
                        )
                else :
                    raise Cmd_Error  ("Invalid arg-spec: `%s'" % a)
            self.argument.append     (arg)
            self.argv.append         (arg.value)
            self.arg_dict [arg.name] = arg
    # end def _setup_arg

    def _setup_opt (self, option_spec) :
        self.optn    = 0
        self.option  = TFL.Abbr_Key_Dict ()
        for o in option_spec :
            if isinstance (o, Opt) :
                opt = o
            else :
                if self.opt_spec_pat.match (o) :
                    match_group = self.opt_spec_pat.group
                    opt = Opt \
                        ( name        = match_group ("name")
                        , type        = match_group ("type")
                        , default     = match_group ("default")
                        , description = match_group ("help")
                        , valued      = match_group ("valued")
                        , max_occur   = match_group ("max_occur")
                        , auto_split  = match_group ("auto_split")
                        )
                else :
                    raise Cmd_Error ("Invalid option-spec: `%s'" % o)
            self.option [opt.name] = opt
    # end def _setup_opt

    def help (self) :
        return str (_Help_ (self))
    # end def help

    def __bool__ (self) :
        return 1
    # end def __bool__

# end class Command_Spec

class Command_Line (Command_Spec) :
    """Provide access to command line arguments and options in `sys.argv'.

       The constructor takes the same arguments as Command_Spec, plus:

           - the flag `help_on_err' specifies if a help message is displayed
             when the command line does not fit the specification
           - exc_on_err specifies which exception to raise when an error
             occurs (if `help_on_err' is set and no value for `exc_on_err' is
             given, then SystemExit is raised, if `help_on_err' is not set,
             the default for `exc_on_err' is Cmd_Error)

       The options are available in the attribute `option'. This is a hash
       table providing one entry of type `Opt' per option.

       The easiest way to access argument values is the function `arg' which
       takes an index or a name as parameter and returns the corresponding
       command line argument. The function `arg_pos' returns the position of
       the specified command line argument (taking into account the options,
       too).

       In addition, the arguments are available in the attributes `argv',
       `argd', `argument', and `arg_dict'. `argv' is a list of the values
       given in the command line, `argd' is a dictionary of the values given
       in the command line, `argument' is a list of `Arg' objects.
       `arg_dict' is a dictionary of `Arg' objects -- the dictionary
       keys are the names of the arguments as specified in `arg_spec'.

       The number of parameters specified is given by `argn'.

       Both `argv' and `argument' are instances of `PL_List', i.e., if you
       reference an undefined index, you get an `undefined' value instead of
       an exception.

       The path and name of the python __main__ module are provided by the
       attributes with the corresponding `script_path' and `script_name'.
    """

    ### stores the first instance of `Command_Line' created by a python
    ### program
    instance = None

    def __init__ ( self
                 , option_spec      = ()
                 , arg_spec         = ()
                 , min_args         = 0
                 , max_args         = -1
                 , description      = ""
                 , help_on_err      = 1
                 , exc_on_err       = 0
                 , arg_array        = None
                 , process_keywords = 0
                 ) :
        self.__super.__init__ \
            (option_spec, arg_spec, min_args, max_args, description)
        if not Command_Line.instance :
            Command_Line.instance = self
        if arg_array is None :
            arg_array = sys.argv
        elif not arg_array :
            return
        if arg_array != sys.argv :
            arg_array = [None] + arg_array
        self.keywords = {}
        self.process_keywords = process_keywords
        try :
            i, j, n = 1, 0, len (arg_array)
            while i < n :
                arg = arg_array [i]
                if arg == "--" :
                    self._finish (i + 1, n, j, arg_array)
                    break
                if self.opt_pat.match (arg) :
                    match_group = self.opt_pat.group
                    name  = match_group ("name")
                    value = match_group ("value")
                    hpat  = re.escape   (name)
                    try :
                        option = self.option [name]
                    except KeyError :
                        if re.match (hpat, "help") or re.match (hpat, "?") :
                            print (self.help ())
                            if i == 1 and n == 2 :
                                raise SystemExit
                        else :
                            matching = self.option.matching_keys (name)
                            if matching and not name [:2] == "__" :
                                raise Cmd_Error \
                                    ( "\nAmbiguous option `%s' matches %s\n"
                                    % (name, matching)
                                    )
                            else :
                                raise Cmd_Error ("Unknown option `%s'" % name)
                    else :
                        option = self.option [name]
                        if (option.valued and (not value) and (i + 1 < n)) :
                            i     = i + 1
                            value = arg_array [i]
                            if value and self.opt_pat.match (value) :
                                value = None
                        option.set_value (value, i)
                        self.optn = self.optn + 1
                else :
                    j = self._handle_arg (arg, i, j)
                i = i + 1
            # end while i < n
            ### assert (self.argn == j)
            if self._max_args >= 0 and self.argn > self._max_args :
                raise Cmd_Error \
                    ( "%s doesn't accept more than %d arguments"
                    % (self.script_name, self._max_args)
                    )
            if self.argn < self._min_args :
                raise Cmd_Error \
                    ( "%s requires at least %d arguments"
                    % (self.script_name, self._min_args)
                    )
        except KeyboardInterrupt :
            raise
        except Exception as exc :
            print (exc)
            if help_on_err :
                sys.stderr.write ("\n%s\n" % (self.help (), ))
                exc_on_err = exc_on_err or self.exc_on_err
                if not exc_on_err :
                    raise SystemExit
            raise
    # end def __init__

    exc_on_err = 0

    def __str__ (self) :
        return "%s" % (self.argv.body, )
    # end def __str__

    def arg (self, index_or_name) :
        """Returns the value of the argument `index_or_name'."""
        if isinstance (index_or_name, pyk.int_types) :
            return self.argv     [index_or_name]
        elif isinstance (index_or_name, pyk.string_types) :
            return self.arg_dict [index_or_name].value
        else :
            raise KeyError (index_or_name)
    # end def arg

    def arg_pos (self, index_or_name) :
        """Returns the position of the argument `index_or_name' in the
           command line. (The position takes into account options and
           arguments).
        """
        if isinstance (index_or_name, pyk.int_types) :
            return self.argv     [index_or_name].pos
        elif isinstance (index_or_name, pyk.string_types) :
            return self.arg_dict [index_or_name].pos
        else :
            raise KeyError (index_or_name)
    # end def arg_pos

    def key_value (self, name) :
        """Returns the value of the keyword parameter `name'."""
        if name in self.keywords :
            return self.keywords [name]
        else :
            return TFL.sos.environ.get (name, "")
    # end def key_value

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return self._attribute_value (name)
    # end def __getattr__

    def __getitem__ (self, index) :
        if isinstance (index, pyk.int_types) :
            return self.arg (index)
        else :
            try :
                return self._attribute_value (index)
            except AttributeError :
                raise KeyError (index)
    # end def __getitem__

    def _attribute_value (self, name) :
        if self.option.really_has_key (name) :
            result = self.option [name]
            if not result.valued :
                return result.pos
            elif not result.list_p :
                return result.value_1 ()
            else :
                return result.values  ()
        elif name in self.arg_dict :
            return self.arg_dict [name].value
        _name = "_" + name
        if _name [:2] != "__" and hasattr (self, _name) :
            return getattr (self, _name)
        if name in self.keywords :
            return self.keywords [name].value
        raise AttributeError (name)
    # end def _attribute_value

    def _finish (self, i, n, j, arg_array) :
        while i < n :
            j = self._handle_arg (arg_array [i], i, j)
            i = i + 1
    # end def _finish

    def _handle_arg_1 (self, arg, i, j) :
        if j >= len (self.argument.body) :
            self.argument [j] = Arg ()
        self.argument [j].set_value (arg, i)
        name             = self.argument [j].name
        self.argv [j]    = self.argument [j].value
        self.argd [name] = self.argument [j].value
        return j + 1
    # end def _handle_arg_1

    def _handle_arg (self, arg, i, j) :
        if self.process_keywords and self.keyw_arg_pat.match (arg) :
            key                 = self.keyw_arg_pat.group ("name")
            value               = self.keyw_arg_pat.group ("value")
            self.keywords [key] = value
        else :
            self.argn = self.argn + 1
            if (   j == len (self.argument.body) - 1
               and self.argument [j].type in "IUX"
               and Arg.range_pat.match (arg)
               ) :
                cook  = self.argument [j].cook
                rp    = Arg.range_pat
                for k in range (cook (rp.head), cook (rp.tail) + 1) :
                    j = self._handle_arg_1 (k, i, j)
            else :
                j = self._handle_arg_1 (arg, i, j)
        return j
    # end def _handle_arg

    def _setup (self, arg_spec, option_spec) :
        self.script_name = TFL.Environment.script_name ()
        self.script_path = TFL.Environment.script_path ()
        Command_Spec._setup (self, arg_spec, option_spec)
    # end def _setup

# end class Command_Line

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Command_Line
