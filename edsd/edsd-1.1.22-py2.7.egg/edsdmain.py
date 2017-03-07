#!/usr/local/python
# coding:utf-8
# Copyright (C) Alibaba Group

"""
EDAS detector - A simple script to detect the EDAS running environment.

$ edsd help
  show this document.

$ edsd list [check_id][.point_id]

$ edsd list 1

$ edsd list 1.1

$ edsd check 1

$ edsd check 1.1

$ edsd check all

$ edsd view [check_id.point_id]
"""

__author__ = "Thomas Li <yanliang.lyl@alibaba-inc.com>"
__license__ = "GNU License"

import sys

from edsd import __version__, colored
import edsd.collect

err = sys.stderr.write

try:
    import warnings
    warnings.filterwarnings("ignore")

    import getpass
    user = getpass.getuser()
    if user != 'admin':
        err(colored("Warning", 'red') +
                         ": edsd is recommended running with user 'admin'\n")

    import sys
    ver = sys.version_info
    if ver < (2, 6):
        print colored("Warning", 'red') + ': python version needs 2.6+'

    from edsd.cps import install
    install()
except Exception as e:
    err('init error: ' + str(e))
    sys.exit(-1)


def collect():
    import edsd.collect
    edsd.collect.collect()

def main_shell():
    import edsd.commandline
    cpc = edsd.commandline.CheckPointCmd()
    try:
        cpc.cmdloop()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as _:
        import traceback
        traceback.print_exc()


def commandline():
    from optparse import OptionParser
    parser = OptionParser("usage %prog [options] action")
    parser.add_option('-v', '--verbose', dest="verbose", action="store_true",
                      default=False, help="print detail messages.")

    (options, args) = parser.parse_args()

    if options.verbose:
        edsd.collect.DEBUG = True

    if len(args) == 0:
        usage()
        sys.exit(-1)

    try:
        do(args[0], *args[1:])
    except Exception as e:
        err(e.message)


def do(name, *args):
    cmd = CommandLine()
    func = getattr(cmd, 'do_'+name, None)
    if func is None:
        usage()
        sys.exit(-1)
    func(*args)


def usage():
    import os

    err('usage: %s [options] args, options: \n'
        '    check [all|n|n.n]: check a check point or a single point.\n'
        '    list  [all|n|n.n]: list a check point or a single point.\n'
        '    checkp service_name : check a provider service.\n'
        '    checkc service_name : check a consumer service.\n'
        '    version          : view the current version.\n'

        % os.path.basename(sys.argv[0]))


class CommandLine():
    def do_view(self, *args):
        edsd.collect.view(*args)

    def do_list(self, cp):
        if cp is None:
            err("check point is none.")
            return

        from .commandline import list_cp
        list_cp(cp)

    def do_check(self, cp):
        if cp is None:
            err("check point is none.")
            return

        from .commandline import check
        check(cp)

    def do_checkp(self, servicename):
        """Check a provider service name"""

        import edsd.hsfgrepper
        edsd.hsfgrepper.ping(servicename, consumer=False)

    def do_checkc(self, servicename):
        """Check a consumer service name"""
        import edsd.hsfgrepper
        edsd.hsfgrepper.ping(servicename, consumer=True)


    def do_version(self, *args):
        print __version__


if __name__ == '__main__':
    commandline()

