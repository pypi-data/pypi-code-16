from distutils.core import setup

setup(
    # Application name:
    name="PyGoSec",

    # Version number (initial):
    version="0.5.0",

    # Application author details:
    author="Gaurab Bhattacharjee",
    author_email="gaurabb@hotmail.com",

    # Packages
    packages=["goinstallchecks","installscanners","scannerwrappers"],

    # Details
    url="http://pypi.python.org/pypi/PyGoSec_v050/",

    #
    # license="LICENSE.txt",
    description="Python wrapper for GO Lang static secure code analyzers",

    long_description=open("README.md").read(),

)
