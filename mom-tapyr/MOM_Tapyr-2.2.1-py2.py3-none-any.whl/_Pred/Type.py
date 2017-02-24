# -*- coding: utf-8 -*-
# Copyright (C) 2009-2016 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package MOM.Pred.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.Pred.Type
#
# Purpose
#    Model predicate types of MOM meta object model
#
# Revision Dates
#     1-Oct-2009 (CT) Creation (factored from TOM.Pred.Type)
#    21-Oct-2009 (CT) `attr_none` added to `Attribute_Check`
#    26-Nov-2009 (CT) Use `except ... as ...` (3-compatibility)
#     3-Dec-2009 (CT) `set_s_attr_value` changed to apply `attr.cooked` to
#                     values taken from `attr_dict`
#                     * 3-compatibility: passing a `str` for an attribute of
#                       type `float` breaks checks like `value > 0`
#    21-Jan-2010 (CT) `set_s_attr_value` changed to not call `cooked` for `None`
#    25-Feb-2010 (CT) `check_always` added
#    11-Mar-2010 (CT) `check_always` removed (was a Bad Idea (tm))
#    22-Jun-2010 (CT) `is_mandatory` added
#     8-Feb-2011 (CT) s/Mandatory/Required/
#     8-Nov-2011 (CT) Factor `Error_Type` and allow `** kw` in `Attribute_Check`
#    15-Apr-2012 (CT) Adapted to changes of `MOM.Error`
#    16-Apr-2012 (CT) Simplify `_Quantifier_._satisfied`, `._is_correct`
#    16-Apr-2012 (CT) Add `val_disp` containing FO-formatted attribute values
#    16-Apr-2012 (CT) Convert `error_info` and `extra_links` to property
#    17-Apr-2012 (CT) Remove `val_desc`, use `val_disp` instead
#    27-Apr-2012 (CT) Add argument `obj` to `_add_entities_to_extra_links`
#    12-Aug-2012 (CT) Add `Unique`
#    12-Aug-2012 (CT) Adapt to export-change of `MOM.Meta.M_Pred_Type`
#    10-Sep-2012 (CT) Move `do_check` fo `_Condition_`
#    11-Sep-2012 (CT) Change `Unique` to use `attr_none`, not `attributes`
#    30-Jan-2013 (CT) Add `Unique.ems_check`
#    30-Jan-2013 (CT) Change `Unique.satisfied` and `_query_filters` to
#                     use `_val_dict`
#    30-Jan-2013 (CT) Change `Unique.satisfied` to query `epk_sig_root`
#    26-Feb-2013 (CT) Fix `set_c_attr_value` for case that `result` is taken
#                     from `val_dict`, not `obj`
#    11-Mar-2013 (CT) Derive `_Condition_` from `MOM.Prop.Type`, not `object`
#     3-Jun-2013 (CT) Print exception info to stderr, not stdout
#     3-Apr-2014 (CT) Change `set_c_attr_value` to use `obj.FO`, not `r0.FO`
#     3-Sep-2014 (CT) Change `set_s_attr_value` to use `attr.prop`, not
#                     `hasattr (obj, name)`
#    10-Oct-2014 (CT) Use `portable_repr`
#     2-Apr-2015 (CT) Don't put `FO` object into `val_disp`,
#                     convert them with `pyk.text_type` to string
#    15-Aug-2015 (CT) Add stub for `_Condition_.predicates`
#    25-Feb-2016 (CT) Improve automatic `__doc__` of `New_Pred`
#    21-Jun-2016 (CT) Add missing import for `flattened`
#    21-Jun-2016 (CT) Allow `callable` bindings
#    22-Jun-2016 (CT) Change `satisfied` to use `ui_display`,
#                     not `portable_repr`
#    10-Aug-2016 (CT) Add `Exclude`, factor `_Unique_`
#                     + factor `_auto_doc`, `_query_filters_xs`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals, print_function

from   _MOM                  import MOM
from   _TFL                  import TFL

from   _MOM._Attr.Filter     import Q

import _MOM._Meta.M_Pred_Type
import _MOM._Pred
import _MOM._Prop.Type
import _MOM.Error

