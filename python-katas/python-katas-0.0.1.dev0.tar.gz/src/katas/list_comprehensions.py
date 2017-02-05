import random

from .kata import Kata


WORDS = ['cat', 'dog', 'bat', 'hog', 'fish', 'sheep', 'goat']


class MapInts1(Kata):
    def get_environment(self):
        lst = [random.randint(1, 10) for _ in range(random.randint(3, 7))]
        return {'lst': lst}

    def get_target_str(self):
        operator = random.choice(['+', '-', '*'])
        operand = random.randint(2, 5)
        return '[x {} {} for x in lst]'.format(operator, operand)


class MapStrs1(Kata):
    def get_environment(self):
        lst = random.sample(WORDS, random.randint(3, len(WORDS)))
        return {'lst': lst}

    def get_target_str(self):
        method = random.choice(['upper', 'title'])
        return '[x.{}() for x in lst]'.format(method)


class FilterInts1(Kata):
    def get_environment(self):
        lst = [random.randint(1, 10) for _ in range(random.randint(3, 7))]
        return {'lst': lst}

    def get_target_str(self):
        operator = random.choice(['<', '<=', '>', '>='])
        operand = random.randint(4, 6)
        return '[x for x in lst if x {} {}]'.format(operator, operand)
