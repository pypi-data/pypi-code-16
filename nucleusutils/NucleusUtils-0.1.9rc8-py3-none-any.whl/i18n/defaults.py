from jinja2 import Undefined as _Undef

CONTEXT_NAME = 'global'
LOGGER_NAME = 'Internalization'
UNDEFINED_WORD = '%undefined%'


class Undefined(_Undef):
    def __int__(self):
        return 0

    def __str__(self):
        return UNDEFINED_WORD

    def __int__(self):
        return 0

    def __float__(self):
        return .0

    def __le__(self, other):
        return False

    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return None

    def __ge__(self, other):
        return None

    def __iter__(self):
        yield from UNDEFINED_WORD

    def __add__(self, other):
        return other

    def __sub__(self, other):
        return other

    def __divmod__(self, other):
        return other

    def __get__(self, instance, owner):
        return UNDEFINED_WORD

    def __getitem__(self, item):
        return UNDEFINED_WORD