from   _TFL.I18N             import _, _T
from   _TFL.portable_repr    import portable_repr
from   _TFL.predicate        import callable, flattened
from   _TFL.pyk              import pyk
from   _TFL.ui_display       import ui_display

import _TFL._Meta.Object
import _TFL.Caller
import _TFL.d_dict

import traceback

@pyk.adapt__bool__
class _Condition_ \
          ( TFL.Meta.BaM
              ( MOM.Prop.Type
              , metaclass = MOM.Meta.M_Pred_Type._Condition_
              )
          ) :
    ### Base class for all predicates (atomic and quantifiers).

    assertion       = ""
    assert_code     = None
    attributes      = ()
    attr_none       = ()
    bindings        = {}
    description     = ""
    explanation     = ""
    _extra_links_s  = ()
    guard           = None
    guard_attr      = ()
    guard_code      = None
    is_required     = False ### set by meta machinery
    kind            = None
    parameters      = ()
    predicates      = None  ### set by meta machinery: nested predicates, if any
    rank            = 1
    renameds        = ()    ### only for compatibility with MOM.Attr.Type
    severe          = True

    ### DBW backend may set `do_check` to `False` if database performs the check
    do_check = True

    def __init__ (self, kind, obj, attr_dict = {}) :
        self.kind           = kind
        self.obj            = obj
        self.attr_dict      = attr_dict
        self.val_dict       = {}
        self.val_disp       = {}
        self.error          = None
        self._error_info    = []
        self._extra_links_d = []
        if self.do_check :
            self.satisfied (obj, attr_dict)
    # end def __init__

    @property
    def error_info (self) :
        """Additional information about the object violating the predicate.

           Override when necessary.
        """
        return self._error_info
    # end def error_info

    @property
    def extra_links (self) :
        """Additional links to be displayed."""
        return tuple (self._extra_links_d) + tuple (self._extra_links_s)
    # end def extra_links

    def satisfied (self, obj, attr_dict = {}) :
        """Checks if `obj' satisfies the predicate.
           `attr_dict' can provide values for `self.attributes'.

           If there is a `self.guard' the predicate is checked only if
           `self.guard' evaluates to true.
        """
        glob_dict = obj.globals ()
        if not self._guard_open (obj, attr_dict, glob_dict) :
            return True
        val_disp = self.val_disp = {}
        val_dict = self.val_dict = self._val_dict (obj, attr_dict)
        if not val_dict :
            return True
        for p in self.parameters :
            exc, val = self._eval_expr \
                (p, obj, glob_dict, val_dict, "parameter")
            if val is None or exc is not None :
                return True
            val_disp [p] = val if val is None else ui_display (val)
        for b, expr in pyk.iteritems (self.bindings) :
            if callable (expr) :
                val  = expr
                disp = "%s" % (ui_display (val), )
            else :
                exc, val = self._eval_expr \
                    (expr, obj, glob_dict, val_dict, "binding")
                if exc is not None :
                    return True
                disp = "%s << %s" % (ui_display (val), expr)
            val_dict [b] = val
            val_disp [b] = disp
        return self._satisfied (obj, glob_dict, val_dict)
    # end def satisfied

    def set_attr_value (self, obj, dict, attr, val_dict) :
        if "." in attr :
            return self.set_c_attr_value (obj, dict, attr, val_dict)
        else :
            return self.set_s_attr_value (obj, dict, attr, val_dict)
    # end def set_attr_value

    def set_c_attr_value (self, obj, dict, c_attr, val_dict) :
        attr, tail  = c_attr.split (".", 1)
        result      = self.set_s_attr_value (obj, dict, attr, val_dict)
        for a in tail.split (".") :
            if result is None :
                return None
            if hasattr (result, a) or (attr in self.attr_none) :
                result = getattr (result, a, None)
            else :
                raise AttributeError \
                    ( "Invalid predicate: references undefined attribute "
                      "`%s'\n    %s: %s"
                    % (attr, obj, self.assertion)
                    )
        if result is not None :
            if tail :
                self.val_disp [c_attr] = pyk.text_type (obj.FO (c_attr, result))
        return result
    # end def set_c_attr_value

    def set_s_attr_value (self, obj, dict, name, val_dict) :
        result = None
        attr   = obj.attr_prop (name)
        if name in dict :
            result = dict [name]
            if attr is not None and result is not None :
                try :
                    result = attr.cooked (result)
                except Exception as exc :
                    print \
                        ( "Error in `cooked` of `%s` for value `%s` [%s]"
                        % (attr, result, obj)
                        )
                    raise
        elif attr is not None or (name in self.attr_none) :
            result = self.kind.get_attr_value (obj, name)
        else :
            raise AttributeError \
                ( "Invalid predicate `%s` references undefined attribute `%s`"
                  "\n    %s:"
                  "\n    %s"
                % (self.name, name, obj, self.assertion)
                )
        val_dict [name] = result
        self.val_disp [name] = pyk.text_type (obj.FO (name, result))
        return result
    # end def set_s_attr_value

    def _add_entities_to_extra_links (self, obj, lst) :
        self._extra_links_d.extend \
            (e for e in lst if isinstance (e, MOM.Entity.Essence))
    # end def _add_entities_to_extra_links

    def _eval_expr (self, expr, obj, glob_dict, val_dict, kind, text = None) :
        try :
            val = eval (expr, glob_dict, val_dict)
        except Exception as exc :
            print \
                ( "Exception `%s` in %s `%s` of %s for predicate %s"
                % (exc, kind, text or expr, obj, self)
                )
            return exc, True
        return None, val
    # end def _eval_expr

    def _guard_open (self, obj, attr_dict, glob_dict) :
        result = True
        if self.guard :
            val_dict = {"this" : obj}
            for a in self.guard_attr :
                try :
                    self.set_attr_value (obj, attr_dict, a, val_dict)
                except Exception :
                    ### allow guards accessing global objects to fail
                    pass
            exc, result = self._eval_expr \
                (self.guard_code, obj, glob_dict, val_dict, "guard", self.guard)
        return result
    # end def _guard_open

    def _val_dict (self, obj, attr_dict = {}) :
        result = dict (this = obj)
        for a in self.attributes :
            if self.set_attr_value (obj, attr_dict, a, result) is None :
                return {}
        for a in self.attr_none :
            self.set_attr_value (obj, attr_dict, a, result)
        return result
    # end def _val_dict

    def __bool__ (self) :
        return not self.error
    # end def __bool__

    def __repr__ (self) :
        if self.error :
            return "%s"    % (self.error, )
        else :
            return "%s %s" % (self.name, "satisfied")
    # end def __repr__

