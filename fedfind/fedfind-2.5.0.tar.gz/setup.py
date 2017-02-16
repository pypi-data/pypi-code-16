import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below. Stolen from
# https://pythonhosted.org/an_example_pypi_project/setuptools.html
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "fedfind",
    version = "2.5.0",
    entry_points = {'console_scripts': ['fedfind = fedfind.cli:main'],},
    author = "Adam Williamson",
    author_email = "awilliam@redhat.com",
    description = "Fedora Finder finds Fedora - images, more to come?",
    license = "GPLv3+",
    keywords = "fedora release image media iso",
    url = "https://www.happyassassin.net/fedfind/",
    packages = ["fedfind"],
    install_requires = ['cached-property', 'productmd', 'setuptools', 'six'],
    tests_require=['pytest', 'mock'],
    cmdclass = {'test': PyTest},
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 or later "
        "(GPLv3+)",
    ],
)
