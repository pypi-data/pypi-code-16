"""Packaging settings."""

from codecs import open
from os.path import abspath, dirname, join
from subprocess import call
from setuptools import Command, find_packages, setup
from simplefc import __version__

this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
    long_description = file.read()

#class RunTests(Command):
#    """Run all tests."""
#    description = 'run tests'
#    user_options = []
#
#    def initialize_options(self):
#        pass
#
#    def finalize_options(self):
#        pass
#
#    def run(self):
#        """Run all tests!"""
#        errno = call(['py.test', '--cov=simplefc', '--cov-report=term-missing'])
#        raise SystemExit(errno)

setup(
    name = 'simplefc',
    version = __version__,
    description = 'A simple command-line flash card interface.',
    long_description = long_description,
    url = 'https://github.com/vlahm/simplefc',
    author = 'Mike Vlah',
    author_email = 'vlahm13@gmail.com',
    license = 'GPL-3',
    classifiers = [
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    keywords = 'cli, desktop, tools, utility, study, memory, lifehacks, brain',
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires = ['docopt', 'numpy', 'future'],
  #  extras_require = {
  #      'test': ['coverage', 'pytest', 'pytest-cov'],
  #  },
    entry_points = {
        'console_scripts': [
            'simplefc=simplefc.cli:main',
        ],
    },
   # cmdclass = {'test': RunTests},
)
