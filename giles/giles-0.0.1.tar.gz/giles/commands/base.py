from . import registry
from giles.parsers import subparses

import chalk
import six
import sys


class CommandBase(type):

    def __new__(cls, name, bases, attrs):
        new_class = super(CommandBase, cls).__new__(cls, name, bases, attrs)
        parents = [base for base in bases if isinstance(base, CommandBase)]
        if parents:
            new_class._instance = None
            registry[new_class.name] = new_class
        return new_class


class Command(six.with_metaclass(CommandBase)):
    """
    """

    _instance = None
    name = NotImplemented
    parser = NotImplemented
    needs_config = True

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, giles):
        self.giles = giles
        self.parser.set_defaults(func=self._run)

    def run(self, args):
        raise NotImplementedError()

    def render(self, output):
        output = output or {}
        _chalk = getattr(chalk, output.get('color', 'blue'))
        if 'message' in output:
            _chalk('{}'.format(output.get('message')))

        table = output.get('table')
        if table:
            width = table.get('width', 12)
            heading = self.format_row(table.get('heading', []), width=width)
            _chalk(heading, opts=['bold'])
            for item in table.get('data', []):
                _chalk(self.format_row(item, width=width))

    def format_row(self, row, width):
        return '\t'.join([str(_).ljust(width) for _ in row])

    def _run(self, args):
        try:
            if self.needs_config:
                self.giles._configure()
            output = self.run(args)
            self.render(output)
        except Exception as err:
            chalk.red(str(err), opts=['bold'])
            raise SystemError(err)
