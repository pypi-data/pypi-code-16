# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


version_suffix = ''


class TestRunner(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        tox.cmdline(self.test_args)




setup(
    name="urlhmac",
    version="0.4.0" + version_suffix,
    url='',
    description='',
    author='Florian Ludwig',
    install_requires=[
    ],
    extras_requires={
        'test': ['tox', 'pytest'],
        'docs': ['sphinx_rtd_theme']
    },
    packages=['urlhmac'],
    include_package_data=True,
    cmdclass={
        'test': TestRunner
    }
)
