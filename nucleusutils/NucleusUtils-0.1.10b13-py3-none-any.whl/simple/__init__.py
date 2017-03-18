class Counter:
    """
    Simple iterator object
    >>> foo = Counter()
    >>> next(foo)
    <<< 0
    >>> next(foo)
    <<< 1
    """

    def __init__(self, index=0):
        self.index = index

    def reset(self, index=0):
        self.index = index

    def __iter__(self):
        return self

    def __next__(self):
        self.index += 1
        return self.index - 1

    def __str__(self):
        return 'Counter::' + str(self.index)


class Set:
    """
    Simple ordered set
    """

    def __init__(self, elements=None):
        if elements is None:
            elements = []
        self.__elements = []
        self.update(elements)

    def append(self, element):
        if element not in self.__elements:
            self.__elements.append(element)

    def pop(self, element):
        if isinstance(element, int):
            return self.__elements.pop(element)
        index = self.__elements.index(element)
        return self.__elements.pop(index)

    def update(self, elements):
        for element in elements:
            self.append(element)

    def __iter__(self):
        yield from self.__elements
