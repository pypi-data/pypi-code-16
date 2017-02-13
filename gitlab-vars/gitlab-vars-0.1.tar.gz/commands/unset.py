from basecommand import Command
from client import APIClient


class CommandUnset(Command):
    """
    Unset one or more variables.
    """
    @classmethod
    def configure_argument_parser(cls, parser):
        parser.usage = 'Unset KEY1 [KEY2 KEY3 ...]'
        parser.add_argument(
            'variables',
            action='store',
            type=str,
            nargs='+',
            help='Variable keys to unset.'
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
        client.unset(self.args.variables)
