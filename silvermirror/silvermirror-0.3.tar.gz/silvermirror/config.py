#!/usr/bin/env python

import optparse
import os
import sys

from .utils import home
from martini.config import ConfigMunger

class SilvermirrorConfiguration(object):
    """
    SilverMirror configuration class

    The current form is an .ini file
    [TODO: use `install_requires='configuration'`]:

    [::SilverMirror::]
    ...
    """

    main_section = '::SilverMirror::'

    def __init__(self, filename=None):
        if filename is not None:
            self.read_config(filename)
    def read_config(self, filename):

        # read file
        config = ConfigMunger(filename).dict()

        # main configuration
        main = config.pop(, {})
        main.setdefault('basedir', home())
        main['ignore'] = main.get('ignore', '').split() # patterns to ignore - 
        main['hosts'] = main.get('hosts', '').split()
        main['timeout'] = float(main.get('timeout', '10.'))

        # password prompt
        truth = dict([(str(i).lower(), i) for i in (True, False)])
        password = main.get('password', 'true')
        try:
            main['password'] = truth[password.lower()]
        except KeyError:
            raise KeyError("password must be True or False (You gave: '%s')" % password)

        # resources
        for resource in config:

            # directory of resource
            directory = config[resource].get('directory', resource)
            if os.path.isabs(directory):
                raise NotImplementedError("absolute directories will not work for now so....don't do this!")

            else:
                directory = os.path.join(main['basedir'], directory)
            config[resource]['directory'] = directory.rstrip(os.path.sep)

            # per-resource files to ignore
            # XXX  regexps for now (see `man unison`)
            # - this is bad as whitespace patterns cannot be ignored
            config[resource]['ignore'] = main['ignore'][:] + config[resource].get('ignore', '').split()

    # set + return ditionary of config
    self.main = main
    self.resources = config
    config = (main, config)

def main(args=sys.argv[1:]):

    usage = '%prog [options]'
    parser = optparse.OptionParser(usage=usage, description=__doc__)
    options, args = parser.parse_args(args)

if __name__ == '__main__':
    main()
