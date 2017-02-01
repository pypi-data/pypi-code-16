#!/usr/bin/env python

import os, sys, subprocess
from setuptools import setup
from setuptools.command.install import install as _install
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg


def _pre_install(dir=None):
    subprocess.check_call(
        ['make'],
        cwd='./signal_unkillable',
        env=dict(os.environ, PWD=os.environ['PWD'] + '/signal_unkillable'),
    )


class bdist_egg(_bdist_egg):
    def run(self):
        _pre_install()
        super(bdist_egg, self).run()


class install(_install):
    def run(self):
        self.execute(
            _pre_install, (self.install_lib,), msg="Running pre install task"
        )
        super(install, self).run()


setup(
    name='signal_unkillable',
    version='0.0.5',
    description=(
        'A python interface to the SIGNAL_UNKILLABLE flag in linux.'
    ),
    packages=['signal_unkillable'],
    package_data={'signal_unkillable': ['*.c', '*.ko', 'Makefile']},
    cmdclass={'install': install},
)
