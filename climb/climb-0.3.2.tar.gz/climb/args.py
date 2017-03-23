import argparse
from collections import namedtuple

from climb.exceptions import UnknownCommand

Command = namedtuple("Command", ['name', 'parser'])


class ArgsParser(argparse.ArgumentParser):

    def error(self, message):
        raise UnknownCommand(self.format_help().strip())


class Args(object):

    def __init__(self, cli):
        self._cli = cli
        self._commands = []

        self._parser = ArgsParser(add_help=False)
        self._commands_parser = self._parser.add_subparsers(help="command")

        self._load_commands()

        help = self._add_command("help", "show detailed help for command",
                                 parser=self._parser, all_commands=self._commands)
        help.add_argument("subject", nargs="?", default=None)

        self._add_command("exit", "exit console")

        # Store all subparsers for improved help messages and completion support
        actions = [action for action in self._parser._actions
                   if isinstance(action, argparse._SubParsersAction)]
        self._commands.extend([Command(choice, subparser)
                               for action in actions
                               for choice, subparser in action.choices.items()])

    def _load_commands(self):
        """Should be overridden by subclass."""
        pass

    def _add_command(self, name, help, **kwargs):
        command = self._commands_parser.add_parser(name, help=help, add_help=False)
        command.set_defaults(command=name, **kwargs)
        return command

    def parse(self, *args):
        return self._parser.parse_args(args)

    @property
    def commands(self):
        return self._commands
