import os
import sys
import argparse
import logging
import pathlib
import configparser
import importlib

from commands import *
from basecommand import Command
from colors import ANSIColors

logger = logging.getLogger(__name__)
ROOT = pathlib.Path(__file__).parent
TILDA = f'{ANSIColors.BLUE}~{ANSIColors.ENDC}'
DEFAULT_CONFIG_NAME = pathlib.Path('.gitlabvars.ini')


class CLI:
    def command_map(self):
        # for command in commands.__all__:
        #     importlib.import_module(f'commands.{command}')
        return {subclass.command_name(): subclass for subclass in Command.__subclasses__()}

    @classmethod
    def main(cls):
        cls().run()

    def _get_config(self):
        virtualenv = os.environ.get('VIRTUAL_ENV')
        if virtualenv:
            print(f'{TILDA} I\'m inside a virtualenv {ANSIColors.GREEN}{virtualenv}{ANSIColors.ENDC}')
            virtualenv_path = pathlib.Path(virtualenv)
            local_config = virtualenv_path.parent / DEFAULT_CONFIG_NAME
        homedir = pathlib.Path.home()
        global_config = homedir / DEFAULT_CONFIG_NAME
        if local_config.exists():
            print(f'{TILDA} Using local config file: {ANSIColors.GREEN}{local_config}{ANSIColors.ENDC}\n')
            config_file = local_config
        elif global_config.exists():
            print(f'{TILDA} Using global config file: {ANSIColors.GREEN}{global_config}{ANSIColors.ENDC}\n')
            config_file = global_config
        else:
            print(f'''
{TILDA} Config file does not exist.
Please, specify config file as argument or put it
in $HOME directory under the name ".gitlabvars.ini"''')
            sys.exit(1)
        config = configparser.ConfigParser()
        config.read(str(config_file))
        defaults = dict(config.items('Defaults'))
        return defaults

    def run(self):
        conf_parser = argparse.ArgumentParser(add_help=False)
        conf_parser.add_argument('-c', '--conf_file',
                                 help='Specify config file', metavar='FILE')
        args, remaining_argv = conf_parser.parse_known_args()
        if args.conf_file:
            config = configparser.SafeConfigParser()
            config.read([args.conf_file])
            defaults = dict(config.items('Defaults'))
        else:
            defaults = self._get_config()
            if not defaults:
                sys.exit(1)

        parser = argparse.ArgumentParser(
            parents=[conf_parser],
            description='Usage/documentation for this CLI'
        )
        parser.add_argument('--private_token', action='store', help='Private token')
        parser.add_argument(
            '-v',
            '--verbose',
            action='store_true',
            help='Verbose logging mode.'
        )
        parser.add_argument('--cert_path', help='Path to certificate for GitLab.')
        parser.set_defaults(**defaults)
        subparsers = parser.add_subparsers(title='Command', dest='command')

        command_map = self.command_map()
        for command_name, command_class in command_map.items():
            subparser = subparsers.add_parser(
                command_name,
                help=command_class.__doc__)
            command_class.configure_argument_parser(subparser)

        args = parser.parse_args(remaining_argv)
        if args.verbose:
            logging.basicConfig(level=logging.DEBUG)
            logger.debug(args)
        if not args.command:
            parser.print_help()
            sys.exit(1)
        if not args.private_token:
            print(f'{TILDA} Set {ANSIColors.RED}private token{ANSIColors.ENDC} as a positional argument or specify in config file.')
            parser.print_help()
            sys.exit(1)
        command_class = command_map[args.command]
        command_class(args).run()


def main():
    CLI.main()


if __name__ == '__main__':
    CLI.main()
