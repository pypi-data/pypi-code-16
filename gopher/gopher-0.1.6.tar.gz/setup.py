from setuptools import setup
from setuptools import find_packages

import gopher

with open('README.rst', "r") as f:
    long_description = f.read()


def _requires_from_file(filename):
    return open(filename).read().splitlines()

setup(
    name=gopher.__name__,
    version=gopher.__version__,
    author=gopher.__author__,
    author_email=gopher.__email__,
    packages=find_packages(),
    description="Download randomized gopher image (png) from gopherize.me",
    long_description=long_description,
    url=gopher.__url__,
    license=gopher.__license__,
    install_requires=_requires_from_file('requirements.txt'),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Utilities",
        "Environment :: Console"
    ],
    entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      gopher = gopher:main
    """,
)
