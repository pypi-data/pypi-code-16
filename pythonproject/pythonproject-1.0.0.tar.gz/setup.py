#!/usr/local/bin/python3

from distutils.core import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pythonproject",
    version = "1.0.0",
    author = "Akis, Christina, Paschalis",
    author_email = "pnatsidis@hotmail.com",
    description = "This is our little project...",
    url="https://github.com/pnatsi/thisisatest",
    keywords="project python linux bioinfo-grad",
    packages=['pythonproject'],
    long_description=read('README'),
)
