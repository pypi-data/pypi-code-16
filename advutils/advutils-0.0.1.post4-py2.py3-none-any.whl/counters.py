#!/usr/bin/env python
# -*- coding: latin-1 -*-
"""
This module defines counters useful to generate numbers simulating digital counters
"""

from __future__ import division
from __future__ import print_function
#from builtins import str
from builtins import range
from builtins import object
from numbers import Number

from past.utils import old_div

# import exceptions
from . import VariableNotSettable, VariableNotDeletable, VariableNotGettable


def decima2base(decimal, base, array=None):
    """
    Convert from decimal to any base.

    :param decimal: number in base 10
    :param base: base to convert to e.g. 2 for binary, 16 for hexadecimal
    :param array: control list
    :return: list of number in converted base
    """
    if array is None:
        array = []
    array.insert(0, decimal % base)
    div = old_div(decimal, base)
    if(div == 0):
        return array
    return decima2base(div, base, array)


class NumericalCounter(object):
    """
    Simulates a signed integer counter from -Inf to Inf
    """

    def __int__(self, *args, **kwargs):
        raise NotImplementedError


class BaseCounter(object):
    """
    Base class to create counters
    """

    def __init__(
            self,
            min_state,
            max_state,
            child=None,
            parent=None,
            invert_count=False):
        """
        :param max_state: from 1 to inf
        :param child: counter instance of least significant position
        :param parent: counter instance of most significant position thus to control.
        :param invert_count: if True then next method decreases, else increases
        """
        self._master = None  # keep track of who is the master
        self._min_state = min_state
        self._max_state = max_state
        self._state = min_state
        self.stopped = False  # recognize when iterations should stop
        # True to decrease and False to increase when self.count()
        self._invert_count = invert_count
        self.count = None  # count function
        self.set_child(child)  # set this counter child
        self.set_parent(parent)  # set this counter parent and master

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value=None):
        """
        restart count function
        """
        # restart each time it is set
        def set_count_func():
            if self.invert_count:
                self._count = self.decrease_confirm
                self._count()
            else:
                self._count = self.increase_confirm
            return False  # Iterations not stopped
        # if self.invert_count:
        #    master.decrease()
        if self.invert_count:
            self._count = set_count_func
        else:
            self._count = set_count_func

    @property
    def invert_count(self):
        return self._invert_count

    @invert_count.setter
    def invert_count(self, value):
        self._invert_count = value

    @invert_count.deleter
    def invert_count(self):
        del self._invert_count

    @count.deleter
    def count(self):
        # restart each time it is deleted
        self.count = None

    @property
    def master(self):
        if self._master is None:
            return self  # return self if there is no master
        return self._master

    @master.setter
    def master(self, value):
        if value is not None:
            value = value.master  # get master's master
        self._master = value

    @master.deleter
    def master(self):
        del self._master

    @property
    def min_state(self):
        return self._min_state

    @min_state.setter
    def min_state(self, value):
        self._min_state = value

    @min_state.deleter
    def min_state(self):
        del self._min_state

    @property
    def max_state(self):
        return self._max_state

    @max_state.setter
    def max_state(self, value):
        self._max_state = value

    @max_state.deleter
    def max_state(self):
        del self._max_state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @state.deleter
    def state(self):
        del self._state

    ## CONTROL METHODS ##

    def take_place(self, new):
        """
        Changes counter place with another counter.

        :param new: counter which place is to be taken
        :return: taken counter, if not successful returns None
        """
        if new is not None and new != self:  # confirm if other valid place
            nparent, nchild = new.parent, new.child
            sparent, schild = self.parent, self.child
            if sparent != new:
                new.set_parent(sparent)
            else:  # works for "nchild != self" too
                new.set_parent(self)
            if schild != new:
                new.set_child(schild)
            else:  # works for "nparent != self" too
                new.set_child(self)

            if nparent != self:  # no need to implement else, "schild != place" else replaced it
                self.set_parent(nparent)
            if nchild != self:  # no need to implement else, "sparent != place" else replaced it
                self.set_child(nchild)
            return new

    def demote(self):
        """
        Takes child place.

        :return: master counter, if not successful returns None
        """
        child = self.child
        if child is not None:
            return self.take_place(child)  # new master

    def promote(self):
        """
        Takes parent place.

        :return: master counter, if not successful returns None
        """
        parent = self.parent
        if parent is not None:
            self.take_place(parent)
            return self  # new master

    def invert_ranks(self):
        """
        Counters in Train are repositioned so that last counter
        takes first place and vice-versa.

        :return: master counter of actual counter train
        """
        counterList = self.get_counter_train()
        last = counterList[-1]
        l = len(counterList) - 1
        for i in range(old_div((l + 1), 2)):
            counterList[i].take_place(counterList[l - i])
        return last

    # reset functions #
    def reset(self):
        """
        Resets itself and children.

        :return: None
        """
        self._state = self._min_state
        self.reset_children()

    def reset_children(self):
        """
        Resets only children.

        :return: None
        """
        if self.child is not None:
            self.child.reset()

    def increase(self):
        """
        Increases counter Train state.

        :return: None, use getting methods to know new states
        """
        value = self._state + 1
        if value >= self.max_state:
            self._state = self._min_state
            if self.child is not None:
                self.child.increase()
        else:
            self._state = value

    def decrease(self):
        """
        Decreases counter Train state.

        :return: None, use getting methods to know new states
        """
        value = self._state - 1
        if value < self.min_state:
            self._state = self._max_state - 1
            if self.child is not None:
                self.child.decrease()
        else:
            self._state = value

    def increase_confirm(self):
        """
        Increases counter Train state and confirms when get_max_state() is depleted.
        That is when counters overall state change from get_max_state()-1 to 0.

        :return: True if confirmation otherwise None, use getting methods to know new states
        """
        value = self._state + 1
        if value >= self._max_state:
            self._state = self._min_state
            if self.child is not None:
                return self.child.increase_confirm()
            else:
                return True
        else:
            self._state = value

    def decrease_confirm(self):
        """
        Decreases counter Train state and confirms when get_max_state() is depleted.
            That is when counters overall state change from 0 to get_max_state()-1.

        :return: True if confirmation otherwise None, use getting methods to know new states
        """
        value = self._state - 1
        if value < self._min_state:
            self._state = self._max_state - 1
            if self.child is not None:
                return self.child.decrease_confirm()
            else:
                return True
        else:
            self._state = value

    def confirm(self):
        """
        Confirm whether in next count state is truncated
        """
        if (self.state -
            1 < self._min_state) or (self.state +
                                     1 >= self._max_state):
            if self.child is not None:
                return self.child.confirm()
            else:
                return True

    ## SETTING METHODS ##

    def set_parent(self, parent):
        """
        Sets parent safely by telling the other counter who is the new child.

        :param parent: parent counter
        :return: None
        """
        self.parent = parent
        if parent is not None and parent.child != self:
            parent.set_child(self)

    def set_child(self, child):
        """
        Sets child safely by telling the other counter who is the new parent.

        :param child: child counter
        :return: None
        """
        self.child = child
        if child is not None and child.parent != self:
            child.set_parent(self)

    def set_this_state(self, value):
        """
        Sets safely this counter state.

        :param value: new value state. If value exceeds max_state
                then value takes max_state-1 or if value
                is less than 0 it takes 0
        :return: None
        """
        if value >= self._max_state:
            self.state = self._max_state - 1
        elif value < self.min_state:
            self.state = self._min_state
        else:
            self.state = value

    def set_state_train(self, values):
        """
        Sets safely a counter state train.

        :param values: new train of states (list). If value exceeds max_state
            then value takes max_state-1 or if value is less than 0 it takes 0
        :return: None
        """
        self.set_this_state(values[0])
        if self.child is not None and len(values) >= 2:
            self.child.set_state_train(values[1:])

    def set_this_max_state(self, value):
        """
        Sets safely this counter max_state.

        :param value: new max_state. If state exceeds
                max_state then state takes max_state-1
        :return: None
        """
        self._max_state = value
        if self.state >= value:
            self.state = value - 1

    def set_max_state_train(self, values):
        """
        Sets safely a counter max_state train.

        :param value: new train of max_state(list). If state exceeds
                max_state then state takes max_state-1.
        :return: None
        """
        self.set_this_max_state(values[0])
        if self.child is not None and len(values) >= 2:
            self.child.set_max_state_train(values[1:])

    ## REQUESTING METHODS ##

    def get_state(self, train=None):
        """
        Get overall state of train.

        :param train:
        :return: overall state
        """
        if not train:
            train = []
        iter = self._state
        for i in train:
            iter *= i
        if self.child is not None:
            train.append(self._max_state)
            iter += self.child.get_state(train)
        return iter

    def get_state_train(self, train=None):
        """
        All states or state train.

        :param train: list containing parent states
        :return: list of state from itself and children
        """
        if not train:
            train = []
        train.append(self._state)
        if self.child is not None:
            self.child.get_state_train(train)
        return train

    def get_max_state(self, train=None):
        """
        Get the overall maximum state of train.

        :param train: list containing parent maximum states
        :return: overall maximum state.
            Note: maximum state is never reached but this.get_max_state()-1
        """
        iter = self._max_state
        if train:
            for i in train:
                iter *= i
        if self.child is not None:
            iter *= self.child.get_max_state()
        return iter

    def get_max_state_train(self, train=None):
        """
        Get each max_state of train.

        :param train: list containing max_state of parents
        :return: list of max_state from itself and children
        """
        if not train:
            train = []
        train.append(self._max_state)
        if self.child is not None:
            self.child.get_max_state_train(train)
        return train

    def get_counter_train(self, train=None):
        """
        Get each instance of train.

        :param train: list containing instances of parents
        :return: list of instances from itself and children
        """
        if not train:
            train = []
        train.append(self)
        if self.child is not None:
            self.child.get_counter_train(train)
        return train

    def yield_counter_train(self):
        """
        Get generator of each instance of train.

        :return: generator of instances from itself and children
        """
        yield self
        if self.child is not None:
            for i in self.child.yield_counter_train():
                yield i

    ## OTHER METHODS ##
    def __str__(self):
        return str(self.state)

    def __repr__(self):
        return str(self.state)

    def __int__(self):
        return int(self.state)

    def __float__(self):
        return float(self.state)

    def __iter__(self):
        self.count = None
        self.stopped = False
        return self

    def __next__(self):
        if self.stopped:
            raise StopIteration
        self.stopped = self.count()  # first call is to get the count function
        if self.stopped:
            raise StopIteration
        return self

    next = __next__  # compatibility with python 2

    def __bool__(self):
        return bool(self.get_state())

    __nonzero__ = __bool__  # compatibility with python 2


