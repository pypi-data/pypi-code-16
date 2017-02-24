"""Contains the core Matrix class and its methods."""

from .exceptions import MatrixError

class Matrix:
    """Represents a matrix.

    Matrices can be added using the ``+`` operator, and multuplied using the
    ``*`` operator to get the dot product. They also support scalar
    multiplication.

    Two matrices are considered equal by the ``==`` operator if they have the
    same size, and equivalent values at each position.

    :param \*rows: The rows for the matrix."""

    def __init__(self, *rows):
        if not rows:
            raise TypeError("Matrix needs at least one row")
        clean_rows = []
        row_length = -1
        for row in rows:
            if not isinstance(row, list) and not isinstance(row, tuple):
                raise TypeError("Matrix needs lists or tuples")
            if row_length != -1 and len(row) != row_length:
                raise ValueError("All Matrix rows must be of equal length")
            row_length = len(row)
            clean_rows.append(tuple(row))
        if row_length == 0:
            raise TypeError("Matrix rows cannot be empty")
        self._rows = tuple(clean_rows)


    def __repr__(self):
        return "<Matrix (%i×%i)>" % (len(self._rows), len(self._rows[0]))


    def __eq__(self, other):
        if not isinstance(other, Matrix) or self.size() != other.size():
            return False
        for index, row in enumerate(self._rows):
            if row != other._rows[index]:
                return False
        return True


    def __add__(self, other):
        from .functions import can_add
        if not can_add(self, other):
            raise MatrixError("Cannot add %s and %s." % (str(self), str(other)))
        new_rows = []
        for rindex, row in enumerate(self._rows):
            other_row = other._rows[rindex]
            new_row = [val + other_row[vindex] for vindex, val in enumerate(row)]
            new_rows.append(new_row)
        return Matrix(*new_rows)


    def __sub__(self, other):
        from .functions import can_add
        if not can_add(self, other):
            raise MatrixError(
             "Cannot subtract %s from %s." % (str(other), str(self))
            )
        new_rows = []
        for rindex, row in enumerate(self._rows):
            other_row = other._rows[rindex]
            new_row = [val - other_row[vindex] for vindex, val in enumerate(row)]
            new_rows.append(new_row)
        return Matrix(*new_rows)


    def __mul__(self, other):
        from .functions import can_multiply
        if isinstance(other, Matrix):
            if not can_multiply(self, other):
                raise MatrixError(
                 "Cannot multiply %s and %s." % (str(self), str(other))
                )
            new_rows = []
            columns = other.columns()
            for rindex, row in enumerate(self._rows):
                new_row = []
                for column in columns:
                    new_row.append(
                     sum([val * column[index] for index, val in enumerate(row)])
                    )
                new_rows.append(new_row)
            return Matrix(*new_rows)
        else:
            return Matrix(*[[val * other for val in row] for row in self._rows])


    def __rmul__(self, other):
        return Matrix(*[[val * other for val in row] for row in self._rows])


    def rows(self):
        """Returns the Matrix's rows.

        :rtype: ``tuple``"""

        return self._rows


    def columns(self):
        """Returns the Matrix's columns.

        :rtype: ``tuple``"""

        return tuple([tuple(
         [row[n] for row in self._rows]
        ) for n in range(len(self._rows[0]))])


    def size(self):
        """Returns the Matrix's size in (rows, columns) notation.

        :rtype: ``tuple``"""

        return (len(self.rows()), len(self.columns()))
