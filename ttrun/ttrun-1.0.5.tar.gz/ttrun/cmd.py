# Copyright (c) 2016 Red Hat, Inc
#
# This file is part of ttrun
#
# ttrun is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ttrun is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import os
import subprocess
import sys

import testtools


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Simple CLI to run tests with testtools')
    parser.add_argument(
        '-e', dest='environment', help='tox environment to use')
    parser.add_argument('tests', nargs='*', help='Tests to run')
    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.environment:
        envpath = '.tox/{environment}/bin'.format(environment=args.environment)
        pyexe = '{envpath}/python'.format(envpath=envpath)
        # Executables in the virtualenv need to be in the path
        os.environ['PATH'] = '{envpath}:{path}'.format(
            envpath=envpath, path=os.environ['PATH'])
        return subprocess.Popen(
            [pyexe, '-m', 'testtools.run'] + args.tests,
            env=os.environ).wait()
    else:
        return testtools.run.main([sys.argv[0]] + args.tests, sys.stdout)


if __name__ == '__main__':
    sys.exit(main())
