import sys
from basecommand import Command
from client import APIClient
from utils import ask


class CommandClear(Command):
    """
    Clears all variables.
    """
    def run(self):
        proceed = ask('Proceed (y,n)? ', ['y', 'n'])
        if proceed == 'n':
            sys.exit(1)

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
        client.clear()
