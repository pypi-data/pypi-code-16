import os
import shlex
import readline
import traceback

from climb.config import load_config, config
from climb.exceptions import CLIException
from climb.paths import ROOT_PATH


class Climb(object):
    _prompt = "[{path}]> "
    _running = False

    def __init__(self, name, args, commands, completer, prompt=None, skip_delims=None):
        self._name = name
        load_config(name)

        self._current_path = ROOT_PATH
        self._verbose = config.getboolean(name, 'verbose')
        self._history_file = os.path.expanduser(config[name].get('history', ''))

        self._args = args(self)
        self._commands = commands(self)
        self._completer = completer(self)

        if prompt is not None:
            self._prompt = prompt

        self._skip_delims = skip_delims

    def run(self):
        """Loops and executes commands in interactive mode."""
        if self._skip_delims:
            delims = readline.get_completer_delims()
            for delim in self._skip_delims:
                delims = delims.replace(delim, '')
            readline.set_completer_delims(delims)

        readline.parse_and_bind("tab: complete")
        readline.set_completer(self._completer.complete)

        if self._history_file:
            # Ensure history file exists
            if not os.path.isfile(self._history_file):
                open(self._history_file, 'w').close()

            readline.read_history_file(self._history_file)

        self._running = True
        try:
            while self._running:
                try:
                    command = input(self._format_prompt())
                    if command:
                        result = self.execute(*shlex.split(command))
                        if result:
                            print(result)
                except CLIException as exc:
                    print(exc)
                except (KeyboardInterrupt, EOFError):
                    self._running = False
                    print()
                except Exception as exc:
                    if self._verbose:
                        traceback.print_exc()
                    else:
                        print(exc)
        finally:
            if self._history_file:
                readline.write_history_file(self._history_file)

    def _format_prompt(self):
        return self._prompt.format(path=self._current_path)

    def execute(self, *args):
        """Executes single command and returns result."""
        command, kwargs = self.parse(*args)
        return self._commands.execute(command, **kwargs)

    def parse(self, *args):
        parsed = self._args.parse(*args)

        kwargs = dict(parsed._get_kwargs())
        command = kwargs.pop('command')

        return command, kwargs

    def log(self, message, *args, **kwargs):
        if self._verbose:
            print(message.format(*args, **kwargs))

    def set_running(self, running):
        self._running = running

    def set_current_path(self, current_path):
        self._current_path = current_path

    @property
    def args(self):
        return self._args

    @property
    def commands(self):
        return self._commands

    @property
    def current_path(self):
        return self._current_path