# end class _Condition_

class Condition \
          ( TFL.Meta.BaM
              ( _Condition_
              , metaclass = MOM.Meta.M_Pred_Type.Condition
              )
          ) :
    """A predicate defined by a simple assertion."""

    Error_Type    = MOM.Error.Invariant

    def eval_condition (self, obj, glob_dict, val_dict) :
        """Do **not** override this function directly!

           If you really need a function to compute the predicate,
           define `assert_function` (see
           `eval_condition_assert_code_as_function`).
        """
        return eval (self.assert_code, glob_dict, val_dict)
    # end def eval_condition

    def eval_condition_assert_code_as_function (self, obj, glob_dict, val_dict) :
        """Use `eval_condition = eval_condition_assert_code_as_function` in
           descendent classes which want to define a function `assert_function`
           to evaluate the predicate.

           Think thrice before specifying `assert_function` instead of
           `assertion` -- whenever `assertion` does the job, it should
           be used (it's far simpler, it's useful as documentation, it
           provides more information about the error).

           Such an `assert_function` is called in a non-standard way to
           pass in the right parameters. The object to be checked is
           available as `this`, the predicate itself as `self` and the
           `attributes`, `attr_none`, and `parameters` as specified in the
           predicate definition.
        """
        ### I used to pass `glob_dict` and `val_dict` to `eval` but somehow
        ### that didn't work as expected -- the called function had empty
        ### `locals ()` and therefore crashed and burned with `NameError`s
        return eval \
            ( self.assert_function.__func__.func_code
            , TFL.d_dict (val_dict, glob_dict, self = self)
            )
    # end def eval_condition_assert_code_as_function

    def _satisfied (self, obj, glob_dict, val_dict) :
        """Checks if `obj' satisfies the predicate.
           `attr_dict' can provide values for `self.attributes'.
        """
        try    :
            if self.eval_condition (obj, glob_dict, val_dict) :
                self.error = None
            else :
                self._add_entities_to_extra_links (obj, [])
                self.error = self.Error_Type (obj, self)
        except Exception as exc :
            print \
                ( "Exception `%s` in evaluation of predicate `%s` for %s"
                % (exc, self.name, obj)
                )
            self.error = self.Error_Type (obj, self)
        return not self.error
    # end def _satisfied

