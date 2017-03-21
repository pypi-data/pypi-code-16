import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "SMIT",
    version = "0.3",
    packages = find_packages(),
    author = "ELIAS ARNAUD",
    author_email = "jgaelia@starxpert.fr",
    description = "A package to help automate creation of testing in Django",
    url = "http://code.google.com/p/SMIT/",
    include_package_data = True
)

