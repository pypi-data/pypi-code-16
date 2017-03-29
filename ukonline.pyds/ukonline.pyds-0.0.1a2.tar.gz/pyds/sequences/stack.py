# stack.py
# Author: Sébastien Combéfis
# Version: March 24, 2017

from abc import ABCMeta, abstractmethod

class Stack(metaclass=ABCMeta):
    @abstractmethod
    def size(self):
        pass

    @abstractmethod
    def isempty(self):
        pass

    @abstractmethod
    def top(self):
        pass

    @abstractmethod
    def pop(self):
        pass

    @abstractmethod
    def push(self, elem):
        pass


class EmptyStackError(Exception):
    pass


class FullStackError(Exception):
    pass


class ArrayStack(Stack):
    def __init__(self, capacity):
        self.__data = [None] * capacity
        self.__top = -1
        self.__capacity = capacity

    def size(self):
        return self.__top + 1

    def isempty(self):
        return self.size() == 0

    def top(self):
        if self.isempty():
            raise EmptyStackError()
        return self.__data[self.__top]

    def pop(self):
        if self.isempty():
            raise EmptyStackError()
        elem = self.__data[self.__top]
        self.__data[self.__top] = None
        self.__top -= 1
        return elem

    def push(self, elem):
        if self.size() == self.__capacity:
            raise FullStackError()
        self.__top += 1
        self.__data[self.__top] = elem

    def __str__(self):
        return str(self.__data)