class IntegerCounter(BaseCounter):
    """
    Simulates an unsigned integer counter from 0 to Inf

    +------+
    | 0    |
    +------+

    to

    +------+
    | Inf  |
    +------+
    """

    def __init__(self, max_state, child=None, parent=None, invert_count=False):
        """
        :param max_state: from 1 to inf
        :param child: counter instance of least significant position
        :param parent: counter instance of most significant position thus to control.
        :param invert_count: if True then next method decreases, else increases
        """
        super(
            IntegerCounter,
            self).__init__(
            0,
            max_state,
            child,
            parent,
            invert_count)
        self.max_state = max_state

    @property
    def max_state(self):
        return self._max_state

    @max_state.setter
    def max_state(self, value):
        assert value > self.min_state, "number of states must be greater than 0"
        self._max_state = value

    @max_state.deleter
    def max_state(self):
        del self._max_state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value > self.max_state - 1:
            raise Exception(
                "Value must not be greater than {}".format(
                    self.max_state - 1))
        if value < 0:
            raise Exception("Value must non negative and got {}".format(value))
        self._state = value

    @state.deleter
    def state(self):
        del self._state

    ## SETTING METHODS ##

    def set_state(self, state, truncate=True, train=None):
        """
        Sets safely this and all counters state train from the overall state.

        :param state: overall state
        :param truncate: it is by default True. If True it calculates the
            states as if in a for loop::

                for i in xrange(state):
                    this.increase()
                this.get_state()

            If False it just stops to the last possible
            state before this.get_max_state()
        :param train: previously calculated train if this counter is not master
            ex: if this and master counters maxStates are T and M then extract
            the trains using get_max_state_train from both this and master,
            so that master elements reach until previous counter of this
            counter [M,10, ...,T-1]. Similarly, get_max_state method can
            be used as [master.get_max_state()/this.get_max_state()]

        :return: reached_overall_state
            ::

                if truncate == True:
                    assert reached_overall_state == state % a.get_max_state()
                else:
                    remaining = state - reached_overall_state
        """
        # This only works if self.min_state = 0
        if not train:  # first recursive level
            assert self.min_state == 0
            train = []

        if truncate:
            state = state % self.get_max_state()  # truncate max iteration

        ans, self.state, newval, iter = 0, 0, 0, 1  # init variables
        if self.child is not None:
            train.append(self.max_state)
            ans = self.child.set_state(state, False, train)
            train.pop()

        remaining = state - ans
        for i in train:
            iter *= i

        if iter <= remaining:
            for i in range(self.max_state - 1, -1, -1):
                newval = iter * i
                if newval <= remaining:
                    self.state = i
                    break

        return newval + ans  # overall state


