import os
from setuptools import setup, find_packages


PACKAGE = "kyd"
VERSION = __import__(PACKAGE).__version__

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="kyd",
    version=VERSION,
    author="ShangHai Shilai",
    author_email="developers@kuaiyudian.com",
    description=read("README"),
    license="BSD",
    keywords="stock kuaiyudian sdk kyd",
    url="http://packages.python.org/kyd",
    packages=find_packages(exclude=["tests.*", "tests"]),
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)
