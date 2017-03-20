#!/usr/bin/env python

import os
import shutil
from setuptools import setup, Command

__version__ = '1.1.1'

class Doc(Command):
    description = "Custom doc command that converts README.md to the reStructured text file README.txt"
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        import pypandoc
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd
        description = pypandoc.convert('README.md', 'rst')
        with open('README.txt','w+') as f:
            f.write(description)

class Clean(Command):
    description = "Custom clean command that forcefully removes dist/build directories"
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd
        shutil.rmtree("./build", ignore_errors=True)
        shutil.rmtree("./dist", ignore_errors=True)
        shutil.rmtree("./viewlog.egg-info", ignore_errors=True)
        try:
            os.remove("./MANIFEST")
        except OSError:
            pass
setup(
    name='pickpaged',
    packages= ['pickpaged'],
    version=__version__,
    author='roubles',
    author_email='rouble@gmail.com',
    url='https://github.com/roubles/pickpaged',
    download_url='https://github.com/roubles/pickpaged/tarball/' + __version__,
    license='MIT',
    description='pick an option in the terminal with a simple paged GUI',
    long_description=open('README.txt').read(),
    install_requires=['pick>=0.6.1'],
    cmdclass={ 'doc': Doc, 'clean': Clean}
)
