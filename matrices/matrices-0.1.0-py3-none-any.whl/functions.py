"""This module contains various utility functions for making and processing
Matrix objects."""

from .matrix import Matrix

def create_vertex(*values):
    """Will create a vertex - a Matrix with a single column.

    :param \*values: The vertex values.
    :rtype: :py:class:`.Matrix`"""

    return Matrix(*[(value,) for value in values])


def can_add(matrix1, matrix2):
    """Checks to see if two Matrix objects can be added by ensuring they have
    the same size.

    :param Matrix matrix1: the first matrix.
    :param Matrix matrix2: the second matrix.
    :rtype: ``bool``"""

    return matrix1.size() == matrix2.size()


def can_multiply(matrix1, matrix2):
    """Checks to see if two Matrix objects can be multiplied by ensuring that
    their dimensions are compatible.

    :param Matrix matrix1: the first matrix.
    :param Matrix matrix2: the second matrix.
    :rtype: ``bool``"""

    return matrix1.size()[1] == matrix2.size()[0]
