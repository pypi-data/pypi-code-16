"""
http://www.php2python.com/wiki/class.arrayaccess/

Author: Asher Wolfstein (http://wunk.me/)
Package Homepage: http://wunk.me/programming-projects/objconfig-python/
GitHub: http://github.com/asherwunk/objconfig for the source repository
"""

from objconfig.exception import IndexException

"""
Emulates the ArrayAccess "interface" as a class in Python
"""


class ArrayAccess():

    def __getitem__(self, key):
        raise IndexException("ArrayAccess: __getitem__ not implemented in child class")

    def __setitem__(self, key, value):
        raise IndexException("ArrayAccess: __setitem__ not implemented in child class")

    def __delitem__(self, key):
        raise IndexException("ArrayAccess: __delitem__ not implemented in child class")
