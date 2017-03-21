"""
micros

Usage:
  micros authenticate <cred-file> <aws_key> <aws_secret>
  micros create <project> [--create_www] [--create_zone]
  micros deploy <project> <directory>
  micros run <port>
  micros delete <project>
  micros -h | --help
  micros --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.
  --create_www                      Create a second S3 bucket with prepended 'www.' which redirects to the default
  --create_zone                     Create hosted Route 53 zone on AWS

Examples:
  micros authenticate ~/.aws/credentials 76231 18290
  micros create festive_season
  micros run 8080
  micros deploy festive_season local/directory/
  micros delete festive_season

Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/zwennesm/micros-cli
"""

from __future__ import absolute_import, division, print_function

from inspect import getmembers, isclass
from docopt import docopt
from . import __version__ as VERSION


def main():
    """Main CLI entrypoint."""
    import micros.commands
    options = docopt(__doc__, version=VERSION)

    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    for (key, value) in options.items():
        if hasattr(micros.commands, key) and value:
            module = getattr(micros.commands, key)
            micros.commands = getmembers(module, isclass)
            command = [command[1] for command in micros.commands if command[0] != 'Base'][0]
            command = command(options)
            command.run()