# end class Condition

class _Quantifier_ \
          ( TFL.Meta.BaM
              ( _Condition_
              , metaclass = MOM.Meta.M_Pred_Type.Quantifier
              )
          ) :
    ### Base class for quantifier predicates of the MOM object model.

    Error_Type      = MOM.Error.Quant

    attr_code       = None
    """code object for displaying attribute values of violating sequence
       elements.
       """
    bvar            = None
    bvar_attr       = ()
    seq             = None
    seq_code        = None ### code object for `seq`

    def _attr_val (self, obj, res, seq, glob_dict, val_dict) :
        violators = []
        v_values  = []
        if self.attr_code is not None :
            info = self._eval_over_seq \
                (seq, self.attr_code, glob_dict, val_dict)
            for r, s, i in zip (res, seq, info) :
                if self._is_violator (r, res) :
                    violators.append (s)
                    v_values.append  (i)
        else :
            for r, s in zip (res, seq) :
                if self._is_violator (r, res) :
                    violators.append (s)
            v_values = []
        return violators, v_values
    # end def _attr_val

    def _eval_over_seq (self, seq, code, glob_dict, val_dict) :
        if seq :
            val_dict ["seq"] = seq
            res = eval (code, glob_dict, val_dict)
            del val_dict ["seq"]
        else :
            res = ()
        return res
    # end def _eval_over_seq

    def _quantified (self, seq, obj, glob_dict, val_dict) :
        return self._eval_over_seq (seq, self.assert_code, glob_dict, val_dict)
    # end def _quantified

    def _q_sequence (self, obj, glob_dict, val_dict) :
        try :
            return list (eval (self.seq_code, glob_dict, val_dict))
        except Exception as exc :
            if __debug__ :
                import sys
                print ("Exception in _q_sequence", self, obj, file = sys.stderr)
                traceback.print_exc ()
            return ()
    # end def _q_sequence

    def _satisfied (self, obj, glob_dict, val_dict) :
        ###+ the `gd` hackery is necessary for the `eval` of `self.attr_code`
        gd = glob_dict.copy ()
        gd.update (val_dict)
        ###-
        try :
            seq = self._q_sequence (obj, gd, val_dict)
            res = self._quantified (seq, obj, gd, val_dict)
        except Exception as exc :
            self.val_disp ["*** Exception ***"] = portable_repr (exc)
            self.error = self.Error_Type (obj, self)
        else :
            if self._is_correct (r for r in res if r) :
                self.error = None
            else :
                violators, violator_values = self._attr_val \
                    (obj, res, seq, gd, val_dict)
                vs = violators
                if "," in self.bvar :
                    vs = flattened (violators)
                self._add_entities_to_extra_links (obj, vs)
                self.error = self.Error_Type \
                    (obj, self, violators, violator_values)
        return not self.error
    # end def _satisfied

# end class _Quantifier_

class E_Quant (_Quantifier_) :
    """A predicate defined by an existential quantifier over a set of
       values or objects.
    """

    def _is_correct (self, res) :
        return any (res)
    # end def _is_correct

    def _is_violator (self, result, res_seq) :
        return not result
    # end def is_violator

# end class E_Quant

