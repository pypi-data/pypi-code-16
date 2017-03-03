# kuhn_munkres.py
## an implementation of the Kuhn-Munkres assignment algorithm
##
## ACKNOWLEDGEMENTS:
## Derfellios on Warlight
## - introducing me to the field of combinatorial optimization
## mhcuervo on StackOverflow
## - a detailed explanation of the Hungarian algorithm
## David Eisenstat on StackOverflow
## - the clever idea of using tuple costs

# imports
import copy

# decorators

def check_type(func):
    """performs a typecheck before running"""
    def func_wrapper(self, other):
        if self._check_type(other) is NotImplemented:
            return NotImplemented
        return func(self, other)
    return func_wrapper

def restore(func):
    """restores values if an exception is encountered"""
    def func_wrapper(self, *args, **kwargs):
        old_v = copy.copy(self.v)
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self.v = old_v
            raise e
    return func_wrapper

# errors

class ImproperCost(Exception):
    """error raised for invalid Cost objects"""
    pass

# classes

class Cost(object):
    """
    class to represent cost values
    and handle disallowed pairings
    :argument val: integer/float value
    """

    def __init__(self, *vals):
        if len(vals) != 2: raise ImproperCost("Need exactly two vals")
        self.v = list(vals)

    @staticmethod
    def is_numeric(val):
        return (isinstance(val, int) or isinstance(val, float))

    @staticmethod
    def is_array(val):
        return (isinstance(val, list) or isinstance(val, tuple))

    @staticmethod
    def _check_type(val):
        """return NotImplemented for invalid operations"""
        if not isinstance(val, Cost):
            return NotImplemented

    @check_type
    def __add__(self, other):
        return Cost(self.v[0] + other.v[0], self.v[1] + other.v[1])

    @check_type
    @restore
    def __iadd__(self, other):
        self.v[0] += other.v[0]
        self.v[1] += other.v[1]
        return self

    @check_type
    def __sub__(self, other):
        return Cost(self.v[0] - other.v[0], self.v[1] - other.v[1])

    @check_type
    @restore
    def __isub__(self, other):
        self.v[0] -= other.v[0]
        self.v[1] -= other.v[1]
        return self

    def __neg__(self):
        return Cost(-self.v[0], -self.v[1])

    def _numeric_mul(self, val):
        """multiplication with numeric values"""
        return Cost(self.v[0] * val, self.v[1] * val)

    def _numeric_imul(self, val):
        """augmented multiplication with numeric values"""
        self.v[0] *= val
        self.v[1] *= val
        return self

    @check_type
    def _cost_mul(self, other):
        """multiplication with cost objects"""
        return Cost(self.v[0] * other.v[0], self.v[1] * other.v[1])

    @check_type
    def _cost_imul(self, other):
        """augmented multiplication with cost objects"""
        self.v[0] *= other.v[0]
        self.v[1] *= other.v[1]
        return self

    def __mul__(self, other):
        if self.is_numeric(other):
            return self._numeric_mul(other)
        return self._cost_mul(other)

    @restore
    def __imul__(self, other):
        if self.is_numeric(other):
            return self._numeric_imul(other)
        return self._cost_imul(other)

    def __rmul__(self, other):
        return (self * other)

    def _numeric_div(self, val):
        """division with numeric values"""
        return Cost(self.v[0] / val, self.v[1] / val)

    def _numeric_idiv(self, val):
        """augmented division with numeric values"""
        self.v[0] /= val
        self.v[1] /= val
        return self

    def _numeric_rdiv(self, val):
        """right-side division with numeric values"""
        return Cost(val / self.v[0], val / self.v[1])

    @check_type
    def _cost_div(self, other):
        """division with cost objects"""
        return Cost(self.v[0] / other.v[0], self.v[1] / other.v[1])

    @check_type
    def _cost_idiv(self, other):
        """augmented division with cost objects"""
        self.v[0] /= other.v[0]
        self.v[1] /= other.v[1]
        return self

    def __div__(self, other):
        if self.is_numeric(other):
            return self._numeric_div(other)
        return self._cost_div(other)

    @restore
    def __idiv__(self, other):
        if self.is_numeric(other):
            return self._numeric_idiv(other)
        return self._cost_idiv(other)

    def __rdiv__(self, other):
        if self.is_numeric(other):
            return self._numeric_rdiv(other)
        return NotImplemented

    @check_type
    def __lt__(self, other):
        return (self.v[0] < other.v[0] or
                self.v[0] == other.v[0] and
                self.v[1] < other.v[1])

    @check_type
    def __gt__(self, other):
        return (self.v[0] > other.v[0] or
                self.v[0] == other.v[0] and
                self.v[1] > other.v[1])

    def _numeric_eq(self, other):
        """equality check against numeric values"""
        return (self.v[0] == other and self.v[1] == other)

    def _array_eq(self, other):
        """equality check against arrays"""
        return (self.v[0] == other[0] and self.v[1] == other[1])

    @check_type
    def _cost_eq(self, other):
        """equality check against cost objects"""
        return (self.v[0] == other.v[0] and self.v[1] == other.v[1])

    def __eq__(self, other):
        if self.is_numeric(other):
            return self._numeric_eq(other)
        elif self.is_array(other):
            return self._array_eq(other)
        return self._cost_eq(other)

    def __cmp__(self, other):
        """
        Returns -1 (less than) for non-Cost objects
        that aren't arrays or ints equal to the instance
        """
        if self.__lt__(other):
            return -1
        elif self.__gt__(other):
            return 1
        else:
            return 0

    def __str__(self):
        return "Cost(%3.2f, %3.2f)" % (self.v[0], self.v[1])

    def __repr__(self):
        return str(self.v)

