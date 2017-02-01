#!/usr/bin/env python

import os, sys, subprocess
from setuptools import setup
from setuptools.command.install import install as _install
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg
#from setuptools.command import bdist_wheel as _bdist_wheel


def _pre_install(dir=None):
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(THIS_DIR, 'signal_unkillable')
    subprocess.check_call(['make'], cwd=d, env=dict(os.environ, PWD=d))


class install(_install):
    def run(self):
        _pre_install()
        _install.run(self)


class bdist_egg(_bdist_egg):
    def run(self):
        _pre_install()
        _bdist_egg.run(self)


#class bdist_wheel(_bdist_wheel):
#    def run(self):
#        _pre_install()
#        _bdist_wheel.run(self)


setup(
    name='signal_unkillable',
    version='0.0.9',
    description=(
        'A python interface to the SIGNAL_UNKILLABLE flag in linux.'
    ),
    packages=['signal_unkillable'],
    package_data={'signal_unkillable': ['*.c', '*.ko', 'Makefile']},
    cmdclass={
        'install': install, 'bdist_egg': bdist_egg,# 'bdist_wheel': bdist_wheel,
    },
)