class N_Quant \
          ( TFL.Meta.BaM
              ( _Quantifier_
              , metaclass = MOM.Meta.M_Pred_Type.N_Quantifier
              )
          ) :
    """A predicate defined by a numeric quantifier over a set of
       values or objects.
    """

    lower_limit = None
    upper_limit = None

    def _is_correct (self, res) :
        return self.lower_limit <= len (tuple (res)) <= self.upper_limit
    # end def _is_correct

    def _is_violator (self, result, res_seq) :
        if len (res_seq) < self.lower_limit :
            return not result
        else :
            return result
    # end def is_violator

# end class N_Quant

class U_Quant \
          ( TFL.Meta.BaM
              ( _Quantifier_
              , metaclass = MOM.Meta.M_Pred_Type.U_Quantifier
              )
          ) :
    """A predicate defined by an universal quantifier over a set of
       values or objects.
    """

    def _is_correct (self, res) :
        return not any (res)
    # end def _is_correct

    def _is_violator (self, result, res_seq) :
        return result
    # end def is_violator

# end class U_Quant

class _Unique_ (_Condition_) :
    """Common base class for `Unique` and `Exclude`"""

    ems_check   = True

    @classmethod
    def New_Pred (cls, * attrs, ** kw) :
        """Return a new predicate class for the attributes specified by `attrs`.

        The keyword arguments can specify any properties of
        :class:`_Condition_` (except `attributes` and `attr_none`), plus:

        .. attribute:: name_suffix

          :attr:`name` will be derived from `cls.Kind_Cls.typ`, i.e., either
          "unique" or `exclude`, and the value of `name_suffix`.

        .. attribute:: __doc__

          A docstring describing the predicate. By default, the docstring is
          computed by the class's :meth:`_auto_doc`.

        .. attribute:: __module__

          The name of the module defining the class. By default, the module
          name of the caller is used.

        """
        name = kw.get ("name")
        if not name:
            suffix = kw.pop ("name_suffix", None) or \
                "__" + "___".join (a.replace (".", "__") for a in attrs)
            name = "%s_%s" % (cls.Kind_Cls.typ, suffix, )
        if not kw.get ("__doc__") :
            kw ["__doc__"] = cls._auto_doc (attrs, kw)
        if not kw.get ("__module__") :
            kw ["__module__"] = TFL.Caller.globals () ["__name__"]
        kw.update (attr_none = attrs)
        return cls.__class__ (name, (cls, ), kw)
    # end def New_Pred

    @classmethod
    def _auto_doc (cls, attrs, kw) :
        """Auto-compute docstring for predicate over `attrs`."""
        return  \
            ( _ ("The attribute values for %s must be %s for each object")
            % ( portable_repr (attrs) if len (attrs) > 1
                  else portable_repr (attrs [0])
              , cls.Kind_Cls.typ
              )
            )
    # end def _auto_doc

    def satisfied (self, obj, attr_dict = {}) :
        self.val_disp = {}
        self.val_dict = val_dict = self._val_dict (obj, attr_dict)
        qfs      = self._query_filters (obj, val_dict)
        scope    = obj.home_scope
        ETM      = scope [obj.E_Type.epk_sig_root.type_name]
        q        = ETM.query (* qfs)
        result   = q.count () == 0
        if not result :
            self._extra_links_d = self.clashes = \
                sorted (q.all (), key = obj.E_Type.sort_key)
            self.error = self.Error_Type (obj, self)
        return result
    # end def satisfied

    def _query_filters (self, obj, val_dict) :
        result = []
        if obj.pid :
            result.append (Q.pid != obj.pid)
        attr_values = tuple (val_dict [a] for a in self.attr_none)
        result.extend (self._query_filters_xs (attr_values))
        return result
    # end def _query_filters

# end class _Unique_

class Unique \
        (TFL.Meta.BaM (_Unique_, metaclass = MOM.Meta.M_Pred_Type.Unique)) :
    """A predicate defining a uniqueness constraint over a set of attributes.

    For Unique predicates, the predicate is evaluated even if some
    attributes have a value equal to `None`, i.e., all attributes must be
    listed in `attr_none`.

    DBW backend sets `ems_check` to `False` if database performs the check.

    .. automethod:: New_Pred

    .. automethod:: _auto_doc

       >>> print (Unique._auto_doc (('foo', ), {}))
       The attribute values for 'foo' must be unique for each object

       >>> print (Unique._auto_doc (('foo', 'bar'), {}))
       The attribute values for ('foo', 'bar') must be unique for each object

    """

    Error_Type  = MOM.Error.Not_Unique

    def _query_filters_xs (self, attr_values) :
        for aq, v in zip (self.aqs, attr_values) :
            yield aq == v
    # end def _query_filters_xs

