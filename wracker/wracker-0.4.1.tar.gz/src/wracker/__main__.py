from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import contextlib
import sys

import wracker


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parsed_args = wracker.parse_args(args)
    cmd = parsed_args.command
    if cmd == 'install':
        project_dir = wracker.look_up_for_file_or_die(wracker.INPUT_FILE)
        reqs, locks = wracker.get_requirements(project_dir)
        dists = wracker.ensure_packages(
            reqs, locks, wracker.get_platform_info())
        wracker.write_frozen(project_dir, [d.as_requirement() for d in dists])
    elif cmd == 'exec':
        wracker.handle_exec(parsed_args.exec_args)
    else:
        wracker.die("Unknown command:", args[1])


if __name__ == '__main__':
    main(sys.argv[1:])
