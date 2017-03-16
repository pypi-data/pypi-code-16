import random


class Generator:
    def __init__(self, hint):
        self.hint = hint

    def __call__(self, idx):
        raise NotImplementedError('invalid generator: %r' % self)


class CommandGenerator(Generator):
    def __call__(self, idx):
        pass


class TypeHintGenerator(Generator):
    def __call__(self, idx):
        method = getattr(self, 'from_' + self.hint.__name__)
        return method(idx)

    def from_int(self, idx):
        return random.randint(-1000000, 1000000)

    def from_float(self, idx):
        return random.uniform(-1000000, 1000000)

    def from_str(self, idx):
        return fake.text()