class DigitCounter(IntegerCounter):
    """
    Simulates a digit counter from 0 to 9

    +---+
    | 0 |
    +---+

    to

    +---+
    | 9 |
    +---+
    """
    @IntegerCounter.max_state.setter
    def max_state(self, value):
        assert value < 10, "number of states must be less than 10"
        assert value > 0, "number of states must be greater than 0"
        self._max_state = value


class MechanicalCounter(BaseCounter):
    """
    Simulates a mechanical counter. It is a wrapper over a train of counters.
    By default it uses a DigitCounter for each slot in the Train.

    +---+---+---+---+---+
    | 0 | 0 | 0 | 0 | 0 |
    +---+---+---+---+---+

    to

    +---+---+---+---+---+
    | 9 | 9 | 9 | 9 | 9 |
    +---+---+---+---+---+
    """

    def __init__(self, values, invert_count=False, invert_order=False,
                 order=None, default_class=DigitCounter):
        """
        :param values: list of maximum states (excluded) or
                default_class objects inherited from counter
        :param invert_count: Default is False that begins to
                increase counters, else decrease counters
        :param invert_order: if True, take inverted values from order
        :param order: index order from Train of counters
        :param default_class: default class of any object to convert from values.
        """
        super(MechanicalCounter, self).__init__(0, None)
        self.stopped = False
        self.default_class = default_class
        #super(MechanicalCounter, self).__setattr__("train", None)
        #super(MechanicalCounter, self).__setattr__("invert_count", None)
        #super(MechanicalCounter, self).__setattr__("order", None)
        self._train = None
        self._invert_count = None
        self._order = None
        self.master = None
        self.config(values, invert_count, invert_order, order)

    @property
    def state(self):
        return self.get_state_train()

    # self.master.set_state

    @property
    def max_state(self):
        return self.get_max_state_train()

    @property
    def train(self):
        return self._train

    @train.setter
    def train(self, value):
        self.config(values=value)

    @train.deleter
    def train(self):
        self._train = None

    @property
    def invert_count(self):
        return self._invert_count

    @invert_count.setter
    def invert_count(self, value):
        self.config(invert_count=value)

    @invert_count.deleter
    def invert_count(self):
        self._invert_count = None

    @property
    def order(self):
        return self._order

    @order.setter
    def order(self, value):
        self.config(order=value)

    @order.deleter
    def order(self):
        self._order = None

    ## CONTROL METHODS ##

    def config(
            self,
            values=None,
            invert_count=None,
            invert_order=False,
            order=None):
        """
        Safely configure MechanicalCounter instance values

        :param values: list of maximum states (excluded) or
                default_class objects inherited from counter
        :param invert_count: Default is False that begins to
                increase counters, else decrease counters
        :param invert_order: if True, take inverted values from order
        :param order: index order from Train of counters
        :param default_class: default class of any object to convert from values.
        """
        tolink = False

        # FOR TRAIN
        if values is not None:
            if not isinstance(values, list):
                values = list(values)
            if self.train != values:
                #super(MechanicalCounter, self).__setattr__("train", values)
                self._train = values
                tolink = True
        # FOR ORDER
        l = len(self.train)

        if order is not None:  # replace old order

            assert l == len(order), "train and order lengths are different"
            if self.order != order:
                cmp1, cmp2 = 0, 0
                for i, j in enumerate(order):
                    cmp1 += i
                    cmp2 += j
                assert cmp1 == cmp2, "incomplete order"

                #super(MechanicalCounter, self).__setattr__("order", order)
                self._order = order
                tolink = True

        if self.order is None:  # if order is None then use generic
            #super(MechanicalCounter, self).__setattr__("order", list(range(l)))
            self._order = list(range(l))
            tolink = True

        if invert_order:
            order = self.order
            for i, item in enumerate(order[::-1]):
                order[i] = item
            tolink = True

        # FOR COUNTING
        if invert_count is not None and self.invert_count != invert_count:  # set decreasing
            #super(MechanicalCounter, self).__setattr__("invert_count", invert_count)
            self._invert_count = invert_count
            tolink = True

        if tolink:
            self.link()

    def link(self):
        """
        Linker method to link counters in the train so that increasing and decreasing
        methods affect all the counters in the due order.
        """
        # print("linking...")
        order = self.order
        trainl = self.train
        for i, link in enumerate(order):
            item = trainl[link]
            if not isinstance(item, self.default_class):
                item = self.default_class(item)
                trainl[link] = item
            item.child = None
            item.parent = None
            if i > 0:
                trainl[order[i - 1]].set_child(item)
        #super(MechanicalCounter, self).__setattr__("master", trainl[order.index(0)])
        self.master = trainl[order.index(0)]
        self.count = None
        # self.reset()

    def invert_real_order(self):
        """
        Counters in Train are repositioned so that last
        counter takes first place and vice-versa.

        :return: master counter of actual counter trainl
        """
        trainl = self.train
        for i, item in enumerate(trainl[::-1]):
            trainl[i] = item
        self.link()

    def invert_ranks(self):
        """
        Counters hierarchy in Train are repositioned so that
        last counter takes first this.Order and vice-versa.

        :return: master counter of actual counter train

        ..Note::

            Same as self.invert_link_order() but self.invert_ranks()
            does not touch the links but the real positions
        """
        #super(MechanicalCounter, self).__setattr__("master", self.master.invert_ranks())
        self.master = self.master.invert_ranks()
        order = self.order
        for i, item in enumerate(order[::-1]):
            order[i] = item

    def invert_link_order(self):
        """
        Counters hierarchy in Train are repositioned so that last
        counter takes first this.Order and vice-versa.

        :return: master counter of actual counter train

        ..Note:

            Same as self.invert_ranks()
        """
        self.config(invert_order=True)

    # reseting functions #
    def reset(self):
        """
        Resets itself and children.

        :return: None
        """
        return self.master.reset()

    # reseting functions #
    def reset_children(self):
        """
        Resets itself and children.

        :return: None
        """
        return self.master.reset_children()

    ## COUNTING METHODS ##

    def increase(self):
        """
        Increases counter Train state.

        :return: None, use getting methods to know new states
        """
        return self.master.increase()

    def decrease(self):
        """
        Decreases counter Train state.

        :return: None, use getting methods to know new states
        """
        return self.master.decrease()

    def increase_confirm(self):
        """
        Increases counter Train state and confirms when get_max_state()
        is depleted. That is when counters overall state change from
        get_max_state()-1 to self.min_state.

        :return: True if confirmation otherwise None,
            use getting methods to know new states
        """
        return self.master.increase_confirm()

    def decrease_confirm(self):
        """
        Decreases counter Train state and confirms when get_max_state()
        is depleted. That is when counters overall state change from
        self.min_state to get_max_state()-1.

        :return: True if confirmation otherwise None,
            use getting methods to know new states
        """
        return self.master.decrease_confirm()

    def confirm(self):
        """
        Confirm whether in next count states are truncated
        """
        return self.master.confirm()

    ## SETTING METHODS ##

    def set_state_train(self, values):
        """
        Sets safely a counter state train.

        :param values: new train of states (list). If value exceeds max_state
            then value takes max_state-1 or if value is less than
            self.min_state it takes self.min_state
        :return: None
        """
        return self.master.set_state_train(values)

    def set_max_state_train(self, values):
        """
        Sets safely a counter max_state train.

        :param value: new train of max_state(list). If state exceeds max_state
            then state takes max_state-1
        :return: None
        """
        return self.master.set_max_state_train(values)

    def set_this_max_state(self, value):
        """
        Sets safely this counter max_state.

        :param value: new max_state. If state exceeds
                max_state then state takes max_state-1
        :return: None
        """
        return self.master.set_this_max_state(value)

    def set_this_state(self, value):
        """
        Sets safely this counter state.

        :param value: new value state. If value exceeds max_state
                then value takes max_state-1 or if value
                is less than 0 it takes 0
        :return: None
        """
        return self.master.set_this_state(value)

    def set_state(self, state, truncate=True, train=None):
        """
        Sets safely this and all counters state train from the overall state.

        :param state: overall state
        :param truncate: it is by default True. If True it calculates the
            states as if in a for loop::

                for i in xrange(state):
                    this.increase()
                return this.get_state()

            If False it just stops to the last possible
            state before this.get_max_state()
        :param train: previously calculated train if this counter is not master
            ex: if this and master counters maxStates are T and M then extract
            the trains using get_max_state_train from both this and master,
            so that master elements reach until previous counter of this
            counter [M,10, ...,T-1]. Similarly, get_max_state method can
            be used as [master.get_max_state()/this.get_max_state()]
        :return: reached_overall_state
            ::

                if truncate == True:
                    assert reached_overall_state == state % a.get_max_state()
                else:
                    remaining = state - reached_overall_state
        """
        return self.master.set_state(state, truncate, train)

    ## REQUESTING METHODS ##

    def get_state(self, train=None):
        """
        Get overall state of train.

        :param train:
        :return: overall state
        """
        return self.master.get_state(train)

    def get_state_train(self, train=None):
        """
        All states or state train.

        :param train: list containing parent states
        :return: list of state from itself and children
        """
        return self.master.get_state_train(train)

    def get_real_state_train(self):
        """
        All states or state train.

        :return: list of state from itself and children
        """
        return [i.state for i in self.train]

    def get_max_state(self, train=None):
        """
        Get the overall maximum state of train.

        :param train: list containing parent maximum states
        :return: overall maximum state.
            Note: maximum state is never reached but this.get_max_state()-1
        """
        return self.master.get_max_state(train)

    def get_max_state_train(self, train=None):
        """
        Get each max_state of train.

        :param train: list containing max_state of parents
        :return: list of max_state from itself and children
        """
        return self.master.get_max_state_train(train)

    def get_real_max_state_train(self):
        """
        Get each max_state of train.

        :return: list of max_state from itself and children
        """
        return [i.max_state for i in self.train]

    def get_counter_train(self, train=None):
        """
        Get each instance of train virtually organized.

        :param train: list containing instances of parents
        :return: list of instances from itself and children
        """
        return self.master.get_counter_train(train)

    def yield_counter_train(self):
        """
        Yield each instance of train virtually organized.

        :return: generator of instances from itself and children
        """
        return self.master.yield_counter_train()

    def get_real_counter_train(self):
        """
        Get each instance of train physically organized.

        :return: list of instances from itself and children
        """
        return self.train

    ## OTHER METHODS ##

    def __next__(self):
        super(MechanicalCounter, self).__next__()
        return self.get_real_state_train()

    next = __next__  # compatibility with python 2

    def __bool__(self):
        """
        If any state is True it returns True, else False if all states are False
        """
        for item in self.train:
            if not bool(item):
                return False
        return True

    __nonzero__ = __bool__  # compatibility with python 2


