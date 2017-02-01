#!/usr/bin/env python

import os, sys, subprocess
from setuptools import setup
from setuptools.command.install import install as _install
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg


def _pre_install(dir=None):
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(THIS_DIR, 'signal_unkillable')
    subprocess.check_call(['make'], cwd=d, env=dict(os.environ, PWD=d))


class bdist_egg(_bdist_egg):
    def run(self):
        _pre_install()
        _bdist_egg.run(self)


class install(_install):
    def run(self):
        self.execute(
            _pre_install, (self.install_lib,), msg="Running pre install task"
        )
        _install.run(self)


setup(
    name='signal_unkillable',
    version='0.0.8',
    description=(
        'A python interface to the SIGNAL_UNKILLABLE flag in linux.'
    ),
    packages=['signal_unkillable'],
    package_data={'signal_unkillable': ['*.c', '*.ko', 'Makefile']},
    cmdclass={'install': install},
)