# end class Unique

class Exclude \
        (TFL.Meta.BaM (_Unique_, metaclass = MOM.Meta.M_Pred_Type.Exclude)) :
    """A predicate defining an exclusion constraint over a set of attributes.

    For Exclude predicates, the predicate is evaluated even if some
    attributes have a value equal to `None`, i.e., all attributes must be
    listed in `attr_none`.

    DBW backend sets `ems_check` to `False` if the database performs the check.

    Exclude predicates are characterized by the additional property:

    .. automethod:: New_Pred

    .. automethod:: _auto_doc

       >>> print (Exclude._auto_doc (('foo', ), {}))
       The attribute values for 'foo' must be exclusive for each object

       >>> print (Exclude._auto_doc (('foo', 'bar'), {}))
       The attribute values for ('foo', 'bar') must be exclusive for each object

    .. attribute:: exclude_op_map

      A dictionary mapping attribute names to operation names.

      The operation names specified are applied to the :obj:`Q<_MOM.Q_Exp.Q>`
      instance corresponding to the attribute, i.e., one can specify all query
      functions supported by :mod:`Q-expressions<_TFL.Q_Exp>` here.

      Attributes not mapped by `exclude_op_map` are compared for equality.

    """

    Error_Type     = MOM.Error.Not_Exclude
    auto_index     = False
    exclude_op_map = {}

    _op_aliases    = dict \
        ( EQ       = "__eq__"
        , GE       = "__ge__"
        , GT       = "__gt__"
        , LE       = "__le__"
        , LT       = "__lt__"
        , NE       = "__ne__"
        )

    def _query_filters_xs (self, attr_values) :
        al_map = self._op_aliases
        op_map = self.exclude_op_map
        for aq, v in zip (self.aqs, attr_values) :
            name = aq._name
            try :
                op_name = op_map [name]
            except KeyError :
                yield aq == v
            else :
                op = getattr (aq, al_map.get (op_name, op_name))
                yield op (v)
    # end def _query_filters_xs

# end class Exclude

def Attribute_Check (name, attr, assertion, attr_none = (), ** kw) :
    attributes = () if attr_none else (attr, )
    try :
        result = MOM.Meta.M_Pred_Type.Condition \
            ( name, (Condition, )
            , dict
                ( assertion  = assertion.replace ("value", attr)
                , attributes = attributes
                , attr_none  = attr_none
                , __doc__    = " "
                    ### Space necessary to avoid inheritance of `Condition.__doc__`
                , ** kw
                )
            )
    except Exception :
        print ("%s [%s, %s] : `%s`" % (name, attr, attr_none, assertion))
    else :
        return result
# end def Attribute_Check

