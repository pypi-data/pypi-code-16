#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function
from __future__ import unicode_literals

from pytypeutil import StrictLevel
import pytypeutil
from pytypeutil.type import (
    Integer,
    RealNumber,
    String,
    NullString,
    Infinity,
    Nan,
)
import six


nan = float("nan")
inf = float("inf")


class Params(object):

    def __init__(self):
        self.strict_level = None
        self.typeclass = None

    def write_test_params(self, method, value):
        if isinstance(value, six.string_types):
            write_value = '"{:s}"'.format(value)
        else:
            write_value = value

        print('["{:s}", {:d}, {}, {}],'.format(
            method, self.strict_level,
            write_value,
            self.__exeute_method(method, value)))

    def __exeute_method(self, method, value):
        try:
            result = getattr(
                self.typeclass(value, self.strict_level), method)()
            if method == "validate":
                result = "-"
            """
            elif pytypeutil.type.RealNumber(result, StrictLevel.MIN).is_type():
                result = 'Decimal("{}")'.format(result)
            elif pytypeutil.type.Infinity(result, StrictLevel.MIN).is_type():
                result = 'Decimal("inf")'
            elif pytypeutil.type.Nan(result, StrictLevel.MIN).is_type():
                result = 'Decimal("nan")'
            """

        except (TypeError, pytypeutil.TypeConversionError):
            return '"E"'
            #result = 'EXCEPTION_RESULT'

        # for string tests
        if NullString(result, StrictLevel.MAX).is_type():
            return '""'

        typeobj = Integer(result, 1)
        if typeobj.is_type():
            return typeobj.convert()

        typeobj = RealNumber(result, 1)
        if typeobj.is_type():
            return typeobj.convert()

        if String(result, 1).is_type():
            return '"{}"'.format(result)

        if Infinity(result, 1).is_type():
            return '"inf"'

        if Nan(result, 1).is_type():
            return '"nan"'

        return result


class TestParamWriter(object):
    METHOD_LIST = (
        #"is_type",
        #"validate",
        "convert",
        "try_convert",
        "force_convert",
    )

    class Bool(object):
        VALUE_LIST = [True, "true", 1, 1.1, None]

    class String(object):
        VALUE_LIST = [
            "abc", "", 1, "-1", None, True, inf, nan,
        ]

    class Number(object):
        VALUE_LIST = [
            1, 1.0, 1.1, "0", "1.0", "1.1", True,
            None, inf, nan, "test", "",
        ]

    def __init__(self):
        self.__writer = Params()

    def write_bool_tests(self):
        self.__writer.typeclass = pytypeutil.type.Bool

        for method in self.METHOD_LIST:
            for strict_level in (0, 1, 2):
                self.__writer.strict_level = strict_level
                for value in self.Bool.VALUE_LIST:
                    self.__writer.write_test_params(method, value)

    def write_string_tests(self):
        self.__writer.typeclass = pytypeutil.type.String

        for method in self.METHOD_LIST:
            for strict_level in (0, 1):
                self.__writer.strict_level = strict_level
                for value in self.String.VALUE_LIST:
                    self.__writer.write_test_params(method, value)

    def write_integer_tests(self):
        self.__writer.typeclass = pytypeutil.type.Integer

        for method in self.METHOD_LIST:
            for strict_level in (0, 1, 2):
                self.__writer.strict_level = strict_level
                for value in self.Number.VALUE_LIST:
                    self.__writer.write_test_params(method, value)

    def write_realnumber_tests(self):
        self.__writer.typeclass = pytypeutil.type.RealNumber

        for method in self.METHOD_LIST:
            for strict_level in (0, 1, 2):
                self.__writer.strict_level = strict_level
                for value in self.Number.VALUE_LIST:
                    self.__writer.write_test_params(method, value)


if __name__ == "__main__":

    """
    NoneType
    """

    writer = TestParamWriter()
    writer.write_bool_tests()

    """
    writer.write_integer_tests()
    # writer.write_realnumber_tests()
    writer.write_string_tests()
    """
