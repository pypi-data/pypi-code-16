from __future__ import absolute_import, division, print_function

from argparse import ArgumentParser
from subprocess import Popen
import os


DEPENDENCIES = [
    ('develop', [
        # Install development packages
        '-rdevelop-requirements.txt',
        '-rtests/develop-requirements.txt',

        # Install extra packages
        '-rrequirements.txt',
        '-rtest-requirements.txt'
    ]),
    ('pip', [
        '-rrequirements.txt',
        '-rtest-requirements.txt'
    ]),
    ('travis', [
        '--editable=git+https://github.com/OpenEntityMap/oem-framework.git@{BRANCH}#egg=oem-framework',
        '--editable=git+https://github.com/OpenEntityMap/oem-core.git@{BRANCH}#egg=oem-core',
        '--editable=git+https://github.com/OpenEntityMap/oem-format-json.git@{BRANCH}#egg=oem-format-json',
        '--editable=git+https://github.com/OpenEntityMap/oem-storage-file.git@{BRANCH}#egg=oem-storage-file',

        '-rrequirements.txt',
        '-rtest-requirements.txt'
    ])
]


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('env')

    args = parser.parse_args()

    # Retrieve branch
    branch = os.environ.get('CURRENT_BRANCH') or 'master'

    # Install environment dependencies
    env_parts = args.env.split('-')

    for key, dependencies in DEPENDENCIES:
        if key not in env_parts:
            continue

        for dep in dependencies:
            dep = dep.replace('{BRANCH}', branch)

            # Install dependency
            print('Installing dependency: %r' % (dep,))
            process = Popen(['pip', 'install', dep])
            process.wait()
