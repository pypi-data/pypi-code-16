#!/usr/bin/env python3
from __future__ import print_function
import sys
from .catchers import __version__, StdErrCatcher, StdOutCatcher

if __name__ == '__main__':
    print('Test run for OutputCatcher v. {}\n'.format(__version__))

    with StdOutCatcher(escaped=False, max_length=0) as fakeout:
        print(
            'This is a test. you shouldn\'t see it right away.',
            file=sys.stdout,
        )
    print('Captured stdout: {}'.format(fakeout.output))

    with StdErrCatcher(escaped=False, max_length=0) as fakeerr:
        print('Testing stderr output.', file=sys.stderr)
    print('Captured stderr: {}'.format(fakeerr.output))

    print('\nFinished with tests.')
    sys.exit(0)
