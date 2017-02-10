# coding: utf-8
import inspect

import enum

from tvu._compat import text


class TVU(object):

    TYPES = (object,)

    def __init__(self, variable_name=None):
        self._variable_name = \
            variable_name or self.__class__.__name__ + u'() argument'

    def _type_name(self, type_):
        return type_.__name__

    def type_check(self):
        value = self._value
        types = self.__class__.TYPES
        if isinstance(value, types):
            return

        if len(types) == 1:
            possible_types_string = self._type_name(types[0])
        else:
            possible_types_string = \
                u', '.join([self._type_name(type_) for type_ in types[:-1]]) \
                + u' or ' + self._type_name(types[-1])

        err_msg = u'%s must be %s, not %s' % (self._variable_name,
                                              possible_types_string,
                                              text(self._value))
        raise TypeError(err_msg)

    def unify_validate(self, value):
        self._value = value
        self.type_check()
        unified_value = self.unify(self._value)
        self.validate(unified_value)
        return unified_value

    def error(self, msg, soft=False):
        word = u'could' if soft else u'must'
        full_msg = (u'%s %s be ' + msg + u', not: %s') % \
            (self._variable_name, word, text(self._value))
        raise ValueError(full_msg)

    def unify(self, value):
        return value

    def validate(self, value):
        pass


def validate_and_unify(**arg_validators):
    def wrapper(fun):
        spec_args, spec_varargs, spec_keywords, spec_defaults = \
            inspect.getargspec(fun)

        def inner_wrapper(*args, **kwargs):
            args_values = inspect.getcallargs(fun, *args, **kwargs)
            for arg in args_values:
                try:
                    validator = arg_validators[arg]
                except KeyError:
                    pass
                else:
                    args_values[arg] = \
                        validator(arg).unify_validate(args_values[arg])

            new_args = []

            # TODO: support default arguments
            try:
                for arg in spec_args:
                    new_args.append(args_values.pop(arg))
                if spec_varargs is not None:
                    new_args += args_values.pop(spec_varargs)
            except KeyError:
                raise TypeError()
            if spec_keywords is not None:
                kwargs = args_values.pop(spec_keywords)
                for key, val in kwargs.items():
                    args_values[key] = val

            return fun(*new_args, **args_values)
        return inner_wrapper
    return wrapper


class EnumTVU(TVU):

    def _get_enum_type(self):
        for type_ in self.TYPES:
            if issubclass(type_, enum.Enum):
                return type_

    def type_check(self):
        value = self._value
        if isinstance(value, str):
            enum_type = self._get_enum_type()
            try:
                self._value = getattr(enum_type, value)
            except AttributeError:
                msg = enum_type.__name__ + u"'s variant name"
                self.error(msg, soft=True)
            return
        super(EnumTVU, self).type_check()


def instance(class_, enum=False):
    base = EnumTVU if enum else TVU

    class InstanceTVU(base):
        TYPES = (class_,)

    return InstanceTVU


def nullable(tvu):

    class NullableTVU(tvu):
        TYPES = tvu.TYPES + (type(None),)

        def _type_name(self, type_):
            if isinstance(None, type_):
                return 'None'
            else:
                return super(NullableTVU, self)._type_name(type_)

        def unify(self, value):
            if value is None:
                return value
            return super(NullableTVU, self).unify(value)

        def validate(self, value):
            if value is None:
                return
            super(NullableTVU, self).validate(value)

        def error(self, err_msg):
            err_msg = u'None or ' + err_msg
            return super(NullableTVU, self).error(err_msg)

    return NullableTVU
