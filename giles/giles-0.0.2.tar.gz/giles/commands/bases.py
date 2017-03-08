from __future__ import unicode_literals, print_function, absolute_import
import argparse
import chalk
import six

# https://docs.python.org/2/library/argparse.html

class CommandTypeBase(type):

    def __new__(cls, name, bases, attrs):
        is_abstract = attrs.pop('abstract', False)
        new_class = super(CommandTypeBase, cls).__new__(cls, name, bases, attrs)
        parents = [base for base in bases if isinstance(base, CommandTypeBase)]
        if parents:
            new_class._instance = None
            new_class.is_abstract = is_abstract
            cls.setup(new_class)
        return new_class

    def setup(cls):
        raise NotImplementedError()


class CommandType(CommandTypeBase):

    def setup(cls):
        parser = argparse.ArgumentParser(
            prog=cls.__name__.lower(),
            description=cls.__doc__
        )

        cls.subparses = parser.add_subparsers(help='Summary')
        cls.parser = parser


class SubCommandType(CommandTypeBase):

    def setup(cls):
        if not cls.is_abstract:
            cls.parser = cls.parent.subparses.add_parser(
                cls.__name__.lower(),
                description=cls.__doc__
            )
            # prime the singleton
            cls()


class CommandBase(six.with_metaclass(CommandType)):

    additional_commands = []

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def run(self):
        args = self.parser.parse_args()
        args.func(args)


class SubCommandBase(six.with_metaclass(SubCommandType)):
    """
    """

    _instance = None
    parent = NotImplemented

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        self.parser.set_defaults(func=self._run)
        self.add_arguments()

    def add_arguments(self):
        pass

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
            output = self.run(args)
            self.render(output)
        except Exception as err:
            chalk.red(str(err), opts=['bold'])
            raise SystemError(err)
