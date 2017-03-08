import sys


class Iterator:
    def __init__(self, max_index=sys.maxsize):
        self._index = 0
        self.max = max_index

    def __iter__(self):
        """
        Iterator
        :return:
        """
        return self

    def __next__(self):
        """
        Get next number
        :return: int
        """
        if self._index < self.max:
            self._index += 1
            return self._index
        raise StopIteration()

    def next(self):
        """
        Get next value
        call __next__()
        :return:
        """
        return self.__next__()

    def current(self):
        """
        Get current value
        :return:
        """
        return self._index
