import sys
from basecommand import Command
from utils import StoreKeyValuePair
from client import APIClient


class CommandSet(Command):
    """
    Set one or more variables.
    """
    @classmethod
    def configure_argument_parser(cls, parser):
        parser.usage = 'Set KEY1=VALUE1 [KEY2=VALUE2 ...]'
        parser.add_argument(
            'variables',
            action=StoreKeyValuePair,
            nargs='+',
            help='Variables to set in format FOO=BAR'
        )
        parser.add_argument(
            '-o',
            '--override',
            action='store_true',
            help='Override variable, if it exists'
        )
        cls.parser = parser

    def run(self):
        kwargs = {
            'cert_path': self.args.cert_path,
            'debug': self.args.verbose
        }
        client = APIClient(
            self.args.base_url,
            self.args.project_id,
            self.args.private_token,
            **kwargs
        )
        client.set(self.args.variables)
