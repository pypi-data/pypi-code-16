import codecs
import os
import sys

try:
    from setuptools import setup
except:
    from distutils.core import setup

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

NAME = "TestPackageQSC"
PACKAGES = ["TestPackageQSC",]
DESCRIPTION = "This package can do the Chinese semantic analysis."
LONG_DESCRIPTION = read("README.rst")
KEYWORDS = "package test"
AUTHOR = "qushichao"
AUTHOR_EMAIL = "578312618@qq.com"
URL = "https://bitbucket.org/shichaoqu/semantic-analysis-tool/overview"
VERSION = "0.0.2"
LICENSE = "MIT"
setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords = KEYWORDS,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    url = URL,
    license = LICENSE,
    packages = PACKAGES,
    include_package_data=True,
    zip_safe=True,
)
