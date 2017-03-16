import inspect
from collections import namedtuple

from funspec.arguments import CommandGenerator, TypeHintGenerator
from funspec.utils import capture_output


class AnswerKey:
    """
    Wraps a function decorated with @answer_key in a funspec module.
    """

    def __init__(self, function, name=None):
        self.function = function
        self.name = name or function.__name__
        self._spec = inspect.getfullargspec(self.function)
        self._generators = create_arg_generators(self._spec.annotations)

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def __repr__(self):
        return 'TestFunction(%r)' % getattr(self.function, '__name__',
                                            '<function>')

    def arguments(self, i):
        """
        Return a tuple of valid arguments from the AnswerKey object.
        """

        values = {k: g(i) for k, g in self._generators.items()}
        return tuple(values[arg] for arg in self._spec.args)

    def examples(self, size, keep_errors=False, simple=False):
        """
        Return a sequence of `size` examples with the results of
        running the answer key function through all inputs.
        """

        example_list = []
        for i in range(size):
            args = self.arguments(i)
            with capture_output(True) as out:
                result = self.function(*args)
            example_list.append(Example(args, result, str(out)))
        return example_list


def create_arg_generators(hints):
    """
    Return a dictionary of generator functions from the dictionary of type
    hints.
    """

    generators = {}
    for name, hint in hints.items():
        if isinstance(hint, str):
            generator = CommandGenerator(hint)
        elif isinstance(hint, type):
            generator = TypeHintGenerator(hint)
        elif callable(hint):
            generator = TypeHintGenerator(hint)
        else:
            raise ValueError('unsupported type hint: %r' % hint)
        generators[name] = generator
    return generators


#
# Examples
#
ExampleBase = namedtuple('Example', ['args', 'result', 'output'])


class Example(ExampleBase):
    """
    Represents examples that ran successful.
    """

    def is_valid(self):
        return True


class ErrorExample(ExampleBase):
    """
    Represents examples that produced errors while running.
    """
    
    def is_valid(self):
        return False