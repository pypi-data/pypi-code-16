"""
Generate a macOS property list file for environment variables.

Should be run with the names of one or more environment variables to include
in the resulting plist file.  If no filename argument is provided via the
command line the resulting plist file is output to the terminal.  If a
filename is provided via the command line no output to the terminal is
performed unless the --verbose flag is also provided.
"""

import argparse
import os
import plistlib


def genplist(envvars):
    "Generate the launchctl program argument plist."
    launchctl = [
        "/bin/launchctl",
        "setenv",
    ]

    for ev in envvars:
        if ev.upper() in os.environ:
            launchctl.append(ev.upper())
            launchctl.append(os.environ[ev.upper()])

    return dict(Label="setenv.startup", ProgramArguments=launchctl,
                RunAtLoad=True, ServiceIPC=False)


def parse_args():
    "Parse command line arguments."
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", default=None)
    parser.add_argument("--verbose", "-v", action="store_true", default=False)
    parser.add_argument("envvar", nargs="+")
    return parser.parse_args()


def main():
    "Main application logic."
    args = parse_args()

    plist = genplist(args.envvar)
    if args.filename is not None:
        plistlib.writePlist(plist, os.path.expanduser(args.filename))
    if args.verbose or args.filename is None:
        print(plistlib.writePlistToString(plist))


if __name__ == '__main__':
    main()
