"""
pwdc

Usage:
  pwdc init     [-d] --pwd-url=<url-of-pwd>
  pwdc create   [-d] [--session_file=<sf>] [--pwd-url=<url-of-pwd>]
  pwdc env      [-d] [-u] [--session_file=<sf>] [--pwd-url=<url-of-pwd>]
  pwdc delete   [-d] [--session_file=<sf>] [--pwd-url=<url-of-pwd>]
  pwdc info     [-d] [--session_file=<sf>] [--pwd-url=<url-of-pwd>]
  pwdc attach   [-d] --session_id=<si> [--pwd-url=<url-of-pwd>]
  pwdc -h | --help
  pwdc --version

Options:
  --session_file=<sf>               File were to store the pwd session [default: /tmp/pwd.session]
  --pwd-url=<url-of-pwd>            Play With Docker Domain Name
  -d                                Debug mode
  -u                                unset environment
  -h --help                         Show this screen.
  --version                         Show version.
  --session_id=<si>                 Attach to an existing session_id (this will replace your current session)

Examples:
  pwdc init --pwd-url=http://play-with-docker.com
  pwdc create                       Create a PWD session with Swarm enabled
  eval $(pwdc env)                  To Setup your docker client to call to your PWD instance
  pwdc delete                       Delete a PWD Session
  pwdc status                       Print the session status

Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/allamand/pwd-cli
"""


from inspect import getmembers, isclass

from docopt import docopt

from . import __version__ as VERSION

from . import utils





#global utils

def main():
    """Main CLI entrypoint."""
    import pwdc.commands
    options = docopt(__doc__, version=VERSION)

    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    for (k, v) in options.items(): 
        if hasattr(pwdc.commands, k) and v:
            module = getattr(pwdc.commands, k)
            pwdc.commands = getmembers(module, isclass)
            command = [command[1] for command in pwdc.commands if command[0] != 'Base'][0]

            u = utils.Utils(options) 
            command = command(u, options)

            command.run()
