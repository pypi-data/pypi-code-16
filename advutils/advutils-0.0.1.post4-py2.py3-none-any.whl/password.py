"""
This module defines simple numerical and mapped passwords using letters in a deterministic
way i.e. in order
"""

from __future__ import print_function
from __future__ import absolute_import
# https://docs.python.org/2/library/itertools.html
# http://stackoverflow.com/questions/104420/how-to-generate-all-permutations-of-a-list-in-python
from builtins import map
from builtins import chr
from builtins import zip
from builtins import range
from itertools import product
from string import ascii_letters

from .counters import IntegerCounter, MechanicalCounter

COMBINATIONS = ascii_letters + "".join(map(str, list(range(10))))


def num2chr(nums):
    """ converts a number to string
    """
    for c in nums:
        yield chr(c)


def chr2num(strings):
    """ converts a string to number
    """
    for c in strings:
        yield ord(c)


class Permutator(IntegerCounter):
    """
    Permute an iterable object
    """

    def __init__(self, iterable, child=None, parent=None, invert_count=False):
        super(
            Permutator,
            self).__init__(
            len(iterable),
            child,
            parent,
            invert_count)
        self.iterable = iterable

    def get_value(self):
        """
        Get current value from permutation state
        """
        return self.iterable[self.state]

    def set_value(self, value):
        """
        Set current value for permutation state
        """
        self.state = self.iterable.index(value)

    def get_value_train(self, train=None):
        """
        All states or state train.

        :param train: list containing parent states
        :return: list of state from itself and children
        """
        if not train:
            train = []
        train.append(self.iterable[self.state])
        if self.child:
            self.child.get_value_train(train)
        return train

    def set_value_train(self, values):
        """
        Sets safely a counter state train.

        :param values: new train of states (list). If value exceeds
            max_state then value takes max_state-1 or if value
            is less than 0 it takes 0.
        :return: None
        """
        """
        # This is the legacy method
        self.set_value(values[0])
        if self.child and len(values)>=2:
            self.child.set_value_train(values[1:])"""
        train = self.get_counter_train()
        assert len(values) == len(
            train), "values do not correspond to permutation train"
        try:
            for i, (per, val) in enumerate(zip(train, values)):
                per.set_value(val)
        except ValueError:
            raise ValueError(
                "Value '{}' at position {} is not in train".format(
                    val, i))

    def __next__(self):
        super(Permutator, self).__next__()
        return self.get_value()

    next = __next__  # compatibility with python 2


class PermutatorTrain(MechanicalCounter):
    """
    Permute a Train of iterable objects
    """

    def __init__(self, values, invert_count=False, invert_order=False,
                 order=None, default_class=Permutator):
        """
        :param values: list of maximum states (excluded) or
                default_class objects inherited from counter
        :param invert_count: Default is False that begins to
                increase counters, else decrease counters
        :param invert_order: if True, take inverted values from order
        :param order: index order from Train of counters
        :param default_class: default class of any object to convert from values.
        """
        super(
            PermutatorTrain,
            self).__init__(
            values,
            invert_count,
            invert_order,
            order,
            default_class)

    def get_value_train(self, train=None):
        """
        All states or state train.

        :param train: list containing parent states
        :return: list of state from itself and children
        """
        return self.master.get_value_train(train)

    def get_real_value_train(self):
        """
        All states or state train.

        :return: list of state from itself and children
        """
        return [i.get_value() for i in self.train]

    def set_value_train(self, values):
        """
        Sets safely a counter state train.

        :param values: new train of states (list). If value exceeds
                max_state then value takes max_state-1 or if value
                is less than 0 it takes 0.
        :return: None
        """
        return self.master.set_value_train(values)

    def set_real_value_train(self, values):
        """
        Sets safely a counter state train.

        :param values: new train of states (list). If value exceeds max_state
            then value takes max_state-1 or if value is less than 0 it takes 0
        :return: None
        """
        train = self.train
        assert len(values) == len(
            train), "values do not correspond to permutation train"
        try:
            for i, (per, val) in enumerate(zip(train, values)):
                per.set_value(val)
        except ValueError:
            raise ValueError(
                "Value '{}' at position {} is not in train".format(
                    val, i))

    # iteration functions #
    def __next__(self):
        super(PermutatorTrain, self).__next__()
        return self.get_real_value_train()

    next = __next__  # compatibility with python 2


def deterministic(length=1, iterable=COMBINATIONS):
    """
    It generates permutations faster but it is not
        customizable. (it uses product from itertools).
        Deterministic function generates "iterable^length"
        combinations from iterable each row of "length" columns.

    :param length: length of how many columns, or factor number
    :param iterable: list of items to permute
    :return: itertools iterator

    ..Example:

        factor = 1
        assert len(list(deterministic(factor, iterable = COMBINATIONS))) \
                    == len(COMBINATIONS)**factor
    """
    return product(iterable, repeat=length)


def repeat_iterator(length=1, iterable=COMBINATIONS):
    """
    Repeats iterable "length" times.

    :param length: length of how many columns or times to repeat
    :param iterable: list of items to repeat
    :return: tuple of iterable rows and length columns
    """
    return (iterable,) * length


def get_permutations(length=1, combination=COMBINATIONS,
                     invert_count=False, invert_order=False, order=None):
    """
    Like deterministic but customizable.

    :param length: length of how many columns, or factor number
    :param combination: list of items to permute
    :param invert_count: Default is False, if True, take inverted
            index from combinations (see :param combinations)
    :param invert_order: Default is False, if True, take inverted
            index from order (see :param order)
    :param order: index order of columns
    :return: PermutatorTrain object (it can be use as a generator)
    """
    return PermutatorTrain(repeat_iterator(length, combination),
                           invert_count, invert_order, order)
