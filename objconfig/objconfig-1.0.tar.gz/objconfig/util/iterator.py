"""
Author: Asher Wolfstein (http://wunk.me/)
Package Homepage: http://wunk.me/programming-projects/objconfig-python/
GitHub: http://github.com/asherwunk/objconfig for the source repository
"""

from objconfig.exception.runtimeexception import RuntimeException

"""
Emulates the Iterator "interface" as a class in Python
"""


class Iterator():

    def __iter__(self):
        raise RuntimeException("Iterator: __iter__ not implemented in child class")

    def __next__(self):
        raise RuntimeException("Iterator: __next__ not implemented in child class")
