#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
bling.py

usage:
    bling start
    bling stop
    bling run
    bling build [--publish] [--debug]

commands:
    start         starts app inside an interactive container
    stop          stops running container
    run           starts app inside a container, executing the specified run command
    build         invokes `packer build` with packer template json file

options:
    --publish     publishes the build artifact to a remote registry
    --debug       enables debug mode

    -h --help     shows this
    -v --version  shows version
"""
from . import __version__

from .core import blingrc
from .core import commands
from .core.io import err

from .domain.blingrc import MissingBlingConfig
from .domain.blingrc import MalformedBlingConfig
from .domain.blingrc import InvalidBlingConfig

from docopt import docopt


def _parse_user_input(config, args):
    is_valid = blingrc.validate_config(config)
    if not is_valid:
        err('invalid bling config (see above), exiting')
        return None
    if args['start']:
        return commands.start(config)
    if args['stop']:
        return commands.stop(config)
    if args['build']:
        return commands.build(config, should_publish=args['--publish'], is_debug=args['--debug'])
    if args['run']:
        return commands.run(config)
    err('unexpected bling command..., exiting')


def main():
    args = docopt(__doc__, version=__version__)
    try:
        config = blingrc.open_config()
    except (MissingBlingConfig, MalformedBlingConfig, InvalidBlingConfig) as e:
        return err('%s' % e)
    try:
        _parse_user_input(config, args)
    except KeyboardInterrupt:
        pass
    exit(0)


if __name__ == '__main__':
    main()
