#!/usr/bin/env python3
# pylint: disable=missing-docstring
import codecs
from glob import glob
from setuptools.command.sdist import sdist
from setuptools import setup, find_packages
try:
    codecs.lookup('mbcs')
except LookupError:
    def func(name, enc=codecs.lookup('ascii')):
        return {True: enc}.get(name == 'mbcs')
    codecs.register(func)


class Sdist(sdist):
    """Custom ``sdist`` command to ensure that mo files are always created."""

    def run(self):
        self.run_command('compile_catalog')
        # sdist is an old style class so super cannot be used.
        sdist.run(self)


setup(name='gscli',
      version='1.3.0',
      description='Command-line shell for GNU Social',
      long_description=open('README.rst').read(),
      author='dtluna',
      author_email='dtluna@openmailbox.org',
      maintainer='dtluna',
      maintainer_email='dtluna@openmailbox.org',
      license='GPLv3',
      classifiers=[
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
      ],
      package_data={
          '': '*.mo',
      },
      url='https://gitgud.io/dtluna/gscli',
      platforms=['any'],
      packages=find_packages(),
      include_package_data=True,
      install_requires=['gnusocial>=2.2.0', 'prompt-toolkit', 'voluptuous', 'tzlocal',
                        'pyxdg', 'keyring', 'keyrings.alt', 'babel'],
      scripts=glob('scripts/*'))
