import codecs
import os
import sys
 
try:
    from setuptools import setup
except:
    from distutils.core import setup
 
def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()
 
 
 
NAME = "qzonesecret"
PACKAGES = ["qzonesecret"]
 
DESCRIPTION = "Find secrets in Qzone of any QQ."
 
LONG_DESCRIPTION = "Find secrets in Qzone of any QQ."
 
KEYWORDS = "Qzone python QQ"

 
AUTHOR = "Charles Yang"

 
AUTHOR_EMAIL = "mryang@minelandcn.com"

 
URL = "https://pypi.python.org/pypi/qzonesecret/"

 
VERSION = "0.13"

 
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
