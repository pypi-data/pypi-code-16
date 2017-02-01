#!/usr/bin/env python

import os, sys, subprocess
from distutils.core import setup
from distutils.command.install import install as _install


def _pre_install(dir):
    subprocess.check_call(
        ['make'],
        cwd='./signal_unkillable',
        env=dict(os.environ, PWD=os.environ['PWD'] + '/signal_unkillable'),
    )


class install(_install):
    def run(self):
        self.execute(
            _pre_install, (self.install_lib,), msg="Running pre install task"
        )
        super(install, self).run()


setup(
    name='signal_unkillable',
    version='0.0.4',
    description=(
        'A python interface to the SIGNAL_UNKILLABLE flag in linux.'
    ),
    packages=['signal_unkillable'],
    package_data={'signal_unkillable': ['*.c', '*.ko', 'Makefile']},
    cmdclass={'install': install},
)
