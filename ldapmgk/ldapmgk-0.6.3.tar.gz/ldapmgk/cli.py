# -*- coding: utf-8 -*-
"""ldapmgk

Usage:
    ldapmgk [options] user ACTION [<username>] [<email>] [<name>]
    ldapmgk [options] group ACTION [<groupname>] [<username>]
    ldapmgk [options] servergroup ACTION [<groupname>] [<username>]
    ldapmgk --version
    ldapmgk -h

User ACTION argument:
    list      List all users on the LDAP directory
    show      Show details for a user
    add       Add a new user to the LDAP directory
    remove    Delete a user from the LDAP directory
    resetpwd  Reset a user's password

Group ACTION argument:
    create    Add a new group to the LDAP directory
    delete    Delete a group from the LDAP directory
    add       Add a user to a group
    remove    Remove a user from a group

Server Group ACTION argument:
    add       Add a user to a server group
    remove    Remove a user from a server group

Examples:
    ldapmgk user list
    ldapmgk user add ldapmgk ldapmk@example.com "ldapmgk user"
    ldapmgk user show ldapmgk
    ldapmgk group create vpn
    ldapmgk group add vpn ldapmgk
    ldapmgk group show vpn
    ldapmgk servergroup add server_admin ldapmgk
    ldapmgk user resetpwd ldapmgk

Global Options:
    -c, --config=<file>     Configuration file [default:
                            /etc/ldapmgk/config.cfg]
    -o, --output=<file>     Log output to file
    -f, --force             Force some procedures
    -v, --verbose           Verbose output
    -d, --debug             Debug output
    -q, --quiet             Quiet output
    -h, --help              Show this screen
    -V, --version           Show version

"""
from inspect import getmembers, isclass
from docopt import docopt
import sys
import logging
from . import __version__ as VERSION


def main():
    """Main CLI entrypoint."""
    import commands

    options = docopt(
        __doc__,
        version="ldapmgk %s" % (VERSION)
    )

    # intialize logging
    if options['--debug'] is True:
        log_level = logging.DEBUG
    elif options['--verbose'] is True:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    log = logging.getLogger("")
    log.setLevel(log_level)

    # stdout handler if needed
    if not (options['--quiet']):
        log_ch = logging.StreamHandler(sys.stdout)
        log_ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        log.addHandler(log_ch)

    # file handler if needed
    if (options['--output']):
        log_fh = logging.FileHandler(options['--output'])
        log_fh.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        log.addHandler(log_fh)

    # dinamically match the command line and load corresponding class
    for k, v in options.iteritems():
        if hasattr(commands, k) and v:
            module = getattr(commands, k)
            commands = getmembers(module, isclass)
            command = [
                command[1] for command in commands if command[0] != 'Base'
            ][0]
            command = command(options)
            command.run()
