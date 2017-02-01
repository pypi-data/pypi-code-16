#!/usr/bin/env python

import os, sys, subprocess
from distutils.core import setup

print sys.argv

if 'install' in sys.argv:
    subprocess.check_call(
        ['make'],
        cwd='./signal_unkillable',
        env=dict(os.environ, PWD=os.environ['PWD'] + '/signal_unkillable'),
    )


setup(
    name='signal_unkillable',
    version='0.0.3',
    description=(
        'A python interface to the SIGNAL_UNKILLABLE flag in linux.'
    ),
    packages=['signal_unkillable'],
    package_data={'signal_unkillable': ['*.c', '*.ko', 'Makefile']},
)
