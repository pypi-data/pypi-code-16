from argparse import ArgumentParser
from os.path import expanduser
from sys import stderr
from locale import setlocale, LC_ALL
from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.history import FileHistory
from gnusocial.utils import GNUSocialAPIError
from .config import Config, NoDefaultConfigError, create_default_config
from .commands import commands, execute
from .validation import CommandValidator
from .i18n import _


parser = ArgumentParser(description=_('A CLI client for GNU Social.'))
parser.add_argument('command', nargs='*', help=_('command to run'), metavar=_('COMMAND'))
parser.add_argument('--help-cmds', nargs='+', metavar=_('COMMAND'),
                    help=_('show info about specified commands'))
parser.add_argument('--list-commands', action='store_true',
                    help=_('show available commands'))
command_completer = WordCompleter(commands.keys())
history = FileHistory(expanduser('~/.gscli_history'))


def main():
    setlocale(LC_ALL, '')
    args = parser.parse_args()
    try:
        try:
            config = Config()
        except NoDefaultConfigError:
            config = create_default_config()
        if args.list_commands:
            execute('help', config)
            quit()
        if args.help_cmds:
            execute(['help'] + args.help_cmds, config, no_split=True)
            quit()
        if args.command:
            execute(args.command, config, no_split=True)
            quit()
        while True:
            text = prompt(
                '(gscli) ', completer=command_completer,
                history=history, auto_suggest=AutoSuggestFromHistory(),
                validator=CommandValidator(), get_title=lambda: 'gscli',
            )
            if text:
                try:
                    execute(text, config)
                except SystemExit:
                    continue
                except GNUSocialAPIError as e:
                    print(_('Error: '), e.error_message, file=stderr)
    except (EOFError, KeyboardInterrupt):
        quit()
