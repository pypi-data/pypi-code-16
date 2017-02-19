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
    name = "wikitcms",
    version = "1.2",
    author = "Adam Williamson",
    author_email = "awilliam@redhat.com",
    description = ("Fedora QA wiki test management library"),
    license = "GPLv3+",
    keywords = "fedora qa mediawiki validation",
    url = "https://www.happyassassin.net/wikitcms/",
    packages = find_packages(),
    install_requires = ['mwclient>=0.6.5'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 or later "
        "(GPLv3+)",
    ],
)
