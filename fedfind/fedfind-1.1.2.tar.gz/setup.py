import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below. Stolen from
# https://pythonhosted.org/an_example_pypi_project/setuptools.html
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "fedfind",
    version = "1.1.2",
    entry_points = {'console_scripts': ['fedfind = fedfind.cli:main'],},
    author = "Adam Williamson",
    author_email = "awilliam@redhat.com",
    description = "Fedora Finder finds Fedora - images, more to come?",
    license = "GPLv3+",
    keywords = "fedora release image media iso",
    url = "https://www.happyassassin.net/fedfind/",
    packages = ["fedfind"],
    install_requires = ['setuptools', 'six'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 or later "
        "(GPLv3+)",
    ],
)
