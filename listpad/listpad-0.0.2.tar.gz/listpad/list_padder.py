class ListPadder:
    """
    >>> ListPadder([4, None], 0).pad([[1, 2], [3, 4, 5]])
    [[1, 2, 0, 0], [3, 4, 5, 0]]
    >>> ListPadder([4, None], 0, centerize=True).pad([[1, 2], [3, 4, 5]])
    [[0, 1, 2, 0], [3, 4, 5, 0]]
    >>> ListPadder([4, 3, None], 0).pad([
    ...     [[1, 2], [3, 4, 5]],
    ...     [[6, 7, 8]]
    ... ])
    [[[1, 2, 0, 0], [3, 4, 5, 0], [0, 0, 0, 0]], [[6, 7, 8, 0], [0, 0, 0, 0], [0, 0, 0, 0]]]
    """

    def __init__(self, lengths, bottom_dummy, centerize=False):
        self._lengths = {(level + 1): length
                         for level, length in enumerate(lengths)}
        self._dummies = {0: bottom_dummy}  # level -> dummy
        self._centerize = centerize

    def _dummy(self, level):
        if level in self._dummies:
            return self._dummies[level]

        assert level != 0

        self._dummies[level] = [self._dummy(level - 1)] * self._lengths[level]
        return self._dummies[level]

    def pad(self, list_):
        if not isinstance(list_, list):
            return list_

        padded_sub_lists = [self.pad(sub_list) for sub_list in list_]

        return (padded_sub_lists
                if self._lengths[self._level(list_)] is None else
                self._pad_list_of_padded_sub_lists(padded_sub_lists))

    def _pad_list_of_padded_sub_lists(self, list_):
        level = self._level(list_)
        length = self._lengths[level]

        dummy_head, dummy_tail = self._split_in_half(
            self._dummy(level)[:max(length - len(list_), 0)])

        return (dummy_head + list_[:length]
                if self._centerize else
                list_[:length] + dummy_head) + dummy_tail

    def _level(self, list_):
        if not isinstance(list_, list):
            return 0

        if len(list_) == 0:
            return 1

        if not all(self._level(elem) == self._level(list_[0]) for elem in list_):
            raise ValueError("Nest levels of sublists are not balanced. {}"
                             .format(list_))

        return self._level(list_[0]) + 1

    @staticmethod
    def _split_in_half(list_):
        half_length = len(list_) // 2
        return list_[:half_length], list_[half_length:]