class Bit(DigitCounter):
    """
    Simulates a bit counter from 0 to 1
    """

    def __init__(
            self,
            state=1,
            name=None,
            description=None,
            child=None,
            parent=None):
        """

        :param state:
        :param name:
        :param description:
        :param child:
        :param parent:
        """
        super(Bit, self).__init__(2, child, parent)
        self.name = name
        self.state = state
        self.description = description

    @property
    def max_state(self):
        raise VariableNotGettable()

    @max_state.setter
    def max_state(self, value):
        raise VariableNotSettable()

    @max_state.deleter
    def max_state(self):
        raise VariableNotDeletable()


class Bitstream(MechanicalCounter):
    """
    Simulates a bitstream of data

    example::

        a = Bitstream([1,1,1])
        for i in a:
            print(i)
    """

    def __init__(
            self,
            stream,
            invert_count=False,
            invert_order=False,
            order=None,
            default_class=Bit):
        """
        :param stream: list of Bits or default_class objects inherited from Bit
        :param invert_count: Default is False that begins to
                increase Bitstream, else decrease Bitstream
        :param invert_order: if True, take inverted Bits from order list
        :param order: index order from Train of Bits
        :param default_class: default class of any object to convert from stream
        """
        if isinstance(stream, Number):
            stream = [default_class() for _ in range(stream)]
        super(
            Bitstream,
            self).__init__(
            stream,
            invert_count,
            invert_order,
            order,
            default_class=Bit)