### «text» ### start of documentation
__doc__ = """
The module `MOM.Pred.Type` provides the framework for defining the
type of predicates of essential objects and links. There are five
different predicate types:

* :class:`Condition`: a simple assertion

* :class:`U_Quant`: a `universal quantifier`_

* :class:`E_Quant`: an `existential quantifier`_

* :class:`N_Quant`: a `numeric quantifier`_

* :class:`Unique`: a uniqueness constraint

* :class:`Exclude`: an exclusion constraint

Concrete predicates are specified by defining a class derived from the
appropriate predicate type, e.g., :class:`Condition` or :class:`U_Quant`.

.. class:: _Condition_()

    Base class for all predicates (atomic and quantifiers).

    Concrete predicates are characterized by the properties:

    .. attribute:: name

      Specified by the name of the class.

    .. attribute:: description

      A short description of the predicate in question.

      Normally specified via the doc-string of the
      class (but can also be defined by defining a class attribute
      `description`).

      `description` should be written in a way as to clearly explain to
      the user what is wrong when the predicate is violated and how the
      error can be fixed.

    .. attribute:: explanation

      A long description of the predicate in question
      (optional).

    .. attribute:: kind

      Refers to the specific class defining the
      :class:`~_MOM._Pred.Kind.Kind` of the predicate in question.

    .. attribute:: assertion

      A logical expression defining the constraint (specified
      as a string).

    .. attribute:: attributes

      List of names of the attributes constrained by the
      predicate.

      * The predicate is only evaluated if all `attributes` have a
        value differing from `None`.

      * The names listed can be dotted names, e.g., `a.b.c`.

    .. attribute:: attr_none

      List of names of the attributes constrained by the
      predicate.

      * The predicate is even evaluated if some elements of `attr_none` have
        a value of `None`.

      * The names listed can be dotted names, e.g., `a.b.c`.

    .. attribute:: bindings

      A dictionary of names to be bound to the results of
      epxressions usable in the :attr:`assertion`.

      * Judicious use of `bindings` can dramatically simplify :attr:`assertion`.

      * The name, the symbolic expression, and the calculated value of each
        binding will be displayed in the error message of the predicate.

    .. attribute:: guard

      A logical expression defining a guard for the predicate
      (specified as a string).

      * The predicate is only evaluated if `guard` evaluates to True.

    .. attribute:: guard_attr

      List of names of attributes used by :attr:`guard`.

      * The names listed can be dotted names, e.g., `a.b.c`.

    .. attribute:: parameters

      List of properties of other objects constrained by the
      predicate.

      * The predicate is only evaluated if all `parameters` have a
        value differing from `None`.

    .. attribute:: rank

      For each object, the predicates of a specific kind are
      evaluated in the sequence of `rank` (lower rank first).

      * If a predicate of a specific rank is violated, predicates of
        higher rank are not evaluated.

      * This can be used to avoid lots of spurious error messages that all
        follow from a violation of one (or a small set of) basic predicate(s).

    .. attribute:: severe

      Specifies whether a predicate describes an error condition
      or a warning (by default, it's an error).

    .. attribute:: _extra_links_s

      List of essential types to be hyperlinked in an
      error message for this predicate.

      * The names of these types must appear somewhere in :attr:`description`,
        :attr:`explanation`, or :attr:`assertion` for `_extra_links_s` to have a
        noticeable effect.

.. class:: _Quantifier_

    Concrete quantifier predicates are characterized by the additional
    required properties:

    .. attribute:: bvar

      A string listing the `bounded variables`_ of the quantified
      `assertion`.

      * Corresponds to the loop variables in a python loop.

    .. attribute:: bvar_attr

      A list of expressions referring to attributes of the bounded
      variables to be shown for violating elements of `seq`.

    .. attribute:: seq

      An expression defining the sequence over which `assertion` is
      quantified.

Namespace for evaluation of `assertion` (and `seq`)
----------------------------------------------------

* All names listed in :attr:`attributes`, :attr:`attr_none`, and
  :attr:`bindings` are available (and refer to the respective attributes of
  the object the predicate is checked for).

  - When an object predicate is checked before attributes of the
    object are changed, the names listed in :attr:`attributes` and
    :attr:`attr_none` refer to the values passed to `set` (or `set_raw`,
    `setattr`).

* All names listed in `parameters` are available (and refer to the
  respective objects taken from the global scope of the object's
  class).

* `this` refers to the object the predicate is checked for. Use of
  `this` should be avoided, when possible (e.g., by adding names to
  :attr:`attributes` or :attr:`attr_none`).

Namespace for evaluation of `guard`
-----------------------------------

* All names listed in :attr:`guard_attr`.

* `this` refers to the object the predicate is checked for.

.. _`universal quantifier`: http://en.wikipedia.org/wiki/Universal_quantifier
.. _`existential quantifier`: http://en.wikipedia.org/wiki/Existential_quantification
.. _`numeric quantifier`: http://en.wikipedia.org/wiki/Counting_quantification
.. _`bounded variables`: http://en.wikipedia.org/wiki/Bound_variable

"""

if __name__ != "__main__" :
    MOM.Pred._Export ("*", "_Condition_")
### __END__ MOM.Pred.Type
