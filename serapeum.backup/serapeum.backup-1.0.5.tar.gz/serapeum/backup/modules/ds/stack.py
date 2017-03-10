

class Stack:
    def __init__(self):
        self.__stack = []

    def add(self, item):
        self.__stack.append(item)

    def pop(self):
        if self.size > 0:
            return self.__stack.pop()
        else:
            return None

    def peek(self):
        if self.size > 0:
            return self.__stack[-1]
        else:
            return None

    @property
    def size(self):
        return len(self.__stack)

    @property
    def is_empty(self):
        if self.size != 0:
            return False
        return True
