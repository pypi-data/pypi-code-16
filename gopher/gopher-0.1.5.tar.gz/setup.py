from setuptools import setup
from setuptools import find_packages

import gopher

with open('README.rst', "r") as f:
    long_description = f.read()

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
    install_requires=[
        'click==6.7',
        'requests==2.13.0'
    ],
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
