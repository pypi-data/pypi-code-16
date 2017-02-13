from basecommand import Command
from client import APIClient


class CommandProjects(Command):
    """
    List all projects you have access to with their
    corresponding IDs.
    """
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
        client.projects()
