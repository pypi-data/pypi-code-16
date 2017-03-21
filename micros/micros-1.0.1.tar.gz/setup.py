"""Packaging settings."""


from codecs import open
from os.path import abspath, dirname, join
from subprocess import call

from setuptools import Command, find_packages, setup

from micros import __version__


this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.rst'), encoding='utf-8') as general_file:
    long_description = general_file.read()


class RunTests(Command):
    """Run all tests."""
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run all tests!"""
        errno = call(['py.test', '--cov=micros', '--cov-report=term-missing'])
        raise SystemExit(errno)


setup(
    name = 'micros',
    version = __version__,
    description = 'A skeleton command line program in Python.',
    long_description = long_description,
    url = 'https://github.com/zwennesm/micros-cli',
    author = 'Martijn Zwennes',
    author_email = 'martijn.zwennes@debijenkorf.nl',
    license = 'Apache Licence 2.0',
    classifiers = [
        'Intended Audience :: Developers',
    ],
    keywords = 'cli',
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires = ['docopt', 'boto3'],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    entry_points = {
        'console_scripts': [
            'micros=micros.cli:main',
        ],
    },
    cmdclass = {'test': RunTests},
)
