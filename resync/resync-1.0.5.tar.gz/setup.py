"""Setup for ResurceSync library and client implementation."""
from setuptools import setup, Command
import os

# Extract version number from resync/_version.py. Here we 
# are very strict about the format of the version string 
# as an extra sanity check. (Thanks for comments in 
# http://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package )
import re
VERSIONFILE="resync/_version.py"
verfilestr = open(VERSIONFILE, "rt").read()
match = re.search(r"^__version__ = '(\d\.\d.\d+(\.\d+)?)'", verfilestr, re.MULTILINE)
if match:
    version = match.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE))

class Coverage(Command):
    """Class to allow coverage run from setup."""

    description = "run coverage"
    user_options = []

    def initialize_options(self):
        """Empty initialize_options."""
        pass

    def finalize_options(self):
        """Empty finalize_options."""
        pass

    def run(self):
        """Run coverage program."""
        os.system("coverage run --source=resync setup.py test")
        os.system("coverage report")
        os.system("coverage html")
        print("See htmlcov/index.html for details.")

setup(
    name='resync',
    version=version,
    packages=['resync'],
    scripts=['bin/resync','bin/resync-explorer'],
    classifiers=["Development Status :: 4 - Beta",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: Apache Software License",
                 "Operating System :: OS Independent", #is this true? know Linux & OS X ok
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 2.6",
                 "Programming Language :: Python :: 2.7",
                 "Programming Language :: Python :: 3.3",
                 "Programming Language :: Python :: 3.4",
                 "Programming Language :: Python :: 3.5",
                 "Programming Language :: Python :: 3.6",
                 "Topic :: Internet :: WWW/HTTP",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 "Environment :: Web Environment"],
    author='Simeon Warner',
    author_email='simeon.warner@cornell.edu',
    description='ResourceSync library and client',
    long_description=open('README').read(),
    url='http://github.com/resync/resync',
    install_requires=[
        "requests",
        "python-dateutil>=1.5",
        "defusedxml>=0.4.1",
        "testfixtures"
    ],
    test_suite="tests",
    cmdclass={
        'coverage': Coverage
    }
)
