# -*- coding: utf-8 -*-

from specpie.printer import green, red, printer, bold, dump


class Be(object):
    def __init__(self, target):
        self.__target = target

    def equals_to(self, other: object):
        """
        Compare if the :target is equals to :other, if it's not result on a AssertionError
        :type other: object
        :param other:
        """
        if self.__target == other:
            message = green('Expected ')
            message += bold(dump(self.__target))
            message += green(' to be equals to ')
            message += bold(dump(other))
            message += green(' and it was!')
        else:
            message = red('Expected ')
            message += bold(dump(self.__target))
            message += red(' to be equals to ')
            message += bold(dump(other))
            message += red(', but it was not!')
        printer.show(message)
        assert self.__target == other

    def same_as(self, other: object):
        """
        Compare if the :target is the same as :other, if it's not result on a AssertionError
        :type other: object
        :param other:
        """
        if self.__target is other:
            message = green('Expected ')
            message += bold(dump(self.__target))
            message += green(' to be the same as ')
            message += bold(other)
            message += green(' and it was!')
        else:
            message = red('Expected ')
            message += bold(dump(self.__target))
            message += red(' to be the same as ')
            message += bold(dump(other))
            message += red(', but it was not!')
        printer.show(message)
        assert self.__target is other

    def instance_of(self, kind: type):
        """
        Compare if the :target is of the type :kind, if it's not result on a AssertionError
        :type kind: type
        :param kind:
        """
        if isinstance(self.__target, kind):
            message = green('Expected ')
            message += bold(dump(self.__target))
            message += green(' to be a instance o type ')
            message += bold(dump(kind))
            message += green(' and it was!')
        else:
            message = red('Expected ')
            message += bold(self.__target)
            message += red(' to be a instance o type ')
            message += bold(dump(kind))
            message += red(', but it was not!')
        printer.show(message)
        assert isinstance(self.__target, kind)


class NotBe(object):
    def __init__(self, target: object):
        self.__target = target

    def equals_to(self, other: object):
        """
        Compare if the :target is equals to :other. If it's, result on a AssertionError
        :type other: object
        :param other:
        """
        if self.__target == other:
            message = red('Expected ')
            message += bold(dump(self.__target))
            message += red(' to not be equals to ')
            message += bold(other)
            message += red(', but it was!')
        else:
            message = green('Expected ')
            message += bold(dump(self.__target))
            message += green(' to not be equals to ')
            message += bold(dump(other))
            message += green(' and it was not!')
        printer.show(message)
        assert self.__target != other

    def same_as(self, other: object):
        """
        Compare if the :target is the same as :other. If it's, result on a AssertionError
        :type other: object
        :param other:
        """
        if self.__target is other:
            message = red('Expected ')
            message += bold(dump(self.__target))
            message += red(' to not be the same as ')
            message += bold(dump(other))
            message += red(', but it was!')
        else:
            message = green('Expected ')
            message += bold(dump(self.__target))
            message += green(' to not be the same as ')
            message += bold(dump(other))
            message += green(' and it was not!')
        printer.show(message)
        assert self.__target is not other

    def instance_of(self, kind: type):
        """
        Compare if the :target is of the type :kind. If it's, result on a AssertionError
        :type kind: type
        :param kind:
        """
        if isinstance(self.__target, kind):
            message = red('Expected ')
            message += bold(dump(self.__target))
            message += red(' to not be a instance o type ')
            message += bold(dump(kind))
            message += red(', but it was!')
        else:
            message = green('Expected ')
            message += bold(dump(self.__target))
            message += green(' to be a instance o type ')
            message += bold(dump(kind))
            message += green(' and it was not!')
        printer.show(message)
        assert not isinstance(self.__target, kind)


class Should(object):
    def __init__(self, target):
        self.be = Be(target)
        self.not_be = NotBe(target)


def should(instance):
    return Should(instance)


def spec(f):
    def deco(*args, **kwargs):
        f(*args, **kwargs)

    deco()
    return deco