def copy_cost(cost):
    """:return: a copy of the given Cost object"""
    return Cost(cost.v[0], cost.v[1])

class Matrix(object):
    """
    a class to handle and solve 2D assignment matrices
    :param array: a 2D array representing a rectangular matrix
    """

    def __init__(self, array):
        array = self._process(array)
        self.array = array
        self.col_array = self._transpose(array)
        self.stars, self.primes = set(), set()
        self.covers = {'rows': set(), 'cols': set()}
        self.uncovered = {'rows': set(range(self.row_count)),
                          'cols': set(range(self.col_count))}

    def __repr__(self):
        return repr(self.array)

    @staticmethod
    def _get_max(array):
        max_cost = None
        for row in array:
            for val in row:
                if max_cost is None or val > max_cost:
                    max_cost = val
        return Cost(max_cost.v[0], max_cost.v[1])

    @classmethod
    def _process(cls, array):
        """
        handles irregularities in an array-matrix
        :return: a square array matrix
        :rtype: list of lists
        """
        array = copy.deepcopy(array)
        if len(array) == 0: return array

        max_val = cls._get_max(array)
        max_cost = lambda: Cost(max_val.v[0], max_val.v[1])
        zero_cost = lambda: Cost(0, 0)

        # first make matrices rectangular
        max_len = max(len(row) for row in array)
        for row in array:
            while len(row) < max_len:
                row.append(max_cost())

        # then make the matrix square
        col_count = len(array[0])
        len_diff = len(array) - col_count
        if len_diff > 0: # more rows than columns
            for row in array:
                row += [max_cost() for i in xrange(len_diff)]
        elif len_diff < 0: # more columns than rows
            array += [[zero_cost() for j in xrange(col_count)]
                      for i in xrange(len_diff, 0)]

        return array

    @staticmethod
    def _transpose(array):
        """
        gets the transpose of an array-matrix
        :return: array transpose
        :rtype: list of lists
        """
        col_array = list()
        for row in array:
            for i in xrange(len(row)):
                if len(col_array) <= i:
                    col_array.append([copy.deepcopy(row[i]),])
                else:
                    col_array[i].append(copy.deepcopy(row[i]))
        return col_array

    @property
    def size(self):
        """the matrix dimensions as a (rows, cols) tuple"""
        return (len(self.array), len(self.col_array))

    @property
    def n(self):
        """size of the (square) matrix along any dimension"""
        return self.row_count

    def __len__(self):
        """the length of the square matrix"""
        return self.n

    @property
    def row_count(self):
        return len(self.array)

    @property
    def col_count(self):
        return len(self.col_array)

    @property
    def covered_rows(self):
        """
        :return: a set of all covered rows
        :rtype: set of ints
        """
        return self.covers['rows']

    @property
    def covered_cols(self):
        """
        :return: a set of all covered cols
        :rtype: set of ints
        """
        return self.covers['cols']

    @property
    def uncovered_rows(self):
        """
        :return: a set of all uncovered rows
        :rtype: set of ints
        """
        return self.uncovered['rows']

    @property
    def uncovered_cols(self):
        """
        :return: a set of all uncovered cols
        :rtype: set of ints
        """
        return self.uncovered['cols']

    def get_row(self, index):
        """:return: a row at a given index"""
        return self.array[index]

    def get_col(self, index):
        """:return: a column at a given index"""
        return self.col_array[index]

    def get_val(self, row, col):
        """:return: a copy of the value at a given row and column"""
        return copy_cost(self.array[row][col])

    def set_val(self, row, col, val):
        """sets a value at a desired row and column"""
        self.array[row][col] = val
        self.col_array[col][row] = val

    def add_val(self, row, col, amt):
        """adds an amount to the value at a given row/col"""
        self.array[row][col] += amt
        self.col_array[col][row] += amt

    def sub_val(self, row, col, amt):
        """subtracts a given amount from the value at a given row/col"""
        self.array[row][col] -= amt
        self.col_array[col][row] -= amt

    def cover(self, **kwargs):
        """
        covers given rows and/or columns
        passed in using the rows and cols keywargs
        (as lists)
        """
        rows = kwargs.get('rows', [])
        cols = kwargs.get('cols', [])
        for row in rows:
            self.covered_rows.add(row)
            self.uncovered_rows.remove(row)
        for col in cols:
            self.covered_cols.add(col)
            self.uncovered_cols.remove(col)

    def uncover(self, **kwargs):
        """
        uncovers given rows and/or columns
        passed in using the rows and cols keywargs
        (as lists)
        """
        rows = kwargs.get('rows', [])
        cols = kwargs.get('cols', [])
        for row in rows:
            self.covered_rows.remove(row)
            self.uncovered_rows.add(row)
        for col in cols:
            self.covered_cols.remove(col)
            self.uncovered_cols.add(col)

    def cover_rows(self, *rows):
        """covers given rows"""
        self.cover(rows=rows)

    def cover_cols(self, *cols):
        """covers given cols"""
        self.cover(cols=cols)

    def uncover_rows(self, *rows):
        """uncovers given rows"""
        self.uncover(rows=rows)

    def uncover_cols(self, *cols):
        """uncovers given cols"""
        self.uncover(cols=cols)

    def minimize_row(self, row):
        """given a row index, subtracts the minimum value from that row"""
        row_vals = self.get_row(row)
        min_val = min(row_vals)
        for col in xrange(len(row_vals)):
            self.sub_val(row, col, min_val)

    def _minimize_rows(self):
        """minimizes every row"""
        for row in xrange(self.row_count):
            self.minimize_row(row)

    def minimize_col(self, col):
        """given a col index, subtracts the minimum value from that col"""
        col_vals = self.get_col(col)
        min_val = min(col_vals)
        for row in xrange(len(col_vals)):
            self.sub_val(row, col, min_val)

    def _minimize_cols(self):
        """minimizes every col"""
        for col in xrange(self.col_count):
            self.minimize_col(col)

    @staticmethod
    def get_zeros(array):
        """
        :return: the indices of all zeros in an array
        :rtype: list of tuples
        """
        return [i for i in xrange(len(array)) if array[i] == 0]

    def get_row_zeros(self, row):
        """
        :param row: a row index
        :return: indices of rows with the row zeros
        :rtype: list
        """
        return self.get_zeros(self.get_row(row))

    def get_col_zeros(self, col):
        """
        :param col: a col index
        :return: indices of rows with the col zeros
        :rtype: list
        """
        return self.get_zeros(self.get_col(col))

    def _get_min_uncovered(self):
        """
        :return: the minimal uncovered value
        :rtype: Cost object
        """
        min_val = None
        for row in xrange(self.row_count):
            if row in self.covered_rows: continue
            for col in xrange(self.col_count):
                if col in self.covered_cols: continue
                val = self.get_val(row, col)
                if (min_val is None or
                    val < min_val):
                    min_val = copy_cost(val)
        return min_val

    def _init_stars(self):
        s_rows, s_cols = set(), set()
        for row in xrange(self.row_count):
            zeros = self.get_row_zeros(row)
            for col in zeros:
                if (row not in s_rows and
                    col not in s_cols):
                    self.stars.add((row, col))
                    s_rows.add(row)
                    s_cols.add(col)
                    break # no more stars for this row

    def _clear_state(self):
        """clears primes and covers but not stars"""
        self.primes.clear()
        self.covered_rows.clear()
        self.uncovered_rows.update(range(len(self)))
        self.covered_cols.clear()
        self.uncovered_cols.update(range(len(self)))

    def _clear_and_return(self, pairings):
        """clears state and returns pairings"""
        retval = copy.deepcopy(pairings) # for safety
        self._clear_state()
        return retval

    def _cover_starred_cols(self):
        self.cover_cols(*[zero[1] for zero in self.stars])
        if (len(self.covered_cols) == self.col_count):
            return self._clear_and_return(self.stars)
        return self._prime_uncovered()

    def _make_star_dict(self):
        result = dict()
        for zero in self.stars:
            result[zero[0]] = zero[1]
        return result

    def _find_uncovered_zeros(self):
        results = list()
        for row in xrange(self.row_count):
            if row in self.covered_rows: continue
            zeros = self.get_row_zeros(row)
            for col in zeros:
                if col not in self.covered_cols:
                    results.append((row, col))
        return results

    def _prime_uncovered(self):
        star_dict = self._make_star_dict()
        uncovered_zeros = self._find_uncovered_zeros()
        while (len(uncovered_zeros) > 0):
            current_zero = uncovered_zeros[0]
            self.primes.add(current_zero)
            if current_zero[0] not in star_dict: # check row
                return self._increment_starred(current_zero)
            else:
                self.cover_rows(current_zero[0])
                self.uncover_cols(star_dict[current_zero[0]])
                uncovered_zeros = self._find_uncovered_zeros()
        return self._make_more_zeros()

    def _make_zero_dicts(self):
        col_zeros, row_zeros = dict(), dict()
        for star in self.stars:
            col_zeros[star[1]] = star
        for prime in self.primes:
            row_zeros[prime[0]] = prime
        return col_zeros, row_zeros

    def _process_series(self, series):
        # unstar starred zeroes - odd indices
        for i in xrange(1, len(series), 2):
            self.stars.remove(series[i])
        # star primed zeroes - even indices
        for i in xrange(0, len(series), 2):
            self.stars.add(series[i])
        self._clear_state()

    def _increment_starred(self, zero):
        col_zeros, row_zeros = self._make_zero_dicts()
        series = [zero,] # even indices are primes, odd stars
        zero_found = True
        while zero_found:
            latest_zero = series[-1]
            if (len(series) % 2 == 1): # latest is primed
                next_zero = col_zeros.get(latest_zero[1], None)
                if next_zero is None: # primed zero w/o col star
                    zero_found = False
                else:
                    series.append(next_zero)
            else: # latest is starred
                next_zero = row_zeros.get(latest_zero[0])
                # should always find a primed zero here
                series.append(next_zero)
        self._process_series(series)
        return self._cover_starred_cols()

    def _make_more_zeros(self):
        min_val = self._get_min_uncovered()
        for row in self.covered_rows:
            for col in xrange(self.col_count):
                self.add_val(row, col, min_val)
        for col in self.uncovered_cols:
            for row in xrange(self.row_count):
                self.sub_val(row, col, min_val)
        return self._prime_uncovered()

    def solve(self):
        """
        :return: the optimal assignments for the matrix
        :rtype: set of tuples
        """
        if (len(self.stars) > 0): # solved once
            return self.stars
        self._minimize_rows()
        self._init_stars()
        return self._cover_starred_cols()