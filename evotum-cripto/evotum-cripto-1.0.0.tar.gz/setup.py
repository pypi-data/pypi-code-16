    # coding: latin-1

import os
from setuptools import setup

# Utility function to read the README file
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name = "evotum-cripto",
    version = "1.0.0",
    author = "André Baptista",
    author_email = "andre.baptista@devisefutures.com",
    description = ("eVotUM Cripto"),
    license = "GPL-3.0",
    keywords = "electronic vote crypto",
    url = "https://gitlab.com/eVotUM/Cripto-py",
    packages=["eVotUM", "eVotUM/Cripto"],
    long_description=read("README"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    install_requires=required,
)
