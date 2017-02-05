import importlib

from .kata import Kata
from .suite import Suite


def main(argv):
    if len(argv) != 1:
        display_usage_and_quit()

    elements = argv[0].split('::')

    if len(elements) > 3:
        display_usage_and_quit()

    module_name = elements.pop(0)

    try:
        module = importlib.import_module('.{}'.format(module_name), 'katas')
    except ModuleNotFoundError:
        display_usage_and_quit()

    if len(elements) == 0:
        suite = Suite.from_module(module)
        suite.run()
        exit(0)

    class_name = elements.pop(0)

    try:
        kata_class = getattr(module, class_name)
    except AttributeError:
        message = 'Available classes:\n' + '\n'.join('  {}'.format(class_name) for class_name in available_class_names(module))
        display_usage_and_quit(message)

    if len(elements) == 0:
        suite = Suite.from_class(kata_class)
        suite.run()
        exit(0)

    try:
        seed = int(elements[0])
    except ValueError:
        display_usage_and_quit('seed must be an integer')

    kata = kata_class()
    kata.run(seed)


def available_class_names(module):
    return sorted(k for k, v in vars(module).items() if isinstance(v, type) and issubclass(v, Kata) and k != 'Kata')


def available_module_names():
    return ['list_comprehensions']


def display_usage_and_quit(message=None):
    if message is None:
        message = 'Available modules:\n' + '\n'.join('  {}'.format(module_name) for module_name in available_module_names())

    print('Usage: python -m katas module[::class[::seed]]')
    print()
    print(message)

    exit(1)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
