from distutils.core import setup
from setuptools import find_packages

PACKAGE = "weixunsdkcore"
NAME = "WeixunSDKCore"
DESCRIPTION = "WeixunSDKCore"
AUTHOR = "Maple Liu"
AUTHOR_EMAIL = "maple.liu@microfastup.com"
URL = "http://github.com/weixunsdkcore"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    # long_description=read("README.md"),  
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="Apache License, Version 2.0",
    url=URL,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)  