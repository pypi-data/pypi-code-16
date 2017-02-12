"""
Author: Asher Wolfstein (http://wunk.me/)
Package Homepage: http://wunk.me/programming-projects/objconfig-python/
GitHub: http://github.com/asherwunk/objconfig for the source repository
"""

from objconfig.exception.runtimeexception import RuntimeException

"""
Emulates the Countable "interface" as a class in Python
"""


class Countable():

    def __len__(self):
        raise RuntimeException("Countable: __len__ not implemented in child class")

    def count(self):
        return self.__len__
